from __future__ import annotations

from dataclasses import replace
import math
import unittest

from mcm_field_organism.w7aa_p0_seven_path_consumer import (
    consume_w7aa_p0_seven_path_plan,
)
from mcm_field_organism.w7ac_observer_seven_path_consumer import (
    consume_w7ac_observer_seven_path_result,
)
from mcm_field_organism.w7ae_cap_seven_path_consumer import (
    consume_w7ae_cap_seven_path_plan,
)
from mcm_field_organism.w7ag_passive_cap_measurement_handoff import (
    W7AGPassiveCAPMeasurementError,
    compose_w7ag_passive_cap_measurement_handoff,
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


class W7AGPassiveCAPMeasurementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = build_w7m_capacity_function_matrix_adapter()
        cls.family = build_w7w_symmetric_source_family(cls.adapter)
        cls.authorization = build_w7w_source_authorization(
            cls.adapter,
            cls.family,
        )
        cls.plan = build_w7y_seven_path_source_plan(
            cls.adapter,
            cls.family,
            cls.authorization,
        )
        cls.p0_result = consume_w7aa_p0_seven_path_plan(
            cls.adapter,
            cls.family,
            cls.authorization,
            cls.plan,
        )
        cls.observer_result = consume_w7ac_observer_seven_path_result(
            cls.adapter,
            cls.authorization,
            cls.plan,
            cls.p0_result,
        )
        cls.cap_result = consume_w7ae_cap_seven_path_plan(
            cls.adapter,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.p0_result,
            cls.observer_result,
        )
        cls.cap_digest = cls.cap_result.cap_seven_path_consumption_digest
        cls.result = compose_w7ag_passive_cap_measurement_handoff(
            cls.adapter,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.cap_result,
        )

    def test_global_handoff_and_digest_are_bound(self) -> None:
        self.assertEqual(
            "w7ag.passive-cap-measurement-handoff.v1",
            self.result.handoff_id,
        )
        self.assertEqual(
            "898e94bdbc2b5b0f893c5c512a684fd15544845d25de1a97febc83ffc8bcccd8",
            self.result.measurement_handoff_digest,
        )
        self.assertEqual(self.cap_digest, self.result.cap_consumption_digest)

    def test_all_35_path_checkpoint_roles_are_present(self) -> None:
        expected = tuple(
            (path_id, checkpoint)
            for path_id in ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
            for checkpoint in range(5)
        )
        self.assertEqual(
            expected,
            tuple((item.path_id, item.checkpoint) for item in self.result.measurements),
        )

    def test_measurement_starts_have_zero_fast_state_and_unchanged_mass(self) -> None:
        for measurement in self.result.measurements:
            aligned = measurement.aligned_state
            self.assertTrue(
                all(
                    item.activation == 0.0 and item.afterimage == 0.0
                    for item in aligned.field.layer.neurons
                )
            )
            self.assertEqual(
                tuple(item.mass for item in measurement.main_state.field.substrate.masses),
                tuple(item.mass for item in aligned.field.substrate.masses),
            )
            if measurement.path_id.startswith("u") and measurement.checkpoint == 0:
                self.assertIsNone(aligned.continuation_binding)
                self.assertIsNone(aligned.field.last_distribution)
            else:
                self.assertIsNotNone(aligned.continuation_binding)

    def test_main_technical_probe_and_measurement_are_three_branches(self) -> None:
        by_role = {
            (path.path_id, checkpoint.checkpoint): checkpoint
            for path in self.cap_result.path_results
            for checkpoint in path.checkpoints
        }
        for measurement in self.result.measurements:
            checkpoint = by_role[(measurement.path_id, measurement.checkpoint)]
            self.assertIs(measurement.main_state, checkpoint.main_state)
            self.assertIsNot(measurement.aligned_state, checkpoint.main_state)
            self.assertIsNot(measurement.aligned_state, checkpoint.probe_initial_state)
            self.assertIsNot(measurement.aligned_state.field, checkpoint.main_state.field)
            self.assertIsNot(
                measurement.aligned_state.field,
                checkpoint.probe_initial_state.field,
            )

    def test_samples_use_actual_strict_boundaries_and_terminal_tick(self) -> None:
        self.assertEqual(
            3185,
            sum(len(item.samples) for item in self.result.measurements),
        )
        for measurement in self.result.measurements:
            ticks = tuple(item.tick for item in measurement.samples)
            self.assertEqual(tuple(sorted(set(ticks))), ticks)
            self.assertEqual(
                measurement.measurement_production.interval[1],
                ticks[-1],
            )
            self.assertEqual(
                ticks,
                measurement.field_measurement.probe_observation_ticks,
            )

    def test_field_measurements_match_sample_norms(self) -> None:
        for measurement in self.result.measurements:
            samples = measurement.samples
            expected_s = max(
                abs(value) for sample in samples for value in sample.s_values
            )
            expected_h = max(
                abs(value) for sample in samples for value in sample.h_values
            )
            expected_l2 = math.sqrt(
                math.fsum(
                    value * value
                    for sample in samples
                    for values in (sample.s_values, sample.h_values)
                    for value in values
                )
            )
            self.assertEqual("cap", measurement.field_measurement.model_id)
            self.assertEqual(expected_s, measurement.field_measurement.probe_S_linf)
            self.assertEqual(expected_h, measurement.field_measurement.probe_H_linf)
            self.assertEqual(
                expected_l2,
                measurement.field_measurement.probe_SH_trajectory_l2,
            )

    def test_capacity_and_regional_ledgers_close_without_feedback(self) -> None:
        for measurement in self.result.measurements:
            capacity = measurement.capacity_measurement
            ledger = measurement.regional_ledger
            self.assertEqual("cap", capacity.model_id)
            self.assertAlmostEqual(1.0, capacity.total_mass, places=12)
            self.assertAlmostEqual(1.0, capacity.total_free_capacity, places=12)
            self.assertLessEqual(capacity.balance_residual, 1e-12)
            self.assertAlmostEqual(capacity.total_mass, ledger.total_mass, places=12)
            self.assertAlmostEqual(
                capacity.total_free_capacity,
                ledger.total_free_capacity,
                places=12,
            )

    def test_order_passivity_and_p0_gate_are_explicit(self) -> None:
        self.assertTrue(self.result.order_countercontrol_digest)
        self.assertTrue(self.result.observer_passivity_digest)
        self.assertFalse(self.result.p0_absolute_comparison_ready)
        self.assertEqual(
            self.cap_digest,
            self.cap_result.cap_seven_path_consumption_digest,
        )

    def test_tampered_measurement_and_handoff_digests_are_rejected(self) -> None:
        with self.assertRaisesRegex(
            W7AGPassiveCAPMeasurementError,
            "measurement result digest",
        ):
            replace(
                self.result.measurements[0],
                measurement_result_digest="changed",
            )
        with self.assertRaisesRegex(
            W7AGPassiveCAPMeasurementError,
            "handoff digest",
        ):
            replace(self.result, measurement_handoff_digest="changed")

    def test_module_is_not_reexported(self) -> None:
        import mcm_field_organism
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(
                mcm_field_organism,
                "compose_w7ag_passive_cap_measurement_handoff",
            )
        )
        self.assertFalse(
            hasattr(
                current_api,
                "compose_w7ag_passive_cap_measurement_handoff",
            )
        )


if __name__ == "__main__":
    unittest.main()
