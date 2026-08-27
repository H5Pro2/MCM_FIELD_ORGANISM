"""One authorized unittest process; evidence recording only, no project calls."""
from __future__ import annotations

import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PREFIX = ROOT / "reports/s2ej_tspm1_51_contract_tests"
AUDIT = "docs/S2EG_REPEAT_AFTER_S2EI_TSPM1_STATISCHER_AUDIT_V1.json"
CONTRACT = "docs/S2EH_TSPM1_STATISCHER_KORREKTURVERTRAG_V1.json"
TEST = "tests/test_tspm1_s2dr_private_comparison_contract.py"
AUDIT_DIGEST = "b9dfcafb00b3b28aa3821a52e576ef20d568cd208f3ee0ff72017cd8c719179e"
SOURCE_HEAD = "e42ec19dea213c8b3b73b8f70c1e33e504414793"


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                      separators=(",", ":")).encode("ascii")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def sealed(value):
    return {**value, "artifact_digest": digest(encoded(value))}


def write_new(path, raw):
    with path.open("xb", buffering=0) as handle:
        if handle.write(raw) != len(raw):
            raise OSError("short evidence write")
        os.fsync(handle.fileno())
    if path.read_bytes() != raw:
        raise OSError("evidence reread differs")


def publish_new(path, value):
    # On Windows, rename is same-directory and fails when the target exists.
    stage = path.with_suffix(path.suffix + ".staging")
    raw = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True,
                     allow_nan=False).encode("ascii") + b"\n"
    write_new(stage, raw)
    os.rename(stage, path)
    if path.read_bytes() != raw:
        raise OSError("published evidence differs")


