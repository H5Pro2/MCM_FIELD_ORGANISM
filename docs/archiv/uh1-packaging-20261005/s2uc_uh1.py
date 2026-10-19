"""UH1 bounded preparation, qualification and separately authorized one-shot replay."""
import argparse,gzip,hashlib,io,json,multiprocessing,os,sys,time,unittest,uuid,zipfile
from pathlib import Path
from tools import _s2uc_uh1_sources as source
from tools import _s2uc_uh1_engine as engine
from tools import _s2uc_uh1_stats as stats
from tools import _s2uc_hx1_windows as windows
from tools import s2uc_hx1 as hx
ROOT=source.ROOT
PREFIX='S2UC_UH1_V1_20261005'
BINDING=ROOT/'docs'/f'{PREFIX}_CODEBINDUNG.json'
PRESTART=ROOT/'docs'/f'{PREFIX}_VORSTARTBINDUNG.json'
TEMPLATE=ROOT/'docs'/f'{PREFIX}_AUTORISIERUNG_VORLAGE.json'
MATRIX=ROOT/'docs'/f'{PREFIX}_BOOTSTRAP.bin'
QUAL=ROOT/'reports/s2uc/uh1-neutral-20261005-01'
PACKED=ROOT/'reports/s2uc/uh1-neutral-20261005-01.zip'
OUT=ROOT/'reports/s2uc/uh1-comparison-20261004-01'
LIMIT=64*1048576;RESERVE=1048576
VERDICTS={'Technik':'NOT_EVALUABLE','Leistung':'NOT_EVALUABLE'}
raw=hx.raw;save=hx.save;Ledger=hx.Ledger
FILES=('tools/_s2uc_uh1_h.py','tools/_s2uc_uh1_reference.py','tools/_s2uc_uh1_sources.py',
 'tools/_s2uc_uh1_engine.py','tools/_s2uc_uh1_stats.py','tools/s2uc_uh1.py','tests/test_s2uc_uh1.py')

def prepare():
    if BINDING.exists() or MATRIX.exists():raise ValueError('PREPARATION_EXISTS')
    old=source.read(ROOT/'docs/S2UC_HX1_V1_20261004_CODEBINDUNG.json')
    for n,h in old['files'].items():
        if source.sha(ROOT/n)!=h:raise ValueError('UNCHANGED_HX1:'+n)
    specification=source.read(ROOT/'docs/S2UC_UH1_SPEZIFIKATIONSBINDUNG_20261004.json')
    for n,v in specification['files'].items():
        if source.sha(ROOT/n)!=v['sha256']:raise ValueError('SPECIFICATION_BINDING')
    source.validate_all();data=stats.matrix_bytes();stats.verify_matrix(data)
    with MATRIX.open('xb') as f:f.write(data)
    files=dict(old['files'])
    extra=(*FILES,'docs/S2UC_UH1_PRUEFVERTRAG_20261004.md','docs/S2UC_UH1_QUELLENBINDUNG_20261004.json',
        'docs/S2UC_UH1_SPEZIFIKATIONSBINDUNG_20261004.json',MATRIX.relative_to(ROOT).as_posix())
    files.update({n:source.sha(ROOT/n) for n in extra})
    save(BINDING,dict(files=files,runtime=hx.runtime(),research_replays=0,profile=source.PROFILE))

def verify_code():
    b=source.read(BINDING)
    if b['runtime']!=hx.runtime() or sys.flags.optimize:raise ValueError('RUNTIME_BINDING')
    for n,h in b['files'].items():
        if source.sha(ROOT/n)!=h:raise ValueError('CODE_BINDING:'+n)
    stats.verify_matrix(MATRIX.read_bytes());source.validate_all();return b

