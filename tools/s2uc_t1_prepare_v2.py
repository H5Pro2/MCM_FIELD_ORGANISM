"""Separately authorized T1 envelope. Qualification uses neutral sources only."""
import argparse
import base64
import io
import json
import math
import struct
import sys
import time
import unittest
from pathlib import Path
from types import FunctionType
from tools import s2uc_repeat_prepare_v4 as q
from tools import _s2uc_t1_source as source
from tools import _s2uc_t1_assessment_v2 as assessment

ROOT=q.ROOT
PREFIX='S2UC_T1_V2_'
PLAN=ROOT/'docs'/f'{PREFIX}PLAN_20261003.json'
BINDING=ROOT/'docs'/f'{PREFIX}BINDUNG_20261003.json'
INDEX=ROOT/'docs'/f'{PREFIX}HERKUNFTSINDEX_20261003.json'
TEMPLATE=ROOT/'docs'/f'{PREFIX}AUTORISIERUNG_VORLAGE_20261003.json'
GUIDE=ROOT/'docs'/f'{PREFIX}AUFRUF_20261003.txt'
CONTRACT=ROOT/'docs/S2UC_TRANSFERPRUEFVERTRAG_T1_20261003.txt'
CLARIFICATION=ROOT/'docs/S2UC_T1_PRAEZISIERUNG_20261003.txt'
QUAL=ROOT/'reports/s2uc/t1-neutral-qualification-20261003-02'
NEUTRAL=QUAL/'integration'
OUT=ROOT/'reports/s2uc/t1-transfer-20261003-01'
STATUS='SYNTHETIC_TRANSFER_VECTOR_BOUNDARY_ONLY'
FILES=('tools/_s2uc_t1_source.py','tools/_s2uc_t1_evidence_v2.py','tools/_s2uc_t1_assessment_v2.py',
       'tools/s2uc_t1_prepare_v2.py','tests/test_s2uc_t1_v2.py')
supervise=FunctionType(q.supervise.__code__,dict(q.supervise.__globals__,STATUS=STATUS),
    'supervise',q.supervise.__defaults__)


def plan():
    return dict(cases=source.cases(),arms=list(q.old.ARMS),source_positions=1280,arm_admissions=6400,
        reference_advances=6400,transitions=52,negative_controls=20,late_window='FIXED_TARGETS_NOT_ASSUMED_WARM',
        limits=q.old.plan()['policy_limits'],file_caps=q.old.plan()['file_caps'],
        total_seconds=3600,worker_seconds=3540,closure_seconds=60,export_bytes=64*1048576,
        preparation_bytes=8*1048576,closure_reserve=1048576,
        criteria=dict(recognition_cases=4,recognition_groups=2,adaptation=26,adaptation_denominator=52,
            per_group=4,per_group_denominator=13,G='STRICT_EACH_BASELINE',late='NO_WORSE_EACH_BASELINE',damage='1/32'),
        qualification=dict(namespace=source.NEUTRAL,replays=10,seconds=900,bytes=16*1048576),
        evidence_status=STATUS,audio_video_chain=False,status='PENDING_SEPARATE_AUTHORIZATION')


def encode(values):
    return dict(encoding='FLOAT64_LE_BASE64',frames=len(values),width=48,
        data=base64.b64encode(struct.pack('<'+'d'*(48*len(values)),*(x for v in values for x in v))).decode('ascii'))


def decode(record):
    n=record['frames']
    if record['encoding']!='FLOAT64_LE_BASE64' or record['width']!=48 or type(n) is not int or not 4<=n<=80 or n%2:
        raise ValueError('SOURCE_ENCODING')
    raw=base64.b64decode(record['data'],validate=True)
    if len(raw)!=n*48*8:raise ValueError('SOURCE_BYTES')
    values=struct.unpack('<'+'d'*(n*48),raw)
    if not all(math.isfinite(x) for x in values):raise ValueError('SOURCE_FINITE')
    return [list(values[i*48:(i+1)*48]) for i in range(n)]


def restore(values,provenance):
    b=provenance|dict(values=values,modal=[])
    for i,mode in enumerate(b['modes']):
        state=None if i==0 or mode=='I' else (b['states'][i-1]+(1 if mode=='C' else -1 if mode=='R' else 0))%8
        b['modal'].append(None if state is None else b['library'][b['banks'][i]][state])
    return b


def fingerprints(values):
    return {str(n):sorted({q.old.digest(values[i:i+n]) for i in range(len(values)-n+1)}) for n in (1,2,4)}


