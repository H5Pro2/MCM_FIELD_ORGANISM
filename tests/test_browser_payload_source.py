from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import math
from pathlib import Path
import unittest

import cv2
import numpy as np

from mcm_field_organism import (
    BrowserPayloadCapturePreflight,
    BrowserPayloadSourceConfig,
    BrowserPayloadSourceError,
    BrowserReceptorBridge,
    BrowserWorldContract,
    BrowserWorldPhase,
    NeutralLocalFieldSubstrateConfig,
    advance_audio_video_receptor_sequences,
    browser_payload_asset_digests,
    browser_payload_source_public_roles,
    capture_browser_payload_page,
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


ASSETS = (
    Path(__file__).parents[1] / "tools" / "controlled_browser_payload_world"
)


def world_contract() -> BrowserWorldContract:
    return BrowserWorldContract(
        contract_id="browser.world.payload.test.v1",
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


def source_config() -> BrowserPayloadSourceConfig:
    return BrowserPayloadSourceConfig(
        source_id="browser.payload.test.v1",
        canvas_width=12,
        canvas_height=8,
        device_scale_factor=1,
        visual_frames_per_second=10.0,
        motion_axis="horizontal",
        motion_amplitude_fraction=0.2,
        foreground_size_fraction=0.2,
        background_rgb=(16, 24, 32),
        foreground_rgb=(224, 232, 240),
        audio_sample_rate=1000,
        audio_hop_size=20,
    )


def receptor_bridge() -> BrowserReceptorBridge:
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
    return BrowserReceptorBridge(world_contract(), visual, auditory)


def preflight() -> BrowserPayloadCapturePreflight:
    return BrowserPayloadCapturePreflight(
        fresh_isolated_context=True,
        persistent_profile=False,
        extensions_enabled=False,
        viewport_width=12,
        viewport_height=8,
        device_scale_factor=1,
        java_script_enabled=True,
    )


def png_payload(value: int) -> bytes:
    rgb = np.full((8, 12, 3), value, dtype=np.uint8)
    ok, encoded = cv2.imencode(".png", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    if not ok:
        raise AssertionError("test PNG encoding failed")
    return encoded.tobytes()


class FakeRequest:
    def __init__(self, url: str) -> None:
        self.url = url


class FakeRoute:
    def __init__(self) -> None:
        self.continued = False
        self.aborted = False

    def continue_(self) -> None:
        self.continued = True

    def abort(self, error_code: str = "blockedbyclient") -> None:
        self.aborted = True


class FakePage:
    def __init__(self, *, foreign_request: bool = False, bad_audio_index: int | None = None) -> None:
        self.url = "about:blank"
        self.foreign_request = foreign_request
        self.bad_audio_index = bad_audio_index
        self.route_handler = None
        self.visual_index = 0
        self.audio_released = False
        self.calls: list[tuple[str, object | None]] = []

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
                raise AssertionError("local fake request was not continued")
        if self.foreign_request:
            route = FakeRoute()
            self.route_handler(route, FakeRequest("https://example.invalid/world.js"))
            if not route.aborted:
                raise AssertionError("foreign fake request was not blocked")

    def evaluate(self, expression: str, arg: object | None = None):
        self.calls.append((expression, arg))
        if "configureWorld" in expression:
            return None
        if "renderVisualFrame" in expression:
            self.visual_index = int(arg)
            return None
        if "renderAudio" in expression:
            return 300
        if "readAudioChunk" in expression:
            index = int(arg)
            if self.bad_audio_index == index:
                return [0.0] * 19
            return [
                0.25 * math.sin(2.0 * math.pi * 100.0 * sample / 1000.0)
                for sample in range(index * 20, (index + 1) * 20)
            ]
        if "releaseAudio" in expression:
            self.audio_released = True
            return None
        raise AssertionError(f"unexpected evaluate expression: {expression}")

    def locator(self, selector: str):
        if selector != "canvas#world":
            raise AssertionError(selector)
        return self

    def screenshot(self, **kwargs: object) -> bytes:
        return png_payload((self.visual_index + 1) * 48)


class BrowserPayloadSourceTests(unittest.TestCase):
    def test_source_config_and_asset_digests_are_deterministic(self) -> None:
        first = source_config()
        second = source_config()
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(
            ("index.html", "styles.css", "world.js"),
            tuple(name for name, _ in browser_payload_asset_digests(ASSETS)),
        )
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            first.motion_axis = "vertical"  # type: ignore[misc]
        with self.assertRaises(BrowserPayloadSourceError):
            replace(first, device_scale_factor=2)
        with self.assertRaises(BrowserPayloadSourceError):
            replace(first, motion_amplitude_fraction=0.45)

    def test_assets_expose_only_direct_local_payload_functions(self) -> None:
        combined = "\n".join(
            (ASSETS / name).read_text(encoding="ascii")
            for name in ("index.html", "styles.css", "world.js")
        )
        for required in (
            "configureWorld",
            "renderVisualFrame",
            "OfflineAudioContext",
            "readAudioChunk",
            "releaseAudio",
        ):
            self.assertIn(required, combined)
        for forbidden in (
            "Date.now",
            "performance.now",
            "requestAnimationFrame",
            "new AudioContext",
            "mediaDevices",
            "getUserMedia",
            "MediaRecorder",
            "fetch(",
            "WebSocket",
            "localStorage",
            "sessionStorage",
            "indexedDB",
            "requestFullscreen",
        ):
            self.assertNotIn(forbidden, combined)

    def test_fake_page_reaches_bridge_and_existing_shared_field(self) -> None:
        page = FakePage()
        bridge = receptor_bridge()
        batch, receipt = capture_browser_payload_page(
            page,
            world_contract(),
            source_config(),
            bridge,
            asset_directory=ASSETS,
            preflight=preflight(),
        )

        self.assertEqual((11, 3), tuple(len(item.frames) for item in batch.sequences))
        self.assertEqual(batch.digest(), receipt.batch_digest)
        self.assertEqual((3, 3, 15, 300), (
            receipt.local_request_count,
            receipt.visual_png_count,
            receipt.audio_chunk_count,
            receipt.rendered_audio_sample_count,
        ))
        self.assertTrue(receipt.audio_buffer_released)
        self.assertGreater(receipt.audio_total_energy, 0.0)
        self.assertTrue(page.audio_released)
        self.assertFalse(receipt.raw_payloads_retained)

        field = advance_audio_video_receptor_sequences(
            batch.sequences,
            bridge.visual_receptor,
            NeutralLocalFieldSubstrateConfig(1.0),
            ticks_per_second=1_000_000_000.0,
        )
        self.assertEqual(14, field.field_run.handoff.assigned_event_count)

    def test_foreign_request_stops_before_payload_handoff(self) -> None:
        page = FakePage(foreign_request=True)
        bridge = receptor_bridge()
        with self.assertRaisesRegex(BrowserPayloadSourceError, "non-local"):
            capture_browser_payload_page(
                page,
                world_contract(),
                source_config(),
                bridge,
                asset_directory=ASSETS,
                preflight=preflight(),
            )
        self.assertEqual([], page.calls)

    def test_audio_buffer_is_released_after_bridge_failure(self) -> None:
        page = FakePage(bad_audio_index=2)
        with self.assertRaisesRegex(ValueError, "audio chunk"):
            capture_browser_payload_page(
                page,
                world_contract(),
                source_config(),
                receptor_bridge(),
                asset_directory=ASSETS,
                preflight=preflight(),
            )
        self.assertTrue(page.audio_released)

    def test_public_roles_and_source_have_no_forbidden_state(self) -> None:
        roles = set(browser_payload_source_public_roles())
        self.assertTrue(
            {
                "raw_png",
                "raw_pcm",
                "semantic_label",
                "object_class",
                "reward",
                "target_topology",
                "field_writeback",
            }.isdisjoint(roles)
        )
        source = (
            Path(__file__).parents[1]
            / "mcm_field_organism"
            / "browser_payload_source.py"
        ).read_text(encoding="ascii")
        for forbidden in (
            "z4a_",
            "OpenCVVideoFrameSource",
            "SoundDeviceInputSource",
            "mcm_f3_",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
