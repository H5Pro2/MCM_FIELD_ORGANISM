"""One preregistered neutral replay call and a separately unapproved binding."""
import ast
from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import sys

from reports import run_selected_media_restart_once as entry
from reports.qualify_media_checkpoint_budget_profile_once import full_projection
from tools import _media_restart_evidence as e
from tools import _media_checkpoint_budget_profile as profile

ROOT = entry.ROOT
OUT = ROOT/"reports/media-replay-sections-qualification-20260913-01"
OLD = ROOT/"reports/media-restart-real-20260913-02-binding/binding.json"
OWN = ("tools/_media_replay_protocol.py", "tools/_media_restart_work.py",
       "tools/_s2oe_decoder_worker.py", "tools/_media_restart_checkpoint.py",
       "tools/_media_restart_player.py", "tools/_media_publication_plan.py",
       "reports/run_selected_media_restart_once.py", "tests/media_replay_neutral.py",
       "tests/test_media_replay_sections.py", "reports/qualify_media_replay_sections_once.py")
VERSION = "media.replay-sections-qualification.v1"
PROTOCOL = dict(version=entry.w.replay.VERSION, request_seconds=30.0,
                total_seconds=600.0, max_requests=20, max_windows_per_request=1)


def reference(path, category="metadata"):
    return dict(path=str(path.resolve()), category=category, **entry.identity(path))


def refs(q):
    return [dict(path=str(ROOT/n), category="sources", **q["inventory"][n])
            for n in q["charged_sources"]]+q["external"]


def make_plan(old):
    by_role = {p["id"]: p for p in old["positions"]}
    positions = []
    for role, (category, count) in e.publication.full_layout(profile.digest(), True).items():
        positions.append(dict(by_role[role]) if role in by_role else
            dict(id=role, category=category, count=count, lower=0, upper=4096))
    return dict(version=e.publication.VERSION, scope="FULL_REPLAY_RESTART",
                budget_profile_digest=profile.digest(), positions=positions)


