"""One isolated filesystem preflight; never import or run the MCM package."""
from __future__ import annotations

import ast
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import traceback


ROOT = Path(__file__).resolve().parents[1]
HEAD = "030bb266507ec6703d51b65e163735a7b3270776"
SOURCE = "mcm_field_organism/_tspm1_s2dr_private_comparison.py"
SOURCE_HASH = "d3153cb0ef1a9ecd8c1ec09e6171f0ad2d86c827934277e118bc5c5dc08d1ed8"
AUDIT = "docs/S2EL_TSPM1_STATISCHER_AUSFUEHRUNGSPREFLIGHT_56_ZELLEN_V1.json"
AUDIT_DIGEST = "ddc1a4ac2a295fb0d2f0102d1d54ae1d81e5de16600c331df2129d44316eface"
PREFIX = ROOT / "reports/s2em_platform_preflight"
SCRATCH = ROOT / ".git/s2em-platform-preflight-001"
STUDY = "s2em.platform.001"
FORBIDDEN = (
    "reports/s2ee_tspm1_56_cell_comparison_v1.json",
    "reports/.s2ee_tspm1_56_cell_comparison.attempt-001.staging",
    ".git/mcm-execution-ledger/s2dr.tspm1.h1-h7.56.v1",
    ".git/mcm-execution-ledger/s2dr.tspm1.h1-h7.56.v1.authorization.json",
)
CASES = (
    "P0_native_fixed_ntfs_volume_handle_and_flush",
    "P1_exclusive_complete_file_write",
    "P2_no_replace_publication_and_completion",
    "P3_existing_target_cannot_be_replaced",
    "P4_incomplete_or_readable_only_is_not_complete",
    "P5_post_rename_flush_error_has_no_completion",
)


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                      separators=(",", ":")).encode("ascii")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def sealed(value):
    return {**value, "artifact_digest": digest(encoded(value))}


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def write_new(path, raw):
    with path.open("xb", buffering=0) as stream:
        require(stream.write(raw) == len(raw), "short diagnostic write")
        os.fsync(stream.fileno())
    require(path.read_bytes() == raw, "diagnostic reread differs")


def publish_diagnostic(path, value):
    # This recorder is not evidence for the volume-flush backend under test.
    raw = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True,
                     allow_nan=False).encode("ascii") + b"\n"
    stage = path.with_suffix(path.suffix + ".staging")
    write_new(stage, raw)
    os.rename(stage, path)  # Windows same-directory rename without replacement.
    require(path.read_bytes() == raw, "diagnostic publication differs")
    return digest(raw)


class Payload:
    """Inert publication metadata, not a study plan or memory state."""

    def __init__(self, value):
        self.raw = encoded(value)

    def payload(self):
        return json.loads(self.raw)


class BackendError(RuntimeError):
    def __init__(self, code, message):
        self.native_error = ctypes.get_last_error()
        self.code = code
        super().__init__(message)


def isolated_backend(tree, domain):
    nodes = [node for node in tree.body
             if isinstance(node, ast.ClassDef) and node.name == "_DurableStudyStore"]
    require(len(nodes) == 1, "publication class is not unique")
    node = nodes[0]
    require(not node.decorator_list and not node.bases, "unexpected class evaluation")
    module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[
        ast.alias(name="annotations")], level=0), node], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {
        "__name__": "s2em_isolated_filesystem_backend", "ctypes": ctypes,
        "wintypes": wintypes, "os": os, "Path": Path, "_require": require,
        "_root": lambda: ROOT, "_execution_domain": lambda: dict(domain),
        "_json_bytes": encoded, "S2DRError": BackendError,
        "S2DR_ATOMIC_RESULT_REQUIRED": "S2DR_ATOMIC_RESULT_REQUIRED",
        "S2EE_STUDY_ID": STUDY,
    }
    # Only this source-bound filesystem class is evaluated, not its module.
    exec(compile(module, SOURCE, "exec"), namespace)
    return namespace["_DurableStudyStore"], node


def plan_for(name, domain):
    folder = SCRATCH / name
    return Payload({"execution_domain": domain, "publication_paths": {
        "final": str(folder / "final.json"),
        "staging": str(folder / ".staging"),
        "reservation": str(Path(domain["durable_ledger_root"]) / STUDY),
    }})


def observed_error(error):
    result = {"type": type(error).__name__, "message": str(error),
              "code": getattr(error, "code", None),
              "winerror": getattr(error, "winerror", None),
              "native_error_at_raise": getattr(error, "native_error", None),
              "frames": []}
    for frame, line in traceback.walk_tb(error.__traceback__):
        result["frames"].append({"file": frame.f_code.co_filename,
                                 "function": frame.f_code.co_name, "line": line})
        if frame.f_code.co_filename == SOURCE and frame.f_code.co_name == "__init__":
            if "drive" in frame.f_locals:
                result["drive"] = frame.f_locals["drive"]
            if "filesystem" in frame.f_locals:
                result["filesystem"] = frame.f_locals["filesystem"].value
            if "handle" in frame.f_locals:
                result["invalid_volume_handle"] = (
                    frame.f_locals["handle"] == ctypes.c_void_p(-1).value)
    return result


