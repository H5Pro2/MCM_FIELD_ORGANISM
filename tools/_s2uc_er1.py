"""ER1 F: same observation marks, without retained-order refresh."""
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools._s2uc_four_arm import tu,ub

class FifoObservationArm(ProvisionalHintArm):
    def __init__(self,profile,owner):
        super().__init__(profile,owner)
        self._observation_end={}  # At most two scalar ordinal bounds, no frames.

    def close_segment(self,segment):
        tu.need(not self._closed and segment==self._forming_segment,'SEGMENT_INVALID')
        forming=tuple(self._forming)
        matches=[t for t in self._retained_many if ub._same_values(t.frames,forming)] if len(forming)==4 else []
        # Strictly later interval, not merely disjoint individual ordinal sets.
        eligible=len(matches)==1 and forming[0].ordinal>self._observation_end.get(matches[0].generation,matches[0].frames[-1].ordinal)
        result=super().close_segment(segment)
        if eligible and result['action']=='TRACE_CONFIRMED':
            trace=matches[0]
            self._observation_end[trace.generation]=forming[-1].ordinal
            self._check_budget()
        self._observation_end={t.generation:self._observation_end.get(t.generation,forming[-1].ordinal if result['action']=='TRACE_PROMOTED' and t.generation==result['generation'] else t.frames[-1].ordinal) for t in self._retained_many}
        return result

    def close_owner(self):
        super().close_owner()
        self._observation_end.clear()

from tools._s2uc_factor_hint import FactorHintArm
FifoObservationArm.hint = FactorHintArm.hint

from tools._s2uc_pair_context_adapter import PairContextAdapter, AdapterError
from tools._s2uc_multi_error import MultiErrorAdapter
class _FifoPairInit(PairContextAdapter):
    """Same initialization/scoping rules; exact ER1 F type instead of legacy type."""
    def __init__(self, arm, stream, *, hop=4800, window=4800, start_sample=0, first_ordinal=1):
        if type(arm) is not FifoObservationArm or arm._closed or arm._forming or arm._hints:
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


class FifoAdapter(MultiErrorAdapter, _FifoPairInit):
    """Only the exact-type constructor differs; all policy methods are inherited."""

