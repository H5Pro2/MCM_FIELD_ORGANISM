"""Neutral qualification only; sealed receptor values are never loaded."""

from copy import deepcopy
from dataclasses import FrozenInstanceError, asdict, replace
from fractions import Fraction
import json
import math
from pathlib import Path
import struct
import hashlib
import unittest

from tools import _s2nc_private_rule_comparison as c
from tools import _s2nc_private_decision_baseline as baseline
from tools import _s2nc_private_rule_evaluation as evaluation


ROOT = Path(__file__).resolve().parents[1]
ROOT_DIGEST = c.digest("neutral-root")
PROFILE_DIGEST = c.digest("neutral-profile")


def source(name, observed=None, hidden=None, start=0):
    values = tuple(observed if observed is not None else (0.0,) * 24)
    values += tuple(hidden if hidden is not None else (0.0,) * 24)
    return c.sealed(c.Source48(name, ROOT_DIGEST, PROFILE_DIGEST, c.digest("parent-" + name),
                               "neutral-clock", start, start + 4800, values, c.digest(values)))


def case(b4=(), fast=(), cue=None, name="neutral-case"):
    cue = cue if cue is not None else source("neutral-cue", start=48000)
    return c.sealed(c.Case(name, "neutral-panel", ROOT_DIGEST, c.project_cue(cue),
                           tuple(b4) + (None,) * (9 - len(b4)),
                           tuple(fast) + (None,) * (3 - len(fast))))


def pair(item):
    return tuple(c.compare_case(item, rule) for rule in c.RULES)


def assess(results, accepted=()):
    left, right = results
    return evaluation.evaluate((left,), (right,),
                               (evaluation.Expectation(left.case_id, "KNOWN_EXACT", accepted),))


