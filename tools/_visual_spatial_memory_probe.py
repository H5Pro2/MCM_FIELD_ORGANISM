"""Private, one-shot spatial receptor/B4 experiment; no field integration."""

from __future__ import annotations

import argparse
import base64
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import traceback

import numpy as np

from mcm_field_organism import _tspm1_s2dr_private_comparison as b4
from mcm_field_organism.finite_video_path import (
    LocalChannelGridReceptor, VisualGridConfig, global_channel_mean_baseline,
)
from mcm_field_organism.receptor_contract import ReceptorContactFrame, from_visual_receptor_state
from tools._tspm1_functional_study import _publish, _write_new


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "reports/tspm1_functional"
RUN_ID = "spatial-20260828-01"
QUALIFICATION_ID = "spatial-qualification-20260828-01"
PLAN = "docs/VISUELLE_ORTSSTRUKTUR_AUFGABEN_UND_PRUEFPLAN.md"
_RUN_RELEASE_ENABLED = False
CONFIG = VisualGridConfig(120, 80, 3, 2, 30.0)
PATTERNS = {"A": (64, 64, 64, 192, 192, 192),
            "B": (192, 192, 192, 64, 64, 64),
            "C": (192, 64, 64, 64, 192, 192)}
EPISODES = (("A", "B"), ("B", "A"), ("A", "C"), ("C", "A"))
CONDITIONS = ("B4_SPATIAL", "B4_NO_LOCATION")
SCHEMA = "visual.spatial.b4.private.v1"


class SpatialError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise SpatialError(message)


def raw_hash(raw):
    return hashlib.sha256(raw).hexdigest()


def seal(kind, payload):
    body = {"schema": SCHEMA, "kind": kind, "payload": b4._canonical(payload)}
    return {**body, "digest": b4._digest(body)}


def read_sealed(path, kind):
    value = json.loads(Path(path).read_bytes())
    require(set(value) == {"schema", "kind", "payload", "digest"}, "record shape")
    require(value["schema"] == SCHEMA and value["kind"] == kind, "record identity")
    require(value["digest"] == b4._digest({k: v for k, v in value.items() if k != "digest"}),
            "record digest")
    return value


def source_manifest():
    paths = {PLAN, "tools/_visual_spatial_memory_probe.py",
             "tests/test_visual_spatial_memory_probe.py", "tests/test_finite_video_path.py",
             "tests/test_ppb1_receptor_profiles.py"}
    dependencies = []
    for name, module in sorted(sys.modules.copy().items()):
        filename = getattr(module, "__file__", None)
        if not filename or not Path(filename).is_file():
            continue
        path = Path(filename).resolve()
        if path.is_relative_to(ROOT):
            paths.add(path.relative_to(ROOT).as_posix())
        else:
            dependencies.append({"module": name, "path": str(path),
                                 "sha256": raw_hash(path.read_bytes())})
    sources = []
    for path in sorted(paths):
        raw = (ROOT / path).read_bytes()
        sources.append({"path": path, "sha256": raw_hash(raw),
                        "bytes_base64": base64.b64encode(raw).decode("ascii")})
    return {"sources": sources, "runtime": {"executable": sys.executable,
            "sha256": raw_hash(Path(sys.executable).read_bytes()), "version": sys.version,
            "numpy_version": np.__version__, "dependencies": dependencies}}


def check_sources(source):
    for item in source["sources"]:
        require(raw_hash(base64.b64decode(item["bytes_base64"], validate=True))
                == item["sha256"] == raw_hash((ROOT / item["path"]).read_bytes()),
                "source changed: " + item["path"])


def _values(values, length):
    require(type(values) in (list, tuple) and len(values) == length, "value dimension")
    require(all(type(x) in (int, float) and math.isfinite(x) and 0 <= x <= 1 for x in values),
            "finite normalized values required")
    return tuple(float(x) for x in values)


