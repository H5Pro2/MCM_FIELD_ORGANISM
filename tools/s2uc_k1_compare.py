"""Bound comparison preparation, neutral qualification, one-shot supervisor."""
import argparse
import io
import json
import multiprocessing
import os
import sys
import time
import traceback
import unittest
import uuid
import zipfile
import hashlib
from pathlib import Path
from tools import _s2uc_k1_compare_sources as source
from tools import _s2uc_k1_compare_engine as engine

ROOT=source.ROOT
PREFIX='S2UC_K1_VERGLEICH_V2_20261004'
PLAN=ROOT/'docs'/f'{PREFIX}_PLAN.json'
BINDING=ROOT/'docs'/f'{PREFIX}_CODEBINDUNG.json'
PRESTART=ROOT/'docs'/f'{PREFIX}_VORSTARTBINDUNG.json'
TEMPLATE=ROOT/'docs'/f'{PREFIX}_AUTORISIERUNG_VORLAGE.json'
QUAL=ROOT/'reports/s2uc/k1-comparison-neutral-20261004-02'
PACKED=ROOT/'reports/s2uc/k1-comparison-neutral-20261004-02.zip'
OUT=ROOT/'reports/s2uc/k1-comparison-20261004-01'
LIMIT=64*1048576
RESERVE=1048576
FILES=('tools/_s2uc_k1_compare_engine.py','tools/_s2uc_k1_compare_sources.py',
       'tools/s2uc_k1_compare.py','tests/test_s2uc_k1_compare.py')
VERDICTS={k:'NOT_EVALUABLE' for k in ('Technik','Mechanismus','Gesamtnutzen','Schaden')}


def raw(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def save(p,v):
    with Path(p).open('xb') as f:f.write(raw(v));f.flush();os.fsync(f.fileno())


class Ledger:
    def __init__(self,folder,charged=0,limit=LIMIT,reserve=RESERVE):
        self.folder=Path(folder);self.charged=charged;self.limit=limit;self.reserve=reserve
    def used(self):return sum(p.stat().st_size for p in self.folder.iterdir() if p.is_file())
    @staticmethod
    def category(name):
        if name.endswith('-source.json'):return 'source',160*1024
        if name.endswith(('-U.json','-K1.json')) and not name.startswith('active-'):return 'arm',512*1024
        if name.endswith('-assessment.json'):return 'case',1048576
        return 'admin',1048576
    def write(self,name,value):
        if Path(name).name!=name:raise ValueError('OUTPUT_NAME')
        data=raw(value)
        kind,cap=self.category(name)
        if len(data)>cap:raise ValueError('FILE_CAP:'+kind)
        if kind=='admin' and len(data)+sum(p.stat().st_size for p in self.folder.iterdir()
                if p.is_file() and self.category(p.name)[0]=='admin')>1048576:raise ValueError('ADMIN_CAP')
        if self.charged+self.used()+len(data)>self.limit-self.reserve:raise ValueError('EXPORT_LIMIT')
        with (self.folder/name).open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())


def prepare():
    if BINDING.exists() or PLAN.exists():raise ValueError('PREPARATION_EXISTS')
    p=source.plan();save(PLAN,p)
    anchor=ROOT/'docs/S2UC_K1_IMPLEMENTIERUNGSBINDUNG_20261003.json'
    old=source.read(anchor)
    files={n:h for n,h in old['files'].items() if n.endswith('.py')}
    for n,h in files.items():
        if source.sha(ROOT/n)!=h:raise ValueError('FROZEN_K1_CHANGED:'+n)
    for s in p['cases']:
        if s['source']['kind']=='SAVED_T1':
            for k in ('values','provenance'):
                n=s['source'][k+'_path'];h=s['source'][k+'_sha256']
                if source.sha(ROOT/n)!=h:raise ValueError('T1_SOURCE_HASH')
                files[n]=h
    extras=(*FILES,PLAN.relative_to(ROOT).as_posix(),anchor.relative_to(ROOT).as_posix(),
        'docs/S2UC_KANDIDATENERHALTUNG_K1_KONZEPTVERTRAG_20261003.md',
        'reports/s2uc/t1-transfer-20261003-02/manifest.json')
    files.update({n:source.sha(ROOT/n) for n in extras})
    save(BINDING,dict(files=files,python=sys.version,executable_sha256=source.sha(sys.executable),
        no_source_materialization=True,ancestor_scope='All frozen Python files plus K1 anchor digest; historical reports not runtime inputs'))


