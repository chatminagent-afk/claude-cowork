"""Roll usage records up into the windows the indicator displays.

The aggregator is mutated by the polling thread and read by the UI thread, so
every public method takes an internal lock. Records are kept in timestamp order
and pruned to a retention horizon to bound memory.
"""

from __future__ import annotations

import bisect
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable, Sequence

from . import pricing
from .parser import UsageRecord

FIVE_HOURS = timedelta(hours=5)
SEVEN_DAYS = timedelta(days=7)


@dataclass
class Totals:
    """Summed token counts and cost for some slice of records."""

    requests: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_5m_tokens: int = 0
    cache_write_1h_tokens: int = 0
    cost_usd: float = 0.0
    first_seen: datetime | None = None
    last_seen: datetime | None = None

    @property
    def cache_write_tokens(self) -> int:
        return self.cache_write_5m_tokens + self.cache_write_1h_tokens

    @property
    def total_tokens(self) -> int:
        """Every token touched, cache reads included."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_read_tokens
            + self.cache_write_5m_tokens
            + self.cache_write_1h_tokens
        )

    @property
    def billable_tokens(self) -> int:
        """Tokens excluding cache reads."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_write_5m_tokens
            + self.cache_write_1h_tokens
        )

    @property
    def weighted_tokens(self) -> float:
        """Cache-adjusted tokens, in input-token equivalents.

        Raw totals are dominated by cache reads -- typically 90%+ of every
        token touched -- but a cache read bills at a tenth of an input token
        and consumes correspondingly less quota. Weighting each bucket by its
        billing multiplier gives a usage number that tracks real consumption
        instead of tracking cache-hit rate.
        """
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_write_5m_tokens * pricing.CACHE_WRITE_5M_MULTIPLIER
            + self.cache_write_1h_tokens * pricing.CACHE_WRITE_1H_MULTIPLIER
            + self.cache_read_tokens * pricing.CACHE_READ_MULTIPLIER
        )

    def add(self, record: UsageRecord) -> None:
        self.requests += 1
        self.input_tokens += record.input_tokens
        self.output_tokens += record.output_tokens
        self.cache_read_tokens += record.cache_read_tokens
        self.cache_write_5m_tokens += record.cache_write_5m_tokens
        self.cache_write_1h_tokens += record.cache_write_1h_tokens
        self.cost_usd += record.cost_usd
        if self.first_seen is None or record.timestamp < self.first_seen:
            self.first_seen = record.timestamp
        if self.last_seen is None or record.timestamp > self.last_seen:
            self.last_seen = record.timestamp


@dataclass
class Snapshot:
    """An immutable view handed to the UI."""

    generated_at: datetime
    window_5h: Totals
    window_7d: Totals
    today: Totals
    all_time: Totals
    by_model: dict[str, Totals]
    by_project: dict[str, Totals]
    active_session_id: str = ""
    active_session: Totals = field(default_factory=Totals)
    last_activity: datetime | None = None
    scope_label: str = "Today"
    scope_totals: Totals = field(default_factory=Totals)

    @property
    def window_5h_resets_in(self) -> timedelta | None:
        """Time until the oldest call in the 5h window ages out of it.

        This is what "when do I get headroom back" actually means for a rolling
        window: the earliest request leaving the window is the next moment usage
        drops, not some fixed clock boundary.
        """
        if self.window_5h.first_seen is None:
            return None
        remaining = (self.window_5h.first_seen + FIVE_HOURS) - self.generated_at
        return remaining if remaining.total_seconds() > 0 else timedelta(0)


METRICS: tuple[str, ...] = ("weighted", "total", "billable", "cost")

_METRIC_LABELS = {
    "weighted": "cache-adjusted tokens",
    "total": "total tokens",
    "billable": "tokens excluding cache reads",
    "cost": "cost (USD)",
}


