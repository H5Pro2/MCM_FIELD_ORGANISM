"""Stdlib bootstrap and Windows-limited audio worker. No registry operations."""
import ctypes as ct
from ctypes import wintypes as wt
import hashlib
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time

ROOT=Path(__file__).resolve().parents[1]
MEMORY=640*1048576
MESSAGE=65536
BINDING=ROOT/'docs/S2UC_AUDIO_READER_BINDING_20260930.json'

def need(ok,code):
    if not ok:raise ValueError(code)

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        while block:=f.read(1048576):h.update(block)
    return h.hexdigest()

def verify_binding(path,expected):
    need(sha(path)==expected,'BINDING_CHANGED')
    value=json.loads(Path(path).read_text(encoding='utf-8-sig'))
    for row in value['files']:
        need(sha(row['path'])==row['sha256'],'RUNTIME_CHANGED:'+row['path'])
    return value

def confirm_job(name):
    need(type(name) is str and name.startswith('Local\\MCMDecoderJob-'),'JOB_REQUIRED')
    from tools._s2oe_decoder_worker import ExtendedLimits
    api=ct.WinDLL('kernel32',use_last_error=True)
    api.OpenJobObjectW.argtypes=[wt.DWORD,wt.BOOL,wt.LPCWSTR];api.OpenJobObjectW.restype=wt.HANDLE
    api.GetCurrentProcess.restype=wt.HANDLE
    api.IsProcessInJob.argtypes=[wt.HANDLE,wt.HANDLE,ct.POINTER(wt.BOOL)]
    api.QueryInformationJobObject.argtypes=[wt.HANDLE,ct.c_int,ct.c_void_p,wt.DWORD,ct.c_void_p]
    api.CloseHandle.argtypes=[wt.HANDLE]
    job=api.OpenJobObjectW(4,False,name);need(bool(job),'JOB_REQUIRED')
    try:
        member=wt.BOOL();data=ExtendedLimits()
        need(api.IsProcessInJob(api.GetCurrentProcess(),job,ct.byref(member)) and member.value,'JOB_MEMBERSHIP')
        need(api.QueryInformationJobObject(job,9,ct.byref(data),ct.sizeof(data),None),'JOB_QUERY')
        need(data.basic.flags==0x2308 and data.basic.active_processes==1 and data.process_memory==MEMORY and data.job_memory==MEMORY,'JOB_LIMITS')
        return dict(member=True,flags=data.basic.flags,process_commit_limit=data.process_memory,job_commit_limit=data.job_memory)
    finally:api.CloseHandle(job)

def send(value):
    raw=json.dumps(value,separators=(',',':'),allow_nan=False)
    need(len(raw.encode())<=MESSAGE,'MESSAGE_LIMIT')
    print(raw,flush=True)

def receive():
    line=sys.stdin.buffer.readline(MESSAGE+2)
    need(line.endswith(b'\n') and len(line)<=MESSAGE+1,'COMMAND_LIMIT')
    return json.loads(line)

