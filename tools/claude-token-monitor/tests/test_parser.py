import json
import unittest
from datetime import datetime, timezone

from claude_token_monitor.parser import parse_line, parse_timestamp
from tests.helpers import BASE_TIME, assistant_record, line


class ParseTimestampTests(unittest.TestCase):
    def test_zulu_suffix(self):
        parsed = parse_timestamp("2026-07-29T14:19:05.112Z")
        self.assertEqual(parsed.tzinfo, timezone.utc)
        self.assertEqual(parsed.year, 2026)
        self.assertEqual(parsed.hour, 14)

    def test_offset_converted_to_utc(self):
        parsed = parse_timestamp("2026-07-29T21:19:05+07:00")
        self.assertEqual(parsed.hour, 14)
        self.assertEqual(parsed.tzinfo, timezone.utc)

    def test_naive_assumed_utc(self):
        parsed = parse_timestamp("2026-07-29T14:19:05")
        self.assertEqual(parsed.tzinfo, timezone.utc)

    def test_invalid_returns_none(self):
        self.assertIsNone(parse_timestamp("not a time"))
        self.assertIsNone(parse_timestamp(""))
        self.assertIsNone(parse_timestamp(None))
        self.assertIsNone(parse_timestamp(12345))


class ParseLineTests(unittest.TestCase):
    def test_parses_a_full_assistant_record(self):
        record = parse_line(
            line(
                assistant_record(
                    input_tokens=2,
                    output_tokens=372,
                    cache_read=33_777,
                    cache_1h=24_033,
                )
            ),
            project="proj",
        )
        self.assertIsNotNone(record)
        self.assertEqual(record.model, "claude-opus-5")
        self.assertEqual(record.input_tokens, 2)
        self.assertEqual(record.output_tokens, 372)
        self.assertEqual(record.cache_read_tokens, 33_777)
        self.assertEqual(record.cache_write_1h_tokens, 24_033)
        self.assertEqual(record.cache_write_5m_tokens, 0)
        self.assertEqual(record.project, "proj")
        self.assertEqual(record.session_id, "sess-1")
        self.assertFalse(record.is_sidechain)

    def test_token_properties(self):
        record = parse_line(
            line(
                assistant_record(
                    input_tokens=1,
                    output_tokens=2,
                    cache_read=4,
                    cache_5m=8,
                    cache_1h=16,
                )
            )
        )
        self.assertEqual(record.total_tokens, 31)
        self.assertEqual(record.billable_tokens, 27)
        self.assertEqual(record.cache_write_tokens, 24)

    def test_cost_is_computed(self):
        record = parse_line(
            line(assistant_record(input_tokens=1_000_000, output_tokens=0))
        )
        self.assertAlmostEqual(record.cost_usd, 5.0, places=6)

    def test_accepts_bytes(self):
        payload = line(assistant_record()).encode("utf-8")
        self.assertIsNotNone(parse_line(payload))

    def test_multibyte_utf8_content_parses(self):
        record = assistant_record(session_id="sesi-répons-日本語")
        parsed = parse_line(line(record).encode("utf-8"))
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.session_id, "sesi-répons-日本語")

    def test_invalid_utf8_bytes_are_rejected_without_raising(self):
        # Corrupt trailing byte makes the line un-parseable; the contract is
        # that it is skipped, not that it raises.
        payload = line(assistant_record()).encode("utf-8") + b"\xff"
        self.assertIsNone(parse_line(payload))

    # ---------------------------------------------------------- rejections

    def test_non_assistant_type_ignored(self):
        record = assistant_record()
        record["type"] = "user"
        self.assertIsNone(parse_line(line(record)))

    def test_synthetic_model_ignored(self):
        self.assertIsNone(parse_line(line(assistant_record(model="<synthetic>"))))

    def test_missing_usage_ignored(self):
        record = assistant_record()
        del record["message"]["usage"]
        self.assertIsNone(parse_line(line(record)))

    def test_all_zero_usage_ignored(self):
        record = assistant_record(input_tokens=0, output_tokens=0)
        self.assertIsNone(parse_line(line(record)))

    def test_missing_timestamp_ignored(self):
        record = assistant_record()
        del record["timestamp"]
        self.assertIsNone(parse_line(line(record)))

    def test_malformed_json_ignored(self):
        self.assertIsNone(parse_line('{"type": "assistant", '))

    def test_blank_and_non_object_lines_ignored(self):
        for candidate in ("", "   ", "null", "[1,2,3]", "plain text"):
            self.assertIsNone(parse_line(candidate), candidate)

    def test_message_not_a_dict_ignored(self):
        self.assertIsNone(
            parse_line(json.dumps({"type": "assistant", "message": "nope"}))
        )

    def test_negative_token_counts_clamped_to_zero(self):
        record = assistant_record()
        record["message"]["usage"]["input_tokens"] = -5
        parsed = parse_line(line(record))
        self.assertEqual(parsed.input_tokens, 0)

    def test_non_numeric_token_counts_treated_as_zero(self):
        record = assistant_record(output_tokens=7)
        record["message"]["usage"]["input_tokens"] = "lots"
        parsed = parse_line(line(record))
        self.assertEqual(parsed.input_tokens, 0)
        self.assertEqual(parsed.output_tokens, 7)

    # ------------------------------------------------------ cache splitting

    def test_cache_split_uses_detail_when_consistent(self):
        record = parse_line(line(assistant_record(cache_5m=100, cache_1h=250)))
        self.assertEqual(record.cache_write_5m_tokens, 100)
        self.assertEqual(record.cache_write_1h_tokens, 250)

    def test_missing_detail_attributes_all_to_5m(self):
        record = parse_line(
            line(assistant_record(cache_5m=300, cache_1h=0, include_detail=False))
        )
        self.assertEqual(record.cache_write_5m_tokens, 300)
        self.assertEqual(record.cache_write_1h_tokens, 0)

    def test_detail_disagreeing_with_total_puts_remainder_in_5m(self):
        record = assistant_record(cache_5m=100, cache_1h=200)
        record["message"]["usage"]["cache_creation_input_tokens"] = 500
        parsed = parse_line(line(record))
        self.assertEqual(parsed.cache_write_1h_tokens, 200)
        self.assertEqual(parsed.cache_write_5m_tokens, 300)
        self.assertEqual(parsed.cache_write_tokens, 500)

    def test_detail_exceeding_total_falls_back_to_total_at_cheap_rate(self):
        record = assistant_record(cache_5m=0, cache_1h=900)
        record["message"]["usage"]["cache_creation_input_tokens"] = 100
        parsed = parse_line(line(record))
        self.assertEqual(parsed.cache_write_5m_tokens, 100)
        self.assertEqual(parsed.cache_write_1h_tokens, 0)

    # ------------------------------------------------------------- identity

    def test_dedup_key_from_message_and_request_id(self):
        a = parse_line(line(assistant_record(message_id="m1", request_id="r1")))
        b = parse_line(
            line(
                assistant_record(
                    message_id="m1", request_id="r1", session_id="other-session"
                )
            ),
            source="different-file.jsonl",
        )
        self.assertEqual(a.dedup_key, b.dedup_key)

    def test_different_requests_get_different_keys(self):
        a = parse_line(line(assistant_record(message_id="m1", request_id="r1")))
        b = parse_line(line(assistant_record(message_id="m2", request_id="r2")))
        self.assertNotEqual(a.dedup_key, b.dedup_key)

    def test_dedup_key_falls_back_to_uuid_and_source(self):
        record = assistant_record(uuid="u-1")
        del record["requestId"]
        del record["message"]["id"]
        a = parse_line(line(record), source="file-a")
        b = parse_line(line(record), source="file-b")
        self.assertTrue(a.dedup_key.startswith("uuid:"))
        self.assertNotEqual(a.dedup_key, b.dedup_key)

    def test_sidechain_flag_preserved(self):
        record = parse_line(line(assistant_record(is_sidechain=True)))
        self.assertTrue(record.is_sidechain)

    def test_timestamp_is_utc_aware(self):
        record = parse_line(line(assistant_record(timestamp=BASE_TIME)))
        self.assertEqual(record.timestamp, BASE_TIME)
        self.assertIsNotNone(record.timestamp.tzinfo)

    def test_fast_mode_speed_changes_cost(self):
        standard = parse_line(
            line(assistant_record(input_tokens=1_000_000, output_tokens=0))
        )
        fast = parse_line(
            line(
                assistant_record(
                    input_tokens=1_000_000, output_tokens=0, speed="fast"
                )
            )
        )
        self.assertAlmostEqual(standard.cost_usd, 5.0, places=6)
        self.assertAlmostEqual(fast.cost_usd, 10.0, places=6)


if __name__ == "__main__":
    unittest.main()