def execute(folder,plan,charged,deadline,neutral=False,fault=None):
    if fault is not None:
        if not neutral:raise PermissionError('FAULT_NEUTRAL_ONLY')
        return hx.execute(folder,dict(cases=[]),charged,deadline,True,fault)
    ledger=Ledger(folder,charged);context={'phase':'start'}
    def check():
        if time.monotonic_ns()>=deadline:raise TimeoutError('WORKER_TIME_LIMIT')
    try:
        windows.worker_membership();begin=time.monotonic();reports=[]
        if not neutral:source.validate_all()
        else:
            for spec in plan['cases']:
                check();ledger.write(spec['id']+'-source.json',source.load(spec,neutral=True))
        ledger.write('manifest.json',dict(neutral_only=neutral,known_sources=not neutral,
            source_binding_sha256=source.sha(source.BINDING),all_sources_before_policy=True,
            cases=plan['cases'],input_mode='neutral fixed pattern' if neutral else 'read-only archived bytes'))
        for number,spec in enumerate(plan['cases'],1):
            check();context={'phase':'load','case':spec['id']}
            record=source.read(Path(folder)/(spec['id']+'-source.json')) if neutral else source.load(spec,authorized=True)
            context={'phase':'replay','case':spec['id']}
            result=engine.replay(record,check);result.update(spec)
            ledger.packed(spec['id']+'-case.json.gz',result)
            reports.append({k:result[k] for k in ('replicate','condition','rows','complete')})
            if number%8==0:print('UH1_NEUTRAL' if neutral else 'UH1_RESEARCH',number,'/64',flush=True)
        context={'phase':'assessment'};assessment=stats.aggregate(reports,MATRIX.read_bytes(),check)
        if neutral:
            assessment['verdict']='NEUTRAL_TECHNICAL_ONLY';assessment['primary']['verdict']='NEUTRAL_TECHNICAL_ONLY'
        ledger.write('assessment.json',assessment|dict(neutral_only=neutral,known_sources=not neutral))
        ledger.write('worker-complete.json',dict(status='COMPLETE',cases=64,arms=128,source_frames=65536,
            arm_frames=131072,reference_advances=131072,targets_per_arm=32704,Q_targets_per_arm=16384,
            engine_seconds=time.monotonic()-begin,neutral_only=neutral))
    except BaseException as exc:
        try:ledger.write('worker-error.json',dict(error=type(exc).__name__+':'+str(exc),context=context,verdicts=VERDICTS))
        except BaseException:pass
        raise

def supervise(folder,validator,*,neutral=False,seconds=3600,reserve_seconds=60,fault=None):
    """Reserve evidence before validation; every ordinary pre-worker error is sealed."""
    windows.install(fresh=True)
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
        if charged>10*1048576:raise ValueError('PREPARATION_PLUS_SOURCE_LIMIT')
        Ledger(folder,charged).write('start.json',dict(plan_sha256=source.digest(plan),charged=charged,neutral_only=neutral))
        if time.monotonic_ns()>=deadline:raise TimeoutError('PRESTART_TIME_LIMIT')
        if fault=='start_error':raise OSError('INJECTED_PROCESS_START_ERROR')
        proc=multiprocessing.get_context('spawn').Process(target=execute,args=(str(folder),plan,charged,deadline,neutral,fault))
        proc.start();started=True
        windows.verify_worker(proc.sentinel)
        if fault=='cancel':raise KeyboardInterrupt('NEUTRAL_RUNNING_CANCEL')
        while proc.is_alive():
            windows.snapshot()
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
        memory=windows.snapshot()
        if memory['peak_job_committed_bytes']>windows.LIMIT:error=error or 'JOB_PEAK_LIMIT'
        files={p.name:dict(bytes=p.stat().st_size,sha256=source.sha(p)) for p in folder.iterdir() if p.is_file()}
        elapsed=(time.monotonic_ns()-begin)/1e9
        if elapsed>seconds:error=error or 'TOTAL_DEADLINE'
        result=dict(status='COMPLETE' if error is None else 'NOT_EVALUABLE',error=error,
            worker_started=started,worker_alive=alive,worker_exitcode=None if not started else proc.exitcode,
            charged_previous_bytes=charged,files=files,process_memory=memory,elapsed_before_terminal_write=elapsed,
            total_seconds=seconds,total_deadline_met=elapsed<=seconds,resume_permitted=False,neutral_only=neutral)
        if error:result['verdicts']=VERDICTS
        data=raw(result)
        if len(data)>RESERVE or charged+sum(v['bytes'] for v in files.values())+len(data)>LIMIT:
            # Compact terminal still records export failure; never silently omit closure.
            result=dict(status='NOT_EVALUABLE',error='CLOSURE_EXPORT_LIMIT',worker_started=started,
                worker_alive=alive,verdicts=VERDICTS,resume_permitted=False)
        save(folder/'closure.json',result)
    return result


