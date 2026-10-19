"""Bind/qualify stock preparation; real material requires a separate once-only grant."""
import argparse
import ast
import json
import sys
from fractions import Fraction
from pathlib import Path

from tools.s2uc_factor_material import ROOT,sha,read
from tools.s2uc_ema_qualification import save,hashes as legacy_hashes
from tools._s2uc_bounded_audio import OutputLedger
from tools._s2uc_ema_stock_observer import observed_replay,digest
from tools._s2uc_ema_stock_assessment import assess

PLAN=ROOT/'docs/S2UC_EMA_BESTANDSPLAN_20261001.json'
BINDING=ROOT/'docs/S2UC_EMA_BESTANDSBINDUNG_20261001.json'
CONTRACT=ROOT/'docs/S2UC_EMA_WECHSELNDER_BESTAND_GEGENPROBENVERTRAG_20261001.txt'
AUTH=ROOT/'docs/S2UC_EMA_BESTAND_AUTORISIERUNG_20261001.json'
TEMPLATE=ROOT/'docs/S2UC_EMA_BESTAND_AUTORISIERUNG_VORLAGE_20261001.json'
REAL_OUT=ROOT/'reports/s2uc/ema-stock-counterprobe-20261001-01'


def plan():
    main=[19,23,31,35,39,51,55,59,63];all_targets=list(range(3,64,2))
    stocks=[([],['A',1]),([['A',1]],None),([['A',1]],['B',2]),
        ([['A',1],['B',2]],None),([['A',1],['B',2]],['Bp',3]),
        ([['B',2],['A',1]],['Bp',3]),([['B',2],['A',1]],['C',4]),
        ([['B',2],['A',1]],['Bp',5]),([['B',2],['A',1]],['Bp',5]),
        ([['A',1],['Bp',3]],None),([['A',1],['Bp',3]],['C',6]),
        ([['Bp',3],['C',4]],None),([['Bp',3],['C',4]],['A',7]),
        ([['C',4],['A',5]],None),([['C',4],['A',5]],None),([['C',4],['A',5]],None)]
    expected={19:([[0,2,0]],'PERSISTENCE'),23:([[0,1,0]],'PERSISTENCE'),
        31:([[0,2,0]],'PERSISTENCE'),35:([[0,1,0]],'CONTEXT'),
        39:([[0,2,0],[1,5,0]],'PERSISTENCE'),51:([],'PERSISTENCE'),
        55:([[1,7,0]],'PERSISTENCE'),59:([[0,5,0]],'PERSISTENCE'),63:([[0,5,0]],'CONTEXT')}
    return dict(version='s2uc.ema.stock.v1',status='BOUND_NOT_AUTHORIZED',execution_authorized=False,
        frames=64,components=48,arms=['E','K','P'],hop=4800,window=4800,
        recipes=dict(A=['1/8','1/4','3/4','7/8'],B=['3/8','5/8','1/16','13/16'],
            Bp=['3/8','5/8','5/8','13/16'],C=['7/16','9/16','11/16','15/16']),
        blocks=['A','A','B','B','Bp','A','C','Bp','A','Bp','C','C','A','A','A','A'],
        masks=dict(V=[19,23,31,35,55,59,63],D=[31,35,63],M=main,
            N=[t for t in all_targets if t not in main],Gesamt=all_targets),
        expected_stock=[dict(frame=4*(i+1),retained=r,candidate=c) for i,(r,c) in enumerate(stocks)],
        expected_targets={str(t):dict(matches=m,choice=c,context_available=len(m)==1) for t,(m,c) in expected.items()},
        expectation_status='HYPOTHESES_ONLY_NOT_MEASUREMENTS_OR_SYSTEM_INPUTS',
        hypothesis_mismatch='Preserve actual data; distinguish expectation error from implementation error; dependent criteria NOT_EVALUABLE; never repair system to fit table',
        policies=dict(E='paired_error_ema_v1',K='context_else_persistence',P='persistence',
            alpha=.5,retrieval='exact_v1',continuation='legacy_v1',arithmetic='unchanged ordered mae48',tie='PERSISTENCE'),
        criteria=dict(stock='identical states/receipts across arms; unique/ambiguous/missing hypotheses observed; atomic target updates; only dead generations pruned at admission',
            experience='own-key prior errors only; opposite A/B evaluations; no update39; no old r1 after48; cold c7/r5;63 learns from59',
            benefit='V availability confirmed and E MAE strictly below BOTH K and P; otherwise SCHADEN/NICHT_NACHGEWIESEN; D diagnostic only',
            reporting='V,D,M,N,Gesamt sums and MAEs; every gain/harm; cold starts; deletion and lost experience; missing evidence never zero'),
        limits=dict(experimental_admissions=192,internal_reference_advances=192,raw_numeric_source_bytes=24576,
            retained=2,candidate=1,frames=18,proposal_vectors=2,cells=12,tickets=1,packed_bytes=416,
            additional_python_bytes=16384,receipt_bytes=16384,transient_utf8_bytes=32768,
            export_bytes=4194304,closure_reserve_bytes=262144),
        censored_target=65,output_directory=str(REAL_OUT.relative_to(ROOT)).replace('\\','/'),
        no_reset=True,no_direct_memory_mutation=True,no_protected_trace=True,
        failure_policy='exclusive output directory consumed before materialization; preserve partial export and closure; no retry',
        scope='controlled functional counterprobe, no general learning or cluster-organization claim')


