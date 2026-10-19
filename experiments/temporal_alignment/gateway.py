"""New technical one-shot authorization, worker capability and immutable closure."""
import os,sys,time,json,uuid,subprocess
from pathlib import Path
from .entry import ROOT,OUT,save,job,CONCEPT,CONCEPT_SHA,timeout
from experiments.as480.common import need,read,sha,info,raw,exclusive,size
ORDER='6d248902-bf8b-4eeb-805e-8014fcf4edca'
CHAT='01a0beeb-9c11-7510-95a7-f0d1409eadc7'
PRIOR_SHA='4c297a6a29e904289a2aee10e8adece08ccb5b95157374660f07b71f857148eb'
Q=OUT/'qualification-6d248902';FULL=Q/'full-neutral-01'
SOURCE=Path('C:/Users/TV/Documents/Codex_Workflow_Tool/data/projects/f6f2c2a07540e9c4c19834bca1bcb9be9a658572f2201b1bf7434330631c8fda/order-context')/(ORDER+'.txt')
_ACTIVE=None

def code_files():
    result=job.code_files()
    for p in (ROOT/'experiments/temporal_alignment').glob('*.py'):result[p.relative_to(ROOT).as_posix()]=sha(p)
    return result
def verify_code(files):
    for name,digest in files.items():need(sha(ROOT/name)==digest,'FINAL_CODE:'+name)
def authorized(binding_hash):return dict(kind='TECHNICAL_NEUTRAL_ONCE',workflow=ORDER,chat=CHAT,binding_sha256=binding_hash,target=str(FULL),research=False)
def verify_authorization(auth,binding_hash):need(auth==authorized(binding_hash),'NEW_AUTHORIZATION_MISMATCH')
def consume_once(path,record):
    need(Path(path).resolve().is_relative_to(Q.resolve()),'CONSUMPTION_SCOPE');exclusive(path,record)
def binding():
    p=Q/'binding.json';b=read(p);h=sha(p)
    need(h==(Q/'binding.sha256').read_text().strip(),'FINAL_BINDING_HASH')
    need(b['workflow']==ORDER and b['target']==str(FULL) and b['source_sha256']==sha(SOURCE),'ORDER_BINDING')
    need(b['runtime']==job.runtime(),'RUNTIME_BINDING');verify_code(b['files'])
    from .full import NEUTRAL,CASES
    need(b['neutral']==NEUTRAL and b['cases']==json.loads(raw(CASES)),'RECIPE_BINDING')
    verify_authorization(read(Q/'authorization.json'),h)
    for name,digest in b['inherited_evidence'].items():need(sha(OUT/name)==digest,'INHERITED_EVIDENCE')
    need(sha(Q/'connection-tests-01/tests.json')==b['connection_tests_sha256'],'CONNECTION_TEST_BINDING')
    return b,h
def seal():
    job.install();need(os.environ.get('CODEX_THREAD_ID')==CHAT,'OWN_CHAT')
    need(sha(CONCEPT)==CONCEPT_SHA and sha(OUT/'delivery-binding.json')==PRIOR_SHA,'PRIOR_BINDING')
    old=read(OUT/'delivery-binding.json')
    for name,value in old['files'].items():need(info(OUT/name)==value,'PRIOR_ARTIFACT_CHANGED')
    for name,value in old['code'].items():need(info(Q/'prior-code'/Path(name).name)==value,'PRIOR_SOURCE_SNAPSHOT')
    need(read(Q/'connection-tests-01/tests.json')['passed'],'CONNECTION_TESTS')
    need(not (Q/'consumed.json').exists() and not FULL.exists(),'NEW_ORDER_ALREADY_USED')
    from .full import NEUTRAL,CASES
    b=dict(workflow=ORDER,chat=CHAT,target=str(FULL),prior_delivery_sha256=PRIOR_SHA,source_sha256=sha(SOURCE),
        historical_consumption='UNPROVEN',new_permission='INDEPENDENT_TECHNICAL_ONCE',research=False,
        runtime=job.runtime(),files=code_files(),neutral=NEUTRAL,cases=CASES,
        inherited_evidence={name:v['sha256'] for name,v in old['files'].items()},
        connection_tests_sha256=sha(Q/'connection-tests-01/tests.json'),concept_sha256=CONCEPT_SHA)
    save(Q,'binding.json',b);h=sha(Q/'binding.json');save(Q,'binding.sha256',(h+'\n').encode());save(Q,'authorization.json',authorized(h))
    print(json.dumps(dict(status='SEALED',binding_sha256=h)))

def check_active(folder,permit):
    need(_ACTIVE is not None and permit is _ACTIVE['permit'] and Path(folder).resolve()==FULL,'SUPERVISED_CAPABILITY_REQUIRED')
    need(os.getpid()==_ACTIVE['pid'],'WORKER_CAPABILITY_PID')
    marker=read(Q/'consumed.json');request=read(FULL/'request.json');gate=read(FULL/'gate.json')
    need(marker['workflow']==ORDER and marker['nonce']==request['nonce']==gate['nonce']==_ACTIVE['nonce'],'CONSUMPTION_NONCE')
    need(gate['pid']==os.getpid() and request['supervisor_pid']==os.getppid(),'WORKER_LINEAGE')
    job.win.worker_membership()
    # This second durable marker also rejects two full.run calls in the same worker.
    save(FULL,'worker-entered.json',dict(workflow=ORDER,nonce=_ACTIVE['nonce'],pid=os.getpid()))

def dispatch(task,folder,permit=None):
    if task=='full':
        from .full import run
        return run(folder,permit=permit)
    need(task=='connections','WORKER_TASK')
    from .connection_tests import run
    result=run(folder);save(folder,'tests.json',result);need(result['passed'],'CONNECTION_TEST_FAILURE')

