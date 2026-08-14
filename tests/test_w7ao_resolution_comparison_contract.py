from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.w7ao_resolution_comparison_contract import (
    W7AOResolutionComparisonContractError,
    build_w7ao_resolution_comparison_contract,
)


class W7AOResolutionComparisonContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_w7ao_resolution_comparison_contract()

    def test_contract_binds_real_w7an_container(self) -> None:
        self.assertEqual(
            "4f150aad9f5c3803f1432550aa4db79b40aea3f7a4975b49802694fad2fff3e5",
            self.contract.w7an_container_digest,
        )

    def test_exact_resolution_comparisons_are_fixed(self) -> None:
        self.assertEqual(
            (("r1-r2", "r1", "r2"), ("r2-r4", "r2", "r4")),
            self.contract.comparisons,
        )
        self.assertEqual(35, len(self.contract.roles))

    def test_primary_and_diagnostic_metrics_are_separate(self) -> None:
        self.assertEqual(("S_linf", "H_linf"), self.contract.primary_metrics)
        self.assertEqual(("SH_l2",), self.contract.diagnostic_metrics)

    def test_numerical_floor_is_preregistered(self) -> None:
        self.assertEqual(
            "maximum-r2-r4-primary-linf-distance",
            self.contract.epsilon_source,
        )
        self.assertEqual(10.0, self.contract.effect_floor_factor)

    def test_contract_does_not_evaluate_or_allow_function_claim(self) -> None:
        self.assertFalse(self.contract.evaluate_values)
        self.assertFalse(self.contract.field_function_decision_allowed)
        self.assertTrue(self.contract.p0_reused_once)

    def test_builder_does_not_accept_or_read_result_values(self) -> None:
        self.assertEqual(
            0,
            len(inspect.signature(build_w7ao_resolution_comparison_contract).parameters),
        )

    def test_tampered_floor_factor_is_rejected(self) -> None:
        with self.assertRaises(W7AOResolutionComparisonContractError):
            replace(self.contract, effect_floor_factor=1.0)

    def test_contract_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "build_w7ao_resolution_comparison_contract")
        )


if __name__ == "__main__":
    unittest.main()
