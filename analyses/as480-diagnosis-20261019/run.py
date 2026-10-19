"""Archive-only AS480 diagnosis. Never imports material, engine, receptor or policy."""
import sys,os,time,math,json,hashlib,gzip,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from experiments.as480 import entry
from experiments.as480.common import read,raw,sha,info,size,need,exclusive,append,PREP,RESEARCH,EPS,TAU,LIMITS
OUT=ROOT/'reports/s2uc/as480-diagnosis-20261019-01'
CASES=('A0','A480','B0','B480')
ORDER='60d11630-4c59-4467-99c5-1d5fa8c1e3d0'
DELIVERY='a7c19ad4b944bf39a8f3f1bb224623389db3587c0672bdb787f97e3104a38448'
COUNTS=dict(pcm_created=0,receptor_calls=0,nj_calls=0,policy_calls=0,reference_replays=0,archive_cases=0,
    offset_distances=0,exact_factor_checks=0,channel_contributions=0,projection_files=0,artificial_fixtures=0)

def event(name,**kw):append(OUT/'execution.jsonl',dict(event=name,counts=COUNTS,**kw))
def save(name,value):
    payload=value if isinstance(value,bytes) else raw(value)
    need(len(payload)<=1048576 and size(OUT)+len(payload)<=1048576,'DIAGNOSTIC_EXPORT')
    need(size(PREP)+size(RESEARCH)+size(OUT)+len(payload)<=16777216,'TOTAL_EXPORT')
    exclusive(OUT/name,payload)
def amplitude(v):return math.fsum(abs(x) for x in v)/48
def exact(h,s):return [math.ldexp(1.,e) for e in (-1,0,1) if all(math.ldexp(s[j][k],e)==h[j][k] for j in range(2) for k in range(48))]
def distance(h,s):
    ha=[amplitude(v) for v in h];sa=[amplitude(v) for v in s]
    denom=max((ha[0]+ha[1])/2,(sa[0]+sa[1])/2)
    need(math.isfinite(denom) and denom>=sys.float_info.min,'DENOMINATOR')
    absdiff=[[abs(h[j][k]-s[j][k]) for k in range(48)] for j in range(2)]
    maes=[math.fsum(v)/48 for v in absdiff]
    d=math.fsum(x for v in absdiff for x in v)/96/denom
    need(math.isfinite(d),'NONFINITE_DISTANCE')
    return dict(hint_amplitudes=ha,stored_amplitudes=sa,denominator=denom,frame_mae=maes,
        frame_relative_l1=[maes[j]/max(ha[j],sa[j]) for j in range(2)],
        frame_pair_contribution=[x/2/denom for x in maes],pair_distance=d,
        signal_pass=min(ha+sa)>EPS,within_tau=d<=TAU,
        channel_contributions=[[x/96/denom for x in v] for v in absdiff])
def fixtures():
    v=lambda x:[float(x)]*48
    checks=[]
    def check(name,condition):need(condition,'FIXTURE:'+name);checks.append(name)
    check('identical',distance([v(1),v(1)],[v(1),v(1)])['pair_distance']==0)
    q=distance([v(1),v(1)],[v(1-TAU),v(1-TAU)])
    check('fixed_tau_boundary',q['pair_distance']==TAU and q['within_tau'])
    q=distance([v(1),v(1)],[v(math.nextafter(1-TAU,0)),v(math.nextafter(1-TAU,0))])
    check('above_fixed_tau',q['pair_distance']>TAU and not q['within_tau'])
    q=distance([v(1),v(2)],[v(.5),v(1)])
    check('two_frame_contributions',q['pair_distance']==.5 and q['frame_pair_contribution']==[1/6,1/3])
    check('channel_sum',math.isclose(math.fsum(x for row in q['channel_contributions'] for x in row),q['pair_distance'],rel_tol=1e-15))
    check('exact_factors',exact([v(1),v(2)],[v(.5),v(1)])==[2.] and exact([v(1),v(2)],[v(1),v(2)])==[1.])
    check('signal_equality_rejected',not distance([v(EPS),v(EPS)],[v(EPS),v(EPS)])['signal_pass'])
    check('signal_above_accepted',distance([v(math.nextafter(EPS,1)),v(math.nextafter(EPS,1))],[v(math.nextafter(EPS,1)),v(math.nextafter(EPS,1))])['signal_pass'])
    COUNTS['artificial_fixtures']=len(checks);save('fixtures.json',dict(passed=True,tests=checks,thresholds=dict(tau=TAU,epsilon=EPS)))

