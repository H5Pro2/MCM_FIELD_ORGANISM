from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.w7ax_observer_profile_evaluator import (
    W7AXObserverProfileEvaluationResult,
    W7AXObserverProfileRecord,
)
from mcm_field_organism.w7az_cap_field_profile_compositor import (
    W7AZCAPFieldProfileComposition,
    W7AZCAPProfileRecord,
)
from mcm_field_organism.w7ba_cap_observer_profile_comparison_contract import (
    build_w7ba_cap_observer_profile_comparison_contract,
)
import mcm_field_organism.w7bb_terminal_profile_evaluator as evaluator
from mcm_field_organism.w7p_measurement_compositor import W7PLifecycleProfile


def _profile(surface, model, direction, value, resolution="RESOLVED"):
    curves = () if resolution == "NOT_RESOLVED" else (value,) * 5
    return W7PLifecycleProfile(
        surface,
        model,
        direction,
        resolution,
        curves,
        curves,
        curves,
    )


def _sources(observer_values, cap_value=0.0, unresolved=False):
    observer = object.__new__(W7AXObserverProfileEvaluationResult)
    object.__setattr__(
        observer,
        "evaluation_digest",
        "7729f162d5702bf9008eac107148bbb9f85f58dce244e5bf726657b4535cd9ba",
    )
    observer_profiles = []
    for model in ("leak", "sat", "norm"):
        for direction in ("ab", "ba"):
            profile = _profile(
                "observer",
                model,
                direction,
                observer_values[model],
                "NOT_RESOLVED" if unresolved and model == "leak" else "RESOLVED",
            )
            record = object.__new__(W7AXObserverProfileRecord)
            object.__setattr__(record, "profile", profile)
            observer_profiles.append(record)
    object.__setattr__(observer, "profiles", tuple(observer_profiles))

    cap = object.__new__(W7AZCAPFieldProfileComposition)
    object.__setattr__(
        cap,
        "composition_digest",
        "ecb14d76ab49a05010c4d988308f729415d7583570d0908f2588df0964254d9f",
    )
    cap_profiles = []
    for direction in ("ab", "ba"):
        record = object.__new__(W7AZCAPProfileRecord)
        object.__setattr__(record, "profile", _profile("field", "cap", direction, cap_value))
        cap_profiles.append(record)
    object.__setattr__(cap, "profiles", tuple(cap_profiles))
    return observer, cap


class W7BBTerminalProfileEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = build_w7ba_cap_observer_profile_comparison_contract()

    def test_precedence_selects_first_matched_model(self) -> None:
        observer, cap = _sources({"leak": 0.04, "sat": 0.03, "norm": 0.02})
        state = evaluator._start_w7bb_terminal_profile_evaluator()
        result = evaluator._evaluate_w7bb_terminal_profiles(
            state, self.contract, observer, cap
        )
        self.assertEqual("PROFILE_EXPLAINED_BY_LEAK", result.outcome)
        self.assertEqual((True, True, True), tuple(item.matched for item in result.model_comparisons))

    def test_unmatched_profiles_have_only_not_matched_outcome(self) -> None:
        observer, cap = _sources({"leak": 0.06, "sat": 0.07, "norm": 0.08})
        result = evaluator._evaluate_w7bb_terminal_profiles(
            evaluator._start_w7bb_terminal_profile_evaluator(),
            self.contract,
            observer,
            cap,
        )
        self.assertEqual("PROFILE_NOT_MATCHED", result.outcome)

    def test_unresolved_profile_stops_before_distances(self) -> None:
        observer, cap = _sources(
            {"leak": 0.0, "sat": 0.0, "norm": 0.0}, unresolved=True
        )
        result = evaluator._evaluate_w7bb_terminal_profiles(
            evaluator._start_w7bb_terminal_profile_evaluator(),
            self.contract,
            observer,
            cap,
        )
        self.assertEqual("NOT_RESOLVED", result.outcome)
        self.assertEqual((), result.model_comparisons)

    def test_success_locks_state_and_keeps_claims_false(self) -> None:
        observer, cap = _sources({"leak": 0.0, "sat": 1.0, "norm": 1.0})
        state = evaluator._start_w7bb_terminal_profile_evaluator()
        result = evaluator._evaluate_w7bb_terminal_profiles(
            state, self.contract, observer, cap
        )
        self.assertIs(result, state.result)
        self.assertFalse(result.persisted)
        self.assertFalse(result.writes_back)
        self.assertFalse(result.field_function_decision_allowed)
        self.assertFalse(result.memory_claim_allowed)
        with self.assertRaisesRegex(
            evaluator.W7BBTerminalProfileEvaluatorError,
            "already attempted",
        ):
            evaluator._evaluate_w7bb_terminal_profiles(
                state, self.contract, observer, cap
            )

    def test_failure_locks_state(self) -> None:
        observer, cap = _sources({"leak": 0.0, "sat": 0.0, "norm": 0.0})
        state = evaluator._start_w7bb_terminal_profile_evaluator()
        object.__setattr__(observer, "evaluation_digest", "wrong")
        with self.assertRaisesRegex(
            evaluator.W7BBTerminalProfileEvaluatorError,
            "provenance",
        ):
            evaluator._evaluate_w7bb_terminal_profiles(
                state, self.contract, observer, cap
            )
        with self.assertRaisesRegex(
            evaluator.W7BBTerminalProfileEvaluatorError,
            "already attempted",
        ):
            evaluator._evaluate_w7bb_terminal_profiles(
                state, self.contract, observer, cap
            )

    def test_result_tampering_is_rejected(self) -> None:
        observer, cap = _sources({"leak": 0.0, "sat": 1.0, "norm": 1.0})
        result = evaluator._evaluate_w7bb_terminal_profiles(
            evaluator._start_w7bb_terminal_profile_evaluator(),
            self.contract,
            observer,
            cap,
        )
        with self.assertRaises(evaluator.W7BBTerminalProfileEvaluatorError):
            replace(result, memory_claim_allowed=True)

    def test_evaluator_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(current_api, "_evaluate_w7bb_terminal_profiles"))


if __name__ == "__main__":
    unittest.main()
