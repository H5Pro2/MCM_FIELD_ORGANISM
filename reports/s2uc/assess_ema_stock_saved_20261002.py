"""Read saved once-only results. No replay, material generation, or system edits."""
import json
from pathlib import Path
from tools import s2uc_ema_stock as s
from tools._s2uc_bounded_audio import OutputLedger
from tools._s2uc_ema_stock_assessment import assess
from tools._s2uc_ema_stock_observer import digest


def main():
    binding=s.verify_binding();source=s.REAL_OUT
    closure=s.read(source/'closure.json')
    assert closure['status']=='COMPLETE' and closure['error'] is None
    assert closure['experimental_admissions']==closure['internal_reference_advances']==192
    for name,info in closure['files'].items():
        assert s.sha(source/name)==info['sha256']
        assert (source/name).stat().st_size==info['bytes']
    core_files={p.name:dict(bytes=p.stat().st_size,sha256=s.sha(p)) for p in source.iterdir() if p.is_file()}
    core_bytes=sum(x['bytes'] for x in core_files.values())
    assert core_bytes==closure['charged_bytes_before_closure']+(source/'closure.json').stat().st_size
    plan=s.read(s.PLAN);results={a:s.read(source/(a+'.json')) for a in ('E','K','P')}
    assessment=s.read(source/'assessment.json')
    assert assess(results,plan)==assessment
    material=s.read(source/'source.json')
    assert digest(material['values'])==material['sha256'] and len(material['values'])==64
    assert s.read(source/'plan.json')==plan
    assert s.read(s.AUTH)==s.authorization('AUTHORIZED_ONCE')
    template=s.read(s.TEMPLATE);template['status']='AUTHORIZED_ONCE'
    assert template==s.read(s.AUTH)
    for a,r in results.items():
        assert r['admitted']==list(range(1,65)) and len(r['rows'])==31
        assert r['censored_target']==65 and r['slots_released'] and r['ema_cleared']
    rows={a:{r['target']:r for r in result['rows']} for a,result in results.items()}
    forecasts={f['target']:f for f in results['E']['forecasts']}
    updates={u['target']:u for u in results['E']['error_updates']}
    decisions=[]
    for target in plan['masks']['Gesamt']:
        f=forecasts[target];u=updates[target]
        decisions.append(dict(target=target,masks=[k for k,v in plan['masks'].items() if target in v],
            choices={a:rows[a][target]['choice'] for a in rows},
            selected_mae={a:rows[a][target]['selected_mae'] for a in rows},
            E_minus_K=rows['E'][target]['selected_mae']-rows['K'][target]['selected_mae'],
            E_minus_P=rows['E'][target]['selected_mae']-rows['P'][target]['selected_mae'],
            context_available=f['context_available'],matches=f['receipt']['matches'],ticket=f['ticket'],
            errors_before=u['before'],errors_after=u['after'],frozen_before_target=f['frozen_before_target']))
    comparisons={}
    for baseline in ('K','P'):
        key='E_minus_'+baseline
        gains=[dict(target=d['target'],gain=-d[key]) for d in decisions if d[key]<0]
        harms=[dict(target=d['target'],harm=d[key]) for d in decisions if d[key]>0]
        comparisons[baseline]=dict(gains=gains,harms=harms,
            ties=[d['target'] for d in decisions if d[key]==0],
            total_gain=sum(d['gain'] for d in gains),total_harm=sum(d['harm'] for d in harms),
            E_minus_baseline_sum=sum(d[key] for d in decisions))
    resources=dict(arms={a:r['resources'] for a,r in results.items()},
        experimental_admissions=192,internal_reference_advances=192,source_frames=64,
        raw_numeric_source_bytes=64*48*8,core_export_bytes=core_bytes,
        whole_export_limit=OutputLedger.LIMIT,closure_reserve=OutputLedger.RESERVE,
        process_RAM_claim=False,EMA_default='disabled')
    out=s.ROOT/'reports/s2uc/ema-stock-assessment-20261002-01'
    ledger=OutputLedger(out)
    # The supplementary reader uses only the unconsumed part of the SAME cap.
    ledger.LIMIT=OutputLedger.LIMIT-core_bytes
    def text_file(name,text):
        raw=text.encode('utf-8')
        assert not ledger.finalized and Path(name).name==name
        assert ledger.used+len(raw)<=ledger.LIMIT-ledger.RESERVE
        ledger.used+=len(raw)
        with (out/name).open('xb') as f:assert f.write(raw)==len(raw)
    status='NOT_EVALUABLE';error=None
    try:
        ledger.write('verification.json',dict(status='PASS',date='2026-10-02',
            binding_sha256=s.sha(s.BINDING),plan_sha256=s.sha(s.PLAN),
            authorization_sha256=s.sha(s.AUTH),bound_files=len(binding['code']),
            unchanged_legacy_files=len(binding['unchanged_legacy_code']),core_files=core_files,
            recomputed_saved_assessment_identical=True,additional_replays=0,
            script_sha256=s.sha(__file__),authorization_changed_only_status=True))
        ledger.write('single-decisions.json',decisions)
        ledger.write('all-gains-and-harms.json',comparisons)
        ledger.write('error-cell-trajectories.json',dict(target_consumption=results['E']['error_updates'],
            admission=results['E']['generation_events'],pruning=results['E']['cell_lifetime_events'],
            censored_forecast=forecasts[65],final_cells_cleared=results['E']['ema_cleared']))
        ledger.write('five-target-sets.json',assessment['metrics'])
        ledger.write('resources.json',resources)
        lines=['# MCM-KI: einmalige Bestands-Gegenprobe abgeschlossen',
            '', '2026-10-02. Genau ein gebundener synthetischer Lauf, Exit 0. Keine Wiederholung.',
            '192 Versuchsarm-Aufnahmen und separat 192 interne Referenzfortschreibungen; kein Zwischenreset.',
            '', '**Bestand/Kausalität: PASS. Erfahrungsauswahl: PASS. Nettonutzen auf V: SCHADEN.**',
            'Keine technischen Fehler, keine Abweichung von den vorab erwarteten Speicherübergängen.',
            'V besitzt an allen 7 Zielen verfügbaren Kontext. E ist dort besser als P, aber schlechter als K.',
            'Die bessere Diagnose D ersetzt den Vergleich auf V einschließlich Kaltstarts nicht.',
            '', '## Alle fünf Zielmengen', '',
            '| Menge | Anzahl | Summe E | Summe K | Summe P | MAE E | MAE K | MAE P |',
            '|---|---:|---:|---:|---:|---:|---:|---:|']
        for name in ('V','D','M','N','Gesamt'):
            arm=assessment['metrics'][name]['arms']
            vals=[str(arm['E']['count'])]+[format(arm[a][k],'.12g') for k in ('error_sum','mae') for a in ('E','K','P')]
            lines.append('| '+name+' | '+' | '.join(vals)+' |')
        lines += ['', '## Einzelentscheidungen aller 31 eingetroffenen Ziele', '',
            'C = Kontext, P = Persistenz. Positive Differenz bedeutet Mehrfehler von E.', '',
            '| Ziel | E/K/P-Wahl | Fehler E | Fehler K | Fehler P | E−K | E−P |',
            '|---:|---|---:|---:|---:|---:|---:|']
        for d in decisions:
            choices='/'.join('C' if d['choices'][a]=='CONTEXT' else 'P' for a in ('E','K','P'))
            numbers=[d['selected_mae'][a] for a in ('E','K','P')]+[d['E_minus_K'],d['E_minus_P']]
            lines.append('| '+str(d['target'])+' | '+choices+' | '+' | '.join(format(x,'.12g') for x in numbers)+' |')
        lines += ['', '## Sämtliche Gewinne und Schäden', '']
        for a,c in comparisons.items():
            lines.append('Gegen '+a+': Gewinne '+json.dumps(c['gains'])+'; Schäden '+json.dumps(c['harms'])+'.')
            lines.append('Gewinnsumme '+str(c['total_gain'])+', Schadenssumme '+str(c['total_harm'])+
                ', Netto-Fehlerdifferenz E−'+a+' = '+str(c['E_minus_baseline_sum'])+'.')
        lines += ['', '## Fehlererfahrung, Verlust und Wiederkehr', '',
            '- Ziel19: B:r2 startet kalt mit P und lernt (EC,EP)=(0.5625,0). Ziel23: A:r1 startet kalt mit P und lernt (0,0.5).',
            '- Ziel31: beide Bewertungen gleichzeitig erhalten; E wählt für B P. Die A-Zelle bleibt unverändert. Ziel35: E wählt für A C; die B-Zelle bleibt unverändert.',
            '- Ziel39: B:r2 und Bp:c5 sind mehrdeutig. Kein gültiges Ticket, kein Kontext und kein Fehlerupdate; die vollständige Fehlertabelle bleibt vor/nach Zielkonsum gleich.',
            '- Aufnahme40: Bp wird normal promoviert, B:r2 verdrängt und dessen Zelle (0.5625,0) gelöscht. Dies ist ein späteres Aufnahmeereignis, kein Update aus Ziel39.',
            '- Aufnahme48: A:r1 wird verdrängt; seine letzte Fehlerzelle (0,0.5) verschwindet. Auch C:c6 verliert bei Promotion seine Kandidatenzelle (0,0.125).',
            '- Ziel51: kein A-Treffer, keine alte A-Zelle, E/K/P wählen P und haben jeweils Fehler0.5. Der Verlust der Verfügbarkeit bleibt in M und Gesamt enthalten.',
            '- Ziel55: gleicher A-Werteverlauf als neuer Kandidat c7, leere Fehlererfahrung und P-Wahl; danach (0,0.5). Aufnahme56 löscht diese Kandidatenzelle bei Promotion.',
            '- Ziel59: neue retained-Generation r5 beginnt erneut leer und wählt P; danach eigene Erfahrung (0,0.5). Ziel63 wählt C ausschließlich aus dieser neuen Erfahrung.',
            '- Auch die Kandidatenzellen c1/c2 wurden bei Promotion8/16 gelöscht. Alle Aufnahmeereignisse und sämtliche Fehlerzellen vor/nach Zielkonsum stehen in error-cell-trajectories.json.',
            '- V enthält die drei kostentragenden kalten A-Starts23/55/59: zusammen1.5 Mehrfehler gegen K. Die B-Persistenzgewinne19/31 betragen zusammen1.125. Somit bleibt auf V ein Mehrfehler von0.375 (MAE-Differenz0.0535714285714).',
            '', '## Ressourcen und Abschluss', '',
            'Endziel65 ist zensiert, ohne Zielkonsum/Fehlerupdate; Vorschläge und EMA-Zellen nach Ende freigegeben.',
            'Memoryzustände nach jedem Frame und Matchreceipts sind zwischen E/K/P identisch. Der Replay prüfte zusätzlich seine interne Referenz.',
            '46 gebundene Dateien unverändert; alle42 bisherigen EMA-Dateien weiterhin hashidentisch. Plan und Laufzeit ebenfalls vor/nach bestätigt.',
            'Frame-Peak16/18, Vorschläge2/2, gemeinsamer Peak17/20. EMA-Zusatz4281/16384 Byte inklusive gemessener temporärer Allokation; Beobachter ausgeschlossen.',
            'Receipt457/16384 Byte, transiente UTF8-Obergrenze914/32768 Byte. Gepackter EMA-Kern416 Byte; keine Gesamtprozess-RAM-Aussage.',
            'Originalexport einschließlich Quelle und Abschluss: '+str(core_bytes)+' Byte. Er bleibt unverändert.',
            'Dieser ergänzende Bericht und seine Tabellen teilen mit dem Originalexport dasselbe4MiB-Budget. Die exakte gemeinsame Schlussbilanz steht in closure.json;256KiB bleiben bis zum Schreiben des Abschlusses reserviert.',
            'Einzelausgaben und Abschluss des Laufs: ../ema-stock-counterprobe-20261001-01/. Autorisierung ist durch den exklusiv beanspruchten Zielordner verbraucht; kein Neustart.',
            '', '## Einordnung und nächster Vorschlag an den Projektleiter', '',
            'Der Mechanismus erfüllt die geprüfte Generationstrennung und kausale Auswahl. Für diese gebundene Bestandsfolge trägt er gegenüber sofortiger Kontextnutzung jedoch zusätzliche Fehler. Kein Nettonutzenbeleg, keine allgemeine Lern- oder Clusterorganisationsaussage. EMA bleibt standardmäßig deaktiviert.',
            'Empfehlung: den technisch korrekten, wirtschaftlich negativen Befund abnehmen. Als nächsten begrenzten Konzeptschritt die kalte Persistenzwahl anhand dieser gespeicherten Kosten den Kontext-Risiken gegenüberstellen und vor einem weiteren Versuch eine prüfbare Alternative begründen. Keine generationenübergreifende Fehlerübernahme, Parameteränderung oder erneute Ausführung aus diesem Bericht ableiten.', '']
        text_file('REPORT.md','\n'.join(lines))
        s.verify_binding()
        assert all(s.sha(source/name)==info['sha256'] for name,info in core_files.items())
        status='COMPLETE'
    except BaseException as exc:
        error=type(exc).__name__+':'+str(exc)
        raise
    finally:
        files={p.name:dict(bytes=p.stat().st_size,sha256=s.sha(p)) for p in out.iterdir() if p.is_file()}
        final=dict(status=status,error=error,original_export_bytes=core_bytes,
            supplementary_bytes_before_closure=ledger.used,combined_bytes_including_closure=0,
            limit=OutputLedger.LIMIT,closure_reserve=OutputLedger.RESERVE,files=files,
            additional_replays=0,original_closure_sha256=s.sha(source/'closure.json'))
        for _ in range(10):
            total=core_bytes+ledger.used+len(json.dumps(final,sort_keys=True,separators=(',',':'),allow_nan=False).encode())+1
            if final['combined_bytes_including_closure']==total:break
            final['combined_bytes_including_closure']=total
        ledger.write('closure.json',final,final=True)
    actual=core_bytes+sum(p.stat().st_size for p in out.iterdir() if p.is_file())
    assert actual==final['combined_bytes_including_closure'] and actual<=OutputLedger.LIMIT
    print(json.dumps(dict(status=status,combined_export_bytes=actual,original_export_bytes=core_bytes,
        stock=assessment['stock_causality'],selection=assessment['experience_selection'],net=assessment['net_benefit'])))


if __name__=='__main__':main()
