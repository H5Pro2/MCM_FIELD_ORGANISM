"""Read sealed evidence only: no source generation, adapter calls or replay."""
import json
from pathlib import Path

from tools import s2uc_multi_qualification as q
from tools._s2uc_bounded_audio import OutputLedger

DEST = q.ROOT/'reports/s2uc/multi-assessment-20261003-01'
ARMS = ['U','M','E','K','P']


def key(r):
    role = r['role']
    if isinstance(role, str): role = {'retained':0,'candidate':1}[role]
    return ('r' if role == 0 else 'c')+str(r['generation'])+'/'+str(r['offset'])+'/EXACT'


def verify_run():
    c = q.read(q.OUT/'closure.json')
    assert c['status'] == 'COMPLETE' and c['error'] is None and c['completed_arms'] == ARMS
    for name, item in c['files'].items():
        p = q.OUT/name
        assert p.stat().st_size == item['bytes'] and q.sha(p) == item['sha256']
    return sum(p.stat().st_size for p in q.OUT.iterdir() if p.is_file())


def select(pairs):
    """Arithmetic interpretation of saved error pairs; no adapter/state simulation."""
    candidates = [(v[0]-v[1], k) for k,v in pairs.items() if v is not None and v[0]-v[1] < 0]
    if not candidates: return 'P'
    lowest = min(d for d,k in candidates)
    winners = [k for d,k in candidates if d == lowest]
    return winners[0] if len(winners) == 1 else 'P'


