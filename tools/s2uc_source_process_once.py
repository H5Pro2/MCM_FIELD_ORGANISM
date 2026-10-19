"""Neutral-only V9 child bootstrap; stdlib-only until verified Windows job admission."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "reports/s2uc/v8-process-limit-corrected-20260920/limit.py"


def save(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2), encoding="utf-8")


def need(ok, code):
    if not ok:
        raise ValueError(code)


def child(config):
    before = not any(n == "numpy" or n.startswith(("numpy.", "tools.", "tests.", "mcm_field_organism.")) for n in sys.modules)
    need(sys.flags.no_site and before, "V9_PREIMPORT_INVALID")
    need(set(config) == {"binding", "run_id", "output", "folder", "job", "case", "inventory_sha256"}
         and config["case"] in ("success", "memoryerror"), "V9_PROCESS_CONFIG_INVALID")
    folder = Path(config["folder"])
    save(folder / "bootstrap.json", {"ns": time.perf_counter_ns(), "product_numpy_absent": before, "no_site": True})
    need(sys.stdin.readline().strip() == "admit", "V9_ADMISSION_MISSING")
    api = runpy.run_path(str(HELPER), run_name="v9_limit_helpers")
    job = api["openjob"](4, False, config["job"])
    need(bool(job), "V9_JOB_MISSING")
    try:
        proof = api["evidence"](job, api["current"]())
    finally:
        api["close"](job)
    inventory_bytes = (Path(config["binding"]).parent / "dependency-inventory.json").read_bytes()
    need(hashlib.sha256(inventory_bytes).hexdigest() == config["inventory_sha256"], "V9_PROCESS_INVENTORY_CHANGED")
    inv = json.loads(inventory_bytes)
    for row in inv["files"]:
        path = ROOT / row["path"]
        need(path.resolve().is_relative_to(ROOT) and not path.is_symlink(), "V9_PROCESS_PATH_INVALID")
        data = path.read_bytes()
        need(len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"], "V9_PROCESS_CODE_CHANGED")
    before = not any(n in ("numpy", "tools", "tests", "mcm_field_organism")
                     or n.startswith(("numpy.", "tools.", "tests.", "mcm_field_organism.")) for n in sys.modules)
    need(before, "V9_PRODUCT_IMPORTED_BEFORE_ADMISSION")
    save(folder / "child-admission.json", {**proof, "product_numpy_absent": before,
                                          "inventory_sha256": config["inventory_sha256"]})
    import site
    site.main()
    sys.path.insert(0, str(ROOT))
    from tools import _s2uc_source_execution as execution
    from tools import _s2uc_source_context_v9 as context
    from tools import _s2nu_private_source_binding as nu
    # Neutral entry must never touch production, including accidental defaults.
    def forbidden(*args, **kwargs):
        raise AssertionError("V9_REAL_PRODUCTION_FORBIDDEN")
    nu.pcm_window = forbidden
    calls = 0
    def supplier(endpoint):
        nonlocal calls
        calls += 1
        if calls == 58 and config["case"] == "memoryerror":
            raise MemoryError("NEUTRAL_INJECTED_NOT_EXHAUSTION")
        return context.neutral_payload(endpoint["source_id"])
    save(folder / "after-imports.json", {"ns": time.perf_counter_ns()})
    result = execution.run_neutral(config["binding"], supplier, run_id=config["run_id"], output_directory=config["output"])
    save(folder / "result.json", result)
    save(folder / "facts.json", {"calls": calls, "gate": execution.core.GATE,
                                 "public_gate": execution.legacy_entry.MAIN_GATE, "real_production_calls": 0})


def run_neutral(binding_path, *, case="success", folder):
    from tools import _s2uc_source_execution_binding as binding
    initial = binding.validate(binding_path)
    need(case in ("success", "memoryerror"), "V9_PROCESS_CASE_INVALID")
    folder = Path(folder)
    folder.mkdir()  # Fresh observer evidence, never confused with product closure.
    config = {"binding": str(Path(binding_path).resolve()), "run_id": initial["run_id"],
              "output": initial["output"], "folder": str(folder.resolve()),
              "job": "Local\\MCM-V9-" + os.urandom(16).hex(), "case": case,
              "inventory_sha256": binding.discovery.sha(binding.old.canonical(initial["inventory"]))}
    save(folder / "config.json", config)
    api = runpy.run_path(str(HELPER), run_name="v9_limit_helpers")
    job = api["create"](None, config["job"])
    need(bool(job) and api["c"].get_last_error() != 183, "V9_JOB_CREATE_FAILED")
    process = None
    try:
        limit = api["Extended"]()
        limit.basic.flags, limit.limit = 0x2100, 640 * 1048576
        api["need"](api["setjob"](job, 9, api["c"].byref(limit), api["c"].sizeof(limit)))
        with (folder / "stdout.txt").open("x") as out, (folder / "stderr.txt").open("x") as err:
            process = subprocess.Popen([sys.executable, "-S", str(Path(__file__).resolve()), "child", str(folder.resolve() / "config.json")],
                                       stdin=subprocess.PIPE, stdout=out, stderr=err, text=True, cwd=ROOT,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            api["need"](api["assign"](job, int(process._handle)))
            proof = api["evidence"](job, int(process._handle))
            save(folder / "parent-admission.json", proof)
            process.communicate("admit\n", timeout=120)
        code = process.returncode
    except Exception:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait()
        raise
    finally:
        api["close"](job)
    result_path = folder / "result.json"
    closed = code == 0 and result_path.is_file()
    result = {"exit_code": code, "status": "PRODUCT_RESULT_PRESENT" if closed else "EXTERNAL_ABORT_NO_PRODUCT_SUCCESS",
              "evaluation_allowed": False, "real_execution_authorized": False}
    if closed:
        result["product"] = json.loads(result_path.read_text())
    save(folder / "process-exit.json", result)
    return result


if __name__ == "__main__":
    need(len(sys.argv) == 3 and sys.argv[1] == "child", "V9_PUBLIC_REAL_ENTRY_DISABLED")
    child(json.loads(Path(sys.argv[2]).read_text()))
