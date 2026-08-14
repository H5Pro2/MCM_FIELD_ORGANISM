from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.w7bf_const_v_ba_r1_repeat_contract import (
    W7BFConstVBAR1RepeatContractError,
    build_w7bf_const_v_ba_r1_repeat_contract,
)


class W7BFConstVBAR1RepeatContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_w7bf_const_v_ba_r1_repeat_contract()

    def test_contract_binds_current_const_v_chain(self) -> None:
        self.assertEqual(
            "973ac16436c15352132f3103e9c91887c71e388ebb3ac62f73a29e8b8643f5f9",
            self.contract.required_w7bc_contract_digest,
        )
        self.assertEqual(
            "496a795531ce61222fdfea7571f6c34079d5a6f1eb52b56798970a5de3e458db",
            self.contract.required_w7bd_adapter_digest,
        )
        self.assertEqual(
            "88fd9722420a94f09c15fbce9e4e0b2a283a1a56422ed653e92ef2a7aeaf8708",
            self.contract.required_w7be_result_digest,
        )
        self.assertEqual(
            "e7d819ad3eb236360ffda717e0abb8b250a4489b390179d893e755f3a0dc40d0",
            self.contract.contract_digest,
        )

    def test_repeat_precedes_ba_and_failure_stops_ba(self) -> None:
        self.assertEqual(
            ("ab-r1-exact-repeat", "ba-r1-primary"),
            self.contract.execution_roles,
        )
        self.assertEqual(
            "all-canonical-w7be-surfaces-must-be-exactly-equal",
            self.contract.repeat_rule,
        )
        self.assertEqual("stop-before-ba-r1", self.contract.repeat_failure_rule)

    def test_ba_uses_only_authorized_symmetric_sources(self) -> None:
        self.assertEqual("additive.b.combined", self.contract.ba_prefix_role)
        self.assertEqual("additive.a.step", self.contract.ba_continuation_role)
        self.assertTrue(self.contract.ba_source_authorization_required)
        self.assertEqual(
            (
                ("ab-r1-exact-repeat", "ab"),
                ("ba-r1-primary", "ba"),
            ),
            self.contract.path_bindings,
        )

    def test_exact_structural_inventory_is_frozen(self) -> None:
        self.assertEqual(5, self.contract.main_production_count_per_role)
        self.assertEqual(5, self.contract.checkpoint_count_per_role)
        self.assertEqual(91, self.contract.expected_sample_count_per_checkpoint)
        self.assertEqual(
            "deep-copy-then-set-s-h-zero-preserve-scalar",
            self.contract.checkpoint_alignment_rule,
        )
        self.assertFalse(self.contract.probe_returns_to_main)

    def test_r1_pair_cannot_create_epsilon_or_function_decision(self) -> None:
        self.assertEqual(
            "raw-s-h-technical-scalar-trajectories-only",
            self.contract.ba_comparison_surface,
        )
        self.assertFalse(self.contract.ba_distance_evaluation_allowed)
        self.assertFalse(self.contract.r1_numerical_epsilon_allowed)
        self.assertFalse(self.contract.cap_comparison_allowed)
        self.assertFalse(self.contract.profile_comparison_allowed)
        self.assertFalse(self.contract.field_function_decision_allowed)
        self.assertFalse(self.contract.memory_claim_allowed)

    def test_builder_is_value_free_and_tampering_is_rejected(self) -> None:
        self.assertEqual(
            0,
            len(
                inspect.signature(
                    build_w7bf_const_v_ba_r1_repeat_contract
                ).parameters
            ),
        )
        self.assertFalse(self.contract.accept_result_values)
        self.assertFalse(self.contract.execution_allowed)
        with self.assertRaises(W7BFConstVBAR1RepeatContractError):
            replace(self.contract, r1_numerical_epsilon_allowed=True)

    def test_contract_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "build_w7bf_const_v_ba_r1_repeat_contract")
        )


if __name__ == "__main__":
    unittest.main()
