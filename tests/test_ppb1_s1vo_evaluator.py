from __future__ import annotations

from dataclasses import fields, replace
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism._ppb1_s1vn_matrix import (
    S1VN_BASELINE_IDS,
    S1VN_FAMILY_IDS,
    S1VN_MODALITY_IDS,
    S1VN_PARAMETER_IDS,
    s1vn_config,
)
from mcm_field_organism._ppb1_s1vo_evaluator import (
    S1VO_BLOCKERS,
    S1VO_EXPECTED_PLAN_DIGEST,
    S1VO_INVALID_EVALUATION_INPUT,
    S1VO_PREFLIGHT_DECISION,
    S1VOArmSummary,
    S1VOEvaluatorError,
    evaluate_s1vo_summaries,
    run_s1vo_static_preflight,
)
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]


def expected_calls(parameter_id: str, modality_id: str) -> int:
    config = s1vn_config(parameter_id, modality_id)
    return 42 + config.capacity + 2 * config.expire_after_steps


def summaries() -> tuple[S1VOArmSummary, ...]:
    return tuple(
        S1VOArmSummary(
            family,
            parameter,
            modality,
            False,
            6,
            0,
            False,
            False,
            False,
            0,
            expected_calls(parameter, modality),
        )
        for family in S1VN_FAMILY_IDS
        for parameter in S1VN_PARAMETER_IDS
        for modality in S1VN_MODALITY_IDS
    )


def set_summary(
    rows: tuple[S1VOArmSummary, ...],
    family: str,
    parameter: str,
    modality: str,
    **changes: object,
) -> tuple[S1VOArmSummary, ...]:
    return tuple(
        replace(row, **changes)
        if (row.family_id, row.parameter_id, row.modality_id)
        == (family, parameter, modality)
        else row
        for row in rows
    )


ADMISSIBLE = {
    "lifecycle_valid": True,
    "diagnostic_match_count": 3,
    "near_assignment_consistent": True,
    "separated_assignment_distinct": True,
    "repeatability_confirmed": True,
}


