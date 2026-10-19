"""Bind completed diagnosis, preserve overview history; no source archive replay."""
import gzip,time
import diagnose as d

def main():
    started=time.monotonic();d.install_job();out=d.OUT
    d.need(d.read(out/'terminal.json')['status']=='DIAGNOSIS_COMPLETE','NOT_COMPLETE')
    d.need(not (out/'delivery-closure.json').exists(),'ALREADY_DELIVERED')
    result=d.read(out/'diagnosis.json');resources=d.read(out/'resources.json')
    fixtures=d.read(d.Path(__file__).parent/'fixture-results.json')
    d.need(fixtures['passed'] and fixtures['tests']==15,'FIXTURES')
    binding=d.read(d.ROOT/'reports/s2uc/fw1-research-preparation-20261018-01/prestart.json')
    for group in ('files','qualification'):
        for name,expected in binding[group].items():d.need(d.sha(d.ROOT/name)==expected,'BOUND:'+name)
    # Consistency of delivered derived records, not a second historical decode.
    counts={g:{str(c):d.empty() for c in (1,2,3)} for g in ('A','B','ALL')}
    link_occurrences={};target_count=0;max_record=0
    for number in range(1,33):
        data=gzip.decompress((out/f'case-{number:02d}.jsonl.gz').read_bytes())
        records=[d.json.loads(x) for x in data.splitlines()]
        d.need([x['target'] for x in records]==list(range(3,1024,2)),'TARGET_COVERAGE')
        for x in records:
            max_record=max(max_record,len(d.raw(x)));target_count+=1
            for g in (x['condition'],'ALL'):d.add(counts[g][str(x['category'])],d.F(x['difference']))
            for h in x['hypotheses']:
                if not h['different']:continue
                cold=h['keep'] is None or h['reset_values'] is None
                d.need(h['state']==('NOT_YET_UPDATED' if cold else 'UPDATED'),'LINK_CONSISTENCY')
                key='availability_difference' if cold else 'warm_rating_difference'
                link_occurrences[key]=link_occurrences.get(key,0)+1
                d.need(h['reset']<x['target']-1,'RESET_TIMING')
                d.need(all(h['reset']<u['target']<x['target']-1 for u in h['feedback']),'FEEDBACK_TIMING')
    d.need(d.serial(counts)==result['groups'],'DELIVERY_CONSERVATION')
    d.write(out/'delivery-verification.json',dict(status='PASS',targets=target_count,fixture_tests=15,
        bound_code_files=len(binding['files']),bound_qualification_files=len(binding['qualification']),
        derived_record_peak=max_record,differing_hypothesis_occurrences=link_occurrences,
        scope='Checks derived evidence only; no second source archive decode, no policy/reference.'))
    lines=['FW1 – deskriptive Anschlussdiagnose, 2026-10-19',f'Auftrag {d.WORKFLOW}',
        '', 'Ergebnis',
        'Alle beobachteten Fehlerunterschiede liegen in Kategorie 1 (Warm-/Kaltverfügbarkeit).',
        'Nach bereits erfolgtem Feedback bestehen bei 552 Zielen trotz gleicher Verfügbarkeit',
        'noch unterschiedliche Fehlerbewertungen; dort sind die Vorhersagefehler gleich.',
        '47 Kategorie-1-Ziele enthalten gleichzeitig kalte und bereits aktualisierte',
        'abweichende Hypothesen. Deshalb keine Behauptung einer einzigen lokalen Ursache.',
        'Die Diagnose beschreibt Zusammenhänge der vorhandenen Serie, keinen separaten',
        'kausalen Eingriff und keine allgemeine Aussage über Lernfähigkeit.',
        '', 'Definitionen und Vollständigkeit',
        'Ziele 3,5,...,1023: 511 je Geschichte, 8176 je A/B, 16352 insgesamt.',
        'Verglichen werden alle berechtigten Hypothesen per (Rolle, Generation, Offset).',
        'Warm bedeutet gültiges ec/ep-Paar einschließlich (0,0); kalt bedeutet beide None.',
        'Kategorie 1: mindestens ein Verfügbarkeitsunterschied, unabhängig von weiteren Bewertungen.',
        'Kategorie 2: gleiche Verfügbarkeit überall, mindestens ein unterschiedliches (ec,ep)-Paar.',
        'Kategorie 3: identische Verfügbarkeit und Werte; leere Mengen eingeschlossen.',
        'Bewertung meint das rohe numerische Paar, nicht nur delta oder Bewertungsetikett.',
        'Matching-Bestand und Ziel-/Fehleralignment wurden geprüft. Keine Filterung.',
        '10917 leere berechtigte Hypothesenmengen (A 5270, B 5647) bleiben in Kategorie 3.',
        '757 Ziele haben mehrere berechtigte Hypothesen (A 490, B 267); alle bleiben sichtbar.',
        'Differenz = Fehler KEEP minus RESET; negativ Gewinn, positiv Schaden, null Gleichstand.',
        '', 'Kategorie | Gruppe | Ziele | Gewinne | Schäden | Gleichstände | Differenzsumme']
    for g in ('A','B','ALL'):
        for c,b in result['groups'][g].items():lines.append(f"{c} | {g} | {b['targets']} | {b['gains']} | {b['harms']} | {b['ties']} | {b['error_sum']}")
    lines+=['','Gesamtbilanz exakt: A -525/4, B -457/4, insgesamt -491/2.',
        '1628 Gewinne, 646 Schäden, 14078 Gleichstände; Mittel -491/32704.',
        'Das vorhandene Primärergebnis bleibt unverändert; keine neue Bootstrapziehung.',
        '', 'Reset-/Feedback-Verknüpfung',
        'Pro Hypothese wird die letzte tatsächliche Löschung derselben retained Generation',
        'und desselben Offsets VOR der Auswahl verknüpft. Der Reset am Auswahlindex liegt',
        'nach der Auswahl und zählt daher nicht. Nur live Feedback nach dieser Löschung',
        'und vor der aktuellen Auswahl zählt als Aktualisierung. Alle passenden Updates',
        'werden mit Ziel, Originalordinal und ec/ep in den Einzelbelegen aufgeführt.',
        'UPDATED bedeutet mindestens ein solches Update, nicht vollständige Konvergenz.',
        'Neue Löschung beginnt eine neue Kette. Kandidaten erhalten keinen fremden Reset.',
        'NO_PRIOR_DELETION ist erlaubt und bleibt sichtbar; bei keiner abweichenden',
        'Hypothese dieser Serie bleibt die Reset-Verknüpfung ungeklärt.',
        '', 'Kategorie:Zustände abweichender Hypothesen | Gruppe | Ziele | Gewinne | Schäden | Gleichstände | Summe']
    for g in ('A','B','ALL'):
        for signature,b in result['linked'][g].items():lines.append(f"{signature} | {g} | {b['targets']} | {b['gains']} | {b['harms']} | {b['ties']} | {b['error_sum']}")
    lines+=['','2227 Ziele: abweichende Hypothesen ausschließlich noch nicht wieder aktualisiert.',
        '47 Ziele: gemischte Zustände (25 Gewinne, 22 Schäden, Summe -3/4).',
        '552 Ziele: abweichende Bewertungen ausschließlich bereits aktualisierter Hypothesen;',
        'alle 552 haben gleiche Vorhersagefehler. Zusammen 599 Ziele mit mindestens einer',
        'bereits aktualisierten abweichenden Hypothese; die 47 Mischfälle sind keine',
        'Belege für einen Fehlerunterschied allein nach Wiederanlernen.',
        '', 'Beispiele – feste Auswahlregel',
        'Aufsteigend nach Fall, dann Ziel: erstes Beispiel je A/B × Kategorie ×',
        'Gewinn/Schaden/Gleichstand × Zustandsmenge der abweichenden Hypothesen.',
        'Alle 12 tatsächlich vorkommenden Kombinationen stehen in examples.json.',
        'Nicht vorkommende Kombinationen werden nicht mit Ersatzfällen aufgefüllt.',
        'Fall 01, Ziel 23: Gen1/Offset0, Reset12, noch kein Update; KEEP(0,0.25),',
        'RESET kalt, Gewinn -1/4. Fall01/Ziel55: Gen2/Offset0, Reset52, kein Update,',
        'Schaden +1/4; zusätzliche identische Kandidatenhypothese bleibt erhalten.',
        'Fall01/Ziel71: Gen2/Offset0, Reset52, Feedback55; KEEP(0.3125,0.25),',
        'RESET(0.5,0.25), gleiche Fehler. Weitere identische Gen3-Hypothese enthalten.',
        'Fall03/Ziel227: Gen11/Offset0 nach Reset220 und Feedback223 bereits warm,',
        'Gen12/Offset0 nach Reset224 noch kalt; Mischfall mit Gewinn -1/4.',
        '', 'Prüfungen, Ausführungen und Ressourcen',
        '15 kleine künstliche Fixture-Tests bestanden (fixture-results.json im Analyseordner).',
        'Abgedeckt: leere Mengen, gültige Nullwerte, Kategorienvorrang, rohe Paare,',
        'Schlüsselabweichung, gleiche Generation/Offset, Auswahl-/Feedbackzeitpunkt,',
        'erneuter Reset, mehrere Hypothesen und exakte Bruchbilanz.',
        'Eine Namenskollision im neuen Belegformat brach den ersten Analyseversuch vor',
        'dem ersten abgeschlossenen Fall ab. Fehlerbeleg in fw1-diagnosis-20261019-01.',
        'Korrektur nur im neuen Skript; danach einmalige vollständige 32-Archivdiagnose.',
        'Zusätzlich eine vorherige begrenzte Archivinspektion von Fall01. Somit insgesamt',
        '34 Decoderöffnungen: 1 Inspektion, 1 abgebrochener Fall, 32 vollständige Diagnosefälle.',
        'Keine Policy-Ausführung, semantische Referenzwiederholung, Forschungsquelle oder Bootstrapziehung.',
        f"Vollständige Diagnose: {resources['seconds']:.6f} s; Jobpeak {resources['job']['peak_job_committed_bytes']} Bytes.",
        'Harter Job 512 MiB, jeweils ein Prozess. Alte Codecgrenzen unverändert.',
        'Ressourcen der Fixture- und Lieferphase separat in ihren JSON-Nachweisen.',
        'Peak des abgebrochenen Versuchs und der Vorabinspektion nicht separat gespeichert;',
        'beide liefen ebenfalls mit hartem Joblimit. Keine nachträgliche Peakbehauptung.',
        '32 neue komprimierte Zielbelege; keine zusätzlichen Kopien der Forschungsarchive.',
        'Datei-/Vorbereitungs-/Archiv-/Verwaltungsbilanz: delivery-resources.json.',
        '', 'Historische Bindungen',
        '161 Forschungsdateien und 12 externe Lieferbelege vor/nach Diagnose geprüft.',
        '2996 Vorstart-Codebindungen und 197 Qualifikationsbindungen unverändert geprüft.',
        'Die drei bisherigen Übersichten sind vor Aktualisierung bytegenau gesichert in',
        str(d.PREP)+'. Alte Liefermanifeste bleiben unverändert; preservation.json',
        'ordnet ihre früheren Übersichtspfade den Snapshots zu. Neue Übersichten werden',
        'durch die neue delivery-closure.json gebunden.',
        '', 'Anschlussvorschlag zur fachlichen Entscheidung',
        'Die Zielklassifikation spricht für eine Konzentration der nächsten fachlichen',
        'Prüfung auf die Kaltstart-Verfügbarkeit. Vor einer neuen Variante sollte der',
        'Projektleiter entscheiden, ob der gesamte Reset-Effekt damit für FW1 ausreichend',
        'beschrieben ist oder ein separat begründeter Gegenversuch benötigt wird.',
        'Keine neue Variante und kein weiterer Versuch ist hier gestartet.',
        '', 'Belege',
        'diagnosis.json, case-01..32.jsonl.gz, examples.json, delivery-verification.json,',
        'historical-verification-before/after.json, resources.json, terminal.json,',
        'preservation.json, delivery-resources.json, delivery-closure.json und .sha256.',
        'Skripte und Fixture-Ergebnis: analyses/fw1-diagnosis-20261019/.']
    d.write(out/'REPORT.txt',('\n'.join(lines)+'\n').encode())
    paragraph=('## Aktuell: FW1-Anschlussdiagnose abgeschlossen (2026-10-19)\n\n'
        'Alle 16352 Ziele überschneidungsfrei eingeordnet; Gesamtbilanz exakt reproduziert.\n'
        '2274 Ziele mit unterschiedlicher Warm-/Kaltverfügbarkeit enthalten sämtliche\n'
        '1628 Gewinne und 646 Schäden (Fehlerdifferenzsumme KEEP minus RESET -491/2).\n'
        '552 Ziele mit gleicher Verfügbarkeit und unterschiedlichen Bewertungen nach\n'
        'Feedback zeigen gleiche Vorhersagefehler. 13526 Ziele haben identische Werte.\n'
        '47 Kategorie-1-Ziele enthalten kalte und bereits aktualisierte abweichende\n'
        'Hypothesen zugleich; keine behauptete Einzelursache. 10917 leere Mengen enthalten.\n'
        '15 künstliche Fixtures bestanden, vorhandene Archive ausgewertet; keine Policy-,\n'
        'Referenz- oder Bootstrapwiederholung. Ein Formatfehler vor Fallabschluss dokumentiert.\n'
        'Historische Bindungen erhalten, bisherige Übersichten bytegenau gesichert.\n'
        'Anschlussvorschlag: fachliche Bewertung des Kaltstartbefunds vor neuer Variante.\n\n'
        f'[Diagnose und Belege]({(out/"REPORT.txt").as_posix()}).\n'
        'Ältere Abschnitte sind historische Zeitstände.\n\n')
    mappings={}
    for name in d.OVERVIEWS:
        original=(d.PREP/name).read_bytes();p=d.ROOT/name
        d.need(p.read_bytes()==original,'OVERVIEW_CONCURRENT_CHANGE')
        split=original.find(b'\n')+1;d.need(split>0,'OVERVIEW_HEADER')
        p.write_bytes(original[:split]+b'\n'+paragraph.encode()+original[split:])
        mappings[name]=dict(snapshot=(d.PREP/name).relative_to(d.ROOT).as_posix(),sha256=d.sha(d.PREP/name))
    d.write(out/'preservation.json',dict(historical=d.verify_history(relocated=True),overview_snapshots=mappings))
    files=list(out.rglob('*'));files=[p for p in files if p.is_file()]
    admin=sum(p.stat().st_size for p in files if p.suffix!='.gz');archives=sum(p.stat().st_size for p in files if p.suffix=='.gz')
    preparation=sum(p.stat().st_size for p in d.PREP.rglob('*') if p.is_file())
    code=list(d.Path(__file__).parent.glob('*'));code=[p for p in code if p.is_file()]
    failed=d.ROOT/'reports/s2uc/fw1-diagnosis-20261019-01'
    failure_bytes=sum(p.stat().st_size for p in failed.rglob('*') if p.is_file())
    # Reserve 64 KiB for remaining resource/closure records, included before write.
    d.need(admin+failure_bytes+65536<2097152 and preparation<8388608,'ADMIN_PREP_LIMIT')
    old_archive=sum(p.stat().st_size for p in d.SOURCE.glob('*.gz'))
    d.need(archives+old_archive<33554432,'ARCHIVE_TOTAL_LIMIT')
    export=admin+archives+preparation+failure_bytes+sum(p.stat().st_size for p in code)+65536
    d.need(export<67108864,'EXPORT_LIMIT')
    job=d.snapshot();d.need(job['peak_job_committed_bytes']<=536870912,'JOB')
    d.write(out/'delivery-resources.json',dict(seconds=time.monotonic()-started,job=job,actual_processes=1,
        administration_before_final_records=admin,failed_attempt_bytes=failure_bytes,
        final_records_reserve=65536,diagnostic_archive_bytes=archives,source_archive_bytes=old_archive,
        preparation_snapshot_bytes=preparation,export_with_reserve=export,temporary_bytes=0,
        limits=dict(job=536870912,administration=2097152,archives=33554432,preparation=8388608,export=67108864,closure=1048576),
        no_source_archive_decodes=True))
    def info(p):return dict(bytes=p.stat().st_size,sha256=d.sha(p))
    external=code+[d.ROOT/n for n in d.OVERVIEWS]+[p for p in d.PREP.rglob('*') if p.is_file()]+[p for p in failed.rglob('*') if p.is_file()]
    external += [d.SOURCE/'delivery-closure.json',d.SOURCE/'delivery-closure.sha256',d.ROOT/'tools/_s2uc_ura1_delta_fast_decode.py',d.ROOT/'tools/s2uc_ura1_runtime_qualify.py',d.ROOT/'tools/_s2uc_hx1_windows.py']
    closure=dict(kind='FW1_DESCRIPTIVE_DIAGNOSIS_DELIVERY',workflow=d.WORKFLOW,
        files={p.relative_to(out).as_posix():info(p) for p in out.rglob('*') if p.is_file()},
        external_files={p.relative_to(d.ROOT).as_posix():info(p) for p in external})
    d.need(len(d.raw(closure))<65536,'CLOSURE_RESERVE')
    d.write(out/'delivery-closure.json',closure)
    d.write(out/'delivery-closure.sha256',(d.sha(out/'delivery-closure.json')+'\n').encode())
    print(d.json.dumps(dict(status='DELIVERED',sha256=d.sha(out/'delivery-closure.json'),files=len(closure['files']),external=len(closure['external_files']),resources=d.read(out/'delivery-resources.json'))))

if __name__=='__main__':main()
