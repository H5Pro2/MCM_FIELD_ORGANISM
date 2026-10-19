"""UH1 archival verification only: no policy imports, replay or source generation."""
import gzip,hashlib,json,struct,zlib
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from math import lcm
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).parent
RUN=ROOT/'reports/s2uc/uh1-comparison-20261004-01'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,v):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def dec(x):return f'{float(F(x)):.12f}'
def select(rows,mask):return [r for r in rows if mask=='G_all' or mask=='Q' and r['target']%4==3 or mask=='S' and r['target']%4==1 or mask.startswith('Q_') and r.get('cue')==mask[-1]]
def maxima(dst,src):
    for k,v in src.items():
        if isinstance(v,dict):maxima(dst.setdefault(k,{}),v)
        elif isinstance(v,(int,float)):dst[k]=max(dst.get(k,0),v)
def gains(rows):
    gain=harm=F(0);improved=worse=equal=0;mh=F(0)
    for r in rows:
        u,h=F(r['U']),F(r['H'])
        if u<h:gain+=h-u;improved+=1
        elif u>h:harm+=u-h;worse+=1;mh=max(mh,u-h)
        else:equal+=1
    return dict(count=len(rows),gain=str(gain),harm=str(harm),net=str(gain-harm),improved=improved,worse=worse,equal=equal,max_harm=str(mh))

closure=read(RUN/'closure.json')
assert closure['status']=='COMPLETE' and closure['error'] is None
assert closure['worker_exitcode']==0 and not closure['worker_alive'] and not closure['resume_permitted']
assert not closure['neutral_only']
assert {p.name for p in RUN.iterdir()}==set(closure['files'])|{'closure.json'}
for name,e in closure['files'].items():assert sha(RUN/name)==e['sha256'] and (RUN/name).stat().st_size==e['bytes']
prefix=ROOT/'docs/S2UC_UH1_V1_20261005'
pre=Path(str(prefix)+'_VORSTARTBINDUNG.json');code=Path(str(prefix)+'_CODEBINDUNG.json')
auth=Path(str(prefix)+'_AUTORISIERUNG.json');template=Path(str(prefix)+'_AUTORISIERUNG_VORLAGE.json')
assert sha(pre)=='49c8118f34cd4b7e13f0de720d3521e164ac3a35cca761d023ca830fe55becc7'
assert read(auth)==read(template)|{'status':'AUTHORIZED_ONCE'}
for name,h in read(code)['files'].items():assert sha(ROOT/name)==h
sources=read(ROOT/'docs/S2UC_UH1_QUELLENBINDUNG_20261004.json')
assessment=read(RUN/'assessment.json');done=read(RUN/'worker-complete.json')
assert (done['cases'],done['arms'],done['arm_frames'],done['reference_advances'])==(64,128,131072,131072)
assert not done['neutral_only'] and assessment['known_sources'] and not assessment['neutral_only']
assert read(RUN/'manifest.json')['all_sources_before_policy']
data=Path(str(prefix)+'_BOOTSTRAP.bin').read_bytes();assert len(data)==320000
assert hashlib.sha256(data).hexdigest()==assessment['bootstrap_sha256']
draws=[data[i:i+32] for i in range(0,len(data),32)]
rows={};means={};peaks={};decoded=errors_checked=u_equal=0;packed=expanded=0
availability=Counter();replacement_total=0
for e in sources['entries']:
    p=ROOT/e['path'];assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes']
    s=read(p);rep,c=e['replicate'],e['condition'];case=RUN/f'UH1-{rep:02d}-{c}-case.json.gz'
    raw=gzip.decompress(case.read_bytes());v=json.loads(raw);packed=max(packed,case.stat().st_size);expanded=max(expanded,len(raw))
    assert v['complete'] and v['cleanup'] and not v['neutral_only'] and v['censored_target']==1025
    assert v['reference_advances']=={'U':1024,'H':1024}
    rs=v['rows'];assert [r['target'] for r in rs]==list(range(3,1024,2));rows[rep,c]=rs;by={r['target']:r for r in rs}
    state=bytearray(3520)
    for expected,(i,payload) in enumerate(v['H_trace'],1):
        assert i==expected
        if i>1 and i%2:
            assert int.from_bytes(state[2352:2360],'little')==i
            output=struct.unpack_from('<48d',state,3136);target=s['catalog'][s['ids'][i-1]]
            total=0.0
            for a,b in zip(output,target):total=total+abs(a-b)
            assert total/48.0==by[i]['H'];errors_checked+=1
            if i%4==3:
                assert state[2360] in (1,2) and by[i]['H_known']==(state[2360]==1)
                slot=state[2361];assert by[i]['H_slot']==(None if slot==255 else slot)
        delta=zlib.decompress(bytes.fromhex(payload));assert len(delta)==3520
        for j,byte in enumerate(delta):state[j]^=byte
        assert int.from_bytes(state[2336:2344],'little')==i;decoded+=1
    assert len(v['H_trace'])==1024 and int.from_bytes(state[2352:2360],'little')==1025
    previous=read_gzip=ROOT/f'reports/s2uc/hx1-comparison-20261004-01/HX1-{rep:02d}-{c}-case.json.gz'
    old=json.loads(gzip.decompress(previous.read_bytes()))
    assert [r['U'] for r in rs]==[r['U'] for r in old['rows']];u_equal+=len(rs)
    cum=qcum=F(0)
    for r in rs:
        cum+=F(r['U'])-F(r['H']);assert cum==F(r['cumulative'])
        if r['target']%4==3:
            qcum+=F(r['U'])-F(r['H']);assert qcum==F(r['cumulative_Q'])
            availability[c+':'+r['class']]+=1;availability[c+':H_known='+str(r['H_known'])]+=1
            replacement_total+=int(r['H_replaced'])
        else:assert r['U']==r['H']
    for mask in ('Q','G_all','S','Q_X','Q_Y'):
        subset=select(rs,mask);assert len(subset)=={'Q':256,'G_all':511,'S':255,'Q_X':128,'Q_Y':128}[mask]
        for arm in ('U','H'):means[rep,c,mask,arm]=sum((F(r[arm]) for r in subset),F(0))/len(subset)
    maxima(peaks,v['resources']);maxima(peaks.setdefault('observer',{}),v['observer'])

