import unittest
from datetime import datetime, timedelta, timezone

from claude_token_monitor.aggregate import (
    FIVE_HOURS,
    Aggregator,
    Totals,
    local_day_start,
    metric_label,
    metric_value,
    record_metric,
    resolve_scope,
)
from claude_token_monitor.parser import UsageRecord

NOW = datetime(2026, 7, 20, 18, 0, 0, tzinfo=timezone.utc)


def make_record(
    key: str = "k",
    minutes_ago: float = 0,
    model: str = "claude-opus-5",
    project: str = "projA",
    session: str = "s1",
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read: int = 0,
    cache_5m: int = 0,
    cache_1h: int = 0,
    cost: float = 0.0,
    now: datetime = NOW,
) -> UsageRecord:
    return UsageRecord(
        dedup_key=key,
        timestamp=now - timedelta(minutes=minutes_ago),
        model=model,
        raw_model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_tokens=cache_read,
        cache_write_5m_tokens=cache_5m,
        cache_write_1h_tokens=cache_1h,
        session_id=session,
        project=project,
        cwd="",
        is_sidechain=False,
        speed="standard",
        cost_usd=cost,
    )


class TotalsTests(unittest.TestCase):
    def test_empty_totals(self):
        totals = Totals()
        self.assertEqual(totals.total_tokens, 0)
        self.assertEqual(totals.billable_tokens, 0)
        self.assertEqual(totals.weighted_tokens, 0)
        self.assertIsNone(totals.first_seen)

    def test_add_accumulates(self):
        totals = Totals()
        totals.add(make_record(input_tokens=10, output_tokens=5, cost=1.0))
        totals.add(make_record(input_tokens=1, output_tokens=2, cost=0.5))
        self.assertEqual(totals.requests, 2)
        self.assertEqual(totals.input_tokens, 11)
        self.assertEqual(totals.output_tokens, 7)
        self.assertAlmostEqual(totals.cost_usd, 1.5)

    def test_total_and_billable_differ_by_cache_reads(self):
        totals = Totals()
        totals.add(
            make_record(input_tokens=1, output_tokens=2, cache_read=100, cache_5m=4)
        )
        self.assertEqual(totals.total_tokens, 107)
        self.assertEqual(totals.billable_tokens, 7)

    def test_weighted_tokens_apply_billing_multipliers(self):
        totals = Totals()
        totals.add(
            make_record(
                input_tokens=100,
                output_tokens=200,
                cache_read=1000,
                cache_5m=400,
                cache_1h=50,
            )
        )
        expected = 100 + 200 + 400 * 1.25 + 50 * 2.0 + 1000 * 0.1
        self.assertAlmostEqual(totals.weighted_tokens, expected)

    def test_first_and_last_seen_track_extremes(self):
        totals = Totals()
        totals.add(make_record(key="a", minutes_ago=10))
        totals.add(make_record(key="b", minutes_ago=60))
        totals.add(make_record(key="c", minutes_ago=30))
        self.assertEqual(totals.first_seen, NOW - timedelta(minutes=60))
        self.assertEqual(totals.last_seen, NOW - timedelta(minutes=10))


class MetricTests(unittest.TestCase):
    def setUp(self):
        self.totals = Totals()
        self.totals.add(
            make_record(
                input_tokens=100,
                output_tokens=200,
                cache_read=1000,
                cache_5m=400,
                cache_1h=50,
                cost=3.5,
            )
        )

    def test_metric_selection(self):
        self.assertEqual(metric_value(self.totals, "total"), 1750)
        self.assertEqual(metric_value(self.totals, "billable"), 750)
        self.assertAlmostEqual(metric_value(self.totals, "cost"), 3.5)
        self.assertAlmostEqual(
            metric_value(self.totals, "weighted"), 100 + 200 + 500 + 100 + 100
        )

    def test_unknown_metric_falls_back_to_weighted(self):
        self.assertEqual(
            metric_value(self.totals, "nonsense"),
            metric_value(self.totals, "weighted"),
        )

    def test_record_metric_matches_totals_metric(self):
        record = make_record(
            input_tokens=7, output_tokens=9, cache_read=11, cache_5m=13, cache_1h=17
        )
        totals = Totals()
        totals.add(record)
        for metric in ("weighted", "total", "billable", "cost"):
            self.assertAlmostEqual(
                record_metric(record, metric), metric_value(totals, metric), places=9
            )

    def test_metric_labels_exist(self):
        for metric in ("weighted", "total", "billable", "cost"):
            self.assertTrue(metric_label(metric))


