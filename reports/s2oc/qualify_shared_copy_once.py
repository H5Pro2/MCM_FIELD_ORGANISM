"""One conditional qualification with the unchanged lossless OC packager."""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from tools import _s2oc_shared_binding as s
from tools import _s2oc_shared_verification as v

b, qa = s.b, s.qa


def synthetic_manifest(inv):
    events=[]
    for n in range(1,22):
        kind=b.V if n in (2,15,21) else b.AV
        rgb=b.Payload(f"synthetic-visual-{n}","reports/s2oc/unread-synthetic-rgb.bin","0"*64,6220800)
        pcm=None if kind==b.V else b.Payload(f"synthetic-audio-{n}","reports/s2oc/unread-synthetic-pcm.bin","0"*64,19200)
        events.append(b.Event(f"synthetic-event-{n}",n,kind,**b.expected_times(n,kind),pcm=pcm,rgb=rgb))
    return b.build_manifest("synthetic-complete-memory-cycle",tuple(events),b.digest(inv["ob"]))


def error_text(names):
    frames=(("reports/s2oc/run_bound_session_once.py","run"),
            ("reports/s2oc/run_bound_session_once.py","_run_bound"),
            ("tools/_s2oc_bound_session.py","run_once"),
            ("tools/_s2oc_bound_session.py","open_session"),
            ("tools/_s2oc_bound_session.py","_check_progress_budget"),
            ("tools/_s2oc_bound_session.py","alternatives"),
            ("tools/_s2oc_shared_binding.py","ledger"),
            ("tools/_s2oc_shared_binding.py","pack"),
            ("tools/_s2oc_shared_binding.py","transform"))
    blocks=[]
    for name in names:
        blocks.append("="*70+f"\nERROR: {name} (tests.test_s2oc_shared_closure.SharedClosureTests.{name})\n"
            +"-"*70+"\nTraceback (most recent call last):\n")
        for path,func in ((s.OWN[4],name),*frames):
            tree=ast.parse((b.ROOT/path).read_text(encoding="utf-8"))
            node=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==func)
            line=(b.ROOT/path).read_text(encoding="utf-8").splitlines()[node.lineno]
            blocks.append(f'  File "{b.ROOT/path}", line {node.lineno+1}, in {func}\n    {line.strip()}\n')
        # Complete bounded diagnostic shape, not a measured exception or memory state.
        diagnostic=dict(phase="EVIDENCE",ordinal=21,completed_events=20,
            alternatives={arm:dict(parts={key:4194304 for key in
                ("record","session","common","native","prefix_steps","metadata_references","source_references","report","proof")},
                totals={key:4194304 for key in b.LIMITS},limits=b.LIMITS,
                violations=[key.upper()+"_LIMIT" for key in b.LIMITS]) for arm in ("success","failure")})
        blocks.append("tools._s2oc_budget_closure.BudgetError: COMBINED_RUNTIME_METADATA_LIMIT\n"
                      +b.canonical(diagnostic).decode("ascii")+"\n\n")
    return ("E"*len(names)+"\n"+"".join(blocks)+f"Ran {len(names)} tests in 999.999s\nFAILED (errors={len(names)})\n").encode("utf-8")


def package_probe(names, pr, metrics):
    with tempfile.TemporaryDirectory(prefix="oc-copy-envelope-",dir=b.ROOT/"reports/s2oc") as temp:
        root=Path(temp)
        s.prior.save(root/"preregistration.json",pr)
        (root/"stdout.txt").write_bytes(b"")
        (root/"stderr.txt").write_bytes(error_text(names))
        s.prior.save(root/"metrics.json",metrics)
        s.prior.save(root/"final-balance.json",dict(kind="SYNTHETIC_FULL_ERROR",totals=b.LIMITS,
            files={name:4194304 for name in qa.FILES},violations=[k.upper()+"_LIMIT" for k in b.LIMITS]))
        q=b.sealed(dict(run_id=s.QUAL_ID,status="NOT_QUALIFIED",test_calls=0,
            expected_tests=s.TEST_COUNT,passed_tests=None,exit_code=1,source_digest=pr["source_digest"],
            hashes_unchanged=True,gates=False,budget_violations=[k.upper()+"_LIMIT" for k in b.LIMITS],
            evidence={n:s.sha((root/n).read_bytes()) for n in qa.FILES if n!="result.json"}),"result_digest")
        s.prior.save(root/"result.json",q)
        qa.package.create_package(root,root/"qualification.zip",qa.FILES)
        measured=qa.measure(root/"qualification.zip",root)
        return dict(stored=measured["stored"],expanded=measured["expanded"],sha256=measured["sha256"],
            physical=measured["stored_total"],index_expanded=measured["index_expanded"],
            unpack_work=measured["decompressed_bytes"],maximum_member=measured["maximum_member"],
            receipt_reserve=qa.RECEIPT_LIMIT,qualification_bytes=measured["stored"]["qualification"]+qa.RECEIPT_LIMIT,
            violations=qa.violations(measured),restored_exactly=measured["restored_exactly"])


