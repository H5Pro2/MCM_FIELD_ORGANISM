"""Separately bound URA1 preparation: actual neutral arms, fresh gated sources."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from tools._s2uc_ura1_terminal_v3 import Terminal, ReservedLedger, supervise, execute_with_receipts
from tools._s2uc_ura1_v2_series import LIMITS, raw, policy_case
from tools.s2uc_ura1_runtime_qualify import runtime, sha, install_job

ROOT = Path(__file__).resolve().parents[1]
PREP = ROOT/'reports/s2uc/ura1-v3-preparation-20261015-01'
TARGET = ROOT/'reports/s2uc/ura1-comparison-v3-terminal16h'
AUTH = PREP/'authorization.json'
NAMESPACE = 'MCM-URA1/source/v3'


def treebytes(folder):
    return sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())


def validate_binding(path):
    path = Path(path).resolve()
    if path != PREP/'prestart.json':
        raise ValueError('PRESTART_PATH')
    b = json.loads(path.read_bytes()); digest = sha(path)
    if path.with_suffix('.sha256').read_text().strip() != digest:
        raise ValueError('PRESTART_HASH')
    if b['limits'] != LIMITS or b['runtime'] != runtime() or b['target'] != str(TARGET) or b['namespace'] != NAMESPACE:
        raise ValueError('PRESTART_SCOPE')
    if b['call'] != [sys.executable,'-m','tools.s2uc_ura1_prepare_v3','run',str(path),str(AUTH)]:
        raise ValueError('PRESTART_CALL')
    for name, digest_file in b['files'].items():
        if sha(ROOT/name) != digest_file:
            raise ValueError('FILE_BINDING:'+name)
    return b, digest


def authorization(path, digest):
    if Path(path).resolve() != AUTH:
        raise PermissionError('AUTH_PATH')
    if json.loads(AUTH.read_bytes()) != dict(kind='URA1_RESEARCH_ONCE_V3',prestart_sha256=digest,allow_research=True):
        raise PermissionError('RESEARCH_NOT_AUTHORIZED')


def validate_admission(auth, folder):
    _, digest = validate_binding(PREP/'prestart.json')
    authorization(auth,digest)
    if Path(folder).resolve() != TARGET:
        raise PermissionError('RESEARCH_TARGET')
    marker = json.loads((TARGET/'START.json').read_bytes())
    if marker != dict(consumed=True,prestart_sha256=digest,namespace=NAMESPACE):
        raise PermissionError('RESEARCH_MARKER')
    if not (TARGET/'gate').exists():
        raise PermissionError('RESEARCH_GATE')


class IntegratedLedger(ReservedLedger):
    """Neutral faults injected only after a real second-case arm is created."""
    def __init__(self, terminal, prep, neutral_mode):
        super().__init__(terminal,prep)
        self.mode=neutral_mode; self.arm_started=False; self.fired=False

    def check(self):
        if self.mode in ('export','admin','deadline') and self.arm_started and self.terminal.value['active_case']==2 and not self.fired:
            self.fired=True
            if self.mode=='deadline':
                time.sleep(20)
            else:
                super().check()
                files=[p for p in self.folder.iterdir() if p.is_file()]
                if self.mode=='export':
                    size=self.limits['export']-self.prep_bytes-sum(p.stat().st_size for p in files)
                    name='neutral-budget.partial'
                else:
                    size=self.limits['administration']-sum(p.stat().st_size for p in files if self.entries[str(p.resolve())][0]=='admin')
                    name='neutral-budget.txt'
                with (self.folder/name).open('xb') as f:
                    f.truncate(size)
                self.write('neutral-overflow.json',dict(injected=True))
        super().check()


def worker(folder, started, mode):
    from tools import _s2uc_hx1_windows as win
    from tools import _s2uc_ura1_v3_sources as src
    from tools import _s2uc_ura1_v3_source_reference as sr
    from tools import _s2uc_ura1_v2_engine as engine
    from tools import _s2uc_ura1_delta_encode as codec
    win.worker_membership()
    while not (folder/'gate').exists():
        time.sleep(.01)
    terminal=Terminal.attach(folder,started)
    ledger=IntegratedLedger(terminal,treebytes(PREP),mode)
    result=dict(status='TECHNICAL_ABORT',research=mode=='research')
    arms=[]; original_create=engine.create
    def tracked(policy):
        arm=original_create(policy);arms.append(arm);ledger.arm_started=True
        return arm
    engine.create=tracked
    try:
        if mode=='research':
            validate_admission(AUTH,folder)
            permit=src.admit(AUTH,folder);manifest=[]
            for r in range(1,33):
                ledger.check(); value=src.generate(r,neutral=False,permit=permit)
                sr.verify(value,r,neutral=False,permit=permit)
                name=f'URA1-{r:02d}-D-source.json'
                digest=ledger.write(name,value,'source')
                manifest.append(dict(replicate=r,path=name,sha256=digest))
            ledger.write('sources-manifest.json',dict(entries=manifest,all_before_policy=True,namespace=NAMESPACE))
            cases=[]
            for entry in manifest:
                path=folder/entry['path']
                if sha(path)!=entry['sha256']:
                    raise ValueError('SOURCE_CHANGED')
                cases.append((entry['replicate'],json.loads(path.read_bytes())))
        else:
            # Fixed eight-frame hand fixtures; never calls a research generator.
            catalog=[[x+j/4096 for j in range(48)] for x in (.125,.875,.5,.25,.75,.0625)]
            cases=[(r,dict(catalog=catalog,ids=([0,2,3,5,1,2,4,5] if r==1 else [1,2,3,5,0,2,4,5]))) for r in (1,2)]
        def run_case(number,value,current):
            ledger.arm_started=False
            return policy_case(number,value,current,neutral=mode!='research')
        reports=execute_with_receipts(cases,run_case,ledger,[r for r,_ in cases])
        if mode=='research':
            from tools import _s2uc_ura1_v2_stats as stats
            from tools import _s2uc_ura1_v2_stats_reference as ref
            matrix=(PREP/'bootstrap.bin').read_bytes()
            ref.verify_matrix(matrix); summary=stats.aggregate(reports,matrix,ledger.check)
            ref.verify(reports,matrix,summary,ledger.check)
            ledger.write('statistics.json',summary)
        else:
            ledger.write('neutral-integrity.json',dict(cases=[dict(replicate=r['replicate'],integrity=r['integrity'],counts=r['counts']) for r in reports]))
        result.update(status='COMPLETE',complete_cases=len(reports),archive_integrity=True,reference_equal=True)
    except Exception as exc:
        terminal.fail(type(exc).__name__+':'+str(exc))
        terminal.save()
    finally:
        engine.create=original_create
        clean=bool(arms) and all(a.closed and not any(a.bank) for a in arms) and codec.ACTIVE is None
        terminal.value['cleanup']='CONFIRMED' if clean else 'UNCONFIRMED'
        terminal.value['arms_created']=len(arms)
        terminal.value['distinct_arms']=len({id(a) for a in arms})
        result.update(completed_cases=terminal.value['completed_cases'],active_case=terminal.value['active_case'],cleanup=terminal.value['cleanup'])
        if terminal.value['first_failure']:
            result['first_failure']=terminal.value['first_failure']
        terminal.save()
        try:
            if mode=='export' and ledger.fired:
                # execute() removed the first injected partial during cleanup.
                # Refill only in this neutral probe to exercise report failure too.
                size=LIMITS['export']-ledger.prep_bytes-treebytes(folder)
                with (folder/'neutral-report-budget.partial').open('xb') as f:
                    f.truncate(size)
            ledger.write('worker.json',result)
        except Exception as exc:
            terminal.fail('WORKER_REPORT_FAILED:'+type(exc).__name__+':'+str(exc))
            terminal.save()


def launch(folder, started, mode, digest=None):
    from tools import _s2uc_hx1_windows as win
    terminal=Terminal(folder,started,treebytes(PREP))
    terminal.value.update(research=mode=='research',prestart_sha256=digest,namespace=NAMESPACE if mode=='research' else 'fixed-neutral-hand-fixtures')
    terminal.save()
    ledger=ReservedLedger(terminal,treebytes(PREP));ledger.final=True
    def admit(child):
        win.verify_worker(int(child._handle));ledger.write('gate','verified')
    def finish(current):
        terminal.refresh()
        p=folder/'worker.json'
        if not p.exists():
            raise ValueError('WORKER_REPORT_MISSING')
        value=json.loads(p.read_bytes())
        if value['status']!='COMPLETE':
            terminal.fail(value.get('first_failure','WORKER_INCOMPLETE'))
        if value['status']=='COMPLETE' and (len(value['completed_cases'])!=(32 if mode=='research' else 2) or value['cleanup']!='CONFIRMED'):
            raise ValueError('COMPLETENESS_OR_CLEANUP')
        terminal.value['job']=win.snapshot();terminal.save()
        current.write('result.json',value|dict(retry_allowed=False,authorization_consumed=mode=='research',job=win.snapshot()),'closure')
        entries={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.iterdir() if p.is_file() and p!=terminal.path}
        current.write('closure.json',dict(files=entries,prestart_sha256=digest),'closure')
    value=supervise(terminal,[sys.executable,'-m','tools.s2uc_ura1_prepare_v3','worker',str(folder),str(started),mode],ledger,
                    admitted=admit,report_writer=finish,worker_deadline=8 if mode=='deadline' else None)
    # Saved terminal is the final authoritative supervisor record, also on abort.
    terminal.refresh();terminal.value['job']=win.snapshot()
    if time.monotonic()-started>LIMITS['total_seconds']:
        terminal.fail('GLOBAL_TIMEOUT');terminal.value['status']='TECHNICAL_ABORT'
    terminal.save()
    print(json.dumps(terminal.value))
    return terminal.value


def run(binding,auth):
    started=time.monotonic();install_job()
    _,digest=validate_binding(binding);authorization(auth,digest)
    if time.monotonic()-started>LIMITS['worker_seconds']:
        raise TimeoutError('ADMISSION_DEADLINE')
    TARGET.mkdir(exist_ok=False)
    with (TARGET/'START.json').open('xb') as f:
        f.write(raw(dict(consumed=True,prestart_sha256=digest,namespace=NAMESPACE)))
    return launch(TARGET,started,'research',digest)


if __name__=='__main__':
    action=sys.argv[1]
    if action=='run':
        run(sys.argv[2],sys.argv[3])
    elif action=='neutral':
        mode=sys.argv[2]
        if mode not in ('complete','export','admin','deadline'):
            raise ValueError('NEUTRAL_MODE')
        started=time.monotonic();install_job()
        folder=PREP/('integration-'+mode);folder.mkdir(exist_ok=False)
        launch(folder,started,mode)
    elif action=='worker':
        folder=Path(sys.argv[2]).resolve();mode=sys.argv[4]
        if (mode=='research' and folder!=TARGET) or (mode!='research' and (mode not in ('complete','export','admin','deadline') or folder!=PREP/('integration-'+mode))):
            raise PermissionError('WORKER_SCOPE')
        worker(folder,float(sys.argv[3]),mode)
    else:
        raise ValueError('ACTION')
