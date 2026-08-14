from __future__ import annotations

import unittest

from mcm_field_organism.s1p_exposure_retention_evaluator import (
    evaluate_s1p_exposure_retention_matrix,
    s1p_exposure_retention_evaluation_public_roles,
)


class S1PExposureRetentionEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = evaluate_s1p_exposure_retention_matrix()

    def test_complete_matrix_and_every_control_are_present(self) -> None:
        result = self.result

        self.assertEqual(32, len(result.cells))
        self.assertEqual(8, len(result.erhaltungshorizons))
        self.assertTrue(result.source_controls_hold)
        self.assertTrue(result.alignment_controls_hold)
        self.assertTrue(result.mass_controls_hold)
        self.assertTrue(result.sentinel_null_controls_hold)
        self.assertTrue(result.repeatability_control_holds)
        self.assertTrue(result.finite_metrics_hold)
        self.assertTrue(result.all_controls_hold)

    def test_every_cell_uses_its_local_preregistered_floor(self) -> None:
        for cell in self.result.cells:
            with self.subTest(cell=cell.cell.cell_id):
                self.assertEqual(
                    8.0 * cell.refinement_2_4_linf,
                    cell.convergence_floor,
                )
                self.assertEqual(
                    max(1e-12, cell.convergence_floor),
                    cell.detection_floor,
                )
                self.assertGreaterEqual(cell.linear_relative_residual, 0.0)

    def test_outputs_are_only_preregistered_classification_roles(self) -> None:
        result = self.result

        self.assertEqual(
            "MONOTONIC_DOSE_GRADATION",
            result.dose_classification,
        )
        self.assertEqual(
            "NONMONOTONIC_NULL_CONTACT_RESPONSE",
            result.attenuation_classification,
        )
        self.assertEqual(
            "EVENT_SEGMENTATION_SENSITIVE",
            result.segmentation_classification,
        )
        self.assertEqual(
            "CURVE_LINEARLY_EXPLAINED",
            result.mechanism_classification,
        )
        self.assertEqual(27, result.detected_cell_count)
        self.assertLessEqual(result.maximum_linear_relative_residual, 0.05)
        self.assertGreater(result.maximum_segmentation_effect_vector_linf, 0.0)
        self.assertTrue(
            all(item.right_censored for item in result.erhaltungshorizons)
        )

    def test_evaluator_has_no_runtime_or_claim_authority(self) -> None:
        result = self.result

        self.assertFalse(result.raw_payload_retained)
        self.assertFalse(result.runtime_writeback_allowed)
        self.assertFalse(result.formal_research_run)
        self.assertFalse(result.memory_claim_allowed)
        self.assertFalse(result.learning_claim_allowed)
        self.assertFalse(result.field_time_claim_allowed)
        self.assertFalse(result.organization_claim_allowed)
        self.assertFalse(result.ai_claim_allowed)
        self.assertTrue(
            {
                "world_payload",
                "label",
                "reward",
                "meaning",
                "observer_writeback",
                "target_topology",
            }.isdisjoint(s1p_exposure_retention_evaluation_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
