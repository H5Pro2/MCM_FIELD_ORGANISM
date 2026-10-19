"""One bound private S2-SP comparison over actual formed memory states."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools import _s2jw_default_live_profile as profile_module
from tools import _s2sp_private_memory_compare as core


RUN_ID = "s2sp-memory-compare-real-20260919-01"
LIMIT = 524_288


def canonical(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def visible(values: tuple[float, ...]) -> list[float]:
    return list(values[:30])


def _scan(cue: tuple[float, ...], state) -> dict[str, object]:
    banks = []
    for bank, candidates in core._candidate_rows(state).items():
        comparison = core.compare_state(state=state, cue_values=cue)
        row = next(item for item in comparison["banks"] if item["bank"] == bank)
        bindings = [
            {"candidate_id": candidate_id, "visible_values": visible(values), "visible_digest": digest(visible(values))}
            for candidate_id, values in candidates
        ]
        banks.append({**row, "candidate_bindings": bindings})
    payload = {"state_digest": state.state_digest, "cue_visible_values": visible(cue), "cue_visible_digest": digest(visible(cue)), "banks": banks}
    return {**payload, "scan_digest": digest(payload)}


def _independent(cue: list[float], candidate: list[float]) -> tuple[str, list[int]]:
    matches = []
    for offset in (-1, 0, 1):
        columns = [column for column in range(10) if 0 <= column - offset < 10]
        if all(cue[3 * column : 3 * column + 3] == candidate[3 * (column - offset) : 3 * (column - offset) + 3] for column in columns):
            matches.append(offset)
    if len(matches) == 1:
        return "SHIFT_MATCH", matches
    if len(matches) > 1:
        return "SHIFT_OFFSET_AMBIGUOUS", matches
    return "SHIFT_NOT_APPLICABLE", []


def verify(record: dict[str, object]) -> dict[str, object]:
    for item in record["events"]:
        if item["kind"] != "CUE":
            continue
        scan = item["scan"]
        cue = scan["cue_visible_values"]
        if digest(cue) != scan["cue_visible_digest"]:
            raise ValueError("cue digest differs")
        for bank in scan["banks"]:
            matching, offset_ambiguous, exact = [], False, []
            for candidate in bank["candidate_bindings"]:
                if digest(candidate["visible_values"]) != candidate["visible_digest"]:
                    raise ValueError("candidate digest differs")
                status, offsets = _independent(cue, candidate["visible_values"])
                if status == "SHIFT_MATCH":
                    matching.append(candidate["candidate_id"])
                offset_ambiguous = offset_ambiguous or status == "SHIFT_OFFSET_AMBIGUOUS"
                if cue[:32] == candidate["visible_values"][:32]:
                    exact.append(candidate["candidate_id"])
            expected = "HINT_SINGLE" if len(matching) == 1 else "HINT_CANDIDATE_AMBIGUOUS" if len(matching) > 1 else "HINT_OFFSET_AMBIGUOUS" if offset_ambiguous else "HINT_NOT_APPLICABLE"
            if bank["hint_status"] != expected or bank["hint_candidate_ids"] != matching or bank["exact_baseline_candidate_ids"] != exact:
                raise ValueError("scan differs")
    return {"status": "VERIFIED", "run_id": RUN_ID, "record_digest": digest(record)}


def run_once() -> Path:
    root = Path(__file__).resolve().parents[1]
    output = root / "reports" / RUN_ID
    if output.exists():
        raise RuntimeError("output exists")
    profile = profile_module.build_s2jw_default_live_profile()
    config = core.build_config()
    source = core.Sources(profile)
    state = core.coordinator.initial_s2jv_composite_state(config)
    events, initial_b4 = [], None
    sequence = (
        ("e01", "FORMATION", core.TARGET), ("e02", "CUE", core.TARGET),
        ("e03", "FORMATION", core.TARGET), ("e04", "FORMATION", core.TARGET), ("e05", "FORMATION", core.TARGET),
        ("e06", "CUE", core.TARGET), ("e07", "CUE", core.SHIFTED),
        ("e08", "FORMATION", core.BOUNDARY),
        *tuple((f"e{index:02d}", "FORMATION", core.FOREIGN) for index in range(9, 17)),
        ("e17", "CUE", core.TARGET), ("e18", "CUE", core.SHIFTED), ("e19", "CUE", core.FOREIGN),
    )
    formation_ordinal = 0
    for event_ordinal, (event_id, kind, cells) in enumerate(sequence):
        if kind == "FORMATION":
            pair, values = source.formation(event_id=event_id, ordinal=formation_ordinal, cells=cells)
            result = core.form(config=config, state=state, pair=pair, event_id=event_id, run_id=RUN_ID)
            state = result.poststate
            rows = core._candidate_rows(state)
            if event_id == "e01":
                initial_b4 = [candidate_id for candidate_id, _ in rows["B4"]]
            events.append({"event_id": event_id, "kind": kind, "state_digest": state.state_digest, "formation_receipt": result.receipt.receipt_digest, "visual_values_digest": digest(list(values)), "b4_candidate_ids": [candidate_id for candidate_id, _ in rows["B4"]]})
            formation_ordinal += 1
        else:
            cue = source.cue(ordinal=event_ordinal, cells=cells)
            events.append({"event_id": event_id, "kind": kind, "state_digest": state.state_digest, "scan": _scan(cue, state)})
    _ = initial_b4
    record = {
        "schema": core.SCHEMA, "run_id": RUN_ID, "status": "RECORDING_COMPLETE", "config_digest": config.config_digest,
        "events": events, "counts": {"events": len(events), "formations": formation_ordinal, "cues": len(events) - formation_ordinal, "audio_analyses": source.audio_analyses, "visual_analyses": source.visual_analyses, "field_contacts": 0},
        "initial_b4_candidate_ids": initial_b4, "final_b4_candidate_ids": events[-4]["b4_candidate_ids"],
    }
    record["record_digest"] = digest(record)
    verification = verify(record)
    evaluation = {"run_id": RUN_ID, "rows": [{"event_id": item["event_id"], "banks": [{"bank": bank["bank"], "exact": bank["exact_baseline_candidate_ids"], "hint": bank["hint_status"], "hint_candidates": bank["hint_candidate_ids"]} for bank in item["scan"]["banks"]]} for item in events if item["kind"] == "CUE"], "b4_original_generation_available_finally": bool(set(initial_b4 or ()) & set(record["final_b4_candidate_ids"])), "statement": "Private partial hints are not public hypotheses and do not establish whole-content identity."}
    payloads = {"record.json": canonical(record), "verification.json": canonical(verification), "evaluation.json": canonical(evaluation)}
    if sum(map(len, payloads.values())) > LIMIT:
        raise RuntimeError("record budget exceeded")
    output.mkdir(parents=True)
    for name, value in payloads.items():
        (output / name).write_bytes(value)
    return output


if __name__ == "__main__":
    print(run_once())
