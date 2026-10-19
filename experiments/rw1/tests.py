"""C1-C6: artificial vectors, small adapter fixture, mock I/O. No source synthesis."""
import copy,json,math
from unittest.mock import patch
from .common import *
from . import gateway,evaluate,audit,engine

def rejects(fn,contains=None):
    try:fn()
    except (ValueError,FileExistsError,FileNotFoundError) as e:
        if contains:need(contains in str(e),'WRONG_REJECTION:'+str(e))
        return
    raise AssertionError('EXPECTED_REJECTION')
def v(x):return [float(x)]*48
def synthetic(case,arm):
    k=int(case[1:])//480;correct=case[0]=='A' and (arm=='T' or k==0)
    receipt=dict(matches=[])
    if correct:
        if k:receipt['alignment']=dict(matches=[[0,k,[1.]]],sources=[['retained',1,[1,2,3,4]]])
        else:receipt['matches']=[dict(role='retained',generation=1,ordinals=[1,2,3,4],offset=0,factors=[1.])]
    f=dict(provenance_json=json.dumps(receipt),context_values=v(0) if correct else None,persistence_values=v(1),status='PREDICTED' if correct else 'ABSTAIN')
    return dict(target=11,forecast=f,actual=v(0),hint=[v(CASES.index(case)+2),v(1)],stock_fingerprint='same')
def sample_archives():
    return {c+'-'+a:dict(records=[dict(copy.deepcopy(synthetic(c,a)),target=i) for i in (3,5,7,9,11)]) for c in CASES for a in ('N','T')}

class FakeLedger:
    def __init__(self):self.counts={k:0 for k in EXPECTED}
    def bump(self,k):self.counts[k]+=1
class FakeMaterial:
    """Zero bytes are opaque fixture buffers, never generated RW1 source samples."""
    def __init__(self):self.payload=bytes(19200);self.reads=[]
    def row(self,name):
        c,kind,*tail=name.split('-')
        if kind=='base':
            i=int(tail[0]);value=((i-1)%4+1)/10;start=(i-1)*4800
        else:
            b,k=map(int,tail);value=.001*(k+1);start=b*19200+k*480
        projection=dict(values=v(value),profile_digest='4a56de2f630055816533ecb45cdef5662157993bc1192023d01cf29e92247c9f',window_start_tick=start,window_end_tick=start+4800)
        projection['projection_digest']=digest(json.dumps(projection,sort_keys=True,separators=(',',':')).encode('ascii'))
        return dict(projection=projection,pcm_sha256=digest(self.payload),start=start)
    def read_input(self,c,i):self.reads.append(i);return self.row(key(c,i)),self.payload
    def historical(self,c,p,t):
        b,k=divmod(t,19200);return tuple(self.row(f'{c}-bank-{b}-{k//480}')['projection']['values'])

