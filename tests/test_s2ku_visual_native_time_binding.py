"""Focused neutral qualification of the corrected S2-KU visual time binding."""

from __future__ import annotations

from dataclasses import replace
import unittest

from tools import _s2kq_private_direct_slot_scan_baseline as baseline
from tools import _s2kq_private_partial_cue_retrieval_336 as subject
from tools import _s2ks_real_partial_cue_fixtures as fixtures
from tests.test_s2kq_private_partial_cue_retrieval_336 import (
    MATCH_A,
    _config,
    _semantic,
    _state,
)


def _cue(
    config,
    *,
    visual_clock_id: str = "video.frame",
    visual_start: int = 1_000,
    visual_end: int = 1_100,
):
    return subject.build_masked_memory_cue_336(
        source_digest="7" * 64,
        config_digest=config.config_digest,
        field_clock_id="shared.field",
        window_start_tick=1_000_000,
        window_end_tick=1_100_000,
        visual_source_clock_id=visual_clock_id,
        visual_window_start_tick=visual_start,
        visual_window_end_tick=visual_end,
        values=(0.0,) * 32 + (None,) * 256,
    )


def _separate_clock_state(config):
    return _state(
        config,
        b4=(MATCH_A,),
        fast=(MATCH_A,),
        auditory_clock_id="audio.sample",
        visual_clock_id="video.frame",
    )


class S2KUVisualNativeTimeBindingQualification(unittest.TestCase):
    def test_01_separate_native_clocks_are_valid_and_read_only(self) -> None:
        config = _config()
        state = _separate_clock_state(config)
        cue = _cue(config)
        before = (state.state_digest, state.b4_state, state.tspm_state, cue)
        primary = subject.form_partial_cue_retrieval_336(config=config, state=state, cue=cue)
        direct = baseline.form_direct_partial_cue_slot_scan_baseline_336(config=config, state=state, cue=cue)
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual("ADMIT_SINGLE_CONTEXT", primary.decision)
        self.assertEqual("A_RECENT", primary.hypothesis.area)
        self.assertEqual(before, (state.state_digest, state.b4_state, state.tspm_state, cue))
        self.assertEqual(primary.prestate_digest, primary.poststate_digest)
        self.assertNotEqual(cue.field_clock_id, cue.visual_source_clock_id)

    def test_02_wrong_native_visual_clock_fails_closed_in_both_arms(self) -> None:
        config = _config()
        state = _separate_clock_state(config)
        cue = _cue(config, visual_clock_id="foreign.video")
        for function in (subject.form_partial_cue_retrieval_336, baseline.form_direct_partial_cue_slot_scan_baseline_336):
            with self.subTest(function=function.__module__), self.assertRaises(subject.S2KQError):
                function(config=config, state=state, cue=cue)

    def test_03_stale_native_visual_window_fails_closed_in_both_arms(self) -> None:
        config = _config()
        state = _separate_clock_state(config)
        cue = _cue(config, visual_start=899, visual_end=900)
        for function in (subject.form_partial_cue_retrieval_336, baseline.form_direct_partial_cue_slot_scan_baseline_336):
            with self.subTest(function=function.__module__), self.assertRaises(subject.S2KQError):
                function(config=config, state=state, cue=cue)

    def test_04_digest_inconsistent_native_time_mutation_fails_closed(self) -> None:
        config = _config()
        state = _separate_clock_state(config)
        cue = replace(_cue(config), visual_window_start_tick=1_001)
        for function in (subject.form_partial_cue_retrieval_336, baseline.form_direct_partial_cue_slot_scan_baseline_336):
            with self.subTest(function=function.__module__), self.assertRaises(subject.S2KQError):
                function(config=config, state=state, cue=cue)

    def test_05_real_occluded_frame_supplies_native_visual_binding(self) -> None:
        config = _config()
        state = _separate_clock_state(config)
        cue, receipt = fixtures.materialize_masked_cue(
            profile=config.profile,
            history_id="neutral",
            cue_id="cue-native-time",
            ordinal=400,
            visible_recipe_id="S0",
            config_digest=config.config_digest,
        )
        self.assertEqual("video.frame", cue.visual_source_clock_id)
        self.assertEqual((1_202, 1_203), (cue.visual_window_start_tick, cue.visual_window_end_tick))
        self.assertEqual(cue.visual_source_clock_id, receipt.visual_source_clock_id)
        self.assertEqual(cue.visual_window_start_tick, receipt.visual_window_start_tick)
        self.assertEqual(cue.visual_window_end_tick, receipt.visual_window_end_tick)
        self.assertNotEqual(cue.field_clock_id, cue.visual_source_clock_id)
        primary = subject.form_partial_cue_retrieval_336(config=config, state=state, cue=cue)
        direct = baseline.form_direct_partial_cue_slot_scan_baseline_336(config=config, state=state, cue=cue)
        self.assertEqual(_semantic(primary), _semantic(direct))
        self.assertEqual(state.state_digest, primary.prestate_digest)
        self.assertEqual(state.state_digest, primary.poststate_digest)


if __name__ == "__main__":
    unittest.main()
