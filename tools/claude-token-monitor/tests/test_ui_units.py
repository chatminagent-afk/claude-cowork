"""Unit coverage for the presentation layer that does not need a display."""

import unittest
from datetime import datetime, timedelta, timezone

from claude_token_monitor import formatting, icon, startup
from claude_token_monitor.aggregate import Aggregator, Totals
from claude_token_monitor.config import Config
from claude_token_monitor.tray import TOOLTIP_LIMIT, build_tooltip

NOW = datetime(2026, 7, 20, 18, 0, 0, tzinfo=timezone.utc)


class FormattingTests(unittest.TestCase):
    def test_token_scales(self):
        self.assertEqual(formatting.tokens(0), "0")
        self.assertEqual(formatting.tokens(999), "999")
        self.assertEqual(formatting.tokens(1_500), "1.5K")
        self.assertEqual(formatting.tokens(2_500_000), "2.50M")
        self.assertEqual(formatting.tokens(3_120_000_000), "3.12B")

    def test_negative_tokens(self):
        self.assertEqual(formatting.tokens(-1_500), "-1.5K")

    def test_tokens_exact_has_separators(self):
        self.assertEqual(formatting.tokens_exact(1234567), "1,234,567")

    def test_money_precision(self):
        self.assertEqual(formatting.money(0), "$0.00")
        self.assertEqual(formatting.money(0.0004), "$0.0004")
        self.assertEqual(formatting.money(12.5), "$12.50")
        self.assertEqual(formatting.money(1234.5), "$1,234")

    def test_duration(self):
        self.assertEqual(formatting.duration(None), "--")
        self.assertEqual(formatting.duration(timedelta(seconds=0)), "now")
        self.assertEqual(formatting.duration(timedelta(seconds=30)), "30s")
        self.assertEqual(formatting.duration(timedelta(minutes=5)), "5m")
        self.assertEqual(formatting.duration(timedelta(hours=2)), "2h")
        self.assertEqual(formatting.duration(timedelta(hours=4, minutes=12)), "4h 12m")

    def test_ago(self):
        self.assertEqual(formatting.ago(None), "never")
        self.assertEqual(formatting.ago(NOW, NOW), "just now")
        self.assertEqual(formatting.ago(NOW - timedelta(minutes=3), NOW), "3m ago")

    def test_metric_number_units(self):
        self.assertEqual(formatting.metric_number(12.5, "cost"), "$12.50")
        self.assertEqual(formatting.metric_number(1500, "weighted"), "1.5K")
        self.assertEqual(formatting.metric_number(1500, "weighted", exact=True), "1,500")

    def test_data_size_units(self):
        self.assertEqual(formatting.data_size(0), "0 B")
        self.assertEqual(formatting.data_size(812), "812 B")
        self.assertEqual(formatting.data_size(45_056), "44.0 KB")
        self.assertEqual(formatting.data_size(128_450_560), "122.5 MB")
        self.assertEqual(formatting.data_size(2_147_483_648), "2.00 GB")

    def test_clock_and_percent(self):
        self.assertEqual(formatting.percent(0.5), "50%")
        self.assertEqual(formatting.clock(None), "--")
        self.assertRegex(formatting.clock(NOW), r"^\d{2}:\d{2}:\d{2}$")


