"""One prebound administrative suite; no media authorization or processing."""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys

from reports import run_selected_media_restart_once as entry
from tools import _media_restart_evidence as e

ROOT = entry.ROOT
OUT = ROOT/"reports/media-publication-plan-qualification-20260913-01"
PARENT = ROOT/"reports/media-restart-admission-qualification-20260913-02"
OWN = ("tools/_media_publication_plan.py", "tools/_media_restart_evidence.py",
       "reports/run_selected_media_restart_once.py", "tests/test_media_publication_plan.py",
       "reports/qualify_media_publication_plan_once.py")
CASE = ROOT/"reports/MEDIA_RESTART_DRAIN_METADATA_CASE_20260913.json"
FAILURE = ROOT/"reports/media-restart-real-20260913-01/reference/failure.json"
VERSION = "media.publication-qualification.v1"
FIXTURES = 8192


def ref(path, category="metadata"):
    return dict(path=str(path), category=category, **entry.identity(path))


def resolve(binding):
    parent = binding["parent"]
    old = entry.bound_json(parent["path"], parent["sha256"])
    inventory = {**old["inventory"], **binding["inventory_changes"]}
    e.require(e.c.b.digest(inventory) == binding["inventory_digest"], "QUAL_INVENTORY_BINDING")
    for name, expected in inventory.items():
        e.require(entry.identity(ROOT/name) == expected, "QUAL_CODE_CHANGED", name)
    external = [dict(path=str(ROOT/name), category="sources", **inventory[name])
                for name in binding["charged_sources"]] + binding["proofs"]
    return inventory, external


