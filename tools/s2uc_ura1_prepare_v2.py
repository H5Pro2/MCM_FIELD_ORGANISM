"""URA1 16-hour contract: preparation and separately authorized future research."""
import gc
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from tools._s2uc_ura1_v2_series import LIMITS,Ledger,raw,execute,policy_case
from tools.s2uc_ura1_runtime_qualify import runtime,sha,install_job

ROOT=Path(__file__).resolve().parents[1]
PREP=ROOT/'reports/s2uc/ura1-v2-preparation-20261015-01'
TARGET=ROOT/'reports/s2uc/ura1-comparison-v2-time16h'
AUTH=PREP/'authorization.json'


def treebytes(folder):return sum(p.stat().st_size for p in Path(folder).rglob('*') if p.is_file())


def validate_binding(path):
    path=Path(path).resolve();b=json.loads(path.read_text());digest=sha(path)
    if path.with_suffix('.sha256').read_text().strip()!=digest:raise ValueError('PRESTART_HASH')
    if b['limits']!=LIMITS or b['runtime']!=runtime() or b['target']!=str(TARGET):raise ValueError('PRESTART_SCOPE')
    if b['call']!=[sys.executable,'-m','tools.s2uc_ura1_prepare_v2','run',str(path),str(AUTH)]:raise ValueError('PRESTART_CALL')
    for name,h in b['files'].items():
        if sha(ROOT/name)!=h:raise ValueError('FILE_BINDING:'+name)
    return b,digest


def authorization(path,digest):
    if Path(path).resolve()!=AUTH:raise PermissionError('AUTH_PATH')
    a=json.loads(Path(path).read_text())
    if a!=dict(kind='URA1_RESEARCH_ONCE_V2',prestart_sha256=digest,allow_research=True):raise PermissionError('RESEARCH_NOT_AUTHORIZED')


def validate_admission(auth,folder):
    _,digest=validate_binding(PREP/'prestart.json');authorization(auth,digest)
    if Path(folder).resolve()!=TARGET:raise PermissionError('RESEARCH_TARGET')
    marker=json.loads((TARGET/'START.json').read_text())
    if marker['prestart_sha256']!=digest or marker.get('consumed') is not True or not (TARGET/'gate').exists():raise PermissionError('RESEARCH_MARKER')


def research_worker(started):
    from tools import _s2uc_hx1_windows as win
    from tools import _s2uc_ura1_v2_sources as src
    from tools import _s2uc_ura1_v2_source_reference as sr
    from tools import _s2uc_ura1_v2_stats as stats
    from tools import _s2uc_ura1_v2_stats_reference as ref
    win.worker_membership()
    while not (TARGET/'gate').exists():time.sleep(.01)
    validate_admission(AUTH,TARGET);ledger=Ledger(TARGET,started,treebytes(PREP));permit=src.admit(AUTH,TARGET)
    result=dict(status='TECHNICAL_ABORT',research=True,complete_cases=0)
    try:
        # All 32 independently checked sources are sealed before the first policy.
        manifest=[]
        for r in range(1,33):
            ledger.check();v=src.generate(r,neutral=False,permit=permit);sr.verify(v,r,neutral=False,permit=permit)
            name=f'URA1-{r:02d}-D-source.json';h=ledger.write(name,v,'source')
            manifest.append(dict(replicate=r,path=name,sha256=h))
        ledger.write('sources-manifest.json',dict(entries=manifest,all_before_policy=True,namespace='MCM-URA1/source/v1'))
        cases=[]
        for e in manifest:
            p=TARGET/e['path']
            if sha(p)!=e['sha256']:raise ValueError('SOURCE_CHANGED')
            cases.append((e['replicate'],json.loads(p.read_text())))
        reports=execute(cases,lambda n,v,l:policy_case(n,v,l,neutral=False),ledger,list(range(1,33)))
        result['complete_cases']=len(reports);data=(PREP/'bootstrap.bin').read_bytes()
        ledger.check();ref.verify_matrix(data);summary=stats.aggregate(reports,data,ledger.check)
        ref.verify(reports,data,summary,ledger.check);ledger.write('statistics.json',summary)
        ledger.check();result.update(status='COMPLETE',reference_equal=True,archive_integrity=True,cleanup=True)
    except Exception as e:result.update(first_failure=type(e).__name__+':'+str(e))
    finally:
        for p in TARGET.glob('*.partial'):p.unlink()
        # The supervisor always supplies an abort record if a deadline prevents this write.
        ledger.write('worker.json',result)


