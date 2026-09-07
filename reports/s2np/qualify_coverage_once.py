"""Exactly one bounded neutral qualification; no corpus comparison entry point."""

import ast
import json
import subprocess
import sys

from tools import _s2np_private_source_binding as b

RUN_ID = "s2np-coverage-comparison-qualification-20260907-02"
TEST_FILE = "tests/test_s2np_private_coverage_comparison.py"
OWN = (
    "tools/_s2np_private_coverage_comparison.py",
    "tools/_s2np_private_coverage_baseline.py",
    "tools/_s2np_private_coverage_evaluation.py", TEST_FILE,
    "reports/s2np/qualify_coverage_once.py",
    "reports/s2np/S2NP_ABDECKUNGSVERGLEICH_QUALIFIKATIONSBINDUNG.md",
)
PRIOR = (
    "tools/_s2np_private_receptor_materialization.py",
    "tools/_s2np_private_materialization_verification.py",
    "reports/s2np/s2np-source-preseal-20260907-01/execution-plan.json",
    "reports/s2np/s2np-source-preseal-20260907-01/evaluation-plan.json",
    "reports/s2np/s2np-source-preseal-20260907-01/seal.json",
    "reports/s2np/s2np-receptor-nj-materialization-20260907-01/result.json",
    "reports/s2np/s2np-receptor-nj-materialization-20260907-01/verification.json",
)


def hashes():
    return {**b.watched(), **{path: b.filehash(b.ROOT / path) for path in OWN + PRIOR}}


def main():
    out = b.ROOT / "reports/s2np" / RUN_ID
    out.mkdir(exist_ok=False)
    before = hashes()
    names = []
    for path in OWN[:4]:
        tree = ast.parse((b.ROOT / path).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = getattr(node.func, "attr", getattr(node.func, "id", None))
                b.require(name not in ("preseal_once", "analyze", "project_auditory_half_v1", "run_main_once",
                                       "pcm_bytes", "pure_generator", "materialize_once"), "FORBIDDEN_CALL")
            if isinstance(node, ast.ImportFrom):
                b.require(node.module is None or not node.module.startswith("mcm_field_organism"), "SYSTEM_IMPORT")
            if path == TEST_FILE and isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                names.append(node.name)
    names.sort()
    b.require(len(names) == len(set(names)) == 22, "TEST_INVENTORY_INVALID")
    command = [sys.executable, "-m", "unittest", "tests.test_s2np_private_coverage_comparison", "-v"]
    b.publish(out / "preregistration.json", dict(run_id=RUN_ID, command=command, cwd=str(b.ROOT),
        test_ids=["tests.test_s2np_private_coverage_comparison.CoverageTests." + name for name in names],
        expected_tests=22, unittest_calls=1, retry=False, hashes_before=before, environment=b.environment(),
        neutral_difference_limit=16384, neutral_full_panel_sets=2,
        future_panel_findings_per_implementation=360, future_total_band_differences=7680,
        max_output_bytes=2097152, max_panel_bytes=32768,
        np_materialization_read_mode="file-hash-only-no-parsing", np_value_comparisons=0,
        payload_generation_calls=0, receptor_calls=0, nj_calls=0, system_calls=0, main_gate=False), b.MAX_METADATA_BYTES)
    process = subprocess.run(command, cwd=b.ROOT, capture_output=True, check=False)
    for name, data in (("stdout.txt", process.stdout), ("stderr.txt", process.stderr)):
        with (out / name).open("xb") as handle:
            handle.write(data)
    after = hashes()
    transcript = (process.stdout + process.stderr).decode("utf-8", errors="replace")
    metrics = [json.loads(line.removeprefix("NEUTRAL_METRICS ")) for line in transcript.splitlines()
               if line.startswith("NEUTRAL_METRICS ")]
    passed = (process.returncode == 0 and "Ran 22 tests" in transcript and transcript.rstrip().endswith("OK")
              and before == after and len(metrics) == 1 and metrics[0]["band_differences"] <= 16384
              and 0 < metrics[0]["maximum_serialized_bytes"] <= 2097152)
    result = b.sealed(dict(run_id=RUN_ID, status="S2NP_COVERAGE_COMPARISON_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=process.returncode, unittest_calls=1, expected_tests=22, passed_tests=22 if passed else None,
        hashes_before=before, hashes_after=after, neutral_metrics=metrics,
        stdout_sha256=b.filehash(out / "stdout.txt"), stderr_sha256=b.filehash(out / "stderr.txt"),
        np_payload_generation_calls=0, np_receptor_value_comparisons=0, receptor_calls=0, nj_calls=0,
        memory_calls=0, field_calls=0, context_calls=0, runtime_calls=0, main_gate_after=False), "result_digest")
    b.publish(out / "result.json", result, b.MAX_METADATA_BYTES)
    print(json.dumps({key: result[key] for key in ("run_id", "status", "exit_code", "passed_tests", "result_digest")}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
