from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_final_execution_preflight import (
    PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError,
    audit_public_av_return_replication_repeatability_final_execution_preflight,
    public_av_return_replication_repeatability_final_execution_preflight_to_jsonable,
    start_public_av_return_replication_repeatability_from_final_preflight,
)
from mcm_field_organism.public_av_return_replication_repeatability_final_orchestration import (
    orchestrate_public_av_return_replication_repeatability_candidates,
)
from mcm_field_organism.public_media_source_contract import (
    PublicMediaSourceAudit,
    nasa_earthrise_av_source_contract,
)
from tests.test_public_av_return_replication_repeatability_final_orchestration import (
    PublicAVReturnReplicationRepeatabilityFinalOrchestrationTests,
)


class PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightTests(
    PublicAVReturnReplicationRepeatabilityFinalOrchestrationTests
):
    def setUp(self) -> None:
        super().setUp()
        self.orchestration = orchestrate_public_av_return_replication_repeatability_candidates(
            self.binding_acceptance
        )
        source = nasa_earthrise_av_source_contract()
        self.source_audit = PublicMediaSourceAudit(
            source.source_id, True, True, True, True,
            source.expected_size_bytes, source.expected_sha1,
        )

    def build_preflight(self):
        return audit_public_av_return_replication_repeatability_final_execution_preflight(
            self.orchestration, self.source_audit
        )

    def test_rechecks_source_integrity_and_three_fresh_candidates(self) -> None:
        preflight = self.build_preflight()
        self.assertTrue(preflight.source_audit_accepted)
        self.assertTrue(preflight.receptor_release_still_locked)
        self.assertEqual((1, 2, 3), tuple(x.repeat_index for x in preflight.slot_preflights))
        self.assertTrue(preflight.all_three_one_shot_states_fresh)

    def test_rejects_source_identity_or_integrity_change(self) -> None:
        with self.assertRaises(PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError):
            audit_public_av_return_replication_repeatability_final_execution_preflight(
                self.orchestration, replace(self.source_audit, sha1_matches=False, accepted=False)
            )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError):
            audit_public_av_return_replication_repeatability_final_execution_preflight(
                self.orchestration, replace(self.source_audit, source_id="changed.source")
            )

    def test_rejects_nonfresh_candidate(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.orchestration.ordered_start_candidates[0], scheduled=True)
            replace(self.orchestration, ordered_start_candidates=(changed, *self.orchestration.ordered_start_candidates[1:]))

    def test_objects_scheduler_run_receptors_and_claims_remain_locked(self) -> None:
        preflight = self.build_preflight()
        for role in (
            "callable_objects_created", "gate_instances_created", "bindings_performed",
            "scheduler_available", "start_release_granted", "repeatability_run_allowed",
            "media_decode_allowed", "receptor_feed_allowed", "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError):
                replace(preflight, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightError):
            start_public_av_return_replication_repeatability_from_final_preflight(preflight)

    def test_json_contains_no_execution_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_final_execution_preflight_to_jsonable(
            self.build_preflight()
        )
        self.assertEqual(len(payload["slot_preflights"]), 3)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
