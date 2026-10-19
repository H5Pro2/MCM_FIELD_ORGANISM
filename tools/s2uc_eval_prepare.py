"""32-case preparation and separately authorized one-shot evaluation."""
import argparse
import io
import json
import multiprocessing
import sys
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tools import s2uc_xyx_prepare as old
from tools import _s2uc_eval_source as source
from tools._s2uc_eval_multi_replay import replay as multi_replay
from tools._s2uc_eval_baseline_replay import replay as baseline_replay
from tools._s2uc_eval_assessment import assess_case, aggregate, ARMS
from tools._s2uc_ema_stock_observer import digest
from tools._s2uc_bounded_audio import OutputLedger

ROOT = old.ROOT
PREFIX = 'S2UC_RASTER32_V2_'
PLAN = ROOT/'docs'/f'{PREFIX}PLAN_20261003.json'
BINDING = ROOT/'docs'/f'{PREFIX}BINDUNG_20261003.json'
INDEX = ROOT/'docs'/f'{PREFIX}ENTWICKLUNGSINDEX_20261003.json'
TEMPLATE = ROOT/'docs'/f'{PREFIX}AUTORISIERUNG_VORLAGE_20261003.json'
AUTH = ROOT/'docs'/f'{PREFIX}AUTORISIERUNG_20261003.json'
CONTRACT = ROOT/'docs/S2UC_EINGEFRORENE_POLICY_EVALUATIONSVERTRAG_20261003.txt'
QUAL = ROOT/'reports/s2uc/raster32-preparation-qualification-20261003-02'
OUT = ROOT/'reports/s2uc/raster32-evaluation-20261003-01'
GUIDE = ROOT/'docs/S2UC_RASTER32_RESSOURCEN_UND_VORBEREITETER_AUFRUF_20261003.txt'
PREVIOUS_PREP = ROOT/'reports/s2uc/raster32-preparation-qualification-20261003-01'
PREVIOUS_DOCS = tuple(ROOT/'docs'/f'S2UC_RASTER32_{name}_20261003.json' for name in
    ('PLAN','BINDUNG','ENTWICKLUNGSINDEX','AUTORISIERUNG_VORLAGE'))
NEW = ('tools/_s2uc_eval_source.py', 'tools/_s2uc_eval_multi_replay.py',
       'tools/_s2uc_eval_baseline_replay.py', 'tools/_s2uc_eval_evidence.py',
       'tools/_s2uc_eval_assessment.py', 'tools/s2uc_eval_prepare.py',
       'tests/test_s2uc_eval_prepare.py')
LIMIT = 64*1048576
RESERVE = 1048576
SECONDS = 3600
MAX_CHARGED = 8*1048576
sha, read, save = old.prior.sha, old.prior.read, old.prior.save


def utc():
    return datetime.now(timezone.utc).isoformat()


def plan():
    return dict(status='BOUND_NOT_AUTHORIZED', cases=source.cases(), recipes=source.RECIPES,
        arms=list(ARMS), source_positions=2048, experimental_admissions=10240,
        reference_advances=10240, max_case_frames=80, export_limit=LIMIT,
        closure_reserve=RESERVE, execution_seconds=SECONDS,
        preparation_and_reference_cap=MAX_CHARGED,
        file_caps=dict(source=65536,arm=196608,case_assessment=524288,resources=32768,start=1024,other=524288),
        policy_limits=old.plan()['limits'] | {'export':LIMIT, 'reserve':RESERVE},
        criteria=dict(adaptation_total=39, denominator=48, per_duration=18,
            duration_denominator=24, deadline_ordinal=3, damage='1/32',
            primary='equal_case_mae', H='strict_each_baseline', G='strict_each_baseline',
            warm_stable='no_worse_each_baseline'),
        output=OUT.relative_to(ROOT).as_posix(), independent_generalization='NICHT_GEPRUEFT')


