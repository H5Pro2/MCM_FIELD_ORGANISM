from __future__ import annotations

import unittest

from mcm_field_organism.s1s_phase_separation_evaluator import (
    evaluate_s1s_phase_separation_matrix,
    s1s_phase_separation_evaluation_public_roles,
)


class S1SPhaseSeparationEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = evaluate_s1s_phase_separation_matrix()

    def test_complete_matrix_and_controls_are_present(self) -> None:
        result = self.result

        self.assertEqual(32, len(result.cells))
        self.assertEqual(16, len(result.windows))
        self.assertTrue(result.source_controls_hold)
        self.assertTrue(result.alignment_controls_hold)
        self.assertTrue(result.mass_controls_hold)
        self.assertTrue(result.sentinel_null_controls_hold)
        self.assertTrue(result.repeatability_control_holds)
        self.assertTrue(result.finite_metrics_hold)
        self.assertTrue(result.all_controls_hold)

    def test_every_cell_uses_separate_local_floors(self) -> None:
        for cell in self.result.cells:
            with self.subTest(cell=cell.cell.cell_id):
                self.assertEqual(
                    max(1e-12, 8.0 * cell.mass_refinement_2_4_linf),
                    cell.mass_detection_floor,
                )
                self.assertEqual(
                    max(1e-12, 8.0 * cell.probe_refinement_2_4_linf),
                    cell.probe_detection_floor,
                )
                self.assertGreaterEqual(cell.mass_linear_relative_residual, 0.0)
                self.assertGreaterEqual(cell.probe_linear_relative_residual, 0.0)

    def test_outputs_use_only_preregistered_roles(self) -> None:
        result = self.result

        self.assertEqual(
            "FORMATION_EXTENDS_BEYOND_FIXED_BOUNDARY",
            result.phase_classification,
        )
        self.assertEqual(
            "PHASE_CURVES_LINEARLY_EXPLAINED",
            result.mechanism_classification,
        )
        self.assertEqual(29, result.detected_mass_cell_count)
        self.assertEqual(29, result.detected_probe_cell_count)
        self.assertLessEqual(result.maximum_mass_linear_relative_residual, 0.05)
        self.assertLessEqual(result.maximum_probe_linear_relative_residual, 0.05)
        self.assertAlmostEqual(
            0.03741898881868446,
            result.maximum_mass_linear_relative_residual,
            places=15,
        )
        self.assertAlmostEqual(
            0.043589721634606275,
            result.maximum_probe_linear_relative_residual,
            places=15,
        )
        expected = {
            ("preprobe-mass", 1, "repeated-supports", "early"):
                "WINDOW_INCREASE",
            ("preprobe-mass", 1, "repeated-supports", "late"):
                "WINDOW_MIXED",
            ("preprobe-mass", 1, "continuous-support", "early"):
                "WINDOW_INCREASE",
            ("preprobe-mass", 1, "continuous-support", "late"):
                "WINDOW_MIXED",
            ("preprobe-mass", 8, "repeated-supports", "early"):
                "WINDOW_INCREASE",
            ("preprobe-mass", 8, "repeated-supports", "late"):
                "WINDOW_DECREASE",
            ("preprobe-mass", 8, "continuous-support", "early"):
                "WINDOW_INCREASE",
            ("preprobe-mass", 8, "continuous-support", "late"):
                "WINDOW_MIXED",
            ("probe-effect", 1, "repeated-supports", "early"):
                "WINDOW_INCREASE",
            ("probe-effect", 1, "repeated-supports", "late"):
                "WINDOW_DECREASE",
            ("probe-effect", 1, "continuous-support", "early"):
                "WINDOW_INCREASE",
            ("probe-effect", 1, "continuous-support", "late"):
                "WINDOW_DECREASE",
            ("probe-effect", 8, "repeated-supports", "early"):
                "WINDOW_MIXED",
            ("probe-effect", 8, "repeated-supports", "late"):
                "WINDOW_DECREASE",
            ("probe-effect", 8, "continuous-support", "early"):
                "WINDOW_INCREASE",
            ("probe-effect", 8, "continuous-support", "late"):
                "WINDOW_DECREASE",
        }
        self.assertEqual(
            expected,
            {
                (
                    item.metric_role,
                    item.dose_count,
                    item.source_form,
                    item.window_role,
                ): item.classification
                for item in result.windows
            },
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
            }.isdisjoint(s1s_phase_separation_evaluation_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
