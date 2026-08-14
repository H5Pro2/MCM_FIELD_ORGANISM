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
from mcm_field_organism.e1_confirmation_full_probe_release_audit import (
    E1FullProbeResourceSnapshot,
    S1_EC22_FIELD_ARM_STEP_COUNT,
    S1_EC22_POLICY_DIGEST,
    audit_full_probe_release,
)
from mcm_field_organism.e1_confirmation_published_probe_handoff_audit import (
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
SOURCE_DIRECTORY = ROOT / "synthetic_runs" / "s1ec19_full_published_once_v1"
SOURCE_REPORT = SOURCE_DIRECTORY / "e1_full_formation_published_s1ec19_once_v1.json"


class E1ConfirmationFullProbeReleaseAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        run = prepare_e1_confirmation_synthetic_run_contract(
            descriptor, SOURCE_DIRECTORY
        )
        cls.bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
            run, UPSTREAM
        )
        cls.handoff = audit_published_probe_handoff(SOURCE_REPORT, cls.bundle)

    def _snapshot(self, directory: Path) -> E1FullProbeResourceSnapshot:
        return E1FullProbeResourceSnapshot(
            free_memory_bytes=8 * 1024**3,
            free_disk_bytes=200 * 1024**3,
            proposed_directory=str(directory.resolve()),
            report_path_unused=True,
            attempt_path_unused=True,
            lock_path_unused=True,
            s1ec19_report_sha256=S1_EC20_REPORT_SHA256,
        )

    def test_all_static_gates_release_preparation_only(self) -> None:
        with TemporaryDirectory() as directory:
            result = audit_full_probe_release(
                self.handoff, self.bundle, self._snapshot(Path(directory))
            )

            self.assertEqual("FREIGABE", result.decision)
            self.assertEqual(S1_EC22_POLICY_DIGEST, result.policy_digest)
            self.assertEqual(
                S1_EC22_FIELD_ARM_STEP_COUNT, result.field_arm_step_count
            )
            self.assertTrue(all(value for _, value in result.checks))
            self.assertFalse(result.probe_execution_authorized)
            self.assertFalse(result.field_execution_performed)

    def test_insufficient_memory_yields_correction(self) -> None:
        with TemporaryDirectory() as directory:
            snapshot = replace(
                self._snapshot(Path(directory)),
                free_memory_bytes=4 * 1024**3 - 1,
            )
            result = audit_full_probe_release(
                self.handoff, self.bundle, snapshot
            )

            self.assertEqual("KORREKTUR", result.decision)
            self.assertIn("free-memory-at-least-four-gib", result.reason)

    def test_used_target_path_invalidates_snapshot(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = self._snapshot(root)
            root.joinpath(
                "e1_full_published_probe_s1ec23_once_v1.json"
            ).write_text("used\n", encoding="ascii")
            with self.assertRaises(ValueError):
                audit_full_probe_release(self.handoff, self.bundle, snapshot)

    def test_audit_has_no_probe_marker_or_writer_call(self) -> None:
        source = inspect.getsource(audit_full_probe_release)
        for forbidden in (
            "run_published_probe_fixture_consumer",
            "advance_frozen_e1_fast_shared_field_transient",
            "_exclusive_marker",
            "_atomic_publish",
            "mkdir",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)

    def test_protected_artifacts_remain_unchanged(self) -> None:
        paths = (*CANONICAL_TARGETS, S1_EC13_REPORT, SOURCE_REPORT)
        before = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in paths
        )
        with TemporaryDirectory() as directory:
            audit_full_probe_release(
                self.handoff, self.bundle, self._snapshot(Path(directory))
            )
        after = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in paths
        )

        self.assertEqual(before, after)
        self.assertEqual(
            S1_EC13_REPORT_SHA256,
            hashlib.sha256(S1_EC13_REPORT.read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
