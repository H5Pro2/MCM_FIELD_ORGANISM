"""Narrow neutral Windows-memory probe; no source/policy/replay imports."""
import ctypes as C
from ctypes import wintypes as W
import json
import multiprocessing as MP
import os
from pathlib import Path
import sys
from tools import _s2uc_hx1_windows as win

class Counters(C.Structure):
    _fields_=[('cb',W.DWORD),('faults',W.DWORD)]+[(s,C.c_size_t) for s in
        ('peak_working_set','working_set','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile','private')]

class Region(C.Structure):
    _fields_=[('base',C.c_void_p),('allocation_base',C.c_void_p),('allocation_protect',W.DWORD),
        ('partition',W.WORD),('size',C.c_size_t),('state',W.DWORD),('protect',W.DWORD),('type',W.DWORD)]

class Members(C.Structure):
    _fields_=[('assigned',W.DWORD),('listed',W.DWORD),('pids',C.c_size_t*16)]

class Performance(C.Structure):
    _fields_=[('cb',W.DWORD)]+[(n,C.c_size_t) for n in
        ('commit_total','commit_limit','commit_peak','physical_total','physical_available',
         'system_cache','kernel_total','kernel_paged','kernel_nonpaged','page_size')]+[
        ('handles',W.DWORD),('processes',W.DWORD),('threads',W.DWORD)]

def system_commit():
    k=api();k.K32GetPerformanceInfo.argtypes=[C.c_void_p,W.DWORD]
    v=Performance();v.cb=C.sizeof(v)
    if not k.K32GetPerformanceInfo(C.byref(v),C.sizeof(v)):raise C.WinError(C.get_last_error())
    return dict(total_bytes=v.commit_total*v.page_size,limit_bytes=v.commit_limit*v.page_size,
                available_bytes=(v.commit_limit-v.commit_total)*v.page_size)

def api():
    k=win.api()
    k.K32GetProcessMemoryInfo.argtypes=[W.HANDLE,C.c_void_p,W.DWORD]
    k.VirtualAlloc.argtypes=[C.c_void_p,C.c_size_t,W.DWORD,W.DWORD];k.VirtualAlloc.restype=C.c_void_p
    k.VirtualFree.argtypes=[C.c_void_p,C.c_size_t,W.DWORD]
    k.VirtualQuery.argtypes=[C.c_void_p,C.c_void_p,C.c_size_t];k.VirtualQuery.restype=C.c_size_t
    return k

def memory(handle=None):
    k=api();v=Counters();v.cb=C.sizeof(v)
    if not k.K32GetProcessMemoryInfo(handle or k.GetCurrentProcess(),C.byref(v),C.sizeof(v)):
        raise C.WinError(C.get_last_error())
    return {name:getattr(v,name) for name in ('private','pagefile','peak_pagefile','working_set')}

def region(address):
    v=Region();k=api()
    if k.VirtualQuery(address,C.byref(v),C.sizeof(v))!=C.sizeof(v):raise C.WinError(C.get_last_error())
    return {n:getattr(v,n) for n in ('size','state','protect','type')}

def details(worker=None):
    k=api();v=win.Extended();m=Members()
    if not k.QueryInformationJobObject(win.HANDLE,9,C.byref(v),C.sizeof(v),None):raise C.WinError(C.get_last_error())
    if not k.QueryInformationJobObject(win.HANDLE,3,C.byref(m),C.sizeof(m),None):raise C.WinError(C.get_last_error())
    k.IsProcessInJob.argtypes=[W.HANDLE,W.HANDLE,C.POINTER(W.BOOL)]
    def member(h):
        yes=W.BOOL()
        if not k.IsProcessInJob(h,win.HANDLE,C.byref(yes)):raise C.WinError(C.get_last_error())
        return bool(yes.value)
    return dict(flags=v.basic.flags,job_limit=v.job_limit,process_limit=v.process_limit,
        peak_job=v.peak_job,peak_process=v.peak_process,pids=list(m.pids)[:m.listed],
        supervisor_member=member(k.GetCurrentProcess()),worker_member=member(worker) if worker else None,
        supervisor=memory(),worker=memory(worker) if worker else None)

