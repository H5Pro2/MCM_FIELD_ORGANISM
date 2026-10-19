"""State-delta qualification of existing small cases only."""
import ctypes as C
from ctypes import wintypes as W
import gc
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


class Counters(C.Structure):
    _fields_ = [('cb', W.DWORD), ('faults', W.DWORD)] + [(n, C.c_size_t) for n in
        ('peak_ws','ws','paged_peak','paged','nonpaged_peak','nonpaged','pagefile','peak_pagefile','private')]


def memory(handle):
    p = C.WinDLL('psapi', use_last_error=True)
    p.GetProcessMemoryInfo.argtypes = [W.HANDLE,C.c_void_p,W.DWORD]
    data = Counters(); data.cb = C.sizeof(data)
    if not p.GetProcessMemoryInfo(handle,C.byref(data),data.cb): raise C.WinError(C.get_last_error())
    return dict(private_bytes=data.private, lifetime_peak_commit=data.peak_pagefile,
                working_set=data.ws)


def save(path, value):
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n',encoding='utf-8')


def worker(out, mode):
    import tracemalloc
    from tools import _s2uc_hx1_windows as win
    win.worker_membership()
    while not (out/'gate').exists(): time.sleep(.01)
    phases=[]; started=time.monotonic(); last=None
    handle=win.api().GetCurrentProcess()
    tracemalloc.start()
    def phase(name):
        nonlocal last
        now=time.monotonic()
        if last is not None:
            last['seconds']=now-last.pop('_start')
            last['end_process']=memory(handle)
            last['python_current'],last['python_peak']=tracemalloc.get_traced_memory()
        (out/'phase.txt').write_text(name,encoding='utf-8')
        tracemalloc.reset_peak()
        last=dict(name=name,_start=now,start_process=memory(handle));phases.append(last)
    phase('imports_and_initialization')
    import gzip
    from tools import _s2uc_ura1_delta_encode as codec
    from tools._s2uc_ura1_delta_decode import verify
    from tools._s2uc_ura1_capture_integrity import manifest
    from tools import _s2uc_ura1_delta_neutral as neutral
    from tests.test_s2uc_ura1 import D_ITEMS,LIFECYCLE
    result=dict(mode=mode,worker_pid=os.getpid(),membership=True,cases=[])
    if mode=='faults':
        phase('delta_fault_and_bound_tests')
        import unittest,io
        from tests.test_s2uc_ura1_delta import DeltaTests
        log=io.StringIO()
        class Result(unittest.TextTestResult):
            def __init__(self,*args,**kwargs):
                super().__init__(*args,**kwargs);self.ids=[]
            def addSuccess(self,test):
                self.ids.append(dict(id=test.id(),status='PASS'));super().addSuccess(test)
        tests=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Result).run(unittest.defaultTestLoader.loadTestsFromTestCase(DeltaTests))
        (out/'tests.txt').write_text(log.getvalue(),encoding='utf-8')
        if not tests.wasSuccessful():raise AssertionError(log.getvalue())
        result['tests']=tests.ids
    else:
        baseline=ROOT/'reports/s2uc/ura1-direct-development-20261015-01'
        sealed=json.loads((baseline/'closure.json').read_text())
        bound=baseline/'normal-corrected/worker.json'
        assert hashlib.sha256(bound.read_bytes()).hexdigest()==sealed['files']['normal-corrected/worker.json']['sha256']
        previous={c['name']:c for c in json.loads(bound.read_text())['cases']}
        for name,items in [('D_hand_case',D_ITEMS),('lifecycle_trace',LIFECYCLE)]:
            phase(name+'_source_read')
            expected={k:previous[name]['archive'][k] for k in ('original_bytes','original_sha256')}
            source=baseline/'normal-corrected'/(name+'.dag.json.gz')
            assert hashlib.sha256(source.read_bytes()).hexdigest()==sealed['files']['normal-corrected/'+source.name]['sha256']
            doc=json.loads(gzip.decompress(source.read_bytes())) if mode=='archive' else None
            path=out/(name+'.delta.json.gz')
            with codec.store(out) as owner:
                phase(name+'_capture_and_deltas')
                if mode=='archive':
                    nodes=doc['nodes']
                    paths={'/'+a+'/'+field for a in ('U','R') for field in ('events','internal','forecasts','rows')}
                    def expand(ref):
                        tag,body=nodes[ref]
                        if tag=='scalar':return body
                        if tag=='array':return [expand(v) for v in body]
                        return {k:expand(v) for k,v in body}
                    def capture(ref,location):
                        tag,body=nodes[ref]
                        if location in paths:
                            assert tag=='array'
                            seq=codec.collection()
                            for child in body:seq.append(expand(child))
                            return seq
                        if tag=='object':return {k:capture(v,location+'/'+k) for k,v in body}
                        if tag=='array':return [capture(v,location+'/'+str(i)) for i,v in enumerate(body)]
                        return body
                    record=capture(doc['root'],'')
                elif mode=='integration':record=neutral.pair(neutral.blocks(items),trace=True)
                else:raise ValueError('MODE')
                proof=manifest(record)
                save(out/(name+'-capture.json'),proof)
                details=dict(name=name,frames=record['U']['frames'],capture=owner.stats(),
                             events={a:dict(outer=len(record[a]['events']),internal=len(record[a]['internal'])) for a in ('U','R')})
                phase(name+'_encoding_and_file_output')
                info=codec.write_archive(record,path,expected)
                details['final_store']=owner.stats()
                phase(name+'_independent_decoder')
                try:decoded=verify(path.read_bytes(),proof,expected)
                except Exception:path.unlink(missing_ok=True);raise
                details['archive']=info;details['decoder']=decoded
                phase(name+'_cleanup');record=None;doc=None
            gc.collect()
            assert owner.closed and not owner.pool.nodes and not owner.deltas
            assert not list(out.glob('*.partial'))
            details['store_released']=True;result['cases'].append(details)
    phase('final_cleanup');gc.collect();phase('complete');phases.pop();tracemalloc.stop()
    result.update(phases=phases,seconds=time.monotonic()-started,status='PASS')
    save(out/'worker.json',result)


