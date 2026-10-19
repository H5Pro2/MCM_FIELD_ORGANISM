"""One bounded S2-SP visible partial-structure hint comparison."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor
from tools import _s2sp_private_shift_hint as hint


RUN_ID = "s2sp-shift-hint-real-20260919-02"
SCHEMA = "s2sp.shift-hint-run.v1"
RESOURCE_LIMITS = {
    "source_count": 6,
    "condition_count": 5,
    "receptor_analyses": 6,
    "stored_values": 1728,
    "memory_or_field_calls": 0,
    "record_bytes": 131_072,
    "verification_bytes": 16_384,
    "evaluation_bytes": 16_384,
    "balance_bytes": 8_192,
    "report_bytes": 8_192,
    "published_total_bytes": 196_608,
}
BACKGROUND = (24, 32, 48)
RED = (224, 64, 64)
GREEN = (64, 224, 64)
BLUE = (64, 64, 224)
YELLOW = (224, 224, 64)


def canonical(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def shifted(cells: tuple[tuple[int, int, int], ...]) -> tuple[tuple[int, int, int], ...]:
    return (BACKGROUND,) + cells[:-1]


TARGET = (BACKGROUND, RED, GREEN, BLUE, BACKGROUND, BACKGROUND, BACKGROUND, BACKGROUND, BACKGROUND, BACKGROUND, BACKGROUND, BACKGROUND)
SHIFTED = shifted(TARGET)
FOREIGN = SHIFTED[:4] + (YELLOW,) + SHIFTED[5:]
BOUNDARY = TARGET[:9] + (YELLOW,) + TARGET[10:]
CONTRADICTORY = SHIFTED[:5] + (YELLOW,) + SHIFTED[6:]
UNIFORM = (BACKGROUND,) * 12

SOURCES = (
    ("source-001", TARGET),
    ("source-002", SHIFTED),
    ("source-003", FOREIGN),
    ("source-004", BOUNDARY),
    ("source-005", CONTRADICTORY),
    ("source-006", UNIFORM),
)

EVALUATION_ROLES = {
    "source-001": "reference",
    "source-002": "one-cell-shift",
    "source-003": "foreign-interior",
    "source-004": "boundary-variant",
    "source-005": "contradictory-interior",
    "source-006": "uniform",
}

CONDITIONS = (
    ("same-position", "source-001", ("source-001",)),
    ("shifted-single", "source-002", ("source-001", "source-003")),
    ("boundary-ambiguity", "source-002", ("source-001", "source-004")),
    ("contradictory-rejected", "source-005", ("source-001",)),
    ("uniform-offset-ambiguity", "source-006", ("source-006",)),
)

EVALUATION_EXPECTATIONS = {
    "same-position": {"exact_baseline": True, "hint_status": "HINT_SINGLE"},
    "shifted-single": {"exact_baseline": False, "hint_status": "HINT_SINGLE"},
    "boundary-ambiguity": {"exact_baseline": False, "hint_status": "HINT_CANDIDATE_AMBIGUOUS"},
    "contradictory-rejected": {"exact_baseline": False, "hint_status": "HINT_NOT_APPLICABLE"},
    "uniform-offset-ambiguity": {"exact_baseline": True, "hint_status": "HINT_OFFSET_AMBIGUOUS"},
}


def make_frame(cells: tuple[tuple[int, int, int], ...]) -> np.ndarray:
    frame = np.empty((1080, 1920, 3), dtype=np.uint8)
    frame[:, :, :] = BACKGROUND
    for column, color in enumerate(cells):
        frame[0:135, column * 160 : (column + 1) * 160, :] = color
    return frame


def source_record(source_id: str, cells: tuple[tuple[int, int, int], ...], frame_index: int) -> dict[str, object]:
    frame = make_frame(cells)
    frame_hash = hashlib.sha256(frame.tobytes()).hexdigest()
    state = LocalChannelGridReceptor().analyze(frame, frame_index=frame_index)
    del frame
    recipe = {"source_id": source_id, "top_row_rgb": [list(item) for item in cells], "frame_index": frame_index}
    return {
        "source_id": source_id,
        "recipe_digest": digest(recipe),
        "frame_sha256": frame_hash,
        "frame_index": frame_index,
        "geometry_id": state.geometry_id,
        "values": list(state.channel_values),
        "values_digest": digest(list(state.channel_values)),
    }


def _finding_payload(finding: hint.ShiftFinding) -> dict[str, object]:
    return {"status": finding.status, "matching_offsets": list(finding.matching_offsets), "overlap_cells": list(finding.overlap_cells)}


def _hint_payload(result: hint.ShiftHint) -> dict[str, object]:
    return {"status": result.status, "candidate_ids": list(result.candidate_ids), "findings": [_finding_payload(item) for item in result.findings]}


def _reference_compare(cue: tuple[float, ...], candidate: tuple[float, ...]) -> tuple[str, tuple[int, ...], tuple[int, ...]]:
    """Independent fixed-offset calculation; does not call the productive helper."""

    matches: list[int] = []
    overlap: tuple[int, ...] = ()
    for offset in (-1, 0, 1):
        columns = tuple(index for index in range(10) if 0 <= index - offset < 10)
        equal = True
        for column in columns:
            left = cue[3 * column : 3 * column + 3]
            right_index = column - offset
            right = candidate[3 * right_index : 3 * right_index + 3]
            if left != right:
                equal = False
                break
        if equal:
            matches.append(offset)
            overlap = columns
    if len(matches) == 1:
        return "SHIFT_MATCH", tuple(matches), overlap
    if len(matches) > 1:
        return "SHIFT_OFFSET_AMBIGUOUS", tuple(matches), ()
    return "SHIFT_NOT_APPLICABLE", (), ()


def verify_record(record: dict[str, object]) -> dict[str, object]:
    if record.get("schema") != SCHEMA or record.get("run_id") != RUN_ID:
        raise ValueError("record binding is invalid")
    sources = record["sources"]
    if not isinstance(sources, list) or len(sources) != 6:
        raise ValueError("source count is invalid")
    values: dict[str, tuple[float, ...]] = {}
    for item in sources:
        source_id = item["source_id"]
        vector = tuple(item["values"])
        if not isinstance(source_id, str) or len(vector) != 288 or digest(list(vector)) != item["values_digest"]:
            raise ValueError("stored source values are invalid")
        values[source_id] = vector
    for row in record["conditions"]:
        cue = values[row["cue_source_id"]]
        candidate_ids = tuple(row["candidate_source_ids"])
        expected_findings = []
        matching_ids = []
        offset_ambiguous = False
        exact_ids = []
        for candidate_id in candidate_ids:
            status, offsets, overlap = _reference_compare(cue, values[candidate_id])
            expected_findings.append({"status": status, "matching_offsets": list(offsets), "overlap_cells": list(overlap)})
            if status == "SHIFT_MATCH":
                matching_ids.append(candidate_id)
            offset_ambiguous = offset_ambiguous or status == "SHIFT_OFFSET_AMBIGUOUS"
            if cue[:32] == values[candidate_id][:32]:
                exact_ids.append(candidate_id)
        expected_status = "HINT_SINGLE" if len(matching_ids) == 1 else "HINT_CANDIDATE_AMBIGUOUS" if len(matching_ids) > 1 else "HINT_OFFSET_AMBIGUOUS" if offset_ambiguous else "HINT_NOT_APPLICABLE"
        if row["hint"] != {"status": expected_status, "candidate_ids": matching_ids, "findings": expected_findings}:
            raise ValueError("shift hint verification mismatch")
        if row["exact_baseline_candidate_ids"] != exact_ids:
            raise ValueError("exact baseline verification mismatch")
    return {"schema": "s2sp.shift-hint-verification.v1", "run_id": RUN_ID, "status": "VERIFIED", "condition_count": len(record["conditions"]), "record_digest": digest(record)}


def _bounded_payloads(payloads: dict[str, bytes]) -> dict[str, object]:
    limits = {
        "record.json": RESOURCE_LIMITS["record_bytes"],
        "verification.json": RESOURCE_LIMITS["verification_bytes"],
        "evaluation.json": RESOURCE_LIMITS["evaluation_bytes"],
        "balance.json": RESOURCE_LIMITS["balance_bytes"],
        "REPORT.md": RESOURCE_LIMITS["report_bytes"],
    }
    sizes = {name: len(contents) for name, contents in payloads.items()}
    violations = {name: {"actual": sizes[name], "limit": limits[name]} for name in sizes if sizes[name] > limits[name]}
    total = sum(sizes.values())
    if total > RESOURCE_LIMITS["published_total_bytes"]:
        violations["published_total"] = {"actual": total, "limit": RESOURCE_LIMITS["published_total_bytes"]}
    if violations:
        raise RuntimeError(f"S2SP_RESOURCE_LIMIT: {json.dumps(violations, sort_keys=True)}")
    return {"schema": "s2sp.shift-hint-balance.v1", "run_id": RUN_ID, "sizes": sizes, "total_bytes": total, "limits": limits, "published_total_limit": RESOURCE_LIMITS["published_total_bytes"]}


def render_report(evaluation: dict[str, object]) -> str:
    """Render only recorded result classes; no outcome is stated in advance."""

    rows = evaluation["rows"]
    if not isinstance(rows, list):
        raise ValueError("evaluation rows are invalid")
    by_status: dict[str, list[str]] = {}
    exact_ids: list[str] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("condition_id"), str) or not isinstance(row.get("hint_status"), str):
            raise ValueError("evaluation row is invalid")
        by_status.setdefault(row["hint_status"], []).append(row["condition_id"])
        if row.get("exact_baseline_candidate_ids"):
            exact_ids.append(row["condition_id"])
    def listed(status: str) -> str:
        return ", ".join(by_status.get(status, ())) or "keine"
    exact_summary = ", ".join(exact_ids) or "keine"
    return "\n".join((
        "# S2-SP Teilstrukturhinweisvergleich",
        "",
        "Der Bericht beschreibt ausschließlich die gespeicherten und unabhängig verifizierten Entscheidungen.",
        "",
        f"Exaktbaseline mit mindestens einem Kandidaten: {exact_summary}.",
        f"Eindeutige Teilstrukturhinweise: {listed('HINT_SINGLE')}.",
        f"Kandidatenmehrdeutigkeiten: {listed('HINT_CANDIDATE_AMBIGUOUS')}.",
        f"Offsetmehrdeutigkeiten: {listed('HINT_OFFSET_AMBIGUOUS')}.",
        f"Enthaltungen ohne anwendbaren Teilstrukturhinweis: {listed('HINT_NOT_APPLICABLE')}.",
        "",
        "Der Vergleich verändert weder Memory noch Feld und erzeugt keine öffentliche Hypothese. Ein passender sichtbarer Teilbereich belegt weder Identität einer ganzen Wahrnehmung noch korrekte öffentliche Zuordnung.",
        "",
        "Siehe `record.json`, `verification.json`, `evaluation.json` und `balance.json`.",
        "",
    ))


def run_once() -> Path:
    root = Path(__file__).resolve().parents[1]
    output = root / "reports" / RUN_ID
    if output.exists():
        raise RuntimeError(f"output already exists: {output}")
    materialized = [source_record(source_id, cells, index) for index, (source_id, cells) in enumerate(SOURCES)]
    vectors = {item["source_id"]: tuple(item["values"]) for item in materialized}
    rows = []
    for condition_id, cue_id, candidate_ids in CONDITIONS:
        candidates = tuple((candidate_id, vectors[candidate_id]) for candidate_id in candidate_ids)
        result = hint.collect_shift_hints(vectors[cue_id], candidates)
        rows.append(
            {
                "condition_id": condition_id,
                "cue_source_id": cue_id,
                "candidate_source_ids": list(candidate_ids),
                "exact_baseline_candidate_ids": [candidate_id for candidate_id in candidate_ids if hint.exact_visible_match(vectors[cue_id], vectors[candidate_id])],
                "hint": _hint_payload(result),
            }
        )
    plan = {"schema": SCHEMA, "offsets": list(hint.OFFSETS), "complete_visible_cells": hint.COMPLETE_CELL_COUNT, "source_ids": [item[0] for item in SOURCES], "conditions": [item[0] for item in CONDITIONS]}
    record = {"schema": SCHEMA, "run_id": RUN_ID, "plan_digest": digest(plan), "sources": materialized, "conditions": rows, "resource_limits": RESOURCE_LIMITS}
    verification = verify_record(record)
    evaluation_rows = []
    for row in rows:
        expected = EVALUATION_EXPECTATIONS[row["condition_id"]]
        actual_exact = bool(row["exact_baseline_candidate_ids"])
        actual_status = row["hint"]["status"]
        evaluation_rows.append(
            {
                "condition_id": row["condition_id"],
                "exact_baseline_candidate_ids": row["exact_baseline_candidate_ids"],
                "hint_status": actual_status,
                "hint_candidate_ids": row["hint"]["candidate_ids"],
                "evaluation": "EXPECTED" if actual_exact == expected["exact_baseline"] and actual_status == expected["hint_status"] else "DEVIATION",
            }
        )
    evaluation = {
        "schema": "s2sp.shift-hint-evaluation.v1",
        "run_id": RUN_ID,
        "roles": EVALUATION_ROLES,
        "rows": evaluation_rows,
        "statement": "Hints describe visible partial-structure compatibility only; they do not identify a whole experience.",
    }
    report = render_report(evaluation)
    payloads = {
        "record.json": canonical(record),
        "verification.json": canonical(verification),
        "evaluation.json": canonical(evaluation),
        "REPORT.md": report.encode("utf-8"),
    }
    preliminary = _bounded_payloads({**payloads, "balance.json": b"{}"})
    payloads["balance.json"] = canonical(preliminary)
    balance = _bounded_payloads(payloads)
    payloads["balance.json"] = canonical(balance)
    _bounded_payloads(payloads)
    output.mkdir(parents=True)
    for name, contents in payloads.items():
        (output / name).write_bytes(contents)
    return output


if __name__ == "__main__":
    try:
        print(run_once())
    except Exception as exc:
        print(f"S2SP_RUN_FAILED: {exc}", file=sys.stderr)
        raise
