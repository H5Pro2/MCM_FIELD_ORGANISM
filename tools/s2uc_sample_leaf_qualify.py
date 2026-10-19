"""JSON input, direct calls, full trace; fixed16 neutral sample-leaf comparisons."""
import argparse
import io
import json
from pathlib import Path
import sys
import time
import unittest
from tools import s2uc_repeat_prepare_v2 as q
from tools._s2uc_frame_leaf_observer_v1 import FrameLeafBudgetObserver
from tools._s2uc_sample_leaf_observer_v1 import SampleLeafBudgetObserver

ROOT=q.ROOT
PLAN=ROOT/'docs/S2UC_SAMPLE_BLATT_V1_PLAN_20261003.json'
BINDING=ROOT/'docs/S2UC_SAMPLE_BLATT_V1_BINDUNG_20261003.json'
OUT=ROOT/'reports/s2uc/sample-leaf-qualification-20261003-01'
REPORT=ROOT/'reports/s2uc/sample-leaf-assessment-20261003-01'
FILES=('tools/_s2uc_sample_leaf_observer_v1.py','tools/s2uc_sample_leaf_qualify.py','tests/test_s2uc_sample_leaf_observer.py')
LIMIT=16*1048576


def spec():return dict(cases=['N1','N2'],frames=80,arms=['M','E','K','P'],orders={'N1':['OLD','NEW'],'N2':['NEW','OLD']},
    input='fresh json.load of saved neutral source per replay; source preparation outside replay timer',
    old='FrameLeafBudgetObserver',new='SampleLeafBudgetObserver',trace=True,diagnostic_counters=False,
    direct_call=True,mock_frames=False,replays=16,admissions=1280,reference_advances=1280,seconds=900,bytes=LIMIT,
    comparisons='all non-resource functional fields; complete meter; separately full resources with every difference retained',
    tests='S01-S10 in parent before spawning fresh matrix worker; no warmups or time repetitions',
    projection='Retain historical6330.087716s and class4760.361887s; apply weakest measured NEW/OLD ratio only as explicitly unproved transfer scenario; keep25pct and180+30+60s allowances. Also compare neutral80s context maxima,charging80s for48s; stack overhead transfer remains unknown.')


def history():
    paths=[q.BINDING,q.TEMPLATE,q.leaf.BINDING]
    for folder in (q.leaf.OUT,ROOT/'reports/s2uc/identity-stack-diagnosis-20261003-01',ROOT/'reports/s2uc/identity-stack-diagnosis-verification-20261003-01'):
        paths.extend(p for p in folder.rglob('*') if p.is_file())
    return {p.relative_to(ROOT).as_posix():q.old.sha(p) for p in paths}


def prepare():
    q.preparation_check();q.leaf.verify()
    if OUT.exists() or REPORT.exists():raise RuntimeError('PREPARATION_USED')
    q.old.save(PLAN,spec())
    q.old.save(BINDING,dict(code={n:q.old.sha(ROOT/n) for n in FILES},plan_sha256=q.old.sha(PLAN),history=history(),
        reused_code=q.verify()['code'],python=sys.version,executable_sha256=q.old.sha(sys.executable)))


def verify():
    b=q.old.read(BINDING);q.preparation_check()
    assert b['code']=={n:q.old.sha(ROOT/n) for n in FILES}
    assert b['plan_sha256']==q.old.sha(PLAN) and q.old.read(PLAN)==json.loads(json.dumps(spec()))
    assert b['history']==history() and b['reused_code']==q.verify()['code']
    assert b['python']==sys.version and b['executable_sha256']==q.old.sha(sys.executable)
    return b


def used():return sum(p.stat().st_size for folder in (OUT,REPORT) if folder.exists() for p in folder.rglob('*') if p.is_file())


