"""Terminal-only revision. No research entry point or authorization renewal.

The fixed terminal slot is allocated before worker admission and counted in
export and closure budgets. Updating it never calls the regular Ledger.
"""
import json
import os
from pathlib import Path
import subprocess
import time

from tools._s2uc_ura1_v2_series import Ledger, LIMITS, raw

SLOT = 16384
TIME_RESERVE = 5


class Terminal:
    def __init__(self, folder, started, prep=0, limits=None):
        self.folder = Path(folder)
        self.started = started
        self.limits = dict(LIMITS if limits is None else limits)
        self.path = self.folder / 'terminal.json'
        self.value = dict(status='ADMITTED', first_failure=None, followup_failures=[],
                          completed_cases=[], active_case=None, worker_ended=False,
                          cleanup='UNCONFIRMED', retry_allowed=False)
        if SLOT > self.limits['closure']:
            raise ValueError('TERMINAL_RESERVE_CLOSURE')
        if prep + sum(p.stat().st_size for p in self.folder.rglob('*') if p.is_file()) + SLOT > self.limits['export']:
            raise ValueError('TERMINAL_RESERVE_EXPORT')
        with self.path.open('xb') as f:
            f.write(b' ' * SLOT)
            f.flush()
            os.fsync(f.fileno())
        self.save()

    def fail(self, reason):
        reason = str(reason)[:512]
        if self.value['first_failure'] is None:
            self.value['first_failure'] = reason
        elif reason != self.value['first_failure'] and reason not in self.value['followup_failures'] and len(self.value['followup_failures']) < 8:
            self.value['followup_failures'].append(reason)

    def refresh(self):
        self.value = json.loads(self.path.read_bytes())

    @classmethod
    def attach(cls, folder, started, limits=None):
        self = cls.__new__(cls)
        self.folder = Path(folder)
        self.path = self.folder / 'terminal.json'
        self.started = started
        self.limits = dict(LIMITS if limits is None else limits)
        self.refresh()
        return self

    def begin(self, number):
        self.value['active_case'] = number
        self.value['cleanup'] = 'UNCONFIRMED'
        self.save()

    def completed(self, number, cleanup):
        if cleanup is not True:
            raise ValueError('CLEANUP_UNCONFIRMED')
        if number != len(self.value['completed_cases']) + 1 or number > 32:
            raise ValueError('CASE_ORDER')
        self.value['completed_cases'].append(number)
        self.value['active_case'] = None
        self.value['cleanup'] = 'CONFIRMED'
        self.save()

    def save(self):
        self.value['seconds'] = time.monotonic() - self.started
        data = raw(self.value)
        if len(data) > SLOT:
            raise ValueError('TERMINAL_SCHEMA_SIZE')
        # Fixed-size in-place update: no allocation, temporary file or Ledger.
        with self.path.open('r+b', buffering=0) as f:
            f.write(data + b' ' * (SLOT - len(data)))
            os.fsync(f.fileno())
        if json.loads(self.path.read_bytes()) != self.value:
            raise OSError('TERMINAL_READBACK')


class ReservedLedger(Ledger):
    """Preflight writes before consuming regular budgets; slot stays charged."""
    def __init__(self, terminal, prep=0):
        super().__init__(terminal.folder, terminal.started, prep, limits=terminal.limits)
        self.terminal = terminal
        self.entries[str(terminal.path.resolve())] = ('closure', SLOT)

    def check(self):
        for p in self.folder.iterdir():
            if p.is_file() and not p.name.endswith('.partial'):
                category = ('closure' if p.name in ('terminal.json','result.json','closure.json')
                            else 'source' if p.name.endswith('-source.json')
                            else 'archive' if p.name.endswith('.gz') else 'admin')
                self.entries[str(p.resolve())] = (category, p.stat().st_size)
        if self.clock() - self.started >= self.limits['total_seconds'] - TIME_RESERVE:
            raise TimeoutError('GLOBAL_CLOSING_RESERVE')
        super().check()

    def write(self, name, value, category='admin'):
        if name == 'worker.json':
            # Persist the worker's original cause before its regular report can fail.
            if value.get('first_failure'):
                self.terminal.fail(value['first_failure'])
            self.terminal.value['worker_report_status'] = value.get('status')
            self.terminal.save()
        self.check()
        size = len(raw(value))
        files = [p for p in self.folder.rglob('*') if p.is_file()]
        if self.prep_bytes + sum(p.stat().st_size for p in files) + size > self.limits['export']:
            raise ValueError('EXPORT_LIMIT')
        key = {'admin':'administration','closure':'closure','source':'source_total','archive':'archives'}[category]
        used = sum(p.stat().st_size for p in files if self.entries.get(str(p.resolve()), ('admin',0))[0] == category)
        if used + size > self.limits[key]:
            raise ValueError('CATEGORY_LIMIT:' + category)
        return super().write(name, value, category)


