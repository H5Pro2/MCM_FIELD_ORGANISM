from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_two_stage_return_runner import (
    PublicAVTwoStageReturnRunnerError,
    execute_public_av_two_stage_return_runner,
    public_av_two_stage_return_runner_json_value,
    public_av_two_stage_return_runner_public_roles,
    wire_public_av_two_stage_return_runner,
)


class PublicAVTwoStageReturnRunnerTests(unittest.TestCase):
    def test_exact_global_intervals_are_wired_for_both_arms(self) -> None:
        wiring = wire_public_av_two_stage_return_runner()
        self.assertEqual(2, len(wiring.arms))
        for arm in wiring.arms:
            self.assertEqual((0, 500_000_000), arm.stage_one_interval_ticks)
            self.assertEqual((500_000_000, 600_000_000), arm.resolution_interval_ticks)
            self.assertEqual((600_000_000, 1_100_000_000), arm.stage_two_interval_ticks)
            self.assertEqual(600_000_000, arm.stage_two_tick_offset)

    def test_state_modes_are_disjoint_on_the_same_stage_two_schedule(self) -> None:
        wiring = wire_public_av_two_stage_return_runner()
        continued, baseline = wiring.arms
        self.assertTrue(continued.carry_field_state_to_stage_two)
        self.assertFalse(continued.fresh_field_before_stage_two)
        self.assertFalse(baseline.carry_field_state_to_stage_two)
        self.assertTrue(baseline.fresh_field_before_stage_two)
        self.assertEqual(continued.stage_two_interval_ticks, baseline.stage_two_interval_ticks)
        self.assertEqual(continued.stage_two_sequence_id, baseline.stage_two_sequence_id)

    def test_execution_and_release_flags_are_blocked(self) -> None:
        wiring = wire_public_av_two_stage_return_runner()
        with self.assertRaisesRegex(PublicAVTwoStageReturnRunnerError, "not released"):
            execute_public_av_two_stage_return_runner(wiring)
        with self.assertRaisesRegex(PublicAVTwoStageReturnRunnerError, "cannot release"):
            replace(wiring, field_run_allowed=True)

    def test_json_and_roles_exclude_payloads_and_content_claims(self) -> None:
        wiring = wire_public_av_two_stage_return_runner()
        encoded = repr(public_av_two_stage_return_runner_json_value(wiring))
        self.assertIn("fresh_stage_two_baseline", encoded)
        forbidden = {"raw_samples", "pixels", "label", "reward", "memory_score", "field_state"}
        self.assertTrue(forbidden.isdisjoint(public_av_two_stage_return_runner_public_roles()))


if __name__ == "__main__":
    unittest.main()
