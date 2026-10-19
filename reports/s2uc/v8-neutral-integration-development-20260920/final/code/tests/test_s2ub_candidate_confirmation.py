import unittest

from tools import _s2tu_retained_trace as tu
from tools import _s2ub_candidate_confirmation as ub
from tools import _s2ub_candidate_verification as verify


P = "a" * 64


def frames(values, owner, segment, start):
    return tuple(tu.Frame((float(value),) * 48, P, owner, segment, start + index) for index, value in enumerate(values))


class CandidateConfirmationTests(unittest.TestCase):
    def submit(self, arm, values, segment, start):
        group = frames(values, arm.owner if hasattr(arm, "owner") else arm.store.owner, segment, start)
        for frame in group:
            arm.form(frame)
            self.assertLessEqual(arm.resources()["trace_frames"], ub.TRACE_STORAGE_LIMIT)
        return arm.close_segment(segment), group

    def hint(self, arm, values, segment, start):
        owner = arm.owner if hasattr(arm, "owner") else arm.store.owner
        first, second = frames(values, owner, segment, start)
        self.assertIsNone(arm.hint(first))
        return arm.hint(second)

    def test_immediate_arm_uses_tw_confirmation_and_two_retained_slots(self):
        arm = ub.ImmediateTwArm(P, "tw")
        self.assertEqual(self.submit(arm, (1, 2, 3, 4), "a1", 1)[0]["action"], "TRACE_RETAINED")
        self.assertEqual(self.submit(arm, (1, 2, 3, 4), "a2", 5)[0], {"action": "TRACE_CONFIRMED", "generation": 1, "evicted": None})
        self.submit(arm, (5, 6, 7, 8), "b", 9)
        receipt, _ = self.submit(arm, (9, 10, 11, 12), "c", 13)
        self.assertEqual((receipt["evicted"], arm.inventory), (1, (2, 3)))
        self.assertLessEqual(arm.resources()["trace_frames"], ub.TRACE_STORAGE_LIMIT)

    def test_confirmed_trace_survives_one_off_pressure_while_candidate_is_lost(self):
        immediate = ub.ImmediateTwArm(P, "tw")
        candidate = ub.CandidateConfirmationArm(P, "candidate")
        for arm in (immediate, candidate):
            self.submit(arm, (1, 2, 3, 4), "a1", 1)
            self.submit(arm, (1, 2, 3, 4), "a2", 5)
            self.submit(arm, (5, 6, 7, 8), "b", 9)
            self.submit(arm, (9, 10, 11, 12), "c", 13)
        self.assertEqual(self.hint(immediate, (1, 2), "h-a", 17)["decision"], "ABSTAIN_NO_RETAINED_TRACE")
        self.assertEqual(self.hint(candidate, (1, 2), "h-a", 17)["decision"], "TRACE_MATCH")
        self.assertEqual(self.hint(immediate, (5, 6), "h-b", 19)["decision"], "TRACE_MATCH")
        self.assertEqual(self.hint(candidate, (5, 6), "h-b", 19)["decision"], "ABSTAIN_NO_RETAINED_TRACE")
        self.assertLessEqual(candidate.resources()["trace_frames"], ub.TRACE_STORAGE_LIMIT)

    def test_candidate_is_lost_when_interruption_precedes_second_exact_observation(self):
        arm = ub.CandidateConfirmationArm(P, "candidate")
        self.assertEqual(self.submit(arm, (1, 2, 3, 4), "a1", 1)[0]["action"], "TRACE_CANDIDATE_CREATED")
        self.assertEqual(self.submit(arm, (5, 6, 7, 8), "b", 5)[0]["action"], "TRACE_CANDIDATE_REPLACED")
        self.assertEqual(self.submit(arm, (1, 2, 3, 4), "a2", 9)[0]["action"], "TRACE_CANDIDATE_REPLACED")
        self.assertEqual((arm.inventory, arm.candidate_generation), ((), 3))

    def test_second_confirmed_trace_replaces_only_retained_generation(self):
        arm = ub.CandidateConfirmationArm(P, "candidate")
        self.submit(arm, (1, 2, 3, 4), "a1", 1)
        self.assertEqual(self.submit(arm, (1, 2, 3, 4), "a2", 5)[0]["action"], "TRACE_PROMOTED")
        self.submit(arm, (5, 6, 7, 8), "b1", 9)
        receipt, _ = self.submit(arm, (5, 6, 7, 8), "b2", 13)
        self.assertEqual(receipt, {"action": "TRACE_PROMOTED", "generation": 2, "candidate_generation": 2, "evicted": 1})
        self.assertEqual((arm.inventory, arm.candidate_generation), ((2,), None))

    def test_partial_reverse_and_overlap_do_not_promote(self):
        arm = ub.CandidateConfirmationArm(P, "candidate")
        self.submit(arm, (1, 2, 3, 4), "a", 1)
        self.assertEqual(self.submit(arm, (4, 3, 2, 1), "reverse", 5)[0]["action"], "TRACE_CANDIDATE_REPLACED")
        self.assertEqual(self.submit(arm, (1, 2, 3, 5), "partial", 9)[0]["action"], "TRACE_CANDIDATE_REPLACED")
        overlap = frames((1, 2, 3, 5), "candidate", "overlap", 9)
        for frame in overlap:
            arm.form(frame)
        self.assertEqual(arm.close_segment("overlap")["action"], "TRACE_CANDIDATE_OVERLAP_NOT_CONFIRMED")
        self.assertEqual((arm.inventory, arm.candidate_generation), ((), 3))

    def test_hints_read_only_and_never_read_candidate(self):
        arm = ub.CandidateConfirmationArm(P, "candidate")
        self.submit(arm, (1, 2, 3, 4), "a1", 1)
        self.submit(arm, (1, 2, 3, 4), "a2", 5)
        self.submit(arm, (5, 6, 7, 8), "b", 9)
        before = (arm.inventory, arm.candidate_generation, arm.resources())
        self.assertEqual(self.hint(arm, (1, 2), "h-a", 13)["decision"], "TRACE_MATCH")
        self.assertEqual(self.hint(arm, (5, 6), "h-b", 15)["decision"], "ABSTAIN_NO_RETAINED_TRACE")
        self.assertEqual((arm.inventory, arm.candidate_generation, arm.resources()), before)

    def test_retained_exact_confirmation_leaves_other_candidate_unchanged(self):
        arm = ub.CandidateConfirmationArm(P, "candidate")
        self.submit(arm, (1, 2, 3, 4), "a1", 1)
        self.submit(arm, (1, 2, 3, 4), "a2", 5)
        self.submit(arm, (5, 6, 7, 8), "b", 9)
        before = (arm.inventory, arm.candidate_generation)
        receipt, _ = self.submit(arm, (1, 2, 3, 4), "a3", 13)
        self.assertEqual(receipt, {"action": "TRACE_CONFIRMED", "generation": 1, "candidate_generation": 2, "evicted": None})
        self.assertEqual((arm.inventory, arm.candidate_generation), before)

    def test_independent_replay_matches_every_receipt_for_documented_cases(self):
        cases = {
            "gain-and-loss": (((1, 2, 3, 4), "a1", 1), ((1, 2, 3, 4), "a2", 5), ((5, 6, 7, 8), "b", 9), ((9, 10, 11, 12), "c", 13)),
            "interruption": (((1, 2, 3, 4), "a1", 1), ((5, 6, 7, 8), "b", 5), ((1, 2, 3, 4), "a2", 9)),
            "second-promotion": (((1, 2, 3, 4), "a1", 1), ((1, 2, 3, 4), "a2", 5), ((5, 6, 7, 8), "b1", 9), ((5, 6, 7, 8), "b2", 13)),
            "partial-and-reverse": (((1, 2, 3, 4), "a", 1), ((4, 3, 2, 1), "reverse", 5), ((1, 2, 3, 5), "partial", 9)),
            "overlap": (((1, 2, 3, 4), "a", 1), ((1, 2, 3, 4), "overlap", 1)),
        }
        for name, rows in cases.items():
            with self.subTest(name=name):
                arm = ub.CandidateConfirmationArm(P, "candidate")
                receipts, groups = [], []
                for values, segment, start in rows:
                    receipt, group = self.submit(arm, values, segment, start)
                    receipts.append(receipt); groups.append(group)
                direct = verify.replay(tuple(groups))
                self.assertEqual(receipts, direct["transitions"])
                self.assertEqual((arm.inventory, arm.candidate_generation), (direct["inventory"], direct["candidate_generation"]))
                self.assertEqual(arm.evidence()["retained"], direct["retained"])
                self.assertEqual(arm.evidence()["candidate"], direct["candidate"])
                corrupted = dict(receipts[-1]); corrupted["action"] = "CORRUPTED"
                with self.assertRaisesRegex(ValueError, "TRANSITION_MISMATCH"):
                    verify.require_equal(corrupted, direct["transitions"][-1], "TRANSITION_MISMATCH")

    def test_independent_hint_replay_covers_offsets_ambiguity_and_candidate_exclusion(self):
        arm = ub.CandidateConfirmationArm(P, "candidate")
        self.submit(arm, (1, 2, 1, 2), "a1", 1)
        self.submit(arm, (1, 2, 1, 2), "a2", 5)
        self.submit(arm, (5, 6, 7, 8), "candidate", 9)
        before = arm.evidence()
        hint_frames = frames((1, 2), "candidate", "h-a", 13)
        self.assertIsNone(arm.hint(hint_frames[0]))
        observed = arm.hint(hint_frames[1])
        direct = verify.hint(before["retained"], hint_frames)
        self.assertEqual(observed, direct)
        self.assertEqual(observed["decision"], "ABSTAIN_AMBIGUOUS_RETAINED_TRACE")
        candidate_hint = frames((5, 6), "candidate", "h-b", 15)
        self.assertIsNone(arm.hint(candidate_hint[0]))
        observed_candidate = arm.hint(candidate_hint[1])
        direct_candidate = verify.hint(before["retained"], candidate_hint)
        self.assertEqual(observed_candidate, direct_candidate)
        self.assertEqual(observed_candidate["decision"], "ABSTAIN_NO_RETAINED_TRACE")
        corrupted = dict(observed); corrupted["decision"] = "TRACE_MATCH"
        with self.assertRaisesRegex(ValueError, "HINT_MISMATCH"):
            verify.require_equal(corrupted, direct, "HINT_MISMATCH")
        self.assertEqual(arm.evidence(), before)

    def test_frame_budget_is_reached_during_formation_and_hints_are_separate(self):
        for arm in (ub.ImmediateTwArm(P, "tw"), ub.CandidateConfirmationArm(P, "candidate")):
            with self.subTest(arm=type(arm).__name__):
                self.submit(arm, (1, 2, 3, 4), "a1", 1)
                self.submit(arm, (1, 2, 3, 4), "a2", 5)
                self.submit(arm, (5, 6, 7, 8), "b", 9)
                group = frames((9, 10, 11, 12), arm.owner if hasattr(arm, "owner") else arm.store.owner, "c", 13)
                for count, frame in enumerate(group, start=1):
                    arm.form(frame)
                    self.assertEqual(arm.resources()["trace_frames"], 8 + count)
                    self.assertEqual(arm.resources()["hint_frames"], 0)
                arm.close_segment("c")
                hint_frame = frames((1, 2), arm.owner if hasattr(arm, "owner") else arm.store.owner, "h", 17)[0]
                arm.hint(hint_frame)
                self.assertEqual(arm.resources()["hint_frames"], 1)
                self.assertLessEqual(arm.resources()["trace_frames"], ub.TRACE_STORAGE_LIMIT)

    def test_owner_close_rejects_new_inputs_without_state_change_in_both_arms(self):
        for arm in (ub.ImmediateTwArm(P, "tw"), ub.CandidateConfirmationArm(P, "candidate")):
            with self.subTest(arm=type(arm).__name__):
                arm.close_owner()
                before = arm.evidence()
                owner = arm.owner if hasattr(arm, "owner") else arm.store.owner
                with self.assertRaisesRegex(tu.S2TUError, "FRAME_SCOPE_INVALID"):
                    arm.form(frames((1, 2, 3, 4), owner, "after", 1)[0])
                self.assertEqual(arm.evidence(), before)
                with self.assertRaisesRegex(tu.S2TUError, "FRAME_SCOPE_INVALID"):
                    arm.hint(frames((1, 2), owner, "after-hint", 2)[0])
                self.assertEqual(arm.evidence(), before)