def supervise(terminal, command, ledger, *, worker_deadline=None, report_writer=None, admitted=None):
    """Bounded terminal supervisor, including missing/failed worker report.

No policy callbacks are supplied by this package. A future integration must
persist completed-case receipts only after archive verification AND cleanup.
"""
    child = None
    deadline = terminal.limits['worker_seconds'] if worker_deadline is None else worker_deadline
    try:
        ledger.check()
        child = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if admitted is not None:
            admitted(child)
        while child.poll() is None:
            if time.monotonic() - terminal.started >= deadline:
                raise TimeoutError('WORKER_DEADLINE')
            ledger.check()
            time.sleep(.01)
        if child.returncode:
            worker_failure = 'WORKER_EXIT:' + str(child.returncode)
            terminal.fail(worker_failure)
        if report_writer is not None:
            report_writer(ledger)
        else:
            terminal.fail('WORKER_REPORT_MISSING')
    except Exception as exc:
        pending_failure = type(exc).__name__ + ':' + str(exc)
    finally:
        try:
            if child is not None and child.poll() is None:
                child.kill()
                child.wait(timeout=2)
            terminal.value['worker_ended'] = child is None or child.poll() is not None
            terminal.value['worker_started'] = child is not None
            terminal.value['worker_exitcode'] = None if child is None else child.returncode
        except Exception as exc:
            terminal.fail('WORKER_END_UNCONFIRMED:' + str(exc))
        ended = {k:terminal.value[k] for k in ('worker_ended','worker_started','worker_exitcode') if k in terminal.value}
        prior = terminal.value['first_failure']
        followups = terminal.value['followup_failures'][:]
        terminal.refresh()
        terminal.value.update(ended)
        if prior:
            terminal.fail(prior)
        for failure in followups:
            terminal.fail(failure)
        if 'pending_failure' in locals():
            terminal.fail(pending_failure)
        if 'worker_failure' in locals():
            terminal.fail(worker_failure)
        # No cleanup assertion is inferred from process exit.
        partials = list(terminal.folder.glob('*.partial'))
        terminal.value['partial_files_before_cleanup'] = [p.name for p in partials][:32]
        if terminal.value['worker_ended']:
            for path in partials:
                try:
                    path.unlink()
                except OSError as exc:
                    terminal.fail('PARTIAL_CLEANUP:' + str(exc))
        terminal.value['partial_files'] = [p.name for p in terminal.folder.glob('*.partial')][:32]
        terminal.value['file_cleanup_confirmed'] = terminal.value['worker_ended'] and not terminal.value['partial_files']
        terminal.value['status'] = 'TECHNICAL_ABORT' if terminal.value['first_failure'] else 'TERMINAL_COMPLETE'
        terminal.save()
    return terminal.value


def execute_with_receipts(cases, run_case, ledger, expected):
    from tools._s2uc_ura1_v2_series import execute
    def checked(number, material, current_ledger):
        ledger.terminal.begin(number)
        result = run_case(number, material, current_ledger)
        if result['replicate'] != number:
            raise ValueError('SERIES_CLEANUP_OR_ID')
        ledger.terminal.completed(number, result.get('cleanup'))
        return result
    return execute(cases, checked, ledger, expected)


def worker_adapter(started):
    """Same bound worker body, with only ledger/terminal/progress replacement.

    Admission remains the original worker's responsibility. This function is
    deliberately not exposed as a research CLI or a renewed authorization.
    """
    from tools import s2uc_ura1_prepare_v2 as original
    terminal = Terminal.attach(original.TARGET, started)
    old_ledger, old_execute = original.Ledger, original.execute
    original.Ledger = lambda folder, start, prep: ReservedLedger(terminal, prep)
    original.execute = execute_with_receipts
    try:
        original.research_worker(started)
    except Exception as exc:
        terminal.fail(type(exc).__name__ + ':' + str(exc))
        terminal.save()
        raise
    finally:
        original.Ledger, original.execute = old_ledger, old_execute


def supervisor_adapter(folder, command, started, prep_bytes, *, worker_deadline=None):
    """Production terminal path; invoked only after separate bound admission.

    The caller must already have installed the unchanged two-process 512 MiB
    job. Verification precedes the worker gate. No admission/marker is created.
    """
    from tools import _s2uc_hx1_windows as win
    terminal = Terminal(folder, started, prep_bytes)
    ledger = ReservedLedger(terminal, prep_bytes)
    def admit(child):
        win.verify_worker(int(child._handle))
        ledger.write('gate', 'verified')
    def finish(current):
        terminal.refresh()
        report = current.folder / 'worker.json'
        if not report.exists():
            raise ValueError('WORKER_REPORT_MISSING')
        result = json.loads(report.read_bytes())
        if result.get('first_failure'):
            terminal.fail(result['first_failure'])
        current.final = True
        result.update(authorization_consumed=True, retry_allowed=False)
        current.write('result.json', result, 'closure')
        import hashlib
        files = {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in current.folder.iterdir() if p.is_file() and p != terminal.path}
        current.write('closure.json', dict(files=files), 'closure')
    return supervise(terminal, command, ledger, report_writer=finish, admitted=admit, worker_deadline=worker_deadline)
