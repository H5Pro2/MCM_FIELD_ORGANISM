"""Bound S2-ND one-shot call, recording, read-only verification, evaluation."""

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import sys

from tools import _s2nc_private_rule_comparison as c
from tools import _s2nc_private_decision_baseline as baseline
from tools import _s2nd_private_comparison_binding as binding


ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "s2nd-retention-loss-corpus-comparison-20260906-01"
OUT = ROOT / "reports/s2nd" / RUN_ID
PRESEAL = "reports/s2nd/s2nd-source-panel-preseal-20260906-02/"
MATERIALIZATION = "reports/s2nd/s2nd-receptor-materialization-20260906-01/"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(relative):
    return json.loads((ROOT / relative).read_bytes())


def hashes(plan):
    return {p: sha((ROOT / p).read_bytes()) for p in plan["source_hashes_before"]}


def sealed(value, key):
    return {**value, key: c.digest(value)}


def publish(name, value):
    raw = c.canonical(value)
    c.require(len(raw) <= c.MAX_OUTPUT_BYTES, "OUTPUT_TOO_LARGE")
    c.require(len(raw) + sum(p.stat().st_size for p in OUT.glob("*.json")) <= c.MAX_OUTPUT_BYTES,
              "TOTAL_OUTPUT_TOO_LARGE")
    destination = OUT / name
    c.require(not destination.exists(), "OUTPUT_ALREADY_EXISTS")
    pending = OUT / (name + ".pending")
    with pending.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    os.rename(pending, destination)
    return sha(raw)


def decode_decision(item):
    return c.Decision(**{**item, "source_ids": tuple(item["source_ids"])})


def decode_result(item):
    value = dict(item)
    value["visited_positions"] = tuple(tuple(p) for p in value["visited_positions"])
    value["rows"] = tuple(c.Relation(**{**row, "terms": tuple(row["terms"])}) for row in value["rows"])
    for key in ("b4_matches", "fast_matches"):
        value[key] = tuple(value[key])
    value["decision"] = decode_decision(value["decision"])
    return c.CaseResult(**value)


def verify_once(bound, expected_sha, plan_sha):
    # Re-read the published trace; no evaluator, matching or fresh differences.
    path = OUT / "recording.json"
    raw = path.read_bytes()
    c.require(sha(raw) == expected_sha, "RECORDING_FILE_INVALID")
    record = json.loads(raw)
    binding.check_root(record, "record_digest", record["record_digest"])
    c.require(record["run_id"] == RUN_ID and record["run_plan_sha256"] == plan_sha
              and record["technical_status"] == "RECORDING_COMPLETE"
              and record["comparison"]["evaluation"] is None, "RECORDING_BINDING_INVALID")
    results = tuple(decode_result(r) for r in record["comparison"]["results"])
    decisions = tuple(decode_decision(d) for d in record["comparison"]["baseline_decisions"])
    status = binding.verify_comparison(bound, results, decisions)
    c.require(status == "TECHNICALLY_VALID"
              and binding.encode_comparison(bound, results, decisions) == c.canonical(record["comparison"]),
              "COMPARISON_ENCODING_INVALID")
    equality = sum(r.equality_terms for r in results)
    expected_counters = dict(cases_per_rule=48, a_decisions=96, baseline_decisions=96,
                             relations=144, band_differences=3456, position_visits=1152,
                             comparison_equality_terms=equality, baseline_equality_terms=equality,
                             receptor_calls=0, memory_calls=0, context_calls=0, field_calls=0, runtime_calls=0)
    c.require(record["counters"] == expected_counters, "RECORDED_COUNTERS_INVALID")
    c.require(path.read_bytes() == raw, "RECORDING_MUTATED")
    receipt = sealed({"run_id": RUN_ID, "verification_status": status, "recording_sha256": expected_sha,
                      "record_digest": record["record_digest"], "run_plan_sha256": plan_sha,
                      "input_digest": bound.digest, "case_results_verified": 96,
                      "independent_verification_calls": 1, "distance_recalculations": 0,
                      "verification_equality_terms": equality, "read_only": True,
                      "recording_unchanged": True}, "verification_digest")
    publish("verification.json", receipt)
    return results, receipt


def arm_summary(rows, results):
    summaries = {}
    for rule, key in zip(c.RULES, ("mean", "all_bands"), strict=True):
        controls = [r for r in rows if not r["reference_present"]]
        summaries[rule] = {
            "total_cases": len(rows), "known_present": sum(r["reference_present"] for r in rows),
            "target_removal_controls": len(controls),
            "correct_known": sum(r[key]["correct_known"] for r in rows),
            "missed_known": sum(r[key]["missed_known"] for r in rows),
            "false_admissions": sum(r[key]["false_admission"] for r in rows),
            "correct_abstentions": sum(r[key]["correct"] and r[key]["abstention"] for r in rows),
            "statuses": dict(Counter(r[key]["status"] for r in rows)),
            "matched_positions": sum(len(r.b4_matches) + len(r.fast_matches) for r in results if r.rule == rule),
            "removal_correct_abstentions": sum(r[key]["abstention"] for r in controls),
            "removal_false_admissions": sum(r[key]["false_admission"] for r in controls),
            "removal_statuses": dict(Counter(r[key]["status"] for r in controls))}
    return summaries


