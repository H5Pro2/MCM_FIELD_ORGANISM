from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.w7aq_numerical_evaluation_contract import (
    W7AQNumericalEvaluationContractError,
    build_w7aq_numerical_evaluation_contract,
)


class W7AQNumericalEvaluationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_w7aq_numerical_evaluation_contract()

    def test_contract_binds_canonical_provenance_without_result_digest(self):
        self.assertEqual(
            "4f150aad9f5c3803f1432550aa4db79b40aea3f7a4975b49802694fad2fff3e5",
            self.contract.required_w7an_container_digest,
        )
        self.assertEqual(
            "14455f15e6f3d0f96106aa766ae544ec76f19b5c94308329ec45fd0cd12067dc",
            self.contract.required_w7ao_contract_digest,
        )
        self.assertEqual(
            "w7ap.raw-r1-r2-r2-r4-resolution-distance-compositor.v1",
            self.contract.required_w7ap_compositor_id,
        )

    def test_exact_inventory_and_component_checks_are_fixed(self):
        self.assertEqual(
            (35, 70, 105, 70),
            (
                self.contract.role_count,
                self.contract.distance_count,
                self.contract.identity_control_count,
                self.contract.component_check_count,
            ),
        )
        self.assertEqual(("S_linf", "H_linf"), self.contract.primary_metrics)
        self.assertEqual(("SH_l2",), self.contract.diagnostic_metrics)

    def test_convergence_rule_has_only_the_exact_zero_exception(self):
        self.assertEqual(
            "each-role-and-primary-metric-d24-less-than-d12-or-both-zero",
            self.contract.convergence_rule,
        )

    def test_numerical_floor_is_available_only_after_full_convergence(self):
        self.assertEqual(
            "maximum-of-all-r2-r4-primary-linf-distances",
            self.contract.epsilon_source,
        )
        self.assertEqual(10.0, self.contract.effect_floor_factor)
        self.assertEqual(
            "no-epsilon-and-no-effect-floor",
            self.contract.unresolved_policy,
        )

    def test_only_two_nonfunctional_outcomes_are_allowed(self):
        self.assertEqual(
            (
                "NUMERICALLY_UNRESOLVED",
                "RESOLUTION_COMPARISON_CONVERGED",
            ),
            self.contract.outcomes,
        )
        self.assertFalse(self.contract.field_function_decision_allowed)
        self.assertFalse(self.contract.memory_claim_allowed)

    def test_all_ten_missing_function_baselines_remain_explicit(self):
        self.assertEqual(
            (
                "LEAK",
                "LIN",
                "F3",
                "CONST-V",
                "SAT",
                "MOB",
                "NORM",
                "ETA0",
                "KAPPA0",
                "SIGN",
            ),
            self.contract.missing_function_baselines,
        )

    def test_builder_accepts_no_values_and_tampering_is_rejected(self):
        self.assertEqual(
            0,
            len(
                inspect.signature(
                    build_w7aq_numerical_evaluation_contract
                ).parameters
            ),
        )
        self.assertFalse(self.contract.accept_result_values)
        with self.assertRaises(W7AQNumericalEvaluationContractError):
            replace(self.contract, effect_floor_factor=1.0)

    def test_contract_is_not_publicly_exported(self):
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "build_w7aq_numerical_evaluation_contract")
        )


if __name__ == "__main__":
    unittest.main()
