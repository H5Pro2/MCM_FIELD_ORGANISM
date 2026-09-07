"""Neutral synthetic reduced values only; never open NP receptor materialization."""

import ast
from dataclasses import FrozenInstanceError, asdict, replace
import json
import math
from pathlib import Path
import unittest

from tools import _s2np_private_coverage_comparison as c
from tools import _s2np_private_coverage_baseline as baseline
from tools import _s2np_private_coverage_evaluation as evaluation


def view(n, values, name="CONTIGUOUS_24"):
    return c.project_values(source_id=f"np-a{n:02d}", source_digest=c.digest(["synthetic-source", n]),
        payload_digest=c.digest(["synthetic-payload", tuple(values)]),
        projection_digest=c.digest(["synthetic-projection", n, values]), profile_digest=c.PROFILE,
        start_tick=(n - 1) * 4800, end_tick=n * 4800, snapshot_index=(n - 1) * 10,
        values=tuple(values), view_id=name)


def reseal(record):
    payload = asdict(record)
    payload.pop("record_digest")
    return replace(record, record_digest=c.digest(payload))


class CoverageTests(unittest.TestCase):
    differences = 0

    @classmethod
    def setUpClass(cls):
        cls.synthetic = (
            (0.0,) * 48, (0.6,) * 48, (0.0,) * 48, (0.04,) * 48,
            (0.0,) * 47 + (0.4,), (0.2,) * 24 + (0.0,) * 24,
            (0.6,) * 48, (0.56,) * 48, (0.6,) * 47 + (0.9,),
            (0.7,) * 24 + (0.5,) * 24, (0.3,) * 48, (1.0,) * 48)
        cls.catalog = tuple(view(n, values, name) for name, _ in c.VIEWS
                            for n, values in enumerate(cls.synthetic, 1))
        cls.before = c.digest([asdict(v) for v in cls.catalog])
        cls.primary = c.compare_fixed(cls.catalog, "PRIMARY")
        cls.direct = c.compare_fixed(cls.catalog, "DIRECT")
        cls.differences = 7680
        cls.verification = c.verify_fixed(cls.catalog, cls.primary, cls.direct)
        cls.execution_digest = c.digest("synthetic-execution-root")
        cls.plan = c.binding.evaluation_plan({"execution_digest": cls.execution_digest})
        cls.payloads = tuple((f"np-a{n:02d}", c.digest(["synthetic-payload", values]))
                             for n, values in enumerate(cls.synthetic, 1))
        cls.evaluated = evaluation.evaluate(cls.catalog, cls.primary, cls.verification,
                                           cls.plan, cls.execution_digest, cls.payloads)
        cls.maximum_serialized = 0

    @classmethod
    def tearDownClass(cls):
        print("NEUTRAL_METRICS " + json.dumps(dict(band_differences=cls.differences,
            maximum_serialized_bytes=cls.maximum_serialized, synthetic_only=True,
            np_materialization_reads=0, receptor_calls=0, nj_calls=0)))

    def pair(self, cue, refs):
        type(self).differences += 2 * len(cue.indices) * len(refs)
        self.assertLessEqual(type(self).differences, 16384)
        full = cue.view_id == "FULL_48_DIAGNOSTIC"
        p = (c.compare_diagnostic if full else c.compare_partial)("panel", cue, refs)
        d = (baseline.direct_diagnostic if full else baseline.direct_partial)("panel", cue, refs)
        c.verify_panel("panel", cue, refs, p, d)
        return p, d

    def test_01_mask_binding(self):
        q = view(3, (0.0,) * 48)
        for indices in (tuple(reversed(q.indices)), tuple(range(1, 25)), list(q.indices)):
            with self.subTest(indices=indices), self.assertRaisesRegex(c.S2NPCoverageError, "MASK_INVALID"):
                replace(q, indices=indices)

    def test_02_hidden_values_isolated(self):
        r = view(1, (0.0,) * 48)
        for name, indices in c.VIEWS[:2]:
            base = (0.02,) * 48
            changed = tuple(x if i in indices else 0.99 for i, x in enumerate(base))
            q1, q2 = view(3, base, name), view(3, changed, name)
            ref = view(1, (0.0,) * 48, name)
            a, _ = self.pair(q1, (ref,))
            b, _ = self.pair(q2, (ref,))
            self.assertEqual(q1.values, q2.values)
            self.assertEqual(a.findings, b.findings)
            self.assertEqual(a.relations, b.relations)
            self.assertNotEqual(a.input_digest, b.input_digest)
            self.assertEqual(len(q1.values), 24)
            self.assertFalse(hasattr(q1, "full_values"))
        self.assertEqual(len(r.values), 24)

    def test_03_diagnostic_isolation(self):
        q = view(3, (0.0,) * 48, "FULL_48_DIAGNOSTIC")
        for function in (c.compare_partial, baseline.direct_partial):
            with self.subTest(function=function.__name__), self.assertRaisesRegex(c.S2NPCoverageError, "DIAGNOSTIC_ISOLATION"):
                function("panel", q, ())
        with self.assertRaisesRegex(c.S2NPCoverageError, "DIAGNOSTIC_ISOLATION"):
            c.compare_diagnostic("panel", view(3, (0.0,) * 48), ())
        p, _ = self.pair(q, (view(1, (0.0,) * 48, "FULL_48_DIAGNOSTIC"),))
        self.assertEqual(p.difference_count, 48)

    def test_04_complete_panel_and_no_dedup(self):
        p, _ = self.pair(view(3, (0.0,) * 48), (view(1, (0.0,) * 48), view(2, (0.0,) * 48)))
        self.assertEqual(len(p.relations), 2)
        self.assertEqual(p.difference_count, 48)
        self.assertTrue(all(f.hits == ("np-a01", "np-a02") for f in p.findings))

    def test_05_empty_panel(self):
        p, _ = self.pair(view(3, (0.0,) * 48), ())
        self.assertEqual((p.relations, p.difference_count), ((), 0))
        self.assertTrue(all(f.status == "NO_APPLICABILITY" for f in p.findings))

    def test_06_arithmetic_inclusive_neighbors(self):
        for limit in (0.1, 0.01):
            for x in (math.nextafter(limit, 0.0), limit, math.nextafter(limit, 1.0)):
                with self.subTest(limit=limit, x=x.hex()):
                    p, _ = self.pair(view(3, (x,) * 48), (view(1, (0.0,) * 48),))
                    row = p.relations[0]
                    self.assertEqual(row.mean.hex(), (sum((x,) * 24) / 24).hex())
                    self.assertEqual(row.applicable, (row.mean <= 0.1, x <= 0.1, row.mean <= 0.01))

    def test_07_sum_order_and_full_divisor(self):
        source = (0.1,) + (2.0 ** -54,) * 47
        for name, indices in c.VIEWS:
            p, _ = self.pair(view(3, source, name), (view(1, (0.0,) * 48, name),))
            expected = tuple(source[i] for i in indices)
            self.assertEqual(p.relations[0].mean.hex(), (sum(expected) / len(indices)).hex())
            self.assertEqual(tuple(d.original_index for d in p.relations[0].differences), indices)

    def test_08_all_band_subset_and_slow_mean(self):
        for values in ((0.05,) * 48, (0.12,) + (0.0,) * 47, (0.2,) * 48):
            p, _ = self.pair(view(3, values), (view(1, (0.0,) * 48),))
            flags = p.relations[0].applicable
            self.assertFalse(flags[1] and not flags[0])
            if values[0] == 0.12:
                self.assertEqual(flags, (True, False, True))

    def test_09_source_profile_time_forms(self):
        q = view(3, (0.0,) * 48)
        mutations = ({"source_id": "BAD"}, {"source_digest": "bad"}, {"profile_digest": "0" * 64},
                     {"clock_id": "field"}, {"end_tick": q.end_tick + 1}, {"snapshot_index": 0},
                     {"values": [0.0] * 24}, {"values": (float("nan"),) * 24})
        for change in mutations:
            with self.subTest(change=change), self.assertRaises(c.S2NPCoverageError):
                replace(q, **change)
        with self.assertRaisesRegex(c.S2NPCoverageError, "SOURCE_TIME_MISMATCH"):
            c.compare_partial("panel", view(1, (0.0,) * 48), (q,))

    def test_10_frozen_inputs_and_results(self):
        with self.assertRaises(FrozenInstanceError):
            self.catalog[0].values = (1.0,) * 24
        with self.assertRaises(FrozenInstanceError):
            self.primary[0].relations[0].mean = 0.9
        self.assertEqual(self.before, c.digest([asdict(v) for v in self.catalog]))

    def test_11_fixed_counts(self):
        for records in (self.primary, self.direct):
            self.assertEqual(sum(len(r.findings) for r in records), 360)
            self.assertEqual(sum(len(r.relations) * 3 for r in records), 360)
            self.assertEqual(sum(r.difference_count for r in records), 3840)
        self.assertEqual(self.verification["verification_band_differences"], 0)

    def test_12_catalog_missing_order_and_cross_view(self):
        for catalog in (self.catalog[:-1], tuple(reversed(self.catalog))):
            with self.subTest(size=len(catalog)), self.assertRaises(c.S2NPCoverageError):
                c.fixed_inputs(catalog)
        corrupt = list(self.catalog)
        corrupt[12] = replace(corrupt[12], values=(0.7,) * 24)
        with self.assertRaisesRegex(c.S2NPCoverageError, "CROSS_VIEW_VALUES_INVALID"):
            c.fixed_inputs(tuple(corrupt))

    def test_13_incomplete_and_swapped_evidence(self):
        for result in (self.primary[:-1], (self.primary[1], self.primary[0]) + self.primary[2:]):
            with self.subTest(size=len(result)), self.assertRaises(c.S2NPCoverageError):
                c.verify_fixed(self.catalog, result, self.direct)

    def test_14_term_and_source_manipulation(self):
        args = c.fixed_inputs(self.catalog)[0]
        original = self.primary[0]
        rel = original.relations[0]
        for changed in (
            replace(original, cue_digest="0" * 64),
            replace(original, relations=()),
            replace(original, relations=(replace(rel, differences=(c.BandDifference(47, 0.0),) + rel.differences[1:]),) + original.relations[1:]),
            replace(original, relations=(replace(rel, mean=0.8),) + original.relations[1:])):
            with self.subTest(changed=changed.cue_digest), self.assertRaises(c.S2NPCoverageError):
                c.verify_panel(*args, reseal(changed), self.direct[0])

    def test_15_forged_consistent_terms_baseline_detects(self):
        args = c.fixed_inputs(self.catalog)[0]
        p = self.primary[0]
        rel = replace(p.relations[0], differences=tuple(c.BandDifference(i, 0.001) for i in range(24)),
                      mean=sum((0.001,) * 24) / 24, maximum=0.001)
        forged = reseal(replace(p, relations=(rel,) + p.relations[1:]))
        with self.assertRaisesRegex(c.S2NPCoverageError, "DIRECT_BASELINE_DIFFERS"):
            c.verify_panel(*args, forged, self.direct[0])

    def test_16_baseline_independence_static(self):
        tree = ast.parse(Path(baseline.__file__).read_text(encoding="utf-8"))
        calls = {getattr(n.func, "attr", getattr(n.func, "id", "")) for n in ast.walk(tree) if isinstance(n, ast.Call)}
        self.assertFalse(calls & {"compare_partial", "compare_diagnostic", "_compare", "verify_panel", "input_binding"})

    def test_17_relation_loss_not_unique_loss(self):
        row = dict(case_id="neutral", target_present=True, subtype="LEVEL", before_variation="NON_BITIDENTICAL",
            after_variation="NON_BITIDENTICAL", before=evaluation._outcome(("target", "other"), "target"),
            after=evaluation._outcome(("other",), "target"), nontarget_count=1,
            new_false_applicability=[], relationship_gain=False, unique_gain=False,
            relationship_loss=True, unique_loss=False)
        result = evaluation.summarize([row])
        self.assertEqual([result["relationship"][x] for x in "NDRL"], [1, 1, 0, 1])
        self.assertEqual(result["correct_unique"]["D"], 0)
        self.assertEqual(result["sides"]["after"]["false_unique"], 1)
        self.assertEqual(result["status"], "LOSSLESS_COVERAGE_CLAIM_FALSIFIED")

    def test_18_retention_gain_loss_separate(self):
        rows = []
        for n, (left, right) in enumerate(((True, True), (True, False), (False, True))):
            rows.append(dict(case_id=str(n), target_present=True,
                before={"correct_unique": left}, after={"correct_unique": right}))
        result = evaluation.retention(rows, "correct_unique")
        self.assertEqual([result[x] for x in "NDRL"], [3, 2, 1, 1])
        self.assertEqual(result["D"], result["R"] + result["L"])

    def test_19_empty_denominator_and_valid_abstention(self):
        self.assertEqual(evaluation.retention([], "correct_unique")["status"], "ERHALTUNG_NICHT_GEPRUEFT")
        empty = [r for r in self.evaluated["rows"] if r["panel_id"] == "p04"]
        self.assertTrue(empty and all(r["before"]["empty"] and r["after"]["empty"] for r in empty))
        self.assertEqual(self.verification["status"], "TECHNICALLY_VALID")

    def test_20_evaluation_binding_variation_and_diagnostic(self):
        with self.assertRaisesRegex(c.S2NPCoverageError, "VERIFICATION_REQUIRED"):
            evaluation.evaluate(self.catalog, self.primary, {**self.verification, "status": "BAD"},
                self.plan, self.execution_digest, self.payloads)
        bad = {**self.plan, "relations": []}
        with self.assertRaisesRegex(c.S2NPCoverageError, "EVALUATION_PLAN_INVALID"):
            evaluation.evaluate(self.catalog, self.primary, self.verification, bad, self.execution_digest, self.payloads)
        row = next(r for r in self.evaluated["rows"] if r["cue_id"] == "np-a05" and r["panel_id"] == "p01"
                   and r["comparison_view"] == "DISTRIBUTED_24")
        self.assertEqual((row["before_variation"], row["after_variation"]), ("BITIDENTICAL", "NON_BITIDENTICAL"))
        self.assertTrue(all(r["diagnostic_only"] == (r["comparison_view"] == "FULL_48_DIAGNOSTIC") for r in self.evaluated["rows"]))

    def test_21_output_budget_and_resource_rejection(self):
        bundle = dict(neutral_materialization_reserve="x" * 131072, metadata_reserve="x" * 65536,
            projected_inputs=[asdict(v) for v in self.catalog], primary=[asdict(r) for r in self.primary],
            direct=[asdict(r) for r in self.direct], verification=self.verification, evaluation=self.evaluated)
        data = c.bounded_payload(bundle)
        type(self).maximum_serialized = len(data)
        self.assertLessEqual(len(data), 2097152)
        with self.assertRaisesRegex(c.S2NPCoverageError, "OUTPUT_SIZE_EXCEEDED"):
            c.bounded_payload({"oversized": "x" * 2097152})
        q = view(4, (0.0,) * 48)
        with self.assertRaisesRegex(c.S2NPCoverageError, "INPUT_FORM_INVALID"):
            c.compare_partial("panel", q, tuple(view(n, (0.0,) * 48) for n in (1, 2, 3)))

    def test_22_domains_subnormal_and_numeric_terms(self):
        tiny = float.fromhex("0x0.0000000000001p-1022")
        p, _ = self.pair(view(3, (tiny,) * 48), (view(1, (0.0,) * 48),))
        self.assertEqual(p.relations[0].differences[0].value.hex(), tiny.hex())
        for x in (float("inf"), -0.01, 1.01):
            with self.subTest(x=x), self.assertRaisesRegex(c.S2NPCoverageError, "VALUE_DOMAIN_INVALID"):
                view(3, (x,) * 48)
        serialized = json.loads(c.canonical(asdict(p)))
        self.assertEqual(serialized["relations"][0]["differences"][0]["original_index"], 0)
        self.assertIsInstance(serialized["relations"][0]["differences"][0]["value"], float)


if __name__ == "__main__":
    unittest.main()
