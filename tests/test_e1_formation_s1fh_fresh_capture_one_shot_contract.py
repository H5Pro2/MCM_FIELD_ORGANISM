from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_formation_s1fh_fresh_capture_one_shot_contract import (
    E1FormationS1FHFreshCaptureOneShotContractError,
    prepare_e1_formation_s1fh_fresh_capture_one_shot_contract,
)


class E1FormationS1FHFreshCaptureOneShotContractTests(unittest.TestCase):
    def test_exact_fifteen_arm_budget_is_bound(self) -> None:
        contract = prepare_e1_formation_s1fh_fresh_capture_one_shot_contract()
        self.assertEqual(15, contract.formation_arm_count)
        self.assertEqual(14_000, contract.maximum_formation_field_steps)
        self.assertEqual((1, 1), (contract.capture_count, contract.evaluation_count))
        self.assertEqual(15, contract.retained_state_count)
        self.assertEqual(2_175, contract.retained_binding_count_upper_bound)
        self.assertEqual((84, 145), (contract.field_node_count, contract.state_edge_count))

    def test_fresh_resource_and_owner_gates_are_required(self) -> None:
        contract = prepare_e1_formation_s1fh_fresh_capture_one_shot_contract()
        self.assertTrue(contract.fresh_preflight_required)
        self.assertTrue(contract.immediate_pre_execution_preflight_required)
        self.assertTrue(contract.explicit_new_owner_authorization_required)
        self.assertEqual(4 * 1024**3, contract.minimum_free_memory_bytes)
        self.assertEqual(900.0, contract.maximum_runtime_seconds)
        self.assertFalse(contract.owner_authorization_present)
        self.assertFalse(contract.execution_permitted)

    def test_probe_persistence_retry_and_historical_reuse_are_closed(self) -> None:
        contract = prepare_e1_formation_s1fh_fresh_capture_one_shot_contract()
        self.assertFalse(contract.probe_execution_permitted)
        self.assertFalse(contract.persistence_permitted)
        self.assertFalse(contract.automatic_retry_permitted)
        self.assertFalse(contract.posthoc_parameter_change_permitted)
        self.assertFalse(contract.historical_artifact_reuse_permitted)
        self.assertFalse(contract.historical_authorization_reuse_permitted)

    def test_all_research_claims_remain_closed(self) -> None:
        contract = prepare_e1_formation_s1fh_fresh_capture_one_shot_contract()
        self.assertFalse(contract.research_decision_permitted)
        self.assertFalse(contract.memory_claim_permitted)
        self.assertFalse(contract.field_time_claim_permitted)
        self.assertFalse(contract.organization_claim_permitted)
        self.assertFalse(contract.semantic_claim_permitted)
        self.assertFalse(contract.self_regulation_claim_permitted)
        self.assertFalse(contract.ai_claim_permitted)

    def test_contract_is_deterministic_and_tamper_evident(self) -> None:
        first = prepare_e1_formation_s1fh_fresh_capture_one_shot_contract()
        second = prepare_e1_formation_s1fh_fresh_capture_one_shot_contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(E1FormationS1FHFreshCaptureOneShotContractError):
            replace(first, authorized_execution_count=1)

    def test_prepare_calls_no_formation_capture_probe_or_writer(self) -> None:
        source = inspect.getsource(
            prepare_e1_formation_s1fh_fresh_capture_one_shot_contract
        )
        for forbidden in (
            "consume_prepared_full_formation(",
            "run_small_five_arm_formation_in_memory(",
            "capture_e1_formation_s1ff_in_memory(",
            "evaluate_e1_formation_s1fd_state_convergence(",
            "run_full_persistent_probe(",
            "write_text(",
            "write_bytes(",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
