from __future__ import annotations

import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_a0_av_history_evidence_audit import (
    E1A0AVHistoryEvidenceAuditError,
    S1_DJ_DECISION,
    S1_DJ_E1_INTEGRATOR_DIGEST,
    S1_DJ_FROZEN_PROBE_OPERATOR_DIGEST,
    S1_DJ_TRANSIENT_COUPLING_DIGEST,
    audit_e1_a0_av_history_evidence,
    current_s1_dj_implementation_digests,
)


REPORT = Path("reports/e1_a0_av_history_s1di_once_v1.json")


class E1A0AVHistoryEvidenceAuditTests(unittest.TestCase):
    def test_published_report_releases_only_narrow_state_transfer(self) -> None:
        result = audit_e1_a0_av_history_evidence(REPORT)

        self.assertEqual(S1_DJ_DECISION, result.decision)
        self.assertEqual(145, result.edge_count)
        self.assertEqual(0.000830161044915372, result.d_state)
        self.assertEqual(
            0.00037698677602994446,
            result.d_total_binding,
        )
        self.assertTrue(result.controls_complete)
        self.assertFalse(result.numerical_refinement_present)
        self.assertFalse(result.analytic_global_error_bound_present)
        self.assertFalse(result.history_rerun_permitted)
        self.assertFalse(result.full_s1_dc_probe_permitted)
        self.assertTrue(result.narrow_frozen_state_transfer_contract_permitted)
        self.assertEqual(64, len(result.audit_digest))

    def test_changed_or_missing_report_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(
                E1A0AVHistoryEvidenceAuditError,
                "missing",
            ):
                audit_e1_a0_av_history_evidence(root / "missing.json")

            changed = json.loads(REPORT.read_text(encoding="ascii"))
            changed["d_state"] = 0.0
            changed_path = root / "changed.json"
            changed_path.write_text(
                json.dumps(changed, separators=(",", ":")) + "\n",
                encoding="ascii",
            )
            with self.assertRaisesRegex(
                E1A0AVHistoryEvidenceAuditError,
                "report digest",
            ):
                audit_e1_a0_av_history_evidence(changed_path)

    def test_relevant_implementation_sources_are_exactly_bound(self) -> None:
        self.assertEqual(
            (
                S1_DJ_E1_INTEGRATOR_DIGEST,
                S1_DJ_TRANSIENT_COUPLING_DIGEST,
                S1_DJ_FROZEN_PROBE_OPERATOR_DIGEST,
            ),
            current_s1_dj_implementation_digests(),
        )

    def test_audit_has_no_field_history_or_probe_execution_reference(self) -> None:
        source = inspect.getsource(audit_e1_a0_av_history_evidence)
        for forbidden in (
            "produce_e1_a0_av_histories",
            "run_e1_asynchronous_field",
            "advance_frozen_e1_fast_shared_field_transient",
            "advance_fixed_e1_adapter_fast_shared_field_transient",
        ):
            self.assertNotIn(forbidden, source)

    def test_audit_roles_remain_private(self) -> None:
        for role in (
            "E1A0AVHistoryEvidenceAudit",
            "audit_e1_a0_av_history_evidence",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
