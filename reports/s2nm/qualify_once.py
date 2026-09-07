"""One focused qualification, following the existing report-local NL pattern."""

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
QUAL_ID = "s2nm-subnormal-a-conflict-qualification-20260907-01"
OUT = ROOT / "reports/s2nm" / QUAL_ID
TEST = "tests/test_s2nm_subnormal_a_conflict.py"
NL = "reports/s2nl/s2nl-versioned-rank-scale-qualification-20260907-01/"
SOURCES = (
    TEST, "reports/s2nm/qualify_once.py", "reports/s2nm/QUALIFIKATIONSBINDUNG.md",
    NL+"observations.json", NL+"result.json",
    "mcm_field_organism/_tspm1_private.py", "mcm_field_organism/_tspm1_s2dr_private_comparison.py",
    "mcm_field_organism/_ppb1_reference.py", "mcm_field_organism/_ppb1_receptor_profiles.py",
    "mcm_field_organism/log_spectral_receptor.py", "mcm_field_organism/broadband_hearing_path.py",
    "tools/_s2jw_default_live_profile.py", "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2jw_profiled_memory_ledger.py", "tools/_s2nj_private_auditory_output_projection.py",
    "tools/_s2nl_private_half_profile_binding.py",
    "tools/_s2kz_private_auditory_partial_cue_retrieval_336.py",
    "tools/_s2kz_private_direct_auditory_slot_scan_baseline.py",
    "tools/_s2ne_private_auditory_transfer.py", "tools/_s2ne_private_direct_and_verification.py",
    "tools/_s2nh_private_runtime_binding.py", "tools/_s2ng_private_runtime_comparison.py",
)
GATES = ("tools/_s2nh_private_runtime_binding.py", "tools/_s2ng_private_runtime_comparison.py",
         "tools/_s2nl_private_half_profile_binding.py")


def sha(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def publish(name, value):
    data = canonical(value)
    if len(data) > 1048576:
        raise ValueError("ARTIFACT_SIZE_LIMIT")
    with (OUT/name).open("xb") as handle:
        handle.write(data)


def gates():
    for path in GATES:
        nodes = ast.parse((ROOT/path).read_text(encoding="utf-8")).body
        found = [ast.literal_eval(n.value) for n in nodes if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == "MAIN_GATE" for t in n.targets)]
        if found != [False]:
            raise ValueError("GATE_NOT_FALSE")
    return {p: False for p in GATES}


def main():
    OUT.mkdir(exist_ok=False)
    before = {p: sha(ROOT/p) for p in SOURCES}
    tree = ast.parse((ROOT/TEST).read_text(encoding="utf-8"))
    inventory = sorted(n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
    expected = ["test_01_smallest_subnormal_zero", "test_02_three_four_subnormal", "test_03_normal_boundary"]
    if inventory != expected:
        raise ValueError("TEST_INVENTORY_INVALID")
    command = [sys.executable, "-B", "-m", "unittest", "tests.test_s2nm_subnormal_a_conflict", "-v", "-f"]
    gate_before = gates()
    publish("preregistration.json", dict(qualification_id=QUAL_ID, command=command, cwd=str(ROOT),
        test_inventory=inventory, expected_tests=3, hashes_before=before,
        python=dict(version=sys.version, build=platform.python_build(), executable=sys.executable,
                    executable_sha256=sha(Path(sys.executable)), float_info=tuple(sys.float_info)),
        gates=gate_before, unittest_calls=1, retry=False,
        budgets=dict(pairs=3, profiles=2, rules=2, evidence_records=24, projection_calls=6,
            scan_capacities=[9,3,8], scan_value_limit=528, actual_total_value_comparisons=2304,
            arm_bytes_exclusive=32768, json_bytes=1048576, timeout_seconds=120,
            formations=0, receptor_analyses=0, field_calls=0, runtime_calls=0)))
    try:
        process = subprocess.run(command, cwd=ROOT, env=dict(os.environ, S2NM_QUAL_DIR=str(OUT)),
                                 capture_output=True, check=False, timeout=120)
        code, stdout, stderr = process.returncode, process.stdout, process.stderr
    except subprocess.TimeoutExpired as exc:
        code, stdout, stderr = 124, exc.stdout or b"", exc.stderr or b""
    for name, data in (("stdout.txt", stdout), ("stderr.txt", stderr)):
        with (OUT/name).open("xb") as handle:
            handle.write(data)
    after = {p: sha(ROOT/p) for p in SOURCES}
    path = OUT/"observations.json"
    observations = json.loads(path.read_bytes()) if path.exists() else None
    log = (stdout+stderr).decode("utf-8", errors="replace")
    ran = re.search(r"Ran (\d+) tests?", log)
    ok = (code == 0 and ran is not None and int(ran[1]) == 3 and log.rstrip().endswith("OK")
          and before == after and gates() == gate_before and observations is not None
          and observations["primary_decisions"] == 12 and observations["evidence_records"] == 24)
    changes = observations["semantic_changes"] if observations else []
    result = dict(qualification_id=QUAL_ID,
        technical_status="S2NM_FOCUSED_QUALIFICATION_PASSED" if ok else "NOT_QUALIFIED",
        exit_code=code, tests_run=int(ran[1]) if ran else None, expected_tests=3,
        unittest_calls=1, retry=False, hashes_before=before, hashes_after=after, gates_after=gates(),
        observations_sha256=sha(path) if path.exists() else None,
        stdout_sha256=sha(OUT/"stdout.txt"), stderr_sha256=sha(OUT/"stderr.txt"),
        semantic_changes=changes, semantic_status=("SEMANTIC_DEVIATION_CONFIRMED" if ok and
            len(changes) == 6 and all(r["old"] == "ABSTAIN_INTERNAL_CONFLICT" and
            r["new"] == "ADMIT_SINGLE_CONTEXT" for r in changes) else "NOT_ESTABLISHED"),
        universal_float_guarantee=False, system_integration=False)
    result["result_digest"] = hashlib.sha256(canonical(result)).hexdigest()
    publish("result.json", result)
    print(json.dumps({k: result[k] for k in ("qualification_id", "technical_status", "semantic_status",
                                            "exit_code", "tests_run", "result_digest")}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
