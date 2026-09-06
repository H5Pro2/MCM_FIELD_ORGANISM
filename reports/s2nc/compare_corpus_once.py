"""Archived S2-NC one-shot call; no receptor or system-runtime imports."""

from collections import Counter
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from tools import _s2nc_private_rule_comparison as c
from tools import _s2nc_private_decision_baseline as baseline


ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "s2nc-two-rule-corpus-comparison-20260906-01"
OUT = ROOT / "reports/s2nc" / RUN_ID
PRESEAL = "reports/s2nc/s2nc-source-panel-preseal-20260906-01/"
MATERIALIZATION = "reports/s2nc/s2nc-receptor-materialization-20260906-01/result.json"
CONTRACT = "docs/S2NC_PROSPEKTIVER_AUDITIVER_A_ANWENDBARKEITSVERGLEICH.md"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(relative):
    return json.loads((ROOT / relative).read_bytes())


def hashes(plan):
    return {name: sha((ROOT / name).read_bytes()) for name in plan["source_hashes_before"]}


def publish(name, payload):
    data = c.canonical(payload)
    c.require(len(data) <= c.MAX_OUTPUT_BYTES, "OUTPUT_TOO_LARGE")
    destination = OUT / name
    c.require(not destination.exists(), "OUTPUT_ALREADY_EXISTS")
    temporary = OUT / (name + ".pending")
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.rename(temporary, destination)
    return sha(data)


def with_digest(payload, key):
    return {**payload, key: c.digest(payload)}


def decode_result(value):
    value = dict(value)
    value["visited_positions"] = tuple(tuple(p) for p in value["visited_positions"])
    value["rows"] = tuple(c.Relation(**{**row, "terms": tuple(row["terms"])}) for row in value["rows"])
    for key in ("b4_matches", "fast_matches"):
        value[key] = tuple(value[key])
    value["decision"] = c.Decision(**{**value["decision"], "source_ids": tuple(value["decision"]["source_ids"])})
    return c.CaseResult(**value)


