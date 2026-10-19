"""Separate technical-repeat preparation. No raster generation during qualify."""
import argparse
from collections import defaultdict
from datetime import datetime,timezone,timedelta
import io
import json
import multiprocessing
from pathlib import Path
import sys
import time
from types import FunctionType
import unittest
from unittest.mock import patch
from tools import s2uc_eval_prepare as old
from tools import s2uc_frame_leaf_qualify as leaf
from tools._s2uc_sample_leaf_observer_v1 import SampleLeafBudgetObserver
from tools import s2uc_repeat_prepare_v2 as v2
from tools import s2uc_sample_leaf_qualify as sample
from tools.s2uc_context_prediction_check import BudgetObserver

ROOT=old.ROOT
PREFIX='S2UC_TECHNISCHE_WIEDERHOLUNG_V3_'
PLAN=ROOT/'docs'/f'{PREFIX}PLAN_20261003.json'
BINDING=ROOT/'docs'/f'{PREFIX}BINDUNG_20261003.json'
TEMPLATE=ROOT/'docs'/f'{PREFIX}AUTORISIERUNG_VORLAGE_20261003.json'
GUIDE=ROOT/'docs'/f'{PREFIX}AUFRUF_20261003.txt'
QUAL=ROOT/'reports/s2uc/technical-repeat-preparation-20261003-03'
PREVIOUS_QUAL=ROOT/'reports/s2uc/technical-repeat-preparation-20261003-01'
OUT=ROOT/'reports/s2uc/technical-repeat-20261003-01'
NEW=('tools/s2uc_repeat_prepare_v3.py','tests/test_s2uc_repeat_prepare_v3.py')
STATUS='KNOWN_DATA_TECHNICAL_REPEAT_NOT_UNTOUCHED_EVALUATION'
TOTAL_SECONDS=3600
CLOSURE_SECONDS=60
NEUTRAL=QUAL/'integration'
QUAL_LIMIT=16*1048576
QUAL_PARENT_RESERVE=1048576


def stamp(event):return dict(event=event,monotonic_ns=time.monotonic_ns(),utc=datetime.now(timezone.utc).isoformat())


def plan():
    p=old.plan()
    p.update(status='PENDING_SEPARATE_AUTHORIZATION',output=OUT.relative_to(ROOT).as_posix(),
        evidence_status=STATUS,merge_with_old_run=False,worker_seconds=3540,closure_seconds=60,
        integration=dict(cases=['N1','N2'],frames=80,arms=list(old.ARMS),replays=10,
            admissions=800,reference_advances=800,seconds=900,bytes=16*1048576),
        old_run_closed=True,time_reserve_demonstrated=False)
    return p


def references():
    paths=[v2.PLAN,v2.BINDING,v2.GUIDE,v2.TEMPLATE,sample.PLAN,sample.BINDING,
        sample.REPORT/'closure.json',sample.REPORT/'analysis.json',sample.REPORT/'tests.json',
        sample.REPORT/'test-facts.json',sample.REPORT/'verification.json',
        ROOT/'reports/s2uc/runtime-reconciliation-20261003-01/analysis.json']
    paths.extend(p for p in v2.QUAL.rglob('*') if p.is_file())
    paths.extend(p for p in sample.OUT.rglob('*') if p.is_file())
    refs=dict(v2.verify()['references'])
    refs.update({p.relative_to(ROOT).as_posix():old.sha(p) for p in paths})
    return refs


def prepare():
    if OUT.exists() or QUAL.exists():raise RuntimeError('PREPARATION_ALREADY_USED')
    sample.verify();v2.preparation_check()
    closure=old.read(sample.REPORT/'closure.json')
    if closure['status']!='PASS':raise RuntimeError('SAMPLE_NOT_QUALIFIED')
    for n,v in closure['files'].items():
        if old.sha(sample.REPORT/n)!=v['sha256']:raise RuntimeError('SAMPLE_EVIDENCE_CHANGED')
    for n,v in old.read(sample.REPORT/'verification.json')['files'].items():
        if old.sha(sample.OUT/n)!=v['sha256']:raise RuntimeError('SAMPLE_MATRIX_CHANGED')
    codes=dict(v2.verify()['code'])
    for n in (*sample.FILES,*NEW):codes[n]=old.sha(ROOT/n)
    old.save(PLAN,plan())
    old.save(BINDING,dict(code=codes,references=references(),plan_sha256=old.sha(PLAN),
        guide_sha256=old.sha(GUIDE),python=sys.version,executable_sha256=old.sha(sys.executable)))


