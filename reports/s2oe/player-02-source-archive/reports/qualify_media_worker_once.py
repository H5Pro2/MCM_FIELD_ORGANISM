"""One prebound neutral worker qualification; no selected media access."""
import ast
from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

from tools import _s2oe_media_session as m
from tools import _s2oc_shared_verification as shapes
from tools._s2oe_decoder_worker import resource_profile
from reports.prepare_direct_media_budget import META_PARTS

p,b,s=m.p,m.b,m.s
OUT=b.ROOT/"reports/s2oe"/m.QUAL_ID
QFILES=("preregistration.json","stdout.txt","stderr.txt","result.json","final-balance.json")
QCLOSURE=14336
RESOURCE_FILES=6*1024
FOLDERS=("native-full","native-blocked","native-exit")


def fixture_binding(inventory_ref, src=None):
    base_dir=b.ROOT/"reports/s2oc"/s.QUAL_ID
    anchor=s.read_json(base_dir/"caller-common.json")
    base,inv=s.qualified_common(b.decode_manifest(anchor["manifest"]),base_dir)
    run_id="q"*80 if src is None else "worker-neutral-"+Path(src.path).stem
    if src is None:
        src=p.Source(str(b.ROOT/"sources/s2oe-worker-neutral"/m.QUAL_ID/("x"*24+".bin")),"0"*64,32)
    manifest=p.build(run_id,src,b.digest(m.inventory()))
    refs=base["references"]+[s.file_reference("sources",b.ROOT/n) for n in m.OWN
        if not any(ref[1]==n for ref in base["references"])]
    refs += [s.file_reference("metadata",base_dir/"caller-common.json"),inventory_ref]
    return m.bind_common(manifest,base,refs),inv


def with_media(pair,n):
    record,session=pair
    record.pop("record_digest")
    record["media"]=dict(receipts=["x"*510 for _ in range(min(n+1,24))],
        decoder="x"*900,resources="x"*1120)
    record=b.sealed(record,"record_digest")
    session.pop("session_digest")
    session["record_digest"]=record["record_digest"]
    return record,b.sealed(session,"session_digest")


def preflight(common):
    # Media receipts/resources are in the synthetic record, not an additional copy.
    reserve=tuple(("metadata",k,v) for k,v in META_PARTS.items()
        if k not in ("@selection-receipts","@decoder-counter-and-closure"))
    positions=[]
    for n in range(25):
        alternatives={}
        for name,pair in zip(("success","failure"),shapes.synthetic_forms(common,n)):
            row=p.ledger(*with_media(pair,n),common,attachments=reserve)
            alternatives[name]=dict(totals=row["totals"],violations=row["violations"])
        positions.append(dict(completed=n,**alternatives))
    return dict(positions=positions,limits=p.SESSION_LIMITS,
        maxima={k:max(x[a]["totals"][k] for x in positions for a in ("success","failure"))
            for k in p.SESSION_LIMITS},
        violations=[dict(completed=x["completed"],alternative=a,violations=x[a]["violations"])
            for x in positions for a in ("success","failure") if x[a]["violations"]])


def qualification_bound(common):
    refs=common["references"]
    source=sum(n for k,_,n,_ in refs if k=="sources")
    refmeta=sum(n for k,_,n,_ in refs if k=="metadata")
    metadata=native=0
    parts=dict(nj=0,formations=0,generations=0)
    for n,a in ((24,0),(1,1),(1,1)):
        row=p.ledger(*with_media(shapes.synthetic_forms(common,n)[a],n),common,
            attachments=(),proof_bytes=0,report_bytes=0)
        if row["violations"]:
            raise p.MediaError("QUALIFICATION_SESSION_LIMIT",row)
        metadata+=row["totals"]["metadata"]-refmeta
        native+=sum(row["contributions"]["native"].values())+row["contributions"]["prefix_steps"]
        for key in parts:
            parts[key]+=row["totals"][key]
    metadata+=refmeta+QCLOSURE+512+RESOURCE_FILES
    totals=dict(metadata=metadata,sources=source,verification=262144,**parts)
    totals.update(shared=source+sum(parts.values()),total=metadata+source+native+262144)
    return dict(totals=totals,limits=p.QUAL_LIMITS,native=native,
        qualification_and_report=QCLOSURE+512,resource_evidence=RESOURCE_FILES,
        violations=[k for k,v in totals.items() if v>p.QUAL_LIMITS[k]])


