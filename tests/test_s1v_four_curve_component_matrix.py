from __future__ import annotations

import math
import unittest

from mcm_field_organism.s1v_four_curve_component_matrix import (
    S1V_EARLY_CUMULATIVE_ENDS,
    S1V_LATE_INTERVALS,
    S1V_MODELS,
    S1VFourCurveComponentMatrixError,
    run_s1v_ledger_cell,
    s1v_four_curve_component_matrix_public_roles,
    s1v_ledger_inventory,
)


class S1VFourCurveComponentMatrixTests(unittest.TestCase):
    def test_inventory_separates_cumulative_and_nested_interval_ledgers(self) -> None:
        inventory = s1v_ledger_inventory()

        self.assertEqual(28, len(inventory))
        self.assertEqual(28, len({cell.ledger_id for cell in inventory}))
        self.assertEqual(
            16,
            sum(cell.ledger_role == "early-cumulative" for cell in inventory),
        )
        self.assertEqual(
            12,
            sum(cell.ledger_role == "late-interval" for cell in inventory),
        )
        self.assertEqual(
            set(S1V_EARLY_CUMULATIVE_ENDS),
            {
                cell.end_seconds
                for cell in inventory
                if cell.ledger_role == "early-cumulative"
            },
        )
        self.assertEqual(
            set(S1V_LATE_INTERVALS),
            {
                (cell.start_seconds, cell.end_seconds)
                for cell in inventory
                if cell.ledger_role == "late-interval"
            },
        )

    def test_all_four_arms_close_one_nested_late_interval(self) -> None:
        results = {
            model_id: run_s1v_ledger_cell(
                model_id,
                8,
                "repeated-supports",
                "late-interval",
                0.2,
                0.4,
                4,
            )
            for model_id in S1V_MODELS
        }

        self.assertEqual(set(S1V_MODELS), set(results))
        for model_id, measurement in results.items():
            with self.subTest(model=model_id):
                ledger = measurement.ledger
                self.assertTrue(ledger.observer_transparent)
                self.assertLessEqual(ledger.closure_linf, 1e-12)
                self.assertLessEqual(abs(ledger.transport_sum), 1e-12)
                self.assertLessEqual(
                    abs(ledger.activation_forcing_sum),
                    1e-12,
                )
                self.assertAlmostEqual(
                    0.2,
                    ledger.integrated_weight_seconds,
                    places=14,
                )
        self.assertEqual(
            (0.0,) * 26,
            results["kappa-null"].ledger.delta_activation_forcing,
        )
        self.assertEqual(
            (0.0,) * 26,
            results["kappa-null"].ledger.delta_transport,
        )
        self.assertEqual(
            (0.0,) * 26,
            results["kappa-null"].ledger.delta_mass,
        )
        self.assertGreater(
            max(
                abs(value)
                for value in results["eta-null"].ledger.delta_activation_forcing
            ),
            0.0,
        )

    def test_refinement_two_four_floors_are_finite_for_every_arm(self) -> None:
        for model_id in S1V_MODELS:
            coarse = run_s1v_ledger_cell(
                model_id,
                1,
                "continuous-support",
                "early-cumulative",
                0.0,
                0.2,
                2,
            ).ledger
            fine = run_s1v_ledger_cell(
                model_id,
                1,
                "continuous-support",
                "early-cumulative",
                0.0,
                0.2,
                4,
            ).ledger
            for role in (
                "delta_transport",
                "delta_activation_forcing",
                "delta_mass",
            ):
                difference = max(
                    abs(left - right)
                    for left, right in zip(
                        getattr(coarse, role),
                        getattr(fine, role),
                        strict=True,
                    )
                )
                with self.subTest(model=model_id, role=role):
                    self.assertTrue(math.isfinite(difference))
                    self.assertGreaterEqual(
                        max(1e-12, 8.0 * difference),
                        1e-12,
                    )

    def test_non_nested_interval_is_rejected(self) -> None:
        with self.assertRaises(S1VFourCurveComponentMatrixError):
            run_s1v_ledger_cell(
                "f3",
                1,
                "repeated-supports",
                "late-interval",
                0.025,
                0.05,
                4,
            )

    def test_adapter_has_no_classification_or_runtime_authority(self) -> None:
        result = run_s1v_ledger_cell(
            "f3",
            1,
            "repeated-supports",
            "early-cumulative",
            0.0,
            0.025,
            2,
        )

        self.assertFalse(result.classification_allowed)
        self.assertFalse(result.runtime_writeback_allowed)
        self.assertFalse(result.memory_claim_allowed)
        self.assertFalse(result.field_time_claim_allowed)
        self.assertTrue(
            {
                "classification",
                "decision",
                "label",
                "reward",
                "meaning",
                "observer_writeback",
                "target_topology",
            }.isdisjoint(s1v_four_curve_component_matrix_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
