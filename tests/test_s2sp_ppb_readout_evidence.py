"""Focused neutral coverage for private S2-SP PPB readout evidence."""

from __future__ import annotations

import unittest

from tools import _s2sp_private_memory_compare as core


class S2SPPpbReadoutEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = core.build_config()
        self.profile = core.profile_module.build_s2jw_default_live_profile()
        self.sources = core.Sources(self.profile)

    def test_committed_visual_readout_is_exposed_and_bound(self) -> None:
        state = core.coordinator.initial_s2jv_composite_state(self.config)
        first, _ = self.sources.formation(event_id="n01", ordinal=0, cells=core.TARGET)
        first_result = core.form(config=self.config, state=state, pair=first, event_id="n01", run_id="qual-n01")
        self.assertIsNone(first_result.visual_ppb1_readout)

        second, _ = self.sources.formation(event_id="n02", ordinal=1, cells=core.TARGET)
        result = core.form(config=self.config, state=first_result.poststate, pair=second, event_id="n02", run_id="qual-n02")
        evidence = core.transition_evidence(prestate=first_result.poststate, result=result)
        readout = result.visual_ppb1_readout
        self.assertIsNotNone(readout)
        assert readout is not None
        self.assertEqual(evidence["visual_ppb_readout"]["event"], readout.event)
        self.assertEqual(evidence["visual_ppb_readout"]["slot_id"], readout.slot_id)
        self.assertEqual(evidence["visual_ppb_readout"]["input_digest"], readout.input_digest)
        self.assertEqual(evidence["visual_ppb_readout"]["prestate_digest"], readout.prestate_digest)
        self.assertEqual(evidence["visual_ppb_readout"]["poststate_digest"], readout.poststate_digest)
        self.assertEqual(evidence["visual_ppb_readout"]["readout_digest"], readout.digest())

    def test_noneligible_transition_exposes_no_visual_readout(self) -> None:
        state = core.coordinator.initial_s2jv_composite_state(self.config)
        pair, _ = self.sources.formation(event_id="n03", ordinal=0, cells=core.TARGET)
        result = core.form(config=self.config, state=state, pair=pair, event_id="n03", run_id="qual-n03")
        evidence = core.transition_evidence(prestate=state, result=result)
        self.assertEqual(evidence["consolidation_status"], "NOT_ELIGIBLE")
        self.assertIsNone(evidence["visual_ppb_readout"])


if __name__ == "__main__":
    unittest.main()