def project_values(values, condition):
    visual = _values(values, 18)
    require(condition in CONDITIONS, "condition")
    if condition == "B4_NO_LOCATION":
        means = tuple(math.fsum(visual[channel::3]) / 6 for channel in range(3))
        visual = means * 6
    return (0.0,) * 8 + visual


def frame_to_b4(frame, condition):
    require(type(frame) is ReceptorContactFrame, "exact receptor frame required")
    require(frame.modality_id == "visual" and frame.geometry_id == CONFIG.geometry_id,
            "foreign frame geometry")
    require(frame.carrier_ids == CONFIG.carrier_ids, "foreign or reordered carriers")
    return project_values(frame.values, condition)


def fresh_state():
    return b4._B4State(0, tuple(b4._FIFOEntry(f"b4.slot.{i:03d}", False, (), None)
                              for i in range(9)))


def empty_payload():
    return {"accepted_count": 0, "entries": [
        {"slot_id": f"b4.slot.{i:03d}", "occupied": False, "values": [],
         "formation_index": None} for i in range(9)]}


def state_payload(state):
    require(type(state) is b4._B4State, "B4 state type")
    payload = b4._canonical(state)
    require(len(payload["entries"]) == 9, "B4 capacity")
    for i, entry in enumerate(payload["entries"]):
        require(entry["slot_id"] == f"b4.slot.{i:03d}", "B4 slot identity")
        if entry["occupied"]:
            _values(entry["values"], 26)
        else:
            require(entry["values"] == [] and entry["formation_index"] is None, "empty slot")
    return payload


def validate_storage(payload, offered):
    expected = empty_payload()
    expected["accepted_count"] = 1
    expected["entries"][0].update(occupied=True, values=list(offered), formation_index=1)
    require(payload == expected, "stored values or state metadata changed")


def score(expected_recognized, recognized, selected, original):
    returned_correct = not recognized or selected == original
    if not returned_correct:
        label = "WRONG_RETURNED_VALUES"
    elif recognized and not expected_recognized:
        label = "FALSE_EQUIVALENCE"
    elif not recognized and expected_recognized:
        label = "FALSE_REJECTION"
    else:
        label = "CORRECT_RECOGNITION" if recognized else "CORRECT_REJECTION"
    return {"expected_recognized": expected_recognized, "classification": label,
            "returned_values_correct": returned_correct}


def expected_visual(pattern, delta):
    return tuple((value + delta) / 255.0 for value in PATTERNS[pattern] for _ in range(3))


def episode_recipe(stored, other):
    return ((stored, 0, "formation"), (stored, 0, "probe"), (other, 0, "probe"),
            (stored, -8, "probe"), (other, -8, "probe"),
            (stored, 8, "probe"), (other, 8, "probe"))


class Journal:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(exist_ok=False)
        self.path = self.directory / "events.jsonl"
        self.handle = self.path.open("xb")
        self.index = 0
        self.previous = None

    def emit(self, kind, payload):
        record = seal(kind, {"index": self.index, "previous": self.previous, **payload})
        raw = b4._json_bytes(record) + b"\n"
        require(self.handle.write(raw) == len(raw), "short journal write")
        self.handle.flush()
        import os
        os.fsync(self.handle.fileno())
        self.index += 1
        self.previous = record["digest"]
        return record

    def close(self):
        self.handle.close()


