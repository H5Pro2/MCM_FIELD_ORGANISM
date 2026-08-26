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
    prepare_e1_formation_s1fv_live_state_ten_role_contract,
)
from mcm_field_organism.e1_formation_s1fw_synthetic_live_state_handoff import (
    E1FormationS1FWSyntheticLiveStateHandoffError,
    coordinate_e1_formation_s1fw_synthetically,
)


class E1FormationS1FWSyntheticLiveStateHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        probe_contract = audit_e1_formation_s1fp_common_probe_contract()
        cls.inputs = prepare_e1_formation_s1fi_inputs(
            Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json")
        )
        cls.inventory = build_e1_formation_s1fj_synthetic_inventory(cls.inputs)
        integration = coordinate_e1_formation_s1fq_synthetically(
            probe_contract, cls.inventory
        )
        resource_audit = audit_e1_formation_s1fr_static_resources_and_matrix(
            probe_contract, integration
        )
        one_shot = prepare_e1_formation_s1fs_fresh_chain_one_shot_contract(
            resource_audit
        )
        chain, schema = prepare_e1_formation_s1ft_synthetic_objects(
            one_shot, resource_audit, probe_contract, cls.inputs
        )
        preflight = preflight_e1_formation_s1ft_synthetically(
            one_shot,
            resource_audit,
            chain,
            build_e1_formation_s1ft_synthetic_resource_snapshot(),
            schema,
        )
        connection_audit = audit_e1_formation_s1fu_real_adapter_connections(
            one_shot, preflight
        )
        cls.contract = prepare_e1_formation_s1fv_live_state_ten_role_contract(
            connection_audit
        )

    def test_exact_live_objects_route_to_all_thirty_slots(self) -> None:
        result = coordinate_e1_formation_s1fw_synthetically(
            self.contract, self.inventory, self.inputs
        )
        self.assertEqual((12, 12, 30, 24, 6), (
            result.live_state_object_count,
            result.unique_live_state_object_count,
            result.slot_handoff_count,
            result.state_consuming_slot_count,
            result.p0_slot_count,
        ))
        self.assertTrue(result.exact_object_identity_preserved)
        self.assertTrue(result.all_routes_complete)

    def test_usage_counts_match_active_and_ablated_routes(self) -> None:
        result = coordinate_e1_formation_s1fw_synthetically(
            self.contract, self.inventory, self.inputs
        )
        self.assertEqual((3, 3, 1, 1) * 3, tuple(
            count for _, _, count in result.usage_counts
        ))
        p0 = tuple(item for item in result.slot_handoffs if item.state is None)
        self.assertEqual(6, len(p0))
        self.assertTrue(all(item.fixed_adapter is None for item in p0))

    def test_fixed_adapters_derive_without_mutating_sources_or_field_steps(self) -> None:
        result = coordinate_e1_formation_s1fw_synthetically(
            self.contract, self.inventory, self.inputs
        )
        fixed = tuple(
            item for item in result.slot_handoffs if item.fixed_adapter is not None
        )
        self.assertEqual(6, len(fixed))
        self.assertTrue(all(item.fixed_adapter.backreaction_enabled for item in fixed))
        self.assertTrue(result.source_state_digests_preserved)
        self.assertEqual(0, result.field_steps_executed)
        self.assertFalse(result.real_probe_adapter_called)

    def test_untyped_adapter_result_fails_closed(self) -> None:
        def invalid_adapter(layer, state, config):
            return object()

        with self.assertRaisesRegex(
            E1FormationS1FWSyntheticLiveStateHandoffError,
            "no typed fixed adapter",
        ):
            coordinate_e1_formation_s1fw_synthetically(
                self.contract,
                self.inventory,
                self.inputs,
                adapter_factory=invalid_adapter,
            )

    def test_result_is_deterministic_tamper_evident_and_calls_no_field_runner(self) -> None:
        first = coordinate_e1_formation_s1fw_synthetically(
            self.contract, self.inventory, self.inputs
        )
        second = coordinate_e1_formation_s1fw_synthetically(
            self.contract, self.inventory, self.inputs
        )
        self.assertEqual(first.result_digest, second.result_digest)
        with self.assertRaises(E1FormationS1FWSyntheticLiveStateHandoffError):
            replace(first, execution_permitted=True)
        source = inspect.getsource(coordinate_e1_formation_s1fw_synthetically)
        for forbidden in (
            "run_small_five_arm_formation_in_memory(",
            "run_e1_common_probe_real_probe_wrapper(",
            "advance_frozen_e1_fast_shared_field_transient(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
