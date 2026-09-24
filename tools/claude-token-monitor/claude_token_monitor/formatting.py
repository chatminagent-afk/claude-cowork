"""Display helpers shared by the tray icon, the dashboard, and the CLI report."""

from __future__ import annotations

from datetime import datetime, timedelta


def tokens(value: int | float) -> str:
    """Compact token count: 950, 12.3K, 4.05M, 1.20B."""
    value = float(value or 0)
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value < 1_000:
        return f"{sign}{int(value)}"
    if value < 1_000_000:
        return f"{sign}{value / 1_000:.1f}K"
    if value < 1_000_000_000:
        return f"{sign}{value / 1_000_000:.2f}M"
    return f"{sign}{value / 1_000_000_000:.2f}B"


def tokens_exact(value: int | float) -> str:
    """Thousands-separated exact count, for tooltips and detail rows."""
    return f"{int(value or 0):,}"


def money(value: float) -> str:
    """USD, with enough precision that small amounts are not all '$0.00'."""
    value = float(value or 0.0)
    if value and abs(value) < 0.01:
        return f"${value:.4f}"
    if abs(value) < 100:
        return f"${value:,.2f}"
    return f"${value:,.0f}"


def percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def metric_number(value: float, metric_name: str = "weighted", exact: bool = False) -> str:
    """Render a gauge metric with the right units for its kind."""
    if metric_name == "cost":
        return money(value)
    return tokens_exact(value) if exact else tokens(value)


def data_size(num_bytes: int | float) -> str:
    """Byte count with a sensible unit: 812 B, 44.0 KB, 122.5 MB."""
    value = float(num_bytes or 0)
    if value < 1024:
        return f"{int(value)} B"
    if value < 1024 * 1024:
        return f"{value / 1024:.1f} KB"
    if value < 1024 * 1024 * 1024:
        return f"{value / (1024 * 1024):.1f} MB"
    return f"{value / (1024 * 1024 * 1024):.2f} GB"


def duration(delta: timedelta | None) -> str:
    """Human duration: '4h 12m', '38m', 'just now'."""
    if delta is None:
        return "--"
    seconds = int(delta.total_seconds())
    if seconds <= 0:
        return "now"
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    if hours and minutes:
        return f"{hours}h {minutes}m"
    if hours:
        return f"{hours}h"
    if minutes:
        return f"{minutes}m"
    return f"{seconds}s"


def ago(moment: datetime | None, now: datetime | None = None) -> str:
    """'3m ago' style relative time."""
    if moment is None:
        return "never"
    now = now or datetime.now(moment.tzinfo)
    delta = now - moment
    if delta.total_seconds() < 45:
        return "just now"
    return f"{duration(delta)} ago"


def clock(moment: datetime | None) -> str:
    """Local wall-clock time."""
    if moment is None:
        return "--"
    return moment.astimezone().strftime("%H:%M:%S")


__all__ = [
    "ago",
    "clock",
    "data_size",
    "duration",
    "metric_number",
    "money",
    "percent",
    "tokens",
    "tokens_exact",
]
