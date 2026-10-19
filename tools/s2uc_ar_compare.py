"""AR export bridge and pure seven-grid selector; no automatic research search."""
import math
from tools.s2uc_ar_material import read_verified,need,IDS
from tools._s2uc_origin_judge import Truth
from tools._s2uc_signal_approx_compare import compare,report
GRID=(0.,1/256,1/128,1/64,1/32,1/16,1/8)

def recipe_epsilon(frames):
    need(len(frames)==8 and all(len(v)==48 and all(type(x) is float and math.isfinite(x) and abs(x)==2**-10 for x in v) for v in frames),'CALIBRATION_RECIPE')
    value=max(math.fsum(abs(x) for x in v)/48 for v in frames)
    need(value==2**-10,'CALIBRATION_FIXED_MAGNITUDE')
    return value

def named(data):
    """Public schema uses retrieval names, never the reused scorer aliases."""
    if isinstance(data,list):return [named(x) for x in data]
    if not isinstance(data,dict):return data
    def key(k):
        if k=='exact':return 'exact_retrieval'
        if k=='approx':return 'signal_approx_retrieval'
        return k.replace('legacy','exact_retrieval').replace('scaled','signal_approx_retrieval')
    return {key(k):named(v) for k,v in data.items() if k!='schema_mapping'}

def evaluate_export(folder,spec,part,profile,*,epsilon,tau):
    rows,_=read_verified(folder,spec,part,profile);cases={}
    for cid,row in rows.items():
        roots={tuple(range(4*i+1,4*i+5)):spec['episodes'][k]['root'] for i,k in enumerate(spec['cases'][cid]['learn'])}
        cases[cid]=compare(row['values'],row['profile']['digest'],Truth(row['truth'],row['positive'],roots,cid),epsilon=epsilon,tau=tau)
    return dict(cases=named(cases),summary=named(report(cases)),epsilon=epsilon,tau=tau,
        labels=dict(exact_retrieval='Exakter Abruf',signal_approx_retrieval='Signal-/Naeherungsabruf'),
        continuation_policy_for_both='legacy_v1',factor_scaled_v1_used=False,
        semantics='context_mae is concrete; null means abstention. observer_hybrid_mae/full_rows use context-else-persistence; no product fallback.')

def selection_rows(result):
    return {cid:{k:c['rows'][k]['origin_category'] for k in ('exact_retrieval','signal_approx_retrieval')} for cid,c in result['cases'].items()}

def select_parameters(results):
    """Only evaluates supplied outcomes. Never generates/replays research data."""
    need(len(results)==7 and all(type(r['tau']) is float for r in results) and sorted(r['tau'] for r in results)==list(GRID),'SEVEN_GRID_REQUIRED')
    baseline=None;assessments=[]
    for r in sorted(results,key=lambda x:x['tau']):
        rows=r['rows'];need(set(rows)==IDS,'ELEVEN_CASES_REQUIRED')
        for row in rows.values():
            need(set(row)=={'exact_retrieval','signal_approx_retrieval'} and all(v in ('CORRECT','WRONG','AMBIGUOUS','ABSTAIN') for v in row.values()),'ORIGIN_CATEGORY')
        exact={cid:row['exact_retrieval'] for cid,row in rows.items()}
        if baseline is None:baseline=exact
        need(exact==baseline,'REFERENCE_CHANGED')
        additional=sorted(cid for cid,row in rows.items() if row['signal_approx_retrieval']=='WRONG' and row['exact_retrieval']!='WRONG')
        correct=sum(rows[cid]['signal_approx_retrieval']=='CORRECT' for cid in ('R1','R2'))
        gain=correct-sum(rows[cid]['exact_retrieval']=='CORRECT' for cid in ('R1','R2'))
        assessments.append(dict(tau=r['tau'],eligible=not additional,additional_wrong=additional,correct_R1_R2=correct,gain_R1_R2=gain))
    allowed=[r for r in assessments if r['eligible']]
    if not allowed:return dict(status='NO_ELIGIBLE_PARAMETER',selected_tau=None,evaluation_selection_allowed=False,assessments=assessments)
    best=min(allowed,key=lambda r:(-r['correct_R1_R2'],r['tau']))
    if best['gain_R1_R2']<=0:return dict(status='NO_GAIN_NO_EVALUATION_SELECTION',selected_tau=None,evaluation_selection_allowed=False,assessments=assessments)
    return dict(status='DEVELOPMENT_CANDIDATE_ONLY',selected_tau=best['tau'],evaluation_selection_allowed=True,
        evaluation_execution_authorized=False,assessments=assessments)