def supervise_worker(out,command,started,deadline,prep):
    from tools import _s2uc_hx1_windows as win
    from tools.s2uc_ura1_resource_qualify import memory
    own=win.api().GetCurrentProcess();peak=0;phase_peaks={};failure=None;child=None
    with (out/'worker.log').open('w',encoding='utf-8') as log:
        try:
            child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            win.verify_worker(int(child._handle));(out/'gate').write_text('verified')
            while child.poll() is None:
                if time.monotonic()-started>deadline:failure='WORKER_DEADLINE';break
                if treebytes(out)+treebytes(prep)>LIMITS['export']:failure='EXPORT_LIMIT';break
                if sum(p.stat().st_size for p in out.glob('*.partial'))>LIMITS['temp']:failure='TEMP_LIMIT';break
                a=memory(own);b=memory(int(child._handle));total=a['private_bytes']+b['private_bytes'];peak=max(peak,total)
                phase=(out/'phase.txt').read_text() if (out/'phase.txt').exists() else 'worker'
                phase_peaks[phase]=max(phase_peaks.get(phase,0),total);time.sleep(.05)
        except Exception as e:failure='SUPERVISOR:'+str(e)
        finally:
            if child and child.poll() is None:child.kill();child.wait()
    if child and child.returncode and failure is None:failure='WORKER_EXIT:'+str(child.returncode)
    snap=win.snapshot()
    if snap['peak_job_committed_bytes']>LIMITS['job']:failure='JOB_LIMIT'
    return dict(failure=failure,worker_exitcode=None if child is None else child.returncode,
        worker_terminated=child is None or child.poll() is not None,job=snap,combined_sample_peak=peak,
        phase_sample_peaks=phase_peaks,seconds=time.monotonic()-started,same_job_verified=child is not None and (out/'gate').exists())


def run(binding,auth):
    started=time.monotonic();install_job();_,digest=validate_binding(binding);authorization(auth,digest)
    if time.monotonic()-started>LIMITS['worker_seconds']:raise TimeoutError('ADMISSION_DEADLINE')
    TARGET.mkdir(exist_ok=False)
    with (TARGET/'START.json').open('xb') as f:f.write(raw(dict(consumed=True,prestart_sha256=digest)))
    info=supervise_worker(TARGET,[sys.executable,'-m','tools.s2uc_ura1_prepare_v2','research_worker',str(started)],started,LIMITS['worker_seconds'],PREP)
    ledger=Ledger(TARGET,started,treebytes(PREP));ledger.final=True
    # Restore category accounting for all worker files before finalization.
    for p in TARGET.iterdir():
        if p.is_file() and not p.name.endswith('.partial'):
            category='source' if p.name.endswith('-source.json') else 'archive' if p.name.endswith('.gz') else 'admin'
            ledger.entries[str(p.resolve())]=(category,p.stat().st_size)
    for p in TARGET.glob('*.partial'):p.unlink()
    ledger.check();result=json.loads((TARGET/'worker.json').read_text()) if (TARGET/'worker.json').exists() else dict(status='TECHNICAL_ABORT')
    if info['failure']:result.update(status='TECHNICAL_ABORT',first_failure=info['failure'])
    result.update(supervisor=info,authorization_consumed=True,retry_allowed=False,total_seconds=time.monotonic()-started)
    ledger.write('result.json',result,'closure')
    entries={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in TARGET.iterdir() if p.is_file()}
    ledger.write('closure.json',dict(files=entries,prestart_sha256=digest,status=result['status']),'closure');ledger.check()
    print(json.dumps(dict(status=result['status'],seconds=time.monotonic()-started)))


