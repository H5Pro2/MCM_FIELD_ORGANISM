from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_resolution_curve import ARM_IDS
from mcm_field_organism.public_av_return_resolution_mode_audit import (
    PublicAVReturnResolutionModeAudit,
    PublicAVReturnResolutionModeAuditError,
    PublicAVReturnResolutionModeAuditPoint,
    _mode_metrics,
    public_av_return_resolution_mode_audit_to_jsonable,
)
from mcm_field_organism.public_av_return_resolution_tail import TAIL_RESOLUTION_DURATION_TICKS


def _point(duration: int) -> PublicAVReturnResolutionModeAuditPoint:
    zero = (0.0, 0.0, 0.0, 0.0)
    fraction = (0.5, 0.5, 0.0, 0.0)
    return PublicAVReturnResolutionModeAuditPoint(
        duration, 56, 56, ARM_IDS, zero, zero, zero, zero, fraction, fraction
    )


def _audit() -> PublicAVReturnResolutionModeAudit:
    return PublicAVReturnResolutionModeAudit(
        "audit", "source", "clock", TAIL_RESOLUTION_DURATION_TICKS,
        tuple(_point(duration) for duration in TAIL_RESOLUTION_DURATION_TICKS),
    )


class PublicAVReturnResolutionModeAuditTests(unittest.TestCase):
    def test_duration_axis_arms_and_measure_are_fixed(self) -> None:
        audit = _audit()
        self.assertEqual(TAIL_RESOLUTION_DURATION_TICKS, audit.resolution_duration_ticks)
        self.assertEqual(ARM_IDS, audit.points[0].arm_ids)
        self.assertEqual("l2_energy_fraction", audit.constant_component_measure)

    def test_mode_metrics_separate_constant_and_centered_components(self) -> None:
        mean, centered, fraction = _mode_metrics((3.0, 3.0), (1.0, 1.0))
        self.assertEqual(2.0, mean)
        self.assertEqual(0.0, centered)
        self.assertEqual(1.0, fraction)
        mean, centered, fraction = _mode_metrics((2.0, 0.0), (1.0, 1.0))
        self.assertEqual(0.0, mean)
        self.assertEqual(1.0, centered)
        self.assertEqual(0.0, fraction)

    def test_audit_rejects_axis_measure_and_claim_changes(self) -> None:
        audit = _audit()
        with self.assertRaises(PublicAVReturnResolutionModeAuditError):
            replace(audit, resolution_duration_ticks=TAIL_RESOLUTION_DURATION_TICKS[:-1])
        with self.assertRaises(PublicAVReturnResolutionModeAuditError):
            replace(audit, constant_component_measure="linf_fraction")
        with self.assertRaises(PublicAVReturnResolutionModeAuditError):
            replace(audit, memory_claim_allowed=True)

    def test_json_contains_all_measurement_fields_without_claim_release(self) -> None:
        payload = public_av_return_resolution_mode_audit_to_jsonable(_audit())
        self.assertEqual(4, len(payload["points"]))
        expected = {
            "activation_mean_delta_to_fresh",
            "afterimage_mean_delta_to_fresh",
            "activation_centered_linf_to_fresh",
            "afterimage_centered_linf_to_fresh",
            "activation_constant_energy_fraction",
            "afterimage_constant_energy_fraction",
        }
        self.assertTrue(expected.issubset(payload["points"][0]))
        self.assertFalse(payload["threshold_defined"])
        self.assertFalse(payload["ai_claim_allowed"])


if __name__ == "__main__":
    unittest.main()