def analyze_input(journal, episode, position, pattern, delta, role):
    identity = {"episode": episode, "position": position, "pattern": pattern,
                "delta": delta, "role": role}
    journal.emit("image_start", identity)
    cells = np.array(PATTERNS[pattern], dtype=np.uint8).reshape(2, 3)
    cells = (cells.astype(np.int16) + delta).astype(np.uint8)
    image = np.repeat(np.repeat(cells, 40, axis=0), 40, axis=1)
    image = np.repeat(image[:, :, None], 3, axis=2)
    image.setflags(write=False)
    input_hash = raw_hash(image.tobytes())
    receptor = LocalChannelGridReceptor(CONFIG).analyze(image, frame_index=position)
    frame = from_visual_receptor_state(receptor)
    means = global_channel_mean_baseline(image, CONFIG)
    expected = expected_visual(pattern, delta)
    error = max(abs(x - y) for x, y in zip(frame.values, expected, strict=True))
    require(error <= 1e-12, "receptor position values lost or changed")
    require(tuple(receptor.channel_values) == frame.values, "frame conversion changed values")
    require(input_hash == raw_hash(image.tobytes()), "image mutated during reduction")
    require(all(abs(x - (128 + delta) / 255.0) <= 1e-12 for x in means), "global means")
    pooled = frame_to_b4(frame, "B4_NO_LOCATION")[8:11]
    require(all(abs(x-y) <= 1e-12 for x,y in zip(pooled, means, strict=True)), "control reduction mismatch")
    record = journal.emit("image", {**identity, "input_sha256": input_hash,
        "pixel_histogram_per_channel": {str(64 + delta): 4800, str(192 + delta): 4800},
        "receptor": b4._canonical(receptor), "frame": b4._canonical(frame),
        "global_means": means, "max_position_error": error,
        "costs": {"image_bytes": image.nbytes, "receptor_channel_samples": image.size,
                  "global_control_channel_samples": image.size, "position_validation_terms": 18,
                  "control_validation_sum_inputs": 18, "control_validation_mean_divisions": 3}})
    return frame, record["digest"], means


def form(journal, episode, condition, frame, input_digest):
    owner = f"{RUN_ID}.episode.{episode}.{condition}"
    offered = frame_to_b4(frame, condition)
    initial = fresh_state()
    before = state_payload(initial)
    journal.emit("formation_start", {"episode": episode, "condition": condition,
        "owner": owner, "input_digest": input_digest, "prestate": before})
    post, event, native_cost = b4._advance_b4(initial, offered, 1)
    after = state_payload(post)
    validate_storage(after, offered)
    record = journal.emit("formation", {"episode": episode, "condition": condition,
        "owner": owner, "input_digest": input_digest, "offered": offered,
        "prestate": before, "poststate": after, "state_digest": b4._digest(after),
        "event": event, "native_cost": native_cost,
        "projection_costs": projection_costs(condition),
        "costs": {"functional_write_words": 29, "functional_l1_terms": 0,
                  "validation_l1_terms": 0, "stored_value_equality_checks": 26,
                  "resource_word_limit": 255, "capacity_slots": 9,
                  "initialized_slots": 9}})
    return post, record["digest"]


def projection_costs(condition):
    return {"normalized_values_checked": 18,
            "control_sum_inputs": 18 if condition == "B4_NO_LOCATION" else 0,
            "control_mean_divisions": 3 if condition == "B4_NO_LOCATION" else 0}


def probe(journal, episode, position, condition, frame, input_digest, state,
          formation_digest, expected_recognized):
    offered = frame_to_b4(frame, condition)
    before = state_payload(state)
    entries = [(x.slot_id, x.values, x.formation_index) for x in state.entries if x.occupied]
    require(len(entries) == 1, "one formed slot required")
    original = entries[0][1]
    context = {"episode": episode, "position": position, "condition": condition,
        "owner": f"{RUN_ID}.episode.{episode}.{condition}",
        "input_digest": input_digest, "formation_digest": formation_digest}
    journal.emit("probe_start", {**context, "state_digest": b4._digest(before)})
    selected = b4._probe_joint_slots(entries, offered)
    after = state_payload(state)
    require(before == after, "probe mutated bank")
    distances = (math.fsum(abs(x - y) for x, y in zip(offered[:8], original[:8], strict=True)) / 8,
                 math.fsum(abs(x - y) for x, y in zip(offered[8:], original[8:], strict=True)) / 18)
    if selected is not None:
        require(selected[5:] == distances, "native and validation distances disagree")
        require(selected[3] == entries[0][0], "foreign selected slot")
    recognized = selected is not None
    returned = tuple(selected[4]) if recognized else None
    journal.emit("probe", {**context, "offered": offered, "prestate": before,
        "poststate": after, "prestate_digest": b4._digest(before),
        "poststate_digest": b4._digest(after), "distances": distances,
        "recognized": recognized, "native_selected": selected, "returned": returned,
        "score": score(expected_recognized, recognized, returned, original),
        "projection_costs": projection_costs(condition),
        "costs": {"functional_write_words": 0, "functional_l1_terms": 26,
                  "validation_l1_terms": 26, "state_value_equality_checks": 26,
                  "resource_word_limit": 255}})


