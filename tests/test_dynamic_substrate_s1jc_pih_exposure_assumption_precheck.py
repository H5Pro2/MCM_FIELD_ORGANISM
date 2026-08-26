from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

import mcm_field_organism.dynamic_substrate_dts1_attenuation_audit as pih_audit
from mcm_field_organism.dynamic_substrate_s1jb_adapter_implementation_readiness_precheck import (
    build_dts1_s1jb_adapter_implementation_readiness_precheck,
)
from mcm_field_organism.dynamic_substrate_s1jc_pih_exposure_assumption_precheck import (
    DTS1S1JCPIHExposureAssumptionPrecheckError,
    S1_JC_DECISION,
    build_dts1_s1jc_pih_exposure_assumption_precheck,
)


class DTS1S1JCPIHExposureAssumptionPrecheckTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1jc_pih_exposure_assumption_precheck()

    def test_binds_exact_s1jb_precheck(self) -> None:
        self.assertEqual(
            build_dts1_s1jb_adapter_implementation_readiness_precheck().audit_digest,
            self._audit().source_s1jb_digest,
        )

    def test_confirms_only_pie_of_the_two_retained_blocks(self) -> None:
        records = {row[0]: row[2] for row in self._audit().profile_records}
        self.assertEqual("COMMON_CAUSAL_EXPOSURE_CONFIRMED", records["P_IE_CAUSAL_TWO_SUBSTEP"])
        self.assertEqual("INVALID_RETAINED_COMMON_EXPOSURE_ASSUMPTION", records["P_IH_ATTENUATION"])
        self.assertEqual((2, 1), (self._audit().retained_profile_block_count, self._audit().invalid_retained_profile_block_count))

    def test_source_contains_separate_resource_and_fresh_field_calls(self) -> None:
        active_source = inspect.getsource(pih_audit._run_c01)
        field_source = inspect.getsource(pih_audit._field_call)
        self.assertIn("_resource_call", active_source)
        self.assertIn("_field_call", active_source)
        self.assertIn("_initial_field(afterimage)", field_source)
        self.assertIn("advance_dts1_coupled_fast_shared_field", field_source)

    def test_records_why_stateful_baseline_history_is_absent(self) -> None:
        facts = " ".join(self._audit().p_ih_source_facts)
        self.assertIn("compute_dts1_closed_prestate_step", facts)
        self.assertIn("new-initial-field", facts)
        self.assertIn("cannot-supply-equivalent-prior-A-exposure", facts)

    def test_requires_three_common_two_node_a_intervals(self) -> None:
        correction = " ".join(self._audit().required_correction)
        self.assertIn("two-node-A-boundary", correction)
        self.assertIn("three-identical-positive-A-active-intervals", correction)
        self.assertIn("model-owned-hidden-state-carries", correction)
        self.assertIn("checkpoint-after-each-active-interval", correction)

    def test_quarantines_only_old_field_vectors_and_retains_direct_ledgers(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.old_p_ih_field_vectors_quarantined)
        self.assertTrue(audit.p_ih_direct_ledgers_retained)
        self.assertFalse(audit.p_ih_common_exposure_valid)

    def test_keeps_all_24_cases_blocked_without_execution(self) -> None:
        audit = self._audit()
        self.assertEqual((24, 24), (audit.planned_adapter_case_count, audit.blocked_adapter_case_count))
        self.assertFalse(audit.common_interval_envelope_bound)
        self.assertFalse(audit.adapters_implemented)
        self.assertFalse(audit.baseline_models_executed)
        self.assertEqual((0, 0), (audit.technical_field_steps_executed, audit.research_field_steps_executed))
        self.assertEqual(S1_JC_DECISION, audit.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1JCPIHExposureAssumptionPrecheckError):
            replace(audit, p_ih_common_exposure_valid=True)
        with self.assertRaises(DTS1S1JCPIHExposureAssumptionPrecheckError):
            replace(audit, old_p_ih_field_vectors_quarantined=False)
        source = inspect.getsource(build_dts1_s1jc_pih_exposure_assumption_precheck)
        for forbidden in ("advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
