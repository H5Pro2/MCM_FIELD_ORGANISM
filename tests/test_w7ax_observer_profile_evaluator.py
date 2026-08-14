from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.w7aa_p0_seven_path_consumer import consume_w7aa_p0_seven_path_plan
from mcm_field_organism.w7ac_observer_seven_path_consumer import consume_w7ac_observer_seven_path_result
from mcm_field_organism.w7av_observer_path_contrast_binder import bind_w7av_observer_path_contrasts
from mcm_field_organism.w7aw_observer_profile_evaluation_contract import build_w7aw_observer_profile_evaluation_contract
from mcm_field_organism.w7ax_observer_profile_evaluator import (
    W7AXObserverProfileEvaluatorError,
    evaluate_w7ax_observer_profiles,
)
from mcm_field_organism.w7m_capacity_function_matrix import build_w7m_capacity_function_matrix_adapter
from mcm_field_organism.w7w_symmetric_source_family import build_w7w_source_authorization, build_w7w_symmetric_source_family
from mcm_field_organism.w7y_seven_path_source_plan import build_w7y_seven_path_source_plan


class W7AXObserverProfileEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        adapter = build_w7m_capacity_function_matrix_adapter()
        family = build_w7w_symmetric_source_family(adapter)
        authorization = build_w7w_source_authorization(adapter, family)
        plan = build_w7y_seven_path_source_plan(adapter, family, authorization)
        p0 = consume_w7aa_p0_seven_path_plan(adapter, family, authorization, plan)
        cls.primary = consume_w7ac_observer_seven_path_result(
            adapter, authorization, plan, p0
        )
        cls.repeated = consume_w7ac_observer_seven_path_result(
            adapter, authorization, plan, p0
        )
        cls.raw = bind_w7av_observer_path_contrasts(cls.primary)
        cls.contract = build_w7aw_observer_profile_evaluation_contract()
        cls.result = evaluate_w7ax_observer_profiles(
            cls.contract, cls.raw, cls.primary, cls.repeated
        )

    def test_all_105_repeat_controls_are_exact_zero(self) -> None:
        self.assertEqual(105, len(self.result.repeat_controls))
        self.assertTrue(all(item.trace_linf == 0.0 for item in self.result.repeat_controls))
        self.assertEqual(0.0, self.result.observer_epsilon)
        self.assertEqual(0.0, self.result.observer_effect_floor)

    def test_six_symmetric_profiles_are_composed(self) -> None:
        self.assertEqual(
            tuple(
                (model, direction)
                for model in ("leak", "sat", "norm")
                for direction in ("ab", "ba")
            ),
            tuple(
                (item.profile.model_id, item.profile.direction)
                for item in self.result.profiles
            ),
        )

    def test_profile_resolution_is_reported_without_explanation(self) -> None:
        self.assertTrue(
            all(item.profile.resolution == "RESOLVED" for item in self.result.profiles)
        )
        self.assertEqual(
            "NOT_EVALUATED_NO_FIELD_PROFILES",
            self.result.observer_explanation,
        )
        self.assertEqual(
            "7729f162d5702bf9008eac107148bbb9f85f58dce244e5bf726657b4535cd9ba",
            self.result.evaluation_digest,
        )

    def test_evaluation_is_passive_and_keeps_claims_locked(self) -> None:
        self.assertFalse(self.result.field_floor_applied_to_observer)
        self.assertFalse(self.result.writes_back)
        self.assertFalse(self.result.field_function_decision_allowed)
        self.assertFalse(self.result.memory_claim_allowed)

    def test_same_object_cannot_pose_as_independent_repeat(self) -> None:
        with self.assertRaisesRegex(
            W7AXObserverProfileEvaluatorError,
            "independent repeat",
        ):
            evaluate_w7ax_observer_profiles(
                self.contract,
                self.raw,
                self.primary,
                self.primary,
            )

    def test_result_and_control_tampering_are_rejected(self) -> None:
        with self.assertRaises(W7AXObserverProfileEvaluatorError):
            replace(self.result, writes_back=True)
        with self.assertRaises(W7AXObserverProfileEvaluatorError):
            replace(self.result.repeat_controls[0], trace_linf=1.0)

    def test_evaluator_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(current_api, "evaluate_w7ax_observer_profiles"))


if __name__ == "__main__":
    unittest.main()
