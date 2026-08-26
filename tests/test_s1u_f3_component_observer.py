from __future__ import annotations

import math
import unittest

from mcm_field_organism.s1u_f3_component_observer import (
    run_s1u_component_cell,
    s1u_component_observer_public_roles,
)


class S1UF3ComponentObserverTests(unittest.TestCase):
    def test_active_cell_closes_component_ledger_and_is_transparent(self) -> None:
        result = run_s1u_component_cell(
            "f3",
            8,
            "repeated-supports",
            0.2,
            4,
        )

        self.assertTrue(result.observer_transparent)
        self.assertEqual(result.observed_end_digest, result.reference_end_digest)
        self.assertEqual(96, result.stage_count)
        self.assertAlmostEqual(0.2, result.integrated_weight_seconds, places=14)
        self.assertLessEqual(result.closure_linf, 1e-12)
        self.assertLessEqual(abs(result.transport_sum), 1e-12)
        self.assertLessEqual(abs(result.activation_forcing_sum), 1e-12)
        self.assertLessEqual(abs(result.total_rate_sum), 1e-12)
        self.assertLessEqual(abs(result.delta_mass_sum), 1e-12)
        self.assertGreater(
            max(abs(value) for value in result.delta_activation_forcing),
            0.0,
        )
        self.assertAlmostEqual(
            0.0028248369534719484,
            max(abs(value) for value in result.delta_transport),
            places=15,
        )
        self.assertAlmostEqual(
            0.0028452129424663976,
            max(abs(value) for value in result.delta_activation_forcing),
            places=15,
        )
        self.assertAlmostEqual(
            0.0006167263531163397,
            max(abs(value) for value in result.delta_mass),
            places=15,
        )
        self.assertEqual(
            "organism.mcm_field.auditory.n0",
            result.argmax_start_neuron_id,
        )
        self.assertEqual(
            "organism.mcm_field.auditory.n0",
            result.argmax_end_neuron_id,
        )

    def test_p0_and_uniform_active_null_are_exact_component_nulls(self) -> None:
        p0 = run_s1u_component_cell(
            "p0",
            1,
            "repeated-supports",
            0.2,
            4,
        )
        uniform = run_s1u_component_cell(
            "f3",
            1,
            "repeated-supports",
            0.2,
            4,
            source_role="uniform-null",
        )

        for result in (p0, uniform):
            with self.subTest(model=result.model_id, source=result.source_role):
                self.assertTrue(result.observer_transparent)
                self.assertEqual((0.0,) * 26, result.delta_transport)
                self.assertEqual((0.0,) * 26, result.delta_activation_forcing)
                self.assertEqual((0.0,) * 26, result.delta_total_rate)
                self.assertEqual((0.0,) * 26, result.delta_mass)
                self.assertEqual(0.0, result.closure_linf)

    def test_refinement_two_four_component_difference_is_finite(self) -> None:
        coarse = run_s1u_component_cell(
            "f3",
            8,
            "repeated-supports",
            0.2,
            2,
        )
        fine = run_s1u_component_cell(
            "f3",
            8,
            "repeated-supports",
            0.2,
            4,
        )

        for role in ("delta_transport", "delta_activation_forcing"):
            difference = max(
                abs(left - right)
                for left, right in zip(
                    getattr(coarse, role),
                    getattr(fine, role),
                    strict=True,
                )
            )
            with self.subTest(role=role):
                self.assertTrue(math.isfinite(difference))
                self.assertGreaterEqual(difference, 0.0)
                self.assertGreaterEqual(max(1e-12, 8.0 * difference), 1e-12)

    def test_public_contract_has_no_state_or_claim_authority(self) -> None:
        result = run_s1u_component_cell(
            "f3",
            1,
            "continuous-support",
            0.025,
            2,
        )

        self.assertFalse(result.raw_payload_retained)
        self.assertFalse(result.classification_allowed)
        self.assertFalse(result.runtime_writeback_allowed)
        self.assertFalse(result.memory_claim_allowed)
        self.assertFalse(result.field_time_claim_allowed)
        self.assertTrue(
            {
                "world_payload",
                "label",
                "reward",
                "meaning",
                "observer_writeback",
                "target_topology",
            }.isdisjoint(s1u_component_observer_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
