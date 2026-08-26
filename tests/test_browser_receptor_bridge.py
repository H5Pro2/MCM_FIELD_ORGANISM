from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import math
from pathlib import Path
import unittest

import cv2
import numpy as np

from mcm_field_organism import (
    BrowserReceptorBridge,
    BrowserReceptorBridgeConfig,
    BrowserReceptorBridgeError,
    BrowserWorldContract,
    BrowserWorldPhase,
    NeutralLocalFieldSubstrateConfig,
    advance_audio_video_receptor_sequences,
    browser_receptor_bridge_public_roles,
)
from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_video_path import (
    LocalChannelGridReceptor,
    VisualGridConfig,
)
from mcm_field_organism.log_spectral_receptor import (
    LogSpectralConfig,
    LogSpectralReceptor,
)


def world_contract() -> BrowserWorldContract:
    return BrowserWorldContract(
        contract_id="browser.world.bridge.test.v1",
        startup_frame_count=1,
        start_lead_ns=1,
        movement_cycles=1,
        tone_frequency_hz=100.0,
        phases=(
            BrowserWorldPhase("rest.before", 100_000_000, "static", 0.0),
            BrowserWorldPhase("change", 100_000_000, "moving", 0.2),
            BrowserWorldPhase("rest.after", 100_000_000, "static", 0.0),
        ),
    )


def components():
    visual = LocalChannelGridReceptor(
        VisualGridConfig(
            source_width=12,
            source_height=8,
            grid_columns=2,
            grid_rows=2,
            frames_per_second=10.0,
        )
    )
    auditory = BroadbandHearingPath(
        LogSpectralReceptor(
            LogSpectralConfig(
                sample_rate=1000,
                window_size=100,
                hop_size=20,
                min_frequency=10.0,
                max_frequency=400.0,
                band_count=4,
            )
        )
    )
    return visual, auditory


