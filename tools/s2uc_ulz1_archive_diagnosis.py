"""Post-hoc ULZ1 archive diagnosis; no policy, source generator or replay imports."""
import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARC = ROOT / 'reports/s2uc/ulz1-comparison-20261004-01'
OLD = ROOT / 'reports/s2uc/ulz1-assessment-20261004-01'
OUT = ROOT / 'reports/s2uc/ulz1-diagnosis-20261004-01'
LABEL = ['H1', 'P', 'A', 'B', 'Z']


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def csvsave(name, rows):
    with (OUT / name).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def verify(directory):
    closure = read(directory / 'closure.json')
    for name, meta in closure['files'].items():
        p = directory / name
        assert p.stat().st_size == meta['bytes'] and sha(p) == meta['sha256'], p
    return len(closure['files'])


def lineage(h):
    return tuple(h['ordinals']), h['offset']


def scopes(row):
    c, b = row['condition'], row['block']
    result = [c + '_Y_all']
    if c == 'S' and 33 <= b <= 128:
        result.append('S_primary_33_128')
    if c == 'W' and 129 <= b <= 160:
        result.append('W_primary_129_160')
    return result


def main():
    assert sha(ARC / 'closure.json') == 'df4bb51d44eb4e188e4c7a41e30c4d80d56daac1758d5ec41a75df3ae9da036e'
    verified = {'run': verify(ARC), 'assessment': verify(OLD)}
    assert not OUT.exists(), 'Output exists; do not overwrite an archived diagnosis.'
    plan = read(ROOT / 'docs/S2UC_ULZ1_V1_20261004_PLAN.json')
    cycles = {x['case']: x for x in read(OLD / 'cycles.json')}
    targets, contexts, lifecycle = [], {}, []
    checks = Counter()
    non_y = Counter()
    age_stats = defaultdict(Counter)
    for spec in plan['cases']:
        name = spec['id']
        src = read(ARC / (name + '-source.json'))
        raw = json.loads(gzip.decompress((ARC / (name + '-case.json.gz')).read_bytes()))
        assert raw['complete'] and raw['reference_equal'] and raw['lifecycle_equal']
        assert raw['L']['shared_stock_with_U']
        histories = {a: defaultdict(list) for a in ('U', 'L')}
        cells = {a: {} for a in ('U', 'L')}
        def label(ordinal):
            return LABEL[src['ids'][ordinal - 1]]
        for pair, ur, lr in zip(raw['rows'], raw['U']['rows'], raw['L']['rows'], strict=True):
            t = pair['target']
            assert t == ur['target'] == lr['target']
            is_y = t >= 19 and (t - 19) % 4 == 0
            ctx = {}
            outputs = {}
            for arm, row in [('U', ur), ('L', lr)]:
                hs = []
                for h in row['hypotheses']:
                    key = lineage(h)
                    before = cells[arm].get(key)
                    assert before == h['before'], (name, t, arm, h, before)
                    checks['pretarget_cells_reconstructed'] += 1
                    history = histories[arm][key]
                    assert all(x['target'] < t for x in history)
                    hs.append(dict(h, output=label(h['original']),
                                   delta=None if before is None else before[0] - before[1],
                                   valid_feedback_count=len(history),
                                   first_feedback_target=history[0]['target'] if history else None,
                                   last_feedback_target=history[-1]['target'] if history else None,
                                   age_since_first_feedback=t-history[0]['target'] if history else None,
                                   history=list(history)))
                selected = row['selected']
                ordinal = selected['original'] if selected else t - 1
                outputs[arm] = label(ordinal)
                actual = src['catalog'][src['ids'][t - 1]]
                output = src['catalog'][src['ids'][ordinal - 1]]
                error = sum(abs(F(x)-F(y)) for x, y in zip(actual, output, strict=True)) / len(actual)
                assert error == F(row['error']) == F(pair[arm])
                checks['output_errors_recomputed'] += 1
                warm = [h for h in hs if h['delta'] is not None]
                best = min((h['delta'] for h in warm), default=0)
                winners = [h for h in warm if h['delta'] == best]
                expected = winners[0]['original'] if best < 0 and len(winners) == 1 else None
                assert expected == (selected['original'] if selected else None)
                checks['archived_choices_explained_by_cells'] += 1
                ctx[arm] = {'output': outputs[arm], 'reason': row['reason'],
                            'no_choice_reason': row['no_choice_reason'], 'hypotheses': hs}
            assert [(lineage(h), h['before'] is None) for h in ur['hypotheses']] == [(lineage(h), h['before'] is None) for h in lr['hypotheses']]
            if is_y:
                assert outputs['U'] in 'ABZP' and outputs['L'] in 'ABZP'
                benefit = F(pair['L']) - F(pair['U'])
                group = ('same' if outputs['U'] == outputs['L'] else
                         'context_persistence' if 'P' in outputs.values() else 'different_context')
                ages = [h['valid_feedback_count'] for h in ctx['U']['hypotheses']]
                r = dict(case=name, condition=name[-1], target=t, block=(t-15)//4,
                         U_output=outputs['U'], L_output=outputs['L'], actual=label(t),
                         pair=outputs['U']+'/'+outputs['L'], group=group,
                         U_error=pair['U'], L_error=pair['L'],
                         gain=str(max(benefit, F(0))), harm=str(max(-benefit, F(0))),
                         net=str(benefit), age_counts=json.dumps(ages),
                         unequal_ages=len(set(ages)) > 1,
                         cold_cells=sum(h['before'] is None for h in ur['hypotheses']))
                targets.append(r)
                if benefit:
                    contexts[name, t] = ctx
                for scope in scopes(r):
                    age_stats[scope]['targets'] += 1
                    age_stats[scope]['unequal_feedback_counts'] += r['unequal_ages']
                    age_stats[scope]['any_cold'] += r['cold_cells'] > 0
                    age_stats[scope]['max_feedback_count'] = max(age_stats[scope]['max_feedback_count'], max(ages, default=0))
            else:
                assert pair['U'] == pair['L']
                non_y[name[-1]] += 1
            # Reconstruct only observed, valid feedback; never run a policy or source.
            for arm, row in [('U', ur), ('L', lr)]:
                for u in row['updates']:
                    if not u['live']:
                        checks['invalid_feedback_ignored'] += 1
                        continue
                    key = lineage(u)
                    old = cells[arm].get(key)
                    new = [u['ec'], u['ep']]
                    if arm == 'U' and old is not None:
                        new = [.5*old[0]+.5*u['ec'], .5*old[1]+.5*u['ep']]
                    cells[arm][key] = new
                    histories[arm][key].append(dict(target=t, ec=u['ec'], ep=u['ep'],
                                                   key=u['key'], after=new))
                    checks['valid_feedback_updates'] += 1
        # Promotion is a role/key change; verify values carried to the next boundary.
        evs = raw['U']['events']
        for i, e in enumerate(evs[:-1]):
            before = {tuple(x['ordinals']): x for x in e['before']['retained']}
            after = {tuple(x['ordinals']): x for x in e['after']['retained']}
            promoted = set(after) - set(before)
            for original in promoted:
                candidate = e['before']['candidate']
                assert candidate and tuple(candidate['ordinals']) == original
                for arm in ('U', 'L'):
                    prev = {tuple(x['key']): x['values'] for x in raw[arm]['events'][i]['cells']}
                    nxt = {tuple(x['key']): x['values'] for x in raw[arm]['events'][i+1]['cells']}
                    for k, v in prev.items():
                        if k[:2] == (1, candidate['generation']):
                            nk = (0, after[original]['generation'], k[2])
                            assert nxt[nk] == v, (name, e['index'], arm, k)
                            checks['promotion_cells_carried_unchanged'] += 1
            if promoted or set(before) - set(after):
                lifecycle.append(dict(case=name, at=e['index'],
                                      promoted=[dict(after[x], output=label(x[2])) for x in sorted(promoted)],
                                      evicted=[dict(before[x], output=label(x[2])) for x in sorted(set(before)-set(after))]))
    assert len(targets) == 16384
    groups = defaultdict(list)
    for r in targets:
        for scope in scopes(r):
            groups[scope, r['pair']].append(r)
    categories, totals = [], {}
    for scope in ['S_primary_33_128', 'W_primary_129_160', 'S_Y_all', 'W_Y_all']:
        subtotal = []
        for u in 'ABZP':
            for l in 'ABZP':
                rows = groups[scope, u+'/'+l]
                gain = sum((F(r['gain']) for r in rows), F(0))
                harm = sum((F(r['harm']) for r in rows), F(0))
                cat = dict(scope=scope, pair=u+'/'+l,
                           group='same' if u == l else 'context_persistence' if 'P' in (u,l) else 'different_context',
                           count=len(rows), improved=sum(F(r['net']) > 0 for r in rows),
                           worse=sum(F(r['net']) < 0 for r in rows),
                           equal=sum(F(r['net']) == 0 for r in rows),
                           gain=str(gain), harm=str(harm), net=str(gain-harm))
                categories.append(cat)
                subtotal.append(cat)
        total = {k: sum(x[k] for x in subtotal) for k in ('count','improved','worse','equal')}
        total.update({k: str(sum((F(x[k]) for x in subtotal), F(0))) for k in ('gain','harm','net')})
        mask = 'G_Y' if scope.endswith('all') else 'Y_33_128' if scope.startswith('S') else 'Y_129_160'
        expected = next(h for h in read(ARC/'assessment.json')['harms'] if h['condition'] == scope[0] and h['mask'] == mask)
        for k in ('improved','worse','equal'):
            assert total[k] == expected[k]
        assert F(total['gain']) == F(expected['gain_sum']) and F(total['harm']) == F(expected['harm_sum'])
        totals[scope] = total
    # Deterministic post-hoc examples: max positive/negative contribution per nonzero
    # primary pair; plus first maximum harm in each full condition.
    chosen = {}
    for (scope, pair), rows in sorted(groups.items()):
        if 'primary' not in scope:
            continue
        for sign, reason in [(1, 'gain'), (-1, 'harm')]:
            eligible = [r for r in rows if sign*F(r['net']) > 0]
            if eligible:
                r = sorted(eligible, key=lambda r: (-sign*F(r['net']), r['case'], r['target']))[0]
                chosen.setdefault((r['case'], r['target']), []).append(scope+':'+pair+':'+reason)
    maxima = []
    for c in 'SW':
        rows = [r for r in targets if r['condition'] == c]
        maximum = max(F(r['harm']) for r in rows)
        ties = [r for r in rows if F(r['harm']) == maximum]
        maxima.extend(ties)
        chosen.setdefault((ties[0]['case'], ties[0]['target']), []).append(c+':first_full_max_harm')
    examples = []
    lookup = {(r['case'],r['target']):r for r in targets}
    for key, reasons in sorted(chosen.items()):
        r = lookup[key]
        events = cycles[r['case']]['events']
        past = [e for e in events if e['at'] < r['target']]
        future = [e for e in events if e['at'] >= r['target']]
        examples.append(dict(target=r, selected_posthoc_for=reasons, decisions=contexts[key],
                             last_lifecycle_events=past[-3:], next_lifecycle_event=future[0] if future else None,
                             evidence=f"../ulz1-comparison-20261004-01/{r['case']}-case.json.gz; U/L.rows[target={r['target']}]; earlier rows and U.events"))
    OUT.mkdir()
    csvsave('targets.csv', targets)
    csvsave('categories.csv', categories)
    csvsave('maximum-harms.csv', maxima)
    save('examples.json', examples)
    save('lifecycle.json', lifecycle)
    verification = dict(status='COMPLETE_ARCHIVE_DIAGNOSIS', archive_files_verified=verified,
                        run_closure_sha256=sha(ARC/'closure.json'), assessment_closure_sha256=sha(OLD/'closure.json'),
                        script_sha256=sha(Path(__file__)), checks=dict(checks), totals=totals,
                        age_statistics=dict(age_stats), non_Y_equal_targets=dict(non_y),
                        example_count=len(examples), maximum_harm_targets=len(maxima),
                        replay_executed=False, inference='post-hoc descriptive only')
    save('verification.json', verification)
    lines = ['# ULZ1: abschließende Archivdiagnose (2026-10-04)', '',
             '**ULZ1 wissenschaftlich abgeschlossen. U bleibt unverändert; A1/K1 aus.**', '',
             'Ausschließlich Auswertung vorhandener, hashgeprüfter Belege. Keine Replays, neuen Quellen, Regeländerungen oder neuen Konfidenztests.',
             'Die Kategorien und Beispiele sind nachträgliche Diagnose, keine bestätigenden Untergruppenbefunde.', '',
             '## Definition und exakte Bilanz', '',
             'Ausgabepaar = U/L. P bezeichnet Persistenz H2; A/B/Z die tatsächlichen Katalogvektoren, unabhängig von Originalidentität oder Speicherrolle.',
             'Gewinn=max(Fehler L−Fehler U,0), Schaden=max(Fehler U−Fehler L,0), Netto=Gewinn−Schaden. Positives Netto begünstigt U; es hat das umgekehrte Vorzeichen zu D=U−L.',
             'Alle Fehler wurden aus den 48 archivierten Vektorkomponenten exakt mit rationaler Arithmetik rekonstruiert. Tabellenwerte sind exakte endliche Dezimalzahlen.',
             'Die CSV-Dateien speichern dieselben Summen als exakte Brüche. Überlappende Fenster nicht addieren.', '']
    for scope, total in totals.items():
        lines += ['### '+scope, '', '| U/L | Anzahl | Gewinne | Schäden | Netto |', '| --- | ---: | ---: | ---: | ---: |']
        for cat in categories:
            if cat['scope'] == scope:
                lines.append(f"| {cat['pair']} | {cat['count']} | {float(F(cat['gain'])):g} | {float(F(cat['harm'])):g} | {float(F(cat['net'])):g} |")
        lines.append(f"| **Gesamt** | **{total['count']}** | **{float(F(total['gain'])):g}** | **{float(F(total['harm'])):g}** | **{float(F(total['net'])):g}** |")
        lines += ['', f"U besser/schlechter/gleich: {total['improved']}/{total['worse']}/{total['equal']}. Exakter Abgleich mit bestehender Gesamtauswertung bestanden.", '']
    lines += ['Der vollständige G-Verlauf enthält zusätzlich je 8.416 Präfix-/Gerüstziele mit identischen U/L-Fehlern. Seine Gewinn-, Schadens- und Nettosummen entsprechen exakt den vollständigen Y-Summen.',
              'S und W zusammen: 16.384 Y-Ziele, Gewinn 153,25, Schaden 81,875, Netto 71,375. Diese gepoolte Beschreibung ist kein zusätzlicher unabhängiger Nachweis.', '',
              '## Entscheidungsrekonstruktion und Beispiele', '',
              'Zellen werden über Originalordinalfolge und Offset verfolgt, auch beim Rollenwechsel Kandidat→Retained. Nur frühere Updates mit live=true zählen. Erstfeedback wird direkt übernommen; danach U=.5*alt+.5*Feedback in archivierter binary64-Reihenfolge, L=letztes Feedback.',
              'Jeder vor der Entscheidung gespeicherte Zellwert und jede beobachtete Wahl wurde gegen diese Rückmeldungen geprüft. Ein eindeutiges negatives Minimum EC−EP wählt den Kontext; sonst P. Zukünftige Rückmeldungen werden dafür nicht verwendet.',
              'Die Beispiele wurden nachträglich deterministisch gewählt: je nichtleerem Primär-Ausgabepaar der größte Gewinn und Schaden, bei Gleichstand Fall-ID/Ziel; zusätzlich der erste maximale Schaden je Gesamtbedingung. Alle maximalen Schäden stehen in maximum-harms.csv.', '']
    for i, e in enumerate(examples, 1):
        r = e['target']
        lines += [f"### Beispiel {i}: {r['case']}, Ziel {r['target']} (Y{r['block']})", '',
                  f"Ausgabe {r['pair']}, tatsächlich {r['actual']}; Fehler U={r['U_error']}, L={r['L_error']}; Netto={float(F(r['net'])):g}.", '',
                  '| Arm | Hypothese/Original | Rolle | EC | EP | EC−EP | gültige frühere Feedbacks | letztes Feedback (Ziel: ec/ep) |',
                  '| --- | --- | --- | ---: | ---: | ---: | ---: | --- |']
        for arm, decision in e['decisions'].items():
            for h in decision['hypotheses']:
                b = h['before']
                last = h['history'][-1] if h['history'] else None
                lines.append(f"| {arm} | {h['output']}/{h['original']} | {'Retained' if h['key'][0]==0 else 'Kandidat'} | {b[0] if b else 'kalt'} | {b[1] if b else 'kalt'} | {h['delta']} | {h['valid_feedback_count']} | {str(last['target'])+': '+str(last['ec'])+'/'+str(last['ep']) if last else 'keines'} |")
        for arm, decision in e['decisions'].items():
            lines += ['', f"{arm} gibt {decision['output']} aus: {decision['reason']} / {decision['no_choice_reason']}.", '']
        lines += [f"Beleg: examples.json, Eintrag {i-1}; {e['evidence']}. Dort vollständige frühere Feedbackfolge, Zellalter und benachbarte Lebenszyklusereignisse.", '']
    lines += ['## Zellenalter, Promotion und Verdrängung', '',
              'Zellenalter wird als Anzahl gültiger früherer Feedbacks gemessen; zusätzlich stehen erstes/letztes Feedbackziel und Abstand seit Erstfeedback in den Beispielen. Das ist nicht das Alter des Originalframes.', '',
              '| Fenster | Ziele mit ungleichen Feedbackzahlen | Ziele mit kalter Zelle | maximale Feedbackzahl |', '| --- | ---: | ---: | ---: |']
    for scope in totals:
        a = age_stats[scope]
        lines.append(f"| {scope} | {a['unequal_feedback_counts']} | {a['any_cold']} | {a['max_feedback_count']} |")
    lines += ['', f"{checks['promotion_cells_carried_unchanged']} Zellübernahmen bei Promotion in beiden Armen gegen die nächste archivierte Grenze bitwertgleich geprüft. Promotion setzt die Erfahrung nicht zurück. Alle übrigen Vorzustände wurden ebenfalls exakt aus gültigem Feedback rekonstruiert.",
              'Verdrängung entfernt einen Originalbestand samt seinen Zellen; ein späteres neues Original desselben Ausgabevektors erbt dessen Fehlergeschichte nicht. Die nachfolgende kalte Zelle bleibt bis zum eigenen gültigen Erstfeedback ohne bewertbare Erfahrung.',
              'U/L teilen denselben Speicherlebenszyklus und dieselben Feedbackgelegenheiten. Unterschiedliche Werte entstehen durch die Bewertungsregel und unterschiedlich lange Vorgeschichten einzelner Hypothesen. Nähe eines Schadens zu Promotion oder Verdrängung beweist keinen eigenständigen Verdrängungsschaden; ein isolierendes Gegenexperiment fehlt.', '',
              '## Wissenschaftlicher Abschluss', '',
              'Der vorab bestimmte Stabilitätsvorteil bleibt belegt: D=−0,0048828125, 97,5%-Intervall [−0,006591796875; −0,003214009603].',
              'Früher Wechsel: D=−0,0029296875, 97,5%-Intervall [−0,006713867188; +0,0009765625]. Weder erwarteter L-Vorteil noch gegenläufiger U-Vorteil nachgewiesen; keine Gleichwertigkeitsbehauptung.',
              'Die erwartete gemeinsame Stabilitäts-/Wechselabwägung bleibt nicht nachgewiesen. Die Diagnose erklärt beobachtete Entscheidungen, erweitert aber keine Primärnachweise. Kein allgemeiner MCM-Mehrwert, Transfer oder Feld-Memory-Nachweis.',
              'ULZ1 ist damit abgeschlossen. U unverändert, L nicht übernommen, Einmalfreigabe verbraucht. LZ1-/T1-/F-Einordnungen unverändert. Eine weitere Studie benötigt eine eigenständige Forschungsfrage; aus dieser Diagnose folgt kein automatischer Folgeversuch.', '',
              '## Belege und Integrität', '',
              '[Alle Y-Ziele](targets.csv), [alle 64 Kategorien einschließlich Nullkategorien](categories.csv), [Entscheidungsketten](examples.json), [maximale Schäden](maximum-harms.csv), [Promotionen/Verdrängungen](lifecycle.json), [Prüfbilanz](verification.json).',
              '[Bestehender Ergebnisbericht](../ulz1-assessment-20261004-01/REPORT.md), [ursprünglicher Laufabschluss](../ulz1-comparison-20261004-01/closure.json).',
              'Archivbelegstellen verwenden Fall-Dateiname und eindeutiges Ziel bzw. Ereignisindex; die kompakten JSON-Dateien besitzen keine sinnvollen Textzeilennummern. Diagnoseabschluss bindet die neuen Artefakte per SHA256.']
    (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    assert verify(ARC) == verified['run'] and verify(OLD) == verified['assessment']
    save('closure.json', dict(status='COMPLETE_ARCHIVE_DIAGNOSIS', files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(OUT.iterdir())}))
    print(json.dumps(verification, indent=2))


if __name__ == '__main__':
    main()
