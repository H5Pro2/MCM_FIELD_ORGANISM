"""Bind complete code and qualification envelopes before one unittest process."""
import ast
from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import sys

from tools import _s2oe_media_session as m
from tools import _s2oc_shared_verification as shapes
from reports.prepare_direct_media_budget import prepare

p, b, s = m.p, m.b, m.s
OUT = b.ROOT/"reports/s2oe"/m.QUAL_ID
QFILES = ("preregistration.json", "stdout.txt", "stderr.txt", "result.json", "final-balance.json")


def fixture_binding(inventory_ref):
    base_dir = b.ROOT/"reports/s2oc"/s.QUAL_ID
    anchor = s.read_json(base_dir/"caller-common.json")
    base, inv = s.qualified_common(b.decode_manifest(anchor["manifest"]), base_dir)
    manifest = p.build("q"*80, p.Source(str(b.ROOT/"sources/s2oe-neutral"/("x"*32+".bin")), "0"*64, 32), b.digest(m.inventory()))
    refs = base["references"] + [s.file_reference("sources", b.ROOT/n) for n in m.OWN
        if not any(ref[1] == n for ref in base["references"])]
    refs += [s.file_reference("metadata", base_dir/"caller-common.json"), inventory_ref]
    return m.bind_common(manifest, base, refs), inv


def qualification_bound(common):
    refs = common["references"]
    source = sum(n for k,_,n,_ in refs if k == "sources")
    refmeta = sum(n for k,_,n,_ in refs if k == "metadata")
    native = metadata = 0
    shared_parts = dict(nj=0, formations=0, generations=0)
    for n, alternative in ((24,0),(1,1),(1,1)):
        record, session = shapes.synthetic_forms(common,n)[alternative]
        record.pop("record_digest")
        record["media"] = dict(receipts=["x"*510 for _ in range(min(n+1,24))], decoder="x"*2046)
        record = b.sealed(record,"record_digest")
        session["record_digest"] = record["record_digest"]
        session = b.sealed({k:v for k,v in session.items() if k != "session_digest"},"session_digest")
        ledger = s.ledger(record,session,common,attachments=(),proof_bytes=0,report_bytes=0)
        metadata += ledger["totals"]["metadata"] - refmeta
        parts = ledger["contributions"]
        native += sum(parts["native"].values()) + parts["prefix_steps"]
        for key in shared_parts:
            shared_parts[key] += ledger["totals"][key]
    metadata += refmeta + 6607 + 512
    totals = dict(metadata=metadata,sources=source,verification=262144,**shared_parts)
    totals["shared"] = source + sum(shared_parts.values())
    totals["total"] = metadata + source + native + 262144
    return dict(totals=totals,limits=b.LIMITS,
        violations=[k for k,v in totals.items() if v>b.LIMITS[k]],
        native=native,qualification_and_report=7119,
        basis="One full native success, two one-event failure prefixes; all native item maxima. Shared references counted once.")


def actual_bound(common):
    files = {str(f.relative_to(OUT)):f.stat().st_size for f in OUT.rglob("*") if f.is_file()}
    native = proof = 0
    parts = dict(nj=0,formations=0,generations=0)
    for folder in ("native-full","native-stop","native-failure"):
        path = OUT/folder
        if not (path/"record.json").exists():
            continue
        c = s.load_common(path)
        record,session = s.unpack(s.read_json(path/"record.json"),s.read_json(path/"session.json"),c)
        contribution = s.ledger(record,session,c)["contributions"]
        native += sum(contribution["native"].values())+contribution["prefix_steps"]
        for k in parts: parts[k] += contribution["native"].get(k,0)
    proof = sum(n for name,n in files.items() if name.endswith(("verification.json","verification.claim")))
    external = [r for r in common["references"] if not (b.ROOT/r[1]).is_relative_to(OUT)]
    sources = sum(r[2] for r in common["references"] if r[0] == "sources")
    physical = sum(files.values()) + sum(r[2] for r in external)
    qbytes = sum(files.get(n,0) for n in QFILES)
    reserve = max(0,6607-qbytes)+512
    totals = dict(metadata=physical-native-proof-sources+reserve,sources=sources,
        verification=proof,**parts,shared=sources+sum(parts.values()),total=physical+reserve)
    return dict(files=files,totals=totals,qualification_bytes=qbytes,
        violations=[k for k,v in totals.items() if v>b.LIMITS[k]] + (["qualification"] if qbytes>6607 else []))


