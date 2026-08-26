from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import cv2
import numpy as np

from mcm_field_organism.z4a_playwright_runtime_binding import (
    Z4APlaywrightRuntimeBinding,
)
from mcm_field_organism.z4a_playwright_smoke import (
    Z4APlaywrightSmokeError,
    run_z4a_playwright_smoke,
)


ASSETS = (Path(__file__).parents[1] / "tools" / "z4a_browser_world_v2").resolve()


def _png() -> bytes:
    image = np.zeros((480, 480, 3), dtype=np.uint8)
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise AssertionError("PNG fixture failed")
    return encoded.tobytes()


class _Locator:
    def screenshot(self, **kwargs: object) -> bytes:
        return _png()


class _Page:
    def __init__(self) -> None:
        self.url = "about:blank"

    def route(self, pattern: str, handler: object) -> None:
        self.handler = handler

    def goto(self, url: str, **kwargs: object) -> None:
        self.url = url

    def evaluate(self, expression: str, arg: object | None = None) -> object:
        if "document.querySelector" in expression:
            return {"width": 480, "height": 480}
        return None

    def locator(self, selector: str) -> _Locator:
        return _Locator()


class _Context:
    def __init__(self) -> None:
        self.closed = False

    def new_page(self) -> _Page:
        return _Page()

    def close(self) -> None:
        self.closed = True


class _Browser:
    version = "151.0.7922.34"

    def __init__(self) -> None:
        self.connected = True

    def new_context(self, **kwargs: object) -> _Context:
        return _Context()

    def close(self) -> None:
        self.connected = False

    def is_connected(self) -> bool:
        return self.connected


class _Chromium:
    def __init__(self) -> None:
        self.browser = _Browser()

    def launch(self, **kwargs: object) -> _Browser:
        return self.browser


class _Playwright:
    def __init__(self) -> None:
        self.chromium = _Chromium()

    def __enter__(self) -> "_Playwright":
        return self

    def __exit__(self, *args: object) -> None:
        return None


class Z4APlaywrightSmokeTests(unittest.TestCase):
    def test_fake_runtime_completes_one_tick_and_retains_no_png(self) -> None:
        with TemporaryDirectory() as directory:
            executable = Path(directory) / "chrome.exe"
            binary = b"synthetic browser"
            executable.write_bytes(binary)
            binding = Z4APlaywrightRuntimeBinding(
                "z4a.playwright-runtime.chromium.v1",
                "playwright",
                "1.62.0",
                "chromium",
                "chromium-headless-shell",
                "151.0.7922.34",
                "1234",
                str(Path(directory) / "browsers.json"),
                "0" * 64,
                str(executable),
                len(binary),
                sha256(binary).hexdigest(),
            )
            receipt = run_z4a_playwright_smoke(
                binding,
                asset_directory=ASSETS,
                playwright_factory=_Playwright,
            )
            self.assertEqual((480, 480), (receipt.canvas_width, receipt.canvas_height))
            self.assertTrue(receipt.browser_started)
            self.assertTrue(receipt.browser_closed)
            self.assertFalse(receipt.raw_png_retained)

    def test_binary_drift_stops_before_factory(self) -> None:
        with TemporaryDirectory() as directory:
            executable = Path(directory) / "chrome.exe"
            executable.write_bytes(b"changed")
            binding = Z4APlaywrightRuntimeBinding(
                "z4a.playwright-runtime.chromium.v1",
                "playwright",
                "1.62.0",
                "chromium",
                "chromium-headless-shell",
                "151.0.7922.34",
                "1234",
                str(Path(directory) / "browsers.json"),
                "0" * 64,
                str(executable),
                len(b"changed"),
                "1" * 64,
            )
            with self.assertRaisesRegex(Z4APlaywrightSmokeError, "digest changed"):
                run_z4a_playwright_smoke(
                    binding,
                    asset_directory=ASSETS,
                    playwright_factory=lambda: (_ for _ in ()).throw(AssertionError()),
                )


if __name__ == "__main__":
    unittest.main()
