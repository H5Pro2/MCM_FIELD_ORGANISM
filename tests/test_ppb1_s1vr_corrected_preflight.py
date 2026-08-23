from __future__ import annotations

from dataclasses import fields
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism._ppb1_s1vo_evaluator import S1VOArmSummary
from mcm_field_organism._ppb1_s1vq_corrected_matrix import S1VQMatrixResult
from mcm_field_organism._ppb1_s1vr_corrected_preflight import (
    S1VR_BLOCKERS,
    S1VR_CLOSED_S1VO_BLOCKERS,
    S1VR_EXPECTED_CORRECTED_PLAN_DIGEST,
    S1VR_PREFLIGHT_DECISION,
    run_s1vr_static_preflight,
)
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PREFLIGHT_DIGEST = (
    "93c9bc7b092c0e947e5efd212e00c27cdc2096163b31ca7b20fc4065857e89e3"
)


class PPB1S1VRCorrectedPreflightTests(unittest.TestCase):
    def test_preflight_binds_parent_and_corrected_plan_digests(self) -> None:
        result = run_s1vr_static_preflight()
        self.assertEqual(
            "35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3",
            result.parent_plan_digest,
        )
        self.assertEqual(
            S1VR_EXPECTED_CORRECTED_PLAN_DIGEST, result.corrected_plan_digest
        )

    def test_preflight_binds_exact_corrected_case_and_call_budgets(self) -> None:
        result = run_s1vr_static_preflight()
        self.assertEqual(528, result.case_count)
        self.assertEqual(9476, result.ppb_call_budget)
        self.assertEqual(66332, result.baseline_call_budget)
        self.assertEqual(75808, result.total_call_budget)
        self.assertEqual(0, result.accepted_call_count)

    def test_original_s1vo_blockers_are_closed(self) -> None:
        result = run_s1vr_static_preflight()
        self.assertEqual(S1VR_CLOSED_S1VO_BLOCKERS, result.closed_s1vo_blockers)
        checks = dict(result.checks)
        self.assertTrue(checks["BASELINE_IDENTITY_ROLES_PRESENT"])
        self.assertTrue(checks["F04_F05_F06_R0_R1_PATHS_PRESENT"])

    def test_preflight_stops_on_exact_result_pipeline_blockers(self) -> None:
        result = run_s1vr_static_preflight()
        self.assertEqual(S1VR_PREFLIGHT_DECISION, result.decision)
        self.assertEqual(S1VR_BLOCKERS, result.blockers)
        self.assertFalse(result.ready_for_execution)

    def test_only_the_three_bound_pipeline_checks_fail(self) -> None:
        result = run_s1vr_static_preflight()
        failed = tuple(role for role, passed in result.checks if not passed)
        self.assertEqual(
            (
                "CORRECTED_MATRIX_RESULT_CANONICALLY_SEALED",
                "CORRECTED_RECEIPT_TO_48_SUMMARY_COMPOSITOR_PRESENT",
                "EVALUATOR_SUMMARY_COUNTS_IDENTITY_METADATA",
            ),
            failed,
        )

    def test_parent_mapping_repeat_receipts_and_gate_are_intact(self) -> None:
        checks = dict(run_s1vr_static_preflight().checks)
        for role in (
            "R0_PLAN_PRESERVES_ALL_384_PARENT_PATHS",
            "PATH_IDS_ARE_UNIQUE",
            "NORMALIZED_REPEAT_RECEIPT_ROLES_PRESENT",
            "EXECUTION_GATE_ACTIVE",
            "ZERO_REGISTERED_CALLS_EXECUTED",
        ):
            self.assertTrue(checks[role])

    def test_existing_matrix_result_is_not_yet_atomically_sealed(self) -> None:
        self.assertFalse(callable(getattr(S1VQMatrixResult, "canonical_payload", None)))
        self.assertFalse(callable(getattr(S1VQMatrixResult, "digest", None)))
        self.assertNotIn("__post_init__", S1VQMatrixResult.__dict__)

    def test_existing_evaluator_summary_has_no_identity_metadata_budget(self) -> None:
        self.assertNotIn(
            "peak_identity_metadata_value_count",
            {item.name for item in fields(S1VOArmSummary)},
        )

    def test_preflight_is_canonical_and_deterministic(self) -> None:
        first = run_s1vr_static_preflight()
        second = run_s1vr_static_preflight()
        self.assertEqual(first, second)
        self.assertEqual(EXPECTED_PREFLIGHT_DIGEST, first.digest())
        self.assertEqual(first.digest(), second.digest())

    def test_s1vr_remains_private_and_snapshot_free(self) -> None:
        names = set(getattr(current_api, "__all__", ())) | set(ROOT_LAZY_EXPORTS)
        names |= {item.name for item in fields(SharedMCMFieldSnapshot)}
        for name in ("S1VRPreflightResult", "run_s1vr_static_preflight"):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertNotIn(name, names)

    def test_s1vr_source_has_no_field_media_or_matrix_body_call(
        self,
    ) -> None:
        source = (
            ROOT
            / "mcm_field_organism"
            / "_ppb1_s1vr_corrected_preflight.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "shared_mcm_field",
            "public_av_receptor_run",
            "live_audio_video_field",
            "_execute_s1vq_corrected_matrix",
            "_execute_s1vq_registered_path",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
