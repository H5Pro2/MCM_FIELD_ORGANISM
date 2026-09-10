"""One current administrative qualification; prepare before explicit run."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from tools import _s2oa_private_active_connection as a
from reports.s2oa import prepare_active_connection as prep

ROOT=prep.ROOT
RUN_ID="s2oa-active-connection-qualification-20260910-01"
TEST="tests/test_s2oa_private_active_connection.py"
COMMAND=[sys.executable,"-m","tests.test_s2oa_private_active_connection"]
FILES=("stdout.txt","stderr.txt","metrics.json","invoked.claim","BEFUND.md","preflight-balance.json","final-balance.json")


def write_raw(path,raw):
    with path.open("xb") as f:
        f.write(raw);f.flush();os.fsync(f.fileno())


def qualification_bytes(result,metrics,stdout,stderr):
    return len(result)+len(metrics)+len(stdout)+len(stderr)


def manifest_fields():
    return dict(qualification_run_id=RUN_ID,qualification_command=COMMAND,
        qualification_test_ids=["a%02d"%n for n in range(1,31)],
        qualification_test_calls=1,qualification_retry=False,
        python=sys.version,executable=sys.executable,
        qualification_scope="current administrative connection only; no historical test credits",
        classification=dict(manifest="metadata",inventory="metadata",
            result_logs_metrics="metadata, shared 4096-byte qualification reserve",
            report="metadata, unchanged 512-byte report reserve",
            preflight_and_final_balances="verification, shared 262144-byte ceiling including prior and later verification"))


def outcome(manifest,metrics,status,files):
    passed=set(metrics.get("passed",[]))
    q=dict(schema="s2oa.active-qualification.v1",run_id=RUN_ID,status=status,test_calls=1,
        main_gate_after=False,manifest_sha256=hashlib.sha256(a.canonical(manifest)).hexdigest(),
        code_before=a.digest(manifest["code_hashes"]),code_after=metrics["code_after"],
        tests=[["a%02d"%n,"PASS" if "a%02d"%n in passed else "NOT_PASSED"] for n in range(1,31)],files=files)
    q["result_digest"]=a.digest(q)
    return q


def prepare():
    out=ROOT/a.DIRECTORY
    out.mkdir(exist_ok=False)
    names=sorted(n.name for n in ast.walk(ast.parse((ROOT/TEST).read_text(encoding="utf-8")))
                 if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    expected=["test_a%02d"%n for n in range(1,31)]
    if names!=expected:raise ValueError("TEST_INVENTORY_INVALID")
    manifest,balance,_=prep.build_preparation(manifest_fields())
    # The success envelope is fully serializable before a test is invoked.
    metrics=dict(lm_bindings=1,payloads=0,receptors=0,nj=0,memory=0,field=0,runtime=0,replays=0,
        event_id_length=14,owner_id_length=20,consume_id_length=22,lm_input_bytes=16384,lm_source_bytes=1024,
        metadata_bytes=65536,record_bytes=4194304,tests_run=30,passed=["a%02d"%n for n in range(1,31)],
        failures=0,errors=0,skipped=0,code_after=a.digest(manifest["code_hashes"]))
    mbytes=a.canonical(metrics)
    result=outcome(manifest,metrics,"QUALIFIED",{name:["0"*64,262144] for name in FILES})
    result_cap=len(a.canonical(result))
    # Remaining bytes belong to full logs, not to another reservation.
    logs_cap=4096-result_cap-len(mbytes)-4
    balance.update(qualification_group=dict(limit=4096,result_ceiling=result_cap,
        metrics_ceiling=len(mbytes),combined_stdout_stderr_ceiling=logs_cap,
        invocation_claim_bytes=4,total_reserved=4096,full_failure_logs_preserved=True),
        qualification_calls=0,status="READY_FOR_ONE_QUALIFICATION",main_gate=False)
    concrete=balance["concrete_shape_with_additional_and_completion_reserves"]
    violations=balance["actual_shape"]["violations"]+concrete["violations"]
    if logs_cap<256:violations.append(dict(code="QUALIFICATION_PREFLIGHT_LIMIT",actual=result_cap+len(mbytes)+256,limit=4096))
    balance["preflight_violations"]=violations
    proof_bytes=len(a.canonical(balance))+8192+sum(x["bytes"] for x in manifest["verification_dependencies"])
    if proof_bytes>262144:violations.append(dict(code="VERIFICATION_PREFLIGHT_LIMIT",actual=proof_bytes,limit=262144))
    if violations:balance["status"]="BUDGET_BLOCKED_NOT_RUN"
    write_raw(out/"manifest.json",a.canonical(manifest))
    write_raw(out/"preflight-balance.json",a.canonical(balance))
    print(json.dumps(dict(status=balance["status"],metadata=balance["actual_shape"]["balance"]["metadata_bytes"],
        concrete_total=concrete["balance"]["total_reserved_bytes"],qualification_group=balance["qualification_group"],
        violations=violations),sort_keys=True))
    return 0 if not violations else 1


def run():
    out=ROOT/a.DIRECTORY
    manifest=json.loads((out/"manifest.json").read_bytes())
    pre=json.loads((out/"preflight-balance.json").read_bytes())
    if pre["status"]!="READY_FOR_ONE_QUALIFICATION" or pre["preflight_violations"]:
        raise ValueError("PREFLIGHT_NOT_VALID")
    current={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in manifest["code_hashes"]}
    if current!=manifest["code_hashes"] or any(manifest.get(k)!=value for k,value in manifest_fields().items()):
        raise ValueError("PREREGISTERED_CODE_CHANGED")
    if pre["manifest_sha256"]!=hashlib.sha256((out/"manifest.json").read_bytes()).hexdigest():
        raise ValueError("PREREGISTRATION_CHANGED")
    if any((out/name).exists() for name in ("qualification.json","metrics.json","stdout.txt","stderr.txt","BEFUND.md","final-balance.json","invoked.claim")):
        raise FileExistsError("QUALIFICATION_ALREADY_INVOKED")
    # Exclusive one-use marker, kept in the 4096-byte qualification budget.
    write_raw(out/"invoked.claim",b"once")
    process=subprocess.run(COMMAND,cwd=ROOT,env=dict(os.environ,S2OA_ACTIVE_QUAL_DIR=str(out)),capture_output=True,check=False)
    write_raw(out/"stdout.txt",process.stdout);write_raw(out/"stderr.txt",process.stderr)
    metrics_raw=(out/"metrics.json").read_bytes() if (out/"metrics.json").exists() else b"{}"
    if not (out/"metrics.json").exists():write_raw(out/"metrics.json",metrics_raw)
    metrics=json.loads(metrics_raw)
    after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in manifest["code_hashes"]}
    metrics["code_after"]=a.digest(after)
    expected=["a%02d"%n for n in range(1,31)]
    passed=(process.returncode==0 and metrics.get("tests_run")==30 and metrics.get("passed")==expected
            and metrics.get("lm_bindings")==1 and not any(metrics.get(k,1) for k in
                ("payloads","receptors","nj","memory","field","runtime","replays","failures","errors","skipped"))
            and after==current)
    status="QUALIFIED" if passed else "NOT_QUALIFIED"
    report=("S2-OA konsolidierter administrativer Anschluss\n"
            +status+"; "+str(len(metrics.get("passed",[])))+"/30; Exit "+str(process.returncode)+".\n"
            "Genau ein Testaufruf; keine historische Passuebernahme.\n"
            "Keine OA-Payloads, keine Geschichte, kein Hauptlauf. Gates False.\n"
            "Vollstaendige Ist-/Reservebilanz: final-balance.json.\n")
    report_bytes=report.encode("ascii")
    fixed={name:(out/name).read_bytes() for name in ("stdout.txt","stderr.txt","metrics.json","invoked.claim","preflight-balance.json")}
    fixed["BEFUND.md"]=report_bytes
    # Only serialized lengths feed this fixed point, never test execution.
    result_bytes=0;final_bytes=b"{}"
    for _ in range(8):
        actual_without_result=sum(len(fixed[n]) for n in ("stdout.txt","stderr.txt","metrics.json"))+4
        group=result_bytes+actual_without_result
        verification=len(fixed["preflight-balance.json"])+len(final_bytes)+sum(x["bytes"] for x in manifest["verification_dependencies"])
        final=dict(schema="s2oa.active-final-balance.v1",run_id=RUN_ID,test_calls=1,exit_code=process.returncode,
            passed_tests=len(metrics.get("passed",[])),code_unchanged=after==current,
            metadata_reserved=pre["actual_shape"]["balance"]["metadata_bytes"],metadata_limit=65536,
            shared_reserved=246289,shared_limit=262144,
            concrete_total_reserved=pre["concrete_shape_with_additional_and_completion_reserves"]["balance"]["total_reserved_bytes"],total_limit=4194304,
            qualification_actual_bytes=group,qualification_reserved_bytes=4096,
            qualification_items={**{n:len(fixed[n]) for n in ("stdout.txt","stderr.txt","metrics.json")},"invoked.claim":4,"qualification.json":result_bytes},
            report_actual_bytes=len(report_bytes),report_reserved_bytes=512,
            prior_and_qualification_verification_bytes=verification,verification_shared_limit=262144,
            remaining_runtime_verification_bytes=262144-verification,main_gate=False,
            full_error_logs_preserved=True,preflight_sha256=hashlib.sha256(fixed["preflight-balance.json"]).hexdigest(),
            violations=[])
        for name,actual,limit in (("QUALIFICATION_LIMIT",group,4096),("REPORT_LIMIT",len(report_bytes),512),("VERIFICATION_LIMIT",verification,262144)):
            if actual>limit:final["violations"].append(dict(code=name,actual=actual,limit=limit))
        if final["violations"] and status=="QUALIFIED":
            status="NOT_QUALIFIED"
            report_bytes=report.replace("QUALIFIED;","NOT_QUALIFIED;").encode("ascii")
            fixed["BEFUND.md"]=report_bytes
            continue
        fb=a.canonical(final)
        file_refs={n:[hashlib.sha256(raw).hexdigest(),len(raw)] for n,raw in {**fixed,"final-balance.json":fb}.items()}
        q=outcome(manifest,metrics,status if not final["violations"] else "NOT_QUALIFIED",file_refs)
        qb=a.canonical(q)
        if len(qb)==result_bytes and len(fb)==len(final_bytes):break
        result_bytes=len(qb);final_bytes=fb
    else:raise ValueError("ADMINISTRATIVE_SIZE_FIXED_POINT_FAILED")
    write_raw(out/"BEFUND.md",report_bytes)
    write_raw(out/"final-balance.json",fb)
    write_raw(out/"qualification.json",qb)
    print(json.dumps(dict(status=q["status"],passed_tests=final["passed_tests"],exit_code=process.returncode,
        qualification_actual_bytes=final["qualification_actual_bytes"],metadata_reserved=final["metadata_reserved"],
        violations=final["violations"],result_digest=q["result_digest"]),sort_keys=True))
    return 0 if q["status"]=="QUALIFIED" else 1


if __name__=="__main__":
    if sys.argv[1:]==["--prepare"]:raise SystemExit(prepare())
    if sys.argv[1:]==["--run"]:raise SystemExit(run())
    raise SystemExit("Use --prepare, then the separately authorized --run once")
