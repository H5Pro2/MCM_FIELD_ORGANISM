"""Bind current code and one neutral suite before its only invocation."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"reports/media-restart-qualification-20260913-01"
OWN = ["tools/_media_restart_work.py", "tools/_media_restart_checkpoint.py",
       "tools/_media_restart_evidence.py", "tools/_media_restart_player.py",
       "tests/media_restart_neutral.py", "tests/test_media_restart_connection.py",
       "reports/qualify_media_restart_once.py"]


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def identity(path):
    data = path.read_bytes()
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def prepare():
    from tools import _media_restart_checkpoint as c
    from tools import _media_restart_evidence as evidence
    require = c.require
    require(not OUT.exists(), "QUALIFICATION_USED")
    previous = json.loads((ROOT/"reports/memory-restart-transfer-final/settings.json").read_bytes())
    names = set(previous["inventory"]["files"]) | set(c.media.FULL_OWN) | set(OWN)
    inventory = {name: identity(ROOT/name) for name in sorted(names)}
    # Unchanged base libraries remain explicitly hash-bound, as in the existing
    # checkpoint admission; only active adapter source artifacts are charged here.
    charged = sorted(set(c.media.FULL_OWN) | set(OWN) | {
        "tools/_memory_checkpoint.py", "tools/_memory_checkpoint_ledger.py"})
    external = [dict(path=str(ROOT/name), category="sources", **inventory[name]) for name in charged]
    source = ROOT/"sources/media-restart-neutral/qualification-20260913-01.bin"
    require(not source.exists(), "NEUTRAL_INPUT_EXISTS")
    data = bytes(range(256))*32
    spec = c.p.Source(str(source), hashlib.sha256(data).hexdigest(), len(data))
    manifest = c.p.build("media-restart-neutral-20260913-01", spec,
                         c.b.digest(inventory), mode=c.p.FULL_VERSION)
    tests = sorted(node.name for node in ast.walk(ast.parse((ROOT/OWN[5]).read_text()))
                   if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"))
    # A shared object is admitted only after actual byte equality. Allocations
    # bound the finite qualification store, not arbitrary real-world results.
    reserve = dict(metadata=131072, sources=sum(x["bytes"] for x in external),
        native=1507328, field=1706320, nj=22528, formations=30720, generations=30720,
        verification=131072)
    reserve["shared"] = sum(reserve[k] for k in ("sources", "nj", "formations", "generations"))
    reserve["total"] = sum(reserve[k] for k in ("metadata", "sources", "native", "field", "nj",
                                               "formations", "generations", "verification"))
    violations = [k for k, cap in evidence.LIMITS.items() if reserve[k] > cap]
    binding = dict(version="media.restart-qualification.v1", tests=tests, test_calls=0,
        inventory=inventory, charged_sources=charged, external=external,
        manifest=c.asdict(manifest), work_version=c.work.VERSION, limits=evidence.LIMITS,
        reservation=reserve, violations=violations,
        neutral_source=dict(recipe="bytes(range(256))*32", bytes=len(data), sha256=spec.sha256),
        neutral_backend="Synthetic packet/frame codec; real OS worker and native receptor/runtime",
        comparisons=[dict(reference="reference", save="early-save", restore="early-restore", cut=1),
                     dict(reference="reference", save="late-save", restore="late-restore", cut=19)],
        work_upper=dict(video_frames=1602, audio_frames=2510, packets=4112,
                        container_read_bytes=36880),
        work_derivation="801 video and 1255 audio packets/frames incl delayed final packet per complete pass; two file hash reads per decoder plus one byte per packet. Prefix plus complete restore <= two complete passes.",
        envelope_notes=["Field: three different snapshots plus one temporary copy, 4*426580.",
            "Native shared object allocation 1507328; enforced actual total and item caps. No expected equality substituted for generated data.",
            "Metadata allocation includes all role indices, preregistration, logs, claims and closure.",
            "Verification permanent and temporary bodies share 131072 reserved bytes.",
            "Full error logs retained even if the reservation fails; never truncate.",
            "This is a qualification allocation, not a universal size bound for changed data."])
    OUT.mkdir()
    (OUT/"preregistration.json").write_bytes(raw(binding))
    require(not violations, "QUALIFICATION_PREFLIGHT_BUDGET", binding)
    source.parent.mkdir(parents=True, exist_ok=True)
    with source.open("xb") as stream:
        stream.write(data)
    print(json.dumps(dict(tests=len(tests), reservation=reserve, violations=violations)))


def run():
    value = json.loads((OUT/"preregistration.json").read_bytes())
    if value["violations"]:
        raise RuntimeError("precondition failed")
    for name, expected in value["inventory"].items():
        if identity(ROOT/name) != expected:
            raise RuntimeError("source changed: "+name)
    with (OUT/"test.claim").open("xb") as stream:
        stream.write(b"one complete neutral suite")
    env = dict(os.environ, MEDIA_RESTART_QUAL_OUT=str(OUT), OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    with (OUT/"stdout.log").open("xb") as stdout, (OUT/"stderr.log").open("xb") as stderr:
        result = subprocess.run([sys.executable, "-m", "unittest", "tests.test_media_restart_connection", "-v"],
            cwd=ROOT, env=env, stdout=stdout, stderr=stderr, timeout=1200)
    unchanged = all(identity(ROOT/name) == expected for name, expected in value["inventory"].items())
    from tools import _media_restart_evidence as evidence
    store = evidence.Store(OUT, value["external"])
    ledger = store.ledger()
    summary = dict(status="QUALIFIED" if result.returncode == 0 and unchanged and not ledger["violations"] else "NOT_QUALIFIED",
        exit_code=result.returncode, test_calls=1, hashes_unchanged=unchanged, gates=False,
        actual_before_closure=ledger["totals"], violations=ledger["violations"],
        preregistration_sha256=identity(OUT/"preregistration.json")["sha256"])
    # Complete diagnostics are kept even if a failure exceeds an allocation.
    with (OUT/"result.json").open("xb") as stream:
        stream.write(raw(summary))
    ledger = store.ledger()
    with (OUT/"balance-before-report.json").open("xb") as stream:
        stream.write(raw(ledger))
    print(json.dumps(summary))


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif sys.argv[1:] == ["run"]:
        run()
    else:
        raise SystemExit("prepare or run required")
