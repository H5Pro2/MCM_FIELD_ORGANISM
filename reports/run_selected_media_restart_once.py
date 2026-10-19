"""File-bound one-use reference and suspend-19 comparison. Never auto-authorize."""
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

from tools import _media_restart_admission as a
from tools import _media_restart_checkpoint as c
from tools import _media_restart_evidence as e
from tools import _media_restart_player as p
from tools import _media_restart_work as w

ROOT = c.b.ROOT
VERSION = "media.selected-restart-entry.v4-window-replay"
STAGES = ("reference", "suspend19", "restore20")


def identity(path):
    digest, size = hashlib.sha256(), 0
    with Path(path).open("rb") as stream:
        while block := stream.read(65536):
            size += len(block)
            digest.update(block)
    return dict(bytes=size, sha256=digest.hexdigest())


def bound_json(path, sha):
    path = Path(path).resolve()
    w.require(path.is_relative_to(ROOT) and path != a.SOURCE.resolve(), "REAL_BINDING_PATH")
    raw = e.serialization.read_bounded(path, 65536)
    w.require(hashlib.sha256(raw).hexdigest() == sha, "REAL_BINDING_HASH")
    value = json.loads(raw)
    w.require(type(value) is dict, "REAL_BINDING_FORM")
    return value


def reference_rows(data):
    rows = list(data["external"])
    catalogs = data.get("reference_catalogs", [])
    w.require(type(catalogs) is list and len(catalogs) <= 4, "REAL_REFERENCE_CATALOGS")
    for catalog in catalogs:
        value = bound_json(ROOT/catalog["path"], catalog["sha256"])
        w.require(set(value) == {"references"} and type(value["references"]) is list,
                  "REAL_REFERENCE_CATALOG_FORM")
        rows.extend(value["references"])
        rows.append(dict(path=str(ROOT/catalog["path"]), category="metadata",
                         **identity(ROOT/catalog["path"])))
    return rows


