from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    build_dts1_s1ja_finite_configuration_matrix_contract,
)
from mcm_field_organism.dynamic_substrate_s1jn_finite_materialization_schema_contract import (
    build_dts1_s1jn_finite_materialization_schema_contract,
)
from mcm_field_organism.dynamic_substrate_s1jp_baseline_adapter_bridge_contract import (
    build_dts1_s1jp_baseline_adapter_bridge_contract,
)
from mcm_field_organism.dynamic_substrate_s1jr_corrected_role_refinement_contract import (
    build_dts1_s1jr_corrected_role_refinement_contract,
)
from mcm_field_organism.dynamic_substrate_s1js_adapter_payload_readiness_precheck import (
    DTS1S1JSAdapterPayloadReadinessPrecheckError,
    S1_JS_DECISION,
    build_dts1_s1js_adapter_payload_readiness_precheck,
)


class DTS1S1JSAdapterPayloadReadinessPrecheckTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1js_adapter_payload_readiness_precheck()

    def test_binds_exact_prior_sources(self) -> None:
        audit = self._audit()
        self.assertEqual(build_dts1_s1jr_corrected_role_refinement_contract().contract_digest, audit.source_s1jr_digest)
        self.assertEqual(build_dts1_s1jp_baseline_adapter_bridge_contract().contract_digest, audit.source_s1jp_digest)
        self.assertEqual(build_dts1_s1jn_finite_materialization_schema_contract().contract_digest, audit.source_s1jn_digest)
        self.assertEqual(build_dts1_s1ja_finite_configuration_matrix_contract().contract_digest, audit.source_s1ja_digest)

    def test_distinguishes_key_names_from_finite_payload_schemas(self) -> None:
        facts = " ".join(self._audit().bound_but_insufficient)
        self.assertIn("key-names", facts)
        self.assertIn("without-role-payload-shapes", facts)
        self.assertIn("not-all-runtime-object-construction-identities", facts)

    def test_blocks_all_six_roles_with_explicit_gap_records(self) -> None:
        audit = self._audit()
        self.assertEqual((6, 0, 6), (audit.baseline_role_count, audit.role_payload_schema_count, audit.roles_blocked_count))
        self.assertEqual(("B1", "B2", "B3", "B4", "B5", "B6"), tuple(row[0] for row in audit.role_gap_records))

    def test_b1_requires_typed_edge_rate_roundtrip(self) -> None:
        gap = " ".join(self._audit().role_gap_records[0][3])
        self.assertIn("edge-endpoint-and-rate-record", gap)
        self.assertIn("payload-to-typed-result-reconstruction", gap)

    def test_b2_requires_node_bound_L_and_complete_field_commit(self) -> None:
        gap = " ".join(self._audit().role_gap_records[1][3])
        self.assertIn("node-id-to-L-value-association", gap)
        self.assertIn("S2-output-to-SharedMCMField", gap)
        self.assertIn("private-L-commit-protocol", gap)

    def test_b3_to_b5_require_exact_runtime_context_records(self) -> None:
        rows = self._audit().role_gap_records[2:5]
        self.assertTrue(all("runtime-config-object-construction-record" in " ".join(row[3]) for row in rows))
        self.assertTrue(all("embedded-arm-identity" in " ".join(row[3]) for row in rows))

    def test_b6_requires_frozen_spec_payload_and_digest_roundtrip(self) -> None:
        gap = " ".join(self._audit().role_gap_records[5][3])
        self.assertIn("frozen-spec-payload", gap)
        self.assertIn("spec-digest-algorithm", gap)

    def test_common_output_digest_and_error_schema_are_missing(self) -> None:
        gaps = " ".join(self._audit().common_output_gaps)
        self.assertIn("role-specific-diagnostic-record-schema", gaps)
        self.assertIn("canonical-payload-schema", gaps)
        self.assertIn("single-publication-error-type", gaps)

    def test_forbids_inference_hidden_state_and_platform_serialization(self) -> None:
        forbidden = " ".join(self._audit().forbidden_implementation_choices)
        self.assertIn("infer-a-typed-object", forbidden)
        self.assertIn("platform-dependent-numpy-bytes", forbidden)
        self.assertIn("hide-it-in-a-closure-cache-or-global", forbidden)

    def test_preserves_prior_contracts_and_blocks_all_cases(self) -> None:
        audit = self._audit()
        preserved = " ".join(audit.preserved_bindings)
        self.assertIn("S1-JR-exact-and-native", preserved)
        self.assertIn("existing-baseline-kernels-equations", preserved)
        self.assertTrue(audit.all_twenty_four_cases_blocked_atomically)

    def test_stops_before_implementation_or_execution(self) -> None:
        audit = self._audit()
        self.assertFalse(audit.adapter_implementation_ready)
        self.assertFalse(audit.adapters_implemented)
        self.assertFalse(audit.baseline_models_executed)
        self.assertFalse(audit.runtime_integration_present)
        self.assertEqual((0, 0), (audit.technical_field_steps_executed, audit.research_field_steps_executed))
        self.assertTrue(audit.finite_payload_contract_authorized_next_stage)
        self.assertEqual(S1_JS_DECISION, audit.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1JSAdapterPayloadReadinessPrecheckError):
            replace(audit, adapter_implementation_ready=True)
        source = inspect.getsource(build_dts1_s1js_adapter_payload_readiness_precheck)
        for forbidden in ("advance_", "compute_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
