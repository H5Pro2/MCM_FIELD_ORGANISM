"""Full bound P2 replay; E/F classes and confirmation remain untouched."""
from fractions import Fraction
import hashlib
import json
import math
import sys
import tracemalloc
from tools._s2uc_record_codec import loads
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools._s2uc_factor_hint import FactorHintArm
from tools.s2uc_factor_hint_check import HintMeter
from tools.s2uc_k2_check import ROOT,state,candidates,tu

OUT=ROOT/'reports/s2uc/factor-transfer-20260930-01'
SOURCE=ROOT/'reports/s2uc/p2-supplier-correction-20260930-01/final/retained-success'


def variants(values):
    half=tuple(tuple(math.ldexp(x,-1) for x in f) for f in values)
    double=tuple(tuple(math.ldexp(x,1) for x in f) for f in values)
    return dict(original=values,half=half,double=double,reverse=values[::-1],local=(half[0],values[1]))


def independent_matches(arm,hint):
    """Exact rational arithmetic, independent of the ldexp matcher."""
    result=[]
    sources=[('retained',t.generation,t.frames) for t in arm._retained_many]
    sources += [('candidate',c.candidate_generation,c.frames) for c in candidates(arm)]
    for role,generation,frames in sources:
        for offset in range(3):
            factors=[]
            for f in (Fraction(1,2),Fraction(1),Fraction(2)):
                if all(Fraction.from_float(frames[offset+j].values[b])*f==Fraction.from_float(hint[j][b])
                       for j in range(2) for b in range(48)):
                    factors.append(float(f))
            if factors:
                result.append(dict(role=role,generation=generation,formation=frames[0].segment,
                                   ordinals=[f.ordinal for f in frames],offset=offset,factors=factors))
    return result


def target_kind(matches,variant,target):
    if not matches:return 'NO_MATCH'
    if len(matches)>1:return 'AMBIGUOUS'
    if variant in ('reverse','local'):return 'UNIQUE_CONTROL_ORIGIN_UNASSIGNED'
    match=matches[0]
    correct=match['offset']==target['position'] and any(match['formation']==x['formation'] and match['ordinals']==x['ordinals'] for x in target['origins'])
    return ('TARGET_' if correct else 'OTHER_')+match['role'].upper()


def classify(e,f,kind):
    return dict(additional_access=not e and len(f)==1,
                correct_target_gain=not e and len(f)==1 and kind.startswith('TARGET_'),
                other_origin_gain=not e and len(f)==1 and kind.startswith('OTHER_'),
                lost_uniqueness=len(e)==1 and len(f)>1,
                new_competition=not e and len(f)>1)


