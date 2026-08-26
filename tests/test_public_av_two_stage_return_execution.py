from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_two_stage_return_execution import (
    PublicAVTwoStageReturnArmResult,
    PublicAVTwoStageReturnExecution,
    PublicAVTwoStageReturnExecutionError,
    public_av_two_stage_return_execution_public_roles,
    shift_receptor_time_sequences,
)
from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_time_alignment import OrganismTimedReceptorFrame, ReceptorTimeSequence


def _sequence() -> ReceptorTimeSequence:
    frame = ReceptorContactFrame("auditory", "geometry.test", "snapshot.test", "source.test", 0, 1, ("carrier.test",), (0.25,))
    timed = OrganismTimedReceptorFrame(frame, CommonFieldTime("public.media.pts_ns", 0, 10))
    return ReceptorTimeSequence("auditory", "geometry.test", "public.media.pts_ns", (timed,))


def _arm(arm_id: str, carry: bool) -> PublicAVTwoStageReturnArmResult:
    return PublicAVTwoStageReturnArmResult(
        arm_id, 1, 1, "a" * 64, "b" * 64 if carry else None, "c" * 64, "d" * 64,
        (0.1,), (0.2,), carry, not carry,
    )


class PublicAVTwoStageReturnExecutionTests(unittest.TestCase):
    def test_stage_two_shift_changes_only_organism_time(self) -> None:
        original = _sequence()
        shifted = shift_receptor_time_sequences((original,), 600_000_000)[0]
        self.assertIs(original.frames[0].frame, shifted.frames[0].frame)
        self.assertEqual(600_000_000, shifted.frames[0].field_time.window_start_tick)
        self.assertEqual(600_000_010, shifted.frames[0].field_time.window_end_tick)

    def test_non_preregistered_offset_is_rejected(self) -> None:
        with self.assertRaisesRegex(PublicAVTwoStageReturnExecutionError, "offset"):
            shift_receptor_time_sequences((_sequence(),), 500_000_000)

    def test_fresh_baseline_has_no_pre_receptor_snapshot(self) -> None:
        self.assertIsNone(_arm("fresh_stage_two_baseline", False).post_resolution_snapshot_digest)

    def test_result_keeps_claims_and_payloads_blocked(self) -> None:
        result = PublicAVTwoStageReturnExecution(
            "runner", "source", "clock", 500_000_000, 100_000_000,
            (_arm("continued_field", True), _arm("fresh_stage_two_baseline", False)),
            0.1, 0.2, False, False,
        )
        with self.assertRaisesRegex(PublicAVTwoStageReturnExecutionError, "cannot retain"):
            replace(result, memory_claim_allowed=True)

    def test_public_roles_exclude_source_payloads_and_content_scores(self) -> None:
        forbidden = {"samples", "pixels", "metadata", "label", "reward", "memory_score", "meaning"}
        self.assertTrue(forbidden.isdisjoint(public_av_two_stage_return_execution_public_roles()))


if __name__ == "__main__":
    unittest.main()
