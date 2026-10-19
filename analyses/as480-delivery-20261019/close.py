"""Technical delivery only: no projection, source construction or arm replay."""
import sys,time,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from experiments.as480 import entry
from experiments.as480.common import *

def main():
    start=time.monotonic();entry.install()
    append(PREP/'attempts.jsonl',dict(event='DELIVERY_CHECKS_BEGIN',sources=0,policy=0,receptor=0))
    full=read(PREP/'full-neutral-01/terminal.json');need(full['status']=='COMPLETE','FULL_NEUTRAL')
    request=read(PREP/'full-neutral-01/request.json');rt=entry.runtime()
    for key in ('python','executable','executable_sha256','numeric_threads','platform','numpy','dlls'):
        need(rt[key]==request['runtime'][key],'RUNTIME_LINEAGE:'+key)
    for key,value in request['runtime']['numpy_files'].items():need(rt['numpy_files'][key]==value,'NUMPY_BINARY_LINEAGE')
    need(bool(rt['numpy_external_libraries']),'NUMPY_LIBS_NOT_BOUND')
    changes=[n for n,h in request['files'].items() if sha(ROOT/n)!=h]
    need(changes==['experiments/as480/entry.py'],'QUALIFIED_LINEAGE')
    need(sha(PREP/'qualified-code/entry-full-neutral.py')==request['files']['experiments/as480/entry.py'],'QUALIFIED_ENTRY_SNAPSHOT')
    import difflib
    diff=''.join(difflib.unified_diff((PREP/'qualified-code/entry-full-neutral.py').read_text().splitlines(True),
        (ROOT/'experiments/as480/entry.py').read_text().splitlines(True),fromfile='qualified-entry',tofile='final-entry'))
    exclusive(PREP/'runtime-binding-extension.diff',diff.encode())
    exclusive(PREP/'runtime-binding-extension.json',dict(changed_files=changes,reason='Add NumPy Python source and adjacent numpy.libs binary hashes to admission binding; no material/engine/oracle change',
        prior_runtime=request['runtime'],final_runtime=rt,full_neutral_repeated=False,original_numpy_binary_hashes_equal=True,
        limitation='Additional Python/library hashes established at delivery, not retroactively claimed as pre-run hashes.'))
    checks=[]
    for label,folder,expect in [('repeat-full','full-neutral-02','FULL_NEUTRAL_ALREADY_COMPLETE'),('exclusive-target','fixtures-02','EXCLUSIVE_TARGET')]:
        cmd=[sys.executable,'-B',str(ROOT/'experiments/as480/entry.py'),'--task','full' if label=='repeat-full' else 'fixtures','--out',str(PREP/folder)]
        proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
        output=(proc.stdout+proc.stderr).decode(errors='replace');need(proc.returncode!=0 and expect in output,'ENTRY_NEGATIVE:'+label)
        checks.append(dict(id=label,exitcode=proc.returncode,output=output,policy=0,receptor=0))
    need(not (PREP/'full-neutral-02').exists(),'REPEAT_CREATED_OUTPUT')
    need(not (PREP/'research.consumed.json').exists() and not RESEARCH.exists(),'RESEARCH_UNTOUCHED')
    fix=read(PREP/'fixtures-02/fixtures.json');need(fix['passed'] and fix['tests']==17,'FIXTURES')
    for folder,reason in [('fault-crash-01','ARTIFICIAL_WORKER_CRASH'),('fault-wait-01','WORKER_TIMEOUT'),('fault-budget-01','OUTPUT_MATERIAL'),('fault-job-install-01','ARTIFICIAL_JOB_INSTALL_FAILURE')]:
        t=read(PREP/folder/'terminal.json');need(t['status']=='TECHNICAL_ERROR' and t['cleanup'],'FAULT_TERMINAL')
        w=read(PREP/folder/'worker-result.json') if (PREP/folder/'worker-result.json').exists() else t
        need(reason in str(w['error']) and not any(t['counts'].values()),'FAULT_EXPECTED:'+folder)
        checks.append(dict(id=folder,expected=reason,matched=True,counts=t['counts']))
    # Final code/runtime binding, no authorization is minted.
    qualification={p.relative_to(ROOT).as_posix():sha(p) for p in PREP.rglob('*') if p.is_file() and p.name!='attempts.jsonl'}
    b=dict(kind='AS480_TECHNICAL_PRESTART',contract_sha256=CONTRACT_SHA,limits=LIMITS,runtime=rt,
           files=entry.code_files(),qualification=qualification,research_authorized=False,
           neutral_recipe=NEUTRAL,research_recipe=RECIPE,
           target=str(RESEARCH),call=f'C:/Python314/python.exe -B experiments/as480/entry.py --mode research --task full --out "{RESEARCH}" --authorization "{PREP / "authorization.json"}"')
    exclusive(PREP/'binding.json',b);exclusive(PREP/'binding.sha256',(sha(PREP/'binding.json')+'\n').encode())
    entry.binding()
    # Schema example only; absence of authorization.json is deliberate.
    exclusive(PREP/'authorization-template.json',dict(status='PENDING_NOT_AUTHORIZED',mode='research',binding_sha256=sha(PREP/'binding.json'),target=str(RESEARCH),contract_sha256=CONTRACT_SHA))
    with_rejection=False
    try:authorize('research',read(PREP/'authorization-template.json'),sha(PREP/'binding.json'),RESEARCH)
    except ValueError:with_rejection=True
    need(with_rejection,'PENDING_AUTH_ACCEPTED')
    checks.append(dict(id='final-binding-valid-pending-auth-rejected',passed=True,authorization_issued=False))
    exclusive(PREP/'delivery-checks.json',dict(checks=checks,seconds=time.monotonic()-start,job=entry.job(),policy=0,receptor=0))
    terms=[(p,read(p)) for p in PREP.glob('*/terminal.json')]
    totals={k:sum(t['counts'][k] for _,t in terms) for k in COUNTERS}
    exclusive(PREP/'execution-balance.json',dict(attempts=[dict(path=p.relative_to(PREP).as_posix(),status=t['status'],error=t['error'],counts=t['counts'],seconds=t['seconds'],job=t['job']) for p,t in terms],totals=totals,
        fixture_tests=17,full_neutral_successes=1,research_sources=0,research_arms=0,extra_entry_rejections=checks[:2]))
    text='''AS480 – technischer Anschluss und neutrale Qualifikation
Auftrag 4f08f99b-59fb-4713-bd6e-dda48328a22e | 2026-10-19

Ergebnis: Q1–Q5 technisch abgeschlossen, Forschung NICHT autorisiert.
Getrennter Anschluss unter experiments/as480/: common, material, oracle, engine,
entry, tests. Historische Rezeptor-/NJ-/Abruf-/Fortsetzungsmodule unverändert.
Festes neutrales Rezept A=[260,620,1040,1580], B=[280,640,2020,2260] Hz,
Sinusbildung/Amplituden/Phasen wie im Vertrag; vor erster Ausführung im Code
und request.json gebunden. Keine Frequenzüberschneidung mit Forschungsrezept.
Das neutrale Ergebnis ist keine wissenschaftliche AS480-Nutzenauswertung.

Q1: feste PCM-Ausschnitte und Randindizes, Wiederholung, logische Zeitachse.
Q2: tatsächliche achtframeige künstliche Kandidaten-/Promotionsfixture,
Bestandsreferenz und Zukunftsgate vor Iteratorzugriff. Vollständiger Freeze und
frische Arme zusätzlich im einmaligen neutralen Größenablauf kontrolliert.
Q3: tau/epsilon-Grenzen, Null, Exaktpriorität, Mehrdeutigkeit, falscher Offset,
fehlender Nachfolger, nicht unterstützte Faktorfortsetzung, numerische Enthaltung,
Manipulation des vorhergesagten Fehlers, S1–S4 und alle vier Ergebnisurteile.
17/17 kleine künstliche Fixtures bestanden; IDs/Protokoll in fixtures-02/.
Die Fixtures enthalten einen zusätzlichen neutralen Arm und eine Bestandsreferenz
mit je8 Aufnahmen, keine Rezeptor-/NJ-Aufrufe. Bestandsreferenz ist keine
unabhängige Näherungsentscheidung; dafür existiert das getrennte skalare Orakel.

Q4: full-neutral-01 einmal vollständig erfolgreich. Genau44 Rezeptor-/44 NJ-
Aufrufe,8 frische Arme und8 frische Referenzen, jeweils88 Aufnahmen,40 unabhängige
skalare Entscheidungsprüfungen. Sämtliche8 Arme/Referenzen beendet, Ausgabeslots
freigegeben, Material unverändert; Worker beendet, kein Temp-/Teilbestand nötig.
Die40 Prüfungen rekonstruieren Matches einschließlich aller Offsets/Faktoren,
Signalzulassung, Mehrdeutigkeit, konkrete Fortsetzung und MAE aus archiviertem
Vorzustand, ohne produktive Auswahl-/Distanz-/Fehlerfunktionen als Orakel.
Bestands- und Entscheidungsprüfer haben unterschiedliche Prüfgegenstände.

Erster Fixture-Start fixtures-01: OpenBLAS-Speicheranforderung vom harten Job
abgewiesen, Worker Exit1 vor Tests/Material/Armen. Windows meldet559681536 Bytes
Peak inklusive abgewiesener Allokation; dies ist KEIN bestandener Ressourcenlauf.
Korrektur: OPENBLAS/OMP/MKL/NUMEXPR jeweils ein Thread vor NumPy-Import.
Erst danach fixtures-02 erfolgreich. Keine Grenzerhöhung, keine Ersatzgrenze.
Gezielte künstliche Abbrüche: Workerexception, reduzierte1s-Timeoutschwelle,
prospektiver Materialbudgetüberlauf und injizierter Job-Installationsfehler.
Alle enden korrekt ohne Material-/Policy-Aufruf. Job-Installationsfehler ist
Fehlerinjektion; ein echter OS-Installationsfehler wird daraus nicht behauptet.
Erfolgreichen Größenablauf nicht wiederholt; erneuter Start davor abgewiesen.

Q5: exklusive Ausgabe, Digestabweichung, Mode-/Autorisierungstrennung,
reservierte Quellenprüfung, Runtime-/Code-/Qualifikationsbindung.
Forschungsautorisation fehlt; PENDING-Vorlage wird abgewiesen. Keine
authorization.json, kein research.consumed.json, kein Forschungsziel angelegt.
Späterer exakt vorbereiteter Start siehe START.txt; erst nach separater Freigabe.

Runtimebindung nach dem Größenablauf enger gefasst: zusätzlich NumPy-Pythondateien
und externe numpy.libs-Dateien. Alte Einstiegsversion separat erhalten;
runtime-binding-extension.diff zeigt ausschließlich diese Bindungserweiterung.
Alle zuvor gebundenen NumPy-Binaries unverändert; die zusätzlichen Hashes sind
erst bei Lieferung festgestellt, nicht rückwirkend als Vorstartbeleg ausgegeben.
Material, Engine, Orakel und Tests seit bestandenem Größenablauf unverändert.
Finale Bindung validiert, Neustart-/Exklusiv-/PENDING-Sperren gezielt geprüft;
keine neue Materialisierung zum Prüfen der Bindungserweiterung.

Ressourcenrahmen:512MiB gemeinsamer Windows-Job,2 Prozesse, Kill-on-close,
kein Breakaway; Worker240s/Gesamt300s, Material4MiB, Vorbereitung8MiB,
Observer3MiB, Abschluss1MiB, Gesamt16MiB. Bibliotheksthreads nun explizit1.
Die ausgelöste künstliche Timeoutprüfung benutzt eine strengere1s-Grenze.
Die300s-Grenze zusätzlich mit künstlichen Uhrwerten geprüft, nicht300s gewartet.
Die tatsächlichen Datei- und Jobwerte stehen in delivery-resources.json.

Historische Archive/Bindungen unverändert. Die drei aktuellen Übersichten werden
mit bytegenauen Vorgängersnapshots aktualisiert; preservation.json dokumentiert
die Zuordnung. Alte Forschungs-/Qualifikationsläufe wurden nicht wiederholt.

Empfehlung: technische Lieferung abnehmen; anschließend separat über die
einmalige AS480-Forschungsausführung entscheiden. Keine Nutzenbehauptung aus
neutralen Quellen. U und der abgeschlossene Fehlerbewertungszweig unverändert.
'''
    text+=f'\nVollständiger neutraler Lauf: {full["seconds"]:.6f}s; Jobpeak {full["job"]["peak_job_committed_bytes"]} Bytes.\n'
    text+=f'Gesamte tatsächliche Aufrufbilanz dieses Pakets: {json.dumps(totals)}\n'
    exclusive(PREP/'REPORT.txt',text.encode())
    exclusive(PREP/'START.txt',('NICHT AUSFÜHREN OHNE SEPARATE FORSCHUNGSFREIGABE\nArbeitsverzeichnis: '+str(ROOT)+'\n'+b['call']+'\n\nBinding SHA256: '+sha(PREP/'binding.json')+'\nVorlage authorization-template.json ist PENDING und keine Berechtigung.\n').encode())
    previous=read(ROOT/'reports/s2uc/as480-contract-documentation-20261019-01/preservation.json')
    para='''## Aktuell: AS480 technisch qualifiziert, Forschung nicht freigegeben (2026-10-19)

Getrennter Material-/Replay-Anschluss und unabhängiges skalares Entscheidungsorakel
implementiert. 17 künstliche Fixtures bestanden; ein vollständiger neutraler
Größenablauf mit44 Rezeptor-/NJ-Aufrufen, acht Armen und acht Bestandsreferenzen
(je88 Aufnahmen) sowie40 Entscheidungsprüfungen erfolgreich. Kein Forschungsfall.
Lauf31,30s, Jobpeak299634688 Bytes; harte512MiB-/Zweiprozessgrenze eingehalten.
Erster Fixture-Start vor Tests an OpenBLAS-Allokation gescheitert; numerische
Bibliotheken danach auf einen Thread gebunden. Fehler- und Abbruchbilanz erhalten.
Gezielte negative Gates bestanden; erfolgreicher Größenablauf nicht wiederholt.
Code-/Runtime-/Rezept-/Qualifikationsbindung und genauer späterer Start liegen vor.
Forschungsberechtigung unausgestellt. Nächster Schritt: technische Abnahme und
separate Entscheidung über einen Forschungsstart. U unverändert; Fehlerzweig zu.

[Technischer Bericht](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/as480-neutral-qualification-20261019-01/REPORT.txt).
Frühere Übersichtsfassungen bytegenau unter as480-neutral-qualification-20261019-01/
historical-overviews gesichert. Ältere Abschnitte sind historische Zeitstände.

'''
    mappings={}
    for name in ('README.md','AKTUELLER_FORSCHUNGSWEG.md','docs/README.md'):
        p=ROOT/name;old=p.read_bytes();need(info(p)==previous['overviews'][name]['current'],'OVERVIEW_CONCURRENT_CHANGE')
        exclusive(PREP/'historical-overviews'/name,old)
        split=old.find(b'\n')+1;p.write_bytes(old[:split]+b'\n'+para.encode()+old[split:])
        mappings[name]=dict(snapshot=(PREP/'historical-overviews'/name).relative_to(ROOT).as_posix(),previous=info(PREP/'historical-overviews'/name),current=info(p))
    exclusive(PREP/'preservation.json',dict(overviews=mappings,contract_sha256=sha(CONTRACT),prior_preservation='reports/s2uc/as480-contract-documentation-20261019-01/preservation.json'))
    # Existing qualified source dependencies, except the isolated entry extension, remain exact.
    for name,h in request['files'].items():
        if name not in changes:need(sha(ROOT/name)==h,'DEPENDENCY_CHANGED:'+name)
    all_bytes=size(PREP);need(all_bytes+65536<LIMITS['preparation'],'FINAL_PREPARATION_LIMIT')
    exclusive(PREP/'delivery-resources.json',dict(preparation_before_final_records=all_bytes,final_records_reserve=65536,
       total_export_limit=LIMITS['export'],preparation_limit=LIMITS['preparation'],full_neutral_job=full['job'],
       full_neutral_seconds=full['seconds'],delivery_job=entry.job(),delivery_seconds=time.monotonic()-start,
       material_bytes=size(PREP/'full-neutral-01/material'),temporary_bytes=0))
    append(PREP/'attempts.jsonl',dict(event='DELIVERY_CHECKS_COMPLETE',sources=0,policy=0,receptor=0))
    closure=dict(workflow='4f08f99b-59fb-4713-bd6e-dda48328a22e',research_authorized=False,
      files={p.relative_to(PREP).as_posix():info(p) for p in PREP.rglob('*') if p.is_file()},
      external_files={p.relative_to(ROOT).as_posix():info(p) for p in [ROOT/n for n in mappings]+[Path(__file__)]})
    need(len(raw(closure))<65536,'DELIVERY_CLOSURE_RESERVE')
    exclusive(PREP/'delivery-closure.json',closure);exclusive(PREP/'delivery-closure.sha256',(sha(PREP/'delivery-closure.json')+'\n').encode())
    print(json.dumps(dict(status='TECHNICAL_DELIVERY_COMPLETE',binding_sha256=sha(PREP/'binding.json'),delivery_sha256=sha(PREP/'delivery-closure.json'),bytes=size(PREP),totals=totals)))

if __name__=='__main__':main()
