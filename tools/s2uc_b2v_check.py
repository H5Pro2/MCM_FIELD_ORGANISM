"""Bounded stored-data B2/B2-V comparison. No source production."""
import hashlib
import json
from pathlib import Path
import sys

from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools._s2uc_four_arm import CandidateTwoArm, tu
from tools._s2uc_record_codec import loads
from tools.s2uc_four_arm_check import normalized, TemporaryObserver, reachable_frames


class VariantObserver(TemporaryObserver):
    def trace(self, frame, event, arg):
        if frame.f_code.co_filename not in self.files:
            return None
        found, seen = {}, set()
        cursor=frame
        while cursor is not None:
            if cursor.f_code.co_filename in self.files:
                for value in cursor.f_locals.values():
                    reachable_frames(vars(value) if isinstance(value,ProvisionalHintArm) else value,found,seen)
            cursor=cursor.f_back
        hints=sum(f.ordinal in self.hint_ordinals for f in found.values())
        self.peak_hint=max(self.peak_hint,hints)
        self.peak_trace=max(self.peak_trace,len(found)-hints)
        self.peak_total=max(self.peak_total,len(found))
        self.samples+=1
        return self.trace

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/s2uc/b2v-20260930-01'
SOURCE = ROOT/'reports/s2uc/p2-supplier-correction-20260930-01/final/retained-success/product/record.json'
MAP = {'TRACE_MATCH':'CONFIRMED_RETAINED_MATCH',
       'ABSTAIN_NO_RETAINED_TRACE':'ABSTAIN_NO_MATCH',
       'ABSTAIN_AMBIGUOUS_RETAINED_TRACE':'ABSTAIN_AMBIGUOUS'}


def state(arm):
    return normalized((arm.evidence(), arm._candidate_generation, arm._retained_generation))


def matches(arm, receipt, variant):
    if variant:
        return receipt['matches']
    return [dict(role='retained', generation=g, formation=t.frames[0].segment,
                 ordinals=[f.ordinal for f in t.frames], offset=o)
            for g,o in receipt['matches'] for t in arm._retained_many if t.generation==g]


