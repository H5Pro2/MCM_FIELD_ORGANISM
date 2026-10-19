"""Format already saved observer results; no replay or material production."""
import json
from pathlib import Path
from tools import s2uc_factor_material as m
OUT=Path(__file__).resolve().parent
r=m.read(OUT/'result.json');v=m.read(OUT/'verification.json');pre=m.read(OUT/'preanalysis.json')
probe=m.read(OUT/'candidate-probe.json');s=r['test_targets'];ls=r['learning_targets']
fmt=lambda x:'undefiniert (Enthaltung)' if x is None else format(x,'.12g')
lines=['MCM S2UC -- FC-DEV einmalige Produktion und Dreiarm-Auswertung','2026-10-01','',
'ERGEBNIS: MATERIAL_COMPLETE, genau ein Produktionsaufruf (Exit0), anschliessend lokale Auswertung.11 Pruefziele und48 Lernziele pro Policy getrennt; Kandidatenprobe separat. FC-EVAL unproduziert/unausgewertet.',
'', '1. Bindungen und Material',
'Originalplan SHA256 '+pre['plan_sha256'],
'Zusaetzliche Produktionsbindung SHA256 '+pre['production_binding_sha256'],
'Konkrete Autorisierung: docs/S2UC_FC_DEV_AUTORISIERUNG_20261001.json, exakt aus PENDING-Vorlage mit Status AUTHORIZED_ONCE. Kein Parameter-, Seed-, Fall- oder Codewechsel.',
'Aufruf: C:/Python314/python.exe -m tools.s2uc_factor_material produce docs/S2UC_FC_DEV_AUTORISIERUNG_20261001.json',
'Material: reports/s2uc/factor-continuation-material-fc-dev-01.18 Dateien,4 Basisepisoden mit16 Vektoren/768 Komponenten,11 Fallsequenzen mit129 Frames. Elf Pruefziele,48 weitere erreichbare Lernziele. Kein Rezeptor-/NJ-Aufruf.',
'Materialumfang '+str(v['material_bytes'])+'/4194304 Byte einschliesslich Abschluss,262144 Byte Abschlussreserve. claim/manifest/closure und Einzeldateihashes erhalten.',
'Vollstaendigkeit, finite binary64-Werte, Profile/Digests, Herkunft, bitgleicher A/D-Anfang, positiver Nullpraefix sowie saemtliche Gain-/Fallableitungen mit unveraendertem Leser bestaetigt. Keine erneute Basissynthese. Nach Auswertung saemtliche Materialhashes unveraendert.',
'Code-/Laufzeit-/Planbindungen vor Produktion und nach Auswertung bestaetigt. Qualifikation G1-G7 wiederverwendet; keine unveraenderten Volltests wiederholt.',
'', '2. Elf Pruefziele: konkrete Prognosen',
'Fall | Herkunft scaled/legacy | Status scaled | Status legacy | MAE scaled konkret | MAE legacy konkret | MAE Persistenz']
for n,l in zip(s['policies']['scaled']['rows'],s['policies']['legacy']['rows']):
    assert n['case_id']==l['case_id']
    lines.append(' | '.join([n['case_id'],n['origin_category']+'/'+l['origin_category'],n['prediction_status'],l['prediction_status'],fmt(n['context_mae']),fmt(l['context_mae']),fmt(n['persistence_mae'])]))
for key in ('scaled','legacy'):
    lines+=['',key+' Herkunft/Abdeckung/Enthaltungen:',json.dumps(s['policies'][key]['origin_and_prediction'],indent=2)]
lines+=['','3. Gemeinsame Zielmengen und Vergleich',
'Positive Delta bedeutet: Vergleichsarm-MAE minus getestete Policy-MAE. Konkrete Prognosen ausschliesslich auf identischen gemeinsam abgedeckten Zielmengen verglichen. Keine Enthaltung als MAE0 interpretiert.']
for key,part in s['paired'].items():
    lines+=[key+': Ziele '+','.join(x['case_id'] for x in part['rows'])+'; n='+str(part['count'])+', links MAE '+fmt(part['left_mae'])+', rechts MAE '+fmt(part['right_mae'])+', Delta '+fmt(part['delta'])+'; besser/gleich/schlechter='+str((part['better'],part['equal'],part['worse']))]
lines+=['','Festes Vollabdeckungsschema auf allen elf Zielen: H_scaled=scaled wenn konkrete Prognose vorhanden, sonst Persistenz; H_legacy entsprechend. Ausschliesslich Observer, kein Produkt-Fallback.',
json.dumps(s['full_means'],indent=2),
'Die Schluessel legacy/scaled unter full_means/full_rows bezeichnen diese Beobachterschemata; die konkreten Werte stehen oben und unter policies.*.rows.context_mae.',
'','4. Alle Schadensfaelle auf den elf Pruefzielen',
'Gegen Persistenz:',json.dumps(s['harms_against_persistence'],indent=2),
'Gegen Legacy-sonst-Persistenz:',json.dumps(s['harms_against_legacy'],indent=2),
'Enthaltung, eindeutige Herkunft und konkrete Prognose bleiben getrennt. Ein Gain aus dem Hinweis ist eine Hypothese fuer die Fortsetzung; Gainwechsel und GP werden nicht nachtraeglich ausgeschlossen.',
'','5. 48 Lernziele getrennt',
'Die weiteren erreichbaren Ziele einschliesslich Uebergaenge zur Query gehoeren nicht zum Primaerergebnis. Herkunft extern aus der Zielposition; positive Lernherkunft nur bei vorher abgeschlossener Vierergruppe vor dem Hinweispaar. Keine Aenderung der vorab festgelegten elf Prueflabels.']
for key in ('scaled','legacy'):
    lines += [key+':',json.dumps(ls['policies'][key]['origin_and_prediction'],indent=2)]
