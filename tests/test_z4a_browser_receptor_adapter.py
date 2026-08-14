from __future__ import annotations

from pathlib import Path
import unittest

import cv2
import numpy as np

from mcm_field_organism.z4a_browser_receptor_adapter import (
    Z4A_BROWSER_AUDIO_CHUNK_COUNT,
    Z4A_BROWSER_INDEPENDENT_WORLD_ID,
    Z4A_BROWSER_REFERENCE_WORLD_ID,
    Z4A_BROWSER_VISUAL_FRAME_COUNT,
    Z4ABrowserReceptorAdapter,
    Z4ABrowserReceptorError,
    Z4ABrowserWorldContract,
    independent_z4a_browser_world_contract,
    reference_z4a_browser_world_contract,
    z4a_browser_asset_digests,
    z4a_browser_sequence_receipt,
)


ASSETS = Path(__file__).parents[1] / "tools" / "z4a_browser_world_v2"


def _png() -> bytes:
    image = np.zeros((480, 480, 3), dtype=np.uint8)
    image[:, :] = (32, 36, 40)
    image[197:283, 197:283] = (245, 247, 248)
    ok, encoded = cv2.imencode(".png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    if not ok:
        raise AssertionError("test PNG encoding failed")
    return encoded.tobytes()


class Z4ABrowserReceptorAdapterTests(unittest.TestCase):
    def test_contracts_are_exact_and_distinct(self) -> None:
        reference = reference_z4a_browser_world_contract()
        independent = independent_z4a_browser_world_contract()
        self.assertEqual(Z4A_BROWSER_REFERENCE_WORLD_ID, reference.world_id)
        self.assertEqual(Z4A_BROWSER_INDEPENDENT_WORLD_ID, independent.world_id)
        self.assertNotEqual(reference.digest(), independent.digest())
        self.assertEqual("horizontal", reference.canonical_payload()["visual"]["motion_axis"])
        self.assertEqual(990.0, independent.canonical_payload()["audio"]["tone_frequency_hz"])
        with self.assertRaises(Z4ABrowserReceptorError):
            Z4ABrowserWorldContract("other", "other", "horizontal", 660.0)

    def test_assets_are_complete_and_contain_only_direct_interfaces(self) -> None:
        digests = z4a_browser_asset_digests(ASSETS)
        self.assertEqual(("index.html", "styles.css", "world.js"), tuple(name for name, _ in digests))
        script = (ASSETS / "world.js").read_text(encoding="ascii")
        self.assertIn("renderVisualAt", script)
        self.assertIn("OfflineAudioContext", script)
        for forbidden in ("Date.now", "requestAnimationFrame", "mediaDevices", "getUserMedia", "fetch("):
            self.assertNotIn(forbidden, script)

    def test_adapter_rejects_non_png_and_out_of_order_payloads(self) -> None:
        adapter = Z4ABrowserReceptorAdapter(reference_z4a_browser_world_contract())
        with self.assertRaises(Z4ABrowserReceptorError):
            adapter.push_visual_png(b"not-png", frame_index=0)
        with self.assertRaises(Z4ABrowserReceptorError):
            adapter.push_visual_png(_png(), frame_index=1)
        with self.assertRaises(Z4ABrowserReceptorError):
            adapter.push_audio_chunk((0.0,) * 480, chunk_index=1)
        with self.assertRaises(Z4ABrowserReceptorError):
            adapter.push_audio_chunk((0.0,) * 479, chunk_index=0)

    def test_complete_synthetic_payloads_reduce_to_bound_sequences(self) -> None:
        adapter = Z4ABrowserReceptorAdapter(reference_z4a_browser_world_contract())
        png = _png()
        for index in range(Z4A_BROWSER_VISUAL_FRAME_COUNT):
            adapter.push_visual_png(png, frame_index=index)
        silence = (0.0,) * 480
        for index in range(Z4A_BROWSER_AUDIO_CHUNK_COUNT):
            adapter.push_audio_chunk(silence, chunk_index=index)
        auditory, visual = adapter.finalize()
        self.assertEqual((3491, 875), (len(auditory.frames), len(visual.frames)))
        self.assertEqual((90_000_000, 100_000_000), (
            auditory.frames[0].field_time.window_start_tick,
            auditory.frames[0].field_time.window_end_tick,
        ))
        self.assertEqual(35_000_000_000, auditory.frames[-1].field_time.window_end_tick)
        self.assertEqual(35_000_000_000, visual.frames[-1].field_time.window_end_tick)
        receipt = z4a_browser_sequence_receipt(reference_z4a_browser_world_contract(), (auditory, visual))
        self.assertEqual(3491, receipt.auditory_state_count)
        self.assertEqual(875, receipt.visual_state_count)
        self.assertFalse(receipt.raw_payloads_retained)
        self.assertFalse(adapter.raw_payloads_retained)
        with self.assertRaises(Z4ABrowserReceptorError):
            adapter.finalize()


if __name__ == "__main__":
    unittest.main()
