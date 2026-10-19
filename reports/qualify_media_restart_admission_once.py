"""Bind, then invoke only the twelve new admission checks once."""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys

from reports import run_selected_media_restart_once as entry
from tools import _media_restart_evidence as e

ROOT = entry.ROOT
OUT = ROOT/"reports/media-restart-admission-qualification-20260913-02"
PREVIOUS = ROOT/"reports/media-restart-qualification-20260913-05"
ORIGINAL = ROOT/"reports/media-restart-qualification-20260913-01"
FIXTURE_OUTPUT = ROOT/"reports/media-admission-neutral-20260913-02"
OWN = ("tools/_media_restart_admission.py", "tools/_media_restart_player.py",
       "tools/_media_restart_checkpoint.py", "reports/run_selected_media_restart_once.py",
       "tests/test_media_restart_real_admission.py", "reports/qualify_media_restart_admission_once.py")


def refs(binding):
    return [dict(path=str(ROOT/name), category="sources", **binding["inventory"][name])
            for name in binding["charged_sources"]] + binding["proofs"]


def prepare():
    e.require(not OUT.exists() and not FIXTURE_OUTPUT.exists(), "ADMISSION_QUALIFICATION_USED")
    old = json.loads((ORIGINAL/"preregistration.json").read_bytes())
    previous = json.loads((PREVIOUS/"preregistration.json").read_bytes())
    inventory = {**old["inventory"], **previous["inventory_changes"]}
    for name, expected in inventory.items():
        if name not in OWN:
            e.require(entry.identity(ROOT/name) == expected, "ADMISSION_INHERITED_CODE_CHANGED", name)
    inventory.update({name: entry.identity(ROOT/name) for name in OWN})
    charged_sources = sorted({Path(ref["path"]).relative_to(ROOT).as_posix()
        for ref in previous["external"] if ref["category"] == "sources"} | set(OWN))
    proofs = [dict(path=str(folder/name), category="metadata", **entry.identity(folder/name))
              for folder in (ORIGINAL, PREVIOUS)
              for name in ("preregistration.json", "result.json", "stderr.log")]
    tests = [node.name for node in ast.walk(ast.parse((ROOT/OWN[4]).read_text()))
             if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")]
    future = [dict(name="logs", paths=["stdout.log", "stderr.log"], limit=8192, closed_by="result.json"),
        dict(name="closure", paths=["result.json", "REPORT.md", "balance.json"],
             limit=8192, closed_by="balance.json")]
    binding = dict(version="media.real-admission-qualification.v2-classified", inventory=inventory, proofs=proofs,
        charged_sources=charged_sources,
        classification=dict(copied_sources=[],
            rule="Each inventory member in charged_sources is fully counted by the existing -05 external rule or is new mandatory connection code. Every other member is unchanged installed basis, bound and hash-checked, not copied. Historical proof files remain fully counted.",
            basis=str(PREVIOUS/"preregistration.json")),
        tests=tests, test_calls=1, future=future, limits=e.LIMITS, fixture_envelope=32768,
        fixture_derivation="Four binding fixtures: each at most 6144 bytes including inventory, qualification and authorization. Other claims, shared objects, error evidence and external dispatch fixture together at most 8192. No media data except one 16-byte neutral hash fixture.",
        fixture_output=str(FIXTURE_OUTPUT), source_policy="Selected real payload access blocked in every test.",
        inheritance="Eight -05 continuation checks not repeated. Work, codec, evidence, reservations and serialization unchanged; admission sites and entry newly checked.",
        scope="Administrative fixtures. Both actual guard sites reached, then NativeRuntime construction stopped. No native history or real media claimed.")
    OUT.mkdir()
    store = e.Store(OUT, refs(binding), future=future)
    raw = e.canonical(binding)
    # The fixture reserve is additional, not borrowed from log or failure space.
    publication = store.budget([dict(path="preregistration.json", category="metadata", bytes=len(raw)),
        dict(path="preregistration.json.pending", category="metadata", bytes=len(raw))])
    prospective = store.budget([dict(path="preregistration.json", category="metadata", bytes=len(raw)),
        dict(path="all-neutral-fixtures-maximum", category="metadata", bytes=binding["fixture_envelope"])])
    if prospective["violations"] or publication["violations"]:
        print(json.dumps(dict(status="PRESTART_BLOCKED", test_calls=0, budget=prospective, publication=publication)))
        return
    store._write(OUT/"preregistration.json", raw, "metadata")
    print(json.dumps(dict(status="BOUND_NOT_RUN", tests=len(tests),
        preregistration=entry.identity(OUT/"preregistration.json"), budget=prospective, publication=publication)))


def run(sha):
    binding = entry.bound_json(OUT/"preregistration.json", sha)
    e.require(len(binding["tests"]) == 12, "ADMISSION_TEST_INVENTORY")
    for name, expected in binding["inventory"].items():
        e.require(entry.identity(ROOT/name) == expected, "ADMISSION_CODE_CHANGED")
    store = e.Store(OUT, refs(binding), future=binding["future"])
    projected = store.budget([dict(path="all-neutral-fixtures-maximum", category="metadata", bytes=binding["fixture_envelope"])])
    e.require(not projected["violations"], "ADMISSION_PREFLIGHT_BUDGET", projected)
    store._write(OUT/"test.claim", b"exactly one twelve-group neutral admission call", "metadata")
    env = dict(os.environ, MEDIA_ADMISSION_QUAL_OUT=str(OUT))
    with (OUT/"stdout.log").open("xb") as stdout, (OUT/"stderr.log").open("xb") as stderr:
        child = subprocess.run([sys.executable, "-m", "unittest", "tests.test_media_restart_real_admission", "-v"],
            cwd=ROOT, env=env, stdout=stdout, stderr=stderr, timeout=180)
    # The entry fixture must use a legal run-root; its complete files are still counted.
    extra = [dict(path=str(path), category="metadata", **entry.identity(path))
             for path in FIXTURE_OUTPUT.rglob("*") if path.is_file()]
    store = e.Store(OUT, refs(binding)+extra, future=binding["future"])
    unchanged = all(entry.identity(ROOT/name) == expected for name, expected in binding["inventory"].items())
    text = (OUT/"stderr.log").read_text()
    reached = "Ran 12 tests" in text
    result = dict(version=binding["version"], status="QUALIFIED" if child.returncode == 0 and reached and unchanged else "NOT_QUALIFIED",
        test_calls=1, tests_run=12 if reached else None, exit_code=child.returncode,
        inventory_digest=entry.c.b.digest(binding["inventory"]), hashes_unchanged=unchanged, gates=False,
        preregistration_sha256=sha, fixture_external=extra,
        scope=binding["scope"], unchanged_coverage=binding["inheritance"])
    store._write(OUT/"result.json", e.canonical(result), "metadata")
    print(json.dumps(dict(status=result["status"], tests_run=result["tests_run"], budget=store.budget())))


def prepare_real():
    """Metadata only, after the new proof is complete; never grant execution."""
    from dataclasses import asdict
    from tools import _media_restart_admission as admission
    proof = json.loads((OUT/"result.json").read_bytes())
    e.require(proof["status"] == "QUALIFIED" and (OUT/"balance.json").exists(), "ADMISSION_NOT_COMPLETE")
    binding = entry.bound_json(OUT/"preregistration.json", proof["preregistration_sha256"])
    for name, expected in binding["inventory"].items():
        e.require(entry.identity(ROOT/name) == expected, "ADMISSION_CODE_CHANGED")
    run_id = "media-restart-real-20260913-01"
    setup = ROOT/"reports"/(run_id+"-binding")
    output = ROOT/"reports"/run_id
    e.require(not setup.exists() and not output.exists(), "REAL_BINDING_USED")
    manifest = entry.c.p.build(run_id, entry.c.p.Source(str(admission.SOURCE), admission.SHA256, admission.SIZE),
        entry.c.b.digest(binding["inventory"]), mode=entry.c.p.FULL_VERSION)
    external = binding["proofs"] + proof["fixture_external"] + [
        dict(path=str(path), category="metadata", **entry.identity(path))
        for path in sorted(OUT.rglob("*")) if path.is_file()]
    future = [dict(name="logs", paths=[stage+suffix for stage in entry.STAGES for suffix in (".stdout", ".stderr")],
                   limit=8192, closed_by="result.json"),
        dict(name="closure", paths=["evaluation.json", "result.json", "REPORT.md", "balance.json"],
             limit=8192, closed_by="balance.json")]
    data = dict(version=entry.VERSION, output="reports/"+run_id, limits=e.LIMITS,
        stages=list(entry.STAGES), manifest=asdict(manifest), future=future, external=external,
        inventory_binding=dict(path=(OUT/"preregistration.json").relative_to(ROOT).as_posix(),
            sha256=entry.identity(OUT/"preregistration.json")["sha256"]),
        qualification=dict(path=(OUT/"result.json").relative_to(ROOT).as_posix(),
            sha256=entry.identity(OUT/"result.json")["sha256"]))
    raw = e.canonical(data)
    auth = e.canonical(dict(version=entry.VERSION, authorized=False, single_use=True,
        run_id=run_id, binding_sha256=e.sha(raw)))
    sources = [row for row in refs(binding) if row["category"] == "sources"]
    source_bytes = sum(row["bytes"] for row in sources)
    meta = sum(row["bytes"] for row in external)+len(raw)+len(auth)
    charged_meta = meta+8192+8192+e.FAILURE_RESERVE
    check = dict(metadata=charged_meta, sources=source_bytes, shared=source_bytes,
                 verification=0, total=charged_meta+source_bytes)
    e.require(not [key for key in check if check[key] > e.LIMITS[key]], "REAL_ADMINISTRATIVE_BUDGET", check)
    setup.mkdir()
    for name, contents in (("binding.json", raw), ("authorization-template.json", auth)):
        with (setup/name).open("xb") as stream:
            stream.write(contents)
    print(json.dumps(dict(status="BOUND_AWAITING_NEW_AUTHORIZATION", run_id=run_id,
        binding=entry.identity(setup/"binding.json"), template=entry.identity(setup/"authorization-template.json"),
        initial_with_future_and_failure=check, limits=e.LIMITS,
        caveat="Native/field/evidence occupancy is enforced per actual publication, including temporary copies. Not a universal success upper bound.",
        output_absent=not output.exists(), payload_reads=0)))


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif len(sys.argv) == 3 and sys.argv[1] == "run":
        run(sys.argv[2])
    elif sys.argv[1:] == ["prepare-real"]:
        prepare_real()
    else:
        raise SystemExit("prepare | run <preregistration-sha256>")
