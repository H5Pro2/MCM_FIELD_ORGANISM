from __future__ import annotations

from dataclasses import replace
import inspect
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
from mcm_field_organism.e1_formation_s1fx_common_probe_receipt_contract import (
    E1FormationS1FXCommonProbeReceiptContractError,
    S1_FX_RECEIPT_SCHEMA,
    prepare_e1_formation_s1fx_common_probe_receipt_contract,
)


class E1FormationS1FXCommonProbeReceiptContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        probe_contract = audit_e1_formation_s1fp_common_probe_contract()
        inputs = prepare_e1_formation_s1fi_inputs(Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json"))
        inventory = build_e1_formation_s1fj_synthetic_inventory(inputs)
        integration = coordinate_e1_formation_s1fq_synthetically(probe_contract, inventory)
        resource_audit = audit_e1_formation_s1fr_static_resources_and_matrix(probe_contract, integration)
        one_shot = prepare_e1_formation_s1fs_fresh_chain_one_shot_contract(resource_audit)
        chain, schema = prepare_e1_formation_s1ft_synthetic_objects(one_shot, resource_audit, probe_contract, inputs)
        preflight = preflight_e1_formation_s1ft_synthetically(one_shot, resource_audit, chain, build_e1_formation_s1ft_synthetic_resource_snapshot(), schema)
        connection = audit_e1_formation_s1fu_real_adapter_connections(one_shot, preflight)
        cls.handoff_contract = prepare_e1_formation_s1fv_live_state_ten_role_contract(connection)
        cls.handoff = coordinate_e1_formation_s1fw_synthetically(cls.handoff_contract, inventory, inputs)

    def test_three_branch_inventory_covers_thirty_receipts(self) -> None:
        result = prepare_e1_formation_s1fx_common_probe_receipt_contract(self.handoff_contract, self.handoff)
        self.assertEqual((30, 6, 18, 6), (result.total_receipt_count, result.p0_receipt_count, result.frozen_e1_receipt_count, result.fixed_adapter_receipt_count))
        self.assertEqual(S1_FX_RECEIPT_SCHEMA, result.receipt_schema)

    def test_causal_evidence_stays_separate_by_branch(self) -> None:
        result = prepare_e1_formation_s1fx_common_probe_receipt_contract(self.handoff_contract, self.handoff)
        nulls = dict(result.causal_nullability)
        self.assertIn("fixed_adapter_digest", nulls["neutral-p0"])
        self.assertEqual(("fixed_adapter_digest",), nulls["frozen-e1"])
        self.assertEqual(("state_digest_before", "state_digest_after"), nulls["fixed-adapter"])
        self.assertFalse(result.fixed_adapter_may_be_reported_as_dynamic_e1_backreaction)

    def test_real_implementation_and_execution_remain_closed(self) -> None:
        result = prepare_e1_formation_s1fx_common_probe_receipt_contract(self.handoff_contract, self.handoff)
        self.assertFalse(result.common_receipt_converter_implemented)
        self.assertFalse(result.fixed_adapter_real_wrapper_implemented)
        self.assertFalse(result.real_wrapper_implementation_permitted)
        self.assertFalse(result.execution_permitted)
        self.assertTrue(result.synthetic_counting_implementation_permitted)

    def test_contract_is_deterministic_and_tamper_evident(self) -> None:
        first = prepare_e1_formation_s1fx_common_probe_receipt_contract(self.handoff_contract, self.handoff)
        second = prepare_e1_formation_s1fx_common_probe_receipt_contract(self.handoff_contract, self.handoff)
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(E1FormationS1FXCommonProbeReceiptContractError):
            replace(first, execution_permitted=True)

    def test_builder_calls_no_probe_kernel_or_writer(self) -> None:
        source = inspect.getsource(prepare_e1_formation_s1fx_common_probe_receipt_contract)
        for forbidden in ("run_e1_common_probe_real_probe_wrapper(", "advance_fixed_e1_adapter_fast_shared_field_transient(", "advance_frozen_e1_fast_shared_field_transient(", "open(", "write_text(", "write_bytes("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
