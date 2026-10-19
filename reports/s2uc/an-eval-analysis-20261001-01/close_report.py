"""Verify and report saved evaluation; no material synthesis or replay."""
import json
from pathlib import Path
from tools import s2uc_an_material as m

OUT=Path(__file__).resolve().parent


def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)


def main():
    r=m.read(OUT/'result.json',8388608);freeze=m.read(OUT/'freeze.json');criteria=m.read(OUT/'criteria.json')
    dev=m.read(m.ROOT/'reports/s2uc/an-dev-search-20261001-01/tau-4.json',8388608)
    assert (r['epsilon'],r['tau'])==(freeze['epsilon'],freeze['tau'])==(dev['epsilon'],dev['tau'])
    assert len(r['cases'])==11 and len(r['learning_cases'])==48
    resources=[];origins={};harms={'primary':{},'learning':{}}
    for cid,c in r['cases'].items():
        exact=c['systems']['exact_retrieval'];approx=c['systems']['signal_approx_retrieval']
        assert exact['states']==approx['states'] and exact['final_state']==approx['final_state']
        for arm,system in c['systems'].items():
            assert system['admitted']==list(range(1,c['target']+1)) and system['slots_released']
            assert all(row['forecast_bound'] for row in system['pull_log'] if row['index']>=3 and row['index']%2)
            resources.append(dict(case=cid,arm=arm,**system['resources']))
        origins[cid]=dict(rows=c['rows'],receipts={arm:json.loads(s['targets'][-1]['forecast']['provenance_json']) for arm,s in c['systems'].items()})
    for arm in ('exact_retrieval','signal_approx_retrieval'):
        assert sum(len(c['systems'][arm]['admitted']) for c in r['cases'].values())==129
        for left,right in [('R1','R3'),('R0','N3')]:
            assert r['cases'][left]['systems'][arm]['targets'][-1]['forecast']==r['cases'][right]['systems'][arm]['targets'][-1]['forecast']
    for group,rows in [('primary',r['cases']),('learning',r['learning_cases'])]:
        for cid,c in rows.items():
            exact=c['rows']['exact_retrieval'];approx=c['rows']['signal_approx_retrieval']
            for label,delta in [('exact_vs_persistence',exact['observer_hybrid_mae']-exact['persistence_mae']),
                ('approx_vs_persistence',approx['observer_hybrid_mae']-approx['persistence_mae']),
                ('approx_vs_exact',approx['observer_hybrid_mae']-exact['observer_hybrid_mae'])]:
                if delta>0:harms[group].setdefault(label,[]).append(dict(case=cid,target=c['target'],mae_increase=delta,exact=exact,approx=approx))
    extra=[cid for cid,c in r['cases'].items() if c['rows']['signal_approx_retrieval']['origin_category']=='WRONG' and c['rows']['exact_retrieval']['origin_category']!='WRONG']
    gain=sum(r['cases'][cid]['rows']['signal_approx_retrieval']['origin_category']=='CORRECT' for cid in ('R1','R2'))-sum(r['cases'][cid]['rows']['exact_retrieval']['origin_category']=='CORRECT' for cid in ('R1','R2'))
    assert extra==criteria['additional_wrong'] and gain==criteria['gain_R1_R2']
    assert criteria['status']==('SYNTHETIC_PCM_NJ_CRITERIA_MET' if not extra and gain>=1 else 'CRITERIA_NOT_MET')
    peaks={k:max(x[k] for x in resources) for k in resources[0] if k not in ('case','arm')}
    assert peaks['frame_peak']<=18 and peaks['output_slots_peak']<=2 and peaks['combined_peak']<=20
    assert peaks['receipt_bytes_peak']<=16384 and peaks['receipt_transient_utf8_bytes_peak']<=32768
    assert peaks['temporary_numeric_vectors_peak']==0
    save('resource-ledger.json',dict(peaks=peaks,rows=resources))
    save('origin-and-abstentions.json',origins);save('all-harms.json',harms)
    comparison={}
    for label,value in [('AN-DEV',dev),('AN-EVAL',r)]:
        comparison[label]=dict(epsilon=value['epsilon'],tau=value['tau'],primary=11,learning=48,
            primary_summary=value['summary'],learning_summary=value['learning_summary'])
    save('dev-eval-comparison.json',dict(partitions=comparison,pooled_success_rate=None,
        limitation='Same controlled synthetic recipe; DEV selected parameters, EVAL tested one frozen setting. No general natural audio claim.'))
    b,p=m.load_binding();folder=m.ROOT/p['partitions']['AN-EVAL']['output_directory'];pre=m.read(OUT/'preevaluation.json')
    assert all(m.sha(folder/name)==h for name,h in pre['material'].items())
    assert all(m.sha(m.ROOT/name)==h for name,h in freeze['dev_files'].items())
    assert m.sha(OUT/'run_evaluation.py')==freeze['runner_sha256']
    assert m.sha(m.ROOT/'docs/S2UC_AN_EVAL_AUTORISIERUNG_20261001.json')==freeze['authorization_sha256']
    assert m.sha(m.PLAN)==freeze['plan_sha256'] and m.sha(m.BINDING)==freeze['binding_sha256']
    save('final-verification.json',dict(status='PASS',production_calls=1,production_exit_code=0,
        evaluation_calls=1,evaluation_exit_code=0,settings=1,frames_per_arm=129,primary=11,learning=48,
        dev_files_preserved=len(freeze['dev_files']),eval_material_unchanged=True,parameters_unchanged=True,
        calibration_performed=False,search_performed=False,code_profile_plan_unchanged=True,
        frozen_runner_unchanged=True,causality=True,states_identical=True,slots_released=True,peaks=peaks))
    part=m.read(OUT/'partition-verification.json')
    lines=[]
    for cid,c in r['cases'].items():
        e=c['rows']['exact_retrieval'];a=c['rows']['signal_approx_retrieval']
        lines.append(f"{cid:2} | {e['origin_category']:7} | {a['origin_category']:7} | {e['persistence_mae']:.15g} | {e['observer_hybrid_mae']:.15g} | {a['observer_hybrid_mae']:.15g}")
    report=f'''MCM S2UC -- AN-EVAL: einmalige Produktion und eingefrorene Einzelauswertung
2026-10-01

ERGEBNIS
{criteria['status']}: zwei zusaetzliche korrekte R1/R2-Zuordnungen,
keine zusaetzlichen falschen Einzelzuordnungen, keine verlorenen exakten,
signalbedingt verlorenen exakten oder verlorenen korrekten Exaktzuordnungen.
Die festgelegten Kriterien sind in diesem kontrollierten synthetischen
PCM-/Rezeptor-/NJ-Pfad erfuellt. Keine allgemeine natuerliche Wiedererkennung
und keine schaedigungsfreie Fortsetzung nachgewiesen.

PARAMETER UND VORHERIGE BINDUNG
epsilon_AUDIO={r['epsilon']!r} ({r['epsilon'].hex()})
tau_AUDIO={r['tau']!r}=1/32 ({r['tau'].hex()})
Exakt aus gespeichertem DEV-Auswahlbeleg uebernommen, keine neue Kalibration.
freeze.json vor Produktion: korrigierter Auswertungsrunner, lokaler Code,
Python-/NumPy-Bindung, Profil, Materialplan, Herkunftslabels und Parameter.
103 DEV-Dateien inklusive Material und Auswertung vorher gehasht und am
Ende unveraendert bestaetigt. Der DEV-Beobachterfix ist unveraendert uebernommen.
Evaluation-Runner ohne Kalibrations- und Parameterauswahlaufruf.

PRODUKTION UND PARTITIONSTRENNUNG
Genau ein AN-EVAL-Produktionsaufruf: MATERIAL_COMPLETE,Exit0.
49 Rezeptor-/49 NJ-Aufrufe, {part['eval_files']} Dateien,
{part['eval_bytes']}/4194304 Byte einschliesslich Abschluss.
Keine Kalibrationsdateien, keine Ersatzdaten, kein Wiederholungsversuch.
Seeds von DEV/EVAL disjunkt; vier Basis-PCM-Hashes ebenfalls disjunkt.
Herkunft, PCM-Ableitungen, Zeitpunkte/Retiming, Profile und Projektionsdigests
durch unveraenderten Leser geprueft. EVAL-Material nach Auswertung bytegleich.
Beide Partitionen teilen das synthetische Rezept; keine Behauptung allgemeiner
Unabhaengigkeit aus verschiedenen Seeds. Keine gemeinsame Erfolgsquote.
closure.json ist der Materialabschluss; die separate Auswertung ist in
verification.json und final-verification.json belegt.

HERKUNFT, SIGNALVERLUST UND ABDECKUNG
Exakt:1 korrekt,9 Enthaltungen,1 falsch; Kontextabdeckung2/11.
Signal-/Naeherungsabruf:4 korrekt,6 Enthaltungen,1 falsch; Kontextabdeckung5/11.
R0/R1/R2/R3 korrekt; N1/N2/N4/Z0/Z1/P0 enthalten sich.
P0: positive Herkunft wegen geringem Signal unabgedeckt. Kein verlorener
Exakttreffer, da auch der exakte Abruf dort keine Zuordnung lieferte.
N3: beide Arme ordnen trotz wahrer D-Herkunft dem A-Kontext zu. Gemeinsamer
Anfang bleibt Identifizierbarkeitsgrenze. Der bestehende Fehler wird sichtbar
ausgewiesen, obwohl er gegenueber der exakten Referenz nicht zusaetzlich ist.
Alle Receipt-/Enthaltungsgruende in origin-and-abstentions.json.

ELF PRUEFZIELE
Fall | Herkunft exakt | Herkunft neu | Persistenz-MAE | Exaktschema-MAE | Naeherungsschema-MAE
{chr(10).join(lines)}
Schema-MAE bezeichnet den festen Beobachter Kontext-sonst-Persistenz.
Konkrete Kontext-MAE bei Enthaltung null, niemals als0 ausgegeben.
Gemeinsame Kontext-Zielmasken und Paarvergleiche in result.json/summary.

DEV / EVAL GETRENNT, BEI DEMSELBEN AUSGEWAEHLTEN PARAMETER
AN-DEV Vollabdeckungs-Mittelwerte:
{json.dumps(dev['summary']['comparison']['full_means'],indent=2)}
AN-EVAL Vollabdeckungs-Mittelwerte:
{json.dumps(r['summary']['comparison']['full_means'],indent=2)}
Beide jeweils elf Pruefziele und 48 getrennte Lernziele.
DEV ist Auswahlmaterial; EVAL prueft genau eine vorher festgelegte Einstellung.
Keine gepoolte Quote. Vollstaendige Gegenueberstellung dev-eval-comparison.json.

PROGNOSESCHAEDEN
EVAL R3: korrekte Herkunft, aber MAE0.0018484613305405366 statt0 gegen
Persistenz und exaktes Schema. DEV R3 separat:0.0023763522335992263 statt0.
Keine weiteren beobachteten Pruefziel-Schaeden gegen diese Baselines;
auch das exakte Schema zeigt hier keinen Schaden gegen Persistenz.
Keine beobachteten Lernziel-Schaeden oder zusaetzlichen Lern-Herkunftsfehler
in den48 EVAL-Lernzielen. Alle Einzelfaelle/Delta-Werte in all-harms.json,
Lernziel-Einzelwerte und eigener Bericht in result.json/learning_cases.
Mittlere Gewinne heben weder R3-Schaden noch N3-Herkunftsfehler auf.

KAUSALITAET, SPEICHER UND RESSOURCEN
Ein Auswertungsaufruf, eine Einstellung, Exit0; kein Auswertungsabbruch,
keine Wiederholung und keine Aenderung am eingefrorenen Runner.
129 Aufnahmen je Arm, leerer Start je Geschichte, beide Arme legacy_v1.
Vorhersage vor Zielzugriff, jeder Frame einmal aufgenommen, Speicherzustand
nach jedem Frame identisch zur Referenz und zwischen beiden Armen,
Ausgabeslots am Ende freigegeben. R1/R3 und R0/N3 geben vor Folgeframe
identische Vorhersagen aus. Gespeicherte Nachweise ohne Replay nachgeprueft.
Peaks:{peaks['frame_peak']} Frames,{peaks['output_slots_peak']} Ausgaben,
{peaks['combined_peak']} gemeinsam. Receipt{peaks['receipt_bytes_peak']} Byte,
transiente Receipt-UTF8 {peaks['receipt_transient_utf8_bytes_peak']} Byte,
{peaks['temporary_numeric_vectors_peak']} temporaere48er-Distanzkopien.
Grenzen18+2 eingehalten; kein harter Prozess-RAM-Beleg fuer gesamten Export,
NumPy oder Betriebssystem. Einzelmessungen resource-ledger.json.

ENTSCHEIDUNGSVORSCHLAG
Projektleiter: Befund als begrenzten Nachweis verbesserter Wiedererkennung
bei den vorgegebenen synthetischen PCM-Stoerungen abnehmen. signal_approx_v1
explizit waehlbar und experimentell lassen; exakter Abruf und legacy_v1
bleiben Standard. Keine automatische Skalierungskombination oder Aktivierung.
Naechster sinnvoller Entwicklungsauftrag waere ein begrenzter Konzeptvertrag
zur Trennung von Herkunftszuordnung und Fortsetzungsnutzen: R3 zeigt, dass
korrekte Herkunft noch keine verlaessliche Fortsetzung garantiert. Erst
eine unabhaengig pruefbare Hypothese/Gegenprobe definieren, keine nachtraeglich
auf R3 zugeschnittene Regel einbauen. Kein weiterer Versuch heute.
AN-DEV und AN-EVAL sind nun bekanntes Material, nicht erneut unberuehrte Tests.

BELEGE
freeze.json: Bindung vor Produktion.
preevaluation.json: Evaluationsexport vor genau einer Auswertung.
result.json: alle elf Pruef- und48 Lernziele, Zustaende/Receipts/Ressourcen.
criteria.json: fachliche Kriterien; keine nachtraegliche Parameterwahl.
partition-verification.json: Seeds/PCM-Trennung, Mengen/Produktionsabschluss.
verification.json/final-verification.json: Integritaet, Kausalitaet, Freigabe.
dev-eval-comparison.json: getrennte Ergebnisse, keine gemeinsame Erfolgsquote.
all-harms.json/origin-and-abstentions.json/resource-ledger.json: Detailbelege.
inventory.json: Dateihashes dieses Abschlusses.
'''
    with (OUT/'REPORT.txt').open('x',encoding='utf-8') as f:f.write(report)
    save('inventory.json',{f.name:m.sha(f) for f in OUT.iterdir() if f.is_file() and f.name!='inventory.json'})
    print(json.dumps(dict(criteria=criteria,peaks=peaks,dev_files_preserved=len(freeze['dev_files']),material_bytes=part['eval_bytes']),indent=2))


if __name__=='__main__':main()