def worker(folder):
    global _ACTIVE
    job.win.worker_membership();folder=Path(folder).resolve();request=read(folder/'request.json')
    until=time.monotonic()+10
    while not (folder/'gate.json').exists():need(time.monotonic()<until,'WORKER_GATE_TIMEOUT');time.sleep(.02)
    gate=read(folder/'gate.json');need(gate==dict(pid=os.getpid(),nonce=request['nonce']),'WORKER_GATE_ID')
    try:
        verify_code(request['files']);need(request['runtime']==job.runtime(),'WORKER_RUNTIME')
        if request['task']=='full':
            need(folder==FULL,'FULL_TARGET');b,h=binding();need(h==request['binding_sha256'],'REQUEST_BINDING')
            marker=read(Q/'consumed.json');need(marker['nonce']==request['nonce'] and marker['binding_sha256']==h and marker['workflow']==ORDER,'START_MARKER')
            _ACTIVE=dict(permit=object(),pid=os.getpid(),nonce=request['nonce'])
        dispatch(request['task'],folder,_ACTIVE['permit'] if _ACTIVE else None)
        verify_code(request['files']);save(folder,'worker-result.json',dict(status='COMPLETE',task=request['task']));return 0
    except BaseException as exc:
        import traceback
        save(folder,'worker-error.json',dict(status='TECHNICAL_ERROR',first_error=type(exc).__name__+':'+str(exc),traceback=traceback.format_exc()))
        return 1
    finally:_ACTIVE=None

def supervise(task):
    start=time.monotonic();folder=FULL if task=='full' else Q/'connection-tests-01'
    need(not folder.exists(),'EXCLUSIVE_TARGET')
    if task=='full':need(not (Q/'consumed.json').exists(),'ONE_SHOT_CONSUMED')
    child=None;error=None;installed=False;nonce=uuid.uuid4().hex
    try:
        job.install();installed=True
        h=None
        if task=='full':
            need(os.environ.get('CODEX_THREAD_ID')==CHAT,'OWN_CHAT');b,h=binding()
            # Consumption precedes directory creation, worker start and every source call.
            consume_once(Q/'consumed.json',dict(workflow=ORDER,chat=CHAT,binding_sha256=h,nonce=nonce,
                target=str(FULL),supervisor_pid=os.getpid(),historical_consumption='UNPROVEN',kind='NEW_TECHNICAL_ONCE'))
        folder.mkdir(parents=True)
        request=dict(task=task,workflow=ORDER,nonce=nonce,supervisor_pid=os.getpid(),binding_sha256=h,files=code_files(),runtime=job.runtime())
        save(folder,'request.json',request)
        with (folder/'worker.log').open('xb') as log:
            child=subprocess.Popen([sys.executable,'-B',str(ROOT/'experiments/temporal_alignment/entry.py'),'--worker-full',str(folder)],cwd=ROOT,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            began=time.monotonic();job.win.verify_worker(int(child._handle));save(folder,'gate.json',dict(pid=child.pid,nonce=nonce))
            while child.poll() is None:
                cause=timeout(time.monotonic(),start,began)
                if cause:raise RuntimeError(cause)
                if size(OUT)>16*1048576:raise RuntimeError('PACKAGE_EXPORT')
                time.sleep(.05)
            if child.returncode!=0:
                cause=read(folder/'worker-error.json')['first_error'] if (folder/'worker-error.json').exists() else 'WORKER_EXIT:'+str(child.returncode)
                raise RuntimeError(cause)
        need(read(folder/'worker-result.json')['status']=='COMPLETE','WORKER_RESULT')
    except BaseException as exc:error=type(exc).__name__+':'+str(exc)
    finally:
        if child is not None and child.poll() is None:child.kill();child.wait(timeout=5)
        folder.mkdir(parents=True,exist_ok=True)
        counts=json.loads((folder/'counts.jsonl').read_bytes().splitlines()[-1])['counts'] if (folder/'counts.jsonl').exists() else None
        if time.monotonic()-start>=300:error=error or 'TOTAL_TIMEOUT'
        terminal=dict(status='TECHNICAL_ERROR' if error else 'COMPLETE',first_error=error,task=task,workflow=ORDER,counts=counts,
            seconds=time.monotonic()-start,job=job.job() if installed else None,worker_exitcode=child.returncode if child else None,
            cleanup=child is None or child.poll() is not None,consumed=(Q/'consumed.json').exists(),retry_allowed=False,
            package_bytes_before_terminal=size(OUT))
        save(folder,'terminal.json',terminal)
        closure=dict(workflow=ORDER,files={p.relative_to(folder).as_posix():info(p) for p in folder.rglob('*') if p.is_file()},
            consumption=info(Q/'consumed.json') if (Q/'consumed.json').exists() else None)
        save(folder,'technical-closure.json',closure);save(folder,'technical-closure.sha256',(sha(folder/'technical-closure.json')+'\n').encode())
        need(time.monotonic()-start<300,'TECHNICAL_CLOSURE_TIMEOUT')
        save(folder,'completion.json',dict(status=terminal['status'],seconds_including_technical_closure=time.monotonic()-start,
            technical_closure_sha256=sha(folder/'technical-closure.json'),package_bytes_before_completion=size(OUT)))
        need(time.monotonic()-start<300,'COMPLETION_TIMEOUT')
        print(json.dumps(dict(status=terminal['status'],error=error,counts=counts,seconds_including_closure=time.monotonic()-start,
            technical_closure_sha256=sha(folder/'technical-closure.json'),job=terminal['job'])))
    return 1 if error else 0

def main(args):
    if args[0]=='--seal':seal();return 0
    if args[0]=='--worker-full':return worker(args[1])
    return supervise('full' if args[0]=='--full' else 'connections')
