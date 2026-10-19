"""UHR1 neutral archive verification: no policy imports or source generation."""
import gzip,hashlib,json,struct,zlib
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from math import lcm
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
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


def verify(folder,matrix):
    RUN=Path(folder)
    closure=read(RUN/'closure.json')
    assert closure['status']=='COMPLETE' and closure['error'] is None
    assert closure['worker_exitcode']==0 and not closure['worker_alive'] and not closure['resume_permitted']
    assert closure['neutral_only']
    assert {p.name for p in RUN.iterdir()}==set(closure['files'])|{'closure.json'}
    for name,e in closure['files'].items():assert sha(RUN/name)==e['sha256'] and (RUN/name).stat().st_size==e['bytes']
    sources=read(RUN/'manifest.json')
    assessment=read(RUN/'assessment.json');done=read(RUN/'worker-complete.json')
    assert (done['cases'],done['arms'],done['arm_frames'],done['reference_advances'])==(64,128,131072,131072)
    assert done['neutral_only'] and not assessment['known_sources'] and assessment['neutral_only']
    assert read(RUN/'manifest.json')['all_sources_before_policy']
    data=Path(matrix).read_bytes();assert len(data)==320000
    assert hashlib.sha256(data).hexdigest()==assessment['bootstrap_sha256']
    draws=[data[i:i+32] for i in range(0,len(data),32)]
    rows={};means={};peaks={};decoded=errors_checked=u_equal=0;packed=expanded=0
    availability=Counter();replacement_total=0
    for e in sources['entries']:
        p=RUN/e['path'];assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes']
        s=read(p);rep,c=e['replicate'],e['condition'];case=RUN/f'UHR1-{rep:02d}-{c}-case.json.gz'
        raw=gzip.decompress(case.read_bytes());v=json.loads(raw);packed=max(packed,case.stat().st_size);expanded=max(expanded,len(raw))
        assert v['complete'] and v['cleanup'] and v['neutral_only'] and v['censored_target']==1025
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
        assert v['U']['reference_equal'] and v['U']['cleanup']
        assert len(v['U']['rows'])==511 and len(v['U']['forecasts'])==512 and len(v['U']['events'])==513
        for ur,row in zip(v['U']['rows'],rs,strict=True):
            target=row['target'];assert target==ur['target']
            predicted_index=ur['selected']['original'] if ur['selected'] else target-1
            pred=s['catalog'][s['ids'][predicted_index-1]];actual=s['catalog'][s['ids'][target-1]]
            total=0.0
            for j in range(48):total=total+abs(pred[j]-actual[j])
            assert total/48.0==ur['error']==row['U'];u_equal+=1
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
    expected='NEUTRAL_TECHNICAL_ONLY'
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
    sourcebytes=sum(p.stat().st_size for p in RUN.glob('*-source.json'))
    assert sourcebytes<=2*1048576
    admin=export-casebytes-sourcebytes-(RUN/'closure.json').stat().st_size
    assert casebytes<=32*1048576 and admin<=2*1048576 and packed<=524288 and expanded<=4194304
    assert export+closure['charged_previous_bytes']<=64*1048576
    return dict(status='PASS_ARCHIVE_VERIFICATION',neutral_only=True,closure_sha256=sha(RUN/'closure.json'),
        files_verified=len(closure['files']),counts=done,H_decoded_frames=decoded,H_outputs_independently_scored=errors_checked,
        U_outputs_independently_scored=u_equal,primary_and_all_secondary_intervals_recomputed=True,
        availability=dict(availability),H_replacements=replacement_total,maxima=peaks,process_memory=closure['process_memory'],
        supervisor_seconds=closure['elapsed_before_terminal_write'],case_compressed_max=packed,case_expanded_max=expanded,
        export_bytes=export,case_total_bytes=casebytes,source_bytes=sourcebytes,admin_bytes=admin,
        terminal_bytes=(RUN/'closure.json').stat().st_size,charged_plus_export_bytes=closure['charged_previous_bytes']+export,
        policy_replays_in_verification=0,source_materializations=0)
