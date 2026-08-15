from __future__ import annotations

from dataclasses import replace
import inspect
import math
import unittest

from mcm_field_organism.dynamic_substrate_s1hz_free_refractory_intervention_contract import (
    build_dts1_s1hz_free_refractory_intervention_contract,
)
from mcm_field_organism.dynamic_substrate_s1ia_free_refractory_audit_contract import (
    DTS1S1IAFreeRefractoryAuditContractError,
    S1_IA_DECISION,
    build_dts1_s1ia_free_refractory_audit_contract,
)


class DTS1S1IAFreeRefractoryAuditContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1ia_free_refractory_audit_contract()

    def test_binds_s1hz_digest_and_one_private_target(self) -> None:
        contract = self._contract()
        self.assertEqual(
            build_dts1_s1hz_free_refractory_intervention_contract().contract_digest,
            contract.source_s1hz_contract_digest,
        )
        self.assertEqual(
            "mcm_field_organism.dynamic_substrate_dts1_free_refractory_audit",
            contract.target_module,
        )

    def test_fixture_binds_one_edge_two_matched_inner_arms(self) -> None:
        fixture = dict(self._contract().synthetic_fixture)
        self.assertEqual(
            "one-isolated-existing-canonical-edge-node-a-node-b",
            fixture["geometry"],
        )
        self.assertEqual("0.4", fixture["conductive_bound_both_arms"])
        self.assertEqual("0.2", fixture["F_HIGH_refractory"])
        self.assertEqual("0.8", fixture["R_HIGH_refractory"])
        self.assertEqual("0.7", fixture["F_HIGH_derived_free_per_node"])
        self.assertEqual(
            "0.3999999999999999",
            fixture["R_HIGH_derived_free_per_node"],
        )

    def test_derived_free_values_preserve_both_local_identities(self) -> None:
        capacity = 1.0
        conductive = 0.4
        for refractory, expected_free in ((0.2, 0.7), (0.8, 0.3999999999999999)):
            allocated = math.fsum((0.5 * conductive, 0.5 * refractory))
            derived_free = capacity - allocated
            self.assertEqual(derived_free, expected_free)
            self.assertEqual(
                math.fsum((derived_free, 0.5 * conductive, 0.5 * refractory)),
                capacity,
            )

    def test_analytic_preflight_matches_independent_float64_calculation(self) -> None:
        preflight = {
            name: float(value) for name, value in self._contract().analytic_preflight
        }
        alpha = -math.expm1(-0.4 * 0.5)
        f_engagement = alpha * 1.0 * 2.0 * 0.7
        r_free = 1.0 - math.fsum((0.5 * 0.4, 0.5 * 0.8))
        r_engagement = alpha * 1.0 * 2.0 * r_free
        self.assertEqual(preflight["alpha_bind"], alpha)
        self.assertEqual(preflight["F_HIGH_engagement_offer"], f_engagement)
        self.assertEqual(preflight["R_HIGH_engagement_offer"], r_engagement)
        self.assertEqual(
            preflight["expected_engagement_difference"],
            f_engagement - r_engagement,
        )
        self.assertLess(preflight["F_HIGH_node_demand"], 0.7)
        self.assertLess(preflight["R_HIGH_node_demand"], r_free)

    def test_four_cases_bind_exactly_eight_calls_per_audit(self) -> None:
        contract = self._contract()
        self.assertEqual(
            (
                "C01_DIRECT_INTERVENTION_PAIR",
                "N01_EQUAL_PARTITION_REPEAT",
                "N02_ZERO_PARTICIPATION",
                "N03_ZERO_BINDING_RATE",
            ),
            tuple(case_id for case_id, _, _ in contract.audit_cases),
        )
        self.assertEqual(8, sum(calls for _, _, calls in contract.audit_cases))
        self.assertEqual(8, contract.pure_step_calls_per_audit)
        self.assertEqual(16, contract.maximum_double_audit_pure_step_calls)

    def test_decision_uses_direct_engagement_floor_and_exact_nulls(self) -> None:
        contract = self._contract()
        joined = " ".join(contract.numeric_decision_rules)
        self.assertTrue(contract.direct_engagement_measurement_required)
        self.assertTrue(contract.exact_null_controls_required)
        self.assertIn("target-edge-engagement-field", joined)
        self.assertIn("0.2537769456908254", joined)
        self.assertIn("0.14501539753761447", joined)
        self.assertIn("strictly-greater", joined)
        self.assertIn("exactly-zero", joined)

    def test_baselines_are_static_unaugmented_records_only(self) -> None:
        rules = " ".join(self._contract().baseline_record_rules)
        self.assertIn("five-S1HZ-baseline-counterpredictions", rules)
        self.assertIn("do-not-execute-baseline-models", rules)
        self.assertIn("hidden-free-refractory-coordinate", rules)
        self.assertFalse(self._contract().baseline_models_executed)

    def test_acceptance_is_atomic_repeatable_and_field_free(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.atomic_decision_required)
        self.assertTrue(contract.exact_repeat_required)
        self.assertEqual(0, contract.maximum_field_steps)
        self.assertIn(
            "one-failure-makes-the-whole-double-audit-STOPP-with-no-partial-PASS",
            contract.acceptance_rules,
        )

    def test_values_are_synthetic_and_execution_remains_closed(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.synthetic_values_bound)
        self.assertTrue(contract.audit_implementation_and_execution_authorized_next_stage)
        for value in (
            contract.equation_added_or_changed,
            contract.material_parameters_selected,
            contract.audit_implemented,
            contract.audit_executed,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
            contract.functional_effect_proven,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.pure_resource_steps_executed)
        self.assertEqual(0, contract.field_steps_executed)
        self.assertEqual(0, contract.research_field_steps_executed)
        self.assertEqual(S1_IA_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_static(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1IAFreeRefractoryAuditContractError):
            replace(contract, maximum_double_audit_pure_step_calls=17)
        with self.assertRaises(DTS1S1IAFreeRefractoryAuditContractError):
            replace(contract, audit_executed=True)
        source = inspect.getsource(build_dts1_s1ia_free_refractory_audit_contract)
        for forbidden in ("compute_", "advance_", "numpy", "open(", "field_runner"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