def code_hashes():
    pending=list(legacy_hashes())+['tools/s2uc_ema_stock.py','tools/_s2uc_ema_stock_assessment.py',
        'tools/_s2uc_ema_stock_observer.py','tests/test_s2uc_ema_stock.py'];found=set()
    while pending:
        name=pending.pop()
        if name in found:continue
        found.add(name)
        for node in ast.walk(ast.parse((ROOT/name).read_text(encoding='utf-8'))):
            modules=[]
            if isinstance(node,ast.Import):modules=[a.name for a in node.names]
            elif isinstance(node,ast.ImportFrom) and node.module:modules=[node.module]+[node.module+'.'+a.name for a in node.names]
            for module in modules:
                file=module.replace('.','/')+'.py'
                if module.startswith(('tools.','tests.','mcm_field_organism.')) and (ROOT/file).is_file():pending.append(file)
    return {n:sha(ROOT/n) for n in sorted(found)}


def prepare():
    assert not REAL_OUT.exists()
    old=read(ROOT/'docs/S2UC_EMA_IMPLEMENTIERUNGSBINDUNG_20261001.json')
    assert old['code']==legacy_hashes(),'LEGACY_CODE_CHANGED'
    save(PLAN,plan())
    save(BINDING,dict(status='PREPARATION_BOUND_REAL_PROBE_NOT_AUTHORIZED',plan_sha256=sha(PLAN),
        contract_sha256=sha(CONTRACT),code=code_hashes(),unchanged_legacy_code=old['code'],
        python=sys.version,python_executable_sha256=sha(sys.executable)))
    save(TEMPLATE,authorization('PENDING_SEPARATE_AUTHORIZATION'))


def authorization(status):
    return dict(status=status,action='RUN_EMA_STOCK_ONCE',plan_sha256=sha(PLAN),
        binding_sha256=sha(BINDING),output_directory=plan()['output_directory'],frames=64,arms=['E','K','P'])


def verify_binding():
    if sys.flags.optimize:raise RuntimeError('ASSERTIONS_REQUIRED_FOR_BOUND_OBSERVER')
    b=read(BINDING)
    assert b['code']==code_hashes(),'CODE_BINDING'
    assert b['unchanged_legacy_code']==legacy_hashes(),'LEGACY_BINDING'
    assert b['plan_sha256']==sha(PLAN) and read(PLAN)==plan(),'PLAN_BINDING'
    assert b['contract_sha256']==sha(CONTRACT),'CONTRACT_BINDING'
    assert b['python']==sys.version and b['python_executable_sha256']==sha(sys.executable),'RUNTIME_BINDING'
    return b


