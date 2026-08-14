from __future__ import annotations

import unittest

from mcm_field_organism.s1w_component_matrix_evaluator import (
    evaluate_s1w_component_matrix,
    s1w_component_matrix_evaluation_public_roles,
)


class S1WComponentMatrixEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = evaluate_s1w_component_matrix()

    def test_complete_matrix_and_controls_are_present(self) -> None:
        result = self.result

        self.assertEqual(28, len(result.cells))
        self.assertTrue(result.inventory_control_holds)
        self.assertTrue(result.balance_controls_hold)
        self.assertTrue(result.observer_transparency_holds)
        self.assertTrue(result.kappa_null_controls_hold)
        self.assertTrue(result.null_controls_hold)
        self.assertTrue(result.repeatability_control_holds)
        self.assertTrue(result.finite_metrics_hold)
        self.assertTrue(result.all_controls_hold)

    def test_every_cell_has_separate_component_floors(self) -> None:
        for cell in self.result.cells:
            with self.subTest(cell=cell.cell.ledger_id):
                self.assertGreaterEqual(cell.transport_detection_floor, 1e-12)
                self.assertGreaterEqual(
                    cell.activation_forcing_detection_floor,
                    1e-12,
                )
                self.assertGreaterEqual(
                    cell.mass_increment_detection_floor,
                    1e-12,
                )
                self.assertLessEqual(cell.maximum_closure_linf, 1e-12)
                self.assertTrue(cell.all_arms_transparent)

    def test_outputs_use_only_preregistered_roles(self) -> None:
        result = self.result

        self.assertEqual(
            "ACTIVATION_FORCING_REQUIRED_FOR_LATE_MIXTURE",
            result.direct_drive_classification,
        )
        self.assertEqual(
            "RECIPROCAL_BACKREACTION_CHANGES_LATE_LEDGER",
            result.backreaction_classification,
        )
        self.assertEqual(
            "COMPONENT_LEDGER_CONTAINS_BASELINE_DIFFERENT_INTERVAL",
            result.mechanism_classification,
        )
        self.assertEqual(56, result.detected_direct_component_count)
        self.assertEqual(3, result.active_late_increase_count)
        self.assertEqual(9, result.active_late_decrease_count)
        self.assertEqual(0, result.kappa_null_late_increase_count)
        self.assertEqual(12, result.eta_different_late_interval_count)
        self.assertAlmostEqual(
            0.05752400477029081,
            result.maximum_linear_relative_residual,
            places=15,
        )
        self.assertAlmostEqual(
            3.346118954833388e-16,
            result.maximum_closure_linf,
            places=28,
        )
        self.assertEqual(
            {
                "s1v.d1.repeated.interval-0p200-0p400",
                "s1v.d1.continuous.interval-0p200-0p400",
                "s1v.d8.continuous.interval-0p200-0p400",
            },
            {
                cell.cell.ledger_id
                for cell in result.cells
                if cell.cell.ledger_role == "late-interval"
                and cell.active_mass_direction == "INCREASE"
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
            }.isdisjoint(s1w_component_matrix_evaluation_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
