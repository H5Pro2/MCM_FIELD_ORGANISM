"""Whole-series evaluation after 32 verified case receipts; no policy calls."""
from fractions import Fraction
from tools import _s2uc_er1_stats as stats

def evaluate(reports,matrix,check=lambda:None):
    if any(r.get('integrity')!='PASS_DELTA_INTEGRITY' or not r.get('cleanup') for r in reports):raise ValueError('UNVERIFIED_CASE')
    check();summary=stats.aggregate(reports,matrix);reference=stats.reference(reports,matrix);check()
    if any(summary['primary'][k]!=reference[k] for k in ('mean','ci','pairs')):raise ValueError('STATISTICS_REFERENCE')
    pairs=list(map(Fraction,summary['primary']['pairs']))
    summary['worst_stories']=[r['replicate'] for r,d in zip(reports,pairs,strict=True) if d==max(pairs)]
    summary['mechanisms']={m:dict(retention_events=sum(r['mechanisms'][m]['retention_events'] for r in reports),warm_uses=sum(r['mechanisms'][m]['warm_uses'] for r in reports),local_gains=sum(r['mechanisms'][m]['local_gains'] for r in reports),first_witness=next((dict(replicate=r['replicate'],**r['mechanisms'][m]['first_witness']) for r in reports if r['mechanisms'][m]['first_witness']),None)) for m in ('E','F')}
    summary['retention_enables_useful_reuse_global']=summary['primary']['verdict']=='E_BETTER' and summary['mechanisms']['E']['first_witness'] is not None
    summary['execution_totals']={k:sum(r['executions'][k] for r in reports) for k in reports[0]['executions']}
    if summary['execution_totals']!=dict(policy=64,live_reference=64,archive_reference=64,extra_policy_measurement=0):raise ValueError('EXECUTION_COUNTS')
    summary['arm_warm_partitions']={m:{str(label):stats.balance([x for r in reports for x in r['rows'] if x[m+'_warm'] is label]) for label in (False,True)} for m in ('E','F')}
    # Independent exact error balance, not only the confidence interval.
    all_d=[Fraction(x['E'])-Fraction(x['F']) for r in reports for x in r['rows']]
    reference['cost_balance']=dict(gain=str(sum((-d for d in all_d if d<0),Fraction())),harm=str(sum((d for d in all_d if d>0),Fraction())),max_harm=str(max([Fraction()]+all_d)),count=len(all_d),better=sum(d<0 for d in all_d),worse=sum(d>0 for d in all_d),equal=sum(d==0 for d in all_d))
    if any(summary['balance'][k]!=v for k,v in reference['cost_balance'].items()):raise ValueError('COST_REFERENCE')
    summary['diagnostic_counting']='Retention events and event-linked warm uses may overlap; never added to target counts.'
    return summary,reference
