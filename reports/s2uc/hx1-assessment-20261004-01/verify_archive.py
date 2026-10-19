"""Read sealed HX1 output only. Never materialize sources or execute policies."""
import gzip
import hashlib
import json
import struct
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
from math import lcm

ROOT=Path(__file__).resolve().parents[3]
RUN=ROOT/'reports/s2uc/hx1-comparison-20261004-01'
OUT=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,v):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def dec(x):return f'{float(F(x)):.12f}'
def pick(rows,mask):return [r for r in rows if mask=='G_all' or mask=='S' and r['target']%4==1 or mask=='Q' and r['target']%4==3 or mask.startswith('Q_') and r.get('cue')==mask[-1]]
def maximum(dst,src):
    for k,v in src.items():
        if isinstance(v,dict):maximum(dst.setdefault(k,{}),v)
        elif isinstance(v,(int,float)):dst[k]=max(dst.get(k,0),v)

closure=read(RUN/'closure.json')
pre_path=ROOT/'docs/S2UC_HX1_V1_20261004_VORSTARTBINDUNG.json'
supplement=ROOT/'docs/S2UC_HX1_SPEICHERGRENZE_ERGAENZUNGSBINDUNG_20261004.json'
auth=ROOT/'docs/S2UC_HX1_V1_20261004_AUTORISIERUNG.json'
assert sha(pre_path)=='e8cb8f935d28a5624239aafdbab75d0cb8246b665045442afcc9ec4a8931d36e'
assert sha(supplement)=='b134eb66d8c633debc46901be0ea7ea0c518dd18f004cdb52491e9b6362af580'
assert read(auth)==read(ROOT/'docs/S2UC_HX1_V1_20261004_AUTORISIERUNG_VORLAGE.json')|dict(status='AUTHORIZED_ONCE')
for name,digest in read(ROOT/'docs/S2UC_HX1_V1_20261004_CODEBINDUNG.json')['files'].items():assert sha(ROOT/name)==digest
for name,entry in read(supplement)['files'].items():assert sha(ROOT/name)==entry['sha256']
assert closure['status']=='COMPLETE' and not closure['worker_alive'] and closure['worker_exitcode']==0
assert not closure['neutral_only'] and not closure['resume_permitted']
assert {p.name for p in RUN.iterdir() if p.is_file()}==set(closure['files'])|{'closure.json'}
for name,entry in closure['files'].items():
    p=RUN/name;assert sha(p)==entry['sha256'] and p.stat().st_size==entry['bytes'],name
