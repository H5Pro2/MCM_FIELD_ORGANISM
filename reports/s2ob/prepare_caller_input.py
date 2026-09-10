"""Caller-side file provisioning only; no project imports or functional execution."""
from pathlib import Path
import hashlib
import json
import math
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports/s2ob/caller-input-binding"
DATA = ROOT / "sources/s2ob/caller-av-basic"
QUAL = ROOT / "reports/s2ob/s2ob-caller-qualification-20260910-02"
RUN_ID = "caller-av-basic-20260910-01"  # Reserved, not an executed runtime run.
AV, A, V = "COMPLETE_AV_PERCEPTION", "PARTIAL_AUDITORY_CUE", "PARTIAL_VISUAL_CUE"
KINDS = (V, AV, A, AV, AV, AV, V)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(65536):
            h.update(block)
    return h.hexdigest()


def seal(x, key):
    return {**x, key: sha(canonical(x))}


def save(path, x):
    with path.open("xb") as stream:
        stream.write(canonical(x))


def times(n, kind):
    g = n - 1
    return dict(field_window=[0 if g == 0 else 200000000*g-100000000, 200000000*g+100000000],
        audio_window=[9600*g, 9600*g+4800] if kind != V else None,
        audio_index=20*g if kind != V else None,
        audio_common=[200000000*g, 200000000*g+100000000] if kind != V else None,
        visual_window=[6*g+2, 6*g+3] if kind != A else None,
        visual_common=[(6*g+2)*1000000000//30, 200000000*g+100000000] if kind != A else None)


def main():
    if OUT.exists() or DATA.exists():
        raise RuntimeError("BINDING_OR_INPUT_ALREADY_EXISTS")
    inventory = json.loads((QUAL / "code-inventory.json").read_bytes())
    result = json.loads((QUAL / "result.json").read_bytes())
    if result["status"] != "QUALIFIED" or result["passed_tests"] != 30:
        raise RuntimeError("QUALIFICATION_NOT_BOUND")
    for path, (digest, size) in inventory["files"].items():
        p = ROOT / path
        if p.stat().st_size != size or file_hash(p) != digest:
            raise RuntimeError("QUALIFIED_SOURCE_CHANGED")
    if sha(canonical(inventory)) != result["code_digest"] or sys.version != inventory["environment"]["python"]:
        raise RuntimeError("CODE_OR_INTERPRETER_CHANGED")
    if file_hash(Path(sys.executable)) != inventory["environment"]["executable_sha256"]:
        raise RuntimeError("INTERPRETER_CHANGED")
    if result["result_digest"] != sha(canonical({k: v for k, v in result.items() if k != "result_digest"})):
        raise RuntimeError("QUALIFICATION_DIGEST_INVALID")
    for name, digest in result["files"].items():
        if file_hash(QUAL / name) != digest:
            raise RuntimeError("QUALIFICATION_ATTACHMENT_CHANGED")
    if file_hash(QUAL / "final-balance.json") != result["balance_sha256"]:
        raise RuntimeError("QUALIFICATION_BALANCE_CHANGED")
    OUT.mkdir(parents=True)
    DATA.mkdir(parents=True)
    proposal = dict(schema="s2ob.caller-provisioning.v1", run_id_reserved=RUN_ID,
        event_kinds=list(KINDS), main_execution_authorized=False,
        pcm=dict(format="mono-float32-le", sample_rate=48000, samples=4800,
            expression="(5.0/256.0)*sin((2.0*pi*440.0)*n/48000.0) + (3.0/512.0)*sin((2.0*pi*880.0)*n/48000.0)",
            order="n=0..4799; two products and sum in written Binary64 order; one final float32 packing",
            phase="local zero; exactly the same file for each occurrence"),
        rgb=dict(format="rgb8-row-major", width=1920, height=1080, grid=[12, 8],
            cell_width=160, cell_height=135,
            channels=["32+16*(column%4)", "48+16*(row%4)", "64+8*((row+column)%8)"],
            cue="keep original flattened grid-row/grid-column/RGB indices 0..31; zero indices 32..287 before analysis"),
        producer=dict(path=Path(__file__).relative_to(ROOT).as_posix(), sha256=file_hash(Path(__file__)),
            bytes=Path(__file__).stat().st_size, python=sys.version,
            interpreter_sha256=file_hash(Path(sys.executable)),
            math_origin=math.__spec__.origin,
            math_builtin=math.__spec__.origin == "built-in" and "math" in sys.builtin_module_names,
            math_file_sha256=None if math.__spec__.origin == "built-in" else file_hash(Path(math.__file__))))
    save(OUT / "provisioning.json", seal(proposal, "provisioning_digest"))
    pcm = bytearray()
    for n in range(4800):
        value = (5.0/256.0)*math.sin((2.0*math.pi*440.0)*n/48000.0) + (3.0/512.0)*math.sin((2.0*math.pi*880.0)*n/48000.0)
        pcm.extend(struct.pack("<f", value))
    with (DATA / "window.pcm").open("xb") as stream:
        stream.write(pcm)
    del pcm
    for cue, name in ((False, "full.rgb"), (True, "partial.rgb")):
        # One encoded pixel row at a time; never a collection of full frames.
        with (DATA / name).open("xb") as stream:
            for row in range(8):
                line = bytearray()
                for col in range(12):
                    rgb = [32+16*(col%4), 48+16*(row%4), 64+8*((row+col)%8)]
                    for channel in range(3):
                        if cue and (row*12+col)*3+channel >= 32:
                            rgb[channel] = 0
                    line.extend(bytes(rgb)*160)
                for _ in range(135):
                    stream.write(line)
                del line
    payloads = {name: dict(path=(DATA/name).relative_to(ROOT).as_posix(),
        sha256=file_hash(DATA/name), byte_count=(DATA/name).stat().st_size)
        for name in ("window.pcm", "full.rgb", "partial.rgb")}
    events = []
    for ordinal, kind in enumerate(KINDS, 1):
        event = dict(event_id=f"input-basic-{ordinal:02d}", ordinal=ordinal, kind=kind, **times(ordinal, kind))
        event["pcm"] = None if kind == V else dict(source_id=f"input-pcm-{ordinal:02d}", **payloads["window.pcm"])
        event["rgb"] = None if kind == A else dict(source_id=f"input-rgb-{ordinal:02d}", **payloads["partial.rgb" if kind == V else "full.rgb"])
        events.append(event)
    manifest = seal(dict(schema="s2ob.caller.v2", run_id=RUN_ID, field_clock_id="s2ob-caller-field-clock",
        config_digest="55f1de8602c945749728ce17c74cdff8320d1b5fc72c800f239bc86737db1a1e",
        profile_digest="4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f",
        code_digest=result["code_digest"], events=events), "manifest_digest")
    save(OUT / "manifest.json", manifest)
    evaluation = seal(dict(schema="s2ob.caller-task-expectations.v1", manifest_digest=manifest["manifest_digest"],
        task="finite caller input: formation, repetition, stabilization, read-only retrieval and abstention",
        main_execution_authorized=False,
        decisions=[dict(event_id="input-basic-01", expected="ABSTAIN_NO_CONTEXT", area=None, reason="empty memory"),
            dict(event_id="input-basic-03", expected="ADMIT_SINGLE_CONTEXT", area="A_RECENT", reason="one B4 entry and one equal Fast entry; no stable B"),
            dict(event_id="input-basic-07", expected="ABSTAIN_INTERNAL_AMBIGUITY", area=None, reason="four separately occupied matching B4 entries; no deduplication or B priority")],
        formations=[dict(event_id=f"input-basic-{n:02d}", b4_occupied=i, fast_occupied=1,
            fast_support=min(i, 2), ppb_occupied=0 if i == 1 else 1,
            ppb_support=None if i == 1 else min(i-1, 3), both_modalities_stable=i == 4)
            for i, n in enumerate((2, 4, 5, 6), 1)],
        provenance=dict(formation_events=["input-basic-02", "input-basic-04", "input-basic-05", "input-basic-06"],
            source_relation="intentional exact repetition; each event has a distinct source/time identity",
            generation="derive from transactions; new B4 occupation starts new generation; Fast/PPB MATCHED preserves birth"),
        technical_controls=["one runtime without reset", "all hints read-only", "independent field and memory",
            "atomic formations", "native state reconstruction", "full scans and direct baselines",
            "close preserves field and memory", "all failures before functional evaluation"],
        assessment="each decision and support criterion separately; valid deviations are FALSIFIED, not technical failure",
        exclusions=["stable B public retrieval after A eviction", "variants", "competition with different contents",
            "general robustness", "live input", "prediction", "hypothesis application"]), "evaluation_digest")
    save(OUT / "evaluation-plan.json", evaluation)
    # This administrative ledger charges input bindings as well as future closure files.
    sizes = {p.name: p.stat().st_size for p in OUT.iterdir() if p.is_file()}
    caps = dict(states=5*98304, inputs=7*16384, steps=7*16384, scans=6*32767,
        nj=5*1024, formations=4*1536, generations=4*1536,
        sources=174080, metadata=65536, verification=262144)
    metadata = dict(runtime_metadata=24576, manifest=8192, evaluation_plan=8192,
        provisioning_and_binding=6144, future_evaluation=4096, future_final_balance=4096,
        qualification=4096, report=512)
    total = sum(caps.values())
    shared = sum(caps[k] for k in ("sources", "nj", "formations", "generations"))
    ledger = seal(dict(schema="s2ob.caller-input-budget.v1", manifest_digest=manifest["manifest_digest"],
        evaluation_digest=evaluation["evaluation_digest"], counts=dict(events=7, formations=4, auditory_cues=1,
            visual_cues=2, audio=5, nj=5, visual=6, payload_reads=11, field_contacts=1968, scan_receipts=6),
        prerequisite=dict(qualification_path=QUAL.relative_to(ROOT).as_posix(),
            result_digest=result["result_digest"], code_inventory_digest=result["code_digest"],
            code_inventory_bytes=(QUAL/"code-inventory.json").stat().st_size,
            qualification_bytes=3131, qualification_reserve=4096),
        input_files=payloads, intentional_equal_source_groups=[
            ["input-pcm-02", "input-pcm-03", "input-pcm-04", "input-pcm-05", "input-pcm-06"],
            ["input-rgb-02", "input-rgb-04", "input-rgb-05", "input-rgb-06"],
            ["input-rgb-01", "input-rgb-07"]],
        raw_input_storage_bytes=sum(p["byte_count"] for p in payloads.values()),
        raw_input_read_bytes=5*19200+6*6220800,
        raw_input_boundary="caller input files outside evidence envelope; one payload at a time; not embedded in runtime records",
        preparation_files_bytes=sizes, source_attachments=dict(producer_file_bytes=Path(__file__).stat().st_size),
        caps=caps, metadata_reservations=metadata, metadata_reservation_total=sum(metadata.values()),
        total_upper_bound=total, shared_upper_bound=shared,
        limits=dict(total=4194304, shared=262144, metadata=65536, state=98304),
        future_read_only_verification=dict(state_validation_passes=116, formation_count=4,
            fast_selection_comparisons=20160, ppb_target_comparisons=30720,
            update_relation_comparisons=13440, scan_comparisons=11712,
            boundary="existing per-verification ceilings retained separately; no recalculation now"),
        gates=False, preparation_is_not_runtime_or_qualification=True), "binding_digest")
    save(OUT / "binding.json", ledger)
    binding_bytes = (OUT/"binding.json").stat().st_size
    if (sizes["manifest.json"] > 8192 or sizes["evaluation-plan.json"] > 8192
        or sizes["provisioning.json"]+binding_bytes > 6144 or sum(metadata.values()) > 65536
        or total > 4194304 or shared > 262144
        or Path(__file__).stat().st_size+(QUAL/"code-inventory.json").stat().st_size > 174080):
        raise RuntimeError("INPUT_BINDING_BUDGET_EXCEEDED")
    print(json.dumps(dict(manifest_digest=manifest["manifest_digest"], binding_digest=ledger["binding_digest"],
        files={**sizes, "binding.json": binding_bytes}, total_upper_bound=total,
        shared_upper_bound=shared, metadata_reserved=sum(metadata.values()), gates=False)))


if __name__ == "__main__":
    main()