def completion_observed(final, expected, flush_confirmed, marker):
    # Platform-fixture predicate only; not the matrix's completion protocol.
    return (flush_confirmed and final.is_file() and final.read_bytes() == expected
            and marker.is_file()
            and marker.read_bytes() == encoded({"completed_sha256": digest(expected)}))


def platform_cases(backend, domain, cases):
    store = None
    case = CASES[0]
    try:
        store = backend(plan_for("normal", domain))
        cases[case] = {"status": "PASS", "local_fixed_ntfs": True,
                       "volume_handle_opened": True, "initial_volume_flush_returned": True}
        SCRATCH.mkdir(exist_ok=False)
        store.paths["final"].parent.mkdir()
        case = CASES[1]
        payload = Payload({"scope": "platform-fixture-only", "attempt": STUDY})
        raw = encoded(payload.payload())
        store.write_new(store.paths["staging"], payload)
        try:
            store.write_new(store.paths["staging"], payload)
        except FileExistsError:
            pass
        else:
            raise RuntimeError("exclusive write accepted an existing file")
        require(store.paths["staging"].read_bytes() == raw, "duplicate write changed bytes")
        cases[case] = {"status": "PASS", "file_sha256": digest(raw),
                       "file_fsync_and_volume_flush_returned": True,
                       "duplicate_write_rejected": True}
        case = CASES[2]
        store.publish()
        final = store.paths["final"]
        require(final.read_bytes() == raw, "published bytes differ")
        marker = final.parent / "completion.json"
        write_new(marker, encoded({"completed_sha256": digest(raw)}))
        store.flush()
        require(completion_observed(final, raw, True, marker), "completion absent")
        cases[case] = {"status": "PASS", "final_volume_flush_returned": True,
                       "byte_match": True, "platform_completion_marker": True}
        case = CASES[3]
        store.write_new(store.paths["staging"], Payload({"different": True}))
        try:
            store.publish()
        except OSError as error:
            require(error.winerror in (80, 183), "unexpected no-replace error")
            refusal = observed_error(error)
        else:
            raise RuntimeError("publication replaced existing final")
        require(final.read_bytes() == raw, "no-replace failure changed final")
        cases[case] = {"status": "PASS", "expected_refusal": refusal,
                       "original_bytes_preserved": True}
        case = CASES[4]
        partial = final.parent / "partial.json"
        write_new(partial, raw[:len(raw) // 2])
        require(not completion_observed(partial, raw, True, marker), "partial accepted")
        require(not completion_observed(final, raw, False, marker), "unflushed accepted")
        require(not completion_observed(final, raw, True, final.parent / "missing"),
                "missing completion accepted")
        cases[case] = {"status": "PASS", "truncation_rejected": True,
                       "readable_without_confirmed_flush_rejected": True,
                       "missing_completion_rejected": True,
                       "scope": "platform fixture predicate, not matrix protocol"}
        case = CASES[5]
        store.plan = plan_for("flush-error", domain)
        store.paths = {key: Path(value) for key, value in
                       store.plan.payload()["publication_paths"].items()}
        store.paths["final"].parent.mkdir()
        store.write_new(store.paths["staging"], payload)

        def injected_flush_error():
            raise OSError("S2EM_INJECTED_FINAL_FLUSH_ERROR")

        store.flush = injected_flush_error
        confirmed = False
        try:
            store.publish()
            confirmed = True
        except OSError as error:
            require(str(error) == "S2EM_INJECTED_FINAL_FLUSH_ERROR", "unexpected flush error")
        final = store.paths["final"]
        marker = final.parent / "completion.json"
        require(final.read_bytes() == raw and not confirmed and not marker.exists(),
                "flush fault did not leave the expected incomplete publication")
        require(not completion_observed(final, raw, confirmed, marker),
                "readable final falsely completed")
        cases[case] = {"status": "PASS", "fault_injected": True,
                       "readable_final": True, "completion": False,
                       "scope": "platform fixture; no matrix finalization invoked"}
        return "PLATFORM_CAPABILITIES_CONFIRMED", 0
    except Exception as error:
        evidence = observed_error(error)
        blocked = case == CASES[0]
        cases[case] = {"status": "BLOCKED" if blocked else "FAIL", "error": evidence}
        return ("BLOCKED_PLATFORM_PREREQUISITE" if blocked else "FAIL_CLOSED_PLATFORM_CHECK"), 2 if blocked else 1
    finally:
        if store is not None:
            store.close()


def main():
    require(os.name == "nt", "Windows-only platform preflight")
    require(not list(PREFIX.parent.glob(PREFIX.name + "*"))
            and not os.path.lexists(SCRATCH), "attempt already exists; no retry")
    require(git("rev-parse", "HEAD") == HEAD, "source commit differs")
    audit = json.loads((ROOT / AUDIT).read_bytes())
    declared = audit.pop("artifact_digest")
    require(declared == AUDIT_DIGEST and digest(encoded(audit)) == declared, "audit differs")
    before = {}
    for entry in audit["source_files"]:
        path = entry["path"]
        before[path] = digest((ROOT / path).read_bytes())
        require(before[path] == entry["raw_sha256"]
                and git("rev-parse", "HEAD:" + path) == entry["git_blob"], "source differs: " + path)
    raw = (ROOT / SOURCE).read_bytes()
    require(digest(raw) == SOURCE_HASH, "backend source differs")
    tree = ast.parse(raw)
    gates = [node.value for node in tree.body if isinstance(node, ast.Assign)
             and any(isinstance(target, ast.Name) and target.id == "_EXECUTION_RELEASE_ENABLED"
                     for target in node.targets)]
    require(len(gates) == 1 and ast.literal_eval(gates[0]) is False, "matrix gate opened")
    forbidden_before = {path: os.path.lexists(ROOT / path) for path in FORBIDDEN}
    require(not any(forbidden_before.values()), "real matrix path already exists")
    domain = {"canonical_git_common_dir": str((ROOT / ".git").resolve()),
              "durable_ledger_root": str(SCRATCH / "ledger")}
    backend, node = isolated_backend(tree, domain)
    started = datetime.now(timezone.utc).isoformat()
    attempt = sealed({"schema_version": "mcm.s2em.platform-attempt.v1",
                      "attempt_id": "s2em.001", "execution_domain": "isolated filesystem only",
                      "consumed": True, "retry_allowed": False, "source_commit": HEAD,
                      "audit_digest": declared, "started_at_utc": started,
                      "helper_sha256": digest(Path(__file__).read_bytes()),
                      "backend_source_sha256": SOURCE_HASH,
                      "backend_ast_sha256": digest(ast.dump(node, include_attributes=False).encode()),
                      "backend_lines": [node.lineno, node.end_lineno],
                      "scratch_root": str(SCRATCH), "cases": list(CASES),
                      "source_sha256_before": before,
                      "authorization": "S2-EM isolated platform preflight only; no memory, tests or matrix."})
    write_new(Path(str(PREFIX) + "_attempt_v1.json"), encoded(attempt) + b"\n")
    print("S2EM_START s2em.001; filesystem only; no retry or elevation", flush=True)
    cases = {case: {"status": "NOT_RUN"} for case in CASES}
    status, exit_code = platform_cases(backend, domain, cases)
    after = {path: digest((ROOT / path).read_bytes()) for path in before}
    forbidden_after = {path: os.path.lexists(ROOT / path) for path in FORBIDDEN}
    loaded = sorted(name for name in sys.modules
                    if name == "mcm_field_organism" or name.startswith("mcm_field_organism."))
    unchanged = before == after and forbidden_before == forbidden_after and not loaded
    if not unchanged:
        status, exit_code = "FAIL_CLOSED_SCOPE_OR_SOURCE_DRIFT", 1
    result = sealed({"schema_version": "mcm.s2em.platform-preflight.v1", "attempt_id": "s2em.001",
                     "attempt_artifact_digest": attempt["artifact_digest"], "audit_digest": declared,
                     "source_commit": HEAD, "status": status, "exit_code": exit_code,
                     "started_at_utc": started, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                     "platform": platform.platform(), "python": sys.version,
                     "process_elevated": bool(ctypes.windll.shell32.IsUserAnAdmin()),
                     "cases": cases, "source_sha256_after": after, "protected_sources_unchanged": unchanged,
                     "forbidden_paths_before": forbidden_before, "forbidden_paths_after": forbidden_after,
                     "project_modules_loaded": loaded, "memory_state_calls": 0, "matrix_cells": 0,
                     "contract_tests": 0, "retry_executed": False, "elevation_attempted": False,
                     "matrix_gate": False, "power_loss_or_process_crash_tested": False,
                     "diagnostic_recording_is_volume_durability_evidence": False,
                     "limitations": ["Platform fixture only; no actual study reservation or authorization.",
                                     "Successful OS calls do not prove physical power-loss persistence.",
                                     "NOT_RUN cases have no capability verdict; stop at first blocker."]})
    final = Path(str(PREFIX) + "_v1.json")
    raw_hash = publish_diagnostic(final, result)
    confirmation = sealed({"schema_version": "mcm.s2em.diagnostic-publication.v1",
                           "attempt_id": "s2em.001", "result_artifact_digest": result["artifact_digest"],
                           "result_raw_sha256": raw_hash, "result_path": final.relative_to(ROOT).as_posix(),
                           "same_directory_no_replace_rename": True, "file_fsync_returned": True,
                           "complete_byte_reread": True, "volume_durability_claim": False})
    publish_diagnostic(Path(str(PREFIX) + "_publication_v1.json"), confirmation)
    print(json.dumps({"status": status, "exit_code": exit_code,
                      "result_artifact_digest": result["artifact_digest"], "cases": cases}, indent=2), flush=True)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