def development_index():
    """Saved top-level S2UC source exports only; no adapter/source generation."""
    found = []
    for p in sorted((ROOT/'reports/s2uc').glob('*/*source*.json')):
        if 'raster32-' in p.parent.name:
            continue
        raw = read(p)
        value = raw.get('values') if isinstance(raw,dict) else raw
        if not isinstance(value, list) or not value or not all(
            isinstance(v, list) and len(v)==48 and all(type(x) in (float,int) for x in v) for v in value):
            continue
        found.append(dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p), bytes=p.stat().st_size,
            length=len(value), profile=digest(value),
            blocks=sorted({digest(value[i:i+4]) for i in range(0,len(value)-3,4)}),
            prefixes={str(n):digest(value[:n]) for n in range(4,min(len(value),80)+1,4)}))
    return dict(scope='All top-level reports/s2uc/*/*source*.json numeric48 exports at preparation; not all historical modalities or nested fixtures',
        known_building_blocks=True, entries=found)


def prior_bytes():
    c=read(PREVIOUS_PREP/'closure.json')
    if c['status']!='PASS': raise RuntimeError('PREVIOUS_PREPARATION_RECORD')
    for n,v in c['files'].items():
        if sha(PREVIOUS_PREP/n)!=v['sha256'] or (PREVIOUS_PREP/n).stat().st_size!=v['bytes']:
            raise RuntimeError('PREVIOUS_PREPARATION_TAMPER')
    return (old.prior.check_qualification()+old.check_preparation()+
        sum(p.stat().st_size for p in PREVIOUS_PREP.iterdir() if p.is_file())+
        sum(p.stat().st_size for p in PREVIOUS_DOCS))


def code_hashes():
    return dict(old.verify()['code'], **{n:sha(ROOT/n) for n in NEW})


def authorization(status):
    return dict(status=status, action='MATERIALIZE_AND_RUN_RASTER32_ONCE',
        binding_sha256=sha(BINDING), plan_sha256=sha(PLAN),
        preparation_closure_sha256=sha(QUAL/'closure.json') if (QUAL/'closure.json').exists() else None,
        output=plan()['output'], cases=32, positions=2048, arms=list(ARMS))


def prepare():
    if OUT.exists() or AUTH.exists() or QUAL.exists(): raise RuntimeError('OPERATIVE_STATE')
    old.verify(); prior_bytes()
    save(PLAN, plan()); save(INDEX, development_index())
    save(BINDING, dict(code=code_hashes(), plan_sha256=sha(PLAN), contract_sha256=sha(CONTRACT),guide_sha256=sha(GUIDE),
        index_sha256=sha(INDEX), python=sys.version, executable_sha256=sha(sys.executable),
        previous_binding_sha256=sha(old.BINDING), reused_bytes=prior_bytes(),
        reused_closures={str(p.relative_to(ROOT)):sha(p) for p in
            (old.QUAL/'closure.json', old.prior.QUAL/'closure.json',PREVIOUS_PREP/'closure.json',*PREVIOUS_DOCS)}))


def verify():
    b = read(BINDING)
    if sys.flags.optimize or b['code'] != code_hashes(): raise RuntimeError('CODE_BINDING')
    if read(PLAN) != json.loads(json.dumps(plan())) or b['plan_sha256'] != sha(PLAN): raise RuntimeError('PLAN_BINDING')
    if b['contract_sha256'] != sha(CONTRACT) or b['index_sha256'] != sha(INDEX): raise RuntimeError('DOCUMENT_BINDING')
    if b['guide_sha256'] != sha(GUIDE): raise RuntimeError('GUIDE_BINDING')
    if b['python'] != sys.version or b['executable_sha256'] != sha(sys.executable): raise RuntimeError('RUNTIME_BINDING')
    if b['previous_binding_sha256'] != sha(old.BINDING) or b['reused_bytes'] != prior_bytes(): raise RuntimeError('PRIOR_BINDING')
    for p, h in b['reused_closures'].items():
        if sha(ROOT/p) != h: raise RuntimeError('PRIOR_CLOSURE')
    for item in read(INDEX)['entries']:
        if sha(ROOT/item['path']) != item['sha256']: raise RuntimeError('DEVELOPMENT_SOURCE_CHANGED')
    return b


