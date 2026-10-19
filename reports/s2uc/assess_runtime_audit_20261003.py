"""Read saved neutral diagnosis only; never invokes replay or changes bindings."""
import json
from collections import defaultdict
from pathlib import Path
from tools import s2uc_runtime_audit as a

ROOT=a.ROOT
OUT=ROOT/'reports/s2uc/runtime-neutral-audit-assessment-20261003-01'


def main():
    binding=a.verify()
    closure=a.frozen.read(a.OUT/'closure.json')
    assert closure['status']=='PASS'
    for name,item in closure['files'].items():
        p=a.OUT/name
        assert p.stat().st_size==item['bytes'] and a.frozen.sha(p)==item['sha256']
    measurements=a.frozen.read(a.OUT/'measurements.json')
    checks=a.frozen.read(a.OUT/'equivalence.json')
    assert len(measurements)==18 and len(checks)==8
    assert all(c['on_off_equal'] and c['complete_release'] for c in checks)
    assert all(c['anchor_equal'] is (True if c['arm']=='M' else None) for c in checks)
    totals={mode:{'wall_ns':defaultdict(int),'cpu_ns':defaultdict(int),'replay_wall_ns':0} for mode in ('ON','OFF')}
    paired=[];anchors=[];verified=[]
    for case in ('N1','N2'):
        anchor=next(m for m in measurements if m['case']==case and m['mode']=='ANCHOR')
        for arm in a.ARMS:
            pair={m['mode']:m['timing'] for m in measurements if m['case']==case and m['arm']==arm and m['mode']!='ANCHOR'}
            raw={mode:a.frozen.read(a.OUT/f'{case}-{arm}-{mode}.json') for mode in pair}
            canonical={mode:json.dumps(a.semantic(r),sort_keys=True,separators=(',',':'),allow_nan=False).encode() for mode,r in raw.items()}
            assert canonical['ON']==canonical['OFF']
            if arm=='M':
                original=a.frozen.read(a.OUT/f'{case}-M-anchor.json')
                assert a.semantic(original)==a.semantic(raw['ON'])
                anchors.append(dict(case=case,original_seconds=anchor['timing']['replay_wall_ns']/1e9,
                    instrumented_seconds=pair['ON']['replay_wall_ns']/1e9,
                    instrumented_to_original=pair['ON']['replay_wall_ns']/anchor['timing']['replay_wall_ns']))
            verified.append(dict(case=case,arm=arm,canonical_equal=True,bytes=len(canonical['ON'])))
            row=dict(case=case,arm=arm,on_seconds=pair['ON']['replay_wall_ns']/1e9,off_seconds=pair['OFF']['replay_wall_ns']/1e9)
            row['ratio']=row['on_seconds']/row['off_seconds'];paired.append(row)
            for mode,t in pair.items():
                assert sum(t['wall_ns'].values())==t['partition_wall_ns']
                assert sum(t['cpu_ns'].values())==t['partition_cpu_ns']
                totals[mode]['replay_wall_ns']+=t['replay_wall_ns']
                for kind in ('wall_ns','cpu_ns'):
                    for category,value in t[kind].items():totals[mode][kind][category]+=value
    lifecycle=a.frozen.read(a.OUT/'matrix-lifecycle.json')
    events={e['event']:e for e in lifecycle['events']}
    duration=(events['worker_end_confirmed']['monotonic_ns']-events['deadline_established']['monotonic_ns'])/1e9
    assert lifecycle['status']=='NORMAL' and duration<900
    probes=a.frozen.read(a.OUT/'watchdog-probes.json')
    timeout={e['event']:e for e in probes['timeout']['events']}
    watchdog=dict(matrix_until_worker_confirmation_seconds=duration,
        deadline_to_abort_ms=(timeout['abort_requested']['monotonic_ns']-timeout['deadline_established']['deadline_monotonic_ns'])/1e6,
        abort_to_confirmation_ms=(timeout['worker_end_confirmed']['monotonic_ns']-timeout['abort_requested']['monotonic_ns'])/1e6,
        sample_closure_admin_ms=(timeout['closure_admin_finished']['monotonic_ns']-timeout['closure_admin_started']['monotonic_ns'])/1e6)
    on=totals['ON']['wall_ns'];partition=sum(on.values());traces=sum(v for k,v in on.items() if k.startswith('resource_trace_'))
    summary=dict(totals=totals,pairs=paired,anchors=anchors,watchdog=watchdog,
        on_trace_share=traces/partition,on_base_trace_share=on['resource_trace_base']/partition,
        previous_code_files=len(binding['previous_code']),historical_files=len(binding['historical']),
        canonical_verification=verified,audit_bytes=sum(p.stat().st_size for p in a.OUT.iterdir() if p.is_file()))
    OUT.mkdir(exist_ok=False)
    a.frozen.save(OUT/'analysis.json',summary)
    a.frozen.save(OUT/'verification.json',dict(audit_closure_sha256=a.frozen.sha(a.OUT/'closure.json'),
        audit_binding_sha256=a.frozen.sha(a.BINDING),all_original_hashes_verified=True,
        previous_code_files=len(binding['previous_code']),historical_files=len(binding['historical']),
        tests=a.frozen.read(a.OUT/'tests.json'),replays=18,positions_per_replay=80,
        experimental_admissions=1440,reference_advances=1440,canonical_pairs=8,original_M_anchors=2,
        raster_replays=0,operative_repair=False))
    lines=['# Neutraler Laufzeitaudit – fachlicher Abschluss (2026-10-03)', '',
        'Ergebnis: Die acht gepaarten Diagnosen sind abgeschlossen. Hauptkostenquelle ist der zeilenweise Ressourcenbeobachter, insbesondere `BudgetObserver.trace`. Keine operative Reparatur und kein Raster32-Replay.', '',
        '## Ausführung und Bindung', '',
        f'18 Replays × 80 Positionen: 1.440 experimentelle Aufnahmen und 1.440 Referenzfortschreibungen. Zwei feste neutrale Quellen N1/N2, M/E/K/P je ON/OFF sowie zwei unveränderte M-Originalanker. Matrix bis bestätigtem Workerende: {duration:.3f} s bei 900 s Grenze. Diagnoseexport einschließlich Abschluss: {summary["audit_bytes"]:,} Byte.',
        f'Vor Beginn und nach Abschluss geprüft: Auditplan, zwei Diagnosedateien, 71 Altdateien und {len(binding["historical"])} historische Dateien. Originalexporte und Bindungen unverändert. D01–D05: 5/5 bestanden, keine Fehler oder Skips; D01–D04 zuvor als Vorbereitung geprüft, ohne Replay. D05 enthält genau zwei Prozessproben.', '',
        '## Gemessene Kosten', '',
        '| Quelle/Arm | ON Replay s | OFF Replay s | ON/OFF |', '|---|---:|---:|---:|']
    for p in paired:lines.append(f'| {p["case"]}/{p["arm"]} | {p["on_seconds"]:.6f} | {p["off_seconds"]:.6f} | {p["ratio"]:.2f} |')
    lines+=['', 'Exklusive Kategorien, summiert über acht Replays je Modus. Diese Partition enthält auch Diagnoseaufbau und Ergebnisexport; die Replayzeiten oben schließen beides aus.', '',
        '| Kategorie | ON Wall s | OFF Wall s | ON CPU s | OFF CPU s |', '|---|---:|---:|---:|---:|']
    for category in sorted(set(totals['ON']['wall_ns'])|set(totals['OFF']['wall_ns'])):
        vals=[totals[mode][kind].get(category,0)/1e9 for kind in ('wall_ns','cpu_ns') for mode in ('ON','OFF')]
        lines.append('| '+category+' | '+' | '.join(f'{v:.6f}' for v in vals)+' |')
    lines+=['',f'Die drei Traceebenen beanspruchen {100*traces/partition:.2f}% der ON-Wall-Partition; allein der Basisbeobachter {100*on["resource_trace_base"]/partition:.2f}%. Die Kategorien summieren sich exakt zur jeweiligen gemessenen Wall-/CPU-Partition.', '',
        'Codebefund: Der Basisbeobachter durchsucht bei relevanten Traceereignissen aktive Stackframes und rekursiv deren Objektgraphen. Auch bereits als Frame erkannte Objekte werden anschließend als Dataclasses bis in ihre 48 Skalarwerte durchlaufen. Die abgeleiteten Beobachter dispatchen zusätzlich bei weiteren Python-Ereignissen. Die Messung belegt die dominierende Traceebene; sie isoliert nicht den Anteil einzelner Visitor-Zweige oder einzelner Path-Aufrufe.', '',
        'Die OFF-Messung unterdrückt ausschließlich sys.settrace in der isolierten Replaykopie. Die unveränderten Adapteroperationen, sonstigen Ressourcenprüfungen, Heapbeobachtung und Referenzfortschreibung bleiben. Der ON/OFF-Unterschied zeigt Beobachtungskosten in diesen Fixtures, keine bewiesene Geschwindigkeit einer noch nicht implementierten Reparatur.', '',
        '## Timerperturbation und Messgrenzen', '',
        '| Quelle | Original M s | Diagnose M ON s | Diagnose/Original |', '|---|---:|---:|---:|']
    for p in anchors:lines.append(f'| {p["case"]} | {p["original_seconds"]:.6f} | {p["instrumented_seconds"]:.6f} | {p["instrumented_to_original"]:.3f} |')
    lines+=['', 'Hooks verändern Stacktiefe, Traceereignisse und Allokationen. Policy-/Belegzeiten enthalten verbleibende Dispatch-/Hookkosten; sie sind keine exakt bereinigten Algorithmuszeiten. Der Rest `replay_other` enthält Aufbau, Schleifen-/Prüfverwaltung und nicht separat erfasste Arbeit. `outside_partition_ns` steht pro Messung in den Rohdaten. Prozess-CPU-Zeit ist grob quantisiert; Nullwerte kleiner Kategorien bedeuten nicht kostenlosen Betrieb. Keine Statistik aus Wiederholungen, keine Warmups. Dateiausgabe misst open/write/close ohne fsync; sie belegt keinen physischen Datenträgerdurchsatz.', '',
        '## Fachliche Gleichheit', '',
        '8/8 ON/OFF-Paare sind nach Entfernung ausschließlich des Feldes `resources` kanonisch byteidentisch. Beide M-Paare stimmen außerdem mit dem jeweils unveränderten Original-M überein. E/K/P werden nicht mit einer anderen Policy verglichen. Enthalten sind Entscheidungen/Receipts, Fehlerupdates, Aufnahmen und Originalbestände, Zustandshashes, Endziel 81, Ausgabefreigabe, EMA-Löschung und terminales Cleanup. Alle 18 Replays haben ihre terminalen Zustände freigegeben.',
        'N2 konkurrierende Prognosen pro Arm: '+', '.join(f'{c["arm"]}={c["competing_forecasts"]}' for c in checks if c['case']=='N2')+'. Die Aussagen gelten für diese zwei Fixtures; keine allgemeine Gleichheit oder Ressourcenqualifikation daraus ableiten. OFF und zeitinstrumentiertes ON sind ausdrücklich keine operativen Ressourcenbelege.', '',
        '## Zeitwächter', '',
        f'Normalprobe und Abbruchprobe bestanden. Bei der Abbruchprobe: Anforderung {watchdog["deadline_to_abort_ms"]:.3f} ms nach Deadline; bestätigtes Workerende weitere {watchdog["abort_to_confirmation_ms"]:.3f} ms später. Protokollierte Beispiel-Abschlussserialisierung: {watchdog["sample_closure_admin_ms"]:.3f} ms. UTC und monotone Zeit sind für Deadlinefestlegung, Abbruchanforderung, bestätigtes Workerende und Beginn/Ende dieser Verwaltung getrennt gespeichert.',
        'Die Bestätigung nach join ist kein exakt gemessener Todeszeitpunkt. Der historische Raster32-Workerstop bleibt UNKNOWN_NOT_RECONSTRUCTED. Die prototypische Verwaltungsphase misst nur ihre eigene Serialisierung, nicht die spätere gesamte Dateiversiegelung. Die operative supervise-Funktion wurde nicht geändert.', '',
        '## Genau ein minimaler Reparaturvorschlag – noch nicht umgesetzt', '',
        'Den rekursiven Ressourcenvisitor um einen sicheren Frame-Blattfall ergänzen: Frame-Identität weiterhin zählen, aber nachgewiesen unveränderliche reine Skalarfelder nicht erneut rekursiv besuchen. Nur exakt typisierte Frames mit unveränderlichem tuple aus echten floats und skalaren Bindungsfeldern dürfen den kurzen Pfad verwenden. Für mutable/custom Payloads, Unterklassen oder ungeklärte Typinvarianten bleibt der bisherige vollständige Visitor. Die derzeitige Frame-Validierung prüft Werte, erzwingt aber keinen tuple-Typ; ein bedingungsloses return nach isinstance(Frame) wäre daher unzureichend. Kein Abschalten von Traceereignissen, kein Caching fachlicher Entscheidungen, keine Policyänderung.', '',
        'Notwendige Abnahme dieses einen eng begrenzten Hüllenpatches: alter/neuer Visitor mit identischen erreichbaren Frame-IDs, Outputslots, transienten Maxima und Budgetfehlern; Grenz-/Überschreitungsfälle, Aliasfälle, sechs Hypothesen, Eviction/Promotion und Fehlercleanup sowie mutable/custom-Payload-Fallback prüfen. Fachbelege vor/nachher pro gleicher Policy vollständig vergleichen. Anschließend separat freigegebene neutrale ON-Messung bei voller Ressourcenbeobachtung; tatsächliche Zeitersparnis und Zusatzspeicher messen. Erst diese Abnahme könnte eine operative Ressourcenqualifikation begründen. Vor einem späteren bewachten Evaluationslauf sind die hier geprüften getrennten Lebenszyklusereignisse als Protokollanforderung zu übernehmen; dies ist keine zweite Optimierungsalternative und keine jetzige Ausführungsfreigabe.', '',
        'Raster32 bleibt geschlossen: TIME_LIMIT, globale Kriterien NOT_EVALUABLE, keine Fortsetzung oder fehlenden Arme. Zuständig für die nächste Entscheidung ist der Projektleiter: begrenzten Visitor-Patch mit den genannten Abnahmekriterien freigeben oder ändern.', '',
        '## Belege', '',
        '- `analysis.json`: vollständige Summen, Paare, Anker und Zeitwächterdifferenzen.',
        '- `verification.json`: Hashprüfung, Umfang und vollständige Test-IDs.',
        '- `../runtime-neutral-audit-20261003-01/`: versiegelte Rohbelege, 16 Timingdateien, acht Gleichheitsprüfungen, zwei Quellen, Prozessproben und Abschluss.',
        '- Diagnosecode: `tools/s2uc_runtime_audit.py`; Tests: `tests/test_s2uc_runtime_audit.py`; Plan/Bindung unter `docs/S2UC_NEUTRALER_LAUFZEITAUDIT_*_20261003.*`.', '']
    (OUT/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    total=summary['audit_bytes']+sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())+Path(__file__).stat().st_size+a.BINDING.stat().st_size+a.PLAN.stat().st_size+sum((ROOT/n).stat().st_size for n in a.NEW)
    assert total+65536<a.LIMIT
    a.verify()
    a.frozen.save(OUT/'closure.json',dict(status='PASS',package_bytes_before_this_closure=total,
        closure_reserve=65536,limit=a.LIMIT,assessment_script_sha256=a.frozen.sha(Path(__file__)),
        files={p.name:dict(bytes=p.stat().st_size,sha256=a.frozen.sha(p)) for p in OUT.iterdir() if p.is_file()}))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
