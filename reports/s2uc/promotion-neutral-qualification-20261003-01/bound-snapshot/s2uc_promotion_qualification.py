"""Bind optional promotion development and prepare separately authorized S/W/L."""
import ast
import argparse
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from tools.s2uc_factor_material import ROOT,sha,read
from tools.s2uc_ema_qualification import save
from tools.s2uc_ema_stock import plan as stock_plan,verify_binding as verify_legacy
from tools._s2uc_bounded_audio import OutputLedger
from tools._s2uc_promotion_replay import replay
from tools._s2uc_ema_stock_observer import digest

PLAN=ROOT/'docs/S2UC_PROMOTION_PLAN_20261003.json'
BINDING=ROOT/'docs/S2UC_PROMOTION_BINDUNG_20261003.json'
CONTRACT=ROOT/'docs/S2UC_EMA_DIREKTE_PROMOTIONSMITNAHME_GEGENPRUEFVERTRAG_20261003.txt'
TEMPLATE=ROOT/'docs/S2UC_PROMOTION_AUTORISIERUNG_VORLAGE_20261003.json'
AUTH=ROOT/'docs/S2UC_PROMOTION_AUTORISIERUNG_20261003.json'
OUT=ROOT/'reports/s2uc/promotion-counterprobe-20261003-01'


def plan():
    old=stock_plan();short=dict(G=list(range(3,16,2)),H=[7,11,15],N=[3,5,9,13],V=[7,11],D=[11],J=[11])
    return dict(status='BOUND_NOT_AUTHORIZED',arms=['M','E','K','P'],
        terminology='synthetische Folgen mit regulaerer Aufnahme; technische Fixtures getrennt',
        stories=dict(S=dict(frames=16,blocks=['X']*4,masks=short,
            expected_stock=[[4,[],1],[8,[1],None],[12,[1],None],[16,[1],None]],
            expected_M_choices={'7':'PERSISTENCE','11':'CONTEXT','15':'CONTEXT'}),
            W=dict(frames=16,blocks=['X','X','Xp','Xp'],masks=short,
                expected_stock=[[4,[],1],[8,[1],None],[12,[1],2],[16,[1,2],None]],
                expected_M_choices={'7':'PERSISTENCE','11':'CONTEXT','15':'PERSISTENCE'}),
            L=dict(frames=64,blocks=old['blocks'],
                masks=dict(G=old['masks']['Gesamt'],H=old['masks']['M'],N=old['masks']['N'],
                    V=old['masks']['V'],D=old['masks']['D'],J=[19,23,59]),
                expected_stock=[[e['frame'],[t[1] for t in e['retained']],None if e['candidate'] is None else e['candidate'][1]] for e in old['expected_stock']],
                expected_M_choices={str(t):'CONTEXT' if t in (19,23,35,59,63) else 'PERSISTENCE' for t in old['masks']['M']})),
        recipes=dict(**old['recipes'],X=['3/16','5/16','13/16','15/16'],Xp=['3/16','5/16','5/16','15/16']),
        components=48,hop=4800,window=4800,alpha=.5,retrieval='exact_v1',continuation='legacy_v1',
        selection='paired_error_ema_v1',promotion='direct_promotion_v1',
        independent_evaluation='NOT_TESTED_DEVELOPMENT_ONLY',
        limits=dict(frames=18,proposals=2,cells=12,tickets=1,packed_bytes=416,additional_python=16384,
            receipt=16384,transient_utf8=32768,export=4194304,reserve=262144,
            source_frames=96,experimental_admissions=384,internal_reference_advances=384),
        output=str(OUT.relative_to(ROOT)).replace('\\','/'),
        criteria=dict(assignment='bitwise pairs, immediate original-frame identity, no ticket transfer; unchanged memory and receipts',
            stable='S H and G strictly better M than E',robust='each story H/G M<=E and at least one strict improvement',
            benefit='per story V available and M strictly better than E,K,P; D/J cannot replace V,H,G',
            hypothesis_mismatch='NOT_EVALUABLE dependent criteria; preserve data, no repair or replacement'))


def hashes():
    pending=list(verify_legacy()['code'])+['tools/_s2uc_promotion_ema.py','tools/_s2uc_promotion_replay.py',
        'tools/s2uc_promotion_qualification.py','tests/test_s2uc_promotion_ema.py','tests/test_s2uc_promotion_runner.py']
    found=set()
    while pending:
        name=pending.pop()
        if name in found:continue
        found.add(name)
        for node in ast.walk(ast.parse((ROOT/name).read_text(encoding='utf-8'))):
            modules=[]
            if isinstance(node,ast.Import):modules=[a.name for a in node.names]
            elif isinstance(node,ast.ImportFrom) and node.module:modules=[node.module]+[node.module+'.'+a.name for a in node.names]
            for module in modules:
                f=module.replace('.','/')+'.py'
                if module.startswith(('tools.','tests.','mcm_field_organism.')) and (ROOT/f).is_file():pending.append(f)
    return {f:sha(ROOT/f) for f in sorted(found)}


