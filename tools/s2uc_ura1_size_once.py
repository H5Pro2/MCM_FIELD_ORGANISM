"""Bound, exclusive, single periodic 1024-frame technical size test."""
import ctypes as C
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'reports/s2uc/ura1-size-neutral-20261015-01'
PREP=ROOT/'reports/s2uc/ura1-size-preparation-20261015-01'
LIMITS=dict(job=536870912,total_seconds=3600,worker_seconds=3540,gzip=524288,
            encoded=4194304,record=262144,nodes=65536,edges=262144,indices=65536,
            collections=16,dictionary=4194304,temp=67108864,export=67108864,
            preparation=8388608,source_total=2097152,source_case=32768,
            administration=2097152,closure=1048576)


def raw(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def treebytes(path):return sum(p.stat().st_size for p in Path(path).rglob('*') if p.is_file()) if Path(path).exists() else 0


def save(path,value):
    data=raw(value)
    if len(data)>LIMITS['closure']:raise ValueError('ADMIN_FILE_LIMIT')
    resolved=Path(path).resolve()
    if resolved.is_relative_to(PREP) and treebytes(PREP)+len(data)>LIMITS['preparation']:
        raise ValueError('PREPARATION_LIMIT')
    if resolved.is_relative_to(TARGET):
        admin=sum(p.stat().st_size for p in TARGET.rglob('*') if p.is_file() and not p.name.endswith(('.gz','.partial')))
        if admin+len(data)>LIMITS['administration']:raise ValueError('ADMINISTRATION_LIMIT')
    if treebytes(PREP)+treebytes(TARGET)+len(data)>LIMITS['export']:raise ValueError('EXPORT_LIMIT')
    Path(path).write_bytes(data)


def runtime():
    executable=Path(sys.executable).resolve()
    return dict(executable=str(executable),executable_sha256=sha(executable),version=sys.version,
                platform=platform.platform(),architecture=platform.machine(),
                dlls={p.name:sha(p) for p in executable.parent.glob('python*.dll')})


def material():
    from tests.test_s2uc_ura1 import D_ITEMS
    from tools._s2uc_ura1_direct_neutral import blocks
    if len(D_ITEMS)!=16:raise ValueError('BASE_BLOCK_COUNT')
    return blocks(D_ITEMS*16)


def validate_binding(path,check_call=False):
    path=Path(path).resolve();payload=path.read_bytes();digest=hashlib.sha256(payload).hexdigest()
    if path.with_suffix('.sha256').read_text().strip()!=digest:raise ValueError('PRESTART_HASH')
    b=json.loads(payload)
    if b['limits']!=LIMITS or b['target']!=str(TARGET):raise ValueError('BOUND_LIMIT_OR_TARGET')
    if b['runtime']!=runtime():raise ValueError('RUNTIME_BINDING')
    for name,value in b['files'].items():
        if sha(ROOT/name)!=value:raise ValueError('CODE_BINDING:'+name)
    if b['material']['frames']!=1024 or b['material']['sha256']!=hashlib.sha256(raw(material())).hexdigest():
        raise ValueError('MATERIAL_BINDING')
    if check_call and b['call']!=[sys.executable,'-m','tools.s2uc_ura1_size_once','run',str(path)]:raise ValueError('EXACT_CALL')
    return b,digest


def reserve(path,digest):
    # Exclusive marker, immutable even when process startup or execution fails.
    path=Path(path);path.mkdir(exist_ok=True)
    with (path/'START.json').open('xb') as target:
        target.write(raw(dict(prestart_sha256=digest,consumed=True,pid=os.getpid(),unix_time=time.time())))


def execute_case(out,values,*,small=False,inject_limit=None):
    from tools import _s2uc_ura1_size_engine as engine
    from tools import _s2uc_ura1_direct_archive as archive
    from tools._s2uc_ura1_capture_integrity import manifest,full_record_digest
    from tools._s2uc_ura1_integrity_decode import verify
    from tools.s2uc_ura1_resource_qualify import memory
    from tools import _s2uc_hx1_windows as win
    import tracemalloc
    expected=raw(values)
    if small:
        if not 4<=len(values)<=128:raise ValueError('PREPARATION_SMALL_ONLY')
    elif len(values)!=1024 or expected!=raw(material()):raise ValueError('FIXED_MATERIAL_ONLY')
    def validate(candidate):
        if raw(candidate)!=expected:raise ValueError('ENGINE_FIXED_MATERIAL')
    engine.VALIDATE=validate
    arms=[];base=engine.create
    def create(mode):
        arm=base(mode);arms.append(arm);return arm
    engine.create=create
    progress={};phases=[];last=None;started=time.monotonic();owner=None
    tracemalloc.start()
    handle=win.api().GetCurrentProcess()
    def phase(name):
        nonlocal last
        now=time.monotonic()
        if last:
            last['seconds']=now-last.pop('_start');last['process_end']=memory(handle)
            last['python_current'],last['python_peak']=tracemalloc.get_traced_memory()
        last=dict(name=name,_start=now,process_start=memory(handle));phases.append(last)
        tracemalloc.reset_peak();(out/'phase.txt').write_text(name,encoding='utf-8')
    def checkpoint(arm,mode,frame,stage):
        state=progress.setdefault(mode,dict(last_frame_started=0,last_frame_verified=0))
        if stage=='frame_before':state['last_frame_started']=frame
        elif stage=='frame_verified':state['last_frame_verified']=frame
        else:state['cleanup']=arm.closed and not any(arm.bank)
        if stage=='frame_verified' and frame%16==0:
            save(out/'progress.json',dict(arms=progress,store=owner.stats(),seconds=time.monotonic()-started))
    engine.CHECKPOINT=checkpoint
    result=dict(status='TECHNICAL_ABORT',research=False,small=small,frames_requested=len(values))
    partial=None
    try:
        phase('capture_references_events_and_anchors')
        with archive.store(out) as owner:
            if inject_limit is not None:owner.limits['dictionary']=inject_limit
            try:
                record=engine.pair(values,trace=True)
                proof=manifest(record)
                save(out/'capture-integrity.json',proof) # committed before encoding
                phase('envelope_checksum_and_encoding')
                envelope=full_record_digest(record)
                info=archive.write_archive(record,out/'case.dag.json.gz',envelope)
                phase('independent_decode')
                verified=verify((out/'case.dag.json.gz').read_bytes(),proof)
                save(out/'decoder.json',verified)
                result.update(status='COMPLETE_NEUTRAL_SIZE' if not small else 'PASS_SMALL',
                              archive=info,integrity=verified['status'],paired_equal=record['paired_equal'])
            except Exception as error:
                result.update(first_failure=type(error).__name__+':'+str(error),failure_phase=last['name'])
                partial=dict(collections=[dict(slot=i,**c.anchor()) for i,c in enumerate(owner.items)],
                             complete_record=False,reason='prefix anchors only; no successful size result')
                save(out/'partial-capture-integrity.json',partial)
            finally:
                result['store_before_cleanup']=owner.stats()
                result['events_by_collection']=[len(c) for c in owner.items]
                phase('cleanup')
                record=None
        gc.collect()
        result['store_released']=owner.closed and not owner.nodes and not owner.known
    finally:
        engine.create=base;engine.CHECKPOINT=lambda *args:None
        for arm in arms:
            if not arm.closed:arm._terminate()
        result['arm_cleanup']=[dict(closed=a.closed,bank_zero=not any(a.bank),
            originals_released=not a.arm._retained_many and a.arm._candidate is None) for a in arms]
        result['progress']=progress
        if result['status'] not in ('COMPLETE_NEUTRAL_SIZE','PASS_SMALL'):
            (out/'case.dag.json.gz').unlink(missing_ok=True)
        for p in out.glob('*.partial'):p.unlink()
        phase('complete');phases.pop();tracemalloc.stop()
        result.update(phases=phases,seconds=time.monotonic()-started,partial_files_remaining=len(list(out.glob('*.partial'))))
        save(out/'worker.json',result)
    return result


def worker(out,binding):
    from tools import _s2uc_hx1_windows as win
    win.worker_membership()
    while not (out/'gate').exists():time.sleep(.01)
    _,digest=validate_binding(binding)
    if json.loads((out/'START.json').read_text())['prestart_sha256']!=digest:raise ValueError('MARKER_BINDING')
    execute_case(out,material())


def child_job(out,command,*,worker_limit,total_limit,started=None):
    from tools import _s2uc_hx1_windows as win
    from tools.s2uc_ura1_resource_qualify import memory
    started=time.monotonic() if started is None else started
    k=win.api();own=k.GetCurrentProcess();baseline=memory(own)
    peaks={};child=None;failure=None;membership=False
    with (out/'worker.log').open('w',encoding='utf-8') as log:
        try:
            child=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            worker_start=time.monotonic();win.verify_worker(int(child._handle));membership=True
            (out/'gate').write_text('verified',encoding='ascii')
            while child.poll() is None:
                now=time.monotonic()
                if now-started>total_limit:failure='TOTAL_TIMEOUT';break
                if now-worker_start>worker_limit:failure='WORKER_TIMEOUT';break
                if treebytes(PREP)+treebytes(TARGET)>LIMITS['export']:failure='EXPORT_LIMIT';break
                try:label=(out/'phase.txt').read_text() or 'transition'
                except FileNotFoundError:label='startup'
                a=memory(own);b=memory(int(child._handle))
                item=peaks.setdefault(label,dict(supervisor=0,worker=0,combined=0,samples=0))
                item['supervisor']=max(item['supervisor'],a['private_bytes'])
                item['worker']=max(item['worker'],b['private_bytes'])
                item['combined']=max(item['combined'],a['private_bytes']+b['private_bytes']);item['samples']+=1
                time.sleep(.02)
        except Exception as error:failure='START_OR_SUPERVISOR:'+str(error)
        finally:
            if child and child.poll() is None:child.kill();child.wait()
    if child and child.returncode!=0 and failure is None:failure='WORKER_EXIT:'+str(child.returncode)
    result=dict(failure=failure,baseline=baseline,phases=peaks,job=win.snapshot(),seconds=time.monotonic()-started,
                worker_exitcode=None if child is None else child.returncode,worker_terminated=child is None or child.poll() is not None,
                same_job_verified=membership,active_process_limit=2)
    save(out/'supervisor.json',result)
    return result


def install_job():
    from tools import _s2uc_hx1_windows as win
    win.install();k=win.api();info=win.Extended()
    if not k.QueryInformationJobObject(win.HANDLE,9,C.byref(info),C.sizeof(info),None):raise C.WinError()
    info.basic.flags|=0x8;info.basic.active=2
    if not k.SetInformationJobObject(win.HANDLE,9,C.byref(info),C.sizeof(info)):raise C.WinError()


def run(binding):
    started=time.monotonic();b,digest=validate_binding(binding,True)
    install_job();reserve(TARGET,digest)
    info=child_job(TARGET,[sys.executable,'-m','tools.s2uc_ura1_size_once','worker',str(TARGET),str(Path(binding).resolve())],
                   worker_limit=LIMITS['worker_seconds'],total_limit=LIMITS['total_seconds'],started=started)
    result=json.loads((TARGET/'worker.json').read_text()) if (TARGET/'worker.json').exists() else dict(status='TECHNICAL_ABORT',first_failure=info['failure'])
    if info['failure']:result['status']='TECHNICAL_ABORT';result.setdefault('first_failure',info['failure'])
    if info['job']['peak_job_committed_bytes']>LIMITS['job']:
        result['status']='TECHNICAL_ABORT';result.setdefault('first_failure','JOB_MEMORY_LIMIT')
    if result['status']!='COMPLETE_NEUTRAL_SIZE':
        (TARGET/'case.dag.json.gz').unlink(missing_ok=True)
        for p in TARGET.glob('*.partial'):p.unlink()
    result.update(prestart_sha256=digest,authorization_consumed=True,retry_allowed=False,
                  supervisor=info,export_bytes_before_final=treebytes(PREP)+treebytes(TARGET),research_ready=False)
    save(TARGET/'result.json',result)
    print(json.dumps(dict(status=result['status'],first_failure=result.get('first_failure'),prestart_sha256=digest)))


if __name__=='__main__':
    action=sys.argv[1]
    if action=='run':run(sys.argv[2])
    elif action=='worker':worker(Path(sys.argv[2]),Path(sys.argv[3]))
    elif action=='timeout_probe':time.sleep(10)
    elif action=='qualification_worker':
        import unittest,io
        from tests.test_s2uc_ura1_size_once import SizeTests
        out=Path(sys.argv[2]);log=io.StringIO()
        suite=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SizeTests))
        (out/'tests.txt').write_text(log.getvalue(),encoding='utf-8')
        if not suite.wasSuccessful():raise SystemExit(log.getvalue())
        save(out/'tests.json',dict(status='PASS',tests=suite.testsRun))
    elif action=='qualify':
        out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=False);install_job()
        failure=out/'start-failure';failure.mkdir();reserve(failure,'0'*64)
        rejected=child_job(failure,[str(out/'nonexistent-python.exe')],worker_limit=1,total_limit=2)
        if not rejected['failure'].startswith('START_OR_SUPERVISOR:'):raise AssertionError('START_FAILURE')
        if not (failure/'START.json').exists():raise AssertionError('MARKER_NOT_CONSUMED')
        timeout=out/'timeout';timeout.mkdir()
        proof=child_job(timeout,[sys.executable,'-m','tools.s2uc_ura1_size_once','timeout_probe'],worker_limit=.1,total_limit=10)
        if proof['failure']!='WORKER_TIMEOUT' or not proof['worker_terminated']:raise AssertionError('TIMEOUT_CLEANUP')
        total=out/'total-timeout';total.mkdir()
        proof=child_job(total,[sys.executable,'-m','tools.s2uc_ura1_size_once','timeout_probe'],worker_limit=10,total_limit=.1)
        if proof['failure']!='TOTAL_TIMEOUT' or not proof['worker_terminated']:raise AssertionError('TOTAL_TIMEOUT_CLEANUP')
        tests=out/'tests';tests.mkdir()
        result=child_job(tests,[sys.executable,'-m','tools.s2uc_ura1_size_once','qualification_worker',str(tests)],worker_limit=300,total_limit=310)
        if result['failure']:raise AssertionError((tests/'worker.log').read_text())
        print('PASS_PREPARATION_SMALL_AND_TIMEOUT')
