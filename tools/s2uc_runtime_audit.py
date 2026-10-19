"""Isolated neutral timing diagnosis. Never repairs or resumes Raster32."""
import argparse
import ast
from collections import defaultdict
from contextlib import ExitStack
from datetime import datetime, timezone, timedelta
import hashlib
import io
import json
import multiprocessing
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

from tools import s2uc_eval_prepare as frozen
from tools import _s2uc_eval_baseline_replay as baseline
from tools._s2uc_promotion_replay import PromotionMeter, PromotionAdapter
from tools._s2uc_signal_approx_compare import ApproxBudgetObserver
from tools.s2uc_context_prediction_check import BudgetObserver
from tools._s2uc_signal_approx_adapter import SignalApproxAdapter

ROOT=frozen.ROOT
PLAN=ROOT/'docs/S2UC_NEUTRALER_LAUFZEITAUDIT_PLAN_20261003.txt'
BINDING=ROOT/'docs/S2UC_NEUTRALER_LAUFZEITAUDIT_BINDUNG_20261003.json'
OUT=ROOT/'reports/s2uc/runtime-neutral-audit-20261003-01'
NEW=('tools/s2uc_runtime_audit.py','tests/test_s2uc_runtime_audit.py')
ARMS=('M','E','K','P')
SECONDS=900
LIMIT=16*1048576


def spec():
    return dict(recipes={'A':['1/32','7/32','19/32','29/32'],
                         'B':['1/32','7/32','11/32','29/32']},
        cases={'N1':['A']*20,'N2':['A']*5+['B']*5+['A']*5+['B']*5},
        arms=list(ARMS),orders={'N1':['ON','OFF'],'N2':['OFF','ON']},
        anchors=['N1-M','N2-M'],frames=80,replays=18,experimental_admissions=1440,
        reference_advances=1440,seconds=SECONDS,export_limit=LIMIT)


def fixture(name):
    p=spec()
    return [(int(x.split('/')[0])/int(x.split('/')[1]),)*48 for b in p['cases'][name] for x in p['recipes'][b]]


class Book:
    """Exclusive nested wall/CPU accounting; own hooks are not cost-free."""
    def __init__(self):
        self.wall=defaultdict(int);self.cpu=defaultdict(int);self.calls=defaultdict(int)
        self.stack=['replay_other'];self.start_wall=self.last_wall=time.perf_counter_ns()
        self.start_cpu=self.last_cpu=time.process_time_ns()

    def account(self):
        w=time.perf_counter_ns();c=time.process_time_ns()
        self.wall[self.stack[-1]]+=w-self.last_wall;self.cpu[self.stack[-1]]+=c-self.last_cpu
        self.last_wall=w;self.last_cpu=c

    def push_raw(self, category):
        self.account();self.stack.append(category);self.calls[category]+=1

    def pop_raw(self):
        self.account();self.stack.pop()

    def scope(self, category):
        return Scope(self,category)

    def wrap(self, category, operation):
        def called(*args,**kwargs):
            with self.scope(category):return operation(*args,**kwargs)
        return called

    def trace_wrap(self, category, operation):
        # Python disables recursive tracing while dispatching this callback.
        def called(*args,**kwargs):
            self.push_raw(category)
            try:return operation(*args,**kwargs)
            finally:self.pop_raw()
        return called

    def finish(self):
        self.account()
        if self.stack!=['replay_other']:raise RuntimeError('UNBALANCED_CLOCKS')
        w=self.last_wall-self.start_wall;c=self.last_cpu-self.start_cpu
        if sum(self.wall.values())!=w or sum(self.cpu.values())!=c:raise RuntimeError('TIME_PARTITION')
        return dict(wall_ns=dict(self.wall),cpu_ns=dict(self.cpu),calls=dict(self.calls),
                    partition_wall_ns=w,partition_cpu_ns=c)


class Scope:
    def __init__(self,book,category):self.book=book;self.category=category
    def __enter__(self):
        prior=sys.gettrace();sys.settrace(None)
        try:self.book.push_raw(self.category)
        finally:sys.settrace(prior)
    def __exit__(self,*args):
        prior=sys.gettrace();sys.settrace(None)
        try:self.book.pop_raw()
        finally:sys.settrace(prior)


