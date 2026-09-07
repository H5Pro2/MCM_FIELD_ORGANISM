"""Independent read-only preseal checks; no PCM generation or receptor calls."""

import hashlib
import json
from pathlib import Path

from tools import _s2np_private_source_binding as b


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=True, allow_nan=False).encode("ascii")).hexdigest()


def root(value, key):
    b.require(type(value) is dict and value.get(key) == sha({k: v for k, v in value.items() if k != key}),
              "ROOT_DIGEST_INVALID")


def check_plans(execution, evaluation):
    root(execution, "execution_digest")
    root(evaluation, "evaluation_digest")
    b.require(evaluation["execution_digest"] == execution["execution_digest"], "ROOT_LINK_INVALID")
    b.require(execution["contract_sha256"] == evaluation["contract_sha256"] == b.PINS[b.CONTRACT], "CONTRACT_INVALID")
    specs = b.source_specs()
    b.require(execution["source_order"] == [s.source_id for s in specs] and len(execution["sources"]) == 12,
              "SOURCE_ORDER_INVALID")
    for spec, source in zip(specs, execution["sources"], strict=True):
        root(source, "source_digest")
        b.check_digest(source["pcm_sha256"])
        b.require({k: v for k, v in source.items() if k not in ("source_digest", "pcm_sha256")} == spec.payload(),
                  "SOURCE_FORM_INVALID")
    b.require(execution["views"] == [dict(view_id=n, indices=list(i), diagnostic_only=n == "FULL_48_DIAGNOSTIC")
                                    for n, i in b.VIEWS], "VIEW_BINDING_INVALID")
    b.require(execution["panels"] == [dict(panel_id=p, reference_ids=list(r), cue_ids=list(b.CUES))
                                     for p, r in b.PANELS], "PANEL_BINDING_INVALID")
    expected_cases = [dict(case_id=f"c{10*j+k+1:02d}", panel_id=p, cue_id=c)
                      for j, (p, _) in enumerate(b.PANELS) for k, c in enumerate(b.CUES)]
    b.require(execution["cases"] == expected_cases, "CASE_BINDING_INVALID")
    b.require(execution["profiles"] == b.profile_binding(), "PROFILE_BINDING_INVALID")
    b.require(execution["conditions"] == [
        dict(condition_id="A_HISTORICAL_SUM", arithmetic="sum_in_index_order/len(indices)", threshold=0.1),
        dict(condition_id="A_ALL_BANDS", arithmetic="max", threshold=0.1),
        dict(condition_id="SLOW_HISTORICAL_SUM", arithmetic="sum_in_index_order/len(indices)", threshold=0.01)],
        "CONDITION_BINDING_INVALID")
    # Rebuilding metadata does not regenerate payloads or execute a comparison.
    expected = b.execution_plan(execution["sources"], execution["environment"],
                                execution["source_hashes"], execution["generator"])
    b.require(execution == expected, "EXECUTION_FORM_INVALID")
    expected_relations = []
    for i, cue in enumerate(b.CUES):
        expected_relations.append(dict(cue_id=cue, target_source_id="np-a01" if i < 4 else "np-a02" if i < 8 else None,
            subtype=("EXACT", "LEVEL", "FREQUENCY", "SPECTRAL")[i % 4] if i < 8 else "INDEPENDENT_CONTROL"))
    b.require(evaluation["relations"] == expected_relations and evaluation == b.evaluation_plan(execution),
              "EVALUATION_FORM_INVALID")
    b.require(not any(k in json.dumps(execution) for k in ("target_source_id", "subtype", "retention_identity")),
              "EVALUATION_LEAK")
    b.require(len(b.canonical(execution)) <= b.MAX_METADATA_BYTES
              and len(b.canonical(evaluation)) <= b.MAX_METADATA_BYTES, "METADATA_SIZE_EXCEEDED")


