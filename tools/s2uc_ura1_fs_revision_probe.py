"""Neutral concurrent-filesystem probes. No sources, arms or research CLI."""
import json
import os
from pathlib import Path
import sys
import time
from tools._s2uc_ura1_fs_accounting_v4 import Terminal, Ledger, inventory, supervise, LIMITS


def wait(path):
    end=time.monotonic()+5
    while not path.exists():
        if time.monotonic()>end:raise TimeoutError('NEUTRAL_HANDSHAKE:'+str(path))
        time.sleep(.002)


def worker(base,mode,started):
    from tools import _s2uc_hx1_windows as win
    win.worker_membership();data=base/'data';control=base/'control'
    if mode in ('rename','legacy','delete'):(data/'neutral.json.partial').write_bytes(b'x'*192)
    elif mode in ('permission','io','unstable'):(data/'neutral.txt').write_bytes(b'x')
    elif mode in ('export','admin','temp'):
        name='oversized.partial' if mode=='temp' else 'oversized.txt'
        size=LIMITS[dict(export='export',admin='administration',temp='temp')[mode]]+1
        with (data/name).open('xb') as f:f.truncate(size)
    (control/'ready').touch()
    step=1
    while not (control/'release').exists():
        if (control/f'go-{step}').exists():
            if mode in ('rename','legacy'):(data/'neutral.json.partial').rename(data/'neutral.json')
            elif mode=='delete':(data/'neutral.json.partial').unlink()
            elif mode=='create':(data/'created.json').write_bytes(b'x'*192)
            elif mode=='unstable':(data/'neutral.txt').write_bytes(b'x'*(step+1))
            (control/f'ack-{step}').touch();step+=1
        time.sleep(.002)
    t=Terminal.attach(data,started);l=Ledger(t)
    l.write('worker.json',dict(status='COMPLETE',neutral_files_only=True))


def probe(base,mode):
    from tools.s2uc_ura1_runtime_qualify import install_job
    from tools import _s2uc_hx1_windows as win
    base.mkdir(parents=True,exist_ok=False);data=base/'data';data.mkdir();control=base/'control';control.mkdir()
    started=time.monotonic();install_job();terminal=Terminal(data,started)
    state=dict(armed=False,fired=False,steps=0,accepted=None)
    def hook(attempt,parent,names):
        if not state['armed'] or parent!=data.resolve():return
        if mode in ('rename','legacy','delete','create','unstable') and (not state['fired'] or mode=='unstable'):
            state['fired']=True;state['steps']+=1
            (control/f"go-{state['steps']}").touch();wait(control/f"ack-{state['steps']}")
    def stat_fn(path):
        if state['armed'] and path.name=='neutral.txt' and mode in ('permission','io'):
            if mode=='permission':raise PermissionError(13,'NEUTRAL_PERMISSION_DENIED',str(path))
            raise OSError(5,'NEUTRAL_IO_ERROR',str(path))
        return path.stat(follow_symlinks=False)
    class ProbeLedger(Ledger):
        def check(self):
            if state['armed'] and mode=='legacy':
                files=[p for p in self.folder.rglob('*') if p.is_file()]
                hook(1,self.folder.resolve(),[p.name for p in files])
                # Same vulnerable list-then-stat operation as the historical path.
                sum(p.stat().st_size for p in files)
                raise AssertionError('LEGACY_FAILURE_NOT_REPRODUCED')
            result=super().check()
            if state['armed'] and state['accepted'] is None:
                state['accepted']=result
                (control/'release').touch()
            return result
    ledger=ProbeLedger(terminal,hook=hook,stat_fn=stat_fn);ledger.final=True
    def admitted(child):
        win.verify_worker(int(child._handle));wait(control/'ready');state['armed']=True
    def finish(current):
        current.write('result.json',dict(status='COMPLETE',neutral_files_only=True),'closure')
    value=supervise(terminal,[sys.executable,'-m',__spec__.name,'worker',mode,str(base),str(started)],ledger,admitted=admitted,report_writer=finish)
    persisted=json.loads((data/'terminal.json').read_bytes())
    assert persisted==value and value['worker_ended']
    expected_success=mode in ('rename','delete','create')
    assert (value['status']=='TERMINAL_COMPLETE')==expected_success
    if expected_success:
        snap=state['accepted'];name='created.json' if mode=='create' else 'neutral.json'
        assert (snap['files'].get(name,{}).get('bytes')==192) if mode!='delete' else name not in snap['files']
        assert snap['groups']['temp']==0
        if mode!='delete':assert snap['groups']['admin']==192
    else:
        assert 'first_diagnostic' in value and value['first_diagnostic']['traceback']
        key={'legacy':'FileNotFoundError','export':'budget:export','admin':'budget:admin','temp':'budget:temp','permission':'NEUTRAL_PERMISSION_DENIED','io':'NEUTRAL_IO_ERROR','unstable':'INVENTORY_UNSTABLE'}[mode]
        assert key in value['first_failure'],value
    if mode=='unstable':assert state['steps']==8
    # Oversized neutral final files are removed only AFTER persisted failure;
    # preserve size evidence separately, never alter the supervisor terminal.
    removed=[]
    for p in data.glob('oversized.txt'):
        removed.append(dict(name=p.name,bytes=p.stat().st_size));p.unlink()
    evidence=dict(mode=mode,status='PASS',terminal=value,accepted_inventory=state['accepted'],handshake_steps=state['steps'],job=win.snapshot(),neutral_post_probe_removals=removed)
    (base/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(dict(mode=mode,status='PASS',seconds=value['seconds'],job_peak=evidence['job']['peak_job_committed_bytes'],first_failure=value['first_failure'],steps=state['steps'])))


if __name__=='__main__':
    action,mode,folder=sys.argv[1:4];base=Path(folder).resolve()
    if action=='worker':worker(base,mode,float(sys.argv[4]))
    elif action=='probe':probe(base,mode)
    else:raise ValueError('ACTION')
