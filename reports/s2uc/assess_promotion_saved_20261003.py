"""Read and annotate saved S/W/L records only; no generator or replay call."""
import json
from pathlib import Path
from tools import s2uc_promotion_qualification as q
from tools._s2uc_bounded_audio import OutputLedger
from tools._s2uc_ema_stock_observer import digest


def key(c):return (c['role'],c['generation'],c['offset'],c['quality'])


def annotate(result):
    """Join existing feedback/admission receipts; do not compute new EMA states."""
    updates={u['target']:u for u in result['error_updates']}
    admissions={e['frame']:e for e in result['admissions']}
    forecasts={f['target']:f for f in result['forecasts']}
    metadata={};annotations={}
    for source_index in range(1,result['frames']+1):
        if source_index in updates:
            u=updates[source_index];assert set(metadata)=={key(c) for c in u['before']}
            ticket=u['ticket'];updated=None
            if ticket and ticket[-1]:updated=(ticket[2],ticket[0],ticket[3],ticket[4])
            following={}
            for cell in u['after']:
                k=key(cell);entry=metadata.get(k,dict(observed_targets=[],promotions=[]))
                entry=dict(observed_targets=list(entry['observed_targets']),promotions=list(entry['promotions']))
                if k==updated:entry['observed_targets'].append(source_index)
                following[k]=entry
            metadata=following
        if source_index%2==0:
            f=forecasts[source_index+1];ticket=f['ticket'];cell=None;origin=None
            if ticket and ticket[-1]:
                k=(ticket[2],ticket[0],ticket[3],ticket[4])
                cell=next((c for c in f['cells_before'] if key(c)==k),None)
                origin=metadata.get(k)
            if not f['context_available']:basis='KEIN_AUSWAEHLBARER_KONTEXT'
            elif cell is None:basis='KALTER_STANDARD'
            else:
                assert origin is not None
                if origin['promotions']:
                    last=origin['promotions'][-1]['frame']
                    basis='MITGENOMMEN_DANACH_AKTUALISIERT' if any(t>last for t in origin['observed_targets']) else 'MITGENOMMENE_ERFAHRUNG'
                else:basis='NEU_ERWORBENE_ERFAHRUNG'
            annotations[f['target']]=dict(target=f['target'],choice=f['choice'],basis=basis,
                prior_cell=cell,history=origin,censored=f['target']>result['frames'])
            for frame in (source_index-1,source_index):
                e=admissions[frame];assert set(metadata)=={key(c) for c in e['cells_before']}
                candidate=e['before']['candidate'];old_g={t['generation'] for t in e['before']['retained']}
                new=[t for t in e['after']['retained'] if t['generation'] not in old_g]
                following={}
                for c in e['cells_after']:
                    k=key(c)
                    if k in metadata:following[k]=metadata[k]
                    else:
                        assert candidate and len(new)==1 and c['role']==0 and c['generation']==new[0]['generation']
                        prior=(1,candidate['generation'],c['offset'],c['quality']);entry=metadata[prior]
                        following[k]=dict(observed_targets=list(entry['observed_targets']),
                            promotions=entry['promotions']+[dict(frame=frame,candidate=prior[1],retained=c['generation'])])
                metadata=following
    return annotations


