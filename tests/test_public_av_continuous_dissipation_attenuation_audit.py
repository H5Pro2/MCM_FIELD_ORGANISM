from __future__ import annotations

import math
import unittest

from mcm_field_organism.public_av_continuous_dissipation_attenuation_audit import (
    PublicAVContinuousDissipationAttenuationError,
    _absolute_metrics,
    _carry_metrics,
    _centered_form_correlation,
    _norm_ratio,
    _vector_stats,
)


class PublicAVContinuousDissipationAttenuationAuditTests(unittest.TestCase):
    def test_vector_stats_are_fixed_population_metrics(self) -> None:
        stats = _vector_stats((-2.0, 0.0, 2.0))
        self.assertEqual(4.0, stats["l1"])
        self.assertAlmostEqual(math.sqrt(8.0), stats["l2"])
        self.assertEqual(2.0, stats["linf"])
        self.assertEqual(0.0, stats["mean"])
        self.assertAlmostEqual(math.sqrt(8.0 / 3.0), stats["standard_deviation"])

    def test_norm_zero_rule_is_explicit(self) -> None:
        self.assertEqual(1.0, _norm_ratio(0.0, 0.0))
        with self.assertRaises(PublicAVContinuousDissipationAttenuationError):
            _norm_ratio(1.0, 0.0)

    def test_centered_shape_zero_rules_are_explicit(self) -> None:
        self.assertEqual(1.0, _centered_form_correlation((1.0, 1.0), (2.0, 2.0)))
        self.assertEqual(0.0, _centered_form_correlation((1.0, 1.0), (0.0, 1.0)))
        self.assertAlmostEqual(1.0, _centered_form_correlation((1.0, 2.0), (2.0, 4.0)))

    def test_absolute_metrics_include_norm_ratios_and_shape_only(self) -> None:
        metrics = _absolute_metrics((0.5, 1.0), (1.0, 2.0))
        self.assertAlmostEqual(0.5, metrics["l1_ratio_to_zero_rate"])
        self.assertAlmostEqual(0.5, metrics["l2_ratio_to_zero_rate"])
        self.assertAlmostEqual(0.5, metrics["linf_ratio_to_zero_rate"])
        self.assertAlmostEqual(1.0, metrics["centered_form_correlation_to_zero_rate"])

    def test_carry_metrics_use_zero_carry_and_rate_fresh_references(self) -> None:
        metrics = _carry_metrics(
            (3.0, 1.0), (1.0, 1.0), (5.0, 1.0), (1.0, 1.0)
        )
        self.assertAlmostEqual(0.5, metrics["l2_ratio_to_zero_rate_carry"])
        self.assertAlmostEqual(math.sqrt(2.0), metrics["l2_ratio_to_rate_fresh_field"])
        self.assertIn("constant_energy_fraction_change_from_zero_rate", metrics)

    def test_fixed_axes_claims_and_no_preferred_rate_are_source_constants(self) -> None:
        from pathlib import Path
        source = Path(
            "mcm_field_organism/public_av_continuous_dissipation_attenuation_audit.py"
        ).read_text(encoding="utf-8")
        self.assertIn("DISSIPATION_LEAK_RATES_PER_SECOND", source)
        self.assertIn("TAIL_RESOLUTION_DURATION_TICKS", source)
        self.assertIn('"preferred_rate_selected": False', source)
        self.assertIn('"threshold_defined": False', source)
        self.assertIn('"memory_claim_allowed": False', source)


if __name__ == "__main__":
    unittest.main()