assessment=read(RUN/'assessment.json');done=read(RUN/'worker-complete.json')
assert (done['cases'],done['arms'],done['arm_frames'],done['reference_advances'])==(64,192,196608,196608)
assert assessment['reference_equal'] and not assessment['neutral_only']
manifest=read(RUN/'manifest.json');assert manifest['all_sources_before_policy'] and len(manifest['entries'])==64
rows={};means={};cross=[];maxima={a:{} for a in 'UGP'};previous=None;g_positions=0
expanded_max=packed_max=source_max=0;classes=Counter();diagnosis=[];g_checks=[]
for entry in manifest['entries']:
    name=entry['id'];rep=int(name.split('-')[1]);condition=name[-1]
    sp=RUN/entry['file'];assert sha(sp)==entry['sha256'];s=read(sp)
    assert not s['neutral_only'] and len(s['ids'])==1024
    source_max=max(source_max,sp.stat().st_size)
    ids=s['ids'];table=Counter((ids[i],ids[i+2]) for i in range(0,1024,4))
    assert Counter(ids[0::4])=={0:128,1:128} and Counter(ids[2::4])=={3:128,4:128}
    assert all(ids[i]==2 and ids[i+2]==5 for i in range(1,1024,4))
    counts=[table[h,y] for h,y in ((0,3),(0,4),(1,3),(1,4))]
    if condition=='D':assert counts==([96,32,32,96] if rep%2 else [32,96,96,32])
    cross.append(dict(replicate=rep,condition=condition,counts=counts,draws=s['draws']))
    p=RUN/(name+'-case.json.gz');data=gzip.decompress(p.read_bytes());v=json.loads(data)
    expanded_max=max(expanded_max,len(data));packed_max=max(packed_max,p.stat().st_size)
    assert v['complete'] and v['cleanup'] and not v['neutral_only'] and v['censored_target']==1025
    assert v['U']['reference_equal'] and v['U']['cleanup'] and v['reference_advances']==dict(U=1024,G=1024,P=1024)
    assert [r['target'] for r in v['rows']]==list(range(3,1024,2))
    assert [r['target'] for r in v['G_Q']]==list(range(3,1024,4))
    for b,q in enumerate(v['G_Q']):
        pre=bytes.fromhex(q['pre']);post=bytes.fromhex(q['post'])
        assert len(pre)==len(post)==400
        assert struct.unpack_from('<Q',pre,384)[0]==b and struct.unpack_from('<Q',post,384)[0]==b+1
        expected=pre[:384] if b else struct.pack('<48d',*s['catalog'][2])
        assert bytes.fromhex(q['output'])==expected
    if condition=='D':previous=(ids[2::4],v['G_Q'])
    else:
        assert ids[2::4]==previous[0] and v['G_Q']==previous[1]
        g_positions+=256;g_checks.append(dict(replicate=rep,positions=256,pre_output_error_post_bit_equal=True))
    rs=v['rows'];rows[rep,condition]=rs
    cumulative={k:F(0) for k in ('U/G','U/P','G/P')}
    for r in rs:
        for key in cumulative:
            cumulative[key]+=F(r[key[0]])-F(r[key[2]])
            assert F(r['cumulative'][key])==cumulative[key]
        if r['target']%4==3:
            assert r['P']==.25 and r['class'] in ('V0','V1','V2','V3')
            classes[condition+':'+r['class']]+=1
        else:assert r['U']==r['G']==r['P'] and 'class' not in r
    for mask in ('Q','G_all','S','Q_X','Q_Y'):
        selected=pick(rs,mask);assert len(selected)=={'Q':256,'G_all':511,'S':255,'Q_X':128,'Q_Y':128}[mask]
        for a in 'UGP':means[rep,condition,mask,a]=sum((F(r[a]) for r in selected),F(0))/len(selected)
    for a in 'UGP':maximum(maxima[a],v['resources'][a])

for d in assessment['diagnosis']:
    rs=[r for r in rows[d['replicate'],d['condition']] if r.get('class')==d['classification']]
    delta=[F(r[d['comparison'][-1]])-F(r['U']) for r in rs]
    assert len(rs)==d['count'] and sum((max(x,0) for x in delta),F(0))==F(d['gain']) and sum((max(-x,0) for x in delta),F(0))==F(d['harm'])
for c in ('D','N'):
    assert sum(classes[c+':'+v] for v in ('V0','V1','V2','V3'))==8192
    for cls in ('V0','V1','V2','V3'):
        for comp in ('U/G','U/P'):
            ds=[d for d in assessment['diagnosis'] if d['condition']==c and d['classification']==cls and d['comparison']==comp]
            gain=sum((F(d['gain']) for d in ds),F(0));harm=sum((F(d['harm']) for d in ds),F(0))
            diagnosis.append(dict(condition=c,classification=cls,comparison=comp,count=sum(d['count'] for d in ds),gain=str(gain),harm=str(harm),net=str(gain-harm)))

for d in assessment['secondary']:
    reps=list(range(1,33)) if d['orientation'] is None else list(range(d['orientation']+1,33,2))
    a,b=d['comparison'].split('/');c=d['condition'];mask=d['mask']
    selected=[(rep,r) for rep in reps for r in pick(rows[rep,c],mask)]
    delta=[F(r[a])-F(r[b]) for _,r in selected]
    gain=sum((max(-x,0) for x in delta),F(0));harm=sum((max(x,0) for x in delta),F(0));mh=max([F(0)]+delta)
    assert (len(delta),sum(x<0 for x in delta),sum(x>0 for x in delta),sum(x==0 for x in delta))==(d['count'],d['improved'],d['worse'],d['equal'])
    assert (gain,harm,mh)==(F(d['gain']),F(d['harm']),F(d['max_harm']))
    assert [[rep,r['target']] for rep,r in selected if mh>0 and F(r[a])-F(r[b])==mh]==d['maximum_harm_targets']
    vals=[means[rep,c,mask,a]-means[rep,c,mask,b] for rep in reps]
    assert vals==list(map(F,d['pairs'])) and max(vals)==F(d['worst_mean'])
    for arm in 'UGP':assert sum((means[rep,c,mask,arm] for rep in reps),F(0))/len(reps)==F(d['means'][arm])
    if mask=='Q' and d['orientation'] is None and a=='U':
        ds=[x for x in diagnosis if x['condition']==c and x['comparison']==d['comparison']]
        assert sum((F(x['gain']) for x in ds),F(0))==gain and sum((F(x['harm']) for x in ds),F(0))==harm

