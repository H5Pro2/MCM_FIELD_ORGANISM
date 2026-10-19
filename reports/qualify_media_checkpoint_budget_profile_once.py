"""One administrative profile qualification and an unapproved real binding."""
import ast
from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import sys

from reports import run_selected_media_restart_once as entry
from tools import _media_restart_evidence as e
from tools import _media_checkpoint_budget_profile as b

ROOT = entry.ROOT
OUT = ROOT/"reports/media-checkpoint-budget-profile-qualification-20260913-01"
CATALOG = ROOT/"reports/MEDIA_RESTART_SUCCESS_ENVELOPE_20260913.json"
OWN = ("tools/_media_checkpoint_budget_profile.py", "tools/_media_publication_plan.py",
       "tools/_media_restart_evidence.py", "tools/_media_restart_player.py",
       "reports/run_selected_media_restart_once.py", "tests/test_media_checkpoint_budget_profile.py",
       "reports/qualify_media_checkpoint_budget_profile_once.py")
VERSION = "media.checkpoint-budget-profile-qualification.v1"


def reference(path, category="metadata"):
    return dict(path=str(path), category=category, **entry.identity(path))


def previous_inventory():
    q = json.loads((ROOT/"reports/media-publication-plan-qualification-20260913-01/preregistration.json").read_bytes())
    base = entry.bound_json(q["parent"]["path"], q["parent"]["sha256"])
    focused = json.loads((ROOT/"reports/media-failure-form-qualification-20260913-01/preregistration.json").read_bytes())
    result = {**base["inventory"], **q["inventory_changes"], **focused["new_sources"]}
    for name, expected in result.items():
        if name not in OWN:
            e.require(entry.identity(ROOT/name) == expected, "PROFILE_UNCHANGED_SOURCE", name)
    return result


def refs(binding):
    return [dict(path=str(ROOT/name), category="sources", **binding["inventory"][name])
            for name in binding["charged_sources"]]+binding["proofs"]


def plan(catalog):
    old = {row["role"]: row for row in catalog["roles"]}
    positions = [dict(id=role, category=category, count=count, lower=0,
        upper=len(e.canonical(b.payload())) if role == "budget-profile.json" else old[role]["upper_each"])
        for role, (category, count) in e.publication.full_layout(b.digest()).items()]
    return dict(version=e.publication.VERSION, scope="FULL_RESTART", budget_profile_digest=b.digest(), positions=positions)


def full_projection(ledger, value, future):
    # Qualification files are external to the prospective run, never its markers.
    ledger = dict(ledger, files=[dict(row, path="external:"+row["path"]) for row in ledger["files"]])
    groups = e.reservations.bind(future)
    outcomes = e.publication.Plan.bind(value).preflight(ledger, groups, groups, e.FAILURE_BYTES)
    peaks = {key: max(row["decision"]["success"]["charged"][key] for row in outcomes) for key in b.Profile().limits}
    failure = {key: max(v["charged"][key] for row in outcomes for v in row["decision"]["failure"]) for key in peaks}
    return dict(status="PASSEND", upper_peaks=peaks, failure_peaks=failure,
        remaining={key: cap-peaks[key] for key, cap in b.LIMITS}, limits=dict(b.LIMITS), roles=len(outcomes),
        interpretation="Conservative reservation, not measured media consumption or jointly observed maxima.")


