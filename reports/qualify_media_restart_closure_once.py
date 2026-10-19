"""Prospective binding and single focused closure qualification, never a video run."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"reports/media-restart-qualification-20260913-02"
OLD = ROOT/"reports/media-restart-qualification-20260913-01"
NEW = ["tests/test_media_restart_closure.py", "reports/qualify_media_restart_closure_once.py"]
CHANGED = ["tools/_media_restart_evidence.py", "tools/_media_restart_checkpoint.py",
           "tools/_media_restart_player.py"]


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def identity(path):
    value = Path(path).read_bytes()
    return dict(bytes=len(value), sha256=hashlib.sha256(value).hexdigest())


def inventory(binding):
    prior = json.loads((OLD/"preregistration.json").read_bytes())["inventory"]
    return {**prior, **binding["inventory_changes"]}


def prepare():
    from tools import _media_restart_checkpoint as c
    from tools import _media_restart_evidence as e
    c.require(not OUT.exists(), "QUALIFICATION_ID_USED")
    historical = json.loads((OLD/"preregistration.json").read_bytes())
    old_inventory = historical["inventory"]
    changes = {name: identity(ROOT/name) for name in CHANGED+NEW}
    for name, expected in old_inventory.items():
        if name not in CHANGED:
            c.require(identity(ROOT/name) == expected, "UNCHANGED_DEPENDENCY_CHANGED", name)
    current = {**old_inventory, **changes}
    charged = sorted(set(historical["charged_sources"]) | set(NEW))
    external = [dict(path=str(ROOT/name), category="sources", **current[name]) for name in charged]
    for name in ("preregistration.json", "result.json", "stderr.log"):
        external.append(dict(path=str(OLD/name), category="metadata", **identity(OLD/name)))
    source = ROOT/"sources/media-restart-neutral/qualification-20260913-02.bin"
    c.require(not source.exists(), "NEUTRAL_INPUT_USED")
    data = bytes(range(256))*32
    spec = c.p.Source(str(source), hashlib.sha256(data).hexdigest(), len(data))
    manifest = c.p.build("media-restart-neutral-20260913-02", spec, c.b.digest(current), mode=c.p.FULL_VERSION)
    tests = sorted(n.name for n in ast.walk(ast.parse((ROOT/NEW[0]).read_text()))
                   if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
    binding = dict(version="media.restart-closure-qualification.v2", test_calls=0, tests=tests,
        inventory_changes=changes, inherited_inventory=str(OLD/"preregistration.json"), external=external,
        manifest=c.asdict(manifest), limits=e.LIMITS,
        inherited_coverage=dict(status="OLD_RUN_REMAINS_NOT_QUALIFIED", groups=[1,2,3,4,5,9,10,11],
            evidence=[str(OLD/name) for name in ("preregistration.json", "result.json", "stderr.log")],
            note="No new pass count. Decoder/work/worker and old tests retain their exact source hashes. Changed reference paths are qualified independently."),
        neutral_backend="Unchanged synthetic codec; native OS worker, receptors and memory/field runtime",
        source_recipe="bytes(range(256))*32; new neutral source identity; no real media",
        comparisons=[dict(reference="reference", save="early-save", restore="early-restore", cut=1),
                     dict(reference="reference", save="late-save", restore="late-restore", cut=19)],
        failure_reserve=e.FAILURE_RESERVE, failure_file_max=e.FAILURE_BYTES,
        stages=5, additional_native_failure_formations=1,
        scope="One new focused invocation; old missing budget sum remains unknown.")
    # Finite schema allowances are charged together, including the old proof
    # dependencies. They are not inferred from the previous successful record.
    metadata = dict(active_historical_proofs=sum(x["bytes"] for x in external if x["category"] == "metadata"),
        binding=16384, shared_administrative_objects=40960, role_roots_and_claims=16384,
        qualification_logs=8192, report_result_and_balance=4096,
        controls=2048, pending_largest_administrative_object=4096,
        reserved_primary_failure=e.FAILURE_RESERVE)
    # The shared-object allowance is a bounded admission allocation, not an
    # assumption of arm equality. A larger index must fail before publication.
    reservation = dict(metadata=sum(metadata.values()), sources=sum(x["bytes"] for x in external if x["category"] == "sources"),
        native=1507328, field=1706320, nj=22528, formations=30720, generations=30720, verification=131072)
    reservation["shared"] = sum(reservation[k] for k in ("sources", "nj", "formations", "generations"))
    reservation["total"] = sum(reservation[k] for k in ("metadata", "sources", "native", "field", "nj", "formations", "generations", "verification"))
    binding["metadata_contributions"] = metadata
    binding["reservation"] = reservation
    binding["violations"] = [k for k, cap in e.LIMITS.items() if reservation[k] > cap]
    # Store one shared reservation, not 42 copies of identical administrative data.
    binding["progress_envelopes"] = dict(completed=list(range(21)), success="reservation",
        failure="reservation", alternatives_not_added=True,
        note="Failure allocation already included; publication peak counts pending plus final. All physical logs remain counted even on overrun.")
    actual_binding = len(raw(binding))
    if actual_binding > metadata["binding"]:
        binding["violations"].append("binding_format")
    binding["bound_binding_bytes_before_this_field"] = actual_binding
    OUT.mkdir()
    with (OUT/"preregistration.json").open("xb") as stream:
        stream.write(raw(binding))
    c.require(not binding["violations"], "QUALIFICATION_PREFLIGHT_BUDGET", dict(
        metadata_contributions=metadata, reservation=reservation, limits=e.LIMITS,
        violations=binding["violations"]))
    source.parent.mkdir(parents=True, exist_ok=True)
    with source.open("xb") as stream:
        stream.write(data)
    print(json.dumps(dict(test_calls=0, tests=len(tests), reservation=reservation,
        metadata_contributions=metadata, preregistration=identity(OUT/"preregistration.json"))))


def run():
    from tools import _media_restart_evidence as e
    binding = json.loads((OUT/"preregistration.json").read_bytes())
    if binding["violations"]:
        raise RuntimeError("preflight rejected; no test call")
    for ref in binding["external"]:
        if identity(ref["path"]) != {k: ref[k] for k in ("bytes", "sha256")}:
            raise RuntimeError("external dependency changed")
    expected = inventory(binding)
    if any(identity(ROOT/name) != value for name, value in expected.items()):
        raise RuntimeError("source changed")
    with (OUT/"test.claim").open("xb") as stream:
        stream.write(b"one focused neutral qualification")
    env = dict(os.environ, MEDIA_RESTART_QUAL_OUT=str(OUT), OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    with (OUT/"stdout.log").open("xb") as stdout, (OUT/"stderr.log").open("xb") as stderr:
        result = subprocess.run([sys.executable, "-m", "unittest", "tests.test_media_restart_closure", "-v"],
            cwd=ROOT, env=env, stdout=stdout, stderr=stderr, timeout=1200)
    unchanged = all(identity(ROOT/name) == value for name, value in expected.items())
    store = e.Store(OUT, binding["external"])
    ledger = store.ledger()
    summary = dict(status="QUALIFIED" if result.returncode == 0 and unchanged and not ledger["violations"] else "NOT_QUALIFIED",
        test_calls=1, exit_code=result.returncode, hashes_unchanged=unchanged, gates=False,
        actual_before_report=ledger["totals"], violations=ledger["violations"],
        preregistration_sha256=identity(OUT/"preregistration.json")["sha256"])
    with (OUT/"result.json").open("xb") as stream:
        stream.write(raw(summary))
    # The available file tree and digest-named objects are the complete index;
    # do not duplicate that index inside its own closure diagnostics.
    print(json.dumps(summary))


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif sys.argv[1:] == ["run"]:
        run()
    else:
        raise SystemExit("prepare or run required")