pv=[[],[],[]]
for rep in range(1,33):
    du=means[rep,'D','Q','U'];dg=means[rep,'D','Q','G'];nu=means[rep,'N','Q','U'];ng=means[rep,'N','Q','G']
    assert dg==ng
    pv[0].append(du-dg);pv[1].append(du-F(1,4));pv[2].append(du-nu)
# Independent archive-only implementation of specified stratified bootstrap.
draws=[]
for z in range(10000):
    draw=[]
    for o in range(2):
        for k in range(16):
            key=f'MCM-HX1/bootstrap/v1/z={z}/orientation={o}/k={k}'
            draw.append(2*(int.from_bytes(hashlib.sha256(key.encode()).digest()[:8],'big')%16)+o)
    draws.append(draw)
assert hashlib.sha256(bytes(i for d in draws for i in d)).hexdigest()==assessment['bootstrap_sha256']
for values,d in zip(pv,assessment['primary'],strict=True):
    assert values==list(map(F,d['pairs'])) and sum(values,F(0))/32==F(d['mean'])
    den=lcm(*(v.denominator for v in values));nums=[int(v*den) for v in values]
    bs=sorted(sum(nums[i] for i in draw) for draw in draws);ci=[]
    for numerator in (1,119):
        q,r=divmod(9999*numerator,120)
        ci.append(F(bs[q]*(120-r)+bs[min(q+1,9999)]*r,120*32*den))
    assert ci==list(map(F,d['ci']))
    assert d['verdict']==('BELEGT' if ci[1]<0 else 'WIDERLEGT' if ci[0]>0 else 'NICHT_NACHGEWIESEN')

assert g_positions==8192 and len(assessment['secondary'])==90 and len(assessment['diagnosis'])==512
assert maxima['U']['additional_python_peak']<=16384 and maxima['G']['own_heap_peak']<=8192 and maxima['P']['own_heap_peak']<=4096
assert closure['process_memory']['peak_job_committed_bytes']<=536870912
assert source_max<=32768 and packed_max<=524288 and expanded_max<=4194304
export=sum(p.stat().st_size for p in RUN.iterdir());assert export+closure['charged_previous_bytes']<=67108864
source_total=sum(p.stat().st_size for p in RUN.glob('*-source.json'))
case_total=sum(p.stat().st_size for p in RUN.glob('*-case.json.gz'))
admin_total=export-source_total-case_total-(RUN/'closure.json').stat().st_size
assert source_total<=2*1048576 and case_total<=32*1048576 and admin_total<=2*1048576
assert (RUN/'closure.json').stat().st_size<=1048576 and closure['total_deadline_met']
facts=dict(status='PASS_ARCHIVE_VERIFICATION',closure_sha256=sha(RUN/'closure.json'),authorization_consumed=True,
    prestart_sha256=sha(pre_path),supplement_sha256=sha(supplement),authorization_sha256=sha(auth),production_files_verified=139,
    files_verified=len(closure['files']),counts=done,G_DN_positions=g_positions,G_pair_checks=g_checks,
    primary=assessment['primary'],verdict=assessment['verdict'],classes=dict(classes),diagnosis=diagnosis,
    source_cross_tables=cross,maxima=maxima,source_file_max=source_max,case_compressed_max=packed_max,case_expanded_max=expanded_max,
    process_memory=closure['process_memory'],supervisor_seconds=closure['elapsed_before_terminal_write'],export_bytes=export,
    preparation_bytes=closure['charged_previous_bytes'],export_plus_preparation_bytes=export+closure['charged_previous_bytes'],
    source_total_bytes=source_total,case_total_bytes=case_total,admin_total_bytes=admin_total,terminal_bytes=(RUN/'closure.json').stat().st_size,
    secondary_records_verified=90,diagnosis_records_verified=512,primary_bootstrap_independently_verified=True,
    policy_replays_in_this_verification=0,source_materializations_in_this_verification=0)