def prepare():
    e.require(not OUT.exists(), "PROFILE_QUALIFICATION_USED")
    catalog = json.loads(CATALOG.read_bytes())
    inventory = previous_inventory()
    inventory.update({name: entry.identity(ROOT/name) for name in OWN})
    charged = sorted({Path(row["path"]).as_posix() for row in catalog["active"] if row["category"] == "sources"} | set(OWN))
    proofs = [reference(ROOT/row["path"]) for row in catalog["active"] if row["category"] == "metadata"]
    tests = [n.name for n in ast.walk(ast.parse((ROOT/OWN[-2]).read_text()))
             if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    e.require(len(tests) == 16, "PROFILE_TEST_INVENTORY")
    future = [dict(name="logs", paths=["stdout.log", "stderr.log"], limit=8192, closed_by="result.json"),
        dict(name="closure", paths=["result.json", "REPORT.md", "balance.json"], limit=8192, closed_by="balance.json")]
    binding = dict(version=VERSION, budget_profile=b.payload(), inventory=inventory, charged_sources=charged,
        proofs=proofs, tests=tests, test_calls=1, future=future, publication_plan=plan(catalog),
        real_future=catalog["joint_reservations"], fixture_reserve=16384, publication_extra=8192,
        real_setup_reserves=dict(binding=61440, authorization_template=1024, budget=4096, plan=1024,
                                 budget_profile=len(e.canonical(b.payload()))),
        fixture_derivation="Sixteen administrative cases; small profile/record markers and one 100-byte file. No native data. Oversized values are rejected before publication. Joint fixture peak reserved at 16384, complete logs at 8192, closure at 8192, additional publication at 8192 and protected failure copies at 8192.",
        scope="Only budget/profile/administrative publication. No perception or restore test repetition.",
        unchanged="Worker, decoder, admission, receptors, native checkpoint, state codec, field and memory implementation unchanged. Historical Store defaults unchanged; new semantics require the explicit profile.",
        repository_head="537109994cf777f8d36cda617aafe12226806c25", dirty_tree=True)
    OUT.mkdir()
    store = e.Store(OUT, refs(binding), future=future, budget_profile=b.payload())
    raw = e.canonical(binding)
    extra = [dict(path="preregistration.json", category="metadata", bytes=len(raw)),
        dict(path="budget-profile.json", category="metadata", bytes=len(e.canonical(b.payload()))),
        dict(path="qualification-reserves", category="metadata", bytes=16384+8192+8192+8192+8192+64)]
    projected = e.publication.extend(store.ledger(), extra)
    setup_caps = binding["real_setup_reserves"].values()
    projected = e.publication.extend(projected, [dict(path="future-setup-and-temporary", category="metadata",
        bytes=sum(setup_caps)+max(setup_caps))])
    complete = full_projection(projected, binding["publication_plan"], binding["real_future"])
    local = store.budget(extra[:2]+[dict(path="fixtures-plus-publication", category="metadata", bytes=16384+8192+64)])
    e.require(not local["violations"], "PROFILE_QUALIFICATION_BUDGET", local)
    store.publish_profile()
    store._write(OUT/"preregistration.json", raw, "metadata")
    print(json.dumps(dict(status="BOUND_NOT_RUN", tests=len(tests), qualification=local,
        complete_run_upper=complete, preregistration=entry.identity(OUT/"preregistration.json"))))


def run(sha):
    binding = entry.bound_json(OUT/"preregistration.json", sha)
    for name, expected in binding["inventory"].items():
        e.require(entry.identity(ROOT/name) == expected, "PROFILE_SOURCE_CHANGED", name)
    store = e.Store(OUT, refs(binding), future=binding["future"], budget_profile=b.payload())
    store.verify_budget_profile()
    before = store.budget([dict(path="fixtures-plus-publication", category="metadata", bytes=16384+8192+64)])
    e.require(not before["violations"], "PROFILE_PRESTART_BUDGET", before)
    store._write(OUT/"test.claim", b"exactly one sixteen-case administrative call", "metadata")
    env = dict(os.environ, MEDIA_BUDGET_QUAL_OUT=str(OUT), PYTHONDONTWRITEBYTECODE="1")
    with (OUT/"stdout.log").open("xb") as stdout, (OUT/"stderr.log").open("xb") as stderr:
        child = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_media_checkpoint_budget_profile", "-v"],
            cwd=ROOT, env=env, stdout=stdout, stderr=stderr, timeout=120)
    unchanged = all(entry.identity(ROOT/n) == v for n, v in binding["inventory"].items())
    reached = "Ran 16 tests" in (OUT/"stderr.log").read_text()
    current = store.budget()
    result = dict(version=VERSION, status="QUALIFIED" if child.returncode == 0 and reached and unchanged
        and not current["violations"] else "NOT_QUALIFIED", test_calls=1, tests_run=16 if reached else None,
        exit_code=child.returncode, inventory_digest=e.c.b.digest(binding["inventory"]), hashes_unchanged=unchanged,
        preregistration_sha256=sha, budget_profile_digest=b.digest(), payload_calls=0, gates=False,
        scope=binding["scope"])
    store._write(OUT/"result.json", e.canonical(result), "metadata", emergency=bool(current["violations"]))
    report = ("# Privates Checkpoint-Belegbudget\n\n"
        f"**{result['status']}**, {result['tests_run']} Prüfgruppen, genau ein Aufruf.\n"
        "Profil CHECKPOINT_COMPARISON_24M_V1: Gesamt 25.165.824, Metadaten 3.145.728, "
        "Quellen 524.288, gemeinsame Zusatzhülle 786.432 und Verifikation 262.144 Byte.\n\n"
        "Historische Defaults, Einzelbeleggrenzen, 4.096-Byte-Fehlerform und 8.192-Byte-Fehlerreserve "
        "bleiben unverändert. Der neue private Publikationsweg hält zusätzlich die aus den historischen "
        "Zweikopienprüfungen abgeleiteten Einzelobergrenzen fest. Kein größerer Decoder-/RAM-/Memoryumfang.\n\n"
        "Die Profilbindung wird vor der unabhängigen Verifikation geprüft und jeder neuen "
        "Publikationshülle zugeordnet. Gleichstand, Überschreitung, lokale Klassen bei globalem Überlauf, "
        "gemeinsame Reserven, historische Bytes, falsche Profile und Fehlerabschluss sind Gegenstand "
        "der fokussierten Prüfungen; vollständiges Ergebnis in stderr.log.\n\n"
        "Quellen, gesamter Katalog und Reserven sind in preregistration.json gebunden. "
        "Das frühere NICHT_PASSEND bleibt als Befund unter den alten Grenzen erhalten. "
        "Die neue Oberhülle ist eine Reservierung, keine Behauptung tatsächlicher 17,8 MB Nutzung. "
        "Keine Wahrnehmungs- oder Restoreversuche wiederholt. Kein Medienlauf. Gates False.\n")
    store._write(OUT/"REPORT.md", report.encode("utf-8"), "metadata", emergency=bool(current["violations"]))
    value = dict(preflight=before["charged"], physical={}, charged={}, limits=dict(b.LIMITS))
    for _ in range(12):
        raw = e.canonical(value)
        total = store.budget([dict(path="balance.json", category="metadata", bytes=len(raw))])
        updated = dict(value, physical=total["occupied"], charged=total["charged"], violations=total["violations"])
        if e.canonical(updated) == raw:
            break
        value = updated
    else:
        raise RuntimeError("PROFILE_BALANCE_SIZE")
    store._write(OUT/"balance.json", raw, "metadata", emergency=bool(current["violations"]))
    print(json.dumps(dict(result=result, budget=store.budget(), report=entry.identity(OUT/"REPORT.md"))))


