from __future__ import annotations

from dataclasses import fields, replace
import inspect
from pathlib import Path
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1xr_private_engineering_regression as s1xr
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REGRESSION_RECEIPT_DIGEST = (
    "9dd9358c6a7d9bdeb4ecd7d15c090ddd9f2b1bb040db80fb4f2524b8fc48b2a1"
)


class PPB1S1XRPrivateEngineeringRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = s1xr.run_s1xr_private_engineering_regression()

    def test_regression_is_deterministic_and_contract_bound(self) -> None:
        second = s1xr.run_s1xr_private_engineering_regression()
        self.assertEqual(self.result, second)
        self.assertEqual(
            EXPECTED_REGRESSION_RECEIPT_DIGEST,
            self.result.regression_receipt.regression_receipt_digest,
        )
        self.assertEqual(
            "72eeed148a75a61253099c77f10e359243e287d6c8e8d9517fe4833e29187688",
            s1xr.S1XR_CONTRACT_DIGEST,
        )

    def test_two_real_formations_have_bound_terminal_roles(self) -> None:
        self.assertEqual(2, len(self.result.formation_receipts))
        for receipt in self.result.formation_receipts:
            self.assertEqual(("CREATED", "MATCHED", "MATCHED"), receipt.ordered_events)
            self.assertEqual(1, receipt.occupied_slot_count)
            self.assertEqual(1, receipt.stabilized_slot_count)
            self.assertEqual(3, receipt.support_count)

    def test_exact_call_budget_is_one_fixture_two_initial_and_six_advances(self) -> None:
        original_fixture = s1xr.build_s1xo_numeric_margin_fixture
        original_initial = s1xr.initial_ppb1_bank_state
        original_advance = s1xr.advance_ppb1_bank
        with (
            patch.object(s1xr, "build_s1xo_numeric_margin_fixture", wraps=original_fixture) as fixture,
            patch.object(s1xr, "initial_ppb1_bank_state", wraps=original_initial) as initial,
            patch.object(s1xr, "advance_ppb1_bank", wraps=original_advance) as advance,
        ):
            s1xr.run_s1xr_private_engineering_regression()
        self.assertEqual(1, fixture.call_count)
        self.assertEqual(2, initial.call_count)
        self.assertEqual(6, advance.call_count)

    def test_exact_probe_and_baseline_distance_call_budget(self) -> None:
        original_probe = s1xr.probe_s1wu_perceptual_state
        original_distance = s1xr.normalized_mean_l1_distance
        with (
            patch.object(s1xr, "probe_s1wu_perceptual_state", wraps=original_probe) as probe,
            patch.object(s1xr, "normalized_mean_l1_distance", wraps=original_distance) as distance,
        ):
            s1xr.run_s1xr_private_engineering_regression()
        self.assertEqual(10, probe.call_count)
        self.assertEqual(10, distance.call_count)

    def test_twenty_cells_are_candidate_then_static_baseline_in_bound_order(self) -> None:
        cells = self.result.cell_receipts
        self.assertEqual(20, len(cells))
        self.assertTrue(all(cell.role == "candidate" for cell in cells[:10]))
        self.assertTrue(
            all(cell.role == "static-zero-prototype" for cell in cells[10:])
        )
        self.assertEqual("s1xr.candidate.auditory.exact-positive", cells[0].cell_id)
        self.assertEqual(
            "s1xr.static-zero-prototype.visual.distinct-negative",
            cells[-1].cell_id,
        )

    def test_candidate_cells_match_fixture_and_preserve_state(self) -> None:
        candidates = self.result.cell_receipts[:10]
        self.assertTrue(all(cell.matches_fixture for cell in candidates))
        self.assertTrue(all(cell.state_unchanged for cell in candidates))
        self.assertTrue(all(cell.observed_state_digest is not None for cell in candidates))
        self.assertTrue(all(cell.state_identity_digest is not None for cell in candidates))
        self.assertTrue(all(not cell.raw_history_access_used for cell in candidates))

    def test_static_baseline_has_no_candidate_identity_or_history(self) -> None:
        baselines = self.result.cell_receipts[10:]
        self.assertTrue(all(cell.matches_fixture for cell in baselines))
        self.assertTrue(all(cell.observed_state_digest is None for cell in baselines))
        self.assertTrue(all(cell.state_identity_digest is None for cell in baselines))
        self.assertTrue(all(not cell.raw_history_access_used for cell in baselines))

    def test_candidate_and_static_baseline_are_behaviorally_equal(self) -> None:
        candidates = {
            (cell.modality_id, cell.probe_class): cell
            for cell in self.result.cell_receipts[:10]
        }
        baselines = {
            (cell.modality_id, cell.probe_class): cell
            for cell in self.result.cell_receipts[10:]
        }
        self.assertEqual(candidates.keys(), baselines.keys())
        for key in candidates:
            self.assertEqual(candidates[key].recognized, baselines[key].recognized)
            self.assertEqual(candidates[key].distance, baselines[key].distance)

    def test_atomic_receipt_reports_engineering_equivalence_only(self) -> None:
        receipt = self.result.regression_receipt
        self.assertEqual(10, receipt.candidate_cell_count)
        self.assertEqual(10, receipt.baseline_cell_count)
        self.assertTrue(receipt.all_candidate_cells_match_fixture)
        self.assertTrue(receipt.all_candidate_states_unchanged)
        self.assertTrue(receipt.candidate_baseline_equivalent)
        self.assertEqual(s1xr.S1XR_PASS, receipt.decision)

    def test_receipt_tampering_fails_closed(self) -> None:
        receipt = self.result.regression_receipt
        with self.assertRaises(s1xr.S1XREngineeringRegressionError):
            replace(receipt, decision=s1xr.S1XR_FAIL)
        with self.assertRaises(s1xr.S1XREngineeringRegressionError):
            replace(receipt, ordered_cell_receipt_digests=receipt.ordered_cell_receipt_digests[:-1])
        with self.assertRaises(s1xr.S1XREngineeringRegressionError):
            replace(self.result.cell_receipts[0], state_unchanged=False)

    def test_four_frozen_slotted_types_have_no_field_or_research_roles(self) -> None:
        expected = {
            s1xr.S1XRFormationReceipt: 10,
            s1xr.S1XREngineeringCellReceipt: 13,
            s1xr.S1XREngineeringRegressionReceipt: 10,
            s1xr.S1XREngineeringRegressionResult: 3,
        }
        for kind, count in expected.items():
            self.assertEqual(count, len(fields(kind)))
            self.assertTrue(kind.__dataclass_params__.frozen)
            names = {item.name for item in fields(kind)}
            self.assertTrue(
                names.isdisjoint(
                    {
                        "field_feedback",
                        "memory_capability",
                        "technical_memory_function_decision",
                        "semantic_label",
                        "poststate",
                    }
                )
            )

    def test_source_is_private_and_excludes_historical_matrix_field_and_io(self) -> None:
        source = inspect.getsource(s1xr)
        for forbidden in (
            "_ppb1_s1xc_fixture_registry",
            "_ppb1_s1xi_private_full_runner",
            "materialize_s1xc_fixture_registry",
            "run_s1xi_registered_matrix",
            "SharedMCMField",
            "open(",
            "write_text(",
            "production_adapter",
        ):
            self.assertNotIn(forbidden, source)
        self.assertNotIn("S1XREngineeringRegressionResult", mcm_field_organism.__all__)
        self.assertFalse(hasattr(current_api, "run_s1xr_private_engineering_regression"))
        self.assertNotIn("run_s1xr_private_engineering_regression", ROOT_LAZY_EXPORTS)


if __name__ == "__main__":
    unittest.main()
