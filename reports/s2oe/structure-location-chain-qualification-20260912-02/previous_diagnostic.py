"""Offline PPB table; no media, memory advancement or retrieval calls."""
from dataclasses import asdict
import json
import math
from tools import _s2ob_private_state_evidence as wire
from tools import _s2ng_private_comparison_verification as native
from tools import _s2nl_private_half_profile_binding as profile
from mcm_field_organism import _ppb1_reference as ppb


class DiagnosticError(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise DiagnosticError(code)


def extract(wrapper, proof, common):
    record = wrapper['record']
    native.check(record, 'record_digest')
    native.check(common, 'common_digest')
    native.check(proof, 'verification_digest')
    need(proof['record_digest'] == record['record_digest'] and proof['evaluation_allowed'], 'PARENT_INVALID')
    x = record['execution']
    native.check(x, 'record_digest')
    config = profile.build_config()
    need(x['config_digest'] == config.config_digest, 'PROFILE_INVALID')
    left, row = x['rows'][2:4]
    need(left['post'] == row['pre'] and row['pre']['processed_event_count'] == 3
         and left['step']['memory_status'] == row['step']['memory_status'] == 'FORMATION_COMMITTED', 'ADJACENCY_INVALID')
    events = [native.decode_input(x['inputs'][i], config) for i in (2, 3)]
    need([(e.ordinal, e.event_id, e.event_type) for e in events] ==
         [(3, 'media-event-03', 'COMPLETE_AV_PERCEPTION'), (4, 'media-event-04', 'COMPLETE_AV_PERCEPTION')], 'EVENT_INVALID')
    need([left['step']['event_digest'], row['step']['event_digest']] == [e.event_digest for e in events], 'EVENT_DIGEST_INVALID')
    states = [native.old.decode_state(wire.decode(x['states'][h]), config)
              for h in (left['memory'], row['memory'])]
    need(states[0].state_digest == row['pre']['memory_state_digest']
         and states[1].state_digest == row['post']['memory_state_digest'], 'STATE_LINK_INVALID')
    event = events[1]
    frame = next(t.frame for t in event.field_payload.timed_frames if t.frame.modality_id == 'visual')
    receipt = x['source_receipts'][3]
    need(receipt['source_digest'] == event.source_digest
         and receipt['rgb_digest'] == x['inputs'][3]['operation']['visual_payload_digest']
         and receipt['rgb_digest'] == record['media']['receipts'][3]['rgb'], 'SOURCE_INVALID')
    transition = next(t for t in proof['native']['transitions'] if t['event'] == 4)
    observed = next(t for t in transition['ppb'] if t['modality'] == 'visual')
    pre, post = [s.tspm_state.visual_ppb1_state for s in states]
    cfg = config.profile.profile.visual_config
    need(pre.config_digest == post.config_digest == cfg.digest()
         and observed['pre_digest'] == pre.digest() and observed['post_digest'] == post.digest(), 'PPB_BINDING_INVALID')
    need(frame.clock_id == pre.source_clock_id and frame.window_end_tick > pre.last_source_window_end_tick, 'TIME_INVALID')
    result = dict(config=asdict(cfg), config_digest=cfg.digest(), values=list(frame.values),
                frame=asdict(frame), pre=asdict(pre), post=asdict(post), observed=observed,
                event_digest=event.event_digest, source_receipt=receipt,
                births=left['current_births'][20:24], adjacency=[3, 4])
    return json.loads(wire.canonical(result))


def table(data):
    q = tuple(data['values']); cfg = data['config']; pre = data['pre']
    need(len(q) == 288 and all(type(v) is float and math.isfinite(v) and abs(v) <= 1 for v in q), 'VALUES_INVALID')
    need(len(pre['slots']) == 4 and len({s['slot_id'] for s in pre['slots']}) == 4, 'SLOTS_INVALID')
    step = pre['accepted_step_count'] + 1
    rows, matches, free, surviving = [], [], [], []
    for i, slot in enumerate(pre['slots']):
        expired = slot['occupied'] and step-slot['last_selected_step'] >= cfg['expire_after_steps']
        active = slot['occupied'] and not expired
        item = dict(slot_id=slot['slot_id'], occupied=slot['occupied'], expired=expired,
                    eligible=active, generation=data['births'][i], support=slot['support_count'], terms=[])
        if active:
            values = tuple(slot['prototype_values'])
            need(len(values) == 288, 'VALUES_INVALID')
            terms = [abs(q[j]-values[j]) for j in range(288)]
            distance = ppb.normalized_mean_l1_distance(q, values)
            item.update(terms=[dict(index=j, difference=t, hex=t.hex()) for j,t in enumerate(terms)],
                        distance=distance, distance_hex=distance.hex(), threshold=cfg['match_threshold'],
                        margin=distance-cfg['match_threshold'], matched=distance <= cfg['match_threshold'])
            surviving.append((slot['last_selected_step'], slot['slot_id'], i))
            if item['matched']:
                matches.append((distance, slot['slot_id'], i))
        else:
            free.append((slot['slot_id'], i))
        rows.append(item)
    if matches:
        selected = min(matches)[2]; action = 'MATCHED'
    elif free:
        selected = min(free)[1]; action = 'CREATED'
    else:
        selected = min(surviving)[2]; action = 'REPLACED'
    return dict(rows=rows, action=action, selected_slot_id=pre['slots'][selected]['slot_id'],
                primary_differences=2*sum(len(r['terms']) for r in rows))


def verify(data, result):
    """Independent arithmetic/selection; never calls table or the PPB distance helper."""
    before = wire.canonical(data)
    cfg, bank, q = data['config'], data['pre'], data['values']
    step = bank['accepted_step_count']+1
    need(len(result['rows']) == len(bank['slots']) == 4, 'TABLE_INCOMPLETE')
    hits, vacancies, oldest = [], [], []
    checked = 0
    for i, s in enumerate(bank['slots']):
        r = result['rows'][i]
        expired = s['occupied'] and step-s['last_selected_step'] >= cfg['expire_after_steps']
        live = s['occupied'] and not expired
        need((r['slot_id'], r['eligible'], r['occupied'], r['expired'], r['generation'], r['support']) ==
             (s['slot_id'], live, s['occupied'], expired, data['births'][i], s['support_count']), 'CANDIDATE_INVALID')
        if not live:
            need(r['terms'] == [], 'FREE_TERMS_INVALID')
            vacancies.append((s['slot_id'], i))
            continue
        need(len(r['terms']) == 288, 'TERMS_INCOMPLETE')
        terms = []
        for j in range(288):
            term = abs(float(q[j])-float(s['prototype_values'][j]))
            need(r['terms'][j] == dict(index=j, difference=term, hex=term.hex()), 'TERM_INVALID')
            terms.append(term)
        distance = math.fsum(terms)/288
        need(r['distance'].hex() == r['distance_hex'] == distance.hex()
             and r['threshold'] == cfg['match_threshold'] and r['margin'] == distance-cfg['match_threshold']
             and r['matched'] == (distance <= cfg['match_threshold']), 'DISTANCE_INVALID')
        checked += 288
        oldest.append((s['last_selected_step'], s['slot_id'], i))
        if distance <= cfg['match_threshold']:
            hits.append((distance, s['slot_id'], i))
    chosen = sorted(hits)[0][2] if hits else sorted(vacancies)[0][1] if vacancies else sorted(oldest)[0][2]
    action = 'MATCHED' if hits else 'CREATED' if vacancies else 'REPLACED'
    need((result['action'], result['selected_slot_id']) == (action, bank['slots'][chosen]['slot_id']), 'SELECTION_INVALID')
    observed = data['observed']
    need((observed['event'], observed['slot_id']) == (action, result['selected_slot_id']), 'OBSERVED_TRANSITION_MISMATCH')
    post = data['post']
    need(post['accepted_step_count'] == step and post['source_clock_id'] == data['frame']['clock_id']
         and post['last_source_window_end_tick'] == data['frame']['window_end_tick'], 'POST_TIME_INVALID')
    # Check the recorded poststate, without constructing or advancing a memory state.
    for i, (old, new) in enumerate(zip(bank['slots'], post['slots'], strict=True)):
        if i != chosen:
            expired = old['occupied'] and step-old['last_selected_step'] >= cfg['expire_after_steps']
            need(not expired and old == new, 'UNCHOSEN_CHANGED')
            continue
        expected = [(1-cfg['update_rate'])*v+cfg['update_rate']*z for v,z in zip(old['prototype_values'],q)] if hits else q
        support = min(cfg['stable_after'],old['support_count']+1) if hits else 1
        need(new['occupied'] and new['slot_id'] == old['slot_id'] and new['prototype_values'] == expected
             and new['support_count'] == support and new['last_selected_step'] == step, 'POST_INVALID')
    need(before == wire.canonical(data) and result['primary_differences'] == checked*2, 'MUTATION_OR_WORK_INVALID')
    return dict(status='EVIDENCE_VALID', read_only=True, comparisons=checked, action=action,
                selected_slot_id=result['selected_slot_id'], no_memory_advance=True)
