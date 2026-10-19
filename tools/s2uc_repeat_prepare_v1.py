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
from tools._s2uc_frame_leaf_observer_v1 import FrameLeafBudgetObserver
from tools.s2uc_context_prediction_check import BudgetObserver

ROOT=old.ROOT
PREFIX='S2UC_TECHNISCHE_WIEDERHOLUNG_V1_'
PLAN=ROOT/'docs'/f'{PREFIX}PLAN_20261003.json'
BINDING=ROOT/'docs'/f'{PREFIX}BINDUNG_20261003.json'
TEMPLATE=ROOT/'docs'/f'{PREFIX}AUTORISIERUNG_VORLAGE_20261003.json'
GUIDE=ROOT/'docs'/f'{PREFIX}AUFRUF_20261003.txt'
QUAL=ROOT/'reports/s2uc/technical-repeat-preparation-20261003-01'
OUT=ROOT/'reports/s2uc/technical-repeat-20261003-01'
NEW=('tools/s2uc_repeat_prepare_v1.py','tests/test_s2uc_repeat_prepare_v1.py')
STATUS='KNOWN_DATA_TECHNICAL_REPEAT_NOT_UNTOUCHED_EVALUATION'
TOTAL_SECONDS=3600
CLOSURE_SECONDS=60


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
    # Only these immutable files are inputs to a future execution. Old run
    # payloads stay archived, separately verified at preparation, never merged.
    paths=[old.PLAN,old.BINDING,old.INDEX,old.CONTRACT,old.OUT/'manifest.json',
        leaf.PLAN,leaf.BINDING,leaf.OUT/'closure.json',leaf.OUT/'tests.json',
        leaf.OUT/'test-facts.json',leaf.OUT/'summary.json',
        leaf.audit.OUT/'closure.json',leaf.audit.OUT/'measurements.json',
        ROOT/'reports/s2uc/raster32-assessment-20261003-01/closure.json']
    return {p.relative_to(ROOT).as_posix():old.sha(p) for p in paths}


def prepare():
    if OUT.exists() or QUAL.exists():raise RuntimeError('PREPARATION_ALREADY_USED')
    leaf.verify()
    lc=old.read(leaf.OUT/'closure.json')
    if lc['status']!='PASS':raise RuntimeError('LEAF_NOT_QUALIFIED')
    for n,v in lc['files'].items():
        if old.sha(leaf.OUT/n)!=v['sha256']:raise RuntimeError('LEAF_EVIDENCE_CHANGED')
    codes=dict(old.read(old.BINDING)['code'])
    for n in (*leaf.audit.NEW,*leaf.FILES,*NEW):codes[n]=old.sha(ROOT/n)
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
    with patch.object(BudgetObserver,'trace',FrameLeafBudgetObserver.trace):
        return old.baseline_replay(*args,**kwargs)


def execute(folder,specs,supplier,validator,registry,charged,check,*,summarize=old.aggregate):
    # Same bytecode/defaults as frozen execute; only dependencies are injected.
    times=defaultdict(int);counts=defaultdict(int)
    def timed(name,fn):
        def call(*args,**kwargs):
            t=time.perf_counter_ns()
            try:return fn(*args,**kwargs)
            finally:times[name]+=time.perf_counter_ns()-t;counts[name]+=1
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
        manifest_entry=timed('manifest',provenance))
    engine=FunctionType(old.execute.__code__,ns,old.execute.__name__,old.execute.__defaults__)
    engine.__kwdefaults__=old.execute.__kwdefaults__
    t=time.perf_counter_ns()
    try:
        return engine(folder,specs,timed('materialization',supplier),timed('source_validation',validator),registry,charged,check,
            assess=timed('case_assessment',old.assess_case),summarize=timed('aggregation',summary))
    finally:
        old.Ledger(folder,charged,claimed=True).write('phase-times.json',dict(wall_ns=dict(times),calls=dict(counts),
            engine_wall_ns=time.perf_counter_ns()-t,exclusive_categories=True))


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
        proc.start();proc.join(max(0,(deadline-time.monotonic_ns())/1e9))
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


