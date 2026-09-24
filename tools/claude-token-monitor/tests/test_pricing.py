import unittest
from datetime import date, datetime, timezone

from claude_token_monitor import pricing


class NormalizeModelTests(unittest.TestCase):
    def test_strips_date_suffix(self):
        self.assertEqual(
            pricing.normalize_model("claude-haiku-4-5-20251001"), "claude-haiku-4-5"
        )

    def test_strips_bedrock_prefix(self):
        self.assertEqual(
            pricing.normalize_model("anthropic.claude-opus-5"), "claude-opus-5"
        )

    def test_strips_vertex_version(self):
        self.assertEqual(
            pricing.normalize_model("claude-opus-4-5@20251101"), "claude-opus-4-5"
        )

    def test_lowercases_and_trims(self):
        self.assertEqual(pricing.normalize_model("  Claude-Opus-5 "), "claude-opus-5")

    def test_none_and_empty(self):
        self.assertEqual(pricing.normalize_model(None), "")
        self.assertEqual(pricing.normalize_model(""), "")

    def test_unknown_model_passes_through(self):
        self.assertEqual(pricing.normalize_model("claude-future-9"), "claude-future-9")

    def test_does_not_strip_non_date_numeric_tail(self):
        # Seven digits is not a date suffix and must survive.
        self.assertEqual(pricing.normalize_model("model-1234567"), "model-1234567")


class SyntheticTests(unittest.TestCase):
    def test_synthetic_detected(self):
        self.assertTrue(pricing.is_synthetic("<synthetic>"))
        self.assertTrue(pricing.is_synthetic(""))
        self.assertTrue(pricing.is_synthetic(None))

    def test_real_model_not_synthetic(self):
        self.assertFalse(pricing.is_synthetic("claude-opus-5"))


class RateTests(unittest.TestCase):
    def test_opus_5_base_rate(self):
        rate = pricing.get_rate("claude-opus-5")
        self.assertEqual((rate.input_per_mtok, rate.output_per_mtok), (5.0, 25.0))

    def test_haiku_dated_id_resolves(self):
        rate = pricing.get_rate("claude-haiku-4-5-20251001")
        self.assertEqual((rate.input_per_mtok, rate.output_per_mtok), (1.0, 5.0))

    def test_sonnet_5_intro_rate_applies_before_cutoff(self):
        rate = pricing.get_rate("claude-sonnet-5", when=date(2026, 8, 31))
        self.assertEqual((rate.input_per_mtok, rate.output_per_mtok), (2.0, 10.0))

    def test_sonnet_5_base_rate_after_cutoff(self):
        rate = pricing.get_rate("claude-sonnet-5", when=date(2026, 9, 1))
        self.assertEqual((rate.input_per_mtok, rate.output_per_mtok), (3.0, 15.0))

    def test_sonnet_5_accepts_datetime(self):
        rate = pricing.get_rate(
            "claude-sonnet-5", when=datetime(2026, 9, 2, tzinfo=timezone.utc)
        )
        self.assertEqual(rate.input_per_mtok, 3.0)

    def test_fast_mode_premium(self):
        rate = pricing.get_rate("claude-opus-5", speed="fast")
        self.assertEqual((rate.input_per_mtok, rate.output_per_mtok), (10.0, 50.0))

    def test_fast_mode_ignored_for_unsupported_model(self):
        rate = pricing.get_rate("claude-haiku-4-5", speed="fast")
        self.assertEqual(rate.input_per_mtok, 1.0)

    def test_unknown_model_has_no_rate(self):
        self.assertIsNone(pricing.get_rate("claude-does-not-exist"))
        self.assertFalse(pricing.is_priced("claude-does-not-exist"))

    def test_synthetic_has_no_rate(self):
        self.assertIsNone(pricing.get_rate("<synthetic>"))


class CostTests(unittest.TestCase):
    def test_input_and_output(self):
        cost = pricing.cost_usd(
            "claude-opus-5", input_tokens=1_000_000, output_tokens=1_000_000
        )
        self.assertAlmostEqual(cost, 30.0, places=9)

    def test_cache_read_is_one_tenth_of_input(self):
        cost = pricing.cost_usd("claude-opus-5", cache_read_tokens=1_000_000)
        self.assertAlmostEqual(cost, 0.5, places=9)

    def test_cache_write_5m_is_1_25x_input(self):
        cost = pricing.cost_usd("claude-opus-5", cache_write_5m_tokens=1_000_000)
        self.assertAlmostEqual(cost, 6.25, places=9)

    def test_cache_write_1h_is_2x_input(self):
        cost = pricing.cost_usd("claude-opus-5", cache_write_1h_tokens=1_000_000)
        self.assertAlmostEqual(cost, 10.0, places=9)

    def test_combined_cost(self):
        cost = pricing.cost_usd(
            "claude-opus-5",
            input_tokens=100_000,
            output_tokens=50_000,
            cache_read_tokens=2_000_000,
            cache_write_5m_tokens=200_000,
            cache_write_1h_tokens=100_000,
        )
        expected = (
            100_000 * 5 / 1e6
            + 50_000 * 25 / 1e6
            + 2_000_000 * 0.5 / 1e6
            + 200_000 * 6.25 / 1e6
            + 100_000 * 10.0 / 1e6
        )
        self.assertAlmostEqual(cost, expected, places=9)

    def test_unknown_model_costs_zero(self):
        self.assertEqual(
            pricing.cost_usd("claude-nope", input_tokens=1_000_000), 0.0
        )

    def test_zero_tokens_costs_zero(self):
        self.assertEqual(pricing.cost_usd("claude-opus-5"), 0.0)

    def test_multipliers_are_the_documented_values(self):
        self.assertEqual(pricing.CACHE_WRITE_5M_MULTIPLIER, 1.25)
        self.assertEqual(pricing.CACHE_WRITE_1H_MULTIPLIER, 2.00)
        self.assertEqual(pricing.CACHE_READ_MULTIPLIER, 0.10)


if __name__ == "__main__":
    unittest.main()