class IconTests(unittest.TestCase):
    def test_renders_rgba_image_of_requested_size(self):
        image = icon.render_icon(0.5)
        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(image.size, (icon.SIZE, icon.SIZE))

    def test_custom_size(self):
        self.assertEqual(icon.render_icon(0.2, size=32).size, (32, 32))

    def test_status_colors_follow_thresholds(self):
        self.assertEqual(icon.status_color(0.10), icon.COLOR_OK)
        self.assertEqual(icon.status_color(0.70), icon.COLOR_WARN)
        self.assertEqual(icon.status_color(0.95), icon.COLOR_CRIT)

    def test_threshold_boundaries_are_inclusive(self):
        self.assertEqual(icon.status_color(0.60), icon.COLOR_WARN)
        self.assertEqual(icon.status_color(0.85), icon.COLOR_CRIT)

    def test_no_data_is_idle_grey(self):
        self.assertEqual(icon.status_color(0.9, has_data=False), icon.COLOR_IDLE)

    def test_custom_thresholds(self):
        self.assertEqual(
            icon.status_color(0.4, warn_pct=0.3, crit_pct=0.5), icon.COLOR_WARN
        )

    def test_labels(self):
        self.assertEqual(icon.label_for(0.0), "0")
        self.assertEqual(icon.label_for(0.42), "42")
        self.assertEqual(icon.label_for(1.5), "!")
        self.assertEqual(icon.label_for(0.5, has_data=False), "--")

    def test_extreme_ratios_do_not_raise(self):
        for ratio in (-5.0, 0.0, 1.0, 99.0):
            self.assertIsNotNone(icon.render_icon(ratio))


class TooltipTests(unittest.TestCase):
    def build_snapshot(self):
        agg = Aggregator(retention_days=3650)
        from tests.test_aggregate import make_record

        agg.add([make_record(key="a", minutes_ago=2, input_tokens=1000, cost=1.25)])
        return agg.snapshot(now=NOW, scope="today")

    def test_tooltip_fits_the_shell_limit(self):
        tooltip = build_tooltip(self.build_snapshot(), Config())
        self.assertLessEqual(len(tooltip), TOOLTIP_LIMIT)

    def test_tooltip_mentions_the_window_and_today(self):
        tooltip = build_tooltip(self.build_snapshot(), Config())
        self.assertIn("5h", tooltip)
        self.assertIn("Today", tooltip)

    def test_tooltip_survives_zero_limit(self):
        config = Config(limit_5h_tokens=0)
        self.assertTrue(build_tooltip(self.build_snapshot(), config))

    def test_tooltip_survives_empty_snapshot(self):
        snapshot = Aggregator().snapshot(now=NOW)
        self.assertTrue(build_tooltip(snapshot, Config()))


class StartupTests(unittest.TestCase):
    def test_launcher_script_is_the_repo_entry_point(self):
        self.assertEqual(startup.launcher_script().name, "run_monitor.py")

    def test_launcher_script_exists(self):
        self.assertTrue(startup.launcher_script().exists())

    def test_command_quotes_both_paths(self):
        command = startup.startup_command()
        self.assertEqual(command.count('"'), 4)
        self.assertIn("run_monitor.py", command)

    def test_is_enabled_returns_a_bool_without_raising(self):
        self.assertIsInstance(startup.is_enabled(), bool)

    def test_pythonw_path_is_a_real_executable(self):
        self.assertTrue(startup.pythonw_executable().exists())


class ReportRenderTests(unittest.TestCase):
    def test_renders_without_data(self):
        from claude_token_monitor.report import render

        snapshot = Aggregator().snapshot(now=NOW)
        text = render(snapshot, Config())
        self.assertIn("ROLLING WINDOWS", text)
        self.assertIn("no usage in scope", text)

    def test_renders_with_data(self):
        from claude_token_monitor.report import render
        from tests.test_aggregate import make_record

        agg = Aggregator(retention_days=3650)
        agg.add([make_record(key="a", minutes_ago=1, input_tokens=5000, cost=2.0)])
        text = render(agg.snapshot(now=NOW, scope="all"), Config())
        self.assertIn("claude-opus-5", text)
        self.assertIn("BY PROJECT", text)

    def test_suggest_limits_shape(self):
        from claude_token_monitor.report import CALIBRATION_HEADROOM, suggest_limits
        from tests.test_aggregate import make_record

        agg = Aggregator(retention_days=3650)
        agg.add([make_record(key="a", minutes_ago=1, input_tokens=1000)])
        suggestions = suggest_limits(agg, "total")
        self.assertEqual(set(suggestions), {"5h", "7d"})
        peak, suggested, _at = suggestions["5h"]
        self.assertEqual(peak, 1000)
        self.assertAlmostEqual(suggested, 1000 * CALIBRATION_HEADROOM)


if __name__ == "__main__":
    unittest.main()
