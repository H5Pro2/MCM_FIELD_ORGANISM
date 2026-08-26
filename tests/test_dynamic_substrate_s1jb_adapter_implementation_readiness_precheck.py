from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    build_dts1_s1ja_finite_configuration_matrix_contract,
)
from mcm_field_organism.dynamic_substrate_s1jb_adapter_implementation_readiness_precheck import (
    DTS1S1JBAdapterImplementationReadinessPrecheckError,
    S1_JB_DECISION,
    build_dts1_s1jb_adapter_implementation_readiness_precheck,
)


class DTS1S1JBAdapterImplementationReadinessPrecheckTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1jb_adapter_implementation_readiness_precheck()

    def test_binds_exact_s1ja_contract(self) -> None:
        self.assertEqual(
            build_dts1_s1ja_finite_configuration_matrix_contract().contract_digest,
            self._audit().source_s1ja_digest,
        )

    def test_records_missing_common_envelope_for_all_four_blocks(self) -> None:
        records = {row[0]: row[2] for row in self._audit().surface_records}
        self.assertIn("NO_SINGLE_AUTHORITATIVE", records["COMMON_INTERVAL_ENVELOPE"])
        for block in (
            "P_IE_CAUSAL_TWO_SUBSTEP",
            "P_IH_ATTENUATION",
            "P_IK_INTERFERENCE",
            "P_IN_RELEASE_REUSE",
        ):
            self.assertIn("BLOCKED", records[block])

    def test_distinguishes_existing_types_from_missing_composition(self) -> None:
        facts = " ".join(self._audit().blocking_facts)
        self.assertIn("S1-IZ-applies-one-S-H-boundary", facts)
        self.assertIn("not-the-complete-per-event-adapter-input-values", facts)
        self.assertIn("six-independent-adapter-schedule-builders", facts)

    def test_requires_one_pre_role_model_neutral_envelope_and_digest(self) -> None:
        requirements = " ".join(self._audit().required_next_contract)
        self.assertIn("one-private-immutable-model-neutral-interval-envelope-type", requirements)
        self.assertIn("before-any-baseline-role-is-selected", requirements)
        self.assertIn("without-arm-case-target-or-result-data", requirements)

    def test_preserves_s1ja_and_boundary_bindings(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.configuration_binding_preserved)
        self.assertTrue(audit.case_matrix_binding_preserved)
        preserved = " ".join(audit.preserved_bindings)
        self.assertIn("all-seven-S1-JA-configuration-values-and-digests", preserved)
        self.assertIn("S1-IX-S1-IY-S1-IZ", preserved)

    def test_blocks_all_24_adapter_cases_before_implementation(self) -> None:
        audit = self._audit()
        self.assertEqual((24, 0, 24), (audit.planned_adapter_case_count, audit.ready_adapter_case_count, audit.blocked_adapter_case_count))
        self.assertFalse(audit.common_interval_envelope_bound)
        self.assertFalse(audit.adapters_implemented)

    def test_performs_no_model_or_field_execution(self) -> None:
        audit = self._audit()
        self.assertFalse(audit.baseline_models_executed)
        self.assertFalse(audit.runtime_integration_present)
        self.assertFalse(audit.research_execution_permitted)
        self.assertEqual((0, 0), (audit.technical_field_steps_executed, audit.research_field_steps_executed))
        self.assertEqual(S1_JB_DECISION, audit.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1JBAdapterImplementationReadinessPrecheckError):
            replace(audit, ready_adapter_case_count=1)
        with self.assertRaises(DTS1S1JBAdapterImplementationReadinessPrecheckError):
            replace(audit, adapters_implemented=True)
        source = inspect.getsource(build_dts1_s1jb_adapter_implementation_readiness_precheck)
        for forbidden in ("advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
