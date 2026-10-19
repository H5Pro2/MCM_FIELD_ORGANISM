"""New evaluation-only replay, at most80 positions. Historical entry unchanged."""
from tools._s2uc_multi_observer import *

def replay(values, profile, *, count, evidence=None, check=lambda: None):
    require(type(count) is int and 4 <= count <= 80 and count % 2 == 0, 'MULTI_REPLAY_BOUND')
    out = {} if evidence is None else evidence
    out.update(rows=[], forecasts=[], updates=[], states=[], admissions=[])
    a = MultiErrorAdapter(FactorRecencyArm(profile, 'owner'), 'stream', multi_policy=POLICY)
    ref = SignalApproxAdapter(FactorRecencyArm(profile, 'owner'), 'stream')
    source = GatedReplay(iter(values), profile)
    meter = Meter(a)
    try:
        for _ in range(count):
            check()
            s = source.take(a)
            if a.pending_prediction:
                p = a.pending_prediction
                out['rows'].append(dict(target=s.index, selected_mae=mae48(a.selected_values, s.values),
                    decision=p.status, choice=HEAD.unpack_from(a.bank, 192)[3],
                    persistence_mae=mae48(p.persistence_values, s.values)))
                old = cells(a)
                frozen = []
                expected = { (r['role'], r['generation'], r['offset']): dict(r) for r in old }
                for i in range(HEAD.unpack_from(a.bank, 192)[2]):
                    g, role, off, q, dest = ENTRY.unpack_from(a.bank, 208+16*i)
                    ec, ep = mae48(a._frozen[i].values, s.values), mae48(a._pframe.values, s.values)
                    live = a._generation_live(role, g)
                    frozen.append(dict(generation=g, role=role, offset=off, original_ordinal=a._frozen[i].ordinal,
                                       ec=ec, ep=ep, live=live))
                    if live:
                        prev = expected.get((role, g, off))
                        expected[role, g, off] = dict(generation=g, role=role, offset=off, quality=0,
                            ec=ec if prev is None else .5*prev['ec']+.5*ec,
                            ep=ep if prev is None else .5*prev['ep']+.5*ep)
                record = dict(target=s.index, before=old, hypotheses=frozen, status='STARTED')
                out['updates'].append(record)
                meter.measure('feedback', lambda: a.consume_feedback(s))
                key = lambda r: (r['role'], r['generation'], r['offset'])
                require(sorted(cells(a), key=key) == sorted(expected.values(), key=key), 'MULTI_OBSERVER_UPDATE')
                record.update(after=cells(a), status='COMPLETE')
                consume_prediction(ref, s)
            before = cells(a)
            admission = dict(index=s.index, before=before, status='STARTED')
            out['admissions'].append(admission)
            receipt = meter.measure('perception', lambda: a.accept_perception(s))
            ref.accept_perception(s)
            require(state(a.arm) == state(ref.arm), 'MULTI_MEMORY_CHANGED')
            admission.update(after=cells(a), status='COMPLETE')
            out['states'].append(digest(state(a.arm)))
            if receipt:
                meter.receipt = max(meter.receipt, len(receipt.json_text.encode()))
                out['forecasts'].append(json.loads(receipt.json_text))
        end = a.pending_prediction.target_index
        meter.measure('finish', a.finish_story)
        ref.release_prediction(); ref.finish_story()
        require(end == count+1 and not any(a.bank) and a._frozen == [None]*6, 'MULTI_RELEASE')
        out.update(arm='U', frames=count, censored_target=end, resources=meter.snapshot(),
                   slots_released=True, states_identical=True)
        return out
    finally:
        source.close()
        out_cleanup = out if "out" in locals() else evidence
        if not a.closed: a._terminate()
        if not ref.closed: ref._terminate()

        out_cleanup["terminal_cleanup"] = bool(a.closed and ref.closed and source.closed and
            all(not x.pair and not x.arm._forming and not x.arm._hints and not x.arm._retained_many
                and x.arm._candidate is None and x.pending_prediction is None for x in (a,ref)))