def verify_full(folder):
    c=source.read(folder/'closure.json')
    if c['status']!='COMPLETE':raise ValueError('FULL_NOT_COMPLETE')
    maxima={a:{} for a in ('U','H')};expanded=packed=0;references=0;trace_frames=0
    for n,v in c['files'].items():
        if source.sha(folder/n)!=v['sha256'] or (folder/n).stat().st_size!=v['bytes']:raise ValueError('CLOSURE_HASH')
    for spec in source.plan()['cases']:
        p=folder/(spec['id']+'-case.json.gz');data=gzip.decompress(p.read_bytes());r=json.loads(data)
        if not r['complete'] or not r['cleanup'] or not r['neutral_only'] or len(r['rows'])!=511:raise ValueError('FULL_CASE')
        if r['reference_advances']!={'U':1024,'H':1024}:raise ValueError('REFERENCE_COUNT')
        # Decoder is deliberately a separate loop from the writer.
        import zlib
        state=bytearray(3520)
        for expected,(i,payload) in enumerate(r['H_trace'],1):
            if i!=expected:raise ValueError('H_TRACE_INDEX')
            delta=zlib.decompress(bytes.fromhex(payload))
            if len(delta)!=len(state):raise ValueError('H_TRACE_SIZE')
            for j in range(len(state)):state[j]^=delta[j]
            if int.from_bytes(state[2336:2344],'little')!=i:raise ValueError('H_TRACE_STATE')
            trace_frames+=1
        if len(r['H_trace'])!=1024:raise ValueError('H_TRACE_COUNT')
        references+=sum(r['reference_advances'].values());expanded=max(expanded,len(data));packed=max(packed,p.stat().st_size)
        for a,res in r['resources'].items():
            for key,value in res.items():
                if isinstance(value,(int,float)):maxima[a][key]=max(maxima[a].get(key,0),value)
    return dict(maxima=maxima,expanded_max=expanded,packed_max=packed,reference_advances=references,
        H_decoded_frames=trace_frames,files_verified=len(c['files']),process_memory=c['process_memory'],
        counts=source.read(folder/'worker-complete.json'),neutral_export_bytes=sum(p.stat().st_size for p in folder.iterdir()))

def qualify():
    verify_code();QUAL.mkdir(exist_ok=False)
    from tests import test_s2uc_uh1 as test
    test.OUTPUT=QUAL
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test))
    save(QUAL/'tests.json',dict(success=result.wasSuccessful(),count=result.testsRun,output=stream.getvalue()))
    print(stream.getvalue(),flush=True)
    ok=result.wasSuccessful()
    if ok:
        full=supervise(QUAL/'integration',lambda:(source.plan(),8*1048576),neutral=True)
        ok=full['status']=='COMPLETE'
        if ok:
            try:save(QUAL/'full-size-facts.json',verify_full(QUAL/'integration'))
            except BaseException as exc:ok=False;save(QUAL/'verification-error.json',dict(error=repr(exc)))
    files={p.relative_to(QUAL).as_posix():dict(bytes=p.stat().st_size,sha256=source.sha(p)) for p in QUAL.rglob('*') if p.is_file()}
    save(QUAL/'closure.json',dict(status='PASS' if ok else 'FAILED',files=files,code_binding_sha256=source.sha(BINDING),research_replays=0))
    if not ok:raise RuntimeError('QUALIFICATION_FAILED')

