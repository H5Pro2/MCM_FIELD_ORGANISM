"""Exactly one administrative neutral qualification; no replay."""
import ast
import json
import os
import subprocess
import sys
from tools import _s2oa_private_main_binding as b


def main():
    c=b.compact;out=b.ROOT/"reports/s2oa"/c.QUAL_ID;out.mkdir(exist_ok=False)
    before=b.watched();keys=set(c.REPLACED)|set(c.OWN);delta={k:before[k] for k in sorted(keys)}
    base=b.ROOT/"reports/s2oa"/b.ids.QUAL_ID/"preregistration.json"
    previous={**b.source_manifest(),**json.loads(base.read_bytes())["hashes"]}
    tests=sorted(n.name for n in ast.walk(ast.parse((b.ROOT/c.OWN[1]).read_text()))
        if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    b.require(len(tests)==len(set(tests))==c.TEST_COUNT,"TEST_INVENTORY_INVALID")
    command=[sys.executable,"-m","unittest","tests.test_s2oa_private_compact_references"]
    pr=dict(run_id=c.QUAL_ID,base_sha256=b.r.admin.filehash(base),replaced_hashes=c.REPLACED,
        hashes=delta,full_hashes_digest=b.digest(before),tests=tests,command=command,python=sys.version,
        limits=dict(metadata=65536,old_qualification=4096,correction=4096,report=512,shared=262144,total=4194304),
        work=dict(id_sweeps=128,administrative_roundtrips=32,replay=0,payloads=0,receptors=0),test_calls=1,retry=False)
    b.validate_compact_manifest(pr,previous,before)
    b.r.admin.publish(out/"preregistration.json",pr)
    p=subprocess.run(command,cwd=b.ROOT,env=dict(os.environ,S2OA_COMPACT_QUAL_DIR=str(out)),capture_output=True,check=False)
    for name,data in (("stdout.txt",p.stdout),("stderr.txt",p.stderr)):
        with (out/name).open("xb") as f:f.write(data)
    after=b.watched();log=(p.stdout+p.stderr).decode(errors="replace")
    passed=p.returncode==0 and "Ran 16 tests" in log and log.rstrip().endswith("OK") and before==after
    metrics=out/"metrics.json"
    # Fixed-size report is part of the correction reserve, not an uncounted attachment.
    report=("# OA-Referenzkompaktierung\n\n"+c.QUAL_ID+"\n\n"+
        ("16/16, QUALIFIED. " if passed else "NOT_QUALIFIED. ")+"Ein Aufruf, kein Replay oder Retry.\n"+
        "Bytebilanz: metrics.json; Inventar/Hashes: preregistration.json.\n"+
        "Alte 13/14 bleiben NOT_QUALIFIED, alter OA-Lauf NOT_EVALUABLE.\n"+
        "Gates False. Hauptlauf separat freizugeben.\n").encode("ascii")
    result=b.sealed(dict(run_id=c.QUAL_ID,status="S2OA_COMPACT_REFERENCES_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=p.returncode,test_calls=1,passed_tests=16 if passed else None,expected_tests=16,
        hashes_before_digest=b.digest(delta),hashes_after_digest=b.digest({k:after[k] for k in sorted(keys)}),hashes_unchanged=before==after,
        preregistration_sha256=b.r.admin.filehash(out/"preregistration.json"),
        stdout_sha256=b.r.admin.filehash(out/"stdout.txt"),stderr_sha256=b.r.admin.filehash(out/"stderr.txt"),
        metrics_sha256=b.r.admin.filehash(metrics) if metrics.exists() else None,
        report_sha256=b.hashlib.sha256(report).hexdigest(),main_gate_after=False),"result_digest")
    size=sum(f.stat().st_size for f in out.iterdir() if f.is_file())+len(report)+len(b.canonical(result))
    if size>4096:
        passed=False;report=report.replace(b"16/16, QUALIFIED.",b"NOT_QUALIFIED: qualification bytes exceeded.")
        result=b.sealed({**{k:v for k,v in result.items() if k!="result_digest"},"status":"NOT_QUALIFIED",
            "report_sha256":b.hashlib.sha256(report).hexdigest()},"result_digest")
    with (out/"BEFUND.md").open("xb") as f:f.write(report)
    b.r.admin.publish(out/"result.json",result)
    print(json.dumps(dict(status=result["status"],run_id=c.QUAL_ID,exit_code=p.returncode,
        qualification_bytes=sum(f.stat().st_size for f in out.iterdir() if f.is_file()),result_digest=result["result_digest"])))
    return 0 if passed else 1


if __name__=="__main__":raise SystemExit(main())
