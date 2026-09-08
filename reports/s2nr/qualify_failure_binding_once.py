"""One three-test call, reusing only stored neutral evidence."""
import ast
import json
import os
import subprocess
import sys
from tools import _s2nr_private_run as run

ID="s2nr-main-binding-focused-qualification-20260908-01"
OLD="reports/s2nr/s2nr-main-binding-qualification-20260908-01"
TYPES="reports/s2nr/s2nr-runtime-binding-qualification-20260908-01"
TEST="tests/test_s2nr_private_run.py"
OWN=("reports/s2nr/qualify_failure_binding_once.py","reports/s2nr/FOCUSED_QUALIFIKATIONSBINDUNG.md")
PINS={OLD+"/result.json":"31c63daa509d7e3f516ef769b5537a06d0da189c3135adddfa3d9d042efb0d41",
    TYPES+"/result.json":"f053795a4b4b98d8bd6e258338f97448462336deb9ff50e2704fdc8af757fe6f"}


def hashes():
    values=run.watched()
    paths=set(OWN)
    for directory in (OLD,TYPES):
        paths.update(p.relative_to(run.ROOT).as_posix() for p in (run.ROOT/directory).rglob("*") if p.is_file())
    values.update({p:run.source.filehash(run.ROOT/p) for p in sorted(paths)})
    return dict(sorted(values.items()))


def main():
    out=run.ROOT/"reports/s2nr"/ID
    out.mkdir(exist_ok=False)
    before=hashes()
    run.require(all(before[p]==h for p,h in PINS.items()),"HISTORICAL_RESULT_CHANGED")
    old=json.loads((run.ROOT/OLD/"result.json").read_bytes())
    run.check(old,"result_digest")
    current=run.watched()
    run.require(set(current)==set(old["hashes_after"]) and
        sorted(k for k in current if current[k]!=old["hashes_after"][k])==[TEST],"PRODUCT_OR_BINDINGS_CHANGED")
    previous=subprocess.run(["git","show","161c058a:"+TEST],cwd=run.ROOT,capture_output=True,check=True).stdout
    original=ast.parse(previous.decode("utf-8"))
    tree=ast.parse((run.ROOT/TEST).read_text(encoding="utf-8"))
    prior=next(n for n in original.body if isinstance(n,ast.ClassDef) and n.name=="NRRunTests")
    present=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="NRRunTests")
    prior.body=[n for n in prior.body if not isinstance(n,ast.FunctionDef) or not n.name.startswith("test_12_")]
    run.require(ast.dump(prior)==ast.dump(present),"PREVIOUS_ELEVEN_CHANGED")
    focused=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="NRFailureBindingTests")
    tests=sorted(n.name for n in focused.body if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    run.require(tests==["test_12a_failure_progress_uses_own_plan","test_12b_evaluation_requires_matching_verification",
        "test_12c_wrong_plan_remains_total_binding_invalid"],"INVENTORY_INVALID")
    command=[sys.executable,"-m","unittest","tests.test_s2nr_private_run.NRFailureBindingTests","-v"]
    run.source.publish(out/"preregistration.json",dict(run_id=ID,tests=tests,expected_tests=3,
        command=command,cwd=str(run.ROOT),hashes_before=before,environment=run.source.environment(),
        unittest_calls=1,retry=False,previous_eleven_ast_unchanged=True,
        budgets=dict(verification_entries=2,evaluation_entries=1,payloads=0,receptors=0,nj=0,formations=0,
            runtime_events=0,field_contacts=0,scans=0,distance_calculations=0,control_bytes=65536),
        inherited_results=PINS,product_changes=[],administrative_copy_rebinding=[TEST]))
    result=subprocess.run(command,cwd=run.ROOT,env={**os.environ,"S2NR_MAIN_QUAL_DIR":str(out)},capture_output=True,check=False)
    for name,data in (("stdout.txt",result.stdout),("stderr.txt",result.stderr)):
        with (out/name).open("xb") as f:
            f.write(data)
    after=hashes()
    text=(result.stdout+result.stderr).decode("utf-8",errors="replace")
    metrics=json.loads((out/"metrics.json").read_bytes()) if (out/"metrics.json").exists() else None
    controls={}
    for name in ("progress-control.json","evaluation-control.json","wrong-root-control.json"):
        if (out/name).exists():
            run.require((out/name).stat().st_size<=65536,"CONTROL_SIZE_EXCEEDED")
            c=json.loads((out/name).read_bytes())
            controls[name]=dict(file_sha256=run.source.filehash(out/name),error_class=c["error_class"],
                error_code=c["error_code"],input_unchanged=c["input_unchanged"])
    passed=result.returncode==0 and "Ran 3 tests" in text and text.rstrip().endswith("OK") and before==after
    passed=passed and len(controls)==3 and metrics is not None and metrics["total_verifications"]==2
    passed=passed and all(v==0 for k,v in (metrics or {}).items() if k!="total_verifications")
    report=run.sealed(dict(run_id=ID,status="S2NR_FOCUSED_BINDING_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=result.returncode,passed_tests=3 if passed else None,expected_tests=3,unittest_calls=1,
        hashes_before=before,hashes_after=after,metrics=metrics,controls=controls,
        previous_eleven_ast_unchanged=True,product_sources_unchanged=before==after,
        coverage_completed=passed,inherited_results=PINS,historical_failure_unchanged=True,
        main_gate_after=False,main_entry_qualification_reference_unchanged=True,
        stderr_sha256=run.source.filehash(out/"stderr.txt")),"result_digest")
    run.source.publish(out/"result.json",report)
    print(json.dumps({k:report[k] for k in ("run_id","status","passed_tests","exit_code","result_digest","controls")}))
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
