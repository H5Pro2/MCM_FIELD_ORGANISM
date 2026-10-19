"""Separate, non-operative S2-UC outcome projection after technical verification."""
from __future__ import annotations

EXPECTED = {
    ("g1", 12): ("TRACE_MATCH", "TRACE_MATCH"),
    ("g1", 24): ("ABSTAIN_AMBIGUOUS_RETAINED_TRACE", "TRACE_MATCH"),
    ("g1", 26): ("TRACE_MATCH", "ABSTAIN_NO_RETAINED_TRACE"),
    ("g2", 38): ("TRACE_MATCH", "ABSTAIN_NO_RETAINED_TRACE"),
    ("g3", 60): ("TRACE_MATCH", "TRACE_MATCH"),
    ("g3", 67): ("TRACE_MATCH", "ABSTAIN_NO_RETAINED_TRACE"),
    ("g3", 69): ("TRACE_MATCH", "TRACE_MATCH"),
}

def validate_expected():
    if len(EXPECTED) != 7 or any(type(key) is not tuple or len(key) != 2 or type(key[0]) is not str or type(key[1]) is not int
                             or type(value) is not tuple or len(value) != 2 for key, value in EXPECTED.items()):
        raise ValueError("EXPECTED_BINDING_INVALID")

def evaluate(record: dict[str, object]) -> dict[str, object]:
    validate_expected()
    if record.get("status") != "COMPLETE":
        raise ValueError("EVALUATION_RECORD_INVALID")
    rows = []
    for story in record["stories"]:
        for hint in story["hints"]:
            rows.append({"story": story["story"], "ordinal": hint["ordinal"],
                         "immediate": hint["immediate"]["decision"], "candidate": hint["candidate"]["decision"]})
    if len(rows) != 7 or len({(row["story"], row["ordinal"]) for row in rows}) != 7:
        raise ValueError("EXPECTED_RECEIPT_COUNT_INVALID")
    confirmed, violated, decision_changes = [], [], []
    for row in rows:
        expected = EXPECTED.get((row["story"], row["ordinal"]))
        if expected is None:
            violated.append({"key": (row["story"], row["ordinal"]), "actual": (row["immediate"], row["candidate"]), "expected": None})
            continue
        item = {"key": (row["story"], row["ordinal"]), "actual": (row["immediate"], row["candidate"]), "expected": expected}
        (confirmed if item["actual"] == expected else violated).append(item)
        if row["immediate"] != row["candidate"]: decision_changes.append(item)
    return {"status": "EVALUATED", "hint_decisions": rows, "hint_count": len(rows), "confirmed_expectations": confirmed,
            "violated_expectations": violated, "candidate_decision_changes": decision_changes,
            "candidate_gains": [], "candidate_losses": []}
