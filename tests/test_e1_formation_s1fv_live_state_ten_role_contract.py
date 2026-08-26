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
    audit_e1_formation_s1fu_real_adapter_connections,
)
from mcm_field_organism.e1_formation_s1fv_live_state_ten_role_contract import (
    E1FormationS1FVLiveStateTenRoleContractError,
    prepare_e1_formation_s1fv_live_state_ten_role_contract,
)


class E1FormationS1FVLiveStateTenRoleContractTests(unittest.TestCase):
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
        resource_audit = audit_e1_formation_s1fr_static_resources_and_matrix(
            probe_contract, integration
        )
        one_shot = prepare_e1_formation_s1fs_fresh_chain_one_shot_contract(
            resource_audit
        )
        chain, schema = prepare_e1_formation_s1ft_synthetic_objects(
            one_shot, resource_audit, probe_contract, inputs
        )
        preflight = preflight_e1_formation_s1ft_synthetically(
            one_shot,
            resource_audit,
            chain,
            build_e1_formation_s1ft_synthetic_resource_snapshot(),
            schema,
        )
        cls.audit = audit_e1_formation_s1fu_real_adapter_connections(
            one_shot, preflight
        )

    def test_twelve_live_states_route_to_thirty_slots(self) -> None:
        result = prepare_e1_formation_s1fv_live_state_ten_role_contract(
            self.audit
        )
        self.assertEqual((12, 3, 30, 24, 6), (
            result.live_state_object_count,
            result.identity_control_result_count,
            result.probe_slot_count,
            result.state_consuming_probe_slot_count,
            result.p0_probe_slot_count,
        ))
        self.assertEqual(30, len(result.slot_bindings))

    def test_active_states_feed_active_feedback_ablation_and_fixed_adapter(self) -> None:
        result = prepare_e1_formation_s1fv_live_state_ten_role_contract(
            self.audit
        )
        r2_ab = tuple(
            item for item in result.slot_bindings
            if item.refinement_id == "r2" and item.source_state_role == "active-ab"
        )
        self.assertEqual(
            ("e1-active-ab", "e1-probe-feedback-ablated-ab", "fixed-adapter-ab"),
            tuple(item.role_id for item in r2_ab),
        )
        self.assertEqual(1, sum(item.fixed_adapter_derivation_required for item in r2_ab))

    def test_identity_and_legacy_contact_axis_are_excluded(self) -> None:
        result = prepare_e1_formation_s1fv_live_state_ten_role_contract(
            self.audit
        )
        self.assertFalse(result.identity_control_may_feed_probe)
        self.assertFalse(result.legacy_contact_axis_required)
        self.assertNotIn(
            "ab_identity",
            tuple(item.source_formation_arm_id for item in result.slot_bindings),
        )
        self.assertTrue(all(item.legacy_contact_axis is None for item in result.slot_bindings))

    def test_contract_is_closed_deterministic_and_tamper_evident(self) -> None:
        first = prepare_e1_formation_s1fv_live_state_ten_role_contract(
            self.audit
        )
        second = prepare_e1_formation_s1fv_live_state_ten_role_contract(
            self.audit
        )
        self.assertEqual(first.contract_digest, second.contract_digest)
        self.assertTrue(first.exact_live_object_identity_required)
        self.assertFalse(first.digest_only_handoff_permitted)
        self.assertFalse(first.real_adapter_implementation_permitted)
        self.assertFalse(first.execution_permitted)
        with self.assertRaises(E1FormationS1FVLiveStateTenRoleContractError):
            replace(first, execution_permitted=True)

    def test_builder_calls_no_adapter_runner_or_writer(self) -> None:
        source = inspect.getsource(
            prepare_e1_formation_s1fv_live_state_ten_role_contract
        )
        for forbidden in (
            "run_small_five_arm_formation_in_memory(",
            "capture_e1_formation_s1ff_in_memory(",
            "run_e1_common_probe_real_probe_wrapper(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