def main():
    if OUT.exists():
        raise RuntimeError("QUALIFICATION_ID_USED")
    OUT.mkdir(parents=True)
    sources = m.inventory()
    s.prior.save(OUT/"inventory.json",sources)
    ref = s.file_reference("sources",OUT/"inventory.json")
    common,inv = fixture_binding(ref)
    upper = prepare()
    qbound = qualification_bound(common)
    tree = ast.parse((b.ROOT/"tests/test_s2oe_media.py").read_text(encoding="utf-8"))
    tests = sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    preregistration = dict(run_id=m.QUAL_ID,tests=tests,sources_digest=b.digest(sources),
        qualification_bound=qbound,run_maxima=upper["maxima"],limits=b.LIMITS,
        work=dict(native_sessions=3,formations=22,cues=4,native_audio_nj=24,native_visual=24,
            native_verifications=1,error_binding_checks=2,real_media_reads=0),
        source_inventory_sha256=ref[3],test_calls=1,retry=False)
    s.prior.save(OUT/"preregistration.json",preregistration)
    violations=qbound["violations"]+[f"run:{key}" for name in upper["maxima"]
        for key,value in upper["maxima"][name].items() if value>b.LIMITS[key]]
    if violations:
        s.prior.save(OUT/"precondition-stop.json",dict(status="PRECONDITION_BLOCKED",test_calls=0,
            violations=violations,qualification_bound=qbound,run_maxima=upper["maxima"]))
        print(json.dumps(dict(status="PRECONDITION_BLOCKED",test_calls=0,violations=violations,
            qualification_bound=qbound,run_maxima=upper["maxima"])))
        return 2
    proc=subprocess.run([sys.executable,"-m","unittest","-v","tests.test_s2oe_media"],
        cwd=b.ROOT,env=dict(os.environ,MEDIA_QUAL_OUT=str(OUT)),capture_output=True,check=False)
    for name,raw in (("stdout.txt",proc.stdout),("stderr.txt",proc.stderr)):
        with (OUT/name).open("xb") as f:f.write(raw)
    unchanged=sources==m.inventory()
    log=(proc.stdout+proc.stderr).decode("utf-8",errors="replace")
    passed=proc.returncode==0 and f"Ran {len(tests)} tests" in log and log.rstrip().endswith("OK") and unchanged
    p.MAIN_GATE=False
    result=b.sealed(dict(run_id=m.QUAL_ID,status="QUALIFIED" if passed else "NOT_QUALIFIED",
        sources=sources,hashes_unchanged=unchanged,test_calls=1,expected_tests=len(tests),
        exit_code=proc.returncode,gates=False,files={n:s.sha((OUT/n).read_bytes())
            for n in ("preregistration.json","stdout.txt","stderr.txt")}),"result_digest")
    # Measure closing files before publishing them; no truncation on failure.
    balance=actual_bound(common)
    estimated=len(b.canonical(result))+len(b.canonical(balance))
    excess=max(0,balance["qualification_bytes"]+estimated-6607)
    if balance["violations"] or excess:
        result=b.sealed({**{k:v for k,v in result.items() if k!="result_digest"},
            "status":"NOT_QUALIFIED","closing_budget_excess":excess},"result_digest")
    s.prior.save(OUT/"result.json",result)
    s.prior.save(OUT/"final-balance.json",actual_bound(common))
    print(json.dumps(dict(status=result["status"],test_calls=1,actual=actual_bound(common))))
    return 0 if result["status"]=="QUALIFIED" else 1


if __name__=="__main__":
    raise SystemExit(main())
