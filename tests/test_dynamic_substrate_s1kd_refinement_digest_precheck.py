from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1kd_refinement_digest_precheck import (
    DTS1S1KDRefinementDigestPrecheckError,
    S1_KD_DECISION,
    S1_KD_SOURCE_S1KC_DIGEST,
    S1_KD_SOURCE_S1JX_DIGEST,
    S1_KD_SOURCE_S1JZ_DIGEST,
    build_dts1_s1kd_refinement_digest_precheck,
)


class DTS1S1KDRefinementDigestPrecheckTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1kd_refinement_digest_precheck()

    def test_binds_exact_three_source_digests(self) -> None:
        audit = self._audit()
        self.assertEqual((
            S1_KD_SOURCE_S1KC_DIGEST,
            S1_KD_SOURCE_S1JX_DIGEST,
            S1_KD_SOURCE_S1JZ_DIGEST,
        ), (
            audit.source_s1kc_digest,
            audit.source_s1jx_digest,
            audit.source_s1jz_digest,
        ))

    def test_targets_only_b1_pie_r2_r4_r8(self) -> None:
        self.assertEqual((2, 4, 8), tuple(row[1] for row in self._audit().target_replicas))
        self.assertTrue(all(row[0].startswith("B1:P_IE_CAUSAL_TWO_SUBSTEP:r") for row in self._audit().target_replicas))

    def test_finds_complete_output_identity_fields(self) -> None:
        audit = self._audit()
        self.assertEqual(("replica_id", "refinement"), audit.complete_output_identity_fields)
        self.assertEqual(("replica_id",), audit.checkpoint_identity_fields)

    def test_identity_fields_force_three_distinct_digests(self) -> None:
        audit = self._audit()
        self.assertEqual(3, audit.distinct_hypothetical_digest_count)
        self.assertEqual(3, len(set(audit.hypothetical_identity_digests)))

    def test_requires_dual_provenance_and_comparison_digest_roles(self) -> None:
        required = " ".join(self._audit().required_correction)
        self.assertIn("identity-bearing-complete-output-digest", required)
        self.assertIn("identity-neutral-refinement-comparison", required)
        self.assertIn("without-equating-complete-provenance-digests", required)

    def test_stops_r4_r8_without_execution(self) -> None:
        audit = self._audit()
        self.assertFalse(audit.r4_r8_runner_extension_authorized)
        self.assertEqual((0, 0, 0), (
            audit.r4_r8_replicas_executed,
            audit.interval_calls_executed,
            audit.complete_matrix_cases_executed,
        ))
        self.assertFalse(audit.runtime_integration_present)
        self.assertFalse(audit.research_execution_permitted)

    def test_authorizes_only_correction_contract_next(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.correction_contract_authorized_next_stage)
        self.assertEqual(S1_KD_DECISION, audit.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1KDRefinementDigestPrecheckError):
            replace(audit, r4_r8_runner_extension_authorized=True)
        source = inspect.getsource(build_dts1_s1kd_refinement_digest_precheck)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