def verify_code():
    b=source.read(BINDING)
    if b['python']!=sys.version or sys.flags.optimize or b['executable_sha256']!=source.sha(sys.executable):raise ValueError('RUNTIME_BINDING')
    for n,h in b['files'].items():
        if source.sha(ROOT/n)!=h:raise ValueError('CODE_OR_INPUT_BINDING:'+n)
    if source.read(PLAN)!=source.plan():raise ValueError('PLAN_BINDING')
    return b


def verify_prestart():
    b=verify_code();p=source.read(PRESTART)
    for n,h in p['files'].items():
        if source.sha(ROOT/n)!=h:raise ValueError('PRESTART_BINDING:'+n)
    if source.read(QUAL/'closure.json')['status']!='PASS':raise ValueError('QUALIFICATION_FAILED')
    verify_archive()
    return b,p


def verify_archive():
    closure=source.read(QUAL/'closure.json')
    with zipfile.ZipFile(PACKED) as archive:
        if len(archive.namelist())!=len(set(archive.namelist())) or set(archive.namelist())!=set(closure['files']):raise ValueError('ARCHIVE_FILE_SET')
        if sum(i.file_size for i in archive.infolist())>16*1048576:raise ValueError('ARCHIVE_EXPANSION_LIMIT')
        for n,v in closure['files'].items():
            data=archive.read(n)
            if len(data)!=v['bytes'] or hashlib.sha256(data).hexdigest()!=v['sha256']:raise ValueError('ARCHIVE_HASH:'+n)


def expected_authorization():
    return dict(status='AUTHORIZED_ONCE',action='K1_24_CASE_MATERIALIZE_AND_COMPARE_ONCE',
        prestart_sha256=source.sha(PRESTART),output=OUT.relative_to(ROOT).as_posix(),
        cases=24,arms=['U','K1'],admissions=3584,reference_advances=3584,total_seconds=3600,
        export_bytes=LIMIT,known_development_only=True)


def charge(auth):
    b,p=verify_prestart()
    paths={ROOT/n for n in b['files']|p['files']}
    paths.update((BINDING,PLAN,PRESTART,TEMPLATE,Path(auth)))
    size=sum(x.stat().st_size for x in paths)
    if size>8*1048576:raise ValueError('PREPARATION_LIMIT')
    return size


def execute(folder,plan,charged,deadline,neutral=False,fault=None):
    ledger=Ledger(folder,charged)
    def check():
        if time.monotonic_ns()>=deadline:raise TimeoutError('WORKER_TIME_LIMIT')
    def step():check()
    try:
        if fault=='crash':os._exit(9)
        if fault=='hang':
            while True:time.sleep(.05)
        if fault=='worker_error':raise ValueError('INJECTED_WORKER_ERROR')
        if fault=='export':
            ledger.limit=2048;ledger.reserve=1024
            ledger.write('export-fault.json',dict(data='x'*2048))
        entries=[];reports=[];begin=time.monotonic()
        for spec in plan['cases']:
            check();bundle=source.materialize(spec,authorized=not neutral,neutral=neutral)
            filename=spec['id']+'-source.json';ledger.write(filename,source.record(bundle))
            entries.append(dict(id=spec['id'],file=filename,sha256=source.sha(Path(folder)/filename)))
        ledger.write('manifest.json',dict(entries=entries,all_sources_before_policy=True,neutral_only=neutral))
        for spec,e in zip(plan['cases'],entries,strict=True):
            check();path=Path(folder)/e['file']
            if source.sha(path)!=e['sha256']:raise ValueError('MATERIALIZED_SOURCE_CHANGED')
            bundle=source.restore_record(source.read(path));arms={}
            for name in ('U','K1'):
                check();ledger.write('active-'+spec['id']+'-'+name+'.json',dict(case=spec['id'],arm=name))
                arms[name]=engine.replay(bundle['values'],source.digest(bundle['values']),name=='K1',step)
                ledger.write(spec['id']+'-'+name+'.json',arms[name])
            report=engine.assess_case(arms,bundle,spec);reports.append(report)
            ledger.write(spec['id']+'-assessment.json',report)
        result=engine.aggregate(reports,plan['cases'])
        check();ledger.write('assessment.json',result|dict(neutral_only=neutral))
        ledger.write('worker-complete.json',dict(status='COMPLETE',cases=len(reports),arms=2*len(reports),
            admissions=sum(s['frames']*2 for s in plan['cases']),reference_advances=sum(s['frames']*2 for s in plan['cases']),
            targets=sum(len(s['masks']['G']) for s in plan['cases']),engine_seconds=time.monotonic()-begin,neutral_only=neutral))
    except BaseException as exc:
        try:ledger.write('worker-error.json',dict(error=type(exc).__name__+':'+str(exc),verdicts=VERDICTS))
        except BaseException:pass
        raise


