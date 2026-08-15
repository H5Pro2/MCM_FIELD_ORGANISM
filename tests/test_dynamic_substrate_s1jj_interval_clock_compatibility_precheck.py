from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ji_materialization_readiness_precheck import (
    build_dts1_s1ji_materialization_readiness_precheck,
)
from mcm_field_organism.dynamic_substrate_s1jj_interval_clock_compatibility_precheck import (
    DTS1S1JJIntervalClockCompatibilityPrecheckError,
    S1_JJ_DECISION,
    build_dts1_s1jj_interval_clock_compatibility_precheck,
)


class DTS1S1JJIntervalClockCompatibilityPrecheckTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1jj_interval_clock_compatibility_precheck()

    def test_binds_exact_s1ji_source(self) -> None:
        self.assertEqual(
            build_dts1_s1ji_materialization_readiness_precheck().audit_digest,
            self._audit().source_s1ji_digest,
        )

    def test_records_repeated_s1jh_step_time(self) -> None:
        facts = dict(self._audit().s1jh_clock_facts)
        self.assertEqual((0, 1, 2.0, 0.5), tuple(facts[key] for key in ("start_tick", "end_tick", "ticks_per_second", "elapsed_synthetic_time")))
        self.assertTrue(facts["same_complete_step_time_repeated_in_all_twenty_three_envelopes"])

    def test_binds_existing_carried_field_time_invariants(self) -> None:
        rules = " ".join(self._audit().runtime_invariants)
        self.assertIn("strictly-greater", rules)
        self.assertIn("preserve-last_distribution-by-identity", rules)
        self.assertIn("must-equal-the-current-ReceptorDistribution", rules)

    def test_all_sequences_and_sixteen_continuations_are_affected(self) -> None:
        audit = self._audit()
        self.assertEqual(7, audit.affected_sequence_count)
        self.assertEqual(16, audit.incompatible_continuation_envelopes_per_model_per_refinement)
        self.assertEqual(24, audit.baseline_case_count_still_blocked)
        self.assertEqual(23, sum(row[1] for row in audit.sequence_impact))

    def test_preserves_non_time_bindings_and_supersedes_only_time_dependents(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.non_time_s1jh_bindings_preserved)
        self.assertFalse(audit.s1jh_time_schedule_materializable)
        preserved = " ".join(audit.preserved_bindings)
        superseded = " ".join(audit.superseded_bindings)
        self.assertIn("S-H-values", preserved)
        self.assertIn("zero-contact-values", preserved)
        self.assertIn("sequence-digests-that-commit", superseded)
        self.assertIn("interval-digests-that-commit", superseded)

    def test_requires_contiguous_sequence_relative_correction(self) -> None:
        rules = " ".join(self._audit().correction_requirements)
        self.assertIn("zero-to-one-one-to-two-and-so-on", rules)
        self.assertIn("same-ordinal-window-to-DTS1-and-B1-through-B6", rules)
        self.assertIn("recompute-all-time-dependent", rules)

    def test_blocks_schema_implementation_and_execution(self) -> None:
        audit = self._audit()
        for value in (audit.materialization_schema_bound, audit.common_interval_fixture_implemented, audit.adapters_implemented, audit.baseline_models_executed, audit.runtime_integration_present, audit.research_execution_permitted):
            self.assertFalse(value)
        self.assertEqual((0, 0), (audit.technical_field_steps_executed, audit.research_field_steps_executed))
        self.assertTrue(audit.corrected_monotonic_clock_contract_authorized_next_stage)
        self.assertEqual(S1_JJ_DECISION, audit.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1JJIntervalClockCompatibilityPrecheckError):
            replace(audit, s1jh_time_schedule_materializable=True)
        with self.assertRaises(DTS1S1JJIntervalClockCompatibilityPrecheckError):
            replace(audit, incompatible_continuation_envelopes_per_model_per_refinement=15)
        source = inspect.getsource(build_dts1_s1jj_interval_clock_compatibility_precheck)
        for forbidden in ("apply_", "compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