def prepare():
    e.require(not OUT.exists(), "REPLAY_QUALIFICATION_USED")
    old = json.loads(OLD.read_bytes())
    parent = entry.bound_json(ROOT/old["inventory_binding"]["path"], old["inventory_binding"]["sha256"])
    inventory = dict(parent["inventory"])
    for n, expected in inventory.items():
        if n not in OWN:
            e.require(entry.identity(ROOT/n) == expected, "REPLAY_UNRELATED_SOURCE_CHANGED", n)
    inventory.update({n: entry.identity(ROOT/n) for n in OWN})
    charged = sorted(set(parent["charged_sources"]) | set(OWN))
    tests = [n.name for n in ast.walk(ast.parse((ROOT/OWN[-2]).read_text()))
             if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    e.require(len(tests) == 19, "REPLAY_TEST_INVENTORY")
    source = ROOT/"sources/media-restart-neutral/replay-sections-20260913-01.bin"
    e.require(not source.exists(), "NEUTRAL_INPUT_USED")
    source.parent.mkdir(exist_ok=True)
    with source.open("xb") as stream:
        stream.write(bytes(range(256))*32)
    ident = entry.identity(source)
    manifest = entry.c.p.build("replay-neutral-20260913-01",
        entry.c.p.Source(str(source), ident["sha256"], ident["bytes"]),
        entry.c.b.digest(inventory), mode=entry.c.p.FULL_VERSION)
    external = list(old["external"])+[reference(OLD), reference(source, "sources")]
    q = dict(version=VERSION, budget_profile=profile.payload(), replay_protocol=PROTOCOL,
        inventory=inventory, charged_sources=charged, external=external, tests=tests, test_calls=1,
        manifest=asdict(manifest), publication_plan=make_plan(old["publication_plan"]),
        native_future=old["future"], real_future=old["future"],
        future=[dict(name="logs", paths=["stdout.log", "stderr.log", "suspend19.stdout", "suspend19.stderr",
                                         "restore20.stdout", "restore20.stderr"], limit=8192, closed_by="result.json"),
                dict(name="closure", paths=["result.json", "REPORT.md", "balance.json"], limit=8192, closed_by="balance.json")],
        reserves=dict(test_claim=128, administrative_fixtures=16384, logs=8192, closure=8192,
                      primary_failure=8192, setup_with_temporary=393216),
        derivation="Full reference/suspend19/restore20 publication upper catalog also covers the smaller neutral suspend19/restore20 pair. Twenty separate replay confirmations at 4096 bytes each plus each publication temporary; original individual bounds, failure reserves and native capacities unchanged. No successful-example sizing.",
        source_scope="Only new 8192-byte neutral file; synthetic codec frames and actual native runtime. No selected video.",
        repository_head="537109994cf777f8d36cda617aafe12226806c25")
    OUT.mkdir()
    store = e.Store(OUT, refs(q), future=q["future"], budget_profile=q["budget_profile"])
    raw = e.canonical(q)
    e.require(len(raw) <= 61440, "REPLAY_PREREGISTRATION_SIZE")
    extras = [dict(path="preregistration.json", category="metadata", bytes=len(raw)),
              dict(path="profile-and-prebalance-and-claim", category="metadata", bytes=8192),
              dict(path="qualification-and-setup-reserves", category="metadata", bytes=sum(q["reserves"].values()))]
    projected = e.publication.extend(store.ledger(), extras)
    pre = full_projection(projected, q["publication_plan"], q["native_future"])
    store.publish_profile()
    store._write(OUT/"preregistration.json", raw, "metadata")
    store._write(OUT/"prebalance.json", e.canonical(pre), "metadata")
    print(json.dumps(dict(status="BOUND_NOT_RUN", preregistration=entry.identity(OUT/"preregistration.json"), budget=pre)))


def run(sha):
    q = entry.bound_json(OUT/"preregistration.json", sha)
    for n, expected in q["inventory"].items():
        e.require(entry.identity(ROOT/n) == expected, "REPLAY_SOURCE_CHANGED", n)
    store = e.Store(OUT, refs(q), future=q["future"], budget_profile=q["budget_profile"])
    projected = e.publication.extend(store.ledger(), [dict(path="all-reserves", category="metadata",
                                                          bytes=sum(q["reserves"].values()))])
    full_projection(projected, q["publication_plan"], q["native_future"])
    store._write(OUT/"test.claim", b"one nineteen-group replay qualification", "metadata")
    env = dict(os.environ, MEDIA_REPLAY_QUAL_OUT=str(OUT), PYTHONDONTWRITEBYTECODE="1")
    with (OUT/"stdout.log").open("xb") as out, (OUT/"stderr.log").open("xb") as err:
        child = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_media_replay_sections", "-v"],
                               cwd=ROOT, env=env, stdout=out, stderr=err, timeout=600)
    unchanged = all(entry.identity(ROOT/n) == v for n, v in q["inventory"].items())
    reached = "Ran 19 tests" in (OUT/"stderr.log").read_text()
    status = "QUALIFIED" if child.returncode == 0 and reached and unchanged and not store.budget()["violations"] else "NOT_QUALIFIED"
    result = dict(version=VERSION, status=status, test_calls=1, tests_run=19 if reached else None,
        exit_code=child.returncode, hashes_unchanged=unchanged, inventory_digest=entry.c.b.digest(q["inventory"]),
        preregistration_sha256=sha, budget_profile_digest=profile.digest(), replay_protocol=PROTOCOL,
        real_media_calls=0, gates=False)
    store._write(OUT/"result.json", e.canonical(result), "metadata", emergency=bool(store.budget()["violations"]))
    note = (f"# Fensterweiser Replayanschluss\n\n{status}, {result['tests_run']} Prüfgruppen, genau ein Aufruf.\n\n"
        "Ein Replayfenster je Anfrage, 30 Sekunden je Anfrage, zusätzlich 600 Sekunden für höchstens 20 Anfragen einschließlich Zielfenster. Quellenprüfung zählt mit; keine Fristverlängerung durch Phasenmeldungen. EOF und close behalten eigene Grenzen.\n\n"
        "Quellen-/Zeit-/Sequenzbindungen, fehlende/verdoppelte/rückläufige Bestätigungen, kumulative Zähler, Grenzfälle und Abbruch innerhalb/zwischen Abschnitten neutral geprüft. Native Spätwiederaufnahme nutzt synthetische Codecframes und eine neue neutrale Datei, nicht das reale Video. Ihr tatsächlich erreichter Status und Replay-ohne-Memory-Kontrollen stehen in native/*-process.json und den vollständigen Logs. Keine historische Passzahl übernommen.\n\n"
        "Vollständige Erfolgshülle konservativ vorgebunden, neue Bestätigungen und temporäre Publikationen mitgezählt. Fehler nach letzter Bestätigung lassen unbestätigten Verbrauch ausdrücklich unbekannt. 30/600 Sekunden sind Abbruchgrenzen, keine Garantie realer Laufzeit. Historische Befunde unverändert; kein realer Lauf. Gates False.\n")
    store._write(OUT/"REPORT.md", note.encode("utf-8"), "metadata", emergency=bool(store.budget()["violations"]))
    value = {}
    for _ in range(16):
        raw = e.canonical(value)
        updated = store.budget([dict(path="balance.json", category="metadata", bytes=len(raw))])
        if e.canonical(updated) == raw:
            break
        value = updated
    else:
        raise RuntimeError("REPLAY_BALANCE_SIZE")
    store._write(OUT/"balance.json", raw, "metadata", emergency=bool(store.budget()["violations"]))
    print(json.dumps(dict(result=result, budget=store.budget())))


