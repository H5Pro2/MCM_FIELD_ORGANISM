from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_s1fa_norm_interval_decision import (
    E1CommonProbeS1FANormIntervalDecisionError,
    audit_e1_common_probe_s1fa_norm_interval_decision,
)


class E1CommonProbeS1FANormIntervalDecisionTests(unittest.TestCase):
    def test_reverse_triangle_bounds_are_exactly_derived_from_retained_norms(self) -> None:
        result = audit_e1_common_probe_s1fa_norm_interval_decision()
        for component in result.components:
            self.assertEqual(
                abs(component.r4_norm - component.r8_norm),
                component.fine_distance_lower_bound,
            )
            self.assertEqual(
                component.r4_norm + component.r8_norm,
                component.fine_distance_upper_bound,
            )

    def test_both_relative_lower_bounds_exceed_preregistered_one_percent(self) -> None:
        result = audit_e1_common_probe_s1fa_norm_interval_decision()
        activation, afterimage = result.components
        self.assertGreater(activation.fine_relative_lower_bound, 0.097)
        self.assertGreater(afterimage.fine_relative_lower_bound, 0.095)
        self.assertTrue(
            all(
                item.fine_relative_lower_bound > item.relative_refinement_limit
                for item in result.components
            )
        )

    def test_ec46_clear_outcome_is_excluded_without_exact_vectors(self) -> None:
        result = audit_e1_common_probe_s1fa_norm_interval_decision()
        self.assertFalse(result.exact_vectors_available)
        self.assertFalse(result.exact_fine_distances_computable)
        self.assertFalse(result.relative_convergence_possible)
        self.assertFalse(result.numerically_clear_decision_possible)
        self.assertTrue(result.ec46_decision_identifiable_from_bounds)
        self.assertEqual(
            "NUMERICALLY_UNDECIDABLE_COMMON_PROBE_DIFFERENCE",
            result.ec46_decision,
        )

    def test_no_reconstruction_rerun_or_claim_is_opened(self) -> None:
        result = audit_e1_common_probe_s1fa_norm_interval_decision()
        self.assertFalse(result.posthoc_vector_reconstruction_permitted)
        self.assertFalse(result.field_execution_permitted)
        self.assertFalse(result.rerun_permitted)
        self.assertFalse(result.memory_claim_permitted)

    def test_result_is_deterministic_and_tamper_evident(self) -> None:
        first = audit_e1_common_probe_s1fa_norm_interval_decision()
        second = audit_e1_common_probe_s1fa_norm_interval_decision()
        self.assertEqual(first.audit_digest, second.audit_digest)
        with self.assertRaises(E1CommonProbeS1FANormIntervalDecisionError):
            replace(first, numerically_clear_decision_possible=True)

    def test_audit_does_not_call_decider_runner_adapter_or_writer(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_s1fa_norm_interval_decision)
        for forbidden in (
            "decide_common_probe_evidence(",
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_e1_common_probe_ec96_authorized_r4_r8_once(",
            "run_e1_common_probe_real_formation_receipt_adapter(",
            "write_text(",
            "write_bytes(",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
