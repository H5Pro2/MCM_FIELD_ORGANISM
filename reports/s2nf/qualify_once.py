"""One neutral S2-NF qualification invocation; no PCM source generation."""

import ast
import json
import subprocess
import sys

from tools import _s2nf_private_source_binding as b


def main():
    out = b.ROOT / b.QUAL_DIR
    out.mkdir(exist_ok=False)
    before = b.watched()
    test_path = b.ROOT / "tests/test_s2nf_private_source_binding.py"
    tree = ast.parse(test_path.read_text(encoding="utf-8"))
    names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")]
    b.require(len(names) == len(set(names)) == 10, "TEST_INVENTORY_INVALID")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", getattr(node.func, "id", None))
            b.require(name not in ("generate_digest", "pcm_payload", "_materialize_pcm", "preseal_once", "analyze"), "FORBIDDEN_TEST_CALL")
    command = [sys.executable, "-m", "unittest", "tests.test_s2nf_private_source_binding", "-v"]
    b.publish(out / "preregistration.json", dict(run_id=out.name, command=command, cwd=str(b.ROOT),
        test_ids=["tests.test_s2nf_private_source_binding.SourceBindingTests." + n for n in sorted(names)],
        expected_tests=10, unittest_calls=1, retry=False, hashes_before=before,
        pcm_generation_calls=0, receptor_calls=0, static_call_inventory_checked=True,
        python_version=sys.version, interpreter_sha256=b.filehash(b.ROOT.__class__(sys.executable))))
    process = subprocess.run(command, cwd=b.ROOT, capture_output=True, check=False)
    for name, data in (("stdout.txt", process.stdout), ("stderr.txt", process.stderr)):
        with (out / name).open("xb") as handle:
            handle.write(data)
    after = b.watched()
    transcript = (process.stdout + process.stderr).decode("utf-8", errors="replace")
    passed = process.returncode == 0 and "Ran 10 tests" in transcript and transcript.rstrip().endswith("OK") and before == after
    result = b.sealed(dict(run_id=out.name, status="S2NF_SOURCE_BINDING_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=process.returncode, unittest_calls=1, expected_tests=10,
        passed_tests=10 if passed else None, pcm_generation_calls=0, receptor_calls=0,
        hashes_before=before, hashes_after=after,
        stdout_sha256=b.filehash(out / "stdout.txt"), stderr_sha256=b.filehash(out / "stderr.txt")), "result_digest")
    b.publish(out / "result.json", result)
    print(json.dumps({k: result[k] for k in ("run_id", "status", "exit_code", "passed_tests", "result_digest")}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
