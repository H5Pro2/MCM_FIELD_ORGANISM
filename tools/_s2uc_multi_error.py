"""Optional exact multi-hypothesis feedback. One 416-byte bank, no replay."""
import json
import math
import struct

from tools._s2uc_signal_approx_adapter import SignalApproxAdapter
from tools._s2uc_paired_error_ema import CELL, PairedErrorAdapter, mae48, require
from tools._s2uc_continuation_adapter import PredictionReceipt
from tools._s2uc_pair_context_adapter import ContextReceipt

POLICY = 'multi_error_exact_v1'
HEAD = struct.Struct('<QBBBB4x')
ENTRY = HEAD
PAIR = struct.Struct('<dd')
U64 = struct.Struct('<Q')
F64 = struct.Struct('<d')
REASONS = ('NONE', 'NO_ELIGIBLE_CONTEXT', 'COLD_ONLY',
           'NO_ESTIMATED_IMPROVEMENT', 'TIED_IMPROVEMENT', 'SELECTED_BY_ERROR')
IDLE, FREEZING, PENDING, UPDATING, ADMITTING, CLOSED = range(6)


class MultiErrorAdapter(SignalApproxAdapter):
    _generation_live = PairedErrorAdapter._generation_live
    _validate_feedback_input = PairedErrorAdapter._validate_feedback_input

    def __setattr__(self, name, value):
        if name in ('multi_policy', '_multi_policy') and hasattr(self, '_multi_policy'):
            raise ValueError('MULTI_POLICY_IMMUTABLE')
        super().__setattr__(name, value)

    def __delattr__(self, name):
        require(name not in ('multi_policy', '_multi_policy'), 'MULTI_POLICY_IMMUTABLE')
        super().__delattr__(name)

    @property
    def multi_policy(self):
        return self._multi_policy

    def __init__(self, *args, multi_policy='disabled', **kwargs):
        require(multi_policy in ('disabled', POLICY), 'MULTI_POLICY')
        if multi_policy == POLICY:
            require(kwargs.get('retrieval_policy', 'exact_v1') == 'exact_v1' and
                    kwargs.get('policy', 'legacy_v1') == 'legacy_v1', 'MULTI_EXACT_LEGACY_ONLY')
        self._multi_policy = multi_policy
        self.bank = None
        self._frozen = None
        self._pframe = None
        super().__init__(*args, **kwargs)
        if multi_policy == POLICY:
            self.bank = bytearray(416)
            self._frozen = [None] * 6
            self._feedback_scope = self._scope()
            require(all(0 <= x < 2**63 for x in
                        (self.hop, self.window, self.start_sample, self.first_ordinal)), 'EMA_TIME_RANGE')

    def _scope(self):
        return (self.arm.owner, self.arm.profile, self.stream, self.hop,
                self.window, self.start_sample, self.first_ordinal)

    def _guard(self):
        require(not self.closed, 'CLOSED')
        if self.bank is not None:
            require(self.bank[408] in (IDLE, PENDING), 'MULTI_BUSY')

    def _zero(self, start, end):
        for i in range(start, end):
            self.bank[i] = 0

    def _checkpoint(self, stage, index):
        """Production no-op, overridden only by external technical tests."""

    def _find(self, role, generation, offset):
        for i in range(6):
            r = CELL.unpack_from(self.bank, i*32)
            if r[-1] and (r[3], r[0], r[4]) == (role, generation, offset):
                return i
        return None

    def _validate_cells(self, previous=None, candidate=None):
        for i in range(6):
            g, ec, ep, role, off, q, valid = CELL.unpack_from(self.bank, i*32)
            require(valid in (0, 1), 'CELL_VALID')
            if not valid:
                continue
            require(g > 0 and role in (0, 1) and off in (0, 1) and q == 0 and
                    math.isfinite(ec) and math.isfinite(ep) and ec >= 0 and ep >= 0, 'CELL_INVALID')
            if previous is None:
                live = self._generation_live(role, g)
            else:
                live = (role == 0 and any(t.generation == g for t in previous)) or (
                    role == 1 and candidate is not None and candidate.candidate_generation == g)
            require(live, 'STALE_CELL')
            for j in range(i):
                r = CELL.unpack_from(self.bank, j*32)
                require(not r[-1] or (r[3], r[0], r[4]) != (role, g, off), 'DUPLICATE_CELL')

    def _prune(self):
        for i in range(6):
            r = CELL.unpack_from(self.bank, i*32)
            if r[-1] and not self._generation_live(r[3], r[0]):
                self._zero(i*32, (i+1)*32)

    def _receipt(self, status, indices, intervals, matches):
        if self.bank is None or len(indices) != 2:
            return super()._receipt(status, indices, intervals, matches)
        self._guard()
        try:
            require(self.pending_prediction is None, 'PREDICTION_PENDING')
            require(len(matches) <= 9, 'MATCH_LIMIT')
            self.bank[408] = FREEZING
            self._validate_cells()
            count = warm = 0
            best = 0.0
            choice = ties = 0
            self._pframe = self.pair[1]
            # Serialize each row separately to avoid an additional metadata table.
            rows = []
            for match_index, m in enumerate(matches):
                role = {'retained': 0, 'candidate': 1}[m['role']]
                g, off = m['generation'], m['offset']
                require(type(g) is int and 0 < g < 2**64 and off in (0, 1, 2), 'MATCH_KEY')
                for prior_index in range(match_index):
                    n = matches[prior_index]
                    require((n['role'], n['generation'], n['offset']) != (m['role'], g, off), 'DUPLICATE_MATCH')
                if m['factors'] != [1.0] or off == 2:
                    rows.append(json.dumps(dict(eligible=False, reason='NO_SUCCESSOR' if off == 2 else 'FACTOR_UNSPECIFIED'), separators=(',', ':')))
                    continue
                require(count < 6, 'HYPOTHESIS_LIMIT')
                found = None
                for sr, sg, fs in self._sources():
                    if (sr, sg) == (m['role'], g):
                        require(fs[0].segment == m['formation'] and
                                all(fs[k].ordinal == m['ordinals'][k] for k in range(4)), 'SOURCE_IDENTITY')
                        found = fs[off+2]
                require(found is not None, 'SOURCE_MISSING')
                self._frozen[count] = found
                ENTRY.pack_into(self.bank, 208+16*count, g, role, off, 0, 255)
                slot = self._find(role, g, off)
                ec = ep = d = None
                if slot is not None:
                    r = CELL.unpack_from(self.bank, slot*32)
                    ec, ep = r[1], r[2]
                    d = ec-ep
                    warm += 1
                    if d < best:
                        best, choice, ties = d, count+1, 1
                    elif d == best and d < 0:
                        ties += 1
                rows.append(json.dumps(dict(eligible=True, ticket=count, ec=ec, ep=ep, delta=d,
                    evaluation='COLD' if slot is None else 'TIE_P' if d == 0 else 'WORSE_THAN_P' if d > 0 else 'BETTER_THAN_P'), separators=(',', ':'), allow_nan=False))
                count += 1
            reason = 1 if not count else 2 if not warm else 3 if best == 0 else 4 if ties > 1 else 5
            if reason != 5:
                choice = 0
            HEAD.pack_into(self.bank, 192, indices[-1]+1, 1, count, choice, reason)
            header = dict(status=status, stream=self.stream, owner=self.arm.owner,
                          profile=self.arm.profile, input_indices=indices, source_intervals=intervals,
                          read_revision=self.revision, decision=REASONS[reason], choice=choice)
            raw = json.dumps(header, separators=(',', ':'))[:-1] + ',"matches":['
            raw += ','.join(json.dumps(m, separators=(',', ':'), allow_nan=False) for m in matches)
            raw += '],"hypotheses":[' + ','.join(rows) + ']}'
            require(len(raw.encode('utf-8')) <= 16384, 'RECEIPT_LIMIT')
            context = self._frozen[choice-1].values if choice else None
            self.pending_prediction = PredictionReceipt(indices[-1]+1, self.revision,
                REASONS[reason], context, self._pframe.values, raw)
            self._checkpoint('frozen', -1)
            self.bank[408] = PENDING
            return ContextReceipt(raw)
        except BaseException:
            self._terminate()
            raise

    @property
    def selected_values(self):
        self._guard()
        p = self.pending_prediction
        return None if p is None else p.context_values if p.context_values is not None else p.persistence_values

    def consume_feedback(self, sample):
        self._guard()
        try:
            require(self.bank is not None, 'MULTI_NOT_ENABLED')
            self._validate_feedback_input(sample)
            target, active, count, choice, reason = HEAD.unpack_from(self.bank, 192)
            require(active == 1 and self.pending_prediction is not None and target == sample.index and
                    self.pending_prediction.target_index == target and 0 <= count <= 6, 'FEEDBACK_TARGET')
            self.bank[408] = UPDATING
            self._validate_cells()
            require(self._pframe is not None, 'PERSISTENCE_MISSING')
            ep = mae48(self._pframe.values, sample.values)
            for i in range(count):
                g, role, off, q, _ = ENTRY.unpack_from(self.bank, 208+16*i)
                require(g > 0 and role in (0, 1) and off in (0, 1) and q == 0 and self._frozen[i] is not None, 'TICKET_KEY')
                for j in range(i):
                    old = ENTRY.unpack_from(self.bank, 208+16*j)
                    require((old[0], old[1], old[2]) != (g, role, off), 'DUPLICATE_TICKET')
                ec = mae48(self._frozen[i].values, sample.values)
                new_ep = ep
                slot = None
                if self._generation_live(role, g):
                    slot = self._find(role, g, off)
                    if slot is not None:
                        old = CELL.unpack_from(self.bank, slot*32)
                        ec = .5*old[1]+.5*ec
                        new_ep = .5*old[2]+.5*ep
                    else:
                        for s in range(6):
                            if self.bank[s*32+27]:
                                continue
                            if any(self.bank[208+16*j+11] == s for j in range(i)):
                                continue
                            slot = s
                            break
                        require(slot is not None, 'CELL_LIMIT')
                    self.bank[409] |= 1 << i
                require(math.isfinite(ec) and math.isfinite(new_ep), 'EMA_NONFINITE')
                PAIR.pack_into(self.bank, 304+16*i, ec, new_ep)
                self.bank[208+16*i+11] = 255 if slot is None else slot
            self._checkpoint('validated', -1)
            for i in range(count):
                if not (self.bank[409] & (1 << i)):
                    continue
                g, role, off, q, slot = ENTRY.unpack_from(self.bank, 208+16*i)
                ec, ep = PAIR.unpack_from(self.bank, 304+16*i)
                base = slot*32
                U64.pack_into(self.bank, base, g); self._checkpoint('generation', i)
                F64.pack_into(self.bank, base+8, ec); self._checkpoint('ec', i)
                F64.pack_into(self.bank, base+16, ep); self._checkpoint('ep', i)
                self.bank[base+24] = role; self._checkpoint('role', i)
                self.bank[base+25] = off; self._checkpoint('offset', i)
                self.bank[base+26] = q; self._checkpoint('quality', i)
                self.bank[base+27] = 1; self._checkpoint('valid', i)
            self._checkpoint('published', -1)
            self._release()
        except BaseException:
            self._terminate()
            raise

    def _release(self):
        self.pending_prediction = None
        if self.bank is not None:
            self._zero(192, 400)
            self.bank[408] = IDLE
            self.bank[409] = 0
            for i in range(6):
                self._frozen[i] = None
            self._pframe = None

    def release_prediction(self):
        if self.bank is None:
            return super().release_prediction()
        self._guard()
        self._release()

    def accept_perception(self, sample):
        if self.bank is None:
            return super().accept_perception(sample)
        self._guard()
        try:
            if self.bank is not None:
                self._validate_feedback_input(sample)
            return super().accept_perception(sample)
        except BaseException:
            self._terminate()
            raise

    def _promote(self, candidate, previous, result):
        require(self._scope() == self._feedback_scope, 'PROMOTION_SCOPE')
        require(candidate is not None and result['candidate_generation'] == candidate.candidate_generation and
                self.arm._candidate is None, 'PROMOTION_CANDIDATE')
        old, new = candidate.candidate_generation, result['generation']
        require(type(new) is int and U64.unpack_from(self.bank, 400)[0] < new < 2**64, 'PROMOTION_GENERATION')
        retained = self.arm._retained_many
        evicted = previous[0].generation if len(previous) == 2 else None
        require(result['evicted'] == evicted and len(retained) == min(2, len(previous)+1), 'PROMOTION_STOCK')
        survivors = previous[1:] if len(previous) == 2 else previous
        require(all(retained[i] is t for i, t in enumerate(survivors)) and
                retained[-1].generation == new and retained[-1].frames is candidate.frames,
                'PROMOTION_IDENTITY')
        require(all(t.generation != new for t in previous), 'PROMOTION_REUSED')
        require(len(candidate.frames) == 4 and all(f.owner == self.arm.owner and f.profile == self.arm.profile
                for f in candidate.frames) and all(candidate.frames[i].ordinal < candidate.frames[i+1].ordinal
                for i in range(3)), 'PROMOTION_FRAMES')
        self._validate_cells(previous, candidate)
        self._checkpoint('promotion_validated', -1)
        for i in range(6):
            r = CELL.unpack_from(self.bank, 32*i)
            if r[-1] and r[3] == 0 and r[0] == evicted:
                self._zero(i*32, (i+1)*32)
            elif r[-1] and r[3] == 1 and r[0] == old:
                U64.pack_into(self.bank, i*32, new)
                self._checkpoint('promotion_generation', i)
                self.bank[i*32+24] = 0
                self._checkpoint('promotion_role', i)
        U64.pack_into(self.bank, 400, new)
        self._prune()

    def _admit(self, frame):
        if self.bank is None:
            return super()._admit(frame)
        self._guard()
        before_state = self.bank[408]
        self.bank[408] = ADMITTING
        try:
            # Identical normal admission, capturing the actual close result directly.
            candidate = self.arm._candidate
            previous = tuple(self.arm._retained_many)
            self.arm.form(frame)
            self.admitted += 1
            self.revision += 1
            if (frame.ordinal-self.first_ordinal+1) % 4 == 0:
                result = self.arm.close_segment(frame.segment)
                self.revision += 1
                if result['action'] == 'TRACE_PROMOTED':
                    self._promote(candidate, previous, result)
            self._prune()
            self.bank[408] = before_state
        except BaseException:
            self._terminate()
            raise

    def _terminate(self):
        self.pending_prediction = None
        if self.bank is not None:
            self._zero(0, 416)
            for i in range(6):
                self._frozen[i] = None
            self._pframe = None
        super()._terminate()

    def finish_story(self):
        if self.bank is None:
            return super().finish_story()
        self._guard()
        self._release()
        result = super().finish_story()
        if self.bank is not None:
            self._zero(0, 416)
        return result
