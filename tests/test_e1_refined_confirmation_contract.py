from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_refined_confirmation_contract import (
    E1RefinedConfirmationContractError,
    build_e1_refined_confirmation_contract,
)


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json"
TARGET_NAMES = (
    "e1_refined_confirmation_s1eb_once_v1.json",
    "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    "e1_refined_confirmation_s1eb_once_v1.lock",
)


class E1RefinedConfirmationContractTests(unittest.TestCase):
    def test_contract_binds_r2_r4_r8_and_unchanged_margin(self) -> None:
        contract = build_e1_refined_confirmation_contract(REPORTS, UPSTREAM)

        self.assertEqual((("r2", 2), ("r4", 4), ("r8", 8)), contract.refinements)
        self.assertEqual((
            ("r2", 400), ("r4", 800), ("r8", 1600)
        ), contract.history_step_counts)
        self.assertEqual((
            ("r2", 200), ("r4", 400), ("r8", 800)
        ), contract.probe_step_counts)
        self.assertEqual(8.0, contract.numerical_signal_margin)

    def test_contract_preserves_terminal_s1ea6_boundary(self) -> None:
        contract = build_e1_refined_confirmation_contract(REPORTS, UPSTREAM)

        self.assertEqual("NUMERICALLY_UNDECIDABLE", contract.upstream_decision)
        self.assertFalse(contract.s1_ea6_rerun_permitted)
        self.assertFalse(contract.posthoc_threshold_change_permitted)

    def test_only_planner_implementation_is_permitted(self) -> None:
        contract = build_e1_refined_confirmation_contract(REPORTS, UPSTREAM)

        self.assertTrue(contract.planner_implementation_permitted)
        self.assertFalse(contract.runner_implementation_permitted)
        self.assertFalse(contract.execution_permitted)
        self.assertFalse(contract.execution_started)

    def test_contract_is_repeatable_and_paths_remain_free(self) -> None:
        before = tuple((REPORTS / name).exists() for name in TARGET_NAMES)
        first = build_e1_refined_confirmation_contract(REPORTS, UPSTREAM)
        second = build_e1_refined_confirmation_contract(REPORTS, UPSTREAM)

        self.assertEqual(first.digest(), second.digest())
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple((REPORTS / name).exists() for name in TARGET_NAMES))

    def test_changed_release_flag_and_used_path_fail_closed(self) -> None:
        contract = build_e1_refined_confirmation_contract(REPORTS, UPSTREAM)
        with self.assertRaises(E1RefinedConfirmationContractError):
            replace(contract, execution_permitted=True)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / TARGET_NAMES[0]).write_text("used\n", encoding="ascii")
            with self.assertRaises(E1RefinedConfirmationContractError):
                build_e1_refined_confirmation_contract(root, UPSTREAM)

    def test_contract_has_no_planner_runner_or_execution_call_and_is_private(self) -> None:
        source = inspect.getsource(build_e1_refined_confirmation_contract)
        for forbidden in (
            "build_e1_completion_aligned_refinement_plans",
            "run_e1_asynchronous_field",
            "produce_e1_canonical_refined_chain_result",
            "execute_e1_canonical_refined_chain_once",
        ):
            self.assertNotIn(forbidden, source)
        for role in (
            "E1RefinedConfirmationContract",
            "build_e1_refined_confirmation_contract",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
