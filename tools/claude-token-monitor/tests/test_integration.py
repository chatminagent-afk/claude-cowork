"""End-to-end coverage of the collection pipeline.

Exercises scanner -> aggregator -> snapshot -> tooltip against a transcript tree
that grows the way a live Claude Code session grows, without needing a display.
"""

import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from claude_token_monitor.aggregate import Aggregator, metric_value
from claude_token_monitor.config import Config
from claude_token_monitor.report import render, suggest_limits
from claude_token_monitor.scanner import TranscriptScanner
from claude_token_monitor.tray import build_tooltip
from tests.helpers import append_transcript, assistant_record, write_transcript


class LiveSessionTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.now = datetime.now(timezone.utc)
        self.scanner = TranscriptScanner(root=self.root, bootstrap_days=None)
        self.aggregator = Aggregator(retention_days=90)

    def tick(self) -> int:
        return self.aggregator.add(self.scanner.poll())

    def path(self, *parts) -> Path:
        return self.root.joinpath(*parts)

    def test_usage_accumulates_across_polls(self):
        session = self.path("projA", "live.jsonl")
        write_transcript(
            session,
            [
                assistant_record(
                    message_id="m1",
                    request_id="r1",
                    timestamp=self.now - timedelta(minutes=3),
                    input_tokens=100,
                    output_tokens=200,
                )
            ],
        )
        self.assertEqual(self.tick(), 1)

        snapshot = self.aggregator.snapshot(now=self.now, scope="all")
        self.assertEqual(snapshot.window_5h.total_tokens, 300)
        self.assertEqual(snapshot.window_5h.requests, 1)

        append_transcript(
            session,
            [
                assistant_record(
                    message_id="m2",
                    request_id="r2",
                    timestamp=self.now - timedelta(minutes=1),
                    input_tokens=50,
                    output_tokens=25,
                    cache_read=1000,
                )
            ],
        )
        self.assertEqual(self.tick(), 1)

        snapshot = self.aggregator.snapshot(now=self.now, scope="all")
        self.assertEqual(snapshot.window_5h.requests, 2)
        self.assertEqual(snapshot.window_5h.total_tokens, 1375)
        self.assertEqual(snapshot.window_5h.cache_read_tokens, 1000)

    def test_idle_polls_add_nothing(self):
        write_transcript(self.path("p", "s.jsonl"), [assistant_record()])
        self.tick()
        for _ in range(5):
            self.assertEqual(self.tick(), 0)
        self.assertEqual(len(self.aggregator), 1)

    def test_resumed_session_does_not_double_count(self):
        """A resumed session copies prior turns into a new file.

        This is the single biggest source of overcounting in the real data --
        without dedup the totals roughly double.
        """
        original = [
            assistant_record(
                message_id=f"m{i}",
                request_id=f"r{i}",
                timestamp=self.now - timedelta(minutes=30 - i),
                input_tokens=100,
            )
            for i in range(5)
        ]
        write_transcript(self.path("projA", "session-1.jsonl"), original)
        self.tick()
        self.assertEqual(len(self.aggregator), 5)

        # Resume: everything replayed into a new file, plus one new turn.
        resumed = original + [
            assistant_record(
                message_id="m-new",
                request_id="r-new",
                timestamp=self.now - timedelta(minutes=1),
                input_tokens=100,
            )
        ]
        write_transcript(self.path("projA", "session-2.jsonl"), resumed)

        self.assertEqual(self.tick(), 1)
        self.assertEqual(len(self.aggregator), 6)
        self.assertEqual(self.scanner.last_stats.duplicates, 5)

    def test_subagent_usage_attributed_to_parent_project(self):
        write_transcript(
            self.path("projA", "main.jsonl"),
            [assistant_record(message_id="m1", request_id="r1", input_tokens=10)],
        )
        write_transcript(
            self.path("projA", "subagents", "agent-x.jsonl"),
            [
                assistant_record(
                    message_id="m2",
                    request_id="r2",
                    is_sidechain=True,
                    input_tokens=90,
                )
            ],
        )
        self.tick()
        snapshot = self.aggregator.snapshot(now=self.now, scope="all")
        self.assertEqual(list(snapshot.by_project), ["projA"])
        self.assertEqual(snapshot.by_project["projA"].input_tokens, 100)

    def test_multiple_projects_and_models_split_correctly(self):
        write_transcript(
            self.path("projA", "s.jsonl"),
            [
                assistant_record(
                    message_id="a",
                    request_id="a",
                    model="claude-opus-5",
                    input_tokens=1000,
                    output_tokens=0,
                )
            ],
        )
        write_transcript(
            self.path("projB", "s.jsonl"),
            [
                assistant_record(
                    message_id="b",
                    request_id="b",
                    model="claude-haiku-4-5-20251001",
                    input_tokens=500,
                    output_tokens=0,
                )
            ],
        )
        self.tick()
        snapshot = self.aggregator.snapshot(now=self.now, scope="all")

        self.assertEqual(set(snapshot.by_project), {"projA", "projB"})
        self.assertEqual(set(snapshot.by_model), {"claude-opus-5", "claude-haiku-4-5"})
        self.assertAlmostEqual(
            snapshot.by_model["claude-opus-5"].cost_usd, 1000 * 5 / 1e6, places=9
        )
        self.assertAlmostEqual(
            snapshot.by_model["claude-haiku-4-5"].cost_usd, 500 * 1 / 1e6, places=9
        )

    def test_records_ageing_out_of_the_window(self):
        write_transcript(
            self.path("p", "s.jsonl"),
            [
                assistant_record(
                    message_id="old",
                    request_id="old",
                    timestamp=self.now - timedelta(hours=6),
                    input_tokens=999,
                ),
                assistant_record(
                    message_id="new",
                    request_id="new",
                    timestamp=self.now - timedelta(minutes=2),
                    input_tokens=1,
                ),
            ],
        )
        self.tick()
        snapshot = self.aggregator.snapshot(now=self.now, scope="all")
        self.assertEqual(snapshot.window_5h.input_tokens, 1)
        self.assertEqual(snapshot.all_time.input_tokens, 1000)

    def test_pipeline_feeds_tooltip_and_report(self):
        write_transcript(
            self.path("p", "s.jsonl"),
            [
                assistant_record(
                    message_id="m",
                    request_id="r",
                    timestamp=self.now - timedelta(minutes=2),
                    input_tokens=1000,
                    output_tokens=500,
                    cache_read=20000,
                )
            ],
        )
        self.tick()
        snapshot = self.aggregator.snapshot(now=self.now, scope="today")
        config = Config()

        tooltip = build_tooltip(snapshot, config)
        self.assertIn("5h", tooltip)

        text = render(snapshot, config, self.scanner.last_stats)
        self.assertIn("ROLLING WINDOWS", text)
        self.assertIn("claude-opus-5", text)
        self.assertIn("SCAN", text)

    def test_calibration_reflects_ingested_data(self):
        write_transcript(
            self.path("p", "s.jsonl"),
            [
                assistant_record(
                    message_id=f"m{i}",
                    request_id=f"r{i}",
                    timestamp=self.now - timedelta(minutes=i),
                    input_tokens=1000,
                    output_tokens=0,
                )
                for i in range(4)
            ],
        )
        self.tick()
        peak, suggested, at = suggest_limits(self.aggregator, "total")["5h"]
        self.assertEqual(peak, 4000)
        self.assertGreater(suggested, peak)
        self.assertIsNotNone(at)

    def test_gauge_metric_discounts_cache_reads(self):
        write_transcript(
            self.path("p", "s.jsonl"),
            [
                assistant_record(
                    message_id="m",
                    request_id="r",
                    timestamp=self.now,
                    input_tokens=0,
                    output_tokens=0,
                    cache_read=1_000_000,
                )
            ],
        )
        self.tick()
        totals = self.aggregator.snapshot(now=self.now, scope="all").window_5h
        self.assertEqual(metric_value(totals, "total"), 1_000_000)
        self.assertAlmostEqual(metric_value(totals, "weighted"), 100_000)


