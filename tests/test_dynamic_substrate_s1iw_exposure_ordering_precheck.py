from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1iv_common_causal_exposure_contract import (
    build_dts1_s1iv_common_causal_exposure_contract,
)
from mcm_field_organism.dynamic_substrate_s1iw_exposure_ordering_precheck import (
    DTS1S1IWExposureOrderingPrecheckError,
    S1_IW_DECISION,
    build_dts1_s1iw_exposure_ordering_precheck,
)


class DTS1S1IWExposureOrderingPrecheckTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1iw_exposure_ordering_precheck()

    def test_binds_exact_s1iv_contract(self) -> None:
        self.assertEqual(
            build_dts1_s1iv_common_causal_exposure_contract().contract_digest,
            self._audit().source_s1iv_digest,
        )

    def test_binds_closed_prestate_resource_before_current_field_payload(self) -> None:
        order = self._audit().coupled_step_order
        self.assertLess(order.index("derive-S1-HK-edge-participation-from-the-closed-S-field-prestate"), order.index("only-after-resource-commit-advance-S-H-through-the-current-receptor-distribution"))

    def test_detects_both_profile_misalignments(self) -> None:
        records = dict(self._audit().misalignment_records)
        self.assertEqual(2, self._audit().affected_profile_block_count)
        self.assertIn("following-A-labelled-interval", records["P_IK_INTERFERENCE"])
        self.assertIn("before-the-immediate-common-SH-reset", records["P_IN_RELEASE_REUSE"])

    def test_values_or_duration_cannot_repair_ordering(self) -> None:
        rules = " ".join(self._audit().blocking_rules)
        self.assertIn("changing-contact-amplitude-duration-or-tolerance-cannot-reverse", rules)
        self.assertIn("one-interval-label-shift-is-not-a-shape-adapter", rules)

    def test_requires_common_boundary_clamp_while_preserving_hidden_state(self) -> None:
        rules = " ".join(self._audit().correction_requirements)
        self.assertIn("common-S-H-boundary-clamp-before-each-A-B-or-gap", rules)
        self.assertIn("preserving-each-model-owned-hidden-state", rules)
        self.assertIn("derive-DTS1-participation-only-after-the-common-clamp", rules)

    def test_preserves_unaffected_s1iv_rules_and_direct_evidence(self) -> None:
        rules = " ".join(self._audit().correction_requirements)
        forbidden = " ".join(self._audit().forbidden_interpretations)
        self.assertIn("supersede-only-the-S1-IV-within-history-S-H-carry-rule", rules)
        self.assertIn("invalidity-of-existing-direct-ledgers", forbidden)

    def test_binds_no_values_matrix_implementation_or_execution(self) -> None:
        audit = self._audit()
        for value in (
            audit.event_boundary_contract_valid,
            audit.exposure_values_selected,
            audit.durations_selected,
            audit.reset_prestates_selected,
            audit.configuration_values_selected,
            audit.configuration_digests_bound,
            audit.finite_case_matrix_bound,
            audit.fixture_implemented,
            audit.baseline_models_executed,
            audit.runtime_integration_present,
            audit.research_execution_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0), (audit.technical_field_steps_executed, audit.research_field_steps_executed))
        self.assertEqual(S1_IW_DECISION, audit.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1IWExposureOrderingPrecheckError):
            replace(audit, event_boundary_contract_valid=True)
        with self.assertRaises(DTS1S1IWExposureOrderingPrecheckError):
            replace(audit, affected_profile_block_count=0)
        source = inspect.getsource(build_dts1_s1iw_exposure_ordering_precheck)
        for forbidden in ("compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