def history_index():
    entries=[];unions={str(n):set() for n in (1,2,4)}
    for p in sorted((ROOT/'reports/s2uc').glob('*/*source*.json')):
        raw=q.old.read(p)
        v=(decode(raw) if isinstance(raw,dict) and raw.get('encoding')=='FLOAT64_LE_BASE64'
           else raw.get('values') if isinstance(raw,dict) else raw)
        if not isinstance(v,list) or not v or not all(isinstance(x,list) and len(x)==48 and
            all(type(y) is float for y in x) for x in v):continue
        fp=fingerprints(v)
        for k,hs in fp.items():unions[k].update(hs)
        entries.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=q.old.sha(p),profile=q.old.digest(v),frames=len(v)))
    return dict(entries=entries,fingerprints={k:sorted(v) for k,v in unions.items()},
        scope='Saved top-level reports/s2uc/*/*source*.json numeric48 arrays and FLOAT64_LE_BASE64; plus separately sealed neutral qualification index; not all human or external trials',
        no_policy_scores_used=True,no_case_replacement=True)


def overlaps(values,index):
    fp=fingerprints(values)
    return dict(profile=q.old.digest(values),full_matches=[e['path'] for e in index['entries'] if e['profile']==q.old.digest(values)],
        shared={k:sorted(set(v)&set(index['fingerprints'][k])) for k,v in fp.items()})


def prepare():
    if any(p.exists() for p in (OUT,QUAL,BINDING)):raise RuntimeError('PREPARATION_USED')
    q.preparation_check();prior=q.verify()
    q.old.save(PLAN,plan());q.old.save(INDEX,history_index())
    paths=[CONTRACT,CLARIFICATION,GUIDE,INDEX,q.BINDING,q.PLAN,q.GUIDE,q.QUAL/'closure.json',
        ROOT/'docs/S2UC_T1_V1_BINDUNG_20261003.json',ROOT/'reports/s2uc/t1-neutral-qualification-20261003-01/closure.json']
    refs=dict(prior['references'])
    refs.update({p.relative_to(ROOT).as_posix():q.old.sha(p) for p in paths})
    q.old.save(BINDING,dict(code=prior['code']|{n:q.old.sha(ROOT/n) for n in FILES},references=refs,
        plan_sha256=q.old.sha(PLAN),python=sys.version,executable_sha256=q.old.sha(sys.executable)))


def verify():
    b=q.old.read(BINDING)
    if sys.flags.optimize or b['python']!=sys.version or b['executable_sha256']!=q.old.sha(sys.executable):raise RuntimeError('RUNTIME_BINDING')
    if q.old.read(PLAN)!=json.loads(json.dumps(plan())) or b['plan_sha256']!=q.old.sha(PLAN):raise RuntimeError('PLAN_BINDING')
    for n,h in (b['code']|b['references']).items():
        if q.old.sha(ROOT/n)!=h:raise RuntimeError('BINDING:'+n)
    return b


def authorization(status):
    return dict(status=status,action='T1_MATERIALIZE_AND_RUN_ONCE',binding_sha256=q.old.sha(BINDING),
        plan_sha256=q.old.sha(PLAN),qualification_sha256=q.old.sha(QUAL/'closure.json'),
        output=OUT.relative_to(ROOT).as_posix(),cases=16,source_positions=1280,arms=list(q.old.ARMS),
        admissions=6400,reference_advances=6400,total_seconds=3600,evidence_status=STATUS)


def preparation_check():
    verify();c=q.old.read(QUAL/'closure.json')
    if c['status']!='PASS':raise RuntimeError('QUALIFICATION_REQUIRED')
    for n,v in c['files'].items():
        if q.old.sha(QUAL/n)!=v['sha256']:raise RuntimeError('QUALIFICATION_CHANGED')


def charged_bytes(auth):
    b=verify();paths={ROOT/n for n in b['code']|b['references']}
    paths.update((PLAN,BINDING,TEMPLATE,Path(auth)))
    paths.update(p for p in QUAL.rglob('*') if p.is_file())
    total=sum(p.stat().st_size for p in paths)
    if total>8*1048576:raise RuntimeError('PREPARATION_REFERENCE_CAP')
    return total