def worker(folder,charged,deadline):
    def check():
        if time.monotonic_ns()>=deadline:raise TimeoutError('WORKER_DEADLINE')
    check();verify();check()
    execute(folder,old.source.cases(),old.source.materialize,old.source.validate,known_registry(),charged,check)
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
    timings=old.read(leaf.OUT/'summary.json')['pairs']
    worst_ratio=max(p['new_seconds']/p['old_seconds'] for p in timings)
    # Recorded adjacent historical starts; no historical sources are generated.
    from datetime import datetime
    starts=sorted([old.read(p) for p in old.OUT.glob('*-start.json')],key=lambda x:x['started_at'])
    gaps=[(datetime.fromisoformat(y['started_at'])-datetime.fromisoformat(x['started_at'])).total_seconds()
        for x,y in zip(starts,starts[1:]) if x['arm']!='U']
    historical_max=max(gaps)
    # Treat all128 baseline arms as the slowest observed arm; do not assume
    # faster short cases. 25% host/load contingency on the measured ratio.
    baseline=128*historical_max*worst_ratio*1.25
    phases=[old.read(p) for p in QUAL.rglob('phase-times.json')]
    measured={k:sum(p['wall_ns'].get(k,0) for p in phases)/1e9 for k in
        ('materialization','source_validation','manifest','export','resource_check','case_assessment','aggregation','U_replay')}
    # At least180 s admin,30 s U,60 s closure; increase from neutral data if needed.
    administration=max(180,32*sum(v for k,v in measured.items() if k!='U_replay'))
    u=max(30,32*measured['U_replay']);closure=60
    total=baseline+administration+u+closure
    return dict(status='INSUFFICIENT_DEMONSTRATED_RESERVE',measurement=dict(historical_max_start_gap_s=historical_max,
        worst_neutral_new_old_ratio=worst_ratio,neutral_phase_seconds=measured),
        extrapolation=dict(baseline_seconds=baseline,administration_seconds=administration,U_seconds=u,closure_seconds=closure,
            contingency_factor=1.25,total_seconds=total,limit=3600,reserve_seconds=3600-total),
        assumptions='128 arms each at historical worst interval times weakest observed improvement and1.25 contingency; administration includes materialization/check/export/verification; no formal worst-case proof',
        recommendation='DO_NOT_START_WITHOUT_SEPARATE_DECISION_ON_INSUFFICIENT_RESERVE')


def qualify():
    b=verify();QUAL.mkdir(exist_ok=False);old.save(QUAL/'binding.json',b)
    success=False;error=None
    try:
        suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_s2uc_repeat_prepare_v1')
        def ids(s):
            for t in s:
                if isinstance(t,unittest.TestSuite):yield from ids(t)
                else:yield t.id()
        names=list(ids(suite));stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        old.save(QUAL/'tests.json',dict(ids=names,count=r.testsRun,success=r.wasSuccessful(),failures=len(r.failures),errors=len(r.errors),skips=len(r.skipped),output=stream.getvalue()))
        from tests.test_s2uc_repeat_prepare_v1 import FACTS
        old.save(QUAL/'facts.json',FACTS)
        if not r.wasSuccessful() or r.skipped:raise RuntimeError('INTEGRATION_TESTS')
        old.save(QUAL/'time-plan.json',timeplan());verify();leaf.verify()
        if sum(p.stat().st_size for p in QUAL.rglob('*') if p.is_file())>16*1048576:raise RuntimeError('QUAL_EXPORT_LIMIT')
        success=True
    except BaseException as exc:error=type(exc).__name__+':'+str(exc);raise
    finally:
        old.save(QUAL/'closure.json',dict(status='PASS' if success else 'FAILED',error=error,
            files={p.relative_to(QUAL).as_posix():dict(bytes=p.stat().st_size,sha256=old.sha(p)) for p in QUAL.rglob('*') if p.is_file()},
            raster_materialized=False,raster_executed=False))
    old.save(TEMPLATE,authorization('PENDING_SEPARATE_AUTHORIZATION'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('prepare','qualify','run'));parser.add_argument('--authorization')
    args=parser.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='qualify':qualify()
    else:
        if not args.authorization:parser.error('--authorization required')
        run(args.authorization)
