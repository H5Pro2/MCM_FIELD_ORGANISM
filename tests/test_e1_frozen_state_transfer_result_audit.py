from __future__ import annotations

import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_frozen_state_transfer_result_audit import (
    E1FrozenStateTransferResultAuditError,
    S1_DQ_REPORT_SHA256,
    S1_DQ_RESULT_SHA256,
    S1_DQ_STATUS,
    audit_e1_frozen_state_transfer_result,
)


REPORT = Path("reports/e1_frozen_state_transfer_s1dn_once_v1.json")


class E1FrozenStateTransferResultAuditTests(unittest.TestCase):
    def test_published_report_reconstructs_the_registered_transfer(self) -> None:
        result = audit_e1_frozen_state_transfer_result(REPORT)

        self.assertEqual(S1_DQ_REPORT_SHA256, result.report_sha256)
        self.assertEqual(S1_DQ_RESULT_SHA256, result.result_sha256)
        self.assertEqual(S1_DQ_STATUS, result.technical_status)
        self.assertEqual(6.0604584716517085e-06, result.d_active_s)
        self.assertEqual(6.506083701604548e-06, result.d_active_h)
        self.assertEqual(9.71445146547012e-17, result.d_probe_partition)
        self.assertTrue(result.controls_complete)
        self.assertTrue(result.attempt_marker_absent)
        self.assertTrue(result.lock_marker_absent)

    def test_audit_digest_is_repeatable(self) -> None:
        first = audit_e1_frozen_state_transfer_result(REPORT)
        second = audit_e1_frozen_state_transfer_result(REPORT)

        self.assertEqual(first.audit_digest, second.audit_digest)
        self.assertEqual(64, len(first.audit_digest))

    def test_missing_or_changed_report_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(
                E1FrozenStateTransferResultAuditError,
                "missing",
            ):
                audit_e1_frozen_state_transfer_result(root / "missing.json")

            changed = json.loads(REPORT.read_text(encoding="ascii"))
            changed["metrics"][2][1] = 0.0
            path = root / REPORT.name
            path.write_text(
                json.dumps(changed, separators=(",", ":")) + "\n",
                encoding="ascii",
            )
            with self.assertRaisesRegex(
                E1FrozenStateTransferResultAuditError,
                "report digest",
            ):
                audit_e1_frozen_state_transfer_result(path)

    def test_result_does_not_release_strong_claims(self) -> None:
        result = audit_e1_frozen_state_transfer_result(REPORT)

        self.assertFalse(result.full_s1_dc_decision_permitted)
        self.assertFalse(result.memory_claim_permitted)

    def test_audit_has_no_producer_executor_or_field_execution_reference(self) -> None:
        source = inspect.getsource(audit_e1_frozen_state_transfer_result)
        for forbidden in (
            "produce_e1_frozen_state_transfer",
            "execute_e1_frozen_state_transfer_one_shot",
            "advance_frozen_e1_fast_shared_field_transient",
            "_partition_run",
        ):
            self.assertNotIn(forbidden, source)

    def test_audit_roles_remain_private(self) -> None:
        for role in (
            "E1FrozenStateTransferResultAudit",
            "audit_e1_frozen_state_transfer_result",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
