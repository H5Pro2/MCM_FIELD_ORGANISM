"""Finalize compact archive diagnosis, with explicit pre-feedback time boundary."""
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path
from tools.s2uc_ura1_runtime_qualify import install_job
from tools import _s2uc_hx1_windows as win
from tools import s2uc_ura1_rev1_diagnosis as base


def main():
    begin=time.monotonic();install_job()
    out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else base.OUT
    assert out.is_relative_to(base.ROOT/'reports/s2uc') and out!=base.ARC
    assert not (out/'diagnosis-closure.json').exists()
    read=lambda name:json.loads((out/name).read_bytes())
    def write(name,value):
        (out/name).write_bytes(base.raw(value))
        assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<=2097152
    result=read('result.json');bindings=read('bindings.json');rows=[];cold=[];histories=[]
    assert result['status']=='PASS_ARCHIVE_DIAGNOSIS'
    # Extraction used accepted frame counters. Feedback at accepted=f belongs to target f+1.
    corrections=[]
    for number in range(1,33):
        name=f'case-{number:02d}.json';value=read(name)
        indexed={(tuple(h['origin']),h['offset']):h for h in value['histories']}
        for c in value['cold']:
            h=indexed[(tuple(c['origin']),c['offset'])]
            prior=[e for e in h['events'] if e['frame']+int(e['stage']=='feedback:after')<c['target']]
            actual=any(e['after_cell'] is not None for e in prior)
            if c['prior_warm_cell_seen']!=actual:
                corrections.append(dict(case=number,target=c['target'],key=c['key'],old=c['prior_warm_cell_seen'],corrected=actual))
            c['prior_warm_cell_seen']=actual
            assert c['prior_feedback_count']==sum(e['target']<c['target'] for e in h['feedback'])
            assert c['prior_live_feedback_count']==sum(e['target']<c['target'] and e['live'] for e in h['feedback'])
            # Admission must have an explicit stored close/promotion witness at the same frame.
            c['internal_admission_witnesses']=[e['position'] for e in h['internal'] if e['frame']==c['first_admission_frame'] and e['key'] is not None]
            assert c['internal_admission_witnesses'],('MISSING_ADMISSION_WITNESS',number,c['target'])
            cold.append(dict(case=number,**c))
        write(name,value)
        rows.extend(value['rows']);histories.extend(dict(case=number,**h) for h in value['histories'])
    assert base.balance(rows)==result['total']
    # Reconcile reason partitions independently of the extraction's group assembly.
    for group in result['reasons']:
        selected=[r for r in rows if r['reason']==group['reason']]
        assert base.balance(selected)==group['all']
        assert base.balance([r for r in selected if r['different']])==group['different']
    examples=read('examples.json')
    for entry in examples:
        candidates=[r for r in rows if (r['reason'],r['outcome'])==(entry['reason'],entry['outcome'])]
        expected=min(candidates,key=lambda r:(r['case'],r['target'])) if candidates else None
        assert entry['first']==expected
    result['cold_summary'].update(with_prior_warm_cell=sum(x['prior_warm_cell_seen'] for x in cold),
        internal_admissions_verified=len(cold),prior_cutoff='feedback effective frame = accepted + 1; strictly before target',
        first_admission_frames_before_switch=sum(x['first_admission_frame']<=512 for x in cold),
        first_admission_frames_after_switch=sum(x['first_admission_frame']>512 for x in cold))
    result['information_limits']=[
        'Observed lifecycle and stored decision reasons establish sequence, not the effect of an alternative policy.',
        'Cold denotes no valid error cell for this original identity and offset, not absence of its original sensory observation.',
        'Duplicate-value originals and other offsets are not interchangeable with this lineage.',
        'Internal records contain call/return state snapshots, not arbitrary intermediate locals or causal interventions.']
    write('result.json',result);write('cold-index.json',cold)
    write('clock-boundary-audit.json',dict(status='PASS',derived_flag_corrections=corrections,
        note='No archive re-decoding or policy execution. Corrected from already extracted event order; all target outcomes and sums unchanged.'))
    # Historical source hashes must remain unchanged. A corrected diagnostic script is bound separately.
    for name,digest in bindings['files'].items():
        if name=='tools/s2uc_ura1_rev1_diagnosis.py':continue
        assert base.sha(base.ROOT/name)==digest,name
    bindings['extraction_script_initial_sha256']=bindings['files']['tools/s2uc_ura1_rev1_diagnosis.py']
    for path in (Path(base.__file__),Path(__file__)):
        bindings['files'][str(path.relative_to(base.ROOT)).replace('\\','/')]=base.sha(path)
    write('bindings.json',bindings)
    names=dict(NO_ELIGIBLE_CONTEXT='Kein berechtigter Kontext',COLD_ONLY='Ausschließlich kalte Hypothesen',
        NO_ESTIMATED_IMPROVEMENT='Keine negative warme Bewertung',TIED_IMPROVEMENT='Gleichstand beim besten negativen Wert',SELECTED_BY_ERROR='Eindeutige Kontextwahl')
    lines=['# REV1: Diagnose der gespeicherten Entscheidungen Q129–160','',
        '2026-10-16. Ausschließlich bestehende REV1-Archive; keine Quellen, Policy-Ausführung, Alternativausgaben, Bootstrapziehungen oder Signifikanztests. Das Forschungsurteil INCONCLUSIVE bleibt unverändert.','',
        '## Vollständige Rückführung der Summen','',
        'Alle 1024 Primärziele sind genau einem gespeicherten U-Entscheidungsgrund zugeordnet. Die Gründe wurden zusätzlich anhand der eingefrorenen berechtigten Hypothesen geprüft. 418 unterschiedliche U/R-Ausgaben ergeben 222 bessere und 196 schlechtere Ziele; 606 Ziele bleiben gleich. Gewinn 75,75, Schaden 61,75, Nettogewinn 14. Keine Zielposition wurde entfernt.','',
        '| Entscheidungsgrund | Ziele | Verschiedene Ausgaben | Besser | Schlechter | Gleich | Gewinn | Schaden | Netto |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for group in result['reasons']:
        v=group['all'];lines.append(f"| {names[group['reason']]} | {v['count']} | {v['different']} | {v['better']} | {v['worse']} | {v['equal']} | {v['gain']} | {v['harm']} | {v['net']} |")
    lines+=['','Die vollständigen eigenen Summen für die 418 verschiedenen Ausgaben stehen zusätzlich unter reasons[].different in result.json. Da an diesen binären Primärzielen verschiedene Ausgaben verschiedene Fehler ergeben, sind dort genau 222 Verbesserungen und 196 Verschlechterungen, keine gleich guten verschiedenen Ausgaben.',
        'Deskriptive Einordnung: Eindeutige Kontextwahl trägt netto +15 bei, Enthaltung ohne negative warme Bewertung +2,5, ausschließlich kalte Hypothesen −3,5. Die beiden Enthaltungsgründe zusammen ergeben −1; zusammen mit +15 aus unterschiedlichen Kontextwahlen entstehen die bekannten +14. Ein negativer Bestwert-Gleichstand tritt überhaupt nicht auf. Diese Aufteilung ist keine neue Signifikanz- oder Kausalaussage.','',
        '## Getrennte Warm- und Bestandsklassen','',
        'Jede der folgenden Partitionen deckt für sich dieselben 1024 Ziele ab. Tabellen nicht miteinander aufsummieren. eligible=2 bedeutet mindestens zwei berechtigte Hypothesen. Zusätzliche Kreuztabellen Entscheidungsgrund × Warmklasse bzw. × Bestandsklasse stehen in result.json.','',
        '| Partition | Klasse | Ziele | Besser | Schlechter | Gleich | Gewinn | Schaden | Netto |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for v in result['partitions']:
        lines.append(f"| {v['partition']} | {v['label']} | {v['count']} | {v['better']} | {v['worse']} | {v['equal']} | {v['gain']} | {v['harm']} | {v['net']} |")
    c=result['cold_summary']
    lines+=['','## Herkunft und Rückmeldungen kalter Hypothesen','',
        f"{c['hypothesis_occurrences']} kalte Hypothesenauftritte an {c['targets']} Primärzielen, verteilt auf {c['lineages']} Originalidentitäten einschließlich Offset. Rollen: {c['roles']} (0=retained, 1=candidate). {c['with_prior_feedback']} Auftritte haben eine frühere gespeicherte Rückmeldung für dieselbe Originalidentität und denselben Offset; davon {c['with_prior_live_feedback']} mit gültiger lebender Zelle. Bei {c['with_prior_warm_cell']} Auftritten ist zuvor eine gültige Fehlerzelle im gespeicherten Zustandsverlauf sichtbar.",
        f"Für alle {c['internal_admissions_verified']} Auftritte sind Aufnahmezustand und internes close_segment-/Promotion-Ereignis belegt. {c['first_admission_frames_before_switch']} Auftritte stammen aus spätestens Frame 512 aufgenommenen Originalen, {c['first_admission_frames_after_switch']} aus später aufgenommenen. Abstände zwischen Aufnahme und Vorhersageframe (Frames: Häufigkeit): {c['age_frames']}.",'',
        'cold-index.json verknüpft jeden kalten Auftritt mit seiner Originalfolge, Rolle/Generation, Offset, erster Aufnahme und Belegposition. In case-NN.json enthalten histories die gespeicherten berechtigten Vorkommen, Rückmeldungen und Zustandsübergänge einschließlich Zellanlage, Rollenwechsel oder Entfernung. Maßgeblich sind Originalordinalfolge und Offset; eine Promotion wird nicht als neue unabhängige Erfahrung gezählt. Die Originalbeobachtung selbst ist keine frühere Bewertung dieser später abrufbaren Hypothese.','',
        'Zeitgrenze: feedback:after mit accepted=f gehört zum Ziel f+1. Für eine Vorhersage auf t werden deshalb nur Ereignisse mit effektivem Frame <t als Vorgeschichte gezählt. Die beim aktuellen Ziel entstehende Zelle zählt nicht rückwirkend als warm. Bei der Entwicklung wurde diese Zählermehrdeutigkeit anhand des ersten Archivfalls erkannt und ausschließlich aus den bereits extrahierten Zuständen berichtigt; clock-boundary-audit.json dokumentiert die Korrekturen. Ergebnisrichtungen und Gewinn-/Schadenssummen waren nicht betroffen.','',
        'Belegt sind gespeicherte Zustandsfolgen und Entscheidungswege. Nicht belegt ist, ob eine andere Auswahl- oder Initialisierungsregel die Fehler reduziert hätte. Nicht gespeicherte lokale Zwischenvariablen und kontrafaktische Verläufe werden nicht ergänzt. Keine verbleibende Informationslücke bei Zuordnung und Summen; die kausale Wirkung möglicher Regeländerungen bleibt ungeprüft.','',
        '## Feste Beispiele','',
        'Auswahl vor der Auswertung festgelegt: erste Archivposition nach aufsteigender Geschichte und Zielordinal, getrennt je Entscheidungsgrund und Ergebnisrichtung. Positionen sind nullbasiert innerhalb /U/forecasts; vollständige eingefrorene Hypothesen, Originalverweise, Fehler und Record-SHA stehen in examples.json und case-NN.json. Fehlende Kombinationen sind ausdrücklich ausgewiesen. Angezeigt ist jeweils die erste Vektorkomponente; es werden ausschließlich gespeicherte Ausgaben dargestellt.','',
        '| Grund | Richtung | Geschichte/Ziel | Forecastposition | U/R-Ausgabe | U/R-Fehler |',
        '|---|---|---|---:|---|---|']
    for e in examples:
        v=e['first']
        if v is None:lines.append(f"| {names[e['reason']]} | {e['outcome']} | nicht vorhanden | — | — | — |")
        else:lines.append(f"| {names[e['reason']]} | {e['outcome']} | {v['case']}/{v['target']} | {v['forecast_position']} | {v['output_u']}/{v['output_r']} | {v['u_error']}/{v['r_error']} |")
    lines+=['','## Reproduktion, Bindungen und Ressourcen','',
        'Skript: tools/s2uc_ura1_rev1_diagnosis.py; Abschluss und unabhängige Prüfung der Beispielwahl: tools/s2uc_ura1_rev1_diagnosis_finalize.py. Beide lesen ausschließlich vorhandene Archive bzw. deren kompakte Auszüge. Beispielaufruf mit neuem exklusivem Diagnoseziel (keine Anweisung zu einem weiteren Lauf):','',
        '```powershell',
        r"& 'C:\Python314\python.exe' -m tools.s2uc_ura1_rev1_diagnosis --output reports/s2uc/ura1-rev1-diagnosis-reproduction",
        r"& 'C:\Python314\python.exe' -m tools.s2uc_ura1_rev1_diagnosis_finalize reports/s2uc/ura1-rev1-diagnosis-reproduction",
        '```','',
        'bindings.json bindet alle 106 ursprünglichen Lieferdateien, deren Abschluss und die Auswertungsskripte. Pro Archiv wurden U/R-Forecasts und Rückmeldungen sowie U-Außen- und interne Lebenszyklusereignisse vollständig gegen ihre Erfassungs-Hashes geprüft. Die Gleichheit der U/R-Zustandsfolgen wird aus den unveränderten ursprünglichen Prüfbelegen übernommen. Dekodiert wird immer nur ein Archiv gleichzeitig; kein vollständiger Roharchivexport. Die Decodergrenzen für gzip, Encoded-Daten, Records und Referenztabellen bleiben erhalten.','',
        'resources.json und final-resources.json enthalten Laufzeiten und harte Job-Speichergrenzen; diagnosis-closure.json bindet die finale Lieferung. Höchstens 512 MiB Job, zwei Prozesse zulässig, tatsächlich ein Auswertungsprozess; Workerfrist 54000 s, Gesamtobergrenze 57600 s. Administrative Ausgabe unter 2 MiB und damit unter 64 MiB Gesamtexport. Historische Quellen, Archive und das Urteil INCONCLUSIVE unverändert.','',
        '## Höchstens eine Anschlussfrage','',
        'Lässt sich der beobachtete Nachteil ausschließlich kalter Kandidaten durch einen getrennt vorregistrierten Umgang mit ihrer ersten berechtigten Nutzung verringern, während die warme Fehlerauswahl unverändert bleibt? Begründung ist der isolierte Nettobeitrag −3,5 dieser Klasse gegenüber +15 aus eindeutiger Kontextwahl; fehlende Erstbewertung ist für alle kalten Auftritte belegt. Dies ist eine Anschlussfrage an den Projektleiter, keine Implementierungs- oder Versuchserlaubnis.','']
    (out/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    write('final-resources.json',dict(seconds=time.monotonic()-begin,job=win.snapshot(),archive_traversals=0,compact_cases_checked=32,
        actual_processes=1,primary_verdict='INCONCLUSIVE',script_sha256=base.sha(Path(__file__))))
    entries={str(p.relative_to(out)):dict(bytes=p.stat().st_size,sha256=base.sha(p)) for p in out.rglob('*') if p.is_file()}
    summary=dict(status='PASS_FINAL_DIAGNOSIS',files=entries,final_bytes=0,limits=dict(admin=2097152,export=67108864))
    for _ in range(8):
        n=sum(v['bytes'] for v in entries.values())+len(base.raw(summary))
        if n==summary['final_bytes']:break
        summary['final_bytes']=n
    assert n<=2097152
    write('diagnosis-closure.json',summary)
    assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file())==n
    print(json.dumps(dict(status='PASS',total=result['total'],reasons=result['reasons'],cold=c,bytes=n,clock_corrections=len(corrections))))


if __name__=='__main__':main()
