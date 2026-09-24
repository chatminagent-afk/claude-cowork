"""Coverage for the theme, graphics, and timeline layers.

These are pure functions over colours, images, and numbers, so they can be
asserted on without a display.
"""

import unittest
from datetime import datetime, timedelta, timezone

from PIL import Image

from claude_token_monitor import graphics, theme
from claude_token_monitor.aggregate import Aggregator
from claude_token_monitor.config import Config

NOW = datetime(2026, 7, 20, 18, 0, 0, tzinfo=timezone.utc)


class PaletteTests(unittest.TestCase):
    def test_named_palettes_resolve(self):
        self.assertIs(theme.resolve_palette("light"), theme.LIGHT)
        self.assertIs(theme.resolve_palette("dark"), theme.DARK)

    def test_auto_resolves_to_a_real_palette(self):
        self.assertIn(theme.resolve_palette("auto"), (theme.LIGHT, theme.DARK))

    def test_unknown_mode_falls_back_to_auto(self):
        self.assertIn(theme.resolve_palette("neon"), (theme.LIGHT, theme.DARK))

    def test_system_detection_returns_bool(self):
        self.assertIsInstance(theme.system_prefers_dark(), bool)

    def test_every_palette_field_is_a_hex_colour(self):
        for palette in (theme.LIGHT, theme.DARK):
            for field in palette.__dataclass_fields__:
                value = getattr(palette, field)
                if field in ("name", "shadow"):
                    continue
                self.assertRegex(value, r"^#[0-9a-fA-F]{6}$", f"{palette.name}.{field}")

    def test_palettes_differ(self):
        self.assertNotEqual(theme.LIGHT.bg, theme.DARK.bg)
        self.assertNotEqual(theme.LIGHT.text, theme.DARK.text)


class ModelColorTests(unittest.TestCase):
    def test_stable_for_the_same_model(self):
        self.assertEqual(theme.model_color("claude-opus-5"), theme.model_color("claude-opus-5"))

    def test_known_models_get_distinct_colours(self):
        known = ("claude-opus-5", "claude-sonnet-5", "claude-haiku-4-5", "claude-opus-4-8")
        colors = {theme.model_color(m) for m in known}
        self.assertEqual(len(colors), len(known))

    def test_unknown_model_still_gets_a_colour(self):
        self.assertIn(theme.model_color("something-else"), theme.MODEL_COLORS)

    def test_colour_is_hex(self):
        self.assertRegex(theme.model_color("claude-opus-5"), r"^#[0-9a-fA-F]{6}$")


class GraphicsTests(unittest.TestCase):
    def test_card_size_and_mode(self):
        image = graphics.card(200, 80, bg="#ffffff", fill="#f0f0f0")
        self.assertEqual(image.size, (200, 80))
        self.assertEqual(image.mode, "RGB")

    def test_card_with_shadow_and_border(self):
        image = graphics.card(
            120, 60, bg="#ffffff", fill="#ffffff", border="#cccccc", shadow=True
        )
        self.assertEqual(image.size, (120, 60))

    def test_donut_is_square(self):
        self.assertEqual(graphics.donut(90, 0.5, bg="#fff", fill="#000", track="#eee").size, (90, 90))

    def test_donut_ratio_changes_pixels(self):
        empty = graphics.donut(64, 0.0, bg="#ffffff", fill="#ff0000", track="#eeeeee")
        full = graphics.donut(64, 1.0, bg="#ffffff", fill="#ff0000", track="#eeeeee")
        self.assertNotEqual(empty.tobytes(), full.tobytes())

    def test_donut_clamps_out_of_range_ratios(self):
        for ratio in (-3.0, 0.0, 1.0, 9.0):
            self.assertEqual(
                graphics.donut(48, ratio, bg="#fff", fill="#000", track="#eee").size, (48, 48)
            )

    def test_pill_size(self):
        self.assertEqual(
            graphics.pill(180, 10, 0.4, bg="#fff", fill="#000", track="#eee").size, (180, 10)
        )

    def test_pill_tiny_ratio_still_renders(self):
        image = graphics.pill(180, 10, 0.001, bg="#ffffff", fill="#ff0000", track="#eeeeee")
        empty = graphics.pill(180, 10, 0.0, bg="#ffffff", fill="#ff0000", track="#eeeeee")
        self.assertEqual(image.size, empty.size)

    def test_bars_size_and_empty_input(self):
        self.assertEqual(
            graphics.bars(200, 60, [], bg="#fff", fill="#000").size, (200, 60)
        )
        self.assertEqual(
            graphics.bars(200, 60, [1, 5, 3], bg="#fff", fill="#000").size, (200, 60)
        )

    def test_bars_all_zero_does_not_divide_by_zero(self):
        self.assertEqual(
            graphics.bars(120, 40, [0, 0, 0], bg="#fff", fill="#000").size, (120, 40)
        )

    def test_bars_highlight_changes_last_column(self):
        plain = graphics.bars(120, 40, [3, 3, 3], bg="#ffffff", fill="#000000")
        lit = graphics.bars(
            120, 40, [3, 3, 3], bg="#ffffff", fill="#000000", highlight="#ff0000"
        )
        self.assertNotEqual(plain.tobytes(), lit.tobytes())

    def test_dot_is_square(self):
        self.assertEqual(graphics.dot(9, "#ff0000", bg="#ffffff").size, (9, 9))

    def test_degenerate_sizes_do_not_raise(self):
        self.assertIsInstance(graphics.card(0, 0, bg="#fff", fill="#fff"), Image.Image)
        self.assertIsInstance(graphics.pill(1, 1, 0.5, bg="#fff", fill="#000", track="#eee"), Image.Image)
        self.assertIsInstance(graphics.bars(1, 1, [1], bg="#fff", fill="#000"), Image.Image)


