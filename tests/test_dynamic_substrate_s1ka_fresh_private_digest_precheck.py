from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1jz_finite_orchestrator_api_contract import build_dts1_s1jz_finite_orchestrator_api_contract
from mcm_field_organism.dynamic_substrate_s1ka_fresh_private_digest_precheck import (
    DTS1S1KAFreshPrivateDigestPrecheckError,
    S1_KA_DECISION,
    build_dts1_s1ka_fresh_private_digest_precheck,
)


class DTS1S1KAFreshPrivateDigestPrecheckTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1ka_fresh_private_digest_precheck()

    def test_binds_exact_s1jz_source(self) -> None:
        self.assertEqual(build_dts1_s1jz_finite_orchestrator_api_contract().contract_digest, self._audit().source_s1jz_digest)

    def test_audits_all_twelve_records(self) -> None:
        audit = self._audit()
        self.assertEqual((12, 4, 8), (audit.record_count, audit.failing_record_count, audit.passing_record_count))

    def test_exactly_b1_and_b2_fail_both_geometries(self) -> None:
        failing = tuple((row[0], row[1]) for row in self._audit().digest_roundtrip_records if not row[4])
        self.assertEqual((
            ("B1", "TWO_NODE_OPEN_LINE"), ("B1", "THREE_NODE_OPEN_LINE"),
            ("B2", "TWO_NODE_OPEN_LINE"), ("B2", "THREE_NODE_OPEN_LINE"),
        ), failing)

    def test_b3_through_b6_roundtrip_bit_identically(self) -> None:
        passing = self._audit().digest_roundtrip_records[4:]
        self.assertTrue(all(row[2] == row[3] and row[4] for row in passing))

    def test_exemplar_is_blocked_before_first_interval(self) -> None:
        audit = self._audit()
        self.assertFalse(audit.exemplar_record_passes)
        self.assertEqual((0, 0, 0), (audit.technical_replicas_executed, audit.baseline_interval_calls_executed, audit.profile_cases_executed))

    def test_finds_nested_tuple_object_shape_mismatch(self) -> None:
        findings = " ".join(self._audit().findings)
        self.assertIn("B1-fixed-adapter-tuples-as-arrays", findings)
        self.assertIn("B2-L-entry-tuples-without", findings)
        self.assertIn("before-materialization", findings)

    def test_preserves_non_digest_contract_scope(self) -> None:
        preserved = " ".join(self._audit().preserved_bindings)
        self.assertIn("runner-input-checkpoint-component-index-output-error", preserved)
        self.assertIn("all-twelve-fresh-field-payloads", preserved)
        self.assertIn("S1-JX", preserved)
        self.assertIn("S1-JW", preserved)

    def test_requires_only_four_digest_dependent_corrections(self) -> None:
        required = " ".join(self._audit().required_correction)
        self.assertIn("replace-only-the-nested-B1", required)
        self.assertIn("four-dependent-private-state-digests", required)
        self.assertIn("retain-the-eight-bit-identical", required)

    def test_stops_without_runner_or_runtime(self) -> None:
        audit = self._audit()
        self.assertFalse(audit.initializer_implemented)
        self.assertFalse(audit.orchestrator_implemented)
        self.assertFalse(audit.runtime_integration_present)
        self.assertTrue(audit.corrected_fresh_state_contract_authorized_next_stage)
        self.assertEqual(S1_KA_DECISION, audit.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1KAFreshPrivateDigestPrecheckError):
            replace(audit, orchestrator_implemented=True)
        source = inspect.getsource(build_dts1_s1ka_fresh_private_digest_precheck)
        for forbidden in ("materialize_", "advance_", "compute_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
