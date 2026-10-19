from __future__ import annotations

import unittest

from tools import _s2jw_default_live_profile as profile_module
from tools import _s2sp_private_memory_compare as subject


class S2SPPrivateMemoryComparisonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = profile_module.build_s2jw_default_live_profile()
        self.config = subject.build_config()
        self.sources = subject.Sources(self.profile)
        self.state = subject.coordinator.initial_s2jv_composite_state(self.config)

    def _form(self, event: str, ordinal: int, cells):
        pair, visual_values = self.sources.formation(event_id=event, ordinal=ordinal, cells=cells)
        self.assertEqual(visual_values, pair.visual.timed_frame.frame.values)
        self.state = subject.form(config=self.config, state=self.state, pair=pair, event_id=event, run_id="s2sp-neutral") .poststate

    def test_actual_b4_and_fast_candidates_keep_a_shift_hint_read_only(self) -> None:
        self._form("n01", 0, subject.TARGET)
        cue = self.sources.cue(ordinal=1, cells=subject.SHIFTED)
        before = self.state.state_digest
        result = subject.compare_state(state=self.state, cue_values=cue)
        self.assertEqual(before, self.state.state_digest)
        by_bank = {row["bank"]: row for row in result["banks"]}
        for bank in ("B4", "FAST"):
            self.assertEqual(by_bank[bank]["exact_baseline_candidate_ids"], [])
            self.assertEqual(by_bank[bank]["hint_status"], "HINT_SINGLE")
        self.assertEqual(by_bank["VISUAL_SLOW"]["hint_status"], "HINT_NOT_APPLICABLE")

    def test_foreign_interior_structure_is_not_a_private_hint(self) -> None:
        self._form("n02", 0, subject.TARGET)
        cue = self.sources.cue(ordinal=1, cells=subject.FOREIGN)
        result = subject.compare_state(state=self.state, cue_values=cue)
        self.assertTrue(all(row["hint_status"] == "HINT_NOT_APPLICABLE" for row in result["banks"]))

    def test_b4_replacement_does_not_preserve_the_original_candidate_digest(self) -> None:
        self._form("n03", 0, subject.TARGET)
        original = {candidate_id for candidate_id, _ in subject._candidate_rows(self.state)["B4"]}
        for ordinal in range(1, 10):
            self._form(f"n{ordinal + 3:02d}", ordinal, subject.BOUNDARY)
        final = {candidate_id for candidate_id, _ in subject._candidate_rows(self.state)["B4"]}
        self.assertTrue(original)
        self.assertTrue(original.isdisjoint(final))

    def test_transition_evidence_is_derived_from_the_same_atomic_result(self) -> None:
        pair, _ = self.sources.formation(event_id="n13", ordinal=0, cells=subject.TARGET)
        result = subject.form(config=self.config, state=self.state, pair=pair, event_id="n13", run_id="s2sp-neutral")
        evidence = subject.transition_evidence(prestate=self.state, result=result)
        self.assertEqual(evidence["formation_generation_before"], 0)
        self.assertEqual(evidence["formation_generation_after"], 1)
        self.assertEqual(evidence["native_transition_receipt_digest"], result.tspm_transition_receipt.receipt_digest)
        self.assertEqual(evidence["fast_generation"], None)
        self.assertEqual(evidence["fast_generation_status"], "NOT_AVAILABLE_IN_NATIVE_SLOT")


if __name__ == "__main__":
    unittest.main()
