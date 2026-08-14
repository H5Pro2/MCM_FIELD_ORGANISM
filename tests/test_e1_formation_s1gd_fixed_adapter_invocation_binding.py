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
from mcm_field_organism.e1_formation_s1fw_synthetic_live_state_handoff import coordinate_e1_formation_s1fw_synthetically
from mcm_field_organism.e1_formation_s1gb_fixed_adapter_wrapper_contract import prepare_e1_formation_s1gb_fixed_adapter_wrapper_contract
from mcm_field_organism.e1_formation_s1gc_ten_role_probe_context_bridge import bridge_e1_formation_s1gc_ten_role_probe_contexts
from mcm_field_organism.e1_formation_s1gd_fixed_adapter_invocation_binding import (
    E1FormationS1GDFixedAdapterInvocationBindingError,
    bind_e1_formation_s1gd_fixed_adapter_invocations,
)


class E1FormationS1GDFixedAdapterInvocationBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        probe = audit_e1_formation_s1fp_common_probe_contract()
        cls.inputs = prepare_e1_formation_s1fi_inputs(Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json"))
        cls.inventory = build_e1_formation_s1fj_synthetic_inventory(cls.inputs)
        integration = coordinate_e1_formation_s1fq_synthetically(probe, cls.inventory)
        resources = audit_e1_formation_s1fr_static_resources_and_matrix(probe, integration)
        one_shot = prepare_e1_formation_s1fs_fresh_chain_one_shot_contract(resources)
        chain, schema = prepare_e1_formation_s1ft_synthetic_objects(one_shot, resources, probe, cls.inputs)
        preflight = preflight_e1_formation_s1ft_synthetically(one_shot, resources, chain, build_e1_formation_s1ft_synthetic_resource_snapshot(), schema)
        cls.connections = audit_e1_formation_s1fu_real_adapter_connections(one_shot, preflight)
        cls.live_contract = prepare_e1_formation_s1fv_live_state_ten_role_contract(cls.connections)
        cls.handoffs = coordinate_e1_formation_s1fw_synthetically(cls.live_contract, cls.inventory, cls.inputs)
        cls.wrapper_contract = prepare_e1_formation_s1gb_fixed_adapter_wrapper_contract()
        typed = probe_fixture._typed_inputs()
        cls.contexts = bridge_e1_formation_s1gc_ten_role_probe_contexts(cls.wrapper_contract, probe, cls.live_contract, typed.probe_sequences, typed.probe_plans)

    def test_binds_six_invocations_with_exact_objects(self) -> None:
        result = bind_e1_formation_s1gd_fixed_adapter_invocations(self.wrapper_contract, self.contexts, self.handoffs)
        self.assertEqual(6, result.invocation_count)
        self.assertEqual((("r2", 2), ("r4", 2), ("r8", 2)), result.refinement_invocation_counts)
        self.assertTrue(all(item.exact_binding_object_identity_preserved and item.exact_state_object_identity_preserved and item.exact_adapter_object_identity_preserved for item in result.invocations))

    def test_preserves_all_state_and_adapter_digests(self) -> None:
        result = bind_e1_formation_s1gd_fixed_adapter_invocations(self.wrapper_contract, self.contexts, self.handoffs)
        self.assertTrue(result.source_states_preserved)
        self.assertTrue(result.fixed_adapters_preserved)
        self.assertTrue(result.atomic_binding_complete)

    def test_equal_but_different_binding_objects_fail_closed(self) -> None:
        second_live_contract = prepare_e1_formation_s1fv_live_state_ten_role_contract(self.connections)
        second_handoffs = coordinate_e1_formation_s1fw_synthetically(second_live_contract, self.inventory, self.inputs)
        with self.assertRaises(E1FormationS1GDFixedAdapterInvocationBindingError):
            bind_e1_formation_s1gd_fixed_adapter_invocations(self.wrapper_contract, self.contexts, second_handoffs)

    def test_wrapper_and_execution_remain_closed(self) -> None:
        result = bind_e1_formation_s1gd_fixed_adapter_invocations(self.wrapper_contract, self.contexts, self.handoffs)
        self.assertFalse(result.wrapper_implementation_permitted)
        self.assertFalse(result.wrapper_called)
        self.assertEqual(0, result.field_steps_executed)
        with self.assertRaises(E1FormationS1GDFixedAdapterInvocationBindingError):
            replace(result, execution_permitted=True)

    def test_binder_calls_no_probe_kernel_or_writer(self) -> None:
        source = inspect.getsource(bind_e1_formation_s1gd_fixed_adapter_invocations)
        for forbidden in ("advance_fixed_e1_adapter_fast_shared_field_transient(", "run_e1_common_probe_real_probe_wrapper(", "open(", "write_text(", "write_bytes("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