def prepare_real():
    result = json.loads((OUT/"result.json").read_bytes())
    e.require(result["status"] == "QUALIFIED", "PROFILE_NOT_QUALIFIED")
    q = entry.bound_json(OUT/"preregistration.json", result["preregistration_sha256"])
    for name, expected in q["inventory"].items():
        e.require(entry.identity(ROOT/name) == expected, "PROFILE_SOURCE_CHANGED", name)
    run_id = "media-restart-real-20260913-02"
    setup, output = ROOT/"reports"/(run_id+"-binding"), ROOT/"reports"/run_id
    e.require(not setup.exists() and not output.exists(), "REAL_BINDING_USED")
    manifest = entry.c.p.build(run_id, entry.c.p.Source(str(entry.a.SOURCE), entry.a.SHA256, entry.a.SIZE),
        result["inventory_digest"], mode=entry.c.p.FULL_VERSION)
    sources = [row for row in refs(q) if row["category"] == "sources"]
    external = q["proofs"]+[reference(path) for path in sorted(OUT.rglob("*")) if path.is_file()]
    setup.mkdir()
    store = e.Store(setup, sources+external, budget_profile=b.payload())
    store.publish_profile()
    note = ("# Vorbereitet, nicht autorisiert\n\n"
        f"{run_id}: unveränderte Quelle; Referenz bis EOF, Suspend19, einmal Restore20.\n"
        "Neues privates Belegbudget, keine Änderung an Wahrnehmung oder Memory. "
        "authorization-template.json enthält authorized=false und startet keinen Lauf. "
        "Ein neuer ausdrücklicher Einmallaufentscheid ist erforderlich.\n")
    store._write(setup/"PLAN.md", note.encode("utf-8"), "metadata")
    external += [reference(setup/"budget-profile.json"), reference(setup/"PLAN.md")]
    data = dict(version=entry.VERSION, output="reports/"+run_id, budget_profile=b.payload(), limits=dict(b.LIMITS),
        stages=list(entry.STAGES), manifest=asdict(manifest), future=q["real_future"],
        publication_plan=q["publication_plan"], external=external,
        inventory_binding=dict(path=str((OUT/"preregistration.json").relative_to(ROOT)), sha256=result["preregistration_sha256"]),
        qualification=dict(path=str((OUT/"result.json").relative_to(ROOT)), sha256=entry.identity(OUT/"result.json")["sha256"]))
    budget = dict(status="PREPARING")
    for _ in range(16):
        budget_raw = e.canonical(budget)
        data["external"] = external+[dict(path=str(setup/"budget.json"), category="metadata",
            bytes=len(budget_raw), sha256=e.sha(budget_raw))]
        raw = e.canonical(data)
        auth = e.canonical(dict(version=entry.VERSION, authorized=False, single_use=True,
            run_id=run_id, binding_sha256=e.sha(raw)))
        additions = [dict(path=str(setup/name), category="metadata", bytes=len(body)) for name, body in
            (("budget.json", budget_raw), ("binding.json", raw), ("authorization-template.json", auth))]
        prospective = e.publication.extend(store.ledger(), additions)
        updated = full_projection(prospective, data["publication_plan"], data["future"])
        updated.update(authorization=False, output_absent=True, binding_bytes=len(raw), authorization_bytes=len(auth),
                       active_totals=prospective["totals"], profile_digest=b.digest())
        if e.canonical(updated) == budget_raw:
            break
        budget = updated
    else:
        raise RuntimeError("REAL_BINDING_SIZE_NOT_FIXED")
    for name, body in (("budget.json", budget_raw), ("binding.json", raw), ("authorization-template.json", auth)):
        key = {"budget.json": "budget", "binding.json": "binding", "authorization-template.json": "authorization_template"}[name]
        e.require(len(body) <= q["real_setup_reserves"][key], "REAL_SETUP_ITEM_RESERVE", dict(item=name, bytes=len(body)))
        store._write(setup/name, body, "metadata")
    print(json.dumps(dict(status="BOUND_NOT_AUTHORIZED", run_id=run_id, output_absent=not output.exists(),
        binding=entry.identity(setup/"binding.json"), authorization_template=entry.identity(setup/"authorization-template.json"),
        budget=updated, payload_calls=0, gates=False)))


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif len(sys.argv) == 3 and sys.argv[1] == "run":
        run(sys.argv[2])
    elif sys.argv[1:] == ["prepare-real"]:
        prepare_real()
    else:
        raise SystemExit("prepare | run <sha256> | prepare-real")
