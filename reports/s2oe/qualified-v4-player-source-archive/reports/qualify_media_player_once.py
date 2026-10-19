"""Bind and run only the new local-player qualification, once."""
import ast
import json
import os
import subprocess
import sys
from types import SimpleNamespace
from tools import _s2oe_media_session as m
from tools._s2oc_shared_verification import synthetic_forms
from reports import qualify_media_worker_once as previous

p,b,s=m.p,m.b,m.s
OUT=b.ROOT/"reports/s2oe"/m.QUAL_ID
QFILES=("preregistration.json","stdout.txt","stderr.txt","result.json","final-balance.json")
QCAP=8192
PICTURES=40960
CLIENT=8192


def common_fixture(src=None):
    inv=m.inventory()
    raw=b.canonical(inv)
    ref=["sources",(OUT/"inventory.json").relative_to(b.ROOT).as_posix(),len(raw),s.sha(raw)]
    common,baseinv=previous.fixture_binding(ref,src)
    root=b.ROOT/"reports/s2oe"/m.WORKER_QUAL_ID
    refs=common["references"]+[s.file_reference("metadata",root/n) for n in QFILES]
    return m.bind_common(p.decode(common["manifest"]),common,refs),baseinv


def upper(common):
    extra=(("metadata","@current-player-qualification",QCAP),
        ("metadata","@complete-run-binding",24576),("metadata","@player-close",1024),
        ("metadata","@authorization-claim",512))
    rows=[]
    for n in range(25):
        for name,pair in zip(("success","failure"),synthetic_forms(common,n)):
            row=p.ledger(*previous.with_media(pair,n),common,attachments=m.oc.ATTACHMENTS+extra)
            rows.append(dict(completed=n,alternative=name,totals=row["totals"],violations=row["violations"]))
    return dict(positions=rows,maxima={k:max(r["totals"][k] for r in rows) for k in p.SESSION_LIMITS},
        limits=p.SESSION_LIMITS,violations=[r for r in rows if r["violations"]])


def qualification_bound(common):
    pair=previous.with_media(synthetic_forms(common,1)[1],1)
    row=p.ledger(*pair,common,attachments=(("metadata","@qualification",QCAP),
        ("metadata","@screenshots",PICTURES),("metadata","@client-fixtures",CLIENT)))
    return dict(totals=row["totals"],limits=p.QUAL_LIMITS,violations=row["violations"],
        qualification=QCAP,screenshots=PICTURES,client_fixtures=CLIENT)


def actual(common,pending=None):
    files={f.relative_to(OUT).as_posix():f.stat().st_size for f in OUT.rglob("*") if f.is_file()}
    files.update(pending or {})
    native=0
    parts=dict(nj=0,formations=0,generations=0)
    directory=OUT/"native-player"
    if (directory/"record.json").exists():
        c=s.load_common(directory)
        r,t=s.unpack(s.read_json(directory/"record.json"),s.read_json(directory/"session.json"),c)
        contribution=p.ledger(r,t,c)["contributions"]
        native=sum(contribution["native"].values())+contribution["prefix_steps"]
        for k in parts:parts[k]=contribution["native"].get(k,0)
    proof=sum(n for name,n in files.items() if name.endswith(("verification.json","verification.claim")))
    external=[r for r in common["references"] if not (b.ROOT/r[1]).is_relative_to(OUT)]
    sources=sum(r[2] for r in common["references"] if r[0]=="sources")
    physical=sum(files.values())+sum(r[2] for r in external)
    qbytes=sum(files.get(n,0) for n in QFILES)
    images=sum(n for name,n in files.items() if name.endswith(".jpg"))
    fixture=sum(n for name,n in files.items() if name not in QFILES and name!="inventory.json"
        and not name.startswith("native-player/") and not name.endswith(".jpg"))
    reserve=max(0,QCAP-qbytes)+max(0,PICTURES-images)+max(0,CLIENT-fixture)+512
    totals=dict(metadata=physical-native-proof-sources+reserve,sources=sources,verification=proof,
        **parts,shared=sources+sum(parts.values()),total=physical+reserve)
    return dict(files=files,totals=totals,remaining_reserve=reserve,qualification_bytes=qbytes,
        screenshot_bytes=images,client_fixture_bytes=fixture,violations=[k for k,v in totals.items() if v>p.QUAL_LIMITS[k]]
        +(["qualification"] if qbytes>QCAP else [])+(["screenshots"] if images>PICTURES else [])
        +(["client"] if fixture>CLIENT else []))


