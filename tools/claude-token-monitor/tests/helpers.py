"""Fixture builders shared across the test modules."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

BASE_TIME = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)


def usage_block(
    input_tokens: int = 10,
    output_tokens: int = 20,
    cache_read: int = 0,
    cache_5m: int = 0,
    cache_1h: int = 0,
    include_detail: bool = True,
    speed: str = "standard",
) -> dict:
    block = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_read_input_tokens": cache_read,
        "cache_creation_input_tokens": cache_5m + cache_1h,
        "speed": speed,
    }
    if include_detail:
        block["cache_creation"] = {
            "ephemeral_5m_input_tokens": cache_5m,
            "ephemeral_1h_input_tokens": cache_1h,
        }
    return block


def assistant_record(
    *,
    message_id: str = "msg_1",
    request_id: str = "req_1",
    model: str = "claude-opus-5",
    timestamp: datetime | None = None,
    session_id: str = "sess-1",
    cwd: str = r"D:\work",
    is_sidechain: bool = False,
    uuid: str = "uuid-1",
    **usage_kwargs,
) -> dict:
    return {
        "type": "assistant",
        "uuid": uuid,
        "requestId": request_id,
        "sessionId": session_id,
        "cwd": cwd,
        "isSidechain": is_sidechain,
        "timestamp": (timestamp or BASE_TIME).isoformat().replace("+00:00", "Z"),
        "message": {
            "id": message_id,
            "role": "assistant",
            "model": model,
            "usage": usage_block(**usage_kwargs),
        },
    }


def line(record: dict) -> str:
    return json.dumps(record)


def write_transcript(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        for record in records:
            handle.write(line(record) + "\n")


def append_transcript(path, records, terminate: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="") as handle:
        payload = "\n".join(line(record) for record in records)
        handle.write(payload + ("\n" if terminate else ""))


def minutes(n: int) -> timedelta:
    return timedelta(minutes=n)