def execute(folder,specs,namespace,charged,check,*,authorized=False,neutral=False):
    ledger=q.old.Ledger(folder,charged,claimed=True);entries=[];reports=[];times=[];active=None;partial={}
    begin=time.perf_counter_ns()
    index=dict(entries=[],fingerprints={str(n):[] for n in (1,2,4)}) if neutral else q.old.read(INDEX)
    if not neutral:
        extra=q.old.read(QUAL/'neutral-source-index.json')
        index['entries']+=extra['entries']
        for k,v in extra['fingerprints'].items():index['fingerprints'][k]=sorted(set(index['fingerprints'][k])|set(v))
    try:
        # ALL sources and their provenance sealed before ANY policy call.
        for s in specs:
            check();b=source.generate(s,namespace=namespace,authorized=authorized)
            record=encode(b['values']);provenance={k:v for k,v in b.items() if k not in ('values','modal')}
            if restore(decode(record),provenance)!=b:raise RuntimeError('LOSSLESS_SOURCE')
            stem=s['id'];ledger.write(stem+'-source.json',record);ledger.write(stem+'-provenance.json',provenance)
            entries.append(dict(id=stem,spec=s,source_file=stem+'-source.json',source_sha256=q.old.sha(Path(folder)/(stem+'-source.json')),
                provenance_file=stem+'-provenance.json',provenance_sha256=q.old.sha(Path(folder)/(stem+'-provenance.json')),
                **overlaps(b['values'],index)))
            del b,record,provenance
        ledger.write('manifest.json',dict(entries=entries,sealed_at=q.old.utc(),all_sources_before_policy=True,scope=STATUS))
        mh=q.old.sha(Path(folder)/'manifest.json');source_seconds=(time.perf_counter_ns()-begin)/1e9
        assessment_ns=export_ns=0
        for s,e in zip(specs,entries):
            check()
            if any(q.old.sha(Path(folder)/e[k+'_file'])!=e[k+'_sha256'] for k in ('source','provenance')):raise RuntimeError('SOURCE_TAMPER')
            b=restore(decode(q.old.read(Path(folder)/e['source_file'])),q.old.read(Path(folder)/e['provenance_file']))
            results={}
            for arm in q.old.ARMS:
                check();active=dict(case=s['id'],arm=arm);partial={}
                ledger.write(s['id']+'-'+arm+'-start.json',dict(**active,started_at=q.old.utc(),manifest_sha256=mh))
                start=time.perf_counter_ns();cpu=time.process_time_ns()
                if arm=='U':r=q.old.multi_replay(b['values'],e['profile'],count=s['frames'],evidence=partial,check=check)
                else:r=q.integrated_baseline(b['values'],e['profile'],count=s['frames'],arm=arm,evidence=partial,check=check)
                times.append(dict(**active,wall_ns=time.perf_counter_ns()-start,cpu_ns=time.process_time_ns()-cpu))
                q.old.resource_check(r);check();t=time.perf_counter_ns()
                ledger.write(s['id']+'-'+arm+'.json',r);export_ns+=time.perf_counter_ns()-t
                results[arm]=r;partial={};active=None
            t=time.perf_counter_ns();report=assessment.assess_case(results,b,s);assessment_ns+=time.perf_counter_ns()-t
            ledger.write(s['id']+'-assessment.json',report);reports.append(report)
            if report['technical_errors']:raise RuntimeError('INVALID_CASE_EVIDENCE:'+str(report['technical_errors']))
            del results,b,r
        result=(dict(technical_errors=[],neutral_only=True,scope=STATUS) if neutral else assessment.aggregate(reports,specs))
        result['all_sources_unseen_in_bound_index']=not any(e['full_matches'] for e in entries)
        result['unseen_claim_scope']=index.get('scope','NEUTRAL_ONLY')
        ledger.write('assessment.json',result)
        if result['technical_errors']:raise RuntimeError('INVALID_AGGREGATE')
        ledger.write('phase-times.json',dict(replays=times,source_seconds=source_seconds,
            case_assessment_seconds=assessment_ns/1e9,arm_export_seconds=export_ns/1e9,
            engine_seconds=(time.perf_counter_ns()-begin)/1e9))
        check();ledger.write('worker-complete.json',dict(cases=len(specs),admissions=sum(s['frames'] for s in specs)*5,
            reference_advances=sum(s['frames'] for s in specs)*5,namespace=namespace))
    except BaseException as exc:
        emergency=q.old.Ledger(folder,charged,claimed=True);emergency.LIMIT-=q.old.RESERVE//2
        record=dict(active=active,evidence=partial,error=type(exc).__name__+':'+str(exc))
        if len(json.dumps(record,separators=(',',':')).encode())>q.old.RESERVE//2:
            record=dict(active=active,error=record['error'],evidence_omitted='PARTIAL_OVER_HALF_RESERVE')
        emergency.write('partial.json',record,final=True)
        raise