def actual(common,pending=None):
    files={str(f.relative_to(OUT)).replace("\\","/"):f.stat().st_size for f in OUT.rglob("*") if f.is_file()}
    files.update(pending or {})
    native=0
    parts=dict(nj=0,formations=0,generations=0)
    for folder in FOLDERS:
        directory=OUT/folder
        if not (directory/"record.json").exists():
            continue
        c=s.load_common(directory)
        rec,sess=s.unpack(s.read_json(directory/"record.json"),s.read_json(directory/"session.json"),c)
        contribution=p.ledger(rec,sess,c)["contributions"]
        native+=sum(contribution["native"].values())+contribution["prefix_steps"]
        for k in parts:
            parts[k]+=contribution["native"].get(k,0)
    proof=sum(n for name,n in files.items() if name.endswith(("verification.json","verification.claim")))
    external=[r for r in common["references"] if not (b.ROOT/r[1]).is_relative_to(OUT)]
    sources=sum(r[2] for r in common["references"] if r[0]=="sources")
    physical=sum(files.values())+sum(r[2] for r in external)
    qbytes=sum(files.get(n,0) for n in QFILES)
    resourcebytes=sum(n for name,n in files.items() if name.endswith("-resources.json") or name.startswith("access-markers/"))
    reserve=max(0,QCLOSURE-qbytes)+max(0,RESOURCE_FILES-resourcebytes)+512
    totals=dict(metadata=physical-native-proof-sources+reserve,sources=sources,
        verification=proof,**parts,shared=sources+sum(parts.values()),total=physical+reserve)
    return dict(files=files,totals=totals,qualification_bytes=qbytes,resource_bytes=resourcebytes,
        remaining_reserve=reserve,violations=[k for k,v in totals.items() if v>p.QUAL_LIMITS[k]]
        +(["qualification"] if qbytes>QCLOSURE else [])+(["resources"] if resourcebytes>RESOURCE_FILES else []))


def main():
    if OUT.exists():
        raise RuntimeError("QUALIFICATION_ID_USED")
    sources=m.inventory()
    invraw=b.canonical(sources)
    invref=["sources",str((OUT/"inventory.json").relative_to(b.ROOT)).replace("\\","/"),len(invraw),s.sha(invraw)]
    common,_=fixture_binding(invref)
    upper=preflight(common)
    qbound=qualification_bound(common)
    tree=ast.parse((b.ROOT/"tests/test_s2oe_worker.py").read_text(encoding="utf-8"))
    tests=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    # Bind every progress position through a compact fixed-column table.
    keys=list(p.SESSION_LIMITS)
    prereg=dict(run_id=m.QUAL_ID,tests=tests,source_inventory_sha256=invref[3],
        budget_version=p.VERSION,resource_profile=resource_profile(),qualification_bound=qbound,
        environment=dict(executable=sys.executable,python=sys.version,windows=list(sys.getwindowsversion())),
        session_limits=p.SESSION_LIMITS,run_maxima=upper["maxima"],
        closure_columns=keys,closure_positions=[[x["completed"]]+[
            [x[a]["totals"][k] for k in keys] for a in ("success","failure")] for x in upper["positions"]],
        work=dict(native_sessions=3,formations=22,cues=4,native_audio_nj=24,native_visual=24,
            native_verifications=1,failure_binding_checks=2,real_media_reads=0,
            worker_processes_max=13,allocation_overloads=1,unmodified_timeout_checks=1),
        test_calls=1,retry=False)
    OUT.mkdir(parents=True)
    s.prior.save(OUT/"inventory.json",sources)
    s.prior.save(OUT/"preregistration.json",prereg)
    if upper["violations"] or qbound["violations"]:
        value=dict(status="PRECONDITION_BLOCKED",test_calls=0,run=upper,qualification=qbound)
        s.prior.save(OUT/"precondition-stop.json",value)
        print(json.dumps(value))
        return 2
    try:
        proc=subprocess.run([sys.executable,"-m","unittest","-v","tests.test_s2oe_worker"],
            cwd=b.ROOT,env=dict(os.environ,MEDIA_WORKER_QUAL_OUT=str(OUT)),capture_output=True,check=False,
            timeout=240)
    except subprocess.TimeoutExpired as exc:
        proc=SimpleNamespace(returncode=124,stdout=exc.stdout or b"",
            stderr=(exc.stderr or b"")+b"\nQUALIFICATION_PROCESS_TIMEOUT\n")
    for name,raw in (("stdout.txt",proc.stdout),("stderr.txt",proc.stderr)):
        with (OUT/name).open("xb") as f:
            f.write(raw)
    unchanged=sources==m.inventory()
    log=(proc.stdout+proc.stderr).decode("utf-8",errors="replace")
    passed=proc.returncode==0 and f"Ran {len(tests)} tests" in log and log.rstrip().endswith("OK") and unchanged
    p.MAIN_GATE=False
    result=b.sealed(dict(run_id=m.QUAL_ID,status="QUALIFIED" if passed else "NOT_QUALIFIED",
        sources=sources,hashes_unchanged=unchanged,test_calls=1,expected_tests=len(tests),
        exit_code=proc.returncode,gates=False,files={n:s.sha((OUT/n).read_bytes())
            for n in ("preregistration.json","stdout.txt","stderr.txt")}),"result_digest")
    estimated=0
    for _ in range(16):
        balance=actual(common,{"result.json":len(b.canonical(result)),"final-balance.json":estimated})
        result=b.sealed({**{k:v for k,v in result.items() if k!="result_digest"},
            "status":"QUALIFIED" if passed and not balance["violations"] else "NOT_QUALIFIED",
            "budget_violations":balance["violations"]},"result_digest")
        size=len(b.canonical(balance))
        if size==estimated and balance["files"]["result.json"]==len(b.canonical(result)):
            break
        estimated=size
    else:
        raise RuntimeError("CLOSURE_SIZE_UNSTABLE")
    s.prior.save(OUT/"result.json",result)
    s.prior.save(OUT/"final-balance.json",balance)
    print(json.dumps(dict(status=result["status"],test_calls=1,actual=actual(common))))
    return 0 if result["status"]=="QUALIFIED" else 1


if __name__=="__main__":
    raise SystemExit(main())
