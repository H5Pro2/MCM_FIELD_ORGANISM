"""Prepare, then qualify exactly once; publish a read-only HTML evidence view."""
import argparse
import ast
import json
import os
from pathlib import Path
import subprocess
import sys

from tools import _s2oe_history_view as v

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/s2oe/history-display-qualification-20260912-01"
HISTORY = "reports/s2oe/media-memory-video-20260912-01"
FILES = ("tools/_s2oe_history_view.py", "tools/s2oe_player.html",
         "tests/test_s2oe_history_view.py", "tests/s2oe_history_browser.cjs",
         "reports/qualify_history_view_once.py")
CAPS = {"binding.json":8192, "qualification.log":16384, "result.json":4096,
        "REPORT.md":4096, "view.html":65536, "qualification.claim":4}
NODE = "C:/Program Files/nodejs/node.exe"
PLAYWRIGHT = "C:/Users/TV/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright"


def reference(name):
    raw = (ROOT/name).read_bytes()
    return dict(path=name, bytes=len(raw), sha256=v.sha(raw))


def write(name, value):
    raw = value if type(value) is bytes else v.canonical(value)
    # Keep complete diagnostics even when actual output exceeds its reservation.
    with (OUT/name).open("xb") as stream:
        stream.write(raw)


def prepare():
    v.require(not OUT.exists(), "OUTPUT_USED")
    tests = ast.parse((ROOT/FILES[2]).read_text(encoding="utf-8"))
    inventory = sorted(n.name for n in ast.walk(tests) if isinstance(n, ast.FunctionDef)
                       and n.name.startswith("test_"))
    source = [reference(x) for x in FILES]
    documents = {key:reference(f"{HISTORY}/{name}.json") for key,name in
                 (("wire","record"),("common","common"),("proof","verification"),("session","session"))}
    balance_ref = reference(f"{HISTORY}/final-balance.json")
    historic = json.loads((ROOT/balance_ref["path"]).read_bytes())
    archive_charge = historic["joint_total_including_full_final_reserve"]
    source_total = sum(x["bytes"] for x in source)
    metadata = sum(n for name,n in CAPS.items() if name != "view.html")
    totals = dict(metadata=metadata, sources=source_total,
                  shared=source_total+CAPS["view.html"],
                  total=archive_charge+source_total+sum(CAPS.values()))
    limits = dict(metadata=65536, sources=196608, shared=262144, total=4194304)
    binding = dict(version=v.VERSION, qualification_id=OUT.name,
        run_id="media-memory-video-20260912-01", documents=documents, sources=source,
        historical_balance=balance_ref, historical_charge=archive_charge,
        archive_accounting="Historical complete joint charge retained, including all referenced contents/reserves; four reader inputs are not added a second time.",
        display_accounting="New display/qualification metadata separate from unchanged closed runtime ledger; HTML is a counted display artifact, not a state or raw payload.",
        tests=inventory, expected_tests=15, test_calls=1, caps=CAPS, totals=totals, limits=limits,
        environment=dict(python=sys.version, executable=sys.executable, node=NODE,
                         playwright=PLAYWRIGHT, browser="msedge", viewports=[[1280,900],[390,844]]),
        numerical_reverification=False, new_receptor_or_scan_calls=0, gates=False)
    v.require(len(inventory)==15 and len(v.canonical(binding)) <= CAPS["binding.json"], "BINDING_LIMIT")
    print(json.dumps(dict(totals=totals, limits=limits), indent=2))
    v.require(all(totals[k] <= limits[k] for k in totals), "PREFLIGHT_LIMIT")
    OUT.mkdir()
    write("binding.json", binding)
    print("PREPARED; zero test calls")


def qualify():
    binding = json.loads((OUT/"binding.json").read_bytes())
    for ref in binding["sources"]:
        v.read_bound(ROOT, ref)
    for ref in binding["documents"].values():
        v.read_bound(ROOT, ref)
    v.read_bound(ROOT, binding["historical_balance"])
    v.require(not (OUT/"qualification.claim").exists(), "QUALIFICATION_USED")
    write("qualification.claim", b"once")
    env = dict(os.environ, MCM_NODE=NODE, MCM_PLAYWRIGHT=PLAYWRIGHT)
    proc = subprocess.run([sys.executable,"-m","unittest","tests.test_s2oe_history_view","-v"],
                          cwd=ROOT, env=env, capture_output=True, timeout=120)
    write("qualification.log", proc.stdout+proc.stderr)
    unchanged = all(reference(x["path"]) == x for x in binding["sources"])
    historical_unchanged = all(reference(x["path"]) == x for x in binding["documents"].values())
    passed = proc.returncode == 0 and unchanged and historical_unchanged
    view_error = None
    if passed:
        try:
            data = v.load(ROOT, binding)
            write("view.html", v.page((ROOT/"tools/s2oe_player.html").read_bytes(), data))
        except (v.DisplayError, OSError, ValueError) as exc:
            view_error = getattr(exc,"code",str(exc))
    actual = {p.name:p.stat().st_size for p in OUT.iterdir() if p.is_file()}
    violations = [name for name,n in actual.items() if n > CAPS[name]]
    charged = binding["historical_charge"] + binding["totals"]["sources"] + sum(
        max(actual.get(name,0), cap) if name in ("REPORT.md","result.json") else actual.get(name,0)
        for name,cap in CAPS.items())
    if charged > v.TOTAL_LIMIT: violations.append("TOTAL_LIMIT")
    result = dict(status="QUALIFIED" if passed and not violations else "NOT_QUALIFIED",
        test_calls=1, expected_tests=15, exit_code=proc.returncode,
        sources_unchanged=unchanged, historical_inputs_unchanged=historical_unchanged,
        actual_files=actual, remaining_caps={k:CAPS[k] for k in ("result.json","REPORT.md")},
        charged_total=charged, total_limit=4194304, violations=violations,
        historical_view_available=view_error is None and passed, historical_view_error=view_error,
        media_calls=0, scan_calls=0, runtime_calls=0, numerical_reverification=False, gates=False)
    write("result.json", result)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "QUALIFIED" and view_error is None else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare","qualify"))
    args = parser.parse_args()
    if args.mode == "prepare": prepare()
    else: sys.exit(qualify())
