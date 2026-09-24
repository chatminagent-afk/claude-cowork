"""Pricing model for Claude Code token usage.

Rates are USD per million tokens. Cache multipliers follow the documented
prompt-caching economics:

    cache write, 5-minute TTL -> 1.25x the model's input rate
    cache write, 1-hour TTL   -> 2.00x the model's input rate
    cache read                -> 0.10x the model's input rate

Everything here is pure arithmetic over a static table, so it is trivially
testable and has no runtime dependencies.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime

CACHE_WRITE_5M_MULTIPLIER = 1.25
CACHE_WRITE_1H_MULTIPLIER = 2.00
CACHE_READ_MULTIPLIER = 0.10

_DATE_SUFFIX = re.compile(r"-\d{8}$")


@dataclass(frozen=True)
class Rate:
    """USD per million tokens."""

    input_per_mtok: float
    output_per_mtok: float


@dataclass(frozen=True)
class IntroRate:
    """A promotional rate that applies up to and including ``through``."""

    rate: Rate
    through: date


# Standard first-party API rates.
BASE_RATES: dict[str, Rate] = {
    "claude-fable-5": Rate(10.0, 50.0),
    "claude-mythos-5": Rate(10.0, 50.0),
    "claude-mythos-preview": Rate(10.0, 50.0),
    "claude-opus-5": Rate(5.0, 25.0),
    "claude-opus-4-8": Rate(5.0, 25.0),
    "claude-opus-4-7": Rate(5.0, 25.0),
    "claude-opus-4-6": Rate(5.0, 25.0),
    "claude-opus-4-5": Rate(5.0, 25.0),
    "claude-opus-4-1": Rate(15.0, 75.0),
    "claude-opus-4-0": Rate(15.0, 75.0),
    "claude-sonnet-5": Rate(3.0, 15.0),
    "claude-sonnet-4-6": Rate(3.0, 15.0),
    "claude-sonnet-4-5": Rate(3.0, 15.0),
    "claude-sonnet-4-0": Rate(3.0, 15.0),
    "claude-haiku-4-5": Rate(1.0, 5.0),
    "claude-3-5-haiku": Rate(0.8, 4.0),
    "claude-3-haiku": Rate(0.25, 1.25),
}

# Promotional pricing currently in effect.
INTRO_RATES: dict[str, IntroRate] = {
    "claude-sonnet-5": IntroRate(Rate(2.0, 10.0), date(2026, 8, 31)),
}

# Fast mode (speed="fast") is billed at a premium on the models that support it.
FAST_MODE_RATES: dict[str, Rate] = {
    "claude-opus-5": Rate(10.0, 50.0),
    "claude-opus-4-8": Rate(10.0, 50.0),
}

# Model identifiers that appear in transcripts but represent no billable call.
SYNTHETIC_MODELS = frozenset({"<synthetic>", "synthetic", "", "unknown"})


def normalize_model(model: str | None) -> str:
    """Reduce a wire model id to its canonical alias.

    ``claude-haiku-4-5-20251001`` -> ``claude-haiku-4-5``. Unknown ids are
    returned lowercased and stripped so they still group consistently.
    """
    if not model:
        return ""
    name = model.strip().lower()
    # Bedrock ids carry a provider prefix; Vertex uses an @-separated version.
    if name.startswith("anthropic."):
        name = name[len("anthropic.") :]
    if "@" in name:
        name = name.split("@", 1)[0]
    return _DATE_SUFFIX.sub("", name)


def is_synthetic(model: str | None) -> bool:
    """True for placeholder model ids that never correspond to a real request."""
    return normalize_model(model) in SYNTHETIC_MODELS


def get_rate(
    model: str | None,
    when: datetime | date | None = None,
    speed: str | None = None,
) -> Rate | None:
    """Resolve the rate for a model, honouring fast mode and intro pricing.

    Returns ``None`` for models with no known pricing, so callers can surface
    "unpriced" rather than silently reporting $0.00 as though it were free.
    """
    name = normalize_model(model)
    if not name or name in SYNTHETIC_MODELS:
        return None

    if speed == "fast" and name in FAST_MODE_RATES:
        return FAST_MODE_RATES[name]

    intro = INTRO_RATES.get(name)
    if intro is not None:
        as_of = _as_date(when)
        if as_of is None or as_of <= intro.through:
            return intro.rate

    return BASE_RATES.get(name)


def _as_date(when: datetime | date | None) -> date | None:
    if when is None:
        return None
    if isinstance(when, datetime):
        return when.date()
    return when


def cost_usd(
    model: str | None,
    *,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_write_5m_tokens: int = 0,
    cache_write_1h_tokens: int = 0,
    when: datetime | date | None = None,
    speed: str | None = None,
) -> float:
    """Cost in USD for one call's token counts. Unknown models cost 0.0."""
    rate = get_rate(model, when=when, speed=speed)
    if rate is None:
        return 0.0

    per_token_in = rate.input_per_mtok / 1_000_000.0
    per_token_out = rate.output_per_mtok / 1_000_000.0

    return (
        input_tokens * per_token_in
        + output_tokens * per_token_out
        + cache_read_tokens * per_token_in * CACHE_READ_MULTIPLIER
        + cache_write_5m_tokens * per_token_in * CACHE_WRITE_5M_MULTIPLIER
        + cache_write_1h_tokens * per_token_in * CACHE_WRITE_1H_MULTIPLIER
    )


def is_priced(model: str | None) -> bool:
    """Whether a cost figure for this model is meaningful."""
    return get_rate(model) is not None
