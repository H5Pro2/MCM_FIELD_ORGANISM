"""Private four-frame B4 sequence probe; no public or field integration."""

from __future__ import annotations

import argparse
import base64
from collections import Counter
import itertools
import json
import math
from pathlib import Path
import time
import traceback

from tools import _visual_l1_calibration_probe as calibration


spatial, b4 = calibration.spatial, calibration.b4
ROOT, BASE = calibration.ROOT, calibration.BASE
require, seal = calibration.require, calibration.seal
RUN_ID = "sequence-confirmation-20260829-01"
QUALIFICATION_ID = "sequence-confirmation-validator-20260829-01"
PLAN = "docs/VISUELLE_REIHENFOLGE_UNABHAENGIGE_BESTAETIGUNGSPLAN.md"
AUTHORIZATION = f"reports/tspm1_functional/{RUN_ID}.authorization.txt"
PRESTART = f"reports/tspm1_functional/{RUN_ID}.prestart.md"
_RUN_RELEASE_ENABLED = False
VISUAL_THRESHOLD = float(calibration.CALIBRATED)
PATTERNS = {
    "N1": (200, 200, 40, 200, 40, 40),
    "N2": (200, 200, 40, 40, 200, 40),
    "N3": (200, 200, 40, 40, 40, 200),
    "N4": (200, 40, 200, 200, 40, 40),
}
FORMATIONS = (("N1", "N2", "N3", "N4"), ("N1", "N3", "N2", "N4"))
VIEWS = ("GEORDNET", "REIHENFOLGEBLIND")
FORMATION_COSTS = {**calibration.FORMATION_COSTS, "derived_index_from_accepted_count": True}
SEQUENCE_COSTS = {
    "probe_vectors": 4, "stored_vectors": 4, "av_pair_comparisons": 16,
    "functional_l1_terms": 416, "validation_l1_terms": 416,
    "elemental_functional_terms_per_probe_vector": 104,
    "elemental_validation_terms_per_probe_vector": 104,
    "elemental_combined_limit": 234, "elemental_combined_actual": 208,
    "sequence_combined_limit": 832, "sequence_combined_actual": 832,
    "ordered_bit_checks": 4, "blind_assignment_bit_checks": 96,
    "transient_probe_values": 104, "transient_distance_values": 32,
    "transient_acceptance_bits": 16, "resource_word_limit": 255,
}


def source_manifest():
    source = calibration.source_manifest()
    existing = {item["path"] for item in source["sources"]}
    for relative in (PLAN, AUTHORIZATION, PRESTART,
                     f"reports/tspm1_functional/{QUALIFICATION_ID}.authorization.txt",
                     f"reports/tspm1_functional/{QUALIFICATION_ID}.prestart.md",
                     f"reports/tspm1_functional/{QUALIFICATION_ID}/output.txt",
                     f"reports/tspm1_functional/{QUALIFICATION_ID}/result.json",
                     "tools/_visual_sequence_memory_probe.py",
                     "tests/test_visual_sequence_memory_probe.py"):
        if relative not in existing:
            raw = (ROOT / relative).read_bytes()
            source["sources"].append({"path": relative, "sha256": spatial.raw_hash(raw),
                "bytes_base64": base64.b64encode(raw).decode("ascii")})
    source["sources"].sort(key=lambda item: item["path"])
    return source


def probe_recipe(episode):
    original = FORMATIONS[episode]
    other = FORMATIONS[1 - episode]
    return ((original, 0, True), (other, 0, False),
            (original, -8, True), (other, -8, False),
            (original, 8, True), (other, 8, False))


def _validate_sequence_state(state):
    require(type(state) is b4._B4State and state.accepted_count == 4, "four-entry B4 state required")
    require(len(state.entries) == 9, "B4 capacity")
    slot_ids = {f"b4.slot.{i:03d}" for i in range(9)}
    require({entry.slot_id for entry in state.entries} == slot_ids, "slot identity")
    occupied = [entry for entry in state.entries if entry.occupied]
    require(len(occupied) == 4 and sum(not entry.occupied for entry in state.entries) == 5, "B4 occupancy")
    require({entry.formation_index for entry in occupied} == {1, 2, 3, 4}, "formation chronology")
    for entry in occupied:
        spatial._values(entry.values, 26)
    for entry in state.entries:
        if not entry.occupied:
            require(entry.values == () and entry.formation_index is None, "empty entry metadata")
    return tuple(sorted(occupied, key=lambda entry: entry.formation_index))


