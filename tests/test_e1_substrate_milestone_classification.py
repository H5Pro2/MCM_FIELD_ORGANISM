from __future__ import annotations

import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_substrate_milestone_classification import (
    S1_DR_NEXT_STAGE,
    S1_DR_STATUS,
    classify_e1_substrate_milestone,
)


REPORT = Path("reports/e1_frozen_state_transfer_s1dn_once_v1.json")


class E1SubstrateMilestoneClassificationTests(unittest.TestCase):
    def test_given_state_transfer_milestone_is_classified(self) -> None:
        result = classify_e1_substrate_milestone(REPORT)

        self.assertEqual(S1_DR_STATUS, result.status)
        self.assertTrue(result.given_state_changes_later_field)
        self.assertTrue(result.effect_is_ablatable)
        self.assertTrue(result.fixed_adapter_equivalent)

    def test_unresolved_scientific_steps_remain_false(self) -> None:
        result = classify_e1_substrate_milestone(REPORT)

        self.assertFalse(result.world_formation_causality_established)
        self.assertFalse(result.reconstruction_established)
        self.assertFalse(result.memory_lifecycle_established)
        self.assertFalse(result.full_s1_dc_decision_permitted)

    def test_next_stage_requires_a_new_refined_formation_contract(self) -> None:
        result = classify_e1_substrate_milestone(REPORT)

        self.assertEqual(S1_DR_NEXT_STAGE, result.next_stage)

    def test_classification_digest_is_repeatable(self) -> None:
        first = classify_e1_substrate_milestone(REPORT)
        second = classify_e1_substrate_milestone(REPORT)

        self.assertEqual(first.classification_digest, second.classification_digest)
        self.assertEqual(64, len(first.classification_digest))

    def test_missing_report_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "missing"):
                classify_e1_substrate_milestone(Path(directory) / "missing.json")

    def test_classification_is_static_and_private(self) -> None:
        source = inspect.getsource(classify_e1_substrate_milestone)
        for forbidden in (
            "produce_e1_frozen_state_transfer",
            "execute_e1_frozen_state_transfer_one_shot",
            "advance_frozen_e1_fast_shared_field_transient",
        ):
            self.assertNotIn(forbidden, source)
        for role in (
            "E1SubstrateMilestoneClassification",
            "classify_e1_substrate_milestone",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
