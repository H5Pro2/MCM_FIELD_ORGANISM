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
    prepare_e1_formation_s1fs_fresh_chain_one_shot_contract,
)
from mcm_field_organism.e1_formation_s1ft_synthetic_fresh_chain_preflight import (
    build_e1_formation_s1ft_synthetic_resource_snapshot,
    prepare_e1_formation_s1ft_synthetic_objects,
    preflight_e1_formation_s1ft_synthetically,
)
from mcm_field_organism.e1_formation_s1fu_real_adapter_connection_audit import (
    E1FormationS1FURealAdapterConnectionAuditError,
    S1_FU_MISSING,
    audit_e1_formation_s1fu_real_adapter_connections,
)


class E1FormationS1FURealAdapterConnectionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        probe_contract = audit_e1_formation_s1fp_common_probe_contract()
        inputs = prepare_e1_formation_s1fi_inputs(
            Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json")
        )
        inventory = build_e1_formation_s1fj_synthetic_inventory(inputs)
        integration = coordinate_e1_formation_s1fq_synthetically(
            probe_contract, inventory
        )
        audit = audit_e1_formation_s1fr_static_resources_and_matrix(
            probe_contract, integration
        )
        cls.contract = prepare_e1_formation_s1fs_fresh_chain_one_shot_contract(
            audit
        )
        chain, schema = prepare_e1_formation_s1ft_synthetic_objects(
            cls.contract, audit, probe_contract, inputs
        )
        cls.preflight = preflight_e1_formation_s1ft_synthetically(
            cls.contract,
            audit,
            chain,
            build_e1_formation_s1ft_synthetic_resource_snapshot(),
            schema,
        )

    def test_reuse_and_missing_counts_are_explicit(self) -> None:
        result = audit_e1_formation_s1fu_real_adapter_connections(
            self.contract, self.preflight
        )
        self.assertTrue(result.static_audit_passed)
        self.assertEqual((6, 3, 5), (
            result.unchanged_reusable_count,
            result.adaptable_count,
            result.missing_count,
        ))
        self.assertEqual(S1_FU_MISSING, result.missing_components)

    def test_exact_probe_role_gap_is_fixed_adapter_pair(self) -> None:
        result = audit_e1_formation_s1fu_real_adapter_connections(
            self.contract, self.preflight
        )
        self.assertEqual(
            ("fixed-adapter-ab", "fixed-adapter-ba"),
            result.missing_probe_roles,
        )
        self.assertTrue(result.new_ten_role_slot_binding_required)
        self.assertTrue(result.new_fixed_adapter_wrapper_required)

    def test_missing_work_is_coordination_not_new_field_physics(self) -> None:
        result = audit_e1_formation_s1fu_real_adapter_connections(
            self.contract, self.preflight
        )
        self.assertFalse(result.new_field_mechanic_required)
        self.assertFalse(result.live_state_export_present)
        self.assertTrue(result.new_live_state_handoff_required)
        self.assertTrue(result.new_atomic_coordinator_required)
        self.assertFalse(result.real_runner_implementation_permitted)
        self.assertFalse(result.execution_permitted)

    def test_audit_is_deterministic_and_tamper_evident(self) -> None:
        first = audit_e1_formation_s1fu_real_adapter_connections(
            self.contract, self.preflight
        )
        second = audit_e1_formation_s1fu_real_adapter_connections(
            self.contract, self.preflight
        )
        self.assertEqual(first.audit_digest, second.audit_digest)
        with self.assertRaises(E1FormationS1FURealAdapterConnectionAuditError):
            replace(first, execution_permitted=True)

    def test_audit_calls_no_production_path_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_formation_s1fu_real_adapter_connections
        )
        for forbidden in (
            "prepare_e1_formation_s1fi_inputs(",
            "read_e1_formation_s1fi_resource_snapshot(",
            "run_small_five_arm_formation_in_memory(",
            "capture_e1_formation_s1ff_in_memory(",
            "evaluate_e1_formation_s1fd_state_convergence(",
            "build_e1_common_probe_fresh_field(",
            "run_e1_common_probe_real_probe_wrapper(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "decide_common_probe_evidence(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
