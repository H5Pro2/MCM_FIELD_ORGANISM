"""Exactly four preregistered neutral replays; instrumentation only."""
import ast
from collections import defaultdict
import copy
import inspect
import json
from pathlib import Path
import sys
import textwrap
import time
from unittest.mock import patch
from tools import s2uc_repeat_prepare_v2 as q
from tools import _s2uc_frame_leaf_observer_v1 as visitor
from tools._s2uc_pair_context_adapter import PerceptionSample
from tests.test_s2uc_eval_prepare import neutral

ROOT=q.ROOT
OUT=ROOT/'reports/s2uc/identity-stack-diagnosis-20261003-01'
PLAN=ROOT/'docs/S2UC_IDENTITAET_STACK_DIAGNOSE_PLAN_20261003.json'
BINDING=ROOT/'docs/S2UC_IDENTITAET_STACK_DIAGNOSE_BINDUNG_20261003.json'
FILE='tools/s2uc_identity_stack_diagnosis.py'
LIMIT=16*1048576
ORDER=(('A','direct','shared'),('B','direct','json'),('C','integrated','json'),('D','integrated','shared'))


def spec():return dict(order=ORDER,fixture='N2',arm='M',frames=80,replays=4,admissions=320,reference_advances=320,
    seconds=900,bytes=LIMIT,trace=True,warmups=0,repetitions=0,
    counters_scope='Basisvisitor: all dispatched trace events; own stack and filename checks; per-callback unique float visits and sample payload identities; Frame leaf hits. Derived visitor costs remain active but not individually counted.',
    timing='Identical inner wrapper immediately around original baseline.replay, after source preparation/profile digest and before export; monotonic wall and process CPU.',
    comparisons='All non-resource fields canonical; all meter fields exact; full resource objects additionally compared with every difference retained, including heap.',
    integrated='Frozen execute bytecode via V2 execute, one N2/M case only. Same checked/active/three Mock dispatchers. Manifest length check adapted2->1; diagnostics do not assess a32-case raster.',
    limits='Existing policy resource limits retained; diagnostic counters are separate observer overhead, not a new resource certification.')


def size():return sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())


