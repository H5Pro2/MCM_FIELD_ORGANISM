"""Read-only formatting of the one frozen AR evaluation and saved DEV result."""
import json
from pathlib import Path
from tools import s2uc_ar_material as m
OUT=Path(__file__).resolve().parent
def read(name):return json.loads((OUT/name).read_text())
r=read('result.json');decision=read('criteria.json');v=read('verification.json');freeze=read('freeze.json')
devdir=m.ROOT/'reports/s2uc/ar-dev-search-20261001-01'
d=json.loads((devdir/'tau-3.json').read_text())
fmt=lambda x:'undefiniert (Enthaltung)' if x is None else format(x,'.12g')
s=r['summary'];c=s['comparison'];learning=r['learning_summary'];lc=learning['comparison']
lines=['MCM S2UC -- AR-EVAL einmalige Produktion und feste Evaluation','2026-10-01','',
'ABGESCHLOSSEN: MATERIAL_COMPLETE, genau ein Produktionsaufruf (Exit0), genau eine Parametereinstellung. Elf Pruefziele und48 Lernziele getrennt. Keine Evaluation-Kalibration oder Parametersuche.',
'','1. Vorabbindung und Herkunft',
'epsilon=2^-10=0.0009765625, tau=1/64=0.015625. Beide Werte vor Produktion aus abgenommenem AR-DEV-Ergebnis eingefroren; keine Nachbestimmung anhand Evaluation.',
'Plan SHA256 '+freeze['plan_sha256'],
'Produktionsbindung SHA256 '+freeze['binding_sha256'],
'freeze.json enthaelt Plan/Seeds/Profil/Herkunftslabels, Code-/Laufzeitbindungen, Auswertungsrunnerhash sowie38 Development-Dateibindungen. Urspruenglicher Plan und zusaetzliche Bindung unveraendert.',
'Autorisierung docs/S2UC_AR_EVAL_AUTORISIERUNG_20261001.json. Einziger Aufruf: C:/Python314/python.exe -m tools.s2uc_ar_material produce docs/S2UC_AR_EVAL_AUTORISIERUNG_20261001.json',
'21 Materialdateien in reports/s2uc/signal-approx-material-ar-eval-01. Vier Basisepisoden mit768 Komponenten,2 Rauschhinweisframes,3 reine Stoerungsframes und0 Kalibrationsframes. Elf Fallsequenzen mit129 Frames.',
'Materialausgabe '+str(v['material_bytes'])+'/4194304 Byte,262144 Byte Abschlussreserve. Werte-/Dateihashes, Profile, Genealogie, A/D-Praefix, R1/R3-Gleichheit, Mischherkunft und Kleinsignalvarianten bestaetigt.',
'Partitionstrennung: disjunkte Seeds und Basisepisoden-Hashes, keine Ableitung zwischen DEV/EVAL. Gemeinsames synthetisches Rezept begrenzt jede Unabhaengigkeitsaussage. Evaluation-Kalibrationsdatei leer; reservierter Seed bleibt gemaess gebundenem Generator unbenutzt.',
'','2. Fachliche Kriterien ohne Neuauswahl',json.dumps(decision,indent=2),
'Jede zusaetzliche falsche Einzelzuordnung gegen exakten Abruf haette die Abnahme als verbesserte Wiedererkennung verhindert. Ohne zusaetzlichen korrekten R1/R2-Treffer waere das Robustheitsziel nicht nachgewiesen. MAE ist kein Ersatz fuer diese Herkunftskriterien.',
'Verlorene exakte Zuordnungen: '+str(s['lost_exact_assignments'])+'; signalbedingte Verluste: '+str(s['signal_lost_exact_assignments'])+'; verlorene korrekte Exakttreffer: '+str(s['lost_correct_exact']),
'','3. Elf Pruefziele: Herkunft, Status und konkrete MAE',
'Fall | Herkunft exakt/neu | Status exakt/neu | MAE konkret exakt/neu/Persistenz | MAE Beobachterschema exakt/neu']
for e,n in zip(c['policies']['exact_retrieval']['rows'],c['policies']['signal_approx_retrieval']['rows']):
    assert e['case_id']==n['case_id']
    lines.append(' | '.join([e['case_id'],e['origin_category']+'/'+n['origin_category'],e['prediction_status']+'/'+n['prediction_status'],fmt(e['context_mae'])+'/'+fmt(n['context_mae'])+'/'+fmt(e['persistence_mae']),fmt(e['observer_hybrid_mae'])+'/'+fmt(n['observer_hybrid_mae'])]))
