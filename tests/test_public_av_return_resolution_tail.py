from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_resolution_curve import ARM_IDS
from mcm_field_organism.public_av_return_resolution_tail import (
    TAIL_RESOLUTION_DURATION_TICKS,
    PublicAVReturnResolutionTail,
    PublicAVReturnResolutionTailError,
    PublicAVReturnResolutionTailPoint,
    _tail_arm_start_field,
    public_av_return_resolution_tail_to_jsonable,
)
from tests.test_shared_field_component_intervention import completed_field


def _point(duration: int) -> PublicAVReturnResolutionTailPoint:
    return PublicAVReturnResolutionTailPoint(
        duration, 56, 56, "stage-one", ARM_IDS,
        (0.1, 0.1, 0.0, 0.0),
        (0.1, 0.05, 0.02, 0.0),
        ("a", "b", "c", "d"),
        ("e", "f", "g", "h"),
    )


def _tail() -> PublicAVReturnResolutionTail:
    return PublicAVReturnResolutionTail(
        "tail", "source", "clock", TAIL_RESOLUTION_DURATION_TICKS,
        tuple(_point(duration) for duration in TAIL_RESOLUTION_DURATION_TICKS),
    )


class PublicAVReturnResolutionTailTests(unittest.TestCase):
    def test_tail_axis_and_four_arms_are_fixed(self) -> None:
        self.assertEqual(
            (2_000_000_000, 5_000_000_000, 10_000_000_000, 20_000_000_000),
            TAIL_RESOLUTION_DURATION_TICKS,
        )
        self.assertEqual(4, len(ARM_IDS))

    def test_tail_rejects_changed_axis_and_claims(self) -> None:
        tail = _tail()
        with self.assertRaises(PublicAVReturnResolutionTailError):
            replace(tail, resolution_duration_ticks=TAIL_RESOLUTION_DURATION_TICKS[:-1])
        with self.assertRaises(PublicAVReturnResolutionTailError):
            replace(tail, organization_claim_allowed=True)

    def test_json_keeps_claim_boundaries_and_complete_points(self) -> None:
        payload = public_av_return_resolution_tail_to_jsonable(_tail())
        self.assertEqual(list(TAIL_RESOLUTION_DURATION_TICKS), payload["resolution_duration_ticks"])
        self.assertEqual(4, len(payload["points"]))
        self.assertTrue(all(len(point["arm_ids"]) == 4 for point in payload["points"]))
        self.assertFalse(payload["memory_claim_allowed"])
        self.assertFalse(payload["organization_claim_allowed"])

    def test_carry_copies_are_isolated_and_fresh_control_is_independent(self) -> None:
        stage_one = completed_field()
        starts = {
            arm_id: _tail_arm_start_field(stage_one, arm_id, completed_field)
            for arm_id in ARM_IDS
        }
        self.assertTrue(all(field is not stage_one for field in starts.values()))
        self.assertEqual(4, len({id(field) for field in starts.values()}))
        self.assertEqual(4, len({id(field.layer) for field in starts.values()}))
        self.assertTrue(all(
            field.snapshot().digest() == stage_one.snapshot().digest()
            for field in starts.values()
        ))


if __name__ == "__main__":
    unittest.main()
