"""Post-terminal evidence verification and report formatting; no policy/statistics run."""
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
from tools.s2uc_ura1_prepare_cr1 import PREP, TARGET, LIMITS, validate_binding
from tools._s2uc_ura1_fs_accounting_v4 import category
from tools.s2uc_ura1_runtime_qualify import install_job


def main():
    install_job()
    p = TARGET
    load = lambda name: json.loads((p/name).read_bytes())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    b, h = validate_binding(PREP/'prestart.json')
    assert h == '336f44aa79d8091991cfdc292e550c01e952e4faf5247e2c1b8613fb858ac1f3'
    start, terminal, result, worker, closure, manifest, stats = map(load, (
        'START.json', 'terminal.json', 'result.json', 'worker.json', 'closure.json', 'sources-manifest.json', 'statistics.json'))
    assert start == dict(consumed=True, namespace='MCM-URA1-CR1/source/v1', prestart_sha256=h)
    assert terminal['status'] == 'TERMINAL_COMPLETE' and terminal['cleanup'] == 'CONFIRMED'
    assert terminal['worker_ended'] and terminal['file_cleanup_confirmed']
    assert not terminal['first_failure'] and not terminal['followup_failures'] and terminal['active_case'] is None
    assert terminal['completed_cases'] == list(range(1, 33)) and terminal['arms_created'] == terminal['distinct_arms'] == 64
    for value in (result, worker):
        assert value['status'] == 'COMPLETE' and value['complete_cases'] == 32
        assert value['archive_integrity'] and value['reference_equal']
    assert len(manifest['entries']) == 32 and manifest['all_before_policy'] and manifest['namespace'] == start['namespace']
    for name, item in closure['files'].items():
        path = (p/name).resolve()
        assert path.is_relative_to(p) and path.stat().st_size == item['bytes'] and sha(path) == item['sha256'], name
    cases = []
    for number, item in enumerate(manifest['entries'], 1):
        assert item['replicate'] == number and sha(p/item['path']) == item['sha256']
        proof = load(f'case-{number:02d}-capture.json')['collections']
        for field in ('events', 'internal'):
            assert proof['/U/'+field] == proof['/C/'+field]
        for arm in ('U', 'C'):
            assert proof[f'/{arm}/events']['count'] == 3072
            assert proof[f'/{arm}/forecasts']['count'] == 512 and proof[f'/{arm}/rows']['count'] == 511
        cases.append(dict(case=number, source_sha256=item['sha256'], archive_sha256=sha(p/f'case-{number:02d}.delta.json.gz'),
                          capture_sha256=sha(p/f'case-{number:02d}-capture.json'), counts={k:v['count'] for k,v in proof.items()}))
    assert len(list(p.glob('*.delta.json.gz'))) == 32 and not list(p.glob('*.partial'))
    primary, first = stats['primary'], stats['secondary'][0]
    assert primary['name'] == 'CR1:Q129-160:C-U' and first['mask'] == 'Q_early_post'
    assert first['orientation'] is None and first['count'] == 1024 and len(primary['pairs']) == 32
    assert primary['mean'] == first['mean']
    assert stats['bootstrap_sha256'] == '0b9fbf483e870adac01ded7d2d0d0a651a11474a4ac2e4fbae1c14e793d7d965'
    lo, hi = map(F, primary['ci'])
    verdict = 'C_EARLY_POST_BETTER' if hi < 0 else 'U_EARLY_POST_BETTER' if lo > 0 else 'INCONCLUSIVE'
    assert primary['verdict'] == verdict
    cold = next(x for x in stats['diagnosis'] if x['partition']=='warm' and x['label']=='cold')
    multiple = next(x for x in stats['diagnosis'] if x['partition']=='eligible' and x['label']==2)
    assert cold['count']==75 and cold['better']==48 and cold['worse']==27
    assert multiple['better']==multiple['worse']==0
    assert terminal['seconds'] <= LIMITS['total_seconds'] and terminal['job']['peak_job_committed_bytes'] <= LIMITS['job']

    def save(name, value):
        with (p/name).open('x', encoding='utf-8', newline='\n') as file:
            file.write(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

    save('verification.json', dict(status='PASS_POSTRUN_EVIDENCE_CHECK', prestart_sha256=h, source_hashes_verified=32,
         closure_hashes_verified=len(closure['files']), bound_files_verified=len(b['files']), cases=cases,
         no_policy_or_statistics_reexecution=True, statistics_reference_confirmed_by_worker=True,
         delivery_script_sha256=sha(Path(__file__))))
    dec = lambda value: f'{float(F(value)):.12f}'
    findings = {
        'C_EARLY_POST_BETTER': 'C erzielt im vorab festgelegten frühen Nachwechselfenster einen niedrigeren mittleren Fehler als U. Das vollständig negative Intervall unterstützt die feste kalte Auswahlregel in dieser Quellenfamilie.',
        'U_EARLY_POST_BETTER': 'C erzielt im vorab festgelegten frühen Nachwechselfenster einen höheren mittleren Fehler als U. Das vollständig positive Intervall zeigt einen Nachteil der festen kalten Auswahlregel in dieser Quellenfamilie.',
        'INCONCLUSIVE': 'Der frühe C/U-Unterschied bleibt nach dem vorab festgelegten Intervallkriterium unentschieden. Das ist kein Gleichwertigkeitsnachweis.'}
    recommendations = {
        'C_EARLY_POST_BETTER': 'C als begrenzt belegte Ausgabevariante dieser Testfamilie einordnen. Alle 75 abweichenden Primärziele hatten genau eine kalte Hypothese: Der Befund trägt kalte Originalausgabe gegenüber Persistenz, keinen Vergleich mehrerer kalter Originale. Diese Grenze zuerst abnehmen und danach eine eigene mechanistische Gegenprognose zur Erfahrungsbildung formulieren; kein automatischer weiterer C/U-Lauf oder Tuning.',
        'U_EARLY_POST_BETTER': 'Die feste CR1-Kaltauswahl für diese Testfamilie als nachteilig einordnen und diesen Variantenzweig beenden. Keine nachträgliche Auswahl günstiger Fenster, Kennungen oder Teilgruppen.',
        'INCONCLUSIVE': 'Intervall und Häufigkeit kalter Primärziele gemeinsam bewerten. Keine automatische Wiederholung, Stichprobenvergrößerung oder neue Auswahlregel; nur eine neue mechanistisch begründete Frage rechtfertigt einen gesonderten Auftrag.'}
    lines = ['# URA1-CR1: vollständiger Forschungsabschluss', '',
        'Workflow-Auftrag 09fde789-5ec0-4a2f-9d30-516d4906d587. Genau ein autorisierter Aufruf; Wiederzustellung als derselbe Auftrag behandelt.',
        f'Vorstart-SHA: {h}.', '', '## Ergebnis', '',
        '**COMPLETE / TERMINAL_COMPLETE.** 32 Geschichten, 64 frische C/U-Arme, alle Fallquittungen und unabhängigen Referenz-/Archiv-/Statistikprüfungen bestätigt. Keine Fehlerursache oder Folgefehler. Worker beendet und Cleanup bestätigt. Kein Retry, Resume, Ersatzfall oder Tuning.', '', findings[verdict], '',
        f"C-MAE {dec(first['means']['C'])}, U-MAE {dec(first['means']['U'])}; C−U {dec(primary['mean'])}, nominales 95%-Intervall [{dec(primary['ci'][0])}; {dec(primary['ci'][1])}]. Urteil: {verdict}.", '',
        '## Design und einziger Primärnachweis', '',
        '32 neue, unabhängig geprüfte Quellen unter MCM-URA1-CR1/source/v1, vollständig vor dem ersten Arm versiegelt. Je 1024 Frames; einmalige Kontingenzumkehr nach Block 128, kein Reset oder zusätzliches Wechselsignal. C weicht ausschließlich bei nicht leerem, vollständig kaltem H durch Originalrecency von U ab. Gemeinsamer zugänglicher Bestand, Rückmeldungen und warme Auswahl bleiben identisch. Historische Daten wurden nicht gepoolt. Die Variantenwahl ist ausdrücklich durch die frühere REV1-Diagnose motiviert; jene Daten dienen der Hypothesenbildung, nicht als unabhängiger C-Beleg.', '',
        'Primär: je Geschichte mittlere C−U-MAE über Q129–160, anschließend gleichgewichtetes Mittel über 32 Geschichten. 32 Ziele je Geschichte, 1024 insgesamt. Kalte, leere, Ein-Kandidaten- und schädliche Ziele bleiben eingeschlossen. Statistische Einheit ist die Geschichte. 10000 vorab gebundene Bootstrapziehungen, 16+16 nach Orientierung, nominales zweiseitiges 95%-Perzentilintervall mit linearer Interpolation. Keine neue Matrix oder Seedwahl.', '',
        '| Größe | Exakt | Dezimal |', '|---|---:|---:|']
    for name, value in [('C-MAE', first['means']['C']), ('U-MAE', first['means']['U']), ('C−U', primary['mean']), ('95%-Untergrenze', primary['ci'][0]), ('95%-Obergrenze', primary['ci'][1])]:
        lines.append(f'| {name} | {value} | {dec(value)} |')
    lines += ['', '## Ergänzende Fenster — ausschließlich deskriptiv', '',
        'Nur Q129–160 ist primär. Vorphase Q97–128, späte Nachphase Q161–256, gesamte Nachphase Q129–256 sowie Q/G_all/S/Q_X/Q_Y sind deskriptiv. Orientierung 0: ungerade Geschichten; Orientierung 1: gerade. Keine zusätzlichen Signifikanzurteile.', '',
        '| Maske | Orientierung | Ziele | C-MAE | U-MAE | C−U |', '|---|---|---:|---:|---:|---:|']
    for value in stats['secondary']:
        lines.append(f"| {value['mask']} | {value['orientation'] if value['orientation'] is not None else 'alle'} | {value['count']} | {dec(value['means']['C'])} | {dec(value['means']['U'])} | {dec(value['mean'])} |")
    lines += ['', '## Gewinn und Schaden im Primärfenster', '',
        f"Besser: {first['better']}, schlechter: {first['worse']}, gleich: {first['equal']} von 1024 Zielen. Gewinnsumme {first['gain']}, Schadenssumme {first['harm']}, Netto (Gewinn−Schaden) {first['net']}. Maximaler zusätzlicher Fehler je Ziel {first['max_harm']}, an {len(first['maximum_harm_targets'])} Positionen. Vollständige Positionen stehen in statistics.json.",
        f"Schlechtester mittlerer Geschichtenkontrast: {first['worst_mean']} ({dec(first['worst_mean'])}), Geschichten {first['worst_stories']}.", '',
        'Alle 75 unterschiedlichen Primärausgaben gehören zur vollständig kalten Klasse mit genau einer berechtigten Hypothese. 949 Ausgaben sind identisch. Damit ist in diesem Primärfenster die kalte Originalausgabe gegenüber Persistenz verglichen; ein spezifischer Vorteil der Recency-Rangfolge zwischen mehreren kalten Originalen ist nicht nachgewiesen. Diese Einordnung ist deskriptiv und ändert das vorab festgelegte Primärurteil nicht.', '',
        'Die folgenden überlappenden Partitionen beziehen sich ausschließlich auf das Primärfenster. eligible=2 bedeutet mindestens zwei berechtigte Hypothesen. Warm-/Auswahlklassen sind U-seitig bestimmt. Netto>0 begünstigt C und hat das umgekehrte Vorzeichen zur C−U-Summe. Keine Kausalattribution aus Untergruppen.', '',
        '| Partition | Klasse | Ziele | Besser | Schlechter | Gleich | Gewinn | Schaden | Netto |', '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for value in stats['diagnosis']:
        lines.append(f"| {value['partition']} | {value['label']} | {value['count']} | {value['better']} | {value['worse']} | {value['equal']} | {value['gain']} | {value['harm']} | {value['net']} |")
    lines += ['', 'Die leere Klasse different_context hat Anzahl 0 und mean_delta=null in statistics.json; kein definierter Teilgruppenmittelwert. Geschichten mit Primärkontrast 0 bleiben vollständig im Mittel und Bootstrap enthalten.', '']
    lines += ['', '## Primärkontrast je Geschichte', '', '| Geschichte | C−U exakt | Dezimal |', '|---|---:|---:|']
    for number, value in enumerate(primary['pairs'], 1):
        lines.append(f'| {number} | {value} | {dec(value)} |')
    lines += ['', '## Integrität, Ressourcen und Abschluss', '',
        f"987 Vorstart-Dateibindungen unverändert; 32 Quellenhashes und {len(closure['files'])} Abschlussdateihashes geprüft. Alle 32 Erfassungsbelege zeigen gleiche C/U-Hashes für äußere und interne Zustandsereignisse. Je Geschichte und Arm 3072 äußere Ereignisse, 512 Prognosen und 511 beobachtete Ziele. Das letzte Ziel 1025 ist zensiert. Die unabhängige Statistikreferenz wurde im autorisierten Lauf vollständig bestätigt. Für diesen Bericht wurden keine Policies oder statistischen Versuche wiederholt.", '',
        f"Gesamtdauer {terminal['seconds']:.3f} s ({terminal['seconds']/60:.2f} min), innerhalb 57600 s. Jobpeak {terminal['job']['peak_job_committed_bytes']} Byte, Prozesspeak {terminal['job']['peak_process_committed_bytes']} Byte. Gemeinsamer Job 512 MiB, zwei Prozesse. Workerfrist 54000 s und Abschlussreserve 3600 s innerhalb der Gesamtfrist bleiben durch den gebundenen Einstieg geschützt; ein separater Worker-Walltimewert ist nicht aufgezeichnet.",
        f"Workerbilanzierung: {terminal['worker_accounting']['calls']} Prüfungen, {terminal['worker_accounting']['seconds']:.3f} s; Supervisor: {terminal['supervisor_accounting']['calls']} Prüfungen, {terminal['supervisor_accounting']['seconds']:.3f} s. Zeiten überlappen und werden nicht als Laufdauer addiert.", '',
        'Worker beendet, interner Cleanup und Datei-Cleanup bestätigt. Keine temporären Teilarchive. Die finale Größen- und Dateibilanz einschließlich dieses Berichts steht in delivery-closure.json; preparation_bytes enthält auch die einmalig erstellte Berechtigung. Alle ursprünglichen Laufartefakte bleiben unverändert.', '',
        '## Aussagegrenzen und nächster Schritt', '',
        'Der Befund gilt ausschließlich für die feste diagnosemotivierte Kaltauswahl, diese synthetische Quellenfamilie und das vorab festgelegte Fenster. Ein möglicher Ausgabevorteil beweist keine verbesserte Erfahrungsbildung: Gemeinsame Fehlerzustände und Erfahrungsaufnahme bleiben gerade unverändert. Keine allgemeine Überlegenheit, neue Memory-Organisation oder Übertragung auf reale Audio-/Video-Wahrnehmung nachgewiesen. Neueste Originalfortsetzung bedeutet nicht zwingend zuletzt beobachtete Fortsetzung. Deskriptive Untergruppen und weitere Fenster erhalten kein zusätzliches Signifikanzurteil.', '',
        'Empfehlung an den Projektleiter: '+recommendations[verdict], '',
        'Belege: [START](START.json), [Quellenmanifest](sources-manifest.json), [Statistik](statistics.json), [Worker](worker.json), [Resultat](result.json), [Terminal](terminal.json), [ursprünglicher Abschluss](closure.json), [Nachprüfung](verification.json), [finale Lieferung](delivery-closure.json).', '']
    with (p/'REPORT.md').open('x', encoding='utf-8', newline='\n') as file:
        file.write('\n'.join(lines))
    prep_bytes = sum(x.stat().st_size for x in PREP.rglob('*') if x.is_file())
    files = {str(x.relative_to(p)):dict(bytes=x.stat().st_size, sha256=sha(x)) for x in p.rglob('*') if x.is_file()}
    groups = dict(source=0, archive=0, admin=0, closure=0, temp=0)
    for name, item in files.items():
        groups[category(name)] += item['bytes']
    delivery = dict(status='COMPLETE_DELIVERY', prestart_sha256=h, files=files, preparation_bytes=prep_bytes,
                    groups_before_this_closure=groups, final_receipt_category='admin',
                    export_bytes_including_this_closure=0, limits=LIMITS)
    for _ in range(8):
        encoded = (json.dumps(delivery, ensure_ascii=False, indent=2)+'\n').encode()
        total = prep_bytes+sum(x['bytes'] for x in files.values())+len(encoded)
        if total == delivery['export_bytes_including_this_closure']:
            break
        delivery['export_bytes_including_this_closure'] = total
    assert prep_bytes <= LIMITS['preparation'] and total <= LIMITS['export']
    for group, limit in [('source','source_total'),('archive','archives'),('admin','administration'),('temp','temp')]:
        assert groups[group] <= LIMITS[limit]
    assert groups['closure'] <= LIMITS['closure']
    assert groups['admin']+len(encoded) <= LIMITS['administration']
    save('delivery-closure.json', delivery)
    assert prep_bytes+sum(x.stat().st_size for x in p.rglob('*') if x.is_file()) == total
    print(json.dumps(dict(primary=primary, primary_summary=first, diagnosis=stats['diagnosis'], seconds=terminal['seconds'],
                         job=terminal['job'], export_bytes=total, preparation_bytes=prep_bytes,
                         delivery_sha256=sha(p/'delivery-closure.json')), ensure_ascii=False))


if __name__ == '__main__':
    main()
