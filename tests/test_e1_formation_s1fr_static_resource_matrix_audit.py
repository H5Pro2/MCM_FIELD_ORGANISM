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
    E1FormationS1FRStaticResourceMatrixAuditError,
    S1_FR_EXPECTED_BUDGETS,
    audit_e1_formation_s1fr_static_resources_and_matrix,
)


class E1FormationS1FRStaticResourceMatrixAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = audit_e1_formation_s1fp_common_probe_contract()
        inputs = prepare_e1_formation_s1fi_inputs(
            Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json")
        )
        inventory = build_e1_formation_s1fj_synthetic_inventory(inputs)
        cls.integration = coordinate_e1_formation_s1fq_synthetically(
            cls.contract, inventory
        )

    def test_exact_full_chain_budget_is_bound(self) -> None:
        result = audit_e1_formation_s1fr_static_resources_and_matrix(
            self.contract, self.integration
        )
        self.assertEqual(S1_FR_EXPECTED_BUDGETS, result.budgets)
        self.assertEqual((15, 30, 45), (
            result.formation_call_count,
            result.probe_call_count,
            result.total_field_call_count,
        ))
        self.assertEqual((14_000, 14_000, 28_000), (
            result.formation_field_steps,
            result.probe_field_steps,
            result.total_field_steps,
        ))

    def test_no_causally_equivalent_matrix_reduction_exists(self) -> None:
        result = audit_e1_formation_s1fr_static_resources_and_matrix(
            self.contract, self.integration
        )
        self.assertEqual(10, result.minimum_causally_complete_probe_role_count)
        self.assertEqual(30, result.minimum_causally_complete_probe_slot_count)
        self.assertEqual((), result.removable_probe_roles)
        self.assertEqual((), result.removable_refinements)
        self.assertFalse(result.causally_equivalent_matrix_reduction_available)

    def test_resource_bounds_are_conservative_and_execution_stays_closed(self) -> None:
        result = audit_e1_formation_s1fr_static_resources_and_matrix(
            self.contract, self.integration
        )
        self.assertEqual(2_352_000, result.conservative_node_step_units)
        self.assertEqual(4_060_000, result.conservative_edge_step_units)
        self.assertEqual(2_175, result.retained_binding_count)
        self.assertEqual(4 * 1024**3, result.minimum_free_memory_bytes)
        self.assertFalse(result.exact_peak_ram_estimate_available)
        self.assertFalse(result.execution_permitted)
        self.assertEqual(0, self.integration.field_steps_executed)

    def test_audit_is_deterministic_and_tamper_evident(self) -> None:
        first = audit_e1_formation_s1fr_static_resources_and_matrix(
            self.contract, self.integration
        )
        second = audit_e1_formation_s1fr_static_resources_and_matrix(
            self.contract, self.integration
        )
        self.assertEqual(first.audit_digest, second.audit_digest)
        with self.assertRaises(E1FormationS1FRStaticResourceMatrixAuditError):
            replace(first, execution_permitted=True)

    def test_auditor_calls_no_field_runner_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_formation_s1fr_static_resources_and_matrix
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
