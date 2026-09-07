"""Single report-local neutral qualification, no corpus or main entry point."""

import ast
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
QUAL_ID = "s2nn-half-profile-runtime-qualification-20260907-02"
OUT = ROOT / "reports/s2nn" / QUAL_ID
TEST = "tests/test_s2nn_private_half_runtime_binding.py"
GATES = ("tools/_s2ng_private_runtime_comparison.py", "tools/_s2nh_private_runtime_binding.py",
         "tools/_s2nl_private_half_profile_binding.py", "tools/_s2nn_private_half_runtime_binding.py")


def sha(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle,"sha256").hexdigest()


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")


def publish(name,value):
    data = canonical(value)
    if len(data) > 4194304:
        raise ValueError("ARTIFACT_SIZE_LIMIT")
    with (OUT/name).open("xb") as handle:
        handle.write(data)


def gates():
    for path in GATES:
        nodes = ast.parse((ROOT/path).read_text(encoding="utf-8")).body
        found = [ast.literal_eval(n.value) for n in nodes if isinstance(n,ast.Assign)
                 and any(isinstance(t,ast.Name) and t.id == "MAIN_GATE" for t in n.targets)]
        if found != [False]:
            raise ValueError("GATE_NOT_FALSE")
    return dict.fromkeys(GATES,False)


def main():
    OUT.mkdir(exist_ok=False)
    # Read-only AST reuse of the existing NG source inventory is unnecessary:
    # bind all project module files, without importing any research entry point.
    paths = sorted(str(p.relative_to(ROOT)).replace("\\","/") for folder in ("tools","mcm_field_organism")
                   for p in (ROOT/folder).glob("*.py") if p.name != "_s2fq_readonly_bootstrap_caller.py")
    paths += [TEST,"reports/s2nn/qualify_once.py","reports/s2nn/QUALIFIKATIONSBINDUNG.md",
        "reports/s2nn/QUALIFIKATIONSBINDUNG_02.md",
        "docs/S2NK_PRIVATER_PROFILINTEGRATIONSVERTRAG_AUDITIVE_SKALENUEBERTRAGUNG.md",
        "reports/s2nm/s2nm-subnormal-a-conflict-qualification-20260907-01/result.json"]
    before = {p:sha(ROOT/p) for p in paths}
    inventory = sorted(n.name for n in ast.walk(ast.parse((ROOT/TEST).read_text(encoding="utf-8")))
                       if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    if len(inventory) != 14 or len(set(inventory)) != 14:
        raise ValueError("INVENTORY_INVALID")
    command = [sys.executable,"-B","-m","unittest","tests.test_s2nn_private_half_runtime_binding","-v","-f"]
    gate_before = gates()
    publish("preregistration.json",dict(qualification_id=QUAL_ID,command=command,cwd=str(ROOT),
        test_inventory=inventory,expected_tests=14,hashes_before=before,gates=gate_before,
        python=dict(version=sys.version,build=platform.python_build(),executable=sys.executable,
                    executable_sha256=sha(Path(sys.executable))), unittest_calls=1,retry=False,
        budgets=dict(runtime_events=18,formation_attempts=10,field_contacts=4224,
            valid_projections=3,scan_records=12,scan_value_limit=7424,formation_l1_limit=35520,
            max_record_bytes=4194304,max_input_binding_bytes=65536,timeout_seconds=180)))
    try:
        p = subprocess.run(command,cwd=ROOT,env=dict(os.environ,S2NN_QUAL_DIR=str(OUT)),
                           capture_output=True,check=False,timeout=180)
        code,stdout,stderr = p.returncode,p.stdout,p.stderr
    except subprocess.TimeoutExpired as exc:
        code,stdout,stderr = 124,exc.stdout or b"",exc.stderr or b""
    for name,data in (("stdout.txt",stdout),("stderr.txt",stderr)):
        with (OUT/name).open("xb") as handle:
            handle.write(data)
    after = {p:sha(ROOT/p) for p in paths}
    metrics_path = OUT/"metrics.json"
    metrics = json.loads(metrics_path.read_bytes()) if metrics_path.exists() else None
    log = (stdout+stderr).decode("utf-8",errors="replace")
    ran = re.search(r"Ran (\d+) tests?",log)
    expected = dict(runtime_events=18,formation_attempts=10,field_contacts=4224,
                    valid_projection_calls=3,receptor_analyses=0,nh_calls=0)
    ok = code == 0 and ran is not None and int(ran[1]) == 14 and log.rstrip().endswith("OK")
    ok = ok and before == after and gates() == gate_before and metrics == expected
    artifacts = {p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in OUT.iterdir() if p.is_file()}
    result = dict(qualification_id=QUAL_ID,status="S2NN_HALF_RUNTIME_QUALIFIED" if ok else "NOT_QUALIFIED",
        exit_code=code,tests_run=int(ran[1]) if ran else None,expected_tests=14,unittest_calls=1,retry=False,
        hashes_before=before,hashes_after=after,gates_after=gates(),metrics=metrics,artifacts=artifacts,
        semantic_equivalence_to_historical=False,nh_reopened=False,universal_float_guarantee=False)
    result["result_digest"] = hashlib.sha256(canonical(result)).hexdigest()
    publish("result.json",result)
    print(json.dumps({k:result[k] for k in ("qualification_id","status","exit_code","tests_run","metrics","result_digest")}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