def verify():
    b=old.read(BINDING)
    if sys.flags.optimize or b['python']!=sys.version or b['executable_sha256']!=old.sha(sys.executable):raise RuntimeError('RUNTIME_BINDING')
    if old.read(PLAN)!=json.loads(json.dumps(plan())) or b['plan_sha256']!=old.sha(PLAN):raise RuntimeError('PLAN_BINDING')
    if b['guide_sha256']!=old.sha(GUIDE):raise RuntimeError('GUIDE_BINDING')
    for n,h in (b['code']|b['references']).items():
        if old.sha(ROOT/n)!=h:raise RuntimeError('BINDING:'+n)
    return b


def integrated_baseline(*args,**kwargs):
    with patch.object(BudgetObserver,'trace',SampleLeafBudgetObserver.trace):
        return old.baseline_replay(*args,**kwargs)


def execute(folder,specs,supplier,validator,registry,charged,check,*,summarize=old.aggregate):
    # Frozen engine bytecode; same wrappers for neutral and future real worker.
    times=defaultdict(int);cpus=defaultdict(int);counts=defaultdict(int);replays=[]
    def timed(name,fn):
        def call(*args,**kwargs):
            t=time.perf_counter_ns();c=time.process_time_ns()
            try:return fn(*args,**kwargs)
            finally:
                wall=time.perf_counter_ns()-t;cpu=time.process_time_ns()-c
                times[name]+=wall;cpus[name]+=cpu;counts[name]+=1
                if name in ('baseline_replay','U_replay'):
                    replays.append(dict(case=specs[len(replays)//5]['id'],arm=kwargs.get('arm','U'),
                        wall_ns=wall,cpu_ns=cpu))
        return call
    class TimedLedger(old.Ledger):
        def write(self,*args,**kwargs):return timed('export',super().write)(*args,**kwargs)
    def provenance(values,spec,index):
        e=old.manifest_entry(values,spec,index)
        e.update(novelty=STATUS,evidence_status=STATUS)
        return e
    def summary(reports,specs):
        r=summarize(reports,specs);r.update(evidence_status=STATUS,scope=STATUS,merge_with_old_run=False)
        return r
    ns=dict(old.execute.__globals__)
    ns.update(Ledger=TimedLedger,baseline_replay=timed('baseline_replay',integrated_baseline),
        multi_replay=timed('U_replay',old.multi_replay),resource_check=timed('resource_check',old.resource_check),
        manifest_entry=timed('manifest',provenance),read=timed('source_read',old.read),sha=timed('source_hash',old.sha))
    engine=FunctionType(old.execute.__code__,ns,old.execute.__name__,old.execute.__defaults__)
    engine.__kwdefaults__=old.execute.__kwdefaults__
    t=time.perf_counter_ns();c=time.process_time_ns()
    try:
        return engine(folder,specs,timed('materialization',supplier),timed('source_validation',validator),registry,charged,check,
            assess=timed('case_assessment',old.assess_case),summarize=timed('aggregation',summary))
    finally:
        old.Ledger(folder,charged,claimed=True).write('phase-times.json',dict(wall_ns=dict(times),cpu_ns=dict(cpus),
            calls=dict(counts),replays=replays,engine_wall_ns=time.perf_counter_ns()-t,
            engine_cpu_ns=time.process_time_ns()-c,exclusive_categories=True,
            phase_times_file_export_in_worker_overhead=True))


def supervise(folder,charged,target,seconds=TOTAL_SECONDS,closure_seconds=CLOSURE_SECONDS,metadata=None):
    if not 0<closure_seconds<seconds:raise ValueError('DEADLINE_SPLIT')
    start=stamp('deadline_established');total=start['monotonic_ns']+int(seconds*1e9)
    deadline=total-int(closure_seconds*1e9)
    start.update(total_deadline_ns=total,worker_deadline_ns=deadline,
        total_deadline_utc=(datetime.fromisoformat(start['utc'])+timedelta(seconds=seconds)).isoformat(),
        worker_deadline_utc=(datetime.fromisoformat(start['utc'])+timedelta(seconds=seconds-closure_seconds)).isoformat())
    ledger=old.Ledger(folder,charged)  # atomic exclusive directory claim
    journal=Path(folder)/'lifecycle.jsonl'
    def event(e):
        raw=(json.dumps(e,sort_keys=True,separators=(',',':'))+'\n').encode()
        if journal.stat().st_size+len(raw)>16384:raise RuntimeError('LIFECYCLE_CAP')
        with journal.open('ab') as out:out.write(raw)
    with journal.open('xb') as f:pass
    event(start)
    ledger.write('claim.json',dict(status='CLAIMED_ONCE',evidence_status=STATUS,binding=metadata))
    proc=None;error=None;exitcode=None
    try:
        proc=multiprocessing.get_context('spawn').Process(target=target,args=(str(folder),charged,deadline))
        proc.start()
        while proc.is_alive():
            remaining=(deadline-time.monotonic_ns())/1e9
            if remaining<=0:break
            proc.join(remaining)
        if proc.is_alive():
            error='TIME_LIMIT';event(stamp('abort_requested'));proc.terminate();proc.join(5)
            if proc.is_alive():event(stamp('kill_requested'));proc.kill();proc.join()
        exitcode=proc.exitcode
        event(stamp('worker_end_confirmed')|dict(exitcode=exitcode,alive=proc.is_alive()))
        if exitcode!=0:error=error or 'WORKER_EXIT:'+str(exitcode)
        if not (Path(folder)/'worker-complete.json').exists():error=error or 'MISSING_COMPLETION'
        if time.monotonic_ns()>deadline:error=error or 'TIME_LIMIT'
    except BaseException as exc:
        error=type(exc).__name__+':'+str(exc)
        if proc is not None and proc.is_alive():
            event(stamp('abort_requested'));proc.terminate();proc.join()
            event(stamp('worker_end_confirmed')|dict(exitcode=proc.exitcode,alive=False))
    finally:
        event(stamp('closure_admin_started'))
        if proc is not None:proc.close()
        files={p.name:dict(bytes=p.stat().st_size,sha256=old.sha(p)) for p in Path(folder).iterdir()
            if p.is_file() and p.name!='lifecycle.jsonl'}
        closing=old.Ledger(folder,charged,claimed=True)
        # Keep space for the terminal lifecycle record outside closure.json.
        closing.LIMIT-=16384
        closing.write('closure.json',dict(status='COMPLETE' if error is None else 'FAILED',error=error,
            files=files,evidence_status=STATUS,merge_with_old_run=False,resume_permitted=False,
            charged_previous_bytes=charged,worker_deadline_ns=deadline,total_deadline_ns=total,
            lifecycle_journal='lifecycle.jsonl',historical_worker_stop='UNKNOWN',
            lifecycle_terminal_write_excluded_from_its_own_timestamp=True),final=True)
        closure_hash=old.sha(Path(folder)/'closure.json')
        finish=stamp('closure_admin_finished')
        finish.update(total_deadline_met=finish['monotonic_ns']<=total,closure_file_sha256=closure_hash)
        event(finish)
    if error:raise RuntimeError(error)
    if not finish['total_deadline_met']:raise RuntimeError('TOTAL_TIME_LIMIT')


def known_registry():
    r=old.read(old.INDEX)
    r['entries']+= [dict(path=str(old.OUT.relative_to(ROOT)/e['source_file']),profile=e['profile'],blocks=[],prefixes={})
        for e in old.read(old.OUT/'manifest.json')['entries']]
    r['scope']='Historical registry plus all32 known original raster source profiles; technical repeat only'
    return r


def neutral_inputs():
    specs=[]
    for name in ('N1','N2'):
        g=list(range(3,80,2));h=list(range(7,80,4))
        specs.append(dict(id=name,frames=80,duration=0,word='N',
            blocks=leaf.audit.spec()['cases'][name],switches=[],stable=name=='N1',
            masks=dict(G=g,H=h,N=[t for t in g if t not in h],S=h,S_w=list(range(11,80,4)),F=[],A=[])))
    def supply(spec):return old.read(leaf.OUT/(spec['id']+'-source.json'))
    profiles={s['id']:old.digest(supply(s)) for s in specs}
    def validate(values,spec):
        if len(values)!=80 or any(len(v)!=48 or any(type(x) is not float for x in v) for v in values):
            raise RuntimeError('NEUTRAL_SHAPE')
        if old.digest(values)!=profiles[spec['id']]:raise RuntimeError('NEUTRAL_SOURCE_CHANGED')
        if any(len({id(x) for x in v})!=48 for v in values):raise RuntimeError('JSON_FLOAT_IDENTITIES')
    def summary(reports,specs):
        return dict(technical_errors=[e for r in reports for e in r['technical_errors']],neutral_only=True)
    return specs,supply,validate,dict(entries=[],scope='NEUTRAL_ONLY'),summary


def worker(folder,charged,deadline):
    def check():
        if time.monotonic_ns()>=deadline:raise TimeoutError('WORKER_DEADLINE')
    check();verify();check()
    t=time.perf_counter_ns();c=time.process_time_ns()
    if Path(folder)==NEUTRAL:specs,supplier,validator,registry,summary=neutral_inputs()
    elif Path(folder)==OUT:
        specs,supplier,validator,registry,summary=old.source.cases(),old.source.materialize,old.source.validate,known_registry(),old.aggregate
    else:raise RuntimeError('UNKNOWN_WORKER_DESTINATION')
    preparation=dict(wall_ns=time.perf_counter_ns()-t,cpu_ns=time.process_time_ns()-c)
    execute(folder,specs,supplier,validator,registry,charged,check,summarize=summary)
    if sys.gettrace() is not None or BudgetObserver.trace is not leaf.OLD:raise RuntimeError('TRACE_NOT_RELEASED')
    old.Ledger(folder,charged,claimed=True).write('worker-path.json',dict(
        path=['worker','execute','frozen execute','timed call','integrated_baseline (M/E/K/P)','frozen replay'],
        test_or_mock_dispatch_frames=False,baseline_observer='SampleLeafBudgetObserver',
        trace_scope='Unchanged frozen replay coverage, including its original isolated-heap exclusion',
        input_preparation=preparation,trace_released=True))
    check();verify();check()


def authorization(status):
    return dict(status=status,action='KNOWN_DATA_TECHNICAL_REPEAT_ONCE',evidence_status=STATUS,
        merge_with_old_run=False,time_reserve_demonstrated=False,total_seconds=3600,
        binding_sha256=old.sha(BINDING),plan_sha256=old.sha(PLAN),qualification_sha256=old.sha(QUAL/'closure.json'),
        output=OUT.relative_to(ROOT).as_posix(),cases=32,positions=2048,arms=list(old.ARMS))


def validate_authorization(value,expected):
    if value!=expected:raise RuntimeError('EXPLICIT_SEPARATE_AUTHORIZATION_REQUIRED')


def preparation_check():
    c=old.read(QUAL/'closure.json')
    if c['status']!='PASS' or old.read(QUAL/'binding.json')!=verify():raise RuntimeError('QUALIFICATION_REQUIRED')
    for n,v in c['files'].items():
        if old.sha(QUAL/n)!=v['sha256']:raise RuntimeError('QUALIFICATION_CHANGED')


def charged_bytes(auth):
    b=verify()
    paths={ROOT/n for n in b['code']|b['references']}
    paths.update((PLAN,BINDING,TEMPLATE,GUIDE,Path(auth)))
    paths.update(p for p in QUAL.rglob('*') if p.is_file())
    charge=sum(p.stat().st_size for p in paths)
    if charge>old.MAX_CHARGED:raise RuntimeError('PREPARATION_REFERENCE_CAP')
    return charge


def run(path):
    verify();preparation_check()
    validate_authorization(old.read(Path(path)),authorization('AUTHORIZED_ONCE'))
    charged=charged_bytes(path)
    supervise(OUT,charged,worker,metadata=dict(authorization_sha256=old.sha(Path(path)),binding_sha256=old.sha(BINDING)))


def timeplan():
    phase=old.read(NEUTRAL/'phase-times.json')
    maxima={a:max(r['wall_ns']/1e9 for r in phase['replays'] if r['arm']==a) for a in old.ARMS}
    baseline=32*sum(maxima[a] for a in ('M','E','K','P'))*1.25
    total=baseline+180+30+60
    return dict(status='FEASIBLE_WITH_HARD_STOP' if total<3600 else 'INSUFFICIENT_MARGIN',
        measurement=dict(per_arm_maximum_80_positions_seconds=maxima),
        extrapolation=dict(baseline_seconds=baseline,administration_seconds=180,U_seconds=30,
            closure_seconds=60,contingency_factor=1.25,total_seconds=total,limit=3600,
            reserve_seconds=3600-total),
        assumptions=['All32 cases charged80 positions, including16 actual48-position cases',
            'Each baseline uses its slower N1/N2 direct integrated wall time, then25percent allowance',
            'U charged30 seconds; direct32-case maximum extrapolation recorded separately',
            'Administration180 seconds includes input/hash, evidence, export, binding verification, process overhead',
            'One planning approach; no chained speed ratios and no selection between models'],
        checks=dict(U_extrapolation_seconds=32*maxima['U']),
        uncertainty='Neutral N1/N2 do not prove a worst-case bound for every known contextual trajectory or host load;25percent plus full80 charging and remaining margin are planning safeguards, not a guarantee.',
        historical_comparison=dict(original_run_seconds=3602.419874,
            old_v2_projection_seconds=6330.087716,
            relevance='Historical timings include the old Sample traversal and/or test/mock stack overhead. Retained as context, not multiplied by neutral speed ratios. Frozen policy/source and old NOT_EVALUABLE verdict unchanged.'),
        consequence='Recommend separately authorized technical repeat only if margin positive; unchanged3540s worker deadline and60s closure. A timeout yields incomplete technical evidence, never a completed original evaluation.',
        recommendation='SEPARATE_TECHNICAL_REPEAT_RECOMMENDED' if total<3600 else 'DO_NOT_START')


def evidence_bytes():
    paths=[p for p in QUAL.rglob('*') if p.is_file()]
    paths.extend(ROOT/n for n in NEW)
    paths.extend(p for p in (PLAN,BINDING,GUIDE,TEMPLATE) if p.exists())
    return sum(p.stat().st_size for p in paths)


def bounded_save(name,value):
    raw=(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    if evidence_bytes()+len(raw)+65536>QUAL_LIMIT:raise RuntimeError('QUALIFICATION_EXPORT_LIMIT')
    with (QUAL/name).open('xb') as f:f.write(raw)


def qualify():
    started=time.monotonic_ns();b=verify();QUAL.mkdir(exist_ok=False);bounded_save('binding.json',b)
    success=False;error=None
    try:
        suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_s2uc_repeat_prepare_v3')
        def ids(s):
            for t in s:
                if isinstance(t,unittest.TestSuite):yield from ids(t)
                else:yield t.id()
        names=list(ids(suite));stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        bounded_save('tests.json',dict(ids=names,count=r.testsRun,success=r.wasSuccessful(),
            failures=len(r.failures),errors=len(r.errors),skips=len(r.skipped),output=stream.getvalue()))
        if not r.wasSuccessful() or r.skipped:raise RuntimeError('INTEGRATION_TESTS')
        # Reuse unchanged watchdog tests. This is the sole new worker/matrix.
        remaining=900-(time.monotonic_ns()-started)/1e9
        neutral_charge=old.LIMIT-(QUAL_LIMIT-QUAL_PARENT_RESERVE)
        supervise(NEUTRAL,neutral_charge,worker,remaining,60,metadata=dict(binding_sha256=old.sha(BINDING),
            charge_kind='neutral cap enforcement:15MiB worker plus1MiB qualification closure reserve'))
        t=time.perf_counter_ns();c=time.process_time_ns();checks=[]
        for case in ('N1','N2'):
            for arm in old.ARMS:
                result=old.read(NEUTRAL/f'{case}-{arm}.json');old.resource_check(result)
                ref=(v2.PREVIOUS_QUAL/'integration'/f'{case}-U.json' if arm=='U' else sample.OUT/f'{case}-{arm}-NEW.json')
                previous=old.read(ref)
                equal=leaf.canonical(result)==leaf.canonical(previous)
                meter_equal=({k:v for k,v in result['resources'].items() if k!='additional_python_peak'}==
                    {k:v for k,v in previous['resources'].items() if k!='additional_python_peak'} if arm=='U'
                    else result['resources']['meter']==previous['resources']['meter'])
                differences={k:dict(previous=previous['resources'].get(k),integrated=result['resources'].get(k))
                    for k in set(result['resources'])|set(previous['resources'])
                    if result['resources'].get(k)!=previous['resources'].get(k)}
                if not equal or not meter_equal:raise RuntimeError('SEMANTIC_OR_METER_DIFFERENCE:'+case+arm)
                checks.append(dict(case=case,arm=arm,semantic_equal=equal,meter_equal=meter_equal,
                    reference=ref.relative_to(ROOT).as_posix(),resources=result['resources'],
                    resource_differences=differences,terminal_cleanup=result['terminal_cleanup']))
            if old.read(NEUTRAL/f'{case}-assessment.json')['technical_errors']:raise RuntimeError('CASE_EVIDENCE')
        phase=old.read(NEUTRAL/'phase-times.json')
        if len(phase['replays'])!=10:raise RuntimeError('REPLAY_COUNT')
        complete=old.read(NEUTRAL/'worker-complete.json')
        if complete['experimental_admissions']!=800 or complete['reference_advances']!=800:raise RuntimeError('ADMISSION_COUNT')
        bounded_save('comparisons.json',dict(checks=checks,wall_ns=time.perf_counter_ns()-t,cpu_ns=time.process_time_ns()-c))
        t=time.perf_counter_ns();verify();sample.verify();v2.preparation_check()
        bounded_save('verification.json',dict(historical_bindings_unchanged=True,
            wall_ns=time.perf_counter_ns()-t,raster_materialized=False,raster_executed=False,
            reused_tests=['V01-V08','S01-S10','V2 I01-I07','Raster32 R01-R25'],
            files={p.relative_to(NEUTRAL).as_posix():dict(bytes=p.stat().st_size,sha256=old.sha(p))
                for p in NEUTRAL.rglob('*') if p.is_file()}))
        bounded_save('time-plan.json',timeplan())
        if time.monotonic_ns()-started>=900*1e9:raise RuntimeError('QUALIFICATION_DEADLINE')
        success=True
    except BaseException as exc:error=type(exc).__name__+':'+str(exc);raise
    finally:
        bounded_save('closure.json',dict(status='PASS' if success else 'FAILED',error=error,
            files={p.relative_to(QUAL).as_posix():dict(bytes=p.stat().st_size,sha256=old.sha(p))
                for p in QUAL.rglob('*') if p.is_file()},
            raster_materialized=False,raster_executed=False,started_monotonic_ns=started,
            seconds_before_closure_write=(time.monotonic_ns()-started)/1e9,bytes_before_closure=evidence_bytes()))
    old.save(TEMPLATE,authorization('PENDING_SEPARATE_AUTHORIZATION'))
    # Final timestamp after actual closure write, hash and pending template export.
    h=old.sha(QUAL/'closure.json');finished=time.monotonic_ns()
    bounded_save('completion.json',dict(closure_sha256=h,finished_monotonic_ns=finished,
        duration_seconds=(finished-started)/1e9,total_limit_seconds=900,
        bytes_before_terminal_record=evidence_bytes(),terminal_record_write_excluded=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('prepare','qualify','run'));parser.add_argument('--authorization')
    args=parser.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='qualify':qualify()
    else:
        if not args.authorization:parser.error('--authorization required')
        run(args.authorization)
