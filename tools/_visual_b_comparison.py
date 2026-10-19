"""Fixed B comparison with unchanged A resolution; no memory advancement."""
from types import SimpleNamespace
from tools import _visual_b_diagnostic as d
from tools import _visual_b_frozen as frozen

VERSION='visual-b.frozen-comparison.v1'
MAIN_GATE=False


def a_primary(q,candidates):
    scans=[];matches=[]
    cue=SimpleNamespace(values=tuple(q)+(None,)*256,cue_digest=frozen.digest(q),
                        mask_plan_digest=d.historical.MASK_PLAN_DIGEST)
    for name,role,capacity in (('B4','B4_RECENT',9),('FAST','TSPM_FAST',3)):
        rows=[];hits=[]
        for slot in (c for c in candidates if c['bank']==name):
            record,match=d.historical._slot_record(bank_role=role,slot_id=slot['slot_id'],
                slot_digest=slot['slot_digest'],values=tuple(slot['values']) if slot['occupied'] else None,
                support=slot['support'],cue=cue)
            rows.append(record)
            if match is not None:hits.append(match)
        scan,hit=d.historical._finish_bank(role,capacity,rows,hits)
        scans.append(scan);matches.append(hit)
    finding,count=d.resolve_a(scans[0],matches[0],scans[1],matches[1])
    return dict(status=finding.status,count=finding.public_candidate_count,
                slot_digests=list(finding.provenance_slot_digests),
                internal_comparisons=count,scans=[dict(status=s.status,
                    rows=[dict(slot=r.slot_id,matched=r.observed_match,eligible=r.eligible)
                          for r in s.records]) for s in scans])


def a_direct(q,candidates):
    hits=[];scans=[]
    for bank in ('B4','FAST'):
        selected=[];rows=[]
        for slot in candidates:
            if slot['bank']!=bank:continue
            matched=slot['occupied']
            if matched:
                for i in range(32):
                    if q[i]!=slot['values'][i]:matched=False
            rows.append(dict(slot=slot['slot_id'],matched=matched,eligible=slot['occupied']))
            if matched:selected.append(slot)
        status=('BANK_MULTIPLE_OBSERVED_MATCHES' if len(selected)>1 else
                'BANK_UNIQUE_OBSERVED_MATCH' if selected else
                'BANK_NO_OBSERVED_MATCH' if any(r['eligible'] for r in rows) else 'BANK_ABSENT_VALID')
        scans.append(dict(status=status,rows=rows));hits.append(selected)
    count=0;selected=[]
    if any(len(h)>1 for h in hits):status='A_RECENT_INTERNAL_AMBIGUITY'
    elif all(len(h)==1 for h in hits):
        count=288
        same=all(hits[0][0]['values'][i]==hits[1][0]['values'][i] for i in range(288))
        # Preserve the historical digest condition, including signed-zero distinctions.
        same= same and frozen.digest(hits[0][0]['values'])==frozen.digest(hits[1][0]['values'])
        status='A_RECENT_APPLICABLE' if same else 'A_RECENT_INTERNAL_CONFLICT'
        if same:selected=hits[0]+hits[1]
    elif any(hits):status='A_RECENT_APPLICABLE';selected=hits[0]+hits[1]
    elif all(s['status']=='BANK_ABSENT_VALID' for s in scans):status='A_RECENT_ABSENT_VALID'
    else:status='A_RECENT_NOT_APPLICABLE'
    return dict(status=status,count=int(bool(selected)),slot_digests=[c['slot_digest'] for c in selected],
                internal_comparisons=count,scans=scans)


