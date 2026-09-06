"""Category-interface qualification with synthetic decisions, never corpus values."""

from collections import Counter
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from tools import _s2nc_private_rule_comparison as c
from tools import _s2nc_private_rule_evaluation as evaluation


PLAN = (Path(__file__).resolve().parents[1] / "reports/s2nc/"
        "s2nc-source-panel-preseal-20260906-01/evaluation-plan.json")
PLAN_SHA256 = "0a2e61adb26fa93ed4607a059db87851720a7636c7253f65206827996ec9ae65"
CATEGORIES = (
    "KNOWN_EXACT", "KNOWN_FREQUENCY_VARIANT", "KNOWN_GAIN_VARIANT",
    "LOW_INFORMATION_QUIET", "LOW_INFORMATION_SILENCE", "MIXED_SOURCE", "UNKNOWN",
)


def synthetic_result(case_id, rule, status, source_ids=()):
    # Only the evaluator interface is exercised, not a fabricated scan receipt.
    binding = c.digest(("synthetic-category-interface", case_id))
    decision = c.Decision(status, source_ids, c.digest("synthetic-values") if source_ids else None)
    return c.sealed(c.CaseResult(case_id, rule, binding, c.POSITIONS, (), (), (),
                               decision, 0, 0, binding, binding))


def assess(category, left_status="A_RECENT_NOT_APPLICABLE",
           right_status="A_RECENT_NOT_APPLICABLE", accepted=(), left_ids=(), right_ids=()):
    left = synthetic_result("neutral-case", c.RULES[0], left_status, left_ids)
    right = synthetic_result("neutral-case", c.RULES[1], right_status, right_ids)
    expected = evaluation.Expectation("neutral-case", category, accepted)
    return evaluation.evaluate((left,), (right,), (expected,))


class S2NCCategoryBindingTests(unittest.TestCase):
    def setUp(self):
        for name in ("compare_case", "bind_materialized_sources", "bind_fixed_cases"):
            blocked = patch.object(c, name, side_effect=AssertionError("CORPUS_OR_RULE_CALL_FORBIDDEN"))
            blocked.start()
            self.addCleanup(blocked.stop)

    def test_01_all_48_plan_categories_with_synthetic_decisions(self):
        raw = PLAN.read_bytes()
        self.assertEqual(PLAN_SHA256, hashlib.sha256(raw).hexdigest())
        plan = json.loads(raw)
        self.assertEqual(CATEGORIES, evaluation.EVALUATION_CATEGORIES)
        self.assertEqual(set(CATEGORIES), {row["category"] for row in plan["cases"]})
        expected = tuple(evaluation.Expectation(row["case_id"], row["category"],
                                                tuple(row["accepted_source_ids"]))
                         for row in plan["cases"])
        arms = tuple(tuple(synthetic_result(
            item.case_id, rule,
            "A_RECENT_APPLICABLE" if item.accepted_source_ids else "A_RECENT_ABSENT_VALID",
            item.accepted_source_ids) for item in expected) for rule in c.RULES)
        before = c.digest([[asdict(item) for item in arm] for arm in arms])
        result = evaluation.evaluate(*arms, expected)
        self.assertEqual(48, len(result["cases"]))
        self.assertEqual("CONFIRMED", result["mean_prediction_status"])
        self.assertEqual("CONFIRMED", result["all_prediction_status"])
        counts = Counter(item.category for item in expected)
        self.assertEqual({key: (12 if key == "UNKNOWN" else 6) for key in CATEGORIES}, dict(counts))
        self.assertEqual(dict(counts), {key: row["denominator"] for key, row in result["categories"].items()})
        self.assertEqual(before, c.digest([[asdict(item) for item in arm] for arm in arms]))
        self.assertEqual(raw, PLAN.read_bytes())

    def test_02_each_category_accepts_all_valid_statuses_without_reclassifying_failure(self):
        for category in CATEGORIES:
            for status in c.STATUSES:
                with self.subTest(category=category, status=status):
                    ids = ("neutral-source",) if status == "A_RECENT_APPLICABLE" else ()
                    result = assess(category, status, status, ("neutral-source",), ids, ids)
                    predicted = "CONFIRMED" if ids else "FALSIFIED"
                    self.assertEqual(predicted, result["mean_prediction_status"])
                    self.assertEqual(predicted, result["all_prediction_status"])
                    self.assertEqual(status, result["cases"][0]["all_bands"]["status"])

    def test_03_unbound_categories_fail_closed(self):
        class StringSubclass(str):
            pass

        invalid = (None, 7, True, [], {}, "", "neutral", "known", "KNOWN_NEW", "UNKNOWN_SOURCE")
        invalid += tuple(variant for category in CATEGORIES for variant in (
            category.lower(), category + " ", " " + category, category + "\n", StringSubclass(category)))
        invalid += tuple(category.replace("_", "-") for category in CATEGORIES if "_" in category)
        for category in invalid:
            with self.subTest(category=repr(category)):
                with self.assertRaisesRegex(c.ComparisonError, "^EXPECTATION_INVALID$"):
                    assess(category)

    def test_04_general_identifier_and_source_validation_stay_restricted(self):
        self.assertTrue(c.identifier("neutral-source-01"))
        for category in CATEGORIES:
            self.assertFalse(c.identifier(category))
            with self.assertRaisesRegex(c.ComparisonError, "^EXPECTATION_INVALID$"):
                assess("KNOWN_EXACT", accepted=(category,))
        for source_ids in (["neutral-source"], ("neutral-source", "neutral-source")):
            with self.assertRaisesRegex(c.ComparisonError, "^EXPECTATION_INVALID$"):
                assess("KNOWN_EXACT", accepted=source_ids)

    def test_05_losses_false_admissions_and_digest_integrity_remain_distinct(self):
        lost = assess("KNOWN_GAIN_VARIANT", "A_RECENT_APPLICABLE", accepted=("right",), left_ids=("right",))
        self.assertEqual(1, lost["lost_known_hits"])
        self.assertEqual("NEGATIVE", lost["status"])
        false = assess("UNKNOWN", right_status="A_RECENT_APPLICABLE", right_ids=("wrong",))
        self.assertEqual(1, false["new_false_admissions"])
        self.assertEqual("NEGATIVE", false["status"])
        for result in (lost, false):
            self.assertEqual(result["evaluation_digest"], c.digest({
                key: value for key, value in result.items() if key != "evaluation_digest"}))
        left = synthetic_result("neutral-case", c.RULES[0], "A_RECENT_ABSENT_VALID")
        right = synthetic_result("neutral-case", c.RULES[1], "A_RECENT_ABSENT_VALID")
        with self.assertRaisesRegex(c.ComparisonError, "^DIGEST_INVALID$"):
            evaluation.evaluate((replace(left, poststate_digest=c.digest("changed")),), (right,),
                                (evaluation.Expectation("neutral-case", "KNOWN_EXACT", ()),))


if __name__ == "__main__":
    unittest.main()