def advance_sequence_b4(prestate, offered):
    """One real B4 transition with its index derived only from the prestate."""
    require(type(prestate) is b4._B4State, "B4 prestate required")
    spatial._values(offered, 26)
    require(0 <= prestate.accepted_count < 4, "bounded four-frame formation")
    before = b4._canonical(prestate)
    formation_index = prestate.accepted_count + 1
    poststate, event, native_cost = b4._advance_b4(prestate, tuple(offered), formation_index)
    after = b4._canonical(poststate)
    require(b4._canonical(prestate) == before, "formation mutated prestate")
    validate_formation_transition(before, after, tuple(offered), formation_index, event, native_cost)
    return poststate, {"formation_index": formation_index, "event": event,
                       "native_cost": native_cost, "prestate": before, "poststate": after,
                       "costs": FORMATION_COSTS}


def validate_formation_transition(before, after, offered, formation_index, event, native_cost):
    require(before["accepted_count"] + 1 == formation_index == after["accepted_count"], "derived formation index")
    require(event == {"event": "B4_APPENDED", "slot_id": f"b4.slot.{formation_index-1:03d}"}, "append event")
    require(native_cost == [27, 0] or native_cost == (27, 0), "native formation cost")
    old = {entry["slot_id"]: entry for entry in before["entries"]}
    new = {entry["slot_id"]: entry for entry in after["entries"]}
    require(set(old) == set(new) == {f"b4.slot.{i:03d}" for i in range(9)}, "transition slots")
    selected = event["slot_id"]
    require(old[selected] == {"slot_id": selected, "occupied": False, "values": [],
                              "formation_index": None}, "selected slot was not free")
    require(new[selected] == {"slot_id": selected, "occupied": True, "values": list(offered),
                              "formation_index": formation_index}, "selected slot payload")
    require(all(old[key] == new[key] for key in old if key != selected), "unselected entry changed")


def _distance_table(ordered_entries, probes):
    rows = []
    for probe in probes:
        spatial._values(probe, 26)
        row = []
        for entry in ordered_entries:
            auditory = b4.normalized_mean_l1_distance(probe[:8], entry.values[:8])
            visual = b4.normalized_mean_l1_distance(probe[8:], entry.values[8:])
            row.append((auditory, visual, auditory <= 0.2 and visual <= VISUAL_THRESHOLD))
        rows.append(tuple(row))
    return tuple(rows)


def probe_visual_sequence_read_only(bank, ordered_probe_values):
    """Compare one four-vector query in ordered and order-blind views."""
    require(type(ordered_probe_values) is tuple and len(ordered_probe_values) == 4, "four probe vectors required")
    ordered_entries = _validate_sequence_state(bank)
    before = b4._canonical(bank)
    table = _distance_table(ordered_entries, ordered_probe_values)
    row_hits = tuple(sum(cell[2] for cell in row) for row in table)
    column_hits = tuple(sum(table[row][column][2] for row in range(4)) for column in range(4))
    require(row_hits == (1, 1, 1, 1) and column_hits == (1, 1, 1, 1), "non-unique sequence contents")
    ordered = all(table[index][index][2] for index in range(4))
    assignments = tuple(permutation for permutation in itertools.permutations(range(4))
                        if all(table[row][permutation[row]][2] for row in range(4)))
    blind = len(assignments) > 0
    require(len(assignments) == 1, "unexpected blind assignment multiplicity")
    after = b4._canonical(bank)
    require(before == after, "sequence probe mutated bank")
    return {
        "visual_threshold_numerator": 44, "visual_threshold_denominator": 765,
        "visual_threshold": VISUAL_THRESHOLD, "auditory_threshold": 0.2,
        "distance_table": table, "row_hits": row_hits, "column_hits": column_hits,
        "ordered": {"recognized": ordered,
                    "returned": tuple(entry.values for entry in ordered_entries) if ordered else None,
                    "position_bits": tuple(table[i][i][2] for i in range(4))},
        "order_blind": {"recognized": blind, "assignment_count": len(assignments),
                        "assignment": assignments[0] if blind else None},
        "prestate": before, "poststate": after, "state_digest": b4._digest(before),
        "costs": SEQUENCE_COSTS,
    }


