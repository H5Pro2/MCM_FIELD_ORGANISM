from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1jh_finite_common_interval_fixture_contract import (
    build_dts1_s1jh_finite_common_interval_fixture_contract,
)
from mcm_field_organism.dynamic_substrate_s1ji_materialization_readiness_precheck import (
    DTS1S1JIMaterializationReadinessPrecheckError,
    S1_JI_DECISION,
    build_dts1_s1ji_materialization_readiness_precheck,
)


class DTS1S1JIMaterializationReadinessPrecheckTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1ji_materialization_readiness_precheck()

    def test_binds_exact_s1jh_source(self) -> None:
        self.assertEqual(
            build_dts1_s1jh_finite_common_interval_fixture_contract().contract_digest,
            self._audit().source_s1jh_digest,
        )

    def test_preserves_all_s1jh_bindings(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.s1jh_remains_bound)
        self.assertTrue(audit.information_barrier_preserved)
        self.assertEqual(6, len(audit.bound_surfaces))

    def test_finds_four_independent_missing_binding_groups(self) -> None:
        rows = {row[0]: row[1:] for row in self._audit().missing_materialization_bindings}
        self.assertEqual(4, self._audit().missing_binding_group_count)
        self.assertIn("RECEPTOR_DISTRIBUTION_IDENTITY", rows)
        self.assertIn("FIELD_INPUT_AND_PRESTATE_API", rows)
        self.assertIn("MODEL_FACING_INPUT_DIGEST_SCHEMA", rows)
        self.assertIn("ATOMIC_OUTPUT_AND_ERROR_CONTRACT", rows)

    def test_identifies_missing_receptor_and_dock_roles(self) -> None:
        rows = dict((row[0], row[1]) for row in self._audit().missing_materialization_bindings)
        self.assertEqual(
            ("modality_id", "receptor_geometry_id", "dock_id", "carrier_to_neuron_pairs"),
            rows["RECEPTOR_DISTRIBUTION_IDENTITY"],
        )

    def test_requires_value_only_digest_schema(self) -> None:
        rows = dict((row[0], row[1]) for row in self._audit().missing_materialization_bindings)
        self.assertIn("canonical_field_payload", rows["MODEL_FACING_INPUT_DIGEST_SCHEMA"])
        shortcuts = " ".join(self._audit().invalid_implementation_shortcuts)
        self.assertIn("object-id-or-process-dependent-hashing", shortcuts)

    def test_blocks_all_implementation_and_execution(self) -> None:
        audit = self._audit()
        self.assertFalse(audit.materialization_schema_complete)
        for value in (audit.common_interval_fixture_implemented, audit.adapters_implemented, audit.baseline_models_executed, audit.runtime_integration_present, audit.research_execution_permitted):
            self.assertFalse(value)
        self.assertEqual((0, 0), (audit.technical_field_steps_executed, audit.research_field_steps_executed))
        self.assertEqual(S1_JI_DECISION, audit.decision)

    def test_authorizes_only_corrected_contract_next(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.corrected_materialization_contract_authorized_next_stage)
        self.assertEqual(5, len(audit.next_contract_requirements))
        consequences = " ".join(audit.consequences)
        self.assertIn("zero-of-twenty-four", consequences)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1JIMaterializationReadinessPrecheckError):
            replace(audit, materialization_schema_complete=True)
        with self.assertRaises(DTS1S1JIMaterializationReadinessPrecheckError):
            replace(audit, common_interval_fixture_implemented=True)
        source = inspect.getsource(build_dts1_s1ji_materialization_readiness_precheck)
        for forbidden in ("apply_", "compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
