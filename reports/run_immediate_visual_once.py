"""File-bound, explicitly authorized one-shot control. Never invoked on import."""
import argparse
import hashlib
import json
from pathlib import Path
import traceback
from tools import _s2oe_immediate_visual_input as p
from tools import _s2oe_immediate_visual_control as control
from tools import _s2oe_immediate_visual_verification as verification

MAIN_GATE=False
CAPS={"record.json":("data",393216),"partial.json":("data",393216),
      "verification.json":("verification",8192),"evaluation.json":("metadata",8192),
      "close.json":("metadata",2048),"failure.json":("metadata",8192),
      "balance.json":("metadata",4096),"run.claim":("metadata",5),"verification.claim":("metadata",5)}


def measure(b,binding_bytes,directory,prospective=None):
    parts=dict(metadata=binding_bytes,sources=0,verification=0,supplement=0,data=0)
    seen=set()
    for ref in b["artifacts"]:
        path=(p.ROOT/ref["path"]).resolve()
        p.need(ref["kind"] in ("metadata","sources","verification"),"REFERENCE_CLASS_INVALID")
        if path in seen: continue
        seen.add(path)
        parts[ref["kind"]]+=path.stat().st_size
    files={f.name:f.stat().st_size for f in directory.iterdir() if f.is_file()} if directory.exists() else {}
    if prospective: files.update(prospective)
    overs=[]
    for name,size in files.items():
        p.need(name in CAPS,"OUTPUT_CLASS_INVALID")
        kind,limit=CAPS[name];parts[kind]+=size
        if size>limit: overs.append(name)
    result=p.balance(p.ParentBinding(**b["parent"]),**parts)
    result["files"]=files
    result["violations"]+=overs
    return result


def preflight(b,binding_bytes,directory):
    alternatives=( ("run.claim","record.json","verification.claim","verification.json","evaluation.json","close.json","balance.json"),
                   ("run.claim","partial.json","failure.json","balance.json"),
                   ("run.claim","record.json","verification.claim","verification.json","evaluation.json","failure.json","balance.json"))
    balances=[measure(b,binding_bytes,directory,{n:CAPS[n][1] for n in names}) for names in alternatives]
    for balance in balances: p.enforce_balance(balance)
    return balances


def final_balance(b,binding_bytes,directory):
    size=0
    for _ in range(16):
        result=measure(b,binding_bytes,directory,{"balance.json":size})
        new_size=len(p.canonical(result))
        if new_size==size: return result
        size=new_size
    raise p.InputError("BALANCE_SIZE_UNSTABLE")


def publish(path, value):
    data=p.canonical(value)
    temp=path.with_suffix(path.suffix+".tmp")
    with temp.open("xb") as f:
        f.write(data)
    p.need(not path.exists(),"OUTPUT_EXISTS")
    temp.rename(path)


def execute(binding_path, *, neutral=False, fault=None):
    p.need(MAIN_GATE,"MAIN_GATE_CLOSED")
    binding_raw=Path(binding_path).read_bytes();b=json.loads(binding_raw)
    p.need(b["version"]=="s2oe.immediate-run-binding.v1" and b["status"]=="READY_REQUIRES_AUTHORIZATION",
           "RUN_BINDING_INVALID")
    for name, expected in b["files"].items():
        data=(p.ROOT/name).read_bytes()
        p.need(len(data)==expected[1] and hashlib.sha256(data).hexdigest()==expected[0],"ACTIVE_FILE_CHANGED")
    directory=p.ROOT/b["output_directory"]
    p.need(not directory.exists(),"OUTPUT_EXISTS")
    parent=p.ParentBinding(**b["parent"])
    parent.validate()
    p.need(parent.neutral is neutral and (neutral or fault is None),"PARENT_MODE_INVALID")
    for ref in b["artifacts"]:
        data=(p.ROOT/ref["path"]).read_bytes()
        p.need(p.sha(data)==ref["sha256"],"ACTIVE_REFERENCE_CHANGED")
    preflight(b,len(binding_raw),directory)
    directory.mkdir()
    (directory/"run.claim").write_bytes(b"once\n")
    phase="INPUT"; record=None; reads=dict(bytes=0,operations=0)
    latest=dict(phase="NOT_STARTED",completed_events=0,states=[],scans=[],field_calls=0)
    def checked_publish(name,value):
        measured=measure(b,len(binding_raw),directory,{name:len(p.canonical(value))})
        p.enforce_balance(measured)
        publish(directory/name,value)
    def checkpoint(blob):
        nonlocal latest
        latest=json.loads(blob)
        p.enforce_balance(measure(b,len(binding_raw),directory,{"partial.json":len(blob)}))
        if fault is not None: fault(latest["phase"])
    try:
        excerpt=p.read_extract(parent,reads)
        phase="CONTROL"
        control.MAIN_GATE=True
        try:
            record=control.run(excerpt,parent,run_id=b["run_id"],neutral=neutral,progress=checkpoint)
        finally:
            control.MAIN_GATE=False
        p.need(len(p.canonical(record))<=393216,"RECORD_SIZE_LIMIT")
        phase="PUBLISH"
        checked_publish("record.json",record)
        phase="VERIFY"
        (directory/"verification.claim").write_bytes(b"once\n")
        raw=(Path(parent.path) if parent.neutral else p.ROOT/parent.path).read_bytes();reads["bytes"]+=len(raw);reads["operations"]+=1
        proof=verification.verify(record,parent,raw,b["run_id"])
        p.need(len(p.canonical(proof))<=262144,"PROOF_SIZE_LIMIT")
        checked_publish("verification.json",proof)
        phase="EVALUATE"
        evaluation=verification.evaluate(record,proof)
        p.need(len(p.canonical(evaluation))<=8192,"EVALUATION_SIZE_LIMIT")
        checked_publish("evaluation.json",evaluation)
        checked_publish("close.json",dict(status="CLOSED",evaluation_allowed=True,gates=False,
            parent_read_bytes=reads["bytes"]+record["reads"]["bytes"],parent_read_operations=3))
        checked_publish("balance.json",final_balance(b,len(binding_raw),directory))
    except Exception as exc:
        failure=dict(status="NOT_EVALUABLE",phase=phase,
            code=getattr(exc,"code",type(exc).__name__),message=str(exc),traceback=traceback.format_exc(),
            last_completed_phase=latest["phase"],completed_events=latest["completed_events"],
            evaluation_allowed=False,record_published=(directory/"record.json").exists(),gates=False,
            budget=getattr(exc,"balance",None),secondary_errors=[])
        try:
            if not (directory/"record.json").exists():
                publish(directory/"partial.json",latest)
            measured=measure(b,len(binding_raw),directory,{"failure.json":len(p.canonical(failure)),"balance.json":4096})
            failure["budget_at_failure"]=measured
            # Preserve the primary error even when the failure itself exceeds a cap.
            publish(directory/"failure.json",failure)
            publish(directory/"balance.json",final_balance(b,len(binding_raw),directory))
        except Exception as closing:
            failure["secondary_errors"].append(dict(type=type(closing).__name__,message=str(closing)))
            print(json.dumps(failure,ensure_ascii=True),file=__import__("sys").stderr)
        raise
    finally:
        control.MAIN_GATE=False


if __name__=="__main__":
    args=argparse.ArgumentParser()
    args.add_argument("--binding",required=True)
    args.add_argument("--authorized-once",action="store_true",required=True)
    parsed=args.parse_args()
    MAIN_GATE=parsed.authorized_once
    try:
        execute(parsed.binding)
    finally:
        MAIN_GATE=False
