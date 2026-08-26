from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_formation_s1fe_endpoint_capture_contract import (
    E1FormationS1FEEndpointCaptureContractError,
    audit_e1_formation_s1fe_endpoint_capture_contract,
)


class E1FormationS1FEEndpointCaptureContractTests(unittest.TestCase):
    def test_existing_three_by_five_result_inventory_is_bound(self) -> None:
        contract = audit_e1_formation_s1fe_endpoint_capture_contract()
        self.assertEqual(("r2", "r4", "r8"), tuple(
            role for role, _ in contract.source_refinements
        ))
        self.assertEqual(5, len(contract.source_formation_arms))
        self.assertEqual(15, contract.required_source_result_count)
        self.assertEqual(
            tuple(contract.source_formation_arms),
            tuple(source for source, _ in contract.role_map),
        )

    def test_target_mapping_matches_s1fc_s1fd_schema(self) -> None:
        contract = audit_e1_formation_s1fe_endpoint_capture_contract()
        self.assertEqual(
            (
                "active-ab",
                "active-ba",
                "identity-ab",
                "formation-ablated-ab",
                "formation-ablated-ba",
            ),
            tuple(target for _, target in contract.role_map),
        )
        self.assertIn("ordered_edge_ids", contract.target_state_vector_schema)
        self.assertIn(
            "source_formation_result_digest", contract.target_state_vector_schema
        )
        self.assertIn("resource_budget_error", contract.target_state_vector_schema)

    def test_capture_point_is_atomic_single_use_and_before_probe(self) -> None:
        contract = audit_e1_formation_s1fe_endpoint_capture_contract()
        self.assertTrue(contract.atomic_capture_required)
        self.assertTrue(contract.single_use_capture_required)
        self.assertTrue(contract.object_separation_required)
        self.assertEqual(
            "after-each-formation-result-and-before-any-probe-handoff",
            contract.capture_timing_rule,
        )

    def test_contract_authorizes_only_later_adapter_implementation(self) -> None:
        contract = audit_e1_formation_s1fe_endpoint_capture_contract()
        self.assertTrue(contract.capture_adapter_implementation_permitted)
        self.assertFalse(contract.formation_execution_permitted)
        self.assertFalse(contract.capture_execution_permitted)
        self.assertFalse(contract.probe_execution_permitted)
        self.assertFalse(contract.persistence_permitted)
        self.assertFalse(contract.memory_claim_permitted)

    def test_contract_is_deterministic_and_tamper_evident(self) -> None:
        first = audit_e1_formation_s1fe_endpoint_capture_contract()
        second = audit_e1_formation_s1fe_endpoint_capture_contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(E1FormationS1FEEndpointCaptureContractError):
            replace(first, capture_execution_permitted=True)

    def test_audit_does_not_run_capture_formation_probe_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_formation_s1fe_endpoint_capture_contract
        )
        for forbidden in (
            "run_prepared_real_formation_arm_in_memory(",
            "run_e1_asynchronous_field(",
            "run_e1_common_probe_real_probe_wrapper(",
            "evaluate_e1_formation_s1fd_state_convergence(",
            "write_text(",
            "write_bytes(",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
