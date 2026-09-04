from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools import _s2lu_private_visual_memory_compatibility_comparison as comparison
from tools import _s2lu_private_visual_memory_compatibility_corpus as corpus


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


class S2LUVisualMemoryCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = comparison._load_plan(WORKSPACE_ROOT)
        cls.result = comparison.build_comparison(WORKSPACE_ROOT)

    def test_01_presealed_source_inventory(self) -> None:
        bindings = self.plan["generation_root"]["source_bindings"]
        self.assertEqual(len(bindings), 16)
        self.assertEqual(len({item["payload_sha256"] for item in bindings}), 16)
        self.assertEqual(self.plan["plan_digest"], comparison.EXPECTED_PLAN_DIGEST)

    def test_02_paired_variants_preserve_brightness_distribution(self) -> None:
        bindings = {item["content_id"]: item for item in self.plan["generation_root"]["source_bindings"]}
        for pair in self.plan["evaluation_root"]["paired_variants"]:
            left = bindings[pair["family_01_content_id"]]
            right = bindings[pair["family_02_content_id"]]
            self.assertEqual(left["histogram_digest"], right["histogram_digest"])
            self.assertEqual(left["rgb_value_sum"], right["rgb_value_sum"])

    def test_03_primary_and_diagnostic_dimensions(self) -> None:
        self.assertEqual(len(self.result["state_bindings"]), 16)
        for state in self.result["state_bindings"]:
            self.assertEqual(len(state["baseline_values_digest"]), 64)
            self.assertEqual(len(state["diagnostic_gradient_values_digest"]), 64)
        recipe = self.plan["generation_root"]["recipes"][0]
        frame = corpus.render_frame(recipe)
        self.assertEqual(len(comparison._local_gradients(frame)), 576)

    def test_04_complete_within_and_between_pair_inventory(self) -> None:
        rows = self.result["complete_pair_distances"]
        self.assertEqual(len(rows), 120)
        self.assertEqual(sum(row["relation"] == "WITHIN_FAMILY" for row in rows), 56)
        self.assertEqual(sum(row["relation"] == "BETWEEN_FAMILY" for row in rows), 64)
        self.assertEqual(len({row["pair_digest"] for row in rows}), 120)

    def test_05_threshold_counts_are_derived_from_complete_rows(self) -> None:
        rows = self.result["complete_pair_distances"]
        summaries = {item["relation"]: item for item in self.result["relation_summaries"]}
        for relation, summary in summaries.items():
            selected = [row for row in rows if row["relation"] == relation]
            for field in (
                "baseline_full_mean_l1",
                "baseline_visible_mean_l1",
                "diagnostic_gradient_full_mean_l1",
            ):
                values = [row[field] for row in selected]
                metric = summary[field]
                self.assertEqual(metric["count_at_or_below_visual_slow_0_01"], sum(value <= 0.01 for value in values))
                self.assertEqual(metric["count_at_or_below_fast_0_2"], sum(value <= 0.2 for value in values))

    def test_06_fixed_mask_exact_and_metric_analysis(self) -> None:
        mask = self.result["fixed_partial_cue_mask_analysis"]
        self.assertEqual(mask["visible_positions"], list(range(32)))
        self.assertEqual(mask["masked_positions"], list(range(32, 288)))
        self.assertEqual(mask["coverage"]["rows_represented"], [0])
        self.assertEqual(len(mask["coverage"]["full_cells"]), 10)
        self.assertEqual(mask["coverage"]["partial_cells"], [{"row": 0, "column": 10, "channels": [0, 1]}])
        rows = self.result["complete_pair_distances"]
        self.assertEqual(
            mask["information"]["between_family_visible_exact_collision_count"],
            sum(row["relation"] == "BETWEEN_FAMILY" and row["baseline_visible_exact_equal"] for row in rows),
        )

    def test_07_no_result_gate_or_source_selection(self) -> None:
        self.assertFalse(self.result["thresholds_changed"])
        self.assertFalse(self.result["result_controls_source_inclusion"])
        self.assertFalse(self.result["production_integration"])
        self.assertEqual(self.result["calls"], {"baseline_visual_receptor": 16, "memory": 0, "context": 0, "field": 0})

    def test_08_read_only_verifier_accepts_canonical_and_rejects_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "comparison.json"
            path.write_bytes(comparison._canonical_bytes(self.result, newline=True))
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            receipt = comparison.verify_comparison_file(path)
            self.assertEqual(receipt["verification_status"], "RECORDING_COMPLETE")
            self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())
            mutated = json.loads(path.read_text(encoding="ascii"))
            mutated["thresholds_changed"] = True
            path.write_bytes(comparison._canonical_bytes(mutated, newline=True))
            with self.assertRaises(comparison.S2LUComparisonError):
                comparison.verify_comparison_file(path)

    def test_09_main_gates_remain_closed(self) -> None:
        self.assertFalse(corpus.PLAN_ENABLED)
        self.assertFalse(comparison.COMPARISON_ENABLED)


if __name__ == "__main__":
    unittest.main()
