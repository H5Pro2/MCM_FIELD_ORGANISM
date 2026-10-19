"""Offline PPB table; no media, memory advancement or retrieval calls."""
from dataclasses import asdict
import json
import math
from tools import _s2ob_private_state_evidence as wire
from tools import _s2ng_private_comparison_verification as native
from tools import _s2nl_private_half_profile_binding as profile
from mcm_field_organism import _ppb1_reference as ppb


from tools._ppb_visual_transition_table import DiagnosticError, need, table, verify


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