def main():
    binding=q.verify();p=q.OUT;plan=q.read(q.PLAN);closure=q.read(p/'closure.json')
    assert closure['status']=='COMPLETE' and closure['error'] is None
    assert closure['experimental_admissions']==closure['internal_reference_advances']==384
    template=q.read(q.TEMPLATE);template['status']='AUTHORIZED_ONCE'
    assert template==q.read(q.AUTH)==q.auth('AUTHORIZED_ONCE')
    for name,info in closure['files'].items():
        assert q.sha(p/name)==info['sha256'] and (p/name).stat().st_size==info['bytes']
    original={f.name:dict(bytes=f.stat().st_size,sha256=q.sha(f)) for f in p.iterdir() if f.is_file()}
    core_bytes=sum(x['bytes'] for x in original.values())
    qualification=q.ROOT/'reports/s2uc/promotion-neutral-qualification-20261003-01'
    qc=q.read(qualification/'closure.json')
    for name,info in qc['files'].items():assert q.sha(qualification/name)==info['sha256']
    qualification_bytes=sum(f.stat().st_size for f in qualification.rglob('*') if f.is_file())
    assert qualification_bytes==qc['total_bytes']
    results={};assessments={};origins={};promotions=[];comparisons={};resources={}
    for story,spec in plan['stories'].items():
        results[story]={a:q.read(p/(story+'-'+a+'.json')) for a in ('M','E','K','P')}
        source=q.read(p/(story+'-source.json'))
        assert len(source['values'])==spec['frames'] and digest(source['values'])==source['sha256']
        assessments[story]=q.read(p/(story+'-assessment.json'))
        assert q.assess(results[story],spec)==assessments[story]
        origins[story]={a:annotate(results[story][a]) for a in ('M','E')}
        resources[story]={a:r['resources'] for a,r in results[story].items()}
        for a,r in results[story].items():
            assert r['frames']==spec['frames'] and r['slots_released'] and r['ema_cleared']
            assert r['censored_target']==spec['frames']+1
            assert [e['frame'] for e in r['admissions']]==list(range(1,spec['frames']+1))
        for e in results[story]['M']['admissions']:
            old={t['generation'] for t in e['before']['retained']}
            new=[t for t in e['after']['retained'] if t['generation'] not in old]
            if new:
                candidate=e['before']['candidate'];assert candidate and len(new)==1
                assert candidate['ordinals']==new[0]['ordinals'] and candidate['values_sha256']==new[0]['values_sha256']
                other=next(x for x in results[story]['E']['admissions'] if x['frame']==e['frame'])
                promotions.append(dict(story=story,frame=e['frame'],candidate=candidate['generation'],retained=new[0]['generation'],
                    original_ordinals=candidate['ordinals'],M_before=e['cells_before'],M_after=e['cells_after'],
                    E_before=other['cells_before'],E_after=other['cells_after']))
        comparisons[story]={}
        for a in ('E','K','P'):
            rows=assessments[story]['comparisons']
            comparisons[story][a]=dict(gains=[dict(target=r['target'],gain=-r['M_minus'][a]) for r in rows if r['M_minus'][a]<0],
                harms=[dict(target=r['target'],harm=r['M_minus'][a]) for r in rows if r['M_minus'][a]>0],
                ties=[r['target'] for r in rows if r['M_minus'][a]==0])
    summary=q.read(p/'summary.json')
    limits=dict(additional_python_peak=max(r['additional_python_peak'] for v in resources.values() for r in v.values()),
        frame_peak=max(r['meter']['frame_peak'] for v in resources.values() for r in v.values()),
        proposal_peak=max(r['meter']['output_slots_peak'] for v in resources.values() for r in v.values()),
        combined_peak=max(r['meter']['combined_peak'] for v in resources.values() for r in v.values()),
        receipt_bytes=max(r['meter']['receipt_bytes_peak'] for v in resources.values() for r in v.values()),
        transient_utf8_upper=max(r['meter']['receipt_transient_utf8_bytes_peak'] for v in resources.values() for r in v.values()),packed_bytes=416)
    out=q.ROOT/'reports/s2uc/promotion-assessment-20261003-01';ledger=OutputLedger(out)
    ledger.LIMIT=OutputLedger.LIMIT-core_bytes-qualification_bytes
    def text_file(name,text):
        raw=text.encode('utf-8');assert ledger.used+len(raw)<=ledger.LIMIT-ledger.RESERVE
        ledger.used+=len(raw)
        with (out/name).open('xb') as f:assert f.write(raw)==len(raw)
    status='NOT_EVALUABLE';error=None
    try:
        ledger.write('verification.json',dict(status='PASS',original_files=original,binding_sha256=q.sha(q.BINDING),
            plan_sha256=q.sha(q.PLAN),authorization_sha256=q.sha(q.AUTH),authorization_only_status_changed=True,
            bound_code_unchanged=True,bound_files=len(binding['code']),additional_replays=0,
            script_sha256=q.sha(__file__),qualification_closure_sha256=q.sha(qualification/'closure.json')))
        ledger.write('all-target-sets.json',{s:a['metrics'] for s,a in assessments.items()})
        ledger.write('all-gains-and-harms.json',comparisons)
        ledger.write('choice-origins.json',origins)
        ledger.write('promotion-cells.json',promotions)
        ledger.write('all-decisions.json',{s:a['comparisons'] for s,a in assessments.items()})
        ledger.write('resources.json',dict(arms=resources,peaks=limits,source_positions=96,
            experimental_admissions=384,internal_reference_advances=384,original_export_bytes=core_bytes,
            included_qualification_bytes=qualification_bytes,process_RAM_claim=False))
        lines=['# MCM-KI: gebundener S/W/L-Vergleich abgeschlossen','',
            '2026-10-03. S16,W16,L64 jeweils in M/E/K/P genau einmal; Exit0.',
            '96 Quellpositionen,384 Arm-Aufnahmen und384 separat ausgewiesene interne Referenzfortschreibungen.',
            'Kein Zwischenreset,keine Zusatzfolge,Wiederholung oder Parameteränderung.',
            '', '**Korrekte Zuordnung: PASS in S/W/L. Begrenzter Stabilitätsvorteil mit Wechselschaden. Robuster Auswahlvorteil: NICHT_NACHGEWIESEN.**',
            'Keine technischen Fehler und keine Erwartungsabweichungen. Alle vorgegebenen Ziele vorhanden.',
            'L bleibt Entwicklungsregression; unabhängiger Evaluationsnutzen bleibt NICHT_GEPRUEFT (Maschinenstatus NOT_TESTED).',
            'EMA und Promotionsmitnahme bleiben standardmäßig deaktiviert.',
            '', '## Festgelegte Zielmengen und sämtliche Armvergleiche', '',
            'Je Feld Fehlersumme / MAE. M=Mitnahme,E=Reset,K=Kontext-sonst-Persistenz,P=Persistenz.',
            'H/N partitionieren G. V,D,J überlappen; sie werden nicht addiert oder nachträglich umgewichtet.']
        for story in ('S','W','L'):
            lines+=['','### '+story,'','| Menge | Ziele | M Summe / MAE | E Summe / MAE | K Summe / MAE | P Summe / MAE |',
                '|---|---|---:|---:|---:|---:|']
            for mask in ('H','N','G','V','D','J'):
                values=assessments[story]['metrics'][mask]
                lines.append('| '+mask+' | '+','.join(map(str,plan['stories'][story]['masks'][mask]))+' | '+
                    ' | '.join(format(values[a]['error_sum'],'.12g')+' / '+format(values[a]['mae'],'.12g') for a in ('M','E','K','P'))+' |')
            lines+=['','V-Kontextverfügbarkeit: '+str(assessments[story]['V_context_available'])+
                '; Baseline-Nettonutzen auf V: '+assessments[story]['baseline_benefit_V']+'.']
        lines+=['','## Vollständige Gewinne und Schäden','',
            'Alle folgenden Werte sind einzelne Fehlerdifferenzen von M gegen die jeweilige Baseline; keine Verrechnung zwischen Geschichten.']
        for story in ('S','W','L'):
            for a,c in comparisons[story].items():
                lines.append('- '+story+' gegen '+a+': Gewinne '+json.dumps(c['gains'])+'; Schäden '+json.dumps(c['harms'])+'.')
        lines+=['','## Alle Einzelentscheidungen und Herkunft der Erfahrung','',
            'C=Kontext,P=Persistenz. Ohne auswählbaren Kontext ist P eine Enthaltung vom Kontext, kein gelernter Erfolg.',
            'MITGENOMMEN_DANACH_AKTUALISIERT enthält beide Anteile; die Mitnahme wird nicht als neue Beobachtung gezählt.']
        for story in ('S','W','L'):
            lines+=['','### '+story,'','| Ziel | Wahl M/E/K/P | Fehler M/E/K/P | Grundlage M | Grundlage E |','|---:|---|---|---|---|']
            for r in assessments[story]['comparisons']:
                t=r['target'];choices='/'.join('C' if r['choices'][a]=='CONTEXT' else 'P' for a in ('M','E','K','P'))
                errors='/'.join(format(r['errors'][a],'.12g') for a in ('M','E','K','P'))
                lines.append(f"| {t} | {choices} | {errors} | {origins[story]['M'][t]['basis']} | {origins[story]['E'][t]['basis']} |")
        def celltext(cells):
            return '; '.join(('r' if c['role']==0 else 'c')+str(c['generation'])+f"/o{c['offset']}/q{c['quality']}:({c['ec']},{c['ep']})" for c in cells) or 'leer'
        lines+=['','## Fehlerzellen unmittelbar vor und nach jeder Promotion','',
            'Die Zeilen enthalten die vollständige jeweilige Tabelle, einschließlich fremder oder gleichzeitig verdrängter Zellen.','']
        for e in promotions:
            lines += [f"- {e['story']} Aufnahme{e['frame']}: c{e['candidate']}→r{e['retained']}, Originalordinalen{e['original_ordinals']}.",
                '  M vorher: '+celltext(e['M_before'])+'; nachher: '+celltext(e['M_after'])+'.',
                '  E vorher: '+celltext(e['E_before'])+'; nachher: '+celltext(e['E_after'])+'.']
        lines+=['','## Fachliche Auswertung','',
            'S: An7 lernen M/E aus demselben kalten P-Start das Paar(0,0.5). M erhält es bei8. An11 wählt M daraus C und spart0.5 gegen E; an15 haben beide neue retained-Erfahrung. M erfüllt den Stabilitätsvergleich auf H und G. Gegen K bleibt der kalte Verlust an7 bestehen; deshalb kein V-Nettonutzen gegen alle Baselines.',
            'W: Derselbe Transfer bei8 bewahrt dieselbe Bewertung, die an11 nun unpassend ist. M wählt C und verliert0.5 gegen E/P. Danach steht M auf(0.25,0.25),E auf(0.5,0). An15 verhindert Mehrdeutigkeit eine Kontextwahl; die dortige P-Wahl belegt daher keine erneute eindeutige erfahrungsabhängige Anpassung. Promotion16 erzeugt mangels Kandidatenzelle keine Fehlererfahrung.',
            'L: M verliert an19 gegenüber E/P0.5625 aus mitgenommener B-Kontexterfahrung; E gewinnt dort durch seinen kalten Default, nicht durch Lernen. M spart an23 und59 je0.5 gegen E. An31 wählt M nach neuer Beobachtung19 bei Gleichstand P, E nach eigener B-Bewertung ebenfalls P. Dieser Gewinn gegen K ist kein zusätzlicher M-Gewinn gegen E oder kalte Persistenz.',
            'An39 kein Fehlerupdate bei Mehrdeutigkeit; spätere reguläre B-Löschung bei40 bleibt getrennt. Bei48 wird alte A-Erfahrung gelöscht, während C-Erfahrung mitgenommen wird. An51 fehlt A-Kontext. An55 sind M/E für den neuen Kandidaten c7 kalt; nur dessen neue Erfahrung wird bei56 nach r5 verschoben. M nutzt sie an59; an63 ist sie zusätzlich durch das neue Ziel59 aktualisiert. Keine Übernahme vom alten r1 nach Wiederkehr.',
            'Auf L-V ist M strikt besser als E,K,P und erfüllt das vorab definierte lokale Nutzenkriterium. Über alle31 L-Ziele ist M jedoch weiterhin schlechter als K. L ist bekanntes Entwicklungsmaterial; daraus folgt kein unabhängiger Evaluationsnutzen. Das positive L-V-Ergebnis und der S-Gewinn heben den W-Schaden nicht auf.',
            '', '## Ressourcen, Abweichungen und Abschluss','',
            '51 gebundene Dateien sowie Plan,Vertrag und Python-Laufzeit vor/nach unverändert. Die Autorisierung unterscheidet sich nur im Status von der Vorlage.',
            'Memoryzustände und Matchreceipts zwischen allen Armen identisch. Zielzahlen je Arm S7/W7/L31. Endziele17/17/65 zensiert ohne Zielkonsum; Vorschläge und EMA-Zellen freigegeben.',
            'Gemessene Spitzen über alle Arme: '+json.dumps(limits)+'. Grenzen:16384 Zusatzbyte,18 Frames,2 Vorschläge,20 gemeinsam,16384 Receiptbyte,32768 transiente UTF8-Byte. Keine Gesamtprozess-RAM-Aussage.',
            'Originalexport einschließlich Abschluss:'+str(core_bytes)+' Byte. Die frühere technische Qualifikation mit sämtlichen Fixtures/Snapshots wird mit weiteren'+str(qualification_bytes)+' Byte konservativ in die gemeinsame4MiB-Bilanz einbezogen.',
            'Auch dieser Bericht und seine Tabellen sind enthalten. Exakte gemeinsame Endsumme: closure.json.256KiB Abschlussreserve vorab eingehalten. Keine ursprüngliche Exportdatei geändert. Nachauswertung ausschließlich gespeicherter Daten; keine weiteren Replays.',
            'Keine Ausführungs-/Erwartungsabweichungen. Das Ausbleiben eines robusten Vorteils ist ein fachlicher Gegenbefund, kein technischer Fehler. Die Einmalfreigabe ist verbraucht.',
            '', '## Genau ein nächster fachlicher Vorschlag','',
            'Den Mischbefund abnehmen und die Variante unverändert experimentell/default disabled belassen. Als nächsten begrenzten Konzeptschritt prüfen, welche vor dem Ziel tatsächlich verfügbaren Informationen stabile und veränderte Fortsetzungen überhaupt unterscheiden könnten. S/W besitzen bis zur ersten unterschiedlichen Fortsetzung denselben beobachteten Präfix; ohne zusätzliche Information kann eine kausale Auswahl diesen Wechsel nicht im Voraus erkennen. Deshalb keine bloße Neuabstimmung von Alpha oder Kaltstartdefault als allgemeine Lösung.',
            'Abnahmekriterium dieses Konzeptschritts: ein klar benanntes,vor Ziel verfügbares Informationssignal mit Gegenfall und Informationsgrenze oder die begründete Feststellung,dass mit dem bisherigen Eingang nur nachträgliche Anpassung möglich ist. Keine neue Implementierung,Quelle oder Wiederholung aus diesem Bericht ableiten.','']
        text_file('REPORT.md','\n'.join(lines))
        q.verify();assert all(q.sha(p/name)==info['sha256'] for name,info in original.items())
        status='COMPLETE'
    except BaseException as exc:
        error=type(exc).__name__+':'+str(exc);raise
    finally:
        final=dict(status=status,error=error,original_export_bytes=core_bytes,qualification_bytes=qualification_bytes,
            supplementary_before_closure=ledger.used,total_bytes=0,limit=OutputLedger.LIMIT,reserve=ledger.RESERVE,
            files={f.name:dict(bytes=f.stat().st_size,sha256=q.sha(f)) for f in out.iterdir() if f.is_file()},
            original_closure_sha256=q.sha(p/'closure.json'),additional_replays=0)
        for _ in range(10):
            total=core_bytes+qualification_bytes+ledger.used+len(json.dumps(final,sort_keys=True,separators=(',',':'),allow_nan=False).encode())+1
            if final['total_bytes']==total:break
            final['total_bytes']=total
        ledger.write('closure.json',final,final=True)
    actual=core_bytes+qualification_bytes+sum(f.stat().st_size for f in out.iterdir() if f.is_file())
    assert actual==final['total_bytes'] and actual<=4194304
    print(json.dumps(dict(status=status,original_export_bytes=core_bytes,qualification_bytes=qualification_bytes,
        combined_bytes=actual,resources=limits,summary=summary)))


if __name__=='__main__':main()
