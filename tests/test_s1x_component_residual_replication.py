from __future__ import annotations

import unittest

from mcm_field_organism.s1x_component_residual_replication import (
    evaluate_s1x_component_residual_replication,
    s1x_component_residual_replication_public_roles,
)


class S1XComponentResidualReplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = evaluate_s1x_component_residual_replication()

    def test_deterministic_selection_and_controls_hold(self) -> None:
        result = self.result

        self.assertGreater(result.selected_target_count, 0)
        self.assertEqual(result.selected_target_count, len(result.targets))
        self.assertEqual(len(result.targets), len(result.replications))
        self.assertTrue(result.deterministic_selection_holds)
        self.assertTrue(result.recomputation_control_holds)
        self.assertTrue(result.balance_controls_hold)
        self.assertTrue(result.observer_transparency_holds)
        self.assertTrue(result.repeatability_control_holds)
        self.assertTrue(result.finite_metrics_hold)
        self.assertTrue(result.all_controls_hold)

    def test_every_target_has_bound_convergence_and_countereffect_metrics(self) -> None:
        for replication in self.result.replications:
            with self.subTest(target=replication.target.target_id):
                self.assertGreater(
                    replication.target.s1w_relative_residual_r4,
                    0.05,
                )
                self.assertGreaterEqual(
                    replication.component_detection_floor_4_8,
                    1e-12,
                )
                self.assertLessEqual(replication.maximum_closure_linf, 1e-12)
                self.assertTrue(replication.all_ledgers_transparent)
                self.assertGreaterEqual(
                    replication.total_to_component_difference_ratio,
                    0.0,
                )

    def test_output_uses_only_preregistered_replication_roles(self) -> None:
        result = self.result

        self.assertEqual(
            "COMPONENT_REST_REPLICATED_AT_4_8",
            result.classification,
        )
        self.assertEqual(3, result.selected_target_count)
        self.assertEqual(3, result.replicated_target_count)
        self.assertAlmostEqual(
            0.05752400507649125,
            result.maximum_relative_residual_r8,
            places=15,
        )
        self.assertAlmostEqual(
            0.9639140886543844,
            result.maximum_total_to_component_difference_ratio,
            places=15,
        )
        self.assertEqual(
            {
                "s1v.d8.repeated.cumulative-0p200.activation-forcing",
                (
                    "s1v.d8.repeated.interval-0p200-0p400."
                    "activation-forcing"
                ),
                (
                    "s1v.d8.repeated.interval-0p400-0p800."
                    "activation-forcing"
                ),
            },
            {target.target_id for target in result.targets},
        )
        self.assertTrue(
            all(item.ordered_convergence for item in result.replications)
        )
        self.assertTrue(
            all(item.replicated_above_limit for item in result.replications)
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
            }.isdisjoint(s1x_component_residual_replication_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
