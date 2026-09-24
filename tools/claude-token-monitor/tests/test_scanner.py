import os
import tempfile
import time
import unittest
from pathlib import Path

from claude_token_monitor.scanner import TranscriptScanner, decode_project_name
from tests.helpers import (
    BASE_TIME,
    append_transcript,
    assistant_record,
    line,
    minutes,
    write_transcript,
)


class ScannerTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def scanner(self, **kwargs) -> TranscriptScanner:
        kwargs.setdefault("bootstrap_days", None)
        return TranscriptScanner(root=self.root, **kwargs)

    def path(self, *parts) -> Path:
        return self.root.joinpath(*parts)


class BasicScanTests(ScannerTestCase):
    def test_empty_root_yields_nothing(self):
        self.assertEqual(self.scanner().poll(), [])

    def test_missing_root_does_not_raise(self):
        scanner = TranscriptScanner(root=self.root / "nope", bootstrap_days=None)
        self.assertEqual(scanner.poll(), [])

    def test_reads_records(self):
        write_transcript(
            self.path("projA", "s1.jsonl"),
            [
                assistant_record(message_id="m1", request_id="r1"),
                assistant_record(message_id="m2", request_id="r2"),
            ],
        )
        records = self.scanner().poll()
        self.assertEqual(len(records), 2)
        self.assertEqual({r.project for r in records}, {"projA"})

    def test_ignores_non_jsonl_files(self):
        write_transcript(self.path("projA", "s1.jsonl"), [assistant_record()])
        (self.root / "projA" / "notes.txt").write_text("hello", encoding="utf-8")
        self.assertEqual(len(self.scanner().poll()), 1)

    def test_ignores_lines_without_usage(self):
        path = self.path("projA", "s1.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            '{"type":"user","content":"hi"}\n'
            '{"type":"custom-title","title":"x"}\n'
            + line(assistant_record())
            + "\n",
            encoding="utf-8",
        )
        self.assertEqual(len(self.scanner().poll()), 1)


class IncrementalTests(ScannerTestCase):
    def test_second_poll_returns_only_new_records(self):
        path = self.path("projA", "s1.jsonl")
        write_transcript(path, [assistant_record(message_id="m1", request_id="r1")])
        scanner = self.scanner()
        self.assertEqual(len(scanner.poll()), 1)
        self.assertEqual(scanner.poll(), [])

        append_transcript(path, [assistant_record(message_id="m2", request_id="r2")])
        second = scanner.poll()
        self.assertEqual(len(second), 1)
        self.assertEqual(second[0].dedup_key, "m2|r2")

    def test_only_new_bytes_are_read(self):
        path = self.path("projA", "s1.jsonl")
        write_transcript(path, [assistant_record(message_id=f"m{i}", request_id=f"r{i}") for i in range(20)])
        scanner = self.scanner()
        scanner.poll()
        first_bytes = scanner.last_stats.bytes_read
        append_transcript(path, [assistant_record(message_id="m99", request_id="r99")])
        scanner.poll()
        self.assertLess(scanner.last_stats.bytes_read, first_bytes)
        self.assertGreater(scanner.last_stats.bytes_read, 0)

    def test_partial_trailing_line_is_not_consumed(self):
        path = self.path("projA", "s1.jsonl")
        write_transcript(path, [assistant_record(message_id="m1", request_id="r1")])
        scanner = self.scanner()
        scanner.poll()

        # A record still being written: no terminating newline yet.
        append_transcript(
            path,
            [assistant_record(message_id="m2", request_id="r2")],
            terminate=False,
        )
        self.assertEqual(scanner.poll(), [], "partial line must not be parsed")

        # Writer finishes the line.
        with open(path, "a", encoding="utf-8", newline="") as handle:
            handle.write("\n")
        records = scanner.poll()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].dedup_key, "m2|r2")

    def test_file_with_no_newline_at_all_yields_nothing_then_everything(self):
        path = self.path("projA", "s1.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(line(assistant_record()), encoding="utf-8")
        scanner = self.scanner()
        self.assertEqual(scanner.poll(), [])
        with open(path, "a", encoding="utf-8", newline="") as handle:
            handle.write("\n")
        self.assertEqual(len(scanner.poll()), 1)

    def test_truncated_file_is_reread_from_the_start(self):
        path = self.path("projA", "s1.jsonl")
        write_transcript(
            path, [assistant_record(message_id=f"m{i}", request_id=f"r{i}") for i in range(5)]
        )
        scanner = self.scanner()
        self.assertEqual(len(scanner.poll()), 5)

        # Rotated: same name, shorter, entirely new content.
        write_transcript(path, [assistant_record(message_id="new", request_id="new")])
        records = scanner.poll()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].dedup_key, "new|new")

    def test_deleted_file_is_forgotten(self):
        path = self.path("projA", "s1.jsonl")
        write_transcript(path, [assistant_record()])
        scanner = self.scanner()
        scanner.poll()
        os.unlink(path)
        scanner.poll()
        self.assertEqual(scanner.last_stats.files_seen, 0)

    def test_reset_forces_full_reread(self):
        path = self.path("projA", "s1.jsonl")
        write_transcript(path, [assistant_record()])
        scanner = self.scanner()
        self.assertEqual(len(scanner.poll()), 1)
        scanner.reset()
        self.assertEqual(len(scanner.poll()), 1)


