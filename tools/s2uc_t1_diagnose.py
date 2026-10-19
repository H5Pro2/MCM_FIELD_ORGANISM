"""Read-only diagnosis of sealed T1 evidence; stdlib only, no replay imports."""
import base64
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'reports/s2uc/t1-transfer-20261003-02'
OUT = ROOT / 'reports/s2uc/t1-cause-analysis-20261003-01'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def items(stock):
    return [(0, x) for x in stock['retained']] + ([] if stock['candidate'] is None else [(1, stock['candidate'])])


def same_key(match):
    return [dict(retained=0, candidate=1).get(match['role'], match['role']), match['generation'], match['offset']]


def main():
    seal = read(RUN/'closure.json')
    assert seal['status'] == 'COMPLETE'
    for name, record in seal['files'].items():
        assert sha(RUN/name) == record['sha256']
    before = {x.name: sha(x) for x in RUN.iterdir() if x.is_file()}
    manifest = read(RUN/'manifest.json')
    targets, transitions, lifecycle, sources = [], [], [], []
    for entry in manifest['entries']:
        cid = entry['id']
        spec = entry['spec']
        if not any(not x['negative_control'] for x in spec['phases'][1:]):
            continue
        raw = read(RUN/entry['source_file'])
        flat = struct.unpack('<' + 'd' * (raw['frames']*48), base64.b64decode(raw['data'], validate=True))
        values = [tuple(flat[i:i+48]) for i in range(0, len(flat), 48)]
        provenance = read(RUN/entry['provenance_file'])
        report = read(RUN/(cid+'-assessment.json'))
        u = read(RUN/(cid+'-U.json'))
        m = read(RUN/(cid+'-M.json'))
        assert not report['technical_errors'] and u['states'] == m['state_hashes']
        events = {x['frame']: x for x in m['admissions']}
        forecasts = {x['input_indices'][-1]+1:x for x in u['forecasts']}
        decisions = {x['target']:x for x in report['decisions']}
        changes = []
        for frame, event in events.items():
            before_items, after_items = items(event['before']), items(event['after'])
            for role, trace in before_items:
                after = [(r,x) for r,x in after_items if x['ordinals'] == trace['ordinals']]
                if after and role == 1 and after[0][0] == 0:
                    kind = 'PROMOTION_PRESERVES_ORIGINAL_CHANGES_KEY'
                elif after:
                    continue
                else:
                    kind = 'CANDIDATE_REPLACEMENT' if role == 1 else 'RETAINED_EVICTION'
                change = dict(case=cid, frame=frame, kind=kind, original_ordinals=trace['ordinals'],
                    old_key_prefix=[role,trace['generation']], new_key_prefix=None if not after else [after[0][0],after[0][1]['generation']],
                    evidence=f'{cid}-M.json:admissions[frame={frame}].before/after',
                    classification='DETERMINISTIC_STATE_DIFFERENCE_NOT_LOGGED_ACTION_LABEL')
                changes.append(change)
        lifecycle.extend(changes)
        for phase_number, phase in enumerate(spec['phases'][1:], 1):
            if phase['negative_control']:
                continue
            ts = phase['targets']
            transition = dict(case=cid, phase=phase_number, classification='POTENZIELL_PRUEFBARER_UEBERGANG',
                start=phase['start'], end=phase['end'], mode=phase['mode'], targets=ts,
                count=len(ts), deadline_target=None if not ts else ts[min(3,len(ts))-1],
                fewer_than_two_scoring_opportunities=len(ts)<2, passed=False)
            transitions.append(transition)
            for rank, t in enumerate(ts, 1):
                cut = t-3  # stock before both current hint frames are admitted
                hint = values[t-3:t-1]
                stock = events[t-2]['before']
                f, d = forecasts[t], decisions[t]
                mode, bank = provenance['modes'][t-1], provenance['banks'][t-1]
                modal_state = (provenance['states'][t-2] + (1 if mode=='C' else -1)) % 8
                modal = tuple(provenance['library'][bank][modal_state])
                actual = values[t-1]
                history = []
                # Exclude the current hint itself; retain overlapping earlier pairs separately.
                for j in range(1, t-2):
                    if values[j-1:j+1] != hint:
                        continue
                    block_start = ((j-1)//4)*4+1
                    ordinals = list(range(block_start, block_start+4))
                    block_end = block_start+3
                    pair_segmented = (j-1)//4 != j//4
                    successor_segmented = (j-1)//4 != (j+1)//4
                    observed_successor = j+2 <= t-1
                    admitted_successor = j+2 <= cut
                    relevant = [x for x in changes if x['original_ordinals']==ordinals and x['frame']<=cut]
                    live_original = [(r,x) for r,x in items(stock) if x['ordinals']==ordinals]
                    ever_original = any(x['ordinals']==ordinals for frame,event in events.items() if frame<=cut for r,x in items(event['after']))
                    flags=[]
                    if j+1>cut:flags.append('PRIOR_PAIR_OVERLAPS_CURRENT_HINT_NOT_ADMITTED')
                    if pair_segmented:flags.append('PAIR_CROSSES_SEGMENT_BOUNDARY')
                    elif successor_segmented:flags.append('SUCCESSOR_OUTSIDE_TRACE_OFFSET2')
                    if block_end>cut:flags.append('SEGMENT_NOT_COMPLETE_AT_RETRIEVAL')
                    if not pair_segmented and not live_original:
                        flags.extend(x['kind'] for x in relevant if x['kind']!='PROMOTION_PRESERVES_ORIGINAL_CHANGES_KEY')
                        if block_end<=cut and not ever_original:
                            flags.append('ORIGINAL_NOT_INSERTED_CONFIRMATION_USES_OTHER_ORIGINAL')
                    history.append(dict(pair=[j,j+1], successor=j+2 if observed_successor else None,
                        fully_admitted=j+1<=cut, successor_admitted=admitted_successor,
                        successor_matches_modal=None if not admitted_successor else values[j+1]==modal,
                        successor_matches_actual=None if not admitted_successor else values[j+1]==actual,
                        trace_ordinals=ordinals, trace_closed_at=block_end,
                        exact_original_live=bool(live_original) and not pair_segmented,
                        container_trace_live=bool(live_original), original_ever_inserted=ever_original,
                        diagnostics=sorted(set(flags)), lifecycle=relevant))
                matches=[]
                for role, trace in items(stock):
                    ords=trace['ordinals']
                    for off in range(3):
                        if [values[ords[off]-1],values[ords[off+1]-1]]==hint:
                            matches.append(dict(key=[role,trace['generation'],off],ordinals=ords,eligible=off<2,
                                successor=None if off==2 else ords[off+2],
                                successor_matches_modal=None if off==2 else values[ords[off+2]-1]==modal,
                                successor_matches_actual=None if off==2 else values[ords[off+2]-1]==actual))
                assert sorted(x['key'] for x in matches)==sorted(same_key(x) for x in f['matches'])
                hypotheses=[]
                for h in d['hypotheses']:
                    corresponding=next(x for x in matches if x['key']==h['key'])
                    hypotheses.append(dict(**corresponding, prior_feedback=h['prior_feedback'],
                        phase_prior_feedback=[x for x in h['prior_feedback'] if phase['start']<=x<t],
                        before=h['before'], strict_estimated_advantage=h['before'] is not None and h['before'][0]<h['before'][1],
                        live_at_feedback=h['live_at_feedback'], after=h['after'],
                        loss_between_prediction_and_feedback=[x for x in changes if cut<x['frame']<t and x['original_ordinals']==h['original_ordinals']]))
                assert len(hypotheses)==d['eligible']
                admitted=[x for x in history if x['fully_admitted']]
                flags=[]
                if not admitted:flags.append('NO_PRIOR_ADMITTED_EXACT_PAIR')
                if admitted and not matches:flags.append('HISTORY_EXISTS_BUT_NO_LIVE_MATCH')
                if matches and not hypotheses:flags.append('LIVE_MATCH_WITHOUT_ELIGIBLE_SUCCESSOR')
                if hypotheses and not any(h['prior_feedback'] for h in hypotheses):flags.append('NO_PRIOR_FEEDBACK_FOR_ELIGIBLE_KEYS')
                if hypotheses and not any(h['phase_prior_feedback'] for h in hypotheses):flags.append('NO_PHASE_FEEDBACK_FOR_ELIGIBLE_KEYS')
                if hypotheses and not any(h['strict_estimated_advantage'] for h in hypotheses):flags.append('NO_STRICT_ESTIMATED_ADVANTAGE')
                if not any(h['successor_matches_modal'] for h in hypotheses):flags.append('NO_LIVE_MODAL_SUCCESSOR')
                if not any(h['successor_matches_actual'] for h in hypotheses):flags.append('NO_LIVE_ACTUAL_SUCCESSOR')
                if rank==1:flags.append('NO_EARLIER_FULLY_IN_PHASE_HINT_TARGET')
                if len(ts)<2:flags.append('SHORT_PHASE_FEWER_THAN_TWO_FULLY_IN_PHASE_HINT_TARGETS')
                first=('NO_PRIOR_ADMITTED_EXACT_PAIR' if not admitted else 'NO_LIVE_MATCH' if not matches else
                       'NO_ELIGIBLE_SUCCESSOR' if not hypotheses else 'NO_PRIOR_FEEDBACK' if not any(h['prior_feedback'] for h in hypotheses) else
                       'NO_STRICT_ADVANTAGE' if not any(h['strict_estimated_advantage'] for h in hypotheses) else 'CHAIN_AVAILABLE')
                targets.append(dict(case=cid,phase=phase_number,target=t,hint_ordinals=[t-2,t-1],
                    admitted_through=cut, phase_target_rank=rank, phase_target_count=len(ts),
                    earlier_phase_G_targets=[z for z in spec['masks']['G'] if phase['start']<=z<t],
                    earlier_phase_T_targets=[z for z in ts if z<t],
                    modal_state=modal_state, actual_state=provenance['states'][t-1],modal_equals_actual=modal==actual,
                    history=history,stock=stock,matches=matches,hypotheses=hypotheses,
                    first_observed_break=first, obstacles=flags,decision=d['reason'],
                    historical_occurrence_diagnostics=sorted({z for x in history for z in x['diagnostics']}),
                    source_refs=dict(source=entry['source_file'],provenance=entry['provenance_file'],
                        stock=f'{cid}-M.json:admissions[frame={t-2}].before',
                        forecast=f'{cid}-U.json:forecasts[input_indices={t-2},{t-1}]',
                        feedback=f'{cid}-U.json:updates[target={t}]',
                        frozen_evidence=f'{cid}-assessment.json:decisions[target={t}]'),missing_evidence=[]))
        sources.extend([entry['source_file'],entry['provenance_file'],cid+'-U.json',cid+'-M.json',cid+'-assessment.json'])
    assert len(transitions)==32 and len({(x['case'],x['target']) for x in targets})==len(targets)
    for transition in transitions:
        subset=[x for x in targets if (x['case'],x['phase'])==(transition['case'],transition['phase'])]
        transition['first_break_counts']=dict(Counter(x['first_observed_break'] for x in subset))
    def eligible_original(h):
        return h['fully_admitted'] and h['successor_admitted'] and not any(z in h['diagnostics'] for z in
            ('PAIR_CROSSES_SEGMENT_BOUNDARY','SUCCESSOR_OUTSIDE_TRACE_OFFSET2','SEGMENT_NOT_COMPLETE_AT_RETRIEVAL'))
    summary=dict(transitions=len(transitions),targets=len(targets),
        first_break_counts=dict(Counter(x['first_observed_break'] for x in targets)),
        obstacle_counts=dict(Counter(z for x in targets for z in x['obstacles'])),
        historical_diagnostic_target_counts=dict(Counter(z for x in targets for z in x['historical_occurrence_diagnostics'])),
        lifecycle_counts=dict(Counter(x['kind'] for x in lifecycle)),
        historical_pair_targets=sum(any(h['fully_admitted'] for h in x['history']) for x in targets),
        no_historical_pair_even_overlapping=sum(not x['history'] for x in targets),
        only_overlapping_not_admitted_pair_targets=sum(bool(x['history']) and not any(h['fully_admitted'] for h in x['history']) for x in targets),
        historical_eligible_original_targets=sum(any(eligible_original(h) for h in x['history']) for x in targets),
        replaced_eligible_original_targets=sum(any(eligible_original(h) and 'CANDIDATE_REPLACEMENT' in h['diagnostics'] for h in x['history']) for x in targets),
        replaced_modal_original_targets=sum(any(eligible_original(h) and h['successor_matches_modal'] and 'CANDIDATE_REPLACEMENT' in h['diagnostics'] for h in x['history']) for x in targets),
        historical_modal_triplet_targets=sum(any(h['successor_matches_modal'] for h in x['history']) for x in targets),
        live_match_targets=sum(bool(x['matches']) for x in targets),
        eligible_targets=sum(bool(x['hypotheses']) for x in targets),
        warm_targets=sum(any(h['before'] is not None for h in x['hypotheses']) for x in targets),
        modal_not_realized=sum(not x['modal_equals_actual'] for x in targets),
        short_transitions=[x for x in transitions if x['fewer_than_two_scoring_opportunities']],
        missing_evidence=[], no_policy_replays=True, no_new_sources=True,
        scope='32 potenziell pruefbare Uebergaenge; prior initial phases and I/H transitions excluded from primary denominator')
    assert before=={x.name:sha(x) for x in RUN.iterdir() if x.is_file()}
    OUT.mkdir(exist_ok=True)  # diagnostic artifacts only; sealed RUN is never written
    save(OUT/'targets.json', targets)
    save(OUT/'transitions.json', transitions)
    save(OUT/'lifecycle.json', lifecycle)
    save(OUT/'summary.json', summary)
    save(OUT/'input-binding.json',dict(files={n:sha(RUN/n) for n in sorted(set(sources+['manifest.json','closure.json']))},
        analysis_script_sha256=sha(Path(__file__)), run_unchanged=True))
    with (OUT/'target-map.csv').open('w',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream)
        writer.writerow(['case','phase','target','hint','admitted_through','historical_pairs','live_matches','eligible_successors',
            'keys_with_feedback','strict_advantage','modal_equals_actual','first_break','obstacles','historical_diagnostics','earlier_phase_G','earlier_phase_T'])
        for x in targets:
            writer.writerow([x['case'],x['phase'],x['target'],str(x['hint_ordinals']),x['admitted_through'],
                sum(h['fully_admitted'] for h in x['history']),len(x['matches']),len(x['hypotheses']),
                sum(bool(h['prior_feedback']) for h in x['hypotheses']),sum(h['strict_estimated_advantage'] for h in x['hypotheses']),
                x['modal_equals_actual'],x['first_observed_break'],';'.join(x['obstacles']),';'.join(x['historical_occurrence_diagnostics']),
                str(x['earlier_phase_G_targets']),str(x['earlier_phase_T_targets'])])
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
