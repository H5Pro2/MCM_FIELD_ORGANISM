"""Exactly one neutral S2-NJ test invocation; exclusive qualification folder."""

import ast
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
QUAL_ID = "s2nj-private-output-half-qualification-20260907-01"
OUT = ROOT / "reports/s2nj" / QUAL_ID
TEST = "tests/test_s2nj_private_auditory_output_projection.py"
GATES = ("tools/_s2nh_private_runtime_binding.py", "tools/_s2ng_private_runtime_comparison.py")
WATCHED = (TEST, "tools/_s2nj_private_auditory_output_projection.py", "reports/s2nj/qualify_once.py",
    "reports/s2nj/QUALIFIKATIONSBINDUNG.md", "docs/S2NI_STATISCHER_AUDITIVER_REZEPTOR_KONTAKT_SKALIERUNGSVERTRAG.md",
    "mcm_field_organism/log_spectral_receptor.py", "mcm_field_organism/broadband_hearing_path.py",
    "mcm_field_organism/carrier_baselines.py", "mcm_field_organism/controlled_audio_source.py",
    "mcm_field_organism/receptor_contract.py", "tools/_s2jw_default_live_profile.py",
    "tools/_s2jw_profiled_memory_coordinator.py", "tools/_s2mr_private_minimal_mcm_runtime.py",
    "reports/s2nh/s2nh-runtime-comparison-20260907-01/recording.json",
    "reports/s2nh/s2nh-e02-audio-endpoint-diagnostic-20260907-01/recording.json") + GATES


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def sha(v):
    return hashlib.sha256(v).hexdigest()


def filehash(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def publish(path, value):
    data = canonical(value)
    if len(data) > 131072:
        raise ValueError("QUALIFICATION_OUTPUT_LIMIT")
    with path.open("xb") as f:
        f.write(data)


def gates():
    result = {}
    for name in GATES:
        nodes = ast.parse((ROOT/name).read_text(encoding="utf-8")).body
        matches = [ast.literal_eval(n.value) for n in nodes if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "MAIN_GATE" for t in n.targets)]
        if matches != [False]:
            raise ValueError("MAIN_GATE_NOT_FALSE")
        result[name] = False
    return result


def main():
    OUT.mkdir(exist_ok=False)
    before = {p: filehash(ROOT/p) for p in WATCHED}
    tree = ast.parse((ROOT/TEST).read_text(encoding="utf-8"))
    inventory = sorted(n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
    recipes = [ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == "NEUTRAL_CASES" for t in n.targets)]
    if len(inventory) != len(set(inventory)) or len(inventory) != 16 or len(recipes) != 1 or len(recipes[0]) != 8:
        raise ValueError("INVENTORY_INVALID")
    origin = math.__spec__.origin
    if origin == "built-in" and "math" in sys.builtin_module_names:
        math_id = dict(origin=origin, builtin_membership=True)
    elif origin and Path(origin).is_file() and getattr(math, "__file__", None) == origin:
        math_id = dict(origin=origin, sha256=filehash(Path(origin)))
    else:
        raise ValueError("MATH_IDENTITY_INVALID")
    command = [sys.executable, "-B", "-m", "unittest", "tests.test_s2nj_private_auditory_output_projection", "-v", "-f"]
    gate_before = gates()
    publish(OUT/"preregistration.json", dict(qualification_id=QUAL_ID, command=command, cwd=str(ROOT),
        test_inventory=inventory, expected_tests=16, neutral_cases=recipes[0], hashes_before=before,
        python=dict(version=sys.version, build=platform.python_build(), executable=sys.executable,
                    executable_sha256=filehash(Path(sys.executable)), float_info=tuple(sys.float_info)),
        numpy=dict(version=np.__version__, binary=np._core._multiarray_umath.__file__,
                   binary_sha256=filehash(Path(np._core._multiarray_umath.__file__))), math=math_id,
        limits=dict(real_pcm_windows=8, receptor_analyses=8, real_receptor_values=384,
                    max_live_pcm_windows=1, projection_bytes=16384, json_artifact_bytes=131072),
        gates=gate_before, unittest_calls=1, retry=False, nh_sources=0))
    env = dict(os.environ, S2NJ_QUAL_DIR=str(OUT))
    process = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, check=False)
    for name, data in (("stdout.txt", process.stdout), ("stderr.txt", process.stderr)):
        with (OUT/name).open("xb") as f:
            f.write(data)
    after = {p: filehash(ROOT/p) for p in WATCHED}
    log = (process.stdout+process.stderr).decode("utf-8", errors="replace")
    observation_path = OUT/"observations.json"
    observations = json.loads(observation_path.read_bytes()) if observation_path.exists() else None
    counts = observations["counters"] if observations else None
    ok = (process.returncode == 0 and "Ran 16 tests" in log and log.rstrip().endswith("OK")
          and before == after and gates() == gate_before and counts == dict(pcm_generations=8,
          receptor_calls=8, completed_analyses=8, recorded_projections=8)
          and observation_path.stat().st_size <= 131072)
    ran = re.search(r"Ran (\d+) tests?", log)
    result = dict(qualification_id=QUAL_ID, status="S2NJ_PRIVATE_OUTPUT_PROJECTION_QUALIFIED" if ok else "NOT_QUALIFIED",
        exit_code=process.returncode, unittest_calls=1, expected_tests=16, tests_run=int(ran[1]) if ran else None,
        passed_tests=16 if ok else None, counters=counts, hashes_before=before, hashes_after=after,
        gates_after=gates(), nh_sources=0, integration_calls=0, universal_float_guarantee=False,
        stdout_sha256=filehash(OUT/"stdout.txt"), stderr_sha256=filehash(OUT/"stderr.txt"),
        observations_sha256=filehash(observation_path) if observations else None)
    result["result_digest"] = sha(canonical(result))
    publish(OUT/"result.json", result)
    print(json.dumps({k: result[k] for k in ("qualification_id", "status", "exit_code", "tests_run", "passed_tests", "counters", "result_digest")}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
