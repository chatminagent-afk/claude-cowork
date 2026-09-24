import json
import os
import tempfile
import unittest
from pathlib import Path

from claude_token_monitor.config import Config, config_dir, config_path


class ConfigFileTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.path = self.dir / "config.json"
        self.addCleanup(self._tmp.cleanup)


class DefaultsTests(unittest.TestCase):
    def test_defaults_are_valid(self):
        config = Config()
        config.validate()
        self.assertGreater(config.limit_5h_tokens, 0)
        self.assertGreater(config.limit_7d_tokens, 0)
        self.assertEqual(config.gauge_metric, "weighted")
        self.assertEqual(config.scope, "today")
        self.assertTrue(config.include_sidechains)

    def test_root_path_is_none_by_default(self):
        self.assertIsNone(Config().root_path())

    def test_root_path_when_set(self):
        config = Config(transcript_root=r"C:\somewhere")
        self.assertEqual(config.root_path(), Path(r"C:\somewhere"))


class ValidationTests(unittest.TestCase):
    def test_limits_cannot_be_zero_or_negative(self):
        config = Config(limit_5h_tokens=0, limit_7d_tokens=-5).validate()
        self.assertEqual(config.limit_5h_tokens, 1)
        self.assertEqual(config.limit_7d_tokens, 1)

    def test_poll_interval_clamped(self):
        self.assertEqual(Config(poll_interval_s=0.01).validate().poll_interval_s, 0.5)
        self.assertEqual(Config(poll_interval_s=9999).validate().poll_interval_s, 300.0)

    def test_thresholds_clamped_and_ordered(self):
        config = Config(warn_pct=0.9, crit_pct=0.2).validate()
        self.assertEqual(config.warn_pct, 0.9)
        self.assertGreaterEqual(config.crit_pct, config.warn_pct)

    def test_thresholds_capped_at_one(self):
        config = Config(warn_pct=5.0, crit_pct=9.0).validate()
        self.assertEqual(config.warn_pct, 1.0)
        self.assertEqual(config.crit_pct, 1.0)

    def test_bad_scope_reset(self):
        self.assertEqual(Config(scope="yesterday").validate().scope, "today")

    def test_bad_metric_reset(self):
        self.assertEqual(Config(gauge_metric="vibes").validate().gauge_metric, "weighted")

    def test_retention_minimum_one_day(self):
        self.assertEqual(Config(retention_days=0).validate().retention_days, 1)


class PersistenceTests(ConfigFileTestCase):
    def test_roundtrip(self):
        original = Config(
            limit_5h_tokens=1234,
            limit_7d_tokens=5678,
            gauge_metric="cost",
            poll_interval_s=3.5,
            scope="7d",
            include_sidechains=False,
        )
        original.save(self.path)
        loaded = Config.load(self.path)
        self.assertEqual(loaded.limit_5h_tokens, 1234)
        self.assertEqual(loaded.limit_7d_tokens, 5678)
        self.assertEqual(loaded.gauge_metric, "cost")
        self.assertEqual(loaded.poll_interval_s, 3.5)
        self.assertEqual(loaded.scope, "7d")
        self.assertFalse(loaded.include_sidechains)

    def test_save_creates_parent_directories(self):
        nested = self.dir / "a" / "b" / "config.json"
        Config().save(nested)
        self.assertTrue(nested.exists())

    def test_save_leaves_no_temporary_files(self):
        Config().save(self.path)
        leftovers = [p for p in self.dir.iterdir() if p.suffix == ".tmp"]
        self.assertEqual(leftovers, [])

    def test_save_is_atomic_replacement(self):
        Config(limit_5h_tokens=1).save(self.path)
        Config(limit_5h_tokens=2).save(self.path)
        self.assertEqual(Config.load(self.path).limit_5h_tokens, 2)

    def test_missing_file_yields_defaults(self):
        loaded = Config.load(self.dir / "absent.json")
        self.assertEqual(loaded.limit_5h_tokens, Config().limit_5h_tokens)

    def test_corrupt_file_yields_defaults(self):
        self.path.write_text("{not json", encoding="utf-8")
        self.assertEqual(Config.load(self.path).gauge_metric, "weighted")

    def test_non_object_json_yields_defaults(self):
        self.path.write_text("[1, 2, 3]", encoding="utf-8")
        self.assertEqual(Config.load(self.path).scope, "today")

    def test_unknown_keys_ignored(self):
        self.path.write_text(
            json.dumps({"limit_5h_tokens": 42, "who_knows": "what"}), encoding="utf-8"
        )
        loaded = Config.load(self.path)
        self.assertEqual(loaded.limit_5h_tokens, 42)
        self.assertFalse(hasattr(loaded, "who_knows"))

    def test_wrong_typed_value_is_skipped_not_fatal(self):
        self.path.write_text(
            json.dumps({"limit_5h_tokens": "banana", "scope": "7d"}), encoding="utf-8"
        )
        loaded = Config.load(self.path)
        self.assertEqual(loaded.limit_5h_tokens, Config().limit_5h_tokens)
        self.assertEqual(loaded.scope, "7d")

    def test_loaded_values_are_validated(self):
        self.path.write_text(json.dumps({"poll_interval_s": 0.001}), encoding="utf-8")
        self.assertEqual(Config.load(self.path).poll_interval_s, 0.5)

    def test_saved_file_is_readable_json(self):
        Config().save(self.path)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertIn("limit_5h_tokens", data)
        self.assertIn("gauge_metric", data)


class LocationTests(unittest.TestCase):
    def setUp(self):
        self._previous = os.environ.get("CLAUDE_TOKEN_MONITOR_HOME")

    def tearDown(self):
        if self._previous is None:
            os.environ.pop("CLAUDE_TOKEN_MONITOR_HOME", None)
        else:
            os.environ["CLAUDE_TOKEN_MONITOR_HOME"] = self._previous

    def test_env_override_respected(self):
        os.environ["CLAUDE_TOKEN_MONITOR_HOME"] = r"C:\custom\loc"
        self.assertEqual(config_dir(), Path(r"C:\custom\loc"))
        self.assertEqual(config_path().name, "config.json")

    def test_default_is_home_relative_not_appdata(self):
        """Store Python redirects %APPDATA%, so the default must avoid it.

        A config path under AppData resolves to a different real directory
        depending on which interpreter launched the app.
        """
        os.environ.pop("CLAUDE_TOKEN_MONITOR_HOME", None)
        directory = config_dir()
        self.assertEqual(directory.parent, Path.home())
        self.assertEqual(directory.name, ".claude-token-monitor")

    def test_default_is_stable_under_appdata_changes(self):
        os.environ.pop("CLAUDE_TOKEN_MONITOR_HOME", None)
        previous_appdata = os.environ.get("APPDATA")
        os.environ["APPDATA"] = r"C:\somewhere\else"
        try:
            self.assertEqual(config_dir(), Path.home() / ".claude-token-monitor")
        finally:
            if previous_appdata is None:
                os.environ.pop("APPDATA", None)
            else:
                os.environ["APPDATA"] = previous_appdata


if __name__ == "__main__":
    unittest.main()
