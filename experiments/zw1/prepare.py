"""ZW1 exclusive, bound supervisor/worker entry; no authorization creation."""
import gc,json,os,sys,time
from pathlib import Path
from tools._s2uc_ura1_fs_accounting_v4 import Terminal,Ledger,inventory,treebytes,supervise
from tools._s2uc_ura1_v2_series import LIMITS,raw
from tools.s2uc_ura1_runtime_qualify import runtime,sha,install_job
from .integration import condition_receipt,pair_receipt

ROOT=Path(__file__).resolve().parents[2]
PREP=ROOT/'reports/s2uc/zw1-research-preparation-20261018-01'
TARGET=ROOT/'reports/s2uc/zw1-comparison-16h-01'
AUTH=PREP/'authorization.json'
NAMESPACE='MCM-ZW1/source/v1'
MATRIX_SHA='cd452bee76ea2b1b64c920afdd9c70211e5ba7abc7207049f4e7e280e5703f6c'
MODES=('complete','source_failure','archive_failure','deadline','archive_budget')
EXECUTION_PLAN=dict(pairs=16,stories=32,frames_per_story=1024,policy=64,live_reference=64,archive_reference=64,extra_policy_measurement=0,source_reconstruction=32,statistics_reference=1)

def exact_call():return [sys.executable,'-B','-m','experiments.zw1.prepare','run',str(PREP/'prestart.json'),str(AUTH)]

def binding_paths():
    paths=[]
    for name in ('tools','tests','mcm_field_organism'):
        paths.extend(p.relative_to(ROOT).as_posix() for p in (ROOT/name).rglob('*.py'))
    paths.extend(p.relative_to(ROOT).as_posix() for p in (ROOT/'experiments/zw1').rglob('*') if p.is_file())
    paths.extend(['AGENTS.md','docs/S2UC_ZW1_ZEITLICHE_WIEDERKEHR_KONZEPTVERTRAG_20261018.md',
        'reports/s2uc/zw1-neutral-preparation-20261018-01/delivery-manifest.json',
        'reports/s2uc/zw1-neutral-preparation-20261018-01/dependencies.json',
        'reports/s2uc/zw1-neutral-preparation-20261018-01/matrix-binding.json',
        'reports/s2uc/er1-v2-preparation-20261018-01/prestart.json',
        'reports/s2uc/er1-v2-witness-audit-20261018-03/delivery-manifest.json',
        (PREP/'bootstrap.bin').relative_to(ROOT).as_posix()])
    return sorted(set(paths))

def validate_binding(path):
    path=Path(path).resolve()
    if path!=PREP/'prestart.json':raise ValueError('PRESTART_PATH')
    b=json.loads(path.read_bytes());digest=sha(path)
    if path.with_suffix('.sha256').read_text().strip()!=digest:raise ValueError('PRESTART_HASH')
    if b['kind']!='ZW1_PRESTART' or b['limits']!=LIMITS or b['runtime']!=runtime() or b['target']!=str(TARGET) or b['namespace']!=NAMESPACE:raise ValueError('PRESTART_SCOPE')
    if b['call']!=exact_call() or b['execution_plan']!=EXECUTION_PLAN:raise ValueError('PRESTART_EXECUTION')
    if set(b['files'])!=set(binding_paths()):raise ValueError('BINDING_COVERAGE')
    for group in ('files','qualification'):
        for name,h in b[group].items():
            if sha(ROOT/name)!=h:raise ValueError('FILE_BINDING:'+name)
    if sha(PREP/'bootstrap.bin')!=MATRIX_SHA:raise ValueError('MATRIX_BINDING')
    return b,digest

def authorization(path,digest):
    if Path(path).resolve()!=AUTH:raise PermissionError('AUTH_PATH')
    value=json.loads(AUTH.read_bytes())
    if value!=dict(kind='ZW1_RESEARCH_ONCE',prestart_sha256=digest,allow_research=True) or value.get('allow_research') is not True:raise PermissionError('RESEARCH_NOT_AUTHORIZED')

def validate_admission(auth,folder):
    from tools import _s2uc_hx1_windows as win
    _,digest=validate_binding(PREP/'prestart.json');authorization(auth,digest)
    if Path(folder).resolve()!=TARGET:raise PermissionError('RESEARCH_TARGET')
    if json.loads((PREP/'CONSUMED.json').read_bytes())!=dict(consumed=True,prestart_sha256=digest,target=str(TARGET)):raise PermissionError('CONSUMED_MARKER')
    if json.loads((TARGET/'START.json').read_bytes())!=dict(consumed=True,prestart_sha256=digest,namespace=NAMESPACE):raise PermissionError('START_MARKER')
    if not (TARGET/'gate').exists():raise PermissionError('RESEARCH_GATE')
    win.worker_membership()

def limits_for(mode):return LIMITS|({'worker_seconds':30} if mode=='deadline' else {})

def wait_for(path,seconds=6):
    end=time.monotonic()+seconds
    while not path.exists():
        if time.monotonic()>end:raise TimeoutError('GATE_WAIT')
        time.sleep(.005)