def qualify_worker(out):
    import tracemalloc,io,unittest
    from tools import _s2uc_hx1_windows as win
    from tools.s2uc_ura1_resource_qualify import memory
    from tools import _s2uc_ura1_v2_sources as src
    from tools import _s2uc_ura1_v2_source_reference as sr
    from tools import _s2uc_ura1_v2_stats as stats
    from tools import _s2uc_ura1_v2_stats_reference as ref
    from tests.test_s2uc_ura1_prepare_v2 import PreparationTests,artificial_reports
    win.worker_membership()
    while not (out/'gate').exists():time.sleep(.01)
    tracemalloc.start();phases=[];last=None;start=time.monotonic()
    def phase(name):
        nonlocal last
        now=time.monotonic()
        if last:
            last['seconds']=now-last.pop('_start');last['python_current'],last['python_peak']=tracemalloc.get_traced_memory()
            last['process']=memory(win.api().GetCurrentProcess())
        tracemalloc.reset_peak();last=dict(name=name,_start=now);phases.append(last);(out/'phase.txt').write_text(name)
    phase('matrix_generation');matrix=stats.matrix_bytes()
    with (PREP/'bootstrap.bin').open('xb') as f:f.write(matrix)
    phase('matrix_independent_verification');ref.verify_matrix(matrix)
    phase('neutral_sources_two_orientations')
    for r in (1,2):
        value=src.generate(r);sr.verify(value,r)
        (out/f'neutral-source-{r}.json').write_bytes(raw(value))
    phase('focused_tests');log=io.StringIO()
    tests=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PreparationTests))
    (out/'tests.txt').write_text(log.getvalue(),encoding='utf-8')
    if not tests.wasSuccessful():raise AssertionError(log.getvalue())
    phase('artificial_statistics_input');reports=artificial_reports()
    phase('rational_statistics');summary=stats.aggregate(reports,matrix)
    phase('independent_statistics');ref.verify(reports,matrix,summary)
    phase('closure_serialization_and_hash');data=raw(summary)
    if len(data)>LIMITS['administration']:raise ValueError('STATISTICS_EXPORT_LIMIT')
    (out/'artificial-statistics.json').write_bytes(data)
    check=hashlib.sha256(data).hexdigest();json.loads(data)
    phase('cleanup');reports=None;summary=None;data=None;gc.collect();phase('complete');phases.pop();tracemalloc.stop()
    result=dict(status='PASS_PREPARATION',tests=tests.testsRun,phases=phases,seconds=time.monotonic()-start,
        matrix_bytes=len(matrix),matrix_sha256=hashlib.sha256(matrix).hexdigest(),synthetic_statistics_sha256=check,
        research_sources_generated=0,large_policy_runs=0,neutral_policy_cases=2,research_started=False)
    (out/'worker.json').write_bytes(raw(result))


if __name__=='__main__':
    action=sys.argv[1]
    if action=='qualify':
        out=PREP/'qualification';out.mkdir(parents=True,exist_ok=False);started=time.monotonic();install_job()
        info=supervise_worker(out,[sys.executable,'-m','tools.s2uc_ura1_prepare_v2','qualification_worker'],started,3540,PREP)
        (out/'supervisor.json').write_bytes(raw(info))
        if info['failure']:raise RuntimeError(info)
        fault=PREP/'timeout-probe';fault.mkdir(exist_ok=False)
        timeout=supervise_worker(fault,[sys.executable,'-m','tools.s2uc_ura1_prepare_v2','timeout_probe'],time.monotonic(),.1,PREP)
        (fault/'supervisor.json').write_bytes(raw(timeout))
        if timeout['failure']!='WORKER_DEADLINE' or not timeout['worker_terminated']:raise AssertionError('WATCHDOG_TIMEOUT')
        fault=PREP/'start-failure-probe';fault.mkdir(exist_ok=False)
        failure=supervise_worker(fault,[str(fault/'missing-python.exe')],time.monotonic(),1,PREP)
        (fault/'supervisor.json').write_bytes(raw(failure))
        if not failure['failure'].startswith('SUPERVISOR:') or not failure['worker_terminated']:raise AssertionError('START_FAILURE')
        print(json.dumps(info))
    elif action=='qualification_worker':qualify_worker(PREP/'qualification')
    elif action=='run':run(sys.argv[2],sys.argv[3])
    elif action=='research_worker':research_worker(float(sys.argv[2]))
    elif action=='timeout_probe':time.sleep(10)
    else:raise ValueError('ACTION')