def metric_value(totals: Totals, metric: str = "weighted") -> float:
    """Extract the number a gauge should be measured against."""
    if metric == "total":
        return float(totals.total_tokens)
    if metric == "billable":
        return float(totals.billable_tokens)
    if metric == "cost":
        return float(totals.cost_usd)
    return float(totals.weighted_tokens)


def metric_label(metric: str = "weighted") -> str:
    return _METRIC_LABELS.get(metric, _METRIC_LABELS["weighted"])


def record_metric(record: UsageRecord, metric: str = "weighted") -> float:
    """``metric_value`` for a single record, without building a Totals."""
    if metric == "total":
        return float(record.total_tokens)
    if metric == "billable":
        return float(record.billable_tokens)
    if metric == "cost":
        return float(record.cost_usd)
    return (
        record.input_tokens
        + record.output_tokens
        + record.cache_write_5m_tokens * pricing.CACHE_WRITE_5M_MULTIPLIER
        + record.cache_write_1h_tokens * pricing.CACHE_WRITE_1H_MULTIPLIER
        + record.cache_read_tokens * pricing.CACHE_READ_MULTIPLIER
    )


class Aggregator:
    """Thread-safe store of usage records with windowed rollups."""

    def __init__(self, retention_days: int = 90) -> None:
        self._lock = threading.RLock()
        self._records: list[UsageRecord] = []
        self._keys: set[str] = set()
        self._timestamps: list[datetime] = []
        self.retention_days = retention_days

    # ------------------------------------------------------------------ write

    def add(self, records: Iterable[UsageRecord]) -> int:
        """Insert records, ignoring ones already present. Returns count added."""
        added = 0
        with self._lock:
            for record in records:
                if record.dedup_key in self._keys:
                    continue
                self._keys.add(record.dedup_key)
                index = bisect.bisect_right(self._timestamps, record.timestamp)
                self._timestamps.insert(index, record.timestamp)
                self._records.insert(index, record)
                added += 1
            if added:
                self._prune_locked()
        return added

    def clear(self) -> None:
        with self._lock:
            self._records.clear()
            self._keys.clear()
            self._timestamps.clear()

    def _prune_locked(self) -> None:
        if not self.retention_days:
            return
        cutoff = _utcnow() - timedelta(days=self.retention_days)
        drop = bisect.bisect_left(self._timestamps, cutoff)
        if drop <= 0:
            return
        for record in self._records[:drop]:
            self._keys.discard(record.dedup_key)
        del self._records[:drop]
        del self._timestamps[:drop]

    # ------------------------------------------------------------------- read

    def __len__(self) -> int:
        with self._lock:
            return len(self._records)

    def slice(
        self,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> Sequence[UsageRecord]:
        with self._lock:
            start = 0 if since is None else bisect.bisect_left(self._timestamps, since)
            end = (
                len(self._records)
                if until is None
                else bisect.bisect_right(self._timestamps, until)
            )
            return tuple(self._records[start:end])

    def totals(
        self,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> Totals:
        result = Totals()
        for record in self.slice(since, until):
            result.add(record)
        return result

    def breakdown(
        self,
        key: Callable[[UsageRecord], str],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> dict[str, Totals]:
        grouped: dict[str, Totals] = {}
        for record in self.slice(since, until):
            grouped.setdefault(key(record), Totals()).add(record)
        return dict(
            sorted(grouped.items(), key=lambda kv: kv[1].total_tokens, reverse=True)
        )

    def timeline(
        self,
        now: datetime | None = None,
        span: timedelta = timedelta(hours=24),
        buckets: int = 48,
        metric: str = "weighted",
    ) -> list[float]:
        """Bucket recent usage into equal slices, oldest first.

        Feeds the activity chart. The final bucket is the one in progress.
        """
        buckets = max(1, int(buckets))
        now = now or _utcnow()
        start = now - span
        width = span / buckets
        series = [0.0] * buckets

        for record in self.slice(start, now):
            offset = (record.timestamp - start) / width
            index = min(buckets - 1, max(0, int(offset)))
            series[index] += record_metric(record, metric)

        return series

    def peak_window(
        self,
        window: timedelta = FIVE_HOURS,
        metric: str = "weighted",
    ) -> tuple[float, datetime | None]:
        """Highest value this metric ever reached over a rolling ``window``.

        Two pointers over the timestamp-ordered records, so this is O(n) rather
        than O(n * window size). Used to calibrate a limit from observed
        behaviour instead of guessing one.
        """
        with self._lock:
            records = self._records
            if not records:
                return 0.0, None

            best = 0.0
            best_at: datetime | None = None
            running = 0.0
            start = 0

            for end, record in enumerate(records):
                running += record_metric(record, metric)
                cutoff = record.timestamp - window
                while start <= end and records[start].timestamp <= cutoff:
                    running -= record_metric(records[start], metric)
                    start += 1
                if running > best:
                    best = running
                    best_at = record.timestamp

            return best, best_at

    # --------------------------------------------------------------- snapshot

    def snapshot(
        self,
        now: datetime | None = None,
        scope: str = "today",
        tz: timezone | None = None,
    ) -> Snapshot:
        now = now or _utcnow()
        with self._lock:
            window_5h = self.totals(now - FIVE_HOURS)
            window_7d = self.totals(now - SEVEN_DAYS)
            today_start = local_day_start(now, tz)
            today = self.totals(today_start)
            all_time = self.totals()

            scope_since, scope_label = resolve_scope(scope, now, tz)
            scope_totals = self.totals(scope_since)
            by_model = self.breakdown(lambda r: r.model or "(unknown)", scope_since)
            by_project = self.breakdown(lambda r: r.project or "(unknown)", scope_since)

            session_id = ""
            session_totals = Totals()
            last_activity = self._timestamps[-1] if self._timestamps else None
            if self._records:
                session_id = self._records[-1].session_id
                if session_id:
                    for record in self._records:
                        if record.session_id == session_id:
                            session_totals.add(record)

        return Snapshot(
            generated_at=now,
            window_5h=window_5h,
            window_7d=window_7d,
            today=today,
            all_time=all_time,
            by_model=by_model,
            by_project=by_project,
            active_session_id=session_id,
            active_session=session_totals,
            last_activity=last_activity,
            scope_label=scope_label,
            scope_totals=scope_totals,
        )


SCOPES: tuple[str, ...] = ("5h", "today", "7d", "30d", "all")

_SCOPE_LABELS = {
    "5h": "Last 5 hours",
    "today": "Today",
    "7d": "Last 7 days",
    "30d": "Last 30 days",
    "all": "All time",
}


def resolve_scope(
    scope: str,
    now: datetime,
    tz: timezone | None = None,
) -> tuple[datetime | None, str]:
    """Map a scope name to a start timestamp and a display label."""
    scope = (scope or "today").lower()
    if scope == "5h":
        return now - FIVE_HOURS, _SCOPE_LABELS["5h"]
    if scope == "7d":
        return now - SEVEN_DAYS, _SCOPE_LABELS["7d"]
    if scope == "30d":
        return now - timedelta(days=30), _SCOPE_LABELS["30d"]
    if scope == "all":
        return None, _SCOPE_LABELS["all"]
    return local_day_start(now, tz), _SCOPE_LABELS["today"]


def local_day_start(now: datetime, tz: timezone | None = None) -> datetime:
    """Midnight of ``now``'s local day, expressed in UTC.

    "Today" should mean the user's day, not UTC's -- in WIB (UTC+7) those differ
    for seven hours of every day.
    """
    local = now.astimezone(tz) if tz else now.astimezone()
    midnight = local.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight.astimezone(timezone.utc)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


__all__ = [
    "FIVE_HOURS",
    "METRICS",
    "SCOPES",
    "SEVEN_DAYS",
    "Aggregator",
    "Snapshot",
    "Totals",
    "local_day_start",
    "metric_label",
    "metric_value",
    "record_metric",
    "resolve_scope",
]
