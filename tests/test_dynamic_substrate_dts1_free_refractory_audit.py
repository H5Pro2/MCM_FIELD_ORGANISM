from __future__ import annotations

import ast
import inspect
import json
import unittest

from mcm_field_organism import dynamic_substrate_dts1_free_refractory_audit as audit
from mcm_field_organism.dynamic_substrate_s1ia_free_refractory_audit_contract import (
    build_dts1_s1ia_free_refractory_audit_contract,
)


class DTS1FreeRefractoryAuditTests(unittest.TestCase):
    def test_source_contract_fixture_and_execution_caps_are_fixed(self) -> None:
        source = build_dts1_s1ia_free_refractory_audit_contract()
        self.assertEqual(source.contract_digest, audit.S1_IB_SOURCE_S1IA_CONTRACT_DIGEST)
        self.assertEqual(8, audit.S1_IB_SINGLE_AUDIT_PURE_STEP_CALLS)
        self.assertEqual(16, audit.S1_IB_DOUBLE_AUDIT_PURE_STEP_CALLS)
        self.assertEqual(0.2537769456908254, audit.S1_IB_EXPECTED_F_HIGH_ENGAGEMENT)
        self.assertEqual(0.14501539753761447, audit.S1_IB_EXPECTED_R_HIGH_ENGAGEMENT)

    def test_matching_preflight_builds_two_valid_derived_free_anatomies(self) -> None:
        f_high, r_high = audit._matching_preflight()
        self.assertEqual(
            (0.7, 0.7),
            tuple(ledger.free for ledger in f_high.local_ledgers()),
        )
        self.assertEqual(
            (0.3999999999999999, 0.3999999999999999),
            tuple(ledger.free for ledger in r_high.local_ledgers()),
        )
        self.assertEqual(2.0, f_high.global_accounted_resource)
        self.assertEqual(2.0, r_high.global_accounted_resource)

    def test_single_audit_has_exactly_eight_direct_pure_call_sites(self) -> None:
        tree = ast.parse(inspect.getsource(audit._execute_once))
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_call"
        ]
        self.assertEqual(8, len(calls))

    def test_double_entry_has_exactly_two_direct_single_audit_calls(self) -> None:
        tree = ast.parse(
            inspect.getsource(audit.execute_dts1_s1ib_preregistered_double_audit)
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

    def test_baseline_records_cover_five_groups_without_execution(self) -> None:
        records = audit._baseline_records()
        self.assertEqual(5, len(records))
        self.assertTrue(
            all(value == "STATE_SPACE_DISTINCT_NO_EXECUTION" for _, value in records)
        )

    def test_stopp_case_record_can_represent_a_failed_exact_check(self) -> None:
        payload = (
            0.0,
            0.0,
            0.0,
            "a" * 64,
            "b" * 64,
            0.0,
            0.0,
            2.0,
            2.0,
        )
        record = audit.DTS1S1IBCaseRecord(
            case_id=audit.S1_IB_CASE_IDS[0],
            arm_ids=audit.S1_IB_ARM_IDS,
            input_anatomy_digests=("a" * 64, "b" * 64),
            result_payloads=(payload, payload),
            exact_checks=(("directed_check", False),),
            maximum_local_ledger_residual=0.0,
            maximum_global_ledger_residual=0.0,
            pure_step_calls=2,
        )
        self.assertFalse(record.exact_checks[0][1])
        json.dumps(record.canonical_payload(), allow_nan=False, sort_keys=True)

    def test_primary_values_and_floor_match_preregistration(self) -> None:
        self.assertEqual(
            audit.S1_IB_EXPECTED_ENGAGEMENT_DIFFERENCE,
            audit.S1_IB_EXPECTED_F_HIGH_ENGAGEMENT
            - audit.S1_IB_EXPECTED_R_HIGH_ENGAGEMENT,
        )
        self.assertGreater(
            audit.S1_IB_EXPECTED_ENGAGEMENT_DIFFERENCE,
            audit.S1_IB_ROUNDOFF_FLOOR,
        )

    def test_module_is_private_field_free_and_has_no_io_or_test_dependency(self) -> None:
        source = inspect.getsource(audit)
        for forbidden in (
            "shared_mcm_field",
            "neutral_local_field",
            "current_api",
            "from tests",
            "import tests",
            "open(",
            "Path(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
