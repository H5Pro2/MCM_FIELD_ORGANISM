from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


TOOL_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "run_physical_setup_acceptance.py"
)
SPEC = importlib.util.spec_from_file_location("physical_setup_acceptance", TOOL_PATH)
assert SPEC is not None and SPEC.loader is not None
TOOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOL)


class PhysicalSetupAcceptanceToolTests(unittest.TestCase):
    def test_requires_explicit_camera_device(self) -> None:
        with self.assertRaises(SystemExit):
            TOOL.parse_args([])

    def test_rejects_negative_camera_device(self) -> None:
        with self.assertRaises(SystemExit):
            TOOL.parse_args(["--camera-device", "-1"])

    def test_only_explicit_human_keys_decide(self) -> None:
        self.assertEqual(TOOL.decision_from_key(ord("a")), "HUMAN_ACCEPTED")
        self.assertEqual(TOOL.decision_from_key(ord("R")), "HUMAN_REJECTED")
        self.assertEqual(TOOL.decision_from_key(27), "HUMAN_REJECTED")
        self.assertEqual(TOOL.decision_from_key(ord("x")), "NO_DECISION")

    def test_contract_has_no_field_or_receptor_language(self) -> None:
        source = TOOL_PATH.read_text(encoding="utf-8")
        self.assertNotIn("LocalChannelGridReceptor", source)
        self.assertNotIn("SharedMCMFieldSnapshot", source)
        self.assertNotIn("present_independent_visual", source)
        self.assertEqual(len(TOOL.CHECKLIST), 10)


if __name__ == "__main__":
    unittest.main()
