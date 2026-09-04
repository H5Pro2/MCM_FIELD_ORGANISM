from __future__ import annotations

from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from tools import _s2lw_private_spatial_mask_corpus as lw_corpus
from tools import _s2lx_private_masked_pose_form_comparison as comparison
from tools import _s2lx_private_masked_pose_form_projection as projection


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


class S2LXMaskedPoseFormComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lw_plan = comparison._load_bound_record(WORKSPACE_ROOT, comparison.LW_PLAN)
        cls.result = comparison.build_comparison(WORKSPACE_ROOT)
        cls.mask = next(item for item in cls.lw_plan["mask_root"]["masks"] if item["mask_id"] == "SPATIAL_SEEDED_96")

    def test_01_frozen_artifact_bindings_and_historical_counts_reproduce(self) -> None:
        self.assertTrue(all(self.result["historical_baseline_reproduction"].values()))
        self.assertEqual(self.result["frozen_artifact_bindings"]["s2lv_result_digest"], comparison.LV_RESULT[3])
        self.assertEqual(self.result["frozen_artifact_bindings"]["s2lw_result_digest"], comparison.LW_RESULT[3])
        self.assertEqual(self.result["frozen_artifact_bindings"]["spatial_96_mask_digest"], self.mask["mask_digest"])

    def test_02_masked_view_is_immutable_and_digest_bound(self) -> None:
        positions = tuple(self.mask["positions"])
        values = tuple(float(index) / 287.0 for index in range(288))
        view = projection.bind_masked_visual_view(values, positions, self.mask["mask_digest"])
        self.assertEqual(view.observed_values, tuple(values[index] for index in positions))
        self.assertEqual(view.observed_values_digest, projection._digest(list(view.observed_values)))
        with self.assertRaises(FrozenInstanceError):
            view.mask_digest = "0" * 64

    def test_03_hidden_values_cannot_change_masked_form_descriptor(self) -> None:
        recipe = self.lw_plan["generation_root"]["recipes"][0]
        frame = lw_corpus.render_frame(recipe)
        state = LocalChannelGridReceptor(VisualGridConfig()).analyze(frame, frame_index=0)
        original = tuple(state.channel_values)
        visible = set(self.mask["positions"])
        changed = tuple(value if index in visible else (1.0 - value) for index, value in enumerate(original))
        first_view = projection.bind_masked_visual_view(original, tuple(self.mask["positions"]), self.mask["mask_digest"])
        second_view = projection.bind_masked_visual_view(changed, tuple(self.mask["positions"]), self.mask["mask_digest"])
        first = projection.project_masked_pose_form(first_view)
        second = projection.project_masked_pose_form(second_view)
        self.assertNotEqual(first_view.source_values_digest, second_view.source_values_digest)
        self.assertEqual(first_view.observed_values_digest, second_view.observed_values_digest)
        self.assertEqual(first.pose, second.pose)
        self.assertEqual(first.form_descriptor, second.form_descriptor)

    def test_04_missing_values_are_not_present_or_imputed(self) -> None:
        for dataset in self.result["datasets"]:
            for state in dataset["state_bindings"]:
                descriptor = state["masked_form_descriptor"]
                self.assertEqual(descriptor["missing_values"], "NOT_PRESENT_NOT_IMPUTED")
                self.assertEqual(len(descriptor["values"]), 144)
                self.assertAlmostEqual(sum(descriptor["values"]), 1.0, places=12)
                self.assertNotIn("full_values", descriptor)

    def test_05_both_frozen_corpora_have_complete_pair_matrices(self) -> None:
        self.assertEqual([item["dataset_id"] for item in self.result["datasets"]], ["S2LV_CORPUS", "S2LW_CORPUS"])
        for dataset in self.result["datasets"]:
            self.assertEqual(dataset["source_count"], 32)
            self.assertEqual(len(dataset["state_bindings"]), 32)
            self.assertEqual(len(dataset["complete_pair_distances"]), 496)
            self.assertEqual(sum(row["relation"] == "WITHIN_FAMILY" for row in dataset["complete_pair_distances"]), 112)
            self.assertEqual(sum(row["relation"] == "BETWEEN_FAMILY" for row in dataset["complete_pair_distances"]), 384)

    def test_06_all_six_methods_use_identical_inputs_per_dataset(self) -> None:
        self.assertEqual(tuple(self.result["method_ids"]), comparison.METHOD_IDS)
        self.assertEqual(self.result["mask_application"], "IDENTICAL_SPATIAL_SEEDED_96_TO_EVERY_CUE_AND_CANDIDATE")
        for dataset in self.result["datasets"]:
            for row in dataset["complete_pair_distances"]:
                self.assertEqual(tuple(row["mean_l1"]), comparison.METHOD_IDS)

    def test_07_leave_one_out_reports_accuracy_and_ambiguity_without_success_gate(self) -> None:
        for dataset in self.result["datasets"]:
            evaluations = dataset["leave_one_out_evaluations"]
            self.assertEqual(tuple(item["method_id"] for item in evaluations), comparison.METHOD_IDS)
            for evaluation in evaluations:
                self.assertEqual(evaluation["total"], 32)
                self.assertEqual(len(evaluation["rows"]), 32)
                self.assertEqual(evaluation["ambiguous"], sum(row["ambiguous"] for row in evaluation["rows"]))

    def test_08_invalid_mask_binding_fails_closed(self) -> None:
        values = tuple(0.25 for _ in range(288))
        with self.assertRaises((projection.S2LXProjectionError, IndexError)):
            projection.bind_masked_visual_view(values, tuple(range(95)) + (288,), self.mask["mask_digest"])
        view = projection.bind_masked_visual_view(values, tuple(self.mask["positions"]), self.mask["mask_digest"])
        payload = view.canonical_payload()
        payload["observed_values_digest"] = "0" * 64
        with self.assertRaises(projection.S2LXProjectionError):
            projection.MaskedVisualViewV1(
                mask_digest=payload["mask_digest"],
                source_values_digest=payload["source_values_digest"],
                observed_positions=tuple(payload["observed_positions"]),
                observed_values=tuple(payload["observed_values"]),
                observed_values_digest=payload["observed_values_digest"],
            )

    def test_09_scope_boundaries_and_gates_remain_closed(self) -> None:
        self.assertEqual(self.result["calls"], {"visual_receptor": 64, "memory": 0, "context": 0, "field": 0})
        self.assertFalse(self.result["thresholds_selected_or_changed"])
        self.assertFalse(self.result["training_or_parameter_search"])
        self.assertFalse(self.result["hidden_values_completed"])
        self.assertFalse(self.result["raw_payload_retained"])
        self.assertFalse(self.result["production_integration"])
        self.assertFalse(comparison.COMPARISON_ENABLED)

    def test_10_read_only_verifier_accepts_canonical_and_rejects_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "comparison.json"
            path.write_bytes(comparison._canonical_bytes(self.result, newline=True))
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            receipt = comparison.verify_comparison_file(path)
            self.assertEqual(receipt["verification_status"], "RECORDING_COMPLETE")
            self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())
            mutated = json.loads(path.read_text(encoding="ascii"))
            mutated["hidden_values_completed"] = True
            path.write_bytes(comparison._canonical_bytes(mutated, newline=True))
            with self.assertRaises(comparison.S2LXComparisonError):
                comparison.verify_comparison_file(path)


if __name__ == "__main__":
    unittest.main()
