from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

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
from mcm_field_organism.e1_formation_s1fx_common_probe_receipt_contract import prepare_e1_formation_s1fx_common_probe_receipt_contract
from mcm_field_organism.e1_formation_s1fy_synthetic_common_receipts import (
    E1FormationS1FYSyntheticCommonReceiptError,
    build_s1fy_fixed_adapter_receipt,
    build_s1fy_frozen_e1_receipt,
    build_s1fy_neutral_p0_receipt,
    coordinate_e1_formation_s1fy_synthetically,
)


class E1FormationS1FYSyntheticCommonReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        probe = audit_e1_formation_s1fp_common_probe_contract()
        cls.inputs = prepare_e1_formation_s1fi_inputs(Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json"))
        inventory = build_e1_formation_s1fj_synthetic_inventory(cls.inputs)
        integration = coordinate_e1_formation_s1fq_synthetically(probe, inventory)
        resources = audit_e1_formation_s1fr_static_resources_and_matrix(probe, integration)
        one_shot = prepare_e1_formation_s1fs_fresh_chain_one_shot_contract(resources)
        chain, schema = prepare_e1_formation_s1ft_synthetic_objects(one_shot, resources, probe, cls.inputs)
        preflight = preflight_e1_formation_s1ft_synthetically(one_shot, resources, chain, build_e1_formation_s1ft_synthetic_resource_snapshot(), schema)
        connections = audit_e1_formation_s1fu_real_adapter_connections(one_shot, preflight)
        live_contract = prepare_e1_formation_s1fv_live_state_ten_role_contract(connections)
        cls.handoff = coordinate_e1_formation_s1fw_synthetically(live_contract, inventory, cls.inputs)
        cls.contract = prepare_e1_formation_s1fx_common_probe_receipt_contract(live_contract, cls.handoff)

    def test_builds_thirty_distinct_zero_step_receipts(self) -> None:
        result = coordinate_e1_formation_s1fy_synthetically(self.contract, self.handoff, self.inputs)
        self.assertEqual((30, 30, 0), (result.receipt_count, result.distinct_receipt_count, result.field_steps_executed))
        self.assertEqual((("neutral-p0", 6), ("frozen-e1", 18), ("fixed-adapter", 6)), result.branch_invocation_counts)
        self.assertTrue(result.atomic_result_complete)

    def test_receipts_keep_three_causal_evidence_shapes(self) -> None:
        result = coordinate_e1_formation_s1fy_synthetically(self.contract, self.handoff, self.inputs)
        p0 = next(item for item in result.receipts if item.role_id.startswith("p0-reset"))
        frozen = next(item for item in result.receipts if item.role_id.startswith("e1-active"))
        fixed = next(item for item in result.receipts if item.role_id.startswith("fixed-adapter"))
        self.assertEqual((None, None, None, None), (p0.source_state_digest, p0.state_digest_before, p0.state_digest_after, p0.fixed_adapter_digest))
        self.assertEqual(frozen.source_state_digest, frozen.state_digest_before)
        self.assertEqual(frozen.source_state_digest, frozen.state_digest_after)
        self.assertIsNone(frozen.fixed_adapter_digest)
        self.assertIsNotNone(fixed.source_state_digest)
        self.assertEqual((None, None), (fixed.state_digest_before, fixed.state_digest_after))
        self.assertIsNotNone(fixed.fixed_adapter_digest)

    def test_receipts_use_unchanged_initial_snapshot_vectors(self) -> None:
        neurons = tuple(self.inputs.initial_field.layer.neurons)
        field_digest = dict(self.inputs.input_manifest)["initial_field"]
        neuron_ids = tuple(item.neuron_id for item in neurons)
        activation = tuple(item.activation for item in neurons)
        afterimage = tuple(item.afterimage for item in neurons)
        result = coordinate_e1_formation_s1fy_synthetically(self.contract, self.handoff, self.inputs)
        self.assertTrue(result.common_neuron_order_preserved)
        self.assertTrue(all(item.initial_field_digest == item.terminal_field_digest == field_digest for item in result.receipts))
        self.assertTrue(all(item.ordered_neuron_ids == neuron_ids and item.activation_vector == activation and item.afterimage_vector == afterimage for item in result.receipts))

    def test_wrong_branch_adapter_fails_closed_without_result(self) -> None:
        adapters = {
            "neutral-p0": build_s1fy_frozen_e1_receipt,
            "frozen-e1": build_s1fy_frozen_e1_receipt,
            "fixed-adapter": build_s1fy_fixed_adapter_receipt,
        }
        with self.assertRaises(E1FormationS1FYSyntheticCommonReceiptError):
            coordinate_e1_formation_s1fy_synthetically(self.contract, self.handoff, self.inputs, adapters=adapters)

    def test_result_is_deterministic_and_tamper_evident(self) -> None:
        first = coordinate_e1_formation_s1fy_synthetically(self.contract, self.handoff, self.inputs)
        second = coordinate_e1_formation_s1fy_synthetically(self.contract, self.handoff, self.inputs)
        self.assertEqual(first.result_digest, second.result_digest)
        with self.assertRaises(E1FormationS1FYSyntheticCommonReceiptError):
            replace(first, execution_permitted=True)


if __name__ == "__main__":
    unittest.main()