class Ledger(OutputLedger):
    LIMIT = LIMIT
    RESERVE = RESERVE

    def __init__(self, folder, charged=0, *, claimed=False):
        if claimed:
            self.folder = Path(folder); self.used = sum(p.stat().st_size for p in self.folder.iterdir() if p.is_file())
            self.finalized = False
        else:
            super().__init__(folder)
        self.LIMIT = LIMIT-charged

    def write(self,name,value,final=False):
        if not final:
            cap=(65536 if name.endswith('-source.json') else
                 196608 if any(name.endswith('-'+a+'.json') for a in ARMS) else
                 32768 if name.endswith('-resources.json') else
                 1024 if name.endswith('-start.json') or name in ('claim.json','worker-complete.json') else 524288)
            size=len(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode())+1
            if size>cap: raise RuntimeError('FILE_CAP:'+name)
        super().write(name,value,final=final)


def manifest_entry(values, spec, registry):
    full = digest(values)
    blocks = {digest(values[i:i+4]) for i in range(0,len(values)-3,4)}
    exact = []; overlap = []
    for item in registry['entries']:
        if item['profile'] == full: exact.append(item['path'])
        common = sorted(blocks.intersection(item['blocks']))
        lengths = [int(n) for n,h in item['prefixes'].items() if int(n)<=len(values) and digest(values[:int(n)])==h]
        if common or lengths: overlap.append(dict(path=item['path'], common_block_hashes=common, longest_common_prefix=max(lengths,default=0)))
    return dict(id=spec['id'], frames=spec['frames'], profile=full, masks=spec['masks'],
        start_sample=0, first_ordinal=1, hop=4800, window=4800,
        source_file=spec['id']+'-source.json', full_matches=exact,
        novelty='WIEDERVERWENDET' if exact else 'NEW_WHOLE_SEQUENCE_WITH_KNOWN_FAMILY', overlaps=overlap)


def resource_check(r):
    if not r.get('terminal_cleanup') or not r.get('slots_released') or not r.get('states_identical'):
        raise RuntimeError('ARM_NOT_RELEASED')
    v = r['resources']
    if v['additional_python_peak'] > 16384: raise RuntimeError('PYTHON_LIMIT')
    if r['arm']=='U':
        checks = (v['original_frames_upper_bound']<=18, v['combined_upper_bound']<=20,
                  v['packed']<=416, v['receipt_bytes_peak']<=16384, v['utf8_upper']<=32768)
    else:
        m=v['meter']; checks=(m['frame_peak']<=18,m['combined_peak']<=20,m['output_slots_peak']<=2,
            m['receipt_bytes_peak']<=16384,m['receipt_transient_utf8_bytes_peak']<=32768,
            r.get('ema_cleared',False))
    if not all(checks): raise RuntimeError('SYSTEM_RESOURCE_LIMIT')


