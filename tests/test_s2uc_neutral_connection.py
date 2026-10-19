import unittest
import copy
import tempfile
from pathlib import Path
from unittest.mock import patch

from tools import _s2uc_neutral_connection as connection
from tools import _s2uc_resource_ledger as ledger
from tools import _s2uc_run_entry as entry
from tools import _s2uc_source_binding as binding
from tools import _s2uc_verification as verification
from tools import _s2ub_candidate_confirmation as ub


def neutral_materializer(endpoint):
    index = int(endpoint["source_id"][-1]) + 1
    return tuple(float(index) for _ in range(48))


class S2UCNeutralConnectionTests(unittest.TestCase):
    def test_manifest_binds_all_three_shapes_and_has_no_evaluation_labels(self):
        manifest = binding.manifest()
        self.assertEqual((len(manifest["events"]), manifest["source_plan_sha256"], manifest["source_execution_digest"]), (69, binding.SOURCE_PLAN_SHA256, binding.SOURCE_EXECUTION_DIGEST))
        self.assertTrue(all("label" not in event and "evaluation" not in event for event in manifest["events"]))
        self.assertEqual([sum(event["story"] == story for event in manifest["events"]) for story in ("g1", "g2", "g3")], [26, 17, 26])

    def test_complete_neutral_connection_materializes_once_per_endpoint_and_verifies(self):
        manifest = binding.manifest(); calls = []
        def materializer(endpoint):
            calls.append(endpoint["source_id"])
            return neutral_materializer(endpoint)
        record = connection.execute(manifest, materializer)
        self.assertEqual((record["status"], record["counts"]["materializations"], len(calls), record["not_executed"]), ("COMPLETE", 58, 58, []))
        self.assertEqual(record["counts"]["owner_closes"], 6)
        self.assertEqual(record["terminal"], {"status": "CLOSED", "started_stories": ["g1", "g2", "g3"], "not_executed": []})
        self.assertEqual(verification.verify(record, manifest), {"status": "VERIFIED", "stories": ["g1", "g2", "g3"]})

    def test_failure_between_stories_preserves_completed_story_and_marks_remaining(self):
        manifest = binding.manifest(); calls = [0]
        def materializer(endpoint):
            calls[0] += 1
            if calls[0] == 23:
                raise RuntimeError("NEUTRAL_FAILURE")
            return neutral_materializer(endpoint)
        record = connection.execute(manifest, materializer)
        self.assertEqual(record["status"], "NOT_EVALUABLE")
        self.assertEqual((record["stories"][0]["story"], record["stories"][0]["status"]), ("g1", "COMPLETE"))
        self.assertEqual((record["stories"][1]["story"], record["stories"][1]["status"], record["not_executed"]), ("g2", "NOT_EVALUABLE", ["g3"]))
        self.assertEqual(record["failure"]["progress"]["story"], "g2")
        self.assertEqual(record["failure"]["progress"]["counts"]["materialization_attempts"], 23)
        self.assertEqual(record["failure"]["progress"]["counts"]["materializations"], 22)
        self.assertEqual(record["failure"]["progress"]["counts"]["immediate_calls"], 26)
        self.assertEqual(record["failure"]["progress"]["counts"]["candidate_calls"], 26)
        self.assertEqual(record["terminal"]["status"], "CLOSED_AFTER_FAILURE")
        self.assertEqual(verification.verify_failure(record, manifest), {"status": "VERIFIED_FAILURE", "story": "g2", "failed_ordinal": 27, "phase": "EVENT"})

    def test_common_ledger_uses_alternative_closures_and_rejects_overflow(self):
        manifest = binding.manifest()
        planned = ledger.planned(manifest["binding_bytes"])
        self.assertTrue(all(not branch["violations"] for branch in planned["branches"].values()))
        overflow = ledger.ledger(manifest_bytes=manifest["binding_bytes"], success_record_bytes=ledger.LIMITS["record"] + 1,
                                 failure_record_bytes=1, verification_bytes=1, terminal_bytes=1)
        self.assertIn("record", overflow["branches"]["success"]["violations"])
        self.assertFalse(overflow["branches"]["failure"]["violations"])

    def test_file_entry_rejects_closed_gate_without_invoking_materializer(self):
        with self.assertRaisesRegex(ValueError, "RUN_NOT_AUTHORIZED"):
            entry.run_once(binding.manifest(), neutral_materializer, "unused")

    def test_verifier_rejects_missing_swapped_and_snapshot_manipulations(self):
        manifest = binding.manifest(); record = connection.execute(manifest, neutral_materializer)
        missing = copy.deepcopy(record); missing["stories"] = []
        with self.assertRaisesRegex(ValueError, "STORY_SEQUENCE_INVALID"):
            verification.verify(missing, manifest)
        swapped = copy.deepcopy(record); swapped["stories"][0]["events"][0]["source_id"] = "other"
        with self.assertRaisesRegex(ValueError, "ENDPOINT_BINDING_INVALID"):
            verification.verify(swapped, manifest)
        snapshot = copy.deepcopy(record); snapshot["stories"][0]["hints"][0]["candidate_before"]["retained"] = None
        with self.assertRaisesRegex(ValueError, "CANDIDATE_STATE_INVALID"):
            verification.verify(snapshot, manifest)
        immediate = copy.deepcopy(record); immediate["stories"][0]["hints"][0]["immediate_before"]["retained"] = None
        with self.assertRaisesRegex(ValueError, "IMMEDIATE_STATE_INVALID"):
            verification.verify(immediate, manifest)
        duplicate = copy.deepcopy(record); duplicate["stories"][0]["events"].append(copy.deepcopy(duplicate["stories"][0]["events"][-1]))
        with self.assertRaisesRegex(ValueError, "EVENT_COUNT_INVALID"):
            verification.verify(duplicate, manifest)
        duplicate_hint = copy.deepcopy(record); duplicate_hint["stories"][0]["hints"].append(copy.deepcopy(duplicate_hint["stories"][0]["hints"][0]))
        with self.assertRaisesRegex(ValueError, "DUPLICATE_HINT_RECEIPT_INVALID"):
            verification.verify(duplicate_hint, manifest)

    def test_failure_between_arm_calls_has_independent_progress_verification(self):
        manifest = binding.manifest()
        class FailingImmediate(ub.ImmediateTwArm):
            def form(self, frame):
                raise connection.S2UCConnectionError("IMMEDIATE_ARM_FAILURE")
        with patch.object(connection.ub, "ImmediateTwArm", FailingImmediate):
            record = connection.execute(manifest, neutral_materializer)
        self.assertEqual(record["failure"]["code"], "IMMEDIATE_ARM_FAILURE")
        self.assertEqual(record["failure"]["progress"]["counts"]["immediate_calls"], 1)
        self.assertEqual(record["failure"]["progress"]["counts"]["candidate_calls"], 0)
        self.assertEqual(verification.verify_failure(record, manifest), {"status": "VERIFIED_FAILURE", "story": "g1", "failed_ordinal": 1, "phase": "EVENT"})
        altered = copy.deepcopy(record); altered["failure"]["progress"]["counts"]["immediate_calls"] = 2
        with self.assertRaisesRegex(ValueError, "FAILURE_ARM_PROGRESS_INVALID"):
            verification.verify_failure(altered, manifest)

    def test_first_owner_close_failure_does_not_prevent_second_owner_close(self):
        manifest = binding.manifest(); calls = []
        class CloseFailingImmediate(ub.ImmediateTwArm):
            def close_owner(self):
                calls.append("immediate")
                raise connection.S2UCConnectionError("IMMEDIATE_CLOSE_FAILURE")
        class CountingCandidate(ub.CandidateConfirmationArm):
            def close_owner(self):
                calls.append("candidate")
                return super().close_owner()
        def failing_materializer(endpoint):
            raise connection.S2UCConnectionError("PRIMARY_FAILURE")
        with patch.object(connection.ub, "ImmediateTwArm", CloseFailingImmediate), patch.object(connection.ub, "CandidateConfirmationArm", CountingCandidate):
            record = connection.execute(manifest, failing_materializer)
        self.assertEqual(calls, ["immediate", "candidate"])
        self.assertEqual(record["failure"]["code"], "PRIMARY_FAILURE")
        self.assertEqual(record["stories"][0]["owner_closes"]["immediate"], {"closed": False, "error": "IMMEDIATE_CLOSE_FAILURE"})
        self.assertEqual(record["stories"][0]["owner_closes"]["candidate"], {"closed": True})
        self.assertEqual(verification.verify_failure(record, manifest), {"status": "VERIFIED_FAILURE", "story": "g1", "failed_ordinal": 1, "phase": "EVENT"})

    def test_owner_close_failure_after_complete_story_stops_without_next_story(self):
        manifest = binding.manifest(); calls = []
        class CloseFailingImmediate(ub.ImmediateTwArm):
            def close_owner(self):
                calls.append(self.store.owner)
                raise connection.S2UCConnectionError("IMMEDIATE_CLOSE_FAILURE")
        class CountingCandidate(ub.CandidateConfirmationArm):
            def close_owner(self):
                calls.append(self.owner)
                return super().close_owner()
        with patch.object(connection.ub, "ImmediateTwArm", CloseFailingImmediate), patch.object(connection.ub, "CandidateConfirmationArm", CountingCandidate):
            record = connection.execute(manifest, neutral_materializer)
        self.assertEqual(record["status"], "NOT_EVALUABLE")
        self.assertEqual(record["not_executed"], ["g2", "g3"])
        self.assertEqual(calls, ["s2uc-g1-tw", "s2uc-g1-candidate"])
        self.assertEqual(verification.verify_failure(record, manifest), {"status": "VERIFIED_FAILURE", "story": "g1", "failed_ordinal": None, "phase": "OWNER_CLOSE"})

    def test_failure_verifier_rejects_prior_and_prefix_receipt_manipulations(self):
        manifest = binding.manifest(); counter = [0]
        def fail_after_first_story(endpoint):
            counter[0] += 1
            if counter[0] == 23: raise connection.S2UCConnectionError("LATER_FAILURE")
            return neutral_materializer(endpoint)
        record = connection.execute(manifest, fail_after_first_story)
        transition = copy.deepcopy(record); transition["stories"][0]["transitions"][0]["immediate"]["action"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "TRANSITION_RECEIPT_INVALID"):
            verification.verify_failure(transition, manifest)
        hint = copy.deepcopy(record); hint["stories"][0]["hints"][0]["immediate"]["decision"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "HINT_RECEIPT_INVALID"):
            verification.verify_failure(hint, manifest)
        counter = [0]
        def fail_after_prefix(endpoint):
            counter[0] += 1
            if counter[0] == 6: raise connection.S2UCConnectionError("PREFIX_FAILURE")
            return neutral_materializer(endpoint)
        prefix = connection.execute(manifest, fail_after_prefix)
        altered = copy.deepcopy(prefix); altered["stories"][0]["transitions"][0]["candidate"]["action"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "TRANSITION_RECEIPT_INVALID"):
            verification.verify_failure(altered, manifest)

    def test_entry_resets_gate_after_manifest_failure(self):
        with tempfile.TemporaryDirectory() as root:
            entry.MAIN_GATE = True
            entry.USED = False
            result = entry.run_once({}, neutral_materializer, Path(root) / "out")
        self.assertEqual(result["primary_error"], "MANIFEST_INVALID")
        self.assertFalse(entry.MAIN_GATE)