def verify_once(cases, expected_sha, plan_sha):
    # Only sealed traces and execution inputs enter this stage, never expectations.
    path = OUT / "recording.json"
    raw = path.read_bytes()
    c.require(sha(raw) == expected_sha, "RECORDING_FILE_INVALID")
    record = json.loads(raw)
    c.require(record["record_digest"] == c.digest({k: v for k, v in record.items() if k != "record_digest"}),
              "RECORDING_DIGEST_INVALID")
    c.require(record["run_id"] == RUN_ID and record["run_plan_sha256"] == plan_sha
              and record["technical_status"] == "RECORDING_COMPLETE"
              and record["comparison"]["evaluation"] is None, "RECORDING_BINDING_INVALID")
    results = tuple(decode_result(item) for item in record["comparison"]["results"])
    decisions = tuple(c.Decision(**{**item, "source_ids": tuple(item["source_ids"])})
                      for item in record["comparison"]["baseline_decisions"])
    c.require(len(results) == len(decisions) == 96, "VERIFICATION_COUNT_INVALID")
    for index, (case, result) in enumerate(zip(cases + cases, results, strict=True)):
        c.require(result.rule == c.RULES[index // 48], "VERIFICATION_ORDER_INVALID")
        c.verify_case(case, result, result.digest)
        c.require(result.decision == decisions[index], "RECORDED_BASELINE_DIFFERS")
    c.require(c.encode_complete_comparison(results, decisions, None)
              == c.canonical(record["comparison"]), "CANONICAL_COMPARISON_INVALID")
    for left, right in zip(results[:48], results[48:], strict=True):
        c.require(left.input_digest == right.input_digest
                  and tuple(row.terms for row in left.rows) == tuple(row.terms for row in right.rows)
                  and set(right.b4_matches) <= set(left.b4_matches)
                  and set(right.fast_matches) <= set(left.fast_matches), "ARM_INPUT_OR_SUBSET_INVALID")
    c.require(path.read_bytes() == raw, "RECORDING_MUTATED")
    receipt = with_digest({"run_id": RUN_ID, "verification_status": "TECHNICALLY_VALID",
        "recording_sha256": expected_sha, "record_digest": record["record_digest"],
        "run_plan_sha256": plan_sha, "case_results_verified": 96,
        "read_only": True, "distance_recalculations": 0, "independent_verification_calls": 1,
        "verification_equality_terms": sum(r.equality_terms for r in results),
        "recording_unchanged": True}, "verification_digest")
    publish("verification.json", receipt)
    return results, receipt


def main():
    plan_raw = (OUT / "run-plan.json").read_bytes()
    plan = json.loads(plan_raw)
    # Exclusive reservation prevents this archived caller from repeating the run.
    with (OUT / "invocation.json").open("x", encoding="ascii") as handle:
        json.dump({"run_id": RUN_ID, "run_plan_sha256": sha(plan_raw), "invocations": 1}, handle)
    phase, completed, verification_calls = "SOURCE_BINDING", 0, 0
    try:
        c.require(plan["run_id"] == RUN_ID and hashes(plan) == plan["source_hashes_before"], "SOURCE_HASH_CHANGED")
        historic = subprocess.check_output(["git", "show", "1065db1:" + CONTRACT], cwd=ROOT)
        seal = read(PRESEAL + "seal.json")
        c.require(sha(historic) == seal["source_hashes"][CONTRACT] == plan["historical_contract_sha256"],
                  "HISTORICAL_CONTRACT_INVALID")
        c.require(seal["seal_digest"] == c.digest({k: v for k, v in seal.items() if k != "seal_digest"}),
                  "SEAL_DIGEST_INVALID")
        sources = c.bind_materialized_sources(read(MATERIALIZATION))
        cases = c.bind_fixed_cases(read(PRESEAL + "execution-plan.json"), sources)
        phase = "COMPARISON"
        results, decisions = [], []
        for rule in c.RULES:
            for case in cases:
                result = c.compare_case(case, rule)
                decision, equality = baseline.decide(case, result.b4_matches, result.fast_matches)
                c.require(result.equality_terms == equality, "BASELINE_COUNTER_INVALID")
                results.append(result)
                decisions.append(decision)
                completed += 1
        results, decisions = tuple(results), tuple(decisions)
        c.require(3 * sum(r.equality_terms for r in results) <= 9216, "TOTAL_EQUALITY_BUDGET_INVALID")
        comparison = json.loads(c.encode_complete_comparison(results, decisions, None))
        c.require(hashes(plan) == plan["source_hashes_before"], "SOURCE_HASH_CHANGED")
        recording = with_digest({"run_id": RUN_ID, "run_plan_sha256": sha(plan_raw),
            "technical_status": "RECORDING_COMPLETE", "execution_digest": c.EXECUTION_DIGEST,
            "materialization_digest": c.MATERIALIZATION_DIGEST,
            "comparison": comparison, "counters": {
                "cases_per_rule": 48, "relations": sum(len(r.rows) for r in results),
                "band_differences": sum(r.band_differences for r in results),
                "position_visits": sum(len(r.visited_positions) for r in results),
                "a_decisions": len(results), "baseline_decisions": len(decisions),
                "comparison_equality_terms": sum(r.equality_terms for r in results),
                "baseline_equality_terms": sum(r.equality_terms for r in results),
                "receptor_calls": 0, "memory_calls": 0, "field_calls": 0, "runtime_calls": 0}}, "record_digest")
        recording_sha = publish("recording.json", recording)
        phase, verification_calls = "READ_ONLY_VERIFICATION", 1
        verified, receipt = verify_once(cases, recording_sha, sha(plan_raw))
        phase = "EVALUATION"
        # Evaluator and sealed roles become accessible only after technical verification.
        from tools import _s2nc_private_rule_evaluation as evaluation
        expected_plan = read(PRESEAL + "evaluation-plan.json")
        c.require(expected_plan["evaluation_digest"] == seal["evaluation_digest"]
                  == c.digest({k: v for k, v in expected_plan.items() if k != "evaluation_digest"}),
                  "EVALUATION_PLAN_INVALID")
        expectations = tuple(evaluation.Expectation(item["case_id"], item["category"],
                                                    tuple(item["accepted_source_ids"]))
                             for item in expected_plan["cases"])
        measured = evaluation.evaluate(verified[:48], verified[48:], expectations)
        arm_counts = {}
        for rule, key in zip(c.RULES, ("mean", "all_bands"), strict=True):
            rows = measured["cases"]
            arm_counts[rule] = {
                "total_cases": 48, "known_present": 9, "expected_abstention": 39,
                "correct_known": sum(row[key]["correct_known"] for row in rows),
                "false_admissions": sum(row[key]["false_admission"] for row in rows),
                "missed_known": sum(row[key]["missed_known"] for row in rows),
                "correct_abstentions": sum(row[key]["correct"] and row[key]["abstention"] for row in rows),
                "statuses": dict(Counter(row[key]["status"] for row in rows)),
                "matched_positions": sum(len(r.b4_matches) + len(r.fast_matches) for r in verified if r.rule == rule)}
        evaluation_record = with_digest({"run_id": RUN_ID, "recording_sha256": recording_sha,
            "verification_digest": receipt["verification_digest"],
            "evaluation_plan_digest": expected_plan["evaluation_digest"],
            "evaluation": measured, "arm_counts": arm_counts}, "evaluation_record_digest")
        publish("evaluation.json", evaluation_record)
        after = hashes(plan)
        c.require(after == plan["source_hashes_before"], "SOURCE_HASH_CHANGED")
        c.require(sha((OUT / "recording.json").read_bytes()) == recording_sha, "RECORDING_MUTATED")
        final = {"run_id": RUN_ID, "technical_status": "TECHNICALLY_VALID",
            "recording_status": "RECORDING_COMPLETE", "functional_status": measured["status"],
            "completed_case_results": completed, "verification_calls": verification_calls,
            "source_hashes_after": after, "sources_unchanged": True,
            "artifacts": {name: {"sha256": sha((OUT / name).read_bytes()), "bytes": (OUT / name).stat().st_size}
                          for name in ("recording.json", "verification.json", "evaluation.json")}}
        c.require(sum(item["bytes"] for item in final["artifacts"].values()) <= c.MAX_OUTPUT_BYTES, "OUTPUT_TOO_LARGE")
        publish("completion.json", with_digest(final, "completion_digest"))
        print(json.dumps({"run_id": RUN_ID, "technical_status": "TECHNICALLY_VALID",
                          "functional_status": measured["status"], "arm_counts": arm_counts}, sort_keys=True))
        return 0
    except Exception as error:
        code = str(error) if isinstance(error, c.ComparisonError) else type(error).__name__
        failure = {"run_id": RUN_ID, "technical_status": "NOT_EVALUABLE", "phase": phase,
                   "error_code": code, "completed_case_results": completed,
                   "verification_calls": verification_calls, "execution": None, "evaluation": None,
                   "source_hashes_after": hashes(plan)}
        publish("failure.json", with_digest(failure, "failure_digest"))
        print(json.dumps(failure, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
