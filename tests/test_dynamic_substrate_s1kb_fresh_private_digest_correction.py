from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1kb_fresh_private_digest_correction import (
    DTS1S1KBFreshPrivateDigestCorrectionError,
    S1_KB_CORRECTED_S1JZ_DIGEST,
    S1_KB_DECISION,
    S1_KB_SOURCE_S1KA_DIGEST,
    build_dts1_s1kb_fresh_private_digest_correction,
)


class DTS1S1KBFreshPrivateDigestCorrectionTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1kb_fresh_private_digest_correction()

    def test_binds_s1ka_and_corrected_s1jz_digests(self) -> None:
        audit = self._audit()
        self.assertEqual(S1_KB_SOURCE_S1KA_DIGEST, audit.source_s1ka_digest)
        self.assertEqual(S1_KB_CORRECTED_S1JZ_DIGEST, audit.corrected_s1jz_digest)

    def test_all_twelve_roundtrips_pass(self) -> None:
        audit = self._audit()
        self.assertEqual((12, 12, 0), (
            audit.roundtrip_count,
            audit.passing_roundtrip_count,
            audit.failing_roundtrip_count,
        ))
        self.assertTrue(all(row[2] == row[3] and row[4] for row in audit.roundtrip_records))

    def test_corrects_exactly_b1_and_b2_in_both_geometries(self) -> None:
        corrected = tuple((row[0], row[1]) for row in self._audit().corrected_private_digests)
        self.assertEqual((
            ("B1", "TWO_NODE_OPEN_LINE"),
            ("B1", "THREE_NODE_OPEN_LINE"),
            ("B2", "TWO_NODE_OPEN_LINE"),
            ("B2", "THREE_NODE_OPEN_LINE"),
        ), corrected)

    def test_each_corrected_digest_changed_to_runtime_digest(self) -> None:
        audit = self._audit()
        runtime = {(row[0], row[1]): row[3] for row in audit.roundtrip_records}
        for role, geometry, old_digest, new_digest in audit.corrected_private_digests:
            self.assertNotEqual(old_digest, new_digest)
            self.assertEqual(new_digest, runtime[(role, geometry)])

    def test_preserves_exactly_eight_b3_through_b6_digests(self) -> None:
        audit = self._audit()
        self.assertEqual((4, 8), (audit.corrected_record_count, audit.preserved_record_count))
        current = {(row[0], row[1]): row[2] for row in audit.roundtrip_records}
        for role, geometry, digest in audit.preserved_private_digests:
            self.assertIn(role, ("B3", "B4", "B5", "B6"))
            self.assertEqual(digest, current[(role, geometry)])

    def test_stays_before_factory_runner_and_execution(self) -> None:
        audit = self._audit()
        self.assertFalse(audit.initializer_implemented)
        self.assertFalse(audit.orchestrator_implemented)
        self.assertEqual((0, 0, 0, 0), (
            audit.materializer_calls_executed,
            audit.adapter_calls_executed,
            audit.interval_calls_executed,
            audit.profile_cases_executed,
        ))

    def test_reauthorizes_only_same_exemplar_next_stage(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.same_exemplar_authorized_next_stage)
        self.assertEqual(S1_KB_DECISION, audit.decision)

    def test_is_deterministic_and_tamper_evident(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1KBFreshPrivateDigestCorrectionError):
            replace(audit, orchestrator_implemented=True)

    def test_builder_contains_no_field_execution_calls(self) -> None:
        source = inspect.getsource(build_dts1_s1kb_fresh_private_digest_correction)
        for forbidden in ("materialize_dts1", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
