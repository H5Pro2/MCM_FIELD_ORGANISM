"""Bound preparation, then exactly one new neutral unittest invocation."""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys

from tools import _s2oc_shared_binding as s
from tools import _s2oc_shared_verification as v

b=s.b
QFILES=("preregistration.json","stdout.txt","stderr.txt","metrics.json","result.json","final-balance.json")


def synthetic_manifest(inv):
    events=[]
    for n in range(1,22):
        kind=b.V if n in (2,15,21) else b.AV
        rgb=b.Payload(f"synthetic-visual-{n}","reports/s2oc/unread-synthetic-rgb.bin","0"*64,6220800)
        pcm=None if kind==b.V else b.Payload(f"synthetic-audio-{n}","reports/s2oc/unread-synthetic-pcm.bin","0"*64,19200)
        events.append(b.Event(f"synthetic-event-{n}",n,kind,**b.expected_times(n,kind),pcm=pcm,rgb=rgb))
    return b.build_manifest("synthetic-complete-memory-cycle",tuple(events),b.digest(inv["ob"]))


def balance(out, ownrefs, *, final_bytes=0):
    files={p.relative_to(out).as_posix():p.stat().st_size for p in out.rglob("*") if p.is_file()}
    if final_bytes:files["final-balance.json"]=final_bytes
    native=0;shared_native=dict(nj=0,formations=0,generations=0)
    for folder in ("success","failure"):
        if not (out/folder/"record.json").exists():continue
        c=s.load_common(out/folder)
        r,q=s.unpack(s.read_json(out/folder/"record.json"),s.read_json(out/folder/"session.json"),c)
        p=s.ledger(r,q,c)["contributions"]
        native+=sum(p["native"].values())+p["prefix_steps"]
        for k in shared_native:shared_native[k]+=p["native"].get(k,0)
    own=sum(ref[2] for ref in ownrefs)
    source=files.get("inventory.json",0)+own
    proof=sum(size for name,size in files.items() if name.endswith(("verification.json","verification.claim")))
    physical=sum(files.values())+own
    qbytes=sum(files.get(n,0) for n in QFILES)
    reserve=max(0,4096-qbytes)+max(0,512-files.get("BEFUND.md",0))
    totals=dict(metadata=physical-native-source-proof+reserve,sources=source,
        verification=proof,**shared_native,shared=source+sum(shared_native.values()),total=physical+reserve)
    violations=[k.upper()+"_LIMIT" for k,n in totals.items() if n>b.LIMITS[k]]
    if qbytes>4096:violations.append("QUALIFICATION_LIMIT")
    for name,cap in s.QUAL_CAPS.items():
        if files.get(name,0)>cap:violations.append("QUALIFICATION_PART_LIMIT:"+name)
    for folder in ("success","failure"):
        if files.get(folder+"/verification.json",0)+files.get(folder+"/verification.claim",0)>16384:
            violations.append("NEUTRAL_PROOF_LIMIT")
    return dict(files=files,physical=physical,qualification_bytes=qbytes,reserve=reserve,
        own_source_bytes=own,native_bytes=native,totals=totals,violations=violations)


def neutral_header_bound(inv, inventory_ref):
    sizes=[]
    for kinds in ((b.AV,b.A),(b.A,b.AV)):
        events=[]
        for n,kind in enumerate(kinds,1):
            pcm=b.Payload("a"*79+str(n),"reports/s2oc/"+"p"*100+".bin","0"*64,19200)
            rgb=b.Payload("v"*79+str(n),"reports/s2oc/"+"r"*100+".bin","0"*64,6220800) if kind==b.AV else None
            events.append(b.Event("e"*79+str(n),n,kind,**b.expected_times(n,kind),pcm=pcm,rgb=rgb))
        m=b.build_manifest("q"*80,tuple(events),b.digest(inv["ob"]))
        c=s.build_common(m,inv,[inventory_ref])
        sizes.extend(s.ledger(*pair,c)["totals"]["metadata"]-512 for pair in v.synthetic_forms(c,2))
    return max(sizes)


