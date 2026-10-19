"""Bind existing caller files and the proposed seven-event comparison; no execution."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUN_ID="memory-restart-transfer-20260912-01"
DEST=ROOT/"reports"/RUN_ID
BINDING=ROOT/"reports/memory-restart-transfer-binding-20260912-01"


def canonical(value):return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")
def sha(data):return hashlib.sha256(data).hexdigest()
def reference(path):
    raw=path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(),bytes=len(raw),sha256=sha(raw))


def prepare():
    if DEST.exists() or BINDING.exists():raise RuntimeError("unused binding/output required")
    old=json.loads((ROOT/"reports/s2ob/caller-input-binding/manifest.json").read_bytes())
    pcm=old["events"][1]["pcm"];rgb=old["events"][1]["rgb"];cue=old["events"][0]["rgb"]
    sources=[]
    for p in (pcm,rgb,cue):
        item=reference(ROOT/p["path"])
        if (item["bytes"],item["sha256"])!=(p["byte_count"],p["sha256"]):raise RuntimeError("source changed")
        sources.append(item)
    base=ROOT/"reports/memory-checkpoint-qualification-20260912-02"
    focus=ROOT/"reports/memory-checkpoint-focus-20260912-01"
    q=json.loads((base/"preregistration.json").read_bytes())
    for name,expected in q["inventory"]["files"].items():
        actual=reference(ROOT/name)
        if (actual["bytes"],actual["sha256"])!=(expected["bytes"],expected["sha256"]):raise RuntimeError("qualified code changed")
    qualification=dict(base=[reference(base/n) for n in ("preregistration.json","result.json","qualification.stderr","REPORT.md","final-ledger.json")],
        supplement=[reference(focus/n) for n in ("preregistration.json","result.json","stderr.log","REPORT.md","final-ledger.json")],
        scope="21 passed base groups plus four independent supplementary controls; base remains NOT_QUALIFIED")
    inventory=dict(qualified_inventory=q["inventory"],binding_preparer=reference(Path(__file__).resolve()))
    events=[]
    for g,kind in enumerate(["COMPLETE_AV_PERCEPTION"]*4+["PARTIAL_AUDITORY_CUE","PARTIAL_VISUAL_CUE","COMPLETE_AV_PERCEPTION"]):
        audio=kind!="PARTIAL_VISUAL_CUE";visual=kind!="PARTIAL_AUDITORY_CUE"
        def role(p,m):return dict(path=p["path"],byte_count=p["byte_count"],sha256=p["sha256"],source_id=f"restart-{m}-{g+1:02d}")
        events.append(dict(event_id=f"restart-event-{g+1:02d}",ordinal=g+1,kind=kind,
            field_window=[0 if g==0 else 200000000*g-100000000,200000000*g+100000000],
            audio_window=[9600*g,9600*g+4800] if audio else None,audio_index=20*g if audio else None,
            audio_common=[200000000*g,200000000*g+100000000] if audio else None,
            visual_window=[6*g+2,6*g+3] if visual else None,
            visual_common=[(6*g+2)*1000000000//30,200000000*g+100000000] if visual else None,
            pcm=role(pcm,"pcm") if audio else None,rgb=role(cue if kind=="PARTIAL_VISUAL_CUE" else rgb,"rgb") if visual else None))
    manifest=dict(schema=old["schema"],run_id=RUN_ID,field_clock_id=old["field_clock_id"],
        config_digest=old["config_digest"],profile_digest=old["profile_digest"],code_digest=sha(canonical(inventory)),events=events)
    manifest["manifest_digest"]=sha(canonical(manifest))
    evaluation=dict(schema="checkpoint.function-comparison.v1",manifest_digest=manifest["manifest_digest"],
        task="same valid continuation after process restart",checkpoint_after=4,
        states_to_compare=["field","memory","slot_generations","source_times","runtime_times","expiry_counters","read_accounts"],
        decision_events=[5,6],expectation="equal to uninterrupted arm, including valid abstention",
        allowed_differences=["process_id","OS lock identities","physical output path","checkpoint IO and consume proof"],
        unchanged=["logical runtime ID","manifest","event IDs","logical owner/consume IDs and their used evidence"],
        main_authorized=False)
    plan=dict(status="INPUT_BOUND_NOT_EXECUTABLE",run_id=RUN_ID,output=DEST.relative_to(ROOT).as_posix(),
        output_absent=True,source_reuse="Three unchanged previously investigated OB caller files; not an independent corpus.",
        sources=sources,qualification=qualification,checkpoint=dict(after_event=4,field_class="FIELD_CHECKPOINT.v1",field_cap=524288),
        counts_per_arm=dict(events=7,formations=5,audio=6,nj=6,visual=6,read_only_hints=2,field_contacts=2016,scans=4),
        input_stock_bytes=sum(p["bytes"] for p in sources),planned_read_bytes_per_arm=sum(p["byte_count"] for e in events for p in (e["pcm"],e["rgb"]) if p),
        active_entry=None,admission_created=False,
        missing=["Versioned real-worker admission and ordered process-exit handoff.",
                 "One independent total verification entry and separate comparison evaluator.",
                 "Reachable success/error artifact upper bounds with all active admission dependencies; no sum of mutually exclusive phases."],
        main_gate=False)
    BINDING.mkdir()
    for name,value in (("manifest.json",manifest),("inventory.json",inventory),("evaluation-plan.json",evaluation),("binding.json",plan)):
        (BINDING/name).write_bytes(canonical(value))
    print(json.dumps(dict(run_id=RUN_ID,status=plan["status"],manifest_digest=manifest["manifest_digest"],
        counts=plan["counts_per_arm"],input_stock=plan["input_stock_bytes"],read_bytes_per_arm=plan["planned_read_bytes_per_arm"],
        files=[reference(p) for p in sorted(BINDING.iterdir())]),indent=2))


if __name__=="__main__":prepare()
