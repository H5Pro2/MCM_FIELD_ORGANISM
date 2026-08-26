from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1jn_finite_materialization_schema_contract import (
    build_dts1_s1jn_finite_materialization_schema_contract,
)
from mcm_field_organism.dynamic_substrate_s1ju_geometry_digest_role_precheck import (
    build_dts1_s1ju_geometry_digest_role_precheck,
)
from mcm_field_organism.dynamic_substrate_s1jv_finite_geometry_digest_mapping_contract import (
    DTS1S1JVFiniteGeometryDigestMappingContractError,
    S1_JV_DECISION,
    build_dts1_s1jv_finite_geometry_digest_mapping_contract,
)


class DTS1S1JVFiniteGeometryDigestMappingContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1jv_finite_geometry_digest_mapping_contract()

    def test_binds_exact_s1ju_and_s1jn_sources(self) -> None:
        contract = self._contract()
        self.assertEqual(build_dts1_s1ju_geometry_digest_role_precheck().audit_digest, contract.source_s1ju_digest)
        self.assertEqual(build_dts1_s1jn_finite_materialization_schema_contract().contract_digest, contract.source_s1jn_digest)

    def test_binds_exactly_two_unique_field_and_inventory_keys(self) -> None:
        contract = self._contract()
        self.assertEqual((2, 2), (contract.mapping_count, contract.unique_selection_key_count))
        keys = tuple((row[1], row[4]) for row in contract.geometry_digest_mappings)
        self.assertEqual(len(keys), len(set(keys)))

    def test_two_node_mapping_is_complete_and_exact(self) -> None:
        row = self._contract().geometry_digest_mappings[0]
        self.assertEqual(("TWO_NODE_OPEN_LINE", "mcm.s1jn.field.2n"), row[:2])
        self.assertEqual((("node-a", (0,)), ("node-b", (1,))), row[4])
        self.assertEqual(("node-a", "node-b"), row[5])
        self.assertTrue(row[6].startswith("5f7bdc4e"))
        self.assertTrue(row[7].startswith("77595b85"))

    def test_three_node_mapping_is_complete_and_exact(self) -> None:
        row = self._contract().geometry_digest_mappings[1]
        self.assertEqual(("THREE_NODE_OPEN_LINE", "mcm.s1jn.field.3n"), row[:2])
        self.assertEqual(("node-a", "node-b", "node-c"), row[5])
        self.assertTrue(row[6].startswith("2efcf504"))
        self.assertTrue(row[7].startswith("2536e5e2"))

    def test_binds_two_unequal_noninterchangeable_pairs(self) -> None:
        contract = self._contract()
        self.assertEqual(2, contract.unequal_digest_pair_count)
        self.assertTrue(all(row[6] != row[7] for row in contract.geometry_digest_mappings))

    def test_selection_is_complete_and_information_poor(self) -> None:
        rules = " ".join(self._contract().selection_rules)
        self.assertIn("field-id-and-complete-ordered-node-inventory", rules)
        self.assertIn("partial-reordered-or-cross-paired", rules)
        self.assertIn("never-select-by-model-role-profile-control-label", rules)

    def test_b1_uses_outer_for_invocation_and_internal_for_payload(self) -> None:
        rule = self._contract().role_digest_bindings[0]
        self.assertEqual("B1", rule[0])
        self.assertIn("outer-common-digest-validates", rule[1])
        self.assertIn("edge_inventory_digest-is-exactly-the-selected-internal", rule[2])
        self.assertIn("never-compared-for-equality", rule[3])

    def test_b2_and_b3_b6_validate_both_roles_without_equating(self) -> None:
        b2, f3 = self._contract().role_digest_bindings[1:]
        self.assertIn("complete-materialized-layer-inventory", b2[2])
        self.assertIn("receives-no-edge-digest-field", b2[3])
        self.assertIn("embedded-M-state", f3[2])
        self.assertIn("never-compared-for-equality", f3[3])

    def test_s1jt_overlay_changes_only_ambiguous_digest_role(self) -> None:
        overlay = " ".join(self._contract().s1jt_correction_overlay)
        self.assertIn("immutable-historical-source", overlay)
        self.assertIn("supersedes-only-the-ambiguous-B1", overlay)
        self.assertIn("rates-payload-shapes-runtime-records-diagnostics-output-and-error-rules-remain-bit-identical", overlay)

    def test_fail_closed_rules_reject_role_swaps_and_repairs(self) -> None:
        rules = " ".join(self._contract().fail_closed_rules)
        self.assertIn("outer-digest-used-in-any-B1-or-M-state", rules)
        self.assertIn("internal-digest-used-as-the-model-facing", rules)
        self.assertIn("equate-drop-recompute-relabel-repair-or-infer", rules)
        self.assertIn("no-partial-adapter-context-output", rules)

    def test_authorizes_only_corrected_implementation_next(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.finite_digest_mapping_bound)
        self.assertTrue(contract.corrected_adapter_implementation_authorized_next_stage)
        self.assertFalse(contract.adapters_implemented)
        self.assertFalse(contract.baseline_kernels_called)
        self.assertEqual(0, contract.profile_cases_executed)
        self.assertFalse(contract.runtime_integration_present)
        self.assertEqual(S1_JV_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1JVFiniteGeometryDigestMappingContractError):
            replace(contract, adapters_implemented=True)
        source = inspect.getsource(build_dts1_s1jv_finite_geometry_digest_mapping_contract)
        for forbidden in ("advance_", "compute_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
