from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.w7bh_const_v_r2_repeat_contract import (
    W7BHConstVR2RepeatContractError,
    build_w7bh_const_v_r2_repeat_contract,
)


class W7BHConstVR2RepeatContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_w7bh_const_v_r2_repeat_contract()

    def test_contract_binds_w7bf_w7bg_and_runtime(self) -> None:
        self.assertEqual(
            "e7d819ad3eb236360ffda717e0abb8b250a4489b390179d893e755f3a0dc40d0",
            self.contract.required_w7bf_contract_digest,
        )
        self.assertEqual(
            "3d2abeda7658443639b327f33d79c304ffc1a6bdc8fa56016d7e42040c841927",
            self.contract.required_w7bg_result_digest,
        )
        self.assertEqual(2, self.contract.refinement)
        self.assertEqual(
            "b191a837d4a00c604dba6598c038df92c76a2e5ab9e3be5f30e288f6118c3583",
            self.contract.contract_digest,
        )

    def test_r2_repeat_precedes_ba_r2(self) -> None:
        self.assertEqual(
            ("ab-r2-exact-repeat", "ba-r2-primary"),
            self.contract.execution_roles,
        )
        self.assertEqual(
            "all-r1-canonical-surfaces-must-be-exactly-equal-with-r2",
            self.contract.repeat_rule,
        )
        self.assertEqual("stop-before-ba-r2", self.contract.repeat_failure_rule)

    def test_raw_d12_is_preparable_but_not_evaluable(self) -> None:
        self.assertTrue(self.contract.raw_d12_preparation_allowed)
        self.assertEqual(
            "same-role-r1-vs-r2-raw-s-h-technical-scalar-trajectories",
            self.contract.raw_d12_surface,
        )
        self.assertFalse(self.contract.distance_evaluation_allowed)
        self.assertFalse(self.contract.epsilon_allowed)
        self.assertFalse(self.contract.effect_floor_allowed)
        self.assertFalse(self.contract.profile_comparison_allowed)

    def test_structural_roles_remain_frozen(self) -> None:
        self.assertEqual(
            (("ab-r2-exact-repeat", "ab"), ("ba-r2-primary", "ba")),
            self.contract.path_bindings,
        )
        self.assertEqual(5, self.contract.main_production_count_per_role)
        self.assertEqual(5, self.contract.checkpoint_count_per_role)
        self.assertEqual(91, self.contract.expected_sample_count_per_checkpoint)
        self.assertFalse(self.contract.probe_returns_to_main)

    def test_builder_is_value_free_and_tampering_is_rejected(self) -> None:
        self.assertEqual(
            0,
            len(inspect.signature(build_w7bh_const_v_r2_repeat_contract).parameters),
        )
        self.assertFalse(self.contract.accept_result_values)
        self.assertFalse(self.contract.execution_allowed)
        with self.assertRaises(W7BHConstVR2RepeatContractError):
            replace(self.contract, epsilon_allowed=True)

    def test_contract_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "build_w7bh_const_v_r2_repeat_contract")
        )


if __name__ == "__main__":
    unittest.main()
