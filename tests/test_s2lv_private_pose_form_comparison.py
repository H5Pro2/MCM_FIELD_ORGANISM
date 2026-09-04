from __future__ import annotations

from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from tools import _s2lv_private_pose_form_comparison as comparison
from tools import _s2lv_private_pose_form_corpus as corpus
from tools import _s2lv_private_pose_form_projection as projection


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


class S2LVPoseFormComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = comparison._load_plan(WORKSPACE_ROOT)
        cls.result = comparison.build_comparison(WORKSPACE_ROOT)

    def test_01_presealed_inventory_and_brightness_pairing(self) -> None:
        bindings = {item["content_id"]: item for item in self.plan["generation_root"]["source_bindings"]}
        self.assertEqual(len(bindings), 32)
        self.assertEqual(len({item["payload_sha256"] for item in bindings.values()}), 32)
        for group in self.plan["evaluation_root"]["paired_variants"]:
            selected = [bindings[item] for item in group["content_ids"]]
            self.assertEqual(len({item["histogram_digest"] for item in selected}), 1)
            self.assertEqual(len({item["rgb_value_sum"] for item in selected}), 1)

    def test_02_projection_is_deterministic_and_label_free(self) -> None:
        recipe = self.plan["generation_root"]["recipes"][0]
        frame = corpus.render_frame(recipe)
        state = LocalChannelGridReceptor(VisualGridConfig()).analyze(frame, frame_index=0)
        first = projection.project_pose_form(tuple(state.channel_values))
        second = projection.project_pose_form(tuple(state.channel_values))
        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(len(first.form_descriptor.values), 144)
        self.assertAlmostEqual(sum(first.form_descriptor.values), 1.0, places=12)
        self.assertNotIn("family", json.dumps(first.canonical_payload(), sort_keys=True).lower())

    def test_03_projection_outputs_are_immutable(self) -> None:
        state_binding = self.result["state_bindings"][0]
        values = tuple(float(value) for value in state_binding["form_descriptor"]["values"])
        descriptor = projection.FormDescriptorV1(grid_size=12, values=values)
        with self.assertRaises(FrozenInstanceError):
            descriptor.grid_size = 8
        with self.assertRaises(projection.S2LVProjectionError):
            projection.project_pose_form([0.0] * 288)

    def test_04_pose_reports_position_and_extent_without_entering_form_role(self) -> None:
        rows = {item["content_id"]: item for item in self.result["state_bindings"]}
        for offset in (0, 8, 16, 24):
            base = rows[f"frame-{offset + 1:03d}"]["pose"]
            left = rows[f"frame-{offset + 2:03d}"]["pose"]
            right = rows[f"frame-{offset + 3:03d}"]["pose"]
            small = rows[f"frame-{offset + 6:03d}"]["pose"]
            large = rows[f"frame-{offset + 7:03d}"]["pose"]
            self.assertLess(left["centroid_x"], base["centroid_x"])
            self.assertGreater(right["centroid_x"], base["centroid_x"])
            self.assertLess(small["total_activation"], large["total_activation"])

    def test_05_complete_pair_inventory_is_partitioned(self) -> None:
        rows = self.result["complete_pair_distances"]
        self.assertEqual(len(rows), 496)
        self.assertEqual(sum(row["relation"] == "WITHIN_FAMILY" for row in rows), 112)
        self.assertEqual(sum(row["relation"] == "BETWEEN_FAMILY" for row in rows), 384)
        self.assertEqual(len({row["pair_digest"] for row in rows}), 496)

    def test_06_baseline_threshold_counts_are_observations_only(self) -> None:
        rows = self.result["complete_pair_distances"]
        summaries = {item["relation"]: item for item in self.result["relation_summaries"]}
        for relation, summary in summaries.items():
            selected = [row for row in rows if row["relation"] == relation]
            for field in ("baseline_full_mean_l1", "fixed_mask_visible_mean_l1"):
                values = [row[field] for row in selected]
                self.assertEqual(summary[field]["count_at_or_below_visual_slow_0_01"], sum(value <= 0.01 for value in values))
                self.assertEqual(summary[field]["count_at_or_below_fast_0_2"], sum(value <= 0.2 for value in values))
        self.assertFalse(self.result["thresholds_selected_or_changed"])

    def test_07_leave_one_out_evaluations_are_complete(self) -> None:
        evaluations = self.result["leave_one_out_evaluations"]
        self.assertEqual([item["representation_id"] for item in evaluations], ["BLOCK_MEAN_12X8_RGB", "FORM_DESCRIPTOR_12X12_V1"])
        for evaluation in evaluations:
            self.assertEqual(evaluation["total"], 32)
            self.assertEqual(len(evaluation["rows"]), 32)
            self.assertLessEqual(evaluation["correct"], evaluation["total"])

    def test_08_fixed_mask_analysis_uses_only_bound_positions(self) -> None:
        mask = self.result["fixed_partial_cue_mask_analysis"]
        self.assertEqual(mask["visible_positions"], list(range(32)))
        self.assertEqual(mask["visible_rows"], [0])
        self.assertEqual(mask["visible_value_fraction"], 32 / 288)
        rows = self.result["complete_pair_distances"]
        self.assertEqual(mask["between_exact_collision_count"], sum(row["relation"] == "BETWEEN_FAMILY" and row["fixed_mask_visible_exact_equal"] for row in rows))

    def test_09_comparison_has_no_memory_context_field_or_raw_payload(self) -> None:
        self.assertEqual(self.result["calls"], {"baseline_visual_receptor": 32, "memory": 0, "context": 0, "field": 0})
        self.assertFalse(self.result["raw_payload_retained"])
        self.assertFalse(self.result["production_integration"])
        self.assertFalse(self.result["result_controls_source_inclusion"])

    def test_10_read_only_verifier_and_closed_gates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "comparison.json"
            path.write_bytes(comparison._canonical_bytes(self.result, newline=True))
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            receipt = comparison.verify_comparison_file(path)
            self.assertEqual(receipt["verification_status"], "RECORDING_COMPLETE")
            self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())
            mutated = json.loads(path.read_text(encoding="ascii"))
            mutated["production_integration"] = True
            path.write_bytes(comparison._canonical_bytes(mutated, newline=True))
            with self.assertRaises(comparison.S2LVComparisonError):
                comparison.verify_comparison_file(path)
        self.assertFalse(corpus.PLAN_ENABLED)
        self.assertFalse(comparison.COMPARISON_ENABLED)


if __name__ == "__main__":
    unittest.main()
