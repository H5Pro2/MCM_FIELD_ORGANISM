"""Prebind and run only the missing read-only controls, once."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/"reports/memory-checkpoint-qualification-20260912-02"
OUT=ROOT/"reports/memory-checkpoint-focus-20260912-01"
OWN=("tests/test_checkpoint_roundtrip_focus.py","reports/qualify_checkpoint_focus_once.py")


def canonical(value):return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")
def binding(path):
    raw=path.read_bytes()
    return dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def validate_old():
    prereg=json.loads((OLD/"preregistration.json").read_bytes())
    for name,expected in prereg["inventory"]["files"].items():
        if binding(ROOT/name)!=expected:raise RuntimeError("historical qualified source changed: "+name)
    return prereg


def prepare():
    if OUT.exists():raise RuntimeError("unused directory required")
    prior=validate_old()
    old=json.loads((OLD/"final-ledger.json").read_bytes())
    own={p:binding(ROOT/p) for p in OWN}
    refs={p.name:binding(p) for p in OLD.iterdir() if p.is_file()}
    reserves=dict(preregistration=8192,stdout_stderr=8192,result=2048,report=3072,ledger=4096,claim=4)
    source=sum(x["bytes"] for x in own.values())
    totals=dict(old["totals"])
    totals["metadata"]+=sum(reserves.values())
    for key in ("sources","shared"):totals[key]+=source
    totals["total"]+=sum(reserves.values())+source
    limits=old["limits"]
    violations=[k for k,cap in limits.items() if totals[k]>cap]
    value=dict(status="READY" if not violations else "PRECONDITION_STOP",test_calls=0,
        tests=["test_native_types","test_memory_canonical_roundtrip","test_field_canonical_roundtrip","test_evidence_unchanged"],
        own=own,old_evidence=refs,old_code_digest=prior["code_digest"],reserves=reserves,
        upper=totals,limits=limits,violations=violations,
        work=dict(checkpoint_validations=4,formations=0,field_steps=0,receptor_analyses=0,
                  process_replays=0,old_test_groups=0),
        scope="Complementary read-only coverage; historical 21/22 remains NOT_QUALIFIED.")
    if len(canonical(value))>reserves["preregistration"]:raise RuntimeError("preregistration reserve exceeded")
    OUT.mkdir();(OUT/"preregistration.json").write_bytes(canonical(value))
    print(json.dumps(value,indent=2))


def run():
    q=json.loads((OUT/"preregistration.json").read_bytes())
    validate_old()
    if q["status"]!="READY":raise RuntimeError("precondition not met")
    for name,expected in q["old_evidence"].items():
        if binding(OLD/name)!=expected:raise RuntimeError("old evidence changed")
    for name,expected in q["own"].items():
        if binding(ROOT/name)!=expected:raise RuntimeError("focus code changed")
    with (OUT/"invocation.claim").open("xb") as f:f.write(b"once")
    with (OUT/"stdout.log").open("xb") as out,(OUT/"stderr.log").open("xb") as err:
        p=subprocess.run([sys.executable,"-m","unittest","tests.test_checkpoint_roundtrip_focus","-v"],
                         cwd=ROOT,stdout=out,stderr=err,check=False)
    validate_old()
    unchanged=all(binding(ROOT/n)==v for n,v in q["own"].items())
    logs=(OUT/"stdout.log").stat().st_size+(OUT/"stderr.log").stat().st_size
    value=dict(status="QUALIFIED" if p.returncode==0 and unchanged and logs<=q["reserves"]["stdout_stderr"] else "NOT_QUALIFIED",
        test_calls=1,exit_code=p.returncode,hashes_unchanged=unchanged,log_bytes=logs,
        evidence={p.name:binding(p) for p in OUT.iterdir() if p.is_file()},gates=False)
    (OUT/"result.json").write_bytes(canonical(value));print(json.dumps(value,indent=2))


if __name__=="__main__":
    {"prepare":prepare,"run":run}[sys.argv[1]]()
