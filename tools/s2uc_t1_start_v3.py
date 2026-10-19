"""Bound administrative T1 start; no changes to source, policy or assessment."""
import argparse
import io
import json
import multiprocessing
import sys
import time
import unittest
from pathlib import Path
from tools import s2uc_t1_prepare_v2 as p

ROOT = p.ROOT
PREFIX = 'S2UC_T1_START_V3_'
PLAN = ROOT / 'docs' / (PREFIX + 'PLAN_20261003.json')
BINDING = ROOT / 'docs' / (PREFIX + 'BINDUNG_20261003.json')
TEMPLATE = ROOT / 'docs' / (PREFIX + 'AUTORISIERUNG_VORLAGE_20261003.json')
GUIDE = ROOT / 'docs' / (PREFIX + 'AUFRUF_20261003.txt')
QUAL = ROOT / 'reports/s2uc/t1-start-v3-qualification-20261003-01'
OUT = ROOT / 'reports/s2uc/t1-transfer-20261003-02'
DOSSIERS = (ROOT / 'reports/s2uc/t1-preparation-assessment-20261003-01',
            ROOT / 'reports/s2uc/t1-transfer-assessment-20261003-01')
FILES = ('tools/s2uc_t1_start_v3.py', 'tests/test_s2uc_t1_start_v3.py')
LIMIT = 64 * 1048576
RESERVE = 1048576


