from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools import _s2sfa_private_visual_run as run


class SFABudgetProfileTests(unittest.TestCase):
    def test_record_limit_equality_and_overflow(self) -> None:
        exact = {"payload": "x" * (run.MAX_RECORD_BYTES - len(run._canonical({"payload": ""})))}
        self.assertEqual(run._require_record_budget(exact), run.MAX_RECORD_BYTES)
        with self.assertRaisesRegex(run.SFAVisualRunError, "exceed") as failure:
            run._require_record_budget({"payload": exact["payload"] + "x"})
        self.assertEqual(failure.exception.code, "RECORD_LIMIT")

    def test_atomic_publication_and_error_form(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "record.json"
            size = run.publish_record_once({"status": "INCOMPLETE", "phase": "LEARNING", "progress": 4, "error": {"code": "SFA_TRAINING_DEGENERATE"}}, output)
            self.assertTrue(output.exists())
            self.assertEqual(output.stat().st_size, size)
            with self.assertRaisesRegex(run.SFAVisualRunError, "already exists"):
                run.publish_record_once({"status": "INCOMPLETE"}, output)


if __name__ == "__main__":
    unittest.main()
