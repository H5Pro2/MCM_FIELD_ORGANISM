from __future__ import annotations

from pathlib import Path
import unittest


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


if __name__ == "__main__":
    unittest.main()
