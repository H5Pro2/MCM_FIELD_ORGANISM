from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ic_causal_field_readout_contract import (
    DTS1S1ICCausalFieldReadoutContractError,
    S1_IC_DECISION,
    build_dts1_s1ic_causal_field_readout_contract,
)


class DTS1S1ICCausalFieldReadoutContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1ic_causal_field_readout_contract()

    def test_binds_successful_s1ib_receipt_and_exactly_two_arms(self) -> None:
        contract = self._contract()
        self.assertEqual(
            "55159311a95b555900632014d68b3534aeb958787e0e6bcfba4d3e32dfedb217",
            contract.source_s1ib_audit_receipt_digest,
        )
        self.assertEqual(2, len(contract.arm_ids))
        self.assertTrue(contract.exact_two_substeps_required)

    def test_closed_pair_differs_only_in_free_refractory_partition(self) -> None:
        joined = " ".join(self._contract().closed_pair_rules)
        for required in (
            "value-identical-complete-field-S-and-H-prestates",
            "identical-geometry-capacities-total-resource-and-conductive-binding",
            "only-the-valid-ledger-derived-free-versus-refractory-partition-differs",
            "identical-contact-event-boundaries-field-configs-step-times-and-DTS1-rates",
            "no-arm-label-result-value-or-poststate",
        ):
            self.assertIn(required, joined)

    def test_causal_chain_binds_exact_first_step_and_delayed_field_readout(self) -> None:
        contract = self._contract()
        joined = " ".join(contract.two_substep_causal_chain)
        self.assertTrue(contract.first_substep_field_identity_required)
        self.assertTrue(contract.second_substep_causal_readout_required)
        for required in (
            "substep-1-applied-adapter-is-bit-exact",
            "substep-1-complete-field-proposal-S1-H1-is-bit-exact",
            "b1-F_HIGH-is-strictly-greater",
            "substep-2-applied-adapter-rate-F_HIGH-is-strictly-greater",
            "resource-proposals-cannot-affect-the-concurrent",
            "no-third-substep",
        ):
            self.assertIn(required, joined)

    def test_field_observable_and_direction_are_bound_before_values(self) -> None:
        contract = self._contract()
        self.assertEqual(5, len(contract.field_observables))
        joined = " ".join(contract.direction_rules)
        for required in (
            "positive-target-edge-contrast-before-substep-2",
            "analytically-preregister-the-sign-and-nonzero-margin-before-execution",
            "strictly-smaller-substep-2-contrast",
            "complete-substep-2-S-H-separation-must-exceed",
            "no-observed-direction-threshold-or-fixture-value",
        ):
            self.assertIn(required, joined)

    def test_four_controls_cover_equal_a0_frozen_and_zero_h(self) -> None:
        self.assertEqual(
            (
                "N01_EQUAL_PARTITION_TWO_SUBSTEP_REPEAT",
                "N02_A0_TWO_SUBSTEP_CONTROL",
                "N03_FROZEN_INITIAL_ADAPTER_CONTROL",
                "N04_MATCHED_ZERO_H_CONTROL",
            ),
            tuple(case_id for case_id, _ in self._contract().control_cases),
        )

    def test_all_five_baseline_groups_have_counterpredictions(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.complete_baseline_set_required)
        self.assertEqual(
            (
                "fixed-adapter-and-frozen-e1",
                "leaky-trace-and-integrator",
                "dynamic-two-state-e1",
                "f3-and-const-v",
                "fast-afterimage",
            ),
            tuple(name for name, _ in contract.baseline_counterpredictions),
        )

    def test_acceptance_is_atomic_and_poststate_explanations_stop(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.atomic_decision_required)
        self.assertIn(
            "one-failure-makes-the-whole-readout-audit-STOPP-with-no-partial-PASS",
            contract.acceptance_rules,
        )
        self.assertIn(
            "substep-2-resource-poststate-or-any-third-substep-is-used-to-explain-the-readout",
            contract.stopp_conditions,
        )

    def test_values_equations_execution_runtime_and_claims_remain_closed(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.finite_fixture_audit_contract_authorized_next_stage)
        for value in (
            contract.fixture_values_selected,
            contract.equation_added_or_changed,
            contract.readout_implemented,
            contract.readout_executed,
            contract.baseline_models_executed,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
            contract.field_effect_proven,
            contract.broader_function_proven,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.technical_field_steps_executed)
        self.assertEqual(0, contract.research_field_steps_executed)
        self.assertEqual(S1_IC_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_static(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1ICCausalFieldReadoutContractError):
            replace(contract, readout_executed=True)
        with self.assertRaises(DTS1S1ICCausalFieldReadoutContractError):
            replace(contract, exact_two_substeps_required=False)
        source = inspect.getsource(build_dts1_s1ic_causal_field_readout_contract)
        for forbidden in ("advance_", "compute_", "numpy", "open(", "field_runner"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