def supervise(out,mode):
    from tools import _s2uc_hx1_windows as win
    out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();job=win.install()
    # Cap process count as well as aggregate private commit, without breakaway.
    k=win.api();info=win.Extended()
    if not k.QueryInformationJobObject(win.HANDLE,9,C.byref(info),C.sizeof(info),None):raise C.WinError()
    info.basic.flags |= 0x8;info.basic.active=2
    if not k.SetInformationJobObject(win.HANDLE,9,C.byref(info),C.sizeof(info)):raise C.WinError()
    own=k.GetCurrentProcess();baseline=memory(own);samples={}; peak_sum=0
    with (out/'worker.log').open('w',encoding='utf-8') as log:
        child=subprocess.Popen([sys.executable,'-m','tools.s2uc_ura1_delta_qualify','worker',str(out),mode],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        try:
            win.verify_worker(int(child._handle))
            (out/'gate').write_text('verified',encoding='ascii')
            while child.poll() is None:
                if time.monotonic()-start>300:
                    child.kill();child.wait();raise TimeoutError('SMALL_CASE_300_SECONDS')
                try: phase=(out/'phase.txt').read_text(encoding='utf-8') or 'transition'
                except FileNotFoundError: phase='startup'
                a=memory(own);b=memory(int(child._handle));total=a['private_bytes']+b['private_bytes']
                peak_sum=max(peak_sum,total)
                entry=samples.setdefault(phase,dict(samples=0,supervisor_peak=0,worker_peak=0,combined_sample_peak=0))
                entry['samples']+=1
                entry['supervisor_peak']=max(entry['supervisor_peak'],a['private_bytes'])
                entry['worker_peak']=max(entry['worker_peak'],b['private_bytes'])
                entry['combined_sample_peak']=max(entry['combined_sample_peak'],total)
                time.sleep(.01)
            assert child.returncode==0,(out/'worker.log').read_text()
        finally:
            if child.poll() is None:child.kill();child.wait()
    final=win.snapshot();worker_result=json.loads((out/'worker.json').read_text())
    if mode!='memory':assert final['peak_job_committed_bytes']<=536870912
    save(out/'supervisor.json',dict(status='PASS',mode=mode,supervisor_pid=os.getpid(),worker_pid=child.pid,
         verified_same_job=True,active_process_limit=2,baseline=baseline,phases=samples,
         combined_sample_peak=peak_sum,job=final,seconds=time.monotonic()-start,
         worker_exitcode=child.returncode,worker_status=worker_result['status']))
    print(json.dumps(dict(mode=mode,job=final,seconds=time.monotonic()-start)))


if __name__=='__main__':
    action,path,mode=sys.argv[1:]
    if action=='worker':worker(Path(path),mode)
    else:supervise(Path(path),mode)
