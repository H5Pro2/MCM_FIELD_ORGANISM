from __future__ import annotations

import math
from pathlib import Path
import unittest

import cv2
import numpy as np

from mcm_field_organism.current_api import (
    BroadbandHearingPath,
    BrowserPayloadCapturePreflight,
    BrowserReceptorBridge,
    LocalChannelGridReceptor,
    LogSpectralConfig,
    LogSpectralReceptor,
    S1B_CAUSAL_BROWSER_WORLD_SET_DIGEST,
    S1BCausalCaptureHandoffError,
    VisualGridConfig,
    capture_browser_payload_page,
    prepare_s1b_causal_capture_handoff,
    run_s1b_causal_capture_handoff,
    s1b_causal_browser_world_set,
    s1b_causal_capture_schedule,
)


ASSETS = Path(__file__).parents[1] / "tools" / "controlled_browser_payload_world"


class FakeRequest:
    def __init__(self, url: str) -> None:
        self.url = url


class FakeRoute:
    def __init__(self) -> None:
        self.continued = False

    def continue_(self) -> None:
        self.continued = True

    def abort(self, error_code: str = "blockedbyclient") -> None:
        raise AssertionError(f"unexpected blocked request: {error_code}")


class FakePage:
    def __init__(self) -> None:
        self.url = "about:blank"
        self.route_handler = None
        self.world = None
        self.source = None
        self.visual_index = 0
        self.audio_released = False

    def route(self, url: str, handler: object) -> None:
        self.route_handler = handler

    def goto(self, url: str, **kwargs: object) -> None:
        self.url = url
        root = Path(url.removeprefix("file:///"))
        if root.drive == "":
            root = Path("/" + str(root))
        root = root.parent
        for name in ("index.html", "styles.css", "world.js"):
            route = FakeRoute()
            self.route_handler(route, FakeRequest((root / name).as_uri()))
            if not route.continued:
                raise AssertionError("local request was not continued")

    def evaluate(self, expression: str, arg: object | None = None):
        if "configureWorld" in expression:
            self.world = arg["world"]
            self.source = arg["source"]
            return None
        if "renderVisualFrame" in expression:
            self.visual_index = int(arg)
            return None
        if "renderAudio" in expression:
            return 7200
        if "readAudioChunk" in expression:
            index = int(arg)
            hop = self.source["audio_hop_size"]
            sample_rate = self.source["audio_sample_rate"]
            frequency = self.world["tone_frequency_hz"]
            phase_samples = 2400
            output = []
            for sample_index in range(index * hop, (index + 1) * hop):
                phase_index = min(
                    sample_index // phase_samples,
                    len(self.world["phases"]) - 1,
                )
                gain = self.world["phases"][phase_index]["tone_gain"]
                output.append(
                    gain
                    * math.sin(
                        2.0 * math.pi * frequency * sample_index / sample_rate
                    )
                )
            return output
        if "releaseAudio" in expression:
            self.audio_released = True
            return None
        raise AssertionError(f"unexpected fake expression: {expression}")

    def locator(self, selector: str):
        if selector != "canvas#world":
            raise AssertionError("unexpected fake selector")
        return self

    def screenshot(self, **kwargs: object) -> bytes:
        width = self.source["canvas_width"]
        height = self.source["canvas_height"]
        background = np.asarray(self.source["background_rgb"], dtype=np.uint8)
        foreground = np.asarray(self.source["foreground_rgb"], dtype=np.uint8)
        rgb = np.empty((height, width, 3), dtype=np.uint8)
        rgb[:] = background
        phase_index = min(self.visual_index // 9, len(self.world["phases"]) - 1)
        phase = self.world["phases"][phase_index]
        extent = min(width, height)
        size = round(extent * self.source["foreground_size_fraction"])
        offset = 0
        if phase["visual_mode"] == "moving":
            local_index = self.visual_index - phase_index * 9
            offset = round(
                extent
                * self.source["motion_amplitude_fraction"]
                * math.sin(2.0 * math.pi * local_index / 9.0)
            )
        center_x = width // 2
        center_y = height // 2
        if self.source["motion_axis"] == "horizontal":
            center_x += offset
        else:
            center_y += offset
        half = size // 2
        rgb[center_y - half : center_y + half, center_x - half : center_x + half] = (
            foreground
        )
        ok, encoded = cv2.imencode(
            ".png",
            cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR),
        )
        if not ok:
            raise AssertionError("fake PNG encoding failed")
        return encoded.tobytes()


def bridge(contract, source, config):
    visual = LocalChannelGridReceptor(
        VisualGridConfig(
            source_width=source.canvas_width,
            source_height=source.canvas_height,
            grid_columns=3,
            grid_rows=2,
            frames_per_second=source.visual_frames_per_second,
        )
    )
    auditory = BroadbandHearingPath(
        LogSpectralReceptor(
            LogSpectralConfig(
                sample_rate=source.audio_sample_rate,
                window_size=800,
                hop_size=source.audio_hop_size,
                min_frequency=50.0,
                max_frequency=3000.0,
                band_count=8,
            )
        )
    )
    return BrowserReceptorBridge(contract, visual, auditory, config)