def neutral_header_bound(inv, ref):
    sizes=[]
    for kinds in ((b.AV,b.A),(b.A,b.AV)):
        events=[]
        for n,kind in enumerate(kinds,1):
            pcm=b.Payload("a"*79+str(n),"reports/s2oc/"+"p"*100+".bin","0"*64,19200)
            rgb=b.Payload("v"*79+str(n),"reports/s2oc/"+"r"*100+".bin","0"*64,6220800) if kind==b.AV else None
            events.append(b.Event("e"*79+str(n),n,kind,**b.expected_times(n,kind),pcm=pcm,rgb=rgb))
        m=b.build_manifest("q"*80,tuple(events),b.digest(inv["ob"]))
        c=s.build_common(m,inv,[ref])
        sizes.extend(s.ledger(*pair,c)["totals"]["metadata"]-512 for pair in v.synthetic_forms(c,2))
    return max(sizes)


def physical_balance(out, ownrefs):
    files={p.relative_to(out).as_posix():p.stat().st_size for p in out.rglob("*") if p.is_file()}
    native=0;extras=dict(nj=0,formations=0,generations=0)
    for folder in ("success","failure"):
        if not (out/folder/"record.json").exists():continue
        c=s.load_common(out/folder)
        r,q=s.unpack(s.read_json(out/folder/"record.json"),s.read_json(out/folder/"session.json"),c)
        p=s.ledger(r,q,c)["contributions"]
        native+=sum(p["native"].values())+p["prefix_steps"]
        for k in extras:extras[k]+=p["native"].get(k,0)
    own=sum(r[2] for r in ownrefs)
    sources=files.get("inventory.json",0)+own
    proof=sum(n for p,n in files.items() if p.endswith(("verification.json","verification.claim")))
    # Prospective physical alternative replaces exactly the six packaged files.
    raw_q=sum(files.get(n,0) for n in qa.FILES)
    base=sum(files.values())+own-raw_q
    totals=dict(metadata=base-native-sources-proof+sum(s.QUAL_CAPS.values())+512,
        sources=sources,verification=proof,**extras,shared=sources+sum(extras.values()),
        total=base+sum(s.QUAL_CAPS.values())+512)
    return dict(files=files,raw_qualification_bytes=raw_q,base_bytes=base,native_bytes=native,
        own_source_bytes=own,archive_and_receipt_reserve=sum(s.QUAL_CAPS.values()),report_reserve=512,
        totals=totals,violations=[k.upper()+"_LIMIT" for k,n in totals.items() if n>b.LIMITS[k]])


