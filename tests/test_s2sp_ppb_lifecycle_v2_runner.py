"""Focused neutral qualification for the bound S2-SP V2 runner shell."""

from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
import tempfile
import unittest

import numpy as np

from tools import _s2nl_private_half_profile_binding as half_profile
from tools import _s2ob_private_caller_binding as oa
from tools import _s2sp_oa_materialization_adapter as adapter
from tools import _s2sp_ppb_lifecycle_v2_runner as runner


def _payload(root: Path, name: str, suffix: str, raw: bytes) -> oa.Payload:
    path = root / f"{name}.{suffix}"
    path.write_bytes(raw)
    return oa.Payload(name, path.relative_to(oa.ROOT).as_posix(), hashlib.sha256(raw).hexdigest(), len(raw))


class S2SPPpbLifecycleV2RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="s2sp-v2-runner-neutral-", dir=oa.ROOT / "reports")
        root = Path(cls.temp.name)
        events = []
        for ordinal in range(1, 21):
            cue = ordinal in runner.CUE_ORDINALS
            image = np.full((1080, 1920, 3), 48 + ordinal, dtype=np.uint8)
            if cue:
                cells = image.reshape(8, 135, 12, 160, 3)
                for index in range(32, 288):
                    cell, channel = divmod(index, 3); row, column = divmod(cell, 12)
                    cells[row, :, column, :, channel] = 0
            rgb = _payload(root, f"v2r-rgb-{ordinal:02d}", "rgb", image.tobytes())
            if cue:
                events.append(oa.Event(f"v2r-event-{ordinal:02d}", ordinal, oa.V, **oa.expected_times(ordinal, oa.V), pcm=None, rgb=rgb))
            else:
                pcm = _payload(root, f"v2r-pcm-{ordinal:02d}", "pcm", np.full(4800, 0.03125, dtype="<f4").tobytes())
                events.append(oa.Event(f"v2r-event-{ordinal:02d}", ordinal, oa.AV, **oa.expected_times(ordinal, oa.AV), pcm=pcm, rgb=rgb))
        manifest = oa.build_manifest("s2sp-v2-runner-neutral", tuple(events), "2" * 64)
        materializer = oa.Materializer(manifest)
        cls.items = []
        cls.native_inputs = {}
        for event in events:
            item = materializer.next(event)
            cls.native_inputs[event.event_id] = item
            if event.kind == oa.V:
                cls.items.append(("CUE", item))
            else:
                cls.items.append(("FORMATION", adapter.bind_materialized_input(
                    item, event_id=event.event_id, ordinal=event.ordinal, pcm_digest=event.pcm.sha256, rgb_digest=event.rgb.sha256)))
        cls.counts = {"payloads": 38, "audio": 18, "visual": 20, "nj": 18, "materialized_events": 20}
        cls.source = {"execution_digest": "0" * 64, "generator_identity": {"neutral": True}}

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_complete_neutral_runner_record_reaches_verification_and_evaluation(self) -> None:
        record, proof, evaluation = runner.record_materialized_once(self.items, self.counts, self.source, "s2sp-v2-runner-neutral")
        self.assertEqual((record["status"], proof["status"]), ("RECORDING_COMPLETE", "VERIFIED"))
        self.assertEqual(set(evaluation), set(runner.ARMS))

    def test_rejects_incomplete_envelope_before_memory_advance(self) -> None:
        with self.assertRaisesRegex(runner.S2SPV2Error, "V2_MATERIALIZED_ENVELOPE_INVALID"):
            runner.record_materialized_once(self.items[:-1], self.counts, self.source, "s2sp-v2-runner-short")

    def test_rejects_wrong_kind_at_bound_cue_position(self) -> None:
        altered = list(self.items)
        altered[13] = ("FORMATION", altered[13][1])
        with self.assertRaisesRegex(runner.S2SPV2Error, "V2_PAIR_INVALID"):
            runner.record_materialized_once(altered, self.counts, self.source, "s2sp-v2-runner-kind")

    def test_rejects_invalid_native_field_binding(self) -> None:
        native = self.native_inputs["v2r-event-01"]
        malformed = oa.Input(replace(native.event, field_payload="not-a-field-input"), native.nj_json)
        with self.assertRaisesRegex(adapter.S2SPOAAdapterError, "FIELD_INPUT_TYPE_INVALID"):
            adapter.bind_materialized_input(malformed, event_id=native.event.event_id, ordinal=1,
                                             pcm_digest=native.event.operation_payload.plan.auditory_payload_digest,
                                             rgb_digest=native.event.operation_payload.plan.visual_payload_digest)


if __name__ == "__main__":
    unittest.main()
