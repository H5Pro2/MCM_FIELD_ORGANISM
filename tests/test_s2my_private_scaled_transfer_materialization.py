"""Qualified scaled S2-MT materialization without stateful system execution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from tools import _s2mt_private_transfer_runtime_runner as runner
from tools import _s2mx_private_scaled_transfer_sources as sources


QUALIFICATION_ID = "s2my-scaled-transfer-materialization-20260906-02"
S2MW_RESULT_SHA256 = "b1ca1ad9d11e29c6d5b547d166741f1afbf40fb3e8f240ea6eb07d3f4e7d87ef"


class S2MYScaledTransferMaterializationQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if runner.MAIN_EXECUTION_ENABLED or runner._MAIN_USED:
            raise AssertionError("main execution state differs before qualification")
        workspace = Path(__file__).resolve().parents[1]
        evidence_path = (
            workspace
            / "reports"
            / "s2mw"
            / "s2mw-audio-receptor-compatibility-20260906-02"
            / "result.json"
        )
        if hashlib.sha256(evidence_path.read_bytes()).hexdigest() != S2MW_RESULT_SHA256:
            raise AssertionError("S2-MW evidence file differs")
        cls.s2mw = json.loads(evidence_path.read_text(encoding="ascii"))
        cls.plan = sources.build_presealed_plan()
        cls.config = runner.field_source._build_config()
        cls.materialized = runner._materialize_events(cls.plan, cls.config)
        cls.geometry = runner._geometry(cls.materialized, cls.config)

    def test_01_prospective_plan_and_event_sequence_are_bound(self) -> None:
        self.assertEqual(self.plan.plan_id, "s2mt-presealed-scaled-transfer-plan-v2")
        self.assertEqual(self.plan.audio_input_scale, sources.AUDIO_INPUT_SCALE)
        self.assertEqual(self.plan.audio_input_scale_f32_hex, "e56a7d3f")
        self.assertEqual(self.plan.compatibility_evidence_record_digest, self.s2mw["record_digest"])
        self.assertEqual(self.plan.formation_sequence, sources.FORMATION_SEQUENCE)
        self.assertEqual(self.plan.cue_sequence, sources.CUE_SEQUENCE)

    def test_02_materialization_completes_exactly_28_scaled_events(self) -> None:
        self.assertEqual(len(self.materialized), 28)
        self.assertEqual(sum(item.spec.event_type == "COMPLETE_AV_PERCEPTION" for item in self.materialized), 20)
        self.assertEqual(sum(item.spec.event_type == "PARTIAL_AUDITORY_CUE" for item in self.materialized), 4)
        self.assertEqual(sum(item.spec.event_type == "PARTIAL_VISUAL_CUE" for item in self.materialized), 4)
        self.assertEqual(tuple(item.spec for item in self.materialized), runner.EVENT_SPECS)

    def test_03_all_materialized_audio_values_fit_the_contact_domain(self) -> None:
        frames = [
            timed.frame
            for item in self.materialized
            for timed in item.field_input.timed_frames
            if timed.frame.modality_id == "auditory"
        ]
        self.assertEqual(len(frames), 24)
        self.assertTrue(all(len(frame.values) == 48 for frame in frames))
        self.assertTrue(all(0.0 <= value <= 1.0 for frame in frames for value in frame.values))

    def test_04_all_78_scaled_audio_pair_distances_match_the_bound_audit(self) -> None:
        values_by_recipe = {}
        for item in self.materialized:
            if item.spec.recipe_id in values_by_recipe:
                continue
            auditory = tuple(
                timed.frame
                for timed in item.field_input.timed_frames
                if timed.frame.modality_id == "auditory"
            )
            if auditory:
                values_by_recipe[item.spec.recipe_id] = tuple(auditory[0].values)
        self.assertEqual(tuple(values_by_recipe), sources.RECIPE_IDS)

        expected = {
            (item["left"], item["right"]): item["scaled_full_48_distance"]
            for item in self.s2mw["distances"]["all_recipe_pairs"]
        }
        actual = {}
        for left_index, left in enumerate(sources.RECIPE_IDS):
            for right in sources.RECIPE_IDS[left_index + 1 :]:
                actual[(left, right)] = runner.normalized_mean_l1_distance(
                    values_by_recipe[left],
                    values_by_recipe[right],
                )
        self.assertEqual(len(actual), 78)
        self.assertEqual(actual, expected)

    def test_05_all_four_visual_cues_bind_the_materialized_source_digest(self) -> None:
        visual = tuple(item for item in self.materialized if item.spec.event_type == "PARTIAL_VISUAL_CUE")
        self.assertEqual([item.spec.event_code for item in visual], ["e22", "e24", "e26", "e28"])
        for item in visual:
            with self.subTest(event_code=item.spec.event_code):
                self.assertEqual(item.source_digest, item.operation_payload.source_digest)
                self.assertEqual(item.perception_digest, item.operation_payload.cue_digest)
        self.assertEqual(len({item.source_digest for item in visual}), 4)
        self.assertEqual(len({item.source_receipt_digest for item in visual}), 4)

    def test_06_all_eight_cue_match_sets_are_preserved(self) -> None:
        self.assertEqual(
            [item["matching_training_recipes"] for item in self.geometry["cue_matches"]],
            [["n00"], ["n00"], ["n01"], ["n01"], ["n02"], ["n02"], [], []],
        )
        self.assertEqual(len(self.geometry["cue_matches"]), 8)

    def test_07_thresholds_and_geometry_are_unchanged(self) -> None:
        self.assertEqual(self.config.tspm_config.fast_config.auditory_match_threshold, 0.2)
        self.assertEqual(self.config.tspm_config.fast_config.visual_match_threshold, 0.2)
        self.assertEqual(self.config.tspm_config.profile.auditory_config.match_threshold, 0.02)
        self.assertEqual(self.config.tspm_config.profile.visual_config.match_threshold, 0.01)
        self.assertEqual(len(self.geometry["pairwise"]), 66)
        self.assertTrue(all(item["fast_separated"] for item in self.geometry["pairwise"]))
        self.assertEqual(self.geometry["status"], "S2MT_GEOMETRY_MATERIALIZED")

    def test_08_geometry_digest_is_canonical(self) -> None:
        payload = dict(self.geometry)
        digest = payload.pop("geometry_digest")
        self.assertEqual(digest, runner._digest(payload))

    def test_09_no_main_runtime_or_stateful_system_path_was_used(self) -> None:
        self.assertFalse(runner.MAIN_EXECUTION_ENABLED)
        self.assertFalse(runner._MAIN_USED)


if __name__ == "__main__":
    unittest.main()
