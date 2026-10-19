"""Paired observer; arms cannot access this module's records or histories."""
import json
from tools._s2uc_ulz1_replay import replay as arm_replay
from tools._s2uc_ulz1_resources import deep
from tools import _s2uc_ulz1_sources as source

def need(ok,why):
    if not ok:raise ValueError(why)

def equal_lifecycle(u,l):
    need(len(u['events'])==len(l['events']),'EVENT_COUNT')
    for a,b in zip(u['events'],l['events'],strict=True):
        for k in ('index','before','after','forecast_stock','partial_admission'):
            need(a[k]==b[k],'PAIRED_STOCK:'+k)
        need([(c['key'],c['prior_feedback']) for c in a['before_cells']]==
             [(c['key'],c['prior_feedback']) for c in b['before_cells']],'PAIRED_CELL_LIFETIME')
    for a,b in zip(u['forecasts'],l['forecasts'],strict=True):
        need(a['matches']==b['matches'],'PAIRED_ELIGIBILITY')
        need([(h['eligible'],h.get('evaluation')=='COLD') for h in a['hypotheses']]==
             [(h['eligible'],h.get('evaluation')=='COLD') for h in b['hypotheses']],'PAIRED_WARM')
    for a,b in zip(u['rows'],l['rows'],strict=True):
        need(a['target']==b['target'] and a['updates']==b['updates'],'PAIRED_FEEDBACK')
        need([(h['key'],h['ordinals'],h['original'],h['prior_feedback']) for h in a['hypotheses']]==
             [(h['key'],h['ordinals'],h['original'],h['prior_feedback']) for h in b['hypotheses']],'PAIRED_ORIGINALS')
    need(u['full_confirmations']==l['full_confirmations'],'PAIRED_CONFIRMATIONS')

def compact(r,shared=False):
    # Earlier feedback indices and lineage are reconstructible from all events/updates.
    def h(x):return None if x is None else {k:v for k,v in x.items() if k not in ('prior_feedback','promotion_lineage')}
    rows=[x|dict(hypotheses=[h(v) for v in x['hypotheses']],selected=h(x['selected'])) for x in r['rows']]
    events=[dict(index=e['index'],before=e['before'],after=e['after'],
                 cells=[dict(key=c['key'],values=c['values']) for c in e['before_cells']])
            for e in r['events'] if e['index']%2==0 or e['index']==1]
    if shared:
        events=[dict(index=e['index'],cells=e['cells']) for e in events]
    res=dict(r['resources']);bounds=res.pop('allocation_boundaries')
    cols=list(bounds[0]);res['allocation_columns']=cols
    res['allocation_rows']=[[b[k] for k in cols] for b in bounds]
    return dict(rows=rows,events=events,forecasts=r['forecasts'],resources=res,
        shared_stock_with_U=shared,full_confirmations=r['full_confirmations'],
        reference_equal=r['reference_equal'],cleanup=r['cleanup'],censored_target=r['censored_target'])

def replay(record,check=lambda:None,*,short=False):
    values=source.values(record)
    need(len(values)==1040 or short,'FRAME_COUNT')
    profile=source.digest('ULZ1-schema-48-float64')
    u=arm_replay(values,profile,False,check,last=False)
    l=arm_replay(values,profile,False,check,last=True)
    equal_lifecycle(u,l)
    rows=[];cumulative=0.
    for a,b in zip(u['rows'],l['rows'],strict=True):
        cumulative+=a['error']-b['error']
        rows.append(dict(target=a['target'],U=a['error'],L=b['error'],cumulative_difference=cumulative))
    metrics={m:{arm:sum(x[arm] for x in rows if x['target'] in ts)/len(ts)
                for arm in ('U','L')} for m,ts in source.masks().items()} if not short else {}
    need(u['cleanup'] and l['cleanup'],'CLEANUP')
    resources={arm:{k:v for k,v in r['resources'].items() if k!='allocation_boundaries'} for arm,r in (('U',u),('L',l))}
    # Actual boundary original/cell utilization must match; outputs may differ.
    for a,b in zip(u['resources']['allocation_boundaries'],l['resources']['allocation_boundaries'],strict=True):
        need(all(a[k]==b[k] for k in ('phase','originals','ordinals','valid_cells')),'PAIRED_RESOURCE_OCCUPANCY')
    return dict(rows=rows,U=compact(u),L=compact(l,shared=True),metrics=metrics,
        resources=resources,complete=True,reference_equal=True,lifecycle_equal=True,
        neutral_only=record['neutral_only'],frames_per_arm=len(values),targets_per_arm=len(rows),
        reference_advances=dict(U=len(values),L=len(values)),
        observer=dict(input_payload_bytes=384*len(values),input_reachable_bytes=deep(values),
                      evidence_boundary_bytes=deep(u)+deep(l),
                      note='External input/evidence census, not process peak; no reference history accessible by arms.'))
