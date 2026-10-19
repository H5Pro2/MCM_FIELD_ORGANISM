"""Read-only assessment of a completed ULZ1 archive. No policy/source generation."""
import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'reports/s2uc/ulz1-comparison-20261004-01'
OUT=ROOT/'reports/s2uc/ulz1-assessment-20261004-01'

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,x):(OUT/name).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def render(v,assessment):
    n=lambda x:f'{x:.9f}'
    lines=['# ULZ1: einmaliger Forschungsdurchlauf, 2026-10-04','',
        '**COMPLETE – alle 64 Forschungsquellen und 128 Arme vollständig ausgeführt.**',
        'Einmalfreigabe verbraucht. Kein Neustart, keine Fall-/Seed-Auswahl, keine Regeländerung.',
        'U bleibt unverändert; L wurde nicht als neuer Standard übernommen. A1/K1 aus.','',
        '## Zwei vorab festgelegte Primärfragen','',
        'D=MAE(U)−MAE(L), gepaarte Mittelwerte aus je32 Wiederholungen. Negative Werte',
        'bedeuten geringeren U-Fehler. Vorab bestimmte10.000 Clusterbootstrap-Ziehungen;',
        'zweiseitige97,5%-Intervalle mit Bonferroni-Aufteilung für genau zwei Fragen.','',
        '| Frage | U-MAE | L-MAE | U−L | 97,5%-Intervall | erwartete Richtung | Urteil |',
        '| --- | ---: | ---: | ---: | --- | --- | --- |']
    for x in v['primary']:
        means=v['means'][x['condition']][x['mask']]
        label='Stabil: S, Y33–128' if x['condition']=='S' else 'Früher Wechsel: W, Y129–160'
        lines.append(f"| {label} | {n(means['U'])} | {n(means['L'])} | {n(x['mean'])} | [{n(x['ci'][0])}; {n(x['ci'][1])}] | {'U besser' if x['direction']=='negative' else 'L besser'} | {x['verdict']} |")
    lines+=['',f"**Erwartete Abwägung: {v['tradeoff']}.** Sie gilt nur bei Bestätigung beider Richtungen.",
        'Primärzielzahlen je Arm:3.072 im stabilen und1.024 im frühen Wechselkontrast.',
        'Ein Null einschließendes Intervall ist kein Gleichwertigkeitsnachweis.',
        'Sekundäre Vorteile ersetzen keinen fehlenden Primärnachweis.','',
        '## Vollständige Masken und sekundäre Unsicherheit','',
        'Die beiden Primärzeilen sind oben verbindlich beurteilt. Alle anderen Zeilen',
        'und Orientierungsaufteilungen sind explorativ. Vollständige32 Wiederholungswerte',
        'und alle Orientierungsintervalle: [Kontraste](contrasts.csv).','',
        '| Bedingung | Maske | U | L | U−L | Intervall | Niveau |',
        '| --- | --- | ---: | ---: | ---: | --- | --- |']
    for x in assessment['contrasts']:
        if x['orientation']!='ALL':continue
        means=v['means'][x['condition']][x['mask']]
        lines.append(f"| {x['condition']} | {x['mask']} | {n(means['U'])} | {n(means['L'])} | {n(x['mean'])} | [{n(x['ci'][0])}; {n(x['ci'][1])}] | {x['level']} |")
    lines+=['','Alle519 Ziele je Armgeschichte einschließlich Präfix und Gerüst bleiben enthalten.',
        '[Vollständiger Zielverlauf](targets.csv) enthält U/L-Fehler, Einzeldifferenz,',
        'kumulierte Differenz, Ausgabeoriginal, Wahlgrund und Z-Zustand. Keine Auswahl nur',
        'warmer/erfolgreicher Ziele. [Fallmittel](case-mask-means.csv) enthalten sämtliche Masken.','',
        '## Gewinne und Schäden','',
        '| Bedingung | Maske | U besser | U schlechter | gleich | Gewinnsumme | Schadenssumme | maximaler Schaden | schlechtester Fallmittelwert U−L |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for h in assessment['harms']:
        lines.append(f"| {h['condition']} | {h['mask']} | {h['improved']} | {h['worse']} | {h['equal']} | {n(h['gain_sum'])} | {n(h['harm_sum'])} | {n(h['max_harm'])} | {n(h['worst_replicate_mean'])} |")
    lines+=['','Überlappende Masken nicht addieren. Keine Schadensfreiheitsbehauptung und keine',
        'nachträglich übertragene A1-Schadensschwelle. [Vollständige Schadensbilanz](harms.csv).','',
        '## Regulärer Z-Lebenszyklus','',
        '| Bedingung | Z-Kandidat erzeugt | Z-Kandidat ersetzt | Z promoviert | Z aus Retained verdrängt | alle Promotionen | alle Verdrängungen |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for c,z in v['lifecycle_totals'].items():
        lines.append('| '+c+' | '+' | '.join(str(z.get(k,0)) for k in ('Z_candidate_creations','Z_candidate_replacements','Z_promotions','Z_evictions','all_promotions','all_evictions'))+' |')
    lines+=['','| Bedingung | Arm | Y-Ziele | Z berechtigt | Z kalt | Z warm | Z als Kandidat | Z als Retained | Z ausgewählt | Persistenz ausgewählt | gültiges Z-Feedback |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for c,arms in v['Z'].items():
        for a,z in arms.items():
            lines.append('| '+c+' | '+a+' | '+' | '.join(str(z.get(k,0)) for k in ('Y_targets','Z_present','Z_cold','Z_warm','Z_candidate','Z_retained','Z_selected','P_selected','Z_valid_feedback'))+' |')
    lines+=['','Bestand, Berechtigung, Kalt/Warm-Belegung und Feedbackgelegenheiten sind',
        'ereignisweise innerhalb jedes U/L-Paars gleich. Die jeweiligen Fehlerwerte,',
        'Ausgaben und EP-Historien dürfen verschieden sein. Z wurde nicht ausgeblendet',
        'oder geschützt. [Alle Fall-Lebenszyklen](cycles.json) dokumentieren Originale,',
        'Promotionen, Verluste, Kandidatenersetzungen und Bestätigungen. Die vollständigen',
        'Feedback-/Zellketten beider Arme liegen im hashgeprüften Laufarchiv. Im L-Export',
        'verweist shared_stock_with_U auf den nachweislich gleichen U-Bestand; L-Zellwerte',
        'und Ausgaben sind separat gespeichert. Kein Beobachterverlauf wurde L zugeführt.','',
        '## Integrität und Ressourcen','',
        f"{v['archive_files_verified']} im Abschluss aufgeführte Dateien auf Länge und SHA256 geprüft.",
        '64 Fälle,128 Arme,66.560 Quellenframes,133.120 Produktionsaufnahmen und ebenso',
        'viele separat gezählte unabhängige Referenzfortschreibungen.33.216 gepaarte Ziele,',
        'davon16.384 Y-Ziele; vollständige Bereinigung, Ziel1041 je Armgeschichte zensiert.',
        'Alle Quellen vor erster Policy versiegelt. Keine technische Abweichung und kein',
        'Budgetabbruch; Worker beendet.','',
        '| Ressource | U | L |', '| --- | ---: | ---: |']
    labels={'additional_python_peak':'zusätzlicher Python-Peak (Byte)',
        'packed':'Bank (Byte)','boundary_originals':'Originale an Operationsgrenzen',
        'original_frames_upper_bound':'konservative Originalobergrenze',
        'combined_upper_bound':'konservative kombinierte Obergrenze',
        'boundary_valid_cells':'gültige Zellen, Maximum','output_slots_peak':'Ausgabeslots',
        'boundary_system_reachable_bytes':'gesamte erreichbare Systemobjekte an Operationsgrenzen (Byte)',
        'boundary_base_arm_bytes':'Basisarm an Operationsgrenzen (Byte)',
        'boundary_output_new_payloads':'neue Ausgabepayloads',
        'receipt_bytes_peak':'Receipt (Byte)','utf8_upper':'UTF-8-Obergrenze (Byte)'}
    for k,label in labels.items():lines.append(f"| {label} | {v['resources']['U'][k]} | {v['resources']['L'][k]} |")
    lines+=['','Gleiche tatsächliche Original-/Zellbelegung wurde pro Ereignis kontrolliert.',
        'Die übrige Python-Nutzung wird nicht als identisch behauptet oder künstlich',
        'angeglichen. Ganze Systemobjekte sind Grenzstellenzählungen, keine Messung des',
        'ganzen Prozesspeaks. Zusatzheap enthält Operationstransienten. Überlappende',
        'Kategorien nicht addieren; Frame-Tracing-Zähler0 sind keine Nullbelegung.',
        'Eingang und externe Beobachterdaten sind im Laufexport separat ausgewiesen.','',
        f"Worker: {v['worker']['engine_seconds']:.3f}s; Supervisor vor terminalem Schreiben: {v['supervisor_seconds']:.3f}s.",
        f"Vorbereitung: {v['charged_preparation_bytes']}Byte; Laufexport einschließlich Abschluss: {v['export_bytes']}Byte.",
        f"Maximaler Fall: {v['max_case_expanded']}Byte expandiert, {v['max_case_gzip']}Byte gzip.",
        'Alle gebundenen Grenzen eingehalten. Die zusätzliche Archivauswertung verändert',
        'keine versiegelte Laufdatei und enthält keinen weiteren Replay.','',
        f"Vorstart-SHA256: `{v['prestart_sha256']}`.",
        f"Autorisierungs-SHA256: `{v['authorization_sha256']}`.",
        f"Laufabschluss-SHA256: `{v['closure_sha256']}`.",
        '[Prüfbilanz](verification.json), [versiegelter Laufabschluss](../ulz1-comparison-20261004-01/closure.json).','',
        'Die operative Autorisierung bleibt als historischer Startbeleg unverändert.',
        'Vorhandener Zielordner, resume_permitted=false und Abschluss dokumentieren',
        'den Verbrauch. Keine Wiederholung aus erneuter Zustellung dieser Freigabe.','',
        '## Aussagegrenze','',
        'Untersucht wurde zeitliche Fehlerglättung in dieser synthetischen A/B/Z-Familie',
        'unter gemeinsamem regulären Speicherlebenszyklus und gleichen Budgets.',
        'Kein allgemeiner MCM-Mehrwert, Transfer oder feldinterne Memory nachgewiesen.',
        'Historische LZ1-/T1-/F-Urteile bleiben bestehen. Keine Übernahme von L und',
        'keine weitere Regeländerung durch diesen Lauf.']
    (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def main():
    closure=read(ARCHIVE/'closure.json')
    assert closure['status']=='COMPLETE' and not closure['worker_alive'] and not closure['neutral_only']
    for name,info in closure['files'].items():
        p=ARCHIVE/name
        assert p.stat().st_size==info['bytes'] and sha(p)==info['sha256']
    assessment=read(ARCHIVE/'assessment.json')
    assert assessment['Technik']=='AUSWERTBAR' and not assessment['neutral_only']
    primary=[x for x in assessment['contrasts'] if x['primary']]
    assert len(primary)==2 and {x['level'] for x in primary}=={.975}
    OUT.mkdir(exist_ok=False)
    plan=read(ROOT/'docs/S2UC_ULZ1_V1_20261004_PLAN.json')
    ys=set(plan['masks']['G_Y']);metrics=[];lifecycles=[]
    maxima={a:{} for a in ('U','L')};phases={a:{} for a in ('U','L')}
    zcounts={c:{a:Counter() for a in ('U','L')} for c in ('S','W')}
    counts=Counter();max_raw=max_packed=0
    with (OUT/'targets.csv').open('w',newline='',encoding='utf-8') as tf:
        columns=['case','replicate','condition','target','Y','U','L','delta','cumulative',
                 'U_selected_original','L_selected_original','hypotheses','warm',
                 'Z_present','Z_warm','Z_role','U_reason','L_reason']
        writer=csv.DictWriter(tf,fieldnames=columns);writer.writeheader()
        for spec in plan['cases']:
            name=spec['id'];src=read(ARCHIVE/(name+'-source.json'))
            p=ARCHIVE/(name+'-case.json.gz');data=gzip.decompress(p.read_bytes());r=json.loads(data)
            assert r['complete'] and r['reference_equal'] and r['lifecycle_equal'] and not r['neutral_only']
            assert len(r['rows'])==519 and all(r[a]['cleanup'] for a in ('U','L'))
            max_raw=max(max_raw,len(data));max_packed=max(max_packed,p.stat().st_size)
            for a in ('U','L'):
                assert r[a]['censored_target']==1041
                res=r['resources'][a]
                for k,v in res.items():
                    if isinstance(v,(int,float)):maxima[a][k]=max(maxima[a].get(k,0),v)
                for k,v in res['boundary_peaks'].items():maxima[a]['boundary_'+k]=max(maxima[a].get('boundary_'+k,0),v)
                for phase,vals in res['phase_peaks'].items():
                    dest=phases[a].setdefault(phase,{})
                    for k,v in vals.items():dest[k]=max(dest.get(k,0),v)
            for m,values in r['metrics'].items():metrics.append(dict(case=name,replicate=spec['replicate'],condition=spec['condition'],mask=m,**values))
            for rr,u,l in zip(r['rows'],r['U']['rows'],r['L']['rows'],strict=True):
                t=rr['target'];counts['paired_targets']+=1
                z=[h for h in u['hypotheses'] if src['ids'][h['original']-1]==4]
                assert len(z)<=1
                warm=sum(h['before'] is not None for h in u['hypotheses'])
                writer.writerow(dict(case=name,replicate=spec['replicate'],condition=spec['condition'],target=t,
                    Y=int(t in ys),U=rr['U'],L=rr['L'],delta=rr['U']-rr['L'],cumulative=rr['cumulative_difference'],
                    U_selected_original='' if u['selected'] is None else u['selected']['original'],
                    L_selected_original='' if l['selected'] is None else l['selected']['original'],
                    hypotheses=len(u['hypotheses']),warm=warm,Z_present=bool(z),Z_warm=bool(z and z[0]['before'] is not None),
                    Z_role='' if not z else z[0]['key'][0],U_reason=u['reason'],L_reason=l['reason']))
                if t in ys:
                    counts['paired_Y_targets']+=1
                    for arm,row in (('U',u),('L',l)):
                        count=zcounts[spec['condition']][arm]
                        count['Y_targets']+=1
                        count['three_hypotheses']+=len(row['hypotheses'])==3
                        count['Z_present']+=bool(z)
                        count['Z_warm']+=bool(z and z[0]['before'] is not None)
                        count['Z_cold']+=bool(z and z[0]['before'] is None)
                        count['Z_candidate']+=bool(z and z[0]['key'][0]==1)
                        count['Z_retained']+=bool(z and z[0]['key'][0]==0)
                        count['Z_selected']+=bool(row['selected'] and src['ids'][row['selected']['original']-1]==4)
                        count['P_selected']+=row['selected'] is None
                        count['Z_valid_feedback']+=sum(x['live'] for h,x in zip(row['hypotheses'],row['updates'],strict=True) if src['ids'][h['original']-1]==4)
            def trace_id(trace):return None if trace is None else src['ids'][trace['ordinals'][2]-1]
            events=[];counter=Counter()
            for e in r['U']['events']:
                before=e['before'];after=e['after']
                old={t['generation']:t for t in before['retained']};new={t['generation']:t for t in after['retained']}
                added=[new[k] for k in new.keys()-old.keys()]
                lost=[old[k] for k in old.keys()-new.keys()]
                bc=before['candidate'];ac=after['candidate']
                zp=any(trace_id(x)==4 for x in added)
                ze=any(trace_id(x)==4 for x in lost)
                zcreate=trace_id(ac)==4 and (bc is None or ac['generation']!=bc['generation'])
                zreplace=trace_id(bc)==4 and ac is not None and bc['generation']!=ac['generation']
                if added or lost or zcreate or zreplace:
                    events.append(dict(at=e['index'],promoted=added,evicted=lost,Z_promoted=zp,Z_evicted=ze,
                        Z_candidate_created=zcreate,Z_candidate_replaced=zreplace,
                        before_candidate=bc,after_candidate=ac,before_cells=e['cells']))
                counter['all_promotions']+=len(added);counter['all_evictions']+=len(lost)
                counter['Z_promotions']+=zp;counter['Z_evictions']+=ze
                counter['Z_candidate_creations']+=zcreate;counter['Z_candidate_replacements']+=zreplace
            lifecycles.append(dict(case=name,condition=spec['condition'],counts=dict(counter),events=events,
                confirmations=r['U']['full_confirmations']))
    with (OUT/'case-mask-means.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['case','replicate','condition','mask','U','L']);w.writeheader();w.writerows(metrics)
    for filename,rows in [('contrasts.csv',assessment['contrasts']),('harms.csv',assessment['harms'])]:
        with (OUT/filename).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    means={c:{m:{a:sum(x[a] for x in metrics if x['condition']==c and x['mask']==m)/32 for a in ('U','L')}
                    for m in plan['masks']} for c in ('S','W')}
    lifecycle_totals={c:dict(sum((Counter(x['counts']) for x in lifecycles if x['condition']==c),Counter())) for c in ('S','W')}
    save('cycles.json',lifecycles)
    save('verification.json',dict(status='PASS',archive_files_verified=len(closure['files']),
        closure_sha256=sha(ARCHIVE/'closure.json'),prestart_sha256=sha(ROOT/'docs/S2UC_ULZ1_V1_20261004_VORSTARTBINDUNG.json'),
        authorization_sha256=sha(ROOT/'docs/S2UC_ULZ1_V1_20261004_AUTORISIERUNG.json'),primary=primary,
        tradeoff=assessment['Abwaegung'],means=means,counts=dict(counts),resources=maxima,phase_peaks=phases,
        Z=zcounts,lifecycle_totals=lifecycle_totals,worker=read(ARCHIVE/'worker-complete.json'),
        charged_preparation_bytes=closure['charged_previous_bytes'],supervisor_seconds=closure['elapsed_before_terminal_write'],
        export_bytes=sum(x.stat().st_size for x in ARCHIVE.iterdir() if x.is_file()),
        max_case_expanded=max_raw,max_case_gzip=max_packed,additional_replays=0,
        analysis_script_sha256=sha(Path(__file__))))
    render(read(OUT/'verification.json'),assessment)
    print(json.dumps(dict(primary=primary,tradeoff=assessment['Abwaegung'],resources=maxima,lifecycle_totals=lifecycle_totals),indent=2))

if __name__=='__main__':main()
