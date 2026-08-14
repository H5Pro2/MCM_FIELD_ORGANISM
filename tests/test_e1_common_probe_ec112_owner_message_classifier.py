from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec112_owner_message_classifier import (
    E1CommonProbeEC112OwnerMessageClassifierError,
    classify_e1_common_probe_ec112_owner_message,
)
from mcm_field_organism.e1_common_probe_n2_r2_real_mode_coordinator import (
    S1_EC67_EC59_HANDOFF_DIGEST,
)


class E1CommonProbeEC112OwnerMessageClassifierTests(unittest.TestCase):
    def test_ok_weiter_is_continuation_only(self) -> None:
        result = classify_e1_common_probe_ec112_owner_message("  OK   weiter ")
        self.assertEqual("continuation-only", result.message_class)
        self.assertTrue(result.continuation_work_permitted)
        self.assertFalse(result.owner_scope_token_creation_permitted)

    def test_question_and_stop_are_separate(self) -> None:
        question = classify_e1_common_probe_ec112_owner_message(
            "Wie ist der Forschungsstand?"
        )
        stop = classify_e1_common_probe_ec112_owner_message("Stopp")
        self.assertEqual("question-or-discussion", question.message_class)
        self.assertEqual("stop-or-revoke", stop.message_class)
        self.assertTrue(stop.stop_or_revoke_requested)

    def test_incomplete_release_language_fails_closed(self) -> None:
        result = classify_e1_common_probe_ec112_owner_message(
            "Ich gebe einen Lauf frei"
        )
        self.assertEqual("ambiguous-or-incomplete", result.message_class)
        self.assertTrue(result.missing_release_requirements)
        self.assertFalse(result.execution_permitted)

    def test_complete_candidate_still_cannot_create_token(self) -> None:
        message = (
            "EC67-r2 genau einen Lauf maximal 3.208 Feldschritte nicht persistent "
            "kein Retry reale Ausfuehrung "
            f"gate:{'1' * 64} handoff:{S1_EC67_EC59_HANDOFF_DIGEST} "
            f"session:{'2' * 64}"
        )
        result = classify_e1_common_probe_ec112_owner_message(message)
        self.assertEqual("explicit-run-release-candidate", result.message_class)
        self.assertTrue(result.explicit_release_candidate_complete)
        self.assertTrue(result.external_bridge_validation_required)
        self.assertFalse(result.owner_scope_token_creation_permitted)
        self.assertFalse(result.execution_permitted)

    def test_wrong_handoff_keeps_candidate_incomplete(self) -> None:
        message = (
            "EC67-r2 genau einen Lauf maximal 3208 Feldschritte nicht-persistent "
            "kein Retry reale Ausfuehrung "
            f"gate:{'1' * 64} handoff:{'3' * 64} session:{'2' * 64}"
        )
        result = classify_e1_common_probe_ec112_owner_message(message)
        self.assertEqual("ambiguous-or-incomplete", result.message_class)
        self.assertIn("handoff-binding", result.missing_release_requirements)

    def test_classifier_is_deterministic_and_fail_closed(self) -> None:
        first = classify_e1_common_probe_ec112_owner_message("ok weiter")
        second = classify_e1_common_probe_ec112_owner_message("OK   WEITER")
        self.assertEqual(first.classification_digest, second.classification_digest)
        with self.assertRaises(E1CommonProbeEC112OwnerMessageClassifierError):
            replace(first, execution_permitted=True)

    def test_classifier_does_not_call_factory_coordinator_writer_or_decider(self) -> None:
        source = inspect.getsource(classify_e1_common_probe_ec112_owner_message)
        for forbidden in (
            "create_e1_common_probe_ec110_owner_scope_token(",
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "decide_common_probe_evidence(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