def ci(vals,orientation=None):
    den=lcm(*(x.denominator for x in vals));nums=[int(x*den) for x in vals];bs=[]
    for draw in draws:
        ids=draw if orientation is None else draw[16*orientation:16*(orientation+1)]
        bs.append(sum(nums[i] for i in ids))
    bs.sort();ends=[]
    for numerator in (1,39):
        index,remainder=divmod(9999*numerator,40)
        ends.append(F(bs[index]*(40-remainder)+bs[index+1]*remainder,40*len(ids)*den))
    return ends

for d in assessment['secondary']:
    c,mask,o=d['condition'],d['mask'],d['orientation']
    reps=list(range(1,33)) if o is None else list(range(o+1,33,2))
    vals=[means[r,c,mask,'U']-means[r,c,mask,'H'] for r in range(1,33)]
    assert [vals[r-1] for r in reps]==list(map(F,d['pairs']))
    assert ci(vals,o)==list(map(F,d['ci']))
    assert sum((vals[r-1] for r in reps),F(0))/len(reps)==F(d['mean'])
    selected=[r for rep in reps for r in select(rows[rep,c],mask)];g=gains(selected)
    for k,x in g.items():assert F(x)==F(d[k]),(k,x,d[k])
    for arm in ('U','H'):assert sum((means[r,c,mask,arm] for r in reps),F(0))/len(reps)==F(d['means'][arm])
    mh=F(d['max_harm'])
    assert [[rep,r['target']] for rep in reps for r in select(rows[rep,c],mask) if mh>0 and F(r['U'])-F(r['H'])==mh]==d['maximum_harm_targets']
    assert max(vals[r-1] for r in reps)==F(d['worst_mean'])
for d in assessment['diagnosis']:
    subset=[r for r in select(rows[d['replicate'],d['condition']],'Q') if r[d['partition']]==d['label']]
    for k,x in gains(subset).items():assert F(x)==F(d[k])
primary=assessment['primary'];pv=[means[r,'D','Q','U']-means[r,'D','Q','H'] for r in range(1,33)]
assert pv==list(map(F,primary['pairs'])) and ci(pv)==list(map(F,primary['ci']))
expected='H_VORTEIL_BELEGT' if F(primary['ci'][0])>0 else 'H_ERWARTUNG_WIDERLEGT_U_VORTEIL' if F(primary['ci'][1])<0 else 'LEISTUNGSRICHTUNG_NICHT_NACHGEWIESEN'
assert expected==primary['verdict']==assessment['verdict']
iv=[means[r,'D','Q','U']-means[r,'D','Q','H']-means[r,'N','Q','U']+means[r,'N','Q','H'] for r in range(1,33)]
assert iv==list(map(F,assessment['interaction']['pairs'])) and ci(iv)==list(map(F,assessment['interaction']['ci']))
diagnosis=[]
for c in ('D','N'):
    for field,labels in [('class',('V0','V1','V2','V3')),('H_known',(False,True)),('H_replaced',(False,True))]:
        for label in labels:
            subset=[r for rep in range(1,33) for r in select(rows[rep,c],'Q') if r[field]==label]
            diagnosis.append(dict(condition=c,partition=field,label=label,**gains(subset)))