def prepare_real():
    result = json.loads((OUT/"result.json").read_bytes())
    e.require(result["status"] == "QUALIFIED", "REPLAY_NOT_QUALIFIED")
    q = entry.bound_json(OUT/"preregistration.json", result["preregistration_sha256"])
    for name, expected in q["inventory"].items():
        e.require(entry.identity(ROOT/name) == expected, "REPLAY_SOURCE_CHANGED", name)
    run_id = "media-restart-real-20260913-03"
    setup, output = ROOT/"reports"/(run_id+"-binding"), ROOT/"reports"/run_id
    e.require(not setup.exists() and not output.exists(), "REPLAY_REAL_ID_USED")
    old = json.loads(OLD.read_bytes())
    manifest = entry.c.p.build(run_id, entry.c.p.Source(str(entry.a.SOURCE), entry.a.SHA256, entry.a.SIZE),
                              result["inventory_digest"], mode=entry.c.p.FULL_VERSION)
    ledger = e.Store(OUT, refs(q), budget_profile=q["budget_profile"]).ledger()
    sources = [r for r in refs(q) if r["category"] == "sources"]
    external = [r for r in refs(q) if r["category"] != "sources"]
    external += [reference(OUT/r["path"], r["category"]) for r in ledger["files"] if not Path(r["path"]).is_absolute()]
    # The neutral source is an explicit qualification dependency, not a real input.
    external += [r for r in sources if Path(r["path"]).suffix not in (".py", ".html")]
    charged = [r for r in sources if Path(r["path"]).suffix in (".py", ".html")]
    setup.mkdir()
    store = e.Store(setup, charged+external, budget_profile=q["budget_profile"])
    store.publish_profile()
    note = "# Nicht autorisierte Laufbindung\n\nUnveränderte reale Quelle und 20-Ereignis-Folge. Referenz, Suspend19, einmal Restore20. Fensterweiser Replay mit 30 Sekunden je Anfrage und 600 Sekunden Gesamtfrist für höchstens 20 Anfragen. Neue Einmallauffreigabe erforderlich.\n"
    store._write(setup/"PLAN.md", note.encode("utf-8"), "metadata")
    external += [reference(setup/"budget-profile.json"), reference(setup/"PLAN.md")]
    catalogs = []
    e.require(len(external) <= 400, "REPLAY_REFERENCE_CATALOG_COUNT")
    # Available, digest-bound catalogs, not digest-only omissions of fixture files.
    for start in range(0, len(external), 100):
        path = setup/("references-%02d.json" % (start//100))
        store._write(path, e.canonical(dict(references=external[start:start+100])), "metadata")
        catalogs.append(dict(path=str(path.relative_to(ROOT)), sha256=entry.identity(path)["sha256"]))
    data = dict(version=entry.VERSION, output="reports/"+run_id, limits=dict(profile.LIMITS),
        budget_profile=q["budget_profile"], replay_protocol=PROTOCOL, stages=list(entry.STAGES),
        manifest=asdict(manifest), publication_plan=q["publication_plan"], future=q["real_future"], reference_catalogs=catalogs,
        inventory_binding=dict(path=str((OUT/"preregistration.json").relative_to(ROOT)), sha256=result["preregistration_sha256"]),
        qualification=dict(path=str((OUT/"result.json").relative_to(ROOT)), sha256=entry.identity(OUT/"result.json")["sha256"]))
    budget = {}
    for _ in range(16):
        budget_raw = e.canonical(budget)
        data["external"] = [dict(path=str(setup/"budget.json"), category="metadata",
                                          bytes=len(budget_raw), sha256=e.sha(budget_raw))]
        raw = e.canonical(data)
        auth = e.canonical(dict(version=entry.VERSION, authorized=False, single_use=True,
                               run_id=run_id, binding_sha256=e.sha(raw)))
        prospective = e.publication.extend(store.ledger(), [dict(path=str(setup/n), category="metadata", bytes=len(v))
            for n,v in (("budget.json",budget_raw),("binding.json",raw),("authorization-template.json",auth))])
        updated = full_projection(prospective, data["publication_plan"], data["future"])
        updated.update(authorized=False, output_absent=True, active_totals=prospective["totals"])
        if e.canonical(updated) == budget_raw:
            break
        budget = updated
    else:
        raise RuntimeError("REPLAY_REAL_BALANCE_SIZE")
    for name, body in (("budget.json",budget_raw),("binding.json",raw),("authorization-template.json",auth)):
        store._write(setup/name, body, "metadata")
    print(json.dumps(dict(status="BOUND_NOT_AUTHORIZED", binding=entry.identity(setup/"binding.json"), budget=updated)))


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif len(sys.argv) == 3 and sys.argv[1] == "run":
        run(sys.argv[2])
    elif sys.argv[1:] == ["prepare-real"]:
        prepare_real()
    else:
        raise SystemExit("Explicit prepare/run/prepare-real only")
