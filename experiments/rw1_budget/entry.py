"""Bound synthetic diagnosis supervisor: shared 512MiB job, 240/300 seconds."""
import os,sys,time,json,subprocess,hashlib
from pathlib import Path
for n in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[n]='1'
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from experiments.as480 import entry as job
from experiments.as480.common import raw,sha,info,read,exclusive,size,need
from experiments.rw1_budget.workload import PACKAGE,BASE,actions,boundaries,expected_files
ORDER='9fb2430c-5296-4a5f-b725-2c86be3709ce'
CAP=16777216

def save(path,x):
    data=x if isinstance(x,bytes) else raw(x)
    need(Path(path).resolve().is_relative_to(PACKAGE.resolve()),'DIAGNOSTIC_SCOPE')
    need(size(PACKAGE)+len(data)<CAP-65536,'DIAGNOSTIC_EXPORT')
    exclusive(path,data)
def code():return {p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'experiments/rw1_budget').glob('*.py')}
def inventory(root):
    """Independent final directory traversal, not a budget counter lookup."""
    result={}
    if not root.exists():return result
    stack=[root]
    while stack:
        folder=stack.pop()
        with os.scandir(folder) as entries:
            for e in entries:
                need(not e.is_symlink(),'UNEXPECTED_LINK')
                if e.is_dir(follow_symlinks=False):stack.append(Path(e.path))
                else:result[Path(e.path).relative_to(root).as_posix()]=e.stat(follow_symlinks=False).st_size
    return result

def setup(folder):
    need(not BASE.exists(),'ARTIFICIAL_BASE_EXISTS')
    groups={'old':'reports/s2uc/temporal-alignment-development-20261019-01','doc':'reports/s2uc/raster-recognition-contract-documentation-20261019-01','prep':'reports/s2uc/rw1-development-20261019-01','experiments/rw1':'experiments/rw1'}
    shape=[]
    # Only sizes and directory layout are read; no research payload is copied.
    for group,relative in groups.items():
        source=ROOT/relative
        for i,p in enumerate(sorted(x for x in source.rglob('*') if x.is_file())):
            parent=p.relative_to(source).parent
            name=(Path(group)/parent/f'artificial-{i:04}.fixture').as_posix()
            shape.append(dict(name=name,bytes=p.stat().st_size))
    shape.append(dict(name='contract.fixture',bytes=(ROOT/'docs/S2UC_RASTERWIEDERERKENNUNG_FORSCHUNGSPRUEFVERTRAG_20261019.txt').stat().st_size))
    work=actions();sizes=expected_files(len(work));base_bytes=sum(x['bytes'] for x in shape)
    plan=dict(kind='SYNTHETIC_ONLY_NO_RESEARCH_PAYLOAD',order=ORDER,base_shape=shape,base_bytes=base_bytes,
        operation_count=len(work),boundaries=boundaries(),workload_sha256=hashlib.sha256(raw(work)).hexdigest(),
        target_files=len(sizes),target_bytes=sum(sizes.values()),fixed_order='legacy stages1-3, then corrected stages1-3 only if measured scan cost justifies correction',
        decision_rule='Correct only if legacy scan time >=1 second AND >=10 percent of measured workload time',
        diagnostics_reserve=2000000,maximum_total=CAP,
        timing='perf_counter; scan/serialization/write disjoint; totals include budget logic; setup/checkpoint overhead separately')
    need(base_bytes+2*sum(sizes.values())+2000000<CAP,'PLAN_EXPORT')
    save(PACKAGE/'workload-plan.json',plan)
    for item in shape:
        p=BASE/item['name'];exclusive(p,b'F'*item['bytes'])
    need(sum(inventory(BASE).values())==base_bytes,'BASE_MATCH')
    save(folder/'result.json',dict(status='SETUP_COMPLETE',base_files=len(shape),base_bytes=base_bytes,target_files=len(sizes),target_bytes=sum(sizes.values()),operations=len(work)))

def measure(mode,stage,folder):
    plan=read(PACKAGE/'workload-plan.json');work=actions();need(hashlib.sha256(raw(work)).hexdigest()==plan['workload_sha256'],'FIXED_WORKLOAD')
    lo,hi=boundaries()[stage-1:stage+1];target=PACKAGE/('artificial-'+mode)
    before=inventory(target);before={k:v for k,v in before.items() if not k.startswith('observer/_budget/')}
    need(before==expected_files(lo),'STARTING_STATE')
    if mode=='legacy':
        from experiments.rw1_budget.legacy import MeasuredLegacy
        manager=MeasuredLegacy(target)
    else:
        from experiments.rw1_budget.incremental import MeasuredIncremental
        manager=MeasuredIncremental(target,BASE)
    initialize=time.perf_counter()
    with manager:
        initialize_seconds=time.perf_counter()-initialize
        t=time.perf_counter()
        for a in work[lo:hi]:manager.apply(a)
        elapsed=time.perf_counter()-t
        verify_start=time.perf_counter()
        if hasattr(manager,'verify'):manager.verify()
        verify_seconds=time.perf_counter()-verify_start
    t=time.perf_counter();actual=inventory(target);actual={k:v for k,v in actual.items() if not k.startswith('observer/_budget/')};audit_seconds=time.perf_counter()-t
    need(actual==expected_files(hi),'INDEPENDENT_FILE_BALANCE')
    save(folder/'result.json',dict(mode=mode,stage=stage,operations=hi-lo,elapsed_seconds=elapsed,metrics=manager.metrics,
        independent_inventory_seconds=audit_seconds,independent_inventory_calls=1,files=len(actual),bytes=sum(actual.values()),bookkeeping_matches_actual=True,
        workload_sha256=plan['workload_sha256'],synthetic=True,initialization_seconds=initialize_seconds,
        reconciliation_seconds=verify_seconds,snapshot_sha256=manager.budget.snapshot_hash if mode=='incremental' else None,
        reconciliation=manager.final if mode=='incremental' else None))

