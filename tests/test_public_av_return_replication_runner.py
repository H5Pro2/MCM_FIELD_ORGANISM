from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_runner import (
    PublicAVReturnReplicationRunnerError,
    execute_public_av_return_replication_runner,
    public_av_return_replication_runner_json_value,
    public_av_return_replication_runner_public_roles,
    wire_public_av_return_replication_runner,
)


class PublicAVReturnReplicationRunnerTests(unittest.TestCase):
    def test_all_six_arms_and_fixed_intervals_are_wired(self) -> None:
        wiring = wire_public_av_return_replication_runner()
        self.assertEqual(6, len(wiring.arms))
        self.assertTrue(wiring.all_arms_structurally_supported)
        for arm in wiring.arms:
            self.assertEqual((0, 500_000_000), arm.stage_one_interval_ticks)
            self.assertEqual((500_000_000, 600_000_000), arm.resolution_interval_ticks)
            self.assertEqual((600_000_000, 1_100_000_000), arm.stage_two_interval_ticks)

    def test_component_interventions_map_to_observer_contracts(self) -> None:
        by_id = {arm.arm_id: arm for arm in wire_public_av_return_replication_runner().arms}
        self.assertEqual("reset_afterimage_preserve_activation", by_id["control.activation_only_carry"].component_intervention_mode)
        self.assertEqual("reset_activation_preserve_afterimage", by_id["control.afterimage_only_carry"].component_intervention_mode)
        self.assertIsNone(by_id["return.continued.full_state"].component_intervention_mode)

    def test_permutation_and_withheld_contracts_are_distinct(self) -> None:
        by_id = {arm.arm_id: arm for arm in wire_public_av_return_replication_runner().arms}
        permuted = by_id["control.stage_two_order_permuted"]
        withheld = by_id["control.stage_two_sequence_withheld"]
        self.assertEqual("permuted_reduced_sequence", permuted.stage_two_contact_mode)
        self.assertIsNotNone(permuted.permutation_contract_digest)
        self.assertIsNotNone(permuted.stage_two_sequence_digest)
        self.assertEqual("withheld_contact_free", withheld.stage_two_contact_mode)
        self.assertIsNone(withheld.stage_two_sequence_digest)

    def test_execution_and_release_flags_remain_blocked(self) -> None:
        wiring = wire_public_av_return_replication_runner()
        with self.assertRaisesRegex(PublicAVReturnReplicationRunnerError, "not released"):
            execute_public_av_return_replication_runner(wiring)
        with self.assertRaisesRegex(PublicAVReturnReplicationRunnerError, "cannot release"):
            replace(wiring, replication_run_allowed=True)

    def test_json_and_roles_exclude_payloads_and_claim_scores(self) -> None:
        wiring = wire_public_av_return_replication_runner()
        encoded = repr(public_av_return_replication_runner_json_value(wiring))
        self.assertIn("stage_two_order_permuted", encoded)
        forbidden = {"samples", "pixels", "label", "reward", "memory_score", "organization_score", "field_state"}
        self.assertTrue(forbidden.isdisjoint(public_av_return_replication_runner_public_roles()))


if __name__ == "__main__":
    unittest.main()