def auth(status):
    return dict(status=status,action='RUN_PROMOTION_SWL_ONCE',plan_sha256=sha(PLAN),binding_sha256=sha(BINDING),
        stories=['S','W','L'],arms=['M','E','K','P'],output=plan()['output'])


def prepare():
    assert not OUT.exists() and not AUTH.exists()
    save(PLAN,plan())
    save(BINDING,dict(code=hashes(),plan_sha256=sha(PLAN),contract_sha256=sha(CONTRACT),
        python=sys.version,python_executable_sha256=sha(sys.executable),legacy_binding_sha256=sha(ROOT/'docs/S2UC_EMA_BESTANDSBINDUNG_20261001.json')))
    save(TEMPLATE,auth('PENDING_SEPARATE_AUTHORIZATION'))


def verify():
    if sys.flags.optimize:raise RuntimeError('ASSERTIONS_REQUIRED')
    b=read(BINDING)
    assert b['code']==hashes() and b['plan_sha256']==sha(PLAN) and read(PLAN)==plan(),'PROMOTION_BINDING'
    assert b['contract_sha256']==sha(CONTRACT),'PROMOTION_CONTRACT'
    assert b['python']==sys.version and b['python_executable_sha256']==sha(sys.executable),'PROMOTION_RUNTIME'
    return b


def material(p,story):
    return [(float(Fraction(x)),)*48 for block in p['stories'][story]['blocks'] for x in p['recipes'][block]]


def assess(results,spec):
    deviations=[];technical=[];metrics={}
    expected=spec['masks']['G']
    for a,r in results.items():
        if [row['target'] for row in r['rows']]!=expected:technical.append(a+':TARGET_SET')
        if not r['slots_released'] or not r['ema_cleared'] or r['censored_target']!=spec['frames']+1:
            technical.append(a+':RELEASE_CENSOR')
    if len({digest(r['state_hashes']) for r in results.values()})!=1:technical.append('MEMORY_STATES')
    if len({digest([f['receipt'] for f in r['forecasts']]) for r in results.values()})!=1:technical.append('RECEIPTS')
    rows={a:{r['target']:r for r in result['rows']} for a,result in results.items()}
    for mask,targets in spec['masks'].items():
        arms={}
        for a in rows:
            missing=[t for t in targets if t not in rows[a]]
            errors=[rows[a][t]['selected_mae'] for t in targets if t in rows[a]]
            arms[a]=dict(count=len(errors),missing=missing,error_sum=None if missing else sum(errors),
                mae=None if missing else sum(errors)/len(targets))
        metrics[mask]=arms
    forecasts={f['target']:f for f in results['M']['forecasts']}
    events={e['frame']:e for e in results['M']['admissions']}
    for frame,retained,candidate in spec.get('expected_stock',[]):
        stock=events[frame]['after']
        actual=[[x['generation'] for x in stock['retained']],None if stock['candidate'] is None else stock['candidate']['generation']]
        if actual!=[retained,candidate]:deviations.append(dict(frame=frame,expected=[retained,candidate],actual=actual))
    for t,choice in spec.get('expected_M_choices',{}).items():
        if forecasts[int(t)]['choice']!=choice:deviations.append(dict(target=int(t),expected_choice=choice,actual=forecasts[int(t)]['choice']))
    available=all(forecasts[t]['context_available'] for t in spec['masks']['V'])
    valid=not technical and not deviations
    v=metrics['V'];benefit='NOT_EVALUABLE'
    if valid and available:
        benefit='BELEGT' if all(v['M']['mae']<v[a]['mae'] for a in ('E','K','P')) else (
            'SCHADEN' if any(v['M']['mae']>v[a]['mae'] for a in ('E','K','P')) else 'NICHT_NACHGEWIESEN')
    return dict(metrics=metrics,technical_errors=technical,expectation_deviations=deviations,
        assignment='PASS' if valid else 'NOT_EVALUABLE',V_context_available=available,baseline_benefit_V=benefit,
        comparisons=[dict(target=t,choices={a:rows[a][t]['choice'] for a in rows},
            errors={a:rows[a][t]['selected_mae'] for a in rows},
            M_minus={a:rows['M'][t]['selected_mae']-rows[a][t]['selected_mae'] for a in ('E','K','P')})
            for t in expected if all(t in rows[a] for a in rows)],independent_evaluation='NOT_TESTED')


