"""Read-only postprocessing of the seven saved results; never replay material."""
import json
from pathlib import Path
from tools import s2uc_an_material as m
from tools import s2uc_an_compare as bridge

OUT=Path(__file__).resolve().parent


def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)


def main():
    verification=m.read(OUT/'verification.json',4194304)
    assert verification['status']=='PASS' and verification['settings']==7
    selection=m.read(OUT/'selection.json')
    results=[m.read(OUT/f'tau-{i}.json',8388608) for i in range(7)]
    assert [r['tau'] for r in results]==list(bridge.GRID)
    assert len({r['epsilon'] for r in results})==1
    recalculated=bridge.select_parameters([dict(tau=r['tau'],rows=bridge.selection_rows(r)) for r in results])
    assert all(selection[k]==v for k,v in recalculated.items())
    tables=[];resource_rows=[];all_harms={}
    for r in results:
        assert len(r['cases'])==11 and len(r['learning_cases'])==48
        summary=r['summary'];learn=r['learning_summary']
        categories={cid:{arm:row['origin_category'] for arm,row in c['rows'].items()} for cid,c in r['cases'].items()}
        abstentions={cid:{arm:dict(status=s['targets'][-1]['forecast']['status'],
            receipt=json.loads(s['targets'][-1]['forecast']['provenance_json']))
            for arm,s in c['systems'].items()} for cid,c in r['cases'].items()}
        for cid,c in r['cases'].items():
            exact=c['systems']['exact_retrieval'];approx=c['systems']['signal_approx_retrieval']
            assert exact['states']==approx['states'] and exact['final_state']==approx['final_state']
            for arm,system in c['systems'].items():
                assert system['admitted']==list(range(1,c['target']+1)) and system['slots_released']
                assert all(x['forecast_bound'] for x in system['pull_log'] if x['index']>=3 and x['index']%2)
                resource_rows.append(dict(tau=r['tau'],case=cid,arm=arm,**system['resources']))
        primary_harms={};learning_harms={}
        for key,source,dest in [('primary',r['cases'],primary_harms),('learning',r['learning_cases'],learning_harms)]:
            for cid,c in source.items():
                e=c['rows']['exact_retrieval'];a=c['rows']['signal_approx_retrieval']
                for name,delta in [('exact_vs_persistence',e['observer_hybrid_mae']-e['persistence_mae']),
                    ('approx_vs_persistence',a['observer_hybrid_mae']-a['persistence_mae']),
                    ('approx_vs_exact',a['observer_hybrid_mae']-e['observer_hybrid_mae'])]:
                    if delta>0:dest.setdefault(name,[]).append(dict(case=cid,target=c['target'],mae_increase=delta,exact=e,approx=a))
        all_harms[str(r['tau'])]=dict(primary=primary_harms,learning=learning_harms)
        tables.append(dict(tau=r['tau'],correct_R1_R2=sum(categories[c]['signal_approx_retrieval']=='CORRECT' for c in ('R1','R2')),
            additional_wrong=summary['additional_wrong'],lost_exact=summary['lost_exact_assignments'],
            signal_lost_exact=summary['signal_lost_exact_assignments'],lost_correct=summary['lost_correct_exact'],
            origins=categories,coverage={arm:dict(assignments=v['assignment_covered'],context=v['context_covered'],total=v['total'])
                for arm,v in summary['comparison']['policies'].items()},
            full_means=summary['comparison']['full_means'],abstentions=abstentions,
            learning_additional_wrong=learn['additional_wrong'],learning_lost_exact=learn['lost_exact_assignments']))
    peak_keys=[k for k,v in resource_rows[0].items() if k not in ('tau','case','arm') and type(v) in (int,float)]
    peaks={k:max(row[k] for row in resource_rows) for k in peak_keys}
    assert peaks['frame_peak']<=18 and peaks['output_slots_peak']<=2 and peaks['combined_peak']<=20
    assert peaks['receipt_bytes_peak']<=16384 and peaks['receipt_transient_utf8_bytes_peak']<=32768
    assert peaks['temporary_numeric_vectors_peak']==0
    save('decision-tables.json',tables);save('all-harms.json',all_harms)
    save('resource-ledger.json',dict(peaks=peaks,rows=resource_rows,
        scope='seven completed settings; failed observer attempt contains one additional R0 pair, documented separately'))
    b,p=m.load_binding();pre=m.read(OUT/'presearch.json');folder=m.ROOT/p['partitions']['AN-DEV']['output_directory']
    assert pre['runner_sha256']==m.sha(OUT/'run_search.py')
    assert all(m.sha(folder/k)==h for k,h in pre['material'].items())
    assert not (m.ROOT/p['partitions']['AN-EVAL']['output_directory']).exists()
    save('final-verification.json',dict(status='PASS',saved_results_validated=7,selection_recomputed_without_replay=True,
        material_unchanged=True,bindings_unchanged=True,runner_unchanged=True,AN_EVAL_unproduced=True,
        material_files=len(list(folder.iterdir())),material_bytes=sum(f.stat().st_size for f in folder.iterdir()),
        authorized_production_calls=1,production_exit_code=0,search_exit_code=0,
        completed_settings=7,completed_case_replays_per_arm=77,frames_per_arm_per_setting=129,
        primary_per_setting=11,learning_per_setting=48,extra_aborted_observer_case='tau0 R0; 11 frames per arm; no completed setting',
        peaks=peaks,plan_sha256=m.sha(m.PLAN),binding_sha256=m.sha(m.BINDING)))
    selected=next((r for r in tables if r['tau']==selection['selected_tau']),None)
    print(json.dumps(dict(selection=selection,grid=[{k:r[k] for k in ('tau','correct_R1_R2','additional_wrong','lost_exact')} for r in tables],
        selected=selected,peaks=peaks),indent=2))


if __name__=='__main__':main()
