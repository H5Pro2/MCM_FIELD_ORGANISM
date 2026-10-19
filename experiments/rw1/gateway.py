"""Separate RW1 entry. No authorization issuing API; old gateway is untouched."""
import os,sys,time,uuid,subprocess
from .common import *
from experiments.as480 import entry as job
_ACTIVE=None

def files():
    result=job.code_files()
    for directory in ('experiments/temporal_alignment','experiments/rw1'):
        for p in (ROOT/directory).glob('*.py'):result[p.relative_to(ROOT).as_posix()]=sha(p)
    result[CONTRACT.relative_to(ROOT).as_posix()]=sha(CONTRACT)
    return result
def verify_files(mapping):
    need(mapping==files(),'CODE_SET_OR_HASH')
def inherited():
    need(sha(CONTRACT)==CONTRACT_SHA and sha(OLD_Q/'delivery-binding.json')==OLD_SHA,'INHERITED_BINDING')
    b=read(OLD_Q/'delivery-binding.json')
    for n,v in b['files'].items():need(info(OLD_Q/n)==v,'INHERITED_ARTIFACT:'+n)
    for n,v in b['current_code'].items():need(info(ROOT/n)==v,'QUALIFIED_CODE:'+n)
    return dict(delivery=OLD_SHA,consumed=info(OLD_Q/'consumed.json'),historical_consumption='UNPROVEN')

def seal(tests_folder):
    need(os.environ.get('CODEX_THREAD_ID')==CHAT,'OWN_CHAT')
    p=Path(tests_folder).resolve();need(p.is_relative_to(PREP) and read(p/'closure/completion.json')['status']=='COMPLETE','TEST_COMPLETION')
    tests=read(p/'observer/tests.json');need(tests['passed'] and tests['groups']==['C1','C2','C3','C4','C5','C6'],'SIX_GROUPS')
    need(read(p/'observer/request.json')['files']==files(),'TESTED_FINAL_CODE')
    b=dict(kind='RW1_TECHNICAL_READY',development_order=DEV_ORDER,development_source_sha256=sha(SOURCE_ROOT/(DEV_ORDER+'.txt')),
        chat=CHAT,project=PROJECT,target=str(TARGET),contract_sha256=CONTRACT_SHA,recipe=RECIPE,limits=LIMITS,
        files=files(),runtime=job.runtime(),inherited=inherited(),tests={str(x.relative_to(ROOT)):info(x) for x in p.rglob('*') if x.is_file()})
    budget=Budget(PREP);budget.save('binding.json',b)
    budget.save('binding.sha256',(sha(PREP/'binding.json')+'\n').encode())
    budget.save('permission-status.json',dict(status='NOT_AUTHORIZED',research_authorization_issued=False,research_consumed=False,
        required='Separate future explicit RW1 execution order and matching research-authorization.json',development_order=DEV_ORDER))
    print('SEALED_WITHOUT_RESEARCH_PERMISSION '+sha(PREP/'binding.json'))

def configuration(b,rt,current_files):
    need(b['chat']==CHAT and b['project']==PROJECT and b['target']==str(TARGET),'RECIPIENT_TARGET')
    need(b['contract_sha256']==CONTRACT_SHA and b['recipe']==canonical(RECIPE) and b['limits']==LIMITS,'RECIPE_LIMITS')
    need(b['files']==current_files,'CODE_SET_OR_HASH');need(b['runtime']==rt,'RUNTIME')

def binding():
    b=read(PREP/'binding.json');h=sha(PREP/'binding.json')
    need((PREP/'binding.sha256').read_text().strip()==h,'BINDING_HASH')
    need(b['kind']=='RW1_TECHNICAL_READY' and b['development_order']==DEV_ORDER and b['development_source_sha256']==sha(SOURCE_ROOT/(DEV_ORDER+'.txt')),'DEVELOPMENT_ORDER')
    configuration(b,job.runtime(),files());need(b['inherited']==inherited(),'INHERITED')
    for n,v in b['tests'].items():need(info(ROOT/n)==v,'TEST_BINDING')
    return b,h

