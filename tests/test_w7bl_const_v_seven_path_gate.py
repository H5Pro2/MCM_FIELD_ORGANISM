from __future__ import annotations

import unittest

from mcm_field_organism.w7bc_const_v_r124_trajectory_contract import (
    build_w7bc_const_v_r124_trajectory_contract,
)
from mcm_field_organism.w7bd_const_v_runtime_adapter import (
    build_w7bd_const_v_runtime_adapter,
)
from mcm_field_organism.w7bj_const_v_r4_convergence_contract import (
    build_w7bj_const_v_r4_convergence_contract,
)
from mcm_field_organism.w7bl_const_v_seven_path_gate import (
    W7BLConstVSevenPathGateError,
    build_w7bl_const_v_seven_path_gate,
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


class W7BLConstVSevenPathGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        matrix = build_w7m_capacity_function_matrix_adapter()
        family = build_w7w_symmetric_source_family(matrix)
        authorization = build_w7w_source_authorization(matrix, family)
        cls.plan = build_w7y_seven_path_source_plan(matrix, family, authorization)
        cls.contract = build_w7bj_const_v_r4_convergence_contract()
        cls.gate = build_w7bl_const_v_seven_path_gate(cls.plan, cls.contract)

    def test_gate_binds_seven_paths_and_seventy_components(self) -> None:
        self.assertEqual(
            ("ab", "ag", "ba", "bg", "ua", "ub", "ug"),
            self.gate.required_path_ids,
        )
        self.assertEqual((1, 2, 4), self.gate.required_resolutions)
        self.assertEqual(35, self.gate.required_role_count)
        self.assertEqual(70, self.gate.required_component_count)
        self.assertFalse(self.gate.numeric_evaluation_allowed)
        self.assertFalse(self.gate.convergence_decision_allowed)

    def test_gate_rejects_incomplete_plan(self) -> None:
        with self.assertRaises(W7BLConstVSevenPathGateError):
            build_w7bl_const_v_seven_path_gate(
                object(),
                self.contract,
            )

    def test_gate_is_not_publicly_exported(self) -> None:
        import mcm_field_organism
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(mcm_field_organism, "build_w7bl_const_v_seven_path_gate"))
        self.assertFalse(hasattr(current_api, "build_w7bl_const_v_seven_path_gate"))


if __name__ == "__main__":
    unittest.main()
