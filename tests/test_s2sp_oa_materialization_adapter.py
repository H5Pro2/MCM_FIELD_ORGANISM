"""Focused neutral S2-SP adapter coverage; no OA corpus files are read."""

from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

import numpy as np

from tools import _s2ob_private_caller_binding as oa
from tools import _s2nl_private_half_profile_binding as half_profile
from tools import _s2sp_private_memory_compare as core
from tools import _s2sp_oa_materialization_adapter as adapter


class S2SPOAMaterializationAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="s2sp-oa-neutral-", dir=oa.ROOT / "reports")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        pcm = np.full(4800, 0.03125, dtype="<f4").tobytes()
        rgb = np.full((1080, 1920, 3), 24, dtype=np.uint8).tobytes()
        pcm_path, rgb_path = root / "input.pcm", root / "input.rgb"
        pcm_path.write_bytes(pcm); rgb_path.write_bytes(rgb)
        event = oa.Event(
            "adapter-event-01", 1, oa.AV, **oa.expected_times(1, oa.AV),
            pcm=oa.Payload("adapter-pcm-01", pcm_path.relative_to(oa.ROOT).as_posix(), hashlib.sha256(pcm).hexdigest(), len(pcm)),
            rgb=oa.Payload("adapter-rgb-01", rgb_path.relative_to(oa.ROOT).as_posix(), hashlib.sha256(rgb).hexdigest(), len(rgb)),
        )
        self.manifest = oa.build_manifest("adapter-neutral", (event,), "0" * 64)
        self.event = event

    def test_materialized_half_pair_is_preserved_once(self) -> None:
        materializer = oa.Materializer(self.manifest, track_reads=True)
        value = adapter.materialize_next(materializer, self.event)
        adapter.validate_half_profile_pair(value)
        self.assertEqual(materializer.counts, {"payloads": 2, "audio": 1, "nj": 1, "visual": 1, "materialized_events": 1})
        self.assertEqual(value.pair.plan.auditory_payload_digest, self.event.pcm.sha256)
        self.assertEqual(value.pair.plan.visual_payload_digest, self.event.rgb.sha256)

    def test_rejects_non_av_event_before_materialization(self) -> None:
        cue = oa.Event("adapter-cue-0001", 1, oa.V, **oa.expected_times(1, oa.V), pcm=None, rgb=self.event.rgb)
        manifest = oa.build_manifest("adapter-neutral-cue", (cue,), "0" * 64)
        with self.assertRaisesRegex(adapter.S2SPOAAdapterError, "OA_AV_EVENT_REQUIRED"):
            adapter.materialize_next(oa.Materializer(manifest), cue)

    def test_same_materialized_pair_advances_separate_arms(self) -> None:
        value = adapter.materialize_next(oa.Materializer(self.manifest), self.event)
        config = half_profile.build_config()
        historical = core.coordinator.initial_s2jv_composite_state(config)
        private = core.coordinator.initial_s2jv_composite_state(config)
        first = core.form(config=config, state=historical, pair=value.pair,
                          event_id=self.event.event_id, run_id="qual-historical")
        second = core.form(config=config, state=private, pair=value.pair,
                           event_id=self.event.event_id, run_id="qual-private",
                           ppb_update_mode=core.coordinator.tspm1.PPB_UPDATE_IDENTITY_PRESERVING)
        self.assertNotEqual(first.poststate.state_digest, historical.state_digest)
        self.assertNotEqual(second.poststate.state_digest, private.state_digest)
        self.assertEqual(first.tspm_transition_receipt.exposure_digest,
                         second.tspm_transition_receipt.exposure_digest)


if __name__ == "__main__":
    unittest.main()
