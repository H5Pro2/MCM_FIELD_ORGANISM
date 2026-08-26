from __future__ import annotations

import ast
import inspect
import json
import unittest

from mcm_field_organism import dynamic_substrate_dts1_causal_field_readout_audit as audit
from mcm_field_organism.dynamic_substrate_s1id_causal_field_readout_audit_contract import (
    build_dts1_s1id_causal_field_readout_audit_contract,
)
from mcm_field_organism.mcm_substrate_state import mcm_substrate_edge_inventory


class DTS1CausalFieldReadoutAuditTests(unittest.TestCase):
    def test_source_contract_expected_metrics_and_caps_are_fixed(self) -> None:
        contract = build_dts1_s1id_causal_field_readout_audit_contract()
        self.assertEqual(contract.contract_digest, audit.S1_IE_SOURCE_S1ID_CONTRACT_DIGEST)
        self.assertEqual(dict(contract.analytic_preflight)["substep_1_b1_F_HIGH"], str(dict(audit.S1_IE_EXPECTED)["b1_F_HIGH"]))
        self.assertEqual(20, audit.S1_IE_SINGLE_AUDIT_FIELD_CALLS)
        self.assertEqual(40, audit.S1_IE_DOUBLE_AUDIT_FIELD_CALLS)

    def test_fixture_builds_one_two_node_edge_and_valid_resource_pair(self) -> None:
        field = audit._initial_field(audit._INITIAL_H_MAIN)
        self.assertEqual(2, len(field.layer.neurons))
        self.assertEqual(1, len(mcm_substrate_edge_inventory(field.layer)))
        f_high = audit._anatomy(field, audit._F_REFRACTORY)
        r_high = audit._anatomy(field, audit._R_REFRACTORY)
        self.assertEqual((0.7, 0.7), tuple(item.free for item in f_high.local_ledgers()))
        self.assertEqual(
            (0.3999999999999999, 0.3999999999999999),
            tuple(item.free for item in r_high.local_ledgers()),
        )
        self.assertEqual(0.0, f_high.global_residual)
        self.assertEqual(0.0, r_high.global_residual)

    def test_each_case_has_exactly_four_direct_field_call_sites(self) -> None:
        for function in (
            audit._run_c01,
            audit._run_n01,
            audit._run_n02,
            audit._run_n03,
            audit._run_n04,
        ):
            tree = ast.parse(inspect.getsource(function))
            calls = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "_call"
            ]
            self.assertEqual(4, len(calls), function.__name__)

    def test_double_entry_has_exactly_two_direct_single_audit_calls(self) -> None:
        tree = ast.parse(
            inspect.getsource(audit.execute_dts1_s1ie_preregistered_double_audit)
        )
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_execute_once"
        ]
        loops = [node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While))]
        self.assertEqual(2, len(calls))
        self.assertEqual([], loops)

    def test_frozen_control_uses_first_field_and_original_anatomies(self) -> None:
        source = inspect.getsource(audit._run_n03)
        self.assertIn("_call(f1.field, f0, 1, 2", source)
        self.assertIn("_call(r1.field, r0, 1, 2", source)
        self.assertNotIn("_call(f1.field, f1.anatomy", source)
        self.assertNotIn("_call(r1.field, r1.anatomy", source)

    def test_baseline_records_cover_five_groups_without_execution(self) -> None:
        records = audit._baseline_records()
        self.assertEqual(5, len(records))
        self.assertTrue(
            all(value == "STATE_SPACE_DISTINCT_NO_EXECUTION" for _, value in records)
        )

    def test_failed_case_check_is_representable_for_atomic_stopp(self) -> None:
        step = audit.DTS1S1IEStepRecord(
            arm_id="test-arm",
            substep=1,
            field_vector=(0.0, 0.0, 0.0, 0.0),
            anatomy_digest="a" * 64,
            adapter_rates=(1.0,),
            participation=(0.0,),
            transfer_vector=(0.0, 0.0, 0.0),
            maximum_local_ledger_residual=0.0,
            global_ledger_residual=0.0,
        )
        step2 = audit.DTS1S1IEStepRecord(
            arm_id="test-arm",
            substep=2,
            field_vector=(0.0, 0.0, 0.0, 0.0),
            anatomy_digest="b" * 64,
            adapter_rates=(1.0,),
            participation=(0.0,),
            transfer_vector=(0.0, 0.0, 0.0),
            maximum_local_ledger_residual=0.0,
            global_ledger_residual=0.0,
        )
        record = audit.DTS1S1IECaseRecord(
            case_id=audit.S1_IE_CASE_IDS[0],
            step_records=(step, step, step2, step2),
            exact_checks=(("causal_check", False),),
            technical_field_calls=4,
        )
        self.assertFalse(record.exact_checks[0][1])
        json.dumps(record.canonical_payload(), allow_nan=False, sort_keys=True)

    def test_module_is_private_and_has_no_io_runtime_or_test_dependency(self) -> None:
        source = inspect.getsource(audit)
        for forbidden in (
            "current_api",
            "from tests",
            "import tests",
            "open(",
            "Path(",
            "subprocess",
            "requests",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