def execute(folder, specs, supplier, validator, registry, charged, check, *, assess=assess_case, summarize=aggregate):
    """Worker engine. Parent exclusively claims folder before this call."""
    ledger=Ledger(folder,charged,claimed=True); reports=[]; entries=[]; partial={}; active=None
    try:
        # Entire source/mask manifest is committed before ANY policy call.
        for s in specs:
            check(); values=supplier(s); validator(values,s)
            entry=manifest_entry(values,s,registry)
            ledger.write(entry['source_file'],values)
            entry['source_sha256']=sha(ledger.folder/entry['source_file'])
            entries.append(entry); del values
        ledger.write('manifest.json',dict(sealed_at=utc(), entries=entries,
            all_sources_before_policy=True, registry_scope=registry['scope']))
        manifest_hash=sha(ledger.folder/'manifest.json')
        for s, entry in zip(specs,entries):
            check(); results={}
            values=read(ledger.folder/entry['source_file'])
            if sha(ledger.folder/entry['source_file'])!=entry['source_sha256']: raise RuntimeError('SOURCE_TAMPER')
            validator(values,s)
            for a in ARMS:
                check(); active=dict(case=s['id'],arm=a,started_at=utc()); partial={}
                ledger.write(s['id']+'-'+a+'-start.json',active | {'manifest_sha256':manifest_hash})
                if a=='U': r=multi_replay(values,entry['profile'],count=s['frames'],evidence=partial,check=check)
                else: r=baseline_replay(values,entry['profile'],count=s['frames'],arm=a,evidence=partial,check=check)
                resource_check(r); check()
                ledger.write(s['id']+'-'+a+'.json',r); results[a]=r; partial={}; active=None
            report=assess(results,values,s)
            ledger.write(s['id']+'-assessment.json',report); reports.append(report)
            ledger.write(s['id']+'-resources.json',old.resource_report(results))
            if report['technical_errors']: raise RuntimeError('INVALID_CASE_EVIDENCE')
            del values, results, r
        check(); result=summarize(reports,specs)
        result['whole_set_new']=not any(e['full_matches'] for e in entries)
        if not result['whole_set_new']: result['novel_evaluation_claim']='VERFEHLT_WIEDERVERWENDUNG'
        ledger.write('assessment.json',result)
        if result['technical_errors']: raise RuntimeError('INVALID_AGGREGATE')
        check(); ledger.write('worker-complete.json',dict(completed_at=utc(), cases=len(reports),
            manifest_sha256=manifest_hash, experimental_admissions=sum(s['frames'] for s in specs)*5,
            reference_advances=sum(s['frames'] for s in specs)*5))
    except BaseException as exc:
        # Up to half the protected reserve preserves in-flight evidence; the
        # other half remains for the parent's final inventory even at the cap.
        try:
            record=dict(active=active,evidence=partial,error=type(exc).__name__+':'+str(exc))
            raw=json.dumps(record,sort_keys=True,separators=(',',':'),allow_nan=False).encode()+b'\n'
            if len(raw)>RESERVE//2:
                record=dict(active=active,error=record['error'],evidence_omitted='PARTIAL_EXCEEDS_HALF_RESERVE')
            emergency=Ledger(folder,charged,claimed=True)
            emergency.LIMIT-=RESERVE//2
            emergency.write('partial.json',record,final=True)
        except BaseException: pass
        raise


def _worker(folder, charged, deadline):
    def check():
        if time.monotonic() >= deadline: raise TimeoutError('EXECUTION_60_MINUTES')
    try:
        check(); verify(); check()
        execute(folder,source.cases(),source.materialize,source.validate,read(INDEX),charged,check)
        check(); verify(); check()
    except BaseException as exc:
        # Do not retain live policy objects in traceback beyond process exit.
        print(type(exc).__name__+':'+str(exc),file=sys.stderr)
        raise SystemExit(1)


def supervise(folder, charged, target, seconds=SECONDS, metadata=None):
    """Hard process deadline; never resumes an existing folder, even after failure."""
    started=time.monotonic(); ledger=Ledger(folder,charged)
    ledger.write('claim.json',dict(started_at=utc(), deadline_seconds=seconds,
        charged_previous_bytes=charged, status='CLAIMED_ONCE', binding=metadata))
    proc=None; error=None
    try:
        proc=multiprocessing.get_context('spawn').Process(target=target,args=(str(folder),charged,started+seconds))
        proc.start(); proc.join(max(0,seconds-(time.monotonic()-started)))
        if proc.is_alive():
            error='TIME_LIMIT'; proc.terminate(); proc.join(5)
            if proc.is_alive(): proc.kill(); proc.join()
        elif proc.exitcode != 0: error='WORKER_EXIT:'+str(proc.exitcode)
        elif not (Path(folder)/'worker-complete.json').exists(): error='MISSING_COMPLETION'
        if time.monotonic()-started >= seconds: error=error or 'TIME_LIMIT'
    except BaseException as exc:
        error=type(exc).__name__+':'+str(exc)
        if proc is not None and proc.is_alive(): proc.terminate(); proc.join()
        raise
    finally:
        files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in Path(folder).iterdir() if p.is_file()}
        closing=Ledger(folder,charged,claimed=True)
        closing.write('closure.json',dict(status='COMPLETE' if error is None else 'FAILED',error=error,
            files=files, charged_previous_bytes=charged, charged_before_closure=closing.used,
            duration_seconds=time.monotonic()-started, hard_process_stop=error=='TIME_LIMIT',
            independent_generalization='NICHT_GEPRUEFT', resume_permitted=False),final=True)
        if proc is not None: proc.close()
    if error: raise RuntimeError(error)


