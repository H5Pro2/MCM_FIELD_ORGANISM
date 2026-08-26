from __future__ import annotations

from dataclasses import replace
import inspect
import math
import unittest

import numpy as np

from mcm_field_organism.dynamic_substrate_s1ii_interference_contract import (
    build_dts1_s1ii_interference_contract,
)
from mcm_field_organism.dynamic_substrate_s1ij_interference_audit_contract import (
    DTS1S1IJInterferenceAuditContractError,
    S1_IJ_DECISION,
    build_dts1_s1ij_interference_audit_contract,
)


def _tuple(value: str) -> tuple[float, ...]:
    return tuple(float(item) for item in value.strip("()").split(","))


def _resource_step(state, p_a, p_b):
    b_a, u_a, b_b, u_b = state
    alpha_b = -math.expm1(-0.4 * 0.5)
    alpha_t = -math.expm1(-0.3 * 0.5)
    alpha_r = -math.expm1(-0.2 * 0.5)
    free = (
        1.0 - 0.5 * (b_a + u_a),
        1.0 - 0.5 * (b_a + u_a + b_b + u_b),
        1.0 - 0.5 * (b_b + u_b),
    )
    engagement_a = alpha_b * p_a * 2.0 * min(free[0], free[1])
    engagement_b = alpha_b * p_b * 2.0 * min(free[1], free[2])
    next_state = (
        b_a + engagement_a - alpha_t * b_a,
        u_a + alpha_t * b_a - alpha_r * u_a,
        b_b + engagement_b - alpha_t * b_b,
        u_b + alpha_t * b_b - alpha_r * u_b,
    )
    return next_state, engagement_a, engagement_b, free


class DTS1S1IJInterferenceAuditContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1ij_interference_audit_contract()

    def test_binds_s1ii_digest_and_private_target(self) -> None:
        contract = self._contract()
        self.assertEqual(
            build_dts1_s1ii_interference_contract().contract_digest,
            contract.source_s1ii_contract_digest,
        )
        self.assertEqual(
            "mcm_field_organism.dynamic_substrate_dts1_interference_audit",
            contract.target_module,
        )

    def test_fixture_binds_three_node_shared_endpoint_sequence(self) -> None:
        fixture = dict(self._contract().synthetic_fixture)
        self.assertIn("node-a-node-b-node-c", fixture["geometry"])
        self.assertEqual("(A=1.0,B=0.0)", fixture["A_participation"])
        self.assertEqual("(A=0.0,B=1.0)", fixture["B_participation"])
        self.assertEqual("(A=0.0,B=0.0)", fixture["gap_participation"])
        self.assertEqual("0.5 synthetic-time-units", fixture["interval_duration"])

    def test_resource_preflight_matches_independent_two_arm_recurrence(self) -> None:
        expected = dict(self._contract().analytic_resource_preflight)
        initial = (0.2, 0.1, 0.2, 0.1)
        common, first_a, _, _ = _resource_step(initial, 1.0, 0.0)
        aba_pre, _, middle_b, _ = _resource_step(common, 0.0, 1.0)
        gap_pre, _, gap_b, _ = _resource_step(common, 0.0, 0.0)
        aba_post, aba_final, _, aba_free = _resource_step(aba_pre, 1.0, 0.0)
        gap_post, gap_final, _, gap_free = _resource_step(gap_pre, 1.0, 0.0)
        self.assertEqual(_tuple(expected["common_after_first_A_state_bA_uA_bB_uB"]), common)
        self.assertEqual(float(expected["first_A_engagement"]), first_a)
        self.assertEqual(float(expected["middle_B_engagement_ABA"]), middle_b)
        self.assertEqual(float(expected["middle_B_engagement_gap"]), gap_b)
        self.assertEqual(float(expected["prefinal_shared_free_ABA"]), aba_free[1])
        self.assertEqual(float(expected["prefinal_shared_free_gap"]), gap_free[1])
        self.assertEqual(float(expected["final_A_engagement_ABA"]), aba_final)
        self.assertEqual(float(expected["final_A_engagement_gap"]), gap_final)
        self.assertEqual(_tuple(expected["postsequence_ABA_state_bA_uA_bB_uB"]), aba_post)
        self.assertEqual(_tuple(expected["postsequence_gap_state_bA_uA_bB_uB"]), gap_post)

    def test_field_preflight_matches_independent_symmetric_generator_solution(self) -> None:
        resource = dict(self._contract().analytic_resource_preflight)
        field = dict(self._contract().analytic_field_preflight)
        initial_s = np.asarray((-1.0, 0.0, 1.0), dtype=np.float64)
        outputs = {}
        for arm in ("ABA", "gap"):
            state = _tuple(resource[f"postsequence_{arm}_state_bA_uA_bB_uB"])
            rate_a = 1.0 + 0.5 * state[0]
            rate_b = 1.0 + 0.5 * state[2]
            generator = np.asarray(
                (
                    (-rate_a - 1.0, rate_a, 0.0),
                    (rate_a, -rate_a - rate_b - 1.0, rate_b),
                    (0.0, rate_b, -rate_b - 1.0),
                ),
                dtype=np.float64,
            )
            eigenvalues, eigenvectors = np.linalg.eigh(generator)
            output = eigenvectors @ (
                np.exp(eigenvalues * 0.5) * (eigenvectors.T @ initial_s)
            )
            outputs[arm] = output
            self.assertEqual(_tuple(field[f"{arm}_main_S"]), tuple(float(x) for x in output))
        contrast_aba = float(outputs["ABA"][1] - outputs["ABA"][0])
        contrast_gap = float(outputs["gap"][1] - outputs["gap"][0])
        self.assertEqual(float(field["A_edge_contrast_ABA"]), contrast_aba)
        self.assertEqual(float(field["A_edge_contrast_gap"]), contrast_gap)
        self.assertGreater(contrast_aba, contrast_gap)

    def test_seven_cases_bind_exact_call_budgets(self) -> None:
        contract = self._contract()
        self.assertEqual(24, sum(item[2] for item in contract.audit_cases))
        self.assertEqual(10, sum(item[3] for item in contract.audit_cases))
        self.assertEqual(48, contract.maximum_double_audit_direct_resource_calls)
        self.assertEqual(20, contract.maximum_double_audit_technical_field_calls)
        self.assertEqual(0, contract.maximum_research_field_steps)

    def test_decision_binds_resource_field_and_control_directions(self) -> None:
        rules = " ".join(self._contract().numeric_decision_rules)
        self.assertIn("middle-B-engagement-in-ABA-is-strictly-positive", rules)
        self.assertIn("prefinal-shared-free-ABA-is-strictly-lower", rules)
        self.assertIn("final-A-engagement-ABA-is-strictly-lower", rules)
        self.assertIn("A-edge-contrast-ABA-is-strictly-greater", rules)
        self.assertIn("zero-H-S-vectors-match-main-S-vectors", rules)
        self.assertIn("N06-final-A-engagement-is-exactly-zero", rules)

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
            contract.interference_proven,
            contract.release_or_reuse_proven,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.direct_resource_calls_executed)
        self.assertEqual(0, contract.technical_field_calls_executed)
        self.assertEqual(0, contract.research_field_steps_executed)
        self.assertEqual(S1_IJ_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_static(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1IJInterferenceAuditContractError):
            replace(contract, technical_field_calls_per_audit=11)
        with self.assertRaises(DTS1S1IJInterferenceAuditContractError):
            replace(contract, audit_executed=True)
        source = inspect.getsource(build_dts1_s1ij_interference_audit_contract)
        for forbidden in ("compute_", "advance_", "execute_", "open(", "write_text("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
