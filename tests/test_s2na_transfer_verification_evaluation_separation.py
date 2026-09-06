"""Neutral qualification of S2-MT verification/evaluation separation."""

from __future__ import annotations

import hashlib
import unittest

from tools import _s2mt_private_transfer_runtime_verifier as verifier


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _hypothesis(modality: str) -> dict[str, object]:
    auditory = modality == "AUDITORY"
    payload = {
        "area": "B_STABLE_AUDITORY" if auditory else "B_STABLE",
        "masked_bands" if auditory else "masked_positions": list(
            range(24 if auditory else 256)
        ),
        "proposed_values": [0.0] * (24 if auditory else 256),
    }
    return {
        "modality": modality,
        "payload": payload,
        "hypothesis_digest": verifier._digest(payload),
    }


def _early_observation(ordinal: int, recipe_id: str) -> dict[str, object]:
    return {
        "b4": [
            {
                "formation_index": ordinal,
                "values_digest": _sha(f"{recipe_id}-av"),
            }
        ],
        "fast": [
            {
                "last_selected_step": ordinal,
                "auditory_values_digest": _sha(f"{recipe_id}-auditory"),
                "visual_values_digest": _sha(f"{recipe_id}-visual"),
            }
        ],
        "auditory_slow": [],
        "visual_slow": [],
    }


def _final_observation() -> dict[str, object]:
    return {
        "b4": [{"formation_index": 20, "values_digest": _sha("final-av")}],
        "fast": [
            {
                "last_selected_step": 20,
                "auditory_values_digest": _sha("final-auditory"),
                "visual_values_digest": _sha("final-visual"),
            }
        ],
        "auditory_slow": [{"support_count": value} for value in (2, 3, 3)],
        "visual_slow": [{"support_count": value} for value in (2, 3, 3)],
    }


def _evaluation_fixture() -> tuple[list[dict[str, object]], dict[str, object], dict[str, object]]:
    final_memory_digest = _sha("final-memory")
    events: list[dict[str, object]] = []
    for ordinal in range(1, 21):
        recipe_id = f"n{ordinal - 1:02d}"
        observation = (
            _early_observation(ordinal, recipe_id)
            if ordinal <= 3
            else _final_observation()
        )
        if ordinal == 20:
            observation = _final_observation()
        events.append(
            {
                "ordinal": ordinal,
                "recipe_id": recipe_id,
                "memory_observation": observation,
                "post_snapshot": {
                    "memory_state_digest": (
                        final_memory_digest if ordinal == 20 else _sha(f"memory-{ordinal}")
                    )
                },
            }
        )

    for cue_index in range(8):
        modality = "AUDITORY" if cue_index % 2 == 0 else "VISUAL"
        expected_positive = cue_index < 4
        observed_hypothesis = (
            None if cue_index == 0 or not expected_positive else _hypothesis(modality)
        )
        events.append(
            {
                "runtime_step": {
                    "hypothesis": observed_hypothesis,
                    "payload": {
                        "context_status": (
                            "ABSTAIN_NO_CONTEXT"
                            if observed_hypothesis is None
                            else "CONTEXT_CANDIDATE_AVAILABLE"
                        )
                    },
                },
                "post_snapshot": {"memory_state_digest": final_memory_digest},
            }
        )

    final_open = {
        "processed_event_count": 28,
        "field_attempt_count": 28,
        "memory_formation_attempt_count": 20,
        "scan_attempt_count": 16,
        "status": "OPEN",
    }
    return events, final_open, {"status": "CLOSED"}


class S2NAVerificationEvaluationSeparationTests(unittest.TestCase):
    def test_expected_hypothesis_observed_abstention_is_technical_but_falsified(self) -> None:
        verifier._verify_hypothesis(None, "AUDITORY", "ABSTAIN_NO_CONTEXT")
        events, final_open, closed = _evaluation_fixture()
        evaluation = verifier._expected_evaluation(events, final_open, closed)
        self.assertEqual("S2MT_FUNCTION_FALSIFIED", evaluation["status"])
        self.assertFalse(evaluation["cue_decisions"][0]["hypothesis_present"])

    def test_valid_hypotheses_and_all_abstentions_are_structurally_accepted(self) -> None:
        verifier._verify_hypothesis(
            _hypothesis("AUDITORY"),
            "AUDITORY",
            "CONTEXT_CANDIDATE_AVAILABLE",
        )
        verifier._verify_hypothesis(
            _hypothesis("VISUAL"),
            "VISUAL",
            "CONTEXT_CANDIDATE_AVAILABLE",
        )
        for status in verifier.ABSTENTION_STATUSES:
            verifier._verify_hypothesis(None, "AUDITORY", status)
            verifier._verify_hypothesis(None, "VISUAL", status)

    def test_hypothesis_status_and_digest_contradictions_fail_closed(self) -> None:
        auditory = _hypothesis("AUDITORY")
        mutations = (
            (None, "AUDITORY", "CONTEXT_CANDIDATE_AVAILABLE"),
            (auditory, "AUDITORY", "ABSTAIN_NO_CONTEXT"),
            (auditory, "VISUAL", "CONTEXT_CANDIDATE_AVAILABLE"),
            ({**auditory, "hypothesis_digest": _sha("changed")}, "AUDITORY", "CONTEXT_CANDIDATE_AVAILABLE"),
            (None, "AUDITORY", "NOT_REQUESTED"),
            (None, "AUDITORY", "SCAN_FAILED"),
        )
        for value, modality, status in mutations:
            with self.subTest(modality=modality, status=status):
                with self.assertRaises(verifier.S2MTVerificationError):
                    verifier._verify_hypothesis(value, modality, status)


if __name__ == "__main__":
    unittest.main()
