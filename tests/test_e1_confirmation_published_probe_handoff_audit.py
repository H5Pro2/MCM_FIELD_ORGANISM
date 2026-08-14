from __future__ import annotations

import hashlib
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_published_probe_handoff_audit import (
    E1ConfirmationPublishedProbeHandoffAuditError,
    S1_EC20_DECISION_CANDIDATE_ROLES,
    S1_EC20_PROBE_ARMS,
    S1_EC20_REPORT_SHA256,
    audit_published_probe_handoff,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from tests.test_e1_confirmation_full_formation_handoff import (
    S1_EC13_REPORT,
    S1_EC13_REPORT_SHA256,
)
from tests.test_e1_confirmation_typed_prepared_inputs import (
    CANONICAL_TARGETS,
    UPSTREAM,
)


ROOT = Path(__file__).resolve().parents[1]
S1_EC19_DIRECTORY = ROOT / "synthetic_runs" / "s1ec19_full_published_once_v1"
S1_EC19_REPORT = (
    S1_EC19_DIRECTORY / "e1_full_formation_published_s1ec19_once_v1.json"
)


class E1ConfirmationPublishedProbeHandoffAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        run = prepare_e1_confirmation_synthetic_run_contract(
            descriptor, S1_EC19_DIRECTORY
        )
        cls.bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
            run, UPSTREAM
        )
        cls.audit = audit_published_probe_handoff(S1_EC19_REPORT, cls.bundle)

    def test_complete_report_and_state_inventory_are_bound(self) -> None:
        self.assertEqual(S1_EC20_REPORT_SHA256, self.audit.report_sha256)
        self.assertEqual(15, self.audit.state_count)
        self.assertEqual(2_175, self.audit.edge_binding_count)
        self.assertEqual(15, len(self.audit.all_state_digests))
        self.assertEqual(7, self.audit.unique_state_digest_count)
        self.assertEqual(4, len(self.audit.state_equivalence_classes))

    def test_active_controls_candidates_and_seven_arms_are_separated(self) -> None:
        self.assertEqual(
            S1_EC20_DECISION_CANDIDATE_ROLES,
            self.audit.decision_candidate_roles,
        )
        self.assertEqual(S1_EC20_PROBE_ARMS, self.audit.probe_arms)
        self.assertEqual(6, len(self.audit.active_state_roles))
        self.assertEqual(4, len(self.audit.numerical_control_roles))
        self.assertFalse(self.audit.probe_execution_permitted)
        self.assertFalse(self.audit.result_decision_permitted)
        self.assertFalse(self.audit.claims_permitted)

    def test_changed_report_hash_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            E1ConfirmationPublishedProbeHandoffAuditError, "hash changed"
        ):
            audit_published_probe_handoff(
                S1_EC19_REPORT,
                self.bundle,
                expected_report_sha256="0" * 64,
            )

    def test_different_bundle_identity_is_rejected(self) -> None:
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        with TemporaryDirectory() as directory:
            run = prepare_e1_confirmation_synthetic_run_contract(
                descriptor, Path(directory)
            )
            bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
                run, UPSTREAM
            )
            with self.assertRaisesRegex(
                E1ConfirmationPublishedProbeHandoffAuditError,
                "report controls changed",
            ):
                audit_published_probe_handoff(S1_EC19_REPORT, bundle)

    def test_audit_contains_no_probe_execution_or_persistence(self) -> None:
        source = inspect.getsource(audit_published_probe_handoff)

        for forbidden in (
            "run_synthetic_e1_confirmation_seven_arm_probe",
            "advance_frozen_e1_fast_shared_field_transient",
            "_atomic_publish",
            "_exclusive_marker",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)

    def test_protected_artifacts_remain_unchanged(self) -> None:
        before = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )
        audit_published_probe_handoff(S1_EC19_REPORT, self.bundle)
        after = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )

        self.assertEqual(before, after)
        self.assertEqual(
            S1_EC13_REPORT_SHA256,
            hashlib.sha256(S1_EC13_REPORT.read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