def expected_authorization():
    return dict(action='UH1_32_KNOWN_PAIRS_UH_ONCE',status='AUTHORIZED_ONCE',prestart_sha256=source.sha(PRESTART),
        source_binding_sha256=source.sha(source.BINDING),output=OUT.relative_to(ROOT).as_posix(),arms=['U','H'],cases=64,
        frames_per_case=1024,Q_targets_per_case=256,primary_pairs=32,total_seconds=3600,process_bytes=536870912,export_bytes=LIMIT)

def verify_archive():
    c=source.read(QUAL/'closure.json')
    with zipfile.ZipFile(PACKED) as z:
        if set(z.namelist())!=set(c['files']) or len(z.namelist())!=len(c['files']):raise ValueError('ARCHIVE_SET')
        if sum(i.file_size for i in z.infolist())>272*1048576:raise ValueError('ARCHIVE_EXPANSION')
        for n,v in c['files'].items():
            data=z.read(n)
            if n.endswith('-case.json.gz'):data=gzip.compress(data,compresslevel=9,mtime=0)
            if len(data)!=v['bytes'] or hashlib.sha256(data).hexdigest()!=v['sha256']:raise ValueError('ARCHIVE_HASH')

def verify_prestart():
    b=verify_code();p=source.read(PRESTART)
    for n,h in p['files'].items():
        if source.sha(ROOT/n)!=h:raise ValueError('PRESTART_BINDING')
    if source.read(QUAL/'closure.json')['status']!='PASS':raise ValueError('QUALIFICATION')
    verify_archive();return b,p

def preparation_bytes(auth_bytes):
    b=source.read(BINDING);p=source.read(PRESTART)
    names=set(b['files'])|set(p['files'])|{BINDING.relative_to(ROOT).as_posix(),PRESTART.relative_to(ROOT).as_posix(),TEMPLATE.relative_to(ROOT).as_posix()}
    total=sum((ROOT/n).stat().st_size for n in names)+auth_bytes
    if total>8*1048576:raise ValueError('PREPARATION_LIMIT')
    return total

def seal():
    verify_code();c=source.read(QUAL/'closure.json')
    if c['status']!='PASS':raise ValueError('QUALIFICATION')
    with zipfile.ZipFile(PACKED,'x',compression=zipfile.ZIP_LZMA) as z:
        for n,v in c['files'].items():
            p=QUAL/n
            if source.sha(p)!=v['sha256']:raise ValueError('QUAL_CHANGED')
            data=p.read_bytes()
            if n.endswith('-case.json.gz'):data=gzip.decompress(data)
            z.writestr(n,data)
    verify_archive()
    save(PRESTART,dict(status='NEUTRAL_QUALIFIED_PENDING_AUTHORIZATION',files={p.relative_to(ROOT).as_posix():source.sha(p) for p in (BINDING,PACKED,QUAL/'closure.json',QUAL/'tests.json',source.BINDING)}))
    save(TEMPLATE,expected_authorization()|dict(status='PENDING_SEPARATE_AUTHORIZATION'))
    print('PREPARATION_BYTES',preparation_bytes(len(raw(expected_authorization()))))

def run(auth):
    def validate():
        verify_prestart()
        if source.read(auth)!=expected_authorization():raise PermissionError('EXACT_AUTHORIZATION_REQUIRED')
        prep=preparation_bytes(Path(auth).stat().st_size)
        return source.plan(),prep+source.read(source.BINDING)['total_source_bytes']
    return supervise(OUT,validate)

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','qualify','seal','check','run']);p.add_argument('--authorization',type=Path);a=p.parse_args()
    if a.action=='prepare':prepare()
    elif a.action=='qualify':qualify()
    elif a.action=='seal':seal()
    elif a.action=='check':verify_prestart();print('PASS_UH1_PRESTART_NO_RESEARCH')
    else:
        r=run(a.authorization);print(json.dumps(r));sys.exit(0 if r['status']=='COMPLETE' else 1)
if __name__=='__main__':main()
