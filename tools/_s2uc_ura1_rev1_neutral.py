"""Short explicit hand cases. Not a source-generator option or research input."""
import hashlib
from tools._s2uc_ura1_v2_series import policy_case


def fixtures():
    catalog = [[x+j/4096 for j in range(48)] for x in (.125, .875, .5, .25, .75, .0625)]
    # Four learning blocks then four reversed blocks. The boundary is observer-only.
    pairs = [(0, 3), (0, 3), (1, 4), (1, 4), (0, 4), (0, 4), (1, 3), (1, 3)]
    return [(r, dict(catalog=catalog, ids=[v for cue, y in pairs for v in (cue if r == 1 else 1-cue, 2, y, 5)])) for r in (1, 2)]


def continuity_case(number, value, ledger):
    from tools import _s2uc_ura1_v2_engine as engine
    from tools._s2uc_k1_probe import cellmap
    if (number, value) not in fixtures():
        raise ValueError('NEUTRAL_HAND_CASE_ONLY')
    original = engine.run_arm
    proofs = []

    def observed(values, mode, **kwargs):
        if len(values) != 32:
            raise ValueError('NEUTRAL_FRAME_COUNT')
        old = engine.CHECKPOINT
        snapshots, ids = {}, []

        def checkpoint(arm, arm_mode, i, stage):
            old(arm, arm_mode, i, stage)
            if (i, stage) in ((16, 'frame_verified'), (17, 'frame_before')):
                snapshots[i] = engine.raw(engine.common(arm))
                ids.append((id(arm), id(arm.bank)))
                if i == 16:
                    if not cellmap(arm) or arm.accepted != 16 or arm.closed:
                        raise ValueError('NEUTRAL_WARM_BOUNDARY')
                    snapshots['cells'] = len(cellmap(arm))
            if i == 17 and stage == 'frame_before':
                if snapshots[16] != snapshots[17] or ids[0] != ids[1]:
                    raise ValueError('NEUTRAL_BOUNDARY_RESET')

        engine.CHECKPOINT = checkpoint
        try:
            result = original(values, mode, **kwargs)
            if len(ids) != 2:
                raise ValueError('NEUTRAL_BOUNDARY_MISSING')
            proofs.append(dict(mode=mode, frames=32, boundary_after=16, cells=snapshots['cells'],
                               state_sha256=hashlib.sha256(snapshots[16]).hexdigest(),
                               identical_state_at_next_entry=True, same_arm_and_bank=True,
                               reference_feedback=result['reference_equal'], cleanup=result['cleanup'],
                               policy_inputs='PerceptionSample only; boundary held by observer'))
            return result
        finally:
            engine.CHECKPOINT = old

    engine.run_arm = observed
    try:
        result = policy_case(number, value, ledger, neutral=True)
        if [p['mode'] for p in proofs] != ['U', 'R'] or proofs[0]['state_sha256'] != proofs[1]['state_sha256']:
            raise ValueError('NEUTRAL_PAIRED_BOUNDARY')
        ledger.write(f'case-{number:02d}-continuity.json', dict(neutral_only=True, proofs=proofs, integrity=result['integrity']))
        return result
    finally:
        engine.run_arm = original