def child():
    need(sys.flags.no_site and 'numpy' not in sys.modules and 'av' not in sys.modules,'PREIMPORT')
    config=receive()  # Blocks before decoder/numpy imports until parent attaches Job.
    sys.path.insert(0,str(ROOT))
    proof=confirm_job(config['job'])
    if config['mode']=='helper':
        send(dict(ready=True,job=proof,decoder_imported=False))
        command=receive()
        if command['op']=='sleep':time.sleep(command['seconds']);send({'awake':True})
        elif command['op']=='memory':
            try:ct.create_string_buffer(MEMORY+1048576)
            except (MemoryError,OSError):send({'allocation_denied':True})
            else:send({'allocation_denied':False})
        return
    binding=verify_binding(config['binding'],config['binding_sha256'])
    import site
    site.main()
    from tools._s2uc_bounded_audio import AudioReader,Limits,CONFIG,SOURCE,SOURCE_SIZE,SOURCE_SHA
    reader=None;count=0;calls=dict(receptor=0,nj=0)
    try:
        spec=config['source'];path=Path(spec['path']).resolve()
        if config['mode']=='neutral':
            fixture_root=(ROOT/'reports/s2uc/audio-reader-development-20260930/fixtures').resolve()
            need(path.is_relative_to(fixture_root),'NEUTRAL_SOURCE_OUTSIDE_FIXTURES')
            need(path!=(ROOT/SOURCE).resolve() and spec['sha256']!=SOURCE_SHA,'REAL_SOURCE_FORBIDDEN')
        else:
            need(config['mode']=='materialize' and config.get('authorized') is True,'AUTHORIZATION_REQUIRED')
            need(path==(ROOT/SOURCE).resolve() and spec['size']==SOURCE_SIZE and spec['sha256']==SOURCE_SHA,'SOURCE_BINDING')
        limits=Limits()
        if config['mode']=='neutral' and 'limits' in config:
            import dataclasses
            for key,val in config['limits'].items():
                need(type(val) is int and 0<val<=getattr(limits,key),'NEUTRAL_LIMIT_INVALID')
            limits=dataclasses.replace(limits,**config['limits'])
        reader=AudioReader(path,spec['size'],spec['sha256'],limits,job_name=config['job'])
        from tools._s2oe_media_decoder import load_av
        av=load_av()
        send(dict(ready=True,job=proof,decoder_version=av.__version__,libraries=av.library_versions))
        count=0
        while True:
            request=receive()
            if request['op']=='close':
                if count==100:reader.assembler.finish()
                elif config['mode']=='materialize':raise ValueError('INCOMPLETE_MATERIALIZATION')
                reader.close();send(dict(closed=True,facts=reader.facts(),projection_calls=calls));break
            need(request=={'op':'next','index':count+1} and count<100,'REQUEST_ORDER')
            payload,origin=reader.take();count+=1
            if config['mode']=='materialize' or config.get('neutral_project') is True:
                from tools._s2uc_bounded_audio import project_window
                value=project_window(payload,origin,calls)
                need(value['profile_digest']==binding['nj_profile_digest'],'NJ_PROFILE_CHANGED')
                response=dict(index=count,origin=origin,pcm_sha256=hashlib.sha256(payload).hexdigest(),projection=value)
                del value
            else:
                response=dict(index=count,origin=origin,pcm_sha256=hashlib.sha256(payload).hexdigest(),pcm_bytes=len(payload))
            del payload
            send(response)
            del response
    except BaseException as exc:
        if reader:reader.close()
        send(dict(error=str(exc)[:2000] or type(exc).__name__,phase='DECODE_OR_PROJECTION' if reader else 'OPEN',decoded_windows=count,projection_calls=calls,facts=reader.facts() if reader else None,closed=True))
    finally:
        if reader:reader.close()

