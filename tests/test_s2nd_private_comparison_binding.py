"""Synthetic ND bindings only; never load materialized corpus values."""

import copy
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import struct
import unittest

from tools import _s2nc_private_rule_comparison as c
from tools import _s2nc_private_decision_baseline as baseline
from tools import _s2nd_private_comparison_binding as binding
from tools import _s2nd_private_retention_evaluation as evaluation


METADATA = Path(__file__).resolve().parents[1] / "reports/s2nd/s2nd-source-panel-preseal-20260906-02"
METADATA_HASHES = {
    "execution-plan.json": "0db1fc0f64a5af76616e7652fcf9b8da3bfb6fef8c9e60fa0870a4e49425df4e",
    "evaluation-plan.json": "253143cfdb59cd088628f279aa186b6ab509f20548a196df5753445b38e87a5f",
    "seal.json": "ba49bcf2eb0a294139b4655d6d532b5a7aa4950f0f63d6b144f03b43d92dc34d",
}


def seal(value, key):
    value[key] = c.digest({k: v for k, v in value.items() if k != key})
    return value


def metadata(name):
    raw = (METADATA / name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != METADATA_HASHES[name]:
        raise AssertionError("NEUTRAL_METADATA_BINDING_INVALID")
    return json.loads(raw)


def fixture(overrides=None):
    execution, sealed = metadata("execution-plan.json"), metadata("seal.json")
    channels = [f"neutral-band-{i:02d}" for i in range(48)]
    profile = seal({"config": dict(binding.PROFILE), "config_digest": c.digest(binding.PROFILE),
                    "channel_ids": channels, "bands": [{"channel_id": s} for s in channels],
                    "method": "LogSpectralReceptor.analyze",
                    "receptor_source_sha256": sealed["source_hashes_before"]["mcm_field_organism/log_spectral_receptor.py"]},
                   "profile_digest")
    states = []
    for spec in execution["sources"]:
        n = spec["ordinal"]
        default = 1.0 if 4 <= n <= 6 else 0.1 if n <= 3 or n in (7, 11, 15) else 0.11
        values = list((overrides or {}).get(spec["source_id"], (default,) * 48))
        state = {k: spec[k] for k in ("source_id", "ordinal", "recipe_digest", "pcm_sha256", "clock_id",
                                      "window_start_sample", "window_end_sample", "sample_count")}
        state.update(payload_validated_before_analysis=True,
                     time_semantics="DECLARED_PCM_SOURCE_WINDOW_NOT_RECEPTOR_TIMESTAMP",
                     execution_digest=execution["execution_digest"], profile_digest=profile["profile_digest"],
                     values=values, values_digest=c.digest(values),
                     values_f64le_sha256=hashlib.sha256(struct.pack("<48d", *values)).hexdigest())
        states.append(seal(state, "materialized_state_digest"))
    record = {"schema": "s2nd.receptor-materialization.v1", "run_id": "neutral-materialization",
              "technical_status": "RECEPTOR_MATERIALIZATION_COMPLETE", "failure": None,
              "sources_unchanged": True, "input_hashes": dict(sealed["source_hashes_before"]),
              "source_hashes_after": dict(sealed["source_hashes_before"]),
              "execution_digest": execution["execution_digest"], "seal_digest": sealed["seal_digest"],
              "receptor_profile": profile, "states": states,
              "counts": dict(analyze_attempt_count=18, analyze_return_count=18, completed_analyses=18,
                             receptor_values=864, distance_calculations=0, rule_calls=0, memory_calls=0,
                             context_calls=0, field_calls=0, runtime_calls=0, pcm_payloads_persisted=0)}
    return execution, sealed, record


def bind_fixture(parts, receipt_mutation=None):
    execution, sealed, record = parts
    seal(record, "record_digest")
    receipt = seal({"verification_status": "MATERIALIZATION_EVIDENCE_VALID", "run_id": record["run_id"],
                    "record_digest": record["record_digest"], "result_file_sha256": c.digest(record),
                    "read_only": True, "result_unchanged": True, "source_hashes_unchanged": True,
                    "state_count": 18, "value_count": 864}, "verification_digest")
    if receipt_mutation is not None:
        receipt.update(receipt_mutation)
        seal(receipt, "verification_digest")
    roots = replace(binding.BOUND_ROOTS, materialization=record["record_digest"],
                    profile=record["receptor_profile"]["profile_digest"], verification=receipt["verification_digest"])
    return binding.bind_inputs(execution, sealed, record, receipt, roots)


def neutral_batch(bound):
    results, decisions = [], []
    for rule in c.RULES:
        for case in bound.cases:
            result = c.compare_case(case, rule)
            direct, _ = baseline.decide(case, result.b4_matches, result.fast_matches)
            results.append(result)
            decisions.append(direct)
    return tuple(results), tuple(decisions)


def evaluated(overrides=None):
    bound = bind_fixture(fixture(overrides))
    results, decisions = neutral_batch(bound)
    report = evaluation.evaluate(bound, results[:48], results[48:], metadata("evaluation-plan.json"))
    return bound, results, decisions, report


def group(report, subtype="ALL_VARIANTS", competition="ALL", variation="ALL"):
    return next(g for g in report["retention_groups"] if
                (g["variant_subtype"], g["competition"], g["receptor_variation"]) == (subtype, competition, variation))


class NDComparisonBindingTests(unittest.TestCase):
    def test_01_metadata_and_synthetic_source_binding(self):
        parts = fixture()
        before = c.canonical(parts)
        bound = bind_fixture(copy.deepcopy(parts))
        self.assertEqual(c.canonical(parts), before)
        self.assertEqual(len(bound.sources), 18)
        self.assertEqual(sum(len(s.values) for s in bound.sources), 864)
        self.assertNotEqual(bound.roots.materialization, binding.BOUND_ROOTS.materialization)
        self.assertEqual(bound.roots.execution, binding.BOUND_ROOTS.execution)
        for case in bound.cases:
            self.assertEqual(case.cue.values, bound.sources[int(case.cue.source_id[1:]) - 1].values[:24])

    def test_02_sources_types_times_and_digests_fail_closed(self):
        mutations = (
            ("source_id", "foreign-source"), ("clock_id", "foreign-clock"),
            ("window_start_sample", 1), ("window_end_sample", 4799),
            ("profile_digest", "0" * 64), ("recipe_digest", "0" * 64),
            ("pcm_sha256", "0" * 64), ("values", [0.1] * 47),
            ("values", [0] + [0.1] * 47), ("values", [1.1] + [0.1] * 47),
            ("values_digest", "0" * 64), ("values_f64le_sha256", "0" * 64),
            ("payload_validated_before_analysis", False),
        )
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                parts = fixture()
                parts[2]["states"][0][key] = value
                seal(parts[2]["states"][0], "materialized_state_digest")
                with self.assertRaises(c.ComparisonError):
                    bind_fixture(parts)
        parts = fixture()
        parts[2]["states"][0], parts[2]["states"][1] = parts[2]["states"][1], parts[2]["states"][0]
        with self.assertRaises(c.ComparisonError):
            bind_fixture(parts)
        parts = fixture()
        parts[2]["states"][0]["values"][0] = 0.2
        with self.assertRaises(c.ComparisonError):
            bind_fixture(parts)

    def test_03_roots_profiles_and_plan_bindings(self):
        for position, key, value in ((0, "execution_digest", "0" * 64),
                                     (1, "seal_digest", "0" * 64),
                                     (2, "sources_unchanged", False),
                                     (2, "execution_digest", "0" * 64)):
            parts = fixture()
            parts[position][key] = value
            with self.subTest(key=key), self.assertRaises(c.ComparisonError):
                bind_fixture(parts)
        parts = fixture()
        parts[2]["receptor_profile"]["config"]["band_count"] = 47
        seal(parts[2]["receptor_profile"], "profile_digest")
        with self.assertRaises(c.ComparisonError):
            bind_fixture(parts)
        parts = fixture()
        parts[2]["counts"]["completed_analyses"] = 17
        with self.assertRaises(c.ComparisonError):
            bind_fixture(parts)
        with self.assertRaises(c.ComparisonError):
            binding.bind_inputs({}, {}, {}, {})

    def test_04_full_scans_empty_panels_and_bound_budgets(self):
        bound, results, decisions, _ = evaluated()
        self.assertEqual(binding.verify_comparison(bound, results, decisions), "TECHNICALLY_VALID")
        self.assertEqual(len(results), 96)
        self.assertEqual(sum(len(r.rows) for r in results), 144)
        self.assertEqual(sum(r.band_differences for r in results), 3456)
        self.assertEqual(sum(len(r.visited_positions) for r in results), 1152)
        self.assertLessEqual(3 * sum(r.equality_terms for r in results), 9216)
        self.assertEqual(results[4].rows, ())
        self.assertEqual(results[4].decision.status, "A_RECENT_ABSENT_VALID")
        self.assertTrue(all(r.visited_positions == c.POSITIONS for r in results))
        self.assertEqual(len(results[8].rows), 3)

    def test_05_immutable_bindings_and_read_only_results(self):
        parts = fixture()
        bound = bind_fixture(parts)
        before = c.canonical(c.payload(bound))
        results, decisions = neutral_batch(bound)
        binding.verify_comparison(bound, results, decisions)
        self.assertEqual(before, c.canonical(c.payload(bound)))
        parts[2]["states"][0]["values"][0] = 0.9
        self.assertEqual(bound.sources[0].values[0], 0.1)
        with self.assertRaises(FrozenInstanceError):
            bound.sources[0].start_tick = 1
        self.assertTrue(all(r.prestate_digest == r.poststate_digest for r in results))

    def test_06_verifier_rejects_incomplete_or_mutated_evidence(self):
        bound = bind_fixture(fixture())
        results, decisions = neutral_batch(bound)
        for result in (replace(results[0], poststate_digest="0" * 64),
                       replace(results[0], visited_positions=c.POSITIONS[:-1]),
                       replace(results[0], rows=results[0].rows[:-1]),
                       replace(results[0], b4_matches=())):
            altered = (c.sealed(result),) + results[1:]
            with self.subTest(result=result), self.assertRaises(c.ComparisonError):
                binding.verify_comparison(bound, altered, decisions)
        with self.assertRaises(c.ComparisonError):
            binding.verify_comparison(bound, results[:-1], decisions[:-1])

    def test_07_output_limit_inclusive(self):
        bound = bind_fixture(fixture())
        results, decisions = neutral_batch(bound)
        empty = binding.encode_comparison(bound, results, decisions, {"padding": ""})
        padding = "x" * (c.MAX_OUTPUT_BYTES - len(empty))
        self.assertEqual(len(binding.encode_comparison(bound, results, decisions, {"padding": padding})), c.MAX_OUTPUT_BYTES)
        with self.assertRaisesRegex(c.ComparisonError, "OUTPUT_TOO_LARGE"):
            binding.encode_comparison(bound, results, decisions, {"padding": padding + "x"})

    def test_08_retention_stratification(self):
        _, _, _, report = evaluated()
        self.assertEqual(tuple(group(report)[k] for k in ("N", "D", "R", "L")), (18, 18, 18, 0))
        self.assertEqual(group(report, "EXACT")["D"], 6)
        self.assertEqual(group(report, variation="NON_BITIDENTICAL")["D"], 18)
        self.assertEqual(group(report, competition="COMPETITOR_PRESENT")["N"], 9)
        for entry in report["retention_groups"]:
            self.assertEqual(entry["D"], entry["R"] + entry["L"])

    def test_09_valid_abstention_can_be_functional_loss(self):
        bound, results, decisions, report = evaluated({"s008": (0.5,) + (0.1,) * 47})
        self.assertEqual(binding.verify_comparison(bound, results, decisions), "TECHNICALLY_VALID")
        self.assertEqual(results[49].decision.status, "A_RECENT_NOT_APPLICABLE")
        retained = group(report, "UNIFORM_GAIN")
        self.assertEqual((retained["D"], retained["R"], retained["L"]), (6, 4, 2))
        self.assertEqual(retained["lost_to_abstention"], 2)
        self.assertEqual(retained["status"], "RETENTION_FALSIFIED")

    def test_10_zero_denominator_not_rescued_by_exact_controls(self):
        variants = {f"s{n:03d}": (0.8,) * 48 for n in range(7, 19) if n not in (7, 11, 15)}
        _, _, _, report = evaluated(variants)
        self.assertEqual(group(report, "EXACT")["D"], 6)
        self.assertEqual((group(report)["N"], group(report)["D"]), (18, 0))
        self.assertEqual(group(report)["status"], "ERHALTUNG_NICHT_GEPRUEFT")

    def test_11_gains_cannot_cancel_losses(self):
        _, _, _, report = evaluated({"s004": (0.6,) + (0.1,) * 47,
                                      "s012": (0.5,) + (0.1,) * 47})
        self.assertGreater(report["comparison"]["improved_cases"], 0)
        self.assertEqual(group(report)["L"], 2)
        self.assertEqual(group(report)["status"], "RETENTION_FALSIFIED")

    def test_12_hidden_values_do_not_change_applicability(self):
        b1, r1, _, _ = evaluated({"s008": (0.1,) * 48})
        b2, r2, _, report = evaluated({"s008": (0.1,) * 24 + (0.12,) * 24})
        self.assertNotEqual(b1.sources[7].values_digest, b2.sources[7].values_digest)
        self.assertEqual(tuple((r.b4_matches, r.fast_matches, r.decision) for r in r1),
                         tuple((r.b4_matches, r.fast_matches, r.decision) for r in r2))
        row = next(r for r in report["cases"] if r["case_id"] == "c002")
        self.assertEqual(row["receptor_variation"], "NON_BITIDENTICAL")

    def test_13_evaluation_binding_and_removed_target_controls(self):
        bound, results, decisions, report = evaluated()
        controls = [r for r in report["cases"] if not r["reference_present"]]
        self.assertEqual(len(controls), 24)
        self.assertTrue(all(r["mean"]["abstention"] and r["all_bands"]["abstention"] for r in controls))
        plan = metadata("evaluation-plan.json")
        plan["cases"][0]["accepted_source_ids"] = ["s004"]
        with self.assertRaises(c.ComparisonError):
            evaluation.evaluate(bound, results[:48], results[48:], plan)
        self.assertLess(len(binding.encode_comparison(bound, results, decisions, report)), c.MAX_OUTPUT_BYTES)

    def test_14_false_unique_remaining_candidate_is_not_gain(self):
        bound, results, decisions, report = evaluated({"s001": (0.5,) + (0.1,) * 47,
                                                      "s004": (0.1,) * 48, "s008": (0.1,) * 48})
        self.assertEqual(binding.verify_comparison(bound, results, decisions), "TECHNICALLY_VALID")
        row = next(r for r in report["cases"] if r["case_id"] == "c010")
        self.assertEqual(row["mean"]["status"], "A_RECENT_INTERNAL_AMBIGUITY")
        self.assertEqual(row["all_bands"]["source_ids"], ["s004"])
        self.assertTrue(row["new_false_admission"])
        self.assertFalse(row["improvement"])

    def test_15_materialization_verification_receipt_binding(self):
        for key, value in (("read_only", False), ("result_unchanged", False),
                           ("source_hashes_unchanged", False), ("state_count", 17),
                           ("value_count", 863), ("run_id", "foreign-run"),
                           ("record_digest", "0" * 64), ("result_file_sha256", "0" * 64),
                           ("verification_status", "NOT_EVALUABLE")):
            with self.subTest(key=key), self.assertRaises(c.ComparisonError):
                bind_fixture(fixture(), {key: value})


if __name__ == "__main__":
    unittest.main()
