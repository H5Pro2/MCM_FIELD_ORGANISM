from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_formation_s1fc_state_convergence_contract import (
    E1FormationS1FCStateConvergenceContractError,
    audit_e1_formation_s1fc_state_convergence_contract,
)


class E1FormationS1FCStateConvergenceContractTests(unittest.TestCase):
    def test_contract_requires_fifteen_canonical_state_vectors(self) -> None:
        contract = audit_e1_formation_s1fc_state_convergence_contract()
        self.assertEqual(15, contract.required_state_vector_count)
        self.assertEqual(3, len(contract.refinements))
        self.assertEqual(5, len(contract.formation_roles))
        self.assertIn("ordered_edge_ids", contract.state_vector_schema)
        self.assertIn("ordered_binding_vector", contract.state_vector_schema)

    def test_ab_ba_and_order_convergence_are_separate(self) -> None:
        contract = audit_e1_formation_s1fc_state_convergence_contract()
        for metric in (
            "active-ab-coarse-fine-linf",
            "active-ba-coarse-fine-linf",
            "active-order-coarse-fine-linf",
        ):
            self.assertIn(metric, contract.derived_metrics)
        self.assertIn("active-ab-active-ba-and-order", contract.convergence_rule)

    def test_identity_ablation_and_resource_controls_are_bound(self) -> None:
        contract = audit_e1_formation_s1fc_state_convergence_contract()
        self.assertIn("identity-ab", contract.formation_roles)
        self.assertIn("formation-ablated-ab", contract.formation_roles)
        self.assertIn("formation-ablated-ba", contract.formation_roles)
        self.assertTrue(contract.resource_balance_must_hold_per_state)
        self.assertEqual(1e-12, contract.absolute_control_tolerance)

    def test_ec46_is_not_replaced_or_changed(self) -> None:
        contract = audit_e1_formation_s1fc_state_convergence_contract()
        self.assertFalse(contract.ec46_probe_contract_replaced)
        self.assertFalse(contract.ec46_threshold_changed)
        self.assertEqual(0.01, contract.relative_refinement_limit)

    def test_contract_is_closed_deterministic_and_tamper_evident(self) -> None:
        first = audit_e1_formation_s1fc_state_convergence_contract()
        second = audit_e1_formation_s1fc_state_convergence_contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        self.assertFalse(first.field_execution_permitted)
        self.assertFalse(first.real_state_capture_permitted)
        self.assertFalse(first.memory_claim_permitted)
        with self.assertRaises(E1FormationS1FCStateConvergenceContractError):
            replace(first, field_execution_permitted=True)

    def test_audit_does_not_run_formation_probe_decider_or_writer(self) -> None:
        source = inspect.getsource(audit_e1_formation_s1fc_state_convergence_contract)
        for forbidden in (
            "run_prepared_real_formation_arm_in_memory(",
            "run_e1_asynchronous_field(",
            "run_e1_common_probe_real_probe_wrapper(",
            "advance_frozen_e1_fast_shared_field_transient(",
            "decide_common_probe_evidence(",
            "write_text(",
            "write_bytes(",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