def inspect_records(records):
    """Validate recorded values independently; never call a receptor or B4 operator."""
    images, formations, probes = {}, {}, []
    starts = {}
    previous = None
    for i, record in enumerate(records):
        require(record == seal(record["kind"], record["payload"]), "journal digest")
        p = record["payload"]
        require(p["index"] == i and p["previous"] == previous, "journal order")
        previous = record["digest"]
        kind = record["kind"]
        if kind.endswith("_start"):
            require(i + 1 < len(records) and records[i + 1]["kind"] == kind[:-6], "unfinished call")
            starts[i + 1] = p
            continue
        require(i in starts, "result without a preceding start")
        start = starts[i]
        require(all(p.get(k) == v for k, v in start.items()
                    if k not in {"index", "previous", "state_digest"}), "call/result identity")
        e = p["episode"]
        require(type(e) is int and 0 <= e < 4, "episode identity")
        if kind == "image":
            position = p["position"]
            require(0 <= position < 7 and (e, position) not in images, "image duplicate")
            pattern, delta, role = episode_recipe(*EPISODES[e])[position]
            require((p["pattern"], p["delta"], p["role"]) == (pattern, delta, role), "image recipe")
            f = p["frame"]
            expected = expected_visual(pattern, delta)
            raw_recipe = b"".join(b"".join(bytes((value + delta,)) * 120
                for value in PATTERNS[pattern][row:row+3]) * 40 for row in (0, 3))
            require(p["input_sha256"] == raw_hash(raw_recipe), "recorded image bytes differ from recipe")
            require(p["pixel_histogram_per_channel"] == {
                    str(64 + delta): 4800, str(192 + delta): 4800}, "image histogram")
            require(f["geometry_id"] == CONFIG.geometry_id and f["carrier_ids"] == list(CONFIG.carrier_ids),
                    "recorded geometry or order")
            require(max(abs(x-y) for x,y in zip(_values(f["values"], 18), expected, strict=True)) <= 1e-12,
                    "recorded receptor values")
            require(f["values"] == p["receptor"]["channel_values"], "conversion mismatch")
            require(all(abs(x-(128+delta)/255) <= 1e-12 for x in p["global_means"]), "global control")
            require(p["costs"] == {"image_bytes": 28800, "receptor_channel_samples": 28800,
                    "global_control_channel_samples": 28800, "position_validation_terms": 18,
                    "control_validation_sum_inputs": 18, "control_validation_mean_divisions": 3}, "image costs")
            images[e, position] = record
        elif kind == "formation":
            condition = p["condition"]
            require(condition in CONDITIONS and (e, condition) not in formations, "formation duplicate")
            source = images[e, 0]
            offered = project_values(source["payload"]["frame"]["values"], condition)
            require(p["input_digest"] == source["digest"] and p["offered"] == list(offered), "formation source")
            require(p["prestate"] == empty_payload(), "nonfresh initial state")
            validate_storage(p["poststate"], offered)
            require(p["state_digest"] == b4._digest(p["poststate"]), "stored identity")
            require(p["owner"] == f"{RUN_ID}.episode.{e}.{condition}", "formation owner")
            require(p["native_cost"] == [27, 0] and p["event"] == {
                    "event": "B4_APPENDED", "slot_id": "b4.slot.000"}, "native formation receipt")
            require(p["projection_costs"] == projection_costs(condition), "projection cost")
            require(p["costs"] == {"functional_write_words": 29, "functional_l1_terms": 0,
                "validation_l1_terms": 0, "stored_value_equality_checks": 26,
                "resource_word_limit": 255, "capacity_slots": 9, "initialized_slots": 9}, "formation costs")
            formations[e, condition] = record
        elif kind == "probe":
            condition, position = p["condition"], p["position"]
            source, formation = images[e, position], formations[e, condition]
            require(position > 0 and p["input_digest"] == source["digest"]
                    and p["formation_digest"] == formation["digest"]
                    and p["owner"] == formation["payload"]["owner"], "probe source/owner")
            offered = project_values(source["payload"]["frame"]["values"], condition)
            original = tuple(formation["payload"]["offered"])
            require(p["offered"] == list(offered), "probe input")
            require(p["prestate"] == p["poststate"] == formation["payload"]["poststate"], "probe mutation")
            require(p["prestate_digest"] == p["poststate_digest"]
                    == start["state_digest"] == b4._digest(p["prestate"]), "probe state digest")
            distances = [math.fsum(abs(x-y) for x,y in zip(offered[:8], original[:8], strict=True))/8,
                         math.fsum(abs(x-y) for x,y in zip(offered[8:], original[8:], strict=True))/18]
            require(p["distances"] == distances, "recorded distances")
            recognized = all(d <= 0.2 for d in distances)
            require(p["recognized"] is recognized, "native threshold decision")
            native = [max(distances), sum(distances), -1, "b4.slot.000", list(original), *distances]
            require(p["native_selected"] == (native if recognized else None), "native selection")
            require(p["returned"] == (list(original) if recognized else None), "selected values")
            expected_recognized = source["payload"]["pattern"] == EPISODES[e][0]
            require(p["score"] == score(expected_recognized, recognized,
                    original if recognized else None, original), "external scoring")
            require(p["projection_costs"] == projection_costs(condition), "projection cost")
            require(p["costs"] == {"functional_write_words": 0, "functional_l1_terms": 26,
                "validation_l1_terms": 26, "state_value_equality_checks": 26,
                "resource_word_limit": 255}, "probe costs")
            probes.append(p)
        else:
            raise SpatialError("unexpected journal event")
    require(len(records) == 168 and len(images) == 28 and len(formations) == 8 and len(probes) == 48,
            "incomplete scope")
    require(len({(p['episode'], p['condition'], p['position']) for p in probes}) == 48, "duplicate probes")
    summary = {}
    for condition in CONDITIONS:
        rows = [p for p in probes if p["condition"] == condition]
        summary[condition] = dict(Counter(p["score"]["classification"] for p in rows))
    for e in range(4):
        for position in range(1, 7, 2):
            left = project_values(images[e, position]["payload"]["frame"]["values"], "B4_NO_LOCATION")
            right = project_values(images[e, position+1]["payload"]["frame"]["values"], "B4_NO_LOCATION")
            require(left == right, "location leaked into global control")
    return {"counts": {"image_analyses": 28, "formations": 8, "probes": 48},
        "classifications": summary, "receptor_and_storage_preserved": True,
        "all_probe_states_unchanged": True, "functional_write_words": 232,
        "functional_l1_terms": 1248, "validation_l1_terms": 1248}


