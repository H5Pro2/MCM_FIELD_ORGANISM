from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    build_dts1_s1ja_finite_configuration_matrix_contract,
)
from mcm_field_organism.dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    build_dts1_s1jk_corrected_monotonic_interval_contract,
)
from mcm_field_organism.dynamic_substrate_s1jp_baseline_adapter_bridge_contract import (
    build_dts1_s1jp_baseline_adapter_bridge_contract,
)
from mcm_field_organism.dynamic_substrate_s1jq_adapter_refinement_readiness_precheck import (
    DTS1S1JQAdapterRefinementReadinessPrecheckError,
    S1_JQ_DECISION,
    build_dts1_s1jq_adapter_refinement_readiness_precheck,
)


class DTS1S1JQAdapterRefinementReadinessPrecheckTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1jq_adapter_refinement_readiness_precheck()

    def test_binds_exact_s1jp_s1jk_and_s1ja_sources(self) -> None:
        audit = self._audit()
        self.assertEqual(build_dts1_s1jp_baseline_adapter_bridge_contract().contract_digest, audit.source_s1jp_digest)
        self.assertEqual(build_dts1_s1jk_corrected_monotonic_interval_contract().contract_digest, audit.source_s1jk_digest)
        self.assertEqual(build_dts1_s1ja_finite_configuration_matrix_contract().contract_digest, audit.source_s1ja_digest)

    def test_binds_one_integer_tick_per_physical_interval(self) -> None:
        facts = " ".join(self._audit().bound_time_facts)
        self.assertIn("one-integer-tick", facts)
        self.assertIn("integer-start-and-end-ticks", facts)
        self.assertIn("refinement-levels-two-four-eight", facts)

    def test_classifies_four_native_and_two_blocked_roles(self) -> None:
        audit = self._audit()
        self.assertEqual((6, 4, 2), (audit.baseline_role_count, audit.native_refinement_role_count, audit.blocked_role_count))
        self.assertEqual(("B1", "B2"), tuple(row[0] for row in audit.kernel_capability_records if not row[2]))

    def test_b1_commits_one_complete_atomic_field_step(self) -> None:
        b1 = self._audit().kernel_capability_records[0]
        self.assertFalse(b1[2])
        self.assertTrue(b1[3])
        self.assertIn("one-atomic-field.advance", b1[4])

    def test_b2_is_exact_and_has_no_refinement_argument(self) -> None:
        b2 = self._audit().kernel_capability_records[1]
        self.assertFalse(b2[2])
        self.assertIn("analytic-matrix-exponential", b2[4])
        self.assertIn("no-refinement-argument", b2[4])

    def test_proves_subwindow_and_clock_conflict(self) -> None:
        proof = " ".join(self._audit().conflict_proof)
        self.assertIn("require-at-least-r-ticks", proof)
        self.assertIn("fractional-ticks-are-invalid", proof)
        self.assertIn("change-the-common-exposure", proof)
        self.assertIn("nonmonotonic-field-time", proof)

    def test_forbids_metadata_repair_and_kernel_reimplementation(self) -> None:
        forbidden = " ".join(self._audit().forbidden_repairs)
        self.assertIn("post-hoc-time-repair", forbidden)
        self.assertIn("kernel-reimplementation", forbidden)
        self.assertIn("silent-refinement-ignore", forbidden)

    def test_preserves_prior_fixtures_materializer_and_case_identities(self) -> None:
        preserved = " ".join(self._audit().preserved_bindings)
        self.assertIn("twenty-three-S1-JK-envelopes", preserved)
        self.assertIn("S1-JO-materializer", preserved)
        self.assertIn("twenty-four-case-identities", preserved)

    def test_blocks_all_cases_atomically_without_execution(self) -> None:
        audit = self._audit()
        self.assertEqual(8, audit.blocked_case_count)
        self.assertTrue(audit.all_twenty_four_cases_blocked_atomically)
        self.assertFalse(audit.adapter_implementation_ready)
        self.assertFalse(audit.adapters_implemented)
        self.assertFalse(audit.baseline_models_executed)
        self.assertEqual((0, 0), (audit.technical_field_steps_executed, audit.research_field_steps_executed))
        self.assertEqual(S1_JQ_DECISION, audit.decision)

    def test_requires_role_specific_corrected_refinement_contract(self) -> None:
        correction = " ".join(self._audit().required_correction)
        self.assertIn("classify-refinement-by-existing-kernel", correction)
        self.assertIn("exact-full-interval-evaluation", correction)
        self.assertIn("native-refinement-two-four-eight", correction)
        self.assertTrue(self._audit().corrected_refinement_contract_authorized_next_stage)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1JQAdapterRefinementReadinessPrecheckError):
            replace(audit, adapter_implementation_ready=True)
        source = inspect.getsource(build_dts1_s1jq_adapter_refinement_readiness_precheck)
        for forbidden in ("advance_", "compute_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
