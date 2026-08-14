from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_runner import (
    PublicAVReturnReplicationRepeatabilityRunnerError,
    execute_public_av_return_replication_repeatability_runner,
    public_av_return_replication_repeatability_runner_json_value,
    public_av_return_replication_repeatability_runner_public_roles,
    wire_public_av_return_replication_repeatability_runner,
)


class PublicAVReturnReplicationRepeatabilityRunnerTests(unittest.TestCase):
    def test_three_ordered_repeat_slots_are_structurally_wired(self) -> None:
        wiring = wire_public_av_return_replication_repeatability_runner()
        self.assertEqual((1, 2, 3), tuple(item.repeat_index for item in wiring.repeat_slots))
        self.assertTrue(wiring.all_repeat_slots_structurally_wired)
        self.assertTrue(wiring.runner_wiring_implementation_allowed)

    def test_each_slot_requires_fresh_instance_and_separate_preflight(self) -> None:
        wiring = wire_public_av_return_replication_repeatability_runner()
        for slot in wiring.repeat_slots:
            self.assertTrue(slot.fresh_runner_instance_required)
            self.assertTrue(slot.fresh_field_at_repeat_start)
            self.assertTrue(slot.separate_start_preflight_required)
            self.assertFalse(slot.cross_repeat_state_carry_allowed)
            self.assertFalse(slot.prior_execution_receipt_reusable)

    def test_contract_identity_is_equal_across_slots(self) -> None:
        wiring = wire_public_av_return_replication_repeatability_runner()
        identities = {
            (slot.base_runner_id, slot.permutation_contract_digest, slot.fixed_field_parameters, slot.arm_ids)
            for slot in wiring.repeat_slots
        }
        self.assertEqual(1, len(identities))

    def test_execution_loop_and_claims_are_constructively_blocked(self) -> None:
        wiring = wire_public_av_return_replication_repeatability_runner()
        with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityRunnerError, "not released"):
            execute_public_av_return_replication_repeatability_runner(wiring)
        with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityRunnerError, "cannot release"):
            replace(wiring, automatic_repeat_loop_available=True)
        with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityRunnerError, "cannot release"):
            replace(wiring, repeatability_run_allowed=True)
        with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityRunnerError, "cannot release"):
            replace(wiring, stability_threshold_defined=True)

    def test_json_and_roles_exclude_payloads_and_claim_scores(self) -> None:
        wiring = wire_public_av_return_replication_repeatability_runner()
        encoded = repr(public_av_return_replication_repeatability_runner_json_value(wiring))
        self.assertIn("repeat_index", encoded)
        forbidden = {"samples", "pixels", "memory_score", "organization_score", "reward", "target_topology"}
        self.assertTrue(forbidden.isdisjoint(public_av_return_replication_repeatability_runner_public_roles()))


if __name__ == "__main__":
    unittest.main()
