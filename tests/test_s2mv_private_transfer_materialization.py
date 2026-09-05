"""Focused qualification of S2-MT materialization and geometry."""

from __future__ import annotations

import unittest

from tools import _s2mt_private_presealed_transfer_sources as sources
from tools import _s2mt_private_transfer_runtime_runner as runner


class S2MVTransferMaterializationQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if runner.MAIN_EXECUTION_ENABLED or runner._MAIN_USED:
            raise AssertionError("main execution state differs before qualification")
        cls.plan = sources.build_presealed_plan()
        cls.config = runner.field_source._build_config()
        cls.materialized = runner._materialize_events(cls.plan, cls.config)
        cls.geometry = runner._geometry(cls.materialized, cls.config)

    def test_01_presealed_plan_and_event_sequence_are_unchanged(self) -> None:
        self.assertEqual(self.plan.formation_sequence, sources.FORMATION_SEQUENCE)
        self.assertEqual(self.plan.cue_sequence, sources.CUE_SEQUENCE)
        self.assertEqual(self.plan.event_count, 28)
        self.assertEqual(tuple(item.spec for item in self.materialized), runner.EVENT_SPECS)

    def test_02_materialization_completes_all_28_events(self) -> None:
        self.assertEqual(len(self.materialized), 28)
        self.assertEqual(sum(item.spec.event_type == "COMPLETE_AV_PERCEPTION" for item in self.materialized), 20)
        self.assertEqual(sum(item.spec.event_type == "PARTIAL_AUDITORY_CUE" for item in self.materialized), 4)
        self.assertEqual(sum(item.spec.event_type == "PARTIAL_VISUAL_CUE" for item in self.materialized), 4)

    def test_03_all_visual_cues_share_the_materialized_source_digest(self) -> None:
        visual = tuple(item for item in self.materialized if item.spec.event_type == "PARTIAL_VISUAL_CUE")
        self.assertEqual([item.spec.event_code for item in visual], ["e22", "e24", "e26", "e28"])
        for item in visual:
            with self.subTest(event_code=item.spec.event_code):
                self.assertEqual(item.source_digest, item.operation_payload.source_digest)

    def test_04_visual_cue_receipts_remain_distinct_and_bound(self) -> None:
        visual = tuple(item for item in self.materialized if item.spec.event_type == "PARTIAL_VISUAL_CUE")
        self.assertEqual(len({item.source_digest for item in visual}), 4)
        self.assertEqual(len({item.source_receipt_digest for item in visual}), 4)
        self.assertTrue(all(item.perception_digest == item.operation_payload.cue_digest for item in visual))

    def test_05_geometry_projection_is_independently_complete(self) -> None:
        self.assertEqual(len(self.geometry["pairwise"]), 66)
        self.assertEqual(len(self.geometry["cue_matches"]), 8)
        payload = dict(self.geometry)
        digest = payload.pop("geometry_digest")
        self.assertEqual(digest, runner._digest(payload))

    def test_06_materialization_startgate_is_satisfied(self) -> None:
        self.assertEqual(self.geometry["status"], "S2MT_GEOMETRY_MATERIALIZED")

    def test_07_no_main_runtime_was_armed_or_consumed(self) -> None:
        self.assertFalse(runner.MAIN_EXECUTION_ENABLED)
        self.assertFalse(runner._MAIN_USED)


if __name__ == "__main__":
    unittest.main()