class LimitedWorker:
    def __init__(self,config,request_seconds=30.,total_seconds=300.):
        from tools._s2oe_decoder_worker import DecoderJob,ExtendedLimits
        need(0<request_seconds<=30 and 0<total_seconds<=300,'WATCHDOG_LIMIT_INVALID')
        self.process=None;self.job=None;self.thread=None;self.timer=None;self.closed=False;self.proof=None;self.total_expired=False
        self.responses=queue.Queue(maxsize=1);self.request_seconds=request_seconds;self.deadline=time.monotonic()+total_seconds
        self.config=config
        try:
            self.job=DecoderJob()
            limits=ExtendedLimits();limits.basic.flags=0x2308;limits.basic.active_processes=1
            limits.process_memory=limits.job_memory=MEMORY;self.job._set(9,limits)
            self.proof=self.job.snapshot();need(self.proof['process_commit_limit']==MEMORY and self.proof['job_commit_limit']==MEMORY,'JOB_NOT_ACTIVE')
            self.process=subprocess.Popen([sys.executable,'-S',str(Path(__file__).resolve()),'child'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,cwd=ROOT,creationflags=subprocess.CREATE_NO_WINDOW)
            self.job.attach(self.process.pid)
            self.timer=threading.Timer(max(0.001,self.deadline-time.monotonic()),self._expire)
            self.timer.daemon=True;self.timer.start()
            self.thread=threading.Thread(target=self._read,daemon=True);self.thread.start()
            self.ready=self.request(dict(config,job=self.job.name))
            need(self.ready.get('ready') is True,'WORKER_NOT_READY')
        except BaseException:self.close();raise
    def _expire(self):
        self.total_expired=True
        if self.job and self.job.handle:
            try:self.job.terminate()
            except Exception:pass
    def _read(self):
        try:
            while True:
                line=self.process.stdout.readline(MESSAGE+2)
                need(line.endswith(b'\n') and len(line)<=MESSAGE+1,'WORKER_CHANNEL')
                self.responses.put(json.loads(line),timeout=0.5)
        except Exception as exc:
            try:self.responses.put_nowait({'error':str(exc)})
            except queue.Full:pass
    def request(self,value):
        try:
            need(not self.closed,'WORKER_CLOSED')
            need(not self.total_expired,'TOTAL_TIMEOUT')
            data=json.dumps(value,separators=(',',':')).encode()+b'\n';need(len(data)<=MESSAGE,'COMMAND_LIMIT')
            self.process.stdin.write(data);self.process.stdin.flush()
            seconds=min(self.request_seconds,self.deadline-time.monotonic());need(seconds>0,'TOTAL_TIMEOUT')
            try:result=self.responses.get(timeout=seconds)
            except queue.Empty:raise ValueError('WORKER_TIMEOUT')
            need('error' not in result,'CHILD_ERROR:'+str(result.get('error')))
            return result
        except BaseException:self.close();raise
    def finish(self):
        value=self.request({'op':'close'})
        need(value.get('closed') is True,'CLOSE_NOT_CONFIRMED');self.close();return value
    def close(self):
        if self.closed:return
        self.closed=True
        if self.timer:self.timer.cancel()
        try:
            if self.job:
                self.proof=self.job.snapshot()
                if self.process and self.process.poll() is None:self.job.terminate()
            if self.process:
                if self.process.poll() is None:self.process.kill()
                self.process.wait(timeout=5)
                for stream in (self.process.stdin,self.process.stdout):
                    if stream:stream.close()
        finally:
            if self.job:self.job.close()
            if self.thread:self.thread.join(timeout=1)

def materialize(authorization):
    # Not invoked by development qualification. Exclusive claim, no retry/registry.
    from tools._s2uc_bounded_audio import OutputLedger,SOURCE,SOURCE_SIZE,SOURCE_SHA
    auth=json.loads(Path(authorization).read_text(encoding='utf-8-sig'))
    need(auth==dict(status='AUTHORIZED_ONCE',action='NASA_FIRST_10S_MATERIALIZE_ONLY',binding_sha256=sha(BINDING),output='reports/s2uc/nasa-contiguous-materialization-20260930-01'),'AUTHORIZATION_REQUIRED')
    ledger=OutputLedger(ROOT/auth['output']);worker=None;count=0;status='NOT_EVALUABLE';error=None;facts=None
    try:
        ledger.write('claim.json',auth)
        value=verify_binding(BINDING,auth['binding_sha256'])
        ledger.write('binding.json',value)
        worker=LimitedWorker(dict(mode='materialize',authorized=True,binding=str(BINDING),binding_sha256=auth['binding_sha256'],source=dict(path=str(ROOT/SOURCE),size=SOURCE_SIZE,sha256=SOURCE_SHA)))
        for i in range(1,101):
            row=worker.request({'op':'next','index':i});need(row['index']==i,'OUTPUT_ORDER')
            ledger.write(f'window-{i:03d}.json',row);count=i
        facts=worker.finish();status='MATERIALIZATION_COMPLETE'
    except BaseException as exc:error=str(exc)[:2000] or type(exc).__name__
    finally:
        if worker:worker.close()
        ledger.write('closure.json',dict(status=status,error=error,windows=count,facts=facts,job=worker.proof if worker else None,bytes_before_closure=ledger.used,comparison_executed=False),final=True)
    return status

if __name__=='__main__':
    if sys.argv[1:]==['child']:
        try:child()
        except BaseException as exc:
            send(dict(error=str(exc)[:2000] or type(exc).__name__,phase='BOOTSTRAP',closed=True))
            raise SystemExit(1)
    elif len(sys.argv)==3 and sys.argv[1]=='materialize':
        status=materialize(sys.argv[2]);print(status)
        raise SystemExit(0 if status=='MATERIALIZATION_COMPLETE' else 1)
    else:raise SystemExit('Use child or materialize <explicit-authorization.json>')