class SysProxy:
    def __init__(self,enabled):self.enabled=enabled
    def __getattr__(self,name):return getattr(sys,name)
    def settrace(self,callback):sys.settrace(callback if self.enabled else None)


class HeapProxy:
    def __init__(self,module,book):self.module=module;self.book=book
    def __getattr__(self,name):
        value=getattr(self.module,name)
        return self.book.wrap('resource_other',value) if callable(value) else value


def instrumented(book,enabled):
    """Add observer scopes in memory; source files and algorithm bodies untouched."""
    filename=str(Path(baseline.__file__).resolve())
    tree=ast.parse(Path(filename).read_text(encoding='utf-8'),filename)
    class WrapObserver(ast.NodeTransformer):
        count=0
        def visit_FunctionDef(self,node):
            self.generic_visit(node)
            if node.name in ('_admit','_receipt'):
                self.count+=1
                node.body=[ast.With(items=[ast.withitem(context_expr=ast.Call(
                    func=ast.Attribute(value=ast.Name(id='book',ctx=ast.Load()),attr='scope',ctx=ast.Load()),
                    args=[ast.Constant('evidence_observation')],keywords=[]))],body=node.body)]
            return node
    transform=WrapObserver();tree=transform.visit(tree)
    if transform.count!=2:raise RuntimeError('UNEXPECTED_REPLAY_STRUCTURE')
    ast.fix_missing_locations(tree);ns={'book':book}
    exec(compile(tree,filename,'exec'),ns)
    # Entry scopes only: original superclass methods and policy remain unchanged.
    methods={n:book.wrap('policy',getattr(PromotionAdapter,n)) for n in
        ('accept_perception','consume_feedback','_admit','_receipt','finish_story','_terminate')}
    methods['selected_values']=property(book.wrap('policy',PromotionAdapter.selected_values.fget))
    diagnostic_type=type('DiagnosticPromotion',(PromotionAdapter,),methods)
    reference_type=type('DiagnosticReference',(SignalApproxAdapter,),{
        n:book.wrap('reference',getattr(SignalApproxAdapter,n)) for n in
        ('accept_perception','release_prediction','finish_story','_terminate')})
    ns['PromotionAdapter']=diagnostic_type;ns['SignalApproxAdapter']=reference_type
    consume=ns['consume_prediction']
    def consumption(adapter,sample):
        with book.scope('reference' if isinstance(adapter,reference_type) else 'policy'):
            return consume(adapter,sample)
    ns['consume_prediction']=consumption
    for name in ('cells','inventory','state','digest','mae48'):
        ns[name]=book.wrap('evidence_observation',ns[name])
    ns['owned']=book.wrap('resource_other',ns['owned'])
    ns['tracemalloc']=HeapProxy(ns['tracemalloc'],book)
    gate=ns['GatedReplay']
    ns['GatedReplay']=type('DiagnosticGate',(gate,),{'take':book.wrap('source_gate',gate.take)})
    ns['sys']=SysProxy(enabled)
    return ns['replay']


def semantic(result):
    return {k:v for k,v in result.items() if k!='resources'}


