from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from tools import _s2sfa_private_visual_run as run


def observations() -> dict[str, tuple[float, ...]]:
    result = {}
    for spec in run.PLAN:
        vector = np.zeros(288)
        vector[0] = (spec.ordinal - 1) % 4
        vector[1] = float(spec.episode in {"L2", "RB", "QB"})
        vector[2] = (spec.ordinal - 1) % 2
        result[spec.frame_id] = tuple(vector)
    return result


def ledger() -> tuple[run.LedgerEntry, ...]:
    return (run.LedgerEntry("references", 512 * 1024), run.LedgerEntry("qualification", 512 * 1024),
            run.LedgerEntry("verification", 256 * 1024), run.LedgerEntry("evaluation", 128 * 1024))


class SFAGlobalLedgerConnectionTests(unittest.TestCase):
    def test_full_entry_verification_and_evaluation_require_same_ledger(self) -> None:
        bound = ledger()
        record = run.run_materialized_once(run_id="ledger-neutral", plan_digest=run.PLAN_DIGEST, observations=observations(), authorized=True,
                                           ledger=bound, error_reserve_bytes=512 * 1024)
        with tempfile.TemporaryDirectory() as directory:
            published = Path(directory) / "record.json"
            size = run.publish_record_once(record, published, ledger=bound, error_reserve_bytes=512 * 1024)
            self.assertEqual(size, published.stat().st_size)
        verification = run.verify_read_only(record, ledger=bound, error_reserve_bytes=512 * 1024)
        evaluation = run.evaluate_verified(record, verification, ledger=bound, error_reserve_bytes=512 * 1024)
        self.assertTrue(verification["evaluation_allowed"])
        self.assertIn("losses", evaluation)

        incomplete = run.run_materialized_once(
            run_id="ledger-neutral-incomplete",
            plan_digest=run.PLAN_DIGEST,
            observations={spec.frame_id: tuple(np.zeros(288)) for spec in run.PLAN},
            authorized=True,
            ledger=bound,
            error_reserve_bytes=512 * 1024,
        )
        self.assertEqual(incomplete["status"], "INCOMPLETE")
        with tempfile.TemporaryDirectory() as directory:
            error_output = Path(directory) / "error.json"
            run.publish_record_once(incomplete, error_output, ledger=bound, error_reserve_bytes=512 * 1024)
            self.assertTrue(error_output.is_file())

    def test_missing_or_overflowing_ledger_rejects_before_processing(self) -> None:
        with self.assertRaisesRegex(run.SFAVisualRunError, "requires the bound ledger") as missing:
            run.run_materialized_once(run_id="missing", plan_digest=run.PLAN_DIGEST, observations=observations(), authorized=True,
                                      ledger=None, error_reserve_bytes=None)
        self.assertEqual(missing.exception.code, "LEDGER_REQUIRED")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(run.SFAVisualRunError, "requires the bound ledger") as publisher_missing:
                run.publish_record_once({"status": "INCOMPLETE"}, Path(directory) / "missing.json", ledger=None,
                                        error_reserve_bytes=None)
        self.assertEqual(publisher_missing.exception.code, "LEDGER_REQUIRED")
        with self.assertRaisesRegex(run.SFAVisualRunError, "ledger bytes") as overflow:
            run.run_materialized_once(run_id="overflow", plan_digest=run.PLAN_DIGEST, observations=observations(), authorized=True,
                                      ledger=(run.LedgerEntry("references", 7 * 1024 * 1024),), error_reserve_bytes=512 * 1024)
        self.assertEqual(overflow.exception.code, "EVIDENCE_LIMIT")


if __name__ == "__main__":
    unittest.main()
