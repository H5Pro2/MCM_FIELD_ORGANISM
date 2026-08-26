from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.w7bc_const_v_r124_trajectory_contract import (
    W7BCConstVTrajectoryContractError,
    build_w7bc_const_v_r124_trajectory_contract,
)


class W7BCConstVTrajectoryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_w7bc_const_v_r124_trajectory_contract()

    def test_canonical_sources_and_const_v_equation_are_frozen(self) -> None:
        self.assertEqual("const-v", self.contract.model_id)
        self.assertEqual(
            "a1e3f8a08fbef760c8f0b147f99cbebfcc05621c2265a70d853dd3d4863ffb6a",
            self.contract.required_w7m_matrix_digest,
        )
        self.assertEqual(
            "c771a3c28c04e04a61fa24d187416ef65b17597f9af759682deb576a28c25b32",
            self.contract.required_w7y_plan_digest,
        )
        self.assertEqual(
            (("eta", 1.0), ("kappa", 0.5), ("lambda_sm", 0.5)),
            self.contract.parameter_bindings,
        )
        self.assertFalse(self.contract.organism_runtime_allowed)
        self.assertEqual(
            "973ac16436c15352132f3103e9c91887c71e388ebb3ac62f73a29e8b8643f5f9",
            self.contract.contract_digest,
        )

    def test_const_v_arm_exists_before_the_first_safe_step(self) -> None:
        self.assertEqual(
            "fresh-w7m-initial-field-with-const-v-arm-before-safe-step",
            self.contract.initialization_rule,
        )
        self.assertEqual(
            "mcm_f3_runtime.advance_mcm_f3_shared_field_transient",
            self.contract.runtime_provider,
        )
        self.assertEqual(
            "w7n.compute_w7n_coupling_baseline",
            self.contract.coupling_provider,
        )

    def test_exact_seven_path_r124_inventory_and_repeats_are_required(self) -> None:
        self.assertEqual(
            ("ab", "ag", "ba", "bg", "ua", "ub", "ug"),
            self.contract.path_ids,
        )
        self.assertEqual((1, 2, 4), self.contract.primary_order)
        self.assertEqual((4, 2, 1), self.contract.exact_repeat_order)
        self.assertEqual(35, self.contract.trajectory_role_count_per_resolution)
        self.assertEqual(105, self.contract.primary_trajectory_count)
        self.assertEqual(105, self.contract.exact_repeat_trajectory_count)

    def test_probe_alignment_preserves_only_the_technical_scalar(self) -> None:
        self.assertEqual(
            "align-s-and-h-to-zero-on-full-state-probe-copy",
            self.contract.checkpoint_rule,
        )
        self.assertTrue(self.contract.preserve_scalar_on_alignment)
        self.assertFalse(self.contract.probe_returns_to_main)
        self.assertEqual(
            ("s", "h", "technical_scalar"),
            self.contract.sampled_components,
        )

    def test_const_v_gets_its_own_convergence_before_common_floor(self) -> None:
        self.assertEqual(70, self.contract.convergence_comparison_count)
        self.assertEqual(
            "maximum-of-all-70-r2-r4-s-h-linf-distances",
            self.contract.const_v_epsilon_rule,
        )
        self.assertEqual(
            "maximum-of-cap-epsilon-and-const-v-epsilon",
            self.contract.common_epsilon_rule,
        )
        self.assertEqual(
            "ten-times-common-epsilon",
            self.contract.common_effect_floor_rule,
        )

    def test_contract_makes_no_result_or_function_claim(self) -> None:
        self.assertFalse(self.contract.cap_capacity_ledger_allowed)
        self.assertFalse(self.contract.cap_target_capacity_role_allowed)
        self.assertFalse(self.contract.technical_scalar_is_memory)
        self.assertFalse(self.contract.accept_result_values)
        self.assertFalse(self.contract.execution_allowed)
        self.assertFalse(self.contract.profile_decision_allowed)
        self.assertFalse(self.contract.field_function_decision_allowed)
        self.assertFalse(self.contract.memory_claim_allowed)

    def test_builder_is_value_free_and_tampering_is_rejected(self) -> None:
        self.assertEqual(
            0,
            len(
                inspect.signature(
                    build_w7bc_const_v_r124_trajectory_contract
                ).parameters
            ),
        )
        with self.assertRaises(W7BCConstVTrajectoryContractError):
            replace(self.contract, convergence_comparison_count=69)

    def test_contract_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "build_w7bc_const_v_r124_trajectory_contract")
        )


if __name__ == "__main__":
    unittest.main()
