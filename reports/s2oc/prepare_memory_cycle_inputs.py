"""Caller file preparation only. No project imports, tests or system execution."""
import ast
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports/s2oc/memory-cycle-input-binding"
DATA = ROOT / "sources/s2oc/memory-cycle"
HISTORY = ROOT / "reports/s2oa/s2oa-source-preseal-20260909-01"
QUAL = ROOT / "reports/s2oc/s2oc-admission-qualification-20260910-01"
RUN = "caller-memory-cycle-20260910-01"  # Reserved, not executed.
AV, V = "COMPLETE_AV_PERCEPTION", "PARTIAL_VISUAL_CUE"
# Only file numbers, never expected memory roles, enter the execution manifest.
FILES = (1, 6, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 6, 4, 4, 4, 5, 5, 6)
SELECTED = ("oa-e02-audio", "oa-e02-visual", "oa-e09-visual", "oa-e13-visual",
            "oa-e17-visual", "oa-e22-visual", "oa-e01-visual")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def filehash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def ref(path):
    return dict(path=path.relative_to(ROOT).as_posix(), bytes=path.stat().st_size,
                sha256=filehash(path))


def bound(value, key):
    return {**value, key: sha(canonical(value))}


def check(value, key):
    if value[key] != sha(canonical({k: v for k, v in value.items() if k != key})):
        raise ValueError("DIGEST_INVALID:" + key)


def save(name, value):
    with (OUT / name).open("xb") as stream:
        stream.write(canonical(value))


def extract(identity, namespace):
    path = ROOT / identity["path"]
    if filehash(path) != identity["file_sha256"]:
        raise ValueError("GENERATOR_CHANGED")
    nodes = [n for n in ast.parse(path.read_text(encoding="utf-8")).body
             if isinstance(n, ast.FunctionDef) and n.name == identity["function"]]
    if len(nodes) != 1 or sha(canonical(ast.dump(nodes[0], include_attributes=False))) != identity["ast_digest"]:
        raise ValueError("GENERATOR_AST_CHANGED")
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return namespace[identity["function"]]


