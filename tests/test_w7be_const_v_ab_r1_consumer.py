from __future__ import annotations

from dataclasses import replace
import math
import unittest

from mcm_field_organism.w7bc_const_v_r124_trajectory_contract import (
    build_w7bc_const_v_r124_trajectory_contract,
)
from mcm_field_organism.w7bd_const_v_runtime_adapter import (
    build_w7bd_const_v_runtime_adapter,
)
from mcm_field_organism.w7be_const_v_ab_r1_consumer import (
    W7BEConstVABR1ConsumerError,
    consume_w7be_const_v_ab_r1,
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


class W7BEConstVABR1ConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = build_w7m_capacity_function_matrix_adapter()
        cls.contract = build_w7bc_const_v_r124_trajectory_contract()
        cls.runtime_adapter = build_w7bd_const_v_runtime_adapter(
            cls.matrix,
            cls.contract,
        )
        cls.family = build_w7w_symmetric_source_family(cls.matrix)
        cls.authorization = build_w7w_source_authorization(
            cls.matrix,
            cls.family,
        )
        cls.plan = build_w7y_seven_path_source_plan(
            cls.matrix,
            cls.family,
            cls.authorization,
        )
        cls.result = consume_w7be_const_v_ab_r1(
            cls.matrix,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.runtime_adapter,
        )

    def test_only_ab_r1_is_materialized(self) -> None:
        self.assertEqual("ab", self.result.path_id)
        self.assertEqual(1, self.result.refinement)
        self.assertEqual(5, len(self.result.main_productions))
        self.assertEqual(5, len(self.result.measurements))
        self.assertEqual(
            tuple(range(5)),
            tuple(item.checkpoint for item in self.result.measurements),
        )
        self.assertEqual(
            "88fd9722420a94f09c15fbce9e4e0b2a283a1a56422ed653e92ef2a7aeaf8708",
            self.result.result_digest,
        )

    def test_main_chain_is_contiguous_and_reaches_tick_eight(self) -> None:
        previous = self.result.initial_state
        self.assertEqual(0, previous.tick)
        for production in self.result.main_productions:
            self.assertIs(previous, production.initial_state)
            previous = production.end_state
        self.assertIs(previous, self.result.terminal_main_state)
        self.assertEqual(8_000_000, previous.tick)

    def test_checkpoint_probes_are_deep_aligned_and_isolated(self) -> None:
        for measurement in self.result.measurements:
            main = measurement.main_state
            aligned = measurement.aligned_probe_initial_state
            self.assertIsNot(main, aligned)
            self.assertIsNot(main.field, aligned.field)
            self.assertIsNot(main.field.layer, aligned.field.layer)
            self.assertIsNot(main.field.substrate, aligned.field.substrate)
            self.assertTrue(
                all(
                    neuron.activation == 0.0 and neuron.afterimage == 0.0
                    for neuron in aligned.field.layer.neurons
                )
            )
            self.assertEqual(
                main.field.substrate.masses,
                aligned.field.substrate.masses,
            )
            self.assertIs(
                aligned,
                measurement.probe_production.initial_state,
            )
            self.assertIsNot(
                main,
                measurement.probe_production.end_state,
            )

    def test_raw_samples_cover_s_h_and_the_technical_scalar(self) -> None:
        for measurement in self.result.measurements:
            self.assertGreater(len(measurement.samples), 0)
            self.assertEqual(
                measurement.probe_production.interval[1],
                measurement.samples[-1].tick,
            )
            for sample in measurement.samples:
                self.assertEqual(84, len(sample.s_values))
                self.assertEqual(84, len(sample.h_values))
                self.assertEqual(84, len(sample.technical_scalar_values))

    def test_const_v_invariants_hold_without_cap_capacity_semantics(self) -> None:
        states = [self.result.initial_state, self.result.terminal_main_state]
        for production in self.result.main_productions:
            states.extend((production.initial_state, production.end_state))
        for measurement in self.result.measurements:
            states.extend(
                (
                    measurement.main_state,
                    measurement.aligned_probe_initial_state,
                    measurement.probe_production.end_state,
                )
            )
        for state in states:
            substrate = state.field.substrate
            scalar = tuple(item.mass for item in substrate.masses)
            self.assertEqual("w7n.const-v", substrate.arm.arm_id)
            self.assertEqual(0.5, substrate.arm.lambda_sm_per_second)
            self.assertAlmostEqual(1.0, math.fsum(scalar), places=12)
            self.assertGreaterEqual(min(scalar), 0.0)

    def test_plan_and_inputs_remain_unchanged(self) -> None:
        self.assertEqual(
            "c771a3c28c04e04a61fa24d187416ef65b17597f9af759682deb576a28c25b32",
            self.plan.seven_path_plan_digest,
        )
        self.assertEqual("w7m.cap", self.matrix.initial_field.substrate.arm.arm_id)
        self.assertIsNone(self.matrix.initial_field.last_distribution)

    def test_tampered_result_is_rejected(self) -> None:
        with self.assertRaises(W7BEConstVABR1ConsumerError):
            replace(self.result, refinement=2)
        with self.assertRaises(W7BEConstVABR1ConsumerError):
            replace(
                self.result.measurements[0],
                checkpoint_measurement_digest="changed",
            )

    def test_consumer_is_not_publicly_exported(self) -> None:
        import mcm_field_organism
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(mcm_field_organism, "consume_w7be_const_v_ab_r1")
        )
        self.assertFalse(
            hasattr(current_api, "consume_w7be_const_v_ab_r1")
        )


if __name__ == "__main__":
    unittest.main()
