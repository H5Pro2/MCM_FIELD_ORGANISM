from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import unittest

from reports import run_s2sp_shift_hint_once as runner


class ShiftHintRunnerBindingTests(unittest.TestCase):
    def test_module_import_in_a_fresh_process_does_not_run_materialization(self) -> None:
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "-B", "-c", "import reports.run_s2sp_shift_hint_once; print('IMPORTED')"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "IMPORTED")
        self.assertFalse((root / "reports" / runner.RUN_ID).exists())

    def test_report_renders_positive_and_negative_decisions_from_rows(self) -> None:
        evaluation = {
            "rows": [
                {"condition_id": "positive", "hint_status": "HINT_SINGLE", "exact_baseline_candidate_ids": []},
                {"condition_id": "negative", "hint_status": "HINT_NOT_APPLICABLE", "exact_baseline_candidate_ids": []},
                {"condition_id": "ambiguous", "hint_status": "HINT_CANDIDATE_AMBIGUOUS", "exact_baseline_candidate_ids": ["candidate"]},
            ]
        }
        report = runner.render_report(evaluation)
        self.assertIn("Eindeutige Teilstrukturhinweise: positive.", report)
        self.assertIn("Enthaltungen ohne anwendbaren Teilstrukturhinweis: negative.", report)
        self.assertIn("Kandidatenmehrdeutigkeiten: ambiguous.", report)
        self.assertIn("Exaktbaseline mit mindestens einem Kandidaten: ambiguous.", report)


if __name__ == "__main__":
    unittest.main()
