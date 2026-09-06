"""One read-only S2-NB calculation on frozen JSON; no project imports."""

import ast
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import sys


ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "s2nb-auditory-selectivity-20260906-01"
OUT = Path(__file__).resolve().parent / RUN_ID
PLAN = "docs/S2NB_AUDITIVE_TEILHINWEIS_SELEKTIVITAET_UNTER_KONKURRENZ.md"
INPUTS = {
    "reports/s2mt/s2mt-presealed-transfer-runtime-20260906-05/result.json":
        "2de06dfc17728fd1c9aa7793e616e5a530cbf716306431117ce9dce4325d886f",
    "reports/s2mw/s2mw-audio-receptor-compatibility-20260906-02/result.json":
        "b1ca1ad9d11e29c6d5b547d166741f1afbf40fb3e8f240ea6eb07d3f4e7d87ef",
}
CUES = (("e21", "n00"), ("e23", "n01"), ("e25", "n02"), ("e27", "n12"))
ARMS = (("OBSERVED_24", 24), ("FULL_48_DIAGNOSTIC", 48))


def canonical(value):
    return json.dumps(value, allow_nan=False, ensure_ascii=True,
                      sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_digest(record, key):
    require(record[key] == digest({k: v for k, v in record.items() if k != key}),
            f"canonical {key} differs")


def sha_file(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def calculate():
    require(sys.float_info.mant_dig == 53 and sys.float_info.radix == 2,
            "binary64 runtime required")
    records = []
    for path, expected in INPUTS.items():
        require(sha_file(path) == expected, f"frozen file differs: {path}")
        record = json.loads((ROOT / path).read_bytes())
        check_digest(record, "record_digest")
        records.append(record)
    run, audio = records
    plan = run["presealed_source_plan"]
    require(plan["plan_digest"] == digest({k: v for k, v in plan.items()
                                          if k not in ("plan_digest", "recipes")}),
            "source plan digest differs")
    require(plan["recipe_digests"] == [r["recipe_digest"] for r in plan["recipes"]],
            "ordered source recipe digests differ")
    require(plan["compatibility_evidence_file_sha256"] == list(INPUTS.values())[1]
            and plan["compatibility_evidence_record_digest"] == audio["record_digest"],
            "compatibility evidence is not bound to run plan")
    require(run["technical_status"] == "RECORDING_COMPLETE", "incomplete input record")
    source_hashes = run["source_hashes"]
    for path, expected in source_hashes.items():
        require(sha_file(path) == expected, f"bound source differs: {path}")

    # Inspect literal configuration without importing or constructing project types.
    profile_path = "tools/_s2jw_default_live_profile.py"
    tree = ast.parse((ROOT / profile_path).read_text(encoding="utf-8-sig"))
    constants = {n.targets[0].id: ast.literal_eval(n.value)
                 for n in tree.body if isinstance(n, ast.Assign)
                 and isinstance(n.targets[0], ast.Name)
                 and isinstance(n.value, ast.Constant)}
    builder = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                   and n.name == "build_s2jw_default_live_profile")
    fast_call = next(n for n in ast.walk(builder) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Attribute) and n.func.attr == "TSPM1FastConfig")
    fast_args = [ast.literal_eval(n) for n in fast_call.args]
    fast_fields = ("fast_bank_id", "capacity", "auditory_match_threshold",
                   "visual_match_threshold", "update_factor", "consolidate_after",
                   "expire_after_exposures")
    fast_payload = dict(zip(fast_fields, fast_args, strict=True), schema_version="tspm1.private.v1")
    require(digest(fast_payload) == constants["EXPECTED_FAST_CONFIG_DIGEST"],
            "fast config digest differs")
    parameter_call = next(n for n in ast.walk(builder) if isinstance(n, ast.Call)
                          and isinstance(n.func, ast.Name) and n.func.id == "PPB1ProfileParameters")
    fields = ("capacity", "match_threshold", "update_rate", "stable_after", "expire_after_steps")
    parameters = {role: dict(zip(fields, [ast.literal_eval(x) for x in call.args], strict=True))
                  for role, call in zip(("auditory", "visual"), parameter_call.args, strict=True)}
    require(digest(parameters) == constants["EXPECTED_PARAMETER_DIGEST"], "PPB parameters differ")
    a_threshold = fast_payload["auditory_match_threshold"]
    reference_threshold = parameters["auditory"]["match_threshold"]
    require((a_threshold, reference_threshold) == (0.2, 0.02), "fixed thresholds differ")
    ancillary_paths = (profile_path, "mcm_field_organism/_tspm1_private.py",
                       "mcm_field_organism/_ppb1_receptor_profiles.py",
                       "tools/_s2ms_private_minimal_runtime_reproduction.py")
    ancillary_hashes = {p: sha_file(p) for p in ancillary_paths}
    plan_hash = sha_file(PLAN)

    recipes = {item["recipe_id"]: item for item in plan["recipes"]}
    outputs = {item["recipe_id"]: item for item in audio["scaled_outputs"]}
    require(len(recipes) == len(plan["recipes"]) == len(outputs) == len(audio["scaled_outputs"]) == 13,
            "recipe count or uniqueness differs")
    require(set(recipes) == set(outputs) == {f"n{i:02d}" for i in range(13)}, "recipe ids differ")
    vectors, vector_bindings = {}, {}
    for recipe_id, record in outputs.items():
        check_digest(recipes[recipe_id], "recipe_digest")
        values = record["receptor_values"]
        require(type(values) is list and len(values) == 48
                and all(type(x) in (float, int) and math.isfinite(x) and -1 <= x <= 1 for x in values),
                f"invalid receptor vector: {recipe_id}")
        require(hashlib.sha256(struct.pack("<48d", *values)).hexdigest() == record["receptor_values_digest"],
                f"vector byte digest differs: {recipe_id}")
        require(record["input_digest"] == recipes[recipe_id]["auditory_payload_digest"],
                f"PCM binding differs: {recipe_id}")
        vectors[recipe_id] = values
        vector_bindings[recipe_id] = {
            "json_pointer": f"/scaled_outputs/{audio['scaled_outputs'].index(record)}/receptor_values",
            "pcm_digest": record["input_digest"], "receptor_values_byte_digest": record["receptor_values_digest"],
            "values_canonical_digest": digest(values), "recipe_digest": recipes[recipe_id]["recipe_digest"],
        }

    events = run["execution"]["events"]
    require(len(events) == 28, "event count differs")
    for ordinal, event in enumerate(events, 1):
        require(event["ordinal"] == ordinal and event["event_code"] == f"e{ordinal:02d}", "event order differs")
    for event in events[:20]:
        require(event["event_type"] == "COMPLETE_AV_PERCEPTION", "formation role differs")
        check_digest(event["memory_observation"], "observation_digest")
    final = events[19]["memory_observation"]
    require(final["generation"] == 20, "final generation differs")
    require(all(e["post_snapshot"]["memory_state_digest"] == final["state_digest"] for e in events[20:]),
            "cue memory state changed")
    slots = []
    for entry in sorted(final["b4"], key=lambda e: e["slot_id"]):
        formation = entry["formation_index"]
        require(12 <= formation <= 20, "B4 formation outside bound window")
        event = events[formation - 1]
        recipe = event["recipe_id"]
        require(recipe == f"n{formation - 9:02d}", "B4 source mapping differs")
        original = [x for x in event["memory_observation"]["b4"] if x["slot_id"] == entry["slot_id"]]
        require(original == [entry], "final B4 entry differs from formation entry")
        siblings = [x for x in event["memory_observation"]["fast"] if x["last_selected_step"] == formation]
        require(len(siblings) == 1 and siblings[0]["support_count"] == 1
                and siblings[0]["auditory_values_digest"] == digest(vectors[recipe]), "B4/Fast sibling differs")
        slots.append({"bank": "B4", "slot_id": entry["slot_id"], "formation_index": formation,
                      "recipe_id": recipe, "binding_method": "FORMATION_AND_FAST_SIBLING",
                      "b4_entry": entry, "sibling_fast": siblings[0],
                      "formation_source_digest": event["source_digest"],
                      "formation_source_receipt_digest": event["source_receipt_digest"],
                      "formation_observation_digest": event["memory_observation"]["observation_digest"]})
    require(sorted(s["formation_index"] for s in slots) == list(range(12, 21)), "B4 window incomplete")
    require(len(final["fast"]) == 3, "Fast occupancy differs")
    for slot, recipe, formation in zip(sorted(final["fast"], key=lambda s: s["slot_id"]),
                                     ("n10", "n11", "n09"), (19, 20, 18), strict=True):
        require(slot["last_selected_step"] == formation and slot["support_count"] == 1
                and slot["auditory_values_digest"] == digest(vectors[recipe]), "final Fast binding differs")
        slots.append({"bank": "FAST", "slot_id": slot["slot_id"], "formation_index": formation,
                      "recipe_id": recipe, "binding_method": "FINAL_FAST_VECTOR_DIGEST", "fast_slot": slot})
    cues = []
    for event_code, recipe in CUES:
        event = events[int(event_code[1:]) - 1]
        require(event["recipe_id"] == recipe and event["event_type"] == "PARTIAL_AUDITORY_CUE", "cue differs")
        cues.append({"event_code": event_code, "recipe_id": recipe,
                     "source_digest": event["source_digest"], "source_receipt_digest": event["source_receipt_digest"]})

    # This is the only distance pass: no project scanner, state replay, or hidden band use in OBSERVED_24.
    references = [{"bank": "LEARNING_REFERENCE", "slot_id": None, "formation_index": None,
                   "recipe_id": rid} for rid in ("n00", "n01", "n02")]
    rows, term_count = [], 0
    for arm, count in ARMS:
        for cue in cues:
            for item in slots + references:
                q, x = vectors[cue["recipe_id"]], vectors[item["recipe_id"]]
                distance = sum(abs(float(x[i]) - float(q[i])) for i in range(count)) / count
                term_count += count
                threshold = reference_threshold if item["bank"] == "LEARNING_REFERENCE" else a_threshold
                rows.append({"arm": arm, "band_count": count, "cue_event": cue["event_code"],
                             "cue_recipe": cue["recipe_id"], "bank": item["bank"], "slot_id": item["slot_id"],
                             "formation_index": item["formation_index"], "candidate_recipe": item["recipe_id"],
                             "cue_values_digest": digest(q), "candidate_values_digest": digest(x),
                             "distance": distance, "threshold": threshold, "reserve": threshold - distance,
                             "matched": distance <= threshold})
    require(len(rows) == 120 and term_count == 4320, "calculation budget differs")
    summaries = []
    for arm, _ in ARMS:
        for cue in cues:
            for bank in ("B4", "FAST", "LEARNING_REFERENCE"):
                selected = [r for r in rows if (r["arm"], r["cue_event"], r["bank"]) == (arm, cue["event_code"], bank)]
                matches = [r["slot_id"] if bank != "LEARNING_REFERENCE" else r["candidate_recipe"]
                           for r in selected if r["matched"]]
                summaries.append({"arm": arm, "cue_event": cue["event_code"], "bank": bank,
                                  "match_ids": matches, "match_count": len(matches),
                                  "cardinality": "ZERO" if not matches else "ONE" if len(matches) == 1 else "MULTIPLE",
                                  "minimum_distance": min(r["distance"] for r in selected),
                                  "maximum_distance": max(r["distance"] for r in selected)})
    changes = []
    for cue in cues:
        for bank in ("B4", "FAST", "LEARNING_REFERENCE"):
            a, b = [s for s in summaries if (s["cue_event"], s["bank"]) == (cue["event_code"], bank)]
            changes.append({"cue_event": cue["event_code"], "bank": bank,
                            "observed_24_count": a["match_count"], "full_48_count": b["match_count"],
                            "count_delta": b["match_count"] - a["match_count"],
                            "removed_ids": [x for x in a["match_ids"] if x not in b["match_ids"]],
                            "added_ids": [x for x in b["match_ids"] if x not in a["match_ids"]]})
    all_hashes = {**INPUTS, **source_hashes, **ancillary_hashes, PLAN: plan_hash}
    require(all(sha_file(path) == expected for path, expected in all_hashes.items()), "input or source changed")
    return {"schema": "s2nb.read-only-selectivity-tables.v1", "run_id": RUN_ID,
            "technical_status": "READ_ONLY_TABLES_COMPLETE", "input_hashes": INPUTS,
            "record_digests": [r["record_digest"] for r in records], "plan_sha256": plan_hash,
            "bound_source_hashes": source_hashes, "ancillary_source_hashes": ancillary_hashes,
            "source_hashes_unchanged": True, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "python_version": sys.version, "arithmetic": "Python sum, ascending band order, binary64 inputs; <= threshold",
            "configuration": {"fast": fast_payload, "ppb_parameters": parameters,
                              "fast_config_digest": constants["EXPECTED_FAST_CONFIG_DIGEST"],
                              "ppb_parameter_digest": constants["EXPECTED_PARAMETER_DIGEST"]},
            "vector_bindings": vector_bindings, "cue_bindings": cues, "slot_bindings": slots,
            "rows": rows, "bank_summaries": summaries, "changes": changes,
            "counts": {"distance_values": len(rows), "absolute_value_differences": term_count,
                       "project_imports": 0, "receptor_calls": 0, "memory_calls": 0,
                       "scanner_calls": 0, "context_calls": 0, "field_calls": 0, "runtime_calls": 0},
            "limits": ["Known-source diagnosis, not independent confirmation",
                       "FULL_48_DIAGNOSTIC uses additional information",
                       "Learning references are not final Slow prototypes",
                       "No exact final Slow match set or new context admission inferred",
                       "S2MT run 05 remains S2MT_FUNCTION_FALSIFIED"]}


if __name__ == "__main__":
    OUT.mkdir(exist_ok=False)
    try:
        result = calculate()
    except Exception as exc:
        result = {"schema": "s2nb.read-only-selectivity-tables.v1", "run_id": RUN_ID,
                  "technical_status": "NOT_EVALUABLE", "error_type": type(exc).__name__, "error": str(exc)}
        result["record_digest"] = digest(result)
        (OUT / "result.json").write_bytes(canonical(result) + b"\n")
        print(json.dumps(result, ensure_ascii=True))
        raise SystemExit(1)
    table = io.StringIO(newline="")
    writer = csv.DictWriter(table, fieldnames=list(result["rows"][0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(result["rows"])
    csv_bytes = table.getvalue().encode("ascii")
    result["table_csv_sha256"] = hashlib.sha256(csv_bytes).hexdigest()
    result["record_digest"] = digest(result)
    (OUT / "tables.csv").write_bytes(csv_bytes)
    (OUT / "result.json").write_bytes(canonical(result) + b"\n")
    print(json.dumps({"status": result["technical_status"], "counts": result["counts"],
                      "summaries": result["bank_summaries"], "changes": result["changes"],
                      "record_digest": result["record_digest"]}, ensure_ascii=True))
