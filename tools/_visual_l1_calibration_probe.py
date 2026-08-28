"""Private fixed-threshold confirmation; no field or legacy runner entry."""

from __future__ import annotations

import argparse
import base64
from collections import Counter
from fractions import Fraction
import json
import math
from pathlib import Path
import time
import traceback

from tools import _visual_spatial_memory_probe as spatial


ROOT, BASE, b4 = spatial.ROOT, spatial.BASE, spatial.b4
require, seal = spatial.require, spatial.seal
RUN_ID = "calibration-20260828-01"
QUALIFICATION_ID = "calibration-qualification-20260828-01"
PLAN = "docs/VISUELLE_L1_KALIBRIERUNG_UND_BESTAETIGUNGSPLAN.md"
AUTHORIZATION = f"reports/tspm1_functional/{RUN_ID}.authorization.txt"
DEVELOPMENT = BASE / "spatial-20260828-01"
RULES = ("L1-ALT", "L1-KAL")
CALIBRATED = Fraction(44, 765)
_RUN_RELEASE_ENABLED = False
SETS = (
    ("K1", (32, 96, 32, 96, 32, 96), (0, 1), 64),
    ("K2", (52, 148, 148, 52, 148, 52), (2, 5), 96),
    ("K3", (204, 44, 204, 44, 204, 44), (2, 3), 160),
    ("G1", (104, 128, 104, 128, 128, 104), (2, 4), 24),
)


def calibration_from_development(rows):
    """No confirmation argument: only recorded development distances enter here."""
    require(len(rows) == 24, "development count")
    positives = [r["distances"][1] for r in rows if r["score"]["expected_recognized"]]
    negatives = [r["distances"][1] for r in rows if not r["score"]["expected_recognized"]]
    require(len(positives) == len(negatives) == 12, "development classes")
    require(all(math.isfinite(x) and 0 <= x <= 1 for x in positives + negatives), "development values")
    require(abs(max(positives) - 8 / 255) <= 1e-12, "development positive bound")
    require(abs(min(negatives) - 128 / 765) <= 1e-12, "development negative bound")
    upper = Fraction(8, 255)
    lower = min(Fraction(128, 765), Fraction(64, 765))
    require(upper < lower and (upper + lower) / 2 == CALIBRATED, "calibration interval")
    return {"method": "DEVELOPMENT_AND_TASK_BOUND_MIDPOINT_NOT_LEARNED",
            "development_count": 24, "observed_positive_max": max(positives),
            "observed_negative_min": min(negatives), "minimum_swap_contrast": 64,
            "threshold_numerator": 44, "threshold_denominator": 765,
            "visual_threshold": float(CALIBRATED), "auditory_threshold": 0.2,
            "acceptance": "distance <= threshold", "confirmation_used": False}


def load_development():
    checked = spatial.verify_result(DEVELOPMENT)
    require(checked["recording_status"] == "COMPLETE", "development recording")
    rows = [r["payload"] for r in spatial.read_records(DEVELOPMENT)
            if r["kind"] == "probe" and r["payload"]["condition"] == "B4_SPATIAL"]
    return {"calibration": calibration_from_development(rows),
            "result_digest": checked["result_digest"],
            "files": [{"path": (DEVELOPMENT / name).relative_to(ROOT).as_posix(),
                       "sha256": spatial.raw_hash((DEVELOPMENT / name).read_bytes())}
                      for name in ("manifest.json", "events.jsonl", "result.json", "terminal.json")]}


def source_manifest():
    source = spatial.source_manifest()
    existing = {item["path"] for item in source["sources"]}
    for relative in (PLAN, AUTHORIZATION, "tools/_visual_l1_calibration_probe.py",
                     "tests/test_visual_l1_calibration_probe.py"):
        if relative not in existing:
            raw = (ROOT / relative).read_bytes()
            source["sources"].append({"path": relative, "sha256": spatial.raw_hash(raw),
                "bytes_base64": base64.b64encode(raw).decode("ascii")})
    source["sources"].sort(key=lambda item: item["path"])
    return source


def calibrated_probe(slots, values, visual_threshold):
    require(type(visual_threshold) is float and visual_threshold in (0.2, float(CALIBRATED)),
            "only exact bound thresholds")
    candidates = []
    for slot_id, stored, rank_step in slots:
        auditory = b4.normalized_mean_l1_distance(values[:8], stored[:8])
        visual = b4.normalized_mean_l1_distance(values[8:], stored[8:])
        if auditory <= 0.2 and visual <= visual_threshold:
            candidates.append((max(auditory, visual), auditory + visual, -rank_step,
                               slot_id, stored, auditory, visual))
    return min(candidates, default=None)


