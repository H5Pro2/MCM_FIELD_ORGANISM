"""Bind and run only the corrected closure controls once."""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys

from reports import run_selected_media_restart_once as entry
from tools import _media_restart_evidence as e

ROOT = entry.ROOT
OUT = ROOT/"reports/media-failure-form-qualification-20260913-01"
PREVIOUS = ROOT/"reports/media-publication-plan-qualification-20260913-01"
OWN = ("tests/test_media_failure_form.py", "reports/qualify_media_failure_form_once.py")
ARCHIVE_RUNNERS = ("reports/qualify_media_publication_plan_once.py",
    "reports/qualify_media_restart_admission_once.py", "reports/qualify_media_restart_measured_once.py",
    "reports/qualify_media_restart_once.py")
VERSION = "media.failure-form-qualification.v1"
FIXTURE_LIMIT = 16384


def ref(path):
    return dict(path=str(path), category="metadata", **entry.identity(path))


def inherited():
    previous = json.loads((PREVIOUS/"preregistration.json").read_bytes())
    base = entry.bound_json(previous["parent"]["path"], previous["parent"]["sha256"])
    inventory = {**base["inventory"], **previous["inventory_changes"]}
    for name, expected in inventory.items():
        e.require(entry.identity(ROOT/name) == expected, "FOCUSED_INHERITED_CHANGED", name)
    return previous, inventory


def dependencies(binding):
    _, old = inherited()
    inventory = {**old, **binding["new_sources"]}
    e.require(e.c.b.digest(inventory) == binding["inventory_digest"], "FOCUSED_INVENTORY")
    for name, expected in inventory.items():
        e.require(entry.identity(ROOT/name) == expected, "FOCUSED_SOURCE_CHANGED", name)
    sources = [dict(path=str(ROOT/name), category="sources", **inventory[name])
               for name in binding["charged_sources"]]
    return inventory, sources+binding["proofs"]


