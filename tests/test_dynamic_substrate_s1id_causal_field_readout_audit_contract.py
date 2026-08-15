from __future__ import annotations

from dataclasses import replace
import inspect
import math
import unittest

from mcm_field_organism.dynamic_substrate_s1ic_causal_field_readout_contract import (
    build_dts1_s1ic_causal_field_readout_contract,
)
from mcm_field_organism.dynamic_substrate_s1id_causal_field_readout_audit_contract import (
    DTS1S1IDCausalFieldReadoutAuditContractError,
    S1_ID_DECISION,
    build_dts1_s1id_causal_field_readout_audit_contract,
)


class DTS1S1IDCausalFieldReadoutAuditContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1id_causal_field_readout_audit_contract()

    def test_binds_s1ic_digest_and_one_private_target(self) -> None:
        contract = self._contract()
        self.assertEqual(
            build_dts1_s1ic_causal_field_readout_contract().contract_digest,
            contract.source_s1ic_contract_digest,
        )
        self.assertEqual(
            "mcm_field_organism.dynamic_substrate_dts1_causal_field_readout_audit",
            contract.target_module,
        )

    def test_fixture_binds_two_nodes_zero_contact_and_two_half_steps(self) -> None:
        fixture = dict(self._contract().synthetic_fixture)
        self.assertEqual("two-node-open-line-with-one-canonical-edge", fixture["geometry"])
        self.assertEqual("(-1.0,1.0)", fixture["initial_S"])
        self.assertEqual("(-0.2,0.2)", fixture["initial_H_main"])
        self.assertEqual("(0.0,0.0)", fixture["constant_receptor_contact"])
        self.assertEqual("0.5 synthetic-time-units", fixture["substep_duration"])
        self.assertEqual("2", fixture["substep_count"])

    def test_analytic_preflight_matches_independent_antisymmetric_mode(self) -> None:
        expected = {
            name: float(value) for name, value in self._contract().analytic_preflight
        }
        dt = 0.5
        alpha_bind = -math.expm1(-0.4 * dt)
        f_engagement = alpha_bind * 2.0 * 0.7
        r_free = 1.0 - math.fsum((0.5 * 0.4, 0.5 * 0.8))
        r_engagement = alpha_bind * 2.0 * r_free
        turnover = -math.expm1(-0.3 * dt) * 0.4
        b_f = 0.4 + f_engagement - turnover
        b_r = 0.4 + r_engagement - turnover
        rate_f = 1.0 + 0.5 * b_f
        rate_r = 1.0 + 0.5 * b_r
        c1 = 2.0 * math.exp((-1.0 - 2.0 * 1.2) * dt)
        c2_f = c1 * math.exp((-1.0 - 2.0 * rate_f) * dt)
        c2_r = c1 * math.exp((-1.0 - 2.0 * rate_r) * dt)
        self.assertEqual(expected["substep_1_F_HIGH_engagement"], f_engagement)
        self.assertEqual(expected["substep_1_R_HIGH_engagement"], r_engagement)
        self.assertEqual(expected["substep_1_b1_F_HIGH"], b_f)
        self.assertEqual(expected["substep_1_b1_R_HIGH"], b_r)
        self.assertEqual(expected["substep_2_adapter_rate_F_HIGH"], rate_f)
        self.assertEqual(expected["substep_2_adapter_rate_R_HIGH"], rate_r)
        self.assertEqual(expected["substep_1_field_contrast_both_arms"], c1)
        self.assertEqual(expected["substep_2_field_contrast_F_HIGH"], c2_f)
        self.assertEqual(expected["substep_2_field_contrast_R_HIGH"], c2_r)
        self.assertEqual(expected["substep_2_contrast_margin_R_minus_F"], c2_r - c2_f)

    def test_afterimage_preflight_and_complete_separation_are_independent(self) -> None:
        expected = {
            name: float(value) for name, value in self._contract().analytic_preflight
        }
        dt = 0.5
        afterimage_exponent = math.exp(-2.0 * dt)

        def step(contrast: float, h_contrast: float, eigenvalue: float):
            exponent = math.exp(eigenvalue * dt)
            coupling = 2.0 * (exponent - afterimage_exponent) / (eigenvalue + 2.0)
            return exponent * contrast, afterimage_exponent * h_contrast + coupling * contrast

        c1, h1 = step(2.0, 0.4, -3.4)
        c2_f, h2_f = step(c1, h1, -3.598060136260848)
        c2_r, h2_r = step(c1, h1, -3.4892985881076375)
        separation = max(abs(c2_r - c2_f) / 2.0, abs(h2_r - h2_f) / 2.0)
        self.assertEqual(expected["substep_1_H_contrast_main_both_arms"], h1)
        self.assertEqual(expected["substep_2_complete_SH_separation_main"], separation)
        self.assertGreater(separation, expected["roundoff_floor"])

    def test_five_cases_bind_20_calls_and_double_cap_40(self) -> None:
        contract = self._contract()
        self.assertEqual(5, len(contract.audit_cases))
        self.assertEqual(20, sum(calls for _, _, calls in contract.audit_cases))
        self.assertEqual(20, contract.field_calls_per_audit)
        self.assertEqual(40, contract.maximum_double_audit_field_calls)

    def test_causal_rules_bind_exact_first_step_and_directed_second_step(self) -> None:
        joined = " ".join(self._contract().causal_decision_rules)
        for required in (
            "substep-1-complete-S-H-field-vectors-are-bit-exact",
            "substep-1-b1-values-match-preregistration",
            "substep-2-field-prestates-remain-bit-exact",
            "C_F_HIGH-is-strictly-less-than-C_R_HIGH",
            "complete-S-H-separation-matches-preregistration",
            "second-complete-audit-receipt-is-bit-exact",
        ):
            self.assertIn(required, joined)

    def test_frozen_control_resets_only_anatomy_at_declared_boundary(self) -> None:
        joined = " ".join(self._contract().frozen_control_rules)
        self.assertIn("bit-exact-substep-1-field-output", joined)
        self.assertIn("original-valid-arm-anatomy", joined)
        self.assertIn("identical-b0", joined)
        self.assertIn("not-a-runtime-mode", joined)

    def test_acceptance_is_atomic_and_baseline_execution_is_closed(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.atomic_decision_required)
        self.assertIn(
            "one-failure-makes-the-whole-double-audit-STOPP-with-no-partial-PASS",
            contract.acceptance_rules,
        )
        rules = " ".join(contract.baseline_record_rules)
        self.assertIn("without-executing-baseline-models", rules)
        self.assertIn("A0-and-frozen-b0-are-the-only-executed-field-countercontrols", rules)

    def test_values_are_synthetic_and_execution_remains_closed(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.synthetic_values_bound)
        self.assertTrue(contract.analytic_direction_and_margin_bound)
        self.assertTrue(contract.audit_implementation_and_execution_authorized_next_stage)
        for value in (
            contract.equation_added_or_changed,
            contract.audit_implemented,
            contract.audit_executed,
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
        self.assertEqual(S1_ID_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_static(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1IDCausalFieldReadoutAuditContractError):
            replace(contract, maximum_double_audit_field_calls=41)
        with self.assertRaises(DTS1S1IDCausalFieldReadoutAuditContractError):
            replace(contract, audit_executed=True)
        source = inspect.getsource(build_dts1_s1id_causal_field_readout_audit_contract)
        for forbidden in ("advance_", "compute_", "numpy", "open(", "field_runner"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
