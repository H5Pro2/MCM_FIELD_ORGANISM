"""UF1 research archive verification: no policy imports or source generation."""
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
        u,h=F(r['U']),F(r['F'])
        if u<h:gain+=h-u;improved+=1
        elif u>h:harm+=u-h;worse+=1;mh=max(mh,u-h)
        else:equal+=1
    return dict(count=len(rows),gain=str(gain),harm=str(harm),net=str(gain-harm),improved=improved,worse=worse,equal=equal,max_harm=str(mh))

def check_archived_state(state, previous, i, source, observed):
    """Validate archived bytes against prefix counts; no policy/reference execution.

    UF1 has exactly two keys, so no eviction is possible. Counts are an external
    census of feedback already present in the source, never future feedback.
    """
    vec=lambda n:struct.pack('<48d',*source['catalog'][source['ids'][n-1]])
    phase=i%4
    if phase==3:
        key=vec(i-2)+vec(i-1)
        record=observed.setdefault(key,{'values':{},'last':0})
        value=vec(i)
        record['values'][value]=record['values'].get(value,0)+1
        record['last']=(i+1)//4
    assert len(observed)<=2
    assert struct.unpack_from('<QQ',state,3120)==(i,(i+1)//4)
    assert state[3148:3152]==bytes(4)
    assert state[3147]=={0:0,1:2,2:6,3:0}[phase]
    assert state[3136:3144]==(i+1 if phase in (0,2) else 0).to_bytes(8,'little')
    if phase!=3:assert state[:3120]==previous[:3120]
    for slot in range(2):
        off=1560*slot
        if slot>=len(observed):
            assert state[off:off+1560]==bytes(1560)
            continue
        key,record=list(observed.items())[slot]
        assert state[off:off+768]==key
        entries=list(record['values'].items());assert 1<=len(entries)<=2
        for j in range(2):
            vb,n=entries[j] if j<len(entries) else (bytes(384),0)
            assert state[off+768+384*j:off+1152+384*j]==vb
            assert int.from_bytes(state[off+1536+8*j:off+1544+8*j],'little')==n
        assert int.from_bytes(state[off+1552:off+1560],'little')==record['last']
    if phase in (1,3):
        assert state[3144:3147]==bytes((0,255,255))
        assert state[3920:4304]==bytes(384)
    if phase in (0,3):assert state[3152:3920]==bytes(768)
    if phase==1:assert state[3152:3920]==vec(i)+bytes(384)
    if phase==0:
        assert state[3144:3147]==bytes((4,255,255))
        assert state[3920:4304]==vec(i)
    if phase==2:
        key=vec(i-1)+vec(i);assert state[3152:3920]==key
        keys=list(observed)
        if key not in observed:
            assert state[3144:3147]==bytes((1,255,255))
            assert state[3920:4304]==vec(i)
        else:
            slot=keys.index(key);entries=list(observed[key]['values'].items())
            counts=[n for _,n in entries]+([0] if len(entries)==1 else [])
            if counts[0]==counts[1]:
                assert state[3144:3147]==bytes((2,slot,255))
                assert state[3920:4304]==vec(i)
            else:
                winner=int(counts[1]>counts[0])
                assert state[3144:3147]==bytes((3,slot,winner))
                assert state[3920:4304]==entries[winner][0]

def check_resources(v):
    u,f=v['resources']['U'],v['resources']['F']
    assert u['packed']==416 and u['additional_python_peak']<=16384
    assert u['original_frames_upper_bound']<=18 and u['combined_upper_bound']<=20
    assert u['output_slots_peak']<=2 and u['receipt_bytes_peak']<=16384 and u['utf8_upper']<=32768
    assert f['packed']==4304 and f['numeric_conservative_upper']==4712 and f['numeric_limit']==5120
    assert f['own_heap_peak']<=32768 and f['output_slots']==1 and f['receipt_bytes']==0
    assert f['borrowed_input_payload']==384


def verify(folder,matrix):
    RUN=Path(folder)
    closure=read(RUN/'closure.json')
    assert closure['status']=='COMPLETE' and closure['error'] is None
    assert closure['worker_exitcode']==0 and not closure['worker_alive'] and not closure['resume_permitted']
    assert not closure['neutral_only']
    assert {p.name for p in RUN.iterdir()}==set(closure['files'])|{'closure.json'}
    for name,e in closure['files'].items():assert sha(RUN/name)==e['sha256'] and (RUN/name).stat().st_size==e['bytes']
    sources=read(RUN/'manifest.json')
    assessment=read(RUN/'assessment.json');done=read(RUN/'worker-complete.json')
    assert (done['cases'],done['arms'],done['arm_frames'],done['reference_advances'])==(64,128,131072,131072)
    assert not done['neutral_only'] and not assessment['known_sources'] and not assessment['neutral_only'] and assessment['same_family_new_sources']
    assert done['status']=='COMPLETE' and done['source_frames']==65536
    assert done['targets_per_arm']==32704 and done['Q_targets_per_arm']==16384
    assert assessment['reference_equal']
    assert read(RUN/'manifest.json')['all_sources_before_policy']
    data=Path(matrix).read_bytes();assert len(data)==320000
    assert hashlib.sha256(data).hexdigest()==assessment['bootstrap_sha256']
    draws=[data[i:i+32] for i in range(0,len(data),32)]
    for z,draw in enumerate(draws):
        for o in range(2):
            for k in range(16):
                u=int.from_bytes(hashlib.sha256(f'MCM-UF1/bootstrap/v1/z={z}/orientation={o}/k={k}'.encode()).digest()[:8],'big')
                assert draw[o*16+k]==2*(u%16)+o
    rows={};means={};peaks={};decoded=errors_checked=u_equal=0;packed=expanded=0
    availability=Counter();replacement_total=0
    for e in sources['entries']:
        p=RUN/e['path'];assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes']
        s=read(p);rep,c=e['replicate'],e['condition'];case=RUN/f'UF1-{rep:02d}-{c}-case.json.gz'
        raw=gzip.decompress(case.read_bytes());v=json.loads(raw);packed=max(packed,case.stat().st_size);expanded=max(expanded,len(raw))
        assert (v['replicate'],v['condition'],v['orientation'],v['id'])==(rep,c,(rep-1)%2,f'UF1-{rep:02d}-{c}')
        check_resources(v)
        assert v['complete'] and v['cleanup'] and not v['neutral_only'] and v['censored_target']==1025
        assert v['reference_advances']=={'U':1024,'F':1024}
        rs=v['rows'];assert [r['target'] for r in rs]==list(range(3,1024,2));rows[rep,c]=rs;by={r['target']:r for r in rs}
        state=bytearray(4304);state[3145]=state[3146]=255;histories={};observed={}
        for expected,(i,payload) in enumerate(v['F_trace'],1):
            assert i==expected
            if i>1 and i%2:
                assert int.from_bytes(state[3136:3144],'little')==i
                output=struct.unpack_from('<48d',state,3920);target=s['catalog'][s['ids'][i-1]]
                total=0.0
                for a,b in zip(output,target):total=total+abs(a-b)
                assert total/48.0==by[i]['F'];errors_checked+=1
                if i%4==3:
                    assert state[3144] in (1,2,3) and by[i]['F_known']==(state[3144] in (2,3))
                    slot=state[3145];assert by[i]['F_slot']==(None if slot==255 else slot)
                    kind=state[3144];value=state[3146];row=by[i]
                    assert row['F_class']=={1:'F0',2:'F1',3:'F2'}[kind]
                    assert row['F_value']==(None if value==255 else value)
                    counts=None if slot==255 else list(struct.unpack_from('<QQ',state,slot*1560+1536))
                    assert row['F_counts']==counts
                    assert row['F_stamp']==(None if slot==255 else int.from_bytes(state[slot*1560+1552:slot*1560+1560],'little'))
                    history=[] if slot==255 else histories.get(slot,[])
                    assert row['F_first_feedback']==(history[0] if history else None)
                    assert row['F_last_feedback']==(history[-1] if history else None)
                    assert row['F_values_occupied']==(0 if counts is None else sum(n>0 for n in counts))
                    if kind==3:
                        assert value==(0 if counts[0]>counts[1] else 1) and counts[0]!=counts[1]
                        assert state[3920:4304]==state[slot*1560+768+384*value:slot*1560+1152+384*value]
                    else:
                        assert state[3920:4304]==state[3536:3920]
                        if kind==2:assert counts[0]==counts[1]>0
            previous=bytes(state)
            delta=zlib.decompress(bytes.fromhex(payload));assert len(delta)==4304
            for j,byte in enumerate(delta):state[j]^=byte
            check_archived_state(state,previous,i,s,observed)
            assert int.from_bytes(state[3120:3128],'little')==i;decoded+=1
            if i%4==3:
                t=int.from_bytes(state[3128:3136],'little')
                learned=0 if int.from_bytes(state[1552:1560],'little')==t else 1
                if by[i]['F_class']=='F0':histories[learned]=[]
                histories.setdefault(learned,[]).append(i)
        assert len(v['F_trace'])==1024 and int.from_bytes(state[3136:3144],'little')==1025
        assert v['U']['reference_equal'] and v['U']['cleanup']
        assert len(v['U']['rows'])==511 and len(v['U']['forecasts'])==512 and len(v['U']['events'])==513
        assert v['replacements']==0 and v['U']['censored_target']==1025
        for j,forecast in enumerate(v['U']['forecasts']):
            a,b=2*j+1,2*j+2
            assert forecast['input_indices']==[a,b]
            assert forecast['source_intervals']==[[4800*(a-1),4800*a],[4800*(b-1),4800*b]]
            assert forecast['profile']=='4309cfc91eb99fc2a999fdac99c5a7f1807ee654996e019ec0d94e3900bcbd4b'
            assert forecast['owner']=='comparison' and forecast['stream']=='stream'
        assert [e['index'] for e in v['U']['events']]==[1]+list(range(2,1025,2))
        u_history={};u_cells={}
        lineage=lambda h:(tuple(h['ordinals']),h['offset'])
        def mae(a,b):
            total=0.0
            for x,y in zip(s['catalog'][s['ids'][a-1]],s['catalog'][s['ids'][b-1]],strict=True):total+=abs(x-y)
            return total/48.0
        for ur,row in zip(v['U']['rows'],rs,strict=True):
            target=row['target'];assert target==ur['target']
            hs=ur['hypotheses']
            for h in hs:assert h['before']==u_cells.get(lineage(h))
            scored=[(h['before'][0]-h['before'][1],h) for h in hs if h['before'] is not None and h['before'][0]<h['before'][1]]
            best=min((x for x,h in scored),default=None)
            winners=[h for x,h in scored if x==best]
            assert ur['selected']==(winners[0] if len(winners)==1 else None)
            predicted_index=ur['selected']['original'] if ur['selected'] else target-1
            assert 1<=predicted_index<target
            if target%4==3:
                hs=ur['hypotheses'];warm=[h for h in hs if h['before'] is not None]
                assert row['class']==('V0' if not hs else 'V1' if not warm else 'V3' if ur['selected'] else 'V2')
                assert row['cue']==('X' if s['ids'][target-3]==0 else 'Y')
                histories_u=[u_history.get(lineage(h),[]) for h in hs]
                assert row['age']==[len(history) for history in histories_u]
                assert row['first_feedback']==[history[0] if history else None for history in histories_u]
                assert row['last_feedback']==[history[-1] if history else None for history in histories_u]
                assert all(n<target for history in histories_u for n in history)
                assert not row['F_replaced']
            pred=s['catalog'][s['ids'][predicted_index-1]];actual=s['catalog'][s['ids'][target-1]]
            total=0.0
            for j in range(48):total=total+abs(pred[j]-actual[j])
            assert total/48.0==ur['error']==row['U'];u_equal+=1
            assert len(ur['updates'])==len(hs)
            for h,update in zip(hs,ur['updates'],strict=True):
                assert lineage(h)==lineage(update) and h['key']==update['key']
                assert update['ec']==mae(h['original'],target) and update['ep']==mae(target-1,target)
                if update['live']:
                    key=lineage(update);old=u_cells.get(key)
                    u_cells[key]=[update['ec'],update['ep']] if old is None else [.5*old[0]+.5*update['ec'],.5*old[1]+.5*update['ep']]
                    u_history.setdefault(key,[]).append(target)
        cum=qcum=F(0)
        for r in rs:
            cum+=F(r['U'])-F(r['F']);assert cum==F(r['cumulative'])
            if r['target']%4==3:
                qcum+=F(r['U'])-F(r['F']);assert qcum==F(r['cumulative_Q'])
                availability[c+':'+r['class']]+=1;availability[c+':F_known='+str(r['F_known'])]+=1
                replacement_total+=int(r['F_replaced'])
            else:assert r['U']==r['F']
        for mask in ('Q','G_all','S','Q_X','Q_Y'):
            subset=select(rs,mask);assert len(subset)=={'Q':256,'G_all':511,'S':255,'Q_X':128,'Q_Y':128}[mask]
            for arm in ('U','F'):means[rep,c,mask,arm]=sum((F(r[arm]) for r in subset),F(0))/len(subset)
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
    
    assert {(d['condition'],d['mask'],d['orientation']) for d in assessment['secondary']}=={(c,m,o) for c in ('D','N') for m in ('Q','G_all','S','Q_X','Q_Y') for o in (None,0,1)}
    expected_diagnosis={(r,c,p,label) for r in range(1,33) for c in ('D','N') for p,labels in [('class',('V0','V1','V2','V3')),('F_class',('F0','F1','F2')),('F_known',(False,True)),('F_replaced',(False,True))] for label in labels}
    assert {(d['replicate'],d['condition'],d['partition'],d['label']) for d in assessment['diagnosis']}==expected_diagnosis
    for d in assessment['secondary']:
        c,mask,o=d['condition'],d['mask'],d['orientation']
        reps=list(range(1,33)) if o is None else list(range(o+1,33,2))
        vals=[means[r,c,mask,'U']-means[r,c,mask,'F'] for r in range(1,33)]
        assert [vals[r-1] for r in reps]==list(map(F,d['pairs']))
        assert ci(vals,o)==list(map(F,d['ci']))
        assert sum((vals[r-1] for r in reps),F(0))/len(reps)==F(d['mean'])
        selected=[r for rep in reps for r in select(rows[rep,c],mask)];g=gains(selected)
        for k,x in g.items():assert F(x)==F(d[k]),(k,x,d[k])
        for arm in ('U','F'):assert sum((means[r,c,mask,arm] for r in reps),F(0))/len(reps)==F(d['means'][arm])
        mh=F(d['max_harm'])
        assert [[rep,r['target']] for rep in reps for r in select(rows[rep,c],mask) if mh>0 and F(r['U'])-F(r['F'])==mh]==d['maximum_harm_targets']
        assert max(vals[r-1] for r in reps)==F(d['worst_mean'])
    for d in assessment['diagnosis']:
        subset=[r for r in select(rows[d['replicate'],d['condition']],'Q') if r[d['partition']]==d['label']]
        for k,x in gains(subset).items():assert F(x)==F(d[k])
    primary=assessment['primary'];pv=[means[r,'D','Q','U']-means[r,'D','Q','F'] for r in range(1,33)]
    assert pv==list(map(F,primary['pairs'])) and ci(pv)==list(map(F,primary['ci']))
    assert F(primary['mean'])==sum(pv,F(0))/32 and primary['name']=='D:U-F'
    expected='F_VORTEIL_BELEGT' if F(primary['ci'][0])>0 else 'U_VORTEIL_GEGEN_F_BELEGT' if F(primary['ci'][1])<0 else 'KEIN_EINDEUTIGER_UNTERSCHIED_NACHGEWIESEN'
    assert expected==primary['verdict']==assessment['verdict']
    iv=[means[r,'D','Q','U']-means[r,'D','Q','F']-means[r,'N','Q','U']+means[r,'N','Q','F'] for r in range(1,33)]
    assert iv==list(map(F,assessment['interaction']['pairs'])) and ci(iv)==list(map(F,assessment['interaction']['ci']))
    assert F(assessment['interaction']['mean'])==sum(iv,F(0))/32
    diagnosis=[]
    for c in ('D','N'):
        for field,labels in [('class',('V0','V1','V2','V3')),('F_class',('F0','F1','F2')),('F_known',(False,True)),('F_replaced',(False,True))]:
            for label in labels:
                subset=[r for rep in range(1,33) for r in select(rows[rep,c],'Q') if r[field]==label]
                diagnosis.append(dict(condition=c,partition=field,label=label,**gains(subset)))
    assert decoded==65536 and errors_checked==u_equal==32704
    assert len(assessment['secondary'])==30 and len(assessment['diagnosis'])==704
    assert assessment['story_means']==[dict(replicate=r,condition=c,mask=m,arm=a,mean=str(x)) for (r,c,m,a),x in sorted(means.items())]
    assert closure['process_memory']['peak_job_committed_bytes']<=536870912 and closure['total_deadline_met']
    assert closure['process_memory']['hard_job_limit'] and closure['process_memory']['limit_bytes']==536870912
    assert closure['total_seconds']==3600 and closure['elapsed_before_terminal_write']<=3600 and done['engine_seconds']<=3540
    attempt=read(RUN/'attempt.json');start=read(RUN/'start.json')
    assert not attempt['neutral_only'] and not start['neutral_only']
    assert attempt['total_deadline_ns']-attempt['begin_ns']==3600*10**9
    assert attempt['worker_deadline_ns']-attempt['begin_ns']==3540*10**9
    assert start['charged']==closure['charged_previous_bytes']<=8*1048576
    assert peaks['U']['additional_python_peak']<=16384 and peaks['F']['own_heap_peak']<=32768
    export=sum(p.stat().st_size for p in RUN.iterdir());casebytes=sum(p.stat().st_size for p in RUN.glob('*-case.json.gz'))
    sourcebytes=sum(p.stat().st_size for p in RUN.glob('*-source.json'))
    assert sourcebytes<=2*1048576
    admin=export-casebytes-sourcebytes-(RUN/'closure.json').stat().st_size
    assert casebytes<=32*1048576 and admin<=2*1048576 and packed<=524288 and expanded<=4194304
    assert export+closure['charged_previous_bytes']<=64*1048576
    assert (RUN/'closure.json').stat().st_size<=1048576
    return dict(status='PASS_ARCHIVE_VERIFICATION',neutral_only=False,primary=primary,verdict=expected,diagnosis=diagnosis,story_means=assessment['story_means'],closure_sha256=sha(RUN/'closure.json'),
        files_verified=len(closure['files']),counts=done,F_decoded_frames=decoded,F_outputs_independently_scored=errors_checked,
        U_outputs_independently_scored=u_equal,primary_and_all_secondary_intervals_recomputed=True,
        availability=dict(availability),F_replacements=replacement_total,maxima=peaks,process_memory=closure['process_memory'],
        supervisor_seconds=closure['elapsed_before_terminal_write'],case_compressed_max=packed,case_expanded_max=expanded,
        export_bytes=export,case_total_bytes=casebytes,source_bytes=sourcebytes,admin_bytes=admin,
        terminal_bytes=(RUN/'closure.json').stat().st_size,charged_plus_export_bytes=closure['charged_previous_bytes']+export,
        complete_F_state_prefix_census=True,bootstrap_indices_independently_verified=320000,
        audit_date='2026-10-14',policy_replays_in_verification=0,source_materializations=0)

if __name__=='__main__':
    ROOT=Path(__file__).resolve().parents[3]
    OUT=Path(__file__).parent
    RUN=ROOT/'reports/s2uc/uf1-comparison-20261005-01'
    prefix='S2UC_UF1_V1_20261005'
    pre=ROOT/'docs'/f'{prefix}_VORSTARTBINDUNG.json'
    code=ROOT/'docs'/f'{prefix}_CODEBINDUNG.json'
    auth=ROOT/'docs'/f'{prefix}_AUTORISIERUNG.json'
    matrix=ROOT/'docs'/f'{prefix}_BOOTSTRAP.bin'
    assert sha(pre)=='1a2c3bcab967eeed4d6fa422693216f8ba2853bac7aaab389ecc54aa606eb6d7'
    assert read(auth)==read(ROOT/'docs'/f'{prefix}_AUTORISIERUNG_VORLAGE.json')|{'status':'AUTHORIZED_ONCE'}
    assert read(auth)['prestart_sha256']==sha(pre)
    assert read(auth)['recipe_contract_sha256']==sha(ROOT/'docs/S2UC_UF1_PRUEFVERTRAG_20261005.md')
    plan=read(code)['plan']|{'authorization':str(auth.resolve())}
    assert read(RUN/'start.json')['plan_sha256']==hashlib.sha256((json.dumps(plan,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
    preparation_names=set(read(code)['files'])|set(read(pre)['files'])|{code.relative_to(ROOT).as_posix(),pre.relative_to(ROOT).as_posix(),f'docs/{prefix}_AUTORISIERUNG_VORLAGE.json'}
    assert sum((ROOT/n).stat().st_size for n in preparation_names)+auth.stat().st_size==read(RUN/'closure.json')['charged_previous_bytes']
    for n,h in (read(code)['files']|read(pre)['files']).items():assert sha(ROOT/n)==h,n
    facts=verify(RUN,matrix)
    manifest=read(RUN/'manifest.json');tables=[]
    assert len(manifest['entries'])==64 and not manifest['neutral_only']
    assert manifest['namespace']=='MCM-UF1/source/v1'
    previous=None
    for idx,e in enumerate(manifest['entries']):
        r=idx//2+1;c='D' if idx%2==0 else 'N'
        assert (e['replicate'],e['condition'],e['orientation'],e['id'],e['path'])==(r,c,(r-1)%2,f'UF1-{r:02d}-{c}',f'UF1-{r:02d}-{c}-source.json')
        source=read(RUN/e['path']);assert not source['neutral_only']
        assert (RUN/e['path']).read_bytes()==(json.dumps(source,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
        assert source['catalog']==[[x+j/4096 for j in range(48)] for x in (.125,.875,.5,.25,.75,.0625)]
        ids=source['ids'];assert len(ids)==1024
        assert ids[1::4]==[2]*256 and ids[3::4]==[5]*256
        cues=ids[::4];targets=ids[2::4]
        assert Counter(cues)=={0:128,1:128} and Counter(targets)=={3:128,4:128}
        counts=Counter(zip(cues,targets));table=[counts[x] for x in ((0,3),(0,4),(1,3),(1,4))]
        if c=='D':
            assert table==([96,32,32,96] if r%2 else [32,96,96,32]);previous=targets
        else:assert targets==previous
        assert source['draws']==e['draws'] and set(e['draws'])=={'continuation','dependent-A','dependent-B','null-cue'}
        assert all(type(n) is int and 0<n<=4096 for n in e['draws'].values())
        assert e['bytes']<=32768
        tables.append(dict(replicate=r,condition=c,orientation=(r-1)%2,XA_XB_YA_YB=table,draws=e['draws'],sha256=e['sha256']))
    facts.update(prestart_sha256=sha(pre),code_binding_sha256=sha(code),authorization_sha256=sha(auth),
        manifest_sha256=sha(RUN/'manifest.json'),authorization_consumed=True,source_tables=tables,
        source_recipe_regenerations_in_audit=0,old_results_pooled=False)
    with (OUT/'verification.json').open('x',encoding='utf-8') as stream:json.dump(facts,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({k:facts[k] for k in ('status','verdict','primary','process_memory','supervisor_seconds','charged_plus_export_bytes')},ensure_ascii=False,indent=2))
