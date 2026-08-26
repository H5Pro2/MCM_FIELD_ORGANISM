from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ip_joint_baseline_contract import (
    build_dts1_s1ip_joint_baseline_contract,
)
from mcm_field_organism.dynamic_substrate_s1iq_compatibility_precheck import (
    DTS1S1IQCompatibilityPrecheckError,
    S1_IQ_DECISION,
    build_dts1_s1iq_compatibility_precheck,
)


class DTS1S1IQCompatibilityPrecheckTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1iq_compatibility_precheck()

    def test_binds_exact_s1ip_contract(self) -> None:
        self.assertEqual(
            build_dts1_s1ip_joint_baseline_contract().contract_digest,
            self._audit().source_s1ip_digest,
        )

    def test_derives_two_node_blocks_as_eight_components_each(self) -> None:
        rows = {row[0]: row[1:] for row in self._audit().profile_cardinalities}
        self.assertEqual((2, 2, 4, 8, 12), rows["P_IE_CAUSAL_TWO_SUBSTEP"])
        self.assertEqual((2, 2, 4, 8, 12), rows["P_IH_ATTENUATION"])

    def test_derives_three_node_blocks_as_six_components_each(self) -> None:
        rows = {row[0]: row[1:] for row in self._audit().profile_cardinalities}
        self.assertEqual((3, 1, 6, 6, 6), rows["P_IK_INTERFERENCE"])
        self.assertEqual((3, 1, 6, 6, 6), rows["P_IN_RELEASE_REUSE"])

    def test_detects_exact_total_mismatch(self) -> None:
        audit = self._audit()
        self.assertEqual(28, audit.expected_profile_component_count)
        self.assertEqual(36, audit.registered_profile_component_count)
        self.assertEqual(8, audit.cardinality_excess)
        self.assertFalse(audit.profile_contract_valid)

    def test_applies_first_atomic_decision(self) -> None:
        audit = self._audit()
        self.assertEqual("INVALID_JOINT_BASELINE_AUDIT", audit.first_atomic_decision)
        self.assertEqual(S1_IQ_DECISION, audit.decision)

    def test_leaves_all_six_baselines_unclassified(self) -> None:
        audit = self._audit()
        self.assertEqual(6, len(audit.baseline_statuses))
        self.assertTrue(
            all(status == "NOT_REACHED_INVALID_PROFILE_CARDINALITY" for _, status in audit.baseline_statuses)
        )
        self.assertFalse(audit.baseline_signatures_classified)

    def test_authorizes_only_static_correction_contract_next(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.correction_contract_authorized_next_stage)
        stopp = " ".join(audit.stopp_rules)
        self.assertIn("superseded-by-one-static-corrected-profile-contract", stopp)
        self.assertIn("no-baseline-may-be-classified", stopp)

    def test_executes_nothing_and_expands_no_claim(self) -> None:
        audit = self._audit()
        for value in (
            audit.geometry_adapters_specified,
            audit.parameter_values_selected,
            audit.baseline_models_executed,
            audit.runtime_integration_present,
            audit.research_execution_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0), (audit.technical_field_steps_executed, audit.research_field_steps_executed))

    def test_is_deterministic_tamper_evident_and_model_execution_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1IQCompatibilityPrecheckError):
            replace(audit, expected_profile_component_count=36)
        with self.assertRaises(DTS1S1IQCompatibilityPrecheckError):
            replace(audit, baseline_signatures_classified=True)
        source = inspect.getsource(build_dts1_s1iq_compatibility_precheck)
        for forbidden in ("compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