def run(folder):
    passed=[];details={};checks=0
    # Tripwires guard every known real source/projection entry for the whole suite.
    def forbidden(*args,**kwargs):raise AssertionError('FORBIDDEN_REAL_MATERIAL_OR_PROJECTION')
    with patch('experiments.as480.material.source_pcm',side_effect=forbidden),patch('experiments.temporal_alignment.projector.Projector.__call__',side_effect=forbidden),patch('mcm_field_organism.log_spectral_receptor.LogSpectralReceptor.analyze',side_effect=forbidden),patch('tools._s2nj_private_auditory_output_projection.project_auditory_half_v1',side_effect=forbidden):
        # C1: absence must stop before binding, worker, output, and material.
        with patch.object(gateway,'binding',side_effect=AssertionError('TOO_LATE')):
            rejects(lambda:gateway.supervise('research'), 'AUTHORIZATION_REQUIRED');checks+=1
        fake_order='11111111-1111-4111-8111-111111111111';h='f'*64
        auth=dict(status='AUTHORIZED_ONCE',mode='RW1_RESEARCH',execution_order=fake_order,execution_source_sha256='a'*64,
                  chat=CHAT,project=PROJECT,binding_sha256=h,contract_sha256=CONTRACT_SHA,recipe_sha256=digest(raw(RECIPE)),target=str(TARGET))
        # Only in-memory authorization fixture; no permission file issued.
        with patch('pathlib.Path.is_file',return_value=True),patch.object(gateway,'sha',return_value='a'*64):
            gateway.authorize(auth,h,TARGET);checks+=1
            for field in auth:
                bad=dict(auth);bad[field]='invalid'
                rejects(lambda bad=bad:gateway.authorize(bad,h,TARGET));checks+=1
            rejects(lambda:gateway.authorize(dict(auth,execution_order=DEV_ORDER),h,TARGET));checks+=1
        rejects(lambda:engine.run(TARGET,None),'RESEARCH_CAPABILITY');checks+=1
        cfg=dict(chat=CHAT,project=PROJECT,target=str(TARGET),contract_sha256=CONTRACT_SHA,recipe=canonical(RECIPE),limits=LIMITS,files={'fixture':'h'},runtime={'fixture':'runtime'})
        gateway.configuration(cfg,{'fixture':'runtime'},{'fixture':'h'})
        for name in cfg:
            bad=dict(cfg);bad[name]='changed'
            rejects(lambda bad=bad:gateway.configuration(bad,{'fixture':'runtime'},{'fixture':'h'}));checks+=1
        passed.append('C1');details['C1']='missing/mismatched order, mode, chat, project, binding, contract, recipe, target and direct-call gate; source/projection tripwires active'

        # C2: emulate exclusive filesystem writes, never create a consumption file.
        seen=set()
        def once(path,record):
            if str(path) in seen:raise FileExistsError('consumed fixture')
            seen.add(str(path))
        with patch.object(gateway,'exclusive',side_effect=once):
            gateway.consume(PREP/'research.consumed.json',{'fixture':True})
            rejects(lambda:gateway.consume(PREP/'research.consumed.json',{'fixture':True}));checks+=2
        request=dict(nonce='fixture',supervisor_pid=7,binding_sha256=h,authorization=auth)
        marker=dict(nonce='fixture',binding_sha256=h,execution_order=fake_order);gate=dict(pid=8,nonce='fixture')
        gateway.check_lineage(request,gate,marker,8,7);checks+=1
        for badgate,badmarker,pid,parent in [(dict(gate,pid=9),marker,8,7),(dict(gate,nonce='wrong'),marker,8,7),(gate,dict(marker,binding_sha256='wrong'),8,7),(gate,marker,8,6)]:
            rejects(lambda:gateway.check_lineage(request,badgate,badmarker,pid,parent));checks+=1
        with patch.object(gateway,'_ACTIVE',dict(permit='fixture',pid=8)),patch.object(gateway.os,'getpid',return_value=8),patch.object(gateway.os,'getppid',return_value=7),patch.object(gateway.job.win,'worker_membership'),patch.object(gateway,'read',side_effect=lambda p: request if p.name=='request.json' else gate if p.name=='gate.json' else marker),patch.object(Budget,'save',side_effect=lambda n,x:once(n,x)):
            gateway.enter(TARGET,'fixture');rejects(lambda:gateway.enter(TARGET,'fixture'));checks+=2
        passed.append('C2');details['C2']='exclusive mock consumption, missing-completion retry blocked, PID/parent/nonce/binding and second-entry gates'

        # C3: all intervals and future read sentinel.
        for c in CASES:
            for i in range(1,12):
                s,a,b=interval(c,i);need(b-a==4800 and 0<=a<b<=19200,'INTERVAL');checks+=1
            need(interval(c,11)[1:]==(int(c[1:])+9600,int(c[1:])+14400),'HORIZON')
        fake=FakeMaterial();reader=engine.Reader(fake,'A0');reader.take(1);reader.take(2)
        rejects(lambda:reader.take(3),'FUTURE_BEFORE_FREEZE');need(fake.reads==[1,2],'SENTINEL_READ');checks+=1
        reader.freeze(3,dict(target_index=3),{});reader.take(3);need(fake.reads==[1,2,3],'FUTURE_RELEASE');checks+=1
        rejects(lambda:reader.freeze(3,dict(target_index=3),{}),'FREEZE_ORDER');checks+=1
        passed.append('C3');details['C3']='66 interval checks, six full 100-ms target horizons, pre-read future sentinel and replay rejection'

        # C4: golden success + each clause failure and independent implementation.
        archives=sample_archives();result=evaluate.report(archives)
        need(result['verdict']=='ADDITIONAL_BENEFIT_ON_GRID' and len(result['individual'])==30,'GOLDEN_SUCCESS')
        need({k:result[k] for k in ('verdict','criteria','means')}==audit.independent_verdict(archives),'INDEPENDENT_GOLDEN');checks+=2
        audit.check_metrics(archives,result);checks+=1
        wrong=copy.deepcopy(result);wrong['individual'][0]['N']['context_error']=99.
        rejects(lambda:audit.check_metrics(archives,wrong),'INDEPENDENT_METRIC');checks+=1
        for case,change in [('A480','missing'),('A2400','position'),('A480','factor'),('A0','origin'),('A480','successor')]:
            data=copy.deepcopy(archives);r=data[case+'-T']['records'][-1];p=json.loads(r['forecast']['provenance_json'])
            if change in ('missing','successor'):r['forecast']['context_values']=None
            elif change=='position':p['alignment']['matches'][0][1]=2
            elif change=='factor':p['alignment']['matches'][0][2]=[2.]
            else:p['matches'][0]['ordinals']=[5,6,7,8]
            r['forecast']['provenance_json']=json.dumps(p);x=evaluate.report(data)
            need(x['verdict']=='NO_ADDITIONAL_BENEFIT','GOLDEN_FAILURE:'+change)
            need({k:x[k] for k in ('verdict','criteria','means')}==audit.independent_verdict(data),'INDEPENDENT_FAILURE');checks+=2
        data=copy.deepcopy(archives);data['A480-N']=copy.deepcopy(data['A480-T']);need(not evaluate.report(data)['criteria']['S1'],'N_ALREADY_CORRECT');checks+=1
        data=copy.deepcopy(archives);data['B0-T']['records'][-1]['forecast']=copy.deepcopy(archives['A0-T']['records'][-1]['forecast'])
        need(not evaluate.report(data)['criteria']['S2'],'FOREIGN');checks+=1
        main=copy.deepcopy(result['main'])
        for c in CASES:main[c]['T']['error']=main[c]['N']['error']
        need(not evaluate.decide(main,[])['criteria']['S4'],'STRICT_EQUALITY');checks+=1
        tiny=math.nextafter(1.,0.)
        for c in CASES:main[c]['N']['error']=1.;main[c]['N']['p_error']=1.;main[c]['T']['error']=tiny
        need(evaluate.decide(main,[])['criteria']['S4'],'NO_ROUNDING');checks+=1
        m=evaluate.metrics('B0',synthetic('B0','N'));need(m['context_error'] is None and m['error']==1.,'NO_CONTEXT_ZERO');checks+=1
        data=copy.deepcopy(archives);data['B0-T']['records'][-1]['forecast']['persistence_values']=v(2)
        # Paired P must remain identical; a mismatched baseline is technical.
        rejects(lambda:evaluate.report(data),'P_PAIR_EQUAL');checks+=1
        passed.append('C4');details['C4']='golden S1-S4, both shifts, origin/position/factor/successor losses, N already correct, foreign retrieval, equality/nextafter, missing context, independent judge'

        # C5: all nine comparisons plus precedence and state equality condition.
        data=copy.deepcopy(archives);a=data['A0-T']['records'][-1];b=data['B480-T']['records'][-1];b['hint']=copy.deepcopy(a['hint'])
        x=evaluate.report(data);need(len(x['collisions'])==9 and x['verdict']=='IDENTIFIABILITY_LIMIT','COLLISION_EQUAL_TARGET');checks+=1
        b['actual']=v(.25);data['B480-N']['records'][-1]['actual']=v(.25)
        need(evaluate.report(data)['verdict']=='IDENTIFIABILITY_LIMIT','COLLISION_DIFFERENT_TARGET');checks+=1
        b['stock_fingerprint']='different';need(not any(z['collision'] for z in evaluate.report(data)['collisions']),'DIFFERENT_STOCK');checks+=1
        need(evaluate.decide({},[],technical=True)['verdict']=='TECHNICAL_FAILURE','TECHNICAL_FIRST');checks+=1
        p=json.loads(synthetic('A480','T')['forecast']['provenance_json']);p['alignment']['matches'].append([0,2,[1.]])
        need(evaluate.identity(p) is None,'POSITION_AMBIGUITY');checks+=1
        passed.append('C5');details['C5']='nine collision pairs, equal/different targets, distinct stock, positional ambiguity, technical precedence'

        # C6: two small 11-input synthetic adapters, never material.prepare/full run.
        material=FakeMaterial();ledger=FakeLedger();n=engine.run_arm('A0',False,material,ledger);t=engine.run_arm('A0',True,material,ledger)
        need(n['states']==t['states'] and n['cleanup'] and t['cleanup'],'MINI_STATES_CLEANUP')
        need(ledger.counts['policy_admissions']==22 and ledger.counts['reference_admissions']==22 and ledger.counts['decisions']==10,'MINI_COUNTS')
        for arm,data in [('N',n),('T',t)]:
            for record in data['records']:audit.check_record('A0',arm,record,material.row);checks+=1
        tamper=copy.deepcopy(t['records'][-1]);tamper['forecast']['context_values']=v(99)
        rejects(lambda:audit.check_record('A0','T',tamper,material.row),'OUTPUT_ORACLE');checks+=1
        tamper=copy.deepcopy(t['records'][-1]);tamper['freeze_token']='wrong'
        rejects(lambda:audit.check_record('A0','T',tamper,material.row),'FREEZE_DIGEST');checks+=1
        # Full archive shape is mock I/O assembled from the two small adapters;
        # it executes neither twelve arms nor material generation/projection.
        from io import BytesIO
        archive={};manifest=dict(projections={},sources={s:dict(bytes=76800,sha256=digest(bytes(76800))) for s in ('A','B')},recipe_sha256=digest(raw(RECIPE)))
        for c in CASES:
            names=[key(c,i) for i in range(1,12)]+[f'{c}-bank-{b}-{k}' for b in (0,1) for k in range(31) if k%10]
            for name in names:
                row=material.row(name);_,kind,*tail=name.split('-')
                if kind=='base':s,a,b=interval(c,int(tail[0]))
                else:bl,k=map(int,tail);s='A';a=k*480;b=a+4800
                row.update(source=s,source_interval=[a,b],end=row['start']+4800,source_sha256=digest(bytes(76800)))
                archive['material/'+name+'.json']=row;manifest['projections'][name]=dict(bytes=len(raw(row)),sha256=digest(raw(row)))
            for arm,data in [('N',n),('T',t)]:archive['observer/'+c+'-'+arm+'.json']=data
        archive['material/manifest.json']=manifest;archive['material/recipe.json']=canonical(RECIPE)
        fake_root=Path(folder)/'mock-archive'
        def mockread(path):return copy.deepcopy(archive[Path(path).relative_to(fake_root).as_posix()])
        def mockinfo(path):
            rel=Path(path).relative_to(fake_root).as_posix()
            if rel.endswith('.f32le'):return dict(bytes=76800,sha256=digest(bytes(76800)))
            value=archive[rel];return dict(bytes=len(raw(value)),sha256=digest(raw(value)))
        with patch.object(audit,'read',side_effect=mockread),patch.object(audit,'info',side_effect=mockinfo),patch.object(audit,'sha',return_value=digest(raw(RECIPE))),patch('pathlib.Path.open',return_value=BytesIO(bytes(76800))) as opened:
            # Fresh stream per read, since each with-block closes it.
            opened.side_effect=lambda *args,**kwargs:BytesIO(bytes(76800))
            reconstructed=audit.reconstruct(fake_root)
            evaluation=evaluate.report(reconstructed)
            need({k:evaluation[k] for k in ('verdict','criteria','means')}==audit.independent_verdict(reconstructed),'FULL_MOCK_ARCHIVE_JUDGE');checks+=1
            audit.check_metrics(reconstructed,evaluation);checks+=1
            archive['observer/A0-T.json']=dict(t,cleanup=False)
            rejects(lambda:audit.reconstruct(fake_root),'ARM_COMPLETE');checks+=1
        with patch('experiments.rw1.common.total_size',return_value=0),patch('experiments.rw1.common.size',return_value=0):
            b=Budget(TARGET)
            for group in ('material','observer','closure'):
                b.check(group+'/x',LIMITS[group]);rejects(lambda group=group:b.check(group+'/x',LIMITS[group]+1));checks+=2
            rejects(lambda:b.check('../outside',1),'OUTPUT_SCOPE');checks+=1
        with patch('experiments.rw1.common.total_size',return_value=LIMITS['export']),patch('experiments.rw1.common.size',return_value=0):
            rejects(lambda:Budget(TARGET).check('observer/x',1),'TOTAL_EXPORT');checks+=1
        budget=Budget(Path(folder)/'fixture-evidence');budget.save('mini-adapters.json',dict(N=n,T=t,counts=ledger.counts))
        budget.save('golden-evaluation.json',result)
        passed.append('C6');details['C6']='22+22 synthetic admissions, 10 independently reconstructed decisions, N/T states+bank hashes, cleanup, tampered forecast/freeze, partition and total bounds'
    need(not (PREP/'research.consumed.json').exists() and not (PREP/'research-authorization.json').exists() and not TARGET.exists(),'RESEARCH_UNTOUCHED')
    return dict(passed=True,groups=passed,checks=checks,details=details,scope=dict(rw1_pcm=0,receptor=0,nj=0,neutral_full=0,research_full=0,
        artificial_policy_admissions=22,artificial_reference_admissions=22,artificial_decisions=10),authorization='NOT_ISSUED_NOT_CONSUMED')