def recipe(episode):
    name, first, swap, contrast = SETS[episode // 2]
    second = list(first)
    second[swap[0]], second[swap[1]] = second[swap[1]], second[swap[0]]
    stored, other = (first, tuple(second)) if episode % 2 == 0 else (tuple(second), first)
    return name, contrast, ((stored, 0, True), (stored, 0, True), (other, 0, False),
        (stored, -8, True), (other, -8, False), (stored, 8, True), (other, 8, False))


def image_facts(cells, delta):
    values = tuple(v + delta for v in cells)
    require(len(values) == 6 and all(type(v) is int and 0 <= v <= 255 for v in values), "image domain")
    raw = b"".join(b"".join(bytes((value,)) * 120 for value in values[row:row+3]) * 40
                   for row in (0, 3))
    return {"input_sha256": spatial.raw_hash(raw),
            "histogram": {str(v): n * 1600 for v, n in sorted(Counter(values).items())},
            "expected_visual": tuple(v / 255 for v in values for _ in range(3)),
            "expected_global_mean": sum(values) / (6 * 255)}


IMAGE_COSTS = {"image_bytes": 28800, "receptor_channel_samples": 28800,
               "global_control_channel_samples": 28800, "histogram_channel_samples": 28800,
               "position_validation_terms": 18}
FORMATION_COSTS = {"functional_write_words": 29, "functional_l1_terms": 0,
                   "validation_l1_terms": 0, "stored_value_equality_checks": 26,
                   "resource_word_limit": 255, "capacity_slots": 9,
                   "initialized_slots": 9, "write_limit": 293, "l1_limit": 234}
PROBE_COSTS = {"functional_write_words": 0, "functional_l1_terms": 26,
               "validation_l1_terms": 26, "state_value_equality_checks": 26,
               "resource_word_limit": 255, "write_limit": 293, "l1_limit": 234}


def analyze(journal, episode, position, cells, delta):
    context = {"episode": episode, "position": position, "cells": cells, "delta": delta}
    journal.emit("image_start", context)
    values = spatial.np.array(cells, dtype=spatial.np.int16).reshape(2, 3) + delta
    require(bool(((values >= 0) & (values <= 255)).all()), "clipping")
    image = spatial.np.repeat(spatial.np.repeat(values.astype(spatial.np.uint8), 40, axis=0), 40, axis=1)
    image = spatial.np.repeat(image[:, :, None], 3, axis=2)
    image.setflags(write=False)
    facts = image_facts(cells, delta)
    require(spatial.raw_hash(image.tobytes()) == facts["input_sha256"], "image construction")
    receptor = spatial.LocalChannelGridReceptor(spatial.CONFIG).analyze(image, frame_index=position)
    frame = spatial.from_visual_receptor_state(receptor)
    means = spatial.global_channel_mean_baseline(image, spatial.CONFIG)
    histogram = []
    for channel in range(3):
        unique, counts = spatial.np.unique(image[:, :, channel], return_counts=True)
        histogram.append({str(int(v)): int(n) for v, n in zip(unique, counts, strict=True)})
    payload = {**context, "input_sha256": spatial.raw_hash(image.tobytes()),
        "histograms": histogram, "receptor": b4._canonical(receptor),
        "frame": b4._canonical(frame), "global_means": means, "costs": IMAGE_COSTS}
    validate_image(b4._canonical(payload), cells, delta, position)
    record = journal.emit("image", payload)
    return frame, record


def validate_image(p, cells, delta, position):
    facts = image_facts(cells, delta)
    require(p["cells"] == list(cells) and p["delta"] == delta and p["position"] == position, "image recipe")
    require(p["input_sha256"] == facts["input_sha256"], "image bytes")
    require(p["histograms"] == [facts["histogram"]] * 3, "image histogram")
    f = p["frame"]
    require(f["modality_id"] == "visual" and f["geometry_id"] == spatial.CONFIG.geometry_id
            and f["carrier_ids"] == list(spatial.CONFIG.carrier_ids), "frame geometry")
    require(f["values"] == p["receptor"]["channel_values"], "frame transfer")
    require(max(abs(x-y) for x,y in zip(spatial._values(f["values"], 18), facts["expected_visual"], strict=True))
            <= 1e-12, "receptor spatial values")
    require(len(p["global_means"]) == 3 and all(abs(x-facts["expected_global_mean"]) <= 1e-12
            for x in p["global_means"]), "global mean")
    require(p["costs"] == IMAGE_COSTS, "image costs")


def form(journal, episode, frame, image_record):
    initial = spatial.fresh_state()
    before = spatial.state_payload(initial)
    offered = spatial.frame_to_b4(frame, "B4_SPATIAL")
    context = {"episode": episode, "owner": f"{RUN_ID}.episode.{episode}",
               "input_digest": image_record["digest"], "prestate": before}
    journal.emit("formation_start", context)
    state, event, native_cost = b4._advance_b4(initial, offered, 1)
    after = spatial.state_payload(state)
    require(spatial.state_payload(initial) == before, "initial state mutated")
    spatial.validate_storage(after, offered)
    record = journal.emit("formation", {**context, "offered": offered, "poststate": after,
        "state_digest": b4._digest(after), "event": event, "native_cost": native_cost,
        "costs": FORMATION_COSTS})
    return state, record


def recorded_distances(offered, original):
    return [math.fsum(abs(x-y) for x,y in zip(offered[:8], original[:8], strict=True)) / 8,
            math.fsum(abs(x-y) for x,y in zip(offered[8:], original[8:], strict=True)) / 18]


def validate_probe(p, image_record, formation, rule, expected_same):
    """Record-only arithmetic: no retrieval or formation operator is called."""
    before = formation["payload"]["poststate"]
    original = formation["payload"]["offered"]
    offered = [0.0] * 8 + image_record["payload"]["frame"]["values"]
    require(p["rule"] == rule and p["owner"] == formation["payload"]["owner"], "probe owner/rule")
    require(p["input_digest"] == image_record["digest"] and p["formation_digest"] == formation["digest"], "probe source")
    require(p["offered"] == offered, "probe values")
    require(p["prestate"] == p["poststate"] == before, "probe changed state")
    require(p["state_digest"] == b4._digest(before), "probe state identity")
    distances = recorded_distances(offered, original)
    threshold = 0.2 if rule == "L1-ALT" else float(CALIBRATED)
    require(p["visual_threshold"] == threshold and p["auditory_threshold"] == 0.2, "threshold identity")
    require(p["distances"] == distances, "distance identity")
    recognized = distances[0] <= 0.2 and distances[1] <= threshold
    selected = [max(distances), sum(distances), -1, "b4.slot.000", original, *distances] if recognized else None
    require(p["recognized"] is recognized and p["selected"] == selected, "selection rule")
    # A wrong returned value is retained as a functional error, not hidden by an exception.
    require(p["score"] == spatial.score(expected_same, recognized, p["returned"], original), "score identity")
    require(p["costs"] == PROBE_COSTS, "probe cost")


def probe(journal, episode, position, frame, image_record, state, formation, rule, expected_same):
    offered = spatial.frame_to_b4(frame, "B4_SPATIAL")
    before = spatial.state_payload(state)
    slots = tuple((entry.slot_id, entry.values, entry.formation_index) for entry in state.entries if entry.occupied)
    require(len(slots) == 1, "one stored entry")
    threshold = 0.2 if rule == "L1-ALT" else float(CALIBRATED)
    context = {"episode": episode, "position": position, "rule": rule,
        "owner": formation["payload"]["owner"], "input_digest": image_record["digest"],
        "formation_digest": formation["digest"], "state_digest": b4._digest(before)}
    journal.emit("probe_start", context)
    selected = b4._probe_joint_slots(slots, offered) if rule == "L1-ALT" else calibrated_probe(slots, offered, threshold)
    after = spatial.state_payload(state)
    require(before == after, "state mutation")
    payload = {**context, "offered": offered, "prestate": before, "poststate": after,
        "visual_threshold": threshold, "auditory_threshold": 0.2,
        "distances": recorded_distances(offered, slots[0][1]), "selected": selected,
        "recognized": selected is not None, "returned": selected[4] if selected else None,
        "score": spatial.score(expected_same, selected is not None, selected[4] if selected else None, slots[0][1]),
        "costs": PROBE_COSTS}
    journal.emit("probe", payload)


def checked_pairs(records):
    previous = None
    for index, record in enumerate(records):
        require(record == seal(record["kind"], record["payload"]), "event digest")
        require(record["payload"]["index"] == index and record["payload"]["previous"] == previous, "event chain")
        previous = record["digest"]
    require(len(records) % 2 == 0, "unfinished event")
    pairs = []
    for start, end in zip(records[::2], records[1::2], strict=True):
        require(start["kind"] == end["kind"] + "_start", "call completion")
        require(all(end["payload"].get(k) == v for k,v in start["payload"].items()
                    if k not in ("index", "previous")), "call/result identity")
        pairs.append(end)
    return iter(pairs)


def summarize(rows):
    results = {}
    for group, names in (("PRIMARY", ("K1", "K2", "K3")), ("G1_DIAGNOSTIC", ("G1",))):
        results[group] = {}
        for rule in RULES:
            selected = [p for p in rows if p["set"] in names and p["rule"] == rule]
            results[group][rule] = {
                "count": len(selected),
                "classifications": dict(Counter(p["score"]["classification"] for p in selected)),
                "by_set": {name: dict(Counter(p["score"]["classification"] for p in selected if p["set"] == name))
                           for name in names},
                "by_delta": {str(delta): dict(Counter(p["score"]["classification"] for p in selected if p["delta"] == delta))
                             for delta in (0, -8, 8)},
                "returned_value_errors": sum(not p["score"]["returned_values_correct"] for p in selected),
            }
    primary = [p for p in rows if p["set"] != "G1" and p["rule"] == "L1-KAL"]
    upper = max(p["distances"][1] for p in primary if p["score"]["expected_recognized"])
    lower = min(p["distances"][1] for p in primary if not p["score"]["expected_recognized"])
    return {"counts": {"image_analyses": 56, "b4_formations": 8, "probe_inputs": 48, "rule_calls": 96},
        "results": results, "primary_calibration_sufficient": all(p["score"]["classification"] in
            ("CORRECT_RECOGNITION", "CORRECT_REJECTION") for p in primary),
        "diagnostic_only_interval": {"inclusive_lower": upper, "exclusive_upper": lower,
            "robust_nonempty": lower-upper > 1e-12, "no_new_threshold_selected": True},
        "receptor_and_storage_preserved": True, "all_probe_states_unchanged": True,
        "costs": {"functional_write_words": 232, "functional_l1_terms": 2496,
                  "validation_l1_terms": 2496, "capacity_slots_per_bank": 9,
                  "occupied_slots_per_bank": 1, "resource_words_limit_per_bank": 255,
                  "image_costs_per_analysis": IMAGE_COSTS,
                  "record_validation_and_io": "SEPARATE_FROM_FUNCTIONAL_COUNTS"}}


def inspect_records(records):
    pairs = checked_pairs(records)
    rows = []

    def take(kind, episode, position=None):
        record = next(pairs)
        require(record["kind"] == kind and record["payload"]["episode"] == episode, "event order/episode")
        if position is not None:
            require(record["payload"]["position"] == position, "event position")
        return record

    for episode in range(8):
        name, contrast, inputs = recipe(episode)
        for position, (cells, delta, same) in enumerate(inputs):
            image_record = take("image", episode, position)
            validate_image(image_record["payload"], cells, delta, position)
            if position == 0:
                formation = take("formation", episode)
                p = formation["payload"]
                offered = [0.0] * 8 + image_record["payload"]["frame"]["values"]
                require(p["owner"] == f"{RUN_ID}.episode.{episode}" and p["input_digest"] == image_record["digest"], "formation owner/source")
                require(p["prestate"] == spatial.empty_payload() and p["offered"] == offered, "fresh formation")
                spatial.validate_storage(p["poststate"], offered)
                require(p["state_digest"] == b4._digest(p["poststate"]), "formation digest")
                require(p["event"] == {"event": "B4_APPENDED", "slot_id": "b4.slot.000"}
                        and p["native_cost"] == [27, 0] and p["costs"] == FORMATION_COSTS, "formation receipt")
            else:
                for rule in RULES:
                    record = take("probe", episode, position)
                    p = record["payload"]
                    validate_probe(p, image_record, formation, rule, same)
                    rows.append({**p, "set": name, "contrast": contrast, "delta": delta})
    require(next(pairs, None) is None and len(records) == 320 and len(rows) == 96, "scope mismatch")
    return summarize(rows)


def verify_result(directory):
    try:
        directory = Path(directory)
        require(not (directory / "failure.json").exists(), "recorded failure")
        manifest = spatial.read_sealed(directory / "manifest.json", "calibration_manifest")
        result = spatial.read_sealed(directory / "result.json", "calibration_result")
        terminal = spatial.read_sealed(directory / "terminal.json", "calibration_terminal")
        m = manifest["payload"]
        require(m["run_id"] == RUN_ID and m["sets"] == b4._canonical(SETS)
                and m["rules"] == list(RULES) and m["expected_counts"] == [56, 8, 48, 96], "manifest scope")
        require(m["development"] == load_development(), "development binding")
        require(m["calibration"] == m["development"]["calibration"], "calibration binding")
        for item in m["source"]["sources"]:
            require(spatial.raw_hash(base64.b64decode(item["bytes_base64"], validate=True)) == item["sha256"], "archived source digest")
        result_payload = result["payload"]
        require(result_payload["manifest_digest"] == manifest["digest"], "manifest digest")
        require(result_payload["journal_sha256"] == spatial.raw_hash((directory / "events.jsonl").read_bytes()), "journal hash")
        require(result_payload["summary"] == inspect_records(spatial.read_records(directory)), "summary identity")
        require(result_payload["errors"] == [], "errors present")
        require(terminal["payload"] == {"result_digest": result["digest"], "exit_code": 0, "status": "OK"}, "terminal")
        return {"recording_status": "COMPLETE", "result_digest": result["digest"], "summary": result_payload["summary"]}
    except Exception as exc:
        return {"recording_status": "NOT_EVALUABLE", "error": str(exc)}


def run_once():
    require(_RUN_RELEASE_ENABLED, "calibration attempt closed")
    require(not spatial._RUN_RELEASE_ENABLED and not b4._EXECUTION_RELEASE_ENABLED, "legacy entry opened")
    qualification = spatial.read_sealed(BASE / QUALIFICATION_ID / "result.json", "calibration_qualification")
    q = qualification["payload"]
    require(q["successful"] and q["test_count"] == 8 and q["exit_code"] == 0, "qualification incomplete")
    require(q["output_sha256"] == spatial.raw_hash((BASE / QUALIFICATION_ID / "output.txt").read_bytes()), "test transcript")
    spatial.check_sources(q["source"])
    development = load_development()
    source = source_manifest()
    journal = spatial.Journal(BASE / RUN_ID)
    started = time.perf_counter()
    try:
        manifest = seal("calibration_manifest", {"run_id": RUN_ID, "source": source,
            "qualification_digest": qualification["digest"], "development": development,
            "calibration": development["calibration"], "sets": SETS, "rules": RULES,
            "authorization": (ROOT / AUTHORIZATION).read_text(encoding="utf-8"),
            "expected_counts": [56, 8, 48, 96], "capacity": 9, "retry_policy": "NO_RETRY_OR_RESUME"})
        spatial._write_new(journal.directory / "manifest.json", manifest)
        for episode in range(8):
            _, _, inputs = recipe(episode)
            for position, (cells, delta, same) in enumerate(inputs):
                frame, image_record = analyze(journal, episode, position, cells, delta)
                if position == 0:
                    state, formation = form(journal, episode, frame, image_record)
                else:
                    for rule in RULES:
                        probe(journal, episode, position, frame, image_record, state, formation, rule, same)
        journal.close()
        spatial.check_sources(source)
        summary = inspect_records(spatial.read_records(journal.directory))
        result = seal("calibration_result", {"manifest_digest": manifest["digest"], "summary": summary,
            "journal_sha256": spatial.raw_hash(journal.path.read_bytes()), "errors": [],
            "elapsed_seconds": time.perf_counter()-started, "process_memory_status": "NOT_MEASURED"})
        spatial._publish(journal.directory / "result.json", result)
        spatial._publish(journal.directory / "terminal.json", seal("calibration_terminal", {
            "result_digest": result["digest"], "exit_code": 0, "status": "OK"}))
        checked = verify_result(journal.directory)
        require(checked["recording_status"] == "COMPLETE", str(checked))
        return checked
    except BaseException as exc:
        journal.close()
        spatial._write_new(journal.directory / "failure.json", seal("calibration_failure", {
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
