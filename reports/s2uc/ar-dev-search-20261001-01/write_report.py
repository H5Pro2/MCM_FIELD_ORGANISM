"""Render saved seven-grid results only; no replays, generation or selection."""
import json
from pathlib import Path
from tools import s2uc_ar_material as m
OUT=Path(__file__).resolve().parent
def read(name):return json.loads((OUT/name).read_text())
pre=read('presearch.json');selection=read('selection.json');overview=read('overview.json');verification=read('verification.json')
fmt=lambda x:'undefiniert' if x is None else format(x,'.12g')
lines=['MCM S2UC -- AR-DEV einmalige Produktion und fest begrenzte Siebener-Suche','2026-10-01','',
'ABGESCHLOSSEN: MATERIAL_COMPLETE, ein Produktionsaufruf, danach genau sieben vorgegebene tau. Alle elf Pruefziele und48 Lernziele je Arm/Einstellung separat. AR-EVAL unproduziert und unausgewertet.',
'','1. Bindungen und Produktion',
'Plan SHA256 '+pre['plan_sha256'],
'Produktionsbindung SHA256 '+pre['binding_sha256'],
'Autorisierung docs/S2UC_AR_DEV_AUTORISIERUNG_20261001.json exakt aus PENDING-Vorlage erstellt, Status AUTHORIZED_ONCE. Kein Code-/Seed-/Parameter-/Fallwechsel.',
'Einziger Produktionsaufruf: C:/Python314/python.exe -m tools.s2uc_ar_material produce docs/S2UC_AR_DEV_AUTORISIERUNG_20261001.json',
'Material reports/s2uc/signal-approx-material-ar-dev-01;21 Dateien,vier Basisepisoden,768 Basiskomponenten,2 R-Hinweisrauschframes,3 reine Stoerungsframes,8 Kalibrationsframes;11 exportierte Fallgeschichten mit129 Frames.',
'Materialausgabe '+str(verification['material_bytes'])+'/4194304 Byte einschliesslich Fehlerabschlussreserve262144 Byte. Keine zweite Produktion; keine Ersatzdaten.',
'Integritaetsleser bestaetigt Profile/Wertehashes/Herkunft, gemeinsames A/D-Praefix, R1/R3-Hinweisgleichheit, Stoerungen, Mischung und Kleinsignal-Gain. Materialhashes vor/nach Suche gleich; Code-/Plan-/Laufzeitbindungen abschliessend bestaetigt.',
'','2. Epsilon als Rezeptpruefung',
'Acht Kalibrationsframe-Absolutamplituden: '+str(pre['frame_amplitudes']),
'epsilon='+fmt(selection['epsilon'])+'=2^-10. Konstruktionsbedingt, da jede Rauschkomponente Betrag2^-10 besitzt. Keine Schaetzung eines unbekannten Sensorrauschbodens.',
'','3. Alle sieben Einstellungen und Auswahlregel',
'Beide Arme verwenden ausschliesslich legacy_v1-Fortsetzung. Jede Geschichte startet leer. Kein factor_scaled_v1 und kein automatischer Policywechsel. Zeit-/Ressourcenbeobachtung beeinflusst keine Zuordnung.',
'Zulaessigkeit: keine zusaetzliche falsche Einzelzuordnung pro Position gegen exakten Abruf. Bereits falsche Referenzpositionen bleiben sichtbar; keine Fehler gegeneinander verrechnen.',
'Ziel: maximale korrekte R1/R2-Zuordnungen; Gleichstand kleinstes tau. MAE erreicht den Selector nicht. Auswahlinput ausschliesslich Kategorien in selection-inputs.json.',
'tau | zulaessig | korrekt R1/R2 | Zugewinn R1/R2 | neue Fehler | verlorene exakte Zuordnungen | konkrete Abdeckung neu/exakt | Schema-MAE neu/exakt/Persistenz']
for assessment,item in zip(selection['assessments'],overview):
    assert assessment['tau']==item['tau'];s=item['summary'];c=s['comparison'];n=c['policies']['signal_approx_retrieval'];e=c['policies']['exact_retrieval'];f=c['full_means']
    lines.append(' | '.join([fmt(item['tau']),str(assessment['eligible']),str(assessment['correct_R1_R2']),str(assessment['gain_R1_R2']),str(assessment['additional_wrong']),str(s['lost_exact_assignments']),str(n['context_covered'])+'/11 / '+str(e['context_covered'])+'/11',fmt(f['signal_approx_retrieval'])+' / '+fmt(f['exact_retrieval'])+' / '+fmt(f['persistence'])]))
