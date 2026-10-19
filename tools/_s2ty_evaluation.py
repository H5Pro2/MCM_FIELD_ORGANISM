"""Read-only, post-verification reporting for the fixed S2-TY schedule."""
from __future__ import annotations


class S2TYEvaluationError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _need(ok: bool, code: str) -> None:
    if not ok:
        raise S2TYEvaluationError(code)


EXPECTED = {
    "h1": {"ordinal": 12, "decision": "TRACE_MATCH", "matches": [[1, 1]]},
    "h2": {"ordinal": 19, "decision": "TRACE_MATCH", "matches": [[2, 0]]},
    "h3": {"ordinal": 26, "decision": "ABSTAIN_NO_RETAINED_TRACE", "matches": []},
}


def _normalized_matches(value: object) -> tuple[tuple[int, int], ...]:
    """Compare JSON lists and native tuples without changing match semantics."""
    _need(type(value) in (list, tuple), "EVALUATION_MATCHES_INVALID")
    pairs = []
    for pair in value:
        _need(type(pair) in (list, tuple) and len(pair) == 2, "EVALUATION_MATCHES_INVALID")
        generation, offset = pair
        _need(type(generation) is int and type(offset) is int, "EVALUATION_MATCHES_INVALID")
        pairs.append((generation, offset))
    return tuple(pairs)


def evaluate_verified(envelope: dict[str, object]) -> dict[str, object]:
    """Read decisions only after the envelope's single independent verification."""
    _need(type(envelope) is dict and envelope.get("status") == "COMPLETE", "EVALUATION_STATUS_INVALID")
    verification = envelope.get("verification")
    _need(type(verification) is dict and verification.get("status") == "VERIFIED", "EVALUATION_NOT_VERIFIED")
    record = envelope.get("record")
    _need(type(record) is dict and type(record.get("result")) is dict, "EVALUATION_RECORD_INVALID")
    receipts = record["result"].get("events")
    _need(type(receipts) is list, "EVALUATION_RECORD_INVALID")
    by_ordinal = {item.get("ordinal"): item for item in receipts if type(item) is dict}
    hints = {}
    for label, expected in EXPECTED.items():
        receipt = by_ordinal.get(expected["ordinal"])
        _need(type(receipt) is dict and receipt.get("adapter") == receipt.get("direct"), "EVALUATION_ARM_DIVERGENCE")
        observed = receipt["direct"]
        _need(type(observed) is dict and set(observed) == {"decision", "matches"}, "EVALUATION_DECISION_INVALID")
        observed_matches = _normalized_matches(observed["matches"])
        expected_matches = _normalized_matches(expected["matches"])
        hints[label] = {
            "ordinal": expected["ordinal"],
            "observed": observed,
            "expected": {"decision": expected["decision"], "matches": expected["matches"]},
            "matches_expected": observed["decision"] == expected["decision"] and observed_matches == expected_matches,
        }
    closes = {item.get("ordinal"): item for item in receipts if type(item) is dict and item.get("ordinal") in {5, 10, 17, 24}}
    _need(set(closes) == {5, 10, 17, 24}, "EVALUATION_CLOSE_RECEIPT_INVALID")
    transitions = {
        "p1": closes[5]["direct"],
        "p2": closes[10]["direct"],
        "p3": closes[17]["direct"],
        "p4": closes[24]["direct"],
    }
    _need(all(item.get("adapter") == item.get("direct") for item in closes.values()), "EVALUATION_ARM_DIVERGENCE")
    expected_transitions = {
        "p1": {"action": "TRACE_RETAINED", "generation": 1, "evicted": None},
        "p2": {"action": "TRACE_CONFIRMED", "generation": 1, "evicted": None},
        "p3": {"action": "TRACE_RETAINED", "generation": 2, "evicted": None},
        "p4": {"action": "TRACE_RETAINED", "generation": 3, "evicted": 1},
    }
    return {
        "schema": "s2ty.post-verification-evaluation.v1",
        "hints": hints,
        "transitions": transitions,
        "transition_matches_expected": {key: transitions[key] == value for key, value in expected_transitions.items()},
        "all_expected": all(item["matches_expected"] for item in hints.values()) and all(
            transitions[key] == value for key, value in expected_transitions.items()
        ),
    }