def main():
    if os.name != "nt":
        raise RuntimeError("Windows no-replace publication required")
    if list(PREFIX.parent.glob(PREFIX.name + "*")):
        raise RuntimeError("attempt already consumed or evidence already present; no retry")
    audit = json.loads((ROOT / AUDIT).read_bytes())
    declared = audit.pop("artifact_digest")
    if declared != AUDIT_DIGEST or digest(encoded(audit)) != declared or git("rev-parse", "HEAD") != SOURCE_HEAD:
        raise RuntimeError("audit or source commit differs")
    for path, evidence in audit["sources"].items():
        if digest((ROOT / path).read_bytes()) != evidence["raw_sha256"] or git("rev-parse", "HEAD:" + path) != evidence["git_blob"]:
            raise RuntimeError("bound source differs: " + path)
    for path, expected in audit["protected_raw_sha256"].items():
        if digest((ROOT / path).read_bytes()) != expected:
            raise RuntimeError("protected source differs: " + path)
    tree = ast.parse((ROOT / TEST).read_bytes())
    names = sorted(node.name for node in ast.walk(tree)
                   if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"))
    if len(names) != 51 or [name[5:8] for name in names] != [f"t{i:02d}" for i in range(1, 52)]:
        raise RuntimeError("test inventory differs")
    source_tree = ast.parse((ROOT / "mcm_field_organism/_tspm1_s2dr_private_comparison.py").read_bytes())
    gates = [node.value for node in source_tree.body if isinstance(node, ast.Assign)
             and any(isinstance(target, ast.Name) and target.id == "_EXECUTION_RELEASE_ENABLED" for target in node.targets)]
    if len(gates) != 1 or ast.literal_eval(gates[0]) is not False:
        raise RuntimeError("matrix gate is not closed")
    contract = json.loads((ROOT / CONTRACT).read_bytes())
    paths = sorted(set(contract["test_definition_contract"]["expected_project_sources"] + [TEST, AUDIT, CONTRACT]))
    before = {path: digest((ROOT / path).read_bytes()) for path in paths}
    command = [sys.executable, "-B", "-u", "-m", "unittest",
               "tests.test_tspm1_s2dr_private_comparison_contract", "-v", "-f"]
    started = datetime.now(timezone.utc).isoformat()
    attempt = sealed({"schema_version": "mcm.s2ej.test-attempt.v1", "attempt_id": "s2ej.001",
                      "consumed": True, "authorized_process_count": 1, "retry_allowed": False,
                      "source_commit": SOURCE_HEAD, "audit_digest": declared, "started_at_utc": started,
                      "command": command, "test_names": names, "source_sha256_before": before,
                      "recorder_sha256": digest(Path(__file__).read_bytes()),
                      "authorization": "One fully recorded run of 51 tests, immediate failfast, atomic evidence; no retry or matrix."})
    attempt_path = Path(str(PREFIX) + "_attempt_v1.json")
    # The exclusive reservation is never removed, including on recording failure.
    write_new(attempt_path, encoded(attempt) + b"\n")
    output_path = Path(str(PREFIX) + "_output_v1.txt")
    with output_path.open("xb", buffering=0) as output:
        os.fsync(output.fileno())
        print("S2EJ_START s2ej.001; 51 registered tests; failfast; no retry", flush=True)
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        completed = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT,
                                   env=environment, check=False)
        os.fsync(output.fileno())
    raw = output_path.read_bytes()
    transcript = raw.decode("utf-8", errors="strict")
    lines = transcript.splitlines()
    started_cases = [match[1] for line in lines if (match := re.match(r"^(test_t\d{2}_\w+) \(", line))]
    passed_cases = [match[1] for line in lines if (match := re.match(r"^(test_t\d{2}_\w+) \(.*\) \.\.\. ok$", line))]
    summaries = [match for line in lines if (match := re.fullmatch(r"Ran (\d+) tests? in ([0-9.]+)s", line))]
    total = int(summaries[0][1]) if len(summaries) == 1 else None
    terminal = next((line for line in reversed(lines) if line.strip()), None)
    after = {path: digest((ROOT / path).read_bytes()) for path in paths}
    recorded = (total is not None and total == len(started_cases)
                and started_cases == names[:total] and terminal is not None
                and (terminal == "OK" or terminal.startswith("FAILED")))
    passed = (recorded and completed.returncode == 0 and total == 51
              and passed_cases == names and terminal == "OK" and before == after)
    result = sealed({"schema_version": "mcm.s2ej.51-contract-tests.v1", "attempt_id": "s2ej.001",
                     "attempt_artifact_digest": attempt["artifact_digest"], "audit_artifact_digest": declared,
                     "source_commit": SOURCE_HEAD, "command": command, "python_version": sys.version,
                     "started_at_utc": started, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                     "execution_count_this_authorization": 1, "retry_executed": False,
                     "status": "PASS_51_OF_51" if passed else "FAIL_CLOSED_STOPPED",
                     "exit_code": completed.returncode, "registered_test_count": 51,
                     "reported_test_count": total, "passed_case_count": len(passed_cases),
                     "started_cases": started_cases, "passed_cases": passed_cases,
                     "not_run_cases": [name for name in names if name not in started_cases],
                     "adapted_definitions": audit["sources"][TEST]["changed_test_definitions"],
                     "terminal_status": terminal, "complete_attempt_transcript": recorded,
                     "complete_51_case_coverage": passed_cases == names,
                     "source_sha256_before": before, "source_sha256_after": after,
                     "sources_unchanged": before == after, "raw_output": transcript,
                     "raw_output_sha256": digest(raw), "raw_output_path": output_path.relative_to(ROOT).as_posix(),
                     "matrix_executed": False, "state_calls_outside_test_scope": 0,
                     "atomic_publication": "exclusive staging, fsync, reread, Windows no-replace rename, final reread; separate confirmation required",
                     "claim_boundary": "TECHNICAL_COMPARISON_INFRASTRUCTURE_AUDIT_ONLY"})
    final_path = Path(str(PREFIX) + "_v1.json")
    publish_new(final_path, result)
    confirmation = sealed({"schema_version": "mcm.s2ej.test-result-publication.v1", "attempt_id": "s2ej.001",
                           "result_artifact_digest": result["artifact_digest"],
                           "result_raw_sha256": digest(final_path.read_bytes()),
                           "result_file": final_path.relative_to(ROOT).as_posix(),
                           "final_reread_confirmed": True, "overwrite_performed": False,
                           "retry_performed": False, "test_exit_code": completed.returncode,
                           "status": "RESULT_RECORD_PUBLISHED", "power_loss_durability_claimed": False})
    publish_new(Path(str(PREFIX) + "_publication_v1.json"), confirmation)
    print(f"S2EJ_STATUS={result['status']} TEST_EXIT={completed.returncode} STARTED={total} PASSED={len(passed_cases)}", flush=True)
    print(f"RESULT={final_path}", flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
