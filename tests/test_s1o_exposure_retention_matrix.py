from __future__ import annotations

import unittest

from mcm_field_organism.s1o_exposure_retention_matrix import (
    S1O_DELAY_SECONDS,
    S1O_DOSE_COUNTS,
    S1O_SOURCE_FORMS,
    build_s1o_cell_source_contract,
    run_s1o_matrix_cell,
    s1o_exposure_retention_matrix_public_roles,
    s1o_matrix_inventory,
)


class S1OExposureRetentionMatrixTests(unittest.TestCase):
    def test_matrix_inventory_is_the_exact_preregistered_cross_product(self) -> None:
        inventory = s1o_matrix_inventory()

        self.assertEqual(32, len(inventory))
        self.assertEqual(32, len({cell.cell_id for cell in inventory}))
        self.assertEqual(
            {
                (dose, source_form, delay)
                for dose in S1O_DOSE_COUNTS
                for source_form in S1O_SOURCE_FORMS
                for delay in S1O_DELAY_SECONDS
            },
            {
                (cell.dose_count, cell.source_form, cell.delay_seconds)
                for cell in inventory
            },
        )

    def test_repeated_and_continuous_sources_match_integrated_marginals(self) -> None:
        for dose in S1O_DOSE_COUNTS:
            repeated = build_s1o_cell_source_contract(
                dose,
                "repeated-supports",
                0.0,
            )
            continuous = build_s1o_cell_source_contract(
                dose,
                "continuous-support",
                0.0,
            )
            with self.subTest(dose=dose):
                self.assertEqual(
                    repeated.exposure_invariants.duration_seconds,
                    continuous.exposure_invariants.duration_seconds,
                )
                self.assertEqual(
                    repeated.exposure_invariants.integrated_l1,
                    continuous.exposure_invariants.integrated_l1,
                )
                self.assertEqual(
                    repeated.exposure_invariants.integrated_l2,
                    continuous.exposure_invariants.integrated_l2,
                )
                self.assertEqual(2 * dose, repeated.exposure_invariants.event_count)
                self.assertEqual(2, continuous.exposure_invariants.event_count)
                self.assertNotEqual(
                    repeated.exposure_digest,
                    repeated.exposure_zero_digest,
                )

    def test_one_active_cell_preserves_alignment_mass_and_measurement(self) -> None:
        result = run_s1o_matrix_cell(
            "f3",
            2,
            "repeated-supports",
            0.0,
            4,
        )

        zero = (0.0,) * 26
        self.assertEqual(zero, result.exposed_preprobe.activation)
        self.assertEqual(zero, result.exposed_preprobe.afterimage)
        self.assertEqual(zero, result.zero_preprobe.activation)
        self.assertEqual(zero, result.zero_preprobe.afterimage)
        for state in (
            result.exposed_preprobe,
            result.zero_preprobe,
            *result.exposed_probe,
            *result.zero_probe,
        ):
            self.assertGreaterEqual(min(state.mass), 0.0)
            self.assertAlmostEqual(1.0, sum(state.mass), places=12)
        self.assertGreater(result.preprobe_mass_linf, 0.0)
        self.assertGreater(result.effect_linf, 0.0)
        self.assertEqual(result.exposed_event_count, result.zero_event_count)

    def test_preregistered_sentinel_cells_are_exact_nulls(self) -> None:
        sentinel_cells = (
            (1, "repeated-supports", 0.0),
            (8, "repeated-supports", 1.6),
            (8, "continuous-support", 0.0),
        )
        for model_id in ("eta-null", "p0"):
            for cell in sentinel_cells:
                with self.subTest(model=model_id, cell=cell):
                    result = run_s1o_matrix_cell(model_id, *cell, 4)
                    self.assertEqual(0.0, result.effect_linf)
        for delay in (0.0, 1.6):
            with self.subTest(model="m-neutral", delay=delay):
                result = run_s1o_matrix_cell(
                    "f3",
                    8,
                    "repeated-supports",
                    delay,
                    4,
                    m_neutralized=True,
                )
                self.assertEqual(0.0, result.preprobe_mass_linf)
                self.assertEqual(0.0, result.effect_linf)

    def test_public_contract_has_no_classification_or_runtime_authority(self) -> None:
        roles = set(s1o_exposure_retention_matrix_public_roles())

        self.assertTrue(
            {
                "classification",
                "decision",
                "label",
                "reward",
                "meaning",
                "observer_writeback",
                "target_topology",
            }.isdisjoint(roles)
        )
        result = run_s1o_matrix_cell(
            "f3",
            1,
            "continuous-support",
            0.0,
            2,
        )
        self.assertFalse(result.raw_payload_retained)
        self.assertFalse(result.classification_allowed)
        self.assertFalse(result.runtime_writeback_allowed)
        self.assertFalse(result.memory_claim_allowed)
        self.assertFalse(result.learning_claim_allowed)


if __name__ == "__main__":
    unittest.main()
