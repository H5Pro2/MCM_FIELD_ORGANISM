"""AS480 entry: hard shared Job, exclusive starts, durable attempts, no retries."""
import argparse,ctypes,os,subprocess,sys,time,uuid
for _name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_name]='1'
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from experiments.as480.common import *
from tools import _s2uc_hx1_windows as win

def runtime():
    import platform,numpy
    return dict(python=sys.version,executable=str(Path(sys.executable).resolve()),executable_sha256=sha(sys.executable),numeric_threads=1,
        platform=platform.platform(),numpy=numpy.__version__,numpy_files={p.relative_to(Path(numpy.__file__).parent).as_posix():sha(p)
        for p in Path(numpy.__file__).parent.rglob('*') if p.is_file() and p.suffix in ('.py','.pyd','.dll')},
        numpy_external_libraries={str(p.resolve()):sha(p) for p in (Path(numpy.__file__).parent.parent/'numpy.libs').rglob('*') if p.is_file()},
        dlls={p.name:sha(p) for p in Path(sys.executable).parent.glob('python*.dll')})
def install():
    win.install();k=win.api();v=win.Extended()
    need(k.QueryInformationJobObject(win.HANDLE,9,ctypes.byref(v),ctypes.sizeof(v),None),'JOB_QUERY')
    v.basic.flags=0x200|0x8|0x2000;v.basic.active=2
    need(k.SetInformationJobObject(win.HANDLE,9,ctypes.byref(v),ctypes.sizeof(v)),'JOB_SET')
    return job()
def job():
    k=win.api();v=win.Extended()
    need(k.QueryInformationJobObject(win.HANDLE,9,ctypes.byref(v),ctypes.sizeof(v),None),'JOB_QUERY')
    need(v.job_limit==LIMITS['job'] and v.basic.active==2 and v.basic.flags==(0x200|0x8|0x2000),'JOB_FLAGS')
    return dict(**win.snapshot(),active_process_limit=v.basic.active,flags=v.basic.flags,kill_on_close=True,breakaway=False)
def code_files():
    paths=[p for name in ('tools','mcm_field_organism','experiments/as480') for p in (ROOT/name).rglob('*.py')]
    paths.append(CONTRACT)
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}
def verify_files(files):
    for name,h in files.items():need(sha(ROOT/name)==h,'CODE_BINDING:'+name)
def binding():
    p=PREP/'binding.json';b=read(p)
    need(sha(p)==(PREP/'binding.sha256').read_text().strip(),'BINDING_DIGEST')
    need(b['contract_sha256']==CONTRACT_SHA and b['limits']==LIMITS and b['runtime']==runtime(),'BINDING_RUNTIME')
    verify_files(b['files'])
    for name,h in b['qualification'].items():need(sha(ROOT/name)==h,'QUALIFICATION_BINDING')
    need(read(PREP/'full-neutral-01'/'terminal.json')['status']=='COMPLETE','NEUTRAL_NOT_COMPLETE')
    return b,sha(p)
def timeout(now,start,worker_start,worker_limit=240):
    if now-start>LIMITS['total_seconds']:return 'TOTAL_TIMEOUT'
    if now-worker_start>worker_limit:return 'WORKER_TIMEOUT'
    return None
def worker(folder):
    folder=Path(folder);request=read(folder/'request.json');ledger=Ledger(folder,request['task'])
    try:
        win.worker_membership()
        deadline=time.monotonic()+15
        while not (folder/'gate.json').exists():
            need(time.monotonic()<deadline,'MISSING_GATE');time.sleep(.02)
        need(read(folder/'gate.json')==dict(nonce=request['nonce'],pid=os.getpid()),'GATE_MISMATCH')
        verify_files(request['files']);need(sha(CONTRACT)==CONTRACT_SHA,'CONTRACT')
        need(runtime()==request['runtime'],'WORKER_RUNTIME')
        if request['mode']=='research':
            b,h=binding();authorize('research',read(request['authorization']),h,folder)
            need(read(PREP/'research.consumed.json')['nonce']==request['nonce'],'CONSUMPTION')
        else:need(folder.is_relative_to(PREP),'NEUTRAL_LOCATION')
        task=request['task'];budget=Budget(folder)
        if task=='fault-crash':raise RuntimeError('ARTIFICIAL_WORKER_CRASH')
        if task=='fault-wait':
            while True:time.sleep(.1)
        if task=='fault-budget':budget.save('material/too-large.bin',bytes(4194305))
        if task=='fault-job':raise RuntimeError('ARTIFICIAL_JOB_GATE_REJECTION')
        if task=='fixtures':
            from experiments.as480.tests import run
            result=run(folder,ledger)
        else:
            need(task=='full','TASK');from experiments.as480 import material,engine
            material.materialize(folder,request['mode'],ledger,permit=request['mode']=='research')
            result=engine.compare(folder,request['mode'],ledger)
        verify_files(request['files']);budget.save('worker-result.json',dict(status='COMPLETE',result=result,counts=ledger.counts),final=True)
        ledger.event('COMPLETE');return 0
    except BaseException as exc:
        ledger.event('FAILED',error=type(exc).__name__+':'+str(exc))
        Budget(folder).save('worker-result.json',dict(status='TECHNICAL_ERROR',error=type(exc).__name__+':'+str(exc),counts=ledger.counts),final=True)
        return 1