def main():
    plan_raw = (OUT / "run-plan.json").read_bytes()
    plan = json.loads(plan_raw)
    with (OUT / "invocation.json").open("x", encoding="ascii") as handle:
        json.dump({"run_id": RUN_ID, "run_plan_sha256": sha(plan_raw), "invocations": 1}, handle)
    phase, completed, verification_calls = "SOURCE_BINDING", 0, 0
    case_id = rule = None
    try:
        c.require(plan["run_id"] == RUN_ID and hashes(plan) == plan["source_hashes_before"], "SOURCE_HASH_CHANGED")
        c.require(sys.version == plan["python_version"] and sys.executable == plan["python_executable"]
                  and sha(Path(sys.executable).read_bytes()) == plan["python_executable_sha256"], "PYTHON_BINDING_INVALID")
        execution, seal = read(PRESEAL + "execution-plan.json"), read(PRESEAL + "seal.json")
        bound = binding.bind_inputs(execution, seal, read(MATERIALIZATION + "result.json"),
                                    read(MATERIALIZATION + "verification.json"))
        phase = "COMPARISON"
        results, decisions = [], []
        for rule in c.RULES:
            for case in bound.cases:
                case_id = case.case_id
                result = c.compare_case(case, rule)
                decision, equality = baseline.decide(case, result.b4_matches, result.fast_matches)
                c.require(result.equality_terms == equality, "BASELINE_COUNTER_INVALID")
                results.append(result)
                decisions.append(decision)
                completed += 1
        results, decisions = tuple(results), tuple(decisions)
        case_id = rule = None
        phase = "RECORDING"
        comparison = json.loads(binding.encode_comparison(bound, results, decisions))
        c.require(hashes(plan) == plan["source_hashes_before"], "SOURCE_HASH_CHANGED")
        recording = sealed({"run_id": RUN_ID, "run_plan_sha256": sha(plan_raw),
            "technical_status": "RECORDING_COMPLETE", "comparison": comparison,
            "counters": dict(cases_per_rule=48, a_decisions=len(results), baseline_decisions=len(decisions),
                             relations=sum(len(r.rows) for r in results),
                             band_differences=sum(r.band_differences for r in results),
                             position_visits=sum(len(r.visited_positions) for r in results),
                             comparison_equality_terms=sum(r.equality_terms for r in results),
                             baseline_equality_terms=sum(r.equality_terms for r in results),
                             receptor_calls=0, memory_calls=0, context_calls=0, field_calls=0, runtime_calls=0)}, "record_digest")
        recording_sha = publish("recording.json", recording)
        phase, verification_calls = "READ_ONLY_VERIFICATION", 1
        verified, receipt = verify_once(bound, recording_sha, sha(plan_raw))
        phase = "EVALUATION"
        from tools import _s2nd_private_retention_evaluation as evaluator
        evaluation_plan = read(PRESEAL + "evaluation-plan.json")
        c.require(sha((ROOT / PRESEAL / "evaluation-plan.json").read_bytes()) == seal["evaluation_file_sha256"],
                  "EVALUATION_FILE_INVALID")
        measured = evaluator.evaluate(bound, verified[:48], verified[48:], evaluation_plan)
        summaries = arm_summary(measured["cases"], verified)
        variants = next(g for g in measured["retention_groups"] if
                        (g["variant_subtype"], g["competition"], g["receptor_variation"]) == ("ALL_VARIANTS", "ALL", "ALL"))
        evaluation_record = sealed({"run_id": RUN_ID, "recording_sha256": recording_sha,
            "verification_digest": receipt["verification_digest"], "evaluation_plan_digest": bound.roots.evaluation,
            "evaluation": measured, "arm_counts": summaries,
            "retention_status": variants["status"]}, "evaluation_record_digest")
        publish("evaluation.json", evaluation_record)
        after = hashes(plan)
        c.require(after == plan["source_hashes_before"], "SOURCE_HASH_CHANGED")
        c.require(sha((OUT / "recording.json").read_bytes()) == recording_sha, "RECORDING_MUTATED")
        final = sealed({"run_id": RUN_ID, "technical_status": "TECHNICALLY_VALID",
            "recording_status": "RECORDING_COMPLETE", "retention_status": variants["status"],
            "comparison_status": measured["comparison"]["status"],
            "completed_case_results": completed, "verification_calls": verification_calls,
            "source_hashes_after": after, "sources_unchanged": True,
            "artifacts": {name: {"sha256": sha((OUT / name).read_bytes()), "bytes": (OUT / name).stat().st_size}
                          for name in ("recording.json", "verification.json", "evaluation.json")}}, "completion_digest")
        publish("completion.json", final)
        print(json.dumps({"run_id": RUN_ID, "technical_status": "TECHNICALLY_VALID", "retention": variants,
                          "comparison_status": measured["comparison"]["status"], "arm_counts": summaries}, sort_keys=True))
        return 0
    except Exception as error:
        failure = sealed({"run_id": RUN_ID, "technical_status": "NOT_EVALUABLE", "phase": phase,
            "case_id": case_id, "rule": rule, "error_code": str(error) if isinstance(error, c.ComparisonError) else type(error).__name__,
            "completed_case_results": completed, "verification_calls": verification_calls,
            "execution": None, "evaluation": None, "source_hashes_after": hashes(plan)}, "failure_digest")
        publish("failure.json", failure)
        print(json.dumps(failure, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