def worker(folder,started,mode):
    from tools import _s2uc_hx1_windows as win
    from tools import _s2uc_er1_run_engine as engine
    from tools import _s2uc_ura1_delta_encode as codec
    from . import prepare_sources as src
    from .prepare_series import policy_case
    win.worker_membership();wait_for(folder/'gate')
    terminal=Terminal.attach(folder,started,limits=limits_for(mode));ledger=Ledger(terminal,treebytes(PREP))
    research=mode=='research';count=16 if research else 2
    current_arms=[];created=0;closed=0;pair_counts=[];manifest=[];reports=[]
    executions=dict(policy_started=0,policy_completed=0,live_reference_completed=0,archive_reference_completed=0,extra_policy_measurement=0)
    result=dict(status='TECHNICAL_ABORT',research=research)
    original_create=engine.create;original_run=engine.run_arm
    def source_barrier():
        if terminal.value.get('sources_sealed_before_policy') is not True:raise PermissionError('SOURCE_BARRIER')
        if sha(folder/'sources-manifest.json')!=terminal.value['source_manifest_sha256']:raise ValueError('MANIFEST_CHANGED')
        if len(manifest)!=count*2:raise ValueError('SOURCE_COUNT')
        for entry in manifest:
            if sha(folder/entry['path'])!=entry['sha256']:raise ValueError('SOURCE_CHANGED')
    def create(policy):
        nonlocal created
        source_barrier()
        if created>=count*4 or len(current_arms)>=4:raise ValueError('ARM_COUNT')
        a=original_create(policy)
        if a.closed or a.accepted or a.arm._candidate or a.arm._retained_many or any(a is b for b in current_arms):raise ValueError('ARM_NOT_FRESH')
        current_arms.append(a);created+=1;executions['policy_started']+=1
        terminal.value['cleanup']='UNCONFIRMED';terminal.value['arms_created']=created;terminal.value['executions']=executions;terminal.save()
        return a
    def run_arm(*args,**kwargs):
        value=original_run(*args,**kwargs);executions['policy_completed']+=1;executions['live_reference_completed']+=1
        return value
    engine.create=create;engine.run_arm=run_arm
    try:
        permit=src.admit(AUTH,folder) if research else None
        for pair in range(1,count+1):
            ledger.check();description=src.generate(pair,256 if research else 24,neutral=not research,permit=permit)
            ref=src.reconstruct(pair,256 if research else 24,neutral=not research,permit=permit)
            if description!=ref:raise ValueError('SOURCE_RECONSTRUCTION')
            for label in ('A','B'):
                value=src.materialize(description,label,neutral=not research,permit=permit);src.verify_material(value,ref,label)
                name=f'pair-{pair:02d}-{label}-source.json';digest=ledger.write(name,value,'source')
                manifest.append(dict(pair=pair,condition=label,path=name,sha256=digest))
        del description,ref,value
        ledger.write('sources-manifest.json',dict(namespace=NAMESPACE if research else src.NEUTRAL,entries=manifest,all_before_policy=True))
        terminal.value.update(source_manifest_sha256=sha(folder/'sources-manifest.json'),sources_sealed_before_policy=created==0);terminal.save()
        if mode=='source_failure':
            with (folder/manifest[0]['path']).open('ab') as f:f.write(b' ')
        for pair in range(1,count+1):
            terminal.begin(pair);conditions={}
            if mode=='deadline' and pair==2:
                # No live arm here: test actual supervisor kill without claiming arm cleanup after a kill.
                terminal.value.update(cleanup='CONFIRMED',deadline_wait=True);terminal.save();time.sleep(35)
            for label in ('A','B'):
                source_barrier();ledger.check()
                entry=next(x for x in manifest if x['pair']==pair and x['condition']==label)
                value=json.loads((folder/entry['path']).read_bytes())
                fault='anchor' if mode in ('archive_failure','archive_budget') and pair==2 and label=='B' else None
                report=policy_case(2*(pair-1)+(1 if label=='A' else 2),value,ledger,neutral=not research,fault=fault)
                executions['archive_reference_completed']+=2
                conditions[label]=condition_receipt(pair,label,report)
                del value,report;gc.collect()
            if len(current_arms)!=4 or len({id(a) for a in current_arms})!=4 or not all(a.closed and not any(a.bank) for a in current_arms) or codec.ACTIVE is not None:raise ValueError('PAIR_ARM_CLEANUP')
            receipt=pair_receipt(pair,conditions);ledger.write(f'pair-{pair:02d}-receipt.json',receipt)
            pair_counts.append(dict(pair=pair,arms=4,distinct=4,cleanup=True));closed+=4;current_arms.clear();gc.collect()
            terminal.value.update(arms_closed=closed,pair_arm_counts=pair_counts,executions=executions)
            terminal.completed(pair,True);reports.append(receipt)
        if research:
            from .statistics import primary,reference
            matrix=(PREP/'bootstrap.bin').read_bytes();summary=primary(reports,matrix,MATRIX_SHA);independent=reference(reports,matrix)
            if any(summary[k]!=independent[k] for k in ('mean','pairs','ci')):raise ValueError('STATISTICS_REFERENCE')
            if executions!=dict(policy_started=64,policy_completed=64,live_reference_completed=64,archive_reference_completed=64,extra_policy_measurement=0):raise ValueError('EXECUTION_COUNTS')
            ledger.write('statistics.json',summary);ledger.write('statistics-reference.json',independent)
        result.update(status='COMPLETE',complete_pairs=len(reports),reference_equal=True)
    except Exception as error:
        terminal.diagnose(error,'worker');terminal.save()
    finally:
        engine.create=original_create;engine.run_arm=original_run
        clean=all(a.closed and not any(a.bank) for a in current_arms) and codec.ACTIVE is None
        closed+=sum(a.closed and not any(a.bank) for a in current_arms)
        terminal.value.update(cleanup='CONFIRMED' if clean and closed==created else 'UNCONFIRMED',arms_created=created,arms_closed=closed,executions=executions,pair_arm_counts=pair_counts)
        result.update(completed_pairs=terminal.value['completed_cases'],active_pair=terminal.value['active_case'],cleanup=terminal.value['cleanup'],executions=executions)
        if terminal.value['first_failure']:result['first_failure']=terminal.value['first_failure']
        terminal.save()
        try:
            if mode=='archive_budget' and terminal.value['first_failure']:
                (folder/'budget-injecting').touch();snap=inventory(folder)
                with (folder/'neutral-budget.txt').open('xb') as f:f.truncate(LIMITS['administration']-snap['groups']['admin']+1)
            ledger.write('worker.json',result)
        except Exception as error:terminal.diagnose(error,'worker_report');terminal.save()
        finally:
            if mode=='archive_budget':(folder/'budget-finished').touch()

