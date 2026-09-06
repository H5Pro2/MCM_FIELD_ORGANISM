"""Post-comparison evaluation; target relations do not reach either rule."""

from dataclasses import dataclass

from tools import _s2nc_private_rule_comparison as types


@dataclass(frozen=True, slots=True)
class Expectation:
    case_id: str
    category: str
    accepted_source_ids: tuple[str, ...]


def _classify(result, expectation):
    types.check_digest(result)
    types.require(type(result.decision) is types.Decision and result.decision.status in types.STATUSES,
                  "EVALUATION_STATUS_INVALID")
    types.require(result.case_id == expectation.case_id, "EVALUATION_CASE_MISMATCH")
    types.require(type(expectation.accepted_source_ids) is tuple
                  and len(set(expectation.accepted_source_ids)) == len(expectation.accepted_source_ids)
                  and all(types.identifier(s) for s in expectation.accepted_source_ids)
                  and types.identifier(expectation.category), "EXPECTATION_INVALID")
    admitted = result.decision.status == "A_RECENT_APPLICABLE"
    positive = bool(expectation.accepted_source_ids)
    correct_known = admitted and positive and bool(result.decision.source_ids) and all(
        source in expectation.accepted_source_ids for source in result.decision.source_ids)
    correct = correct_known if positive else not admitted
    return {"correct": correct, "correct_known": correct_known,
            "false_admission": admitted and not correct_known,
            "missed_known": positive and not correct_known,
            "abstention": not admitted, "status": result.decision.status,
            "source_ids": list(result.decision.source_ids)}


def evaluate(mean_results, all_results, expectations):
    types.require(all(type(items) is tuple for items in (mean_results, all_results, expectations))
                  and 0 < len(mean_results) == len(all_results) == len(expectations) <= 48,
                  "EVALUATION_COUNT_INVALID")
    ids = tuple(e.case_id for e in expectations)
    types.require(len(set(ids)) == len(ids), "DUPLICATE_EVALUATION_CASE")
    rows = []
    new_false = lost = improved = 0
    categories = {}
    for left, right, expected in zip(mean_results, all_results, expectations, strict=True):
        types.require(left.rule == types.RULES[0] and right.rule == types.RULES[1]
                      and left.input_digest == right.input_digest, "ARM_BINDING_INVALID")
        a, b = _classify(left, expected), _classify(right, expected)
        introduced = b["false_admission"] and not a["false_admission"]
        lost_known = a["correct_known"] and not b["correct_known"]
        gain = not a["correct"] and b["correct"] and (
            a["false_admission"] or (bool(expected.accepted_source_ids)
                                      and a["status"] == "A_RECENT_INTERNAL_AMBIGUITY"))
        new_false += int(introduced)
        lost += int(lost_known)
        improved += int(gain)
        rows.append({"case_id": expected.case_id, "category": expected.category,
                     "mean": a, "all_bands": b, "new_false_admission": introduced,
                     "lost_known": lost_known, "improvement": gain})
        group = categories.setdefault(expected.category, {"denominator": 0,
                                                        "mean_correct": 0, "all_correct": 0})
        group["denominator"] += 1
        group["mean_correct"] += int(a["correct"])
        group["all_correct"] += int(b["correct"])
    if improved and not new_false and not lost:
        status = "IMPROVEMENT_CONFIRMED"
    elif improved:
        status = "TRADEOFF"
    elif new_false or lost:
        status = "NEGATIVE"
    else:
        status = "NO_FUNCTIONAL_IMPROVEMENT"
    result = {"status": status, "categories": categories, "cases": rows,
              "improved_cases": improved, "new_false_admissions": new_false,
              "lost_known_hits": lost,
              "mean_prediction_status": "CONFIRMED" if all(r["mean"]["correct"] for r in rows) else "FALSIFIED",
              "all_prediction_status": "CONFIRMED" if all(r["all_bands"]["correct"] for r in rows) else "FALSIFIED"}
    return {**result, "evaluation_digest": types.digest(result)}
