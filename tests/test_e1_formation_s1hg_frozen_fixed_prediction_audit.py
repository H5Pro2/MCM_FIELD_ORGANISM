from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_formation_s1hg_frozen_fixed_prediction_audit import (
    E1FormationS1HGFrozenFixedPredictionAuditError,
    S1_HG_DECISION,
    audit_e1_formation_s1hg_frozen_fixed_distinct_prediction,
)


class E1FormationS1HGFrozenFixedPredictionAuditTests(unittest.TestCase):
    def _audit(self):
        return audit_e1_formation_s1hg_frozen_fixed_distinct_prediction()

    def test_binds_real_lauf_198_baseline_and_shared_integrator(self) -> None:
        audit = self._audit()
        self.assertEqual("_advance_with_fixed_adapter", audit.shared_field_integrator_name)
        self.assertTrue(audit.fixed_adapter_baseline_real_and_nonzero)
        self.assertTrue(all(value for _, value in audit.checks))

    def test_stops_only_frozen_probe_branch_without_distinct_prediction(self) -> None:
        audit = self._audit()
        self.assertFalse(audit.frozen_state_changes_during_probe)
        self.assertFalse(audit.active_frozen_e1_has_distinct_prediction)
        self.assertFalse(audit.full_matrix_execution_informative)
        self.assertTrue(audit.frozen_probe_branch_stopped)
        self.assertFalse(audit.overall_project_stopped)
        self.assertEqual(S1_HG_DECISION, audit.decision)

    def test_requires_owner_decision_before_new_substrate_direction(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.new_substrate_direction_requires_owner_decision)
        self.assertFalse(audit.additional_field_execution_performed)
        self.assertFalse(audit.memory_claim_permitted)

    def test_audit_is_deterministic_and_tamper_evident(self) -> None:
        first = self._audit()
        second = self._audit()
        self.assertEqual(first.audit_digest, second.audit_digest)
        with self.assertRaises(E1FormationS1HGFrozenFixedPredictionAuditError):
            replace(first, active_frozen_e1_has_distinct_prediction=True)
        with self.assertRaises(E1FormationS1HGFrozenFixedPredictionAuditError):
            replace(first, overall_project_stopped=True)

    def test_audit_calls_no_field_runner_writer_or_persistence(self) -> None:
        source = inspect.getsource(
            audit_e1_formation_s1hg_frozen_fixed_distinct_prediction
        )
        for forbidden in (
            "advance_frozen_e1_fast_shared_field_transient(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "run_e1_formation_s1gu_six_arm_counting_adapter(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
