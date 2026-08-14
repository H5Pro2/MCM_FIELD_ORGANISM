from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_resolution_curve import ARM_IDS
from mcm_field_organism.public_av_return_resolution_dissipation_intervention import (
    DISSIPATION_LEAK_RATES_PER_SECOND,
    PublicAVReturnResolutionDissipationError,
    PublicAVReturnResolutionDissipationIntervention,
    PublicAVReturnResolutionDissipationPoint,
    _apply_content_neutral_leak,
    public_av_return_resolution_dissipation_to_jsonable,
)
from mcm_field_organism.public_av_return_resolution_tail import TAIL_RESOLUTION_DURATION_TICKS
from mcm_field_organism.public_av_two_stage_return_execution import _fresh_field
from mcm_field_organism.public_av_six_arm_field_execution import _sequences
from mcm_field_organism.public_media_source_contract import nasa_earthrise_av_source_contract
from pathlib import Path


def _point(rate: float, duration: int) -> PublicAVReturnResolutionDissipationPoint:
    zero = (0.0,) * 4
    fractions = (0.5, 0.5, 0.5, 0.0)
    digests = ("a", "b", "c", "d")
    return PublicAVReturnResolutionDissipationPoint(
        rate, duration, 56, 56, ARM_IDS, zero, zero, zero, zero,
        fractions, fractions, digests, digests,
    )


def _result() -> PublicAVReturnResolutionDissipationIntervention:
    return PublicAVReturnResolutionDissipationIntervention(
        "experiment", "source", "clock", DISSIPATION_LEAK_RATES_PER_SECOND,
        TAIL_RESOLUTION_DURATION_TICKS,
        tuple(_point(rate, duration) for rate in DISSIPATION_LEAK_RATES_PER_SECOND
              for duration in TAIL_RESOLUTION_DURATION_TICKS),
    )


class PublicAVReturnResolutionDissipationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        media = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")
        sequences = _sequences(media, nasa_earthrise_av_source_contract())
        cls.field = _fresh_field(sequences)

    def test_rates_and_duration_axis_are_fixed(self) -> None:
        self.assertEqual((0.0, 0.05, 0.10), DISSIPATION_LEAK_RATES_PER_SECOND)
        result = _result()
        self.assertEqual(TAIL_RESOLUTION_DURATION_TICKS, result.resolution_duration_ticks)
        self.assertEqual(12, len(result.points))
        self.assertTrue(all(point.arm_ids == ARM_IDS for point in result.points))

    def test_zero_leak_is_digest_and_metric_identity(self) -> None:
        field = self.field
        changed = _apply_content_neutral_leak(field, 0.0, 20.0)
        self.assertIs(field, changed)
        self.assertEqual(field.layer.digest(), changed.layer.digest())
        self.assertEqual(
            tuple((n.activation, n.afterimage) for n in field.layer.neurons),
            tuple((n.activation, n.afterimage) for n in changed.layer.neurons),
        )

    def test_positive_leak_only_scales_local_field_components(self) -> None:
        neurons = tuple(replace(n, activation=0.8, afterimage=-0.4) for n in self.field.layer.neurons)
        field = replace(self.field, layer=replace(self.field.layer, neurons=neurons))
        changed = _apply_content_neutral_leak(field, 0.05, 2.0)
        factor = __import__("math").exp(-0.1)
        for before, after in zip(field.layer.neurons, changed.layer.neurons, strict=True):
            self.assertAlmostEqual(before.activation * factor, after.activation)
            self.assertAlmostEqual(before.afterimage * factor, after.afterimage)
            self.assertEqual(before.perception, after.perception)
            self.assertEqual(before.position, after.position)

    def test_leak_outputs_are_independent_and_unregistered_rate_is_rejected(self) -> None:
        first = _apply_content_neutral_leak(self.field, 0.05, 2.0)
        second = _apply_content_neutral_leak(self.field, 0.10, 2.0)
        self.assertIsNot(first, second)
        self.assertIsNot(first.layer, second.layer)
        with self.assertRaises(PublicAVReturnResolutionDissipationError):
            _apply_content_neutral_leak(self.field, 0.075, 2.0)

    def test_claims_axes_scope_and_complete_points_are_guarded(self) -> None:
        result = _result()
        with self.assertRaises(PublicAVReturnResolutionDissipationError):
            replace(result, leak_rates_per_second=(0.0, 0.05))
        with self.assertRaises(PublicAVReturnResolutionDissipationError):
            replace(result, points=result.points[:-1])
        with self.assertRaises(PublicAVReturnResolutionDissipationError):
            replace(result, memory_claim_allowed=True)

    def test_json_has_complete_metrics_and_disabled_claims(self) -> None:
        payload = public_av_return_resolution_dissipation_to_jsonable(_result())
        self.assertEqual([0.0, 0.05, 0.1], payload["leak_rates_per_second"])
        self.assertEqual(12, len(payload["points"]))
        expected = {
            "activation_mean_delta_to_fresh", "afterimage_mean_delta_to_fresh",
            "activation_centered_linf_to_fresh", "afterimage_centered_linf_to_fresh",
            "activation_constant_energy_fraction", "afterimage_constant_energy_fraction",
            "layer_digests", "snapshot_digests",
        }
        self.assertTrue(expected.issubset(payload["points"][0]))
        self.assertFalse(payload["threshold_defined"])
        self.assertFalse(payload["ai_claim_allowed"])


if __name__ == "__main__":
    unittest.main()
