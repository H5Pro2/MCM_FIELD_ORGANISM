from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_identifiability_contract import (
    E1CommonProbeIdentifiabilityContractError,
    S1_EC45_PROBE_ROLES,
    build_e1_common_probe_identifiability_contract,
)


class E1CommonProbeIdentifiabilityContractTests(unittest.TestCase):
    def test_contract_moves_all_comparisons_to_one_probe_space(self) -> None:
        result = build_e1_common_probe_identifiability_contract()
        self.assertFalse(result.direct_cross_space_subtraction_permitted)
        self.assertEqual(S1_EC45_PROBE_ROLES, result.probe_roles)
        self.assertTrue(result.identical_reset_field_required)
        self.assertTrue(result.feedback_ablation_is_causal_control)
        self.assertTrue(result.formation_ablation_is_causal_control)

    def test_execution_stays_closed_until_acceptance_bound_exists(self) -> None:
        result = build_e1_common_probe_identifiability_contract()
        self.assertFalse(result.numerical_acceptance_bound_pre_registered)
        self.assertFalse(result.field_execution_permitted)
        self.assertTrue(result.implementation_permitted)
        self.assertFalse(result.result_decision_permitted)
        self.assertFalse(result.memory_claim_permitted)

    def test_cross_space_comparison_fails_closed(self) -> None:
        result = build_e1_common_probe_identifiability_contract()
        with self.assertRaises(E1CommonProbeIdentifiabilityContractError):
            replace(result, direct_cross_space_subtraction_permitted=True)

    def test_builder_contains_no_field_kernel_or_write_path(self) -> None:
        source = inspect.getsource(build_e1_common_probe_identifiability_contract)
        for forbidden in (
            "run_neutral_asynchronous_field",
            "run_prepared_real_formation_arm_in_memory",
            "open(",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