save('verification.json',facts)
lines=['# HX1: Ergebnis des einmaligen Forschungsdurchlaufs','',f"Gesamturteil: **{assessment['verdict']}**. Technischer Abschluss COMPLETE; Archivprüfung PASS.",
    '', '64 Quellen, 32 D/N-Paare, 192 Prädiktorgeschichten; U unverändert, A1/K1 deaktiviert. Einmalfreigabe verbraucht; keine Wiederaufnahme oder Wiederholung.',
    '', '## Drei primäre Kontraste','', 'Negative Werte sprechen für die vorgegebene Erwartung. Nominale 98⅓%-Intervalle aus 10.000 nach Orientierung geschichteten Paarbootstrap-Ziehungen; Bonferroni für drei Kontraste. Anzeigen gerundet, Urteile aus exakten rationalen Werten.',
    '', '| Kontrast | Mittel | Untergrenze | Obergrenze | Urteil |','| --- | ---: | ---: | ---: | --- |']
for d in assessment['primary']:lines.append(f"| {d['name']} | {dec(d['mean'])} | {dec(d['ci'][0])} | {dec(d['ci'][1])} | {d['verdict']} |")
lines+=['','## V0–V3: vollständige Q-Bilanzen','', 'V0 keine berechtigte Spur; V1 nur kalte Zellen; V2 warme Zellen und Persistenz; V3 warme Zellen und Kontextausgabe. Gewinn/Schaden sind Summen von MAE-Differenzen, Netto = Gewinn − Schaden. Keine bestätigende Untergruppenentscheidung.',
    '', '| Bedingung | Klasse | Vergleich | Ziele | Gewinn | Schaden | Netto |','| --- | --- | --- | ---: | ---: | ---: | ---: |']
for d in diagnosis:lines.append('| '+' | '.join([d['condition'],d['classification'],d['comparison'],str(d['count']),dec(d['gain']),dec(d['harm']),dec(d['net'])])+' |')
lines+=['','## Vollständige sekundäre Bilanz','', 'Orientierung alle/0/1; explorative 95%-Intervalle ohne zusätzliche Erfolgsregel. Masken überlappen und dürfen nicht addiert werden. Alle Maximalschadenspositionen und exakten Geschichtenwerte stehen unverändert in assessment.json. Schlechtester Mittelwert bezeichnet die größte Fehlerdifferenz einer Geschichte.',
    '', '| C | Maske | Vergleich | o | n | U-MAE | G-MAE | P-MAE | besser/schlechter/gleich | Gewinn | Schaden | Netto | Max. Schaden | Schlechtester Mittelwert | 95%-Intervall |',
    '| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |']
for d in assessment['secondary']:
    fields=[d['condition'],d['mask'],d['comparison'],'alle' if d['orientation'] is None else str(d['orientation']),str(d['count'])]
    fields += [dec(d['means'][a]) for a in 'UGP']
    fields += [f"{d['improved']}/{d['worse']}/{d['equal']}",dec(d['gain']),dec(d['harm']),dec(F(d['gain'])-F(d['harm'])),dec(d['max_harm']),dec(d['worst_mean']),f"[{dec(d['ci'][0])}; {dec(d['ci'][1])}]"]
    lines.append('| '+' | '.join(fields)+' |')
lines+=['','## Alle 32 Paarwerte','', '| r | D:U−G | D:U−P | Interaktion |','| ---: | ---: | ---: | ---: |']
for i in range(32):lines.append(f'| {i+1} | '+' | '.join(dec(v[i]) for v in pv)+' |')
lines+=['','## Quellenkreuztabellen','', 'Alle Marginalen 128/128, D/N-Fortsetzungsfolgen positionsgleich. N unverändert übernommen, keine Auswahl nach Kreuztabelle.',
    '', '| r | C | XA | XB | YA | YB |','| ---: | --- | ---: | ---: | ---: | ---: |']
