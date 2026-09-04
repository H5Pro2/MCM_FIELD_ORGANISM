from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools import _s2lw_private_spatial_mask_comparison as comparison
from tools import _s2lw_private_spatial_mask_corpus as corpus


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


class S2LWSpatialMaskComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = comparison._load_plan(WORKSPACE_ROOT)
        cls.result = comparison.build_comparison(WORKSPACE_ROOT)

    def test_01_presealed_sources_are_complete_and_brightness_paired(self) -> None:
        bindings = {item["content_id"]: item for item in self.plan["generation_root"]["source_bindings"]}
        self.assertEqual(len(bindings), 32)
        self.assertEqual(len({item["payload_sha256"] for item in bindings.values()}), 32)
        for group in self.plan["evaluation_root"]["paired_variants"]:
            selected = [bindings[item] for item in group["content_ids"]]
            self.assertEqual(len({item["histogram_digest"] for item in selected}), 1)
            self.assertEqual(len({item["rgb_value_sum"] for item in selected}), 1)

    def test_02_coordinate_only_order_is_deterministic_and_complete(self) -> None:
        first = corpus.coordinate_only_order()
        second = corpus.coordinate_only_order()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 288)
        self.assertEqual(set(first), set(range(288)))
        self.assertEqual(corpus._digest(list(first)), self.plan["mask_root"]["coordinate_order_digest"])

    def test_03_masks_are_nested_and_have_bound_coverage(self) -> None:
        masks = {item["mask_id"]: item for item in self.plan["mask_root"]["masks"]}
        self.assertEqual(masks["TOP_ROW_32"]["positions"], list(range(32)))
        self.assertEqual(masks["TOP_ROW_32"]["rows_represented"], [0])
        self.assertEqual(masks["SPATIAL_SEEDED_32"]["rows_represented"], list(range(8)))
        self.assertEqual(masks["SPATIAL_SEEDED_32"]["columns_represented"], list(range(12)))
        self.assertEqual(set(masks["SPATIAL_SEEDED_32"]["positions"]), set(masks["SPATIAL_SEEDED_96"]["positions"][:32]))
        self.assertTrue(set(masks["SPATIAL_SEEDED_32"]["positions"]).issubset(masks["SPATIAL_SEEDED_96"]["positions"]))

    def test_04_complete_pair_inventory_has_all_three_masks(self) -> None:
        rows = self.result["complete_pair_distances"]
        self.assertEqual(len(rows), 496)
        self.assertEqual(sum(row["relation"] == "WITHIN_FAMILY" for row in rows), 112)
        self.assertEqual(sum(row["relation"] == "BETWEEN_FAMILY" for row in rows), 384)
        for row in rows:
            self.assertEqual(tuple(row["masks"]), ("TOP_ROW_32", "SPATIAL_SEEDED_32", "SPATIAL_SEEDED_96"))

    def test_05_distance_and_threshold_summaries_match_pair_rows(self) -> None:
        summaries = {item["relation"]: item for item in self.result["relation_summaries"]}
        rows = self.result["complete_pair_distances"]
        for relation, summary in summaries.items():
            selected = [row for row in rows if row["relation"] == relation]
            for mask_id, mask_summary in summary["masks"].items():
                values = [row["masks"][mask_id]["mean_l1"] for row in selected]
                self.assertEqual(mask_summary["metric"]["count_at_or_below_visual_slow_0_01"], sum(value <= 0.01 for value in values))
                self.assertEqual(mask_summary["metric"]["count_at_or_below_fast_0_2"], sum(value <= 0.2 for value in values))
                self.assertEqual(mask_summary["exact_equal_count"], sum(row["masks"][mask_id]["exact_equal"] for row in selected))

    def test_06_leave_one_out_rows_and_ambiguities_are_explicit(self) -> None:
        evaluations = self.result["leave_one_out_evaluations"]
        self.assertEqual([item["representation_id"] for item in evaluations], ["FULL_288", "TOP_ROW_32", "SPATIAL_SEEDED_32", "SPATIAL_SEEDED_96"])
        for evaluation in evaluations:
            self.assertEqual(evaluation["total"], 32)
            self.assertEqual(len(evaluation["rows"]), 32)
            self.assertEqual(evaluation["ambiguous"], sum(row["ambiguous"] for row in evaluation["rows"]))

    def test_07_collision_inventories_are_reconstructable(self) -> None:
        states = self.result["state_bindings"]
        for mask_id, inventory in self.result["masked_collision_inventories"].items():
            unique = {state["masked_values_digests"][mask_id] for state in states}
            self.assertEqual(inventory["unique_masked_vectors"], len(unique))
            self.assertEqual(inventory["sources_in_cross_family_collision_groups"], sum(len(group["content_ids"]) for group in inventory["groups"]))

    def test_08_scope_boundaries_and_gates_remain_closed(self) -> None:
        self.assertEqual(self.result["calls"], {"visual_receptor": 32, "memory": 0, "context": 0, "field": 0})
        self.assertFalse(self.result["thresholds_selected_or_changed"])
        self.assertFalse(self.result["result_controls_source_or_mask_inclusion"])
        self.assertFalse(self.result["raw_payload_retained"])
        self.assertFalse(self.result["production_integration"])
        self.assertFalse(corpus.PLAN_ENABLED)
        self.assertFalse(comparison.COMPARISON_ENABLED)

    def test_09_read_only_verifier_accepts_canonical_and_rejects_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "comparison.json"
            path.write_bytes(comparison._canonical_bytes(self.result, newline=True))
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            receipt = comparison.verify_comparison_file(path)
            self.assertEqual(receipt["verification_status"], "RECORDING_COMPLETE")
            self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())
            mutated = json.loads(path.read_text(encoding="ascii"))
            mutated["thresholds_selected_or_changed"] = True
            path.write_bytes(comparison._canonical_bytes(mutated, newline=True))
            with self.assertRaises(comparison.S2LWComparisonError):
                comparison.verify_comparison_file(path)


if __name__ == "__main__":
    unittest.main()
