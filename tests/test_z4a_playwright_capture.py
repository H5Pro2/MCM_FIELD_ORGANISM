from __future__ import annotations

from pathlib import Path
import unittest

from mcm_field_organism.z4a_browser_receptor_adapter import (
    Z4ABrowserReceptorAdapter,
    reference_z4a_browser_world_contract,
)
from mcm_field_organism.z4a_playwright_capture import (
    Z4APlaywrightCaptureError,
    Z4APlaywrightCapturePreflight,
    capture_z4a_playwright_page,
)


ASSETS = (Path(__file__).parents[1] / "tools" / "z4a_browser_world_v2").resolve()


class _Route:
    def __init__(self) -> None:
        self.action = ""

    def abort(self, error_code: str = "blockedbyclient") -> None:
        self.action = f"abort:{error_code}"

    def continue_(self) -> None:
        self.action = "continue"


class _Request:
    def __init__(self, url: str) -> None:
        self.url = url


class _Locator:
    def __init__(self, png: bytes) -> None:
        self.png = png
        self.calls = 0

    def screenshot(self, **kwargs: object) -> bytes:
        self.calls += 1
        return self.png


class _RecordingAdapter(Z4ABrowserReceptorAdapter):
    def __init__(self, *, fail_audio_at: int | None = None) -> None:
        super().__init__(reference_z4a_browser_world_contract())
        self.visual_indices: list[int] = []
        self.audio_indices: list[int] = []
        self.fail_audio_at = fail_audio_at

    def push_visual_png(self, png_bytes: bytes, *, frame_index: int) -> None:
        self.visual_indices.append(frame_index)

    def push_audio_chunk(self, samples: object, *, chunk_index: int) -> None:
        if chunk_index == self.fail_audio_at:
            raise Z4APlaywrightCaptureError("synthetic adapter failure")
        self.audio_indices.append(chunk_index)

    def finalize(self) -> tuple[object, object]:
        return "auditory", "visual"


class _Page:
    def __init__(self, *, external_request: bool = False) -> None:
        self.url = "about:blank"
        self._handler = None
        self.external_request = external_request
        self.locator_instance = _Locator(b"\x89PNG\r\n\x1a\nsynthetic")
        self.visual_ticks: list[int] = []
        self.audio_indices: list[int] = []
        self.configured_world = ""
        self.audio_released = False

    def route(self, url: str, handler: object) -> None:
        self._handler = handler

    def goto(self, url: str, **kwargs: object) -> None:
        self.url = url
        urls = [
            (ASSETS / "index.html").as_uri(),
            (ASSETS / "styles.css").as_uri(),
            (ASSETS / "world.js").as_uri(),
        ]
        if self.external_request:
            urls.append("https://example.invalid/forbidden.js")
        for request_url in urls:
            route = _Route()
            self._handler(route, _Request(request_url))

    def evaluate(self, expression: str, arg: object | None = None) -> object:
        if "configureWorld" in expression:
            self.configured_world = str(arg)
            return None
        if "renderVisualAt" in expression:
            self.visual_ticks.append(int(arg))
            return None
        if "renderAudio" in expression:
            return 1_680_000
        if "readAudioChunk" in expression:
            self.audio_indices.append(int(arg))
            return [0.0] * 480
        if "releaseAudio" in expression:
            self.audio_released = True
            return None
        raise AssertionError(f"unexpected expression: {expression}")

    def locator(self, selector: str) -> _Locator:
        self.asserted_selector = selector
        return self.locator_instance


def _preflight() -> Z4APlaywrightCapturePreflight:
    return Z4APlaywrightCapturePreflight(
        fresh_isolated_context=True,
        persistent_profile=False,
        extensions_enabled=False,
        viewport_width=480,
        viewport_height=480,
        device_scale_factor=1,
        java_script_enabled=True,
    )


class Z4APlaywrightCaptureTests(unittest.TestCase):
    def test_preflight_rejects_persistent_or_unbound_contexts(self) -> None:
        with self.assertRaises(Z4APlaywrightCaptureError):
            Z4APlaywrightCapturePreflight(True, True, False, 480, 480, 1, True)
        with self.assertRaises(Z4APlaywrightCaptureError):
            Z4APlaywrightCapturePreflight(True, False, False, 481, 480, 1, True)

    def test_non_local_request_stops_before_capture(self) -> None:
        page = _Page(external_request=True)
        adapter = _RecordingAdapter()
        with self.assertRaises(Z4APlaywrightCaptureError):
            capture_z4a_playwright_page(
                page,
                adapter.contract,
                adapter,
                asset_directory=ASSETS,
                preflight=_preflight(),
            )
        self.assertEqual([], adapter.visual_indices)
        self.assertEqual([], adapter.audio_indices)

    def test_capture_orders_exact_visual_and_audio_inventories(self) -> None:
        page = _Page()
        adapter = _RecordingAdapter()
        sequences, receipt = capture_z4a_playwright_page(
            page,
            adapter.contract,
            adapter,
            asset_directory=ASSETS,
            preflight=_preflight(),
        )
        self.assertEqual(("auditory", "visual"), sequences)
        self.assertEqual(list(range(875)), adapter.visual_indices)
        self.assertEqual(list(range(3500)), adapter.audio_indices)
        self.assertEqual(0, page.visual_ticks[0])
        self.assertEqual(34_960_000_000, page.visual_ticks[-1])
        self.assertEqual(list(range(3500)), page.audio_indices)
        self.assertEqual(3, receipt.local_request_count)
        self.assertEqual(0, receipt.blocked_request_count)
        self.assertFalse(receipt.raw_payloads_retained)
        self.assertTrue(page.audio_released)

    def test_audio_buffer_is_released_after_adapter_failure(self) -> None:
        page = _Page()
        adapter = _RecordingAdapter(fail_audio_at=17)
        with self.assertRaises(Z4APlaywrightCaptureError):
            capture_z4a_playwright_page(
                page,
                adapter.contract,
                adapter,
                asset_directory=ASSETS,
                preflight=_preflight(),
            )
        self.assertEqual(list(range(17)), adapter.audio_indices)
        self.assertTrue(page.audio_released)


if __name__ == "__main__":
    unittest.main()
