from __future__ import annotations

from dataclasses import replace
import inspect
import math
import unittest

import numpy as np

from mcm_field_organism.dynamic_substrate_s1il_release_reuse_contract import (
    build_dts1_s1il_release_reuse_contract,
)
from mcm_field_organism.dynamic_substrate_s1im_release_reuse_audit_contract import (
    DTS1S1IMReleaseReuseAuditContractError,
    S1_IM_DECISION,
    build_dts1_s1im_release_reuse_audit_contract,
)


def _tuple(value: str) -> tuple[float, ...]:
    return tuple(float(item) for item in value.strip("()").split(","))


def _resource_step(state, p_a, p_b, recovery_rate):
    b_a, u_a, b_b, u_b = state
    alpha_b = -math.expm1(-0.4 * 0.5)
    alpha_t = -math.expm1(-0.3 * 0.5)
    alpha_r = -math.expm1(-recovery_rate * 0.5)
    free = (
        1.0 - math.fsum((0.5 * b_a, 0.5 * u_a)),
        1.0
        - math.fsum(
            (
                math.fsum((0.5 * b_a, 0.5 * b_b)),
                math.fsum((0.5 * u_a, 0.5 * u_b)),
            )
        ),
        1.0 - math.fsum((0.5 * b_b, 0.5 * u_b)),
    )
    engagement_a = alpha_b * p_a * 2.0 * min(free[0], free[1])
    engagement_b = alpha_b * p_b * 2.0 * min(free[1], free[2])
    recovery_a = alpha_r * u_a
    recovery_b = alpha_r * u_b
    next_state = (
        b_a + engagement_a - alpha_t * b_a,
        u_a + alpha_t * b_a - recovery_a,
        b_b + engagement_b - alpha_t * b_b,
        u_b + alpha_t * b_b - recovery_b,
    )
    return next_state, engagement_a, engagement_b, recovery_a, recovery_b, free


class DTS1S1IMReleaseReuseAuditContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1im_release_reuse_audit_contract()

    def test_binds_s1il_digest_and_private_target(self) -> None:
        contract = self._contract()
        self.assertEqual(
            build_dts1_s1il_release_reuse_contract().contract_digest,
            contract.source_s1il_contract_digest,
        )
        self.assertEqual(
            "mcm_field_organism.dynamic_substrate_dts1_release_reuse_audit",
            contract.target_module,
        )

    def test_fixture_binds_shared_endpoint_load_release_and_B_probe(self) -> None:
        fixture = dict(self._contract().synthetic_fixture)
        self.assertIn("node-a-node-b-node-c", fixture["geometry"])
        self.assertEqual("(A=1.0,B=0.0)", fixture["A_load_participation"])
        self.assertEqual("(A=0.0,B=0.0)", fixture["release_window_participation"])
        self.assertEqual("(A=0.0,B=1.0)", fixture["B_probe_participation"])
        self.assertIn("recovery=0.0", fixture["recovery_off_rates"])

    def test_resource_preflight_matches_independent_two_arm_recurrence(self) -> None:
        expected = dict(self._contract().analytic_resource_preflight)
        initial = (0.2, 0.1, 0.2, 0.1)
        common, load_a, _, _, _, _ = _resource_step(initial, 1.0, 0.0, 0.2)
        on_pre, _, _, rec_a, rec_b, _ = _resource_step(common, 0.0, 0.0, 0.2)
        off_pre, _, _, off_rec_a, off_rec_b, _ = _resource_step(common, 0.0, 0.0, 0.0)
        on_post, _, on_b, _, _, on_free = _resource_step(on_pre, 0.0, 1.0, 0.2)
        off_post, _, off_b, _, _, off_free = _resource_step(off_pre, 0.0, 1.0, 0.2)
        self.assertEqual(float(expected["common_A_load_engagement"]), load_a)
        self.assertEqual(_tuple(expected["common_postload_state_bA_uA_bB_uB"]), common)
        self.assertEqual(float(expected["recovery_on_window_A_recovery"]), rec_a)
        self.assertEqual(float(expected["recovery_on_window_B_recovery"]), rec_b)
        self.assertEqual((0.0, 0.0), (off_rec_a, off_rec_b))
        self.assertEqual(_tuple(expected["recovery_on_preprobe_state_bA_uA_bB_uB"]), on_pre)
        self.assertEqual(_tuple(expected["recovery_off_preprobe_state_bA_uA_bB_uB"]), off_pre)
        self.assertEqual(float(expected["recovery_on_preprobe_shared_free"]), on_free[1])
        self.assertEqual(float(expected["recovery_off_preprobe_shared_free"]), off_free[1])
        self.assertEqual(float(expected["recovery_on_B_engagement"]), on_b)
        self.assertEqual(float(expected["recovery_off_B_engagement"]), off_b)
        self.assertEqual(_tuple(expected["recovery_on_postprobe_state_bA_uA_bB_uB"]), on_post)
        self.assertEqual(_tuple(expected["recovery_off_postprobe_state_bA_uA_bB_uB"]), off_post)

    def test_preprobe_conductive_state_is_exact_and_margins_are_positive(self) -> None:
        expected = dict(self._contract().analytic_resource_preflight)
        on_pre = _tuple(expected["recovery_on_preprobe_state_bA_uA_bB_uB"])
        off_pre = _tuple(expected["recovery_off_preprobe_state_bA_uA_bB_uB"])
        self.assertEqual((on_pre[0], on_pre[2]), (off_pre[0], off_pre[2]))
        self.assertGreater(float(expected["shared_free_release_margin"]), 0.0)
        self.assertGreater(float(expected["additional_B_engagement_margin"]), 0.0)

    def test_field_preflight_matches_independent_symmetric_generator(self) -> None:
        resource = dict(self._contract().analytic_resource_preflight)
        field = dict(self._contract().analytic_field_preflight)
        initial_s = np.asarray((-1.0, 0.0, 1.0), dtype=np.float64)
        outputs = {}
        for arm in ("recovery_on", "recovery_off"):
            state = _tuple(resource[f"{arm}_postprobe_state_bA_uA_bB_uB"])
            rate_a = 1.0 + 0.5 * state[0]
            rate_b = 1.0 + 0.5 * state[2]
            generator = np.asarray(
                ((-rate_a - 1.0, rate_a, 0.0), (rate_a, -rate_a - rate_b - 1.0, rate_b), (0.0, rate_b, -rate_b - 1.0)),
                dtype=np.float64,
            )
            eigenvalues, eigenvectors = np.linalg.eigh(generator)
            output = eigenvectors @ (np.exp(eigenvalues * 0.5) * (eigenvectors.T @ initial_s))
            outputs[arm] = output
            self.assertEqual(_tuple(field[f"{arm}_main_S"]), tuple(float(x) for x in output))
        on_contrast = float(outputs["recovery_on"][2] - outputs["recovery_on"][1])
        off_contrast = float(outputs["recovery_off"][2] - outputs["recovery_off"][1])
        self.assertEqual(float(field["B_edge_contrast_recovery_on"]), on_contrast)
        self.assertEqual(float(field["B_edge_contrast_recovery_off"]), off_contrast)
        self.assertGreater(off_contrast, on_contrast)

    def test_eight_cases_bind_exact_double_budget(self) -> None:
        contract = self._contract()
        self.assertEqual(8, len(contract.audit_cases))
        self.assertEqual(18, sum(item[2] for item in contract.audit_cases))
        self.assertEqual(10, sum(item[3] for item in contract.audit_cases))
        self.assertEqual(36, contract.maximum_double_audit_direct_resource_calls)
        self.assertEqual(20, contract.maximum_double_audit_technical_field_calls)
        self.assertEqual(0, contract.maximum_research_field_steps)

    def test_decision_binds_release_reuse_and_all_controls(self) -> None:
        rules = " ".join(self._contract().numeric_decision_rules)
        self.assertIn("positive-A-and-B-recovery", rules)
        self.assertIn("conductive-bound-values-are-bit-exact", rules)
        self.assertIn("B-engagement-is-higher", rules)
        for case_id in ("N01", "N02", "N03", "N04", "N05", "N06"):
            self.assertIn(case_id, rules)

    def test_baselines_are_static_and_e1_limit_remains_explicit(self) -> None:
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
            contract.release_proven,
            contract.reuse_proven,
            contract.e1_nonreducibility_proven,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0, 0), (contract.direct_resource_calls_executed, contract.technical_field_calls_executed, contract.research_field_steps_executed))
        self.assertEqual(S1_IM_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_static(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1IMReleaseReuseAuditContractError):
            replace(contract, technical_field_calls_per_audit=11)
        with self.assertRaises(DTS1S1IMReleaseReuseAuditContractError):
            replace(contract, audit_executed=True)
        source = inspect.getsource(build_dts1_s1im_release_reuse_audit_contract)
        for forbidden in ("compute_", "advance_", "execute_", "open(", "write_text("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