def check_preparation():
    c=read(QUAL/'closure.json')
    if c['status']!='PASS' or read(QUAL/'binding.json')!=verify(): raise RuntimeError('PREPARATION_NOT_VALID')
    for n,v in c['files'].items():
        if sha(QUAL/n)!=v['sha256'] or (QUAL/n).stat().st_size!=v['bytes']: raise RuntimeError('QUALIFICATION_TAMPER')
    return sum(p.stat().st_size for p in QUAL.iterdir() if p.is_file())


def run(path):
    verify()
    if read(Path(path)) != authorization('AUTHORIZED_ONCE'): raise RuntimeError('EXPLICIT_AUTHORIZATION_REQUIRED')
    charged=prior_bytes()+check_preparation()+sum((ROOT/e['path']).stat().st_size for e in read(INDEX)['entries'])
    charged+=sum(p.stat().st_size for p in (PLAN,BINDING,INDEX,TEMPLATE,CONTRACT,GUIDE,Path(path)))
    if charged>MAX_CHARGED: raise RuntimeError('PREPARATION_REFERENCE_CAP')
    supervise(OUT,charged,_worker,metadata=dict(authorization_sha256=sha(Path(path)),
        binding_sha256=sha(BINDING),plan_sha256=sha(PLAN),preparation_closure_sha256=sha(QUAL/'closure.json')))


def qualify():
    b=verify()
    if AUTH.exists() or OUT.exists(): raise RuntimeError('OPERATIVE_STATE')
    ledger=Ledger(QUAL,prior_bytes()); success=False; error=None
    try:
        ledger.write('binding.json',b)
        suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_s2uc_eval_prepare')
        def ids(s):
            for t in s:
                if isinstance(t,unittest.TestSuite): yield from ids(t)
                else: yield t.id()
        names=list(ids(suite)); stream=io.StringIO()
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        success=result.wasSuccessful() and not result.skipped
        ledger.write('tests.json',dict(ids=names,count=result.testsRun,success=success,
            failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),output=stream.getvalue()))
        from tests.test_s2uc_eval_prepare import FACTS
        ledger.write('facts.json',FACTS)
        ledger.write('source-snapshot.json',{n:(ROOT/n).read_text(encoding='utf-8') for n in NEW})
        ledger.write('plan.json',plan()); verify()
        if not success: raise RuntimeError('QUALIFICATION_FAILED')
        old.prior.write_text(ledger,'REPORT.md',f'# Raster32 Vorbereitung\n\n{result.testsRun}/{result.testsRun} PASS; keine Fehler/Skips.\n'
            'Nur neutrale Fixtures ausserhalb des Rasters; keine Evaluationsmaterialisierung oder Pilotlaeufe.\n'
            'Historische64 Codebindungen unveraendert. Neue Huelle maximal80 Positionen.\n'
            'Policyqualifikation und XYX-Vorbereitung wiederverwendet, nicht erneut ausgefuehrt.\n'
            'Test-IDs und Einzelresultate in tests.json; neutrale Ressourcen/Fehlerbelege in facts.json.\n'
            '64MiB Gesamtbudget,1MiB Abschlussreserve,3600s Prozessdeadline.\n'
            'Autorisierung bleibt ausstehend. Unabhaengige Generalisierung NICHT_GEPRUEFT.\n')
    except BaseException as exc:
        error=type(exc).__name__+':'+str(exc); raise
    finally:
        ledger.write('closure.json',dict(status='PASS' if success and error is None else 'FAILED',error=error,
            files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in QUAL.iterdir() if p.is_file()},
            reused_bytes=prior_bytes(), charged_before_closure=ledger.used,
            raster_materialized=False,raster_executed=False),final=True)
    save(TEMPLATE,authorization('PENDING_SEPARATE_AUTHORIZATION'))


def main():
    p=argparse.ArgumentParser(); p.add_argument('action',choices=('prepare','qualify','run'))
    p.add_argument('--authorization'); a=p.parse_args()
    if a.action=='prepare': prepare()
    elif a.action=='qualify': qualify()
    else:
        if not a.authorization: p.error('--authorization required')
        run(a.authorization)


if __name__=='__main__': main()