def run():
    raw=(OUT/'preregistration.json').read_bytes();p=json.loads(raw)
    assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==sha for f,sha in p['bindings'].items())
    record=loads((SOURCE/'product/record.json').read_bytes())
    assert [s['story'] for s in record['stories']]==['g1','g2','g3']
    assert all(s['status']=='COMPLETE' and s['completed']==len(s['events']) for s in record['stories'])
    events=[e for s in record['stories'] for e in s['events']]
    assert len(events)==69 and sum(e['kind']=='FORMATION' for e in events)==44 and sum(e['kind']=='HINT' for e in events)==14
    vectors=[tuple(float.fromhex(x) for x in e['values_hex']) for e in events if e['kind']!='CLOSE']
    checks={'shape':all(len(f)==48 for f in vectors),'finite_nonnegative':all(math.isfinite(x) and x>=0 for f in vectors for x in f),
            'all_frames_different_bands':all(len(set(f))>1 for f in vectors),
            'safe_scaling':all(x==0 or (math.ldexp(x,-1)>=sys.float_info.min and math.isfinite(math.ldexp(x,1)) and math.ldexp(math.ldexp(x,-1),1)==x and math.ldexp(math.ldexp(x,1),-1)==x) for f in vectors for x in f)}
    report=dict(preregistration_sha256=hashlib.sha256(raw).hexdigest(),preconditions=checks,cases=[],transitions=[],invariants={},resources={})
    if not all(checks.values()):
        report['status']='UNSUITABLE_NO_REPLAY'
    else:
        report['status']='EVALUATED_BOUND_SYNTHETIC_P2_VECTORS'
        meters={name:HintMeter() for name in ('E','F','no_hint')}
        counters=dict(E_subset_F=0,F_exact_rational_oracle=0,repeats_equal=0,read_only_pairs=0,shared_state_checks=0,close_transitions=0)
        tracemalloc.start()
        for story_index,story in enumerate(record['stories']):
            profile=story['events'][0]['materialization']['projection_binding']['profile_digest']
            arms={'E':ProvisionalHintArm(profile,story['story']+'/E'),'F':FactorHintArm(profile,story['story']+'/F'),
                  'no_hint':ProvisionalHintArm(profile,story['story']+'/no_hint')}
            pending=[]
            for event_index,event in enumerate(story['events']):
                if event['kind']!='CLOSE':
                    assert event['materialization']['projection_binding']['profile_digest']==profile
                if event['kind']!='HINT':
                    results=[]
                    for name,arm in arms.items():
                        if event['kind']=='CLOSE':result=meters[name].call(arm,'close_segment',event['segment'])
                        else:
                            frame=tu.Frame(tuple(float.fromhex(x) for x in event['values_hex']),profile,arm.owner,event['segment'],event['ordinal'])
                            result=meters[name].call(arm,'form',frame)
                        results.append(result)
                    assert results[0]==results[1]==results[2]
                    assert state(arms['E'])==state(arms['F'])==state(arms['no_hint'])
                    counters['shared_state_checks']+=1
                    if event['kind']=='CLOSE':
                        counters['close_transitions']+=1
                        report['transitions'].append(dict(story=story['story'],ordinal=event['ordinal'],receipt=results[0]))
                    continue
                pending.append((event_index,event))
                if len(pending)<2:continue
                key=f"{story['story']}/{event['ordinal']}"
                pair=tuple(tuple(float.fromhex(x) for x in e['values_hex']) for _,e in pending)
                parents=[dict(event_path=f'/record/stories/{story_index}/events/{i}',ordinal=e['ordinal'],source_id=e['source_id'],
                              projection_digest=e['materialization']['projection_digest'],pcm_sha256=e['materialization']['pcm_sha256']) for i,e in pending]
                for variant,values in variants(pair).items():
                    row=dict(key=key,variant=variant,target=p['targets'][key] if variant not in ('reverse','local') else None,
                             data_kind='STORED_HINT_VALUES' if variant=='original' else 'POSTHOC_VECTOR_TEST',
                             parents=parents,values_hex=[[x.hex() for x in f] for f in values],arms={})
                    assert state(arms['E'])==state(arms['F'])==state(arms['no_hint'])
                    for name in ('E','F'):
                        arm=arms[name];outputs=[]
                        for repeat in range(2):
                            before=state(arm)
                            meters[name].hint_positions+=3*(len(candidates(arm))+len(arm._retained_many))
                            for j,vector in enumerate(values):
                                result=meters[name].call(arm,'hint',tu.Frame(vector,profile,arm.owner,f'{key}/{variant}/{repeat}',10000+j))
                                if j==0:assert result is None
                            assert state(arm)==before
                            counters['read_only_pairs']+=1
                            matched=[dict(m,**({'factors':[1.]} if name=='E' else {})) for m in result['matches']]
                            expected_decision=('ABSTAIN_NO_MATCH' if not matched else 'ABSTAIN_AMBIGUOUS' if len(matched)>1
                                               else 'CONFIRMED_RETAINED_MATCH' if matched[0]['role']=='retained' else 'PROVISIONAL_CANDIDATE_MATCH')
                            assert result['decision']==expected_decision
                            outputs.append(dict(decision=result['decision'],matches=matched))
                        assert outputs[0]==outputs[1];counters['repeats_equal']+=1
                        row['arms'][name]=dict(**outputs[0],repeat_equal=True,
                            target_classification=target_kind(outputs[0]['matches'],variant,p['targets'][key]))
                    em=row['arms']['E']['matches'];fm=row['arms']['F']['matches']
                    assert all(any({k:v for k,v in e.items() if k!='factors'}=={k:v for k,v in f.items() if k!='factors'} and 1. in f['factors'] for f in fm) for e in em)
                    counters['E_subset_F']+=1
                    assert fm==independent_matches(arms['F'],values);counters['F_exact_rational_oracle']+=1
                    row['comparison']=classify(em,fm,row['arms']['F']['target_classification'])
                    report['cases'].append(row)
                    assert state(arms['E'])==state(arms['F'])==state(arms['no_hint'])
                    counters['shared_state_checks']+=1
                pending=[]
            assert not pending
            for arm in arms.values():
                arm.close_owner();assert all(v==0 for v in arm.resources().values())
        assert len(report['cases'])==35
        for name,m in meters.items():
            assert m.peak_trace<=16 and m.peak_hint<=2 and m.peak_total<=18
            report['resources'][name]=m.summary()
        tracemalloc.stop()
        report['invariants']=counters
    report['bindings_unchanged']=all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==sha for f,sha in p['bindings'].items())
    report['notes']=['Stored NU identities with synthetic replacement PCM; not original-source production.',
       'Parent production hashes describe stored parents only. Derived hints have no new PCM/NJ production claim.',
       'Cases share data/history, not statistically independent observations.',
       'Independent oracle uses exact rational arithmetic, not factor matcher helpers.',
       'Reference, factor and no-hint control use distinct owners but identical non-hint events.',
       'Allocation peaks include observer/tracing; not process RAM. No new runtime storage banks.']
    with (OUT/'result.json').open('x') as f:json.dump(report,f,indent=2)
    print(report['status'],report['invariants'])
    return report


if __name__=='__main__':run()
