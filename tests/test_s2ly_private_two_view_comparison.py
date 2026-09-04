from __future__ import annotations

from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from tools import _s2ly_private_two_view_comparison as comparison
from tools import _s2ly_private_two_view_corpus as corpus
from tools import _s2ly_private_two_view_projection as projection


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2ly-two-view-neutral-qualification-20260905-02"


class S2LYTwoViewComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = comparison._load_plan(WORKSPACE_ROOT)
        cls.masks = {item["mask_id"]: item for item in cls.plan["mask_root"]["masks"]}
        cls.result = comparison.build_comparison(WORKSPACE_ROOT)

    def test_01_presealed_source_and_split_inventory(self) -> None:
        self.assertEqual(self.result["presealed_plan_file_sha256"], comparison.PLAN_BINDING[1])
        self.assertEqual(self.result["presealed_plan_digest"], comparison.PLAN_BINDING[2])
        self.assertEqual((self.result["source_count"], self.result["candidate_count"], self.result["cue_count"]), (32, 4, 28))
        bindings = self.plan["generation_root"]["source_bindings"]
        self.assertEqual(len({item["payload_sha256"] for item in bindings}), 32)

    def test_02_two_coordinate_masks_are_disjoint_and_cover_the_grid(self) -> None:
        first = set(self.masks["VIEW_A_96"]["positions"])
        second = set(self.masks["VIEW_B_96"]["positions"])
        union = set(self.masks["UNION_192"]["positions"])
        self.assertEqual((len(first), len(second), len(union)), (96, 96, 192))
        self.assertTrue(first.isdisjoint(second))
        self.assertEqual(first | second, union)
        for mask in self.masks.values():
            self.assertEqual(mask["rows_represented"], list(range(8)))
            self.assertEqual(mask["columns_represented"], list(range(12)))
            self.assertTrue(all(mask["channel_counts"][str(channel)] > 0 for channel in range(3)))

    def test_03_mask_generation_and_execution_are_role_free(self) -> None:
        self.assertFalse(self.plan["mask_root"]["image_values_available_to_mask_generation"])
        self.assertFalse(self.plan["mask_root"]["evaluation_roles_available_to_mask_generation"])
        self.assertFalse(self.plan["execution_root"]["candidate_family_roles_available"])
        self.assertFalse(self.plan["execution_root"]["cue_family_roles_available"])
        self.assertFalse(self.plan["evaluation_root"]["result_controls_source_or_mask_inclusion"])

    def test_04_observed_views_are_immutable_and_digest_bound(self) -> None:
        recipe = self.plan["generation_root"]["recipes"][0]
        frame = corpus.render_frame(recipe)
        values = tuple(LocalChannelGridReceptor(VisualGridConfig()).analyze(frame, frame_index=0).channel_values)
        mask = self.masks["VIEW_A_96"]
        view = projection.bind_observed_view(values, mask["mask_id"], tuple(mask["positions"]), mask["mask_digest"])
        self.assertEqual(view.observed_values, tuple(values[index] for index in mask["positions"]))
        with self.assertRaises(FrozenInstanceError):
            view.mask_id = "VIEW_B_96"

    def test_05_hidden_values_do_not_affect_either_mask_projection(self) -> None:
        recipe = self.plan["generation_root"]["recipes"][1]
        frame = corpus.render_frame(recipe)
        original = tuple(LocalChannelGridReceptor(VisualGridConfig()).analyze(frame, frame_index=0).channel_values)
        for mask_id in ("VIEW_A_96", "VIEW_B_96"):
            mask = self.masks[mask_id]
            visible = set(mask["positions"])
            changed = tuple(value if index in visible else 1.0 - value for index, value in enumerate(original))
            first_view = projection.bind_observed_view(original, mask_id, tuple(mask["positions"]), mask["mask_digest"])
            second_view = projection.bind_observed_view(changed, mask_id, tuple(mask["positions"]), mask["mask_digest"])
            first = projection.project_mask_conditioned_form(first_view)
            second = projection.project_mask_conditioned_form(second_view)
            self.assertNotEqual(first_view.source_values_digest, second_view.source_values_digest)
            self.assertEqual(first_view.observed_values_digest, second_view.observed_values_digest)
            self.assertEqual(first.values, second.values)

    def test_06_projection_accepts_only_bound_96_or_192_value_views(self) -> None:
        values = tuple(float(index) / 287.0 for index in range(288))
        for mask_id in ("VIEW_A_96", "VIEW_B_96", "UNION_192"):
            mask = self.masks[mask_id]
            view = projection.bind_observed_view(values, mask_id, tuple(mask["positions"]), mask["mask_digest"])
            self.assertEqual(len(view.observed_values), mask["value_count"])
        with self.assertRaises(projection.S2LYProjectionError):
            projection.bind_observed_view(values, "VIEW_A_96", tuple(range(95)), "0" * 64)
        with self.assertRaises(projection.S2LYProjectionError):
            projection.bind_observed_view(values, "UNION_192", tuple(range(96)), "0" * 64)

    def test_07_unique_ambiguity_and_consensus_rules_are_exact(self) -> None:
        candidates = {
            "candidate-01": (0.0, 0.0),
            "candidate-02": (1.0, 1.0),
            "candidate-03": (0.0, 1.0),
            "candidate-04": (1.0, 0.0),
        }
        unique = comparison._nearest_unique((0.1, 0.1), candidates)
        tied = comparison._nearest_unique((0.5, 0.5), candidates)
        self.assertEqual((unique["status"], unique["selected_candidate_id"]), ("UNIQUE", "candidate-01"))
        self.assertEqual((tied["status"], tied["selected_candidate_id"]), ("AMBIGUOUS", None))
        self.assertEqual(comparison._consensus(unique, unique)["status"], "ADMITTED")
        self.assertEqual(comparison._consensus(unique, tied)["status"], "ABSTAINED")
        other = comparison._nearest_unique((0.9, 0.9), candidates)
        self.assertEqual(comparison._consensus(unique, other)["reason"], "UNIQUE_VIEWS_DISAGREE")

    def test_08_all_two_view_observations_are_strictly_sequential(self) -> None:
        observations = self.plan["execution_root"]["observations"]
        self.assertEqual(len(observations), 56)
        for index in range(0, 56, 2):
            first, second = observations[index:index + 2]
            self.assertEqual(first["content_id"], second["content_id"])
            self.assertEqual((first["mask_id"], second["mask_id"]), ("VIEW_A_96", "VIEW_B_96"))
            self.assertLess(first["tick"], second["tick"])
        observed_states = [item for item in self.result["state_bindings"] if item["observation_digest"] is not None]
        self.assertEqual(len(observed_states), 56)

    def test_09_all_arms_report_false_admissions_abstentions_and_coverage(self) -> None:
        self.assertEqual(tuple(item["arm_id"] for item in self.result["evaluations"]), comparison.ARM_IDS)
        for evaluation in self.result["evaluations"]:
            self.assertEqual(evaluation["total"], 28)
            self.assertEqual(
                evaluation["correct_admissions"] + evaluation["false_admissions"] + evaluation["abstentions"],
                28,
            )
            self.assertEqual(evaluation["correct_coverage"], evaluation["correct_admissions"] / 28)

    def test_10_two_view_consensus_is_reconstructed_only_from_both_views(self) -> None:
        for index in range(28):
            first = self.result["decisions"]["VIEW_A_MASKED_FORM_96"][index]
            second = self.result["decisions"]["VIEW_B_MASKED_FORM_96"][index]
            consensus = self.result["decisions"]["TWO_VIEW_CONSENSUS"][index]
            expected = first["selected_candidate_id"] if first["status"] == second["status"] == "UNIQUE" and first["selected_candidate_id"] == second["selected_candidate_id"] else None
            self.assertEqual(consensus["selected_candidate_id"], expected)

    def test_11_scope_and_resource_boundaries_remain_closed(self) -> None:
        self.assertEqual(self.result["calls"], {"visual_receptor": 60, "memory": 0, "context": 0, "field": 0})
        self.assertFalse(self.result["thresholds_selected_or_changed"])
        self.assertFalse(self.result["training_or_parameter_search"])
        self.assertFalse(self.result["raw_payload_retained"])
        self.assertFalse(self.result["production_integration"])
        self.assertFalse(comparison.COMPARISON_ENABLED)

    def test_12_read_only_verifier_accepts_canonical_and_rejects_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "comparison.json"
            path.write_bytes(comparison._canonical_bytes(self.result, newline=True))
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            receipt = comparison.verify_comparison_file(path)
            self.assertEqual(receipt["verification_status"], "RECORDING_COMPLETE")
            self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())
            mutated = json.loads(path.read_text(encoding="ascii"))
            mutated["rules"]["hidden_values"] = "IMPUTED"
            path.write_bytes(comparison._canonical_bytes(mutated, newline=True))
            with self.assertRaises(comparison.S2LYComparisonError):
                comparison.verify_comparison_file(path)


if __name__ == "__main__":
    unittest.main()
