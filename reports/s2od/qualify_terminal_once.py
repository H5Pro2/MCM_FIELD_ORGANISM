"""One prospectively bounded terminal-control qualification, no native replay."""
import ast
import os
from pathlib import Path
import subprocess
import sys

from tools import _s2od_private_terminal_client as c

s,b=c.s,c.b


def main():
    out=b.ROOT/"reports/s2od"/c.QUAL_ID
    if out.exists(): raise RuntimeError("QUALIFICATION_ID_USED")
    inv=s.inventory()
    own=c.sources()
    names=sorted(n.name for n in ast.walk(ast.parse((b.ROOT/c.OWN[1]).read_text()))
                 if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    if len(names)!=c.TEST_COUNT: raise RuntimeError("TEST_INVENTORY_INVALID")
    out.mkdir()
    s.prior.save(out/"inventory.json",inv)
    events=[]
    for n,kind in enumerate((b.AV,b.V,b.A),1):
        pcm=None if kind==b.V else b.Payload(f"neutral-pcm-{n}","reports/s2od/forbidden.pcm","0"*64,19200)
        rgb=None if kind==b.A else b.Payload(f"neutral-rgb-{n}","reports/s2od/forbidden.rgb","0"*64,6220800)
        events.append(b.Event(f"neutral-event-{n}",n,kind,**b.expected_times(n,kind),pcm=pcm,rgb=rgb))
    m=b.build_manifest("terminal-neutral-bound",tuple(events),b.digest(inv["ob"]))
    common,_=s.qualified_common(m,b.ROOT/"reports/s2oc"/s.QUAL_ID)
    refs=list(common["references"])
    refs.extend(s.file_reference("sources",b.ROOT/p) for p in c.OWN)
    refs.append(["metadata",(out/"qualification-reserve").relative_to(b.ROOT).as_posix(),c.QUAL_LIMIT,"0"*64])
    common=s.build_common(m,inv,refs,common["qualification"])
    upper=c.verification.preflight(common)
    # All qualification files are counted physically, including the base inventory.
    # No synthetic native records are written; they only bound a future wrapper run.
    qbound=dict(metadata=c.QUAL_LIMIT+512+4096,
                sources=len(b.canonical(inv))+sum(n for h,n in own.values()),
                verification=0,nj=0,formations=0,generations=0)
    qbound["shared"]=qbound["sources"]
    qbound["total"]=qbound["metadata"]+qbound["sources"]
    preparation=dict(version=c.VERSION,run_id=c.QUAL_ID,test_calls=0,
        runtime_positions=upper["positions"],runtime_violations=upper["violations"],
        qualification_bound=qbound,limits=b.LIMITS,qualification_cap=c.QUAL_LIMIT,
        preparation_cap=4096,report_reserve=512,
        statement="Synthetic administrative envelope only; no native history. Terminal tests use isolated fake session receipts.")
    s.prior.save(out/"preparation.json",preparation)
    violations=[k for k,n in qbound.items() if n>b.LIMITS[k]]
    if len(b.canonical(preparation))>4096: violations.append("PREPARATION_LIMIT")
    pr=dict(version=c.VERSION,run_id=c.QUAL_ID,test_inventory=names,test_calls=1,retry=False,
        client_sources=own,base_inventory_digest=b.digest(inv),qualification_cap=c.QUAL_LIMIT,
        log_policy="Full stdout/stderr retained; excess is NOT_QUALIFIED, never truncated.",
        input_boundary="Only fake receipts; read_payload, Materializer and CallerRuntime are call-blocked.",
        counts=dict(native_sessions=0,receptor_calls=0,nj_calls=0,real_payload_reads=0),
        preparation_sha256=s.sha(b.canonical(preparation)))
    # Remaining space is explicitly for full logs, not a success-log assumption.
    pr["result_reserve"]=1800
    pr["log_reserve"]=c.QUAL_LIMIT-1800-len(b.canonical(pr))-64
    if pr["log_reserve"]<1024: violations.append("QUALIFICATION_RESERVE")
    if violations or upper["violations"]:
        print(b.canonical(dict(status="PRECONDITION_BLOCKED",violations=violations,
            runtime_violations=upper["violations"],qualification_bound=qbound)).decode())
        return 2
    s.prior.save(out/"preregistration.json",pr)
    print("PRE_TEST_BOUND",flush=True)
    proc=subprocess.run([sys.executable,"-m","unittest","tests.test_s2od_terminal_client"],
        cwd=b.ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1"),capture_output=True,check=False)
    (out/"stdout.txt").write_bytes(proc.stdout)
    (out/"stderr.txt").write_bytes(proc.stderr)
    unchanged=own==c.sources() and inv==s.inventory()
    good=proc.returncode==0 and unchanged
    q=b.sealed(dict(version=c.VERSION,run_id=c.QUAL_ID,status="QUALIFIED" if good else "NOT_QUALIFIED",
        test_calls=1,expected_tests=c.TEST_COUNT,passed_tests=c.TEST_COUNT if good else None,
        exit_code=proc.returncode,client_sources=own,base_inventory_digest=b.digest(inv),
        hashes_unchanged=unchanged,gates=c.entry.MAIN_GATE,
        evidence={n:s.sha((out/n).read_bytes()) for n in ("preregistration.json","stdout.txt","stderr.txt")}),"result_digest")
    used=sum((out/n).stat().st_size for n in q["evidence"])+len(b.canonical(q))
    if used>c.QUAL_LIMIT:
        q=b.sealed({**{k:v for k,v in q.items() if k!="result_digest"},"status":"NOT_QUALIFIED"},"result_digest")
    s.prior.save(out/"result.json",q)
    files={p.name:p.stat().st_size for p in out.iterdir() if p.is_file()}
    print(b.canonical(dict(status=q["status"],files=files,qualification_bytes=used,
        reserved=qbound,actual_with_report_reserve=dict(
            metadata=sum(n for p,n in files.items() if p!="inventory.json")+512,
            sources=qbound["sources"],total=sum(files.values())+sum(n for h,n in own.values())+512),
        gates=c.entry.MAIN_GATE)).decode())
    return 0 if q["status"]=="QUALIFIED" else 1


if __name__=="__main__":
    raise SystemExit(main())
