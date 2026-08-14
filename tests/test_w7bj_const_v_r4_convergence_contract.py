from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.w7bj_const_v_r4_convergence_contract import (
    W7BJConstVR4ConvergenceContractError,
    build_w7bj_const_v_r4_convergence_contract,
)


class W7BJConstVR4ConvergenceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_w7bj_const_v_r4_convergence_contract()

    def test_contract_binds_w7bh_w7bi_and_r4(self) -> None:
        self.assertEqual(
            "b191a837d4a00c604dba6598c038df92c76a2e5ab9e3be5f30e288f6118c3583",
            self.contract.required_w7bh_contract_digest,
        )
        self.assertEqual(
            "b4daf8e5621369d4daa8e504910a4f84bb4fcc59c0722f769dbb20924cfcbf77",
            self.contract.required_w7bi_result_digest,
        )
        self.assertEqual(4, self.contract.refinement)
        self.assertEqual(
            "140370ef40a2f4410edfa89ef96e90457614b4e6f337369f71cc1b02f62a3b74",
            self.contract.contract_digest,
        )

    def test_r4_repeat_precedes_ba_r4(self) -> None:
        self.assertEqual(
            ("ab-r4-exact-repeat", "ba-r4-primary"),
            self.contract.execution_roles,
        )
        self.assertEqual("stop-before-ba-r4", self.contract.repeat_failure_rule)
        self.assertEqual(
            "all-r2-canonical-surfaces-must-be-exactly-equal-with-r4",
            self.contract.repeat_rule,
        )

    def test_convergence_is_allowed_only_after_r4(self) -> None:
        self.assertTrue(self.contract.r124_convergence_evaluation_allowed_after_r4)
        self.assertEqual(("s", "h"), self.contract.convergence_components)
        self.assertEqual(35, self.contract.convergence_roles)
        self.assertEqual(70, self.contract.convergence_comparison_count)
        self.assertEqual(
            "d24-less-than-d12-or-both-exact-zero-per-role-and-component",
            self.contract.convergence_rule,
        )
        self.assertEqual(
            "maximum-of-all-70-r2-r4-s-h-linf-distances",
            self.contract.epsilon_rule,
        )

    def test_effect_floor_and_pre_r4_distance_are_locked(self) -> None:
        self.assertEqual(
            "ten-times-epsilon-after-convergence-only",
            self.contract.effect_floor_rule,
        )
        self.assertFalse(self.contract.distance_evaluation_allowed_before_r4)
        self.assertFalse(self.contract.accept_result_values)
        self.assertFalse(self.contract.execution_allowed)
        self.assertFalse(self.contract.field_function_decision_allowed)
        self.assertFalse(self.contract.memory_claim_allowed)

    def test_structure_and_tampering_are_frozen(self) -> None:
        self.assertEqual(5, self.contract.main_production_count_per_role)
        self.assertEqual(5, self.contract.checkpoint_count_per_role)
        self.assertEqual(91, self.contract.expected_sample_count_per_checkpoint)
        self.assertFalse(self.contract.probe_returns_to_main)
        self.assertEqual(
            0,
            len(inspect.signature(build_w7bj_const_v_r4_convergence_contract).parameters),
        )
        with self.assertRaises(W7BJConstVR4ConvergenceContractError):
            replace(self.contract, convergence_comparison_count=69)

    def test_contract_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "build_w7bj_const_v_r4_convergence_contract")
        )


if __name__ == "__main__":
    unittest.main()