class PPB1S1VOEvaluatorTests(unittest.TestCase):
    def test_constructed_summary_inventory_has_exact_cross_product(self) -> None:
        rows = summaries()
        self.assertEqual(48, len(rows))
        self.assertEqual(48, len({
            (row.family_id, row.parameter_id, row.modality_id) for row in rows
        }))

    def test_no_passing_record_selects_no_configuration(self) -> None:
        result = evaluate_s1vo_summaries(summaries())
        self.assertEqual(
            ("NO_ADMISSIBLE_CONFIGURATION", "NO_ADMISSIBLE_CONFIGURATION"),
            tuple(item.selection for item in result.decisions),
        )
        self.assertTrue(all(
            item.reason == "NO_RECORD_PASSES_BOUND_STOP_RULES"
            for item in result.decisions
        ))

    def test_least_state_admissible_nonreduced_record_is_selected(self) -> None:
        rows = summaries()
        rows = set_summary(
            rows, "PPB1", "P1", "auditory", **ADMISSIBLE,
            peak_logical_value_count=192,
        )
        rows = set_summary(
            rows, "PPB1", "P2", "auditory", **ADMISSIBLE,
            peak_logical_value_count=384,
        )
        decision = evaluate_s1vo_summaries(rows).decisions[0]
        self.assertEqual("P1", decision.selection)
        self.assertEqual(("P1", "P2"), decision.admissible_parameter_ids)

    def test_audio_and_visual_may_select_different_records(self) -> None:
        rows = summaries()
        rows = set_summary(
            rows, "PPB1", "P0", "auditory", **ADMISSIBLE,
            peak_logical_value_count=96,
        )
        rows = set_summary(
            rows, "PPB1", "P2", "visual", **ADMISSIBLE,
            peak_logical_value_count=1152,
        )
        result = evaluate_s1vo_summaries(rows)
        self.assertEqual(("P0", "P2"), tuple(item.selection for item in result.decisions))

    def test_simpler_baseline_reduces_an_otherwise_admissible_record(self) -> None:
        rows = summaries()
        rows = set_summary(
            rows, "PPB1", "P0", "auditory", **ADMISSIBLE,
            peak_logical_value_count=96,
        )
        rows = set_summary(
            rows, "B03", "P0", "auditory", **ADMISSIBLE,
            peak_logical_value_count=96,
        )
        decision = evaluate_s1vo_summaries(rows).decisions[0]
        self.assertEqual("NO_ADMISSIBLE_CONFIGURATION", decision.selection)
        self.assertEqual(("P0",), decision.reduced_parameter_ids)
        self.assertEqual(("B03",), decision.explaining_baseline_ids)

    def test_ppb_off_cannot_reduce_a_stateful_record(self) -> None:
        rows = summaries()
        rows = set_summary(
            rows, "PPB1", "P0", "auditory", **ADMISSIBLE,
            peak_logical_value_count=96,
        )
        rows = set_summary(
            rows, "B07", "P0", "auditory", **ADMISSIBLE,
            peak_logical_value_count=0,
        )
        self.assertEqual("P0", evaluate_s1vo_summaries(rows).decisions[0].selection)

    def test_always_and_never_match_are_rejected(self) -> None:
        for count in (0, 6):
            changes = dict(ADMISSIBLE)
            changes["diagnostic_match_count"] = count
            rows = set_summary(
                summaries(),
                "PPB1",
                "P0",
                "auditory",
                **changes,
                peak_logical_value_count=96,
            )
            self.assertEqual(
                "NO_ADMISSIBLE_CONFIGURATION",
                evaluate_s1vo_summaries(rows).decisions[0].selection,
            )

    def test_missing_repeatability_is_rejected_before_baselines(self) -> None:
        changes = dict(ADMISSIBLE)
        changes["repeatability_confirmed"] = False
        rows = set_summary(
            summaries(), "PPB1", "P0", "auditory", **changes,
            peak_logical_value_count=96,
        )
        self.assertEqual(
            "NO_ADMISSIBLE_CONFIGURATION",
            evaluate_s1vo_summaries(rows).decisions[0].selection,
        )

    def test_incomplete_or_wrong_call_inventory_fails_closed(self) -> None:
        with self.assertRaises(S1VOEvaluatorError) as caught:
            evaluate_s1vo_summaries(summaries()[:-1])
        self.assertEqual(S1VO_INVALID_EVALUATION_INPUT, caught.exception.code)
        rows = list(summaries())
        rows[0] = replace(rows[0], accepted_call_count=rows[0].accepted_call_count + 1)
        with self.assertRaises(S1VOEvaluatorError):
            evaluate_s1vo_summaries(tuple(rows))

    def test_evaluation_is_canonical_and_deterministic(self) -> None:
        first = evaluate_s1vo_summaries(summaries())
        second = evaluate_s1vo_summaries(summaries())
        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(64, len(first.digest()))

    def test_preflight_binds_exact_plan_and_zero_execution(self) -> None:
        preflight = run_s1vo_static_preflight()
        self.assertEqual(S1VO_EXPECTED_PLAN_DIGEST, preflight.plan_digest)
        self.assertEqual(384, preflight.case_count)
        self.assertEqual(74368, preflight.total_call_budget)
        self.assertEqual(0, preflight.accepted_call_count)
        self.assertFalse(preflight.ready_for_execution)

    def test_preflight_stops_on_exact_two_methodological_blockers(self) -> None:
        preflight = run_s1vo_static_preflight()
        self.assertEqual(S1VO_PREFLIGHT_DECISION, preflight.decision)
        self.assertEqual(S1VO_BLOCKERS, preflight.blockers)
        checks = dict(preflight.checks)
        self.assertFalse(checks["BASELINE_SELECTED_IDENTITY_RECORDED"])
        self.assertFalse(checks["F04_F05_F06_REPEATABILITY_PATHS_PRESENT"])
        self.assertTrue(all(
            passed for role, passed in preflight.checks
            if role not in {
                "BASELINE_SELECTED_IDENTITY_RECORDED",
                "F04_F05_F06_REPEATABILITY_PATHS_PRESENT",
            }
        ))

    def test_preflight_is_deterministic(self) -> None:
        first = run_s1vo_static_preflight()
        second = run_s1vo_static_preflight()
        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())

    def test_s1vo_remains_private_and_snapshot_free(self) -> None:
        names = set(getattr(current_api, "__all__", ())) | set(ROOT_LAZY_EXPORTS)
        names |= {item.name for item in fields(SharedMCMFieldSnapshot)}
        for name in ("evaluate_s1vo_summaries", "run_s1vo_static_preflight"):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertNotIn(name, names)

    def test_s1vo_source_has_no_field_media_or_matrix_body_call(self) -> None:
        source = (
            ROOT / "mcm_field_organism" / "_ppb1_s1vo_evaluator.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "shared_mcm_field",
            "public_av_receptor_run",
            "live_audio_video_field",
            "_execute_registered_matrix",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
