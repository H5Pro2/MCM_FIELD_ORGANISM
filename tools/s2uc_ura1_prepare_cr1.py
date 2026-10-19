"""Separately bound URA1 preparation: actual neutral arms, fresh gated sources."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from tools._s2uc_ura1_terminal_v3 import execute_with_receipts
from tools._s2uc_ura1_fs_accounting_v4 import Terminal, Ledger, inventory, treebytes, supervise, InventoryError
from tools._s2uc_ura1_cr1_series import LIMITS, raw, policy_case
from tools.s2uc_ura1_runtime_qualify import runtime, sha, install_job

ROOT = Path(__file__).resolve().parents[1]
PREP = ROOT/'reports/s2uc/ura1-cr1-preparation-20261017-01'
TARGET = ROOT/'reports/s2uc/ura1-cr1-comparison-16h-01'
AUTH = PREP/'authorization.json'
NAMESPACE = 'MCM-URA1-CR1/source/v1'


def validate_binding(path):
    path = Path(path).resolve()
    if path != PREP/'prestart.json':
        raise ValueError('PRESTART_PATH')
    b = json.loads(path.read_bytes()); digest = sha(path)
    if path.with_suffix('.sha256').read_text().strip() != digest:
        raise ValueError('PRESTART_HASH')
    if b['limits'] != LIMITS or b['runtime'] != runtime() or b['target'] != str(TARGET) or b['namespace'] != NAMESPACE:
        raise ValueError('PRESTART_SCOPE')
    if b['call'] != [sys.executable,'-m','tools.s2uc_ura1_prepare_cr1','run',str(path),str(AUTH)]:
        raise ValueError('PRESTART_CALL')
    for name, digest_file in b['files'].items():
        if sha(ROOT/name) != digest_file:
            raise ValueError('FILE_BINDING:'+name)
    return b, digest


def authorization(path, digest):
    if Path(path).resolve() != AUTH:
        raise PermissionError('AUTH_PATH')
    if json.loads(AUTH.read_bytes()) != dict(kind='URA1_CR1_RESEARCH_ONCE',prestart_sha256=digest,allow_research=True):
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


def wait_for(path):
    end=time.monotonic()+6
    while not path.exists():
        if time.monotonic()>end:raise TimeoutError('NEUTRAL_HANDSHAKE:'+str(path))
        time.sleep(.002)


class IntegratedLedger(Ledger):
    """Production accounting, with gated neutral faults and timing counters."""
    def __init__(self, terminal, prep, neutral_mode):
        super().__init__(terminal,prep)
        self.mode=neutral_mode;self.arm_started=False;self.fired=False
        self.calls=0;self.check_seconds=0.;self.max_check_seconds=0.

    def check(self):
        if self.mode in ('export','admin','temp','deadline','rename','unstable') and self.arm_started and self.terminal.value['active_case']==2 and not self.fired:
            self.fired=True
            if self.mode=='deadline':time.sleep(20)
            elif self.mode=='rename':
                path=self.folder/'neutral-rename.json.partial';path.write_bytes(b'x'*192)
                wait_for(self.folder/'scan-go-1');path.rename(self.folder/'neutral-rename.json')
                (self.folder/'scan-ack-1').touch()
            elif self.mode=='unstable':
                path=self.folder/'neutral-unstable.txt';path.write_bytes(b'x')
                for step in range(1,9):
                    wait_for(self.folder/f'scan-go-{step}')
                    path.write_bytes(b'x'*(step+1));(self.folder/f'scan-ack-{step}').touch()
                time.sleep(20)
            else:
                (self.folder/'neutral-injecting').touch()
                s=super().check()
                if self.mode=='export':size=self.limits['export']-self.prep_bytes-s['total']+1;name='neutral-budget.partial'
                elif self.mode=='temp':size=self.limits['temp']+1;name='neutral-budget.partial'
                else:size=self.limits['administration']-s['groups']['admin']+1;name='neutral-budget.txt'
                with (self.folder/name).open('xb') as f:f.truncate(size)
        begin=time.monotonic()
        try:return super().check()
        finally:
            duration=time.monotonic()-begin;self.calls+=1;self.check_seconds+=duration
            self.max_check_seconds=max(self.max_check_seconds,duration)


def worker(folder, started, mode):
    if mode not in ('research','complete','load','rename','export','admin','temp','unstable','deadline'):
        raise PermissionError('WORKER_MODE')
    from tools import _s2uc_hx1_windows as win
    from tools import _s2uc_ura1_cr1_sources as src
    from tools import _s2uc_ura1_cr1_source_reference as sr
    from tools import _s2uc_ura1_cr1_engine as engine
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
                name=f'URA1-CR1-{r:02d}-source.json'
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
            from tools._s2uc_ura1_cr1_neutral import fixtures
            cases=fixtures()
        def run_case(number,value,current):
            ledger.arm_started=False
            if mode=='research':
                return policy_case(number,value,current,neutral=False)
            from tools._s2uc_ura1_cr1_neutral import continuity_case
            return continuity_case(number,value,current)
        reports=execute_with_receipts(cases,run_case,ledger,[r for r,_ in cases])
        if mode=='research':
            from tools import _s2uc_ura1_cr1_stats as stats
            from tools import _s2uc_ura1_cr1_stats_reference as ref
            matrix=(PREP/'bootstrap.bin').read_bytes()
            ref.verify_matrix(matrix); summary=stats.aggregate(reports,matrix,ledger.check)
            ref.verify(reports,matrix,summary,ledger.check)
            ledger.write('statistics.json',summary)
        else:
            ledger.write('neutral-integrity.json',dict(cases=[dict(replicate=r['replicate'],integrity=r['integrity'],counts=r['counts']) for r in reports]))
        result.update(status='COMPLETE',complete_cases=len(reports),archive_integrity=True,reference_equal=True)
    except Exception as exc:
        terminal.diagnose(exc,'worker')
        terminal.save()
    finally:
        engine.create=original_create
        clean=bool(arms) and all(a.closed and not any(a.bank) for a in arms) and codec.ACTIVE is None
        terminal.value['cleanup']='CONFIRMED' if clean else 'UNCONFIRMED'
        terminal.value['arms_created']=len(arms)
        terminal.value['distinct_arms']=len({id(a) for a in arms})
        terminal.value['worker_accounting']=dict(calls=ledger.calls,seconds=ledger.check_seconds,max_seconds=ledger.max_check_seconds)
        result.update(completed_cases=terminal.value['completed_cases'],active_case=terminal.value['active_case'],cleanup=terminal.value['cleanup'])
        if terminal.value['first_failure']:
            result['first_failure']=terminal.value['first_failure']
        terminal.save()
        try:
            if mode in ('export','temp') and ledger.fired:
                # Series cleanup removed the first partial; test report failure too.
                size=(LIMITS['export']-ledger.prep_bytes-treebytes(folder)+1) if mode=='export' else LIMITS['temp']+1
                with (folder/'neutral-report-budget.partial').open('xb') as f:f.truncate(size)
            ledger.write('worker.json',result)
        except Exception as exc:
            terminal.diagnose(exc,'worker_report')
            terminal.save()
        finally:
            if mode in ('export','admin','temp') and ledger.fired:(folder/'neutral-fault-saved').touch()


def launch(folder, started, mode, digest=None):
    from tools import _s2uc_hx1_windows as win
    terminal=Terminal(folder,started,treebytes(PREP),limits=LIMITS|({'worker_seconds':8} if mode=='deadline' else {}))
    terminal.value.update(research=mode=='research',prestart_sha256=digest,namespace=NAMESPACE if mode=='research' else 'MCM-URA1-CR1/neutral/v1')
    terminal.save()
    ledger=IntegratedLedger(terminal,treebytes(PREP),'supervisor');ledger.final=True
    steps=[0];rename_observed=[False]
    def hook(attempt,parent,names):
        if parent!=folder:return
        if mode in ('export','admin','temp') and 'neutral-injecting' in names:
            wait_for(folder/'neutral-fault-saved')
        trigger=(mode=='rename' and 'neutral-rename.json.partial' in names and steps[0]==0) or (mode=='unstable' and 'neutral-unstable.txt' in names)
        if trigger:
            steps[0]+=1;(folder/f'scan-go-{steps[0]}').touch();wait_for(folder/f'scan-ack-{steps[0]}')
        if mode=='rename' and 'neutral-rename.json' in names:rename_observed[0]=True
    if mode!='research':ledger.hook=hook
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
        snap=inventory(folder)
        entries={name:dict(bytes=item['bytes'],sha256=sha(folder/name)) for name,item in snap['files'].items() if name!='terminal.json'}
        current.write('closure.json',dict(files=entries,prestart_sha256=digest),'closure')
    value=supervise(terminal,[sys.executable,'-m','tools.s2uc_ura1_prepare_cr1','worker',str(folder),str(started),mode],ledger,
                    admitted=admit,report_writer=finish)
    # Saved terminal is the final authoritative supervisor record, also on abort.
    terminal.refresh();terminal.value['job']=win.snapshot()
    terminal.value['supervisor_accounting']=dict(calls=ledger.calls,seconds=ledger.check_seconds,max_seconds=ledger.max_check_seconds,handshakes=steps[0],rename_final_seen=rename_observed[0])
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
        if mode not in ('complete','load','rename','export','admin','temp','unstable','deadline'):
            raise ValueError('NEUTRAL_MODE')
        started=time.monotonic();install_job()
        folder=PREP/('integration-'+mode);folder.mkdir(exist_ok=False)
        if mode=='load':
            for i in range(104):(folder/f'neutral-metadata-{i:03d}.json').write_text('{}\n')
        launch(folder,started,mode)
    elif action=='worker':
        folder=Path(sys.argv[2]).resolve();mode=sys.argv[4]
        if (mode=='research' and folder!=TARGET) or (mode!='research' and (mode not in ('complete','load','rename','export','admin','temp','unstable','deadline') or folder!=PREP/('integration-'+mode))):
            raise PermissionError('WORKER_SCOPE')
        worker(folder,float(sys.argv[3]),mode)
    else:
        raise ValueError('ACTION')
