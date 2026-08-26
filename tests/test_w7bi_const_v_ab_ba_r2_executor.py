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
    execute_w7bg_const_v_ab_repeat_then_ba_r1,
)
from mcm_field_organism.w7bh_const_v_r2_repeat_contract import (
    build_w7bh_const_v_r2_repeat_contract,
)
from mcm_field_organism.w7bi_const_v_ab_ba_r2_executor import (
    W7BIConstVABBAR2ExecutorError,
    execute_w7bi_const_v_ab_ba_r2,
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


class W7BIConstVABBAR2ExecutorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = build_w7m_capacity_function_matrix_adapter()
        cls.runtime_adapter = build_w7bd_const_v_runtime_adapter(
            cls.matrix,
            build_w7bc_const_v_r124_trajectory_contract(),
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
        cls.bg_result = execute_w7bg_const_v_ab_repeat_then_ba_r1(
            cls.matrix,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.runtime_adapter,
            build_w7bf_const_v_ba_r1_repeat_contract(),
        )
        cls.contract = build_w7bh_const_v_r2_repeat_contract()
        cls.result = execute_w7bi_const_v_ab_ba_r2(
            cls.matrix,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.runtime_adapter,
            cls.contract,
            cls.bg_result,
        )

    def test_both_roles_are_present_at_r2(self) -> None:
        self.assertEqual(("ab", "ba"), tuple(item.path_id for item in self.result.roles))
        self.assertEqual(
            ("ab-r2-exact-repeat", "ba-r2-primary"),
            self.result.execution_order,
        )
        self.assertEqual("RAW_D12_PREPARED", self.result.outcome)
        self.assertEqual(
            "b4daf8e5621369d4daa8e504910a4f84bb4fcc59c0722f769dbb20924cfcbf77",
            self.result.result_digest,
        )
        self.assertEqual(
            (
                "666bfd0424cdd50aa3380e50ad1b29b223eee0554141863518ceca1c8bd8910a",
                "2d0983995be11c5b36d07cb60a0b07e4c0e5a436ae65c89797b27108a6b1a03d",
            ),
            tuple(item.raw_d12_digest for item in self.result.roles),
        )

    def test_r1_digests_are_bound_and_r2_has_five_by_five_structure(self) -> None:
        self.assertEqual(
            self.bg_result.ab_repeat.result_digest,
            self.result.roles[0].r1_role_digest,
        )
        for role in self.result.roles:
            self.assertEqual(5, len(role.r2_productions))
            self.assertEqual(5, len(role.r2_measurements))
            self.assertEqual(2, role.r2_initial_state.refinement)
            self.assertTrue(all(len(item.samples) == 91 for item in role.r2_measurements))

    def test_r2_const_v_invariants_hold(self) -> None:
        for role in self.result.roles:
            states = [role.r2_initial_state, role.r2_terminal_state]
            for production in role.r2_productions:
                states.extend((production.initial_state, production.end_state))
            for state in states:
                substrate = state.field.substrate
                self.assertEqual("w7n.const-v", substrate.arm.arm_id)
                self.assertAlmostEqual(
                    1.0,
                    math.fsum(item.mass for item in substrate.masses),
                    places=12,
                )

    def test_d12_is_raw_only(self) -> None:
        self.assertTrue(self.contract.raw_d12_preparation_allowed)
        self.assertIsNone(self.result.distance_values)
        self.assertFalse(self.result.epsilon_ready)
        self.assertFalse(self.result.effect_floor_ready)
        self.assertFalse(self.result.profile_ready)

    def test_tampering_is_rejected(self) -> None:
        with self.assertRaises(W7BIConstVABBAR2ExecutorError):
            replace(self.result, profile_ready=True)
        with self.assertRaises(W7BIConstVABBAR2ExecutorError):
            replace(self.result, distance_values=0.0)

    def test_executor_is_not_publicly_exported(self) -> None:
        import mcm_field_organism
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(mcm_field_organism, "execute_w7bi_const_v_ab_ba_r2"))
        self.assertFalse(hasattr(current_api, "execute_w7bi_const_v_ab_ba_r2"))


if __name__ == "__main__":
    unittest.main()
