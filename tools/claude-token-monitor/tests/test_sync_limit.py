"""Deriving the rate limit from a percentage reported by Claude's usage panel."""

import unittest

from claude_token_monitor.report import limit_from_percent, percent_uncertainty


class LimitFromPercentTests(unittest.TestCase):
    def test_back_solves_the_denominator(self):
        self.assertAlmostEqual(limit_from_percent(88.0, 88.0), 100.0, places=9)

    def test_real_world_case(self):
        # Observed: engine counted 7,509,802 while Claude's panel showed 88%.
        self.assertAlmostEqual(
            limit_from_percent(7_509_802, 88), 8_533_866.0, delta=1.0
        )

    def test_half_usage_doubles_the_limit(self):
        self.assertAlmostEqual(limit_from_percent(500.0, 50.0), 1000.0, places=9)

    def test_full_usage_returns_the_usage(self):
        self.assertAlmostEqual(limit_from_percent(1234.0, 100.0), 1234.0, places=9)

    def test_zero_percent_is_rejected(self):
        with self.assertRaises(ValueError):
            limit_from_percent(100.0, 0.0)

    def test_negative_percent_is_rejected(self):
        with self.assertRaises(ValueError):
            limit_from_percent(100.0, -10.0)

    def test_accepts_fractional_percent(self):
        self.assertAlmostEqual(limit_from_percent(87.5, 87.5), 100.0, places=9)


class UncertaintyTests(unittest.TestCase):
    def test_band_brackets_the_point_estimate(self):
        used, percent = 7_509_802, 88
        low, high = percent_uncertainty(used, percent)
        point = limit_from_percent(used, percent)
        self.assertLess(low, point)
        self.assertGreater(high, point)

    def test_band_reflects_half_a_percent_either_way(self):
        low, high = percent_uncertainty(1000.0, 50.0)
        self.assertAlmostEqual(low, 1000.0 / 0.505, places=6)
        self.assertAlmostEqual(high, 1000.0 / 0.495, places=6)

    def test_band_is_narrow_at_high_percentages(self):
        used = 8_000_000
        low, high = percent_uncertainty(used, 88)
        self.assertLess((high - low) / limit_from_percent(used, 88), 0.02)

    def test_low_percentage_gives_a_wide_band(self):
        narrow = percent_uncertainty(1000.0, 90.0)
        wide = percent_uncertainty(1000.0, 5.0)
        self.assertGreater(wide[1] - wide[0], narrow[1] - narrow[0])

    def test_one_percent_does_not_divide_by_zero(self):
        low, high = percent_uncertainty(1000.0, 1.0)
        self.assertGreater(high, low)


if __name__ == "__main__":
    unittest.main()
