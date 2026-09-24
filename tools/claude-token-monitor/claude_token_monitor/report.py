"""Headless text report and limit calibration.

The same engine that drives the tray indicator, rendered to stdout. Useful on
its own (``python -m claude_token_monitor --report``) and as the way the GUI's
data path is verified without a display.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .aggregate import (
    FIVE_HOURS,
    SEVEN_DAYS,
    Aggregator,
    Snapshot,
    Totals,
    metric_label,
    metric_value,
)
from .config import Config
from .formatting import ago, clock, duration, metric_number, money, tokens, tokens_exact
from .scanner import ScanStats, TranscriptScanner, decode_project_name

WIDTH = 72

# Headroom applied when calibrating a limit from observed peak usage: the peak
# is a floor on what the account tolerated, not the cap itself.
CALIBRATION_HEADROOM = 1.35


def build_scanner(config: Config) -> TranscriptScanner:
    scanner = TranscriptScanner(
        bootstrap_days=config.bootstrap_days or None,
        include_sidechains=config.include_sidechains,
    )
    root = config.root_path()
    if root is not None:
        scanner.root = root
    return scanner


def collect(config: Config) -> tuple[Aggregator, TranscriptScanner, ScanStats]:
    """Do one full sweep and return the populated aggregator."""
    scanner = build_scanner(config)
    aggregator = Aggregator(retention_days=config.retention_days)
    aggregator.add(scanner.poll())
    return aggregator, scanner, scanner.last_stats


def _rule(char: str = "-") -> str:
    return char * WIDTH


def _gauge(used: float, limit: float, width: int = 34) -> str:
    ratio = 0.0 if limit <= 0 else min(1.0, used / limit)
    filled = int(round(ratio * width))
    return f"[{'#' * filled}{'.' * (width - filled)}] {ratio * 100:5.1f}%"


def _totals_line(label: str, totals: Totals, metric: str) -> str:
    return (
        f"  {label:<14} {metric_number(metric_value(totals, metric), metric):>10}"
        f"  {tokens(totals.total_tokens):>9}  {money(totals.cost_usd):>10}"
        f"  {totals.requests:>5} req"
    )


def _window_block(
    add,
    label: str,
    totals: Totals,
    limit: int,
    metric: str,
) -> None:
    used = metric_value(totals, metric)
    add(f"  {label:<4} {_gauge(used, limit)}")
    add(
        f"       {metric_number(used, metric, exact=True)} of "
        f"{metric_number(limit, metric, exact=True)} {metric_label(metric)}"
    )
    add(
        f"       raw {tokens_exact(totals.total_tokens)} tokens  |  "
        f"{money(totals.cost_usd)}  |  {totals.requests} req"
    )


def render(snapshot: Snapshot, config: Config, stats: ScanStats | None = None) -> str:
    metric = config.gauge_metric
    lines: list[str] = []
    add = lines.append

    add(_rule("="))
    add(f" Claude Code token usage  --  {clock(snapshot.generated_at)} local")
    add(f" gauge metric: {metric_label(metric)}")
    add(_rule("="))

    add("")
    add(" ROLLING WINDOWS")
    _window_block(add, "5h", snapshot.window_5h, config.limit_5h_tokens, metric)
    resets = snapshot.window_5h_resets_in
    if resets is not None:
        add(f"       oldest call leaves the window in {duration(resets)}")
    add("")
    _window_block(add, "7d", snapshot.window_7d, config.limit_7d_tokens, metric)

    add("")
    add(" TOTALS            gauge      raw tok        cost  requests")
    add(_totals_line("Last 5 hours", snapshot.window_5h, metric))
    add(_totals_line("Today", snapshot.today, metric))
    add(_totals_line("Last 7 days", snapshot.window_7d, metric))
    add(_totals_line("All retained", snapshot.all_time, metric))

    add("")
    add(f" TOKEN MIX ({snapshot.scope_label.lower()})")
    scope = snapshot.scope_totals
    for label, value in (
        ("input", scope.input_tokens),
        ("output", scope.output_tokens),
        ("cache write 5m", scope.cache_write_5m_tokens),
        ("cache write 1h", scope.cache_write_1h_tokens),
        ("cache read", scope.cache_read_tokens),
    ):
        share = 0.0 if not scope.total_tokens else value / scope.total_tokens
        add(f"  {label:<16} {tokens_exact(value):>14}   {share * 100:5.1f}%")

    add("")
    add(f" BY MODEL ({snapshot.scope_label.lower()})")
    if not snapshot.by_model:
        add("  (no usage in scope)")
    for model, totals in snapshot.by_model.items():
        add(
            f"  {model:<28} {tokens(totals.total_tokens):>9}  "
            f"{money(totals.cost_usd):>10}  {totals.requests:>5} req"
        )

    add("")
    add(f" BY PROJECT ({snapshot.scope_label.lower()})")
    if not snapshot.by_project:
        add("  (no usage in scope)")
    for project, totals in snapshot.by_project.items():
        name = decode_project_name(project)
        add(
            f"  {name[:28]:<28} {tokens(totals.total_tokens):>9}  "
            f"{money(totals.cost_usd):>10}  {totals.requests:>5} req"
        )

    add("")
    add(" ACTIVE SESSION")
    if snapshot.active_session_id:
        add(f"  id        {snapshot.active_session_id}")
        add(
            f"  usage     {tokens_exact(snapshot.active_session.total_tokens)} tokens"
            f"  |  {money(snapshot.active_session.cost_usd)}"
            f"  |  {snapshot.active_session.requests} req"
        )
    else:
        add("  (none)")
    add(f"  last call {ago(snapshot.last_activity, snapshot.generated_at)}")

    if stats is not None:
        add("")
        add(" SCAN")
        add(
            f"  {stats.files_seen} files seen, {stats.files_read} read, "
            f"{stats.bytes_read / 1_048_576:.1f} MB, {stats.lines_read} lines"
        )
        add(
            f"  {stats.records} records kept, {stats.duplicates} duplicates skipped, "
            f"{stats.errors} errors, {stats.elapsed_s:.2f}s"
        )

    add(_rule("="))
    return "\n".join(lines)


# --------------------------------------------------------------- calibration


def suggest_limits(
    aggregator: Aggregator,
    metric: str = "weighted",
) -> dict[str, tuple[float, float, datetime | None]]:
    """Peak observed usage per window, plus a suggested limit.

    Returns ``{window: (peak, suggested, peaked_at)}``. The suggestion adds
    headroom because the peak only proves usage reached that level, not that
    the ceiling was anywhere near it.
    """
    result: dict[str, tuple[float, float, datetime | None]] = {}
    for name, window in (("5h", FIVE_HOURS), ("7d", SEVEN_DAYS)):
        peak, at = aggregator.peak_window(window, metric)
        suggested = peak * CALIBRATION_HEADROOM
        result[name] = (peak, suggested, at)
    return result


def limit_from_percent(used: float, percent: float) -> float:
    """Back-solve the real limit from a percentage reported elsewhere.

    Claude's own usage panel shows a percentage against the account's actual
    rate limit -- the number this tool cannot read from disk. Given how much
    usage the engine currently counts in the window, that percentage pins the
    denominator directly, which beats any heuristic.
    """
    percent = float(percent)
    if percent <= 0:
        raise ValueError("percentage must be greater than zero")
    return used / (percent / 100.0)


def percent_uncertainty(used: float, percent: float) -> tuple[float, float]:
    """Range implied by a percentage that was rounded to a whole number.

    A displayed "88%" is anything in [87.5, 88.5), so the implied limit is a
    band, not a point. Worth surfacing rather than implying false precision.
    """
    low = limit_from_percent(used, percent + 0.5)
    high = limit_from_percent(used, max(0.1, percent - 0.5))
    return low, high


def sync_limit(
    config: Config,
    percent: float,
    apply: bool = False,
    used: float | None = None,
) -> str:
    """Derive the 5h limit from a percentage shown by Claude's usage panel.

    ``percent`` and the usage it is paired with must be from the *same moment*.
    Usage climbs continuously while you work, so pairing a fresh count with a
    percentage read even a few minutes ago inflates the implied limit. Pass
    ``used`` to pair against a specific reading (e.g. one taken from a
    screenshot); otherwise the current count is used.
    """
    metric = config.gauge_metric
    measured_now = used is None

    if measured_now:
        aggregator, _scanner, _stats = collect(config)
        now = datetime.now(timezone.utc)
        used = metric_value(aggregator.totals(now - FIVE_HOURS), metric)

    if used <= 0:
        return "No usage in the current 5-hour window -- nothing to calibrate against."

    implied = limit_from_percent(used, percent)
    low, high = percent_uncertainty(used, percent)

    lines = [_rule("="), " Limit synced from Claude's usage panel", _rule("=")]
    lines.append(f" metric        : {metric_label(metric)}")
    lines.append(
        f" paired usage  : {metric_number(used, metric, exact=True)}"
        f"{'  (counted now)' if measured_now else '  (supplied)'}"
    )
    lines.append(f" you reported  : {percent:g}%")
    lines.append(f" implied limit : {metric_number(implied, metric, exact=True)}")
    lines.append(
        f" rounding band : {metric_number(low, metric, exact=True)}"
        f" to {metric_number(high, metric, exact=True)}"
    )
    lines.append(f" currently set : {metric_number(config.limit_5h_tokens, metric, exact=True)}")

    if measured_now:
        lines.append("")
        lines.append(
            " NOTE: paired against usage counted just now. Read the percentage"
        )
        lines.append(
            "       from Claude at this moment -- a reading from minutes ago"
        )
        lines.append(
            "       pairs with a smaller count and inflates the limit. Use"
        )
        lines.append("       --used to pair with a specific earlier reading.")

    if apply:
        config.limit_5h_tokens = max(1, int(implied))
        config.validate()
        path = config.save()
        lines.append("")
        lines.append(f" applied and saved to {path}")
    else:
        lines.append("")
        lines.append(" re-run with --apply to save it")

    lines.append(_rule("="))
    return "\n".join(lines)


def calibrate(config: Config, apply: bool = False) -> str:
    """Derive limits from observed history; optionally persist them."""
    aggregator, _scanner, stats = collect(config)
    metric = config.gauge_metric
    suggestions = suggest_limits(aggregator, metric)

    lines: list[str] = [_rule("="), " Limit calibration from local history", _rule("=")]
    lines.append(f" metric   : {metric_label(metric)}")
    lines.append(f" records  : {len(aggregator)} over {stats.files_seen} files")
    lines.append(f" headroom : x{CALIBRATION_HEADROOM}")
    lines.append("")

    for name, (peak, suggested, at) in suggestions.items():
        when = at.astimezone().strftime("%Y-%m-%d %H:%M") if at else "n/a"
        lines.append(f" {name} window")
        lines.append(f"   observed peak   {metric_number(peak, metric, exact=True)}  (at {when})")
        lines.append(f"   suggested limit {metric_number(suggested, metric, exact=True)}")

    if apply:
        config.limit_5h_tokens = max(1, int(suggestions["5h"][1]))
        config.limit_7d_tokens = max(1, int(suggestions["7d"][1]))
        config.validate()
        path = config.save()
        lines.append("")
        lines.append(f" applied and saved to {path}")
    else:
        lines.append("")
        lines.append(" re-run with --apply to save these as your limits")

    lines.append(_rule("="))
    return "\n".join(lines)


def main(scope: str | None = None) -> int:
    config = Config.load()
    if scope:
        config.scope = scope
        config.validate()
    aggregator, _scanner, stats = collect(config)
    snapshot = aggregator.snapshot(now=datetime.now(timezone.utc), scope=config.scope)
    print(render(snapshot, config, stats))
    return 0


__all__ = [
    "CALIBRATION_HEADROOM",
    "build_scanner",
    "calibrate",
    "collect",
    "limit_from_percent",
    "main",
    "percent_uncertainty",
    "render",
    "suggest_limits",
    "sync_limit",
]
