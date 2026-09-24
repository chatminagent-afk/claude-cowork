"""Turn raw Claude Code transcript lines into usage records.

Claude Code appends one JSON object per line to
``~/.claude/projects/<encoded-cwd>/<session>.jsonl``. Assistant records carry a
``message.usage`` block; everything else is ignored.

The parser is deliberately forgiving: transcripts are written by a live process,
so truncated or unexpected lines are skipped rather than raising.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from . import pricing


@dataclass(frozen=True)
class UsageRecord:
    """One billable assistant turn."""

    dedup_key: str
    timestamp: datetime  # timezone-aware, UTC
    model: str  # normalized alias, e.g. "claude-opus-5"
    raw_model: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_5m_tokens: int
    cache_write_1h_tokens: int
    session_id: str
    project: str
    cwd: str
    is_sidechain: bool
    speed: str | None
    cost_usd: float

    @property
    def total_tokens(self) -> int:
        """Every token the request touched, cache reads included."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_read_tokens
            + self.cache_write_5m_tokens
            + self.cache_write_1h_tokens
        )

    @property
    def billable_tokens(self) -> int:
        """Tokens excluding cache reads, which are billed at 10%."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_write_5m_tokens
            + self.cache_write_1h_tokens
        )

    @property
    def cache_write_tokens(self) -> int:
        return self.cache_write_5m_tokens + self.cache_write_1h_tokens


def _int(value: Any) -> int:
    """Coerce a JSON value to a non-negative int, defaulting to 0."""
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return max(0, value)
    if isinstance(value, float):
        return max(0, int(value))
    return 0


def parse_timestamp(value: Any) -> datetime | None:
    """Parse an ISO-8601 timestamp into an aware UTC datetime."""
    if not isinstance(value, str) or not value:
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _split_cache_writes(usage: dict[str, Any]) -> tuple[int, int]:
    """Split cache-creation tokens into (5-minute TTL, 1-hour TTL).

    ``cache_creation_input_tokens`` is the authoritative total; the nested
    ``cache_creation`` object breaks it down by TTL. When the breakdown is
    missing or disagrees with the total, the remainder is attributed to the
    5-minute bucket -- the cheaper of the two, so cost is never overstated by
    a reconciliation artefact.
    """
    total = _int(usage.get("cache_creation_input_tokens"))
    detail = usage.get("cache_creation")
    if not isinstance(detail, dict):
        return total, 0

    five_m = _int(detail.get("ephemeral_5m_input_tokens"))
    one_h = _int(detail.get("ephemeral_1h_input_tokens"))

    if five_m + one_h == total:
        return five_m, one_h

    if one_h > total:
        # Breakdown is unusable; fall back to the total at the cheap rate.
        return total, 0

    return max(0, total - one_h), one_h


def parse_line(
    line: str | bytes,
    *,
    project: str = "",
    source: str = "",
) -> UsageRecord | None:
    """Parse one transcript line. Returns ``None`` if it carries no usage."""
    if isinstance(line, bytes):
        try:
            line = line.decode("utf-8")
        except UnicodeDecodeError:
            line = line.decode("utf-8", errors="replace")

    line = line.strip()
    if not line or not line.startswith("{"):
        return None

    try:
        obj = json.loads(line)
    except (ValueError, RecursionError):
        return None

    if not isinstance(obj, dict) or obj.get("type") != "assistant":
        return None

    message = obj.get("message")
    if not isinstance(message, dict):
        return None

    usage = message.get("usage")
    if not isinstance(usage, dict):
        return None

    raw_model = message.get("model") or ""
    if pricing.is_synthetic(raw_model):
        return None

    timestamp = parse_timestamp(obj.get("timestamp"))
    if timestamp is None:
        return None

    input_tokens = _int(usage.get("input_tokens"))
    output_tokens = _int(usage.get("output_tokens"))
    cache_read = _int(usage.get("cache_read_input_tokens"))
    write_5m, write_1h = _split_cache_writes(usage)

    if not any((input_tokens, output_tokens, cache_read, write_5m, write_1h)):
        return None

    speed = usage.get("speed")
    if not isinstance(speed, str):
        speed = None

    model = pricing.normalize_model(raw_model)

    return UsageRecord(
        dedup_key=_dedup_key(obj, message, source),
        timestamp=timestamp,
        model=model,
        raw_model=str(raw_model),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_tokens=cache_read,
        cache_write_5m_tokens=write_5m,
        cache_write_1h_tokens=write_1h,
        session_id=str(obj.get("sessionId") or ""),
        project=project,
        cwd=str(obj.get("cwd") or ""),
        is_sidechain=bool(obj.get("isSidechain")),
        speed=speed,
        cost_usd=pricing.cost_usd(
            raw_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_read_tokens=cache_read,
            cache_write_5m_tokens=write_5m,
            cache_write_1h_tokens=write_1h,
            when=timestamp,
            speed=speed,
        ),
    )


def _dedup_key(obj: dict[str, Any], message: dict[str, Any], source: str) -> str:
    """Stable identity for a billable call.

    A single API request can be written to more than one transcript file (a
    subagent's turns land in both its own file and, in some versions, the
    parent's). ``message.id`` plus ``requestId`` identifies the request itself,
    so counting it twice is avoided regardless of how many files mention it.
    """
    message_id = message.get("id")
    request_id = obj.get("requestId")
    if message_id or request_id:
        return f"{message_id or ''}|{request_id or ''}"
    # No request identity available -- fall back to the record's own uuid,
    # qualified by file so two files cannot collide on a reused uuid.
    return f"uuid:{source}|{obj.get('uuid') or ''}"
