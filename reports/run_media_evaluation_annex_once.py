"""One neutral publication qualification, then one read-only-input annex."""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace as NS

from tools import _media_evaluation_annex as a

e, entry = a.e, a.entry
ROOT = entry.ROOT
Q = ROOT/"reports/media-evaluation-publication-qualification-20260919-01"
OUT = ROOT/"reports/media-restart-evaluation-annex-20260919-01"
HISTORY = ROOT/"reports/media-restart-real-20260913-03"
BINDING = ROOT/"reports/media-restart-real-20260913-03-binding/binding.json"
OWN = ("tools/_media_publication_plan.py", "tools/_media_evaluation_annex.py",
       "tests/test_media_evaluation_annex.py", "reports/run_media_evaluation_annex_once.py")
FUTURE = [dict(name="closure",paths=["result.json","REPORT.md","balance.json"],limit=8192,closed_by="balance.json")]


def ref(path,category="metadata"):
    return dict(path=str(path.resolve()),category=category,**entry.identity(path))


def classified(root):
    rows=[]
    for p in sorted(root.rglob("*")):
        if p.is_file():
            category=json.loads(p.read_bytes())["class"] if p.parent.name=="objects" else "metadata"
            rows.append(ref(p,category))
    return rows


def load_refs(q):
    rows=[]
    for r in q["catalogs"]:
        entry.w.require(entry.identity(r["path"])=={k:r[k] for k in ("bytes","sha256")},"ANNEX_CATALOG_HASH")
        rows+=json.loads(Path(r["path"]).read_bytes())["references"]
        rows.append(r)
    return rows


