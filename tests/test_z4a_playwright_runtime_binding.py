from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from importlib import metadata

from mcm_field_organism.z4a_playwright_runtime_binding import (
    Z4APlaywrightRuntimeBindingError,
    bind_installed_z4a_playwright_runtime,
    bind_z4a_playwright_runtime,
    z4a_playwright_runtime_binding_json_value,
)


def _manifest(entry: dict[str, object] | None = None) -> bytes:
    browser = entry or {
        "name": "chromium-headless-shell",
        "revision": "1234567",
        "browserVersion": "140.0.7339.5",
        "installByDefault": True,
    }
    return json.dumps(
        {"comment": "synthetic Playwright manifest", "browsers": [browser]},
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


class Z4APlaywrightRuntimeBindingTests(unittest.TestCase):
    def test_static_binding_reads_manifest_and_binary_without_execution(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "browsers.json"
            executable = root / "chromium-headless-shell" / "chrome.exe"
            executable.parent.mkdir()
            manifest_bytes = _manifest()
            binary_bytes = b"synthetic chromium binary\x00\x01"
            manifest.write_bytes(manifest_bytes)
            executable.write_bytes(binary_bytes)
            binding = bind_z4a_playwright_runtime(
                package_version="1.54.0",
                manifest_path=manifest,
                manifest_entry_name="chromium-headless-shell",
                executable_path=executable,
                installation_root=root,
            )
            self.assertEqual("140.0.7339.5", binding.engine_version)
            self.assertEqual("1234567", binding.browser_revision)
            self.assertEqual(sha256(manifest_bytes).hexdigest(), binding.manifest_sha256)
            self.assertEqual(sha256(binary_bytes).hexdigest(), binding.executable_sha256)
            self.assertFalse(binding.browser_started)

    def test_manifest_entry_must_be_unique_and_versioned(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "browsers.json"
            executable = root / "chrome.exe"
            executable.write_bytes(b"binary")
            duplicate = json.loads(_manifest().decode("ascii"))["browsers"][0]
            manifest.write_text(json.dumps({"browsers": [duplicate, duplicate]}), encoding="utf-8")
            with self.assertRaises(Z4APlaywrightRuntimeBindingError):
                bind_z4a_playwright_runtime(
                    package_version="1.54.0",
                    manifest_path=manifest,
                    manifest_entry_name="chromium-headless-shell",
                    executable_path=executable,
                    installation_root=root,
                )

    def test_binary_cannot_escape_installation_root(self) -> None:
        with TemporaryDirectory() as directory, TemporaryDirectory() as outside:
            root = Path(directory)
            manifest = root / "browsers.json"
            executable = Path(outside) / "chrome.exe"
            manifest.write_bytes(_manifest())
            executable.write_bytes(b"binary")
            with self.assertRaises(Z4APlaywrightRuntimeBindingError):
                bind_z4a_playwright_runtime(
                    package_version="1.54.0",
                    manifest_path=manifest,
                    manifest_entry_name="chromium-headless-shell",
                    executable_path=executable,
                    installation_root=root,
                )

    def test_json_projection_is_scalar_and_installed_lookup_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "browsers.json"
            executable = root / "chrome.exe"
            manifest.write_bytes(_manifest())
            executable.write_bytes(b"binary")
            binding = bind_z4a_playwright_runtime(
                package_version="1.54.0",
                manifest_path=manifest,
                manifest_entry_name="chromium-headless-shell",
                executable_path=executable,
                installation_root=root,
            )
            encoded = json.dumps(z4a_playwright_runtime_binding_json_value(binding))
            self.assertNotIn("synthetic chromium", encoded)
            self.assertNotIn('"binary"', encoded)
        with patch(
            "mcm_field_organism.z4a_playwright_runtime_binding.metadata.distribution",
            side_effect=metadata.PackageNotFoundError,
        ):
            with self.assertRaisesRegex(Z4APlaywrightRuntimeBindingError, "not installed"):
                bind_installed_z4a_playwright_runtime(
                    manifest_entry_name="chromium-headless-shell",
                    executable_path=Path("missing.exe"),
                    installation_root=Path("missing"),
                )


if __name__ == "__main__":
    unittest.main()
