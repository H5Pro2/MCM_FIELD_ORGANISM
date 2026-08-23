from __future__ import annotations

import ast
from dataclasses import fields
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism._ppb1_s1vu_real_handoff_preflight import (
    S1VU_BLOCKERS,
    S1VU_EXPECTED_CORRECTED_PLAN_DIGEST,
    S1VU_EXPECTED_PARENT_PLAN_DIGEST,
    S1VU_PREFLIGHT_DECISION,
    run_s1vu_static_preflight,
)
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PREFLIGHT_DIGEST = (
    "31147b026d7f7faacba93f15e607e077fa55ace537500bf4c450f8c7d278258c"
)


class PPB1S1VURealHandoffPreflightTests(unittest.TestCase):
    def test_preflight_preserves_exact_plans_and_budget(self) -> None:
        result = run_s1vu_static_preflight()
        self.assertEqual(S1VU_EXPECTED_PARENT_PLAN_DIGEST, result.parent_plan_digest)
        self.assertEqual(
            S1VU_EXPECTED_CORRECTED_PLAN_DIGEST, result.corrected_plan_digest
        )
        self.assertEqual(528, result.case_count)
        self.assertEqual(75808, result.total_call_budget)
        self.assertEqual(0, result.accepted_call_count)

    def test_all_existing_runner_pipeline_and_gate_checks_pass(self) -> None:
        checks = dict(run_s1vu_static_preflight().checks)
        for role in (
            "PUBLIC_EXECUTION_GATE_ACTIVE",
            "PRIVATE_REGISTERED_RUNNER_BODY_PRESENT",
            "LEGACY_S1VQ_RESULT_ROLES_PRESENT",
            "S1VT_PIPELINE_STAGES_PRESENT",
            "S1VO_V1_BYPASS_ABSENT",
            "ZERO_REGISTERED_CALLS_EXECUTED",
        ):
            self.assertTrue(checks[role])

    def test_preflight_stops_on_exact_three_handoff_blockers(self) -> None:
        result = run_s1vu_static_preflight()
        self.assertEqual(S1VU_PREFLIGHT_DECISION, result.decision)
        self.assertEqual(S1VU_BLOCKERS, result.blockers)
        self.assertFalse(result.ready_for_execution)

    def test_only_bound_handoff_checks_fail(self) -> None:
        failed = tuple(
            role for role, passed in run_s1vu_static_preflight().checks
            if not passed
        )
        self.assertEqual(
            (
                "RUNNER_OUTPUT_IS_ATOMIC_S1VT_RESULT",
                "ATOMIC_S1VQ_TO_S1VT_HANDOFF_CHAIN_PRESENT",
                "ONE_SHOT_TERMINAL_OUTCOME_PRESENT",
            ),
            failed,
        )

    def test_preflight_is_canonical_and_deterministic(self) -> None:
        first = run_s1vu_static_preflight()
        second = run_s1vu_static_preflight()
        self.assertEqual(first, second)
        self.assertEqual(EXPECTED_PREFLIGHT_DIGEST, first.digest())
        self.assertEqual(first.digest(), second.digest())

    def test_s1vu_remains_private_and_snapshot_free(self) -> None:
        names = set(getattr(current_api, "__all__", ())) | set(ROOT_LAZY_EXPORTS)
        names |= {item.name for item in fields(SharedMCMFieldSnapshot)}
        for name in ("S1VUPreflightResult", "run_s1vu_static_preflight"):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertNotIn(name, names)

    def test_preflight_function_never_calls_private_matrix_body(self) -> None:
        source = (
            ROOT
            / "mcm_field_organism"
            / "_ppb1_s1vu_real_handoff_preflight.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(source)
        function = next(
            item
            for item in tree.body
            if isinstance(item, ast.FunctionDef)
            and item.name == "run_s1vu_static_preflight"
        )
        calls = {
            child.func.id
            for child in ast.walk(function)
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
        }
        calls |= {
            child.func.attr
            for child in ast.walk(function)
            if isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
        }
        self.assertNotIn("_execute_s1vq_corrected_matrix", calls)
        self.assertNotIn("_execute_s1vq_registered_path", calls)

    def test_s1vu_source_has_no_field_or_media_runtime(self) -> None:
        source = (
            ROOT
            / "mcm_field_organism"
            / "_ppb1_s1vu_real_handoff_preflight.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "shared_mcm_field",
            "public_av_receptor_run",
            "live_audio_video_field",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