def score(expected, recognized, returned_correct=True):
    if recognized and not returned_correct:
        label = "WRONG_RETURNED_VALUES"
    elif recognized and not expected:
        label = "FALSE_EQUIVALENCE"
    elif not recognized and expected:
        label = "FALSE_REJECTION"
    else:
        label = "CORRECT_RECOGNITION" if recognized else "CORRECT_REJECTION"
    return {"expected_recognized": expected, "classification": label,
            "returned_values_correct": returned_correct}


def image_record(journal, episode, position, label, delta, role, probe_index):
    frame, record = calibration.analyze(journal, episode, position, PATTERNS[label], delta)
    p = record["payload"]
    require(tuple(p["frame"]["values"]) == calibration.image_facts(PATTERNS[label], delta)["expected_visual"],
            "receptor sequence value")
    require((p["frame"]["window_start_tick"], p["frame"]["window_end_tick"]) == (position, position + 1),
            "receptor sequence tick")
    return frame, record


def form_record(journal, episode, position, frame, image, state):
    offered = spatial.frame_to_b4(frame, "B4_SPATIAL")
    context = {"episode": episode, "position": position,
               "owner": f"{RUN_ID}.episode.{episode}", "input_digest": image["digest"],
               "prestate_digest": b4._digest(b4._canonical(state))}
    journal.emit("sequence_formation_start", context)
    poststate, finding = advance_sequence_b4(state, offered)
    record = journal.emit("sequence_formation", {**context, "offered": offered, **finding,
        "poststate_digest": b4._digest(finding["poststate"])})
    return poststate, record


def sequence_probe_record(journal, episode, probe_index, delta, labels, expected_ordered,
                          frames, images, bank, formations):
    probes = tuple(spatial.frame_to_b4(frame, "B4_SPATIAL") for frame in frames)
    before = b4._canonical(bank)
    context = {"episode": episode, "probe_index": probe_index, "delta": delta,
        "owner": f"{RUN_ID}.episode.{episode}", "input_digests": [item["digest"] for item in images],
        "formation_digests": [item["digest"] for item in formations],
        "state_digest": b4._digest(before)}
    journal.emit("sequence_probe_start", context)
    finding = probe_visual_sequence_read_only(bank, probes)
    require(b4._canonical(bank) == before, "probe changed live bank")
    original = tuple(entry.values for entry in _validate_sequence_state(bank))
    returned = finding["ordered"]["returned"]
    ordered_score = score(expected_ordered, finding["ordered"]["recognized"],
                          returned is None or tuple(returned) == original)
    blind_score = score(True, finding["order_blind"]["recognized"], True)
    journal.emit("sequence_probe", {**context, "probe_labels": labels, "probes": probes,
        "expected_ordered": expected_ordered, "finding": finding,
        "ordered_score": ordered_score, "blind_score": blind_score})


