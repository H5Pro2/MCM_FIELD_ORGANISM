"""One bound neutral call; successful continuation is conditional on actual size."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT/"reports/media-restart-qualification-20260913-01"
OUT = ROOT/"reports/media-restart-qualification-20260913-05"
OWN = ("tools/_media_restart_checkpoint.py", "tools/_media_restart_evidence.py",
       "tools/_media_restart_player.py", "tools/_media_restart_reservations.py",
       "tools/_media_restart_serialization.py", "tests/test_media_restart_reserved.py",
       "tests/test_media_restart_measured.py", "reports/qualify_media_restart_measured_once.py")


def identity(path):
    data = Path(path).read_bytes()
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def inherited_inventory(binding):
    old = json.loads((OLD/"preregistration.json").read_bytes())
    return {**old["inventory"], **binding["inventory_changes"]}


def prepare():
    from tools import _media_restart_checkpoint as c
    from tools import _media_restart_evidence as e
    c.require(not OUT.exists(), "QUALIFICATION_ID_USED")
    old = json.loads((OLD/"preregistration.json").read_bytes())
    changes = {name: identity(ROOT/name) for name in OWN}
    for name, expected in old["inventory"].items():
        if name not in OWN:
            c.require(identity(ROOT/name) == expected, "UNCHANGED_DEPENDENCY_CHANGED", name)
    current = {**old["inventory"], **changes}
    charged = sorted(set(old["charged_sources"]) | set(OWN))
    external = [dict(path=str(ROOT/name), category="sources", **current[name]) for name in charged]
    for name in ("preregistration.json", "result.json", "stderr.log"):
        external.append(dict(path=str(OLD/name), category="metadata", **identity(OLD/name)))
    source_path = ROOT/"sources/media-restart-neutral/qualification-20260913-05.bin"
    c.require(not source_path.exists(), "NEUTRAL_SOURCE_USED")
    data = bytes(range(256))*32
    source = c.p.Source(str(source_path), hashlib.sha256(data).hexdigest(), len(data))
    manifest = c.p.build("media-restart-neutral-20260913-05", source, c.b.digest(current), mode=c.p.FULL_VERSION)
    tests = sorted(node.name for name in OWN[5:7]
                   for node in ast.walk(ast.parse((ROOT/name).read_text()))
                   if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"))
    future = [dict(name="logs", paths=["stdout.log", "stderr.log"]+
                  [folder+extension for folder in ("reference", "early-save", "early-restore", "late-save", "late-restore")
                   for extension in (".stdout", ".stderr")], limit=8192, closed_by="result.json"),
              dict(name="closure", paths=["result.json", "REPORT.md", "closure-balance.json"],
                   limit=4096, closed_by="closure-balance.json")]
    binding = dict(version="media.restart-measured-qualification.v4", ready=True, test_calls=0, tests=tests,
        manifest=c.asdict(manifest), inventory_changes=changes, external=external, future=future,
        inventory_parent=str(OLD/"preregistration.json"), limits=e.LIMITS,
        primary_failure_reserve=e.FAILURE_RESERVE, primary_failure_file_limit=e.FAILURE_BYTES,
        serialization_limit=e.serialization.MAX_BYTES, serialization_chunk_characters=e.serialization.TEXT_CHUNK,
        rule="Actual serialized bytes, all physical copies and remaining declared future slots. No hypothetical arm equality credit.",
        success_scope="All cuts 1..19 supported subject to concrete occupancy; no success guarantee at simultaneous item maxima.",
        qualification_scope="Eight focused groups, including the six never invoked at -03. One call only.",
        historical_scope="Old -01 decoder/work/worker coverage remains historical; no old pass count is transferred. -02/-03 are archived, not required current execution inputs.",
        native_stages=[dict(role=role, cut=cut) for role, cut in
            (("reference", 0), ("early-save", 1), ("early-restore", 0), ("late-save", 19), ("late-restore", 0))],
        extra_native_error_formations=1, offered_cuts=list(range(1, 20)),
        neutral_backend="Synthetic codec only; actual native receptor, NJ, field/memory runtime and fresh OS worker processes.",
        neutral_source=dict(recipe="bytes(range(256))*32", **identity_bytes(data)),
        log_overrun="Preserve complete logs; any excess remains a qualification violation. Emergency publication may report a slot overrun but cannot exceed global bounds.",
        error_scope="Compact actual progress bindings; no claim of reconstructing an unpublished native prefix from its digests.")
    OUT.mkdir()
    store = e.Store(OUT, external, future=future)
    raw = e.canonical(binding)
    store._write(OUT/"preregistration.json", raw, "metadata")
    with source_path.open("xb") as stream:
        stream.write(data)
    print(json.dumps(dict(test_calls=0, groups=len(tests), preregistration=identity(OUT/"preregistration.json"),
        actual_initial_budget=store.budget(), source_bytes=sum(x["bytes"] for x in external if x["category"] == "sources"))))


def identity_bytes(data):
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def run(expected_sha):
    from tools import _media_restart_evidence as e
    if identity(OUT/"preregistration.json")["sha256"] != expected_sha:
        raise RuntimeError("preregistration identity changed")
    binding = json.loads((OUT/"preregistration.json").read_bytes())
    if not binding["ready"]:
        raise RuntimeError("binding not admitted")
    for reference in binding["external"]:
        if identity(reference["path"]) != {key: reference[key] for key in ("bytes", "sha256")}:
            raise RuntimeError("external binding changed")
    expected = inherited_inventory(binding)
    if any(identity(ROOT/name) != value for name, value in expected.items()):
        raise RuntimeError("source binding changed")
    store = e.Store(OUT, binding["external"], future=binding["future"])
    store._write(OUT/"test.claim", b"one focused measured-publication qualification", "metadata")
    env = dict(os.environ, MEDIA_RESTART_QUAL_OUT=str(OUT), OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    with (OUT/"stdout.log").open("xb") as stdout, (OUT/"stderr.log").open("xb") as stderr:
        process = subprocess.run([sys.executable, "-m", "unittest", "tests.test_media_restart_measured", "-v"],
            cwd=ROOT, env=env, stdout=stdout, stderr=stderr, timeout=1200)
    unchanged = all(identity(ROOT/name) == value for name, value in expected.items())
    log = (OUT/"stderr.log").read_text()
    match = re.search(r"Ran (\d+) tests", log)
    count = int(match.group(1)) if match else None
    budget = store.budget()
    good = process.returncode == 0 and unchanged and count == len(binding["tests"])
    summary = dict(status="QUALIFIED" if good else "NOT_QUALIFIED", test_calls=1, tests_run=count,
        exit_code=process.returncode, hashes_unchanged=unchanged, gates=False,
        actual_before_closure=budget["occupied"], pre_result_reserved_violations=budget["violations"],
        preregistration_sha256=expected_sha)
    store.context = dict(phase="QUALIFICATION_RESULT", event=None, completed=count)
    try:
        store._write(OUT/"result.json", e.canonical(summary), "metadata")
    except e.w.RestartError as exc:
        summary["status"] = "NOT_QUALIFIED"
        summary["result_publication_error"] = dict(code=exc.code, details=exc.details)
        store.failure(OUT/"result.json", summary)
    print(json.dumps(summary))


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif len(sys.argv) == 3 and sys.argv[1] == "run":
        run(sys.argv[2])
    else:
        raise SystemExit("prepare, or run <bound-preregistration-sha256>")