def compare(q,binding,*,direct=False):
    frozen.require(binding['binding_digest']==frozen.digest({k:v for k,v in binding.items() if k!='binding_digest'}),'BINDING_DIGEST')
    cs=binding['candidates'];b=[c for c in cs if c['bank']=='B']
    slots=[dict(occupied=c['occupied'],support=c['support'],values=tuple(c['values'])) for c in b]
    a=(a_direct if direct else a_primary)(q,cs)
    results=[]
    for rule in ('EXACT','MAX32_RGB8_STEP'):
        scan=(d.direct if direct else d.scan)(tuple(q),slots,rule)
        matches=scan['matches'];eligible=any(r['eligible'] for r in scan['rows'])
        status=('B_STABLE_INTERNAL_AMBIGUITY' if len(matches)>1 else 'B_STABLE_APPLICABLE'
                if matches else 'B_STABLE_NOT_APPLICABLE' if eligible else 'B_STABLE_ABSENT_VALID')
        if direct:
            if a['status']=='A_RECENT_INTERNAL_AMBIGUITY' or len(matches)>1:decision,area='ABSTAIN_INTERNAL_AMBIGUITY',None
            elif a['status']=='A_RECENT_INTERNAL_CONFLICT':decision,area='ABSTAIN_INTERNAL_CONFLICT',None
            elif a['count']+int(len(matches)==1)==2:decision,area='ABSTAIN_AMBIGUOUS_CONTEXT',None
            elif a['count']+int(len(matches)==1)==1:decision,area='ADMIT_SINGLE_CONTEXT','A_RECENT' if a['count'] else 'B_STABLE'
            elif a['status']=='A_RECENT_ABSENT_VALID' and status=='B_STABLE_ABSENT_VALID':decision,area='ABSTAIN_NO_CONTEXT',None
            else:decision,area='ABSTAIN_NO_APPLICABLE_CONTEXT',None
        else:
            decision,area=d.decide(SimpleNamespace(status=a['status'],public_candidate_count=a['count']),
                                  SimpleNamespace(status=status,public_candidate_count=int(len(matches)==1)))
        results.append(dict(rule=rule,scan=scan,b_status=status,decision=decision,area=area,
            b_generations=[dict(slot=b[i]['slot_id'],generation=b[i]['generation'],
                                slot_digest=b[i]['slot_digest']) for i in matches]))
    return dict(a=a,b=results)