def _recorded_finding(state_payload, probes):
    entries = sorted((entry for entry in state_payload["entries"] if entry["occupied"]),
                     key=lambda entry: entry["formation_index"])
    require([entry["formation_index"] for entry in entries] == [1, 2, 3, 4], "recorded chronology")
    table = []
    for probe in probes:
        row = []
        for entry in entries:
            stored = entry["values"]
            auditory = math.fsum(abs(x-y) for x,y in zip(probe[:8], stored[:8], strict=True)) / 8
            visual = math.fsum(abs(x-y) for x,y in zip(probe[8:], stored[8:], strict=True)) / 18
            row.append([auditory, visual, auditory <= 0.2 and visual <= VISUAL_THRESHOLD])
        table.append(row)
    row_hits = [sum(cell[2] for cell in row) for row in table]
    column_hits = [sum(table[row][column][2] for row in range(4)) for column in range(4)]
    require(row_hits == column_hits == [1, 1, 1, 1], "recorded uniqueness")
    ordered = all(table[i][i][2] for i in range(4))
    assignments = [list(permutation) for permutation in itertools.permutations(range(4))
                   if all(table[row][permutation[row]][2] for row in range(4))]
    require(len(assignments) == 1, "recorded assignment multiplicity")
    return {"visual_threshold_numerator": 44, "visual_threshold_denominator": 765,
        "visual_threshold": VISUAL_THRESHOLD, "auditory_threshold": 0.2,
        "distance_table": table, "row_hits": row_hits, "column_hits": column_hits,
        "ordered": {"recognized": ordered,
            "returned": [entry["values"] for entry in entries] if ordered else None,
            "position_bits": [table[i][i][2] for i in range(4)]},
        "order_blind": {"recognized": True, "assignment_count": 1, "assignment": assignments[0]},
        "prestate": state_payload, "poststate": state_payload,
        "state_digest": b4._digest(state_payload), "costs": SEQUENCE_COSTS}


def recorded_empty_b4_payload():
    """Return the one canonical empty state used by record-only inspection."""
    return spatial.empty_payload()


def inspect_records(records):
    pairs = calibration.checked_pairs(records)
    probes = []
    formation_count = image_count = 0

    def take(kind, episode, position=None):
        record = next(pairs)
        p = record["payload"]
        require(record["kind"] == kind and p["episode"] == episode, "event identity/order")
        if position is not None:
            require(p["position"] == position, "event position")
        return record

    for episode in range(2):
        state_payload = recorded_empty_b4_payload()
        formations = []
        for position, label in enumerate(FORMATIONS[episode]):
            image = take("image", episode, position)
            calibration.validate_image(image["payload"], PATTERNS[label], 0, position)
            image_count += 1
            formation = take("sequence_formation", episode, position)
            p = formation["payload"]
            offered = [0.0] * 8 + image["payload"]["frame"]["values"]
            require(p["owner"] == f"{RUN_ID}.episode.{episode}" and p["input_digest"] == image["digest"], "formation source")
            require(p["prestate"] == state_payload and p["prestate_digest"] == b4._digest(state_payload), "formation prestate")
            validate_formation_transition(p["prestate"], p["poststate"], tuple(offered), position+1,
                                           p["event"], p["native_cost"])
            require(p["formation_index"] == position+1 and p["offered"] == offered
                    and p["poststate_digest"] == b4._digest(p["poststate"])
                    and p["costs"] == FORMATION_COSTS, "formation result")
            state_payload = p["poststate"]
            formations.append(formation)
            formation_count += 1
        require(state_payload["accepted_count"] == 4, "final formation count")
        for probe_index, (labels, delta, expected_ordered) in enumerate(probe_recipe(episode)):
            images = []
            values = []
            for offset, label in enumerate(labels):
                position = 4 + probe_index*4 + offset
                image = take("image", episode, position)
                calibration.validate_image(image["payload"], PATTERNS[label], delta, position)
                images.append(image)
                values.append([0.0]*8 + image["payload"]["frame"]["values"])
                image_count += 1
            record = take("sequence_probe", episode)
            p = record["payload"]
            require(p["probe_index"] == probe_index and p["delta"] == delta
                    and p["probe_labels"] == list(labels) and p["expected_ordered"] is expected_ordered, "probe recipe")
            require(p["input_digests"] == [item["digest"] for item in images]
                    and p["formation_digests"] == [item["digest"] for item in formations]
                    and p["owner"] == f"{RUN_ID}.episode.{episode}", "probe sources")
            require(p["probes"] == values and p["state_digest"] == b4._digest(state_payload), "probe values/state")
            expected_finding = _recorded_finding(state_payload, values)
            require(p["finding"] == expected_finding, "recorded sequence finding")
            original = tuple(tuple(entry["values"]) for entry in sorted(
                (entry for entry in state_payload["entries"] if entry["occupied"]),
                key=lambda entry: entry["formation_index"]))
            returned = expected_finding["ordered"]["returned"]
            require(p["ordered_score"] == score(expected_ordered,
                expected_finding["ordered"]["recognized"], returned is None or tuple(map(tuple, returned)) == original),
                "ordered score")
            require(p["blind_score"] == score(True, True, True), "blind score")
            probes.append({**p, "episode": episode})
    require(next(pairs, None) is None and len(records) == 152, "event scope")
    require(image_count == 56 and formation_count == 8 and len(probes) == 12, "scope counts")
    ordered_counts = dict(Counter(p["ordered_score"]["classification"] for p in probes))
    blind_counts = dict(Counter(p["blind_score"]["classification"] for p in probes))
    by_delta = {str(delta): {
        "GEORDNET": dict(Counter(p["ordered_score"]["classification"] for p in probes if p["delta"] == delta)),
        "REIHENFOLGEBLIND": dict(Counter(p["blind_score"]["classification"] for p in probes if p["delta"] == delta))}
        for delta in (0, -8, 8)}
    return {"counts": {"image_analyses": 56, "b4_formations": 8,
            "sequence_probes": 12, "read_only_view_decisions": 24},
        "ordered_classifications": ordered_counts, "order_blind_classifications": blind_counts,
        "by_delta": by_delta, "ordered_sequence_function_valid": ordered_counts == {
            "CORRECT_RECOGNITION": 6, "CORRECT_REJECTION": 6},
        "order_blind_diagnostic_expected": blind_counts == {"CORRECT_RECOGNITION": 12},
        "receptor_order_preserved": True, "formation_chronology_preserved": True,
        "all_probe_states_unchanged": True, "returned_value_errors": 0,
        "costs": {"functional_write_words": 232, "functional_l1_terms": 4992,
                  "validation_l1_terms": 4992, "capacity_slots_per_bank": 9,
                  "occupied_slots_per_bank": 4, "resource_word_limit_per_bank": 255,
                  "per_sequence": SEQUENCE_COSTS,
                  "record_validation_and_io": "SEPARATE_FROM_FUNCTIONAL_COUNTS"}}