def archive_verify():
    need(sha(RESEARCH/'delivery-binding.json')==DELIVERY,'DELIVERY_BINDING')
    old=read(RESEARCH/'delivery-binding.json')
    for name,value in old['files'].items():need(info(RESEARCH/name)==value,'ARCHIVE_HASH:'+name)
    return old

def projection(case,i,values):
    p=RESEARCH/f'material/{case}-{i:02}.json';d=read(p);v=d['projection']
    need(v['values']==values,'ARCHIVED_VECTOR_LINK')
    # Raw vectors were not separately stored: recover the inverse of exact half scaling,
    # then prove against the original raw-values digest. No NJ function is called.
    restored=[math.ldexp(x,1) for x in values]
    encoded=json.dumps(restored,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
    need(hashlib.sha256(encoded).hexdigest()==v['source_values_digest'],'RAW_INVERSE_DIGEST')
    COUNTS['projection_files']+=1
    return dict(path=p.relative_to(ROOT).as_posix(),info=info(p),source_interval=d['source_interval'],
        carriers=v['carrier_ids'],values=values,raw_recovered=restored,raw_digest_verified=True)

def worker():
    entry.win.worker_membership()
    until=time.monotonic()+10
    while not (OUT/'gate.json').exists():need(time.monotonic()<until,'GATE_TIMEOUT');time.sleep(.02)
    need(read(OUT/'gate.json')['pid']==os.getpid(),'GATE_PID')
    event('WORKER_BEGIN');fixtures();old=archive_verify();rows={};channels={};links={}
    for c in CASES:
        event('CASE_BEGIN',case=c)
        rec=read(RESEARCH/f'{c}-N.json')['records'][-1];e=read(RESEARCH/f'{c}-E.json')['records'][-1]
        need(rec['target']==11 and len(rec['stock'])==1 and rec['stock']==e['stock'] and rec['hint']==e['hint'],'MAIN_RECORD')
        need(rec['receipt']['retrieval']['tau']==TAU and rec['receipt']['retrieval']['epsilon']==EPS,'FIXED_THRESHOLDS')
        stock=rec['stock'][0];need(stock['ordinals']==[1,2,3,4] and stock['role']=='retained' and stock['generation']==1,'STOCK')
        h=rec['hint'];s=stock['values'];hp=[projection(c,j+9,h[j]) for j in range(2)];sp=[projection(c,j+1,s[j]) for j in range(4)]
        links[c]=dict(hints=hp,stored=sp)
        offsets=[]
        for o in range(3):
            r=distance(h,s[o:o+2]);f=exact(h,s[o:o+2]);COUNTS['offset_distances']+=1;COUNTS['exact_factor_checks']+=3
            offsets.append(dict(offset=o,stored_originals=[o+1,o+2],exact_factors=f,successor_original=o+3 if o<2 else None,
                **{k:v for k,v in r.items() if k!='channel_contributions'}))
            if o==0:
                cells=[]
                for j in range(2):
                    for k in range(48):
                        cells.append(dict(frame=j,channel_index=k,carrier=hp[j]['carriers'][k],hint_nj=h[j][k],stored_nj=s[j][k],
                            signed_nj_change=h[j][k]-s[j][k],absolute_nj_change=abs(h[j][k]-s[j][k]),
                            hint_raw=hp[j]['raw_recovered'][k],stored_raw=sp[j]['raw_recovered'][k],
                            contribution=r['channel_contributions'][j][k]))
                        COUNTS['channel_contributions']+=1
                total=math.fsum(x['contribution'] for x in cells)
                need(math.isclose(total,r['pair_distance'],rel_tol=1e-14,abs_tol=1e-17),'CONTRIBUTION_SUM')
                grouped=[dict(channel_index=k,carrier=hp[0]['carriers'][k],contribution=math.fsum(x['contribution'] for x in cells if x['channel_index']==k)) for k in range(48)]
                channels[c]=dict(cells=cells,grouped=grouped,contribution_sum=total,pair_distance=r['pair_distance'],rounding_residual=total-r['pair_distance'])
        exact_offsets=[o['offset'] for o in offsets if o['exact_factors']]
        accepted=[o['offset'] for o in offsets if o['signal_pass'] and o['within_tau']]
        need(len(exact_offsets)==rec['receipt']['retrieval']['exact_match_count'],'ARCHIVED_EXACT_COUNT')
        if c=='A0':need(exact_offsets==[0] and rec['receipt']['status']=='CONFIRMED_RETAINED_MATCH','A0_EXACT')
        else:need(not exact_offsets and not accepted and rec['receipt']['status']=='ABSTAIN_NO_APPROX_CONTEXT','REJECTION_RECONSTRUCTION')
        rows[c]=dict(archived_E_status=e['receipt']['status'],archived_N_status=rec['receipt']['status'],
            archived_continuation=rec['forecast']['status'],hint_signal_pass=min(amplitude(v) for v in h)>EPS,
            exact_offsets=exact_offsets,approximation_executed_in_original_run=not bool(exact_offsets),
            approximate_offsets_under_fixed_tau=accepted,ambiguous=False,offsets=offsets)
        COUNTS['archive_cases']+=1;event('CASE_COMPLETE',case=c)
    save('distances.json',dict(tau=TAU,epsilon=EPS,cases=rows,
        definitions='pair_distance=(sum96 absolute deltas/96)/max(mean hint amplitudes,mean stored amplitudes). frame_relative_l1 has its own frame denominator and is diagnostic only; frame_pair_contribution sums to pair_distance.'))
    save('channel-contributions.json',channels);save('archive-value-links.json',links)
    # All report values below are derived from the fixed four archive records only.
    a=rows['A480'];d=a['offsets'][0]['pair_distance']
    lines=['# AS480 – archivbasierte Diagnose','',f'Auftrag {ORDER}. 2026-10-19.','',
        f'**A480 scheitert an der festen Distanzschranke:** Offset0 hat relative Paar-L1={d:.17g}, größer als τ={TAU}. Alle drei Offsets liegen über τ. Signalzulassung besteht; kein Exaktmatch. Mehrdeutigkeit und fehlender Nachfolger sind nicht der Auslöser.',
        '', '## Ablehnungskette und Gegenfälle','',
        f'ε={EPS:.17g}; τ={TAU:.17g}. Beide Werte unverändert. Signalbedingung: jeder der zwei Hinweise und jeweils beide gespeicherten Frames haben mittlere Absolutaktivität strikt über ε. Exaktprüfung testet die vorhandenen Faktoren0,5/1/2 ohne Toleranz.',
        '', '| Fall | Offset | Hinweisamplituden | Speicheramplituden | L1 Frame0 / Frame1 | Paar-L1 | ≤τ | Exaktfaktoren | Nachfolger |',
        '|---|---:|---|---|---|---:|---|---|---|']
    for c in CASES:
        for r in rows[c]['offsets']:
            fmt=lambda xs:' / '.join(f'{x:.12g}' for x in xs)
            lines.append(f'| {c} | {r["offset"]} | {fmt(r["hint_amplitudes"])} | {fmt(r["stored_amplitudes"])} | {fmt(r["frame_relative_l1"])} | {r["pair_distance"]:.12g} | {r["within_tau"]} | {r["exact_factors"]} | {r["successor_original"]} |')
    lines+=['', 'Die Frame-L1-Werte sind separat normierte Diagnosegrößen. Die produktive Schranke gilt ausschließlich für Paar-L1; keine zusätzliche Frame-Schwelle. Nenner, unnormierte Frame-MAE und additive Framebeiträge sind vollständig in distances.json enthalten.',
        'A0 verwendet Exaktpriorität; seine hier daneben berechneten Näherungsdistanzen wurden im ursprünglichen Abruf nicht benötigt. A480/B0/B480 haben null zulässige Näherungsoffsets; daher keine Mehrdeutigkeit und ABSTAIN_NO_APPROX_CONTEXT.',
        'Offset0 hätte Original3 als Nachfolger, Offset1 Original4; Offset2 hat keinen Nachfolger. Da A480 schon die Distanzprüfung verfehlt, erklärt die Nachfolgerprüfung seine Enthaltung nicht.',
        '', '## Offset0 nach Kanälen','',
        'Jeder Beitrag ist |Hinweis−Original|/(96×Paarnenner). Aufgeführt sind die acht größten Kanalbeiträge über beide Hinweise; die vollständigen96 Beiträge pro Fall liegen in channel-contributions.json. Kanalindizes sind nullbasiert.',
        '', '| Fall | Kanal | Träger | Beitrag | Anteil am Paarabstand |','|---|---:|---|---:|---:|']
    for c in CASES:
        q=channels[c];top=sorted(q['grouped'],key=lambda x:x['contribution'],reverse=True)[:8]
        for x in top:
            share=x['contribution']/q['pair_distance'] if q['pair_distance'] else 0
            lines.append(f'| {c} | {x["channel_index"]} | {x["carrier"]} | {x["contribution"]:.12g} | {share:.6%} |')
    lines+=['', 'Für A480 tragen insbesondere folgende Änderungen bei (größte einzelne Frame/Kanal-Beiträge):','',
        '| Hinweis | Kanal | NJ Original → Hinweis | Rohwert Original → Hinweis | Beitrag |','|---:|---:|---|---|---:|']
    for x in sorted(channels['A480']['cells'],key=lambda x:x['contribution'],reverse=True)[:10]:
        lines.append(f'| {x["frame"]} | {x["channel_index"]} | {x["stored_nj"]:.12g} → {x["hint_nj"]:.12g} | {x["stored_raw"]:.12g} → {x["hint_raw"]:.12g} | {x["contribution"]:.12g} |')
    lines+=['', 'Die Rohrezeptorvektoren waren nicht separat gespeichert. Sie wurden ausschließlich durch inverse Zweierskalierung aus den archivierten NJ-Werten rekonstruiert; jeder rekonstruierte Vektor stimmt mit dem archivierten source_values_digest überein. Keine Rezeptor- oder NJ-Funktion wurde ausgeführt.',
        'Die NJ-Halbierung verändert die hier betrachtete relative L1 nicht: Zähler und Nenner skalieren gleich. Die festgestellten Kanalverschiebungen stammen bereits aus den gebundenen Rezeptorwerten; daraus folgt keine isolierte physikalische Ursachenbestimmung.',
        '', '## Fensterzusammensetzung und Aussagegrenze','',
        'A480-Hinweis0 umfasst4320 Samples aus Abschnitt0 (380Hz plus1,5-fache Komponente) und480 Samples aus Abschnitt1 (740Hz); Hinweis1 entsprechend4320 Samples aus Abschnitt1 und480 aus Abschnitt2 (1260Hz). A0 umfasst jeweils einen vollständigen4800-Sample-Abschnitt. B verwendet die festgelegten400/760/2140/2380Hz mit denselben Schnittregeln.',
        'Nach unverändertem Rezeptorcode werden4800 Samples mit symmetrischem Hann gewichtet, FFT-Beträge gebildet und48 überlappende logarithmische Bänder quadratisch reduziert. Verschobener Abschnittsinhalt, Phase und Fenstergewichtung wirken gemeinsam. Die Archivdiagnose isoliert diese Einflüsse nicht; die10%-Beimischung ist keine10%-Energieaussage.',
        'Der bestehende Abruf verlangt komponentennahe Zwei-Frame-Verläufe. Er besitzt in dieser Gegenprobe keine ausreichende Invarianz gegen den festgelegten480-Sample-Fensterversatz. Das Vierfallurteil NO_ADDITIONAL_BENEFIT bleibt unverändert. Keine alternative Schwelle berechnet oder empfohlen.',
        '', '## Durchführung und Anschluss','',
        'Acht kleine künstliche Fixtures prüfen ausschließlich die neue Diagnoserechnung. Ausgewertet wurden vier archivierte Hauptentscheidungen, zwölf Offsetdistanzen,36 Exaktfaktorprüfungen und384 Kanalbeiträge. Archivierte Status-/Exaktzähler werden wiederverwendet; nicht gespeicherte Distanzen werden als neue Archivberechnungen ausgewiesen.',
        'Null neue PCM-Daten, Rezeptor-/NJ-Aufrufe, Policy-Läufe oder Referenzwiederholungen. Historische Artefakte bleiben unverändert; die drei Übersichtsvorgänger werden verlustfrei komprimiert gesichert. Diese Diagnose hat ihre eigene Ressourcenbilanz und gehört nicht zur früheren300-Sekunden-Laufzeit.',
        'Vorschlag: den unveränderten AS480-Zweig abschließen und fachlich entscheiden, ob zeitliche Ausrichtung vor dem Abruf als eigener konzeptioneller Ansatz sinnvoll ist. Zunächst einen falsifizierbaren Vertrag für Eigen-/Fremdverlaufstrennung formulieren; keine automatische Implementierung, Kalibration oder neue Messung.']
    save('REPORT.md',('\n'.join(lines)+'\n').encode())
    previous=read(RESEARCH/'preservation.json');mapping={}
    paragraph=f'''## Aktuell: AS480-Archivdiagnose abgeschlossen (2026-10-19)

A480 besteht das Signalgate, hat keinen Exaktmatch und überschreitet mit
Paar-L1={d:.12g} am vorgesehenen Offset0 die unveränderte Schwelle τ=0,03125.
Auch Offset1/2 sind ausgeschlossen. Keine Mehrdeutigkeit; Offset0 hätte einen
Nachfolger. Alle vier Fälle und sämtliche Kanalbeiträge sind archivbasiert
gegenübergestellt. Acht künstliche Diagnosefixtures bestanden; keine neuen
PCM-/Rezeptor-/NJ-/Policy-/Referenzläufe. NO_ADDITIONAL_BENEFIT bleibt bestehen.
Nächste fachliche Entscheidung: AS480 abschließen und gegebenenfalls zeitliche
Ausrichtung als getrennten konzeptionellen Ansatz prüfen, ohne Schwellenoptimierung.
Einmalberechtigung verbraucht; U unverändert. Ältere Abschnitte sind historisch.

[Diagnosebericht](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/as480-diagnosis-20261019-01/REPORT.md).

'''
    for name in ('README.md','AKTUELLER_FORSCHUNGSWEG.md','docs/README.md'):
        p=ROOT/name;need(info(p)==previous['overviews'][name]['current'],'OVERVIEW_CHANGED')
        oldbytes=p.read_bytes();compressed=gzip.compress(oldbytes,mtime=0);need(gzip.decompress(compressed)==oldbytes,'SNAPSHOT')
        save('historical-overviews/'+name+'.gz',compressed)
        split=oldbytes.find(b'\n')+1;p.write_bytes(oldbytes[:split]+b'\n'+paragraph.encode()+oldbytes[split:])
        mapping[name]=dict(previous=previous['overviews'][name]['current'],current=info(p),snapshot='historical-overviews/'+name+'.gz')
    save('preservation.json',dict(overviews=mapping))
    archive_verify();event('WORKER_COMPLETE')
    save('worker-result.json',dict(status='COMPLETE',counts=COUNTS,archive_unchanged=True,overview_updates=mapping))

def main():
    if '--worker' in sys.argv:
        try:worker();return 0
        except BaseException as ex:
            event('WORKER_FAILED',error=repr(ex));save('worker-error.json',dict(error=repr(ex),counts=COUNTS));raise
    start=time.monotonic();need(not OUT.exists(),'EXCLUSIVE_TARGET');OUT.mkdir(parents=True);event('START')
    child=None;error=None;installed=False
    try:
        entry.install();installed=True
        b,h=entry.binding();archive_verify()
        save('input-binding.json',dict(workflow=ORDER,research_delivery_sha256=DELIVERY,technical_binding_sha256=h,
            script=info(Path(__file__)),runtime=b['runtime'],limits=LIMITS,thresholds=dict(tau=TAU,epsilon=EPS),
            permitted='archive arithmetic and artificial fixtures only',forbidden_calls=COUNTS))
        with (OUT/'worker.log').open('xb') as log:
            child=subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'--worker'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            wstart=time.monotonic();entry.win.verify_worker(int(child._handle));save('gate.json',dict(pid=child.pid))
            while child.poll() is None:
                need(time.monotonic()-start<300 and time.monotonic()-wstart<240,'TIME_LIMIT')
                time.sleep(.05)
            need(child.returncode==0,'WORKER_EXIT')
        need(read(OUT/'worker-result.json')['status']=='COMPLETE','WORKER_RESULT')
        need(sha(Path(__file__))==read(OUT/'input-binding.json')['script']['sha256'],'SCRIPT_CHANGED')
    except BaseException as ex:error=repr(ex)
    finally:
        if child is not None and child.poll() is None:child.kill();child.wait(timeout=5)
        counters=read(OUT/'worker-result.json')['counts'] if (OUT/'worker-result.json').exists() else json.loads((OUT/'execution.jsonl').read_bytes().splitlines()[-1])['counts']
        save('execution-balance.json',dict(status='TECHNICAL_ERROR' if error else 'COMPLETE',error=error,counts=counters,
            attempts=1,scientific_repeats=0,worker_exitcode=child.returncode if child else None,cleanup=child is None or child.poll() is not None))
        save('resources.json',dict(seconds=time.monotonic()-start,job=entry.job() if installed else None,
            worker_limit_seconds=240,total_limit_seconds=300,diagnostic_bytes_before_binding=size(OUT),
            previous_export_bytes=size(PREP)+size(RESEARCH),combined_before_binding=size(PREP)+size(RESEARCH)+size(OUT),
            final_binding_reserve=65536,diagnostic_limit=1048576,combined_limit=16777216,separate_from_research_runtime=True))
        closure=dict(workflow=ORDER,status='TECHNICAL_ERROR' if error else 'COMPLETE',
            files={p.relative_to(OUT).as_posix():info(p) for p in OUT.rglob('*') if p.is_file()},
            external={str(p):info(p) for p in [Path(__file__),RESEARCH/'delivery-binding.json']+[ROOT/n for n in ('README.md','AKTUELLER_FORSCHUNGSWEG.md','docs/README.md')]})
        save('delivery-binding.json',closure);save('delivery-binding.sha256',(sha(OUT/'delivery-binding.json')+'\n').encode())
        print(json.dumps(dict(status=closure['status'],error=error,counts=counters,sha256=sha(OUT/'delivery-binding.json'),seconds=time.monotonic()-start,total_export=size(PREP)+size(RESEARCH)+size(OUT))))
    return 1 if error else 0

if __name__=='__main__':raise SystemExit(main())