class TimelineTests(unittest.TestCase):
    def setUp(self):
        from tests.test_aggregate import make_record

        self.make_record = make_record
        self.agg = Aggregator(retention_days=3650)

    def test_empty_returns_zeroed_series(self):
        series = self.agg.timeline(now=NOW, span=timedelta(hours=24), buckets=12)
        self.assertEqual(len(series), 12)
        self.assertEqual(sum(series), 0)

    def test_records_land_in_the_right_bucket(self):
        # 24h span across 24 buckets => one bucket per hour.
        self.agg.add(
            [
                self.make_record(key="a", minutes_ago=30, input_tokens=100),
                self.make_record(key="b", minutes_ago=90, input_tokens=200),
            ]
        )
        series = self.agg.timeline(
            now=NOW, span=timedelta(hours=24), buckets=24, metric="total"
        )
        self.assertEqual(series[-1], 100)
        self.assertEqual(series[-2], 200)
        self.assertEqual(sum(series), 300)

    def test_records_outside_the_span_are_excluded(self):
        self.agg.add([self.make_record(key="old", minutes_ago=60 * 30, input_tokens=999)])
        series = self.agg.timeline(
            now=NOW, span=timedelta(hours=24), buckets=24, metric="total"
        )
        self.assertEqual(sum(series), 0)

    def test_metric_is_respected(self):
        self.agg.add([self.make_record(key="a", minutes_ago=5, cache_read=1000)])
        total = self.agg.timeline(now=NOW, buckets=4, metric="total")
        weighted = self.agg.timeline(now=NOW, buckets=4, metric="weighted")
        self.assertEqual(sum(total), 1000)
        self.assertAlmostEqual(sum(weighted), 100.0)

    def test_bucket_count_is_clamped_to_at_least_one(self):
        self.assertEqual(len(self.agg.timeline(now=NOW, buckets=0)), 1)

    def test_series_length_matches_requested_buckets(self):
        for count in (1, 12, 48, 96):
            self.assertEqual(len(self.agg.timeline(now=NOW, buckets=count)), count)


class ThemeConfigTests(unittest.TestCase):
    def test_theme_defaults_to_auto(self):
        self.assertEqual(Config().theme, "auto")

    def test_invalid_theme_is_reset(self):
        self.assertEqual(Config(theme="rainbow").validate().theme, "auto")

    def test_valid_themes_survive_validation(self):
        for mode in ("auto", "light", "dark"):
            self.assertEqual(Config(theme=mode).validate().theme, mode)


if __name__ == "__main__":
    unittest.main()