def child(conn,mode):
    k=api();small=large=None
    def emit(stage,**extra):
        conn.send(dict(stage=stage,pid=os.getpid(),memory=memory(),**extra));return conn.recv()
    try:
        emit('ready')
        small=k.VirtualAlloc(None,8*1048576,0x3000,4)
        if not small:raise C.WinError(C.get_last_error())
        C.memset(small,1,4096)
        requested=emit('small_committed',region=region(small))
        if mode=='python':
            before=memory();system=system_commit();rejected=False
            assert system['available_bytes']>600*1048576
            try:
                payload=bytearray(600*1048576)
                del payload
            except MemoryError:rejected=True
            emit('python_attempt',request=600*1048576,rejected=rejected,before=before,system_before=system)
            if not rejected:raise AssertionError('PYTHON_ALLOCATION_NOT_REJECTED')
        else:
            size=requested if mode=='aggregate' else 600*1048576
            large=k.VirtualAlloc(None,size,0x2000,4)
            if not large:raise C.WinError(C.get_last_error())
            emit('reserved',request=size,region=region(large))
            before=memory();system=system_commit()
            assert system['available_bytes']>size
            C.set_last_error(0)
            committed=k.VirtualAlloc(large,size,0x1000,4);error=C.get_last_error()
            after=region(large)
            emit('commit_attempt',request=size,returned_nonnull=bool(committed),winerror=error,
                 before=before,region=after,system_before=system)
            if committed or after['state']!=0x2000 or after['size']<size:
                raise AssertionError('LARGE_RANGE_NOT_REJECTED_RESERVED')
            recovered=k.VirtualAlloc(large,4*1048576,0x1000,4)
            if not recovered:raise C.WinError(C.get_last_error())
            emit('small_recovery',region=region(large),remaining=region(large+4*1048576))
        k.VirtualFree(small,0,0x8000);small=None
        if large:k.VirtualFree(large,0,0x8000);large=None
        emit('released')
    finally:
        if small:k.VirtualFree(small,0,0x8000)
        if large:k.VirtualFree(large,0,0x8000)
        conn.close()

def main():
    out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
    for mode in ('native','python','aggregate'):
        win.install(fresh=True);parent,remote=MP.Pipe()
        p=MP.get_context('spawn').Process(target=child,args=(remote,mode));p.start();remote.close()
        records=[]
        try:
            while True:
                if not parent.poll(15):raise TimeoutError('MEMORY_PROBE_TIMEOUT')
                event=parent.recv();data=details(p.sentinel)
                assert data['flags']==0x200 and data['job_limit']==536870912
                assert data['supervisor_member'] and data['worker_member']
                assert set(data['pids'])=={os.getpid(),p.pid}
                event['job']=data;records.append(event)
                requested=win.LIMIT-data['supervisor']['private']-data['worker']['private']+8*1048576
                requested=(requested+4095)//4096*4096
                if mode=='aggregate' and event['stage']=='small_committed':
                    event['next_request']=requested
                    assert requested+data['worker']['private']<win.LIMIT
                    assert requested+data['worker']['private']+data['supervisor']['private']>win.LIMIT
                parent.send(requested)
                if event['stage']=='released':break
            p.join(10)
            assert p.exitcode==0
        finally:
            if p.is_alive():p.terminate();p.join(5)
            (out/(mode+'.json')).write_text(json.dumps(dict(mode=mode,exitcode=p.exitcode,records=records,
                layout=dict(extended=C.sizeof(win.Extended),basic=C.sizeof(win.Basic),io=C.sizeof(win.IO),
                    counters=C.sizeof(Counters),region=C.sizeof(Region),offsets={n:getattr(win.Extended,n).offset for n,_ in win.Extended._fields_})),indent=2)+'\n',encoding='utf-8')
        print(mode,'PASS',[(x['stage'],x['job']['peak_job'],x['memory']['private']) for x in records],flush=True)

if __name__=='__main__':main()
