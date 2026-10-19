"""Exclusive FW1 admission; production authorization is never issued here."""
import gc,hashlib,json,os,sys,time
from pathlib import Path
from tools._s2uc_ura1_v2_series import LIMITS,raw
from tools._s2uc_ura1_fs_accounting_v4 import Terminal,Ledger,inventory,treebytes,supervise
from tools.s2uc_ura1_runtime_qualify import runtime,sha,install_job
from experiments.fw1.integration import condition_receipt,pair_receipt

ROOT=Path(__file__).resolve().parents[2]
PREP=ROOT/'reports/s2uc/fw1-research-preparation-20261018-01'
TARGET=ROOT/'reports/s2uc/fw1-comparison-16h-01'
PROBE=ROOT/'reports/s2uc/fw1-neutral-fullsize-20261018-01'
AUTH=PREP/'authorization.json'
CONFIGS={'research':PREP/'prestart.json','fullsize':PREP/'fullsize.json','short':PREP/'short.json'}
TARGETS={'research':TARGET,'fullsize':PROBE,'short':PREP/'short-run'}

def journal(event,**data):
    with (PREP/'execution-ledger.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(dict(event=event,**data),sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())

def code_paths():
    return sorted({p.relative_to(ROOT).as_posix() for base in ('tools','tests','mcm_field_organism','experiments/fw1','experiments/fw1_prepare') for p in (ROOT/base).rglob('*.py')}|{'AGENTS.md','docs/S2UC_FW1_FEHLERWISSEN_GEGENPRUEFVERTRAG_20261018.txt'})

def auth_path(config):return AUTH if config['mode']=='research' else CONFIGS[config['mode']].with_suffix('.authorization.json')
def consumed_path(config):return CONFIGS[config['mode']].with_suffix('.consumed.json')
def exact_call(config):return [sys.executable,'-B','-m','experiments.fw1_prepare.entry','run',str(CONFIGS[config['mode']]),str(auth_path(config))]

def validate_binding(path):
    path=Path(path).resolve();c=json.loads(path.read_bytes());mode=c.get('mode')
    if mode not in CONFIGS or path!=CONFIGS[mode]:raise PermissionError('CONFIG_PATH')
    digest=sha(path)
    if path.with_suffix('.sha256').read_text().strip()!=digest:raise ValueError('CONFIG_HASH')
    count=16 if mode=='research' else 1;frames=96 if mode=='short' else 1024
    ns='MCM-FW1/source/v1' if mode=='research' else 'MCM-FW1/neutral/v1'
    if c['kind']!='FW1_PRESTART' or c['target']!=str(TARGETS[mode]) or c['pairs']!=count or c['frames']!=frames or c['namespace']!=ns or c['limits']!=LIMITS or c['runtime']!=runtime():raise ValueError('CONFIG_SCOPE')
    if c['call']!=exact_call(c) or set(c['files'])!=set(code_paths()):raise ValueError('CODE_COVERAGE')
    for group in ('files','qualification'):
        for name,h in c[group].items():
            if sha(ROOT/name)!=h:raise ValueError('FILE_BINDING:'+name)
    if c['matrix_sha256']!=sha(PREP/'bootstrap.bin'):raise ValueError('MATRIX_BINDING')
    if mode=='research':
        if c['sources']:raise ValueError('RESEARCH_SOURCES_PRECREATED')
    else:
        if len(c['sources'])!=2 or [s['condition'] for s in c['sources']]!=['A','B']:raise ValueError('NEUTRAL_SOURCES')
        for s in c['sources']:
            if s['pair']!=1 or sha(ROOT/s['path'])!=s['sha256']:raise ValueError('SOURCE_BINDING')
    return c,digest

def authorization(path,c,digest):
    if Path(path).resolve()!=auth_path(c):raise PermissionError('AUTH_PATH')
    expected=dict(kind='FW1_RESEARCH_ONCE' if c['mode']=='research' else 'FW1_NEUTRAL_ONCE',prestart_sha256=digest,target=c['target'],allow_research=c['mode']=='research')
    value=json.loads(Path(path).read_bytes())
    if value!=expected or type(value.get('allow_research')) is not bool:raise PermissionError('AUTH_SCOPE')

def validate_admission(auth,folder):
    from tools import _s2uc_hx1_windows as win
    folder=Path(folder).resolve();start=json.loads((folder/'START.json').read_bytes())
    c,digest=validate_binding(start['config']);authorization(auth,c,digest)
    marker=dict(prestart_sha256=digest,target=c['target'],config=str(CONFIGS[c['mode']]))
    if folder!=TARGETS[c['mode']] or start!=marker or json.loads(consumed_path(c).read_bytes())!=marker:raise PermissionError('CONSUMED_BINDING')
    if not (folder/'gate').exists():raise PermissionError('WORKER_GATE')
    win.worker_membership();return c,digest

def write_exclusive(path,value):
    with Path(path).open('xb') as f:f.write(raw(value));f.flush();os.fsync(f.fileno())

def worker(folder,started,configpath):
    from tools import _s2uc_hx1_windows as win
    from tools import _s2uc_ura1_delta_encode as codec
    from . import engine,sources,archive
    from .series import policy_case
    end=time.monotonic()+6
    while not (folder/'gate').exists():
        if time.monotonic()>end:raise TimeoutError('WORKER_GATE')
        time.sleep(.005)
    c,digest=validate_admission(auth_path(json.loads(Path(configpath).read_bytes())),folder)
    terminal=Terminal.attach(folder,started);ledger=Ledger(terminal,treebytes(PREP));research=c['mode']=='research'
    counters=dict(policy_started=0,policy_completed=0,live_started=0,live_completed=0,archive_started=0,archive_completed=0,source_pairs_generated=0,source_pairs_reconstructed=0,source_conditions_verified=0,statistics_reference_started=0,statistics_reference_completed=0)
    arms=[];closed=0;manifest=[];reports=[];state={'source':None}
    original_create=engine.create;original_ref=engine.Reference;original_archive_ref=archive.Reference
    def save():terminal.value['executions']=counters.copy();terminal.save()
    def barrier():
        if terminal.value.get('sources_sealed_before_policy') is not True or len(manifest)!=c['pairs']*2:raise PermissionError('SOURCE_BARRIER')
        if sha(folder/'sources-manifest.json')!=terminal.value['source_manifest_sha256']:raise ValueError('MANIFEST_CHANGED')
        for s in manifest:
            if sha(folder/s['path'])!=s['sha256']:raise ValueError('SOURCE_CHANGED')
    def validate_values(values):
        barrier();entry=state['source']
        if entry is None or len(values)!=c['frames']:raise PermissionError('ARM_SCOPE')
        value=json.loads((folder/entry['path']).read_bytes())
        if raw(values)!=raw([value['catalog'][i] for i in value['ids']]):raise ValueError('ARM_SOURCE')
    def create(mode):
        barrier()
        if counters['policy_started']>=c['pairs']*4 or len(arms)>=4:raise ValueError('ARM_LIMIT')
        counters['policy_started']+=1;terminal.value['cleanup']='UNCONFIRMED';save()
        a=original_create(mode)
        if a.accepted or a.closed or a.arm._retained_many or a.arm._candidate or any(a is old for old in arms):raise ValueError('ARM_NOT_FRESH')
        arms.append(a);return a
    class Live(original_ref):
        def __init__(self,*args):counters['live_started']+=1;save();super().__init__(*args)
        def finish(self):super().finish();counters['live_completed']+=1;save()
    class Archived(original_archive_ref):
        def __init__(self,*args):counters['archive_started']+=1;save();super().__init__(*args)
        def finish(self):super().finish();counters['archive_completed']+=1;save()
    original_run=engine.run_arm
    def measured(*args,**kw):
        result=original_run(*args,**kw);counters['policy_completed']+=1;save();return result
    engine.create=create;engine.Reference=Live;archive.Reference=Archived;engine.run_arm=measured;engine.VALIDATE=validate_values
    result=dict(status='TECHNICAL_ABORT',research=research)
    save()
    try:
        if research:
            permit=sources.admit(AUTH,folder)
            for pair in range(1,17):
                counters['source_pairs_generated']+=1;save();description=sources.generate(pair,256,neutral=False,permit=permit)
                counters['source_pairs_reconstructed']+=1;save();ref=sources.reconstruct(pair,256,neutral=False,permit=permit)
                if description!=ref:raise ValueError('SOURCE_RECONSTRUCTION')
                for label in ('A','B'):
                    value=sources.materialize(description,label,neutral=False,permit=permit);sources.verify_material(value,ref,label);counters['source_conditions_verified']+=1;save()
                    name=f'pair-{pair:02d}-{label}-source.json';h=ledger.write(name,value,'source');manifest.append(dict(pair=pair,condition=label,path=name,sha256=h))
        else:
            for s in c['sources']:
                value=json.loads((ROOT/s['path']).read_bytes());name=f'pair-01-{s["condition"]}-source.json'
                h=ledger.write(name,value,'source');manifest.append(dict(pair=1,condition=s['condition'],path=name,sha256=h))
        ledger.write('sources-manifest.json',dict(namespace=c['namespace'],entries=manifest,all_before_policy=True))
        terminal.value.update(source_manifest_sha256=sha(folder/'sources-manifest.json'),sources_sealed_before_policy=counters['policy_started']==0);save()
        for pair in range(1,c['pairs']+1):
            terminal.begin(pair);conditions={}
            for label in ('A','B'):
                state['source']=next(s for s in manifest if s['pair']==pair and s['condition']==label);barrier()
                value=json.loads((folder/state['source']['path']).read_bytes())
                r=policy_case(2*(pair-1)+(1 if label=='A' else 2),value,ledger,neutral=not research)
                conditions[label]=condition_receipt(pair,label,r);del r,value;gc.collect()
            if len(arms)!=4 or len({id(a) for a in arms})!=4 or not all(a.closed and not any(a.bank) for a in arms) or codec.ACTIVE is not None:raise ValueError('PAIR_CLEANUP')
            receipt=pair_receipt(pair,conditions);ledger.write(f'pair-{pair:02d}-receipt.json',receipt)
            closed+=4;arms.clear();gc.collect();terminal.value.update(arms_closed=closed,cleanup='CONFIRMED');terminal.completed(pair,True);reports.append(receipt)
        if research:
            from experiments.fw1.statistics import primary,reference
            matrix=(PREP/'bootstrap.bin').read_bytes();a=primary(reports,matrix,neutral=False,digest=c['matrix_sha256'])
            counters['statistics_reference_started']+=1;save();b=reference(reports,matrix,neutral=False,digest=c['matrix_sha256']);counters['statistics_reference_completed']+=1;save()
            if any(a[k]!=b[k] for k in ('mean','pairs','ci','informative','verdict')):raise ValueError('STATISTICS_REFERENCE')
            ledger.write('statistics.json',a);ledger.write('statistics-reference.json',b)
        if any(counters[k]!=4*c['pairs'] for k in ('policy_started','policy_completed','live_started','live_completed','archive_started','archive_completed')):raise ValueError('EXECUTION_COUNTS')
        result['status']='COMPLETE'
    except Exception as exc:terminal.diagnose(exc,'worker');terminal.save()
    finally:
        engine.create=original_create;engine.Reference=original_ref;archive.Reference=original_archive_ref;engine.run_arm=original_run
        engine.VALIDATE=lambda _:(_ for _ in ()).throw(PermissionError('UNARMED'))
        for a in arms:
            if not a.closed:a._terminate()
        closed+=sum(a.closed and not any(a.bank) for a in arms)
        cleanup=closed==counters['policy_started'] and codec.ACTIVE is None
        terminal.value.update(arms_created=counters['policy_started'],arms_closed=closed,cleanup='CONFIRMED' if cleanup else 'UNCONFIRMED');save()
        result.update(executions=counters,completed_pairs=terminal.value['completed_cases'],cleanup=terminal.value['cleanup'],first_failure=terminal.value['first_failure']);ledger.final=True
        try:ledger.write('worker.json',result)
        except Exception as exc:terminal.diagnose(exc,'worker_report');terminal.save()

def launch(terminal,c,digest):
    from tools import _s2uc_hx1_windows as win
    folder=terminal.folder;ledger=Ledger(terminal,treebytes(PREP));ledger.final=True
    def admit(child):win.verify_worker(int(child._handle));ledger.write('gate','verified')
    def finish(current):
        terminal.refresh();v=json.loads((folder/'worker.json').read_bytes())
        if v['status']!='COMPLETE':terminal.fail(v['first_failure'] or 'WORKER_INCOMPLETE')
        elif v['completed_pairs']!=list(range(1,c['pairs']+1)) or v['cleanup']!='CONFIRMED':raise ValueError('PAIR_COMPLETENESS')
        current.write('result.json',v|dict(prestart_sha256=digest,retry_allowed=False),'closure')
        snap=inventory(folder);current.write('closure.json',dict(files={n:dict(bytes=v['bytes'],sha256=sha(folder/n)) for n,v in snap['files'].items() if n!='terminal.json'}),'closure')
    supervise(terminal,[sys.executable,'-B','-m','experiments.fw1_prepare.entry','worker',str(folder),str(terminal.started),str(CONFIGS[c['mode']])],ledger,admitted=admit,report_writer=finish)
    terminal.refresh();terminal.value['job']=win.snapshot();terminal.save();return terminal.value

def run(configpath,auth):
    started=time.monotonic();c,digest=validate_binding(configpath);authorization(auth,c,digest)
    if consumed_path(c).exists():raise PermissionError('AUTH_CONSUMED')
    folder=Path(c['target'])
    if folder.exists():raise FileExistsError('TARGET_EXISTS')
    install_job();folder.mkdir(exist_ok=False)
    # Terminal capacity is reserved before consuming authorization or starting a worker.
    terminal=Terminal(folder,started,treebytes(PREP));terminal.value.update(mode=c['mode'],prestart_sha256=digest,research=c['mode']=='research');terminal.save()
    marker=dict(prestart_sha256=digest,target=c['target'],config=str(CONFIGS[c['mode']]))
    write_exclusive(consumed_path(c),marker);write_exclusive(folder/'START.json',marker)
    return launch(terminal,c,digest)

if __name__=='__main__':
    if sys.argv[1]=='run':print(json.dumps(run(sys.argv[2],sys.argv[3])))
    elif sys.argv[1]=='worker':worker(Path(sys.argv[2]).resolve(),float(sys.argv[3]),sys.argv[4])
    else:raise PermissionError('ACTION')
