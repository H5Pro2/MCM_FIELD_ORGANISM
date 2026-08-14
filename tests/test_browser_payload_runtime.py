from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism import (
    BrowserPayloadRuntimeBindingError,
    bind_browser_payload_runtime,
    browser_payload_runtime_binding_json_value,
)


def runtime_tree(root: Path):
    installation = root / "browsers"
    installation.mkdir()
    executable = installation / "headless.exe"
    executable.write_bytes(b"bound-headless-shell")
    requirements = root / "requirements-browser.txt"
    requirements.write_text(
        "# generic browser runtime\nplaywright==1.62.0\n",
        encoding="utf-8",
    )
    manifest = root / "browsers.json"
    manifest.write_text(
        json.dumps(
            {
                "comment": "test",
                "browsers": [
                    {
                        "name": "chromium-headless-shell",
                        "revision": "1234",
                        "browserVersion": "151.0.7922.34",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return requirements, manifest, executable, installation


class BrowserPayloadRuntimeTests(unittest.TestCase):
    def test_static_binding_is_deterministic_and_never_starts_browser(self) -> None:
        with TemporaryDirectory() as directory:
            paths = runtime_tree(Path(directory))
            first = bind_browser_payload_runtime(
                package_version="1.62.0",
                requirements_path=paths[0],
                manifest_path=paths[1],
                executable_path=paths[2],
                installation_root=paths[3],
            )
            second = bind_browser_payload_runtime(
                package_version="1.62.0",
                requirements_path=paths[0],
                manifest_path=paths[1],
                executable_path=paths[2],
                installation_root=paths[3],
            )

        self.assertEqual(first, second)
        self.assertEqual("chromium-headless-shell", first.manifest_entry_name)
        self.assertEqual("151.0.7922.34", first.engine_version)
        self.assertEqual("1234", first.browser_revision)
        self.assertFalse(first.browser_started)
        self.assertEqual(first.requirements_sha256, second.requirements_sha256)
        self.assertEqual(first.manifest_sha256, second.manifest_sha256)
        self.assertEqual(first.executable_sha256, second.executable_sha256)
        self.assertFalse(
            browser_payload_runtime_binding_json_value(first)["browser_started"]
        )

    def test_requirements_pin_and_installation_root_fail_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, manifest, executable, installation = runtime_tree(root)
            requirements.write_text("playwright==1.61.0\n", encoding="utf-8")
            with self.assertRaisesRegex(
                BrowserPayloadRuntimeBindingError, "exact requirements pin"
            ):
                bind_browser_payload_runtime(
                    package_version="1.62.0",
                    requirements_path=requirements,
                    manifest_path=manifest,
                    executable_path=executable,
                    installation_root=installation,
                )

            requirements.write_text("playwright==1.62.0\n", encoding="utf-8")
            outside = root / "outside.exe"
            outside.write_bytes(b"outside")
            with self.assertRaisesRegex(
                BrowserPayloadRuntimeBindingError, "escaped"
            ):
                bind_browser_payload_runtime(
                    package_version="1.62.0",
                    requirements_path=requirements,
                    manifest_path=manifest,
                    executable_path=outside,
                    installation_root=installation,
                )

    def test_manifest_requires_one_exact_headless_shell_entry(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            requirements, manifest, executable, installation = runtime_tree(root)
            manifest.write_text(json.dumps({"browsers": []}), encoding="utf-8")
            with self.assertRaisesRegex(
                BrowserPayloadRuntimeBindingError, "not unique"
            ):
                bind_browser_payload_runtime(
                    package_version="1.62.0",
                    requirements_path=requirements,
                    manifest_path=manifest,
                    executable_path=executable,
                    installation_root=installation,
                )


if __name__ == "__main__":
    unittest.main()
