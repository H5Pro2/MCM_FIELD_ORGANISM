from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1hh_function_falsification_contract import (
    build_dynamic_substrate_s1hh_contract,
)
from mcm_field_organism.dynamic_substrate_s1io_evidence_falsification_audit import (
    DTS1S1IOEvidenceAuditError,
    S1_IO_DECISION,
    build_dts1_s1io_evidence_falsification_audit,
)


class DTS1S1IOEvidenceFalsificationAuditTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1io_evidence_falsification_audit()

    def test_binds_s1hh_and_all_five_immutable_audit_receipts(self) -> None:
        audit = self._audit()
        self.assertEqual(build_dynamic_substrate_s1hh_contract().contract_digest, audit.source_s1hh_contract_digest)
        self.assertEqual(("S1-IB", "S1-IE", "S1-IH", "S1-IK", "S1-IN"), tuple(name for name, _ in audit.source_audit_receipts))
        self.assertTrue(all(len(digest) == 64 for _, digest in audit.source_audit_receipts))

    def test_classifies_all_seven_required_measurements_as_supported(self) -> None:
        audit = self._audit()
        self.assertEqual(7, len(audit.measurement_classifications))
        self.assertTrue(all("SUPPORTED" in status for _, status, _ in audit.measurement_classifications))
        self.assertTrue(audit.all_required_measurement_roles_supported)

    def test_direct_functions_bind_expected_receipts(self) -> None:
        records = {name: sources for name, _, sources in self._audit().measurement_classifications}
        self.assertEqual(("S1-IH",), records["M02_REPEATED_EQUAL_CONTACT_ATTENUATION"])
        self.assertEqual(("S1-IK",), records["M03_ABA_MATCHED_GAP_INTERFERENCE"])
        self.assertEqual(("S1-IN",), records["M04_FREE_RECOVERY_AND_ADJACENT_REUSE"])
        self.assertEqual(("S1-IB", "S1-IE"), records["M06_SH_MATCHED_FREE_REFRACTORY_INTERVENTION"])

    def test_classifies_all_five_baselines_without_false_closure(self) -> None:
        audit = self._audit()
        records = {name: status for name, status, _ in audit.baseline_classifications}
        self.assertEqual(5, len(records))
        self.assertIn("GLOBAL_FIT_OPEN", records["fixed-adapter-and-frozen-e1"])
        self.assertIn("NOT_EXECUTED", records["leaky-trace-and-integrator"])
        self.assertIn("COUNTERPREDICTION_SUPPORTED", records["dynamic-two-state-e1"])
        self.assertIn("NOT_EXECUTED", records["f3-and-const-v"])
        self.assertIn("SUPPORTED", records["fast-afterimage"])
        self.assertFalse(audit.baseline_closure_complete)

    def test_classifies_every_s1hh_falsification_condition(self) -> None:
        audit = self._audit()
        self.assertEqual(10, len(audit.falsification_classifications))
        records = {name: status for name, status, _ in audit.falsification_classifications}
        self.assertIn("OPEN", records["F06_ONE_FIXED_ADAPTER_REPRODUCES_COMPLETE_TRAJECTORY"])
        self.assertIn("OPEN", records["F07_ONE_LEAKY_OR_INTEGRATOR_BASELINE_REPRODUCES_ALL_PROFILES"])
        self.assertIn("OPEN", records["F08_F3_OR_CONSTV_REPRODUCES_ALL_PROFILES_AND_INTERVENTIONS"])
        self.assertFalse(audit.direct_function_falsification_triggered)

    def test_blocks_same_fixture_variants_until_joint_baseline_contract(self) -> None:
        audit = self._audit()
        conclusions = " ".join(audit.scope_conclusions)
        self.assertIn("no-further-same-fixture-variant-is-authorized", conclusions)
        self.assertTrue(audit.joint_baseline_contract_authorized_next_stage)

    def test_remains_static_and_claim_closed(self) -> None:
        audit = self._audit()
        for value in (
            audit.candidate_globally_validated,
            audit.equation_added_or_changed,
            audit.fixture_added_or_changed,
            audit.baseline_models_executed,
            audit.runtime_integration_present,
            audit.research_execution_permitted,
            audit.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0, 0), (audit.technical_resource_calls_executed, audit.technical_field_calls_executed, audit.research_field_steps_executed))
        self.assertEqual(S1_IO_DECISION, audit.decision)

    def test_audit_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1IOEvidenceAuditError):
            replace(audit, baseline_closure_complete=True)
        with self.assertRaises(DTS1S1IOEvidenceAuditError):
            replace(audit, fixture_added_or_changed=True)
        source = inspect.getsource(build_dts1_s1io_evidence_falsification_audit)
        for forbidden in ("compute_", "advance_", "execute_", "run_", "open(", "write_text("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
