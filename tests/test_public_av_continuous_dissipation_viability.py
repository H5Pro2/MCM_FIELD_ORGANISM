from __future__ import annotations

from dataclasses import replace
import math
from pathlib import Path
import unittest

import numpy as np

from mcm_field_organism.neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    _advance_projected_activation_afterimage,
    _apply_projected_point_contacts,
)
from mcm_field_organism.public_av_continuous_dissipation_viability import (
    ContinuousDissipationStageOneMeasurement,
    ContinuousDissipationViabilityPoint,
    PublicAVContinuousDissipationViability,
    PublicAVContinuousDissipationViabilityError,
    _continuous_gap,
    public_av_continuous_dissipation_viability_to_jsonable,
)
from mcm_field_organism.public_av_return_resolution_curve import ARM_IDS
from mcm_field_organism.public_av_return_replication_execution import _advance_contact_free
from mcm_field_organism.public_av_return_resolution_dissipation_intervention import DISSIPATION_LEAK_RATES_PER_SECOND
from mcm_field_organism.public_av_return_resolution_tail import TAIL_RESOLUTION_DURATION_TICKS
from mcm_field_organism.public_av_six_arm_field_execution import _sequences
from mcm_field_organism.public_av_two_stage_return_execution import _fresh_field, _steps
from mcm_field_organism.public_media_source_contract import nasa_earthrise_av_source_contract


def _stage(rate):
    return ContinuousDissipationStageOneMeasurement(
        rate, 56, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, "layer", "snapshot"
    )


def _point(rate, duration):
    zero = (0.0,) * 4
    fractions = (0.5, 0.5, 0.5, 0.0)
    digests = ("a", "b", "c", "d")
    return ContinuousDissipationViabilityPoint(
        rate, duration, 56, ARM_IDS, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        zero, zero, zero, zero, fractions, fractions, digests, digests,
    )


def _result():
    return PublicAVContinuousDissipationViability(
        "experiment", "source", "clock", DISSIPATION_LEAK_RATES_PER_SECOND,
        TAIL_RESOLUTION_DURATION_TICKS,
        tuple(_stage(rate) for rate in DISSIPATION_LEAK_RATES_PER_SECOND),
        tuple(_point(rate, duration) for duration in TAIL_RESOLUTION_DURATION_TICKS
              for rate in DISSIPATION_LEAK_RATES_PER_SECOND),
    )


class PublicAVContinuousDissipationViabilityTests(unittest.TestCase):
    def test_zero_rate_runtime_is_exactly_identical(self) -> None:
        path = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")
        sequences = _sequences(path, nasa_earthrise_av_source_contract())
        steps = _steps(sequences, 0, 500_000_000)
        substrate = NeutralLocalFieldSubstrateConfig(1.0)
        afterimage = NeutralFastAfterimageConfig(0.5)
        baseline = run_neutral_asynchronous_field(
            _fresh_field(sequences), sequences, steps, substrate,
            afterimage_config=afterimage,
        )
        zero = run_neutral_asynchronous_field(
            _fresh_field(sequences), sequences, steps, substrate,
            afterimage_config=afterimage,
            dissipation_config=NeutralFieldDissipationConfig(0.0),
        )
        self.assertEqual(baseline.field.layer.digest(), zero.field.layer.digest())
        self.assertEqual(baseline.field.snapshot().digest(), zero.field.snapshot().digest())
        self.assertEqual(baseline.source_support_count, zero.source_support_count)
        baseline_gap = _advance_contact_free(
            baseline.field, 500_000_000, 2_500_000_000, substrate, afterimage
        )
        zero_gap = _continuous_gap(
            zero.field, 500_000_000, 2_500_000_000, substrate, afterimage,
            NeutralFieldDissipationConfig(0.0),
        )
        self.assertEqual(baseline_gap.layer.digest(), zero_gap.layer.digest())
        self.assertEqual(baseline_gap.snapshot().digest(), zero_gap.snapshot().digest())

    def test_same_proportional_term_acts_on_free_activation_and_afterimage(self) -> None:
        activation = np.asarray([1.0, -1.0])
        afterimage = np.asarray([0.5, -0.5])
        eigenvalues = np.zeros(2)
        zero_a, zero_h = _advance_projected_activation_afterimage(
            activation, afterimage, eigenvalues, 2.0, 0.5, 0.0
        )
        leak_a, leak_h = _advance_projected_activation_afterimage(
            activation, afterimage, eigenvalues, 2.0, 0.5, 0.1
        )
        factor = math.exp(-0.2)
        np.testing.assert_allclose(leak_a, factor * zero_a)
        np.testing.assert_allclose(leak_h, factor * zero_h)

    def test_world_contact_integral_contains_the_same_local_leak(self) -> None:
        projected = np.asarray([0.4])
        eigenvectors = np.asarray([[1.0]])
        grouped = [(0, 2.0, 0.8)]
        changed = _apply_projected_point_contacts(
            projected, eigenvectors, grouped, 1.0, 0.1
        )
        retention = math.exp(-2.2)
        expected = retention * 0.4 + (1.0 - retention) * (0.8 / 1.1)
        self.assertAlmostEqual(expected, changed[0])

    def test_dissipation_does_not_select_the_constant_mode(self) -> None:
        state = np.asarray([1.0, 1.0, 1.0, -1.0])
        changed, _ = _advance_projected_activation_afterimage(
            state, np.zeros(4), np.zeros(4), 5.0, 0.5, 0.1
        )
        np.testing.assert_allclose(changed, math.exp(-0.5) * state)

    def test_axes_isolation_claims_and_complete_measurements_are_guarded(self) -> None:
        result = _result()
        self.assertEqual(12, len(result.points))
        self.assertEqual(3, len(result.stage_one_measurements))
        self.assertTrue(all(point.arm_ids == ARM_IDS for point in result.points))
        with self.assertRaises(PublicAVContinuousDissipationViabilityError):
            replace(result, points=result.points[:-1])
        with self.assertRaises(PublicAVContinuousDissipationViabilityError):
            replace(result, meaning_claim_allowed=True)

    def test_json_contains_world_contact_fresh_and_rate_fresh_metrics(self) -> None:
        payload = public_av_continuous_dissipation_viability_to_jsonable(_result())
        self.assertEqual(3, len(payload["stage_one_measurements"]))
        self.assertEqual(12, len(payload["points"]))
        self.assertIn("activation_centered_linf_to_zero", payload["stage_one_measurements"][0])
        self.assertIn("fresh_activation_centered_linf_to_zero", payload["points"][0])
        self.assertIn("carry_activation_centered_linf_to_rate_fresh", payload["points"][0])
        self.assertIn("layer_digests", payload["points"][0])
        self.assertFalse(payload["threshold_defined"])
        self.assertFalse(payload["ai_claim_allowed"])


if __name__ == "__main__":
    unittest.main()
