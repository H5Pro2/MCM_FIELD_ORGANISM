from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "reports" / "s2dm_tspm1_76_test_closure_v1.json"
MODULES = (
    "tests.test_tspm1_s2dh_private_fast_core",
    "tests.test_tspm1_s2dm_negative_contract",
    "tests.test_ppb1_reference",
    "tests.test_ppb1_s1wu_read_only_perceptual_probe",
    "tests.test_s2al_private_active_receptor_batch_binding",
)


def sha256_file(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main() -> int:
    if RESULT.exists():
        raise RuntimeError("S2DM_RESULT_ALREADY_EXISTS")

    command = [sys.executable, "-m", "unittest", *MODULES, "-v"]
    started = datetime.now(timezone.utc)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    finished = datetime.now(timezone.utc)
    raw_output = completed.stdout
    total_match = re.search(r"Ran\s+(\d+)\s+tests?\s+in", raw_output)
    reported_total = int(total_match.group(1)) if total_match else None
    ok_lines = len(re.findall(r"(?m)^test_.*\.\.\. ok\s*$", raw_output))
    terminal_ok = re.search(r"(?m)^OK\s*$", raw_output) is not None
    passed = (
        completed.returncode == 0
        and reported_total == 76
        and ok_lines == 76
        and terminal_ok
    )

    record = {
        "schema_version": "mcm.s2dm.tspm1.third-stage-closure-run.v1",
        "authorization": "ONE_REEXECUTION_OF_STAGE_3_ONLY",
        "repository_head": subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip(),
        "started_at_utc": started.isoformat(),
        "finished_at_utc": finished.isoformat(),
        "command": " ".join(command),
        "execution_count_this_authorization": 1,
        "stages_1_and_2_reexecuted": False,
        "exit_code": completed.returncode,
        "reported_test_total": reported_total,
        "reported_ok_case_lines": ok_lines,
        "terminal_ok": terminal_ok,
        "status": (
            "PASSED_76_OF_76" if passed else "FAIL_CLOSED_INCOMPLETE_OR_FAILED"
        ),
        "source_digests": {
            "tspm1_private": sha256_file(
                "mcm_field_organism/_tspm1_private.py"
            ),
            "ppb1_reference": sha256_file(
                "mcm_field_organism/_ppb1_reference.py"
            ),
            "s2dh_tests": sha256_file(
                "tests/test_tspm1_s2dh_private_fast_core.py"
            ),
            "s2dm_tests": sha256_file(
                "tests/test_tspm1_s2dm_negative_contract.py"
            ),
        },
        "validated_error_codes": {
            "P01_P04": [
                "TSPM1_INVALID_TYPE_OR_SCHEMA",
                "TSPM1_OWNER_AUTHORIZATION_MISMATCH",
            ],
            "R05_R12": ["TSPM1_ATOMIC_RESULT_REQUIRED"],
            "B13_B15": ["TSPM1_ATOMIC_RESULT_REQUIRED"],
            "A16": ["TSPM1_ATOMIC_RESULT_REQUIRED"],
            "owner_outer_failure": "TSPM1_ATTEMPT_FAILED",
            "retry_failure": "TSPM1_OWNER_TERMINAL",
        },
        "validated_owner_end_states": {
            "terminal_status": "FAILED",
            "attempt_count": 1,
            "use_count": 0,
            "generation": 1,
            "committed_result_digest": None,
            "retry_allowed": False,
        },
        "validated_ppb1_call_budgets": {
            "P01_P04": 0,
            "R05_R07": 0,
            "R08_R12": "DIRECT_CONSTRUCTOR_OR_READ_ONLY_NO_OWNER_BUDGET",
            "B13_B15": {"count": 2, "order": ["auditory", "visual"]},
            "A16": {
                "count": 2,
                "order": ["auditory", "visual"],
                "retry_additional_calls": 0,
            },
        },
        "atomic_publication": {
            "temporary_result_written_first": True,
            "final_path": "reports/s2dm_tspm1_76_test_closure_v1.json",
            "overwrite_allowed": False,
        },
        "raw_output_sha256": hashlib.sha256(
            raw_output.encode("utf-8")
        ).hexdigest(),
        "raw_output": raw_output,
        "claim_boundary": (
            "TECHNICAL_TSPM1_VALIDATOR_RESULT_ONLY_NO_MEMORY_OR_MCM_FIELD_FINDING"
        ),
    }

    RESULT.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=RESULT.name + ".",
        suffix=".tmp",
        dir=RESULT.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(record, handle, ensure_ascii=True, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        decoded = json.loads(temporary.read_text(encoding="utf-8"))
        if (
            decoded["status"] != record["status"]
            or decoded["reported_test_total"] != reported_total
            or decoded["raw_output_sha256"] != record["raw_output_sha256"]
        ):
            raise RuntimeError("S2DM_RESULT_SERIALIZATION_MISMATCH")
        os.replace(temporary, RESULT)
    finally:
        if temporary.exists():
            temporary.unlink()

    print(f"S2DM_STAGE3_STATUS={record['status']}")
    print(f"EXIT_CODE={completed.returncode}")
    print(f"TEST_TOTAL={reported_total}")
    print(f"OK_LINES={ok_lines}")
    print(f"RESULT={RESULT}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
