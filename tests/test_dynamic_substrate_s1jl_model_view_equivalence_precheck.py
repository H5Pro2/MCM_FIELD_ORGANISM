from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    build_dts1_s1jk_corrected_monotonic_interval_contract,
)
from mcm_field_organism.dynamic_substrate_s1jl_model_view_equivalence_precheck import (
    DTS1S1JLModelViewEquivalencePrecheckError,
    S1_JL_DECISION,
    build_dts1_s1jl_model_view_equivalence_precheck,
)


class DTS1S1JLModelViewEquivalencePrecheckTests(unittest.TestCase):
    def _audit(self):
        return build_dts1_s1jl_model_view_equivalence_precheck()

    def test_binds_exact_s1jk_source(self) -> None:
        self.assertEqual(
            build_dts1_s1jk_corrected_monotonic_interval_contract().contract_digest,
            self._audit().source_s1jk_digest,
        )

    def test_records_the_three_conflicting_requirements(self) -> None:
        rows = dict(self._audit().conflicting_requirements)
        self.assertEqual(3, len(rows))
        self.assertIn("value-identical-model-facing-views", rows["S1_JG_COMPLETE_VIEW_IDENTITY"])
        self.assertIn("model-owned-hidden-state-is-carried", rows["S1_JG_MODEL_STATE_CARRY"])
        self.assertIn("complete-S-H", rows["S1_JG_P_IE_COMPLETE_SH_CARRY"])

    def test_covers_all_model_roles_and_profiles(self) -> None:
        audit = self._audit()
        self.assertEqual((7, 4), (audit.model_role_count, audit.affected_profile_count))
        self.assertEqual(("DTS1", "B1", "B2", "B3", "B4", "B5", "B6"), tuple(row[0] for row in audit.model_owned_state_roles))
        self.assertEqual(("P_IE_CAUSAL_TWO_SUBSTEP", "P_IH_ATTENUATION", "P_IK_INTERFERENCE", "P_IN_RELEASE_REUSE"), tuple(row[0] for row in audit.profile_impact))

    def test_preserves_external_exposure_equivalence(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.common_exposure_equivalence_remains_required)
        rules = " ".join(audit.valid_common_exposure_equivalence)
        self.assertIn("same-receptor-contact-distribution", rules)
        self.assertIn("same-envelope-order-checkpoint", rules)
        self.assertIn("no-profile-arm-case-target-result", rules)

    def test_preserves_private_state_without_cross_model_equalization(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.private_model_state_carry_remains_required)
        self.assertFalse(audit.complete_model_view_value_identity_valid)
        rules = " ".join(audit.required_private_prestate_separation)
        self.assertIn("validated-per-model-not-equalized", rules)
        self.assertIn("P_IE-complete-S-H-carry-remains-model-specific", rules)

    def test_requires_separate_common_and_private_digests(self) -> None:
        rows = dict(self._audit().digest_correction_requirements)
        self.assertIn("COMMON_EXPOSURE_DIGEST", rows)
        self.assertIn("PRIVATE_PRESTATE_DIGEST", rows)
        self.assertIn("cross-model-identical", rows["COMMON_EXPOSURE_DIGEST"])
        self.assertIn("orchestrator-only-per-model", rows["PRIVATE_PRESTATE_DIGEST"])

    def test_preserves_prior_bindings_and_blocks_execution(self) -> None:
        audit = self._audit()
        self.assertEqual(24, audit.baseline_case_count_still_blocked)
        self.assertIn("S1-JK-monotonic-times", " ".join(audit.preserved_bindings))
        for value in (audit.materialization_schema_bound, audit.common_interval_fixture_implemented, audit.adapters_implemented, audit.baseline_models_executed, audit.runtime_integration_present, audit.research_execution_permitted):
            self.assertFalse(value)
        self.assertEqual((0, 0), (audit.technical_field_steps_executed, audit.research_field_steps_executed))
        self.assertTrue(audit.corrected_exposure_prestate_contract_authorized_next_stage)
        self.assertEqual(S1_JL_DECISION, audit.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1JLModelViewEquivalencePrecheckError):
            replace(audit, complete_model_view_value_identity_valid=True)
        with self.assertRaises(DTS1S1JLModelViewEquivalencePrecheckError):
            replace(audit, common_exposure_equivalence_remains_required=False)
        source = inspect.getsource(build_dts1_s1jl_model_view_equivalence_precheck)
        for forbidden in ("apply_", "compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
