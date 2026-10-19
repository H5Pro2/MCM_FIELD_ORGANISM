from __future__ import annotations

import unittest

from tools import _s2sfa_private_visual_run as run


class SFAGlobalLedgerTests(unittest.TestCase):
    def test_individually_valid_entries_can_exceed_global_limit(self) -> None:
        entries = (run.LedgerEntry("references", 3 * 1024 * 1024), run.LedgerEntry("qualification", 2 * 1024 * 1024), run.LedgerEntry("verification", 1 * 1024 * 1024), run.LedgerEntry("evaluation", 512 * 1024))
        with self.assertRaisesRegex(run.SFAVisualRunError, "ledger bytes") as failure:
            run.require_ledger(entries, record_bytes=1 * 1024 * 1024, temporary_bytes=1 * 1024 * 1024, error_reserve_bytes=512 * 1024)
        self.assertEqual(failure.exception.code, "EVIDENCE_LIMIT")

    def test_reference_temporary_peak_and_error_reserve_are_counted(self) -> None:
        entries = (run.LedgerEntry("references", 1 * 1024 * 1024), run.LedgerEntry("qualification", 512 * 1024), run.LedgerEntry("verification", 256 * 1024), run.LedgerEntry("evaluation", 128 * 1024))
        total = run.require_ledger(entries, record_bytes=2 * 1024 * 1024, temporary_bytes=2 * 1024 * 1024, error_reserve_bytes=512 * 1024)
        self.assertEqual(total, 6_684_672)


if __name__ == "__main__":
    unittest.main()