def main():
    out=b.ROOT/"reports/s2oc"/s.QUAL_ID
    if out.exists():raise RuntimeError("QUALIFICATION_ID_USED")
    names=sorted(n.name for n in ast.walk(ast.parse((b.ROOT/s.OWN[4]).read_text(encoding="utf-8")))
        if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    if len(names)!=s.TEST_COUNT:raise RuntimeError("TEST_INVENTORY_INVALID")
    inv=s.inventory();out.mkdir();s.prior.save(out/"inventory.json",inv)
    ownrefs=[s.file_reference("sources",b.ROOT/p) for p in s.OWN]
    refs=[s.file_reference("sources",out/"inventory.json"),*ownrefs]
    refs.extend(["metadata",(out/n).relative_to(b.ROOT).as_posix(),cap,"0"*64] for n,cap in s.QUAL_CAPS.items())
    common=s.build_common(synthetic_manifest(inv),inv,refs,next(r for r in refs if r[1].endswith("/package.json")))
    s.prior.save(out/"bound-common.json",common)
    upper=v.preflight(common);s.prior.save(out/"bounds.json",upper)
    expected=dict(sessions=2,audio=3,nj=3,visual=2,core_verifications=1,failure_verifications=1,gates=False)
    native=2*98304+2*16384+3*16384+2*32767+2*1024+1536+1536
    # The preparation record has its own finite, counted metadata reserve.
    qbound=dict(metadata=len(b.canonical(common))+len(b.canonical(upper))+sum(s.QUAL_CAPS.values())+512
        +2*neutral_header_bound(inv,refs[0])+768+1536+512+4096,
        sources=len(b.canonical(inv))+sum(r[2] for r in ownrefs),verification=32768,
        nj=2048,formations=1536,generations=1536)
    qbound["shared"]=qbound["sources"]+5120
    qbound["total"]=native+qbound["metadata"]+qbound["sources"]+qbound["verification"]
    pr=dict(run_id=s.QUAL_ID,expected_tests=s.TEST_COUNT,test_inventory=names,source_digest=b.digest(inv),
        test_calls=1,retry=False,qualification_reserve=qa.QUAL_LIMIT,report_reserve=512,expected=expected,
        qualification_bound=qbound,bound_common_sha256=s.sha(b.canonical(common)),bounds_sha256=s.sha(b.canonical(upper)),
        packaging=qa.package.VERSION,package_code_sha256=s.sha((b.ROOT/"tools/_s2oc_private_evidence_package.py").read_bytes()))
    probe=package_probe(names,pr,expected)
    violations=[k.upper()+"_LIMIT" for k,n in qbound.items() if n>b.LIMITS[k]]+probe["violations"]
    preparation=dict(source_digest=b.digest(inv),test_calls=0,qualification_bound=qbound,error_envelope=probe,
        run_violations=upper["violations"],violations=violations,
        boundary="Synthetic complete error envelope; no test or real history executed. No universal log compression claim.")
    if len(b.canonical(preparation))>4096:violations.append("PREPARATION_LIMIT")
    s.prior.save(out/"preparation.json",preparation)
    if violations or upper["violations"]:
        print(json.dumps(dict(status="PRECONDITION_BLOCKED",**preparation)),flush=True)
        return 2
    s.prior.save(out/"preregistration.json",pr)
    print(json.dumps(dict(phase="PRE_TEST",source_digest=b.digest(inv),qualification_bound=qbound,probe=probe)),flush=True)
    proc=subprocess.run([sys.executable,"-m","unittest","tests.test_s2oc_shared_closure"],cwd=b.ROOT,
        env=dict(os.environ,OC_SHARED_OUT=str(out)),capture_output=True,check=False)
    for name,raw in (("stdout.txt",proc.stdout),("stderr.txt",proc.stderr)):(out/name).write_bytes(raw)
    met=s.read_json(out/"metrics.json") if (out/"metrics.json").exists() else None
    unchanged=inv==s.inventory();log=(proc.stdout+proc.stderr).decode("utf-8",errors="replace")
    passed=proc.returncode==0 and f"Ran {s.TEST_COUNT} tests" in log and log.rstrip().endswith("OK") and met==expected and unchanged
    logical=physical_balance(out,ownrefs);s.prior.save(out/"final-balance.json",logical)
    q=b.sealed(dict(run_id=s.QUAL_ID,status="QUALIFIED" if passed and not logical["violations"] else "NOT_QUALIFIED",
        test_calls=1,expected_tests=s.TEST_COUNT,passed_tests=s.TEST_COUNT if passed else None,exit_code=proc.returncode,
        source_digest=b.digest(inv),hashes_unchanged=unchanged,gates=False,budget_violations=logical["violations"],
        evidence={n:s.sha((out/n).read_bytes()) for n in qa.FILES if n!="result.json" and (out/n).exists()}),"result_digest")
    s.prior.save(out/"result.json",q)
    # Do not remove any original unless every byte has been independently recovered.
    qa.package.create_package(out,out/"qualification.zip",[n for n in qa.FILES if (out/n).exists()])
    measured=qa.measure(out/"qualification.zip",out)
    errors=qa.violations(measured)+logical["violations"]
    stamp=dict(status=q["status"] if not errors else "NOT_QUALIFIED",sha256=measured["sha256"],
        qualification_bytes=measured["stored"]["qualification"]+qa.RECEIPT_LIMIT,
        stored=[measured["stored"][k] for k in qa.package.CLASSES],expanded_total=measured["expanded_total"],
        unpack=[measured["maximum_member"],measured["index_expanded"],measured["decompressed_bytes"],qa.package.UNPACK_MEMORY_LIMIT],
        reserved_totals=logical["totals"],report_reserve=512,violations=errors,gates=False)
    size=0
    for _ in range(12):
        stamp["qualification_bytes"]=measured["stored"]["qualification"]+size
        delta=measured["stored_total"]+size-sum(s.QUAL_CAPS.values())
        stamp["actual_metadata_total"]=[logical["totals"][k]+delta for k in ("metadata","total")]
        current=len(b.canonical(stamp))
        if current==size:break
        size=current
    else:raise RuntimeError("PACKAGE_RECEIPT_SIZE_UNSTABLE")
    if size>qa.RECEIPT_LIMIT:
        stamp["status"]="NOT_QUALIFIED";stamp["violations"].append("QUALIFICATION_RECEIPT_LIMIT")
    s.prior.save(out/"package.json",stamp)
    if not stamp["violations"]:
        root=out.resolve()
        for name in qa.FILES:
            path=(out/name).resolve()
            if not path.is_relative_to(root):raise RuntimeError("CLEANUP_PATH_INVALID")
            if path.exists():path.unlink()
    print(json.dumps(dict(status=stamp["status"],metrics=met,package=stamp)),flush=True)
    return 0 if stamp["status"]=="QUALIFIED" else 1


if __name__=="__main__":raise SystemExit(main())
