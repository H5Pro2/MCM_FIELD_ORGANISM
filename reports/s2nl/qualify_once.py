"""Single bounded qualification process; no research entry points or NH sources."""

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
QUAL_ID = "s2nl-versioned-rank-scale-qualification-20260907-01"
OUT = ROOT / "reports/s2nl" / QUAL_ID
TEST = "tests/test_s2nl_private_rank_scale.py"
HISTORICAL = (
    "test_foreign_timed_binding_fails_closed",
    "test_fast_create_update_and_consolidation_are_separate",
    "test_lru_replacement_uses_last_selected_step_then_slot_id",
    "test_atomic_failure_of_second_ppb_step_publishes_nothing",
    "test_read_only_probe_prefers_slow_then_fast_and_changes_no_state",
)
SOURCES = (
    "mcm_field_organism/_tspm1_private.py",
    "mcm_field_organism/_ppb1_receptor_profiles.py",
    "mcm_field_organism/_ppb1_active_receptor_batch_binding.py",
    "tools/_s2jw_default_live_profile.py",
    "tools/_s2jw_default_live_av_pairing.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2jw_profiled_memory_read_only.py",
    "tools/_s2nl_private_half_profile_binding.py",
    "tools/_s2nl_private_rank_verification.py",
    TEST,
    "reports/s2nl/qualify_once.py",
    "reports/s2nl/QUALIFIKATIONSBINDUNG.md",
    "docs/S2NK_PRIVATER_PROFILINTEGRATIONSVERTRAG_AUDITIVE_SKALENUEBERTRAGUNG.md",
    "tests/test_tspm1_s2dh_private_fast_core.py",
    "mcm_field_organism/_ppb1_reference.py",
    "mcm_field_organism/log_spectral_receptor.py",
    "mcm_field_organism/broadband_hearing_path.py",
    "tools/_s2jw_profiled_memory_ledger.py",
    "tools/_s2nj_private_auditory_output_projection.py",
    "tools/_s2kz_private_auditory_partial_cue_retrieval_336.py",
    "tools/_s2kz_private_direct_auditory_slot_scan_baseline.py",
    "tools/_s2ne_private_auditory_transfer.py",
    "tools/_s2ne_private_direct_and_verification.py",
    "tools/_s2mr_private_minimal_mcm_runtime.py",
    "tools/_s2nh_private_runtime_binding.py",
    "tools/_s2ng_private_runtime_comparison.py",
)
GATES = ("tools/_s2nh_private_runtime_binding.py", "tools/_s2ng_private_runtime_comparison.py",
         "tools/_s2nl_private_half_profile_binding.py")


def sha(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


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
    if len(inventory) != 24 or len(set(inventory)) != 24:
        raise ValueError("TEST_INVENTORY_INVALID")
    hist = ["tests.test_tspm1_s2dh_private_fast_core.TSPM1S2DHPrivateFastCoreTests."+n for n in HISTORICAL]
    command = [sys.executable, "-B", "-m", "unittest", "tests.test_s2nl_private_rank_scale", *hist, "-v", "-f"]
    gate_before = gates()
    publish("preregistration.json", dict(qualification_id=QUAL_ID, command=command, cwd=str(ROOT),
        expected_tests=29, new_tests=inventory, historical_tests=hist, hashes_before=before,
        python=dict(version=sys.version, build=platform.python_build(), executable=sys.executable,
                    executable_sha256=sha(Path(sys.executable)), float_info=tuple(sys.float_info)),
        gates=gate_before, unittest_calls=1, retry=False,
        budgets=dict(match_pairs=30, subnormal_pairs=3, new_atomic_formations=13,
            direct_ppb_steps=16, neutral_receptor_calls=1, max_all_atomic_attempts=40,
            fast_terms=1008, b4_terms=3024, rank_bytes=16384, pair_bytes=65536,
            partial_scan_comparisons=528, partial_scan_bytes_exclusive=32768,
            numeric_state_bytes=44544, json_bytes=1048576, timeout_seconds=300)))
    env = dict(os.environ, S2NL_QUAL_DIR=str(OUT))
    timeout = False
    try:
        process = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, check=False, timeout=300)
        code, stdout, stderr = process.returncode, process.stdout, process.stderr
    except subprocess.TimeoutExpired as exc:
        timeout = True
        code, stdout, stderr = 124, exc.stdout or b"", exc.stderr or b""
    for name, data in (("stdout.txt", stdout), ("stderr.txt", stderr)):
        with (OUT/name).open("xb") as handle:
            handle.write(data)
    after = {p: sha(ROOT/p) for p in SOURCES}
    observation = OUT/"observations.json"
    values = json.loads(observation.read_bytes()) if observation.exists() else None
    log = (stdout+stderr).decode("utf-8", errors="replace")
    ran = re.search(r"Ran (\d+) tests?", log)
    counters = values["counters"] if values else None
    ok = (code == 0 and ran is not None and int(ran[1]) == 29 and log.rstrip().endswith("OK")
          and before == after and gates() == gate_before and counters == dict(atomic_formations=13,
          direct_ppb_steps=16, neutral_receptor_calls=1, match_pairs=30, subnormal_pairs=3))
    numerical = values["numerical"] if values else []
    deviations = [r for r in numerical if not r["exact_scale_equal"]
                  or r.get("old_match") != r.get("new_match")
                  or r.get("old_equal") != r.get("new_equal")]
    result = dict(qualification_id=QUAL_ID,
        status="S2NL_RANK_SCALE_COMPOSITION_QUALIFIED" if ok else "NOT_QUALIFIED",
        exit_code=code, timeout=timeout, tests_run=int(ran[1]) if ran else None,
        expected_tests=29, passed_tests=29 if ok else None, unittest_calls=1, retry=False,
        counters=counters, hashes_before=before, hashes_after=after, gates_after=gates(),
        stdout_sha256=sha(OUT/"stdout.txt"), stderr_sha256=sha(OUT/"stderr.txt"),
        observations_sha256=sha(observation) if observation.exists() else None,
        numerical_deviations=deviations, universal_float_guarantee=False,
        nh_source_calls=0, field_calls=0, runtime_calls=0)
    result["result_digest"] = hashlib.sha256(canonical(result)).hexdigest()
    publish("result.json", result)
    print(json.dumps({k: result[k] for k in ("qualification_id", "status", "exit_code", "tests_run", "counters", "result_digest")}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