class AggregatorTests(unittest.TestCase):
    def setUp(self):
        self.agg = Aggregator(retention_days=365)

    def test_add_returns_count_and_dedupes(self):
        first = make_record(key="a")
        self.assertEqual(self.agg.add([first]), 1)
        self.assertEqual(self.agg.add([first]), 0)
        self.assertEqual(len(self.agg), 1)

    def test_records_kept_in_timestamp_order(self):
        self.agg.add(
            [
                make_record(key="late", minutes_ago=0),
                make_record(key="early", minutes_ago=100),
                make_record(key="mid", minutes_ago=50),
            ]
        )
        keys = [r.dedup_key for r in self.agg.slice()]
        self.assertEqual(keys, ["early", "mid", "late"])

    def test_slice_since_is_inclusive_of_the_boundary(self):
        self.agg.add([make_record(key="on-boundary", minutes_ago=300)])  # exactly 5h
        window = self.agg.slice(NOW - FIVE_HOURS)
        self.assertEqual(len(window), 1)

    def test_slice_excludes_older_than_since(self):
        self.agg.add([make_record(key="old", minutes_ago=301)])
        self.assertEqual(len(self.agg.slice(NOW - FIVE_HOURS)), 0)

    def test_totals_over_window(self):
        self.agg.add(
            [
                make_record(key="in", minutes_ago=10, input_tokens=100, cost=1.0),
                make_record(key="out", minutes_ago=600, input_tokens=999, cost=9.0),
            ]
        )
        totals = self.agg.totals(NOW - FIVE_HOURS)
        self.assertEqual(totals.requests, 1)
        self.assertEqual(totals.input_tokens, 100)
        self.assertAlmostEqual(totals.cost_usd, 1.0)

    def test_breakdown_groups_and_sorts_by_tokens(self):
        self.agg.add(
            [
                make_record(key="a", model="claude-haiku-4-5", input_tokens=10),
                make_record(key="b", model="claude-opus-5", input_tokens=500),
                make_record(key="c", model="claude-opus-5", input_tokens=1),
            ]
        )
        grouped = self.agg.breakdown(lambda r: r.model)
        self.assertEqual(list(grouped), ["claude-opus-5", "claude-haiku-4-5"])
        self.assertEqual(grouped["claude-opus-5"].requests, 2)
        self.assertEqual(grouped["claude-opus-5"].input_tokens, 501)

    def test_clear_empties_everything(self):
        self.agg.add([make_record(key="a")])
        self.agg.clear()
        self.assertEqual(len(self.agg), 0)
        self.assertEqual(self.agg.add([make_record(key="a")]), 1)

    def test_retention_prunes_old_records(self):
        agg = Aggregator(retention_days=1)
        now = datetime.now(timezone.utc)
        agg.add(
            [
                make_record(key="old", minutes_ago=60 * 48, now=now),
                make_record(key="new", minutes_ago=1, now=now),
            ]
        )
        keys = [r.dedup_key for r in agg.slice()]
        self.assertEqual(keys, ["new"])

    def test_pruned_key_can_be_readded(self):
        agg = Aggregator(retention_days=1)
        now = datetime.now(timezone.utc)
        agg.add([make_record(key="old", minutes_ago=60 * 48, now=now)])
        self.assertEqual(len(agg), 0)
        self.assertEqual(agg.add([make_record(key="old", minutes_ago=1, now=now)]), 1)


class PeakWindowTests(unittest.TestCase):
    def test_no_records(self):
        peak, at = Aggregator().peak_window(FIVE_HOURS, "total")
        self.assertEqual(peak, 0.0)
        self.assertIsNone(at)

    def test_peak_is_the_densest_window(self):
        agg = Aggregator(retention_days=3650)
        # Three calls inside one hour, then a lone call much later.
        agg.add(
            [
                make_record(key="a", minutes_ago=600, input_tokens=100),
                make_record(key="b", minutes_ago=580, input_tokens=100),
                make_record(key="c", minutes_ago=560, input_tokens=100),
                make_record(key="d", minutes_ago=10, input_tokens=150),
            ]
        )
        peak, at = agg.peak_window(FIVE_HOURS, "total")
        self.assertEqual(peak, 300)
        self.assertEqual(at, NOW - timedelta(minutes=560))

    def test_records_outside_the_window_do_not_accumulate(self):
        agg = Aggregator(retention_days=3650)
        agg.add(
            [
                make_record(key=f"k{i}", minutes_ago=i * 360, input_tokens=100)
                for i in range(10)
            ]
        )
        peak, _at = agg.peak_window(FIVE_HOURS, "total")
        self.assertEqual(peak, 100)

    def test_peak_uses_the_requested_metric(self):
        agg = Aggregator(retention_days=3650)
        agg.add([make_record(key="a", cache_read=1000)])
        self.assertEqual(agg.peak_window(FIVE_HOURS, "total")[0], 1000)
        self.assertAlmostEqual(agg.peak_window(FIVE_HOURS, "weighted")[0], 100.0)
        self.assertEqual(agg.peak_window(FIVE_HOURS, "billable")[0], 0)


