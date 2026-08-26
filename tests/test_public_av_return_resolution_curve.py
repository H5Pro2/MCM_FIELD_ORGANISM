from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_resolution_curve import (
    ARM_IDS,
    RESOLUTION_DURATION_TICKS,
    PublicAVReturnResolutionCurve,
    PublicAVReturnResolutionCurveError,
    PublicAVReturnResolutionCurvePoint,
    _independent_arm_start_field,
    _shift_sequences,
    public_av_return_resolution_curve_to_jsonable,
)
from tests.test_shared_field_component_intervention import completed_field


def _point(duration: int) -> PublicAVReturnResolutionCurvePoint:
    return PublicAVReturnResolutionCurvePoint(
        resolution_duration_ticks=duration,
        stage_one_event_count=56,
        stage_two_event_count=56,
        stage_one_snapshot_digest="stage-one",
        arm_ids=ARM_IDS,
        activation_linf_to_fresh=(0.1, 0.1, 0.0, 0.0),
        afterimage_linf_to_fresh=(0.1, 0.05, 0.02, 0.0),
        layer_digests=("a", "b", "c", "d"),
        snapshot_digests=("e", "f", "g", "h"),
    )


class PublicAVReturnResolutionCurveTests(unittest.TestCase):
    def test_duration_axis_and_arms_are_fixed(self) -> None:
        self.assertEqual(
            (0, 25_000_000, 50_000_000, 100_000_000, 200_000_000, 500_000_000, 1_000_000_000),
            RESOLUTION_DURATION_TICKS,
        )
        self.assertEqual(4, len(ARM_IDS))

    def test_curve_rejects_changed_axis_and_claims(self) -> None:
        curve = PublicAVReturnResolutionCurve(
            experiment_id="curve",
            source_id="source",
            clock_id="clock",
            resolution_duration_ticks=RESOLUTION_DURATION_TICKS,
            points=tuple(_point(duration) for duration in RESOLUTION_DURATION_TICKS),
        )
        with self.assertRaises(PublicAVReturnResolutionCurveError):
            replace(curve, resolution_duration_ticks=RESOLUTION_DURATION_TICKS[:-1])
        with self.assertRaises(PublicAVReturnResolutionCurveError):
            replace(curve, memory_claim_allowed=True)

    def test_json_exposes_measurements_without_claim_score(self) -> None:
        curve = PublicAVReturnResolutionCurve(
            experiment_id="curve",
            source_id="source",
            clock_id="clock",
            resolution_duration_ticks=RESOLUTION_DURATION_TICKS,
            points=tuple(_point(duration) for duration in RESOLUTION_DURATION_TICKS),
        )
        payload = public_av_return_resolution_curve_to_jsonable(curve)
        self.assertEqual(list(RESOLUTION_DURATION_TICKS), payload["resolution_duration_ticks"])
        self.assertNotIn("memory_score", repr(payload))
        self.assertFalse(payload["memory_claim_allowed"])

    def test_shift_preserves_frames_and_changes_only_time(self) -> None:
        from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
        from mcm_field_organism.receptor_time_alignment import OrganismTimedReceptorFrame, ReceptorTimeSequence

        frame = ReceptorContactFrame(
            "auditory", "geometry.test", "snapshot.test", "source.test", 0, 1, ("carrier.test",), (0.25,)
        )
        sequences = (ReceptorTimeSequence(
            "auditory",
            "geometry.test",
            "public.media.pts_ns",
            (OrganismTimedReceptorFrame(frame, CommonFieldTime("public.media.pts_ns", 0, 10)),),
        ),)
        shifted = _shift_sequences(sequences, 725_000_000)
        for before, after in zip(sequences, shifted, strict=True):
            self.assertEqual(tuple(item.frame for item in before.frames), tuple(item.frame for item in after.frames))
            self.assertEqual(
                tuple(item.field_time.window_start_tick + 725_000_000 for item in before.frames),
                tuple(item.field_time.window_start_tick for item in after.frames),
            )

    def test_carry_arms_receive_digest_identical_independent_copies(self) -> None:
        stage_one = completed_field()
        starts = tuple(
            _independent_arm_start_field(stage_one, arm_id, completed_field)
            for arm_id in ARM_IDS[:-1]
        )
        self.assertTrue(all(item is not stage_one for item in starts))
        self.assertEqual(len(starts), len({id(item) for item in starts}))
        self.assertTrue(all(item.snapshot().digest() == stage_one.snapshot().digest() for item in starts))
        self.assertTrue(all(item.layer is not stage_one.layer for item in starts))
        self.assertEqual(len(starts), len({id(item.layer) for item in starts}))

    def test_arm_start_fields_are_order_independent_and_fresh_control_is_fresh(self) -> None:
        stage_one = completed_field()
        fresh_fields = []

        def fresh_factory():
            fresh = completed_field()
            fresh_fields.append(fresh)
            return fresh

        forward = {
            arm_id: _independent_arm_start_field(stage_one, arm_id, fresh_factory)
            for arm_id in ARM_IDS
        }
        reverse = {
            arm_id: _independent_arm_start_field(stage_one, arm_id, fresh_factory)
            for arm_id in reversed(ARM_IDS)
        }
        self.assertEqual(
            {arm_id: field.snapshot().digest() for arm_id, field in forward.items()},
            {arm_id: field.snapshot().digest() for arm_id, field in reverse.items()},
        )
        self.assertIs(forward["return.fresh_stage_two"], fresh_fields[0])
        self.assertIs(reverse["return.fresh_stage_two"], fresh_fields[1])
        self.assertIsNot(forward["return.fresh_stage_two"], stage_one)


if __name__ == "__main__":
    unittest.main()
