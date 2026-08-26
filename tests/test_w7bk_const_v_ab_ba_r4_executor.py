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
    execute_w7bi_const_v_ab_ba_r2,
)
from mcm_field_organism.w7bj_const_v_r4_convergence_contract import (
    build_w7bj_const_v_r4_convergence_contract,
)
from mcm_field_organism.w7bk_const_v_ab_ba_r4_executor import (
    W7BKConstVABBAR4ExecutorError,
    execute_w7bk_const_v_ab_ba_r4,
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


class W7BKConstVABBAR4ExecutorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = build_w7m_capacity_function_matrix_adapter()
        cls.adapter = build_w7bd_const_v_runtime_adapter(
            cls.matrix,
            build_w7bc_const_v_r124_trajectory_contract(),
        )
        cls.family = build_w7w_symmetric_source_family(cls.matrix)
        cls.authorization = build_w7w_source_authorization(cls.matrix, cls.family)
        cls.plan = build_w7y_seven_path_source_plan(
            cls.matrix,
            cls.family,
            cls.authorization,
        )
        r1 = execute_w7bg_const_v_ab_repeat_then_ba_r1(
            cls.matrix,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.adapter,
            build_w7bf_const_v_ba_r1_repeat_contract(),
        )
        cls.bi = execute_w7bi_const_v_ab_ba_r2(
            cls.matrix,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.adapter,
            build_w7bh_const_v_r2_repeat_contract(),
            r1,
        )
        cls.result = execute_w7bk_const_v_ab_ba_r4(
            cls.matrix,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.adapter,
            build_w7bj_const_v_r4_convergence_contract(),
            cls.bi,
        )

    def test_both_r4_roles_are_complete(self) -> None:
        self.assertEqual(("ab", "ba"), tuple(item.path_id for item in self.result.roles))
        self.assertEqual(
            ("ab-r4-exact-repeat", "ba-r4-primary"),
            self.result.execution_order,
        )
        self.assertEqual("R4_TECHNICAL_ROLES_COMPLETE", self.result.outcome)
        self.assertEqual(
            "9215994d927fe801c71ea3436b09d1091c6d015c2c38e125ebf8fd0e8209d551",
            self.result.result_digest,
        )
        self.assertEqual(
            (
                "09cc1f208e32a2ac979ea13a15541b7078ffda20ad35e66f6978ae3661aa8e9e",
                "7496f414784d524990dc6af1163c9673d985c730248e4363e86f96df8109faa9",
            ),
            tuple(item.r4_role_digest for item in self.result.roles),
        )

    def test_each_r4_role_has_the_bound_structure(self) -> None:
        for role in self.result.roles:
            self.assertEqual(4, role.r4_initial_state.refinement)
            self.assertEqual(4, role.r4_terminal_state.refinement)
            self.assertEqual(5, len(role.r4_productions))
            self.assertEqual(5, len(role.r4_measurements))
            self.assertTrue(all(len(item.samples) == 91 for item in role.r4_measurements))

    def test_const_v_mass_invariant_holds(self) -> None:
        for role in self.result.roles:
            states = [role.r4_initial_state, role.r4_terminal_state]
            for production in role.r4_productions:
                states.extend((production.initial_state, production.end_state))
            for state in states:
                substrate = state.field.substrate
                self.assertEqual("w7n.const-v", substrate.arm.arm_id)
                self.assertAlmostEqual(
                    1.0,
                    math.fsum(item.mass for item in substrate.masses),
                    places=12,
                )

    def test_convergence_is_still_separate(self) -> None:
        self.assertFalse(self.result.convergence_evaluated)
        self.assertFalse(self.result.epsilon_ready)
        self.assertFalse(self.result.effect_floor_ready)

    def test_tampering_is_rejected(self) -> None:
        with self.assertRaises(W7BKConstVABBAR4ExecutorError):
            replace(self.result, convergence_evaluated=True)

    def test_executor_is_not_publicly_exported(self) -> None:
        import mcm_field_organism
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(mcm_field_organism, "execute_w7bk_const_v_ab_ba_r4"))
        self.assertFalse(hasattr(current_api, "execute_w7bk_const_v_ab_ba_r4"))


if __name__ == "__main__":
    unittest.main()
