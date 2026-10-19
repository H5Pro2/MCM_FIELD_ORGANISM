"""Focused neutral coverage for the private S2-SP lifecycle connector."""

from __future__ import annotations

import unittest

from reports import run_s2sp_identity_lifecycle_once as runner
from tools import _s2jw_default_live_profile as profile_module
from tools import _s2sp_private_memory_compare as core


class S2SPIdentityLifecycleTests(unittest.TestCase):
    def test_bound_sequence_stays_within_the_private_lifecycle_limits(self) -> None:
        formations = [item for item in runner.SEQUENCE if item[1] == "FORMATION"]
        cues = [item for item in runner.SEQUENCE if item[1] == "CUE"]
        self.assertEqual((len(runner.SEQUENCE), len(formations), len(cues)), (16, 12, 4))
        self.assertEqual(formations[6][0], "e08")
        self.assertEqual(formations[-1][0], "e14")
        self.assertEqual(cues[-2][0], "e15")

    def test_shared_input_keeps_private_arms_independent_and_read_only(self) -> None:
        profile = profile_module.build_s2jw_default_live_profile()
        config = core.build_config()
        sources = core.Sources(profile)
        pair, values = sources.formation(event_id="neutral.life.e01", ordinal=0, cells=core.TARGET)
        states = {
            arm_id: core.coordinator.initial_s2jv_composite_state(config)
            for arm_id in runner.ARMS
        }
        for arm_id, mode in runner.ARMS.items():
            states[arm_id] = core.form(
                config=config,
                state=states[arm_id],
                pair=pair,
                event_id="neutral.life.e01",
                run_id=f"neutral.lifecycle.{arm_id.lower()}",
                ppb_update_mode=mode,
            ).poststate
        cue = sources.cue(ordinal=1, cells=core.TARGET)
        before = {arm_id: state.state_digest for arm_id, state in states.items()}
        for arm_id, state in states.items():
            scan = core.compare_state(state=state, cue_values=cue)
            self.assertEqual(scan["state_digest"], before[arm_id])
            self.assertEqual(state.state_digest, before[arm_id])
        self.assertEqual(sources.audio_analyses, 1)
        self.assertEqual(sources.visual_analyses, 2)
        self.assertEqual(len(values), 288)


if __name__ == "__main__":
    unittest.main()
