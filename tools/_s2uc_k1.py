"""Optional fixed K1 candidate lifetime. No new persistent arm fields."""
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2ub_candidate_confirmation import _same_values, _disjoint_ordinals
from tools._s2uc_pair_context_adapter import PairContextAdapter, AdapterError
from tools._s2uc_multi_error import MultiErrorAdapter
from tools._s2tu_retained_trace import need

POLICY = 'candidate_hold_one_block_v1'


class K1Arm(FactorRecencyArm):
    def close_segment(self, segment):
        need(not self._closed and segment == self._forming_segment, 'SEGMENT_INVALID')
        if len(self._forming) != 4:
            return super().close_segment(segment)
        candidate = self._candidate
        expired = candidate is not None and self._forming[-1].ordinal - candidate.frames[-1].ordinal >= 8
        retained_match = any(_same_values(t.frames, self._forming) for t in self._retained_many)
        candidate_match = candidate is not None and _same_values(candidate.frames, self._forming)
        if not retained_match and not candidate_match and candidate is not None and not expired:
            self._forming.clear()
            self._forming_segment = None
            self._check_budget()
            return dict(action='TRACE_CANDIDATE_HELD', generation=None,
                        candidate_generation=candidate.candidate_generation, evicted=None)
        if not retained_match:
            if candidate_match and _disjoint_ordinals(candidate.frames, self._forming):
                need(self._retained_generation < 2**64-1, 'K1_GENERATION_LIMIT')
            elif not candidate_match:
                need(self._candidate_generation < 2**64-1, 'K1_GENERATION_LIMIT')
        result = super().close_segment(segment)
        if expired and result['action'] in ('TRACE_CONFIRMED', 'TRACE_CONFIRMED_RECENT', 'TRACE_CANDIDATE_OVERLAP_NOT_CONFIRMED'):
            self._candidate = None
            result['candidate_generation'] = None
        self._check_budget()
        return result


class _K1PairInit(PairContextAdapter):
    """Same initialization/scoping rules; exact K1 type instead of legacy type."""
    def __init__(self, arm, stream, *, hop=4800, window=4800, start_sample=0, first_ordinal=1):
        if type(arm) is not K1Arm or arm._closed or arm._forming or arm._hints:
            raise AdapterError('ARM_NOT_IDLE')
        if any(type(x) is not int or x < 1 for x in (hop, window, first_ordinal)):
            raise AdapterError('CONFIG_INVALID')
        if type(start_sample) is not int or start_sample < 0:
            raise AdapterError('CONFIG_INVALID')
        for x in (stream, arm.owner):
            if type(x) is not str or not x or len(x.encode()) > 96:
                raise AdapterError('ID_INVALID')
        self.arm = arm
        self.stream = stream
        self.hop = hop
        self.window = window
        self.start_sample = start_sample
        self.first_ordinal = first_ordinal
        self.next_index = 1
        self.pair = []
        self.intervals = []
        self.closed = False
        self.revision = 0
        self.accepted = 0
        self.admitted = 0
        self.discarded_on_error = 0


class K1Adapter(MultiErrorAdapter, _K1PairInit):
    """Only the exact-type constructor differs; all policy methods are inherited."""


def create(profile, owner, stream, *, candidate_policy='disabled', multi_policy='disabled', **kwargs):
    if candidate_policy == 'disabled':
        return MultiErrorAdapter(FactorRecencyArm(profile, owner), stream, multi_policy=multi_policy, **kwargs)
    if candidate_policy != POLICY:
        raise AdapterError('K1_POLICY_INVALID')
    return K1Adapter(K1Arm(profile, owner), stream, multi_policy=multi_policy, **kwargs)