def packed(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


def start_records(authorization, charged):
    accounting = dict(authorization=authorization, charged_previous_bytes=charged,
        export_limit=LIMIT, closure_reserve=RESERVE,
        accounting_scope='bound preparation, qualification, prior dossiers, authorization and reserved external report')
    raw = packed(accounting)
    import hashlib
    claim = dict(status='CLAIMED_ONCE', accounting_file='start-accounting.json',
                 accounting_sha256=hashlib.sha256(raw).hexdigest())
    return claim, accounting


def checked_write(folder, name, raw, cap, charged):
    if len(raw) > cap:
        raise RuntimeError('FILE_CAP:' + name)
    used = sum(x.stat().st_size for x in folder.iterdir() if x.is_file())
    if charged + used + len(raw) > LIMIT - RESERVE:
        raise RuntimeError('EXPORT_LIMIT')
    with (folder / name).open('xb') as stream:
        stream.write(raw)


def launch(folder, authorization, expected, charged, target, *, seconds=3600, closure_seconds=60):
    """The exact production start path, also used by neutral admin tests."""
    p.q.validate_authorization(authorization, expected)
    if not 0 < closure_seconds < seconds:
        raise ValueError('DEADLINE_SPLIT')
    claim, accounting = start_records(authorization, charged)
    # Validate the exact bytes subsequently written, before claiming any directory.
    claim_raw, accounting_raw = packed(claim), packed(accounting)
    if len(claim_raw) > 1024:
        raise RuntimeError('FILE_CAP:claim.json')
    if len(accounting_raw) > 524288:
        raise RuntimeError('FILE_CAP:start-accounting.json')
    if charged < 0 or charged + len(claim_raw) + len(accounting_raw) > LIMIT - RESERVE:
        raise RuntimeError('EXPORT_LIMIT')
    folder = Path(folder)
    begin = time.monotonic_ns()
    deadline = begin + int((seconds - closure_seconds) * 1e9)
    total = begin + int(seconds * 1e9)
    folder.mkdir(exist_ok=False)  # only this successful reservation authorizes writes
    proc = None
    error = None
    exitcode = None
    started = False
    try:
        checked_write(folder, 'start-accounting.json', accounting_raw, 524288, charged)
        checked_write(folder, 'claim.json', claim_raw, 1024, charged)
        checked_write(folder, 'start-time.json', packed(dict(start_ns=begin,
            worker_deadline_ns=deadline, total_deadline_ns=total, utc=p.q.old.utc())), 1024, charged)
        proc = multiprocessing.get_context('spawn').Process(target=target, args=(str(folder), charged, deadline))
        proc.start()
        started = True
        while proc.is_alive():
            remaining = (deadline - time.monotonic_ns()) / 1e9
            if remaining <= 0:
                break
            proc.join(remaining)
        if proc.is_alive():
            error = 'TIME_LIMIT'
            proc.terminate()
            proc.join(5)
            if proc.is_alive():
                proc.kill()
                proc.join()
        exitcode = proc.exitcode
        if exitcode != 0:
            error = error or 'WORKER_EXIT:' + str(exitcode)
        if not (folder / 'worker-complete.json').exists():
            error = error or 'MISSING_COMPLETION'
        if time.monotonic_ns() > deadline:
            error = error or 'TIME_LIMIT'
    except BaseException as exc:
        error = type(exc).__name__ + ':' + str(exc)
    finally:
        if proc is not None:
            if started and proc.is_alive():
                proc.terminate()
                proc.join(5)
                if proc.is_alive():
                    proc.kill()
                    proc.join()
            if started:
                exitcode = proc.exitcode
            proc.close()
        files = {x.name: dict(bytes=x.stat().st_size, sha256=p.q.old.sha(x))
                 for x in folder.iterdir() if x.is_file()}
        finish = time.monotonic_ns()
        terminal = packed(dict(status='COMPLETE' if error is None else 'FAILED', error=error,
            worker_started=started, worker_exitcode=exitcode, worker_alive=False,
            files=files, charged_previous_bytes=charged, elapsed_before_terminal_write=(finish-begin)/1e9,
            total_deadline_met=finish <= total, worker_deadline_ns=deadline, total_deadline_ns=total,
            resume_permitted=False, terminal_write_excluded_from_own_timestamp=True))
        # Independent bounded terminal path also works when ordinary start writes fail.
        if len(terminal) > 524288 or charged + sum(v['bytes'] for v in files.values()) + len(terminal) > LIMIT:
            raise RuntimeError('TERMINAL_EXPORT_LIMIT')
        with (folder / 'closure.json').open('xb') as stream:
            stream.write(terminal)
    if error:
        raise RuntimeError(error)
    if time.monotonic_ns() > total:
        raise RuntimeError('TOTAL_TIME_LIMIT')
    return dict(claim_bytes=len(claim_raw), accounting_bytes=len(accounting_raw))


def verify():
    p.preparation_check()
    binding = p.q.old.read(BINDING)
    if binding['python'] != sys.version or binding['executable_sha256'] != p.q.old.sha(sys.executable) or sys.flags.optimize:
        raise RuntimeError('RUNTIME_BINDING')
    for name, digest in binding['files'].items():
        if p.q.old.sha(ROOT / name) != digest:
            raise RuntimeError('START_BINDING:' + name)
    return binding


def authorization(status):
    return p.authorization(status) | dict(output=OUT.relative_to(ROOT).as_posix(),
        start_binding_sha256=p.q.old.sha(BINDING),
        start_qualification_sha256=p.q.old.sha(QUAL / 'closure.json'))


def worker(folder, charged, deadline):
    def check():
        if time.monotonic_ns() >= deadline:
            raise TimeoutError('WORKER_DEADLINE')
    check()
    verify()
    if Path(folder) != OUT:
        raise RuntimeError('UNKNOWN_DESTINATION')
    claim = p.q.old.read(Path(folder) / 'claim.json')
    accounting_path = Path(folder) / 'start-accounting.json'
    if claim['accounting_file'] != accounting_path.name or claim['accounting_sha256'] != p.q.old.sha(accounting_path):
        raise RuntimeError('ACCOUNTING_BINDING')
    accounting = p.q.old.read(accounting_path)
    if accounting['charged_previous_bytes'] != charged:
        raise RuntimeError('ACCOUNTING_CHARGE')
    p.q.validate_authorization(accounting['authorization'], authorization('AUTHORIZED_ONCE'))
    check()
    p.execute(folder, p.source.cases(), p.source.EVALUATION, charged, check, authorized=True, neutral=False)
    check()
    verify()
    check()


def run(path):
    binding = verify()
    qualification = p.q.old.read(QUAL / 'closure.json')
    if qualification['status'] != 'PASS':
        raise RuntimeError('START_QUALIFICATION_REQUIRED')
    for name, entry in qualification['files'].items():
        if p.q.old.sha(QUAL / name) != entry['sha256']:
            raise RuntimeError('START_QUALIFICATION_CHANGED')
    a = p.q.old.read(Path(path))
    p.q.validate_authorization(a, authorization('AUTHORIZED_ONCE'))
    b = p.q.old.read(p.BINDING)
    paths = {ROOT / n for n in b['code'] | b['references'] | binding['files']}
    paths.update((p.PLAN, p.BINDING, p.TEMPLATE, PLAN, BINDING, TEMPLATE, GUIDE, Path(path)))
    paths.update(x for x in p.QUAL.rglob('*') if x.is_file())
    paths.update(x for x in QUAL.rglob('*') if x.is_file())
    for dossier in DOSSIERS:
        paths.update(x for x in dossier.rglob('*') if x.is_file())
    actual = sum(x.stat().st_size for x in paths)
    if actual > 8 * 1048576:
        raise RuntimeError('PREPARATION_REFERENCE_CAP')
    return launch(OUT, a, authorization('AUTHORIZED_ONCE'), actual + 524288, worker)


def prepare():
    if BINDING.exists() or QUAL.exists() or OUT.exists():
        raise RuntimeError('PREPARATION_USED')
    p.preparation_check()
    p.q.old.save(PLAN, dict(output=OUT.relative_to(ROOT).as_posix(), claim_cap=1024,
        accounting_cap=524288, terminal_cap=524288, preparation_cap=8*1048576,
        external_report_reserve=524288, export_limit=LIMIT, closure_reserve=RESERVE,
        total_seconds=3600, worker_seconds=3540, closure_seconds=60,
        source_policy_assessment='UNCHANGED_T1_V2', status='PENDING_SEPARATE_AUTHORIZATION'))
    paths = [ROOT / n for n in FILES] + [PLAN, GUIDE, p.BINDING, p.QUAL/'closure.json']
    for dossier in DOSSIERS:
        paths.extend(x for x in dossier.rglob('*') if x.is_file())
    p.q.old.save(BINDING, dict(files={x.relative_to(ROOT).as_posix(): p.q.old.sha(x) for x in paths},
        python=sys.version, executable_sha256=p.q.old.sha(sys.executable)))


def qualify():
    verify()
    QUAL.mkdir(exist_ok=False)
    output = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromName('tests.test_s2uc_t1_start_v3')
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    p.q.old.save(QUAL/'tests.json', dict(count=result.testsRun, success=result.wasSuccessful(),
        failures=len(result.failures), errors=len(result.errors), skips=len(result.skipped), output=output.getvalue()))
    verify()
    p.q.old.save(QUAL/'closure.json', dict(status='PASS' if result.wasSuccessful() and not result.skipped else 'FAILED',
        files={x.relative_to(QUAL).as_posix(): dict(bytes=x.stat().st_size,sha256=p.q.old.sha(x))
               for x in QUAL.rglob('*') if x.is_file()}, policy_replays=0, t1_sources=0))
    if not result.wasSuccessful() or result.skipped:
        raise RuntimeError('NEUTRAL_START_QUALIFICATION_FAILED')
    p.q.old.save(TEMPLATE, authorization('PENDING_SEPARATE_AUTHORIZATION'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('prepare', 'qualify', 'run'))
    parser.add_argument('--authorization')
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare()
    elif args.action == 'qualify':
        qualify()
    elif not args.authorization:
        parser.error('--authorization required')
    else:
        run(args.authorization)
