"""One focused qualification of the prospective scaled S2-MT materialization."""

from __future__ import annotations

import struct
import unittest

from tools import _s2mt_private_presealed_transfer_sources as base_sources
from tools import _s2mt_private_transfer_runtime_runner as runner
from tools import _s2mx_private_scaled_transfer_sources as sources


class S2MXScaledTransferMaterializationQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if runner.MAIN_EXECUTION_ENABLED or runner._MAIN_USED:
            raise AssertionError("main execution state differs before qualification")
        cls.base_plan = base_sources.build_presealed_plan()
        cls.plan = sources.build_presealed_plan()
        cls.config = runner.field_source._build_config()
        cls.materialized = runner._materialize_events(cls.plan, cls.config)
        cls.geometry = runner._geometry(cls.materialized, cls.config)

    def test_01_new_plan_binds_one_common_factor_and_historical_evidence(self) -> None:
        self.assertEqual(self.plan.audio_input_scale, sources.AUDIO_INPUT_SCALE)
        self.assertEqual(struct.pack("<f", self.plan.audio_input_scale).hex(), "e56a7d3f")
        self.assertEqual(self.plan.compatibility_evidence_directory_id, "s2mw-audio-receptor-compatibility-20260906-02")
        self.assertEqual(self.plan.compatibility_evidence_embedded_audit_id, "s2mw-audio-receptor-compatibility-20260905-01")
        self.assertEqual(self.plan.compatibility_evidence_record_digest, sources.S2MW_EVIDENCE_RECORD_DIGEST)
        self.assertNotEqual(self.plan.plan_digest, self.base_plan.plan_digest)

    def test_02_all_13_scaled_payloads_are_new_and_visual_payloads_are_unchanged(self) -> None:
        self.assertEqual(len(self.plan.recipes), 13)
        for scaled, base in zip(self.plan.recipes, self.base_plan.recipes, strict=True):
            with self.subTest(recipe_id=scaled.recipe_id):
                self.assertEqual(scaled.base_recipe_digest, base.recipe_digest)
                self.assertEqual(scaled.base_auditory_payload_digest, base.auditory_payload_digest)
                self.assertNotEqual(scaled.auditory_payload_digest, base.auditory_payload_digest)
                self.assertEqual(scaled.visual_payload_digest, base.visual_payload_digest)
                self.assertEqual(scaled.partial_visual_payload_digest, base.partial_visual_payload_digest)
                self.assertEqual(scaled.recipe_digest, sources._digest(scaled.payload_without_digest()))

    def test_03_materialization_completes_exactly_28_events(self) -> None:
        self.assertEqual(len(self.materialized), 28)
        self.assertEqual(sum(item.spec.event_type == "COMPLETE_AV_PERCEPTION" for item in self.materialized), 20)
        self.assertEqual(sum(item.spec.event_type == "PARTIAL_AUDITORY_CUE" for item in self.materialized), 4)
        self.assertEqual(sum(item.spec.event_type == "PARTIAL_VISUAL_CUE" for item in self.materialized), 4)
        self.assertEqual(tuple(item.spec for item in self.materialized), runner.EVENT_SPECS)

    def test_04_all_materialized_auditory_values_fit_the_contact_domain(self) -> None:
        auditory_values = []
        for item in self.materialized:
            if item.spec.event_type == "COMPLETE_AV_PERCEPTION":
                auditory_values.append(tuple(item.operation_payload.auditory.timed_frame.frame.values))
            elif item.spec.event_type == "PARTIAL_AUDITORY_CUE":
                auditory_values.append(tuple(value for value in item.operation_payload.cue.values if value is not None))
        self.assertEqual(len(auditory_values), 24)
        self.assertTrue(all(values and max(values) <= 1.0 and min(values) >= 0.0 for values in auditory_values))

    def test_05_all_four_visual_cues_bind_the_materialized_source_digest(self) -> None:
        visual = tuple(item for item in self.materialized if item.spec.event_type == "PARTIAL_VISUAL_CUE")
        self.assertEqual([item.spec.event_code for item in visual], ["e22", "e24", "e26", "e28"])
        for item in visual:
            with self.subTest(event_code=item.spec.event_code):
                self.assertEqual(item.source_digest, item.operation_payload.source_digest)
                self.assertEqual(item.perception_digest, item.operation_payload.cue_digest)
        self.assertEqual(len({item.source_digest for item in visual}), 4)
        self.assertEqual(len({item.source_receipt_digest for item in visual}), 4)

    def test_06_geometry_is_complete_and_canonically_bound(self) -> None:
        self.assertEqual(len(self.geometry["pairwise"]), 66)
        self.assertEqual(len(self.geometry["cue_matches"]), 8)
        payload = dict(self.geometry)
        digest = payload.pop("geometry_digest")
        self.assertEqual(digest, runner._digest(payload))

    def test_07_geometry_startgate_is_satisfied(self) -> None:
        self.assertEqual(self.geometry["status"], "S2MT_GEOMETRY_MATERIALIZED")

    def test_08_no_main_runtime_or_stateful_system_path_was_used(self) -> None:
        self.assertFalse(runner.MAIN_EXECUTION_ENABLED)
        self.assertFalse(runner._MAIN_USED)


if __name__ == "__main__":
    unittest.main()