class ScopeTests(unittest.TestCase):
    def test_named_scopes(self):
        self.assertEqual(resolve_scope("5h", NOW)[0], NOW - FIVE_HOURS)
        self.assertEqual(resolve_scope("7d", NOW)[0], NOW - timedelta(days=7))
        self.assertEqual(resolve_scope("30d", NOW)[0], NOW - timedelta(days=30))
        self.assertIsNone(resolve_scope("all", NOW)[0])

    def test_unknown_scope_defaults_to_today(self):
        since, label = resolve_scope("bogus", NOW)
        self.assertEqual(label, "Today")
        self.assertEqual(since, local_day_start(NOW))

    def test_local_day_start_respects_timezone(self):
        wib = timezone(timedelta(hours=7))
        # 18:00 UTC on the 20th is 01:00 on the 21st in WIB, so the local day
        # started at 17:00 UTC on the 20th.
        self.assertEqual(
            local_day_start(NOW, wib),
            datetime(2026, 7, 20, 17, 0, tzinfo=timezone.utc),
        )

    def test_local_day_start_is_utc_aware(self):
        self.assertEqual(local_day_start(NOW).tzinfo, timezone.utc)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.agg = Aggregator(retention_days=3650)
        self.agg.add(
            [
                make_record(key="recent", minutes_ago=5, input_tokens=100, cost=1.0),
                make_record(
                    key="older",
                    minutes_ago=60 * 24 * 3,
                    model="claude-sonnet-5",
                    project="projB",
                    session="s2",
                    input_tokens=50,
                    cost=0.5,
                ),
            ]
        )

    def test_windows_populated(self):
        snap = self.agg.snapshot(now=NOW, scope="all")
        self.assertEqual(snap.window_5h.requests, 1)
        self.assertEqual(snap.window_7d.requests, 2)
        self.assertEqual(snap.all_time.requests, 2)
        self.assertEqual(snap.generated_at, NOW)

    def test_breakdowns_follow_the_scope(self):
        all_scope = self.agg.snapshot(now=NOW, scope="all")
        self.assertEqual(len(all_scope.by_model), 2)
        five_h = self.agg.snapshot(now=NOW, scope="5h")
        self.assertEqual(list(five_h.by_model), ["claude-opus-5"])
        self.assertEqual(five_h.scope_label, "Last 5 hours")

    def test_active_session_is_the_most_recent(self):
        snap = self.agg.snapshot(now=NOW, scope="all")
        self.assertEqual(snap.active_session_id, "s1")
        self.assertEqual(snap.active_session.requests, 1)

    def test_last_activity_reported(self):
        snap = self.agg.snapshot(now=NOW, scope="all")
        self.assertEqual(snap.last_activity, NOW - timedelta(minutes=5))

    def test_reset_countdown(self):
        snap = self.agg.snapshot(now=NOW, scope="all")
        self.assertEqual(
            snap.window_5h_resets_in, timedelta(hours=5) - timedelta(minutes=5)
        )

    def test_reset_countdown_is_none_without_window_data(self):
        snap = Aggregator().snapshot(now=NOW)
        self.assertIsNone(snap.window_5h_resets_in)

    def test_empty_aggregator_snapshot_is_safe(self):
        snap = Aggregator().snapshot(now=NOW)
        self.assertEqual(snap.all_time.requests, 0)
        self.assertEqual(snap.by_model, {})
        self.assertEqual(snap.active_session_id, "")


class ConcurrencyTests(unittest.TestCase):
    def test_concurrent_add_and_snapshot(self):
        import threading

        agg = Aggregator(retention_days=3650)
        errors: list[BaseException] = []

        def writer(offset: int) -> None:
            try:
                for i in range(200):
                    agg.add([make_record(key=f"{offset}-{i}", minutes_ago=i % 60)])
            except BaseException as exc:  # pragma: no cover - failure path
                errors.append(exc)

        def reader() -> None:
            try:
                for _ in range(200):
                    agg.snapshot(now=NOW, scope="all")
            except BaseException as exc:  # pragma: no cover - failure path
                errors.append(exc)

        threads = [threading.Thread(target=writer, args=(n,)) for n in range(3)]
        threads.append(threading.Thread(target=reader))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(errors, [])
        self.assertEqual(len(agg), 600)


if __name__ == "__main__":
    unittest.main()