def load(path, sha, authorization_path, authorization_sha):
    data = bound_json(path, sha)
    profile = e.profiles.bind(data.get("budget_profile"))
    w.require(profile is not None, "REAL_BUDGET_PROFILE_REQUIRED")
    w.require(data["version"] == VERSION and data["limits"] == profile.limits
              and data["stages"] == list(STAGES), "REAL_BINDING_FORM")
    plan = e.publication.Plan.bind(data.get("publication_plan"))
    w.require(plan.profile_digest == e.profiles.digest(), "REAL_PLAN_PROFILE_BINDING")
    w.require(plan.scope == "FULL_REPLAY_RESTART", "PUBLICATION_PLAN_SCOPE")
    w.require(data.get("replay_protocol") == dict(version=w.replay.VERSION, request_seconds=30.0,
        total_seconds=600.0, max_requests=20, max_windows_per_request=1), "REAL_REPLAY_PROTOCOL")
    manifest = c.p.decode(data["manifest"])
    auth = bound_json(authorization_path, authorization_sha)
    w.require(auth == dict(version=VERSION, authorized=True, single_use=True,
        run_id=manifest.run_id, binding_sha256=sha), "RESTART_REAL_AUTHORIZATION_REQUIRED")
    admission = a.Admission(a.VERSION, manifest.run_id, manifest.manifest_digest,
        manifest.code_digest, manifest.profile_digest, manifest.source.path,
        manifest.source.sha256, manifest.source.size, True)
    a.validate(manifest, a.REAL, admission)
    output = (ROOT/data["output"]).resolve()
    w.require(output.parent == ROOT/"reports" and output.name == manifest.run_id,
              "REAL_OUTPUT_BINDING")
    iref = data["inventory_binding"]
    ipath = ROOT/iref["path"]
    inventory_binding = bound_json(ipath, iref["sha256"])
    inventory = inventory_binding["inventory"]
    charged_sources = inventory_binding["charged_sources"]
    w.require(c.b.digest(inventory) == manifest.code_digest, "REAL_CODE_BINDING")
    w.require(len(charged_sources) == len(set(charged_sources))
        and set(charged_sources) <= inventory.keys(), "REAL_SOURCE_CLASSES")
    for name, expected in inventory.items():
        target = (ROOT/name).resolve()
        w.require(target.is_relative_to(ROOT) and target.suffix in (".py", ".html"), "REAL_CODE_PATH")
        w.require(identity(target) == expected, "REAL_CODE_CHANGED", name)
    external = [dict(path=str(ROOT/name), category="sources", **inventory[name])
                for name in charged_sources]
    for ref in reference_rows(data):
        target = Path(ref["path"]).resolve()
        w.require(target.is_relative_to(ROOT) and not target.is_relative_to(output)
            and ref["category"] in e.publication.CATEGORIES, "REAL_REFERENCE_PATH")
        w.require(identity(target) == {k: ref[k] for k in ("bytes", "sha256")}, "REAL_REFERENCE_CHANGED")
        external.append(ref)
    charged = {Path(x["path"]).resolve() for x in external}
    w.require(len(charged) == len(external), "REAL_REFERENCE_DUPLICATE")
    qref = data["qualification"]
    q = bound_json(ROOT/qref["path"], qref["sha256"])
    w.require((ROOT/qref["path"]).resolve() in charged and q["status"] == "QUALIFIED"
        and q["inventory_digest"] == manifest.code_digest and q["hashes_unchanged"] is True
        and q["preregistration_sha256"] == iref["sha256"],
        "REAL_NOT_QUALIFIED")
    # The separately approved authorization is also a physical required input.
    authref = dict(path=str(Path(authorization_path).resolve()), category="metadata",
                   **identity(authorization_path))
    if Path(path).resolve() not in charged:
        external.append(dict(path=str(Path(path).resolve()), category="metadata", **identity(path)))
    if ipath.resolve() not in charged:
        external.append(dict(path=str(ipath.resolve()), category="metadata", **identity(ipath)))
    if Path(authref["path"]) not in charged:
        external.append(authref)
    return data, manifest, admission, output, external


class SelectedPlayer(p.Player):
    def _after_event(self):
        if self.binding.stage == "suspend19" and len(self.session.runtime.rows) == 19:
            self.stop_event.set()


def stage(data, manifest, admission, output, store, role):
    w.require(role in STAGES, "REAL_STAGE_INVALID")
    w.require(store.read(output/"run.claim")["manifest"] == manifest.manifest_digest,
              "REAL_PARENT_CLAIM")
    if role != "reference":
        previous = STAGES[STAGES.index(role)-1]
        proof = store.read(output/(previous+"-process.json"))
        w.require(proof["closed"] and proof["gate"] is False and proof["qualified_gate"] is False,
                  "REAL_PREVIOUS_NOT_CLOSED")
        w.require(proof["pid"] != os.getpid(), "REAL_PROCESS_NOT_CHANGED")
    binding = SimpleNamespace(manifest=manifest, source=Path(manifest.source.path),
        output=output/role, claim=output/(role+".claim"), mode=a.REAL,
        admission=admission, stage=role)
    app = SelectedPlayer(binding, store,
        selected_checkpoint=output/"suspend19/checkpoint.json" if role == "restore20" else None)
    c.QUALIFIED = True
    try:
        app.start()
        app.thread.join()
        status = json.loads(app.status())
        w.require(status["phase"] == ("SUSPENDED" if role == "suspend19" else "RECORDING_COMPLETE"),
                  "REAL_STAGE_FAILED", status)
    finally:
        c.MAIN_GATE = c.QUALIFIED = False
    store.publish(output/(role+"-process.json"), dict(pid=os.getpid(), closed=app.session.closed,
        gate=c.MAIN_GATE, qualified_gate=c.QUALIFIED, phase=status["phase"], completed=status["completed"]))