def save(path,value):
    raw=(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
    if used()+len(raw)+65536>LIMIT:raise RuntimeError('EXPORT_LIMIT')
    with path.open('xb') as f:f.write(raw)


def matrix(folder,charged,deadline):
    def check():
        if time.monotonic_ns()>=deadline:raise TimeoutError('SAMPLE_LEAF_DEADLINE')
    rows=[];comparisons=[];base=q.BudgetObserver.trace
    try:
        for case in spec()['cases']:
            for arm in spec()['arms']:
                results={}
                for mode in spec()['orders'][case]:
                    check()
                    if used()+1048576>LIMIT:raise RuntimeError('EXPORT_HEADROOM')
                    t=time.perf_counter_ns();cpu=time.process_time_ns()
                    values=q.old.read(q.leaf.OUT/(case+'-source.json'));profile=q.old.digest(values)
                    prep=dict(wall_ns=time.perf_counter_ns()-t,cpu_ns=time.process_time_ns()-cpu)
                    assert len(values)==80 and all(len({id(x) for x in v})==48 for v in values)
                    partial={};method=FrameLeafBudgetObserver.trace if mode=='OLD' else SampleLeafBudgetObserver.trace
                    # Assign before timing. No patch/mock/function wrapper in the call.
                    q.BudgetObserver.trace=method
                    try:
                        start=time.perf_counter_ns();cpu=time.process_time_ns()
                        result=q.old.baseline_replay(values,profile,count=80,arm=arm,evidence=partial,check=check)
                        timing=dict(wall_ns=time.perf_counter_ns()-start,cpu_ns=time.process_time_ns()-cpu)
                    except BaseException:
                        save(OUT/f'{case}-{arm}-{mode}-partial.json',partial);raise
                    finally:q.BudgetObserver.trace=base
                    assert sys.gettrace() is None
                    q.old.resource_check(result)
                    assert result['censored_target']==81 and result['ema_cleared']
                    t=time.perf_counter_ns();save(OUT/f'{case}-{arm}-{mode}.json',result);export=time.perf_counter_ns()-t
                    row=dict(case=case,arm=arm,mode=mode,source_prepare=prep,replay=timing,export_wall_ns=export,
                        profile=profile,resources=result['resources'])
                    save(OUT/f'{case}-{arm}-{mode}-timing.json',row);rows.append(row);results[mode]=result
                old,new=results['OLD'],results['NEW']
                comparison=dict(case=case,arm=arm,semantic_equal=q.leaf.canonical(old)==q.leaf.canonical(new),
                    meter_equal=old['resources']['meter']==new['resources']['meter'],full_resources_equal=old['resources']==new['resources'],
                    resource_differences={k:dict(OLD=old['resources'].get(k),NEW=new['resources'].get(k)) for k in set(old['resources'])|set(new['resources']) if old['resources'].get(k)!=new['resources'].get(k)},
                    terminal_release=old['terminal_cleanup'] and new['terminal_cleanup'])
                save(OUT/f'{case}-{arm}-comparison.json',comparison);comparisons.append(comparison)
        save(OUT/'measurements.json',rows);save(OUT/'comparisons.json',comparisons)
        save(OUT/'worker-complete.json',dict(replays=16,admissions=1280,reference_advances=1280))
    except BaseException as exc:
        save(OUT/'matrix-error.json',dict(error=type(exc).__name__+':'+str(exc),completed=rows,comparisons=comparisons));raise


def assess():
    rows=q.old.read(OUT/'measurements.json');checks=q.old.read(OUT/'comparisons.json')
    assert len(rows)==16 and len(checks)==8
    pairs=[]
    for case in spec()['cases']:
        for arm in spec()['arms']:
            p={r['mode']:r for r in rows if r['case']==case and r['arm']==arm}
            old,new=p['OLD']['replay']['wall_ns']/1e9,p['NEW']['replay']['wall_ns']/1e9
            pairs.append(dict(case=case,arm=arm,old_seconds=old,new_seconds=new,old_cpu_s=p['OLD']['replay']['cpu_ns']/1e9,
                new_cpu_s=p['NEW']['replay']['cpu_ns']/1e9,new_old_ratio=new/old,reduction=1-new/old,
                old_heap=p['OLD']['resources']['additional_python_peak'],new_heap=p['NEW']['resources']['additional_python_peak']))
    totals={mode:sum(r['replay']['wall_ns'] for r in rows if r['mode']==mode)/1e9 for mode in ('OLD','NEW')}
    worst=max(p['new_old_ratio'] for p in pairs)
    prior=q.old.read(ROOT/'reports/s2uc/runtime-reconciliation-20261003-01/analysis.json')['plans']
    neutral={case:max(p['new_seconds'] for p in pairs if p['case']==case) for case in spec()['cases']}
    timing=dict(status='PROJECTION_NOT_GUARANTEE',worst_sample_new_old_ratio=worst,previous_plan_seconds=prior['previous_conservative'],
        previous_class_plan_seconds=prior['historical_stratified_with_unproven_speed_transfer'],
        updated_conservative_seconds=(prior['previous_conservative']-270)*worst+270,
        updated_class_seconds=(prior['historical_stratified_with_unproven_speed_transfer']-270)*worst+270,
        neutral_context_seconds=(16*neutral['N1']+112*neutral['N2'])*1.25+270,
        neutral_case_maxima=neutral,allowances=dict(contingency=1.25,administration=180,U=30,closure=60),limit=3600,
        uncertainty='Direct JSON call differs from full integration stack. Ratio transfer scales costs not all affected by the sample leaf. Neutral80 timings charged to48 too,not a worst-case bound. No extra integration replay authorized here.')
    summary=dict(pairs=pairs,total_seconds=totals,reduction=1-totals['NEW']/totals['OLD'],
        functional_and_meter_pass=all(c['semantic_equal'] and c['meter_equal'] and c['terminal_release'] for c in checks),
        full_resource_equality=all(c['full_resources_equal'] for c in checks),comparisons=checks,
        max_heap=max(r['resources']['additional_python_peak'] for r in rows),time_projection=timing)
    save(REPORT/'analysis.json',summary)
    return summary


def run():
    b=verify();REPORT.mkdir(exist_ok=False);save(REPORT/'binding.json',b)
    save(REPORT/'sources.json',{n:(ROOT/n).read_text(encoding='utf-8') for n in FILES})
    suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_s2uc_sample_leaf_observer')
    def ids(s):
        for x in s:
            if isinstance(x,unittest.TestSuite):yield from ids(x)
            else:yield x.id()
    names=list(ids(suite));stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    save(REPORT/'tests.json',dict(ids=names,count=r.testsRun,success=r.wasSuccessful(),errors=len(r.errors),failures=len(r.failures),skips=len(r.skipped),output=stream.getvalue()))
    from tests.test_s2uc_sample_leaf_observer import FACTS
    save(REPORT/'test-facts.json',FACTS)
    if not r.wasSuccessful() or r.skipped:raise RuntimeError('SAMPLE_LEAF_TESTS')
    q.supervise(OUT,0,matrix,900,30,metadata=dict(binding_sha256=q.old.sha(BINDING)))
    verify();q.leaf.verify();assess()
    save(REPORT/'verification.json',dict(old_bindings_unchanged=True,raster_replays=0,
        matrix_closure_sha256=q.old.sha(OUT/'closure.json'),files={p.relative_to(OUT).as_posix():dict(bytes=p.stat().st_size,sha256=q.old.sha(p)) for p in OUT.rglob('*') if p.is_file()}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('prepare','run'));args=parser.parse_args()
    if args.action=='prepare':prepare()
    else:run()
