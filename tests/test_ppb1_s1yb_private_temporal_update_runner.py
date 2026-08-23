from __future__ import annotations

from dataclasses import fields, replace
import inspect
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_s1ya_private_static_prototype_baseline as s1ya
import mcm_field_organism._ppb1_s1yb_private_temporal_update_runner as s1yb
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS


EXPECTED_AGGREGATE_RECEIPT_DIGEST = (
    "55e074641953bec27de059c32d3720361337b65e5e47a6acd6aabfe03a06ab4b"
)


class PPB1S1YBPrivateTemporalUpdateRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = s1yb.run_s1yb_private_temporal_update_comparison()

    def test_result_is_deterministic_and_digest_bound(self) -> None:
        second = s1yb.run_s1yb_private_temporal_update_comparison()
        self.assertEqual(self.result, second)
        self.assertEqual(
            EXPECTED_AGGREGATE_RECEIPT_DIGEST,
            self.result.aggregate_receipt.aggregate_receipt_digest,
        )
        self.assertEqual(
            "0aac41828eb64ba0f2dfc8488ba6d9c1c636998cb66023ad6bc488a0671bbadb",
            self.result.aggregate_receipt.fixture_bundle_digest,
        )

    def test_exact_function_call_budgets(self) -> None:
        with (
            patch.object(s1yb, "build_s1xz_temporal_update_fixture", wraps=s1yb.build_s1xz_temporal_update_fixture) as fixture,
            patch.object(s1yb, "initial_ppb1_bank_state", wraps=s1yb.initial_ppb1_bank_state) as candidate_initial,
            patch.object(s1ya, "initial_ppb1_bank_state", wraps=s1ya.initial_ppb1_bank_state) as baseline_initial,
            patch.object(s1yb, "advance_s1wq_perceptual_state", wraps=s1yb.advance_s1wq_perceptual_state) as candidate_advance,
            patch.object(s1ya, "advance_s1wq_perceptual_state", wraps=s1ya.advance_s1wq_perceptual_state) as baseline_advance,
            patch.object(s1yb, "receive_s1ya_frozen_exposure", wraps=s1yb.receive_s1ya_frozen_exposure) as frozen_handoff,
            patch.object(s1yb, "probe_s1wu_perceptual_state", wraps=s1yb.probe_s1wu_perceptual_state) as probe,
            patch.object(s1yb, "_relation", wraps=s1yb._relation) as comparator,
        ):
            s1yb.run_s1yb_private_temporal_update_comparison()
        self.assertEqual(1, fixture.call_count)
        self.assertEqual(10, candidate_initial.call_count)
        self.assertEqual(10, baseline_initial.call_count)
        self.assertEqual(64, candidate_advance.call_count)
        self.assertEqual(36, baseline_advance.call_count)
        self.assertEqual(28, frozen_handoff.call_count)
        self.assertEqual(64, probe.call_count)
        self.assertEqual(32, comparator.call_count)

    def test_ten_histories_have_exact_modality_then_history_order(self) -> None:
        self.assertEqual(
            tuple(
                (modality, history)
                for modality in ("auditory", "visual")
                for history in ("H1", "H2", "H3", "H4", "H5")
            ),
            tuple(
                (item.modality_id, item.history_id)
                for item in self.result.history_receipts
            ),
        )

    def test_all_preupdate_behavior_is_equal(self) -> None:
        self.assertTrue(
            all(item.preupdate_behavior_equal for item in self.result.history_receipts)
        )
        self.assertTrue(
            all(
                item.candidate_config_digest != item.baseline_config_digest
                for item in self.result.history_receipts
            )
        )

    def test_all_thirty_two_cells_match_fixture_and_preserve_states(self) -> None:
        cells = self.result.paired_probe_receipts
        self.assertEqual(32, len(cells))
        self.assertTrue(all(item.matches_fixture for item in cells))
        self.assertTrue(all(item.candidate_state_unchanged for item in cells))
        self.assertTrue(all(item.baseline_state_unchanged for item in cells))

    def test_relation_inventory_is_exact_and_expected(self) -> None:
        receipt = self.result.aggregate_receipt
        self.assertEqual(14, receipt.strict_advantage_count)
        self.assertEqual(4, receipt.diagnostic_loss_count)
        self.assertEqual(14, receipt.tie_count)
        losses = {
            (item.modality_id, item.history_id, item.probe_role)
            for item in self.result.paired_probe_receipts
            if item.relation == "DIAGNOSTIC_LOSS"
        }
        self.assertEqual(
            {
                (modality, history, "origin")
                for modality in ("auditory", "visual")
                for history in ("H2", "H5")
            },
            losses,
        )

    def test_all_mandatory_advantage_and_negative_control_cells_pass(self) -> None:
        mandatory = {
            ("H2", "gradual_3"),
            ("H3", "conflict_b"),
            ("H4", "origin"),
            ("H4", "opposite_c"),
            ("H5", "gradual_3"),
        }
        controls = {
            ("H1", "conflict_b"),
            ("H2", "conflict_b"),
            ("H3", "opposite_c"),
            ("H4", "far_control"),
            ("H5", "conflict_b"),
        }
        mandatory_cells = [item for item in self.result.paired_probe_receipts if (item.history_id, item.probe_role) in mandatory]
        control_cells = [item for item in self.result.paired_probe_receipts if (item.history_id, item.probe_role) in controls]
        self.assertEqual(10, len(mandatory_cells))
        self.assertTrue(all(item.relation == "STRICT_ADVANTAGE" for item in mandatory_cells))
        self.assertEqual(10, len(control_cells))
        self.assertTrue(all(not item.candidate_recognized and not item.baseline_recognized for item in control_cells))

    def test_h3_separation_and_h4_displacement_are_observed_in_both_modalities(self) -> None:
        cells = {
            (item.modality_id, item.history_id, item.probe_role): item
            for item in self.result.paired_probe_receipts
        }
        for modality in ("auditory", "visual"):
            h3 = cells[(modality, "H3", "conflict_b")]
            self.assertTrue(h3.candidate_recognized)
            self.assertFalse(h3.baseline_recognized)
            old = cells[(modality, "H4", "origin")]
            new = cells[(modality, "H4", "opposite_c")]
            self.assertEqual((False, True), (old.candidate_recognized, old.baseline_recognized))
            self.assertEqual((True, False), (new.candidate_recognized, new.baseline_recognized))

    def test_all_history_receipts_are_valid_and_atomic(self) -> None:
        for item in self.result.history_receipts:
            self.assertTrue(item.target_policy_satisfied)
            self.assertTrue(item.negative_control_safe)
            self.assertTrue(item.all_probe_states_unchanged)
            self.assertEqual("HISTORY_VALID_EXPECTED_BEHAVIOR", item.decision)

    def test_aggregate_reports_only_the_bound_synthetic_function_result(self) -> None:
        receipt = self.result.aggregate_receipt
        self.assertTrue(receipt.all_histories_valid)
        self.assertEqual(10, receipt.mandatory_advantage_count)
        self.assertEqual(10, receipt.negative_control_safe_count)
        self.assertEqual(s1yb.S1YB_PASS, receipt.decision)
        self.assertEqual((64, 36, 28, 32, 32), (
            receipt.candidate_transition_count,
            receipt.baseline_formation_transition_count,
            receipt.frozen_baseline_handoff_count,
            receipt.candidate_probe_count,
            receipt.baseline_probe_count,
        ))

    def test_receipt_tampering_fails_closed(self) -> None:
        with self.assertRaises(s1yb.S1YBTemporalUpdateRunnerError):
            replace(self.result.aggregate_receipt, decision=s1yb.S1YB_FAIL)
        with self.assertRaises(s1yb.S1YBTemporalUpdateRunnerError):
            replace(self.result.aggregate_receipt, paired_probe_count=31)
        with self.assertRaises(s1yb.S1YBTemporalUpdateRunnerError):
            replace(self.result.history_receipts[0], decision="HISTORY_FAIL")
        with self.assertRaises(s1yb.S1YBTemporalUpdateRunnerError):
            replace(self.result.paired_probe_receipts[0], matches_fixture=False)

    def test_four_types_are_frozen_slotted_and_role_complete(self) -> None:
        expected = {
            s1yb.S1YBPairedProbeReceipt: 21,
            s1yb.S1YBHistoryReceipt: 22,
            s1yb.S1YBAggregateReceipt: 16,
            s1yb.S1YBRunResult: 3,
        }
        for kind, count in expected.items():
            self.assertEqual(count, len(fields(kind)))
            self.assertTrue(kind.__dataclass_params__.frozen)
            self.assertEqual(count, len(kind.__slots__))

    def test_source_is_private_and_excludes_matrix_field_file_and_production(self) -> None:
        source = inspect.getsource(s1yb)
        for forbidden in (
            "_ppb1_s1xc_fixture_registry",
            "_ppb1_s1xi_private_full_runner",
            "run_s1xi_registered_matrix",
            "SharedMCMField",
            "open(",
            "write_text(",
            "production_adapter",
            "semantic_label",
        ):
            self.assertNotIn(forbidden, source)

    def test_runner_is_unexported_and_has_no_public_surface(self) -> None:
        self.assertNotIn("S1YBRunResult", mcm_field_organism.__all__)
        self.assertFalse(hasattr(current_api, "run_s1yb_private_temporal_update_comparison"))
        self.assertNotIn("run_s1yb_private_temporal_update_comparison", ROOT_LAZY_EXPORTS)


if __name__ == "__main__":
    unittest.main()
