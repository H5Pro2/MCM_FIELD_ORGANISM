"""Report sealed XYX evidence only; no replay, adapter or materializer calls."""
import json
from pathlib import Path

from tools import s2uc_xyx_prepare as q
from tools._s2uc_xyx_assessment import assess, ARMS

OUT=q.ROOT/'reports/s2uc/xyx-assessment-20261003-01'


def run_bytes():
    c=q.prior.read(q.OUT/'closure.json')
    assert c['status']=='COMPLETE' and c['error'] is None and c['completed_arms']==list(ARMS)
    for name,item in c['files'].items():
        p=q.OUT/name
        assert p.stat().st_size==item['bytes'] and q.prior.sha(p)==item['sha256']
    return sum(p.stat().st_size for p in q.OUT.iterdir() if p.is_file())


def main():
    b=q.verify(); qb=q.prior.check_qualification(); pb=q.check_preparation(); rb=run_bytes()
    spec=q.prior.read(q.PLAN)
    a=q.prior.read(q.OUT/'assessment.json')
    r={arm:q.prior.read(q.OUT/(arm+'.json')) for arm in ARMS}
    source=q.prior.read(q.OUT/'source.json')
    q.validate_source(source)  # Validate saved values, never generate replacements.
    assert q.digest(assess(r,source,spec))==q.digest(a)
    assert not a['technical_errors']
    assert q.prior.read(q.AUTH)==dict(q.prior.read(q.TEMPLATE),status='AUTHORIZED_ONCE')==q.auth('AUTHORIZED_ONCE')
    assert all(len(x['rows'])==23 and len(x['admissions'])==48 and x['frames']==48 for x in r.values())
    assert all(x['censored_target']==49 and x['slots_released'] and x['states_identical'] for x in r.values())
    decisions={d['target']:d for d in a['decisions']}
    rows={arm:{row['target']:row for row in result['rows']} for arm,result in r.items()}
    gains={}
    for arm in ARMS[1:]:
        gains[arm]=dict(gains=[],harms=[],ties=[])
        for d in a['comparisons']:
            delta=d['U_minus'][arm]
            if delta==0: gains[arm]['ties'].append(d['target'])
            else: gains[arm]['gains' if delta<0 else 'harms'].append(dict(target=d['target'],magnitude=abs(delta),U_minus=delta))
    # Check every pre-registered error-pair prediction against saved observations.
    expected={7:((0.,.5),None),11:((0.,.5),None),15:((0.,.5),None),19:((1/8,3/8),None),
        23:((3/16,5/16),(0.,1/4)),27:((7/32,9/32),(0.,1/4)),31:((15/64,17/64),(0.,1/4)),
        35:((15/128,49/128),(1/8,3/8)),39:((15/256,113/256),(3/16,7/16)),
        43:((15/512,241/512),(7/32,15/32)),47:((15/1024,497/1024),(15/64,31/64))}
    pair_deviations=[]
    for t,pairs in expected.items():
        actual={h['label']:tuple(h['after']) for h in decisions[t]['hypotheses']}
        for label,wanted in zip(('X','Y'),pairs):
            if actual.get(label)!=wanted: pair_deviations.append(dict(target=t,label=label,expected=wanted,actual=actual.get(label)))
    res=q.prior.read(q.OUT/'resources.json')
    limits=spec['limits']
    ures=res['arms']['U']
    assert ures['controlled_original_frame_upper_bound']<=limits['frames'] and ures['controlled_combined_upper_bound']<=limits['combined']
    assert ures['additional_python_peak']<=limits['additional_python'] and ures['packed_bytes']==416
    assert all(x['resources']['additional_python_peak']<=16384 for x in r.values())
    ledger=q.OutputLedger(OUT); ledger.LIMIT-=qb+pb+rb
    ledger.write('verification.json',dict(bound_files=len(b['code']),binding_sha256=q.prior.sha(q.BINDING),
        plan_sha256=q.prior.sha(q.PLAN),contract_sha256=q.prior.sha(q.CONTRACT),run_closure_sha256=q.prior.sha(q.OUT/'closure.json'),
        report_script_sha256=q.prior.sha(Path(__file__)),authorization_only_status_changed=True,
        source_positions=48,experimental_admissions=240,internal_reference_advances=240,
        extra_replays=0,technical_errors=a['technical_errors'],choice_deviations=a['expectation_deviations'],
        error_pair_deviations=pair_deviations))
    ledger.write('all-target-sets.json',dict(masks=spec['masks'],metrics=a['metrics']))
    ledger.write('all-decisions-and-feedback.json',a['decisions'])
    ledger.write('all-individual-differences.json',a['comparisons'])
    ledger.write('all-gains-and-harms.json',gains)
    ledger.write('resources.json',dict(run=res,policy_qualification=q.prior.read(q.prior.QUAL/'facts.json')['R2'],
        policy_qualification_bytes=qb,preparation_bytes=pb,run_bytes=rb,
        legacy_packed_note='Legacy packed_bytes=416 is a constant bound in the old exporter; K/P have disabled error memory. Not a measured allocation of416 in these arms.',
        no_process_ram_claim=True))
    lines=['# MCM-KI: nichtpersistenter XYX-Vergleich abgeschlossen','',
        '2026-10-03. Genau einmal,Exit0:48 Quellpositionen,240 Arm-Aufnahmen plus240 interne Referenzfortschreibungen.',
        '**AUSWAHL_X_Y_X: '+a['selection']['verdict']+'. Nettonutzen auf H: '+a['net_benefit_H']+'. Gesamtnutzen auf G: '+a['total_benefit_G']+'.**',
        'Alle Befunde gelten fuer den festgelegten Entwicklungskontrast. Unabhaengiger Evaluationsnutzen NICHT_GEPRUEFT; Defaults deaktiviert.',
        'Keine technischen Fehler,keine Abweichungen der Entscheidungen oder Fehlerpaare von den statischen Erwartungen. Keine Wiederholung,Ersatzfolge,Parameter- oder Policyaenderung.',
        '64 gebundene Dateien,Plan,Vertrag und Laufzeit unveraendert. Autorisierung ausschliesslich im Status geaendert; Einmalfreigabe verbraucht. Endziel49 zensiert,Ausgaben freigegeben.','',
        '## Alle sieben Zielmengen','',
        'Je Feld Fehlersumme / MAE; keine fehlenden Ziele. H/N partitionieren G; S/F/A_W/A_R bleiben getrennte,ueberlappende Diagnosen. Kontextabdeckung aller Arme je Ziel in all-target-sets.json.','',
        '| Menge | Ziele | U | M | E | K | P |','|---|---|---:|---:|---:|---:|---:|']
    for mask in ('G','H','N','S','F','A_W','A_R'):
        lines.append('| '+mask+' | '+','.join(map(str,spec['masks'][mask]))+' | '+' | '.join(
            str(a['metrics'][mask][arm]['error_sum'])+' / '+str(a['metrics'][mask][arm]['mae']) for arm in ARMS)+' |')
    lines+=['','## Identitaet und kausale Auswahl','',
        'X: Originalframes1..4,Nachfolgerordinal3 mit Wert13/16; nach Promotion retained-Key(Rolle0,Generation1,Offset0,EXACT).',
        'Y: Originalframes17..20,Nachfolgerordinal19 mit Wert9/16; zuerst candidate-Key(1,2,0,EXACT),ab Promotion24 retained-Key(0,2,0,EXACT). Persistenz ist5/16.',
        'Keys,Originalordinalen,Hintwerte,Zeitgrenzen,Read-Revision und vollstaendige Treffer wurden gegen eingefrorene Receipts,Feedbackbelege und normale Bestandsereignisse geprueft. Keine Identifikation ueber feste Ticketnummern.',
        '11/15: warme X-Auswahl aus Feedback7 bzw.7/11; direkte Promotion bei8 erhaelt diese Erfahrung.',
        '19: erster Wechsel,X gewaehlt,Fehler1/4. Danach X=(1/8,3/8),d=-1/4; Y noch nicht gespeichert.',
        '23: Y ist vorhanden,aber kalt. U waehlt weiterhin warmes X,Fehler1/4. Dieser erwartete Verzoegerungsverlust bleibt enthalten. Feedback23 aktualisiert X zu(3/16,5/16) und das NICHT ausgewaehlte Y zu(0,1/4).',
        '24: Y:c2->r2 erhaelt sein Fehlerpaar und seine Originalframes. Keine Ticketumleitung oder zusaetzliche Beobachtung.',
        '27: beide Kontextfortsetzungen warm und besser als P; d_X=-1/8,d_Y=-1/4. U waehlt tatsaechlich Y mit Nachfolgerordinal19,Fehler0. An31 bleibt Y gewaehlt. Vorangehendes Y-Feedback:23 bzw.23/27.',
        '35: erste Rueckkehr,Y gewaehlt,Fehler1/4. Feedback35 bewertet auch das NICHT ausgewaehlte X: X=(15/128,49/128),Y=(1/8,3/8).',
        '39: d_X=-17/64<d_Y=-1/4; U waehlt tatsaechlich X mit Nachfolgerordinal3. Feedback35 ist der neue Rueckkehrbeleg. X bleibt an43/47 gewaehlt,je Fehler0. Die Frist43 ist bereits an39 erfuellt.',
        'Keine dieser gewerteten Kontextentscheidungen ist P,Kaltwahl oder Gleichstand. Die Herkunft bleibt bei Konkurrenz mehrdeutig.',
        'Wichtig: Y an35 ist trotz0.25 Vorteil gegen jede Baseline weiterhin eine falsche Fortsetzung und zaehlt nicht als gelungene Rueckkehr. Die Wahl an23 ist ebenfalls kein Erfolg.','',
        '## Saemtliche eingefrorenen Entscheidungen und Einzelfehler','',
        '| Ziel | U | Grund U | Fehler U/M/E/K/P | U-M / U-E / U-K / U-P |','|---:|---|---|---|---|']
    for d in a['comparisons']:
        t=d['target']; dec=decisions[t]
        lines.append('| '+str(t)+' | '+dec['selected_label']+' | '+dec['reason']+' | '+
            ' / '.join(str(d['errors'][arm]) for arm in ARMS)+' | '+
            ' / '.join(str(d['U_minus'][arm]) for arm in ARMS[1:])+' |')
    lines+=['','## Alle Hypothesenbewertungen vor/nach Feedback','',
        'Paare=(EC,EP). Rohfehler und gesamte Vorgeschichte stehen zusaetzlich im JSON. KALT ist keine Nullbewertung.',
        '| Ziel | Hypothese / Key | Nachfolgerordinal | Vorher | Rohfehler | Nachher | Fruehere Feedbackziele |',
        '|---:|---|---:|---|---|---|---|']
    for dec in a['decisions']:
        for h in dec['hypotheses']:
            lines.append('| '+str(dec['target'])+' | '+h['label']+' '+str(h['key'])+' | '+str(h['original_successor'])+
                ' | '+('KALT' if h['before'] is None else str(h['before']))+' | '+str(h['raw_errors'])+' | '+str(h['after'])+
                ' | '+','.join(map(str,h['prior_feedback']))+' |')
    lines+=['','## Gewinne und Schaeden gegen jede Baseline','']
    for arm,g in gains.items():
        lines.append('- Gegen '+arm+': Gewinne '+json.dumps(g['gains'])+'; Schaeden '+json.dumps(g['harms'])+'.')
    lines+=['Alle anderen Differenzen sind0; genaue Gleichstandsziele in all-gains-and-harms.json.',
        'Der einzige Mehrfehler gegen die Baselines liegt an7 gegen K:0.5 kalte Anfangskosten. Die eigenen Fehler19/23/35 bleiben unabhaengig von Differenzen vollstaendig ausgewiesen.',
        'Auswahlfaehigkeit,H-Nettonutzen und G-Gesamtnutzen sind getrennte,jeweils erfuellte Kriterien. Kein Weglassen der Neben-/Anfangsziele; N bleibt bei allen Armen gleich.','',
        '## Ressourcen und gemeinsame Exportbilanz','',
        '| Arm | Python-Zusatzpeak Bytes | Frameangabe | Gemeinsam | Receipt / UTF8-Obergrenze Bytes |',
        '|---|---:|---|---|---|']
    for arm in ARMS:
        v=res['arms'][arm]
        if arm=='U':
            fields=(v['additional_python_peak'],str(v['controlled_original_frame_upper_bound'])+' kontrollierte Obergrenze',
                    str(v['controlled_combined_upper_bound'])+' Obergrenze',v['receipt_bytes'],v['utf8_upper'])
        else:
            m=v['meter'];fields=(v['additional_python_peak'],str(m['frame_peak'])+' beobachteter Peak',
                               str(m['combined_peak'])+' beobachteter Peak',m['receipt_bytes_peak'],m['receipt_transient_utf8_bytes_peak'])
        lines.append('| '+arm+' | '+str(fields[0])+' | '+fields[1]+' | '+fields[2]+' | '+str(fields[3])+' / '+str(fields[4])+' |')
    lines += ['','U verwendet416 gepackte Bytes inkl.Ticket/Staging,maximal2 Ausgabeplaetze.12 ist die kontrollierte Frameobergrenze,KEIN gemessener U-Framepeak; unbefuellte Tracingpeaks bleiben ohne Verbrauchsaussage.',
        'Der alte Exporter traegt packed_bytes=416 auch fuer K/P als konstante Grenze ein; deren Fehlergedaechtnis ist deaktiviert. Daraus keine gemessene416-Byte-Allokation dieser Arme ableiten.',
        'Wiederverwendete Policyqualifikation:9897/16384 Zusatzbyte,18/18 Originalframes,2/2 Ausgabeplaetze,20/20 gemeinsam,Receipt2012,UTF8-Obergrenze4024 Byte. Kein Gesamtprozess-RAM-Beleg.',
        f'Policyqualifikation{qb} Byte + separate Vorbereitung{pb} Byte + Originalvergleich{rb} Byte = {qb+pb+rb} Byte vor dieser Nachauswertung. Endsumme inklusive Bericht in closure.json; gemeinsame Grenze4194304 Byte,Reserve262144 Byte.',
        'Alle Originalexporte bleiben versiegelt. Berichtsauswertung ausschliesslich gespeicherter Daten,keine weiteren Replays.','',
        '## Genau eine naechste Forschungsentscheidung','',
        'Empfehlung: einen unabhaengigen Evaluationsvertrag fuer die eingefrorene Policy konzipieren. Die Auswertungsquelle soll getrennt bereitgestellt und vor Ausfuehrung gebunden werden; Baselines,Ressourcen und Fehlerkriterien stehen vorher fest. Die jetzige offengelegte,algebraisch vorhergesagte Folge belegt Entwicklungsauswahl,keine unabhaengige Generalisierung.',
        'Heute keine neue Quelle,keine Policyanpassung und keine weitere Ausfuehrungsfreigabe.','']
    q.prior.write_text(ledger,'REPORT.md','\n'.join(lines))
    q.verify(); assert q.prior.check_qualification()==qb and q.check_preparation()==pb and run_bytes()==rb
    closure=dict(status='COMPLETE',policy_qualification_bytes=qb,preparation_bytes=pb,original_run_bytes=rb,
        report_bytes_before_closure=ledger.used,combined_including_closure=0,limit=4194304,reserve=262144,
        selection=a['selection']['verdict'],net_H=a['net_benefit_H'],total_G=a['total_benefit_G'],
        choice_deviations=a['expectation_deviations'],pair_deviations=pair_deviations,extra_replays=0,
        independent_evaluation='NICHT_GEPRUEFT',files={p.name:dict(bytes=p.stat().st_size,sha256=q.prior.sha(p)) for p in OUT.iterdir() if p.is_file()})
    for _ in range(8):
        n=len(json.dumps(closure,sort_keys=True,separators=(',',':'),allow_nan=False).encode())+1
        total=qb+pb+rb+ledger.used+n
        if closure['combined_including_closure']==total: break
        closure['combined_including_closure']=total
    ledger.write('closure.json',closure,final=True)
    assert sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())+qb+pb+rb==closure['combined_including_closure']
    print(json.dumps({k:v for k,v in closure.items() if k!='files'},indent=2))


if __name__=='__main__': main()
