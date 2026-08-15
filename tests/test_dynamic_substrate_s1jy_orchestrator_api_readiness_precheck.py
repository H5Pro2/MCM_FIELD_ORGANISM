from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    build_dts1_s1jx_sequence_carry_orchestration_contract,
)
from mcm_field_organism.dynamic_substrate_s1jy_orchestrator_api_readiness_precheck import (
    DTS1S1JYOrchestratorAPIReadinessPrecheckError,
    S1_JY_DECISION,
    build_dts1_s1jy_orchestrator_api_readiness_precheck,
)


class DTS1S1JYOrchestratorAPIReadinessPrecheckTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1jy_orchestrator_api_readiness_precheck()

    def test_binds_exact_s1jx_source(self) -> None:
        self.assertEqual(
            build_dts1_s1jx_sequence_carry_orchestration_contract().contract_digest,
            self._audit().source_s1jx_digest,
        )

    def test_preserves_ready_sequence_carry_and_adapter_bindings(self) -> None:
        ready = " ".join(self._audit().confirmed_ready_bindings)
        self.assertIn("seventy-two-replica-identities", ready)
        self.assertIn("forward-carry-rules", ready)
        self.assertIn("eight-eight-six-six", ready)
        self.assertIn("six-technically-accepted-private-S1-JW", ready)

    def test_finds_eight_finite_api_gaps(self) -> None:
        audit = self._audit()
        self.assertEqual(8, audit.blocking_gap_count)
        self.assertEqual(
            (
                "orchestrator_input_api",
                "fresh_sequence_state_payloads",
                "initializer_validation",
                "checkpoint_record_schema",
                "signed_component_index",
                "replica_output_schema",
                "error_boundary",
                "technical_exemplar",
            ),
            tuple(row[0] for row in audit.blocking_gaps),
        )

    def test_identifies_missing_fresh_payloads_and_component_order(self) -> None:
        gaps = dict(self._audit().blocking_gaps)
        self.assertIn("complete-field-and-private-state-payload", gaps["fresh_sequence_state_payloads"])
        self.assertIn("sequence-checkpoint-channel-node-index-order", gaps["signed_component_index"])

    def test_identifies_missing_output_error_and_exemplar_contracts(self) -> None:
        gaps = dict(self._audit().blocking_gaps)
        self.assertIn("atomic-output", gaps["replica_output_schema"])
        self.assertIn("single-public-error-family", gaps["error_boundary"])
        self.assertIn("one-exact-replica-id", gaps["technical_exemplar"])

    def test_blocks_hidden_initializer_and_vector_choices(self) -> None:
        risks = " ".join(self._audit().implementation_risks)
        self.assertIn("S-versus-H-node-and-checkpoint-order", risks)
        self.assertIn("role-or-profile-dependent-hidden-inputs", risks)
        self.assertIn("caller-owned-initializers", risks)
        self.assertIn("unselected-replica-set", risks)

    def test_preserves_all_prior_contracts(self) -> None:
        preserved = " ".join(self._audit().preserved_bindings)
        for token in ("S1-JX", "S1-JW", "S1-JO", "S1-JR", "S1-IR"):
            self.assertIn(token, preserved)

    def test_requires_finite_api_payload_index_and_budget(self) -> None:
        required = " ".join(self._audit().required_correction)
        self.assertIn("one-replica-runner-input-schema", required)
        self.assertIn("fresh-field-and-private-state-payloads", required)
        self.assertIn("component-indices", required)
        self.assertIn("exactly-one-technical-exemplar-replica", required)

    def test_stops_before_every_execution_surface(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.sequence_carry_contract_valid)
        self.assertFalse(audit.finite_runner_api_ready)
        self.assertFalse(audit.orchestrator_implemented)
        self.assertEqual((0, 0, 0), (audit.technical_replicas_executed, audit.profile_cases_executed, audit.baseline_interval_calls_executed))
        self.assertFalse(audit.runtime_integration_present)
        self.assertTrue(audit.finite_orchestrator_api_contract_authorized_next_stage)
        self.assertEqual(S1_JY_DECISION, audit.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1JYOrchestratorAPIReadinessPrecheckError):
            replace(audit, orchestrator_implemented=True)
        source = inspect.getsource(build_dts1_s1jy_orchestrator_api_readiness_precheck)
        for forbidden in ("materialize_", "advance_", "compute_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
