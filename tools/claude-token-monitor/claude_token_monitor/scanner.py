"""Incrementally tail Claude Code transcript files.

The transcript tree is ~125 MB across a few hundred files, so re-reading it on
every refresh is not viable. This scanner remembers a byte offset per file and
reads only what has been appended since the last poll.

Two details make that safe against a live writer:

* A poll never consumes a partial trailing line. The offset only ever advances
  to a newline boundary, so a record still being written is picked up whole on
  the next poll instead of being parsed as truncated JSON.
* A file that shrinks (truncated, rotated, or replaced) is detected and re-read
  from the start rather than seeking past the new end.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from .parser import UsageRecord, parse_line

DEFAULT_ROOT = Path.home() / ".claude" / "projects"

# Cheap byte-level prefilter: only assistant records carry a usage block, and
# json.loads on ~400k irrelevant lines is the dominant cost without this.
_USAGE_MARKER = b'"usage"'


@dataclass
class FileState:
    offset: int = 0
    size: int = 0
    mtime: float = 0.0


@dataclass
class ScanStats:
    files_seen: int = 0
    files_read: int = 0
    bytes_read: int = 0
    lines_read: int = 0
    records: int = 0
    duplicates: int = 0
    errors: int = 0
    elapsed_s: float = 0.0


@dataclass
class TranscriptScanner:
    """Stateful reader over a transcript directory tree."""

    root: Path = field(default_factory=lambda: DEFAULT_ROOT)
    bootstrap_days: int | None = 30
    include_sidechains: bool = True

    _files: dict[str, FileState] = field(default_factory=dict, init=False)
    _seen: set[str] = field(default_factory=set, init=False)
    _bootstrapped: bool = field(default=False, init=False)
    last_stats: ScanStats = field(default_factory=ScanStats, init=False)

    # ------------------------------------------------------------------ API

    def poll(self) -> list[UsageRecord]:
        """Return usage records appended since the previous call."""
        started = time.monotonic()
        stats = ScanStats()
        records: list[UsageRecord] = []

        cutoff = self._bootstrap_cutoff()
        alive: set[str] = set()

        for path in self._iter_transcripts():
            key = str(path)
            alive.add(key)
            stats.files_seen += 1

            try:
                stat = path.stat()
            except OSError:
                stats.errors += 1
                continue

            state = self._files.get(key)
            if state is None:
                state = FileState()
                self._files[key] = state
                # On the first sweep, skip the body of files that predate the
                # bootstrap window: mark them fully consumed without parsing.
                if not self._bootstrapped and cutoff is not None and stat.st_mtime < cutoff:
                    state.offset = stat.st_size
                    state.size = stat.st_size
                    state.mtime = stat.st_mtime
                    continue

            if stat.st_size < state.offset:
                # Truncated or replaced -- start over rather than seek past EOF.
                state.offset = 0

            if stat.st_size == state.offset:
                state.size = stat.st_size
                state.mtime = stat.st_mtime
                continue

            project = self._project_for(path)
            try:
                chunk, consumed = self._read_from(path, state.offset)
            except OSError:
                stats.errors += 1
                continue

            stats.files_read += 1
            stats.bytes_read += consumed
            state.offset += consumed
            state.size = stat.st_size
            state.mtime = stat.st_mtime

            for record in self._records_from(chunk, project, key, stats):
                records.append(record)

        for stale in set(self._files) - alive:
            del self._files[stale]

        self._bootstrapped = True
        stats.elapsed_s = time.monotonic() - started
        self.last_stats = stats
        return records

    def reset(self) -> None:
        """Forget all offsets and dedup state, forcing a full re-read."""
        self._files.clear()
        self._seen.clear()
        self._bootstrapped = False

    # -------------------------------------------------------------- internals

    def _bootstrap_cutoff(self) -> float | None:
        if self._bootstrapped or not self.bootstrap_days:
            return None
        return time.time() - self.bootstrap_days * 86400

    def _iter_transcripts(self) -> Iterator[Path]:
        if not self.root.exists():
            return
        try:
            yield from sorted(self.root.rglob("*.jsonl"))
        except OSError:
            return

    def _project_for(self, path: Path) -> str:
        """First directory under the root, e.g. ``D--Documents-...-VIRA``.

        Subagent transcripts live in a ``subagents`` subdirectory, so taking the
        first component rather than the parent keeps them with their project.
        """
        try:
            relative = path.relative_to(self.root)
        except ValueError:
            return path.parent.name
        parts = relative.parts
        return parts[0] if len(parts) > 1 else "(root)"

    @staticmethod
    def _read_from(path: Path, offset: int) -> tuple[bytes, int]:
        """Read from ``offset`` to EOF, stopping at the last complete line."""
        with open(path, "rb") as handle:
            handle.seek(offset)
            data = handle.read()

        if not data:
            return b"", 0

        cut = data.rfind(b"\n")
        if cut == -1:
            # No complete line yet; consume nothing and retry next poll.
            return b"", 0

        return data[: cut + 1], cut + 1

    def _records_from(
        self,
        chunk: bytes,
        project: str,
        source: str,
        stats: ScanStats,
    ) -> Iterator[UsageRecord]:
        for raw in chunk.split(b"\n"):
            if not raw:
                continue
            stats.lines_read += 1
            if _USAGE_MARKER not in raw:
                continue

            record = parse_line(raw, project=project, source=source)
            if record is None:
                continue
            if record.is_sidechain and not self.include_sidechains:
                continue
            if record.dedup_key in self._seen:
                stats.duplicates += 1
                continue

            self._seen.add(record.dedup_key)
            stats.records += 1
            yield record


def decode_project_name(project: str) -> str:
    """Make an encoded project directory name readable.

    ``D--Documents-Claude-Cowork-Persada-Cisoka-Residence`` becomes
    ``Persada Cisoka Residence``: the drive prefix and the shared workspace
    prefix carry no information in a list where every row shares them.
    """
    if not project:
        return "(unknown)"
    name = project
    if len(name) > 3 and name[1:3] == "--":
        name = name[3:]
    name = name.replace("-", " ").strip()
    for prefix in ("Documents Claude Cowork", "Documents Claude", "Documents"):
        if name.startswith(prefix):
            trimmed = name[len(prefix) :].strip()
            if trimmed:
                return trimmed
            # The workspace root itself: keep the last words rather than
            # returning an empty string.
            words = prefix.split()
            return " ".join(words[-2:]) if len(words) > 1 else prefix
    return name or "(unknown)"


__all__ = [
    "DEFAULT_ROOT",
    "FileState",
    "ScanStats",
    "TranscriptScanner",
    "decode_project_name",
]
