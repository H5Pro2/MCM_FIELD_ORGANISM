from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

import cv2
import numpy as np

from mcm_field_organism import (
    BrowserPayloadSmokeError,
    bind_browser_payload_runtime,
    browser_payload_smoke_json_value,
    browser_payload_smoke_public_roles,
    browser_payload_smoke_receptor_bridge,
    browser_payload_smoke_source_config,
    browser_payload_smoke_world_contract,
    run_browser_payload_smoke,
)


ASSETS = (
    Path(__file__).parents[1] / "tools" / "controlled_browser_payload_world"
)


def bound_runtime(root: Path):
    installation = root / "browsers"
    installation.mkdir()
    executable = installation / "headless.exe"
    executable.write_bytes(b"bound-headless-shell")
    requirements = root / "requirements-browser.txt"
    requirements.write_text("playwright==1.62.0\n", encoding="utf-8")
    manifest = root / "browsers.json"
    manifest.write_text(
        json.dumps(
            {
                "browsers": [
                    {
                        "name": "chromium-headless-shell",
                        "revision": "1234",
                        "browserVersion": "151.0.7922.34",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    binding = bind_browser_payload_runtime(
        package_version="1.62.0",
        requirements_path=requirements,
        manifest_path=manifest,
        executable_path=executable,
        installation_root=installation,
    )
    return binding, executable


def png_payload(value: int) -> bytes:
    rgb = np.full((80, 120, 3), value, dtype=np.uint8)
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

    def continue_(self) -> None:
        self.continued = True

    def abort(self, error_code: str = "blockedbyclient") -> None:
        raise AssertionError(f"unexpected blocked request: {error_code}")


class FakePage:
    def __init__(self, *, bad_audio_index: int | None = None) -> None:
        self.url = "about:blank"
        self.bad_audio_index = bad_audio_index
        self.route_handler = None
        self.visual_index = 0
        self.audio_released = False
        self.closed = False

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
            return None
        if "renderVisualFrame" in expression:
            self.visual_index = int(arg)
            return None
        if "renderAudio" in expression:
            return 2400
        if "readAudioChunk" in expression:
            index = int(arg)
            if self.bad_audio_index == index:
                return [0.0] * 79
            return [
                0.2 * math.sin(2.0 * math.pi * 440.0 * sample / 8000.0)
                for sample in range(index * 80, (index + 1) * 80)
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

    def close(self) -> None:
        self.closed = True


class FakeContext:
    def __init__(self, page: FakePage, *, fail_close: bool = False) -> None:
        self.page = page
        self.fail_close = fail_close
        self.closed = False

    def new_page(self) -> FakePage:
        return self.page

    def close(self) -> None:
        if self.fail_close:
            raise RuntimeError("controlled context close failure")
        self.closed = True


class FakeBrowser:
    def __init__(
        self,
        engine_version: str,
        page: FakePage,
        *,
        fail_context_close: bool = False,
    ) -> None:
        self.version = engine_version
        self.page = page
        self.context = FakeContext(page, fail_close=fail_context_close)
        self.closed = False
        self.context_options = None

    def new_context(self, **kwargs: object) -> FakeContext:
        self.context_options = kwargs
        return self.context

    def close(self) -> None:
        self.closed = True


class FakeChromium:
    def __init__(self, browser: FakeBrowser) -> None:
        self.browser = browser
        self.launch_options = None

    def launch(self, **kwargs: object) -> FakeBrowser:
        self.launch_options = kwargs
        return self.browser


class FakePlaywrightManager:
    def __init__(
        self,
        engine_version: str,
        *,
        bad_audio_index: int | None = None,
        fail_context_close: bool = False,
    ) -> None:
        self.page = FakePage(bad_audio_index=bad_audio_index)
        self.browser = FakeBrowser(
            engine_version,
            self.page,
            fail_context_close=fail_context_close,
        )
        self.chromium = FakeChromium(self.browser)
        self.exited = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.exited = True


class BrowserPayloadSmokeTests(unittest.TestCase):
    def test_console_tool_imports_when_started_outside_workspace(self) -> None:
        tool = ASSETS.parent / "run_browser_payload_smoke.py"
        with TemporaryDirectory() as directory:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import runpy,sys; runpy.run_path(sys.argv[1], "
                    "run_name='browser_payload_smoke_import_test')",
                    str(tool),
                ],
                cwd=directory,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(0, completed.returncode, completed.stderr)

    def test_bound_smoke_factories_have_the_exact_short_inventory(self) -> None:
        contract = browser_payload_smoke_world_contract()
        source = browser_payload_smoke_source_config()
        bridge = browser_payload_smoke_receptor_bridge()
        self.assertEqual(300_000_000, contract.total_duration_ns)
        self.assertEqual((3, 30), (
            bridge.expected_visual_frame_count,
            bridge.expected_audio_chunk_count,
        ))
        self.assertEqual((120, 80, 8000, 80), (
            source.canvas_width,
            source.canvas_height,
            source.audio_sample_rate,
            source.audio_hop_size,
        ))

    def test_fake_playwright_lifecycle_reaches_one_scalar_receipt(self) -> None:
        with TemporaryDirectory() as directory:
            binding, _ = bound_runtime(Path(directory))
            manager = FakePlaywrightManager(binding.engine_version)
            receipt = run_browser_payload_smoke(
                binding,
                asset_directory=ASSETS,
                playwright_factory=lambda: manager,
                runtime_validator=lambda _: None,
            )

        self.assertEqual((21, 3, 24), (
            receipt.auditory_state_count,
            receipt.visual_state_count,
            receipt.assigned_event_count,
        ))
        self.assertEqual(receipt.batch_digest, receipt.capture_receipt.batch_digest)
        self.assertEqual(receipt.asset_digests, receipt.capture_receipt.asset_digests)
        self.assertTrue(manager.page.audio_released)
        self.assertTrue(manager.page.closed)
        self.assertTrue(manager.browser.context.closed)
        self.assertTrue(manager.browser.closed)
        self.assertTrue(manager.exited)
        self.assertTrue(manager.chromium.launch_options["headless"])
        self.assertEqual([], manager.browser.context_options["permissions"])
        self.assertFalse(receipt.raw_payloads_retained)
        projected = browser_payload_smoke_json_value(receipt)
        encoded = json.dumps(projected).lower()
        self.assertNotIn("raw_png", encoded)
        self.assertNotIn("raw_pcm", encoded)
        self.assertNotIn("receptor_values", encoded)
        self.assertNotIn("field_values", encoded)

    def test_capture_failure_still_closes_page_context_and_browser(self) -> None:
        with TemporaryDirectory() as directory:
            binding, _ = bound_runtime(Path(directory))
            manager = FakePlaywrightManager(
                binding.engine_version,
                bad_audio_index=2,
            )
            with self.assertRaisesRegex(ValueError, "audio chunk"):
                run_browser_payload_smoke(
                    binding,
                    asset_directory=ASSETS,
                    playwright_factory=lambda: manager,
                    runtime_validator=lambda _: None,
                )

        self.assertTrue(manager.page.audio_released)
        self.assertTrue(manager.page.closed)
        self.assertTrue(manager.browser.context.closed)
        self.assertTrue(manager.browser.closed)
        self.assertTrue(manager.exited)

    def test_runtime_drift_stops_before_playwright_factory(self) -> None:
        with TemporaryDirectory() as directory:
            binding, executable = bound_runtime(Path(directory))
            executable.write_bytes(b"drift")
            factory_called = False

            def factory():
                nonlocal factory_called
                factory_called = True
                raise AssertionError("factory must not be called after drift")

            with self.assertRaisesRegex(BrowserPayloadSmokeError, "size changed"):
                run_browser_payload_smoke(
                    binding,
                    asset_directory=ASSETS,
                    playwright_factory=factory,
                    runtime_validator=lambda _: None,
                )
        self.assertFalse(factory_called)

    def test_w1f_runtime_identity_stops_synthetic_binding_before_factory(self) -> None:
        with TemporaryDirectory() as directory:
            binding, _ = bound_runtime(Path(directory))
            factory_called = False

            def factory():
                nonlocal factory_called
                factory_called = True
                raise AssertionError("factory must not be called after identity drift")

            with self.assertRaisesRegex(BrowserPayloadSmokeError, "differs from W1-F"):
                run_browser_payload_smoke(
                    binding,
                    asset_directory=ASSETS,
                    playwright_factory=factory,
                )
        self.assertFalse(factory_called)

    def test_context_close_failure_still_closes_browser(self) -> None:
        with TemporaryDirectory() as directory:
            binding, _ = bound_runtime(Path(directory))
            manager = FakePlaywrightManager(
                binding.engine_version,
                fail_context_close=True,
            )
            with self.assertRaisesRegex(RuntimeError, "context close failure"):
                run_browser_payload_smoke(
                    binding,
                    asset_directory=ASSETS,
                    playwright_factory=lambda: manager,
                    runtime_validator=lambda _: None,
                )

        self.assertTrue(manager.page.closed)
        self.assertTrue(manager.browser.closed)
        self.assertTrue(manager.exited)

    def test_public_roles_and_runner_contain_no_raw_or_z4_path(self) -> None:
        roles = set(browser_payload_smoke_public_roles())
        self.assertTrue(
            {"raw_png", "raw_pcm", "receptor_values", "field_values"}.isdisjoint(
                roles
            )
        )
        root = Path(__file__).parents[1]
        source = "\n".join(
            (root / path).read_text(encoding="ascii")
            for path in (
                "mcm_field_organism/browser_payload_runtime.py",
                "mcm_field_organism/browser_payload_smoke.py",
                "tools/run_browser_payload_smoke.py",
            )
        )
        self.assertNotIn("z4a_", source)
        self.assertNotIn("reports/", source)
        self.assertNotIn("reports\\", source)


if __name__ == "__main__":
    unittest.main()