def verify_result(directory):
    try:
        directory = Path(directory)
        require(not (directory / "failure.json").exists(), "recorded failure")
        manifest = spatial.read_sealed(directory / "manifest.json", "sequence_manifest")
        result = spatial.read_sealed(directory / "result.json", "sequence_result")
        terminal = spatial.read_sealed(directory / "terminal.json", "sequence_terminal")
        m = manifest["payload"]
        require(m["run_id"] == RUN_ID and m["patterns"] == b4._canonical(PATTERNS)
                and m["formations"] == b4._canonical(FORMATIONS)
                and m["expected_counts"] == [56, 8, 12, 24], "manifest scope")
        require(m["threshold"] == {"numerator": 44, "denominator": 765,
                "value": VISUAL_THRESHOLD, "learned": False}, "threshold binding")
        for item in m["source"]["sources"]:
            require(spatial.raw_hash(base64.b64decode(item["bytes_base64"], validate=True)) == item["sha256"], "archived source")
        require(result["payload"]["manifest_digest"] == manifest["digest"], "manifest digest")
        require(result["payload"]["journal_sha256"] == spatial.raw_hash((directory/"events.jsonl").read_bytes()), "journal hash")
        require(result["payload"]["summary"] == inspect_records(spatial.read_records(directory)), "summary mismatch")
        require(result["payload"]["errors"] == [], "errors present")
        require(terminal["payload"] == {"result_digest": result["digest"], "exit_code": 0, "status": "OK"}, "terminal")
        return {"recording_status": "COMPLETE", "result_digest": result["digest"],
                "summary": result["payload"]["summary"]}
    except Exception as exc:
        return {"recording_status": "NOT_EVALUABLE", "error": str(exc)}