def times(n, kind):
    g = n - 1
    return dict(field_window=[0 if g == 0 else 200000000*g-100000000, 200000000*g+100000000],
        audio_window=[9600*g, 9600*g+4800] if kind == AV else None,
        audio_index=20*g if kind == AV else None,
        audio_common=[200000000*g, 200000000*g+100000000] if kind == AV else None,
        visual_window=[6*g+2, 6*g+3],
        visual_common=[(6*g+2)*1000000000//30, 200000000*g+100000000])


def main():
    if OUT.exists() or DATA.exists() or (ROOT / "reports/s2oc" / RUN).exists():
        raise ValueError("OUTPUT_OR_RESERVED_RUN_EXISTS")
    ex = json.loads((HISTORY / "execution-plan.json").read_bytes())
    se = json.loads((HISTORY / "seal.json").read_bytes())
    check(ex, "execution_digest")
    check(se, "seal_digest")
    if se["seal_digest"] != "28d6d2408f70265c10adf56dacb7f265a231e508e41af484cf9ff5624b7747fc" or se["execution_digest"] != ex["execution_digest"] or filehash(HISTORY / "execution-plan.json") != se["execution_file_sha256"]:
        raise ValueError("HISTORICAL_BINDING_CHANGED")
    sources = [next(s for s in ex["sources"] if s["source_id"] == name) for name in SELECTED]
    for source in sources:
        check(source, "source_digest")
        if sha(canonical(source["recipe"])) != source["recipe_digest"]:
            raise ValueError("RECIPE_CHANGED")
    inv_raw = (QUAL / "admission/inventory.json").read_bytes()
    inv = json.loads(inv_raw)
    q = json.loads((QUAL / "result.json").read_bytes())
    check(q, "result_digest")
    if q["status"] != "QUALIFIED" or q["passed_tests"] != 16 or sha(inv_raw) != q["source_digest"] or filehash(QUAL / "admission/admission.json") != q["admission_sha256"]:
        raise ValueError("ACTIVE_QUALIFICATION_CHANGED")
    watched = {**inv["ob"]["files"], **inv["oc"]["files"], **inv["connector"]}
    for p, (h, size) in watched.items():
        if filehash(ROOT / p) != h or (ROOT / p).stat().st_size != size:
            raise ValueError("ACTIVE_CODE_CHANGED:" + p)
    pcm = extract(ex["generators"]["pcm"], dict(hashlib=hashlib, math=math, struct=struct))
    rgb = extract(ex["generators"]["rgb"], dict(np=np))
    if math.__spec__.origin == "built-in":
        if "math" not in sys.builtin_module_names:
            raise ValueError("MATH_ORIGIN_UNBOUND")
        math_identity = dict(origin="built-in", builtin_confirmed=True)
    else:
        math_identity = dict(origin=math.__spec__.origin, file_sha256=filehash(Path(math.__file__)))
    metadata_caps = dict(manifest=14000, provenance=6000, evaluation_binding=3000,
        execution_binding=4000, budget=3500, admission=4258, qualification=858,
        future_evaluation=3000, future_dispatch=768, future_balance=1536, report=512)
    # All remaining metadata is one shared success/error/session closure allowance.
    metadata_caps["runtime_session_and_error"] = 65536 - sum(metadata_caps.values())
    native = dict(states=19*98304, inputs=21*16384, steps=21*16384, scans=6*32767,
                  nj=18*1024, formations=18*1536, generations=18*1536)
    sources_bytes = len(inv_raw) + Path(__file__).stat().st_size
    shared = sources_bytes + native["nj"] + native["formations"] + native["generations"]
    total = sum(native.values()) + sources_bytes + 65536 + 262144
    if metadata_caps["runtime_session_and_error"] <= 0 or sources_bytes > 174080 or shared > 262144 or total > 4194304:
        raise ValueError("PREPARATION_BUDGET_INVALID")
    OUT.mkdir()
    DATA.mkdir(parents=True)
    phase, completed = "BINDING", 0
    try:
        # Bind the unchanged recipes before producing any caller bytes.
        provenance = bound(dict(schema="s2oc.memory-cycle-provisioning.v1", main_authorized=False,
            historical=[ref(HISTORY / name) for name in ("execution-plan.json", "seal.json", "verification.json")],
            historical_execution_digest=ex["execution_digest"],
            selected_sources=[{k: s[k] for k in ("source_id", "source_digest", "recipe", "recipe_digest",
                "payload_sha256", "byte_count", "historical_recipe_id", "transformation")} for s in sources],
            generators=ex["generators"], producer=ref(Path(__file__)),
            environment=dict(python=sys.version, executable_sha256=filehash(Path(sys.executable)),
                             math=math_identity, numpy=np.__version__),
            boundary="Historical files establish caller provenance here; no historical main or sealer is called. Future processing needs only the bound caller files, not these historical archives or generators.",
            planned_files=["input-00.pcm"]+[f"input-{i:02d}.rgb" for i in range(1, 7)]), "provisioning_digest")
        if len(canonical(provenance)) > metadata_caps["provenance"]:
            raise ValueError("PROVENANCE_LIMIT")
        save("provisioning.json", provenance)
        payloads = []
        for index, source in enumerate(sources):
            phase = "CALLER_FILE:" + source["source_id"]
            if index == 0:
                payload = pcm(source["recipe"])
                name = "input-00.pcm"
            else:
                payload = rgb(source["recipe"]["ordinal"])
                if source["recipe"]["visible_positions"] is not None:
                    for i in range(32, 288):
                        cell, channel = divmod(i, 3)
                        row, col = divmod(cell, 12)
                        payload[row*135:(row+1)*135, col*160:(col+1)*160, channel] = 0
                name = f"input-{index:02d}.rgb"
            view = memoryview(payload).cast("B")
            if len(view) != source["byte_count"] or sha(view) != source["payload_sha256"]:
                raise ValueError("HISTORICAL_PAYLOAD_MISMATCH")
            with (DATA / name).open("xb") as stream:
                stream.write(view)
            payloads.append(dict(path=(DATA / name).relative_to(ROOT).as_posix(),
                                 sha256=sha(view), byte_count=len(view)))
            del view, payload
            completed += 1
        phase = "MANIFEST"
        events = []
        for n, index in enumerate(FILES, 1):
            kind = V if index == 6 else AV
            events.append(dict(event_id=f"cycle-event-{n:02d}", ordinal=n, kind=kind, **times(n, kind),
                pcm=dict(source_id=f"cycle-pcm-{n:02d}", **payloads[0]) if kind == AV else None,
                rgb=dict(source_id=f"cycle-rgb-{n:02d}", **payloads[index])))
        manifest = bound(dict(schema="s2ob.caller.v2", run_id=RUN,
            field_clock_id="s2ob-caller-field-clock", config_digest=ex["profiles"]["coordinator_config_digest"],
            profile_digest="4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f",
            code_digest=sha(canonical(inv["ob"])), events=events), "manifest_digest")
        evaluation = bound(dict(schema="s2oc.memory-cycle-evaluation-binding.v1", manifest_digest=manifest["manifest_digest"],
            roles=dict(A="input-01.rgb", B="input-02.rgb", C="input-03.rgb", D="input-04.rgb", E="input-05.rgb", cue="input-06.rgb"),
            decisions=[dict(event="cycle-event-02", status="ADMIT_SINGLE_CONTEXT", area="A_RECENT", target="A"),
                       dict(event="cycle-event-15", status="ADMIT_SINGLE_CONTEXT", area="B_STABLE", target="A"),
                       dict(event="cycle-event-21", status="ABSTAIN_NO_CONTEXT", area=None, target="A")],
            checkpoints=[dict(event="cycle-event-05", prediction="A stabilized; Fast support 2, auditory and visual PPB support 3"),
                dict(event="cycle-event-13", prediction="A Fast expired after eight further formations; last A B4 still present"),
                dict(event="cycle-event-14", prediction="A absent from B4 and Fast, visual A Slow generation remains"),
                dict(event="cycle-event-16", prediction="four occupied visual Slow slots after second D formation"),
                dict(event="cycle-event-20", prediction="second E formation replaces oldest visual A Slow slot with new generation")],
            generation="Derive actual births and replacements from transactions. MATCHED retains generation; expired/free slots have no current birth. Compare event 15 A generation with event 20 replacement, not slot ID alone. Event 15 receipt cannot establish event 21 availability.",
            support="Fast <= 2, PPB <= 3; saturation is not absent updating or learning.",
            assessment="Each decision and state prediction separately. Unexpected valid inventories and abstentions are functional counterevidence, never technical start gates.",
            new_executable_evaluation_needed="Small task-specific post-verification checks of the three cues, saturated supports, A eviction and visual Slow generation replacement. Existing evaluator for seven-event OB does not establish these criteria. No evaluator implemented here.",
            exclusions=["auditory Slow replacement", "full E restabilization", "independent source generalization",
                        "live input", "process restart", "unbounded operation", "hypothesis application"]), "evaluation_digest")
        for name, obj, cap in (("manifest.json", manifest, "manifest"), ("evaluation-binding.json", evaluation, "evaluation_binding")):
            if len(canonical(obj)) > metadata_caps[cap]:
                raise ValueError(cap.upper()+"_LIMIT")
            save(name, obj)
        execution = bound(dict(schema="s2oc.memory-cycle-execution-binding.v1", main_authorized=False,
            run_id_reserved=RUN, output_directory="reports/s2oc/"+RUN, output_checked_absent=True,
            manifest_digest=manifest["manifest_digest"], entry="tools._s2oc_private_session_admission.open_session",
            admission_sha256=q["admission_sha256"],
            active_references=[ref(QUAL / "admission/admission.json"), ref(QUAL / "admission/inventory.json"), ref(QUAL / "result.json"),
                ref(OUT / "manifest.json"), ref(OUT / "provisioning.json"), ref(OUT / "evaluation-binding.json"), ref(Path(__file__))],
            counts=dict(sessions=1, events=21, formations=18, auditory_cues=0, visual_cues=3, audio=18, nj=18,
                        visual=21, payload_reads=39, contacts=6912, scans=6, independent_verifications=1),
            protocol=["Separate run authorization required. Check current admission, inventory, file hashes and all bindings before open.",
                "One session, ordered manifest events, no reset; hash each payload before analysis; no deduplication or recipe access.",
                "Maintain combined external-reference and session ledger before every next payload and after close; reserve closure/error budget.",
                "Reuse independent verification once, then separately evaluate. No historical batch replay or test repetition.",
                "Close on processing failure, preserve full progress and error. No retry or functional partial evaluation; all gates False."],
            payloads=payloads, historical_archives_required_at_runtime=False), "execution_digest")
        if len(canonical(execution)) > metadata_caps["execution_binding"]:
            raise ValueError("EXECUTION_BINDING_LIMIT")
        save("execution-binding.json", execution)
        budget = bound(dict(schema="s2oc.memory-cycle-budget.v1", metadata_limit=65536,
            metadata_caps=metadata_caps, source_class_bytes=sources_bytes,
            source_class_contributions=[ref(QUAL / "admission/inventory.json"), ref(Path(__file__))],
            native_caps=native, shared_max=shared, shared_limit=262144,
            verification_max=262144, total_max=total, total_limit=4194304,
            binding_actual_bytes={p.name: p.stat().st_size for p in OUT.iterdir()},
            raw_inputs=dict(unique_files=7, stored_bytes=sum(p["byte_count"] for p in payloads),
                            planned_read_bytes=18*19200+21*6220800, system_output=False),
            provenance_archive_bytes=[ref(HISTORY / name) for name in ("execution-plan.json", "seal.json", "verification.json")],
            accounting="Source archive files are preparation-only, explicitly listed in full. Active sources charge inventory and this producer; the recipe/hash extracts and their historical source digests are fully charged inside provisioning metadata. They do not reconstruct the historical execution file. All active metadata, session/record headers, outcomes and errors share 65536. Raw caller inputs are separately counted input stock, not generated system evidence. Native maxima plus all metadata, sources and verification are jointly bounded. No extra result copies may remain uncharged.",
            later_actual_ledger_required=True, main_authorized=False), "budget_digest")
        if len(canonical(budget)) > metadata_caps["budget"]:
            raise ValueError("BUDGET_BINDING_LIMIT")
        save("budget.json", budget)
        for p, (h, size) in watched.items():
            if filehash(ROOT / p) != h or (ROOT / p).stat().st_size != size:
                raise ValueError("ACTIVE_CODE_CHANGED_AFTER_PREPARATION:" + p)
        print(json.dumps(dict(status="CALLER_INPUTS_BOUND_NOT_EXECUTED", files=completed,
            manifest_digest=manifest["manifest_digest"], shared_max=shared, total_max=total,
            metadata_caps=metadata_caps, actual={p.name: p.stat().st_size for p in OUT.iterdir()},
            receptor_calls=0, nj_calls=0, memory_calls=0, field_calls=0, runtime_calls=0)))
    except Exception as exc:
        save("preparation-error.json", dict(phase=phase, completed_files=completed,
             error_class=type(exc).__name__, error=str(exc), main_authorized=False))
        raise


if __name__ == "__main__":
    main()
