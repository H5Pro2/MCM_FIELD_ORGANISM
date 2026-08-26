from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_canonical_confirmation_preflight import (
    E1CanonicalConfirmationPreflightError,
    prepare_e1_canonical_confirmation_preflight,
)


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


class E1CanonicalConfirmationPreflightTests(unittest.TestCase):
    def test_preflight_binds_history_and_probe_step_inventories(self) -> None:
        result = prepare_e1_canonical_confirmation_preflight(REPORTS, UPSTREAM)

        self.assertEqual((220, 110), (
            result.history_source_support_count,
            result.probe_source_support_count,
        ))
        self.assertEqual((200, 100), (
            result.history_completion_count,
            result.probe_completion_count,
        ))
        self.assertEqual((
            ("r2", 400), ("r4", 800), ("r8", 1600)
        ), result.history_step_counts)
        self.assertEqual((
            ("r2", 200), ("r4", 400), ("r8", 800)
        ), result.probe_step_counts)

    def test_ab_ba_keep_equal_evidence_but_different_ordered_paths(self) -> None:
        result = prepare_e1_canonical_confirmation_preflight(REPORTS, UPSTREAM)

        self.assertTrue(result.ab_ba_inventories_equal)
        self.assertTrue(result.ab_ba_completion_ticks_equal)
        self.assertTrue(result.ab_ba_contact_integrals_equal)
        self.assertTrue(result.ordered_ab_ba_paths_different)
        self.assertNotEqual(result.ab_plan_digest, result.ba_plan_digest)

    def test_handoffs_are_invariant_across_refinement(self) -> None:
        result = prepare_e1_canonical_confirmation_preflight(REPORTS, UPSTREAM)

        self.assertTrue(result.handoffs_refinement_invariant)
        self.assertNotEqual(result.ab_handoff_digest, result.ba_handoff_digest)
        self.assertNotEqual(result.probe_handoff_digest, result.ab_handoff_digest)

    def test_preflight_releases_only_runner_implementation(self) -> None:
        result = prepare_e1_canonical_confirmation_preflight(REPORTS, UPSTREAM)

        self.assertTrue(result.runner_implementation_permitted)
        self.assertFalse(result.execution_permitted)
        self.assertFalse(result.execution_started)
        self.assertFalse(result.s1_ea6_rerun_permitted)
        with self.assertRaises(E1CanonicalConfirmationPreflightError):
            replace(result, execution_permitted=True)

    def test_preflight_is_repeatable_and_keeps_paths_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        first = prepare_e1_canonical_confirmation_preflight(REPORTS, UPSTREAM)
        second = prepare_e1_canonical_confirmation_preflight(REPORTS, UPSTREAM)

        self.assertEqual(first, second)
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_preflight_has_no_field_or_e1_execution_and_is_private(self) -> None:
        source = inspect.getsource(prepare_e1_canonical_confirmation_preflight)
        for forbidden in (
            "build_shared_mcm_field",
            "build_neutral_e1_state",
            "run_e1_asynchronous_field",
            "produce_e1_canonical_refined_chain_result",
        ):
            self.assertNotIn(forbidden, source)
        for role in (
            "E1CanonicalConfirmationPreflight",
            "prepare_e1_canonical_confirmation_preflight",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
