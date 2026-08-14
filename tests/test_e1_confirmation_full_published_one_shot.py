from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_full_formation_lifecycle import (
    consume_prepared_full_formation,
)
from mcm_field_organism.e1_confirmation_full_formation_resource_preflight import (
    preflight_prepared_full_formation_resources,
)
from mcm_field_organism.e1_confirmation_full_published_one_shot import (
    E1ConfirmationFullPublishedOneShotError,
    S1_EC19_SCHEMA_ID,
    execute_full_published_formation_once,
)
from mcm_field_organism.e1_confirmation_full_published_release_audit import (
    E1FullPublishedResourceSnapshot,
    audit_full_published_run_release,
)
from mcm_field_organism.e1_confirmation_prepared_formation_consumer import (
    _typed_values_from_bundle,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from mcm_field_organism.e1_confirmation_small_refinement_matrix import (
    run_small_real_refinement_matrix,
)
from tests.test_e1_confirmation_full_formation_handoff import (
    S1_EC13_REPORT,
    S1_EC13_REPORT_SHA256,
)
from tests.test_e1_confirmation_typed_prepared_inputs import (
    CANONICAL_TARGETS,
    UPSTREAM,
)


class E1ConfirmationFullPublishedOneShotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source_directory = TemporaryDirectory()
        descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
        run = prepare_e1_confirmation_synthetic_run_contract(
            descriptor, Path(cls.source_directory.name)
        )
        cls.bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
            run, UPSTREAM
        )
        cls.preflight = preflight_prepared_full_formation_resources(cls.bundle)
        values = _typed_values_from_bundle(cls.bundle)
        matrix = run_small_real_refinement_matrix(
            values.av_permutation.history_ab,
            values.av_permutation.history_ba,
            values.initial_field,
            values.initial_state,
        )
        marker = Path(cls.source_directory.name) / "synthetic.aggregate.attempt"
        marker.write_text("attempt\n", encoding="ascii")
        with patch(
            "mcm_field_organism.e1_confirmation_full_formation_lifecycle."
            "run_small_five_arm_formation_in_memory",
            side_effect=matrix.refinements,
        ):
            cls.formation = consume_prepared_full_formation(
                cls.bundle,
                cls.preflight,
                attempt_path=marker,
            )
        marker.unlink()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.source_directory.cleanup()

    def _release(self, directory: Path):
        snapshot = E1FullPublishedResourceSnapshot(
            free_memory_bytes=8 * 1024**3,
            free_disk_bytes=200 * 1024**3,
            proposed_directory=str(directory.resolve()),
            report_path_unused=True,
            attempt_path_unused=True,
            lock_path_unused=True,
            s1ec13_report_sha256=S1_EC13_REPORT_SHA256,
            s1ec13_reference_runtime_seconds=430.2,
        )
        release = audit_full_published_run_release(
            self.preflight,
            snapshot,
            expected_s1ec13_report_sha256=S1_EC13_REPORT_SHA256,
        )
        return snapshot, release

    def test_full_payload_is_published_and_reloaded_once(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot, release = self._release(root)
            with patch(
                "mcm_field_organism.e1_confirmation_full_published_one_shot."
                "consume_prepared_full_formation",
                return_value=self.formation,
            ) as consumer:
                receipt = execute_full_published_formation_once(
                    release,
                    snapshot,
                    self.bundle,
                    root,
                    owner_authorized=True,
                )
            report = json.loads(Path(receipt.report_path).read_text("ascii"))

            self.assertEqual(1, consumer.call_count)
            self.assertEqual(S1_EC19_SCHEMA_ID, report["schema_id"])
            self.assertEqual(
                snapshot.free_memory_bytes,
                report["resource_snapshot"]["free_memory_bytes"],
            )
            self.assertTrue(report["owner_authorized"])
            self.assertEqual(15, receipt.state_count)
            self.assertEqual(2_175, receipt.edge_binding_count)
            self.assertTrue(receipt.full_formation_executed)
            self.assertTrue(receipt.typed_reload_verified)
            self.assertFalse(receipt.probe_execution_permitted)
            self.assertFalse(receipt.claims_permitted)
            self.assertFalse(root.joinpath(
                "e1_full_formation_published_s1ec19_once_v1.attempt.json"
            ).exists())
            self.assertFalse(root.joinpath(
                "e1_full_formation_published_s1ec19_once_v1.lock"
            ).exists())

            with self.assertRaises(ValueError):
                execute_full_published_formation_once(
                    release,
                    snapshot,
                    self.bundle,
                    root,
                    owner_authorized=True,
                )

    def test_reload_failure_retains_attempt_and_blocks_retry(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot, release = self._release(root)
            with (
                patch(
                    "mcm_field_organism.e1_confirmation_full_published_one_shot."
                    "consume_prepared_full_formation",
                    return_value=self.formation,
                ),
                patch(
                    "mcm_field_organism.e1_confirmation_full_published_one_shot."
                    "load_full_formation_handoff_payload",
                    side_effect=ValueError("reload failure"),
                ),
            ):
                with self.assertRaisesRegex(ValueError, "reload failure"):
                    execute_full_published_formation_once(
                        release,
                        snapshot,
                        self.bundle,
                        root,
                        owner_authorized=True,
                    )

            self.assertTrue(root.joinpath(
                "e1_full_formation_published_s1ec19_once_v1.attempt.json"
            ).is_file())
            self.assertFalse(root.joinpath(
                "e1_full_formation_published_s1ec19_once_v1.lock"
            ).exists())

    def test_missing_owner_authorization_stops_before_directory_change(self) -> None:
        with TemporaryDirectory() as parent:
            root = Path(parent) / "unused"
            snapshot, release = self._release(root)
            with self.assertRaisesRegex(
                E1ConfirmationFullPublishedOneShotError, "not authorized"
            ):
                execute_full_published_formation_once(
                    release,
                    snapshot,
                    self.bundle,
                    root,
                    owner_authorized=False,
                )

            self.assertFalse(root.exists())

    def test_executor_contains_no_probe_or_claim_path(self) -> None:
        source = inspect.getsource(execute_full_published_formation_once)

        for forbidden in (
            "run_seven_arm_probe",
            "run_e1_confirmation_probe",
            "memory_claim",
            "ai_claim",
            "reports/",
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
        self.assertEqual(
            S1_EC13_REPORT_SHA256,
            hashlib.sha256(S1_EC13_REPORT.read_bytes()).hexdigest(),
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


if __name__ == "__main__":
    unittest.main()
