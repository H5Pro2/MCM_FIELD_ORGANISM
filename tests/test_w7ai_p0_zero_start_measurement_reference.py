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
    compose_w7ag_passive_cap_measurement_handoff,
)
from mcm_field_organism.w7ai_p0_zero_start_measurement_reference import (
    W7AIP0MeasurementReferenceError,
    compose_w7ai_p0_zero_start_measurement_references,
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


class W7AIP0ZeroStartMeasurementReferenceTests(unittest.TestCase):
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
        cls.cap_measurements = compose_w7ag_passive_cap_measurement_handoff(
            cls.adapter,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.cap_result,
        )
        cls.input_digests = (
            cls.p0_result.p0_seven_path_consumption_digest,
            cls.observer_result.observer_seven_path_consumption_digest,
            cls.cap_result.cap_seven_path_consumption_digest,
            cls.cap_measurements.measurement_handoff_digest,
        )
        cls.result = compose_w7ai_p0_zero_start_measurement_references(
            cls.adapter,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.p0_result,
            cls.observer_result,
            cls.cap_result,
            cls.cap_measurements,
        )

    def test_global_reference_and_digest_are_bound(self) -> None:
        self.assertEqual(
            "w7ai.p0-zero-start-measurement-reference.v1",
            self.result.reference_id,
        )
        self.assertEqual(
            "8b194514f4ac4074039891d6ba0e0db0ffdd9f28c157ce8a2bac66b238d771f5",
            self.result.p0_zero_start_measurement_reference_digest,
        )
        self.assertTrue(self.result.p0_absolute_comparison_ready)

    def test_all_35_path_checkpoint_roles_are_present(self) -> None:
        expected = tuple(
            (path_id, checkpoint)
            for path_id in ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
            for checkpoint in range(5)
        )
        self.assertEqual(
            expected,
            tuple((item.path_id, item.checkpoint) for item in self.result.references),
        )

    def test_every_role_has_fresh_equal_zero_start(self) -> None:
        for checkpoint in range(5):
            starts = tuple(
                item.initial_state
                for item in self.result.references
                if item.checkpoint == checkpoint
            )
            self.assertEqual(7, len(starts))
            self.assertEqual(1, len({item.s_values for item in starts}))
            self.assertEqual(1, len({item.h_values for item in starts}))
            self.assertEqual(7, len({id(item) for item in starts}))
            self.assertEqual(7, len({id(item.p0_field) for item in starts}))
            for start in starts:
                self.assertFalse(any(start.s_values))
                self.assertFalse(any(start.h_values))
                self.assertIsNone(start.p0_field.substrate)
                self.assertIsNone(start.p0_field.development)

    def test_samples_use_actual_strict_boundaries_and_terminal_tick(self) -> None:
        self.assertEqual(
            3185,
            sum(len(item.samples) for item in self.result.references),
        )
        for reference in self.result.references:
            ticks = tuple(item.tick for item in reference.samples)
            self.assertEqual(tuple(sorted(set(ticks))), ticks)
            self.assertEqual(reference.observed_production.interval[1], ticks[-1])
            self.assertEqual(
                ticks,
                reference.field_measurement.probe_observation_ticks,
            )

    def test_field_measurements_match_sample_norms(self) -> None:
        for reference in self.result.references:
            samples = reference.samples
            measurement = reference.field_measurement
            self.assertEqual("p0", measurement.model_id)
            self.assertEqual(
                max(abs(value) for sample in samples for value in sample.s_values),
                measurement.probe_S_linf,
            )
            self.assertEqual(
                max(abs(value) for sample in samples for value in sample.h_values),
                measurement.probe_H_linf,
            )
            self.assertEqual(
                math.sqrt(
                    math.fsum(
                        value * value
                        for sample in samples
                        for values in (sample.s_values, sample.h_values)
                        for value in values
                    )
                ),
                measurement.probe_SH_trajectory_l2,
            )

    def test_passive_and_modality_order_controls_match_w7r(self) -> None:
        for reference in self.result.references:
            observed = reference.observed_production
            self.assertEqual(
                observed.production_digest,
                reference.unobserved_production.production_digest,
            )
            self.assertEqual(
                observed.production_digest,
                reference.reversed_production.production_digest,
            )
            self.assertEqual(
                observed.end_state.state_digest,
                reference.unobserved_production.end_state.state_digest,
            )
            self.assertEqual(
                observed.end_state.state_digest,
                reference.reversed_production.end_state.state_digest,
            )

    def test_samples_reproduce_event_s_and_terminal_w7r_state(self) -> None:
        for reference in self.result.references:
            by_tick = {item.tick: item for item in reference.samples}
            for event in reference.observed_production.event_states:
                self.assertEqual(
                    event.s_values,
                    by_tick[event.completion_tick].s_values,
                )
            terminal = reference.samples[-1]
            self.assertEqual(
                reference.observed_production.end_state.s_values,
                terminal.s_values,
            )
            self.assertEqual(
                reference.observed_production.end_state.h_values,
                terminal.h_values,
            )

    def test_result_binds_inputs_without_mutating_them(self) -> None:
        self.assertEqual(self.input_digests[0], self.result.p0_consumption_digest)
        self.assertEqual(
            self.input_digests[1],
            self.result.observer_consumption_digest,
        )
        self.assertEqual(self.input_digests[2], self.result.cap_consumption_digest)
        self.assertEqual(
            self.input_digests[3],
            self.result.cap_measurement_handoff_digest,
        )
        self.assertEqual(
            self.input_digests,
            (
                self.p0_result.p0_seven_path_consumption_digest,
                self.observer_result.observer_seven_path_consumption_digest,
                self.cap_result.cap_seven_path_consumption_digest,
                self.cap_measurements.measurement_handoff_digest,
            ),
        )

    def test_reference_contains_no_capacity_or_substrate_role(self) -> None:
        for reference in self.result.references:
            self.assertEqual("p0", reference.field_measurement.model_id)
            self.assertIsNone(reference.initial_state.p0_field.substrate)
            self.assertIsNone(reference.initial_state.p0_field.development)

    def test_tampered_result_digest_is_rejected(self) -> None:
        with self.assertRaises(W7AIP0MeasurementReferenceError):
            replace(
                self.result,
                p0_zero_start_measurement_reference_digest="0" * 64,
            )


if __name__ == "__main__":
    unittest.main()
