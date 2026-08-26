from __future__ import annotations

import hashlib
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_memory_function_gap_audit import (
    S1_EC25_NEXT_FUNCTION,
    S1_EC25_NEXT_STEP,
    audit_e1_memory_function_gaps,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "synthetic_runs"
    / "s1ec23_full_published_probe_once_v1"
    / "e1_full_published_probe_s1ec23_once_v1.json"
)


class E1MemoryFunctionGapAuditTests(unittest.TestCase):
    def test_repetition_formation_is_selected_before_attenuation(self) -> None:
        result = audit_e1_memory_function_gaps(REPORT)
        statuses = dict(result.functions)

        self.assertEqual(S1_EC25_NEXT_FUNCTION, result.next_function)
        self.assertEqual(S1_EC25_NEXT_STEP, result.next_step)
        self.assertEqual(
            "OPEN_NEXT_CAUSAL_FUNCTION",
            statuses["repetition-dependent-formation"],
        )
        self.assertEqual(
            "BLOCKED_UNTIL_REPETITION_FORMATION",
            statuses["field-internal-attenuation"],
        )

    def test_confirmed_transfer_is_not_promoted_to_memory(self) -> None:
        result = audit_e1_memory_function_gaps(REPORT)
        statuses = dict(result.functions)

        self.assertEqual(
            "NUMERICALLY_CONFIRMED_NOT_MEMORY",
            statuses["changed-substrate-affects-later-field-intake"],
        )
        self.assertFalse(result.memory_claim_permitted)
        self.assertFalse(result.ai_claim_permitted)

    def test_current_linear_cue_branch_remains_stopped(self) -> None:
        result = audit_e1_memory_function_gaps(REPORT)

        self.assertIn(
            "more-partial-cue-amplitude-variants-of-current-linear-e1-path",
            result.stopped_continuations,
        )
        self.assertIn(
            "matching-fixed-adapter-as-transfer-control-only",
            result.required_comparisons,
        )

    def test_audit_has_no_runner_or_writer(self) -> None:
        source = inspect.getsource(audit_e1_memory_function_gaps)
        for forbidden in (
            "execute_",
            "run_",
            "write_text",
            "write_bytes",
            "mkdir",
            "_atomic_publish",
        ):
            self.assertNotIn(forbidden, source)

    def test_protected_report_remains_unchanged(self) -> None:
        before = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        audit_e1_memory_function_gaps(REPORT)
        after = hashlib.sha256(REPORT.read_bytes()).hexdigest()

        self.assertEqual(before, after)
        self.assertEqual(
            "85a114b9de5f2152558ca78a03a15f5690607fab98b7f9ddbf10cadf32e8b50e",
            after,
        )


if __name__ == "__main__":
    unittest.main()