def supervise(folder,validator,*,neutral=False,seconds=3600,reserve_seconds=60,fault=None):
    """Reserve evidence before validation; every ordinary pre-worker error is sealed."""
    begin=time.monotonic_ns();folder=Path(folder)
    # Never overwrite an existing attempt. Record collision separately.
    if folder.exists():
        rejected=folder.with_name(folder.name+'-rejected-'+uuid.uuid4().hex)
        rejected.mkdir(parents=True)
        save(rejected/'closure.json',dict(status='REJECTED_EXISTING_OUTPUT',worker_started=False,
            error='OUTPUT_EXISTS',requested=str(folder),verdicts=VERDICTS,resume_permitted=False))
        return source.read(rejected/'closure.json')
    folder.mkdir(parents=True)
    proc=None;started=False;error=None;charged=0
    deadline=begin+int((seconds-reserve_seconds)*1e9);total=begin+int(seconds*1e9)
    try:
        save(folder/'attempt.json',dict(neutral_only=neutral,begin_ns=begin,worker_deadline_ns=deadline,total_deadline_ns=total))
        if not 0<reserve_seconds<seconds:raise ValueError('TIME_SPLIT')
        plan,charged=validator()
        if charged>8*1048576:raise ValueError('PREPARATION_LIMIT')
        Ledger(folder,charged).write('start.json',dict(plan_sha256=source.digest(plan),charged=charged,neutral_only=neutral))
        if time.monotonic_ns()>=deadline:raise TimeoutError('PRESTART_TIME_LIMIT')
        if fault=='start_error':raise OSError('INJECTED_PROCESS_START_ERROR')
        proc=multiprocessing.get_context('spawn').Process(target=execute,args=(str(folder),plan,charged,deadline,neutral,fault))
        proc.start();started=True
        if fault=='cancel':raise KeyboardInterrupt('NEUTRAL_RUNNING_CANCEL')
        while proc.is_alive():
            left=(deadline-time.monotonic_ns())/1e9
            if left<=0:raise TimeoutError('SUPERVISOR_TIME_LIMIT')
            proc.join(min(left,.25))
        if proc.exitcode!=0:raise RuntimeError('WORKER_EXIT:'+str(proc.exitcode))
        if not (folder/'worker-complete.json').exists():raise ValueError('MISSING_COMPLETION')
        if time.monotonic_ns()>deadline:raise TimeoutError('WORKER_DEADLINE')
    except BaseException as exc:
        error=type(exc).__name__+':'+str(exc)
    finally:
        if proc is not None and started and proc.is_alive():
            proc.terminate();proc.join(min(2,max(0,(total-time.monotonic_ns())/1e9)))
            if proc.is_alive():proc.kill();proc.join(min(2,max(0,(total-time.monotonic_ns())/1e9)))
        alive=bool(proc is not None and started and proc.is_alive())
        if alive:error=error or 'WORKER_STILL_ALIVE'
        files={p.name:dict(bytes=p.stat().st_size,sha256=source.sha(p)) for p in folder.iterdir() if p.is_file()}
        elapsed=(time.monotonic_ns()-begin)/1e9
        if elapsed>seconds:error=error or 'TOTAL_DEADLINE'
        result=dict(status='COMPLETE' if error is None else 'NOT_EVALUABLE',error=error,
            worker_started=started,worker_alive=alive,worker_exitcode=None if not started else proc.exitcode,
            charged_previous_bytes=charged,files=files,elapsed_before_terminal_write=elapsed,
            total_seconds=seconds,total_deadline_met=elapsed<=seconds,resume_permitted=False,neutral_only=neutral)
        if error:result['verdicts']=VERDICTS
        data=raw(result)
        if len(data)>RESERVE or charged+sum(v['bytes'] for v in files.values())+len(data)>LIMIT:
            # Compact terminal still records export failure; never silently omit closure.
            result=dict(status='NOT_EVALUABLE',error='CLOSURE_EXPORT_LIMIT',worker_started=started,
                worker_alive=alive,verdicts=VERDICTS,resume_permitted=False)
        save(folder/'closure.json',result)
    return result