for policy in ('exact_retrieval','signal_approx_retrieval'):
    lines += ['',policy+' Herkunft und Abdeckung:',json.dumps(c['policies'][policy]['origin_and_prediction'],indent=2)]
lines += ['','4. Identische gemeinsame Zielmengen und Schaeden',
'Beide Arme verwenden legacy_v1-Fortsetzung. Exakter Abruf bzw. Signal-/Naeherungsabruf bezeichnet ausschliesslich die Abrufpolicy. Null bei context_mae bedeutet Enthaltung, niemals fehlerfreie Prognose.']
for key,pr in c['paired'].items():
    lines.append(key+': Ziele '+str([x['case_id'] for x in pr['rows']])+', n='+str(pr['count'])+', MAE links/rechts='+fmt(pr['left_mae'])+'/'+fmt(pr['right_mae'])+', Delta='+fmt(pr['delta'])+', besser/gleich/schlechter='+str((pr['better'],pr['equal'],pr['worse'])))
lines += ['Festes Vollabdeckungsschema auf allen elf Zielen: Kontext falls konkrete Prognose, sonst Persistenz. Ausschliesslich Observer, keine Produkt-Fallbackregel.',json.dumps(c['full_means'],indent=2),
'Alle Schaeden gegen Persistenz:',json.dumps(c['harms_against_persistence'],indent=2),
'Alle Schaeden gegen exaktes Kontext-sonst-Persistenz-Schema:',json.dumps(c['harms_against_exact_retrieval'],indent=2),
'N3 bleibt die kausale Herkunftsgrenze des gemeinsamen Anfangs; ein gleicher Fehler beider Arme ist kein zusaetzlicher Fehler, aber weiterhin ein Herkunftsfehler. R3 prueft unabhaengig von korrekter Herkunft die unpassende Fortsetzung.',
'','5. 48 Lernziele separat',
'Nichtprimaere erreichbare Positionen einschliesslich Uebergaengen; keine Erfolgsquote mit den elf Pruefzielen vermischt. Positive Lernherkunft bedeutet Basis in einem vor dem Hinweispaar abgeschlossenen Viererblock vorhanden.',
'Neue Lernziel-Fehlzuordnungen: '+str(learning['additional_wrong'])+'; verlorene exakte Zuordnungen: '+str(learning['lost_exact_assignments'])]
for policy in ('exact_retrieval','signal_approx_retrieval'):
    lines += [policy+':',json.dumps(lc['policies'][policy]['origin_and_prediction'],indent=2)]
lines += ['Lernziel-Schaeden gegen Persistenz:',json.dumps(lc['harms_against_persistence'],indent=2),
'Lernziel-Schaeden gegen exaktes Beobachterschema:',json.dumps(lc['harms_against_exact_retrieval'],indent=2),
'Alle48 Einzelwerte und gemeinsamen Masken stehen in result.json/learning_summary.',
'','6. DEV/EVAL getrennt, keine gemeinsame Erfolgsquote','Kennzahl | AR-DEV bei1/64 | AR-EVAL bei1/64']
dc=d['summary']['comparison']
for key in ('persistence','exact_retrieval','signal_approx_retrieval','signal_approx_retrieval_vs_persistence','signal_approx_retrieval_vs_exact_retrieval'):
    lines.append(key+' (Vollabdeckung) | '+fmt(dc['full_means'][key])+' | '+fmt(c['full_means'][key]))