def prepare():
    e.require(not OUT.exists(), "FOCUSED_OUTPUT_USED")
    previous, inventory = inherited()
    new = {name: entry.identity(ROOT/name) for name in OWN}
    inventory.update(new)
    paths = [PREVIOUS/name for name in ("preregistration.json", "result.json", "stderr.log")]
    paths += [Path(previous["parent"]["path"]),
        ROOT/"reports/MEDIA_RESTART_DRAIN_METADATA_CASE_20260913.json",
        ROOT/"reports/media-restart-real-20260913-01/reference/failure.json"]
    tests = [n.name for n in ast.walk(ast.parse((ROOT/OWN[0]).read_text()))
             if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    e.require(len(tests) == 4, "FOCUSED_TEST_COUNT")
    future = [dict(name="logs", paths=["stdout.log", "stderr.log"], limit=8192, closed_by="result.json"),
              dict(name="closure", paths=["result.json", "REPORT.md", "balance.json"], limit=8192, closed_by="balance.json")]
    binding = dict(version=VERSION, previous=ref(PREVIOUS/"preregistration.json"),
        new_sources=new, inventory_digest=e.c.b.digest(inventory),
        charged_sources=sorted((set(previous["charged_sources"])-set(ARCHIVE_RUNNERS)) | set(OWN)),
        proofs=[ref(path) for path in paths], tests=tests, test_calls=1, future=future, limits=e.LIMITS,
        fixture_limit=FIXTURE_LIMIT,
        fixture_derivation="Three final administrative failures <=4096 each. During third publication one additional temporary copy <=4096: peak 16384. Observations <=512 only after publication: final <=12800. No other fixture contents, no native state.",
        publication_reserve=8192,
        publication_derivation="Additional simultaneous closure/report/balance publication allowance; not a larger local closure limit. Log and final closure groups each remain 8192. Protected primary copies remain 8192.",
        classification=dict(archive_only_runners=ARCHIVE_RUNNERS,
            explanation="Prospective scope of this focused qualification only: these historical restart test launchers are neither imported nor executed nor copied. Their content remains available and hash-checked in the inherited inventory. Historical test code, productive sources and all new active files remain fully charged. This is not a new media-run dependency classification.",
            metadata="All inputs actually resolved by this focused proof: previous preregistration/result/log, base inventory, saved administrative case and original failure. Older proof references inside historical documents are provenance, not replayed qualification prerequisites."),
        continuing_coverage="The first eleven tests are not repeated. All their test bodies, helpers and productive dependencies retain their bound hashes. Only a new focused test file supplies the corrected nested fixture and independent literal expected schema. Historical overall NOT_QUALIFIED is unchanged.",
        scope="Administrative closure only. No product changes, no media authorization, no proof of full success envelope.")
    _, external = dependencies(binding)
    OUT.mkdir()
    store = e.Store(OUT, external, future=future)
    raw = e.canonical(binding)
    prospective = store.budget([dict(path="preregistration.json", category="metadata", bytes=len(raw)),
        dict(path="fixtures-maximum", category="metadata", bytes=FIXTURE_LIMIT),
        dict(path="publication-extra", category="metadata", bytes=8192),
        dict(path="test.claim", category="metadata", bytes=64)])
    publication = store.budget([dict(path="preregistration.json", category="metadata", bytes=len(raw)),
        dict(path="preregistration.json.pending", category="metadata", bytes=len(raw))])
    print(json.dumps(dict(status="PRESTART_BLOCKED" if prospective["violations"] or publication["violations"] else "BOUND_NOT_RUN",
        calls=0, prospective=prospective, publication=publication, preregistration_bytes=len(raw))))
    if prospective["violations"] or publication["violations"]:
        return
    store._write(OUT/"preregistration.json", raw, "metadata")
    print(json.dumps(dict(preregistration=entry.identity(OUT/"preregistration.json"))))


def run(sha):
    binding = entry.bound_json(OUT/"preregistration.json", sha)
    inventory, external = dependencies(binding)
    store = e.Store(OUT, external, future=binding["future"])
    before = store.budget([dict(path="fixtures-and-publication", category="metadata", bytes=FIXTURE_LIMIT+8192),
                           dict(path="test.claim", category="metadata", bytes=64)])
    e.require(not before["violations"], "FOCUSED_PREFLIGHT", before)
    store._write(OUT/"test.claim", b"exactly one focused four-test call; no media", "metadata")
    env = dict(os.environ, MEDIA_FAILURE_FORM_OUT=str(OUT), PYTHONDONTWRITEBYTECODE="1")
    with (OUT/"stdout.log").open("xb") as stdout, (OUT/"stderr.log").open("xb") as stderr:
        child = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_media_failure_form", "-v"],
            cwd=ROOT, env=env, stdout=stdout, stderr=stderr, timeout=120)
    unchanged = all(entry.identity(ROOT/n) == v for n, v in inventory.items())
    reached = "Ran 4 tests" in (OUT/"stderr.log").read_text()
    sizes = [p.stat().st_size for p in OUT.glob("test_*/failure.json")]
    current = store.budget()
    result = dict(version=VERSION, status="QUALIFIED" if child.returncode == 0 and reached and unchanged
        and not current["violations"] else "NOT_QUALIFIED", test_calls=1, tests_run=4 if reached else None,
        exit_code=child.returncode, inventory_digest=binding["inventory_digest"], hashes_unchanged=unchanged,
        preregistration_sha256=sha, failure_bytes=sizes, failure_limit=4096,
        gates=False, payload_calls=0, product_changes=False, media_success_envelope="NOT_ESTABLISHED")
    store._write(OUT/"result.json", e.canonical(result), "metadata", emergency=bool(current["violations"]))
    report = ("# Fokussierte Fehlerformprüfung\n\n"
        f"**{result['status']}**, genau ein Aufruf mit {result['tests_run']} neuen Prüfgruppen.\n"
        f"Vollständige publizierte Fehlerformen: {sizes} Byte; Einzelgrenze 4.096 Byte.\n\n"
        "Die neuen Details stehen ausschließlich in failure.details. Die erwartete Hülle wird unabhängig "
        "durch literale Schlüsselmengen geprüft, einschließlich Gegenkontrolle zur früheren Doppelhülle. "
        "Primärfehler, Phase, Fortschritt, Ressourcen und sämtliche neuen Budgetdetails bleiben erhalten. "
        "Prüfungen und vollständige Tracebacks stehen in stderr.log; gemessene Einzelwerte in observations.json.\n\n"
        "## Zusammengeführte Prüfdeckung\n"
        "Die elf bestandenen Prüfungen des Vorgängers wurden nicht wiederholt. Ihre Quelldateien und "
        "sämtliche produktiven Abhängigkeiten sind unverändert hashgeprüft. Die vier neuen Prüfungen "
        "betreffen Fehlerform/Größe/Publikation/Primärerhalt, wiederholten Abschluss, Ablehnung eines "
        "zweiten Pfads und unabhängige Strukturerwartung. Kein neuer vollständiger Zwölf-Test-Lauf; "
        "der historische 11/12-Befund bleibt NOT_QUALIFIED.\n\n"
        "## Bilanz und Grenzen\n"
        "Die vollständigen aktiven Abhängigkeiten und die ausdrücklich abgegrenzte Archivrolle des "
        "vier früheren Teststarter stehen in preregistration.json. Sie bleiben verfügbar und hashgebunden, "
        "werden aber nicht erneut ausgeführt. Keine übertragene Medien-Laufbilanz. Alle lokal erzeugten "
        "Fehlerdateien werden physisch gezählt; weder Kompression noch neue Referenzmechanik. "
        "Die Istbilanz enthält diese Datei und balance.json.\n\n"
        "Produktcode und Grenzen unverändert. Keine Payload-, Decoder-, Rezeptor-, Memory- oder "
        "Medienausführung. Gates False. Selbst bei Bestehen ist nur die administrative Fehlerform "
        "abgesichert: Die vollständige Medien-Erfolgshülle bleibt NOT_ESTABLISHED. "
        "Der historische DRAIN-Fall überschreitet weiterhin um 3.269 Byte; keine neue Freigabe.\n")
    store._write(OUT/"REPORT.md", report.encode("utf-8"), "metadata", emergency=bool(current["violations"]))
    balance = dict(preflight=before["charged"], physical={}, charged={}, limits=e.LIMITS, violations=[])
    for _ in range(12):
        raw = e.canonical(balance)
        projected = store.budget([dict(path="balance.json", category="metadata", bytes=len(raw))])
        updated = dict(balance, physical=projected["occupied"], charged=projected["charged"], violations=projected["violations"])
        if e.canonical(updated) == raw:
            break
        balance = updated
    else:
        raise RuntimeError("FOCUSED_BALANCE_SIZE")
    store._write(OUT/"balance.json", raw, "metadata", emergency=bool(current["violations"]))
    print(json.dumps(dict(result=result, budget=store.budget(), report=entry.identity(OUT/"REPORT.md"))))


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif len(sys.argv) == 3 and sys.argv[1] == "run":
        run(sys.argv[2])
    else:
        raise SystemExit("prepare | run <preregistration-sha256>")
