"""Persisted settings, stored under %APPDATA%\\claude-token-monitor."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, fields
from pathlib import Path

APP_NAME = "claude-token-monitor"


def config_dir() -> Path:
    """Where settings and the log live.

    Deliberately **not** ``%APPDATA%``. Python installed from the Microsoft
    Store runs inside an MSIX container that silently redirects AppData writes
    to ``%LOCALAPPDATA%\\Packages\\PythonSoftwareFoundation.Python...\\LocalCache``.
    That makes the config location depend on which interpreter launched the app,
    so a run started from the .vbs launcher and one started from a plain
    ``python`` on PATH would read different files and appear to lose settings.
    The user profile root is not redirected, so a home-relative path resolves
    identically under every interpreter.
    """
    base = os.environ.get("CLAUDE_TOKEN_MONITOR_HOME")
    if base:
        return Path(base)
    return Path.home() / f".{APP_NAME}"


def config_path() -> Path:
    return config_dir() / "config.json"


@dataclass
class Config:
    """User-tunable settings.

    ``limit_5h_tokens`` has no source of truth in the transcripts -- Claude Code
    does not record the account's rate limit anywhere readable on disk. Rather
    than ship an invented number, the app can calibrate it from the highest
    rolling-5h usage actually observed in local history (``--calibrate``, or the
    dashboard button). The default below is only a starting point, and the raw
    token counts are always shown next to the gauge so the percentage is never
    the only thing on screen.

    ``gauge_metric`` defaults to ``weighted`` -- see ``Totals.weighted_tokens``.
    Raw totals are ~96% cache reads in practice, which bill at 0.1x, so gauging
    on them would mostly measure cache-hit rate rather than consumption.
    """

    limit_5h_tokens: int = 9_000_000
    limit_7d_tokens: int = 70_000_000
    gauge_metric: str = "weighted"
    theme: str = "auto"
    poll_interval_s: float = 2.0
    bootstrap_days: int = 30
    retention_days: int = 90
    include_sidechains: bool = True
    warn_pct: float = 0.60
    crit_pct: float = 0.85
    scope: str = "today"
    transcript_root: str = ""

    # ------------------------------------------------------------------- io

    @classmethod
    def load(cls, path: Path | None = None) -> "Config":
        """Read config from disk, falling back to defaults on any problem."""
        path = path or config_path()
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return cls()
        if not isinstance(raw, dict):
            return cls()

        known = {f.name: f for f in fields(cls)}
        kwargs = {}
        for name, value in raw.items():
            spec = known.get(name)
            if spec is None:
                continue
            try:
                if spec.type in (int, "int"):
                    kwargs[name] = int(value)
                elif spec.type in (float, "float"):
                    kwargs[name] = float(value)
                elif spec.type in (bool, "bool"):
                    kwargs[name] = bool(value)
                else:
                    kwargs[name] = str(value)
            except (TypeError, ValueError):
                continue

        config = cls(**kwargs)
        config.validate()
        return config

    def save(self, path: Path | None = None) -> Path:
        """Write config atomically so a crash mid-write cannot corrupt it."""
        path = path or config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(asdict(self), indent=2, sort_keys=True)

        handle, tmp_name = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as tmp:
                tmp.write(payload)
                tmp.flush()
                os.fsync(tmp.fileno())
            os.replace(tmp_name, path)
        except BaseException:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise
        return path

    # ------------------------------------------------------------ validation

    def validate(self) -> "Config":
        """Clamp values into ranges the app can actually operate in."""
        self.limit_5h_tokens = max(1, int(self.limit_5h_tokens))
        self.limit_7d_tokens = max(1, int(self.limit_7d_tokens))
        self.poll_interval_s = min(300.0, max(0.5, float(self.poll_interval_s)))
        self.bootstrap_days = max(0, int(self.bootstrap_days))
        self.retention_days = max(1, int(self.retention_days))
        self.warn_pct = min(1.0, max(0.05, float(self.warn_pct)))
        self.crit_pct = min(1.0, max(self.warn_pct, float(self.crit_pct)))
        if self.scope not in ("5h", "today", "7d", "30d", "all"):
            self.scope = "today"
        if self.gauge_metric not in ("weighted", "total", "billable", "cost"):
            self.gauge_metric = "weighted"
        if self.theme not in ("auto", "light", "dark"):
            self.theme = "auto"
        return self

    def root_path(self) -> Path | None:
        """Explicit transcript root, or ``None`` to use the default."""
        return Path(self.transcript_root) if self.transcript_root else None


__all__ = ["APP_NAME", "Config", "config_dir", "config_path"]
