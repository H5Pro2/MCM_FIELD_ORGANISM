"""Post-run inventory/report from saved evidence only; never replays or generates."""
from collections import Counter
from datetime import datetime
from pathlib import Path
import json

from tools import s2uc_eval_prepare as q


def main():
    run=q.OUT; closure=q.read(run/'closure.json')
    for name,item in closure['files'].items():
        p=run/name
        if q.sha(p)!=item['sha256'] or p.stat().st_size!=item['bytes']:
            raise RuntimeError('SEALED_FILE_CHANGED:'+name)
    if set(p.name for p in run.iterdir() if p.is_file()) != set(closure['files'])|{'closure.json'}:
        raise RuntimeError('UNLISTED_EXPORT')
    binding=q.verify();q.check_preparation()
    auth=q.read(q.AUTH);template=q.read(q.TEMPLATE)
    template['status']='AUTHORIZED_ONCE'
    if auth!=template:raise RuntimeError('AUTHORIZATION_DIFFERENCE')
    specs=q.source.cases();reports=[];arm_results={a:[] for a in q.ARMS}
    target_differences=[];availability=[];completed=[];partial=None;unreadable=[]
    def saved(path):
        try:return q.read(path)
        except (json.JSONDecodeError,UnicodeDecodeError):
            if closure['status']=='COMPLETE':raise
            unreadable.append(path.name);return None
    for s in specs:
        for a in q.ARMS:
            p=run/(s['id']+'-'+a+'.json')
            if p.exists():
                r=saved(p)
                if r is None:continue
                q.resource_check(r)
                arm_results[a].append(r)
        p=run/(s['id']+'-assessment.json')
        if p.exists():
            r=saved(p)
            if r is None:continue
            reports.append(r);completed.append(s['id'])
            target_differences.extend(dict(case=s['id'],**row) for row in r['comparisons'])
            for d in r['decisions']:
                if d['target'] in s['masks']['H']:
                    availability.append(dict(case=s['id'],target=d['target'],
                        availability=d['availability'],competition=d['competition'],
                        selected=d['selected_label'],reason=d['reason']))
    if (run/'partial.json').exists():partial=saved(run/'partial.json')
    full=closure['status']=='COMPLETE'
    assessment=saved(run/'assessment.json') if (run/'assessment.json').exists() else None
    manifest=q.read(run/'manifest.json') if (run/'manifest.json').exists() else None
    starts=[q.read(p) for p in run.glob('D*-start.json')]
    chronology={}
    if manifest:
        if [e['id'] for e in manifest['entries']] != [s['id'] for s in specs]:raise RuntimeError('MANIFEST_CASES')
        for e,s in zip(manifest['entries'],specs):
            if e['masks']!=s['masks'] or e['source_sha256']!=q.sha(run/e['source_file']):raise RuntimeError('MANIFEST_SOURCE')
        mh=q.sha(run/'manifest.json');sealed=datetime.fromisoformat(manifest['sealed_at'])
        if any(x['manifest_sha256']!=mh or datetime.fromisoformat(x['started_at'])<sealed for x in starts):
            raise RuntimeError('MANIFEST_CHRONOLOGY')
        chronology=dict(manifest_sha256=mh,sealed_at=manifest['sealed_at'],sources=len(manifest['entries']),
            source_positions=sum(e['frames'] for e in manifest['entries']),
            first_arm_start=min((x['started_at'] for x in starts),default=None),
            last_arm_start=max((x['started_at'] for x in starts),default=None),arm_starts=len(starts),
            all_starts_after_seal=True,full_matches=[e['id'] for e in manifest['entries'] if e['full_matches']],
            cases_with_known_parts=[e['id'] for e in manifest['entries'] if e['overlaps']],
            registry_scope=manifest['registry_scope'])
    if full:
        if len(reports)!=32 or any(len(rs)!=32 for rs in arm_results.values()):raise RuntimeError('INCOMPLETE_COMPLETE')
        expected=q.aggregate(reports,specs)
        expected['whole_set_new']=not any(e['full_matches'] for e in manifest['entries'])
        if not expected['whole_set_new']:expected['novel_evaluation_claim']='VERFEHLT_WIEDERVERWENDUNG'
        if q.digest(expected)!=q.digest(assessment):raise RuntimeError('AGGREGATE_DIFFERENCE')
        if chronology['arm_starts']!=160:raise RuntimeError('ARM_START_COUNT')
    resources={}
    for a,rs in arm_results.items():
        normalized=[q.old.resource_report({a:r})[a] for r in rs]
        if a=='U':
            resources[a]=dict(completed_arms=len(rs),additional_python_peak=max((x['additional_python_peak'] for x in normalized),default=None),
                controlled_original_frame_upper_bound=max((x['controlled_original_frame_upper_bound'] for x in normalized),default=None),
                controlled_combined_upper_bound=max((x['controlled_combined_upper_bound'] for x in normalized),default=None),
                measured_original_frame_peak=None,measured_combined_peak=None,output_slot_limit=2,
                packed_byte_limit=416,receipt_bytes=max((x['receipt_bytes'] for x in normalized),default=None),
                utf8_upper=max((x['utf8_upper'] for x in normalized),default=None))
        else:
            resources[a]=dict(completed_arms=len(rs),additional_python_peak=max((x['additional_python_peak'] for x in normalized),default=None),
                frame_peak=max((x['meter']['frame_peak'] for x in normalized),default=None),
                combined_peak=max((x['meter']['combined_peak'] for x in normalized),default=None),
                output_slots_peak=max((x['meter']['output_slots_peak'] for x in normalized),default=None),
                receipt_bytes=max((x['meter']['receipt_bytes_peak'] for x in normalized),default=None),
                utf8_upper=max((x['meter']['receipt_transient_utf8_bytes_peak'] for x in normalized),default=None))
    admissions=sum(r['frames'] for rs in arm_results.values() for r in rs)
    reference_advances=sum(len(r['states'] if a=='U' else r['state_hashes']) for a,rs in arm_results.items() for r in rs)
    if full and (admissions,reference_advances)!=(10240,10240):raise RuntimeError('ADMISSION_COUNTS')
    report_by_case={r['id']:r for r in reports}
    all_switches=[]
    for s in specs:
        r=report_by_case.get(s['id'])
        for i,sw in enumerate(s['switches']):
            all_switches.append(dict(case=s['id'],duration=s['duration'],
                **(r['switches'][i] if r else dict(sw,passed=None,status='NOT_EVALUABLE_INCOMPLETE_CASE'))))
    observed_successes=sum(w['passed'] is True for w in all_switches)
    unobserved=sum(w['passed'] is None for w in all_switches)
    verification=dict(run_status=closure['status'],run_error=closure['error'],bound_files=len(binding['code']),
        authorization_only_status_changed=True,completed_cases=completed,
        completed_arm_admissions=admissions,completed_arm_reference_advances=reference_advances,
        extra_replays=0,source_regeneration=False,aggregate_recomputed_from_saved_case_reports=full,
        independent_generalization='NICHT_GEPRUEFT',duration_seconds=closure['duration_seconds'],
        incomplete_json_exports=unreadable,unfinished_arm_advances='NOT_MEASURED' if not full else 0,
        adaptation_observed_successes=observed_successes,adaptation_fixed_denominator=48,
        adaptation_unobserved=unobserved)
    own_script=Path(__file__).resolve()
    run_bytes=sum(p.stat().st_size for p in run.iterdir() if p.is_file())
    charged=closure['charged_previous_bytes']+run_bytes+own_script.stat().st_size
    folder=q.ROOT/'reports/s2uc/raster32-assessment-20261003-01'
    ledger=q.Ledger(folder,charged)
    ledger.write('verification.json',verification)
    ledger.write('chronology-and-overlap.json',chronology)
    ledger.write('resources.json',resources)
    ledger.write('all-target-differences.json',target_differences)
    ledger.write('all-48-switches.json',all_switches)
    ledger.write('all-context-availability.json',dict(rows=availability,counts=dict(Counter(x['availability'] for x in availability))))
    lines=['# Raster32: Abschluss der einmaligen Evaluation','',
        f"Laufstatus **{closure['status']}**, Fehler: {closure['error']}. Dauer {closure['duration_seconds']:.3f} Sekunden.",
        f"{len(completed)}/32 Faelle abgeschlossen; {admissions} abgeschlossene Arm-Aufnahmen und {reference_advances} Referenzfortschreibungen.",
        'Keine Wiederholung, Fortsetzung oder Neuerzeugung in dieser Nachauswertung. Einmalfreigabe verbraucht.',
        '71 Codebindungen, V2-Vertrag/Plan/Runtime und Qualifikation02 verifiziert. Autorisierung nur im Status geaendert.',
        'Aussagegrenze: prospektive Rasterevaluation derselben konstruierten Aufgabenfamilie; weitergehende Generalisierung NICHT_GEPRUEFT. Defaults deaktiviert.','',
        '## Manifestchronologie und Quellenueberschneidungen','',
        f"Manifest versiegelt: {chronology.get('sealed_at')}; erster Armstart: {chronology.get('first_arm_start')}.",
        f"{chronology.get('sources',0)} Quellen mit {chronology.get('source_positions',0)} Positionen; {chronology.get('arm_starts',0)} Starts an denselben Manifesthash gebunden.",
        f"Volltreffer mit indexierten Altquellen: {len(chronology.get('full_matches',[]))}. Faelle mit bekannten Teilfolgen: {len(chronology.get('cases_with_known_parts',[]))}.",
        'Keine Fallersetzung. Der Index umfasst19 gespeicherte Quellen im gebundenen Suchbereich, nicht alle denkbaren historischen Quellen oder menschlichen Vorversuche.',
        'Einzelne Quellenhashes, gemeinsame Blockhashes und Praefixlaengen stehen im unveraenderten Laufmanifest.','']
    if full:
        ar=assessment['adaptation']
        lines+=['## Getrennte Gesamtergebnisse','',f"Anpassung: **{assessment['verdicts']['adaptation']}**, {ar['successes']}/{ar['denominator']}; je Dauer {ar['per_duration']} bei Nennern {ar['denominators']}.",
            f"H-Nettonutzen: **{assessment['verdicts']['H']}**. G-Gesamtnutzen: **{assessment['verdicts']['G']}**.",
            f"Stabilitaet/Schadensgrenze: **{assessment['verdicts']['stability_damage']}**. Alle Kriterien erfuellt: {assessment['all_criteria_met']}.",
            'Primaer gleichgewichtete Fall-MAEs; Grenzentscheidungen mit exakten Bruechen. Positionsgewichtete Ergebnisse nur ergaenzend.','',
            '| Menge | U | M | E | K | P |','|---|---:|---:|---:|---:|---:|']
        for mask,row in assessment['summaries'].items():lines.append('| '+mask+' | '+' | '.join(str(row[a]['case_mean']) for a in q.ARMS)+' |')
        lines+=['','## Alle Fallergebnisse','',
            'G-MAE je Fall; Anpassung bestanden/Wechsel. Bei stabilen Faellen0/0, keine behauptete Anpassung.','',
            '| Fall | Anpassung | U | M | E | K | P | groesster G-Mehrfehler U |','|---|---:|---:|---:|---:|---:|---:|---:|']
        for r in reports:
            row=r['metrics']['G']; ds=[x['delta'] for x in assessment['case_differences'] if x['case']==r['id']]
            lines.append('| '+r['id']+' | '+str(sum(w['passed'] for w in r['switches']))+'/'+str(len(r['switches']))+' | '+' | '.join(str(row[a]['mae']) for a in q.ARMS)+' | '+str(max(ds))+' |')
        lines+=['','H-MAE je Fall:','', '| Fall | U | M | E | K | P |','|---|---:|---:|---:|---:|---:|']
        for r in reports:lines.append('| '+r['id']+' | '+' | '.join(str(r['metrics']['H'][a]['mae']) for a in q.ARMS)+' |')
        lines+=['','## Alle48 Wechsel und Kontextverfuegbarkeit','',
            '| Fall | Richtung / Art | Ziele | bestanden | Latenz Hauptziel | Ziele ohne Sollkontext |','|---|---|---|---|---:|---|']
        for sw in assessment['switches']:lines.append('| '+sw['case']+' | '+sw['direction']+' / '+sw['kind']+' | '+str(sw['targets'])+' | '+str(sw['passed'])+' | '+str(sw['latency'])+' | '+str(sw['missing_context_targets'])+' |')
        lines+=['',f"Verfuegbarkeit auf allen H-Zielen: {dict(Counter(x['availability'] for x in availability))}.",
            'Fehlende Kontexte bleiben im Nenner48 und in G/H. Kalte Kontexte, fehlende Kontexte und falsche warme Wahl sind getrennte Befunde.',
            'Alle Zielgewinne, Schaeden und Gleichstaende: all-target-differences.json. Keine Anfangs-/Wechselverluste entfernt.','',
            '| Baseline | geschaedigte Faelle | geschaedigte Ziele | Summe Zielmehrfehler | schlechtester Fall |','|---|---:|---:|---:|---|']
        for a,d in assessment['damage_summary'].items():lines.append('| '+a+' | '+str(d['harmed_cases'])+' | '+str(d['harmed_targets'])+' | '+str(d['target_loss_sum'])+' | '+str(d['worst_case'])+' |')
        violations=[d for d in assessment['case_differences'] if not d['within_damage_limit']]
        lines+=['',f"Verletzungen der Fallgrenze1/32: {violations}."]
    else:
        last_start=max(starts,key=lambda s:s['started_at']) if starts else None
        lines+=['## Technischer Teilabschluss','',
            'Alle globalen fachlichen Kriterien sind NOT_EVALUABLE. Vollstaendige48-Wechsel-Auswertung und10240+10240-Aufnahmen nicht erreicht.',
            f"Fester Anpassungsnenner48: {observed_successes} beobachtete Erfolge, {48-unobserved-observed_successes} beobachtete Misserfolge, {unobserved} nicht abschliessend ausgewertete Wechsel. Keine Verkleinerung des Nenners; kein positiver Gesamtbefund daraus.",
            f"Letzter Armstart: {last_start}. Teilbeleg: {partial.get('active') if partial else None}; Fehler: {partial.get('error') if partial else None}.",
            f"Nicht vollstaendig abgeschlossene Faelle: {[s['id'] for s in specs if s['id'] not in completed]}. Unvollstaendige JSON-Dateien: {unreadable}.",
            'Aufnahmezahlen und Ressourcen oben/unten beziehen sich auf abgeschlossene Armexporte. Fortschreibungen im beim Abbruch aktiven Arm sind ohne vollstaendigen Beleg nicht als gemessene Gesamtzahl ausgewiesen.',
            'Abgeschlossene Teilfaelle sind ausschliesslich deskriptiv. Keine Wiederholung oder Weiterfuehrung.','',
            '| Fall | fristgerechte Wechsel / beobachtete Wechsel | G-MAE U/M/E/K/P | H-MAE U/M/E/K/P |','|---|---:|---|---|']
        for r in reports:
            lines.append('| '+r['id']+' | '+str(sum(s['passed'] for s in r['switches']))+'/'+str(len(r['switches']))+' | '+
                ' / '.join(str(r['metrics']['G'][a]['mae']) for a in q.ARMS)+' | '+
                ' / '.join(str(r['metrics']['H'][a]['mae']) for a in q.ARMS)+' |')
    lines+=['','## Ressourcen','', '| Arm | Zusatz-Pythonpeak Bytes | Originalframes | gemeinsam | Receipt / UTF8 |','|---|---:|---|---|---|']
    for a,r in resources.items():
        fr=str(r.get('controlled_original_frame_upper_bound',r.get('frame_peak')))+(' Obergrenze' if a=='U' else ' Peak')
        co=str(r.get('controlled_combined_upper_bound',r.get('combined_peak')))+(' Obergrenze' if a=='U' else ' Peak')
        lines.append(f"| {a} | {r['additional_python_peak']} | {fr} | {co} | {r['receipt_bytes']} / {r['utf8_upper']} |")
    lines+=['','U:416 gepackte Bytes,maximal2 Ausgabeplaetze. Nicht erhobene U-Tracingpeaks sind null im Sinne nicht gemessen, kein Nullverbrauch.',
        'K/P: das historische Feld packed_bytes=416 ist eine Exportkonstante, kein Nachweis aktiver Fehlerbankallokation.',
        'Limits:18 Originalframes,2 Ausgaben,20 gemeinsam,16384 Zusatz-Pythonbytes,Receipt16384,UTF832768. Kein Gesamtprozess-RAM-Beleg.',
        f"Vorbelastung {closure['charged_previous_bytes']} Byte; versiegelter Lauf {run_bytes} Byte; Berichtsskript {own_script.stat().st_size} Byte. Endsumme mit Nachauswertung in closure.json.",
        'Gemeinsamer Deckel67108864 Byte,1048576 Byte Abschlussreserve; diese Nachauswertung belastet dasselbe Budget.','',
        '## Naechste Forschungsentscheidung','',
        ('Empfehlung: die beobachteten Schadens- und Nichtanpassungsfaelle anhand der jetzt gespeicherten Belege kausal einordnen; daraus genau eine begrenzte Aenderungshypothese oder einen begruendeten Stopp ableiten. Keine nachtraegliche Rettung dieses Evaluationssatzes und keine neue Ausfuehrung daraus.'
         if full and not assessment['all_criteria_met'] else
         'Empfehlung: nach Abnahme einen separat abgegrenzten Quellen-/Aufgabentransfer konzipieren; das erfolgreiche Raster allein rechtfertigt keine Generalisierungsbehauptung.' if full else
         'Empfehlung: den technischen Abbruch anhand des erhaltenen Teilbestands diagnostizieren und einen begrenzten Reparaturauftrag formulieren. Der verbrauchte Evaluationslauf bleibt geschlossen; jede weitere Ausfuehrung braucht eine neue Entscheidung.'),'']
    q.old.prior.write_text(ledger,'REPORT.md','\n'.join(lines))
    # Verify originals after report creation; no source regeneration or replay.
    for name,item in closure['files'].items():
        if q.sha(run/name)!=item['sha256']:raise RuntimeError('ORIGINAL_CHANGED')
    q.verify()
    files={p.name:dict(bytes=p.stat().st_size,sha256=q.sha(p)) for p in folder.iterdir() if p.is_file()}
    final=dict(status='COMPLETE',run_status=closure['status'],files=files,charged_previous_bytes=charged,
        report_bytes_before_closure=ledger.used,combined_including_closure=0,limit=q.LIMIT,reserve=q.RESERVE,
        source_script_sha256=q.sha(own_script),extra_replays=0)
    while True:
        n=len(json.dumps(final,sort_keys=True,separators=(',',':'),allow_nan=False).encode())+1
        total=charged+ledger.used+n
        if final['combined_including_closure']==total:break
        final['combined_including_closure']=total
    ledger.write('closure.json',final,final=True)
    print(json.dumps(dict(report=str(folder/'REPORT.md'),verification=verification,chronology=chronology,
        verdicts=assessment['verdicts'] if assessment else None,resources=resources,
        combined_including_closure=final['combined_including_closure']),indent=2))


if __name__=='__main__':main()
