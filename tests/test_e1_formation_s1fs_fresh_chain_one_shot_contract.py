from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_formation_s1fi_fresh_capture_preflight import (
    prepare_e1_formation_s1fi_inputs,
)
from mcm_field_organism.e1_formation_s1fj_synthetic_coordinator import (
    build_e1_formation_s1fj_synthetic_inventory,
)
from mcm_field_organism.e1_formation_s1fp_common_probe_contract import (
    audit_e1_formation_s1fp_common_probe_contract,
)
from mcm_field_organism.e1_formation_s1fq_synthetic_common_probe_coordinator import (
    coordinate_e1_formation_s1fq_synthetically,
)
from mcm_field_organism.e1_formation_s1fr_static_resource_matrix_audit import (
    audit_e1_formation_s1fr_static_resources_and_matrix,
)
from mcm_field_organism.e1_formation_s1fs_fresh_chain_one_shot_contract import (
    E1FormationS1FSFreshChainOneShotContractError,
    S1_FS_RETURN_COMPONENTS,
    prepare_e1_formation_s1fs_fresh_chain_one_shot_contract,
)


class E1FormationS1FSFreshChainOneShotContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        contract = audit_e1_formation_s1fp_common_probe_contract()
        inputs = prepare_e1_formation_s1fi_inputs(
            Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json")
        )
        inventory = build_e1_formation_s1fj_synthetic_inventory(inputs)
        integration = coordinate_e1_formation_s1fq_synthetically(
            contract, inventory
        )
        cls.audit = audit_e1_formation_s1fr_static_resources_and_matrix(
            contract, integration
        )

    def test_exact_one_shot_scope_is_bound_but_not_authorized(self) -> None:
        result = prepare_e1_formation_s1fs_fresh_chain_one_shot_contract(
            self.audit
        )
        self.assertEqual((1, 0), (
            result.planned_execution_count,
            result.authorized_execution_count,
        ))
        self.assertEqual((15, 30, 45), (
            result.formation_call_count,
            result.probe_call_count,
            result.total_field_call_count,
        ))
        self.assertEqual(28_000, result.maximum_total_field_steps)
        self.assertFalse(result.owner_authorization_present)
        self.assertFalse(result.execution_permitted)

    def test_formation_gate_and_atomic_return_are_mandatory(self) -> None:
        result = prepare_e1_formation_s1fs_fresh_chain_one_shot_contract(
            self.audit
        )
        self.assertTrue(result.formation_acceptance_required_before_probe)
        self.assertTrue(result.atomic_result_required)
        self.assertTrue(result.evaluation_after_atomic_return_only)
        self.assertTrue(result.fixed_adapter_evaluation_separate_required)
        self.assertEqual(S1_FS_RETURN_COMPONENTS, result.atomic_return_components)
        self.assertFalse(result.partial_result_decision_permitted)

    def test_freshness_resources_and_error_policy_are_closed(self) -> None:
        result = prepare_e1_formation_s1fs_fresh_chain_one_shot_contract(
            self.audit
        )
        self.assertTrue(result.same_session_fresh_formation_and_probe_required)
        self.assertTrue(result.immediate_pre_execution_resource_preflight_required)
        self.assertEqual(4 * 1024**3, result.minimum_free_memory_bytes)
        self.assertEqual(1_800.0, result.maximum_runtime_seconds)
        self.assertFalse(result.automatic_retry_permitted)
        self.assertFalse(result.posthoc_parameter_change_permitted)
        self.assertFalse(result.persistence_permitted)

    def test_contract_is_deterministic_and_tamper_evident(self) -> None:
        first = prepare_e1_formation_s1fs_fresh_chain_one_shot_contract(
            self.audit
        )
        second = prepare_e1_formation_s1fs_fresh_chain_one_shot_contract(
            self.audit
        )
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(E1FormationS1FSFreshChainOneShotContractError):
            replace(first, execution_permitted=True)

    def test_builder_calls_no_field_runner_or_writer(self) -> None:
        source = inspect.getsource(
            prepare_e1_formation_s1fs_fresh_chain_one_shot_contract
        )
        for forbidden in (
            "run_e1_formation_s1fl_once(",
            "run_small_five_arm_formation_in_memory(",
            "advance_neutral_fast_shared_field_transient(",
            "advance_frozen_e1_fast_shared_field_transient(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
