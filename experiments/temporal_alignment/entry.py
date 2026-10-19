"""Durable development execution. Formal size run stays closed without prior-use evidence."""
import sys,os,time,json,subprocess
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[name]='1'
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from experiments.as480 import entry as job
from experiments.as480.common import need,read,sha,info,raw,exclusive,append,size
OUT=ROOT/'reports/s2uc/temporal-alignment-development-20261019-01'
CONCEPT=ROOT/'docs/S2UC_ZEITLICHE_AUSRICHTUNG_KONZEPT_20261019.txt'
CONCEPT_SHA='169cb1df3118b58f3e7173a711668df4617a8a8727d8b77f6488a0e6e2e2007e'

def save(folder,name,data):
    payload=data if isinstance(data,bytes) else raw(data)
    path=(folder/name).resolve();need(path.is_relative_to(OUT.resolve()),'OUTPUT_SCOPE')
    full=OUT/'qualification-6d248902/full-neutral-01'
    if path.is_relative_to((full/'material').resolve()):need(size(full/'material')+len(payload)<=4*1048576,'MATERIAL_PARTITION')
    elif path.is_relative_to(full.resolve()):
        current=sum(p.stat().st_size for p in full.rglob('*') if p.is_file() and not p.is_relative_to(full/'material'))
        need(current+len(payload)<=4*1048576,'OBSERVER_CLOSURE_PARTITION')
    export_check(size(OUT),len(payload));exclusive(path,payload)
def export_check(current,n):need(current>=0 and n>=0 and current+n<=16*1048576,'PACKAGE_EXPORT_LIMIT')
def formal_gate(folder=None,permit=None):
    from experiments.temporal_alignment.gateway import check_active
    return check_active(folder,permit)
def timeout(now,start,worker_start):
    return 'TOTAL_TIMEOUT' if now-start>300 else 'WORKER_TIMEOUT' if now-worker_start>240 else None
def worker(folder):
    job.win.worker_membership();until=time.monotonic()+10
    while not (folder/'gate.json').exists():need(time.monotonic()<until,'WORKER_GATE');time.sleep(.02)
    need(read(folder/'gate.json')['pid']==os.getpid(),'WORKER_PID')
    from experiments.temporal_alignment.tests import run
    result=run(extra=folder.name.startswith('focused'),projector=folder.name.startswith('projector'));save(folder,'tests.json',result);return 0 if result['passed'] else 1
def main():
    if len(sys.argv)>1 and sys.argv[1] in ('--full','--worker-full','--seal','--connections'):
        from experiments.temporal_alignment.gateway import main as gateway_main
        return gateway_main(sys.argv[1:])
    if len(sys.argv)>1 and sys.argv[1]=='--worker':return worker(Path(sys.argv[2]))
    need(len(sys.argv)==2,'FIXTURE_ATTEMPT_NAME_REQUIRED');folder=OUT/sys.argv[1]
    need(not folder.exists(),'EXCLUSIVE_ATTEMPT');need(sha(CONCEPT)==CONCEPT_SHA,'CONCEPT')
    start=time.monotonic();child=None;error=None;installed=False
    OUT.mkdir(parents=True,exist_ok=True);append(OUT/'attempts.jsonl',dict(event='FIXTURES_START',name=folder.name,formal=False))
    folder.mkdir();files={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'experiments/temporal_alignment').glob('*.py')}
    save(folder,'input-binding.json',dict(files=files,concept=CONCEPT_SHA,workflow='35c1693b-4fd3-4f5b-b4f1-9ab235b35a22',formal_permission='UNPROVEN_NOT_CONSUMED_BY_THIS_ATTEMPT'))
    try:
        job.install();installed=True
        with (folder/'worker.log').open('xb') as log:
            child=subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'--worker',str(folder)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            began=time.monotonic();job.win.verify_worker(int(child._handle));save(folder,'gate.json',dict(pid=child.pid))
            while child.poll() is None:
                error=timeout(time.monotonic(),start,began)
                if error:raise RuntimeError(error)
                time.sleep(.05)
            need(child.returncode==0,'FIXTURE_WORKER_FAILED')
        for name,h in files.items():need(sha(ROOT/name)==h,'CODE_CHANGED')
    except BaseException as exc:error=repr(exc)
    finally:
        if child is not None and child.poll() is None:child.kill();child.wait(timeout=5)
        tests=read(folder/'tests.json') if (folder/'tests.json').exists() else {}
        result=dict(status='FAILED' if error else 'COMPLETE',error=error,seconds=time.monotonic()-start,
            job=job.job() if installed else None,worker_exitcode=child.returncode if child else None,
            cleanup=child is None or child.poll() is not None,formal_size_runs=0,receptor_calls=tests.get('receptor_calls'),nj_calls=tests.get('nj_calls'))
        save(folder,'terminal.json',result);append(OUT/'attempts.jsonl',dict(event='FIXTURES_END',name=folder.name,**result));print(json.dumps(result))
    return 1 if error else 0
if __name__=='__main__':raise SystemExit(main())
