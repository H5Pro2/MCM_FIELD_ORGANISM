from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_s1fb_discretization_scaling_audit import (
    E1CommonProbeS1FBDiscretizationScalingAuditError,
    audit_e1_common_probe_s1fb_discretization_scaling,
)


class E1CommonProbeS1FBDiscretizationScalingAuditTests(unittest.TestCase):
    def test_refinement_doubles_steps_without_changing_physical_inputs(self) -> None:
        result = audit_e1_common_probe_s1fb_discretization_scaling()
        self.assertEqual(
            (("r2", 2, 402, 200), ("r4", 4, 804, 400), ("r8", 8, 1608, 800)),
            result.refinement_budgets,
        )
        self.assertTrue(result.same_physical_horizon_across_refinements)
        self.assertTrue(result.same_source_supports_across_refinements)
        self.assertTrue(result.same_completion_ticks_across_refinements)

    def test_no_missing_elapsed_time_scaling_is_found(self) -> None:
        result = audit_e1_common_probe_s1fb_discretization_scaling()
        self.assertTrue(result.field_rates_are_per_second)
        self.assertTrue(result.e1_rates_are_per_second)
        self.assertFalse(result.fixed_per_step_accumulation_present)
        self.assertFalse(result.missing_dt_scaling_defect_found)

    def test_first_nonexact_stage_is_e1_formation_splitting(self) -> None:
        result = audit_e1_common_probe_s1fb_discretization_scaling()
        self.assertTrue(result.neutral_field_piecewise_exact)
        self.assertTrue(result.frozen_probe_piecewise_exact)
        self.assertTrue(result.e1_formation_uses_endpoint_half_steps)
        self.assertEqual(
            "nonlinear-e1-formation-endpoint-splitting",
            result.first_structurally_discretization_sensitive_stage,
        )

    def test_observed_decrements_nearly_halve_but_do_not_prove_order(self) -> None:
        result = audit_e1_common_probe_s1fb_discretization_scaling()
        activation, afterimage = result.observed_scaling
        self.assertGreater(activation.successive_decrease_ratio, 0.46)
        self.assertLess(activation.successive_decrease_ratio, 0.47)
        self.assertGreater(afterimage.successive_decrease_ratio, 0.46)
        self.assertLess(afterimage.successive_decrease_ratio, 0.47)
        self.assertFalse(result.observed_scaling_proves_convergence_order)
        self.assertFalse(result.observed_scaling_proves_instability)

    def test_audit_is_deterministic_and_cannot_open_execution(self) -> None:
        first = audit_e1_common_probe_s1fb_discretization_scaling()
        second = audit_e1_common_probe_s1fb_discretization_scaling()
        self.assertEqual(first.audit_digest, second.audit_digest)
        with self.assertRaises(E1CommonProbeS1FBDiscretizationScalingAuditError):
            replace(first, field_execution_permitted=True)

    def test_audit_does_not_call_runner_adapter_decider_or_writer(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_s1fb_discretization_scaling)
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_e1_common_probe_ec96_authorized_r4_r8_once(",
            "run_prepared_real_formation_arm_in_memory(",
            "run_e1_common_probe_real_probe_wrapper(",
            "decide_common_probe_evidence(",
            "write_text(",
            "write_bytes(",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