def run(auth):
    def validate():
        verify_prestart()
        if source.read(auth)!=expected_authorization():raise PermissionError('EXACT_AUTHORIZATION_REQUIRED')
        return source.read(PLAN),charge(auth)
    return supervise(OUT,validate)


def qualify():
    verify_code();QUAL.mkdir(exist_ok=False)
    from tests import test_s2uc_k1_compare as test
    test.OUTPUT=QUAL
    stream=io.StringIO();start=time.monotonic()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test))
    save(QUAL/'tests.json',dict(success=result.wasSuccessful(),count=result.testsRun,failures=len(result.failures),errors=len(result.errors),output=stream.getvalue()))
    files={p.relative_to(QUAL).as_posix():dict(sha256=source.sha(p),bytes=p.stat().st_size) for p in QUAL.rglob('*') if p.is_file()}
    save(QUAL/'closure.json',dict(status='PASS' if result.wasSuccessful() else 'FAILED',files=files,
        seconds=time.monotonic()-start,research_replays=0,F_materializations=0,code_binding_sha256=source.sha(BINDING)))
    print(stream.getvalue())
    if not result.wasSuccessful():raise RuntimeError('QUALIFICATION_FAILED')


def seal():
    b=verify_code();closure=source.read(QUAL/'closure.json')
    if closure['status']!='PASS':raise ValueError('QUALIFICATION_REQUIRED')
    for n,v in closure['files'].items():
        if source.sha(QUAL/n)!=v['sha256']:raise ValueError('QUALIFICATION_CHANGED')
    # Original uncompressed evidence stays immutable. The start consumes this
    # lossless, hash-checked copy, not both copies of the historical evidence.
    with zipfile.ZipFile(PACKED,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for n in sorted(closure['files']):archive.write(QUAL/n,n)
    verify_archive()
    files={p.relative_to(ROOT).as_posix():source.sha(p) for p in (PACKED,QUAL/'closure.json',QUAL/'tests.json')}
    files[BINDING.relative_to(ROOT).as_posix()]=source.sha(BINDING)
    size=sum((ROOT/n).stat().st_size for n in set(b['files'])|set(files))
    if size+65536>8*1048576:raise ValueError('PREPARATION_LIMIT')
    save(PRESTART,dict(files=files,input_bytes_before_self_and_authorization=size,
        remaining_preparation_bytes=8*1048576-size,comparison_executed=False,status='NEUTRAL_QUALIFIED_PENDING_AUTHORIZATION'))
    save(TEMPLATE,expected_authorization()|dict(status='PENDING_SEPARATE_AUTHORIZATION'))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','qualify','seal','check','run']);parser.add_argument('--authorization',type=Path)
    args=parser.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='qualify':qualify()
    elif args.action=='seal':seal()
    elif args.action=='check':verify_prestart();print('PASS_PRESTART_BINDING_NO_REPLAY')
    else:
        # Missing/unreadable authorization is processed inside the recorded attempt.
        result=run(args.authorization);print(json.dumps(result));sys.exit(0 if result['status']=='COMPLETE' else 1)


if __name__=='__main__':main()
