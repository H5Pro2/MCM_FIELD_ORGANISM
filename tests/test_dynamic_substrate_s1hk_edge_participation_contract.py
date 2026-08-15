from __future__ import annotations

from dataclasses import replace
import inspect
import math
import unittest

from mcm_field_organism.dynamic_substrate_s1hk_edge_participation_contract import (
    DTS1S1HKEdgeParticipationContractError,
    S1_HK_DECISION,
    build_dts1_s1hk_edge_participation_contract,
    compute_dts1_s1hk_edge_participation,
)


class DTS1S1HKEdgeParticipationContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1hk_edge_participation_contract()

    def test_observable_has_exact_anchor_values_and_range(self) -> None:
        self.assertEqual(0.0, compute_dts1_s1hk_edge_participation(0.0, 0.0))
        self.assertEqual(0.0, compute_dts1_s1hk_edge_participation(0.75, 0.75))
        self.assertEqual(0.25, compute_dts1_s1hk_edge_participation(1.0, 0.0))
        self.assertEqual(1.0, compute_dts1_s1hk_edge_participation(1.0, -1.0))
        for first in (-1.0, -0.25, 0.0, 0.5, 1.0):
            for second in (-1.0, -0.25, 0.0, 0.5, 1.0):
                value = compute_dts1_s1hk_edge_participation(first, second)
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 1.0)

    def test_observable_is_endpoint_and_joint_sign_invariant(self) -> None:
        first = compute_dts1_s1hk_edge_participation(0.8, -0.2)
        self.assertEqual(first, compute_dts1_s1hk_edge_participation(-0.2, 0.8))
        self.assertEqual(first, compute_dts1_s1hk_edge_participation(-0.8, 0.2))

    def test_invalid_fast_field_values_fail_closed(self) -> None:
        for invalid in (True, math.nan, math.inf, -1.01, 1.01, "field"):
            with self.assertRaises(DTS1S1HKEdgeParticipationContractError):
                compute_dts1_s1hk_edge_participation(invalid, 0.0)

    def test_contract_binds_null_cases_and_shared_e1_baseline(self) -> None:
        contract = self._contract()
        self.assertEqual("p_e=((S_i-S_j)/2)^2", contract.formula)
        self.assertEqual(3, len(contract.null_cases))
        self.assertTrue(contract.same_observable_as_e1_baseline)
        self.assertTrue(contract.observable_is_eligibility_not_transfer)
        self.assertTrue(contract.zero_blocks_engagement_eligibility_only)
        self.assertTrue(contract.turnover_and_recovery_ignore_observable)

    def test_selects_no_threshold_transfer_dynamics_or_effect(self) -> None:
        contract = self._contract()
        for value in (
            contract.threshold_selected,
            contract.transfer_amount_selected,
            contract.rate_selected,
            contract.time_law_selected,
            contract.integrator_selected,
            contract.field_backreaction_selected,
            contract.runtime_implemented,
            contract.functional_effect_proven,
            contract.execution_permitted,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.field_steps_executed)
        self.assertEqual(S1_HK_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_side_effect_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1HKEdgeParticipationContractError):
            replace(contract, transfer_amount_selected=True)
        source = inspect.getsource(compute_dts1_s1hk_edge_participation)
        for forbidden in ("advance_", "field_runner", "open(", "write_text("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