def run():
    prereg_bytes=(OUT/'preregistration.json').read_bytes()
    prereg=json.loads(prereg_bytes)
    for path,sha in prereg['bindings'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha
    record=loads(SOURCE.read_bytes())
    history=json.loads((ROOT/'reports/s2uc/four-arm-20260930-01/result.json').read_bytes())['arms']['B2']
    events={e['ordinal']:e for s in record['stories'] for e in s['events']}
    original={h['key']:h for h in history['hints']}
    transitions={(t['story'],t['ordinal']):t['receipt'] for t in history['transitions']}
    results=[]
    owners=[]
    hint_ordinals={e['ordinal'] for e in events.values() if e['kind']=='HINT'} | set(range(1000,1100))
    observer=VariantObserver(hint_ordinals)
    observer.files.add(str((ROOT/'tools/_s2uc_provisional_hint.py').resolve()))
    # The existing observer recognizes base-module objects. Add no observer access to arms.
    peak_roles={}
    counts={'transitions':0,'original_hints':0,'read_only_pairs':0,'equal_input_frames':0}

    def call(arm, method, arg):
        sys.settrace(observer.trace)
        try:
            result=getattr(arm,method)(arg)
        finally:
            sys.settrace(None)
        for k,v in arm.resources().items():
            peak_roles[k]=max(peak_roles.get(k,0),v)
        assert arm.resources()['trace_frames']<=16 and arm.resources()['hint_frames']<=2
        return result

    for story in record['stories']:
        profile=story['events'][0]['materialization']['projection_binding']['profile_digest']
        arms=[CandidateTwoArm(profile,story['story']+'/B2'),ProvisionalHintArm(profile,story['story']+'/B2V')]
        owners.extend(a.owner for a in arms)
        pending=None
        for event in story['events']:
            ordinal=event['ordinal']; kind=event['kind']
            if kind=='HINT' and pending is None:
                pending=[state(a) for a in arms]
            receipts=[]
            for arm in arms:
                if kind=='CLOSE':
                    receipt=call(arm,'close_segment',event['segment'])
                else:
                    frame=tu.Frame(tuple(float.fromhex(x) for x in event['values_hex']),profile,arm.owner,event['segment'],ordinal)
                    receipt=call(arm,'form' if kind=='FORMATION' else 'hint',frame)
                receipts.append(receipt)
            if kind!='CLOSE':
                counts['equal_input_frames']+=1
            if kind=='CLOSE':
                assert receipts[0]==receipts[1]==transitions[(story['story'],ordinal)]
                assert state(arms[0])==state(arms[1])
                counts['transitions']+=1
            if kind=='HINT' and receipts[0] is not None:
                key=f"{story['story']}/{ordinal}"
                old=original[key]
                assert normalized(receipts[0])==normalized(old['receipt'])
                left=matches(arms[0],receipts[0],False); right=matches(arms[1],receipts[1],True)
                assert left==right
                assert all(state(a)==before for a,before in zip(arms,pending))
                prediction=receipts[1]['decision']==MAP[receipts[0]['decision']]
                results.append(dict(key=key,B2=receipts[0]['decision'],B2V=receipts[1]['decision'],matches=right,
                                    prediction='CONFIRMED' if prediction else 'VIOLATED'))
                counts['original_hints']+=1; counts['read_only_pairs']+=1
                pending=None
            for key,probe in prereg['probes'].items():
                if ordinal!=probe['after']:
                    continue
                for repeat in range(2 if key in ('P1','P2') else 1):
                    probe_id=key if repeat==0 else key+'-repeat'
                    before=[state(a) for a in arms]
                    obtained=[]
                    for index,arm in enumerate(arms):
                        receipt=None
                        for j,source_ordinal in enumerate(probe['values_ordinals']):
                            values=tuple(float.fromhex(x) for x in events[source_ordinal]['values_hex'])
                            frame=tu.Frame(values,profile,arm.owner,'probe/'+probe_id,1000+repeat*2+j)
                            receipt=call(arm,'hint',frame)
                        obtained.append(receipt)
                        assert state(arm)==before[index]
                    left=matches(arms[0],obtained[0],False); right=matches(arms[1],obtained[1],True)
                    assert left==[m for m in right if m['role']=='retained']
                    actual=[[m['role'],m['formation'],m['offset']] for m in right]
                    prediction=(obtained[0]['decision']==probe['B2'] and obtained[1]['decision']==probe['B2V'] and actual==probe['matches'])
                    results.append(dict(key=probe_id,after=ordinal,B2=obtained[0]['decision'],B2V=obtained[1]['decision'],
                                        matches=right,prediction='CONFIRMED' if prediction else 'VIOLATED'))
                    counts['read_only_pairs']+=1; counts['equal_input_frames']+=2
        for arm in arms:
            arm.close_owner()
            assert all(v==0 for v in arm.resources().values())
    assert len(set(owners))==6
    assert observer.peak_trace<=16 and observer.peak_hint<=2
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha for p,sha in prereg['bindings'].items())
    return dict(scope='NEUTRAL_STORED_SYNTHETIC_ONLY',preregistration_sha256=hashlib.sha256(prereg_bytes).hexdigest(),
                counts=counts,owners=owners,results=results,peak_roles=peak_roles,
                temporary=dict(trace=observer.peak_trace,hint=observer.peak_hint,total=observer.peak_total),
                notes=['Numeric payload is not RAM. Line-boundary Frame census reuses existing observer.',
                       'Probe ordinals 1000..1003 are local to uniquely named hint segments; historical ordinals unchanged.',
                       'No additional retained/candidate storage. Full matching sets contain provenance metadata, no value copies.'])


if __name__=='__main__':
    result=run()
    with (OUT/'result.json').open('x',encoding='utf-8') as handle:
        json.dump(result,handle,indent=2)
    print(json.dumps(result,indent=2))
