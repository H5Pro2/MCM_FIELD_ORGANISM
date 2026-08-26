from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.browser_payload_runtime import bind_browser_payload_runtime
from mcm_field_organism.current_api import (
    S1BCausalBrowserOneShotError,
    execute_s1b_causal_browser_one_shot,
    prepare_s1b_causal_browser_execution_contract,
)
from tests.test_s1b_causal_capture_handoff import FakePage


ASSETS = Path(__file__).parents[1] / "tools" / "controlled_browser_payload_world"


def binding(root: Path):
    requirements = root / "requirements-browser.txt"
    requirements.write_text("playwright==1.62.0\n", encoding="ascii")
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
        encoding="ascii",
    )
    installation = root / "browser-cache"
    installation.mkdir()
    executable = installation / "headless.exe"
    executable.write_bytes(b"bound-w6i-headless-shell")
    return bind_browser_payload_runtime(
        package_version="1.62.0",
        requirements_path=requirements,
        manifest_path=manifest,
        executable_path=executable,
        installation_root=installation,
    )


class ClosableFakePage(FakePage):
    def __init__(self) -> None:
        super().__init__()
        self.closed = False

    def close(self) -> None:
        self.closed = True


class FakeContext:
    def __init__(self) -> None:
        self.page = ClosableFakePage()
        self.closed = False

    def new_page(self) -> ClosableFakePage:
        return self.page

    def close(self) -> None:
        self.closed = True


class FakeBrowser:
    def __init__(self, version: str = "151.0.7922.34") -> None:
        self.version = version
        self.contexts: list[FakeContext] = []
        self.closed = False

    def new_context(self, **kwargs: object) -> FakeContext:
        context = FakeContext()
        self.contexts.append(context)
        return context

    def close(self) -> None:
        self.closed = True


class FakeChromium:
    def __init__(self, browser: FakeBrowser) -> None:
        self.browser = browser
        self.launch_count = 0

    def launch(self, **kwargs: object) -> FakeBrowser:
        self.launch_count += 1
        return self.browser


class FakePlaywrightManager:
    def __init__(self, version: str = "151.0.7922.34") -> None:
        self.browser = FakeBrowser(version)
        self.chromium = FakeChromium(self.browser)
        self.exited = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.exited = True


def contract_and_binding(root: Path):
    reports = root / "reports"
    reports.mkdir()
    runtime_binding = binding(root)
    contract = prepare_s1b_causal_browser_execution_contract(
        runtime_binding,
        asset_directory=ASSETS,
        report_directory=reports,
    )
    return contract, runtime_binding


class S1BCausalBrowserOneShotTests(unittest.TestCase):
    def test_fake_lifecycle_publishes_exact_scalar_report_once(self) -> None:
        with TemporaryDirectory() as directory:
            contract, runtime_binding = contract_and_binding(Path(directory))
            manager = FakePlaywrightManager()
            receipt = execute_s1b_causal_browser_one_shot(
                contract,
                runtime_binding,
                asset_directory=ASSETS,
                playwright_factory=lambda: manager,
            )
            report = json.loads(Path(contract.report_path).read_text(encoding="ascii"))

            self.assertEqual(tuple(report), contract.report_fields)
            self.assertEqual(contract.digest(), receipt.contract_digest)
            self.assertEqual(1, manager.chromium.launch_count)
            self.assertEqual(3, len(manager.browser.contexts))
            self.assertTrue(manager.browser.closed)
            self.assertTrue(manager.exited)
            self.assertTrue(all(item.closed for item in manager.browser.contexts))
            self.assertTrue(all(item.page.closed for item in manager.browser.contexts))
            self.assertFalse(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())
            self.assertFalse(report["raw_payloads_retained"])
            self.assertTrue(report["audio_buffers_released"])
            self.assertTrue(report["browser_closed"])

            with self.assertRaisesRegex(S1BCausalBrowserOneShotError, "already used"):
                execute_s1b_causal_browser_one_shot(
                    contract,
                    runtime_binding,
                    asset_directory=ASSETS,
                    playwright_factory=lambda: FakePlaywrightManager(),
                )

    def test_started_failure_keeps_attempt_marker_for_manual_review(self) -> None:
        with TemporaryDirectory() as directory:
            contract, runtime_binding = contract_and_binding(Path(directory))
            manager = FakePlaywrightManager("wrong-engine")

            with self.assertRaisesRegex(
                S1BCausalBrowserOneShotError,
                "observed browser version",
            ):
                execute_s1b_causal_browser_one_shot(
                    contract,
                    runtime_binding,
                    asset_directory=ASSETS,
                    playwright_factory=lambda: manager,
                )

            self.assertTrue(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.report_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())
            self.assertTrue(manager.browser.closed)


if __name__ == "__main__":
    unittest.main()
