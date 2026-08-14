from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.w7aa_p0_seven_path_consumer import (
    consume_w7aa_p0_seven_path_plan,
)
from mcm_field_organism.w7ac_observer_seven_path_consumer import (
    consume_w7ac_observer_seven_path_result,
)
from mcm_field_organism.w7av_observer_path_contrast_binder import (
    W7AVObserverPathContrastBinderError,
    bind_w7av_observer_path_contrasts,
)
from mcm_field_organism.w7m_capacity_function_matrix import (
    build_w7m_capacity_function_matrix_adapter,
)
from mcm_field_organism.w7w_symmetric_source_family import (
    build_w7w_source_authorization,
    build_w7w_symmetric_source_family,
)
from mcm_field_organism.w7y_seven_path_source_plan import (
    build_w7y_seven_path_source_plan,
)


class W7AVObserverPathContrastBinderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        adapter = build_w7m_capacity_function_matrix_adapter()
        family = build_w7w_symmetric_source_family(adapter)
        authorization = build_w7w_source_authorization(adapter, family)
        plan = build_w7y_seven_path_source_plan(
            adapter,
            family,
            authorization,
        )
        p0_result = consume_w7aa_p0_seven_path_plan(
            adapter,
            family,
            authorization,
            plan,
        )
        cls.source = consume_w7ac_observer_seven_path_result(
            adapter,
            authorization,
            plan,
            p0_result,
        )
        cls.result = bind_w7av_observer_path_contrasts(cls.source)

    def test_all_three_models_and_eight_contrasts_are_bound(self) -> None:
        self.assertEqual(24, len(self.result.contrasts))
        self.assertEqual(
            tuple(
                (model, role)
                for model in ("leak", "sat", "norm")
                for role in (
                    "ab_old_a_under_b",
                    "ab_old_a_after_gap",
                    "ab_new_b_after_a",
                    "ab_new_b_after_neutral",
                    "ba_old_b_under_a",
                    "ba_old_b_after_gap",
                    "ba_new_a_after_b",
                    "ba_new_a_after_neutral",
                )
            ),
            tuple((item.model_id, item.contrast_role) for item in self.result.contrasts),
        )

    def test_each_contrast_contains_five_raw_nonnegative_distances(self) -> None:
        for item in self.result.contrasts:
            self.assertEqual(5, len(item.checkpoint_linf))
            self.assertTrue(all(value >= 0.0 for value in item.checkpoint_linf))
            self.assertFalse(item.normalized)
            self.assertFalse(item.decision_allowed)

    def test_w7at_field_floor_is_bound_but_never_applied_to_observers(self) -> None:
        self.assertEqual(
            "b6ff73ac1b85344a5aa925506dba599bb9b3956abeb4eca0e6b0f9e63087b99c",
            self.result.w7at_evaluation_digest,
        )
        self.assertEqual(1.8915768951188738e-07, self.result.w7at_field_effect_floor)
        self.assertFalse(self.result.field_floor_applied_to_observer)

    def test_source_is_preserved_and_rebinding_is_exact(self) -> None:
        before = self.source.observer_seven_path_consumption_digest
        repeated = bind_w7av_observer_path_contrasts(self.source)
        self.assertEqual(self.result, repeated)
        self.assertEqual(
            "cc123faadefb32e0cc9d0d35db8512b6ecbb74ff62376ead23475382364f2acd",
            self.result.result_digest,
        )
        self.assertEqual(before, self.source.observer_seven_path_consumption_digest)

    def test_no_profile_explanation_function_or_memory_decision_is_allowed(self) -> None:
        self.assertFalse(self.result.profile_composition_allowed)
        self.assertFalse(self.result.observer_explanation_allowed)
        self.assertFalse(self.result.field_function_decision_allowed)
        self.assertFalse(self.result.memory_claim_allowed)

    def test_result_rejects_role_and_floor_tampering(self) -> None:
        with self.assertRaises(W7AVObserverPathContrastBinderError):
            replace(self.result, field_floor_applied_to_observer=True)
        with self.assertRaises(W7AVObserverPathContrastBinderError):
            replace(self.result.contrasts[0], normalized=True)

    def test_binder_is_not_reexported_from_current_api(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(current_api, "bind_w7av_observer_path_contrasts"))


if __name__ == "__main__":
    unittest.main()
