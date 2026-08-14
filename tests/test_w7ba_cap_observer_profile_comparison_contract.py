from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.w7ba_cap_observer_profile_comparison_contract import (
    W7BACAPObserverProfileComparisonContractError,
    build_w7ba_cap_observer_profile_comparison_contract,
)


class W7BACAPObserverProfileComparisonContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_w7ba_cap_observer_profile_comparison_contract()

    def test_contract_binds_canonical_profile_sources(self) -> None:
        self.assertEqual(
            "7729f162d5702bf9008eac107148bbb9f85f58dce244e5bf726657b4535cd9ba",
            self.contract.required_w7ax_evaluation_digest,
        )
        self.assertEqual(
            "ecb14d76ab49a05010c4d988308f729415d7583570d0908f2588df0964254d9f",
            self.contract.required_w7az_composition_digest,
        )
        self.assertEqual(
            "131e18bb4ab7fa862ea8886ee338353b2fcffc6055e6bd15e2419b29ab36dccc",
            self.contract.contract_digest,
        )

    def test_exact_profile_inventory_is_required(self) -> None:
        self.assertEqual(2, self.contract.required_cap_profile_count)
        self.assertEqual(6, self.contract.required_observer_profile_count)
        self.assertEqual(("ab", "ba"), self.contract.required_directions)
        self.assertEqual(
            ("old_b_retention", "old_g_retention", "new_b_gain"),
            self.contract.profile_curves,
        )

    def test_only_dimensionless_profile_linf_is_compared(self) -> None:
        self.assertEqual(
            "linf-over-three-dimensionless-curves-and-five-checkpoints",
            self.contract.direction_distance_metric,
        )
        self.assertEqual(
            "maximum-of-ab-and-ba-direction-distances",
            self.contract.model_distance_metric,
        )
        self.assertFalse(self.contract.absolute_amplitude_comparison_allowed)
        self.assertFalse(self.contract.neutral_control_is_profile_coordinate)

    def test_resolution_limit_and_precedence_are_frozen(self) -> None:
        self.assertEqual(
            "all-compared-profiles-must-be-resolved",
            self.contract.resolution_rule,
        )
        self.assertEqual(0.05, self.contract.explanation_limit)
        self.assertEqual(
            ("leak", "sat", "norm"),
            self.contract.observer_model_precedence,
        )

    def test_outcomes_are_observer_explanations_not_field_decisions(self) -> None:
        self.assertEqual(
            (
                "NOT_RESOLVED",
                "PROFILE_NOT_MATCHED",
                "PROFILE_EXPLAINED_BY_LEAK",
                "PROFILE_EXPLAINED_BY_SAT",
                "PROFILE_EXPLAINED_BY_NORM",
            ),
            self.contract.outcomes,
        )
        self.assertFalse(self.contract.profile_explanation_decision_allowed)
        self.assertFalse(self.contract.field_function_decision_allowed)
        self.assertFalse(self.contract.memory_claim_allowed)

    def test_builder_accepts_no_values_and_tampering_is_rejected(self) -> None:
        self.assertEqual(
            0,
            len(
                inspect.signature(
                    build_w7ba_cap_observer_profile_comparison_contract
                ).parameters
            ),
        )
        self.assertFalse(self.contract.accept_result_values)
        with self.assertRaises(W7BACAPObserverProfileComparisonContractError):
            replace(self.contract, explanation_limit=0.5)

    def test_contract_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(
                current_api,
                "build_w7ba_cap_observer_profile_comparison_contract",
            )
        )


if __name__ == "__main__":
    unittest.main()
