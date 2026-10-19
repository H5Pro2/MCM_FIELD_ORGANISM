"""Authorized seven-value AN-DEV search; no material synthesis or evaluation."""
import json,math,time
from pathlib import Path
from tools import s2uc_an_material as m
from tools import s2uc_an_compare as bridge
from tools._s2uc_signal_approx_compare import compare,report
from tools._s2uc_origin_judge import Truth,judge
OUT=Path(__file__).resolve().parent
def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)
b,p=m.load_binding();spec=p['partitions']['AN-DEV'];folder=m.ROOT/spec['output_directory']
rows,calibration=m.read_verified(folder,spec,'AN-DEV')
assert not (m.ROOT/p['partitions']['AN-EVAL']['output_directory']).exists()
epsilon=bridge.calibration_epsilon(folder,spec,'AN-DEV')
save('presearch.json',dict(plan_sha256=m.sha(m.PLAN),binding_sha256=m.sha(m.BINDING),runner_sha256=m.sha(__file__),grid=bridge.GRID,epsilon=epsilon,frame_amplitudes=[math.fsum(abs(x) for x in v)/48 for v in calibration],calibration_interpretation='maximum of eight exported Development NJ noise-frame mean absolute amplitudes; finite synthetic reference only',material={f.name:m.sha(f) for f in folder.iterdir()},continuation='legacy_v1 for both arms'))
selection_inputs=[];overview=[];resources={};started=time.perf_counter()
for index,tau in enumerate(bridge.GRID):
    cases={};learning={};case_resources={}
    for cid,row in rows.items():
        origins={tuple(range(4*i+1,4*i+5)):spec['episodes'][k]['root'] for i,k in enumerate(spec['cases'][cid]['learn'])}
        c=compare(row['values'],row['profile_digest'],Truth(row['truth'],row['positive'],origins,cid),epsilon=epsilon,tau=tau,measure=True)
        cases[cid]=c;case_resources[cid]={k:s['resources'] for k,s in c['systems'].items()}
        for n,t in enumerate(c['systems']['exact']['targets'][:-1]):
            target=t['target'];root=spec['episodes'][spec['cases'][cid]['learn'][(target-1)//4]]['root'] if target<=4*len(spec['cases'][cid]['learn']) else row['truth'];available={ix:r for ix,r in origins.items() if ix[-1]<=target-3}
            truth=Truth(root,root in available.values(),available,cid+'@'+str(target))
            lr={key:judge(system['targets'][n],truth) for key,system in c['systems'].items()}
            prov=json.loads(c['systems']['approx']['targets'][n]['forecast']['provenance_json'])
            learning[cid+'@'+str(target)]=dict(rows=lr,target=target,learning_targets=[],
                additional_wrong=lr['approx']['origin_category']=='WRONG' and lr['exact']['origin_category']!='WRONG',
                lost_exact_assignment=lr['exact']['assignment_covered'] and not lr['approx']['assignment_covered'],
                signal_lost_exact_assignment=prov['retrieval']['signal_lost_exact_single'],
                lost_correct_exact=lr['exact']['origin_category']=='CORRECT' and lr['approx']['origin_category']!='CORRECT')
        print(f'tau={tau} case={cid}',flush=True)
    assert len(cases)==11 and len(learning)==48
    for key in ('exact','approx'):
        assert sum(len(c['systems'][key]['admitted']) for c in cases.values())==129
        for x,y in [('R1','R3'),('R0','N3')]:
            assert cases[x]['systems'][key]['targets'][-1]['forecast']==cases[y]['systems'][key]['targets'][-1]['forecast']
            assert cases[x]['systems'][key]['states'][:10]==cases[y]['systems'][key]['states'][:10]
    result=dict(epsilon=epsilon,tau=tau,cases=bridge.named(cases),summary=bridge.named(report(cases)),
        learning_cases=bridge.named(learning),learning_summary=bridge.named(report(learning)),labels=dict(exact_retrieval='Exakter Abruf',signal_approx_retrieval='Signal-/Naeherungsabruf'),continuation_policy_for_both='legacy_v1',
        learning_origin_definition='True target root; positive if available in prior completed four-frame block before hint.',causal_checks=True)
    save(f'tau-{index}.json',result)
    selection_inputs.append(dict(tau=tau,rows=bridge.selection_rows(result)))
    overview.append(dict(tau=tau,summary=result['summary'],learning_summary=result['learning_summary']))
    resources[str(tau)]=bridge.named(case_resources)
    print(f'FINISHED tau={tau}',flush=True)
selection=bridge.select_parameters(selection_inputs)
save('selection-inputs.json',selection_inputs)
save('selection.json',dict(epsilon=epsilon,**selection,scope='Development only, not robustness evidence; no AN-EVAL execution'))
save('overview.json',overview)
pre=m.read(OUT/'presearch.json');assert all(m.sha(folder/k)==h for k,h in pre['material'].items())
m.load_binding();assert not (m.ROOT/p['partitions']['AN-EVAL']['output_directory']).exists()
save('verification.json',dict(status='PASS',material_unchanged=True,code_plan_runtime_unchanged=True,AN_EVAL_unproduced=True,
    material_bytes=sum(f.stat().st_size for f in folder.iterdir()),resources=resources,elapsed_search_seconds=time.perf_counter()-started,
    primary_frames_per_arm_per_setting=129,test_targets_per_arm_per_setting=11,learning_targets_per_arm_per_setting=48,settings=7,closure=m.read(folder/'closure.json')))
print(json.dumps(selection),flush=True)
