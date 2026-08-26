from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_no_input_gap_audit import (
    PublicAVNoInputGapAuditError,
    audit_public_av_no_input_gap_step_time,
    public_av_no_input_gap_audit_json_value,
    public_av_no_input_gap_audit_public_roles,
)
from mcm_field_organism.public_av_two_stage_return_runner import (
    execute_public_av_two_stage_return_runner,
    wire_public_av_two_stage_return_runner,
)


class PublicAVNoInputGapAuditTests(unittest.TestCase):
    def test_fixed_gap_is_represented_as_contact_free_step_time(self) -> None:
        audit = audit_public_av_no_input_gap_step_time()
        self.assertEqual("no_input_gap.step_time_only", audit.resolution_phase)
        self.assertEqual((500_000_000, 600_000_000), audit.resolution_interval_ticks)
        self.assertEqual(100_000_000, audit.resolution_duration_ticks)
        self.assertEqual(0, audit.contact_free_distribution_contact_count)
        self.assertTrue(audit.step_time_only_interval_matches)

    def test_runtime_distinction_is_explicit(self) -> None:
        audit = audit_public_av_no_input_gap_step_time()
        self.assertFalse(audit.high_level_asynchronous_runtime_accepts_empty_sequence)
        self.assertTrue(audit.lower_contact_free_field_step_available)
        self.assertTrue(audit.uses_existing_neutral_fast_field_step)

    def test_audit_does_not_introduce_events_content_or_parameter_changes(self) -> None:
        audit = audit_public_av_no_input_gap_step_time()
        self.assertFalse(audit.artificial_receptor_events_introduced)
        self.assertFalse(audit.special_content_introduced)
        self.assertFalse(audit.field_parameters_changed)

    def test_runner_and_claims_remain_blocked(self) -> None:
        audit = audit_public_av_no_input_gap_step_time()
        self.assertFalse(audit.runner_execution_allowed)
        self.assertFalse(audit.field_run_allowed)
        self.assertFalse(audit.memory_claim_allowed)
        self.assertFalse(audit.meaning_claim_allowed)
        self.assertFalse(audit.organization_claim_allowed)
        self.assertFalse(audit.ai_claim_allowed)
        with self.assertRaisesRegex(PublicAVNoInputGapAuditError, "cannot release"):
            replace(audit, field_run_allowed=True)
        with self.assertRaisesRegex(PublicAVNoInputGapAuditError, "cannot release"):
            replace(audit, artificial_receptor_events_introduced=True)

    def test_existing_runner_is_still_not_executable(self) -> None:
        wiring = wire_public_av_two_stage_return_runner()
        audit = audit_public_av_no_input_gap_step_time(wiring)
        self.assertTrue(audit.audit_complete)
        with self.assertRaisesRegex(Exception, "not released"):
            execute_public_av_two_stage_return_runner(wiring)

    def test_json_and_roles_exclude_payloads_and_claim_scores(self) -> None:
        audit = audit_public_av_no_input_gap_step_time()
        encoded = public_av_no_input_gap_audit_json_value(audit)
        self.assertEqual([500_000_000, 600_000_000], encoded["resolution_interval_ticks"])
        forbidden = {
            "raw_samples",
            "pixels",
            "container_metadata",
            "label",
            "reward",
            "memory_score",
            "meaning_score",
            "organization_score",
        }
        self.assertTrue(forbidden.isdisjoint(public_av_no_input_gap_audit_public_roles()))


if __name__ == "__main__":
    unittest.main()