def save(name,value):
    raw=(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    if size()+len(raw)+65536>LIMIT:raise RuntimeError('DIAG_EXPORT_LIMIT')
    with (OUT/name).open('xb') as f:f.write(raw)


def counted_trace(counts):
    """Inject only accounting statements; stripping them restores original AST."""
    original=ast.parse(textwrap.dedent(inspect.getsource(visitor.FrameLeafBudgetObserver.trace)))
    tree=copy.deepcopy(original)
    def statements(code):
        nodes=ast.parse(code).body
        for node in nodes:node.diagnostic=True
        return nodes
    class Add(ast.NodeTransformer):
        def visit_FunctionDef(self,node):
            self.generic_visit(node)
            if node.name=='trace':
                node.body=statements("counts['trace_events']+=1\ncounts['event_'+event]+=1\ncounts['filename_checks']+=1")+node.body
            elif node.name=='visit':
                node.body=statements("counts['visit_attempts']+=1")+node.body
            return node
        def visit_Expr(self,node):
            if ast.unparse(node)=='seen.add(id(x))':
                return [node]+statements("counts['unique_object_visits']+=1\nif type(x) is float: counts['unique_float_visits']+=1\nif type(x) is PerceptionSample:\n counts['sample_visits']+=1\n counts['sample_float_identity_sum']+=len({id(v) for v in x.values if type(v) is float})\n counts['sample_value_slots']+=len(x.values)")
            return node
        def visit_If(self,node):
            self.generic_visit(node)
            if ast.unparse(node.test)=='scalar_frame_leaf(x)':
                node.body=statements("counts['frame_leaf_hits']+=1")+node.body
            return node
        def visit_While(self,node):
            self.generic_visit(node)
            if isinstance(node.test,ast.Name) and node.test.id=='cursor':
                node.body=statements("counts['stack_frames_checked']+=1\ncounts['filename_checks']+=1")+node.body
            return node
    tree=Add().visit(tree)
    class Strip(ast.NodeTransformer):
        def visit(self,node):
            if getattr(node,'diagnostic',False):return None
            return super().visit(node)
    if ast.dump(Strip().visit(copy.deepcopy(tree)))!=ast.dump(original):raise RuntimeError('COUNTER_AST_CHANGED_LOGIC')
    ast.fix_missing_locations(tree)
    ns=dict(vars(visitor),counts=counts,PerceptionSample=PerceptionSample)
    exec(compile(tree,str(Path(visitor.__file__).resolve()),'exec'),ns)
    return ns['trace'],ast.unparse(tree)


def prepare():
    q.preparation_check();q.leaf.verify()
    q.old.save(PLAN,spec())
    refs={str(q.BINDING.relative_to(ROOT)):q.old.sha(q.BINDING),str(q.QUAL.relative_to(ROOT)/'closure.json'):q.old.sha(q.QUAL/'closure.json')}
    refs.update({p.relative_to(ROOT).as_posix():q.old.sha(p) for p in (ROOT/'reports/s2uc/runtime-reconciliation-20261003-01').iterdir() if p.is_file()})
    q.old.save(BINDING,dict(code={FILE:q.old.sha(ROOT/FILE)},plan_sha256=q.old.sha(PLAN),references=refs))


def verify():
    b=q.old.read(BINDING);q.preparation_check()
    assert b['code']=={FILE:q.old.sha(ROOT/FILE)} and b['plan_sha256']==q.old.sha(PLAN)
    assert q.old.read(PLAN)==json.loads(json.dumps(spec()))
    for n,h in b['references'].items():assert q.old.sha(ROOT/n)==h
    return b


def smoke():
    # No policy replay: verify counter meanings on one synthetic stack snapshot.
    from types import SimpleNamespace
    from tools._s2tu_retained_trace import Frame
    sample=PerceptionSample((.25,)*48,'a'*64,'owner','stream',1,0,4800)
    frame=Frame(sample.values,sample.profile,sample.owner,'p1',1)
    snap=SimpleNamespace(f_code=SimpleNamespace(co_filename='_s2uc_pair_context_adapter.py'),f_locals={'sample':sample,'frame':frame},f_back=None)
    counts=defaultdict(int);fn,source=counted_trace(counts);meter=q.BudgetObserver()
    fn(meter,snap,'line',None)
    assert counts['trace_events']==1 and counts['stack_frames_checked']==1 and counts['filename_checks']==2
    assert counts['sample_visits']==1 and counts['sample_float_identity_sum']==1 and counts['frame_leaf_hits']==1
    assert counts['unique_float_visits']==1 and meter.frame_peak==1
    return dict(test_id='D2X01_COUNTER_AST_AND_SYNTHETIC_SNAPSHOT',passed=True,counters=dict(counts)),source


def matrix(folder,charged,deadline):
    def check():
        if time.monotonic_ns()>=deadline:raise TimeoutError('DIAG_DEADLINE')
    rows=[];results={};original_replay=q.old.baseline_replay;original_read=q.old.read
    try:
        for label,path,representation in ORDER:
            if size()+2*1048576>LIMIT:raise RuntimeError('DIAG_EXPORT_HEADROOM')
            check();start=time.perf_counter_ns();cpu=time.process_time_ns()
            if representation=='shared':values=q.leaf.audit.fixture('N2')
            else:values=original_read(q.leaf.OUT/'N2-source.json')
            profile=q.old.digest(values)
            prep=dict(wall_ns=time.perf_counter_ns()-start,cpu_ns=time.process_time_ns()-cpu)
            identities=sorted({len({id(v) for v in row}) for row in values})
            assert identities==([1] if representation=='shared' else [48])
            assert profile==q.old.digest(original_read(q.leaf.OUT/'N2-source.json'))
            counts=defaultdict(int);trace,_=counted_trace(counts);timing={};partial={}
            def recorded(*args,**kwargs):
                if timing:raise RuntimeError('EXTRA_REPLAY')
                timing['started']=True
                w=time.perf_counter_ns();c=time.process_time_ns()
                try:return original_replay(*args,**kwargs)
                finally:timing.update(wall_ns=time.perf_counter_ns()-w,cpu_ns=time.process_time_ns()-c)
            outer=time.perf_counter_ns()
            with patch.object(visitor.FrameLeafBudgetObserver,'trace',trace):
                if path=='direct':
                    with patch.object(q.BudgetObserver,'trace',trace):
                        result=recorded(values,profile,count=80,arm='M',evidence=partial,check=check)
                    wrapper_ns=time.perf_counter_ns()-outer
                    t=time.perf_counter_ns();save(label+'-result.json',result);export_ns=time.perf_counter_ns()-t
                    outer_phases=None
                else:
                    case_folder=OUT/label;case_folder.mkdir(exist_ok=False)
                    s=neutral(80,'N2');s['blocks']=q.leaf.audit.spec()['cases']['N2'];s['stable']=False
                    original=q.integrated_baseline
                    def checked(*args,**kwargs):
                        if q.BudgetObserver.trace is not q.leaf.OLD:raise RuntimeError('PATCH_LEAK_BEFORE')
                        with patch.object(q.old,'baseline_replay',wraps=q.old.baseline_replay) as wrapped:
                            original_replay_call=wrapped._mock_wraps
                            def active(*a,**kw):
                                if q.BudgetObserver.trace is not visitor.FrameLeafBudgetObserver.trace:raise RuntimeError('LEAF_NOT_ACTIVE')
                                manifest=q.old.read(case_folder/'manifest.json')
                                if len(manifest['entries'])!=1:raise RuntimeError('MANIFEST_NOT_SEALED')
                                return original_replay_call(*a,**kw)
                            wrapped.side_effect=active;result=original(*args,**kwargs)
                        if q.BudgetObserver.trace is not q.leaf.OLD:raise RuntimeError('PATCH_LEAK_AFTER')
                        return result
                    def reading(p):
                        # Keep chosen object identities after numeric source export.
                        if Path(p)==case_folder/'N2-source.json':return values
                        return original_read(p)
                    def validate(v,s):
                        if q.old.digest(v)!=profile:raise RuntimeError('SOURCE_DIFFERENCE')
                    with patch.object(q.old,'ARMS',('M',)),patch.object(q.old,'baseline_replay',recorded),patch.object(q.old,'read',reading),patch.object(q,'integrated_baseline',checked),patch.object(q.old,'assess_case',return_value={'technical_errors':[]}),patch.object(q.old.source,'materialize',side_effect=AssertionError('RASTER_FORBIDDEN')):
                        q.execute(case_folder,[s],lambda s:values,validate,dict(entries=[],scope='N2_ONLY'),0,check,
                            summarize=lambda reports,specs:dict(technical_errors=[],neutral_only=True))
                    wrapper_ns=time.perf_counter_ns()-outer
                    result=original_read(case_folder/'N2-M.json');outer_phases=original_read(case_folder/'phase-times.json')
                    export_ns=outer_phases['wall_ns']['export']
            assert sys.gettrace() is None and q.BudgetObserver.trace is q.leaf.OLD
            q.old.resource_check(result)
            assert counts['sample_float_identity_sum']==counts['sample_visits']*(1 if representation=='shared' else 48)
            assert counts['sample_value_slots']==counts['sample_visits']*48
            assert counts['filename_checks']==counts['trace_events']+counts['stack_frames_checked']
            row=dict(id=label,path=path,representation=representation,source_preparation=prep,source_digest=profile,
                unique_float_ids_per_vector=identities,replay=timing,wrapper_wall_ns=wrapper_ns,export_wall_ns=export_ns,
                outer_phases=outer_phases,counters=dict(counts),resources=result['resources'])
            rows.append(row);results[label]=result;save(label+'-measurement.json',row)
        comparison={}
        for label in ('B','C','D'):
            comparison[label]=dict(semantic_equal=q.leaf.canonical(results['A'])==q.leaf.canonical(results[label]),
                meter_equal=results['A']['resources']['meter']==results[label]['resources']['meter'],
                full_resources_equal=results['A']['resources']==results[label]['resources'],
                resource_differences={k:dict(A=results['A']['resources'].get(k),other=results[label]['resources'].get(k)) for k in set(results['A']['resources'])|set(results[label]['resources']) if results['A']['resources'].get(k)!=results[label]['resources'].get(k)})
        save('measurements.json',rows);save('comparisons.json',comparison)
        save('worker-complete.json',dict(replays=4,admissions=320,reference_advances=320))
    except BaseException as exc:
        save('diagnostic-error.json',dict(error=type(exc).__name__+':'+str(exc),completed=rows,partial=partial if 'partial' in locals() else {}));raise


def run():
    binding=verify();test,source=smoke()
    # The supervisor claims OUT exclusively. Its total deadline includes closure.
    q.supervise(OUT,0,matrix,900,30,metadata=dict(binding_sha256=q.old.sha(BINDING)))
    # Keep sealed supervisor exports immutable; post-verification is separate.
    verify();q.leaf.verify()
    post=ROOT/'reports/s2uc/identity-stack-diagnosis-verification-20261003-01';post.mkdir(exist_ok=False)
    q.old.save(post/'verification.json',dict(binding=binding,smoke=test,counted_source=source,old_bindings_unchanged=True,
        matrix_closure_sha256=q.old.sha(OUT/'closure.json'),total_export_bytes=size(),raster_replays=0))


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('prepare','run'));args=parser.parse_args()
    if args.action=='prepare':prepare()
    else:run()