def prepare():
    e.require(not OUT.exists(), "QUAL_OUTPUT_USED")
    old = json.loads((PARENT/"preregistration.json").read_bytes())
    for name, expected in old["inventory"].items():
        if name not in OWN:
            e.require(entry.identity(ROOT/name) == expected, "QUAL_INHERITED_CHANGED", name)
    changes = {name: entry.identity(ROOT/name) for name in OWN}
    inventory = {**old["inventory"], **changes}
    proofs = old["proofs"]+[ref(PARENT/name) for name in
        ("preregistration.json", "result.json", "stdout.log", "stderr.log", "REPORT.md", "balance.json", "test.claim")]
    proofs += [ref(CASE), ref(FAILURE)]
    tests = [node.name for node in ast.walk(ast.parse((ROOT/OWN[3]).read_text()))
             if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")]
    e.require(len(tests) == 12, "QUAL_TEST_INVENTORY")
    future = [dict(name="logs", paths=["stdout.log", "stderr.log"], limit=8192, closed_by="result.json"),
        dict(name="closure", paths=["result.json", "REPORT.md", "balance.json"], limit=8192, closed_by="balance.json")]
    classes = {}
    for category, count in e.publication.full_layout().values():
        classes[category] = classes.get(category, 0)+count
    binding = dict(version=VERSION, parent=ref(PARENT/"preregistration.json"),
        repository_head="537109994cf777f8d36cda617aafe12226806c25", dirty_tree=True,
        inventory_changes=changes, inventory_digest=e.c.b.digest(inventory),
        charged_sources=sorted(set(old["charged_sources"]) | set(OWN)), proofs=proofs,
        classification="Unchanged installed basis remains hash-bound, not copied. Every previously charged source and new source remains counted once. All referenced old proof contents are counted. No historical pass count is reused.",
        tests=tests, test_calls=1, future=future, limits=e.LIMITS, fixture_envelope=FIXTURES,
        fixture_derivation="One administrative shared roundtrip (four final objects/wrappers, each at most 1024); one full failure at most 4096. Observations replace unused roundtrip space: actual roundtrip fixed small values, at most 1024 total; observations at most 2048. Combined at most 7168, plus 1024 unused reserve. No native state fixtures.",
        diagnostic_policy="Keep complete stdout/stderr even on overrun; report violation without truncation or retry. Protected primary failure: two copies of 4096. Result/report/balance share 8192, logs share 8192.",
        full_success_layout=dict(version=e.publication.VERSION, source=OWN[0], roles=len(e.publication.full_layout()),
            object_count_by_class=classes, derivation="full_layout() in hash-bound source; all final instances and temporary copies, no assumed deduplication",
            upper_bytes=None, status="NOT_ESTABLISHED", reason="No justified upper sizes for all actual inner indices, wrappers and independent native outcomes. Unknown is rejected, never zero."),
        scope="Receptor-free administrative budget defense, not media feasibility. No state, decoder, receptor or payload calls. No main authorization.")
    _, external = resolve(binding)
    OUT.mkdir()
    store = e.Store(OUT, external, future=future)
    raw = e.canonical(binding)
    publication = e.publication.transaction(store.ledger(), [
        dict(path="preregistration.json.pending", category="metadata", bytes=len(raw)),
        dict(path="preregistration.json", category="metadata", bytes=len(raw))],
        store.future, store.future, e.FAILURE_BYTES)
    complete = store.budget([dict(path="preregistration.json", category="metadata", bytes=len(raw)),
        dict(path="all-fixtures", category="metadata", bytes=FIXTURES),
        dict(path="test.claim", category="metadata", bytes=64)])
    # Report all contributions before deciding whether the sole call may start.
    print(json.dumps(dict(status="PRESTART_BLOCKED" if complete["violations"] or publication["violations"] else "BOUND_NOT_RUN",
        test_calls=0, source_bytes=sum(x["bytes"] for x in external if x["category"] == "sources"),
        proof_bytes=sum(x["bytes"] for x in external if x["category"] == "metadata"),
        preregistration_bytes=len(raw), fixture_reserve=FIXTURES, claim_reserve=64,
        complete=complete, publication=publication)))
    if complete["violations"] or publication["violations"]:
        return
    store._write(OUT/"preregistration.json", raw, "metadata")
    print(json.dumps(dict(preregistration=entry.identity(OUT/"preregistration.json"))))


def run(sha):
    binding = entry.bound_json(OUT/"preregistration.json", sha)
    inventory, external = resolve(binding)
    store = e.Store(OUT, external, future=binding["future"])
    preflight = store.budget([dict(path="all-fixtures", category="metadata", bytes=FIXTURES),
                             dict(path="test.claim", category="metadata", bytes=64)])
    e.require(not preflight["violations"], "QUAL_PREFLIGHT_BUDGET", preflight)
    store._write(OUT/"test.claim", b"one twelve-group administrative call; no media", "metadata")
    env = dict(os.environ, MEDIA_PUBLICATION_QUAL_OUT=str(OUT), PYTHONDONTWRITEBYTECODE="1")
    with (OUT/"stdout.log").open("xb") as stdout, (OUT/"stderr.log").open("xb") as stderr:
        child = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_media_publication_plan", "-v"],
            cwd=ROOT, env=env, stdout=stdout, stderr=stderr, timeout=120)
    unchanged = all(entry.identity(ROOT/name) == expected for name, expected in inventory.items())
    log = (OUT/"stderr.log").read_text()
    reached = "Ran 12 tests" in log
    occupied = store.ledger()
    diagnostics = store.budget()
    fixture_bytes = sum(row["bytes"] for row in occupied["files"] if
        not Path(row["path"]).is_absolute() and row["path"] not in
        ("preregistration.json", "test.claim", "stdout.log", "stderr.log"))
    if fixture_bytes > FIXTURES:
        diagnostics["violations"].append("fixture_envelope")
    result = dict(version=VERSION, status="QUALIFIED" if child.returncode == 0 and reached and unchanged
        and not diagnostics["violations"] else "NOT_QUALIFIED", test_calls=1,
        tests_run=12 if reached else None, exit_code=child.returncode, hashes_unchanged=unchanged,
        inventory_digest=binding["inventory_digest"], preregistration_sha256=sha, gates=False,
        payload_calls=0, media_runs=0, feasibility="NOT_ESTABLISHED", violations=diagnostics["violations"],
        fixture_bytes=fixture_bytes, fixture_limit=FIXTURES)
    store._write(OUT/"result.json", e.canonical(result), "metadata", emergency=bool(diagnostics["violations"]))
    report = ("# Publikationsplan: administrative Qualifikation\n\n"
        f"Status: **{result['status']}**; genau ein Aufruf, {result['tests_run']} Prüfgruppen.\n"
        "Kein historischer Test wiederholt. Keine Payload-, Decoder-, Rezeptor-, Memory- oder Medienausführung.\n\n"
        "## Befund\n"
        "Prüfdetails stehen vollständig in stderr.log und observations.json; Quellen und Prüfbestand sind vorab gebunden.\n"
        "Der gespeicherte Fall wird mit 89.972 + 12.049 + 7.744 + 24.576 = 134.341 Byte gegen 131.072 geprüft.\n"
        "Grenzgleichheit, Überschreitung, fehlende Positionen, alternative Fehlerpfade und Primärreserve sind getrennte Kontrollen.\n\n"
        "## Erfolgshülle\n"
        f"Die vollständige Rollenstruktur umfasst {binding['full_success_layout']['roles']} Positionen: "
        f"{binding['full_success_layout']['object_count_by_class']}. Mengen sind obere Instanzzahlen, keine neuen Messwerte.\n"
        "Pro Position müssen finale Bytes und eine gleichzeitig bestehende temporäre Kopie gebunden werden. "
        "Log- und Abschlussreserven werden nur um vorhandene final publizierte Inhalte vermindert. "
        "Fehler vor, während und nach der Verlinkung sind Alternativen, keine addierten Laufabschlüsse. "
        "Eine vollständige obere Bytebilanz ist weiterhin nicht begründet; unbekannte Obergrenzen sperren den Start.\n\n"
        "## Tragfähigkeit und Einsparungen\n"
        "Bereits die historische Metadaten-Untergrenze überschreitet um 3.269 Byte. Neue Pflichtquellen, "
        "Plan- und Qualifikationsbindungen kommen hinzu. Keine behauptete Durchführbarkeit. "
        "Inhaltlich und kanonisch identische Objektdateien werden schon durch vollständigen Bytevergleich gemeinsam abgelegt. "
        "Die sechs bei DRAIN vorhandenen Verwaltungsobjekte sind nicht identisch. Für neue Einsparungen "
        "liegt kein belegter Bytebetrag vor; Quellenklassifikation, Historie und Reserven werden nicht passend geändert.\n\n"
        "Historischer Lauf bleibt NOT_EVALUABLE. Keine neue Medienfreigabe. Gates False.\n")
    store._write(OUT/"REPORT.md", report.encode("utf-8"), "metadata", emergency=bool(diagnostics["violations"]))
    balance = dict(version=VERSION, before_closure=occupied["totals"], preflight=preflight["charged"],
                   limits=e.LIMITS, final_physical=None, final_charged=None, violations=None)
    # Account for the balance's own size without embedding its own ledger.
    for _ in range(12):
        raw = e.canonical(balance)
        final = store.ledger([dict(path="balance.json", category="metadata", bytes=len(raw))])
        charged = e.reservations.assess(final, store.future, e.FAILURE_RESERVE)
        updated = dict(balance, final_physical=final["totals"], final_charged=charged["charged"],
                       violations=charged["violations"])
        if e.canonical(updated) == raw:
            break
        balance = updated
    else:
        raise RuntimeError("BALANCE_SIZE_NOT_FIXED")
    store._write(OUT/"balance.json", raw, "metadata", emergency=bool(diagnostics["violations"]))
    print(json.dumps(dict(result=result, balance=store.budget(), report=entry.identity(OUT/"REPORT.md"))))


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif len(sys.argv) == 3 and sys.argv[1] == "run":
        run(sys.argv[2])
    else:
        raise SystemExit("prepare | run <preregistration-sha256>")
