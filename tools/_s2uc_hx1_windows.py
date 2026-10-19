"""Windows Job Object hard aggregate committed-memory limit (supervisor + child)."""
import ctypes as C
from ctypes import wintypes as W
import os

LIMIT=512*1048576
HANDLE=None

class Basic(C.Structure):
    _fields_=[('process_time',C.c_int64),('job_time',C.c_int64),('flags',W.DWORD),
        ('min_ws',C.c_size_t),('max_ws',C.c_size_t),('active',W.DWORD),
        ('affinity',C.c_size_t),('priority',W.DWORD),('scheduling',W.DWORD)]
class IO(C.Structure):
    _fields_=[(name,C.c_ulonglong) for name in ('read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes')]
class Extended(C.Structure):
    _fields_=[('basic',Basic),('io',IO),('process_limit',C.c_size_t),('job_limit',C.c_size_t),
        ('peak_process',C.c_size_t),('peak_job',C.c_size_t)]

def api():
    if os.name!='nt': raise RuntimeError('WINDOWS_JOB_REQUIRED')
    k=C.WinDLL('kernel32',use_last_error=True)
    k.CreateJobObjectW.argtypes=[C.c_void_p,W.LPCWSTR];k.CreateJobObjectW.restype=W.HANDLE
    k.GetCurrentProcess.restype=W.HANDLE
    k.SetInformationJobObject.argtypes=[W.HANDLE,C.c_int,C.c_void_p,W.DWORD]
    k.AssignProcessToJobObject.argtypes=[W.HANDLE,W.HANDLE]
    k.QueryInformationJobObject.argtypes=[W.HANDLE,C.c_int,C.c_void_p,W.DWORD,C.c_void_p]
    return k

def install(*,fresh=False):
    global HANDLE
    if HANDLE is not None and not fresh: return snapshot()
    k=api();h=k.CreateJobObjectW(None,None)
    if not h: raise C.WinError(C.get_last_error())
    info=Extended();info.basic.flags=0x200;info.job_limit=LIMIT
    if not k.SetInformationJobObject(h,9,C.byref(info),C.sizeof(info)): raise C.WinError(C.get_last_error())
    if not k.AssignProcessToJobObject(h,k.GetCurrentProcess()): raise C.WinError(C.get_last_error())
    HANDLE=h
    # No breakaway and no kill-on-close: this supervisor remains a member until exit.
    # Spawned workers inherit membership, enforced by the OS, not a sampled RSS cap.
    return snapshot()

def snapshot():
    if HANDLE is None: raise RuntimeError('JOB_NOT_INSTALLED')
    info=Extended();k=api()
    if not k.QueryInformationJobObject(HANDLE,9,C.byref(info),C.sizeof(info),None): raise C.WinError(C.get_last_error())
    if info.job_limit!=LIMIT or not info.basic.flags&0x200: raise RuntimeError('JOB_LIMIT_CHANGED')
    return dict(limit_bytes=info.job_limit,peak_job_committed_bytes=info.peak_job,
        peak_process_committed_bytes=info.peak_process,hard_job_limit=True,
        members='supervisor and inherited worker',measurement='Windows JobObjectExtendedLimitInformation',
        note='Peak can include an allocation attempt rejected by the job; successful runs must remain below cap.')

def worker_membership():
    k=api();k.IsProcessInJob.argtypes=[W.HANDLE,W.HANDLE,C.POINTER(W.BOOL)]
    yes=W.BOOL()
    if not k.IsProcessInJob(k.GetCurrentProcess(),None,C.byref(yes)) or not yes.value:
        raise RuntimeError('WORKER_NOT_IN_JOB')
    return True

def verify_worker(handle):
    k=api();k.IsProcessInJob.argtypes=[W.HANDLE,W.HANDLE,C.POINTER(W.BOOL)]
    yes=W.BOOL()
    if not k.IsProcessInJob(handle,HANDLE,C.byref(yes)) or not yes.value:
        raise RuntimeError('WORKER_NOT_IN_SUPERVISOR_JOB')
