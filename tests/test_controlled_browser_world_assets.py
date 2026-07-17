from __future__ import annotations

from pathlib import Path
import unittest

from mcm_field_organism import (
    reference_browser_world_contract,
    reference_external_media_observation_contract,
)
from tools.controlled_browser_world.server import _public_program_payload


ROOT = Path(__file__).resolve().parents[1] / "tools" / "controlled_browser_world"


class ControlledBrowserWorldAssetTests(unittest.TestCase):
    def test_required_local_assets_exist(self) -> None:
        self.assertTrue((ROOT / "index.html").is_file())
        self.assertTrue((ROOT / "styles.css").is_file())
        self.assertTrue((ROOT / "stimulus.js").is_file())
        self.assertTrue((ROOT / "server.py").is_file())

    def test_browser_has_canvas_tone_and_explicit_server_start(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "stimulus.js").read_text(encoding="utf-8")
        self.assertIn("<canvas", html)
        self.assertIn("new AudioContext()", script)
        self.assertIn('fetch("/api/prepare"', script)
        self.assertIn('fetch("/api/start"', script)
        self.assertIn("requestFullscreen", script)
        self.assertIn('classList.add("complete")', script)
        self.assertIn('id="restart"', html)

    def test_browser_does_not_access_or_store_sensor_payloads(self) -> None:
        combined = "\n".join(
            (ROOT / name).read_text(encoding="utf-8")
            for name in ("index.html", "styles.css", "stimulus.js")
        )
        forbidden = (
            "getUserMedia",
            "MediaRecorder",
            "localStorage",
            "indexedDB",
            "download=",
            "FileReader",
        )
        for role in forbidden:
            self.assertNotIn(role, combined)

    def test_public_program_payload_separates_generated_and_external_roles(
        self,
    ) -> None:
        generated = _public_program_payload(
            reference_browser_world_contract(),
            start_epoch_ns=1_000_000,
        )
        external = _public_program_payload(
            reference_external_media_observation_contract(),
            start_epoch_ns=1_000_000,
        )
        self.assertIn("movement_cycles", generated)
        self.assertIn("tone_frequency_hz", generated)
        self.assertNotIn("movement_cycles", external)
        self.assertNotIn("tone_frequency_hz", external)
        self.assertEqual(
            (False, True, False),
            tuple(phase["media_contact"] for phase in external["phases"]),
        )


if __name__ == "__main__":
    unittest.main()
