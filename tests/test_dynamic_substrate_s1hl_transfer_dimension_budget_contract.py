from __future__ import annotations

from dataclasses import replace
import inspect
import math
import unittest

from mcm_field_organism.dynamic_substrate_s1hl_transfer_dimension_budget_contract import (
    DTS1S1HLTransferBudgetContractError,
    S1_HL_DECISION,
    build_dts1_s1hl_transfer_dimension_budget_contract,
    compute_dts1_s1hl_transfer_source_ceilings,
    validate_dts1_s1hl_incident_engagement_budget,
)


class DTS1S1HLTransferDimensionBudgetContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1hl_transfer_dimension_budget_contract()

    def test_source_ceilings_follow_s1hi_half_share_ledger(self) -> None:
        ceilings = compute_dts1_s1hl_transfer_source_ceilings(
            first_endpoint_free=0.25,
            second_endpoint_free=0.75,
            conductive_bound_source=0.4,
            refractory_source=0.3,
        )
        self.assertEqual(0.5, ceilings.engagement_maximum)
        self.assertEqual(0.4, ceilings.turnover_maximum)
        self.assertEqual(0.3, ceilings.recovery_maximum)

    def test_zero_sources_produce_zero_matching_ceilings(self) -> None:
        first = compute_dts1_s1hl_transfer_source_ceilings(0.0, 1.0, 0.0, 0.0)
        second = compute_dts1_s1hl_transfer_source_ceilings(1.0, 0.0, 0.5, 0.25)
        self.assertEqual(0.0, first.engagement_maximum)
        self.assertEqual(0.0, first.turnover_maximum)
        self.assertEqual(0.0, first.recovery_maximum)
        self.assertEqual(0.0, second.engagement_maximum)

    def test_incident_engagement_budget_is_joint_and_fail_closed(self) -> None:
        validate_dts1_s1hl_incident_engagement_budget(0.5, (0.4, 0.6))
        with self.assertRaises(DTS1S1HLTransferBudgetContractError):
            validate_dts1_s1hl_incident_engagement_budget(0.5, (0.4, 0.7))
        with self.assertRaises(DTS1S1HLTransferBudgetContractError):
            validate_dts1_s1hl_incident_engagement_budget(0.5, ())

    def test_invalid_resources_fail_closed_without_clipping(self) -> None:
        for invalid in (True, -0.1, math.nan, math.inf, "resource"):
            with self.assertRaises(DTS1S1HLTransferBudgetContractError):
                compute_dts1_s1hl_transfer_source_ceilings(
                    invalid, 1.0, 1.0, 1.0
                )

    def test_contract_binds_dimensions_nulls_and_no_law(self) -> None:
        contract = self._contract()
        dimensions = dict(contract.dimensions)
        self.assertEqual("resource", dimensions["candidate-transfer-amount"])
        self.assertEqual("dimensionless", dimensions["p_e"])
        self.assertEqual("time", dimensions["physical-interval"])
        self.assertEqual(5, len(contract.required_zeroes))
        self.assertEqual(4, len(contract.source_ceilings))
        self.assertTrue(contract.ceilings_are_not_transfer_amounts)

    def test_selects_no_formula_rate_integrator_runtime_or_effect(self) -> None:
        contract = self._contract()
        for value in (
            contract.transfer_formula_selected,
            contract.parameter_values_selected,
            contract.rate_selected,
            contract.time_law_selected,
            contract.integrator_selected,
            contract.conflict_resolution_selected,
            contract.field_backreaction_selected,
            contract.runtime_implemented,
            contract.functional_effect_proven,
            contract.execution_permitted,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.field_steps_executed)
        self.assertEqual(S1_HL_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_side_effect_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1HLTransferBudgetContractError):
            replace(contract, transfer_formula_selected=True)
        source = inspect.getsource(build_dts1_s1hl_transfer_dimension_budget_contract)
        for forbidden in ("advance_", "field_runner", "open(", "write_text("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
