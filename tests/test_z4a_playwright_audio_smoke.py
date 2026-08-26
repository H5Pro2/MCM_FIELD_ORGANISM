from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.z4a_playwright_audio_smoke import (
    Z4APlaywrightAudioSmokeError,
    run_z4a_playwright_audio_smoke,
)
from mcm_field_organism.z4a_playwright_runtime_binding import (
    Z4APlaywrightRuntimeBinding,
)


ASSETS = (Path(__file__).parents[1] / "tools" / "z4a_browser_world_v2").resolve()


class _Page:
    def __init__(self) -> None:
        self.url = "about:blank"
        self.released = False

    def route(self, pattern: str, handler: object) -> None:
        self.handler = handler

    def goto(self, url: str, **kwargs: object) -> None:
        self.url = url

    def evaluate(self, expression: str, arg: object | None = None) -> object:
        if "renderAudio" in expression:
            return 1_680_000
        if "readAudioChunk" in expression:
            return [0.0] * 480
        if "releaseAudio" in expression:
            self.released = True
        return None


class _Context:
    def __init__(self, page: _Page) -> None:
        self.page = page

    def new_page(self) -> _Page:
        return self.page

    def close(self) -> None:
        self.closed = True


class _Browser:
    version = "151.0.7922.34"

    def __init__(self, page: _Page) -> None:
        self.page = page

    def new_context(self, **kwargs: object) -> _Context:
        return _Context(self.page)

    def close(self) -> None:
        self.closed = True


class _Playwright:
    def __init__(self, page: _Page) -> None:
        self.page = page
        self.chromium = self

    def launch(self, **kwargs: object) -> _Browser:
        return _Browser(self.page)

    def __enter__(self) -> "_Playwright":
        return self

    def __exit__(self, *args: object) -> None:
        return None


def _binding(executable: Path, binary: bytes, digest: str | None = None) -> Z4APlaywrightRuntimeBinding:
    return Z4APlaywrightRuntimeBinding(
        "z4a.playwright-runtime.chromium.v1",
        "playwright",
        "1.62.0",
        "chromium",
        "chromium-headless-shell",
        "151.0.7922.34",
        "1234",
        str(executable.parent / "browsers.json"),
        "0" * 64,
        str(executable),
        len(binary),
        digest or sha256(binary).hexdigest(),
    )


class Z4APlaywrightAudioSmokeTests(unittest.TestCase):
    def test_fake_runtime_releases_audio_and_retains_no_samples(self) -> None:
        with TemporaryDirectory() as directory:
            binary = b"synthetic browser"
            executable = Path(directory) / "chrome.exe"
            executable.write_bytes(binary)
            page = _Page()
            receipt = run_z4a_playwright_audio_smoke(
                _binding(executable, binary),
                asset_directory=ASSETS,
                playwright_factory=lambda: _Playwright(page),
            )
            self.assertEqual(1_680_000, receipt.rendered_sample_count)
            self.assertEqual((480, 480), (receipt.first_chunk_size, receipt.last_chunk_size))
            self.assertTrue(receipt.audio_buffer_released)
            self.assertTrue(page.released)
            self.assertFalse(receipt.raw_samples_retained)

    def test_binary_drift_stops_before_browser_factory(self) -> None:
        with TemporaryDirectory() as directory:
            binary = b"changed"
            executable = Path(directory) / "chrome.exe"
            executable.write_bytes(binary)
            with self.assertRaisesRegex(Z4APlaywrightAudioSmokeError, "digest changed"):
                run_z4a_playwright_audio_smoke(
                    _binding(executable, binary, "1" * 64),
                    asset_directory=ASSETS,
                    playwright_factory=lambda: (_ for _ in ()).throw(AssertionError()),
                )


if __name__ == "__main__":
    unittest.main()