lines += ['','Auswahlstatus: '+selection['status'],'selected_tau='+str(selection['selected_tau']),
'Nur Development-Ergebnis. Auch ein ausgewaehlter Parameter autorisiert keine Evaluation und belegt noch keinen Robustheitsgewinn.',
'','4. Einzelbewertungen, gemeinsame Zielmasken und alle Schaeden']
for index,item in enumerate(overview):
    s=item['summary'];c=s['comparison'];l=item['learning_summary'];lc=l['comparison']
    lines += ['',f'Einstellung{index}, tau={item["tau"]}',
        'Verlorene Exakttreffer: '+str(s['lost_exact_assignments'])+'; signalbedingt: '+str(s['signal_lost_exact_assignments'])+'; verlorene korrekte Exakttreffer: '+str(s['lost_correct_exact']),
        'Fall | Herkunft exakt/neu | Status exakt/neu | MAE konkret exakt/neu/Persistenz | MAE Schema exakt/neu']
    for e,n in zip(c['policies']['exact_retrieval']['rows'],c['policies']['signal_approx_retrieval']['rows']):
        assert e['case_id']==n['case_id']
        lines.append(' | '.join([e['case_id'],e['origin_category']+'/'+n['origin_category'],e['prediction_status']+'/'+n['prediction_status'],fmt(e['context_mae'])+'/'+fmt(n['context_mae'])+'/'+fmt(e['persistence_mae']),fmt(e['observer_hybrid_mae'])+'/'+fmt(n['observer_hybrid_mae'])]))
    for policy in ('exact_retrieval','signal_approx_retrieval'):
        lines += [policy+' Herkunft/Abdeckung:',json.dumps(c['policies'][policy]['origin_and_prediction'],indent=2)]
    for pair,result in c['paired'].items():
        lines += [pair+': Zielmenge '+str([r['case_id'] for r in result['rows']])+', n='+str(result['count'])+', MAE links/rechts='+fmt(result['left_mae'])+'/'+fmt(result['right_mae'])+', Delta='+fmt(result['delta'])]
    lines += ['Alle Primaerschaeden gegen Persistenz:',json.dumps(c['harms_against_persistence'],indent=2),
        'Alle Primaerschaeden gegen exaktes Kontext-sonst-Persistenz-Schema:',json.dumps(c['harms_against_exact_retrieval'],indent=2),
        '48 Lernziele separat: neue Fehler '+str(l['additional_wrong'])+'; verlorene exakte Zuordnungen '+str(l['lost_exact_assignments'])]
    for policy in ('exact_retrieval','signal_approx_retrieval'):
        lines += [policy+' Lernzielbilanz:',json.dumps(lc['policies'][policy]['origin_and_prediction'],indent=2)]
    lines += ['Lernziel-Schaeden gegen Persistenz:',json.dumps(lc['harms_against_persistence'],indent=2),
        'Lernziel-Schaeden gegen exaktes Beobachterschema:',json.dumps(lc['harms_against_exact_retrieval'],indent=2),
        f'Alle48 Lern-Einzelwerte und gemeinsamen Masken stehen in tau-{index}.json/learning_summary; kein Einmischen in Primaerquote.']
lines += ['','5. Semantik und Kausalitaet',
'Undefinierte konkrete MAE bedeutet Enthaltung, niemals Nullfehler. observer_hybrid_mae/full_rows verwenden ein ausschliesslich beobachterseitiges Kontext-sonst-Persistenz-Schema. Die beiden Abrufarme sind Exakter Abruf und Signal-/Naeherungsabruf, beide mit legacy_v1-Fortsetzung.',
'Matching kann sich wie beauftragt unterscheiden. Speicherzustand nach jedem Frame sowie nach Abschluss identisch zur unveraenderten Referenz und zwischen Abrufarmen. Jede Wahrnehmung genau einmal pro Geschichte aufgenommen.129 Frames je Arm/Einstellung;59 erreichbare Ziele=11 Pruefziele+48 Lernziele.7 Einstellungen sind7 Wiederverwendungen desselben DEV-Bestands, keine7 unabhaengigen Materialstichproben.',
'R1/R3 und R0/N3: gleiche Prognosen und Vorzustaende vor unterschiedlichem Zielframe. Gate erzwingt Prognose vor Zukunftsabruf und vor Hinweisaufnahme. Slots nach Verbrauch/Abschluss frei. Provenienz, Rollen, Qualitaet und Einzelreceipts in tau-0..6.json.',
'','6. Ressourcen und Grenzen']
resources=[x for settings in verification['resources'].values() for case in settings.values() for x in case.values()]
peaks={key:max(x[key] for x in resources) for key in ('frame_peak','output_slots_peak','combined_peak','receipt_bytes_peak','receipt_transient_utf8_bytes_peak','receipt_python_bytes_peak','temporary_numeric_vectors_peak','match_metadata_peak')}
lines += [json.dumps(peaks,indent=2),'Instrumentierte Suchdauer Sekunden: '+str(verification['elapsed_search_seconds']),
'Grenzen18 Frames einschliesslich Hinweise,2 Ausgaben,20 zusammen; Receipt16384 Byte, gleichzeitige Provenienz32768 Byte. Kein harter Prozess-RAM-Nachweis. Keine neuen48er-Distanzvektoren; Observerarchive getrennt von Produktmemory und Materialbudget.',
'','7. Weiteres Vorgehen',
('Development-Ergebnis zur Abnahme und Entscheidung vorlegen; epsilon und selected_tau vor einer gesondert beauftragten einmaligen AR-EVAL-Pruefung einfrieren. Kein Nachverfeinern des Gitters, keine Episodenwahl. Neue falsche Einzelzuordnungen auf Evaluation verhindern die Abnahme als verbesserte Wiedererkennung.' if selection['selected_tau'] is not None else 'Kein zulaessiger Zugewinn: selected_tau bleibt null. Keine Auswahl oder automatische Produktion zur Evaluation. Negativen Befund an Projektleiter uebergeben; keine Gitterverfeinerung oder Ersatzepisoden ohne neue fachliche Entscheidung.'),
'AR-EVAL bleibt unproduziert und unausgewertet. Direkte synthetische Adapterpruefung, kein Audio-/NJ-Robustheitsnachweis.']
with (OUT/'REPORT.txt').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
with (OUT/'resource-ledger.json').open('x') as f:json.dump(dict(material_bytes=verification['material_bytes'],observer_bytes_before_ledger_and_inventory=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file()),peaks=peaks,hard_process_ram_measured=False),f,indent=2)
inventory={p.name:dict(sha256=m.sha(p),bytes=p.stat().st_size) for p in OUT.iterdir() if p.is_file()}
with (OUT/'inventory.json').open('x') as f:json.dump(inventory,f,indent=2)
print(json.dumps(selection,indent=2))