for policy in ('exact_retrieval','signal_approx_retrieval'):
    lines.append(policy+' konkrete Prognoseabdeckung | '+str(dc['policies'][policy]['context_covered'])+'/11 | '+str(c['policies'][policy]['context_covered'])+'/11')
lines += ['Zusaetzliche Herkunftsfehler | '+str(d['summary']['additional_wrong'])+' | '+str(s['additional_wrong']),
'Verlorene exakte Zuordnungen | '+str(d['summary']['lost_exact_assignments'])+' | '+str(s['lost_exact_assignments']),
'','7. Kausalitaet, Zustand und Ressourcen',
'Alle Geschichten leer gestartet,129 Frames pro Arm jeweils einmal aufgenommen;59 erreichbare Ziele=11 Pruefziele+48 Lernziele. Speicherzustand nach jedem Frame und Abschluss gegen unveraenderten PairContextAdapter und zwischen Armen identisch.',
'R1/R3 und R0/N3 haben identische eingefrorene Prognosen und Vorzustaende vor ihrem unterschiedlichen Zielframe. Keine Zukunftslabels im Abruf. Ausgabeslots nach Verbrauch/Abschluss freigegeben.',
'Einmalige Erzeugung und je Arm ein Replay dieses Bestands. Keine zweite Materialproduktion, keine Suche oder Anpassung. Ressourcenbeobachtung veraendert keine Auswahl.']
resources=[x for settings in v['resources'].values() for case in settings.values() for x in case.values()]
peaks={key:max(x[key] for x in resources) for key in ('frame_peak','output_slots_peak','combined_peak','receipt_bytes_peak','receipt_transient_utf8_bytes_peak','temporary_numeric_vectors_peak','match_metadata_peak')}
lines += [json.dumps(peaks,indent=2),'Grenzen18 Frames inkl.Hinweise,2 Ausgaben,20 gemeinsam; Receipt16384 Byte, transiente Provenienz32768 Byte. Keine48er-Distanzkopie. Observerarchive getrennt bilanziert, kein harter Prozess-RAM-Nachweis.',
'38 DEV-Dateien, Evaluationsmaterial sowie Code-/Plan-/Laufzeitbindungen nach Abschluss unveraendert bestaetigt. partition-verification.json, verification.json und final-verification.json enthalten die Belege.',
'','8. Aussagegrenze und naechster Vorschlag',
'Befund ausschliesslich fuer diese vorab festgelegte synthetische Aufgabenklasse. Kein Nachweis allgemeiner Wiedererkennung oder Audio-/NJ-Robustheit. Beide AR-Partitionen sind jetzt bekannt; geaenderte Regeln benoetigen neue unberuehrte Pruefdaten.',
'An Projektleiter zur fachlichen Abnahme/Statusentscheidung uebergeben. Empfehlung bei erfuellten Herkunftskriterien: Signal-/Naeherungsabruf als ausdruecklich waehlbare experimentelle Abrufhypothese erhalten, mit R3-Prognoserisiko und N3-Herkunftsgrenze. Exakter Abruf und legacy_v1 bleiben Standard. Keine automatische Aktivierung von Naeherungsabruf oder skalierter Fortsetzung. Bei verletzten Kriterien Ansatz in dieser Fassung nicht als verbesserte Wiedererkennung abnehmen.']
with (OUT/'REPORT.txt').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
with (OUT/'comparison.json').open('x') as f:json.dump(dict(AR_DEV=dict(summary=d['summary'],learning_summary=d['learning_summary']),AR_EVAL=dict(summary=s,learning_summary=learning),pooled=False),f,indent=2)
with (OUT/'resource-ledger.json').open('x') as f:json.dump(dict(material_bytes=v['material_bytes'],observer_bytes_before_ledger_inventory=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file()),peaks=peaks,hard_process_ram_measured=False),f,indent=2)
print(json.dumps(dict(criteria=decision,means=c['full_means'],harms=c['harms_against_persistence'],peaks=peaks),indent=2))