def authorize(auth,h,target):
    required={'status','mode','execution_order','execution_source_sha256','chat','project','binding_sha256','contract_sha256','recipe_sha256','target'}
    need(isinstance(auth,dict) and set(auth)==required,'RESEARCH_AUTHORIZATION_REQUIRED')
    order=auth['execution_order']
    need(isinstance(order,str) and str(uuid.UUID(order))==order and order!=DEV_ORDER,'EXECUTION_ORDER')
    need(auth['status']=='AUTHORIZED_ONCE' and auth['mode']=='RW1_RESEARCH','AUTH_MODE')
    need(auth['chat']==CHAT and auth['project']==PROJECT and auth['binding_sha256']==h,'AUTH_RECIPIENT_BINDING')
    need(auth['contract_sha256']==CONTRACT_SHA and auth['recipe_sha256']==digest(raw(RECIPE)),'AUTH_RECIPE')
    need(Path(target).resolve()==TARGET and auth['target']==str(TARGET),'AUTH_TARGET')
    source=SOURCE_ROOT/(order+'.txt')
    need(source.is_file() and sha(source)==auth['execution_source_sha256'],'EXECUTION_SOURCE')

def consume(path,record):
    need(Path(path).resolve()==PREP/'research.consumed.json','CONSUMPTION_PATH');exclusive(path,record)
def check_lineage(request,gate,marker,pid,parent):
    need(gate==dict(pid=pid,nonce=request['nonce']) and request['supervisor_pid']==parent,'WORKER_LINEAGE')
    need(marker['nonce']==request['nonce'] and marker['binding_sha256']==request['binding_sha256'] and marker['execution_order']==request['authorization']['execution_order'],'WORKER_CONSUMPTION')
def capability(folder,permit):
    need(_ACTIVE is not None and permit is _ACTIVE['permit'] and os.getpid()==_ACTIVE['pid'] and Path(folder).resolve()==TARGET,'RESEARCH_CAPABILITY')
def enter(folder,permit):
    capability(folder,permit);job.win.worker_membership()
    request=read(TARGET/'observer/request.json');gate=read(TARGET/'observer/gate.json');marker=read(PREP/'research.consumed.json')
    check_lineage(request,gate,marker,os.getpid(),os.getppid())
    Budget(TARGET).save('observer/worker-entered.json',dict(pid=os.getpid(),nonce=request['nonce']))

def worker(folder):
    global _ACTIVE
    folder=Path(folder).resolve();need(folder==TARGET or folder.is_relative_to(PREP),'WORKER_TARGET')
    job.win.worker_membership();request=read(folder/'observer/request.json');until=time.monotonic()+10
    while not (folder/'observer/gate.json').exists():need(time.monotonic()<until,'GATE_TIMEOUT');time.sleep(.02)
    budget=Budget(folder)
    try:
        gate=read(folder/'observer/gate.json');need(gate==dict(pid=os.getpid(),nonce=request['nonce']) and request['supervisor_pid']==os.getppid(),'WORKER_ID')
        verify_files(request['files']);need(request['runtime']==job.runtime(),'WORKER_RUNTIME')
        if request['task']=='research':
            b,h=binding();need(h==request['binding_sha256'],'REQUEST_BINDING');authorize(request['authorization'],h,folder)
            check_lineage(request,gate,read(PREP/'research.consumed.json'),os.getpid(),os.getppid())
            _ACTIVE=dict(pid=os.getpid(),permit=object())
            from .engine import run
            run(folder,_ACTIVE['permit'])
        else:
            need(request['task']=='fixtures' and folder.is_relative_to(PREP),'FIXTURE_SCOPE')
            from .tests import run
            result=run(folder);budget.save('observer/tests.json',result);need(result['passed'],'CONNECTION_TEST_FAILURE')
        verify_files(request['files']);budget.save('observer/worker-result.json',dict(status='COMPLETE'));return 0
    except BaseException as e:
        import traceback
        budget.save('observer/worker-error.json',dict(error=type(e).__name__+':'+str(e),traceback=traceback.format_exc()));return 1
    finally:_ACTIVE=None