def prepare():
    entry.w.require(not Q.exists() and not OUT.exists(),"ANNEX_ID_USED")
    old=json.loads(BINDING.read_bytes())
    parent=entry.bound_json(ROOT/old["inventory_binding"]["path"],old["inventory_binding"]["sha256"])
    inventory=dict(parent["inventory"])
    for n,v in inventory.items():
        if n not in OWN: entry.w.require(entry.identity(ROOT/n)==v,"ANNEX_UNRELATED_SOURCE",n)
    inventory.update({n:entry.identity(ROOT/n) for n in OWN})
    rows=entry.reference_rows(old)+[ref(BINDING),ref(BINDING.parent/"authorization.json")]
    rows += [dict(path=str(ROOT/n),category="sources",**inventory[n])
             for n in sorted(set(parent["charged_sources"])|set(OWN))]
    history=classified(HISTORY)
    rows+=history
    unique={}
    for r in rows:
        key=str(Path(r["path"]).resolve())
        entry.w.require(key not in unique or unique[key]==r,"ANNEX_DUPLICATE_REFERENCE")
        unique[key]=r
    Q.mkdir()
    catalogs=[]
    rows=list(unique.values())
    for start in range(0,len(rows),90):
        path=Q/("references-%02d.json"%(start//90))
        raw=e.canonical(dict(references=rows[start:start+90]))
        entry.w.require(len(raw)<=61440,"ANNEX_CATALOG_SIZE")
        with path.open("xb") as f:f.write(raw)
        catalogs.append(ref(path))
    tests=[n.name for n in ast.walk(ast.parse((ROOT/OWN[2]).read_text()))
           if isinstance(n,ast.FunctionDef) and n.name.startswith("test_")]
    entry.w.require(len(tests)==8,"ANNEX_TEST_INVENTORY")
    q=dict(version=a.VERSION,inventory=inventory,catalogs=catalogs,tests=tests,test_calls=1,
        publication_plan=a.plan(),historical_run=str(HISTORY),historical_tree_digest=e.sha(e.canonical(history)),
        original_binding=ref(BINDING),stored_verification=ref(HISTORY/"restore20-verification.json"),
        historical_status="NOT_EVALUABLE",evaluation_id=OUT.name,
        reserves=dict(qualification_fixtures=131072,logs=8192,qualification_closure=8192,
                      annex_publications=262144,preregistration=61440,failure=8192),
        scope="Administrative publication only. Real post-evaluation consumes existing verified evidence; no second verification, media or state calculation.")
    store=e.Store(Q,rows,future=FUTURE,budget_profile=a.profile.payload())
    raw=e.canonical(q)
    entry.w.require(len(raw)<=61440,"ANNEX_PREREGISTRATION_SIZE")
    pre=store.budget([dict(path="all-future",category="metadata",bytes=sum(q["reserves"].values()))])
    entry.w.require(not pre["violations"],"ANNEX_PRESTART_BUDGET",pre)
    store.publish_profile()
    store._write(Q/"preregistration.json",raw,"metadata")
    store._write(Q/"prebalance.json",e.canonical(pre),"metadata")
    print(json.dumps(dict(status="BOUND_NOT_RUN",preregistration=entry.identity(Q/"preregistration.json"),budget=pre)))


def finish(store,result,note):
    store._write(store.root/"result.json",e.canonical(result),"metadata")
    store._write(store.root/"REPORT.md",note.encode("utf-8"),"metadata")
    value={}
    for _ in range(16):
        raw=e.canonical(value)
        new=store.budget([dict(path="balance.json",category="metadata",bytes=len(raw))])
        if e.canonical(new)==raw:break
        value=new
    else:raise RuntimeError("ANNEX_BALANCE_SIZE")
    store._write(store.root/"balance.json",raw,"metadata")
    print(json.dumps(dict(result=result,budget=store.budget())))


def qualify(sha):
    q=entry.bound_json(Q/"preregistration.json",sha)
    for n,v in q["inventory"].items():entry.w.require(entry.identity(ROOT/n)==v,"ANNEX_CODE_CHANGED")
    # Catalogs are local files and must not be charged a second time as externals.
    external=[r for r in load_refs(q) if not Path(r["path"]).is_relative_to(Q)]
    store=e.Store(Q,external,future=FUTURE,budget_profile=a.profile.payload())
    pre=store.budget([dict(path="all-future",category="metadata",bytes=sum(q["reserves"].values()))])
    entry.w.require(not pre["violations"],"ANNEX_PRESTART_BUDGET",pre)
    store._write(Q/"test.claim",b"one eight-test publication qualification","metadata")
    with (Q/"stdout.log").open("xb") as out,(Q/"stderr.log").open("xb") as err:
        child=subprocess.run([sys.executable,"-B","-m","unittest","tests.test_media_evaluation_annex","-v"],cwd=ROOT,
            env=dict(os.environ,MEDIA_ANNEX_QUAL_OUT=str(Q),PYTHONDONTWRITEBYTECODE="1"),stdout=out,stderr=err,timeout=120)
    unchanged=all(entry.identity(ROOT/n)==v for n,v in q["inventory"].items())
    reached="Ran 8 tests" in (Q/"stderr.log").read_text()
    result=dict(status="QUALIFIED" if child.returncode==0 and unchanged and reached else "NOT_QUALIFIED",
        test_calls=1,tests=8 if reached else None,exit_code=child.returncode,hashes_unchanged=unchanged,
        preregistration_sha256=sha,inventory_digest=entry.c.b.digest(q["inventory"]),gates=False)
    finish(store,result,f"# Administrative Auswertungspublikation\n\n{result['status']}: {result['tests']} Prüfgruppen, genau ein Aufruf.\n\n20 konkrete native Zeilenpositionen, ihr Metadatenindex und die vollständige Wurzel gebunden. Unbekannte Pfade, Größenüberschreitung, Mehrfachpublikation und unvollständige Zeilen abgewiesen. Positive und negative neutrale Auswertung publizierbar. Keine historische Testserie, Medienverarbeitung, Zustandsberechnung oder Gesamtverifikation.\n")


def evaluate():
    entry.w.require(not OUT.exists(),"ANNEX_ID_USED")
    qr=json.loads((Q/"result.json").read_bytes())
    entry.w.require(qr["status"]=="QUALIFIED","ANNEX_NOT_QUALIFIED")
    q=entry.bound_json(Q/"preregistration.json",qr["preregistration_sha256"])
    for n,v in q["inventory"].items():entry.w.require(entry.identity(ROOT/n)==v,"ANNEX_CODE_CHANGED")
    before=classified(HISTORY)
    entry.w.require(e.sha(e.canonical(before))==q["historical_tree_digest"],"ANNEX_HISTORY_CHANGED")
    external=[r for r in load_refs(q) if not Path(r["path"]).is_relative_to(Q)]+classified(Q)
    store=e.Store(OUT,external,future=FUTURE,budget_profile=a.profile.payload(),publication_plan=a.plan())
    store.preflight()
    store.publish_profile()
    old=json.loads(BINDING.read_bytes())
    historical=e.Store(HISTORY,budget_profile=old["budget_profile"])
    # This reads and integrity-resolves the saved verification, never runs it.
    proof=historical.read(HISTORY/"restore20-verification.json")
    origin=dict(version=a.VERSION,original_status="NOT_EVALUABLE",original_run=HISTORY.name,
        historical_tree_digest=q["historical_tree_digest"],original_binding=q["original_binding"],
        stored_verification=q["stored_verification"],saved_verification_digest=proof["verification_digest"],
        qualification=ref(Q/"result.json"),new_verification_calls=0,media_calls=0,state_calculations=0)
    store.publish(OUT/"origin.json",origin)
    accounts={}
    for arm in ("reference","restore20"):
        # Accounting is inline in the already bound record header. Do not decode core/states.
        header=json.loads((HISTORY/arm/"record.json").read_bytes())
        entry.w.require(header["budget_profile_digest"]==a.profile.digest(),"ANNEX_RECORD_PROFILE")
        accounts[arm]=header["value"]["accounting"]
    verdict=a.evaluate_once(store,NS(manifest_digest=old["manifest"]["manifest_digest"]),proof,accounts)
    entry.w.require(classified(HISTORY)==before,"ANNEX_HISTORY_CHANGED")
    result=dict(status="EVALUATION_ANNEX_COMPLETE",evaluation_status=verdict["status"],original_status="NOT_EVALUABLE",
        evaluation_calls=1,new_verification_calls=0,media_calls=0,state_calculations=0,historical_unchanged=True,gates=False)
    finish(store,result,"# Separater Auswertungsnachtrag\n\nUrsprünglicher Lauf media-restart-real-20260913-03 bleibt NOT_EVALUABLE.\n\nDie gespeicherte unabhängige Verifikation bestätigt die technische Wiederaufnahme: gleiche Kernzustände, alle 20 Zeilen, Medienauswahl und finaler Feldzustand; 20 Replaybestätigungen. Sie wurde nur gelesen und nicht wiederholt.\n\n"+f"Dieser einmalige getrennte Nachtrag ist EVALUATION_ANNEX_COMPLETE; unveränderter Auswerter: {verdict['status']}. Materialisierungszähler stimmen ebenfalls überein. Vollständige Herkunftsdigests in origin.json, alle Zeilen in evaluation.json. Keine historischen Dateien geändert, keine Medien- oder Zustandsberechnung.\n\nCheckpointzweig geschlossen. Begrenzte technische Wiederaufnahme derselben wiederverwendeten Datei; kein Nachweis von Objekterkennung, Erfahrungsnutzen oder allgemeiner Crash-Recovery. Gates False.\n")


if __name__=="__main__":
    if sys.argv[1:]==["prepare"]:prepare()
    elif len(sys.argv)==3 and sys.argv[1]=="qualify":qualify(sys.argv[2])
    elif sys.argv[1:]==["evaluate"]:evaluate()
    else:raise SystemExit("Explicit prepare, qualify or evaluate")
