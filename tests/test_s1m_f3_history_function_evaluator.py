from __future__ import annotations

import unittest

from mcm_field_organism.s1l_f3_history_function_adapter import (
    S1L_ABSOLUTE_FLOOR,
    S1L_LINEAR_EQUIVALENCE_LIMIT,
)
from mcm_field_organism.s1m_f3_history_function_evaluator import (
    evaluate_s1m_f3_history_function,
    s1m_f3_history_function_evaluation_public_roles,
)


class S1MF3HistoryFunctionEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = evaluate_s1m_f3_history_function()

    def test_every_preregistered_control_holds(self) -> None:
        result = self.result

        self.assertTrue(result.source_controls_hold)
        self.assertTrue(result.fast_alignment_controls_hold)
        self.assertTrue(result.null_controls_hold)
        self.assertTrue(result.mass_controls_hold)
        self.assertTrue(result.repeatability_control_holds)
        self.assertTrue(result.rebind_control_holds)
        self.assertTrue(result.all_controls_hold)

    def test_detection_floor_uses_only_the_preregistered_formula(self) -> None:
        result = self.result

        self.assertEqual(
            8.0 * result.refinement_2_4_linf,
            result.convergence_floor,
        )
        self.assertEqual(
            max(S1L_ABSOLUTE_FLOOR, result.convergence_floor),
            result.detection_floor,
        )
        self.assertGreater(result.f3_effect_linf, result.detection_floor)
        self.assertTrue(result.effect_detected)

    def test_registered_classification_is_linear_explanation(self) -> None:
        result = self.result

        self.assertLessEqual(
            result.linear_relative_residual,
            S1L_LINEAR_EQUIVALENCE_LIMIT,
        )
        self.assertTrue(result.linear_equivalent)
        self.assertEqual(
            "TRANSPARENT_HISTORY_EFFECT_LINEARLY_EXPLAINED",
            result.classification,
        )

    def test_evaluator_has_no_runtime_or_claim_authority(self) -> None:
        result = self.result

        self.assertFalse(result.raw_payload_retained)
        self.assertFalse(result.runtime_writeback_allowed)
        self.assertFalse(result.formal_research_run)
        self.assertFalse(result.memory_claim_allowed)
        self.assertFalse(result.learning_claim_allowed)
        self.assertFalse(result.organization_claim_allowed)
        self.assertFalse(result.topology_claim_allowed)
        self.assertFalse(result.semantics_claim_allowed)
        self.assertFalse(result.ai_claim_allowed)
        self.assertTrue(
            {
                "world_payload",
                "label",
                "reward",
                "meaning",
                "target_topology",
                "observer_writeback",
            }.isdisjoint(s1m_f3_history_function_evaluation_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