def read_records(directory):
    raw = (Path(directory) / "events.jsonl").read_bytes()
    require(raw.endswith(b"\n"), "incomplete journal line")
    return [json.loads(line) for line in raw.splitlines()]


def verify_result(directory):
    try:
        directory = Path(directory)
        require(not (directory / "failure.json").exists(), "failure recorded")
        manifest = read_sealed(directory / "manifest.json", "manifest")
        result = read_sealed(directory / "result.json", "result")
        terminal = read_sealed(directory / "terminal.json", "terminal")
        for source in manifest["payload"]["source"]["sources"]:
            require(raw_hash(base64.b64decode(source["bytes_base64"], validate=True)) == source["sha256"],
                    "archived source bytes")
        require(result["payload"]["manifest_digest"] == manifest["digest"], "manifest binding")
        require(result["payload"]["journal_sha256"] == raw_hash((directory / "events.jsonl").read_bytes()), "journal hash")
        require(result["payload"]["summary"] == inspect_records(read_records(directory)), "summary mismatch")
        require(terminal["payload"] == {"result_digest": result["digest"], "exit_code": 0, "status": "OK"}, "terminal")
        return {"recording_status": "COMPLETE", "result_digest": result["digest"],
                "summary": result["payload"]["summary"]}
    except Exception as exc:
        return {"recording_status": "NOT_EVALUABLE", "error": str(exc)}


