"""One bounded neutral invocation using the existing qualification pattern."""
import ast
import json
import subprocess
import sys

from tools import _s2nr_private_source_binding as b


def main():
    out=b.QUAL_DIR
    out.mkdir(exist_ok=False)
    before=b.watched()
    path=b.ROOT/"tests/test_s2nr_private_source_binding.py"
    tree=ast.parse(path.read_text(encoding="utf-8"))
    names=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    b.require(len(names)==len(set(names))==12,"TEST_INVENTORY_INVALID")
    for n in ast.walk(tree):
        if isinstance(n,ast.Call):
            name=getattr(n.func,"attr",getattr(n.func,"id",None))
            b.require(name not in ("preseal_once","analyze","project_auditory_half_v1","run_main_once","verify_once"),
                      "FORBIDDEN_QUALIFICATION_CALL")
    command=[sys.executable,"-m","unittest","tests.test_s2nr_private_source_binding","-v","-f"]
    b.publish(out/"preregistration.json",dict(run_id=b.QUAL_ID,command=command,cwd=str(b.ROOT),
        test_ids=["tests.test_s2nr_private_source_binding.SourceTests."+n for n in names],
        expected_tests=12,unittest_calls=1,retry=False,hashes_before=before,
        nr_payload_generation_limit=0,neutral_pcm_limit=dict(calls=1,samples=16,bytes=64),
        neutral_rgb_limit=dict(calls=1,bytes=6220800),receptor_calls_limit=0,nj_calls_limit=0,
        forbidden_imports_checked=True,output_limit=b.MAX_OUTPUT_BYTES,metadata_limit=b.MAX_METADATA_BYTES,
        environment=b.environment()),b.MAX_METADATA_BYTES)
    process=subprocess.run(command,cwd=b.ROOT,capture_output=True,check=False)
    for name,data in (("stdout.txt",process.stdout),("stderr.txt",process.stderr)):
        with (out/name).open("xb") as handle:
            handle.write(data)
    after=b.watched()
    transcript=(process.stdout+process.stderr).decode("utf-8",errors="replace")
    passed=process.returncode==0 and "Ran 12 tests" in transcript and transcript.rstrip().endswith("OK") and before==after
    result=b.sealed(dict(run_id=b.QUAL_ID,status="S2NR_SOURCE_BINDING_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=process.returncode,unittest_calls=1,expected_tests=12,passed_tests=12 if passed else None,
        hashes_before=before,hashes_after=after,nr_payload_generation_calls=0,receptor_calls=0,nj_calls=0,
        main_gate_after=False,stdout_sha256=b.filehash(out/"stdout.txt"),stderr_sha256=b.filehash(out/"stderr.txt")),
        "result_digest")
    b.publish(out/"result.json",result,b.MAX_METADATA_BYTES)
    print(json.dumps({k:result[k] for k in ("run_id","status","exit_code","passed_tests","result_digest")}))
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
