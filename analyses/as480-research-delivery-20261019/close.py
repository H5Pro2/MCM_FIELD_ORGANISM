"""Close the existing AS480 archive; no source generation, policy or oracle replay."""
import sys,time,math,gzip
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from experiments.as480 import entry
from experiments.as480.common import *

def main():
    start=time.monotonic();entry.install();budget=Budget(RESEARCH)
    original_save=budget.save
    def save_once(name,x,final=False):
        p=RESEARCH/name;payload=x if isinstance(x,bytes) else raw(x)
        if p.exists():need(p.read_bytes()==payload,'EXISTING_DELIVERY_DIFF:'+name)
        else:original_save(name,x,final)
    budget.save=save_once
    t=read(RESEARCH/'terminal.json');need(t['status']=='COMPLETE' and t['cleanup'] and t['worker_ended'],'TERMINAL')
    b,h=entry.binding();need(h=='65cc36a2da6c3e558842d0bc0e9d509072fb4cdb6cfd6d35f2445347c651c482','APPROVAL')
    authorize('research',read(PREP/'authorization.json'),h,RESEARCH)
    need(read(PREP/'research.consumed.json')['nonce']==read(RESEARCH/'request.json')['nonce'],'CONSUMPTION')
    for name,expected in t['files_before_terminal'].items():need(info(RESEARCH/name)==expected,'ARCHIVE:'+name)
    a=read(RESEARCH/'assessment.json');data={c:{m:read(RESEARCH/f'{c}-{m}.json')['records'] for m in ('E','N')} for c in CASES}
    details=[];main=[];harms=[];lost=[]
    for c in CASES:
        for e,n in zip(data[c]['E'],data[c]['N']):
            need(e['target']==n['target'] and e['p_error']==n['p_error'],'PAIR')
            r=dict(case=c,target=e['target'],phase='main' if e['target']==11 else 'transition' if e['target']==9 else 'learning',
                E=e['error'],N=n['error'],P=e['p_error'],N_minus_E=n['error']-e['error'],N_minus_P=n['error']-e['p_error'],
                E_retrieval=e['receipt']['status'],N_retrieval=n['receipt']['status'],
                E_continuation=e['forecast']['status'],N_continuation=n['forecast']['status'])
            details.append(r)
            if r['N_minus_E']>0 or r['N_minus_P']>0:harms.append(r)
            if n['receipt']['retrieval']['signal_lost_exact_single']:lost.append(dict(case=c,target=n['target']))
            if r['phase']=='main':
                d=dict(r,source=c[0],source_target_interval=[10080,14880] if c.endswith('480') else [9600,14400],policies={})
                for m,rec in [('E',e),('N',n)]:
                    ctx=rec['forecast']['context_values'];p=rec['forecast']['persistence_values']
                    d['policies'][m]=dict(matches=rec['receipt']['matches'],context_vector=ctx,output_vector=ctx if ctx is not None else p,
                        context_mae=None if ctx is None else rec['error'],retrieval=rec['receipt'].get('retrieval'),
                        correct_assignment=a['cases'][c][m]['correct'] if c[0]=='A' else False,
                        false_A_assignment=c[0]=='B' and a['cases'][c][m]['assigned'])
                d['P_vector']=e['forecast']['persistence_values'];d['actual_vector']=e['actual'];main.append(d)
    budget.save('main-target-details.json',main,final=True)
    budget.save('all-errors.json',dict(rows=details,individual_harms=harms,signal_lost_exact=lost,
        learning_means={m:math.fsum(r[m] for r in details if r['phase']=='learning')/12 for m in ('E','N','P')},
        transition_means={m:math.fsum(r[m] for r in details if r['phase']=='transition')/4 for m in ('E','N','P')}),final=True)
    lines=['# AS480 – Ergebnis des einmaligen Forschungslaufs','',
        'Auftrag: 6fecf399-7d55-455f-8f2a-0b576e5f61df. Datum: 2026-10-19.',
        '', '**Gesamturteil: NO_ADDITIONAL_BENEFIT.** Technisch vollständig; keine identischen A/B-Hinweiskollisionen.','',
        '- S1 falsch: A480 wird weder von E noch von N korrekt zugeordnet.',
        '- S2 wahr: keine zusätzliche falsche A-Zuordnung in B0/B480; beide Policies enthalten sich.',
        '- S3 wahr: der korrekte A0-Exaktabruf bleibt erhalten; kein verlorener korrekter A-Abruf.',
        '- S4 falsch: N und E haben identische Hauptzielfehler. Beide liegen unter P, aber N ist nicht strikt besser als E.',
        '', 'Hauptzielmittel: '+json.dumps(a['assessment']['means'])+'.',
        'Beide Schadenflags sind falsch. Gleichstand ist kein Gleichwertigkeitsnachweis.',
        '', '## Vier Hauptziele','', '| Fall | E-MAE | N-MAE | P-MAE | N−E | N−P |','|---|---:|---:|---:|---:|---:|']
    for d in main:lines.append('| '+d['case']+' | '+' | '.join(format(d[k],'.17g') for k in ('E','N','P','N_minus_E','N_minus_P'))+' |')
    lines+=['','A0: Quelle A, Ziel [9600,14400); E und N rufen retained1, Originale1–4, Offset0, Faktor1 exakt ab. Nachfolger ist Original3; Kontext-MAE0.',
        'A480: Quelle A, Ziel [10080,14880); kein Match/Offset/Faktor. E: ABSTAIN_NO_MATCH; N: ABSTAIN_NO_APPROX_CONTEXT. Beide benutzen P.',
        'B0: Quelle B, Ziel [9600,14400); kein Match/Offset/Faktor. E: ABSTAIN_NO_MATCH; N: ABSTAIN_NO_APPROX_CONTEXT. Beide benutzen P.',
        'B480: Quelle B, Ziel [10080,14880); kein Match/Offset/Faktor. E: ABSTAIN_NO_MATCH; N: ABSTAIN_NO_APPROX_CONTEXT. Beide benutzen P.',
        'Bei diesen Enthaltungen lautet die Fortsetzungsentscheidung ABSTAIN_NO_CONTEXT; Kontextvektor und Kontext-MAE fehlen, Schema-MAE verwendet P.',
        'Vollständige E/N/P-Ausgabevektoren, tatsächliche Zielvektoren, Herkunft und Receipts: main-target-details.json; Rohzustände und Hinweise: A0-E.json bis B480-N.json.',
        '', '## Lernfehler (Ziele3/5/7) getrennt','', '| Fall | Ziel | E-MAE | N-MAE | P-MAE | N−E | N−P |','|---|---:|---:|---:|---:|---:|---:|']
    def table(phase):
        for d in details:
            if d['phase']==phase:lines.append('| '+d['case']+' | '+str(d['target'])+' | '+' | '.join(format(d[k],'.17g') for k in ('E','N','P','N_minus_E','N_minus_P'))+' |')
    table('learning')
    lines+=['','## Übergangsfehler (Ziel9) getrennt','', '| Fall | Ziel | E-MAE | N-MAE | P-MAE | N−E | N−P |','|---|---:|---:|---:|---:|---:|---:|'];table('transition')
    lines+=['','Ziele3/5: kein Kontext, P. Ziel7: exakter Kandidat1-Abruf, Originale1–4, Offset0, Faktor1, Fehler0. Ziel9: exakter Kandidat1-Match mit Offset2; ABSTAIN_NO_SUCCESSOR, deshalb P. Die spätere Promotion beim Abschluss8 ändert diese zuvor eingefrorene Entscheidung nicht.',
        '', '## Einzelschäden und Grenzen','',
        f'Über alle20 Zielpaare: {len(harms)} Fälle mit N−E>0 oder N−P>0; {len(lost)} durch Signalgate verlorene eindeutige Exaktmatches. Alle Deltas stehen oben und in all-errors.json.',
        'Keine gemeinsame oder zusätzliche falsche A-Zuordnung an den beiden B-Hauptzielen. Keine zusätzlichen Lern-/Übergangsfälle als unabhängige Hauptprüffälle gezählt.',
        'Die feste Näherungsregel liefert hier keinen zusätzlichen Abruf. Das belegt weder allgemeine Nutzlosigkeit noch natürliche Robustheit, allgemeine Lernfähigkeit oder feldinterne Memory. Keine Parametersuche, kein Bootstrap, keine Ersatzquelle.',
        '', '## Ausführung und Ressourcen','',
        'Genau ein Forschungsstart, zwei Quellen,44 Rezeptor-/44 NJ-Aufrufe, acht Arme und acht Bestandsreferenzen mit je88 Aufnahmen sowie40 bereits im Worker bestandene unabhängige skalare Prüfungen. Kein Replay beim Abschluss.',
        'Alle acht Arme/Referenzen geschlossen, Worker beendet; Material nach Vergleich unverändert. terminal.json, worker-result.json und execution.jsonl enthalten die Nachweise.',
        f'Laufzeit {t["seconds"]:.9f}s; Jobpeak {t["job"]["peak_job_committed_bytes"]} Bytes; Prozesspeak {t["job"]["peak_process_committed_bytes"]} Bytes. Harte Jobgrenze536870912 Bytes, maximal2 Prozesse, Worker240s/Gesamt300s; Bibliotheksthreads1.',
        'Abschluss ist eine separate Archiv-/Dokumentationsphase ohne Material-/Policyaufrufe; deren Job-/Zeit-/Dateibilanz wird separat in delivery-resources.json ausgewiesen. Keine Behauptung, die interaktive Berichtsphase liege innerhalb der Supervisor-Wanduhr.',
        'Einmalberechtigung und Verbrauchsmarker verbleiben unter as480-neutral-qualification-20261019-01. Kein Retry erlaubt. START.txt wurde unverändert verwendet; dessen generisches reason-Feld nennt noch qualification, maßgeblich sind mode=research, Berechtigung und dieser Auftragsbezug.',
        'Der frühere OpenBLAS-Abbruch bleibt in der neutralen Bilanz dokumentiert. Die spätere Runtimebindungserweiterung bleibt eine Lieferbindung und wird nicht rückwirkend als Neutral-Vorstartnachweis ausgegeben.',
        '', '## Anschlussvorschlag','',
        'Diese feste AS480-Gegenprobe abschließen. Als nächsten begrenzten Schritt eine rein lesende Ursachenanalyse der archivierten A480-Hinweise gegen die gespeicherte A-Spur fachlich entscheiden: prüfen, ob Fensterinhalt und Rezeptorprojektion den fehlenden Näherungsabruf erklären. Keine neue Quelle, keine neue Policy und keine Schwellenanpassung daraus automatisch freigeben.',
        'Die unveränderten Regeln und das vorliegende negative Resultat bleiben Referenz. U und der abgeschlossene Fehlerbewertungszweig bleiben unverändert.']
    budget.save('REPORT.md',('\n'.join(lines)+'\n').encode(),final=True)
    previous=read(PREP/'preservation.json');mapping={}
    para='''## Aktuell: AS480 einmalig abgeschlossen – kein Zusatznutzen (2026-10-19)

Die freigegebene Vierfallgegenprobe A0/A480/B0/B480 ist technisch vollständig:
44 Rezeptor-/NJ-Aufrufe, acht Arme und acht Referenzen mit je88 Aufnahmen,
40 unabhängige Entscheidungsprüfungen. Urteil NO_ADDITIONAL_BENEFIT.
S1 falsch, S2 wahr, S3 wahr, S4 falsch. E=N im Hauptzielmittel
0,0023202510123532727; P=0,00302567864944738. Keine zusätzlichen Fehlabrufe,
keine Einzelschäden N−E/N−P, keine A/B-Hinweiskollisionen. A480 bleibt ohne Abruf.
Lauf34,86s; Jobpeak300109824 Bytes unter512MiB, höchstens zwei Prozesse.
Einmalberechtigung verbraucht; kein Retry, Ersatzmaterial oder Parameterwechsel.
Vorschlag zur fachlichen Entscheidung: archivbasierte Ursachenanalyse des
fehlenden A480-Näherungsabrufs, ohne neue Messung oder Regeländerung.
U unverändert; Fehlerbewertungszweig geschlossen. Frühere Abschnitte historisch.

[Forschungsbericht](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/as480-comparison-01/REPORT.md).

'''
    for name in ('README.md','AKTUELLER_FORSCHUNGSWEG.md','docs/README.md'):
        p=ROOT/name;snapshot=RESEARCH/'historical-overviews'/name
        if snapshot.exists():
            old=snapshot.read_bytes();need(info(snapshot)==previous['overviews'][name]['current'],'SNAPSHOT_CHANGED')
            split=old.find(b'\n')+1;need(p.read_bytes()==old[:split]+b'\n'+para.encode()+old[split:],'PARTIAL_OVERVIEW_CHANGED')
            stored=snapshot;compression='none'
        else:
            need(info(p)==previous['overviews'][name]['current'],'OVERVIEW_CHANGED:'+name)
            old=p.read_bytes();packed=gzip.compress(old,mtime=0);need(gzip.decompress(packed)==old,'LOSSLESS_SNAPSHOT')
            stored=Path(str(snapshot)+'.gz');compression='gzip'
            budget.save(stored.relative_to(RESEARCH).as_posix(),packed,final=True)
            split=old.find(b'\n')+1;p.write_bytes(old[:split]+b'\n'+para.encode()+old[split:])
        mapping[name]=dict(previous=previous['overviews'][name]['current'],snapshot=stored.relative_to(RESEARCH).as_posix(),compression=compression,snapshot_info=info(stored),current=info(p))
    budget.save('preservation.json',dict(overviews=mapping,prior=str(PREP/'preservation.json')),final=True)
    budget.save('documentation-recovery.json',dict(first_error='OUTPUT_CLOSURE: uncompressed research-route snapshot exceeds 1 MiB per closure artifact',
        stage='post-run documentation only',first_attempt_files=['main-target-details.json','all-errors.json','REPORT.md','historical-overviews/README.md'],
        first_overview_updated='README.md',recovery='Preserve existing exact artifacts; remaining snapshots losslessly gzip compressed; no limit increase.',
        research_retries=0,new_sources=0,new_policy_admissions=0,scientific_terminal_unchanged=True),final=True)
    entry.verify_files(b['files'])
    need(t['seconds']<300 and t['job']['peak_job_committed_bytes']<=LIMITS['job'],'RUN_LIMITS')
    budget.save('delivery-resources.json',dict(research_execution=t,delivery_seconds=time.monotonic()-start,delivery_job=entry.job(),
        preparation_bytes=size(PREP),research_bytes_before_closure=size(RESEARCH),material_bytes=size(RESEARCH/'material'),
        total_before_closure=size(PREP)+size(RESEARCH),final_reserve=131072,limits=LIMITS,
        new_source_calls=0,new_policy_calls=0,new_oracle_calls=0),final=True)
    closure=dict(workflow='6fecf399-7d55-455f-8f2a-0b576e5f61df',binding_sha256=h,verdict=a['assessment'],
        files={p.relative_to(RESEARCH).as_posix():info(p) for p in RESEARCH.rglob('*') if p.is_file()},
        external={str(p):info(p) for p in [PREP/'authorization.json',PREP/'research.consumed.json',PREP/'attempts.jsonl',Path(__file__)]+[ROOT/n for n in mapping]},
        qualification_note='Historical closure attempts.jsonl is append-only and has new research entries; original qualification files remain bound unchanged.')
    budget.save('delivery-binding.json',closure,final=True)
    budget.save('delivery-binding.sha256',(sha(RESEARCH/'delivery-binding.json')+'\n').encode(),final=True)
    for name,expected in closure['files'].items():need(info(RESEARCH/name)==expected,'FINAL_HASH')
    need(time.monotonic()-start<60,'DELIVERY_TIME')
    print(json.dumps(dict(status='DELIVERY_COMPLETE',sha256=sha(RESEARCH/'delivery-binding.json'),total_bytes=size(PREP)+size(RESEARCH),research_bytes=size(RESEARCH),seconds=time.monotonic()-start)))

if __name__=='__main__':main()
