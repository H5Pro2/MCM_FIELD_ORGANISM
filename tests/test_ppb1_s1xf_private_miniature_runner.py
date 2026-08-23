from __future__ import annotations

from dataclasses import fields, replace
import inspect
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1xf_private_miniature_runner as s1xf
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS


EXPECTED_MATRIX_RECEIPT_DIGEST = (
    "f89ff3d3afc9113b830054470622195670eff525583068e73da0026f615ce210"
)


class PPB1S1XFPrivateMiniatureRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = s1xf.run_s1xf_miniature_contract()

    def test_two_real_formations_match_templates_after_six_steps(self) -> None:
        receipts = self.result.formation_receipts
        self.assertEqual(2, len(receipts))
        self.assertEqual(("auditory", "visual"), tuple(
            receipt.modality_id for receipt in receipts
        ))
        for receipt in receipts:
            self.assertEqual(("CREATED", "MATCHED", "MATCHED"), receipt.ordered_event_sequence)
            self.assertEqual(receipt.template_state_digest, receipt.formed_state_digest)
            self.assertTrue(receipt.template_match)

    def test_call_counts_and_registered_matrix_boundary_are_exact(self) -> None:
        receipt = self.result.matrix_receipt
        self.assertEqual(2, receipt.initial_state_call_count)
        self.assertEqual(6, receipt.formation_advance_call_count)
        self.assertEqual(4, receipt.candidate_probe_call_count)
        self.assertEqual(20, receipt.baseline_probe_call_count)
        self.assertEqual(24, receipt.miniature_cell_count)
        self.assertEqual(0, receipt.registered_matrix_cell_count)

    def test_twenty_four_cells_have_private_miniature_order_and_identity(self) -> None:
        cells = self.result.cell_receipts
        self.assertEqual(24, len(cells))
        self.assertEqual(24, len({cell.cell_id for cell in cells}))
        self.assertEqual("s1xf-mini.auditory.ppb1.exact-positive", cells[0].cell_id)
        self.assertEqual(
            "s1xf-mini.visual.last-vector-distance.distinct-negative",
            cells[-1].cell_id,
        )
        self.assertTrue(all(cell.cell_id.startswith("s1xf-mini.") for cell in cells))
        self.assertTrue(all(not cell.cell_id.startswith("s1xa.") for cell in cells))

    def test_candidate_positive_and_negative_cells_use_formed_identity(self) -> None:
        cells = [cell for cell in self.result.cell_receipts if cell.system_id == "ppb1"]
        self.assertEqual(4, len(cells))
        for cell in cells:
            self.assertEqual(cell.probe_class == "exact-positive", cell.recognized)
            self.assertIsNotNone(cell.state_identity_digest)
            self.assertFalse(cell.raw_history_access_used)
            self.assertTrue(cell.state_unchanged)

    def test_no_memory_cells_use_canonical_null_roles(self) -> None:
        cells = [
            cell for cell in self.result.cell_receipts if cell.system_id == "no-memory"
        ]
        self.assertEqual(4, len(cells))
        for cell in cells:
            self.assertFalse(cell.recognized)
            self.assertIsNone(cell.nearest_distance)
            self.assertFalse(cell.observed_state_present)
            self.assertIsNone(cell.observed_state_digest_before)
            self.assertIsNone(cell.observed_state_digest_after)
            self.assertIsNone(cell.state_provenance_digest)
            self.assertEqual(0, cell.storage_role_count)
            self.assertEqual(0, cell.stored_scalar_value_count)

    def test_four_stateful_baselines_match_miniature_expectations(self) -> None:
        cells = [
            cell
            for cell in self.result.cell_receipts
            if cell.system_id not in {"ppb1", "no-memory"}
        ]
        self.assertEqual(16, len(cells))
        for cell in cells:
            self.assertEqual(cell.probe_class == "exact-positive", cell.recognized)
            self.assertIsNone(cell.state_identity_digest)
            self.assertTrue(cell.observed_state_present)
            self.assertTrue(cell.state_unchanged)
            self.assertTrue(cell.matches_miniature_expectation)

    def test_replay_budget_and_history_access_remain_explicit(self) -> None:
        dimensions = {"auditory": 12, "visual": 72}
        for cell in self.result.cell_receipts:
            if cell.system_id == "replay":
                self.assertTrue(cell.raw_history_access_used)
                self.assertEqual(
                    3 * dimensions[cell.modality_id],
                    cell.stored_scalar_value_count,
                )
            elif cell.system_id != "no-memory":
                self.assertFalse(cell.raw_history_access_used)
                self.assertEqual(
                    dimensions[cell.modality_id],
                    cell.stored_scalar_value_count,
                )

    def test_all_receipts_are_digest_bound_and_matrix_is_atomic(self) -> None:
        for receipt in self.result.formation_receipts:
            self.assertEqual(
                receipt.formation_receipt_digest,
                s1xf._digest(receipt.payload_without_digest()),
            )
        for receipt in self.result.cell_receipts:
            self.assertEqual(
                receipt.cell_receipt_digest,
                s1xf._digest(receipt.payload_without_digest()),
            )
        matrix = self.result.matrix_receipt
        self.assertEqual(
            matrix.matrix_receipt_digest,
            s1xf._digest(matrix.payload_without_digest()),
        )
        self.assertEqual(EXPECTED_MATRIX_RECEIPT_DIGEST, matrix.matrix_receipt_digest)

    def test_output_is_only_a_technical_runner_receipt(self) -> None:
        matrix = self.result.matrix_receipt
        self.assertEqual(s1xf.S1XF_TECHNICAL_RUNNER_PASS, matrix.technical_runner_decision)
        names = {item.name for item in fields(matrix)}
        self.assertTrue(names.isdisjoint({
            "technical_function_decision",
            "baseline_explanation_decision",
            "memory_claim",
            "field_effect",
        }))

    def test_receipt_tampering_and_partial_result_fail_closed(self) -> None:
        cell = self.result.cell_receipts[0]
        with self.assertRaises(s1xf.S1XFError):
            replace(cell, recognized=not cell.recognized)
        no_memory = next(
            item
            for item in self.result.cell_receipts
            if item.system_id == "no-memory"
        )
        invalid_payload = {
            **no_memory.payload_without_digest(),
            "storage_role_count": 1,
        }
        with self.assertRaises(s1xf.S1XFError):
            replace(
                no_memory,
                storage_role_count=1,
                cell_receipt_digest=s1xf._digest(invalid_payload),
            )
        with self.assertRaises(s1xf.S1XFError):
            replace(self.result, cell_receipts=self.result.cell_receipts[:-1])
        with self.assertRaises(s1xf.S1XFError):
            replace(
                self.result,
                cell_receipts=tuple(reversed(self.result.cell_receipts)),
            )

    def test_runner_and_receipts_remain_private(self) -> None:
        self.assertFalse(hasattr(mcm_field_organism, "run_s1xf_miniature_contract"))
        self.assertFalse(hasattr(current_api, "run_s1xf_miniature_contract"))
        self.assertNotIn("run_s1xf_miniature_contract", ROOT_LAZY_EXPORTS)

    def test_source_has_no_registered_runner_field_or_production_path(self) -> None:
        source = inspect.getsource(s1xf)
        for forbidden in (
            "execute_s1vn_matrix",
            "run_s1xa",
            "SharedMCMField",
            "open(",
            "from pathlib",
            "production",
            "semantic_label",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
