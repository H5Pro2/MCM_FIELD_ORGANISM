from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


TOOL_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "run_opencv_keyboard_focus_probe.py"
)
SPEC = importlib.util.spec_from_file_location("opencv_keyboard_focus_probe", TOOL_PATH)
assert SPEC is not None and SPEC.loader is not None
TOOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOL)


class OpenCVKeyboardFocusProbeToolTests(unittest.TestCase):
    def test_default_duration_is_bounded(self) -> None:
        args = TOOL.parse_args([])
        self.assertEqual(args.duration_seconds, 15.0)

    def test_rejects_non_positive_duration(self) -> None:
        with self.assertRaises(SystemExit):
            TOOL.parse_args(["--duration-seconds", "0"])

    def test_reports_only_explicit_probe_keys(self) -> None:
        self.assertEqual(TOOL.key_event_from_key(ord("a")), "KEY_A_RECEIVED")
        self.assertEqual(TOOL.key_event_from_key(ord("R")), "KEY_R_RECEIVED")
        self.assertEqual(TOOL.key_event_from_key(27), "KEY_ESCAPE_RECEIVED")
        self.assertEqual(TOOL.key_event_from_key(ord("x")), "NO_KEY_RECEIVED")

    def test_contract_excludes_camera_and_project_runtime(self) -> None:
        source = TOOL_PATH.read_text(encoding="utf-8")
        self.assertNotIn("VideoCapture", source)
        self.assertNotIn("OpenCVVideoFrameSource", source)
        self.assertNotIn("HUMAN_ACCEPTED", source)
        self.assertNotIn("HUMAN_REJECTED", source)
        self.assertNotIn("mcm_field_organism", source)


if __name__ == "__main__":
    unittest.main()