def worker(kind,folder):
    folder=Path(folder);job.win.worker_membership();request=read(folder/'request.json')
    until=time.monotonic()+10
    while not (folder/'gate.json').exists():need(time.monotonic()<until,'GATE_TIMEOUT');time.sleep(.02)
    need(read(folder/'gate.json')['pid']==os.getpid() and request['parent']==os.getppid(),'WORKER_ID')
    try:
        need(request['code']==code(),'CODE_CHANGED')
        need(request['runtime_sha256']==sha(PACKAGE/'runtime.json'),'RUNTIME_BINDING')
        if kind=='setup':setup(folder)
        elif kind.startswith(('legacy-','incremental-')):
            mode,stage=kind.split('-');measure(mode,int(stage),folder)
        elif kind=='tests':
            from experiments.rw1_budget.tests import run
            save(folder/'result.json',run(folder))
        elif kind=='writers':
            from experiments.rw1_budget.incremental import JournalBudget
            ledger=JournalBudget(folder/'shared',expected_snapshot=request['snapshot_sha256'])
            for i in range(20):ledger.write('observer/shared.jsonl',dict(worker=i),append=True,role='worker')
            save(folder/'worker-finished.json',dict(writes=20))
        else:raise ValueError('TASK')
        need(request['code']==code(),'CODE_CHANGED');return 0
    except BaseException as e:
        import traceback
        save(folder/'error.json',dict(error=repr(e),traceback=traceback.format_exc()));return 1

def supervise(kind):
    start=time.monotonic();folder=PACKAGE/kind;need(not folder.exists(),'EXCLUSIVE_DIAGNOSIS')
    job.install();child=None;error=None
    try:
        rt=job.runtime();runtime_path=PACKAGE/'runtime.json'
        if runtime_path.exists():need(read(runtime_path)==rt,'RUNTIME_CHANGED')
        else:save(runtime_path,rt)
        request=dict(kind=kind,order=ORDER,parent=os.getpid(),code=code(),runtime_sha256=sha(runtime_path))
        if kind=='writers':
            from experiments.rw1_budget.incremental import JournalBudget
            shared=JournalBudget(folder/'shared',create=True);request['snapshot_sha256']=shared.snapshot_hash
        save(folder/'request.json',request)
        child=subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'--worker',kind,str(folder)],cwd=ROOT,
             stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
        began=time.monotonic();job.win.verify_worker(int(child._handle));save(folder/'gate.json',dict(pid=child.pid))
        if kind=='writers':
            for i in range(20):shared.write('observer/shared.jsonl',dict(supervisor=i),append=True,role='supervisor')
        while child.poll() is None:
            need(time.monotonic()-began<240 and time.monotonic()-start<300,'TIME_LIMIT');time.sleep(.05)
        need(child.returncode==0,'WORKER_FAILED')
        if kind=='writers':
            reconciled=shared.reconcile();lines=(folder/'shared/observer/shared.jsonl').read_bytes().splitlines()
            need(len(lines)==40 and {json.loads(x)['worker'] for x in lines if 'worker' in json.loads(x)}==set(range(20)) and {json.loads(x)['supervisor'] for x in lines if 'supervisor' in json.loads(x)}==set(range(20)),'CROSS_PROCESS_WRITERS')
            save(folder/'result.json',dict(passed=True,writes=40,supervisor_writes=20,worker_writes=20,reconciliation=reconciled,shared_lock=True))
    except BaseException as e:error=repr(e)
    finally:
        if child is not None and child.poll() is None:child.kill();child.wait(timeout=5)
        terminal=dict(status='FAILED' if error else 'COMPLETE',error=error,seconds=time.monotonic()-start,job=job.job(),
            worker_exitcode=child.returncode if child else None,cleanup=child is None or child.poll() is not None,package_bytes=size(PACKAGE))
        save(folder/'terminal.json',terminal)
        save(folder/'closure.json',dict(files={p.name:info(p) for p in folder.iterdir() if p.is_file()},seconds=time.monotonic()-start))
        need(time.monotonic()-start<300,'CLOSURE_TIMEOUT');print(raw(terminal).decode())
    return int(error is not None)
if __name__=='__main__':
    raise SystemExit(worker(sys.argv[2],sys.argv[3]) if sys.argv[1]=='--worker' else supervise(sys.argv[1]))
