from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.w7aw_observer_profile_evaluation_contract import (
    W7AWObserverProfileEvaluationContractError,
    build_w7aw_observer_profile_evaluation_contract,
)


class W7AWObserverProfileEvaluationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_w7aw_observer_profile_evaluation_contract()

    def test_contract_binds_w7av_without_accepting_values(self) -> None:
        self.assertEqual(
            "cc123faadefb32e0cc9d0d35db8512b6ecbb74ff62376ead23475382364f2acd",
            self.contract.required_w7av_result_digest,
        )
        self.assertFalse(self.contract.accept_result_values)
        self.assertFalse(self.contract.profile_decision_allowed)
        self.assertEqual(
            "37ae530d3a776db2b7b29f593efcb66482ff6b89a920c5d90b9b9085f4ffa7ff",
            self.contract.contract_digest,
        )

    def test_observer_floor_uses_only_same_input_repeat_controls(self) -> None:
        self.assertEqual(105, self.contract.identity_repeat_control_count)
        self.assertEqual(
            "maximum-same-input-repeat-observer-output-trace-linf",
            self.contract.observer_epsilon_source,
        )
        self.assertEqual(10.0, self.contract.observer_effect_floor_factor)
        self.assertEqual(
            "exact-zero-floor-remains-zero",
            self.contract.zero_identity_policy,
        )
        self.assertFalse(self.contract.field_floor_applied_to_observer)

    def test_profile_mapping_is_symmetric_and_keeps_neutral_controls(self) -> None:
        self.assertEqual(("ab", "ba"), self.contract.required_directions)
        self.assertEqual(2, len(self.contract.profile_mapping))
        self.assertTrue(
            all(len(mapping) == 5 for mapping in self.contract.profile_mapping)
        )
        self.assertEqual(
            "required-audit-control-not-profile-coordinate",
            self.contract.neutral_contrast_role,
        )

    def test_profiles_use_own_resolved_denominator_without_rescue(self) -> None:
        self.assertEqual(
            "initial-old-effect-strictly-above-observer-floor",
            self.contract.denominator_rule,
        )
        self.assertEqual("no-epsilon-rescue", self.contract.unresolved_policy)
        self.assertEqual(
            "each-profile-by-own-initial-old-effect",
            self.contract.normalization_rule,
        )

    def test_explanation_requires_both_directions_at_fixed_limit(self) -> None:
        self.assertEqual(0.05, self.contract.explanation_limit)
        self.assertEqual(
            "linf-over-three-curves-and-five-checkpoints",
            self.contract.profile_distance_metric,
        )
        self.assertEqual(
            "both-ab-and-ba-profile-distances-at-most-limit",
            self.contract.model_match_rule,
        )
        self.assertEqual(("leak", "sat", "norm"), self.contract.model_precedence)

    def test_outcomes_and_claim_locks_are_complete(self) -> None:
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
        self.assertFalse(self.contract.field_function_decision_allowed)
        self.assertFalse(self.contract.memory_claim_allowed)

    def test_builder_has_no_value_input_and_rejects_tampering(self) -> None:
        self.assertEqual(
            0,
            len(
                inspect.signature(
                    build_w7aw_observer_profile_evaluation_contract
                ).parameters
            ),
        )
        with self.assertRaises(W7AWObserverProfileEvaluationContractError):
            replace(self.contract, explanation_limit=0.1)

    def test_contract_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(
                current_api,
                "build_w7aw_observer_profile_evaluation_contract",
            )
        )


if __name__ == "__main__":
    unittest.main()