lines += ['Lernziel-Vollabdeckung:',json.dumps(ls['full_means'],indent=2),
'Alle Lernziel-Schaeden gegen Persistenz:',json.dumps(ls['harms_against_persistence'],indent=2),
'Alle Lernziel-Schaeden gegen Legacy-Beobachterschema:',json.dumps(ls['harms_against_legacy'],indent=2),
'Jede Lernposition einschliesslich Einzel-MAE und gemeinsamer Masken steht unter result.json/learning_targets; nicht mit den elf Pruefzielen poolen.',
'','6. Separate Kandidaten-Rollenprobe',
'Bestehendes A einmal regulaer aufnehmen, dann FH-Hinweis/Folgeframe.7 Frames pro Policy, Ziel7. Kein neues Material, keine Primaerziel-Erweiterung.',
json.dumps(probe['rows'],indent=2),
'','7. Kausalitaet, Zustand und Ressourcen',
'Beide Policies pro Fall leer gestartet. Matchingreceipts, Speicherzustand nach jedem Frame, Endzustand und Aufnahmeordinale identisch; Vergleich gegen PairContextAdapter ohne Prognose ebenfalls Bestandteil jedes Replays. Keine Rueckspeisung von Prognose oder Prueferlabels.',
'Jedes der129 Primaerframes pro Policy genau einmal aufgenommen;59 erreichbare Ziele=11 Pruefziele+48 Lernziele. Kandidatenprobe separat7 Frames. Zwei Policies bedeuten zwei getrennte Replays desselben exportierten Bestands, keine zweite Materialproduktion.',
'Prognose vor Zielframeabruf und vor Hinweispaaraufnahme. FH/GH/GR/GP sowie FD/GD besitzen nachweislich gleiche Prognosen und Vorzustaende vor unterschiedlicher Fortsetzung. Prognoseslots nach Verbrauch/Abschluss frei.',
'Ressourcen je Fall/Policy in verification.json; Kandidatenprobe in candidate-probe.json. Tupelbuilder ueber Generator-Yields als transienter Slot bilanziert; kein harter Prozess-RAM-Beleg.']
resources=[d for c in v['resources'].values() for d in c.values()]+[x['resources'] for x in probe['systems'].values()]
peaks={key:max(x[key] for x in resources) for key in ('frame_peak','output_slots_peak','combined_peak','output_python_bytes_peak','builder_peak_components','transient_output_slots_peak','temporary_vector_lists')}
lines += [json.dumps(peaks,indent=2),'Konservative Obergrenze Framepeak+2 Ausgaben: '+str(peaks['frame_peak']+2)+'/20. Alle Builderzaehler am Ende0: '+str(all(x['builder_components']==0 for x in resources)),
'','8. Aufbauabweichungen und Aussagegrenze',json.dumps(r['setup_deviations'],indent=2),
'Keine Ersatzdaten, Schwellen- oder Matchinganpassung. Es gelten nur die gebundenen synthetischen Adapteraufgaben; keine Audio-/NJ-Robustheit oder allgemeine Herkunftserkennung. FC-DEV ist jetzt bekannt; FC-EVAL bleibt unproduziert und unausgewertet.',
'','9. Naechster Vorschlag',
'Development-Paket nach technischen Kriterien abnehmen; die beobachteten Gainwechsel-/Persistenzschaeden als Grenzen der Faktorhypothese erhalten. Danach unveraenderte Regel und Auswertung fuer eine gesondert beauftragte einmalige FC-EVAL-Pruefung binden. Kein Optimieren der Faelle oder der Regel anhand dieser Development-Ergebnisse. Positiver Gesamtnutzen ist keine technische Abnahmebedingung.']
with (OUT/'REPORT.txt').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
ledger=dict(material_bytes=v['material_bytes'],observer_bytes_before_ledger_and_inventory=sum(f.stat().st_size for f in OUT.iterdir() if f.is_file()),hard_process_ram_measured=False,peaks=peaks)
with (OUT/'resource-ledger.json').open('x') as f:json.dump(ledger,f,indent=2)
inventory={f.name:dict(sha256=m.sha(f),bytes=f.stat().st_size) for f in OUT.iterdir() if f.is_file()}
with (OUT/'inventory.json').open('x') as f:json.dump(inventory,f,indent=2)
print(json.dumps(dict(full=s['full_means'],scaled_coverage=s['policies']['scaled']['context_covered'],legacy_coverage=s['policies']['legacy']['context_covered'],harms=s['harms_against_persistence'],deviations=r['setup_deviations'],resources=peaks),indent=2))