def launch(folder,started,mode,digest=None):
    from tools import _s2uc_hx1_windows as win
    terminal=Terminal(folder,started,treebytes(PREP),limits=limits_for(mode))
    terminal.value.update(research=mode=='research',prestart_sha256=digest,namespace=NAMESPACE if mode=='research' else 'MCM-ZW1/neutral/v1');terminal.save()
    ledger=Ledger(terminal,treebytes(PREP));ledger.final=True
    if mode=='archive_budget':
        def hook(attempt,parent,names):
            if parent==folder and 'budget-injecting' in names:wait_for(folder/'budget-finished')
        ledger.hook=hook
    def admit(child):win.verify_worker(int(child._handle));ledger.write('gate','verified')
    def finish(current):
        terminal.refresh();value=json.loads((folder/'worker.json').read_bytes())
        if value['status']!='COMPLETE':terminal.fail(value.get('first_failure','WORKER_INCOMPLETE'))
        if value['status']=='COMPLETE' and (value['completed_pairs']!=list(range(1,17 if mode=='research' else 3)) or value['cleanup']!='CONFIRMED'):raise ValueError('PAIR_COMPLETENESS')
        current.write('result.json',value|dict(retry_allowed=False,authorization_consumed=mode=='research'),'closure')
        snap=inventory(folder)
        current.write('closure.json',dict(prestart_sha256=digest,files={n:dict(bytes=v['bytes'],sha256=sha(folder/n)) for n,v in snap['files'].items() if n!='terminal.json'}),'closure')
    supervise(terminal,[sys.executable,'-B','-m','experiments.zw1.prepare','worker',str(folder),str(started),mode],ledger,admitted=admit,report_writer=finish)
    terminal.refresh();terminal.value['job']=win.snapshot();terminal.save();print(json.dumps(terminal.value));return terminal.value

def run(binding,auth):
    started=time.monotonic();install_job();_,digest=validate_binding(binding);authorization(auth,digest)
    if time.monotonic()-started>=LIMITS['worker_seconds']:raise TimeoutError('ADMISSION_DEADLINE')
    if (PREP/'CONSUMED.json').exists():raise PermissionError('AUTH_ALREADY_CONSUMED')
    TARGET.mkdir(exist_ok=False)
    with (PREP/'CONSUMED.json').open('xb') as f:f.write(raw(dict(consumed=True,prestart_sha256=digest,target=str(TARGET))));f.flush();os.fsync(f.fileno())
    with (TARGET/'START.json').open('xb') as f:f.write(raw(dict(consumed=True,prestart_sha256=digest,namespace=NAMESPACE)))
    return launch(TARGET,started,'research',digest)

if __name__=='__main__':
    action=sys.argv[1]
    if action=='run':run(sys.argv[2],sys.argv[3])
    elif action=='neutral':
        mode=sys.argv[2]
        if mode not in MODES:raise ValueError('NEUTRAL_MODE')
        started=time.monotonic();install_job();folder=PREP/('integration-'+mode);folder.mkdir(exist_ok=False);launch(folder,started,mode)
    elif action=='worker':
        folder=Path(sys.argv[2]).resolve();mode=sys.argv[4]
        if (mode=='research' and folder!=TARGET) or (mode!='research' and (mode not in MODES or folder!=PREP/('integration-'+mode))):raise PermissionError('WORKER_SCOPE')
        worker(folder,float(sys.argv[3]),mode)
    else:raise ValueError('ACTION')
