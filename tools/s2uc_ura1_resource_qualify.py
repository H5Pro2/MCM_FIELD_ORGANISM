"""Small neutral resource qualification: one supervisor plus one Windows worker."""
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
    from tools import _s2uc_ura1_resource_neutral as neutral
    from tools._s2uc_ura1_stream_archive import store,write_archive
    from tools._s2uc_ura1_archive_decode import read
    from tests.test_s2uc_ura1 import D_ITEMS,LIFECYCLE
    result=dict(mode=mode,worker_pid=os.getpid(),membership=True,cases=[])
    original_create=neutral.create
    def create(arm):
        phase('constructor_'+arm)
        value=original_create(arm)
        phase('processing_'+arm)
        return value
    neutral.create=create
    if mode=='memory':
        phase('native_memory_rejection')
        k=win.api();k.VirtualAlloc.argtypes=[C.c_void_p,C.c_size_t,W.DWORD,W.DWORD];k.VirtualAlloc.restype=C.c_void_p
        k.VirtualFree.argtypes=[C.c_void_p,C.c_size_t,W.DWORD]
        pointer=k.VirtualAlloc(None,600*1048576,0x3000,0x04)
        error=C.get_last_error()
        if pointer:
            k.VirtualFree(pointer,0,0x8000);raise AssertionError('MEMORY_NOT_REJECTED')
        result['allocation_rejected']=True;result['windows_error']=error
    else:
        cases=[('D_hand_case',D_ITEMS),('lifecycle_trace',LIFECYCLE)] if mode=='normal' else [('fault_case',LIFECYCLE[:2])]
        for name,items in cases:
            phase(name+'_material')
            values=neutral.blocks(items)
            path=out/(name+'.dag.json.gz')
            rejected=False
            with store(out) as spool:
                phase(name+'_arms_references_observer')
                record=neutral.pair(values,trace=True)
                details=dict(name=name,frames=len(values),events={a:dict(outer=len(record[a]['events']),internal=len(record[a]['internal'])) for a in ('U','R')},
                             spool_bytes=spool.bytes,max_record_bytes=spool.max_record,
                             cleanup=all(record[a]['cleanup'] for a in ('U','R')))
                phase(name+'_encoder_and_file_output')
                try:
                    meta=write_archive(record,path,fault=mode=='encoder')
                    phase(name+'_stream_decoder')
                    if mode=='decoder':
                        read(path.read_bytes(),'0'*64,meta['original_bytes'])
                    else:
                        decoded=read(path.read_bytes(),meta['original_sha256'],meta['original_bytes'])
                        details['archive']=meta;details['decoder']=decoded
                except ValueError as error:
                    expected='INJECTED_ENCODER' if mode=='encoder' else 'BINDING' if mode=='decoder' else None
                    if str(error)!=expected: raise
                    rejected=True;details['rejected']=str(error)
                phase(name+'_cleanup')
                del record,values
            gc.collect()
            assert not spool.path.exists()
            assert not Path(str(path)+'.partial').exists()
            if mode in ('encoder','decoder'):
                assert rejected
                if path.exists(): path.unlink()
            details['spool_removed']=True;result['cases'].append(details)
    phase('final_cleanup');gc.collect()
    phase('complete')
    phases.pop();tracemalloc.stop()
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
        child=subprocess.Popen([sys.executable,'-m','tools.s2uc_ura1_resource_qualify','worker',str(out),mode],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
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