for d in cross:lines.append('| '+' | '.join(map(str,[d['replicate'],d['condition'],*d['counts']]))+' |')
lines+=['','## Ressourcen und Prüfdeckung','',f"- Worker {done['engine_seconds']:.6f} s; Supervisor {closure['elapsed_before_terminal_write']:.6f} s, Gesamtgrenze 3.600 s; Workergrenze 3.540 s.",
    f"- Gemeinsamer Job-Peak {closure['process_memory']['peak_job_committed_bytes']:,} Byte, Grenze 536.870.912 Byte. Worker beendet, Exitcode 0.",
    f"- Vorbereitung {closure['charged_previous_bytes']:,} Byte; Laufexport {export:,} Byte; zusammen {export+closure['charged_previous_bytes']:,} Byte, Gesamtgrenze 67.108.864 Byte.",
    f"- Größte Quelle {source_max:,} Byte; größter komprimierter Fall {packed_max:,} Byte; größter expandierter Fall {expanded_max:,} Byte.",
    f"- Quellen gesamt {source_total:,}/2.097.152 Byte; Fälle gesamt {case_total:,}/33.554.432 Byte; Verwaltung {admin_total:,}/2.097.152 Byte; terminaler Abschluss {(RUN/'closure.json').stat().st_size:,}/1.048.576 Byte.",
    f"- U-Zusatzheap {maxima['U']['additional_python_peak']:,}, G-eigener Heap {maxima['G']['own_heap_peak']:,}, P-eigener Heap {maxima['P']['own_heap_peak']:,} Byte. Unterschiedliche Messgrenzen beachten.",
    f"- U-Bank {maxima['U']['packed']} Byte; G-Bank 400 Byte; P ohne Lernbank. U-Originalframes konservativ {maxima['U']['original_frames_upper_bound']}, kombiniert {maxima['U']['combined_upper_bound']}; Ausgabeslots U/G/P 2/1/1.",
    f"- U-Receipt-Spitze {maxima['U']['receipt_bytes_peak']} Byte; konservative UTF-8-Obergrenze {maxima['U']['utf8_upper']} Byte. G/P-Receipts 0.",
    '- Original-/combined_peak=0 in Rohressourcen bedeutet deaktiviertes Rohframe-Tracing, nicht tatsächlichen Nullverbrauch. Boundary-Zählungen sind keine kontinuierlichen Gesamtprozessspitzen.',
    f"- {len(closure['files'])} Abschlussdateien hash- und längengeprüft; 196.608 Referenzfortschritte. Alle 8.192 gepaarten G-Q-Positionen vor/nach Update sowie Ausgabe und Fehler bitgleich; Einzelbelege je Paar in verification.json.",
    '- Alle 90 sekundären Bilanzen und 512 Diagnosezeilen aus archivierten Zielreihen kontrolliert; vollständige kumulierte Reihen, U-Lebenszyklen, Hypothesen, Feedback und Verlustereignisse bleiben in den 64 Fallarchiven erhalten.',
    '- Primärpaarwerte und alle drei Intervalle unabhängig aus dem Archiv nachgerechnet. Keine Quellenerzeugung und kein Policy-Replay bei dieser Abschlussprüfung.',
    '', '## Unveränderliche Belege und Aussagegrenze','',
    '[Originalauswertung mit exakten Brüchen, sämtlichen Maximalschadenspositionen und 95%-Intervallen](../hx1-comparison-20261004-01/assessment.json), [terminaler Abschluss](../hx1-comparison-20261004-01/closure.json), [Quellmanifest](../hx1-comparison-20261004-01/manifest.json), [Archivprüfung und Ressourcen](verification.json).',
    '', 'Die Studie betrifft den unveränderten Gesamtpfad unter begrenztem Spurbestand in dieser gebundenen Quellenfamilie. Keine isolierte EMA-Kausalbehauptung, Semantik, Clusterbildung, Feld-Memory oder Generalisierung auf neue Hinweise. Ein nicht belegter N-Vorteil ist kein Gleichwertigkeitsnachweis. Bootstrapintervalle sind nominal und approximativ.',
    '', 'Die operative Autorisierungsdatei bleibt als historischer Beleg AUTHORIZED_ONCE; exklusiver Versuchsmarker und Zielordner sperren die Wiederverwendung. Status der Freigabe: VERBRAUCHT.']
(OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:facts[k] for k in ('status','verdict','primary','classes','maxima','supervisor_seconds','export_plus_preparation_bytes')},ensure_ascii=False,indent=2))