def material(bound_plan):
    """Only called after authorization check and exclusive execution claim."""
    return [tuple([float(Fraction(x))]*48) for block in bound_plan['blocks'] for x in bound_plan['recipes'][block]]


def export(folder,source_factory,bound_plan,*,mode,metadata=None,check=None):
    ledger=OutputLedger(folder);results={};partial={};status='NOT_EVALUABLE';error=None
    try:
        ledger.write('execution-claim.json',dict(mode=mode,metadata=metadata))
        ledger.write('plan.json',bound_plan)
        values=source_factory()
        assert len(values)==64 and all(type(v) is tuple and len(v)==48 for v in values)
        profile=digest(dict(mode=mode,geometry='direct48.stock.v1'))
        ledger.write('source.json',dict(profile=profile,values=values,sha256=digest(values)))
        for arm in ('E','K','P'):
            partial={}
            result=observed_replay(values,profile,arm,count=64,evidence=partial)
            ledger.write(arm+'.json',result);results[arm]=result;partial={}
        assessment=assess(results,bound_plan)
        ledger.write('assessment.json',assessment)
        if check:check()
        status='COMPLETE'
    except BaseException as exc:
        error=type(exc).__name__+':'+str(exc)
        # Observer partial data is bounded by the same ledger; closure stays reserved.
        try:ledger.write('partial-observer.json',partial)
        except Exception:pass
        raise
    finally:
        files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in ledger.folder.iterdir() if p.is_file()}
        ledger.write('closure.json',dict(status=status,error=error,mode=mode,completed_arms=list(results),
            files=files,charged_bytes_before_closure=ledger.used,limit=ledger.LIMIT,reserve=ledger.RESERVE,
            experimental_admissions=sum(r['frames'] for r in results.values()),
            internal_reference_advances=sum(r['frames'] for r in results.values()),
            counts_are_completed_arms_only_on_failure=True,real_counterprobe=mode=='AUTHORIZED_REAL'),final=True)
    actual=sum(p.stat().st_size for p in ledger.folder.iterdir() if p.is_file())
    assert actual==ledger.used and actual<=ledger.LIMIT
    return dict(bytes=actual,results=results,assessment=assessment)


def run(auth_path):
    verify_binding()
    auth=read(auth_path)
    assert auth==authorization('AUTHORIZED_ONCE'),'SEPARATE_AUTHORIZATION_REQUIRED'
    # Exclusive folder creation in export precedes even source generation.
    return export(REAL_OUT,lambda:material(read(PLAN)),read(PLAN),mode='AUTHORIZED_REAL',
        metadata=dict(authorization=auth,binding_sha256=sha(BINDING)),check=verify_binding)


def qualify(folder):
    import unittest
    from tests import test_s2uc_ema_stock as tests
    b=verify_binding();assert not REAL_OUT.exists()
    folder=Path(folder).resolve();assert folder.is_relative_to((ROOT/'reports/s2uc').resolve())
    folder.mkdir(exist_ok=False)
    tests.FACTS.clear();tests.EXPORT_FOLDER=folder/'neutral-export'
    with (folder/'tests.txt').open('x',encoding='utf-8') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(tests.StockTests))
    unchanged=b==verify_binding()
    save(folder/'facts.json',tests.FACTS)
    final=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),
        success=result.wasSuccessful() and unchanged,code_unchanged=unchanged,real_counterprobe_executed=REAL_OUT.exists(),
        binding_sha256=sha(BINDING),plan_sha256=sha(PLAN))
    save(folder/'test-result.json',final);print(json.dumps(final))
    return 0 if final['success'] and not final['real_counterprobe_executed'] else 1


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','qualify','run'])
    parser.add_argument('--output');parser.add_argument('--authorization');args=parser.parse_args()
    if args.action=='prepare':prepare();return 0
    if args.action=='qualify':return qualify(args.output)
    if not args.authorization:parser.error('--authorization required; real run needs separate authorization')
    run(args.authorization);return 0


if __name__=='__main__':sys.exit(main())
