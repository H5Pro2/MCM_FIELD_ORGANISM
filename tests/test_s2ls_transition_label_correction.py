"""Neutral qualification of the S2-LS saturated-support event labels."""

from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace
import unittest

from mcm_field_organism import _ppb1_reference as ppb1
from tools import _s2ls_private_corpus_stream_runner as runner
from tools import _s2ls_private_corpus_stream_verifier as verifier


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_RESULT = ROOT / "reports" / "s2ls" / "s2ls-real-presealed-av-corpus-20260904-01" / "result.json"
HISTORICAL_RESULT_SHA256 = "2be76afc69f7d587cd1098895915c905d8d5349bb6795e3dde903f71744d4fc1"


def _slot(slot_id: str, values: tuple[float, ...], support: int, step: int) -> ppb1.PPB1PrototypeSlot:
    return ppb1.PPB1PrototypeSlot(slot_id, True, values, support, step)


class S2LSTransitionLabelCorrectionTests(unittest.TestCase):
    def test_01_saturated_ppb_support_remains_matched(self) -> None:
        before = _slot("neutral.slot.000", (0.25, 0.5), 3, 3)
        after = _slot("neutral.slot.000", (0.26, 0.5), 3, 4)
        result = runner._ppb_transition(
            SimpleNamespace(slots=(before,)),
            SimpleNamespace(slots=(after,)),
            (0.45, 0.5),
            0.1,
        )
        self.assertEqual("MATCHED", result["event"])
        self.assertLessEqual(result["source_distance"], result["match_threshold"])

    def test_02_actual_ppb_slot_replacement_remains_replaced(self) -> None:
        before = _slot("neutral.slot.000", (0.1, 0.1), 3, 3)
        after = _slot("neutral.slot.000", (0.9, 0.9), 1, 4)
        result = runner._ppb_transition(
            SimpleNamespace(slots=(before,)),
            SimpleNamespace(slots=(after,)),
            (0.9, 0.9),
            0.1,
        )
        self.assertEqual("REPLACED", result["event"])
        self.assertGreater(result["source_distance"], result["match_threshold"])

    def test_03_verifier_accepts_saturated_ppb_match(self) -> None:
        record = runner.neutral_qualification_record(ROOT)
        transition = record["execution"]["events"][0]["formation_transition"]
        ppb = runner._ppb_transition(
            SimpleNamespace(slots=(_slot("neutral.slot.000", (0.25, 0.5), 3, 3),)),
            SimpleNamespace(slots=(_slot("neutral.slot.000", (0.26, 0.5), 3, 4),)),
            (0.45, 0.5),
            0.1,
        )
        transition["auditory_ppb"] = ppb
        payload = dict(transition)
        payload.pop("formation_transition_digest", None)
        transition["formation_transition_digest"] = runner._digest(payload)
        verifier._verify_transition(transition, None, transition["poststate_digest"])

    def test_04_verifier_rejects_saturated_ppb_replaced_label(self) -> None:
        record = runner.neutral_qualification_record(ROOT)
        transition = record["execution"]["events"][0]["formation_transition"]
        ppb = runner._ppb_transition(
            SimpleNamespace(slots=(_slot("neutral.slot.000", (0.25, 0.5), 3, 3),)),
            SimpleNamespace(slots=(_slot("neutral.slot.000", (0.26, 0.5), 3, 4),)),
            (0.45, 0.5),
            0.1,
        )
        ppb["event"] = "REPLACED"
        ppb_payload = dict(ppb)
        ppb_payload.pop("transition_digest", None)
        ppb["transition_digest"] = runner._digest(ppb_payload)
        transition["auditory_ppb"] = ppb
        payload = dict(transition)
        payload.pop("formation_transition_digest", None)
        transition["formation_transition_digest"] = runner._digest(payload)
        with self.assertRaises(verifier.S2LSVerificationError):
            verifier._verify_transition(transition, None, transition["poststate_digest"])

    def test_05_fast_and_rule_is_checked_independently(self) -> None:
        record = runner.neutral_qualification_record(ROOT)
        transition = record["execution"]["events"][0]["formation_transition"]
        fast = transition["fast"]
        fast["pre_slot"] = dict(fast["post_slot"])
        fast["event"] = "REPLACED"
        fast["auditory_source_distance"] = 0.19
        fast["visual_source_distance"] = 0.21
        fast_payload = dict(fast)
        fast_payload.pop("transition_digest", None)
        fast["transition_digest"] = runner._digest(fast_payload)
        payload = dict(transition)
        payload.pop("formation_transition_digest", None)
        transition["formation_transition_digest"] = runner._digest(payload)
        verifier._verify_transition(transition, None, transition["poststate_digest"])
        fast["visual_source_distance"] = 0.2
        fast_payload = dict(fast)
        fast_payload.pop("transition_digest", None)
        fast["transition_digest"] = runner._digest(fast_payload)
        payload = dict(transition)
        payload.pop("formation_transition_digest", None)
        transition["formation_transition_digest"] = runner._digest(payload)
        with self.assertRaises(verifier.S2LSVerificationError):
            verifier._verify_transition(transition, None, transition["poststate_digest"])

    def test_06_historical_result_and_main_gate_remain_unchanged(self) -> None:
        self.assertEqual(HISTORICAL_RESULT_SHA256, hashlib.sha256(HISTORICAL_RESULT.read_bytes()).hexdigest())
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)


if __name__ == "__main__":
    unittest.main()
