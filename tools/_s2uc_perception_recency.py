"""Local S2TX-style refresh of current confirmed traces; exact hints unchanged."""
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools._s2uc_four_arm import tu,ub

class PerceptionRecencyArm(ProvisionalHintArm):
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
            self._retained_many.remove(trace)
            self._retained_many.append(trace)
            self._observation_end[trace.generation]=forming[-1].ordinal
            result=dict(result,action='TRACE_CONFIRMED_RECENT')
            self._check_budget()
        self._observation_end={t.generation:self._observation_end.get(t.generation,forming[-1].ordinal if result['action']=='TRACE_PROMOTED' and t.generation==result['generation'] else t.frames[-1].ordinal) for t in self._retained_many}
        return result

    def close_owner(self):
        super().close_owner()
        self._observation_end.clear()