def png_payload(value: int) -> bytes:
    rgb = np.full((8, 12, 3), value, dtype=np.uint8)
    ok, encoded = cv2.imencode(".png", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    if not ok:
        raise AssertionError("test PNG encoding failed")
    return encoded.tobytes()


def audio_chunk(index: int) -> tuple[float, ...]:
    return tuple(
        0.25 * math.sin(2.0 * math.pi * 100.0 * sample / 1000.0)
        for sample in range(index * 20, (index + 1) * 20)
    )


def complete_bridge() -> tuple[BrowserReceptorBridge, object]:
    visual, auditory = components()
    bridge = BrowserReceptorBridge(
        world_contract(),
        visual,
        auditory,
        BrowserReceptorBridgeConfig(
            clock_id="browser.test",
            ticks_per_second=1000.0,
            sequence_start_tick=7,
        ),
    )
    for index, value in enumerate((16, 128, 240)):
        bridge.push_visual_png(png_payload(value), frame_index=index)
    for index in range(15):
        bridge.push_audio_chunk(audio_chunk(index), chunk_index=index)
    return bridge, bridge.finalize()


class BrowserReceptorBridgeTests(unittest.TestCase):
    def test_inventory_time_and_digest_are_deterministic(self) -> None:
        first_bridge, first = complete_bridge()
        second_bridge, second = complete_bridge()

        self.assertEqual(3, first_bridge.expected_visual_frame_count)
        self.assertEqual(15, first_bridge.expected_audio_chunk_count)
        self.assertEqual((11, 3), tuple(len(item.frames) for item in first.sequences))
        self.assertEqual(("auditory", "visual"), tuple(
            item.modality_id for item in first.sequences
        ))
        self.assertEqual(("browser.test", "browser.test"), tuple(
            item.clock_id for item in first.sequences
        ))
        self.assertEqual((87, 107), (
            first.sequences[0].frames[0].field_time.window_start_tick,
            first.sequences[0].frames[0].field_time.window_end_tick,
        ))
        self.assertEqual((7, 107), (
            first.sequences[1].frames[0].field_time.window_start_tick,
            first.sequences[1].frames[0].field_time.window_end_tick,
        ))
        self.assertEqual(307, first.sequences[0].frames[-1].field_time.window_end_tick)
        self.assertEqual(307, first.sequences[1].frames[-1].field_time.window_end_tick)
        self.assertEqual(first.digest(), second.digest())
        self.assertFalse(first.raw_payloads_retained)
        self.assertFalse(first_bridge.raw_payloads_retained)
        self.assertFalse(second_bridge.raw_payloads_retained)
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            first.raw_payloads_retained = True  # type: ignore[misc]

    def test_invalid_or_out_of_order_payloads_fail_closed(self) -> None:
        visual, auditory = components()
        bridge = BrowserReceptorBridge(world_contract(), visual, auditory)

        with self.assertRaisesRegex(BrowserReceptorBridgeError, "PNG bytes"):
            bridge.push_visual_png(b"not-png", frame_index=0)
        with self.assertRaisesRegex(BrowserReceptorBridgeError, "out of order"):
            bridge.push_visual_png(png_payload(32), frame_index=1)
        with self.assertRaisesRegex(BrowserReceptorBridgeError, "out of order"):
            bridge.push_audio_chunk((0.0,) * 20, chunk_index=1)
        with self.assertRaisesRegex(BrowserReceptorBridgeError, "normalized"):
            bridge.push_audio_chunk((2.0,) * 20, chunk_index=0)
        with self.assertRaisesRegex(BrowserReceptorBridgeError, "incomplete"):
            bridge.finalize()

    def test_nonfresh_audio_and_nonintegral_inventory_are_rejected(self) -> None:
        visual, auditory = components()
        auditory.push((0.0,) * 20)
        with self.assertRaisesRegex(BrowserReceptorBridgeError, "fresh"):
            BrowserReceptorBridge(world_contract(), visual, auditory)

        visual, auditory = components()
        incompatible = replace(
            world_contract(),
            phases=(
                BrowserWorldPhase("rest.before", 100_000_001, "static", 0.0),
                BrowserWorldPhase("change", 100_000_000, "moving", 0.2),
                BrowserWorldPhase("rest.after", 100_000_000, "static", 0.0),
            ),
        )
        with self.assertRaisesRegex(BrowserReceptorBridgeError, "visual frames"):
            BrowserReceptorBridge(incompatible, visual, auditory)

    def test_finalized_batch_reaches_existing_shared_field_handoff(self) -> None:
        bridge, batch = complete_bridge()
        result = advance_audio_video_receptor_sequences(
            batch.sequences,
            bridge.visual_receptor,
            NeutralLocalFieldSubstrateConfig(1.0),
            ticks_per_second=1000.0,
        )

        self.assertEqual(batch.sequences, result.receptor_sequences)
        self.assertEqual(14, result.field_run.source_support_count)
        self.assertEqual(14, result.field_run.handoff.assigned_event_count)
        self.assertEqual(
            ("auditory", "visual"),
            result.field_run.handoff.modality_ids,
        )
        with self.assertRaisesRegex(BrowserReceptorBridgeError, "only once"):
            bridge.finalize()
        with self.assertRaisesRegex(BrowserReceptorBridgeError, "already finalized"):
            bridge.push_audio_chunk((0.0,) * 20, chunk_index=15)

    def test_public_roles_and_source_contain_no_forbidden_shortcuts(self) -> None:
        roles = set(browser_receptor_bridge_public_roles())
        self.assertTrue(
            {
                "semantic_label",
                "object_class",
                "reward",
                "target_topology",
                "raw_png",
                "raw_pcm",
                "field_writeback",
            }.isdisjoint(roles)
        )
        source = (
            Path(__file__).parents[1]
            / "mcm_field_organism"
            / "browser_receptor_bridge.py"
        ).read_text(encoding="ascii")
        for forbidden in (
            "z4a_",
            "playwright",
            "OpenCVVideoFrameSource",
            "SoundDeviceInputSource",
            "mcm_f3_",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
