from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1hx_refinement_causality_audit_contract import (
    DTS1S1HXRefinementCausalityAuditContractError,
    S1_HX_DECISION,
    build_dts1_s1hx_refinement_causality_audit_contract,
)


class DTS1S1HXRefinementCausalityAuditContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1hx_refinement_causality_audit_contract()

    def test_binds_one_private_target_three_scenarios_and_three_levels(self) -> None:
        contract = self._contract()
        self.assertEqual(
            "mcm_field_organism.dynamic_substrate_dts1_refinement_causality_audit",
            contract.target_module,
        )
        self.assertEqual((2, 4, 8), contract.partitions)
        self.assertEqual(3, len(contract.scenarios))

    def test_fixture_is_fixed_synthetic_and_not_a_material_selection(self) -> None:
        fixture = dict(self._contract().synthetic_fixture)
        for role in (
            "physical_duration",
            "initial_S",
            "initial_H",
            "constant_contact",
            "node_capacities",
            "dts1_rates",
            "active_resources",
            "zero_resources",
        ):
            self.assertIn(role, fixture)
        self.assertTrue(self._contract().synthetic_fixture_values_bound)
        self.assertFalse(self._contract().material_rate_values_selected)

    def test_all_levels_share_one_physical_input_and_only_partition_changes(self) -> None:
        rules = self._contract().identical_input_rules
        for required in (
            "all-levels-cover-the-same-closed-physical-interval-zero-to-two",
            "constant-contact-and-all-event-boundaries-are-identical-across-levels",
            "only-the-uniform-substep-count-changes-between-two-four-and-eight",
            "no-result-dependent-fixture-step-or-threshold-change-is-permitted",
        ):
            self.assertIn(required, rules)

    def test_complete_pair_vector_and_residual_are_unambiguously_bound(self) -> None:
        contract = self._contract()
        self.assertEqual(4, len(contract.pair_vector))
        joined = " ".join(contract.residual_rules)
        for required in (
            "maximum-absolute-component-difference",
            "R_n_2n",
            "R_2n_4n",
            "512*float64-epsilon",
            "strictly-less-than",
        ):
            self.assertIn(required, joined)
        self.assertTrue(contract.complete_pair_refinement_required)

    def test_causality_binds_exact_first_step_and_halving_latency(self) -> None:
        joined = " ".join(self._contract().causality_rules)
        for required in (
            "first-A1-and-A0-field-proposals-are-bit-exact",
            "positive-new-binding",
            "final-A1-A0-field-separation-must-exceed",
            "1.0-0.5-0.25",
            "current-substep-use",
        ):
            self.assertIn(required, joined)
        self.assertTrue(self._contract().explicit_latency_halving_required)

    def test_acceptance_is_atomic_and_every_failure_has_stopp_effect(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.atomic_decision_required)
        self.assertIn(
            "one-failure-makes-the-whole-audit-STOPP-with-no-partial-PASS",
            contract.acceptance_rules,
        )
        self.assertEqual(8, len(contract.stopp_conditions))
        self.assertIn(
            "active-fine-residual-not-strictly-smaller-than-coarse-residual",
            contract.stopp_conditions,
        )

    def test_execution_cap_and_output_are_complete_before_next_stage(self) -> None:
        contract = self._contract()
        self.assertEqual(140, contract.maximum_technical_field_steps)
        self.assertTrue(
            contract.audit_implementation_and_execution_authorized_next_stage
        )
        self.assertIn(
            "technical-field-step-count-and-canonical-SHA256-receipt",
            contract.output_schema,
        )

    def test_research_runtime_function_and_claim_boundaries_remain_closed(self) -> None:
        contract = self._contract()
        for value in (
            contract.audit_implemented,
            contract.audit_executed,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
            contract.functional_effect_proven,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.research_field_steps_executed)
        self.assertEqual(S1_HX_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_static(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1HXRefinementCausalityAuditContractError):
            replace(contract, maximum_technical_field_steps=141)
        with self.assertRaises(DTS1S1HXRefinementCausalityAuditContractError):
            replace(contract, audit_executed=True)
        source = inspect.getsource(
            build_dts1_s1hx_refinement_causality_audit_contract
        )
        for forbidden in ("numpy", "advance_", "field_runner", "open("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