def main():
    bound = q.verify()
    qualification_bytes = q.check_qualification()
    run_bytes = verify_run()
    authorization = q.read(q.AUTH); template = q.read(q.TEMPLATE)
    assert dict(template,status='AUTHORIZED_ONCE') == authorization == q.authorization('AUTHORIZED_ONCE')
    p = q.read(q.PLAN)
    r = {a:q.read(q.OUT/(a+'.json')) for a in ARMS}
    saved = q.read(q.OUT/'assessment.json')
    assert q.assess(r,p['masks']) == saved and not saved['technical_errors']
    source = q.read(q.OUT/'source.json')
    assert len(source) == 48 and all(len(v) == 48 for v in source)
    assert all(len(v['rows']) == 23 and v['frames'] == 48 for v in r.values())
    assert len(r['U']['admissions']) == 48
    assert all(len(r[a]['admissions']) == 48 for a in ARMS[1:])
    assert all(v['states_identical'] and v['censored_target'] == 49 and v['slots_released'] for v in r.values())
    forecasts = {f['input_indices'][-1]+1:f for f in r['U']['forecasts']}
    updates = {f['target']:f for f in r['U']['updates']}
    rows = {a:{v['target']:v for v in data['rows']} for a,data in r.items()}
    decisions = []; deviations = []
    for t in p['masks']['G']:
        f, up = forecasts[t], updates[t]
        assert up['status'] == 'COMPLETE'
        before = {key(c):[c['ec'],c['ep']] for c in up['before']}
        after = {key(c):[c['ec'],c['ep']] for c in up['after']}
        observed = {key(h):h for h in up['hypotheses']}
        hypotheses = []
        actual_choice = 'P'
        for match, h in zip(f['matches'],f['hypotheses']):
            if not h['eligible']: continue
            k = key(match)
            pair = None if h['ec'] is None else [h['ec'],h['ep']]
            assert before.get(k) == pair
            o = observed[k]
            assert o['original_ordinal'] == match['ordinals'][match['offset']+2]
            assert o['live']
            wanted = [o['ec'],o['ep']] if pair is None else [.5*pair[0]+.5*o['ec'],.5*pair[1]+.5*o['ep']]
            assert after[k] == wanted
            if h['ticket']+1 == f['choice']: actual_choice = k
            hypotheses.append(dict(key=k, ticket=h['ticket'], before=pair, after=after[k],
                raw_errors=[o['ec'],o['ep']], evaluation=h['evaluation'], delta=h['delta'],
                original_ordinal=o['original_ordinal'], selected=h['ticket']+1 == f['choice']))
        assert select({h['key']:h['before'] for h in hypotheses}) == actual_choice
        assert len(hypotheses) == len(up['hypotheses'])
        selected_error = rows['U'][t]['persistence_mae'] if actual_choice == 'P' else observed[actual_choice]['ec']
        assert selected_error == rows['U'][t]['selected_mae']
        choices = {a:rows[a][t]['choice'] for a in ARMS[1:]}
        choices['U'] = actual_choice
        decisions.append(dict(target=t, choice=actual_choice, choices=choices, reason=f['decision'],
            origin_status=f['status'], hypotheses=hypotheses,
            errors={a:rows[a][t]['selected_mae'] for a in ARMS}))
    bytarget = {d['target']:d for d in decisions}
    # Fixed contractual predictions, checked against saved values only.
    expected = {19:([0.,.5],[.25,.25],'r1/0/EXACT'),23:([.25,.25],[.375,.125],'P'),
                27:([.375,.125],[.4375,.0625],'P'),31:([.4375,.0625],[.46875,.03125],'P'),
                35:([.46875,.03125],[.234375,.265625],'P'),
                39:([.234375,.265625],[.1171875,.3828125],'r1/0/EXACT'),
                43:([.1171875,.3828125],[.05859375,.44140625],'r1/0/EXACT'),
                47:([.05859375,.44140625],[.029296875,.470703125],'r1/0/EXACT')}
    for t,(b,a,c) in expected.items():
        d = bytarget[t]; h = next(h for h in d['hypotheses'] if h['key']=='r1/0/EXACT')
        if (h['before'],h['after'],d['choice']) != (b,a,c): deviations.append(dict(target=t,kind='CONTRACT_PREDICTION'))
    change = {}
    for t in (27,31):
        d = bytarget[t]
        worse = [h for h in d['hypotheses'] if h['before'] is not None and h['delta'] > 0 and
                 h['raw_errors'][0] > d['errors']['U']]
        change[t] = d['choice']=='P' and d['reason']=='NO_ESTIMATED_IMPROVEMENT' and bool(worse)
    recovery = {}
    for t in (39,43,47):
        d = bytarget[t]
        chosen = next((h for h in d['hypotheses'] if h['selected']),None)
        recovery[t] = chosen is not None and chosen['before'] is not None and chosen['delta'] < 0 and \
            chosen['raw_errors'][0] < chosen['raw_errors'][1] and d['reason']=='SELECTED_BY_ERROR'
    prechange = {h['key']:h['before'] for h in bytarget[19]['hypotheses']}
    prereturn = {h['key']:h['before'] for h in bytarget[35]['hypotheses']}
    dependency = dict(before_change_pairs=prechange, choice_from_before_change=select(prechange), actual27=bytarget[27]['choice'],
                      before_return_pairs=prereturn, choice_from_before_return=select(prereturn), actual39=bytarget[39]['choice'],
                      method='saved pair arithmetic only; no adapter or alternative replay')
    assert dependency['choice_from_before_change'] != dependency['actual27']
    assert dependency['choice_from_before_return'] != dependency['actual39']
    adaptations = dict(first_deviations=[19,35], target23='NOT_COUNTED_TIE_AND_COLD', change=change, recovery=recovery,
        causal_dependency=dependency, verdict='BELEGT_IM_ENTWICKLUNGSKONTRAST' if all(change.values()) and all(recovery.values()) and not deviations else 'NICHT_NACHGEWIESEN')
    comparisons = {}
    for arm in ARMS[1:]:
        comparisons[arm] = dict(gains=[],harms=[],ties=[])
        for t in p['masks']['G']:
            delta=rows['U'][t]['selected_mae']-rows[arm][t]['selected_mae']
            if delta == 0: comparisons[arm]['ties'].append(t)
            else: comparisons[arm]['gains' if delta<0 else 'harms'].append(dict(target=t, magnitude=abs(delta), U_minus=delta))
    net = all(saved['metrics']['H']['U']['mae'] < saved['metrics']['H'][a]['mae'] for a in ARMS[1:])
    qfacts = q.read(q.QUAL/'facts.json')
    resources = dict(qualification=qfacts['R2'], qualification_frames=qfacts['R2_frames'],
        run={a:{k:v for k,v in r[a]['resources'].items() if k!='calls'} for a in ARMS},
        U_counter_note='U original_frames_peak/output_slots_peak/combined_peak=0 are unpopulated tracing fields, NOT measured zeros; run uses asserted original_frames_upper_bound and combined_upper_bound. Output slots<=2; saved choices include context so two are used.',
        qualification_bytes=qualification_bytes, original_run_bytes=run_bytes,
        original_and_qualification_bytes=qualification_bytes+run_bytes,
        no_process_ram_claim=True)
    assert r['U']['resources']['original_frames_upper_bound'] <= 18 and r['U']['resources']['combined_upper_bound'] <= 20
    assert all(r[a]['resources']['additional_python_peak'] <= 16384 for a in ARMS)
    ledger = OutputLedger(DEST); ledger.LIMIT -= qualification_bytes+run_bytes
    ledger.write('verification.json', dict(bound_files=len(bound['code']), binding_sha256=q.sha(q.BINDING), plan_sha256=q.sha(q.PLAN),
        contract_sha256=q.sha(q.CONTRACT), authorization_status_only=True, run_manifest_sha256=q.sha(q.OUT/'closure.json'),
        analysis_script_sha256=q.sha(Path(__file__)), no_extra_replays=True, counts=dict(source_positions=48, experimental=240, reference=240),
        technical_errors=saved['technical_errors'], expectation_deviations=deviations))
    ledger.write('all-decisions-and-updates.json',decisions)
    ledger.write('all-gains-and-harms.json',comparisons)
    ledger.write('all-target-sets.json',dict(masks=p['masks'],metrics=saved['metrics']))
    ledger.write('adaptation.json',adaptations)
    ledger.write('resources.json',resources)
    lines = ['# MCM-KI: einmaliger48er-Vergleich U/M/E/K/P abgeschlossen','',
        '2026-10-03. Genau48 Quellpositionen,240 Arm-Aufnahmen plus240 interne Referenzfortschreibungen. Exit0.',
        '**Anpassung nach Wechsel und Rueckkehr: BELEGT_IM_ENTWICKLUNGSKONTRAST. Strikter Nettonutzen auf H: '+('BELEGT' if net else 'NICHT_NACHGEWIESEN')+'.**',
        'Keine technischen Fehler oder Abweichungen von den konkreten Vertragsprognosen.61 Dateien,Plan,Vertrag und Laufzeit unveraendert.',
        'Keine Zusatzfolge,Optimierung,Wiederholung oder neue Messung bei dieser Nachauswertung. Endziel49 zensiert,Ausgaben freigegeben.',
        'Unabhaengiger Evaluationsnutzen NICHT_GEPRUEFT; Defaults deaktiviert.','',
        '## Alle vorab festgelegten Zielmengen','',
        'Je Feld Fehlersumme / MAE. Alle Anfangskosten und ersten Abweichungen bleiben in H/G. N partitioniert G mit H; F/A_W/A_R sind Diagnosen.','',
        '| Menge | Ziele | U | M | E | K | P |','|---|---|---:|---:|---:|---:|---:|']
    for mask in ('G','H','N','F','A_W','A_R'):
        lines.append('| '+mask+' | '+','.join(map(str,p['masks'][mask]))+' | '+' | '.join(
            str(saved['metrics'][mask][a]['error_sum'])+' / '+str(saved['metrics'][mask][a]['mae']) for a in ARMS)+' |')
    lines += ['', '## Vollstaendige Gewinne und Schaeden','', 'Alle nicht genannten Differenzen sind0; genaue Gleichstandsziele in all-gains-and-harms.json.']
    for a,c in comparisons.items(): lines.append('- U gegen '+a+': Gewinne '+json.dumps(c['gains'])+'; Schaeden '+json.dumps(c['harms'])+'.')
    lines += ['', '## Tatsaechlich eingefrorene Entscheidungen','',
        'P=Persistenz;r/c bezeichnet retained/candidate,danach Generation und Offset. Herkunftsmehrdeutigkeit bleibt sichtbar.',
        '| Ziel | Wahl U/M/E/K/P | Fehler U/M/E/K/P | U-Grund |','|---:|---|---|---|']
    for d in decisions: lines.append('| '+str(d['target'])+' | '+' / '.join(str(d['choices'][a]) for a in ARMS)+' | '+
        ' / '.join(str(d['errors'][a]) for a in ARMS)+' | '+d['reason']+' |')
    lines += ['', '## Alle berechtigten Hypothesen vor und nach Feedback','',
        'Keine Zahlen aus einer neuen Simulation: vorab gespeicherte Receiptwerte und tatsaechliche Feedbackbelege. Paare=(EC,EP); KALT ist keine Nullbewertung.',
        '| Ziel | Hypothese | Vorher | Rohfehler am Ziel | Nachher | Gewaehlt |','|---:|---|---|---|---|---|']
    for d in decisions:
        for h in d['hypotheses']:
            lines.append('| '+str(d['target'])+' | '+h['key']+' | '+('KALT' if h['before'] is None else str(h['before']))+
                ' | '+str(h['raw_errors'])+' | '+str(h['after'])+' | '+str(h['selected'])+' |')
    lines += ['', '## Anpassung und Grenzen','',
        '19: erste nicht vorhersehbare Wechselabweichung; U waehlt X und verliert0.5. Erst Feedback19 erzeugt(0.25,0.25).',
        '23: P aus X-Gleichstand und kaltem Y. Kein Anpassungsbeleg. Feedback23 bewertet auch beide nicht ausgewaehlten Kontexte: X(0.375,0.125),Y(0,0).',
        '24: Y:c2->r2 behaelt(0,0) durch direkte Promotion. Kein zusaetzliches Update,keine Ticketumleitung.',
        '27/31: P beruht auf warmem,gegen P strikt schlechterem X; dessen aktueller Fehler0.5 ist groesser als P0. Y ist wertgleich mit P und bleibt Gleichstand. Dieser Gleichstand allein wird NICHT als Anpassung gezaehlt.',
        '35: erste Rueckkehrabweichung,P verliert0.5. Fortgesetztes Feedback trotz Nichtauswahl macht X von(0.46875,0.03125) zu(0.234375,0.265625). Y wird(0.25,0.25).',
        '39: X ist einziges negatives EC-EP=-0.03125 und wird tatsaechlich gewaehlt. An43/47 bleibt dies erhalten. Die Frist43 wird bereits an39 erfuellt.',
        'Gespeicherte Vorwechselpaare wuerden X statt des tatsaechlichen P an27 waehlen; gespeicherte Vor-Rueckkehrpaare P statt X an39. Das ist reine Auswertung vorliegender Paare,kein Ersatzlauf oder Zustandsaustausch.',
        'M/E/K/P liefern in A_W ebenfalls fehlerfreies P. Dort besteht KEIN zusaetzlicher Vorhersagegewinn; bei M/E/K beruht P auf fehlendem eindeutigen Kontext. Der spezifische Zusatzgewinn von U gegen M liegt an39/43/47.',
        'U ist auf H strikt besser als M,E,K,P,ebenso auf G. Trotzdem einzelne Schaeden: kaltes Ziel7 gegen K und Wechsel19 gegen P. Kein allgemeiner robuster Nutzen ueber weitere Folgen belegt.',
        'Der Vertragsnebensatz ueber einen moeglichen Gleichstand mit K beschreibt keinen eingetretenen Befund: auf H liegt U hier strikt unter K. Das strikte Kriterium wurde nicht geaendert.', '',
        '## Ressourcen und Integritaet','',
        'U im Lauf:5134/16384 Byte zusaetzlicher Python-Heap,416 gepackte Bytes; pro Aufruf kontrollierte Obergrenzen12 Originalframes und14 inklusive maximal2 Ausgabeplaetzen. Receipt705 Byte,UTF8-Obergrenze1410 Byte.',
        'U-Tracingzaehler mit Wert0 wurden in diesem Lauf nicht befuellt; sie sind KEINE gemessenen Nullverbraeuche. Die gebundene Obergrenzenpruefung ist der Laufbeleg.',
        'Qualifikation:9897/16384 Zusatzbyte,gemessene18/18 Originalframes,2/2 Ausgaben,20/20 gemeinsam;Receipt2012 Byte,UTF8-Obergrenze4024 Byte. Vollstaendige Armwerte in resources.json; kein Prozess-RAM-Beleg.',
        f'Qualifikation{qualification_bytes} Byte,Originalvergleich{run_bytes} Byte. Zusammen vor dieser Nachauswertung{qualification_bytes+run_bytes} Byte. Endsumme einschliesslich Nachauswertung in closure.json; gemeinsame Grenze4194304 Byte,Abschlussreserve262144 Byte.',
        'Originalexport und Qualifikation bleiben versiegelt. Diese Nachauswertung prueft deren Dateihashes und Bindungen; keine Adapter-/Replayausfuehrung.', '',
        '## Genau eine naechste Forschungsentscheidung','',
        'Empfehlung: einen begrenzten Gegenpruefvertrag mit zwei konkurrierenden Fortsetzungen konzipieren,die beide von Persistenz verschieden sind. Hier ist Y exakt Persistenz; belegt sind fehlergestuetzte Abwahl von X und Rueckkehr zu X,nicht die Auswahl zwischen zwei verschiedenen nichtpersistenten Fortsetzungen.',
        'Die bestehende Policy unveraendert lassen; vorab eine Folge,gleiche Ressourcen und ein falsifizierbares Auswahlkriterium festlegen. Heute keine neue Folge oder Ausfuehrungsfreigabe daraus ableiten.','']
    q.write_text(ledger,'REPORT.md','\n'.join(lines))
    q.verify(); assert q.check_qualification() == qualification_bytes and verify_run() == run_bytes
    files={f.name:dict(bytes=f.stat().st_size,sha256=q.sha(f)) for f in DEST.iterdir() if f.is_file()}
    total = qualification_bytes+run_bytes+ledger.used
    closure=dict(status='COMPLETE',files=files,qualification_bytes=qualification_bytes,original_run_bytes=run_bytes,
                 combined_before_closure=total,combined_including_closure=0,limit=4194304,reserve=262144,
                 adaptation=adaptations['verdict'],net_benefit_H='BELEGT' if net else 'NICHT_NACHGEWIESEN',
                 extra_replays=0,independent_evaluation='NICHT_GEPRUEFT')
    for _ in range(8):
        n=len(json.dumps(closure,sort_keys=True,separators=(',',':'),allow_nan=False).encode())+1
        if closure['combined_including_closure']==total+n: break
        closure['combined_including_closure']=total+n
    ledger.write('closure.json',closure,final=True)
    assert sum(f.stat().st_size for f in DEST.iterdir() if f.is_file())+qualification_bytes+run_bytes == closure['combined_including_closure']
    print(json.dumps({k:v for k,v in closure.items() if k!='files'},indent=2))


if __name__=='__main__': main()
