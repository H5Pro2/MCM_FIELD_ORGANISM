"""Assemble administrative coverage once; qualify only its four admission cases."""
import ast
import json
import os
import subprocess
import sys
from tools import _s2nr_private_qualification_binding as binding

run=binding.run


def static_change_binding():
    previous=subprocess.run(["git","show","519e1db2:"+binding.ENTRY],cwd=run.ROOT,capture_output=True,check=True).stdout
    before=ast.parse(previous.decode("utf-8"))
    after=ast.parse((run.ROOT/binding.ENTRY).read_text(encoding="utf-8"))
    owners=[]
    for tree in (before,after):
        own=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="OWN" for t in n.targets))
        owners.append(ast.literal_eval(own.value))
        tree.body.remove(own)
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="run_main_once")
        block=next(n for n in ast.walk(function) if isinstance(n,ast.Try) and any(isinstance(v,ast.Assign)
            and any(isinstance(t,ast.Name) and t.id=="bound" for t in v.targets) for v in n.body))
        index=next(i for i,n in enumerate(block.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="bound" for t in n.targets))
        removed=block.body[:index]
        if tree is after:
            run.require(len(removed)==2 and isinstance(removed[0],ast.ImportFrom)
                and removed[0].module=="tools._s2nr_private_qualification_binding"
                and ast.unparse(removed[1])=="require_combined_qualification()","ADMINISTRATIVE_CALL_INVALID")
        block.body=block.body[index:]
    run.require(owners[1]==owners[0]+binding.ADDED and ast.dump(before)==ast.dump(after),"UNAUTHORIZED_RUNNER_CHANGE")
    return dict(previous_commit="519e1db2",remaining_runner_ast_equal=True,
        changed_scope=["OWN administrative file additions","qualification admission prefix only"],
        unchanged_body_digest=run.digest(ast.dump(after)))


def main():
    out=run.ROOT/"reports/s2nr"/binding.QUAL_ID
    out.mkdir(exist_ok=False)
    delta=static_change_binding()
    bundle=binding.make_bundle()
    destination=run.ROOT/binding.BUNDLE
    destination.parent.mkdir(exist_ok=False)
    run.source.publish(destination,bundle,65536)
    before=binding.watched()
    test_path=run.ROOT/"tests/test_s2nr_private_qualification_binding.py"
    tree=ast.parse(test_path.read_text(encoding="utf-8"))
    names=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    run.require(len(names)==len(set(names))==4,"TEST_INVENTORY_INVALID")
    command=[sys.executable,"-m","unittest","tests.test_s2nr_private_qualification_binding","-v"]
    run.source.publish(out/"preregistration.json",dict(run_id=binding.QUAL_ID,tests=names,expected_tests=4,
        command=command,cwd=str(run.ROOT),hashes_before=before,environment=run.source.environment(),
        unittest_calls=1,retry=False,qualification_digest=bundle["qualification_digest"],administrative_delta=delta,
        scope="new administrative admission only; no repeated historical qualification",
        budgets=dict(admission_calls=4,control_bytes=65536,bundle_bytes=65536,artifact_bytes=run.ng.MAX_BYTES,
            payloads=0,receptors=0,nj=0,memory=0,field=0,runtime=0,scans=0)))
    p=subprocess.run(command,cwd=run.ROOT,env={**os.environ,"S2NR_CONNECTION_QUAL_DIR":str(out)},capture_output=True,check=False)
    for name,data in (("stdout.txt",p.stdout),("stderr.txt",p.stderr)):
        with (out/name).open("xb") as f:
            f.write(data)
    after=binding.watched()
    text=(p.stdout+p.stderr).decode("utf-8",errors="replace")
    control_names=("accepted.json",)+tuple(n+".json" for n in names[1:])
    controls={n:run.source.filehash(out/n) for n in control_names if (out/n).exists()}
    passed=p.returncode==0 and "Ran 4 tests" in text and text.rstrip().endswith("OK") and before==after and len(controls)==4
    passed=passed and all((out/n).stat().st_size<=65536 for n in controls)
    result=run.sealed(dict(run_id=binding.QUAL_ID,status="S2NR_QUALIFICATION_CONNECTION_QUALIFIED" if passed else "NOT_QUALIFIED",
        passed_tests=4 if passed else None,expected_tests=4,unittest_calls=1,exit_code=p.returncode,
        qualification_digest=bundle["qualification_digest"],qualification_file_sha256=run.source.filehash(destination),
        hashes_before=before,hashes_after=after,administrative_delta=delta,controls=controls,
        no_historical_tests_repeated=True,main_gate_after=False,stderr_sha256=run.source.filehash(out/"stderr.txt")),"result_digest")
    run.source.publish(out/"result.json",result)
    print(json.dumps({k:result[k] for k in ("run_id","status","passed_tests","exit_code","qualification_digest","result_digest")}))
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
