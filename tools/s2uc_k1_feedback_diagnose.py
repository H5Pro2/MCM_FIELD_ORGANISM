"""Read-only archive diagnosis; stdlib only, no policy or source-generator imports."""
import base64
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'reports/s2uc/k1-comparison-20261004-01'
OUT=ROOT/'reports/s2uc/k1-feedback-diagnosis-20261004-01'


def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def ref(file,pointer):return file+'#'+pointer
def items(s):return [(0,x) for x in s['retained']]+([] if s['candidate'] is None else [(1,s['candidate'])])
def item(s,ords):return next(((role,t) for role,t in items(s) if t['ordinals']==ords),None)


def chain(cid,arm,ords,offset,target,archive):
    file=f'{cid}-{arm}.json';data=archive[file]
    appearances=[]
    for fi,f in enumerate(data['forecasts']):
        t=f['input_indices'][-1]+1
        for hi,(m,h) in enumerate(zip(f['matches'],f['hypotheses'],strict=True)):
            if not h['eligible'] or m['ordinals']!=ords or m['offset']!=offset:continue
            k=[0 if m['role']=='retained' else 1,m['generation'],offset]
            row=next(((ri,r) for ri,r in enumerate(data['rows']) if r['target']==t),None)
            up=None;hyp=None
            if row:
                ri,r=row
                ui,up=next((ui,u) for ui,u in enumerate(r['updates']) if u['key']==k)
                hj,hyp=next((hj,v) for hj,v in enumerate(r['hypotheses']) if v['key']==k)
            appearances.append(dict(target=t,key=k,cold=h['ec'] is None,
                ec=h['ec'],ep=h['ep'],feedback='CENSORED' if up is None else 'ACCEPTED' if up['live'] else 'DEAD_KEY_REJECTED',
                raw_errors=None if up is None else [up['ec'],up['ep']],prior_feedback=[] if hyp is None else hyp['prior_feedback'],
                promotion_lineage=[] if hyp is None else hyp['promotion_lineage'],
                forecast_ref=ref(file,f'/forecasts/{fi}/hypotheses/{hi}'),
                hypothesis_ref=None if row is None else ref(file,f'/rows/{ri}/hypotheses/{hj}'),
                feedback_ref=None if row is None else ref(file,f'/rows/{ri}/updates/{ui}')))
    changes=[]
    for ei,e in enumerate(data['events']):
        before=item(e['before'],ords);after=item(e['after'],ords)
        bk=None if before is None else [before[0],before[1]['generation'],offset]
        ak=None if after is None else [after[0],after[1]['generation'],offset]
        if bk!=ak:
            kind='ORIGINAL_ADMITTED' if bk is None else 'PROMOTED_SAME_ORIGINAL' if ak is not None else 'ORIGINAL_REMOVED'
            if kind=='ORIGINAL_REMOVED':
                kind='CANDIDATE_REPLACED' if before[0]==1 and e['after']['candidate'] is not None else 'CANDIDATE_RELEASED' if before[0]==1 else 'RETAINED_EVICTED'
            changes.append(dict(index=e['index'],kind=kind,old_key=bk,new_key=ak,event_ref=ref(file,f'/events/{ei}')))
    present=item(data['events'][-1]['after'],ords) is not None
    formation=next((e for e in changes if e['kind']=='ORIGINAL_ADMITTED'),None)
    removal=next((e for e in changes if e['new_key'] is None),None)
    first=appearances[0] if appearances else None
    current=next((x for x in appearances if x['target']==target),None)
    before=[x for x in appearances if x['target']<target]
    later=[x for x in appearances if x['target']>target]
    raw=archive[cid+'-source.json']['values']
    flat=struct.unpack('<'+'d'*(raw['frames']*48),base64.b64decode(raw['data'],validate=True))
    vectors=[flat[i:i+48] for i in range(0,len(flat),48)]
    pair=[vectors[ords[offset]-1],vectors[ords[offset+1]-1]]
    matches=[]
    for t in range(target+2,len(vectors)+2,2):
        if vectors[t-3:t-1]==pair:
            matches.append(dict(target=t,censored=t>len(vectors),actually_eligible=any(x['target']==t for x in later),
                evidence=ref(cid+'-source.json',f'/values (decoded positions {t-2},{t-1}; originals {ords[offset]},{ords[offset+1]})')))
    disposition='NOT_RECORDED'
    if current:
        if current['feedback']=='DEAD_KEY_REJECTED':disposition='FEEDBACK_REJECTED_DEAD_KEY'
        elif current['feedback']=='CENSORED':disposition='CENSORED'
        elif not later:disposition='ACCEPTED_NO_FURTHER_ELIGIBLE_RETRIEVAL'
        else:disposition='ACCEPTED_LATER_RETRIEVAL'
    return dict(arm=arm,original_ordinals=ords,offset=offset,original_successor=ords[offset+2],
        input_positions=ords,admission_positions=[o+1 if o%2 else o for o in ords],formation=formation,
        first_eligible_forecast=first,current=current,previous_eligible_forecasts=before,next_eligible_forecast=None if not later else later[0],
        appearances=appearances,key_changes=changes,removal=removal,present_at_last_admission=present,
        end='STORY_END_AFTER_80' if present else None,cleanup_verified=data['cleanup'],
        later_value_equal_hints=matches,diagnosis=disposition,
        cold_at_target_cause='NO_PRIOR_ELIGIBLE_FEEDBACK_OPPORTUNITY' if current and current['cold'] and not before else 'SEE_CHAIN',
        future_hint_scope='Read-only value comparison; missing original means NOT a live eligible retrieval',
        cell_evidence_scope='Accepted update is directly recorded. Promotion cell preservation is certified by saved reference_equal and frozen code, not a separate post-promotion cell dump.')