def main():
    out=b.ROOT/"reports/s2oc"/s.QUAL_ID
    if out.exists():raise RuntimeError("QUALIFICATION_ID_USED")
    names=sorted(n.name for n in ast.walk(ast.parse((b.ROOT/s.OWN[4]).read_text(encoding="utf-8")))
                 if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    if len(names)!=26:raise RuntimeError("TEST_INVENTORY_INVALID")
    inv=s.inventory()
    out.mkdir()
    s.prior.save(out/"inventory.json",inv)
    ownrefs=[s.file_reference("sources",b.ROOT/p) for p in s.OWN]
    refs=[s.file_reference("sources",out/"inventory.json"),*ownrefs]
    # Full new qualification allowance is visible in the future run binding.
    refs.extend(["metadata",(out/name).relative_to(b.ROOT).as_posix(),cap,"0"*64] for name,cap in s.QUAL_CAPS.items())
    qref=next(ref for ref in refs if ref[1].endswith("/result.json"))
    common=s.build_common(synthetic_manifest(inv),inv,refs,qref)
    s.prior.save(out/"bound-common.json",common)
    upper=v.preflight(common)
    s.prior.save(out/"bounds.json",upper)
    # Complete maximum native output for one 2-event success and one error prefix.
    native=2*98304+2*16384+3*16384+2*32767+2*1024+1536+1536
    header=neutral_header_bound(inv,refs[0])
    meta_fixed=len(b.canonical(common))+len(b.canonical(upper))+4096+512
    qbound=dict(metadata=meta_fixed+2*header+768+1536+512,sources=len(b.canonical(inv))+sum(r[2] for r in ownrefs),
        verification=32768,nj=2048,formations=1536,generations=1536)
    qbound["shared"]=qbound["sources"]+qbound["nj"]+qbound["formations"]+qbound["generations"]
    qbound["total"]=native+qbound["metadata"]+qbound["sources"]+qbound["verification"]
    pr=dict(run_id=s.QUAL_ID,expected_tests=26,test_inventory_digest=b.digest(names),source_digest=b.digest(inv),
        source_inventory_sha256=s.sha(b.canonical(inv)),test_calls=1,retry=False,
        qualification_reserve=4096,report_reserve=512,qualification_bound=qbound,
        bound_common_sha256=s.sha(b.canonical(common)),bounds_sha256=s.sha(b.canonical(upper)),
        work=dict(synthetic_positions=22,synthetic_alternatives=44,neutral_events=3,audio=3,nj=3,visual=2,
                  native_verifications=1,failure_verifications=1,real_payload_reads=0))
    s.prior.save(out/"preregistration.json",pr)
    violations=[k.upper()+"_LIMIT" for k,n in qbound.items() if n>b.LIMITS[k]]
    if len(b.canonical(pr))>s.QUAL_CAPS["preregistration.json"]:
        violations.append("QUALIFICATION_PART_LIMIT:preregistration.json")
    if upper["violations"] or violations:
        s.prior.save(out/"precondition-stop.json",dict(test_calls=0,qualification_bound=qbound,
            violations=violations,run_violations=upper["violations"]))
        print(json.dumps(dict(status="PRECONDITION_BLOCKED",test_calls=0,qualification_bound=qbound,violations=violations,
                             run_violations=upper["violations"])))
        return 2
    print(json.dumps(dict(phase="PRE_TEST",test_calls=1,source_digest=b.digest(inv),qualification_bound=qbound)),flush=True)
    env=dict(os.environ,OC_SHARED_OUT=str(out))
    proc=subprocess.run([sys.executable,"-m","unittest","tests.test_s2oc_shared_closure"],cwd=b.ROOT,
                        env=env,capture_output=True,check=False)
    for name,raw in (("stdout.txt",proc.stdout),("stderr.txt",proc.stderr)):
        with (out/name).open("xb") as f:f.write(raw)
    met=s.read_json(out/"metrics.json") if (out/"metrics.json").exists() else None
    expected=dict(sessions=2,audio=3,nj=3,visual=2,core_verifications=1,failure_verifications=1,gates=False)
    unchanged=inv==s.inventory()
    log=(proc.stdout+proc.stderr).decode("utf-8",errors="replace")
    passed=proc.returncode==0 and "Ran 26 tests" in log and log.rstrip().endswith("OK") and met==expected and unchanged
    result=b.sealed(dict(run_id=s.QUAL_ID,status="QUALIFIED" if passed else "NOT_QUALIFIED",test_calls=1,
        expected_tests=26,passed_tests=26 if passed else None,exit_code=proc.returncode,
        source_digest=b.digest(inv),hashes_unchanged=unchanged,gates=False,budget_violations=[],
        evidence={**{n:s.sha((out/n).read_bytes()) for n in ("preregistration.json","stdout.txt","stderr.txt","metrics.json")
                  if (out/n).exists()},"final-balance.json":"0"*64}),"result_digest")
    # Result and final ledger are prepared together, including their own lengths.
    estimate=0
    for _ in range(16):
        current=balance(out,ownrefs,final_bytes=estimate)
        rb=len(b.canonical(result))
        current["files"]["result.json"]=rb
        current["physical"]+=rb
        before=current["qualification_bytes"];current["qualification_bytes"]+=rb
        growth=max(0,before+rb-4096)-max(0,before-4096)
        current["reserve"]-=min(rb,max(0,4096-before))
        for k in ("metadata","total"):current["totals"][k]+=growth
        if current["qualification_bytes"]>4096 and "QUALIFICATION_LIMIT" not in current["violations"]:
            current["violations"].append("QUALIFICATION_LIMIT")
        if rb>s.QUAL_CAPS["result.json"]:
            current["violations"].append("QUALIFICATION_PART_LIMIT:result.json")
        current["violations"]=list(dict.fromkeys(current["violations"]))
        for k,value in current["totals"].items():
            if value>b.LIMITS[k] and k.upper()+"_LIMIT" not in current["violations"]:
                current["violations"].append(k.upper()+"_LIMIT")
        result= b.sealed({**{k:v for k,v in result.items() if k!="result_digest"},
            "status":"QUALIFIED" if passed and not current["violations"] else "NOT_QUALIFIED",
            "budget_violations":current["violations"]},"result_digest")
        size=len(b.canonical(current))
        if size==estimate and rb==len(b.canonical(result)):break
        estimate=size
    else:raise RuntimeError("FINAL_SIZE_UNSTABLE")
    result["evidence"]["final-balance.json"]=s.sha(b.canonical(current))
    result=b.sealed({k:v for k,v in result.items() if k!="result_digest"},"result_digest")
    s.prior.save(out/"result.json",result)
    s.prior.save(out/"final-balance.json",current)
    print(json.dumps(dict(status=result["status"],metrics=met,actual=current)),flush=True)
    return 0 if result["status"]=="QUALIFIED" else 1


if __name__=="__main__":
    raise SystemExit(main())
