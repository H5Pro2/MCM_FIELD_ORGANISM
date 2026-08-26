from __future__ import annotations

from dataclasses import replace
import inspect
import math
import unittest

from mcm_field_organism.dynamic_substrate_s1if_attenuation_contract import build_dts1_s1if_attenuation_contract
from mcm_field_organism.dynamic_substrate_s1ig_attenuation_audit_contract import (
    DTS1S1IGAttenuationAuditContractError,
    S1_IG_DECISION,
    build_dts1_s1ig_attenuation_audit_contract,
)


class DTS1S1IGAttenuationAuditContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1ig_attenuation_audit_contract()

    def test_binds_s1if_digest_and_private_target(self) -> None:
        contract = self._contract()
        self.assertEqual(build_dts1_s1if_attenuation_contract().contract_digest, contract.source_s1if_contract_digest)
        self.assertEqual("mcm_field_organism.dynamic_substrate_dts1_attenuation_audit", contract.target_module)

    def test_fixture_binds_three_equal_contacts_and_common_probes(self) -> None:
        fixture = dict(self._contract().synthetic_fixture)
        self.assertEqual("3", fixture["contact_count"])
        self.assertEqual("1.0", fixture["contact_participation"])
        self.assertEqual("0.5 synthetic-time-units", fixture["contact_elapsed_time"])
        self.assertEqual("(node-a=-1.0,node-b=1.0)", fixture["common_probe_S"])
        self.assertEqual("(node-a=0.0,node-b=0.0)", fixture["matched_zero_H"])

    def test_resource_preflight_matches_independent_recurrence(self) -> None:
        preflight = dict(self._contract().analytic_resource_preflight)
        expected_engagement = tuple(float(x) for x in preflight["engagement"].strip("()").split(","))
        b, u = 0.4, 0.2
        alpha_b = -math.expm1(-0.4 * 0.5)
        alpha_t = -math.expm1(-0.3 * 0.5)
        alpha_r = -math.expm1(-0.2 * 0.5)
        observed = []
        for _ in range(3):
            free = 1.0 - math.fsum((0.5 * b, 0.5 * u))
            engagement = alpha_b * 2.0 * free
            turnover = alpha_t * b
            recovery = alpha_r * u
            observed.append(engagement)
            b = b + engagement - turnover
            u = u + turnover - recovery
        self.assertEqual(expected_engagement, tuple(observed))
        self.assertGreater(observed[0], observed[1])
        self.assertGreater(observed[1], observed[2])
        self.assertEqual(float(preflight["postcontact_b3"]), b)
        self.assertEqual(float(preflight["postcontact_refractory3"]), u)

    def test_field_preflight_matches_independent_two_node_solution(self) -> None:
        resource = dict(self._contract().analytic_resource_preflight)
        field = dict(self._contract().analytic_field_preflight)
        bindings = tuple(float(x) for x in resource["precontact_b"].strip("()").split(","))
        expected = tuple(float(x) for x in field["common_probe_S_contrasts"].strip("()").split(","))
        observed = tuple(2.0 * math.exp(-(3.0 + binding) * 0.5) for binding in bindings)
        self.assertEqual(expected, observed)
        self.assertGreater(observed[0], observed[1])
        self.assertGreater(observed[1], observed[2])
        self.assertGreater(float(field["second_contrast_drop"]), float(field["roundoff_floor"]))

    def test_six_cases_bind_exact_call_budgets(self) -> None:
        contract = self._contract()
        self.assertEqual(8, sum(item[2] for item in contract.audit_cases))
        self.assertEqual(14, sum(item[3] for item in contract.audit_cases))
        self.assertEqual(16, contract.maximum_double_audit_direct_resource_calls)
        self.assertEqual(28, contract.maximum_double_audit_technical_field_calls)
        self.assertEqual(0, contract.maximum_research_field_steps)

    def test_decision_binds_both_directions_and_all_controls(self) -> None:
        rules = " ".join(self._contract().numeric_decision_rules)
        self.assertIn("engagement-contact-1-is-strictly-greater", rules)
        self.assertIn("common-probe-contrast-1-is-strictly-greater", rules)
        self.assertIn("zero-H-probe-S-contrasts-match", rules)
        self.assertIn("N02-produces-the-same-neutral-contrast", rules)
        self.assertIn("N03-produces-the-same-initial-adapter", rules)
        self.assertIn("N05-produces-exact-zero-engagement", rules)

    def test_baselines_are_static_and_e1_boundary_remains_explicit(self) -> None:
        rules = " ".join(self._contract().baseline_record_rules)
        self.assertIn("no-baseline-model-is-executed-or-fit", rules)
        self.assertIn("dynamic-two-state-E1-remains-explicitly-not-separated", rules)
        self.assertFalse(self._contract().baseline_models_executed)

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
            contract.attenuation_proven,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.direct_resource_calls_executed)
        self.assertEqual(0, contract.technical_field_calls_executed)
        self.assertEqual(0, contract.research_field_steps_executed)
        self.assertEqual(S1_IG_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_static(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1IGAttenuationAuditContractError):
            replace(contract, technical_field_calls_per_audit=15)
        with self.assertRaises(DTS1S1IGAttenuationAuditContractError):
            replace(contract, audit_executed=True)
        source = inspect.getsource(build_dts1_s1ig_attenuation_audit_contract)
        for forbidden in ("compute_", "advance_", "execute_", "numpy", "open("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