def main():
    if OUT.exists():raise RuntimeError("QUALIFICATION_ID_USED")
    sources=m.inventory();common,_=common_fixture();bound=upper(common);qbound=qualification_bound(common)
    tests=sorted(n.name for n in ast.walk(ast.parse((b.ROOT/"tests/test_s2oe_player.py").read_text()))
        if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    prereg=dict(run_id=m.QUAL_ID,budget_version=p.VERSION,tests=tests,source_inventory_sha256=b.digest(sources),
        limits=p.SESSION_LIMITS,qualification=qbound,run_maxima=bound["maxima"],
        work=dict(native_sessions=1,native_formations=1,native_verifications=1,real_media_reads=0,
            worker_qualification_repeated=False,browser_screenshots=2),test_calls=1,retry=False,
        environment=dict(python=sys.version,executable=sys.executable))
    OUT.mkdir(parents=True);s.prior.save(OUT/"inventory.json",sources);s.prior.save(OUT/"preregistration.json",prereg)
    if bound["violations"] or qbound["violations"]:
        value=dict(status="PRECONDITION_BLOCKED",test_calls=0,run=bound,qualification=qbound)
        s.prior.save(OUT/"precondition-stop.json",value);print(json.dumps(value));return 2
    try:
        proc=subprocess.run([sys.executable,"-m","unittest","-v","tests.test_s2oe_player"],cwd=b.ROOT,
            env=dict(os.environ,MEDIA_PLAYER_QUAL_OUT=str(OUT),MEDIA_WORKER_QUAL_OUT=str(OUT)),
            capture_output=True,timeout=180,check=False)
    except subprocess.TimeoutExpired as exc:
        proc=SimpleNamespace(returncode=124,stdout=exc.stdout or b"",stderr=(exc.stderr or b"")+b"\nQUALIFICATION_TIMEOUT\n")
    for name,raw in (("stdout.txt",proc.stdout),("stderr.txt",proc.stderr)):
        with (OUT/name).open("xb") as stream:stream.write(raw)
    unchanged=sources==m.inventory();log=(proc.stdout+proc.stderr).decode(errors="replace")
    passed=proc.returncode==0 and f"Ran {len(tests)} tests" in log and log.rstrip().endswith("OK") and unchanged
    p.MAIN_GATE=False
    result=b.sealed(dict(run_id=m.QUAL_ID,status="QUALIFIED" if passed else "NOT_QUALIFIED",sources=sources,
        test_calls=1,expected_tests=len(tests),exit_code=proc.returncode,hashes_unchanged=unchanged,gates=False,
        files={n:s.sha((OUT/n).read_bytes()) for n in ("preregistration.json","stdout.txt","stderr.txt")}),"result_digest")
    size=0
    for _ in range(16):
        balance=actual(common,{"result.json":len(b.canonical(result)),"final-balance.json":size})
        result=b.sealed({**{k:v for k,v in result.items() if k!="result_digest"},
            "status":"QUALIFIED" if passed and not balance["violations"] else "NOT_QUALIFIED",
            "budget_violations":balance["violations"]},"result_digest")
        new=len(b.canonical(balance))
        if new==size and balance["files"]["result.json"]==len(b.canonical(result)):break
        size=new
    else:raise RuntimeError("CLOSURE_SIZE_UNSTABLE")
    s.prior.save(OUT/"result.json",result);s.prior.save(OUT/"final-balance.json",balance)
    print(json.dumps(dict(status=result["status"],actual=actual(common))))
    return 0 if result["status"]=="QUALIFIED" else 1


if __name__=="__main__":raise SystemExit(main())
