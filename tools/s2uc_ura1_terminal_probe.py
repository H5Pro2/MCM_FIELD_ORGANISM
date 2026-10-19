"""Short neutral terminal faults only; never imports sources or policies."""
import json
from pathlib import Path
import sys
import time
from tools._s2uc_ura1_terminal_v3 import Terminal, ReservedLedger, supervisor_adapter, LIMITS, SLOT


def worker(folder, started, mode):
    from tools import _s2uc_hx1_windows as win
    win.worker_membership()
    while not (folder/'gate').exists():
        time.sleep(.005)
    if mode == 'deadline':
        time.sleep(10)
        return
    t = Terminal.attach(folder, started)
    ledger = ReservedLedger(t)
    t.begin(1)
    t.completed(1, True)
    t.begin(2)
    t.fail('NEUTRAL_INITIAL_FAILURE')
    t.save()
    if mode == 'export':
        size = LIMITS['export'] - sum(p.stat().st_size for p in folder.iterdir())
        with (folder/'budget.partial').open('xb') as f:
            f.truncate(size)
    elif mode == 'admin':
        size = LIMITS['administration'] - (folder/'gate').stat().st_size
        with (folder/'budget.txt').open('xb') as f:
            f.truncate(size)
    try:
        ledger.write('worker.json', dict(status='TECHNICAL_ABORT',first_failure='NEUTRAL_INITIAL_FAILURE'))
    except Exception as exc:
        t.fail('WORKER_REPORT_FAILED:' + str(exc))
        t.save()
        raise


def main():
    action, mode, folder = sys.argv[1:4]
    folder = Path(folder).resolve()
    if action == 'worker':
        worker(folder, float(sys.argv[4]), mode)
        return
    from tools.s2uc_ura1_runtime_qualify import install_job
    from tools import _s2uc_hx1_windows as win
    folder.mkdir(exist_ok=False)
    started = time.monotonic()
    install_job()
    value = supervisor_adapter(folder, [sys.executable,'-m',__spec__.name,'worker',mode,str(folder),str(started)], started, 0,
                               worker_deadline=.3 if mode=='deadline' else 5)
    saved = json.loads((folder/'terminal.json').read_bytes())
    assert saved == value and value['worker_ended'] and value['file_cleanup_confirmed']
    assert value['status'] == 'TECHNICAL_ABORT'
    assert value['cleanup'] == 'UNCONFIRMED'
    if mode == 'deadline':
        assert 'WORKER_DEADLINE' in value['first_failure']
    else:
        assert value['first_failure'] == 'NEUTRAL_INITIAL_FAILURE'
        assert value['completed_cases'] == [1] and value['active_case'] == 2
        assert any('WORKER_REPORT_FAILED' in s for s in value['followup_failures'])
        assert not (folder/'worker.json').exists()
    assert sum(p.stat().st_size for p in folder.iterdir()) <= LIMITS['export']
    print(json.dumps(dict(mode=mode,status='PASS',terminal=value,job=win.snapshot())))


if __name__ == '__main__':
    main()