class ConcurrentPollingTests(unittest.TestCase):
    """The poller writes while the UI thread reads snapshots."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_polling_while_snapshotting(self):
        now = datetime.now(timezone.utc)
        path = self.root / "p" / "s.jsonl"
        write_transcript(
            path,
            [assistant_record(message_id="m0", request_id="r0", timestamp=now)],
        )

        scanner = TranscriptScanner(root=self.root, bootstrap_days=None)
        aggregator = Aggregator(retention_days=90)
        errors: list[BaseException] = []
        stop = threading.Event()

        def poller():
            try:
                while not stop.is_set():
                    aggregator.add(scanner.poll())
            except BaseException as exc:  # pragma: no cover
                errors.append(exc)

        def reader():
            try:
                for _ in range(150):
                    aggregator.snapshot(now=now, scope="all")
            except BaseException as exc:  # pragma: no cover
                errors.append(exc)

        thread_poll = threading.Thread(target=poller)
        thread_read = threading.Thread(target=reader)
        thread_poll.start()
        thread_read.start()

        for i in range(1, 40):
            append_transcript(
                path,
                [
                    assistant_record(
                        message_id=f"m{i}",
                        request_id=f"r{i}",
                        timestamp=now,
                        input_tokens=10,
                    )
                ],
            )

        thread_read.join()
        stop.set()
        thread_poll.join()

        # Drain anything appended after the poller's last sweep.
        aggregator.add(scanner.poll())

        self.assertEqual(errors, [])
        self.assertEqual(len(aggregator), 40)


if __name__ == "__main__":
    unittest.main()
