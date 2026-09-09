"""Single neutral test invocation; no OA payloads."""
import ast
import json
import subprocess
import sys
from tools import _s2oa_private_source_binding as b


def main():
    out=b.QUAL_DIR; out.mkdir(exist_ok=False)
    before=b.watched()
    tree=ast.parse((b.ROOT/"tests/test_s2oa_private_source_binding.py").read_text(encoding="utf-8"))
    names=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    b.require(len(names)==len(set(names))==b.TEST_COUNT,"TEST_INVENTORY_INVALID")
    command=[sys.executable,"-m","unittest","tests.test_s2oa_private_source_binding","-v"]
    b.publish(out/"preregistration.json",dict(run_id=b.QUAL_ID,command=command,cwd=str(b.ROOT),
        test_ids=names,expected_tests=b.TEST_COUNT,unittest_calls=1,retry=False,hashes_before=before,
        environment=b.environment(),oa_payload_generation_limit=0,neutral_pcm=dict(calls=1,samples=16,bytes=64),
        neutral_rgb=dict(calls=1,ordinal=1,bytes=6220800),receptor_limit=0,nj_limit=0,
        system_import_block=True,metadata_limit=b.MAX_METADATA_BYTES),b.MAX_METADATA_BYTES)
    process=subprocess.run(command,cwd=b.ROOT,capture_output=True,check=False)
    for name,data in (("stdout.txt",process.stdout),("stderr.txt",process.stderr)):
        with (out/name).open("xb") as handle: handle.write(data)
    after=b.watched()
    transcript=(process.stdout+process.stderr).decode("utf-8",errors="replace")
    passed=process.returncode==0 and "Ran 18 tests" in transcript and transcript.rstrip().endswith("OK") and before==after
    result=b.sealed(dict(run_id=b.QUAL_ID,status="S2OA_SOURCE_BINDING_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=process.returncode,unittest_calls=1,expected_tests=b.TEST_COUNT,passed_tests=b.TEST_COUNT if passed else None,
        hashes_before=before,hashes_after=after,oa_payload_calls=0,receptor_calls=0,nj_calls=0,main_gate_after=False,
        stdout_sha256=b.filehash(out/"stdout.txt"),stderr_sha256=b.filehash(out/"stderr.txt")),"result_digest")
    b.publish(out/"result.json",result,b.MAX_METADATA_BYTES)
    print(json.dumps({k:result[k] for k in ("run_id","status","exit_code","passed_tests","result_digest")}))
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
