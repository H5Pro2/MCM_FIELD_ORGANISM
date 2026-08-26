from __future__ import annotations

from dataclasses import replace
import hashlib
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_full_formation_resource_preflight import (
    preflight_prepared_full_formation_resources,
)
from mcm_field_organism.e1_confirmation_full_published_release_audit import (
    E1FullPublishedResourceSnapshot,
    S1_EC18_POLICY_DIGEST,
    audit_full_published_run_release,
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


class E1ConfirmationFullPublishedReleaseAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        with TemporaryDirectory() as directory:
            run = prepare_e1_confirmation_synthetic_run_contract(
                descriptor, Path(directory)
            )
            bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
                run, UPSTREAM
            )
            cls.preflight = preflight_prepared_full_formation_resources(bundle)

    def _snapshot(self, directory: Path) -> E1FullPublishedResourceSnapshot:
        return E1FullPublishedResourceSnapshot(
            free_memory_bytes=8 * 1024**3,
            free_disk_bytes=200 * 1024**3,
            proposed_directory=str(directory),
            report_path_unused=True,
            attempt_path_unused=True,
            lock_path_unused=True,
            s1ec13_report_sha256=S1_EC13_REPORT_SHA256,
            s1ec13_reference_runtime_seconds=430.2,
        )

    def test_all_gates_yield_release_without_authorizing_execution(self) -> None:
        with TemporaryDirectory() as directory:
            result = audit_full_published_run_release(
                self.preflight,
                self._snapshot(Path(directory)),
                expected_s1ec13_report_sha256=S1_EC13_REPORT_SHA256,
            )

            self.assertEqual("FREIGABE", result.decision)
            self.assertEqual(S1_EC18_POLICY_DIGEST, result.policy_digest)
            self.assertTrue(all(value for _, value in result.checks))
            self.assertFalse(result.execution_authorized)
            self.assertFalse(result.field_execution_performed)

    def test_insufficient_memory_yields_correction(self) -> None:
        with TemporaryDirectory() as directory:
            snapshot = replace(
                self._snapshot(Path(directory)),
                free_memory_bytes=4 * 1024**3 - 1,
            )
            result = audit_full_published_run_release(
                self.preflight,
                snapshot,
                expected_s1ec13_report_sha256=S1_EC13_REPORT_SHA256,
            )

            self.assertEqual("KORREKTUR", result.decision)
            self.assertIn("free-memory-at-least-four-gib", result.reason)

    def test_changed_reference_report_yields_correction(self) -> None:
        with TemporaryDirectory() as directory:
            result = audit_full_published_run_release(
                self.preflight,
                self._snapshot(Path(directory)),
                expected_s1ec13_report_sha256="0" * 64,
            )

            self.assertEqual("KORREKTUR", result.decision)
            self.assertIn("s1ec13-reference-report-unchanged", result.reason)

    def test_audit_has_no_execution_marker_or_publication_call(self) -> None:
        source = inspect.getsource(audit_full_published_run_release)

        for forbidden in (
            "_run_arm",
            "run_small_five_arm_formation_in_memory",
            "execute_full_published_run_fixture_once",
            "_exclusive_marker",
            "_atomic_publish",
            "mkdir",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)

    def test_s1ec13_and_terminal_artifacts_remain_unchanged(self) -> None:
        before = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )
        with TemporaryDirectory() as directory:
            audit_full_published_run_release(
                self.preflight,
                self._snapshot(Path(directory)),
                expected_s1ec13_report_sha256=S1_EC13_REPORT_SHA256,
            )
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