def verify_once(directory):
    out = Path(directory)
    b.require(not (out / "verification.json").exists(), "VERIFICATION_ALREADY_EXISTS")
    names = ("execution-plan.json", "evaluation-plan.json", "seal.json", "preregistration.json")
    before = {n: b.filehash(out / n) for n in names}
    execution, evaluation, seal, pre = [json.loads((out / n).read_bytes()) for n in names]
    check_plans(execution, evaluation)
    root(seal, "seal_digest")
    b.require(seal["status"] == "S2NP_SOURCES_PRESEALED" and seal["run_id"] == out.name == pre["run_id"], "RUN_BINDING_INVALID")
    b.require(seal["execution_file_sha256"] == before["execution-plan.json"]
              and seal["evaluation_file_sha256"] == before["evaluation-plan.json"]
              and seal["execution_digest"] == execution["execution_digest"]
              and seal["evaluation_digest"] == evaluation["evaluation_digest"], "SEAL_LINK_INVALID")
    b.require(seal["hashes_before"] == seal["hashes_after"] == execution["source_hashes"] == pre["hashes"] == b.watched(),
              "SOURCE_FILES_CHANGED")
    b.require(execution["environment"] == pre["environment"] == b.environment(), "ENVIRONMENT_CHANGED")
    _, gen = b.pure_generator()  # loads the bound definition, never invokes it
    b.require(gen == execution["generator"] == pre["generator"], "GENERATOR_BINDING_INVALID")
    b.require(pre["profiles"] == execution["profiles"] and pre["generation_limit"] == 12 and pre["retry"] is False
              and pre["sources"] == [s.payload() for s in b.source_specs()], "PREREGISTRATION_INVALID")
    b.require(pre["qualification_sha256"] == b.filehash(b.QUAL_DIR / "result.json"), "QUALIFICATION_CHANGED")
    for k, v in dict(attempted_sources=12, completed_sources=12, generated_samples=57600, generated_pcm_bytes=230400,
                    max_live_payloads=1, max_live_payload_bytes=19200).items():
        b.require(type(seal[k]) is int and seal[k] == v, "COUNTER_INVALID")
    for k in ("raw_payloads_persisted", "receptor_calls", "nj_calls", "distance_calls", "comparison_calls",
              "memory_calls", "context_calls", "field_calls", "runtime_calls"):
        b.require(type(seal[k]) is int and seal[k] == 0, "FORBIDDEN_EXECUTION")
    b.require(seal["main_gate_after"] is False and b.MAIN_GATE is False, "GATE_INVALID")
    sources = execution["sources"]
    pairs = [["np-a01", "np-a03"], ["np-a02", "np-a07"]]
    source_map = {s["source_id"]: s for s in sources}
    for x, y in pairs:
        b.require(source_map[x]["pcm_sha256"] == source_map[y]["pcm_sha256"]
                  and source_map[x]["source_digest"] != source_map[y]["source_digest"], "EXACT_COPY_BINDING_INVALID")
    groups = {}
    for s in sources:
        groups.setdefault(s["pcm_sha256"], []).append(s["source_id"])
    collisions = [dict(pcm_sha256=h, source_ids=ids) for h, ids in sorted(groups.items()) if len(ids) > 1]
    b.require(seal["exact_pairs"] == pairs and seal["collisions"] == collisions, "COLLISION_BINDING_INVALID")
    b.require(sum((out / n).stat().st_size for n in names) <= b.MAX_OUTPUT_BYTES, "OUTPUT_SIZE_EXCEEDED")
    after = {n: b.filehash(out / n) for n in names}
    b.require(before == after, "EVIDENCE_CHANGED")
    result = b.sealed(dict(run_id=out.name, status="S2NP_PRESEAL_BINDINGS_VALID", verification_calls=1,
        read_only=True, payload_generation_calls=0, receptor_calls=0, nj_calls=0,
        execution_digest=execution["execution_digest"], evaluation_digest=evaluation["evaluation_digest"],
        seal_digest=seal["seal_digest"], file_hashes_before=before, file_hashes_after=after,
        source_count=12, payload_bytes_recomputed=False, recipe_and_digest_links_checked=True,
        limitation="Payload hashes are bound, not independently recomputed without regeneration."), "verification_digest")
    b.publish(out / "verification.json", result, b.MAX_METADATA_BYTES)
    return result