def supervise(task,attempt=None,authorization=None):
    start=time.monotonic()
    need(task in ('fixtures','research'),'TASK')
    # Missing permission returns before folder creation, consumption, worker or material imports.
    auth=None;h=None
    if task=='research':
        need(authorization is not None and Path(authorization).resolve()==PREP/'research-authorization.json' and Path(authorization).is_file(),'RESEARCH_AUTHORIZATION_REQUIRED')
        need(os.environ.get('CODEX_THREAD_ID')==CHAT,'OWN_CHAT');b,h=binding();auth=read(authorization);authorize(auth,h,TARGET)
        need(not (PREP/'research.consumed.json').exists(),'RESEARCH_ALREADY_CONSUMED');folder=TARGET
    else:
        need(attempt and attempt.replace('-','').isalnum(),'ATTEMPT_NAME');folder=PREP/attempt
    need(not folder.exists(),'EXCLUSIVE_TARGET');inherited()
    child=None;error=None;installed=False;nonce=uuid.uuid4().hex;budget=Budget(folder)
    try:
        job.install();installed=True
        request=dict(task=task,nonce=nonce,supervisor_pid=os.getpid(),files=files(),runtime=job.runtime(),binding_sha256=h,authorization=auth)
        if task=='research':consume(PREP/'research.consumed.json',dict(execution_order=auth['execution_order'],nonce=nonce,binding_sha256=h,target=str(TARGET),historical_consumption='UNPROVEN'))
        folder.mkdir(parents=True);budget.save('observer/request.json',request)
        # Pipes are not retained; worker reports bounded errors as JSON instead of unbounded logs.
        child=subprocess.Popen([sys.executable,'-B',str(ROOT/'experiments/rw1/entry.py'),'--worker',str(folder)],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
        began=time.monotonic();job.win.verify_worker(int(child._handle));budget.save('observer/gate.json',dict(pid=child.pid,nonce=nonce))
        while child.poll() is None:
            need(time.monotonic()-start<300 and time.monotonic()-began<240,'TIME_LIMIT');need(total_size()<LIMITS['export'],'EXPORT_LIMIT');time.sleep(.05)
        need(child.returncode==0,'WORKER_FAILURE:'+str(read(folder/'observer/worker-error.json') if (folder/'observer/worker-error.json').exists() else child.returncode))
        need(read(folder/'observer/worker-result.json')['status']=='COMPLETE','WORKER_RESULT')
    except BaseException as e:error=type(e).__name__+':'+str(e)
    finally:
        if child is not None and child.poll() is None:child.kill();child.wait(timeout=5)
        need(time.monotonic()-start<300,'CLOSURE_TIMEOUT')
        terminal=dict(status='TECHNICAL_FAILURE' if error else 'COMPLETE',error=error,task=task,seconds=time.monotonic()-start,
            job=job.job() if installed else None,cleanup=child is None or child.poll() is not None,worker_exitcode=child.returncode if child else None,
            research_consumed=(PREP/'research.consumed.json').exists(),retry_allowed=False)
        budget.save('closure/terminal.json',terminal)
        budget.save('closure/technical-closure.json',dict(files={p.relative_to(folder).as_posix():info(p) for p in folder.rglob('*') if p.is_file()},consumed=info(PREP/'research.consumed.json') if task=='research' and (PREP/'research.consumed.json').exists() else None))
        need(time.monotonic()-start<300,'CLOSURE_TIMEOUT')
        budget.save('closure/completion.json',dict(status=terminal['status'],seconds=time.monotonic()-start,technical_closure_sha256=sha(folder/'closure/technical-closure.json')))
        print(raw(terminal).decode())
    return 1 if error else 0
