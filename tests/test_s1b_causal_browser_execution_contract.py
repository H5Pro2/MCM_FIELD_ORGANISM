from __future__ import annotations

from importlib import metadata
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from mcm_field_organism.browser_payload_runtime import bind_browser_payload_runtime
from mcm_field_organism.current_api import (
    S1BCausalBrowserExecutionContractError,
    prepare_s1b_causal_browser_execution_contract,
)


ASSETS = Path(__file__).parents[1] / "tools" / "controlled_browser_payload_world"


def binding(root: Path):
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
    installation = root / "browser-cache"
    installation.mkdir()
    executable = installation / "headless.exe"
    executable.write_bytes(b"bound-w6g-headless-shell")
    return bind_browser_payload_runtime(
        package_version="1.62.0",
        requirements_path=requirements,
        manifest_path=manifest,
        executable_path=executable,
        installation_root=installation,
    )


class S1BCausalBrowserExecutionContractTests(unittest.TestCase):
    def test_matching_static_runtime_is_ready_without_creating_report_files(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            reports = root / "reports"
            reports.mkdir()
            with patch(
                "mcm_field_organism.s1b_causal_browser_execution_contract.metadata.version",
                return_value="1.62.0",
            ):
                contract = prepare_s1b_causal_browser_execution_contract(
                    binding(root),
                    asset_directory=ASSETS,
                    report_directory=reports,
                )

            self.assertEqual(
                "READY_FOR_EXPLICIT_ONE_SHOT_BROWSER_EXECUTION",
                contract.preflight_decision,
            )
            self.assertTrue(contract.execution_permitted)
            self.assertFalse(contract.browser_started)
            self.assertEqual(3, contract.context_count)
            self.assertFalse(Path(contract.report_path).exists())
            self.assertFalse(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())
            self.assertEqual(64, len(contract.digest()))

    def test_missing_python_package_blocks_execution_but_binds_contract(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            reports = root / "reports"
            reports.mkdir()
            with patch(
                "mcm_field_organism.s1b_causal_browser_execution_contract.metadata.version",
                side_effect=metadata.PackageNotFoundError("playwright"),
            ):
                contract = prepare_s1b_causal_browser_execution_contract(
                    binding(root),
                    asset_directory=ASSETS,
                    report_directory=reports,
                )

            self.assertEqual(
                "BLOCKED_PYTHON_PLAYWRIGHT_PACKAGE_MISSING",
                contract.preflight_decision,
            )
            self.assertFalse(contract.execution_permitted)
            self.assertIsNone(contract.python_playwright_version)
            self.assertFalse(contract.browser_started)

    def test_existing_report_reservation_stops_before_runtime_permission(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            reports = root / "reports"
            reports.mkdir()
            (reports / "s1b_causal_browser_w6i_once_v1.json.lock").write_text(
                "occupied",
                encoding="ascii",
            )
            with self.assertRaisesRegex(
                S1BCausalBrowserExecutionContractError,
                "already used",
            ):
                prepare_s1b_causal_browser_execution_contract(
                    binding(root),
                    asset_directory=ASSETS,
                    report_directory=reports,
                )


if __name__ == "__main__":
    unittest.main()