def main():
    seal=read(RUN/'closure.json');assert seal['status']=='COMPLETE'
    before={p.name:sha(p) for p in RUN.iterdir() if p.is_file()}
    for n,v in seal['files'].items():assert before[n]==v['sha256']
    archive={n:read(RUN/n) for n in before if n.endswith('.json')}
    records=[]
    for entry in archive['manifest.json']['entries']:
        cid=entry['id']
        if not cid.startswith('T1-'):continue
        report=archive[cid+'-assessment.json']
        for ri,row in enumerate(report['rows']):
            for relation,arm in (('gained','K1'),('lost','U')):
                for hi,h in enumerate(row[relation]):
                    target=row['target'];ords=h['ordinals'];offset=h['offset']
                    ch=chain(cid,arm,ords,offset,target,archive)
                    other='U' if arm=='K1' else 'K1'
                    counterpart=chain(cid,other,ords,offset,target,archive)
                    assert ch['current'] and ch['current']['cold'] and ch['current']['key']==h['key']
                    records.append(dict(case=cid,relation=relation,target=target,original_trace_id=f'{cid}:{ords}',
                        lineage_id=f'{cid}:{ords}:{offset}',observed_key=h['key'],modal_match=h['modal_match'],actual_match=h['actual_match'],
                        evidence=ref(cid+'-assessment.json',f'/rows/{ri}/{relation}/{hi}'),chain=ch,counterpart=counterpart))
    gained=[r for r in records if r['relation']=='gained'];lost=[r for r in records if r['relation']=='lost']
    assert len(gained)==31 and len(lost)==5
    assert all(not r['chain']['previous_eligible_forecasts'] for r in gained)
    assert all(r['chain']['next_eligible_forecast'] is None for r in gained)
    contrasts=[dict(case=cid,target=t,chain=chain(cid,arm,ords,0,t,archive),
        counterpart=chain(cid,'U' if arm=='K1' else 'K1',ords,0,t,archive))
        for cid,t,arm,ords in [('F1',19,'K1',[1,2,3,4]),('F2',23,'U',[5,6,7,8])]]
    summary=dict(gained_occurrences=31,lost_occurrences=5,
        gained_unique_original_traces=len({r['original_trace_id'] for r in gained}),
        gained_unique_trace_offset_lineages=len({r['lineage_id'] for r in gained}),
        gained_unique_observed_keys=len({(r['case'],*r['observed_key']) for r in gained}),
        cold_causes=dict(Counter(r['chain']['cold_at_target_cause'] for r in gained)),
        feedback=dict(Counter(r['chain']['current']['feedback'] for r in gained)),
        primary_downstream=dict(Counter(r['chain']['diagnosis'] for r in gained)),
        loss_kinds=dict(Counter(r['chain']['removal']['kind'] if r['chain']['removal'] else 'STORY_END' for r in gained)),
        future_value_matches=dict(Counter(('ACCEPTED' if r['chain']['current']['feedback']=='ACCEPTED' else 'REJECTED')+
            ('_WITH_LATER_VALUE_MATCH' if r['chain']['later_value_equal_hints'] else '_NO_LATER_VALUE_MATCH') for r in gained)),
        lost_feedback=dict(Counter(r['chain']['current']['feedback'] for r in lost)),
        lost_later_eligible=sum(r['chain']['next_eligible_forecast'] is not None for r in lost),
        lost_original_ever_admitted_in_K1=sum(r['counterpart']['formation'] is not None for r in lost),
        research_replays=0,new_sources=0,archive_sha256=before['closure.json'])
    OUT.mkdir(exist_ok=False)
    save(OUT/'occurrences.json',records);save(OUT/'contrasts.json',contrasts);save(OUT/'summary.json',summary)
    fields=['relation','case','target','original_ordinals','offset','observed_key','formation','first_forecast','feedback','removal','promotions','next_eligible','later_value_equal_hints','cold_cause','downstream_cause','evidence','feedback_evidence','lifecycle_evidence']
    with (OUT/'mapping.csv').open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in records:
            ch=r['chain'];w.writerow(dict(relation=r['relation'],case=r['case'],target=r['target'],original_ordinals=json.dumps(ch['original_ordinals']),offset=ch['offset'],observed_key=json.dumps(r['observed_key']),formation=ch['formation']['index'],first_forecast=ch['first_eligible_forecast']['target'],feedback=ch['current']['feedback'],removal=ch['removal']['index'] if ch['removal'] else 'STORY_END',promotions=json.dumps([e for e in ch['key_changes'] if e['kind']=='PROMOTED_SAME_ORIGINAL']),next_eligible=None if ch['next_eligible_forecast'] is None else ch['next_eligible_forecast']['target'],later_value_equal_hints=json.dumps([x['target'] for x in ch['later_value_equal_hints']]),cold_cause=ch['cold_at_target_cause'],downstream_cause=ch['diagnosis'],evidence=r['evidence'],feedback_evidence=ch['current']['feedback_ref'],lifecycle_evidence=json.dumps([e['event_ref'] for e in ch['key_changes']])))
    assert before=={p.name:sha(p) for p in RUN.iterdir() if p.is_file()}
    save(OUT/'verification.json',dict(archive_unchanged=True,all_sealed_files_verified=True,
        script_sha256=sha(Path(__file__)),records=36,all_31_cold_and_first_eligible=True,
        all_31_no_later_actual_eligible_same_original_offset=True,no_policy_imports=True,no_replays=True))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