def worker(folder,charged,deadline):
    def check():
        if time.monotonic_ns()>=deadline:raise TimeoutError('WORKER_DEADLINE')
    check();verify()
    if Path(folder)==NEUTRAL:
        specs=[source.specification('neutral-hold',201,'QH',((80,'H',0),)),
            source.specification('neutral-change',202,'QC',((24,'C',0),(16,'R',0),(8,'I',1),(32,'C',1)))]
        namespace=source.NEUTRAL;authorized=False;neutral=True
    elif Path(folder)==OUT:
        a=q.old.read(Path(folder)/'claim.json')['binding']['authorization']
        q.validate_authorization(a,authorization('AUTHORIZED_ONCE'))
        specs=source.cases();namespace=source.EVALUATION;authorized=True;neutral=False
    else:raise RuntimeError('UNKNOWN_DESTINATION')
    execute(folder,specs,namespace,charged,check,authorized=authorized,neutral=neutral)
    check();verify();check()


def run(path):
    preparation_check();a=q.old.read(Path(path));q.validate_authorization(a,authorization('AUTHORIZED_ONCE'))
    supervise(OUT,charged_bytes(path),worker,metadata=dict(authorization=a,binding_sha256=q.old.sha(BINDING)))


def qualify():
    verify();QUAL.mkdir(exist_ok=False);start=time.monotonic();error=None
    try:
        suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromName('tests.test_s2uc_t1_v2.'+name)
            for name in ('StaticTests','BoundaryTests')])
        def ids(s):
            for x in s:
                if isinstance(x,unittest.TestSuite):yield from ids(x)
                else:yield x.id()
        names=list(ids(suite));out=io.StringIO();r=unittest.TextTestRunner(stream=out,verbosity=2).run(suite)
        q.old.save(QUAL/'tests.json',dict(ids=names,count=r.testsRun,success=r.wasSuccessful(),failures=len(r.failures),
            errors=len(r.errors),skips=len(r.skipped),output=out.getvalue()))
        if not r.wasSuccessful() or r.skipped:raise RuntimeError('NEUTRAL_TESTS')
        supervise(NEUTRAL,q.old.LIMIT-15*1048576,worker,900-(time.monotonic()-start),60,metadata=dict(binding_sha256=q.old.sha(BINDING)))
        suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_s2uc_t1_v2.EvidenceTests')
        names=list(ids(suite));out=io.StringIO();r=unittest.TextTestRunner(stream=out,verbosity=2).run(suite)
        q.old.save(QUAL/'evidence-tests.json',dict(ids=names,count=r.testsRun,success=r.wasSuccessful(),failures=len(r.failures),
            errors=len(r.errors),skips=len(r.skipped),output=out.getvalue()))
        if not r.wasSuccessful() or r.skipped:raise RuntimeError('EVIDENCE_TESTS')
        neutral_index=dict(entries=[],fingerprints={str(n):set() for n in (1,2,4)})
        for path in NEUTRAL.glob('*-source.json'):
            values=decode(q.old.read(path));fp=fingerprints(values)
            neutral_index['entries'].append(dict(path=path.relative_to(ROOT).as_posix(),sha256=q.old.sha(path),profile=q.old.digest(values)))
            for k,v in fp.items():neutral_index['fingerprints'][k].update(v)
        neutral_index['fingerprints']={k:sorted(v) for k,v in neutral_index['fingerprints'].items()}
        q.old.save(QUAL/'neutral-source-index.json',neutral_index)
        verify()
        phase=q.old.read(NEUTRAL/'phase-times.json')
        baseline=16*sum(max(x['wall_ns']/1e9 for x in phase['replays'] if x['arm']==a) for a in ('M','E','K','P'))*1.25
        q.old.save(QUAL/'time-plan.json',dict(baseline_seconds=baseline,administration=180,U=30,closure=60,total_seconds=baseline+270,
            reserve=3600-baseline-270,limit=3600,assumption='16 times neutral80 maximum per baseline plus25percent; no guarantee of T1 competition',
            raw_matrix_seconds=phase['engine_seconds']))
        if sum(p.stat().st_size for p in QUAL.rglob('*') if p.is_file())>16*1048576:raise RuntimeError('QUALIFICATION_EXPORT_LIMIT')
    except BaseException as exc:error=type(exc).__name__+':'+str(exc);raise
    finally:
        q.old.save(QUAL/'closure.json',dict(status='PASS' if error is None else 'FAILED',error=error,
            files={p.relative_to(QUAL).as_posix():dict(bytes=p.stat().st_size,sha256=q.old.sha(p)) for p in QUAL.rglob('*') if p.is_file()},
            evaluation_sources_generated=False,evaluation_replays=0,duration_seconds=time.monotonic()-start))
    q.old.save(TEMPLATE,authorization('PENDING_SEPARATE_AUTHORIZATION'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=('prepare','qualify','run'));p.add_argument('--authorization');a=p.parse_args()
    if a.action=='prepare':prepare()
    elif a.action=='qualify':qualify()
    elif not a.authorization:p.error('--authorization required')
    else:run(a.authorization)