def run_once():
    require(_RUN_RELEASE_ENABLED, "sequence attempt closed")
    require(not calibration._RUN_RELEASE_ENABLED and not spatial._RUN_RELEASE_ENABLED
            and not b4._EXECUTION_RELEASE_ENABLED, "old entry opened")
    qualification = spatial.read_sealed(BASE/QUALIFICATION_ID/"result.json", "sequence_validator_qualification")
    q = qualification["payload"]
    require(q["successful"] and q["test_count"] == 1 and q["exit_code"] == 0, "qualification incomplete")
    require(q["completion_receipt"]["recording_status"] == "COMPLETE", "validator completion incomplete")
    require(not any(q["guard_calls"].values()), "validator called excluded functions")
    require(q["output_sha256"] == spatial.raw_hash((BASE/QUALIFICATION_ID/"output.txt").read_bytes()), "qualification transcript")
    for item in q["source"]["sources"]:
        require(spatial.raw_hash(base64.b64decode(item["bytes_base64"], validate=True))
                == item["sha256"], "validator archived source")
    source = source_manifest()
    journal = spatial.Journal(BASE/RUN_ID)
    started = time.perf_counter()
    try:
        manifest = seal("sequence_manifest", {"run_id": RUN_ID, "source": source,
            "qualification_digest": qualification["digest"], "patterns": PATTERNS,
            "formations": FORMATIONS, "probe_recipes": (probe_recipe(0), probe_recipe(1)),
            "threshold": {"numerator": 44, "denominator": 765,
                          "value": VISUAL_THRESHOLD, "learned": False},
            "authorization": (ROOT/AUTHORIZATION).read_text(encoding="utf-8"),
            "expected_counts": [56, 8, 12, 24], "capacity": 9,
            "retry_policy": "NO_RETRY_OR_RESUME"})
        spatial._write_new(journal.directory/"manifest.json", manifest)
        for episode in range(2):
            state = spatial.fresh_state()
            formations = []
            for position, label in enumerate(FORMATIONS[episode]):
                frame, image = image_record(journal, episode, position, label, 0, "formation", None)
                state, formation = form_record(journal, episode, position, frame, image, state)
                formations.append(formation)
            require(state.accepted_count == 4, "incomplete live formation")
            for probe_index, (labels, delta, expected_ordered) in enumerate(probe_recipe(episode)):
                frames, images = [], []
                for offset, label in enumerate(labels):
                    position = 4 + probe_index*4 + offset
                    frame, image = image_record(journal, episode, position, label, delta, "probe", probe_index)
                    frames.append(frame)
                    images.append(image)
                sequence_probe_record(journal, episode, probe_index, delta, labels, expected_ordered,
                                      tuple(frames), tuple(images), state, tuple(formations))
        journal.close()
        spatial.check_sources(source)
        summary = inspect_records(spatial.read_records(journal.directory))
        result = seal("sequence_result", {"manifest_digest": manifest["digest"], "summary": summary,
            "journal_sha256": spatial.raw_hash(journal.path.read_bytes()), "errors": [],
            "elapsed_seconds": time.perf_counter()-started, "process_memory_status": "NOT_MEASURED"})
        spatial._publish(journal.directory/"result.json", result)
        spatial._publish(journal.directory/"terminal.json", seal("sequence_terminal", {
            "result_digest": result["digest"], "exit_code": 0, "status": "OK"}))
        checked = verify_result(journal.directory)
        require(checked["recording_status"] == "COMPLETE", str(checked))
        return checked
    except BaseException as exc:
        journal.close()
        spatial._write_new(journal.directory/"failure.json", seal("sequence_failure", {
            "recording_status": "NOT_EVALUABLE", "error_type": type(exc).__name__,
            "error": str(exc), "traceback": traceback.format_exc(), "recorded_events": journal.index}))
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-once", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    require(bool(args.run_once) != bool(args.verify), "choose run OR record verification")
    finding = run_once() if args.run_once else verify_result(args.verify)
    print(json.dumps(finding, sort_keys=True))
    raise SystemExit(0 if finding["recording_status"] == "COMPLETE" else 1)
