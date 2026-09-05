from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools import _s2lz_private_open_set_comparison as comparison


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2lz-open-set-neutral-qualification-20260905-01"


class S2LZOpenSetComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = comparison._load_plan(WORKSPACE_ROOT)
        cls.result = comparison.build_comparison(WORKSPACE_ROOT)

    def test_01_presealed_open_set_inventory_is_complete(self) -> None:
        self.assertEqual(self.result["presealed_plan_file_sha256"], comparison.PLAN_BINDING[1])
        self.assertEqual(self.result["presealed_plan_digest"], comparison.PLAN_BINDING[2])
        self.assertEqual((self.result["source_count"], self.result["reference_source_count"]), (32, 16))
        self.assertEqual((self.result["case_count"], self.result["observation_count"]), (20, 40))
        kinds = [item["expected_kind"] for item in self.plan["evaluation_root"]["cases"]]
        self.assertEqual([kinds.count(item) for item in ("KNOWN_HOLDOUT", "UNKNOWN_FORM", "AMBIGUOUS_INTERMEDIATE", "INCOMPATIBLE_PAIR")], [8, 4, 4, 4])

    def test_02_masks_are_disjoint_coordinate_only_and_cover_every_axis(self) -> None:
        masks = {item["mask_id"]: item for item in self.plan["mask_root"]["masks"]}
        first, second, union = (set(masks[item]["positions"]) for item in ("VIEW_A_96", "VIEW_B_96", "UNION_192"))
        self.assertTrue(first.isdisjoint(second))
        self.assertEqual((len(first), len(second), len(union)), (96, 96, 192))
        self.assertEqual(first | second, union)
        self.assertFalse(self.plan["mask_root"]["image_values_or_evaluation_roles_available"])

    def test_03_reference_calibration_is_sealed_away_from_all_test_sources(self) -> None:
        references = {source_id for group in self.plan["execution_root"]["reference_groups"] for source_id in group["reference_source_ids"]}
        tests = {case[key] for case in self.plan["execution_root"]["cases"] for key in ("view_a_source_id", "view_b_source_id")}
        self.assertEqual(len(references), 16)
        self.assertTrue(references.isdisjoint(tests))
        self.assertFalse(self.result["calibration_envelopes"]["test_sources_available"])
        self.assertFalse(self.result["test_source_used_for_calibration"])

    def test_04_all_model_envelopes_use_the_literal_reference_maximum(self) -> None:
        envelopes = self.result["calibration_envelopes"]["representations"]
        self.assertEqual(set(envelopes), set(comparison.REPRESENTATION_IDS))
        for representation_id in comparison.REPRESENTATION_IDS:
            self.assertEqual(len(envelopes[representation_id]), 4)
            for envelope in envelopes[representation_id]:
                self.assertEqual(envelope["calibration_radius"], max(envelope["reference_distances"]))
                self.assertEqual(len(envelope["reference_source_ids"]), 4)
                self.assertEqual(len(envelope["reference_value_digests"]), 4)

    def test_05_open_set_rule_distinguishes_zero_one_and_multiple_models(self) -> None:
        one = comparison._open_set_decision((0.0,), {"model-01": ((0.0,), 0.1), "model-02": ((1.0,), 0.1)})
        zero = comparison._open_set_decision((0.5,), {"model-01": ((0.0,), 0.1), "model-02": ((1.0,), 0.1)})
        multiple = comparison._open_set_decision((0.5,), {"model-01": ((0.0,), 0.6), "model-02": ((1.0,), 0.6)})
        self.assertEqual((one["status"], one["selected_model_id"]), ("ADMITTED", "model-01"))
        self.assertEqual((zero["status"], zero["reason"]), ("ABSTAINED", "NO_MODEL_WITHIN_ENVELOPE"))
        self.assertEqual((multiple["status"], multiple["reason"]), ("ABSTAINED", "MULTIPLE_MODELS_WITHIN_ENVELOPE"))

    def test_06_pair_compatibility_binds_source_payload_and_tick_gap(self) -> None:
        compatible = [item for item in self.result["pair_bindings"] if item["compatible"]]
        incompatible = [item for item in self.result["pair_bindings"] if not item["compatible"]]
        self.assertEqual((len(compatible), len(incompatible)), (16, 4))
        self.assertTrue(all(item["same_source_id"] and item["same_payload_digest"] and item["tick_gap"] == 1 for item in compatible))
        self.assertTrue(all(not item["same_source_id"] for item in incompatible))

    def test_07_union_is_built_only_for_compatible_observed_pairs(self) -> None:
        incompatible_ids = {item["case_id"] for item in self.result["pair_bindings"] if not item["compatible"]}
        for arm_id in ("TWO_VIEW_CONSENSUS_OPEN_SET", "UNION_192_OPEN_SET", "FULL_FORM_OPEN_SET_UPPER_BOUND"):
            rows = {item["case_id"]: item for item in self.result["decisions"][arm_id]}
            self.assertTrue(all(rows[case_id]["selected_model_id"] is None for case_id in incompatible_ids))
        self.assertEqual(self.result["rules"]["missing_values"], "NOT_PRESENT_NOT_IMPUTED")

    def test_08_all_arms_and_receptor_events_are_complete(self) -> None:
        self.assertEqual(set(self.result["decisions"]), set(comparison.ARM_IDS))
        self.assertTrue(all(len(rows) == 20 for rows in self.result["decisions"].values()))
        self.assertEqual(len(self.result["state_bindings"]), 56)
        self.assertEqual(self.result["calls"], {"visual_receptor": 56, "memory": 0, "context": 0, "field": 0})

    def test_09_metrics_partition_each_evaluated_case_exactly_once(self) -> None:
        for evaluation in self.result["evaluations"]:
            self.assertEqual(
                evaluation["known_hits"] + evaluation["known_wrong_admissions"] + evaluation["known_abstentions"]
                + evaluation["open_set_correct_abstentions"] + evaluation["open_set_false_admissions"],
                evaluation["evaluated_case_count"],
            )
            self.assertEqual(evaluation["evaluated_case_count"], 16 if evaluation["arm_id"] in {"VIEW_A_OPEN_SET", "VIEW_B_OPEN_SET"} else 20)

    def test_10_test_outcomes_do_not_gate_recording_or_recalibrate(self) -> None:
        self.assertEqual(self.result["status"], "S2LZ_OPEN_SET_COMPARISON_EVALUATED")
        self.assertFalse(self.result["post_test_threshold_selection"])
        self.assertFalse(self.result["test_source_used_for_calibration"])
        self.assertEqual(self.plan["execution_root"]["calibration_rule"], "PER_MODEL_MAX_REFERENCE_TO_REFERENCE_CENTROID_MEAN_L1")

    def test_11_gates_and_scope_boundaries_remain_closed(self) -> None:
        self.assertFalse(comparison.COMPARISON_ENABLED)
        self.assertFalse(self.result["raw_payload_retained"])
        self.assertFalse(self.result["production_integration"])
        self.assertEqual(self.plan["forbidden_calls"], {"memory": 0, "context": 0, "field": 0})

    def test_12_read_only_verifier_accepts_canonical_and_rejects_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "comparison.json"
            path.write_bytes(comparison._canonical_bytes(self.result, newline=True))
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            receipt = comparison.verify_comparison_file(path)
            self.assertEqual(receipt["verification_status"], "RECORDING_COMPLETE")
            self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())
            mutated = json.loads(path.read_text(encoding="ascii"))
            mutated["post_test_threshold_selection"] = True
            path.write_bytes(comparison._canonical_bytes(mutated, newline=True))
            with self.assertRaises(comparison.S2LZComparisonError):
                comparison.verify_comparison_file(path)


if __name__ == "__main__":
    unittest.main()
