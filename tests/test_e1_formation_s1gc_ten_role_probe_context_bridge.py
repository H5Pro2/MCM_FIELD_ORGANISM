from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import unittest

import tests.test_e1_confirmation_typed_prepared_inputs as probe_fixture

from mcm_field_organism.e1_formation_s1fi_fresh_capture_preflight import prepare_e1_formation_s1fi_inputs
from mcm_field_organism.e1_formation_s1fj_synthetic_coordinator import build_e1_formation_s1fj_synthetic_inventory
from mcm_field_organism.e1_formation_s1fp_common_probe_contract import audit_e1_formation_s1fp_common_probe_contract
from mcm_field_organism.e1_formation_s1fq_synthetic_common_probe_coordinator import coordinate_e1_formation_s1fq_synthetically
from mcm_field_organism.e1_formation_s1fr_static_resource_matrix_audit import audit_e1_formation_s1fr_static_resources_and_matrix
from mcm_field_organism.e1_formation_s1fs_fresh_chain_one_shot_contract import prepare_e1_formation_s1fs_fresh_chain_one_shot_contract
from mcm_field_organism.e1_formation_s1ft_synthetic_fresh_chain_preflight import build_e1_formation_s1ft_synthetic_resource_snapshot, prepare_e1_formation_s1ft_synthetic_objects, preflight_e1_formation_s1ft_synthetically
from mcm_field_organism.e1_formation_s1fu_real_adapter_connection_audit import audit_e1_formation_s1fu_real_adapter_connections
from mcm_field_organism.e1_formation_s1fv_live_state_ten_role_contract import prepare_e1_formation_s1fv_live_state_ten_role_contract
from mcm_field_organism.e1_formation_s1gb_fixed_adapter_wrapper_contract import prepare_e1_formation_s1gb_fixed_adapter_wrapper_contract
from mcm_field_organism.e1_formation_s1gc_ten_role_probe_context_bridge import (
    E1FormationS1GCTenRoleProbeContextBridgeError,
    bridge_e1_formation_s1gc_ten_role_probe_contexts,
)


class E1FormationS1GCTenRoleProbeContextBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.probe_contract = audit_e1_formation_s1fp_common_probe_contract()
        inputs = prepare_e1_formation_s1fi_inputs(Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json"))
        inventory = build_e1_formation_s1fj_synthetic_inventory(inputs)
        integration = coordinate_e1_formation_s1fq_synthetically(cls.probe_contract, inventory)
        resources = audit_e1_formation_s1fr_static_resources_and_matrix(cls.probe_contract, integration)
        one_shot = prepare_e1_formation_s1fs_fresh_chain_one_shot_contract(resources)
        chain, schema = prepare_e1_formation_s1ft_synthetic_objects(one_shot, resources, cls.probe_contract, inputs)
        preflight = preflight_e1_formation_s1ft_synthetically(one_shot, resources, chain, build_e1_formation_s1ft_synthetic_resource_snapshot(), schema)
        connections = audit_e1_formation_s1fu_real_adapter_connections(one_shot, preflight)
        cls.live_contract = prepare_e1_formation_s1fv_live_state_ten_role_contract(connections)
        cls.wrapper_contract = prepare_e1_formation_s1gb_fixed_adapter_wrapper_contract()
        typed = probe_fixture._typed_inputs()
        cls.sequences = typed.probe_sequences
        cls.plans = typed.probe_plans

    def _bridge(self):
        return bridge_e1_formation_s1gc_ten_role_probe_contexts(self.wrapper_contract, self.probe_contract, self.live_contract, self.sequences, self.plans)

    def test_binds_six_fixed_slots_with_two_contexts_per_refinement(self) -> None:
        result = self._bridge()
        self.assertEqual(6, result.context_count)
        self.assertEqual((("r2", 2), ("r4", 2), ("r8", 2)), result.refinement_context_counts)
        self.assertTrue(result.all_fixed_slots_bound_once)

    def test_preserves_exact_sequence_and_plan_object_identity(self) -> None:
        result = self._bridge()
        self.assertTrue(result.exact_sequence_tuple_identity_preserved)
        self.assertTrue(result.exact_sequence_item_identity_preserved)
        self.assertTrue(result.exact_plan_object_identity_preserved)
        self.assertTrue(all(item.probe_sequences is self.sequences for item in result.contexts))

    def test_uses_no_old_eight_role_resolved_slot_and_no_execution(self) -> None:
        result = self._bridge()
        self.assertFalse(result.old_eight_role_resolved_slot_used)
        self.assertFalse(result.fixed_adapter_wrapper_called)
        self.assertEqual(0, result.field_steps_executed)
        self.assertFalse(result.execution_permitted)

    def test_wrong_probe_source_fails_closed(self) -> None:
        with self.assertRaises(E1FormationS1GCTenRoleProbeContextBridgeError):
            bridge_e1_formation_s1gc_ten_role_probe_contexts(self.wrapper_contract, self.probe_contract, self.live_contract, self.sequences[:-1], self.plans)

    def test_result_is_deterministic_tamper_evident_and_non_executing(self) -> None:
        first = self._bridge()
        second = self._bridge()
        self.assertEqual(first.result_digest, second.result_digest)
        with self.assertRaises(E1FormationS1GCTenRoleProbeContextBridgeError):
            replace(first, execution_permitted=True)
        source = inspect.getsource(bridge_e1_formation_s1gc_ten_role_probe_contexts)
        for forbidden in ("advance_fixed_e1_adapter_fast_shared_field_transient(", "run_e1_common_probe_real_probe_wrapper(", "open(", "write_text(", "write_bytes("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