assert decoded==65536 and errors_checked==u_equal==32704
assert len(assessment['secondary'])==30 and len(assessment['diagnosis'])==512
assert closure['process_memory']['peak_job_committed_bytes']<=536870912 and closure['total_deadline_met']
assert peaks['U']['additional_python_peak']<=16384 and peaks['H']['own_heap_peak']<=32768
export=sum(p.stat().st_size for p in RUN.iterdir());casebytes=sum(p.stat().st_size for p in RUN.glob('*-case.json.gz'))
admin=export-casebytes-(RUN/'closure.json').stat().st_size
assert casebytes<=32*1048576 and admin<=2*1048576 and packed<=524288 and expanded<=4194304
assert export+closure['charged_previous_bytes']<=64*1048576
facts=dict(status='PASS_ARCHIVE_VERIFICATION',known_sources=True,authorization_consumed=True,prestart_sha256=sha(pre),authorization_sha256=sha(auth),
    closure_sha256=sha(RUN/'closure.json'),files_verified=len(closure['files']),counts=done,primary=primary,verdict=expected,
    H_decoded_frames=decoded,H_outputs_independently_scored=errors_checked,U_errors_equal_HX1=u_equal,
    primary_and_all_secondary_intervals_recomputed=True,availability=dict(availability),diagnosis=diagnosis,H_replacements=replacement_total,
    maxima=peaks,process_memory=closure['process_memory'],supervisor_seconds=closure['elapsed_before_terminal_write'],case_compressed_max=packed,
    case_expanded_max=expanded,export_bytes=export,case_total_bytes=casebytes,admin_bytes=admin,terminal_bytes=(RUN/'closure.json').stat().st_size,
    charged_preparation_and_source_bytes=closure['charged_previous_bytes'],charged_plus_export_bytes=closure['charged_previous_bytes']+export,
    policy_replays_in_verification=0,source_materializations=0)
save('verification.json',facts)
lines=['# UH1 Ergebnis auf bekannten HX1 Quellen','',f"Technischer Abschluss COMPLETE; Archivprüfung PASS. Primärurteil **{expected}**.",
    '', '**Untersuchung auf bekannten Quellen.** Vergleich zweier Gesamtverfahren mit unterschiedlicher Speicherrepräsentation und unterschiedlichem Informationszugang. H kennt die Vierframephase und hält zwei vollständige Hinweisschlüssel mit Mittelwerten. U behält reguläre Originalspuren. Keine isolierte Kausalzuordnung zu Speicherumfang oder Mittelwertbildung. Keine unabhängige Replikation.',
    '', '## Einziger Primärkontrast','', 'D:U−H auf allen Q-Zielen; positive Werte sprechen für H. 32 Paarwerte, 10.000 nach Orientierung geschichtete Clusterbootstrap-Ziehungen. Nominales approximatives 95%-Intervall; Urteile aus exakten rationalen Werten.',
    '',f"Mittel **{dec(primary['mean'])}**, Intervall **[{dec(primary['ci'][0])}; {dec(primary['ci'][1])}]**, Urteil **{expected}**.",
    '', '## Vollständige ergänzende Bilanzen','', 'Alle Zahlen gerundet. Netto = Gewinn_U − Schaden_U. Explorative 95%-Intervalle; keine zusätzlichen bestätigenden Regeln. Masken überlappen und werden nicht addiert.',
    '', '| C | Maske | o | n | U-MAE | H-MAE | U−H | 95%-Intervall | besser/schlechter/gleich | Gewinn U | Schaden U | Netto | Max. Schaden | Schlechtester Geschichtenkontrast |',
    '| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |']
for d in assessment['secondary']:
    parts=[d['condition'],d['mask'],'alle' if d['orientation'] is None else str(d['orientation']),str(d['count']),dec(d['means']['U']),dec(d['means']['H']),dec(d['mean']),f"[{dec(d['ci'][0])}; {dec(d['ci'][1])}]",f"{d['improved']}/{d['worse']}/{d['equal']}"]
    parts += [dec(d[k]) for k in ('gain','harm','net','max_harm','worst_mean')];lines.append('| '+' | '.join(parts)+' |')
i=assessment['interaction'];lines += ['',f"Explorative Q-Interaktion D−N: {dec(i['mean'])}, 95%-Intervall [{dec(i['ci'][0])}; {dec(i['ci'][1])}].",'', '## Verfügbarkeit und vollständige Beiträge auf Q','',
    'U-V0 keine passende Spur, V1 nur kalte Zellen, V2 warme Zellen/Persistenz, V3 warme Zellen/Kontextausgabe. H_known: bekannte Prognose vor Zielbeobachtung. H_replaced: regulärer Slotersatz beim Feedback. Jede Partition separat vollständig; Partitionen nicht miteinander addieren.',
    '', '| C | Partition | Klasse | n | Gewinn U | Schaden U | Netto |','| --- | --- | --- | ---: | ---: | ---: | ---: |']