def measured(values,arm,enabled,path,check):
    started=time.perf_counter_ns();book=Book()
    replay=instrumented(book,enabled);partial={}
    original_dumps=json.dumps;original_loads=json.loads
    with ExitStack() as stack:
        for cls,category in ((BudgetObserver,'resource_trace_base'),
                             (ApproxBudgetObserver,'resource_trace_approx'),
                             (PromotionMeter,'resource_trace_promotion')):
            stack.enter_context(patch.object(cls,'trace',book.trace_wrap(category,cls.trace)))
        stack.enter_context(patch.object(PromotionMeter,'admission_bound',book.wrap('resource_other',PromotionMeter.admission_bound)))
        stack.enter_context(patch.object(json,'dumps',book.wrap('json_internal',original_dumps)))
        stack.enter_context(patch.object(json,'loads',book.wrap('json_internal',original_loads)))
        t=time.perf_counter_ns()
        result=replay(values,frozen.digest(values),count=80,arm=arm,evidence=partial,check=check)
        replay_ns=time.perf_counter_ns()-t
    if sys.gettrace() is not None:raise RuntimeError('TRACE_NOT_RELEASED')
    if not result['terminal_cleanup']:raise RuntimeError('NOT_RELEASED')
    with book.scope('export_serialization'):
        raw=(original_dumps(result,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    with book.scope('file_output'):
        with path.open('xb') as out:
            if out.write(raw)!=len(raw):raise RuntimeError('SHORT_WRITE')
    times=book.finish();outer=time.perf_counter_ns()-started
    times.update(replay_wall_ns=replay_ns,outer_wall_ns=outer,
        outside_partition_ns=outer-times['partition_wall_ns'],bytes=len(raw),
        tracing_enabled=enabled,resource_certification=False)
    return result,times


def anchor(values,path,check):
    started=time.perf_counter_ns()
    result=baseline.replay(values,frozen.digest(values),count=80,arm='M',check=check)
    replay_ns=time.perf_counter_ns()-started
    t=time.perf_counter_ns();raw=(json.dumps(result,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    serialization_ns=time.perf_counter_ns()-t;t=time.perf_counter_ns()
    with path.open('xb') as out:out.write(raw)
    return result,dict(replay_wall_ns=replay_ns,export_serialization_ns=serialization_ns,
                       file_output_ns=time.perf_counter_ns()-t,bytes=len(raw))


def historical():
    paths={}
    for folder in (frozen.OUT,ROOT/'reports/s2uc/raster32-assessment-20261003-01'):
        for p in folder.iterdir():
            if p.is_file():paths[p.relative_to(ROOT).as_posix()]=frozen.sha(p)
    return paths


def prepare():
    old=frozen.verify()
    frozen.save(BINDING,dict(plan_sha256=frozen.sha(PLAN),code={n:frozen.sha(ROOT/n) for n in NEW},
        previous_code=old['code'],previous_binding_sha256=frozen.sha(frozen.BINDING),
        historical=historical(),spec=spec(),python=sys.version,executable_sha256=frozen.sha(sys.executable)))


def verify():
    b=frozen.read(BINDING)
    if b['plan_sha256']!=frozen.sha(PLAN) or b['spec']!=spec():raise RuntimeError('AUDIT_PLAN')
    if b['code']!={n:frozen.sha(ROOT/n) for n in NEW}:raise RuntimeError('AUDIT_CODE')
    if b['previous_code']!=frozen.verify()['code'] or b['historical']!=historical():raise RuntimeError('HISTORICAL_CHANGED')
    if b['previous_binding_sha256']!=frozen.sha(frozen.BINDING):raise RuntimeError('PREVIOUS_BINDING')
    if b['python']!=sys.version or b['executable_sha256']!=frozen.sha(sys.executable):raise RuntimeError('RUNTIME')
    return b


def stamp(event):
    return dict(event=event,monotonic_ns=time.monotonic_ns(),utc=datetime.now(timezone.utc).isoformat())


def supervise_diagnostic(target,args,seconds):
    """Diagnostic prototype only. Does not replace operative supervise()."""
    begin=stamp('deadline_established');deadline=begin['monotonic_ns']+int(seconds*1e9)
    begin.update(deadline_monotonic_ns=deadline,
        deadline_utc=(datetime.fromisoformat(begin['utc'])+timedelta(seconds=seconds)).isoformat())
    events=[begin];proc=multiprocessing.get_context('spawn').Process(target=target,args=(*args,deadline))
    status='NORMAL';proc.start()
    try:
        proc.join(max(0,(deadline-time.monotonic_ns())/1e9))
        if proc.is_alive():
            status='TIME_LIMIT';events.append(stamp('abort_requested'));proc.terminate();proc.join(5)
            if proc.is_alive():events.append(stamp('kill_requested'));proc.kill();proc.join()
        events.append(stamp('worker_end_confirmed')|dict(exitcode=proc.exitcode,alive=proc.is_alive()))
        if status=='NORMAL' and proc.exitcode!=0:status='WORKER_ERROR'
    finally:
        if proc.is_alive():proc.terminate();proc.join()
        proc.close()
    events.append(stamp('closure_admin_started'))
    # A real neutral serialization operation between the administration stamps.
    summary=json.dumps(dict(status=status,events=events),sort_keys=True).encode()
    events.append(stamp('closure_admin_finished')|dict(serialized_bytes=len(summary)))
    return dict(status=status,events=events,actual_worker_death_time='NOT_DIRECTLY_MEASURED',
                historical_worker_stop='UNKNOWN_NOT_RECONSTRUCTED')


def sleeping_worker(seconds,deadline):time.sleep(seconds)


def matrix(folder,deadline):
    folder=Path(folder)
    def check():
        if time.monotonic_ns()>=deadline:raise TimeoutError('NEUTRAL_AUDIT_DEADLINE')
        if sum(p.stat().st_size for p in folder.iterdir() if p.is_file())>LIMIT:raise RuntimeError('AUDIT_EXPORT_LIMIT')
    measurements=[];checks=[]
    try:
        for name in ('N1','N2'):
            values=fixture(name)
            if len(values)!=80 or values[0]!=(1/32,)*48:raise RuntimeError('NEUTRAL_SOURCE')
            frozen.save(folder/(name+'-source.json'),values)
            check();original,tm=anchor(values,folder/(name+'-M-anchor.json'),check)
            measurements.append(dict(case=name,arm='M',mode='ANCHOR',timing=tm))
            for arm in ARMS:
                results={}
                for mode in spec()['orders'][name]:
                    check();r,t=measured(values,arm,mode=='ON',folder/(name+'-'+arm+'-'+mode+'.json'),check)
                    results[mode]=r;measurements.append(dict(case=name,arm=arm,mode=mode,timing=t))
                    frozen.save(folder/(name+'-'+arm+'-'+mode+'-timing.json'),t)
                equivalent=semantic(results['ON'])==semantic(results['OFF'])
                anchored=semantic(results['ON'])==semantic(original) if arm=='M' else None
                competition=sum(sum(m['offset']==0 and m['factors']==[1.0] for m in f['receipt']['matches'])>=2 for f in results['ON']['forecasts'])
                c=dict(case=name,arm=arm,on_off_equal=equivalent,anchor_equal=anchored,
                    semantic_sha256=frozen.digest(semantic(results['ON'])),competing_forecasts=competition,
                    frames=80,reference_advances=80,censored_target=results['ON']['censored_target'],
                    complete_release=all(r['terminal_cleanup'] for r in results.values()))
                checks.append(c)
                if not equivalent or anchored is False or not c['complete_release'] or (name=='N2' and not competition):
                    raise RuntimeError('NEUTRAL_EQUIVALENCE_OR_COVERAGE')
                frozen.save(folder/(name+'-'+arm+'-equivalence.json'),c)
        frozen.save(folder/'measurements.json',measurements);frozen.save(folder/'equivalence.json',checks)
    except BaseException as exc:
        frozen.save(folder/'diagnostic-error.json',dict(error=type(exc).__name__+':'+str(exc),
            completed_measurements=measurements,completed_equivalence=checks))
        raise


def run():
    b=verify();OUT.mkdir(exist_ok=False)
    frozen.save(OUT/'binding.json',b)
    frozen.save(OUT/'source-snapshot.json',{n:(ROOT/n).read_text(encoding='utf-8') for n in NEW})
    error=None;success=False
    try:
        suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_s2uc_runtime_audit')
        def ids(s):
            for x in s:
                if isinstance(x,unittest.TestSuite):yield from ids(x)
                else:yield x.id()
        names=list(ids(suite));stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        frozen.save(OUT/'tests.json',dict(ids=names,count=r.testsRun,success=r.wasSuccessful(),
            failures=len(r.failures),errors=len(r.errors),skipped=len(r.skipped),output=stream.getvalue()))
        from tests.test_s2uc_runtime_audit import FACTS
        frozen.save(OUT/'watchdog-probes.json',FACTS)
        if not r.wasSuccessful() or r.skipped:raise RuntimeError('AUDIT_TESTS')
        lifecycle=supervise_diagnostic(matrix,(str(OUT),),SECONDS)
        frozen.save(OUT/'matrix-lifecycle.json',lifecycle)
        if lifecycle['status']!='NORMAL':raise RuntimeError('MATRIX_'+lifecycle['status'])
        verify();success=True
    except BaseException as exc:error=type(exc).__name__+':'+str(exc);raise
    finally:
        frozen.save(OUT/'closure.json',dict(status='PASS' if success else 'FAILED',error=error,
            files={p.name:dict(bytes=p.stat().st_size,sha256=frozen.sha(p)) for p in OUT.iterdir() if p.is_file()},
            raster_replays=0,operative_repair=False,policy_changed=False))


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('prepare','run'))
    if p.parse_args().action=='prepare':prepare()
    else:run()


if __name__=='__main__':main()
