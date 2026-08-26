from __future__ import annotations

import ast
from dataclasses import fields
from pathlib import Path
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1vx_post_integration_resource_preflight as s1vx
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PREFLIGHT_DIGEST = (
    "a52bb0c852769591aee47dcfce399d6f99a82632e53cd9beb51842f1385e27e5"
)
EXPECTED_SOURCE_DIGESTS = (
    (
        "s1vq_runner",
        "c9485bf36e6bec241ac3e0c565e7b5d5ec7fc4041596557f2e3db26ecb757c48",
    ),
    (
        "s1vt_pipeline",
        "0aeba24aac5732f11500ec02f51aded07097c0e58c54b05a9f6978ff6980b891",
    ),
    (
        "s1vw_synthetic_orchestrator",
        "37ea1c2a76b1a987dc72a3999162cd730484a75a5a3cdf60f04d6562320322f0",
    ),
)


class PPB1S1VXPostIntegrationResourcePreflightTests(unittest.TestCase):
    def test_static_inventory_preserves_bound_plan_and_budget(self) -> None:
        result = s1vx.run_s1vx_static_preflight()
        self.assertEqual(
            s1vx.S1VX_EXPECTED_PARENT_PLAN_DIGEST, result.parent_plan_digest
        )
        self.assertEqual(
            s1vx.S1VX_EXPECTED_CORRECTED_PLAN_DIGEST,
            result.corrected_plan_digest,
        )
        self.assertEqual(
            s1vx.S1VX_EXPECTED_PREFLIGHT_DIGEST,
            result.prior_preflight_digest,
        )
        self.assertEqual(528, result.case_count)
        self.assertEqual(75808, result.call_count)

    def test_existing_synthetic_handoff_and_terminal_roles_pass(self) -> None:
        checks = dict(s1vx.run_s1vx_static_preflight().checks)
        for role in (
            "PRIVATE_REGISTERED_RUNNER_BODY_PRESENT",
            "S1VT_PIPELINE_STAGES_PRESENT",
            "SYNTHETIC_H0_TO_H7_CHAIN_PRESENT",
            "TERMINAL_TYPES_COMPLETE",
            "TERMINAL_DIGEST_ROLES_COMPLETE",
            "SYNTHETIC_RESOURCE_GATE_EXPLICITLY_NON_PRODUCTION",
        ):
            self.assertTrue(checks[role])

    def test_exact_five_production_blockers_remain(self) -> None:
        result = s1vx.run_s1vx_static_preflight()
        self.assertEqual(s1vx.S1VX_DECISION, result.decision)
        self.assertEqual(s1vx.S1VX_BLOCKERS, result.blockers)
        self.assertFalse(result.ready_for_real_execution)
        self.assertIsNone(result.authorization_text)

    def test_only_bound_production_checks_fail(self) -> None:
        failed = tuple(
            role
            for role, passed in s1vx.run_s1vx_static_preflight().checks
            if not passed
        )
        self.assertEqual(
            (
                "PRIVATE_REAL_PRODUCER_BOUND",
                "PRODUCTION_AUTHORIZATION_TYPE_PRESENT",
                "PRODUCTION_RESOURCE_GATE_AND_MINIMA_PRESENT",
                "PRODUCTION_ARTIFACT_PUBLICATION_PATH_WIRED",
                "PRODUCTION_ENTRYPOINT_OPEN",
            ),
            failed,
        )

    def test_preflight_and_source_digests_are_canonical(self) -> None:
        first = s1vx.run_s1vx_static_preflight()
        second = s1vx.run_s1vx_static_preflight()
        self.assertEqual(first, second)
        self.assertEqual(EXPECTED_SOURCE_DIGESTS, first.source_digests)
        self.assertEqual(EXPECTED_PREFLIGHT_DIGEST, first.digest())

    def test_plan_drift_fails_closed(self) -> None:
        with patch.object(s1vx.s1vw, "S1VW_EXPECTED_CASE_COUNT", 527):
            with self.assertRaises(s1vx.S1VXPreflightError) as raised:
                s1vx.run_s1vx_static_preflight()
        self.assertEqual(s1vx.S1VX_PREFLIGHT_DRIFT, raised.exception.code)

    def test_preflight_calls_no_runner_or_orchestrator_function(self) -> None:
        source = Path(s1vx.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        function = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "run_s1vx_static_preflight"
        )
        calls = set()
        for node in ast.walk(function):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
        for forbidden in (
            "_execute_s1vq_corrected_matrix",
            "execute_s1vq_corrected_matrix",
            "run_s1vw_synthetic_once",
            "execute_s1vw_production_once",
            "seal_s1vt_matrix_result",
            "compose_s1vt_arm_records",
            "evaluate_s1vt_composition",
        ):
            self.assertNotIn(forbidden, calls)

    def test_preflight_has_no_resource_probe_field_or_media_runtime(self) -> None:
        source = Path(s1vx.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "psutil",
            "disk_usage",
            "gettempdir",
            "shared_mcm_field",
            "public_av_receptor_run",
            "live_audio_video_field",
            "time.time",
            "datetime",
        ):
            self.assertNotIn(forbidden, source)

    def test_s1vx_remains_private_and_snapshot_neutral(self) -> None:
        names = {
            "S1VXPreflightResult",
            "run_s1vx_static_preflight",
        }
        self.assertTrue(names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(names.isdisjoint(current_api.__all__))
        self.assertTrue(
            names.isdisjoint({item.name for item in fields(SharedMCMFieldSnapshot)})
        )


if __name__ == "__main__":
    unittest.main()
