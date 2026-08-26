from __future__ import annotations

from dataclasses import fields, replace
import inspect
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1xi_private_full_runner as s1xi
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS


EXPECTED_SUBSTITUTE_MATRIX_RECEIPT_DIGEST = (
    "c4c937eb4b80455796ef2fe5bbb68295fdc0d7784f67130938734a27c20b88cb"
)


class PPB1S1XIPrivateFullRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = s1xi.run_s1xi_substitute_contract()

    def test_registered_entry_is_locked_before_materialization(self) -> None:
        self.assertFalse(s1xi.S1XI_REGISTERED_EXECUTION_ENABLED)
        with patch.object(
            s1xi,
            "materialize_s1xc_fixture_registry",
            side_effect=AssertionError("materializer must remain unreachable"),
        ):
            with self.assertRaises(s1xi.S1XIError) as caught:
                s1xi.run_s1xi_registered_matrix()
        self.assertEqual(s1xi.S1XI_REGISTERED_EXECUTION_LOCKED, caught.exception.code)

    def test_two_formations_are_real_and_template_bound(self) -> None:
        receipts = self.result.formation_receipts
        self.assertEqual(2, len(receipts))
        self.assertEqual(("auditory", "visual"), tuple(
            receipt.modality_id for receipt in receipts
        ))
        for receipt in receipts:
            self.assertEqual(("CREATED", "MATCHED", "MATCHED"), receipt.ordered_event_sequence)
            self.assertTrue(receipt.template_match)
            self.assertEqual(receipt.template_state_digest, receipt.formed_state_digest)

    def test_new_receipts_have_exact_nineteen_and_fifteen_roles(self) -> None:
        self.assertEqual(19, len(fields(s1xi.S1XIRegisteredCellReceipt)))
        self.assertEqual(15, len(fields(s1xi.S1XIRegisteredMatrixReceipt)))
        self.assertIn(
            "cell_plan_digest",
            {item.name for item in fields(s1xi.S1XIRegisteredCellReceipt)},
        )
        matrix_roles = {
            item.name for item in fields(s1xi.S1XIRegisteredMatrixReceipt)
        }
        self.assertIn("technical_function_decision", matrix_roles)
        self.assertIn("baseline_explanation_decision", matrix_roles)

    def test_substitute_uses_twenty_four_nonregistered_plan_bound_cells(self) -> None:
        cells = self.result.cell_receipts
        self.assertEqual(24, len(cells))
        self.assertEqual(24, len({cell.cell_id for cell in cells}))
        self.assertEqual(24, len({cell.cell_plan_digest for cell in cells}))
        self.assertEqual(
            "s1xi-sub.auditory.ppb1.exact-positive", cells[0].cell_id
        )
        self.assertEqual(
            "s1xi-sub.visual.last-vector-distance.distinct-negative",
            cells[-1].cell_id,
        )
        self.assertTrue(all(cell.cell_id.startswith("s1xi-sub.") for cell in cells))
        self.assertTrue(all(not cell.cell_id.startswith("s1xa.") for cell in cells))

    def test_all_substitute_cells_match_expectation_and_preserve_state(self) -> None:
        for cell in self.result.cell_receipts:
            self.assertTrue(cell.matches_prebound_expectation)
            self.assertTrue(cell.state_unchanged)
            if cell.observed_state_present:
                self.assertEqual(
                    cell.observed_state_digest_before,
                    cell.observed_state_digest_after,
                )

    def test_candidate_and_baseline_identity_roles_remain_separate(self) -> None:
        for cell in self.result.cell_receipts:
            if cell.system_id == "ppb1":
                self.assertIsNotNone(cell.state_identity_digest)
                self.assertFalse(cell.raw_history_access_used)
            else:
                self.assertIsNone(cell.state_identity_digest)

    def test_baseline_aggregation_uses_one_system_for_every_substitute_key(self) -> None:
        explanations = dict(
            self.result.matrix_receipt.baseline_explanation_by_system
        )
        self.assertFalse(explanations["no-memory"])
        for system in (
            "replay",
            "static-prototype",
            "moving-state",
            "last-vector-distance",
        ):
            self.assertTrue(explanations[system])

    def test_substitute_receipt_cannot_emit_registered_decisions(self) -> None:
        matrix = self.result.matrix_receipt
        self.assertEqual(4, matrix.candidate_pass_cell_count)
        self.assertTrue(matrix.method_valid)
        self.assertIsNone(matrix.technical_function_decision)
        self.assertIsNone(matrix.baseline_explanation_decision)
        self.assertEqual(s1xi.S1XI_SUBSTITUTE_FINAL, matrix.final_decision)
        self.assertNotEqual(s1xi.S1XC_REGISTRY_DIGEST, matrix.registry_digest)

    def test_cell_and_matrix_receipts_are_digest_bound_and_atomic(self) -> None:
        for cell in self.result.cell_receipts:
            self.assertEqual(
                cell.cell_receipt_digest,
                s1xi._receipt_digest(cell.payload_without_digest()),
            )
        matrix = self.result.matrix_receipt
        self.assertEqual(
            matrix.matrix_receipt_digest,
            s1xi._receipt_digest(matrix.payload_without_digest()),
        )
        self.assertEqual(
            EXPECTED_SUBSTITUTE_MATRIX_RECEIPT_DIGEST,
            matrix.matrix_receipt_digest,
        )

    def test_tampering_plan_order_or_decision_fails_closed(self) -> None:
        first = self.result.cell_receipts[0]
        with self.assertRaises(s1xi.S1XIError):
            replace(first, cell_plan_digest="0" * 64)
        with self.assertRaises(s1xi.S1XIError):
            replace(
                self.result,
                cell_receipts=tuple(reversed(self.result.cell_receipts)),
            )
        matrix = self.result.matrix_receipt
        with self.assertRaises(s1xi.S1XIError):
            replace(
                matrix,
                technical_function_decision="TECHNICAL_MEMORY_FUNCTION_PASS",
            )

    def test_registered_path_is_present_but_guarded_and_unexecuted(self) -> None:
        source = inspect.getsource(s1xi.run_s1xi_registered_matrix)
        self.assertLess(
            source.index("S1XI_REGISTERED_EXECUTION_ENABLED"),
            source.index("_execute_plan_set"),
        )
        self.assertIn("registered=True", source)
        self.assertEqual(
            0,
            sum(
                cell.cell_id.startswith("s1xa.")
                for cell in self.result.cell_receipts
            ),
        )

    def test_module_remains_private_and_outside_field_production_paths(self) -> None:
        self.assertFalse(hasattr(mcm_field_organism, "run_s1xi_registered_matrix"))
        self.assertFalse(hasattr(current_api, "run_s1xi_registered_matrix"))
        self.assertNotIn("run_s1xi_registered_matrix", ROOT_LAZY_EXPORTS)
        source = inspect.getsource(s1xi)
        for forbidden in (
            "execute_s1vn_matrix",
            "SharedMCMField",
            "open(",
            "from pathlib",
            "production",
            "semantic_label",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