for d in diagnosis:lines.append('| '+' | '.join([d['condition'],d['partition'],str(d['label']),str(d['count']),dec(d['gain']),dec(d['harm']),dec(d['net'])])+' |')
lines += ['', '## Alle Primärpaarwerte','', '| r | U−H in D |','| ---: | ---: |']
for r,val in enumerate(primary['pairs'],1):lines.append(f'| {r} | {dec(val)} |')
lines += ['', '## Ressourcen und Vollständigkeit','',
    f"- 64 unveränderte Archivquellen, 128 frische Armläufe, {done['arm_frames']:,} Frame-Verarbeitungen und ebenso viele unabhängige Referenzfortschritte. Keine Quellenneugenerierung.",
    f"- Worker {done['engine_seconds']:.6f} s; Supervisor {closure['elapsed_before_terminal_write']:.6f} s; Grenzen 3.540/3.600 s. Worker beendet, Exitcode 0.",
    f"- Gemeinsamer Job-Peak {closure['process_memory']['peak_job_committed_bytes']:,} Byte unter 536.870.912 Byte.",
    f"- U-Zusatzheap {peaks['U']['additional_python_peak']:,} Byte unter 16.384; H-eigener Heap {peaks['H']['own_heap_peak']:,} Byte unter 32.768. Unterschiedliche Messgrenzen, keine Ressourcengleichheit.",
    f"- U-Bank 416 Byte; H-Bank 3.520 Byte, konservative Numerik 3.928 unter 4.096 Byte. U konservativ Original/Kombination {peaks['U']['original_frames_upper_bound']}/{peaks['U']['combined_upper_bound']}; Ausgabeslots U/H 2/1.",
    f"- U Receipt {peaks['U']['receipt_bytes_peak']} Byte, UTF-8-Obergrenze {peaks['U']['utf8_upper']} Byte. H Receipt 0, geliehener aktueller Frame 384 Rohbytes/{peaks['H']['borrowed_input_object_bytes']} Objektbytes.",
    f"- Vorbereitung und Archivquellen belastet: {closure['charged_previous_bytes']:,} Byte; Export {export:,}; zusammen {closure['charged_previous_bytes']+export:,} unter 67.108.864 Byte.",
    f"- Fallarchive gesamt {casebytes:,} unter 33.554.432 Byte; Verwaltung {admin:,} unter 2.097.152; Abschluss {(RUN/'closure.json').stat().st_size:,} unter 1.048.576 Byte.",
    f"- Größter Fall komprimiert {packed:,} unter 524.288 Byte; expandiert {expanded:,} unter 4.194.304 Byte.",
    '- Rohressourcenwerte original_frames_peak/combined_peak=0 bedeuten deaktiviertes Rohframe-Tracing, nicht Nullbelegung. Konservative Belegung und externe Grenzstelleninventare separat in verification.json.',
    f"- {len(closure['files'])} Abschlussdateien hashgeprüft. 65.536 H-Zustände dekodiert, 32.704 H-Ausgaben aus dem Archiv erneut bewertet; 32.704 U-Fehler stimmen mit HX1 überein. U wurde im neuen Lauf frisch ausgeführt.",
    '- Primärintervall und alle 30 ergänzenden Intervalle, Interaktion, 512 Diagnosezeilen, Gewinn-/Schadenssummen und kumulierte Zielverläufe aus archivierten Werten nachgeprüft. Keine Policy während dieser Prüfung ausgeführt.',
    '', '## Grenzen und Belege','',
    'HX1 bleibt abgenommen. UH1 prüft einen weiteren Leistungsvergleich; weder Semantik noch Feld-Memory oder allgemeine Überlegenheit werden behauptet. Der Mittelwert ist unter MAE nicht allgemein optimal. Nichtnachweis ist kein Gleichwertigkeitsnachweis. Eine Übernahme von H ist nicht beauftragt und wurde nicht vorgenommen.',
    '', '[Exakte Auswertung mit allen Maximalschadenspositionen und Geschichtenwerten](../uh1-comparison-20261004-01/assessment.json), [terminaler Laufabschluss](../uh1-comparison-20261004-01/closure.json), [Prüfbilanz und vollständige Ressourcenmaxima](verification.json). Vollständige U-Lebenszyklen, H-Zustandsdeltas und Zielverläufe verbleiben in den 64 ursprünglichen Fallarchiven.',
    '', 'Einmalfreigabe VERBRAUCHT. Die Autorisierungsdatei bleibt als historischer Beleg AUTHORIZED_ONCE; der exklusive Zielordner sperrt Wiederverwendung. Kein weiterer Lauf, keine Ersatzquelle oder Fallkürzung.']
(OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:facts[k] for k in ('status','verdict','primary','availability','H_replacements','process_memory','supervisor_seconds','charged_plus_export_bytes')},ensure_ascii=False,indent=2))
