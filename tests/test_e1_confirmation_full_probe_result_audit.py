from __future__ import annotations

import hashlib
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.e1_confirmation_full_probe_result_audit import (
    E1ConfirmationFullProbeResultAuditError,
    S1_EC24_REPORT_SHA256,
    audit_full_published_probe_result,
    decide_persistent_probe_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "synthetic_runs"
    / "s1ec23_full_published_probe_once_v1"
    / "e1_full_published_probe_s1ec23_once_v1.json"
)


class E1ConfirmationFullProbeResultAuditTests(unittest.TestCase):
    def test_protected_report_passes_registered_probe_decision(self) -> None:
        result = audit_full_published_probe_result(REPORT)

        self.assertEqual(
            "CONFIRMED_NUMERICALLY_CLEAR_PERSISTENT_STATE_PROBE_DIFFERENCE",
            result.technical_decision,
        )
        self.assertGreater(result.active_s_margin_ratio, 8.0)
        self.assertGreater(result.active_h_margin_ratio, 8.0)
        self.assertTrue(all(value for _, value in result.checks))
        self.assertFalse(result.memory_claim_permitted)
        self.assertFalse(result.ai_claim_permitted)

    def test_strict_threshold_rejects_equality(self) -> None:
        self.assertEqual(
            "NUMERICALLY_UNDECIDABLE",
            decide_persistent_probe_evidence(
                active_s=8.0,
                active_h=8.1,
                coarse_residual=2.0,
                fine_residual=1.0,
                controls_passed=True,
            ),
        )

    def test_failed_controls_fail_closed(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationFullProbeResultAuditError, "failed controls"
        ):
            decide_persistent_probe_evidence(
                active_s=9.0,
                active_h=9.0,
                coarse_residual=2.0,
                fine_residual=1.0,
                controls_passed=False,
            )

    def test_changed_report_is_rejected_without_output(self) -> None:
        with TemporaryDirectory() as directory:
            changed = Path(directory) / REPORT.name
            changed.write_bytes(REPORT.read_bytes() + b"\n")
            with self.assertRaisesRegex(
                E1ConfirmationFullProbeResultAuditError, "hash changed"
            ):
                audit_full_published_probe_result(changed)
            self.assertEqual((changed,), tuple(Path(directory).iterdir()))

    def test_audit_contains_no_field_execution_or_writer(self) -> None:
        source = inspect.getsource(audit_full_published_probe_result)
        for forbidden in (
            "run_full_persistent_probe",
            "execute_full_published_probe_once",
            "_atomic_publish",
            "_exclusive_marker",
            "write_text",
            "write_bytes",
            "mkdir",
        ):
            self.assertNotIn(forbidden, source)

    def test_protected_report_remains_unchanged(self) -> None:
        before = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        audit_full_published_probe_result(REPORT)
        after = hashlib.sha256(REPORT.read_bytes()).hexdigest()

        self.assertEqual(S1_EC24_REPORT_SHA256, before)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