def run_once():
    require(_RUN_RELEASE_ENABLED, "spatial execution is closed")
    qualification = read_sealed(BASE / QUALIFICATION_ID / "result.json", "qualification")
    require(qualification["payload"]["successful"] and qualification["payload"]["test_count"] == 11,
            "qualification not complete")
    require(qualification["payload"]["output_sha256"] == raw_hash((BASE / QUALIFICATION_ID / "output.txt").read_bytes()),
            "qualification transcript")
    check_sources(qualification["payload"]["source"])
    source = source_manifest()
    require(not b4._EXECUTION_RELEASE_ENABLED, "old comparison entry opened")
    journal = Journal(BASE / RUN_ID)
    started = time.perf_counter()
    try:
        manifest = seal("manifest", {"run_id": RUN_ID, "source": source,
            "qualification_digest": qualification["digest"],
            "authorization": (BASE / (RUN_ID + ".authorization.txt")).read_text(encoding="utf-8"),
            "episodes": EPISODES, "patterns": PATTERNS, "conditions": CONDITIONS,
            "threshold": 0.2, "capacity": 9, "expected_counts": [28, 8, 48],
            "retry_policy": "NO_RETRY_OR_RESUME"})
        _write_new(journal.directory / "manifest.json", manifest)
        for episode, (stored, other) in enumerate(EPISODES):
            states = {}
            for position, (pattern, delta, role) in enumerate(episode_recipe(stored, other)):
                frame, input_digest, means = analyze_input(journal, episode, position, pattern, delta, role)
                for condition in CONDITIONS:
                    if role == "formation":
                        states[condition] = form(journal, episode, condition, frame, input_digest)
                    else:
                        state, formation_digest = states[condition]
                        probe(journal, episode, position, condition, frame, input_digest,
                              state, formation_digest, pattern == stored)
        journal.close()
        check_sources(source)
        summary = inspect_records(read_records(journal.directory))
        result = seal("result", {"manifest_digest": manifest["digest"], "summary": summary,
            "journal_sha256": raw_hash(journal.path.read_bytes()), "errors": [],
            "elapsed_seconds": time.perf_counter()-started,
            "process_memory_status": "NOT_MEASURED"})
        _publish(journal.directory / "result.json", result)
        _publish(journal.directory / "terminal.json", seal("terminal", {
            "result_digest": result["digest"], "exit_code": 0, "status": "OK"}))
        checked = verify_result(journal.directory)
        require(checked["recording_status"] == "COMPLETE", str(checked))
        return checked
    except BaseException as exc:
        journal.close()
        _write_new(journal.directory / "failure.json", seal("failure", {
            "recording_status": "NOT_EVALUABLE", "error_type": type(exc).__name__,
            "error": str(exc), "traceback": traceback.format_exc(), "recorded_events": journal.index}))
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-once", action="store_true")
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    require(bool(args.run_once) != bool(args.verify), "choose execution OR read-only verification")
    finding = run_once() if args.run_once else verify_result(args.verify)
    print(json.dumps(finding, sort_keys=True))
    raise SystemExit(0 if finding["recording_status"] == "COMPLETE" else 1)
