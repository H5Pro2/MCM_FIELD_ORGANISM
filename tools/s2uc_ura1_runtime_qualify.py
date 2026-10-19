"""Bounded runtime qualification; one archive-only large check."""
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
TARGET=ROOT/'reports/s2uc/ura1-runtime-development-20261015-01'
PREP=TARGET
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


def binding():
    p=TARGET/'binding.json';b=json.loads(p.read_text())
    if sha(p)!=p.with_suffix('.sha256').read_text().strip():raise ValueError('BINDING_HASH')
    if b['runtime']!=runtime() or b['limits']!=LIMITS:raise ValueError('RUNTIME_LIMITS')
    for name,h in b['files'].items():
        if sha(ROOT/name)!=h:raise ValueError('FILE_BINDING:'+name)
    return sha(p)


def worker(out,mode):
    import tracemalloc
    from tools import _s2uc_hx1_windows as win
    from tools.s2uc_ura1_resource_qualify import memory
    win.worker_membership()
    while not (out/'gate').exists():time.sleep(.01)
    bound=binding();phases=[];last=None;start=time.monotonic();tracemalloc.start()
    def phase(name):
        nonlocal last
        now=time.monotonic()
        if last:
            last['seconds']=now-last.pop('_start')
            last['process_end']=memory(win.api().GetCurrentProcess())
            last['python_current'],last['python_peak']=tracemalloc.get_traced_memory()
        tracemalloc.reset_peak();last=dict(name=name,_start=now);phases.append(last)
        (out/'phase.txt').write_text(name)
    result=dict(mode=mode,binding_sha256=bound,instrumentation='tracemalloc throughout; unchanged capture profiling; supervisor 20ms',cases=[])
    if mode=='tests':
        import io,unittest
        from tests.test_s2uc_ura1_delta_fast import FastTests
        phase('focused_tests');log=io.StringIO()
        tests=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FastTests))
        (out/'tests.txt').write_text(log.getvalue(),encoding='utf-8')
        if not tests.wasSuccessful():raise AssertionError(log.getvalue())
        result['tests']=tests.testsRun
    elif mode=='small':
        from tools import _s2uc_ura1_delta_neutral as neutral
        from tools import _s2uc_ura1_delta_encode as codec
        from tools._s2uc_ura1_delta_fast_decode import verify
        from tools._s2uc_ura1_delta_fused import finish,live_sequences
        from tools._s2uc_ura1_capture_integrity import manifest
        from tests.test_s2uc_ura1 import D_ITEMS,LIFECYCLE
        previous=json.loads((ROOT/'reports/s2uc/ura1-delta-development-20261015-01/integration/worker.json').read_text())
        old={x['name']:x for x in previous['cases']}
        for name,items in [('D_hand_case',D_ITEMS),('lifecycle_trace',LIFECYCLE)]:
            values=neutral.blocks(items)
            with codec.store(out) as owner:
                phase(name+'_capture_references')
                u=neutral.run_arm(values,'U',trace=True);r=neutral.run_arm(values,'R',trace=True)
                record=dict(neutral_only=True,source=[list(v) for v in values],U=u,R=r,paired_equal=True,differences=[],performance_claim=False)
                phase(name+'_fused_pair_envelope')
                expected,checks=finish(record,live_sequences(record),build=True)
                assert expected=={k:old[name]['archive'][k] for k in ('original_bytes','original_sha256')}
                proof=manifest(record)
                prior=json.loads((ROOT/'reports/s2uc/ura1-delta-development-20261015-01/integration'/f'{name}-capture.json').read_text())
                assert proof==prior
                save(out/(name+'-capture.json'),proof)
                phase(name+'_encoding_output');path=out/(name+'.delta.json.gz')
                archive=codec.write_archive(record,path,expected)
                phase(name+'_independent_decoder');decoded=verify(path.read_bytes(),proof,expected)
                result['cases'].append(dict(name=name,archive=archive,decoder=decoded,checks=checks,store=owner.stats()))
                phase(name+'_cleanup');record=None;u=None;r=None
            gc.collect();assert owner.closed and not owner.pool.nodes and not owner.deltas
    elif mode=='archive':
        # This branch never imports a policy, a reference engine or a source generator.
        from tools._s2uc_ura1_delta_fast_decode import Reader,verify
        from tools._s2uc_ura1_delta_fused import finish,archive_sequences
        if json.loads((out/'START.json').read_text())['binding_sha256']!=bound:raise ValueError('MARKER_BINDING')
        source=ROOT/'reports/s2uc/ura1-delta-size-neutral-20261015-01'
        phase('archive_read_and_table_validation')
        data=(source/'case.delta.json.gz').read_bytes();proof=json.loads((source/'capture-integrity.json').read_text())
        reader=Reader(data);record=reader.value(reader.doc['root'])
        phase('archive_fused_pair_envelope')
        expected,checks=finish(record,archive_sequences(reader,record))
        assert expected=={k:reader.doc[k] for k in ('original_bytes','original_sha256')}
        reader=None;record=None;gc.collect()
        phase('archive_independent_decoder');decoded=verify(data,proof,expected)
        assert decoded==json.loads((source/'decoder.json').read_text())
        phase('archive_cleanup');data=None;gc.collect()
        result['cases'].append(dict(name='existing_1024_archive',decoder=decoded,checks=checks,policies_executed=False))
    else:raise ValueError('MODE')
    phase('complete');phases.pop();tracemalloc.stop()
    result.update(status='PASS',phases=phases,seconds=time.monotonic()-start,partial_files_remaining=len(list(out.glob('*.partial'))))
    save(out/'worker.json',result)


def supervise(mode):
    if mode not in ('tests','small','archive'):raise ValueError('MODE')
    digest=binding();out=TARGET/mode
    # Every invocation is exclusive. Only archive reserves the large-check authorization.
    out.mkdir(exist_ok=False);started=time.monotonic();install_job()
    if mode=='archive':
        with (out/'START.json').open('xb') as f:f.write(raw(dict(consumed=True,binding_sha256=digest,policies_executed=False)))
    result=child_job(out,[sys.executable,'-m','tools.s2uc_ura1_runtime_qualify','worker',mode],worker_limit=3540 if mode=='archive' else 300,total_limit=3600 if mode=='archive' else 310,started=started)
    if result['failure'] or result['job']['peak_job_committed_bytes']>LIMITS['job']:raise RuntimeError(result)
    print(json.dumps(dict(mode=mode,status='PASS',seconds=result['seconds'],job=result['job'])))


if __name__=='__main__':
    action,mode=sys.argv[1:]
    if action=='worker':worker(TARGET/mode,mode)
    elif action=='run':supervise(mode)
    else:raise ValueError('ACTION')


