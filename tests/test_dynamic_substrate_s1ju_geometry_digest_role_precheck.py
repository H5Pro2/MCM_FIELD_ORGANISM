from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1jt_finite_adapter_payload_contract import (
    build_dts1_s1jt_finite_adapter_payload_contract,
)
from mcm_field_organism.dynamic_substrate_s1ju_geometry_digest_role_precheck import (
    DTS1S1JUGeometryDigestRolePrecheckError,
    S1_JU_DECISION,
    build_dts1_s1ju_geometry_digest_role_precheck,
)


class DTS1S1JUGeometryDigestRolePrecheckTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1ju_geometry_digest_role_precheck()

    def test_binds_exact_s1jt_source(self) -> None:
        self.assertEqual(
            build_dts1_s1jt_finite_adapter_payload_contract().contract_digest,
            self._audit().source_s1jt_digest,
        )

    def test_binds_two_complete_unequal_digest_pairs(self) -> None:
        audit = self._audit()
        self.assertEqual((2, 2), (audit.geometry_count, audit.unequal_digest_pair_count))
        self.assertTrue(all(row[2] != row[3] and row[4] is False for row in audit.geometry_digest_records))

    def test_two_node_digest_pair_is_exact(self) -> None:
        row = self._audit().geometry_digest_records[0]
        self.assertEqual(("node-a", "node-b"), row[1])
        self.assertTrue(row[2].startswith("5f7bdc4e"))
        self.assertTrue(row[3].startswith("77595b85"))

    def test_three_node_digest_pair_is_exact(self) -> None:
        row = self._audit().geometry_digest_records[1]
        self.assertEqual(("node-a", "node-b", "node-c"), row[1])
        self.assertTrue(row[2].startswith("2efcf504"))
        self.assertTrue(row[3].startswith("2536e5e2"))

    def test_defines_noninterchangeable_digest_roles(self) -> None:
        definitions = self._audit().digest_role_definitions
        self.assertEqual(("outer_common_geometry_digest", "internal_edge_inventory_digest"), tuple(row[0] for row in definitions))
        self.assertIn("model-facing", definitions[0][3])
        self.assertIn("DTS1BackreactionResult", definitions[1][3])

    def test_finds_b1_and_generic_equality_conflicts(self) -> None:
        findings = " ".join(self._audit().conflict_findings)
        self.assertIn("B1-binds-one-edge-inventory-digest", findings)
        self.assertIn("equates-both-digests", findings)
        self.assertIn("rejects-every-valid-B1-through-B6", findings)

    def test_preserves_outer_and_internal_algorithms(self) -> None:
        preserved = " ".join(self._audit().preserved_bindings)
        self.assertIn("S1-JK-outer-geometry", preserved)
        self.assertIn("existing-baseline-kernels-and-internal-edge-digest-validation", preserved)
        self.assertIn("B1-two-node-rate-1.2", preserved)

    def test_forbids_relabel_skip_or_algorithm_change(self) -> None:
        forbidden = " ".join(self._audit().forbidden_repairs)
        self.assertIn("relabel-any-existing-S1-JK", forbidden)
        self.assertIn("skip-cross-checking", forbidden)
        self.assertIn("change-the-internal-edge-inventory-digest-algorithm", forbidden)

    def test_requires_finite_pair_mapping_and_internal_b1_digest(self) -> None:
        required = " ".join(self._audit().required_correction)
        self.assertIn("finite-outer-to-internal-digest-pair", required)
        self.assertIn("B1-fixed-adapter-payload", required)
        self.assertIn("without-equating-them", required)

    def test_stops_before_adapter_or_kernel_execution(self) -> None:
        audit = self._audit()
        self.assertFalse(audit.adapter_implementation_ready)
        self.assertFalse(audit.adapters_implemented)
        self.assertFalse(audit.baseline_kernels_called)
        self.assertEqual(0, audit.profile_cases_executed)
        self.assertFalse(audit.runtime_integration_present)
        self.assertTrue(audit.corrected_digest_role_contract_authorized_next_stage)
        self.assertEqual(S1_JU_DECISION, audit.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1JUGeometryDigestRolePrecheckError):
            replace(audit, adapter_implementation_ready=True)
        source = inspect.getsource(build_dts1_s1ju_geometry_digest_role_precheck)
        for forbidden in ("advance_", "compute_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