class DeduplicationTests(ScannerTestCase):
    def test_same_request_in_two_files_counted_once(self):
        record = assistant_record(message_id="m1", request_id="r1")
        write_transcript(self.path("projA", "s1.jsonl"), [record])
        write_transcript(self.path("projA", "s2.jsonl"), [record])
        scanner = self.scanner()
        records = scanner.poll()
        self.assertEqual(len(records), 1)
        self.assertEqual(scanner.last_stats.duplicates, 1)

    def test_duplicate_within_one_file_counted_once(self):
        record = assistant_record(message_id="m1", request_id="r1")
        write_transcript(self.path("projA", "s1.jsonl"), [record, record])
        self.assertEqual(len(self.scanner().poll()), 1)


class SidechainTests(ScannerTestCase):
    def setUp(self):
        super().setUp()
        write_transcript(
            self.path("projA", "s1.jsonl"),
            [assistant_record(message_id="m1", request_id="r1")],
        )
        write_transcript(
            self.path("projA", "subagents", "agent-1.jsonl"),
            [assistant_record(message_id="m2", request_id="r2", is_sidechain=True)],
        )

    def test_included_by_default(self):
        self.assertEqual(len(self.scanner().poll()), 2)

    def test_can_be_excluded(self):
        records = self.scanner(include_sidechains=False).poll()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].dedup_key, "m1|r1")

    def test_subagent_file_keeps_parent_project(self):
        records = self.scanner().poll()
        self.assertEqual({r.project for r in records}, {"projA"})


class BootstrapTests(ScannerTestCase):
    def test_old_files_skipped_on_first_sweep(self):
        old = self.path("projA", "old.jsonl")
        new = self.path("projA", "new.jsonl")
        write_transcript(old, [assistant_record(message_id="old", request_id="old")])
        write_transcript(new, [assistant_record(message_id="new", request_id="new")])

        ancient = time.time() - 60 * 86400
        os.utime(old, (ancient, ancient))

        scanner = self.scanner(bootstrap_days=30)
        records = scanner.poll()
        self.assertEqual([r.dedup_key for r in records], ["new|new"])

    def test_skipped_file_is_not_reread_later(self):
        old = self.path("projA", "old.jsonl")
        write_transcript(old, [assistant_record(message_id="old", request_id="old")])
        ancient = time.time() - 60 * 86400
        os.utime(old, (ancient, ancient))

        scanner = self.scanner(bootstrap_days=30)
        scanner.poll()
        self.assertEqual(scanner.poll(), [])

    def test_appends_to_old_file_are_still_picked_up(self):
        old = self.path("projA", "old.jsonl")
        write_transcript(old, [assistant_record(message_id="old", request_id="old")])
        ancient = time.time() - 60 * 86400
        os.utime(old, (ancient, ancient))

        scanner = self.scanner(bootstrap_days=30)
        scanner.poll()
        append_transcript(old, [assistant_record(message_id="fresh", request_id="fresh")])
        records = scanner.poll()
        self.assertEqual([r.dedup_key for r in records], ["fresh|fresh"])

    def test_bootstrap_disabled_reads_everything(self):
        old = self.path("projA", "old.jsonl")
        write_transcript(old, [assistant_record(message_id="old", request_id="old")])
        ancient = time.time() - 60 * 86400
        os.utime(old, (ancient, ancient))
        self.assertEqual(len(self.scanner(bootstrap_days=None).poll()), 1)


class StatsTests(ScannerTestCase):
    def test_stats_are_reported(self):
        write_transcript(
            self.path("projA", "s1.jsonl"),
            [
                assistant_record(message_id="m1", request_id="r1"),
                assistant_record(message_id="m1", request_id="r1"),
            ],
        )
        scanner = self.scanner()
        scanner.poll()
        stats = scanner.last_stats
        self.assertEqual(stats.files_seen, 1)
        self.assertEqual(stats.files_read, 1)
        self.assertEqual(stats.records, 1)
        self.assertEqual(stats.duplicates, 1)
        self.assertEqual(stats.errors, 0)
        self.assertGreater(stats.bytes_read, 0)
        self.assertGreaterEqual(stats.elapsed_s, 0.0)


class ProjectNameTests(unittest.TestCase):
    def test_decodes_encoded_path(self):
        self.assertEqual(
            decode_project_name("D--Documents-Claude-Cowork-Persada-Cisoka-Residence"),
            "Persada Cisoka Residence",
        )

    def test_workspace_root_keeps_a_name(self):
        self.assertEqual(
            decode_project_name("D--Documents-Claude-Cowork"), "Claude Cowork"
        )

    def test_unknown_shape_passes_through(self):
        self.assertEqual(decode_project_name("some-project"), "some project")

    def test_empty_is_labelled(self):
        self.assertEqual(decode_project_name(""), "(unknown)")


if __name__ == "__main__":
    unittest.main()