def export(folder,p,source_factory,*,mode,metadata=None,check=None):
    ledger=OutputLedger(folder);results={};assessments={};partial={};error=None;status='NOT_EVALUABLE'
    try:
        ledger.write('claim.json',dict(mode=mode,metadata=metadata));ledger.write('plan.json',p)
        for story,spec in p['stories'].items():
            values=source_factory(p,story)
            assert len(values)==spec['frames']
            profile=digest(dict(story=story,mode=mode,geometry='promotion48.v1'))
            ledger.write(story+'-source.json',dict(profile=profile,values=values,sha256=digest(values)))
            results[story]={}
            for arm in ('M','E','K','P'):
                partial={};r=replay(values,profile,count=spec['frames'],arm=arm,evidence=partial)
                ledger.write(story+'-'+arm+'.json',r);results[story][arm]=r;partial={}
            assessments[story]=assess(results[story],spec)
            ledger.write(story+'-assessment.json',assessments[story])
        valid=all(x['assignment']=='PASS' for x in assessments.values())
        robust=valid and all(x['metrics'][k]['M']['mae']<=x['metrics'][k]['E']['mae'] for x in assessments.values() for k in ('H','G'))
        strict=any(x['metrics'][k]['M']['mae']<x['metrics'][k]['E']['mae'] for x in assessments.values() for k in ('H','G')) if valid else False
        stable='NOT_APPLICABLE';mixed='NOT_APPLICABLE'
        if 'S' in assessments and 'W' in assessments:
            stable=('BELEGT' if all(assessments['S']['metrics'][k]['M']['mae']<assessments['S']['metrics'][k]['E']['mae'] for k in ('H','G'))
                else 'NICHT_NACHGEWIESEN') if assessments['S']['assignment']=='PASS' else 'NOT_EVALUABLE'
            harm=any(c['M_minus']['E']>0 for c in assessments['W']['comparisons'])
            mixed='BEGRENZTER_STABILITAETSVORTEIL_MIT_WECHSELSCHADEN' if stable=='BELEGT' and harm else 'NO_MIXED_CLAIM'
        ledger.write('summary.json',dict(robust_advantage='BELEGT' if robust and strict else 'NICHT_NACHGEWIESEN' if valid else 'NOT_EVALUABLE',
            stable_advantage=stable,mixed_finding=mixed,
            judgments={k:dict(assignment=v['assignment'],baseline_benefit_V=v['baseline_benefit_V']) for k,v in assessments.items()},
            independent_evaluation='NOT_TESTED'))
        if check:check()
        status='COMPLETE'
    except BaseException as exc:
        error=type(exc).__name__+':'+str(exc)
        try:ledger.write('partial.json',partial)
        except Exception:pass
        raise
    finally:
        ledger.write('closure.json',dict(status=status,error=error,mode=mode,charged_before_closure=ledger.used,
            files={f.name:dict(bytes=f.stat().st_size,sha256=sha(f)) for f in ledger.folder.iterdir() if f.is_file()},
            completed_arms={k:list(v) for k,v in results.items()},
            experimental_admissions=sum(r['frames'] for v in results.values() for r in v.values()),
            internal_reference_advances=sum(r['frames'] for v in results.values() for r in v.values()),
            counts_are_completed_arms_only_on_failure=True,limit=ledger.LIMIT,reserve=ledger.RESERVE),final=True)
    total=sum(f.stat().st_size for f in ledger.folder.iterdir() if f.is_file())
    assert total==ledger.used
    return dict(bytes=total,results=results,assessments=assessments)


def run(path):
    b=verify();authorization=read(path)
    assert authorization==auth('AUTHORIZED_ONCE'),'PROMOTION_SEPARATE_AUTHORIZATION_REQUIRED'
    return export(OUT,read(PLAN),material,mode='AUTHORIZED_SYNTHETIC_REGULAR_ADMISSION',
        metadata=dict(authorization=authorization,binding=b),check=verify)


def qualify(folder):
    from tests import test_s2uc_promotion_ema as tests
    from tests import test_s2uc_promotion_runner as runner_tests
    from tests import test_s2uc_paired_error_ema as legacy
    from tests import test_s2uc_ema_stock as stock
    b=verify();assert not OUT.exists() and not AUTH.exists()
    folder=Path(folder).resolve();assert folder.is_relative_to((ROOT/'reports/s2uc').resolve())
    folder.mkdir(exist_ok=False);runner_tests.EXPORT_FOLDER=folder/'neutral-four-arm-export'
    stock.EXPORT_FOLDER=folder/'legacy-neutral-export'
    suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(cls) for cls in
        (tests.PromotionTests,runner_tests.RunnerTests,legacy.PairedErrorTests,stock.StockTests))
    with (folder/'tests.txt').open('x',encoding='utf-8') as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    unchanged=b==verify()
    save(folder/'facts.json',dict(promotion=tests.FACTS,runner=runner_tests.FACTS,legacy=legacy.FACTS,stock=stock.FACTS))
    final=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),
        success=result.wasSuccessful() and unchanged,code_unchanged=unchanged,SWL_generated=False,
        binding_sha256=sha(BINDING),plan_sha256=sha(PLAN))
    save(folder/'test-result.json',final);print(json.dumps(final));return 0 if final['success'] else 1


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','qualify','run'])
    parser.add_argument('--output');parser.add_argument('--authorization');a=parser.parse_args()
    if a.action=='prepare':prepare();return 0
    if a.action=='qualify':return qualify(a.output)
    if not a.authorization:parser.error('--authorization required')
    run(a.authorization);return 0


if __name__=='__main__':sys.exit(main())
