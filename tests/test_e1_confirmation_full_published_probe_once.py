from __future__ import annotations

import hashlib
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_descriptor_refinement_planner import (
    build_e1_confirmation_descriptor_refinement_plans,
)
from mcm_field_organism.e1_confirmation_full_probe_release_audit import (
    E1FullProbeResourceSnapshot,
    audit_full_probe_release,
)
from mcm_field_organism.e1_confirmation_full_published_probe_once import (
    E1ConfirmationFullPublishedProbeOnceError,
    E1FullPublishedProbeRawResult,
    execute_full_published_probe_once,
)
from mcm_field_organism.e1_confirmation_prepared_formation_consumer import (
    _typed_values_from_bundle,
)
from mcm_field_organism.e1_confirmation_published_probe_fixture_consumer import (
    run_published_probe_fixture_consumer,
)
from mcm_field_organism.e1_confirmation_published_probe_handoff_audit import (
    S1_EC20_REPORT_SHA256,
    audit_published_probe_handoff,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)
from mcm_field_organism.e1_confirmation_small_refinement_matrix import (
    run_small_real_refinement_matrix,
)
from mcm_field_organism.e1_refined_formation_runner import _digest
from mcm_field_organism.receptor_time_model import ReceptorTimeSequence
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


class E1ConfirmationFullPublishedProbeOnceTests(unittest.TestCase):
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
        values = _typed_values_from_bundle(cls.bundle)
        fixture = run_small_real_refinement_matrix(
            values.av_permutation.history_ab,
            values.av_permutation.history_ba,
            values.initial_field,
            values.initial_state,
        )
        fixture_probe = tuple(
            ReceptorTimeSequence(
                item.modality_id,
                item.geometry_id,
                item.clock_id,
                (item.frames[0],),
            )
            for item in values.probe_sequences
        )
        fixture_plans = build_e1_confirmation_descriptor_refinement_plans(
            values.corridor,
            fixture_probe,
            horizon_start_tick=0,
            horizon_end_tick=1_000_000,
            ticks_per_second=1_000_000.0,
        )
        fixture_result = run_published_probe_fixture_consumer(
            cls.handoff,
            cls.bundle,
            fixture,
            fixture_probe,
            fixture_plans,
        )
        payload = {
            "source_report_sha256": cls.handoff.report_sha256,
            "source_formation_result_digest": cls.handoff.formation_result_digest,
            "probe_source_digest": cls.handoff.probe_source_digest,
            "probe_plan_set_digest": cls.handoff.probe_plan_set_digest,
            "source_state_digests_before": cls.handoff.all_state_digests,
            "source_state_digests_after": cls.handoff.all_state_digests,
            "r2_r4_probe_residual": fixture_result.r2_r4_probe_residual,
            "r4_r8_probe_residual": fixture_result.r4_r8_probe_residual,
            "convergence_nonincreasing": fixture_result.convergence_nonincreasing,
            "all_registered_controls_passed": True,
            "persistent_states_consumed": True,
            "registered_probe_consumed": True,
            "result_decision_permitted": False,
            "claims_permitted": False,
        }
        digest_payload = dict(payload)
        digest_payload["refinement_result_digests"] = tuple(
            item.result_digest for item in fixture_result.refinements
        )
        cls.raw = E1FullPublishedProbeRawResult(
            **payload,
            refinements=fixture_result.refinements,
            result_digest=_digest(digest_payload),
        )

    def _release(self, directory: Path):
        snapshot = E1FullProbeResourceSnapshot(
            free_memory_bytes=8 * 1024**3,
            free_disk_bytes=200 * 1024**3,
            proposed_directory=str(directory.resolve()),
            report_path_unused=True,
            attempt_path_unused=True,
            lock_path_unused=True,
            s1ec19_report_sha256=S1_EC20_REPORT_SHA256,
        )
        release = audit_full_probe_release(
            self.handoff, self.bundle, snapshot
        )
        return snapshot, release

    def test_raw_metrics_publish_and_reload_once(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot, release = self._release(root)
            receipt = execute_full_published_probe_once(
                release,
                snapshot,
                self.handoff,
                self.bundle,
                SOURCE_REPORT,
                root,
                owner_authorized=True,
                probe_runner=lambda *_args: self.raw,
            )

            self.assertTrue(Path(receipt.report_path).is_file())
            self.assertTrue(receipt.typed_reload_verified)
            self.assertFalse(receipt.result_decision_permitted)
            self.assertFalse(receipt.claims_permitted)
            self.assertFalse(root.joinpath(
                "e1_full_published_probe_s1ec23_once_v1.attempt.json"
            ).exists())
            self.assertFalse(root.joinpath(
                "e1_full_published_probe_s1ec23_once_v1.lock"
            ).exists())

            with self.assertRaises(ValueError):
                execute_full_published_probe_once(
                    release,
                    snapshot,
                    self.handoff,
                    self.bundle,
                    SOURCE_REPORT,
                    root,
                    owner_authorized=True,
                    probe_runner=lambda *_args: self.raw,
                )

    def test_reload_failure_retains_attempt(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot, release = self._release(root)
            with patch(
                "mcm_field_organism.e1_confirmation_full_published_probe_once."
                "load_full_published_probe_raw_result",
                side_effect=ValueError("reload failure"),
            ):
                with self.assertRaisesRegex(ValueError, "reload failure"):
                    execute_full_published_probe_once(
                        release,
                        snapshot,
                        self.handoff,
                        self.bundle,
                        SOURCE_REPORT,
                        root,
                        owner_authorized=True,
                        probe_runner=lambda *_args: self.raw,
                    )

            self.assertTrue(root.joinpath(
                "e1_full_published_probe_s1ec23_once_v1.attempt.json"
            ).is_file())
            self.assertFalse(root.joinpath(
                "e1_full_published_probe_s1ec23_once_v1.lock"
            ).exists())

    def test_missing_owner_authorization_stops_before_target_change(self) -> None:
        with TemporaryDirectory() as parent:
            root = Path(parent) / "unused"
            snapshot, release = self._release(root)
            with self.assertRaisesRegex(
                E1ConfirmationFullPublishedProbeOnceError, "not authorized"
            ):
                execute_full_published_probe_once(
                    release,
                    snapshot,
                    self.handoff,
                    self.bundle,
                    SOURCE_REPORT,
                    root,
                    owner_authorized=False,
                    probe_runner=lambda *_args: self.raw,
                )
            self.assertFalse(root.exists())

    def test_executor_contains_no_decision_or_claim_path(self) -> None:
        source = inspect.getsource(execute_full_published_probe_once)
        self.assertNotIn("technical_decision", source)
        self.assertNotIn("memory_claim", source)
        self.assertNotIn("ai_claim", source)

    def test_protected_sources_remain_unchanged(self) -> None:
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
            for path in paths
        )
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