def verify(record,source,binding):
    frozen.require(record.get('version')==VERSION,'RECORD_VERSION')
    failed=record['status']=='NOT_EVALUABLE'
    if failed:
        frozen.require(record['binding']==binding['binding_digest'] and
            0<=len(record['rows'])<7 and record['phase'] in ('MATERIALIZE','COMPARE'),'FAILURE_FORM')
    else:
        frozen.require(record['status']=='RECORDING_COMPLETE' and record['binding']==binding['binding_digest'],'RECORD_BINDING')
        frozen.require(len(record['rows'])==len(source['rows'])==7,'RECORD_COUNT')
    if 'analyses' in record:
        frozen.require(type(record['analyses']) is int and
            (record['analyses'] in (len(record['rows']),len(record['rows'])+1) if failed
             else record['analyses']==7),'ANALYSIS_COUNT')
    for item,expected in zip(record['rows'],source['rows'][:len(record['rows'])],strict=True):
        frozen.require(item['source_digest']==frozen.digest(expected),'CUE_SOURCE')
        frozen.require(item['window']==expected['window'] and item['indices']==list(range(32)),'CUE_WINDOW')
        q=item['values']
        frozen.require(type(q) is list and len(q)==32,'CUE_FORM')
        calculated=compare(q,binding,direct=True)
        frozen.require(item['primary']==item['direct']==calculated,'COMPARISON_INVALID')
    terms=sum(len(bank['scan']['rows'][i]['terms']) for row in record['rows']
        for arm in ('primary','direct') for bank in row[arm]['b'] for i in range(4))
    return dict(status='NOT_EVALUABLE' if failed else 'VERIFIED',evaluation_allowed=not failed,
                record_digest=frozen.digest(record),receptor_repeated=False,
                stored_b_slot_records=16*len(record['rows']),stored_band_terms=terms,
                verification_b_slot_checks=8*len(record['rows']),verification_band_terms=terms//2)


def record_steps(source,binding,materialize):
    frozen.require(len(source['rows'])==7,'SOURCE_COUNT')
    rows=[];phase='MATERIALIZE'
    try:
        for expected in source['rows']:
            phase='MATERIALIZE'
            q=tuple(materialize(expected))
            phase='COMPARE'
            primary=compare(q,binding)
            direct=compare(q,binding,direct=True)
            frozen.require(primary==direct,'BASELINE')
            item=dict(source_digest=frozen.digest(expected),window=expected['window'],
                indices=list(range(32)),values=list(q),primary=primary,direct=direct)
            frozen.require(len(d.source.raw(item))<=32767,'ITEM_LIMIT')
            rows.append(item)
        return dict(version=VERSION,status='RECORDING_COMPLETE',binding=binding['binding_digest'],rows=rows)
    except Exception as exc:
        return dict(version=VERSION,status='NOT_EVALUABLE',binding=binding['binding_digest'],rows=rows,
                    phase=phase,error_type=type(exc).__name__[:80],error=str(exc)[:256])


def evaluate(record,proof,evaluation,source):
    frozen.require(proof.get('evaluation_allowed') is True and
                   proof['record_digest']==frozen.digest(record),'EVALUATION_GATE')
    rows=[]
    for i,(item,role,target) in enumerate(zip(record['rows'],evaluation['roles'],evaluation['target'],strict=True)):
        old,new=item['primary']['b']
        # Target refers solely to the prospectively fixed visual B slot 000.
        old_hit=0 in old['scan']['matches'];new_hit=0 in new['scan']['matches']
        rows.append(dict(id=source['rows'][i]['id'],role=role,target_expected=target,
            relationship=d.classify(old_hit,new_hit,target),
            historical_target_applicable=old_hit,alternative_target_applicable=new_hit,
            public_historical=dict(decision=old['decision'],area=old['area']),
            public_alternative=dict(decision=new['decision'],area=new['area']),
            public_target_retained=(target and old['area']=='B_STABLE' and old_hit and
                                    new['area']=='B_STABLE' and new_hit),
            public_historical_target=bool(target and old['area']=='B_STABLE' and old_hit),
            public_alternative_target=bool(target and new['area']=='B_STABLE' and new_hit),
            public_gain=bool(target and new['area']=='B_STABLE' and new_hit and old['area']!='B_STABLE'),
            public_target_lost=(target and old['area']=='B_STABLE' and old_hit and new['area']!='B_STABLE'),
            public_new_false=(not target and new['area'] is not None and old['area'] is None),
            public_false_historical=bool(not target and old['area'] is not None),
            public_false_alternative=bool(not target and new['area'] is not None),
            a_admission_unassigned_to_b_target=old['area']=='A_RECENT' or new['area']=='A_RECENT',
            b_ambiguity=[old['b_status'],new['b_status']]))
    groups=[]
    for role in dict.fromkeys(evaluation['roles']):
        selected=[r for r in rows if r['role']==role]
        denominator=sum(r['target_expected'] and r['historical_target_applicable'] for r in selected)
        public_d=sum(r['public_historical_target'] for r in selected)
        groups.append(dict(role=role,N=len(selected),D=denominator,
            R=sum(r['relationship']['retained'] for r in selected),L=sum(r['relationship']['lost'] for r in selected),
            preservation='ERHALTUNG_NICHT_GEPRUEFT' if denominator==0 else 'DESCRIPTIVE',
            new_false=sum(r['relationship']['new_false'] for r in selected),
            gains=sum(r['relationship']['gained'] for r in selected),
            public=dict(N=len(selected),D=public_d,R=sum(r['public_target_retained'] for r in selected),
                L=sum(r['public_target_lost'] for r in selected),G=sum(r['public_gain'] for r in selected),
                new_false=sum(r['public_new_false'] for r in selected),
                preservation='ERHALTUNG_NICHT_GEPRUEFT' if public_d==0 else 'DESCRIPTIVE')))
    return dict(status='DESCRIPTIVE_ONLY',rows=rows,groups=groups,
        byte_identical_not_independent=True,independent_replication_count=None,
        public_target_definition='ADMIT B_STABLE with the bound target generation; A admissions listed separately',
        identity_or_robustness_not_demonstrated=True)