class S2NCNeutralComparisonTests(unittest.TestCase):
    def assert_baseline(self, item, result):
        self.assertEqual("TECHNICALLY_VALID", c.verify_case(item, result, result.digest))
        decision, equality = baseline.decide(item, result.b4_matches, result.fast_matches)
        self.assertEqual(result.decision, decision)
        self.assertEqual(result.equality_terms, equality)

    def test_01_inclusive_boundaries_without_tolerance(self):
        exact = case((source("edge", (0.2,) * 24),))
        for result in pair(exact):
            self.assertEqual(0.2, result.rows[0].statistic)
            self.assertTrue(result.rows[0].matched)
            self.assert_baseline(exact, result)
        outside = case((source("outside", (math.nextafter(0.2, 1.0),) * 24),))
        for result in pair(outside):
            self.assertFalse(result.rows[0].matched)
        mixed = case((source("mixed", (0.2,) + (0.0,) * 23),))
        self.assertTrue(pair(mixed)[1].rows[0].matched)

    def test_02_subset_and_arithmetic_mean(self):
        examples = ((0.0,) * 24, (0.2,) * 24, (0.4,) + (0.0,) * 23,
                    (0.1, 0.3) * 12, (1.0,) * 24,
                    (math.nextafter(0.2, 0.0),) * 24,
                    tuple(i / 100.0 for i in range(24)))
        for values in examples:
            left, right = pair(case((source("candidate", values),)))
            self.assertTrue(set(right.b4_matches) <= set(left.b4_matches))
            exact_mean = float(sum((Fraction(v) for v in left.rows[0].terms), Fraction()) / 24)
            self.assertEqual(exact_mean, left.rows[0].mean_distance)

    def test_03_correct_candidate_is_retained(self):
        item = case((source("near"), source("far", (1.0,) * 24)))
        results = pair(item)
        for result in results:
            self.assertEqual(("near",), result.decision.source_ids)
            self.assert_baseline(item, result)
        measured = assess(results, ("near",))
        self.assertEqual("CONFIRMED", measured["mean_prediction_status"])
        self.assertEqual("CONFIRMED", measured["all_prediction_status"])
        self.assertEqual("NO_FUNCTIONAL_IMPROVEMENT", measured["status"])

    def test_04_lost_correct_candidate_counts_as_loss(self):
        item = case((source("related", (0.4,) + (0.0,) * 23),))
        results = pair(item)
        self.assertEqual("A_RECENT_APPLICABLE", results[0].decision.status)
        self.assertEqual("A_RECENT_NOT_APPLICABLE", results[1].decision.status)
        measured = assess(results, ("related",))
        self.assertEqual(1, measured["lost_known_hits"])
        self.assertEqual("NEGATIVE", measured["status"])
        self.assert_baseline(item, results[1])

    def test_05_falsely_unique_remaining_candidate_is_not_progress(self):
        item = case((source("related", (0.4,) + (0.0,) * 23), source("unrelated", (0.1,) * 24)))
        results = pair(item)
        self.assertEqual("A_RECENT_INTERNAL_AMBIGUITY", results[0].decision.status)
        self.assertEqual(("unrelated",), results[1].decision.source_ids)
        measured = assess(results, ("related",))
        self.assertEqual(1, measured["new_false_admissions"])
        self.assertEqual(0, measured["improved_cases"])
        self.assertEqual("NEGATIVE", measured["status"])
        for result in results:
            self.assert_baseline(item, result)

    def test_06_duplicate_bank_hits_do_not_short_circuit_scan(self):
        duplicate = source("same")
        item = case((duplicate,) * 9, (duplicate,) * 3)
        for result in pair(item):
            self.assertEqual(c.POSITIONS, result.visited_positions)
            self.assertEqual(12, len(result.rows))
            self.assertEqual(288, result.band_differences)
            self.assertEqual(tuple(range(9)), result.b4_matches)
            self.assertEqual((0, 1, 2), result.fast_matches)
            self.assertEqual("A_RECENT_INTERNAL_AMBIGUITY", result.decision.status)
            self.assert_baseline(item, result)

    def test_07_cross_bank_equality_preserves_both_provenances(self):
        a, b = source("left"), source("right")
        first, swapped = case((a,), (b,)), case((b,), (a,))
        for rule in c.RULES:
            result, reverse = c.compare_case(first, rule), c.compare_case(swapped, rule)
            self.assertEqual("A_RECENT_APPLICABLE", result.decision.status)
            self.assertEqual(result.decision.status, reverse.decision.status)
            self.assertEqual(result.decision.common_values_digest, reverse.decision.common_values_digest)
            self.assertEqual(set(result.decision.source_ids), set(reverse.decision.source_ids))
            self.assertEqual(48, result.equality_terms)
            self.assert_baseline(first, result)

    def test_08_hidden_candidate_difference_causes_internal_conflict_only(self):
        item = case((source("left"),), (source("right", hidden=(0.1,) * 24),))
        for result in pair(item):
            self.assertEqual((0,), result.b4_matches)
            self.assertEqual((0,), result.fast_matches)
            self.assertEqual("A_RECENT_INTERNAL_CONFLICT", result.decision.status)
            self.assertEqual(48, result.equality_terms)
            self.assert_baseline(item, result)

    def test_09_valid_absence_and_nonapplicability_are_distinct(self):
        for item, expected in ((case(), "A_RECENT_ABSENT_VALID"),
                               (case((source("far", (1.0,) * 24),)), "A_RECENT_NOT_APPLICABLE")):
            for result in pair(item):
                self.assertEqual(expected, result.decision.status)
                self.assert_baseline(item, result)

    def test_10_applicability_ignores_hidden_values(self):
        a = case((source("candidate", (0.1,) * 24),))
        b = case((source("candidate", (0.1,) * 24, (0.9,) * 24),),
                 cue=source("neutral-cue", hidden=(0.8,) * 24, start=48000))
        for rule in c.RULES:
            left, right = c.compare_case(a, rule), c.compare_case(b, rule)
            self.assertEqual(left.b4_matches, right.b4_matches)
            self.assertEqual(left.rows[0].terms, right.rows[0].terms)
            self.assertEqual(left.rows[0].statistic, right.rows[0].statistic)
            self.assertEqual(left.decision.status, right.decision.status)

    def test_11_source_time_root_and_digest_mutations_fail_closed(self):
        good = source("candidate")
        item = case((good,))
        bad_sources = (replace(good, values=(0.2,) * 48),
                       c.sealed(replace(good, values_digest=c.digest("wrong"))),
                       c.sealed(replace(good, root_digest=c.digest("foreign"))),
                       c.sealed(replace(good, start_tick=60000, end_tick=64800)),
                       c.sealed(replace(good, values=list(good.values))))
        for bad in bad_sources:
            corrupted = c.sealed(replace(item, b4=(bad,) + (None,) * 8))
            with self.assertRaises(c.ComparisonError):
                c.compare_case(corrupted, c.RULES[0])
        with self.assertRaises(c.ComparisonError):
            c.compare_case(replace(item, panel_id="changed"), c.RULES[0])
        with self.assertRaises(c.ComparisonError):
            c.compare_case(item, "UNBOUND_RULE")

    def test_12_immutable_read_only_and_valid_functional_failure(self):
        item = case()
        before = deepcopy(asdict(item))
        results = pair(item)
        self.assertEqual(before, asdict(item))
        for result in results:
            self.assertEqual(item.digest, result.prestate_digest)
            self.assertEqual(item.digest, result.poststate_digest)
            self.assert_baseline(item, result)
            with self.assertRaises(FrozenInstanceError):
                result.rule = "changed"
        with self.assertRaises(FrozenInstanceError):
            item.cue.start_tick = 0
        measured = assess(results, ("expected-source",))
        self.assertEqual("FALSIFIED", measured["mean_prediction_status"])
        self.assertEqual("FALSIFIED", measured["all_prediction_status"])

    def test_13_trace_manipulations_are_rejected(self):
        item = case((source("candidate"),))
        result = c.compare_case(item, c.RULES[0])
        mutations = (replace(result, input_digest=c.digest("foreign")),
                     c.sealed(replace(result, rows=())),
                     c.sealed(replace(result, poststate_digest=c.digest("changed"))),
                     c.sealed(replace(result, b4_matches=())),
                     c.sealed(replace(result, decision=c.Decision("A_RECENT_NOT_APPLICABLE", (), None))),
                     c.sealed(replace(result, rows=(replace(result.rows[0], statistic=0.5),))))
        for mutated in mutations:
            with self.assertRaises(c.ComparisonError):
                c.verify_case(item, mutated, result.digest)

    def test_14_fixed_panels_budgets_and_exact_output_limit(self):
        # Plan metadata only. No sealed materialization/result values are opened.
        plan = json.loads((ROOT / "reports/s2nc/s2nc-source-panel-preseal-20260906-01/execution-plan.json").read_text())
        synthetic = tuple(c.sealed(replace(source(f"s{n:03d}", (0.12345678901234568,) * 24,
                                                   start=(n - 1) * 4800),
                                           clock_id="s2nc-source-sample-clock")) for n in range(1, 24))
        cases = c.bind_fixed_cases(plan, synthetic)
        self.assertEqual(48, len(cases))
        self.assertIsNone(cases[8].b4[0])
        self.assertIsNone(cases[8].fast[0])
        results = tuple(c.compare_case(item, rule) for rule in c.RULES for item in cases)
        decisions = tuple(baseline.decide(item, result.b4_matches, result.fast_matches)[0]
                          for item, result in zip(cases + cases, results, strict=True))
        self.assertEqual(1056, sum(len(r.rows) for r in results))
        self.assertEqual(25344, sum(r.band_differences for r in results))
        data = c.encode_complete_comparison(results, decisions, {})
        self.assertLess(len(data), c.MAX_OUTPUT_BYTES)
        print("NEUTRAL_COMPLETE_OUTPUT_BYTES=" + str(len(data)))
        overhead = len(c.encode_complete_comparison(results, decisions, {"padding": ""}))
        exact = {"padding": "x" * (c.MAX_OUTPUT_BYTES - overhead)}
        self.assertEqual(c.MAX_OUTPUT_BYTES, len(c.encode_complete_comparison(results, decisions, exact)))
        with self.assertRaises(c.ComparisonError):
            c.encode_complete_comparison(results, decisions, {"padding": exact["padding"] + "x"})
        with self.assertRaises(c.ComparisonError):
            c.bind_fixed_cases({**plan, "panels": []}, synthetic)

    def test_15_materialization_root_and_values_are_bound(self):
        profile = {"config": dict(sample_rate=48000, window_size=4800, hop_size=480,
                                  min_frequency=50.0, max_frequency=18000.0, band_count=48)}
        profile["profile_digest"] = c.digest(profile)
        states = []
        for n in range(1, 24):
            values = [0.125] * 48
            state = {"source_id": f"s{n:03d}", "ordinal": n, "execution_digest": c.EXECUTION_DIGEST,
                     "profile_digest": profile["profile_digest"], "clock_id": "s2nc-source-sample-clock",
                     "window_start_sample": (n - 1) * 4800, "window_end_sample": n * 4800,
                     "values": values, "values_digest": c.digest(values),
                     "values_f64le_sha256": hashlib.sha256(struct.pack("<48d", *values)).hexdigest()}
            state["materialized_state_digest"] = c.digest(state)
            states.append(state)
        record = {"technical_status": "RECEPTOR_MATERIALIZATION_COMPLETE", "failure": None,
                  "sources_unchanged": True, "execution_digest": c.EXECUTION_DIGEST,
                  "receptor_profile": profile, "states": states}
        expected = c.digest(record)
        record["record_digest"] = expected
        bound = c.bind_materialized_sources(record, expected)
        self.assertEqual(23, len(bound))
        record["states"][0]["values"][0] = 0.5
        self.assertEqual(0.125, bound[0].values[0])
        with self.assertRaises(c.ComparisonError):
            c.bind_materialized_sources(record, expected)

    def test_16_improvement_and_loss_are_evaluated_together(self):
        better_case = case((source("correct"), source("competitor", (0.4,) + (0.0,) * 23)), name="better")
        worse_case = case((source("related", (0.4,) + (0.0,) * 23),), name="worse")
        better, worse = pair(better_case), pair(worse_case)
        expectations = (evaluation.Expectation("better", "KNOWN_EXACT", ("correct",)),
                        evaluation.Expectation("worse", "KNOWN_EXACT", ("related",)))
        result = evaluation.evaluate((better[0], worse[0]), (better[1], worse[1]), expectations)
        self.assertEqual("TRADEOFF", result["status"])
        self.assertEqual(1, result["improved_cases"])
        self.assertEqual(1, result["lost_known_hits"])
        self.assertEqual(2, result["categories"]["KNOWN_EXACT"]["denominator"])
        self.assertEqual("IMPROVEMENT_CONFIRMED", assess(better, ("correct",))["status"])


if __name__ == "__main__":
    unittest.main()
