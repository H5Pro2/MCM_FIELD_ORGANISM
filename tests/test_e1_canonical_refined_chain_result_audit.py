from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_canonical_refined_chain_result_audit import (
    E1CanonicalRefinedChainResultAuditError,
    audit_e1_canonical_refined_chain_result,
)


REPORT = Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json")


class E1CanonicalRefinedChainResultAuditTests(unittest.TestCase):
    def test_terminal_report_is_valid_and_numerically_undecidable(self) -> None:
        audit = audit_e1_canonical_refined_chain_result(REPORT)

        self.assertEqual("NUMERICALLY_UNDECIDABLE", audit.technical_decision)
        self.assertTrue(audit.all_controls_passed)
        self.assertTrue(audit.exact_control_residuals_zero)
        self.assertTrue(audit.state_margin_passed)
        self.assertFalse(audit.probe_s_margin_passed)
        self.assertFalse(audit.probe_h_margin_passed)

    def test_probe_ratios_are_below_preregistered_margin(self) -> None:
        audit = audit_e1_canonical_refined_chain_result(REPORT)

        self.assertGreater(audit.fine_state_margin_ratio, 8.0)
        self.assertLess(audit.fine_probe_s_margin_ratio, 8.0)
        self.assertLess(audit.fine_probe_h_margin_ratio, 8.0)

    def test_rerun_and_claims_remain_forbidden(self) -> None:
        audit = audit_e1_canonical_refined_chain_result(REPORT)

        self.assertFalse(audit.rerun_permitted)
        self.assertFalse(audit.memory_claim_permitted)
        self.assertFalse(audit.ai_claim_permitted)

    def test_changed_report_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            changed = json.loads(REPORT.read_text(encoding="ascii"))
            changed["technical_decision"] = "CHANGED"
            path = Path(directory) / REPORT.name
            path.write_text(json.dumps(changed) + "\n", encoding="ascii")
            with self.assertRaisesRegex(
                E1CanonicalRefinedChainResultAuditError, "missing or changed"
            ):
                audit_e1_canonical_refined_chain_result(path)

    def test_audit_role_remains_private(self) -> None:
        for role in (
            "E1CanonicalRefinedChainResultAudit",
            "audit_e1_canonical_refined_chain_result",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