def capture_parts():
    worlds = s1b_causal_browser_world_set()
    schedule = s1b_causal_capture_schedule(worlds)
    preflight = BrowserPayloadCapturePreflight(
        fresh_isolated_context=True,
        persistent_profile=False,
        extensions_enabled=False,
        viewport_width=120,
        viewport_height=80,
        device_scale_factor=1,
        java_script_enabled=True,
    )
    specifications = (
        (
            worlds.history_a_contract,
            worlds.history_a_source,
            schedule.history_a_bridge_config,
        ),
        (
            worlds.history_b_contract,
            worlds.history_b_source,
            schedule.history_b_bridge_config,
        ),
        (
            worlds.probe_contract,
            worlds.probe_source,
            schedule.probe_bridge_config,
        ),
    )
    output = []
    pages = []
    for contract, source, config in specifications:
        page = FakePage()
        pages.append(page)
        output.append(
            capture_browser_payload_page(
                page,
                contract,
                source,
                bridge(contract, source, config),
                asset_directory=ASSETS,
                preflight=preflight,
            )
        )
    return worlds, schedule, tuple(output), tuple(pages)


class S1BCausalCaptureHandoffTests(unittest.TestCase):
    def test_schedule_aligns_alternative_histories_before_disjoint_probe(self) -> None:
        schedule = s1b_causal_capture_schedule()

        self.assertEqual(0, schedule.history_a_bridge_config.sequence_start_tick)
        self.assertEqual(0, schedule.history_b_bridge_config.sequence_start_tick)
        self.assertEqual(900_000_000, schedule.history_step.end_tick)
        self.assertEqual(
            schedule.history_step.end_tick,
            schedule.probe_bridge_config.sequence_start_tick,
        )
        self.assertEqual(
            schedule.history_step.end_tick,
            schedule.probe_step.start_tick,
        )
        self.assertEqual(1_800_000_000, schedule.probe_step.end_tick)

    def test_fake_capture_handoff_keeps_probe_identity_and_releases_raw_audio(self) -> None:
        worlds, schedule, parts, pages = capture_parts()
        (batch_a, receipt_a), (batch_b, receipt_b), (batch_p, receipt_p) = parts
        handoff = prepare_s1b_causal_capture_handoff(
            batch_a,
            receipt_a,
            batch_b,
            receipt_b,
            batch_p,
            receipt_p,
            world_set=worlds,
        )

        self.assertIs(batch_p.sequences, handoff.probe_sequences)
        self.assertEqual(S1B_CAUSAL_BROWSER_WORLD_SET_DIGEST, handoff.world_set_digest)
        self.assertEqual(schedule.history_step, handoff.history_step)
        self.assertEqual(schedule.probe_step, handoff.probe_step)
        self.assertTrue(all(page.audio_released for page in pages))
        self.assertTrue(
            all(not receipt.raw_payloads_retained for _, receipt in parts)
        )

    def test_fake_capture_runs_complete_technical_four_arm_handoff(self) -> None:
        worlds, _, parts, _ = capture_parts()
        (batch_a, receipt_a), (batch_b, receipt_b), (batch_p, receipt_p) = parts
        handoff = prepare_s1b_causal_capture_handoff(
            batch_a,
            receipt_a,
            batch_b,
            receipt_b,
            batch_p,
            receipt_p,
            world_set=worlds,
        )

        result = run_s1b_causal_capture_handoff(handoff)

        self.assertEqual(
            "LOCAL_L_STATE_CAUSALLY_ALTERS_LATER_S_TRAJECTORY_IN_S1B_REFERENCE",
            result.technical_decision,
        )
        self.assertTrue(result.fast_r_n_equal)
        self.assertTrue(result.fast_r_x_equal)
        self.assertTrue(result.null_formation_equal)
        self.assertTrue(result.null_probe_equal)
        self.assertGreater(result.l_ab_linf, result.tolerance)

    def test_mismatched_receipt_is_rejected_before_handoff(self) -> None:
        worlds, _, parts, _ = capture_parts()
        (batch_a, _), (batch_b, receipt_b), (batch_p, receipt_p) = parts
        with self.assertRaisesRegex(
            S1BCausalCaptureHandoffError,
            "digest binding differs",
        ):
            prepare_s1b_causal_capture_handoff(
                batch_a,
                receipt_b,
                batch_b,
                receipt_b,
                batch_p,
                receipt_p,
                world_set=worlds,
            )

    def test_independent_fake_captures_are_digest_and_result_deterministic(self) -> None:
        outputs = []
        for _ in range(2):
            worlds, _, parts, _ = capture_parts()
            (batch_a, receipt_a), (batch_b, receipt_b), (batch_p, receipt_p) = parts
            handoff = prepare_s1b_causal_capture_handoff(
                batch_a,
                receipt_a,
                batch_b,
                receipt_b,
                batch_p,
                receipt_p,
                world_set=worlds,
            )
            outputs.append(
                (
                    handoff.history_a_batch_digest,
                    handoff.history_b_batch_digest,
                    handoff.probe_batch_digest,
                    run_s1b_causal_capture_handoff(handoff),
                )
            )

        self.assertEqual(outputs[0], outputs[1])


if __name__ == "__main__":
    unittest.main()
