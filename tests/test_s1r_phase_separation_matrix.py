from __future__ import annotations

import unittest

from mcm_field_organism.s1r_phase_separation_matrix import (
    S1R_DELAY_SECONDS,
    S1R_DOSE_COUNTS,
    S1R_PHASE_BOUNDARY_SECONDS,
    S1R_SENTINEL_DELAYS,
    S1R_SOURCE_FORMS,
    build_s1r_cell_source_contract,
    run_s1r_matrix_cell,
    s1r_matrix_inventory,
    s1r_phase_separation_matrix_public_roles,
)
from mcm_field_organism.s1o_exposure_retention_matrix import run_s1o_matrix_cell


class S1RPhaseSeparationMatrixTests(unittest.TestCase):
    def test_inventory_is_the_exact_preregistered_cross_product(self) -> None:
        inventory = s1r_matrix_inventory()

        self.assertEqual(32, len(inventory))
        self.assertEqual(32, len({cell.cell_id for cell in inventory}))
        self.assertEqual(0.2, S1R_PHASE_BOUNDARY_SECONDS)
        self.assertEqual(
            {
                (dose, source_form, delay)
                for dose in S1R_DOSE_COUNTS
                for source_form in S1R_SOURCE_FORMS
                for delay in S1R_DELAY_SECONDS
            },
            {
                (cell.dose_count, cell.source_form, cell.delay_seconds)
                for cell in inventory
            },
        )

    def test_sources_match_marginals_and_bind_exact_delay_boundaries(self) -> None:
        for dose in S1R_DOSE_COUNTS:
            repeated = build_s1r_cell_source_contract(
                dose,
                "repeated-supports",
                0.0,
            )
            continuous = build_s1r_cell_source_contract(
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
        for delay in S1R_DELAY_SECONDS:
            source = build_s1r_cell_source_contract(
                1,
                "repeated-supports",
                delay,
            )
            with self.subTest(delay=delay):
                if delay == 0.0:
                    self.assertIsNone(source.delay)
                    continue
                self.assertIsNotNone(source.delay)
                first = source.delay[0].frames[0].field_time.window_start_tick
                last = source.delay[0].frames[-1].field_time.window_end_tick
                self.assertEqual(round(delay * 1_000_000_000), last - first)
                self.assertTrue(
                    all(
                        frame.field_time.window_end_tick
                        - frame.field_time.window_start_tick
                        <= 100_000_000
                        for frame in source.delay[0].frames
                    )
                )

    def test_active_cell_exposes_preprobe_mass_and_probe_effect_separately(self) -> None:
        result = run_s1r_matrix_cell(
            "f3",
            1,
            "repeated-supports",
            0.025,
            4,
        )

        zero = (0.0,) * 26
        self.assertEqual(zero, result.exposed_preprobe.activation)
        self.assertEqual(zero, result.exposed_preprobe.afterimage)
        self.assertEqual(zero, result.zero_preprobe.activation)
        self.assertEqual(zero, result.zero_preprobe.afterimage)
        self.assertEqual(26, len(result.preprobe_mass_vector))
        self.assertGreater(result.preprobe_mass_linf, 0.0)
        self.assertGreater(result.probe_effect_linf, 0.0)
        self.assertEqual(result.exposed_event_count, result.zero_event_count)
        for state in (
            result.exposed_preprobe,
            result.zero_preprobe,
            *result.exposed_probe,
            *result.zero_probe,
        ):
            self.assertGreaterEqual(min(state.mass), 0.0)
            self.assertAlmostEqual(1.0, sum(state.mass), places=12)

    def test_all_bound_sentinel_cells_are_exact_nulls(self) -> None:
        for dose in S1R_DOSE_COUNTS:
            for delay in S1R_SENTINEL_DELAYS:
                for model_id in ("eta-null", "p0"):
                    with self.subTest(model=model_id, dose=dose, delay=delay):
                        result = run_s1r_matrix_cell(
                            model_id,
                            dose,
                            "repeated-supports",
                            delay,
                            4,
                        )
                        self.assertEqual(0.0, result.probe_effect_linf)
                with self.subTest(model="m-neutral", dose=dose, delay=delay):
                    result = run_s1r_matrix_cell(
                        "f3",
                        dose,
                        "repeated-supports",
                        delay,
                        4,
                        m_neutralized=True,
                    )
                    self.assertEqual(0.0, result.preprobe_mass_linf)
                    self.assertEqual(0.0, result.probe_effect_linf)

    def test_existing_delay_cell_is_identical_to_s1o(self) -> None:
        previous = run_s1o_matrix_cell(
            "f3",
            1,
            "repeated-supports",
            0.2,
            4,
        )
        current = run_s1r_matrix_cell(
            "f3",
            1,
            "repeated-supports",
            0.2,
            4,
        )

        self.assertEqual(previous.exposed_preprobe, current.exposed_preprobe)
        self.assertEqual(previous.zero_preprobe, current.zero_preprobe)
        self.assertEqual(previous.exposed_probe, current.exposed_probe)
        self.assertEqual(previous.zero_probe, current.zero_probe)
        self.assertEqual(previous.effect_vector, current.probe_effect_vector)

    def test_long_boundary_cell_repeats_exactly(self) -> None:
        arguments = (
            "f3",
            8,
            "continuous-support",
            1.6,
            4,
        )

        self.assertEqual(
            run_s1r_matrix_cell(*arguments),
            run_s1r_matrix_cell(*arguments),
        )

    def test_contract_has_no_classification_or_runtime_authority(self) -> None:
        roles = set(s1r_phase_separation_matrix_public_roles())

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
        result = run_s1r_matrix_cell(
            "f3",
            1,
            "continuous-support",
            0.05,
            2,
        )
        self.assertFalse(result.raw_payload_retained)
        self.assertFalse(result.classification_allowed)
        self.assertFalse(result.runtime_writeback_allowed)
        self.assertFalse(result.memory_claim_allowed)
        self.assertFalse(result.field_time_claim_allowed)


if __name__ == "__main__":
    unittest.main()