def launch(path, sha, authpath, authsha, role, store):
    with (store.root/(role+".stdout")).open("xb") as stdout, (store.root/(role+".stderr")).open("xb") as stderr:
        child = subprocess.run([sys.executable, "-m", "reports.run_selected_media_restart_once",
            "stage", str(path), sha, str(authpath), authsha, role], cwd=ROOT,
            stdout=stdout, stderr=stderr)
    w.require(child.returncode == 0, "REAL_CHILD_FAILED", dict(stage=role, exit_code=child.returncode))


def evaluate(store, manifest, verified):
    w.require(verified["status"] == "RECORDING_COMPLETE" and verified["evaluation_allowed"],
              "REAL_EVALUATION_BLOCKED")
    left = store.read(store.root/"reference/record.json")
    right = store.read(store.root/"restore20/record.json")
    result = dict(version=VERSION, manifest=manifest.manifest_digest,
        scope="Same selected file; controlled process restart, not recognition or general recovery.",
        rows=verified["rows"], core_equal=verified["core_equal"],
        selections_equal=verified["selections_equal"], final_field_equal=verified["final_field_equal"],
        materializer_equal=left["accounting"]["materializer"] == right["accounting"]["materializer"],
        reference_account=left["accounting"], restored_account=right["accounting"],
        sources_reused=True, hypotheses_applied=False)
    result["status"] = "CONFIRMED" if all(result[k] for k in
        ("core_equal", "selections_equal", "final_field_equal", "materializer_equal")) else "FALSIFIED"
    store.publish(store.root/"evaluation.json", result)
    return result


def execute(path, sha, authpath, authsha, role=None):
    data, manifest, admission, output, external = load(path, sha, authpath, authsha)
    if role is None:
        w.require(not output.exists(), "REAL_OUTPUT_USED")
    store = e.Store(output, external, future=data["future"], publication_plan=data["publication_plan"],
                    budget_profile=data["budget_profile"])
    w.require(not store.budget()["violations"], "REAL_PREFLIGHT_BUDGET", store.budget())
    if role is None:
        store.preflight()
    try:
        if role is not None:
            stage(data, manifest, admission, output, store, role)
            return
        store.publish_profile()
        store.publish(output/"run.claim", dict(manifest=manifest.manifest_digest, uses=1))
        for current in STAGES:
            store.context = dict(phase=current, event=None, completed=0)
            launch(path, sha, authpath, authsha, current, store)
        store.context = dict(phase="VERIFICATION", event=20, completed=20)
        verified = p.verify_comparison(store, manifest, "reference", "suspend19", "restore20",
            scope="Selected real file; one controlled restart after 19. No general codec work guarantee.")
        store.context = dict(phase="EVALUATION", event=20, completed=20)
        evaluate(store, manifest, verified)
        store.publish(output/"result.json", dict(status="RECORDING_COMPLETE", gates=False,
            evaluation_allowed=True, sources_reused=True, stages=list(STAGES)))
    except Exception as exc:
        # A native primary failure remains authoritative; do not duplicate it.
        primary = [str(x.relative_to(output)) for x in output.glob("*/failure.json")]
        if not primary:
            store.failure(output/"failure.json", dict(status="NOT_EVALUABLE", gate=False,
                code=getattr(exc, "code", type(exc).__name__), details=getattr(exc, "details", None),
                **store.context))
        raise
    finally:
        c.MAIN_GATE = c.QUALIFIED = False


def main(argv):
    w.require(len(argv) in (5, 6) and argv[0] in ("run", "stage"), "REAL_ENTRY_ARGUMENTS")
    w.require((argv[0] == "run" and len(argv) == 5) or
              (argv[0] == "stage" and len(argv) == 6), "REAL_ENTRY_ARGUMENTS")
    execute(*argv[1:5], role=None if argv[0] == "run" else argv[5])


if __name__ == "__main__":
    main(sys.argv[1:])
