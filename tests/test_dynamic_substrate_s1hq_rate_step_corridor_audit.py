from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1hq_rate_step_corridor_audit import (
    DTS1S1HQRateStepCorridorAuditError,
    S1_HQ_DECISION,
    audit_dts1_s1hq_rate_step_corridor,
)


class DTS1S1HQRateStepCorridorAuditTests(unittest.TestCase):
    def _audit(self):
        return audit_dts1_s1hq_rate_step_corridor()

    def test_dimensions_and_dimensionless_groups_are_closed(self) -> None:
        audit = self._audit()
        dimensions = dict(audit.dimensions)
        groups = dict(audit.dimensionless_groups)
        self.assertEqual("inverse-time", dimensions["k_bind,k_turn,k_rec"])
        self.assertEqual("time", dimensions["Delta_t,T"])
        self.assertEqual("k_bind*Delta_t", groups["theta_bind"])
        self.assertEqual("1-exp(-theta_x)", groups["alpha_x"])

    def test_joint_corridor_limits_source_fraction_only_for_resolution(self) -> None:
        audit = self._audit()
        self.assertEqual(0.5, audit.technical_max_source_fraction)
        self.assertIn(
            "each-theta_x-not-greater-than-ln(2)",
            audit.joint_step_corridor,
        )
        self.assertIn(
            "equivalently-each-alpha_x-not-greater-than-0.5",
            audit.joint_step_corridor,
        )
        self.assertTrue(audit.resolution_corridor_is_not_stability_bound)
        self.assertTrue(audit.positivity_unconditional_for_nonnegative_rates)
        self.assertTrue(audit.conservation_unconditional_for_valid_prestate)

    def test_interval_partition_and_refinement_are_bound_without_runtime(self) -> None:
        corridor = self._audit().joint_step_corridor
        self.assertIn(
            "positive-closed-interval-T-uses-n=max(1,ceil(T*k_max/ln(2)))",
            corridor,
        )
        self.assertIn(
            "uniform-substep-Delta_t=T/n-ends-exactly-at-closed-boundary",
            corridor,
        )
        self.assertIn(
            "refinement-levels-use-n-2n-and-4n-with-identical-physical-input",
            corridor,
        )

    def test_null_controls_are_separate_from_positive_functional_interior(self) -> None:
        audit = self._audit()
        self.assertEqual(
            {"k_bind=0", "k_turn=0", "k_rec=0", "all-rates=0", "Delta_t=0"},
            {name for name, _ in audit.null_boundaries},
        )
        self.assertIn(
            "functional-three-role-interior-requires-all-three-rates-positive",
            audit.rate_domains,
        )

    def test_identifiability_keeps_absolute_timescale_and_rate_order_open(self) -> None:
        audit = self._audit()
        self.assertIn(
            "one-step-map-identifies-only-dimensionless-rate-interval-products",
            audit.identifiability_limits,
        )
        self.assertTrue(audit.one_global_triplet_required_later)
        for value in (
            audit.absolute_rate_values_selected,
            audit.positive_lower_rate_bound_selected,
            audit.absolute_upper_rate_bound_selected,
            audit.rate_ordering_selected,
            audit.parameter_estimation_performed,
        ):
            self.assertFalse(value)

    def test_field_runtime_execution_and_claims_remain_closed(self) -> None:
        audit = self._audit()
        for value in (
            audit.field_backreaction_selected,
            audit.runtime_integration_present,
            audit.research_execution_permitted,
            audit.functional_effect_proven,
            audit.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, audit.field_steps_executed)
        self.assertEqual(S1_HQ_DECISION, audit.decision)

    def test_audit_is_deterministic_tamper_evident_and_static(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1HQRateStepCorridorAuditError):
            replace(audit, absolute_rate_values_selected=True)
        with self.assertRaises(DTS1S1HQRateStepCorridorAuditError):
            replace(audit, technical_max_source_fraction=0.75)
        source = inspect.getsource(audit_dts1_s1hq_rate_step_corridor)
        for forbidden in ("compute_dts1_closed_prestate_step", "field_runner", "open("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