def supervise(args):
    start=time.monotonic();folder=Path(args.out).resolve()
    need(sha(CONTRACT)==CONTRACT_SHA,'CONTRACT')
    need(args.mode=='neutral' and folder.is_relative_to(PREP) or args.mode=='research' and folder==RESEARCH,'TARGET_SCOPE')
    need(args.mode=='neutral' or args.task=='full','RESEARCH_TASK')
    if args.mode=='neutral' and args.task=='full':
        need(not any(read(p).get('status')=='COMPLETE' for p in PREP.glob('full-*/terminal.json')),'FULL_NEUTRAL_ALREADY_COMPLETE')
    need(not folder.exists(),'EXCLUSIVE_TARGET')
    append(PREP/'attempts.jsonl',dict(event='START_REQUEST',task=args.task,mode=args.mode,target=str(folder),reason=args.reason))
    child=None;error=None;request=None;installed=False
    folder.mkdir(parents=True)
    budget=Budget(folder)
    try:
        if args.task=='fault-job-install':raise RuntimeError('ARTIFICIAL_JOB_INSTALL_FAILURE')
        install();installed=True
        rt=runtime();files=code_files()
        auth=read(args.authorization) if args.authorization else None
        h=None
        if args.mode=='research':_,h=binding()
        authorize(args.mode,auth,h,folder)
        nonce=uuid.uuid4().hex
        if args.mode=='research':exclusive(PREP/'research.consumed.json',dict(nonce=nonce,binding_sha256=h,target=str(folder)))
        request=dict(mode=args.mode,task=args.task,nonce=nonce,files=files,runtime=rt,
                     authorization=str(Path(args.authorization).resolve()) if args.authorization else None)
        budget.save('request.json',request)
        cmd=[sys.executable,'-B',str(Path(__file__).resolve()),'--worker',str(folder)]
        with (folder/'worker.log').open('xb') as log:
            child=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            worker_start=time.monotonic();win.verify_worker(int(child._handle))
            budget.save('gate.json',dict(nonce=nonce,pid=child.pid))
            while child.poll() is None:
                error=timeout(time.monotonic(),start,worker_start,1 if args.task=='fault-wait' else 240)
                if size(PREP)+ (0 if folder.is_relative_to(PREP) else size(folder))>LIMITS['export']:error='EXPORT_LIMIT'
                if error:child.kill();break
                time.sleep(.05)
            child.wait(timeout=5)
        if error:raise RuntimeError(error)
        need(child.returncode==0,'WORKER_EXIT:'+str(child.returncode))
        result=read(folder/'worker-result.json');need(result['status']=='COMPLETE','WORKER_RESULT')
    except BaseException as exc:error=type(exc).__name__+':'+str(exc)
    finally:
        if child is not None and child.poll() is None:child.kill();child.wait(timeout=5)
        counts=read(folder/'worker-result.json')['counts'] if (folder/'worker-result.json').exists() else ({k:0 for k in COUNTERS})
        if (folder/'execution.jsonl').exists():counts=json.loads((folder/'execution.jsonl').read_bytes().splitlines()[-1])['counts']
        terminal=dict(status='TECHNICAL_ERROR' if error else 'COMPLETE',error=error,counts=counts,
            seconds=time.monotonic()-start,job=job() if installed else None,worker_started=child is not None,
            worker_ended=child is None or child.poll() is not None,worker_exitcode=child.returncode if child else None,
            mode=args.mode,task=args.task,cleanup=child is None or child.poll() is not None,
            files_before_terminal={p.relative_to(folder).as_posix():info(p) for p in folder.rglob('*') if p.is_file()})
        budget.save('terminal.json',terminal,final=True)
        append(PREP/'attempts.jsonl',dict(event='TERMINAL',target=str(folder),status=terminal['status'],error=error,counts=counts))
        print(json.dumps({k:terminal[k] for k in ('status','error','seconds','counts','job')}))
    return 1 if error else 0
def main():
    p=argparse.ArgumentParser();p.add_argument('--worker');p.add_argument('--mode',choices=['neutral','research'],default='neutral')
    p.add_argument('--task',choices=['fixtures','full','fault-crash','fault-wait','fault-budget','fault-job','fault-job-install'],default='full')
    p.add_argument('--out');p.add_argument('--authorization');p.add_argument('--reason',default='initial authorized qualification')
    a=p.parse_args()
    if a.worker:return worker(a.worker)
    need(a.out is not None,'OUTPUT_REQUIRED');return supervise(a)
if __name__=='__main__':raise SystemExit(main())
