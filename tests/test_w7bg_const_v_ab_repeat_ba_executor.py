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
from mcm_field_organism.w7bf_const_v_ba_r1_repeat_contract import (
    build_w7bf_const_v_ba_r1_repeat_contract,
)
from mcm_field_organism.w7bg_const_v_ab_repeat_ba_executor import (
    W7BGConstVABRepeatBAExecutorError,
    execute_w7bg_const_v_ab_repeat_then_ba_r1,
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


class W7BGConstVABRepeatBAExecutorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = build_w7m_capacity_function_matrix_adapter()
        trajectory_contract = build_w7bc_const_v_r124_trajectory_contract()
        cls.runtime_adapter = build_w7bd_const_v_runtime_adapter(
            cls.matrix,
            trajectory_contract,
        )
        cls.contract = build_w7bf_const_v_ba_r1_repeat_contract()
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
        cls.result = execute_w7bg_const_v_ab_repeat_then_ba_r1(
            cls.matrix,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.runtime_adapter,
            cls.contract,
        )

    def test_ab_repeat_is_exact_and_precedes_ba(self) -> None:
        self.assertTrue(self.result.repeat_passed)
        self.assertEqual(
            ("ab-r1-exact-repeat", "ba-r1-primary"),
            self.result.execution_order,
        )
        self.assertEqual(
            self.contract.required_w7be_result_digest,
            self.result.ab_repeat.result_digest,
        )
        self.assertEqual(
            "3d2abeda7658443639b327f33d79c304ffc1a6bdc8fa56016d7e42040c841927",
            self.result.result_digest,
        )

    def test_ba_chain_is_complete_and_uses_five_measurements(self) -> None:
        self.assertEqual("ba", self.result.ba_initial_state.path_id)
        self.assertEqual(5, len(self.result.ba_productions))
        self.assertEqual(5, len(self.result.ba_measurements))
        self.assertEqual(8_000_000, self.result.ba_terminal_state.tick)
        self.assertTrue(
            all(len(item.samples) == 91 for item in self.result.ba_measurements)
        )

    def test_ba_probes_are_aligned_and_do_not_return_to_main(self) -> None:
        for measurement in self.result.ba_measurements:
            main = measurement.main_state
            aligned = measurement.aligned_probe_initial_state
            self.assertIsNot(main.field, aligned.field)
            self.assertEqual(main.field.substrate.masses, aligned.field.substrate.masses)
            self.assertTrue(
                all(
                    neuron.activation == 0.0 and neuron.afterimage == 0.0
                    for neuron in aligned.field.layer.neurons
                )
            )
            self.assertIsNot(
                measurement.probe_production.end_state,
                main,
            )

    def test_const_v_mass_and_arm_invariants_hold_for_ba(self) -> None:
        states = [self.result.ba_initial_state, self.result.ba_terminal_state]
        for production in self.result.ba_productions:
            states.extend((production.initial_state, production.end_state))
        for state in states:
            substrate = state.field.substrate
            self.assertEqual("w7n.const-v", substrate.arm.arm_id)
            self.assertEqual(0.5, substrate.arm.lambda_sm_per_second)
            self.assertAlmostEqual(
                1.0,
                math.fsum(item.mass for item in substrate.masses),
                places=12,
            )

    def test_result_has_no_distance_or_function_decision(self) -> None:
        self.assertEqual("TECHNICAL_TWO_ROLE_COMPLETE", self.result.outcome)
        self.assertFalse(self.result.distance_evaluated)
        self.assertFalse(self.result.epsilon_ready)
        self.assertFalse(self.result.field_function_decision_ready)

    def test_tampering_is_rejected(self) -> None:
        with self.assertRaises(W7BGConstVABRepeatBAExecutorError):
            replace(self.result, repeat_passed=False)
        with self.assertRaises(W7BGConstVABRepeatBAExecutorError):
            replace(self.result, distance_evaluated=True)

    def test_executor_is_not_publicly_exported(self) -> None:
        import mcm_field_organism
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(
                mcm_field_organism,
                "execute_w7bg_const_v_ab_repeat_then_ba_r1",
            )
        )
        self.assertFalse(
            hasattr(
                current_api,
                "execute_w7bg_const_v_ab_repeat_then_ba_r1",
            )
        )


if __name__ == "__main__":
    unittest.main()
