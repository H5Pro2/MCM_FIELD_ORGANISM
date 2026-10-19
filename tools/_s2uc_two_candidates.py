"""Counterprobe only: two FIFO candidates, two retained traces, 20+2 frames."""
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools._s2uc_four_arm import tu, ub


class TwoCandidateArm(ProvisionalHintArm):
    def __init__(self, profile, owner):
        super().__init__(profile, owner)
        self._candidates = []

    def close_segment(self, segment):
        tu.need(not self._closed and segment == self._forming_segment, 'SEGMENT_INVALID')
        forming = tuple(self._forming)
        self._forming.clear()
        self._forming_segment = None
        if len(forming) != 4:
            return dict(action='TRACE_DISCARDED_INCOMPLETE', generation=None, candidate_generation=None, evicted=None)
        for retained in self._retained_many:
            if ub._same_values(retained.frames, forming):
                return dict(action='TRACE_CONFIRMED', generation=retained.generation,
                            candidate_generation=self.candidate_generation, evicted=None)
        for index, candidate in enumerate(self._candidates):
            if ub._same_values(candidate.frames, forming):
                if not ub._disjoint_ordinals(candidate.frames, forming):
                    return dict(action='TRACE_CANDIDATE_OVERLAP_NOT_CONFIRMED', generation=None,
                                candidate_generation=candidate.candidate_generation, evicted=None)
                self._retained_generation += 1
                evicted = self._retained_many.pop(0).generation if len(self._retained_many) == 2 else None
                self._retained_many.append(tu.RetainedTrace(self._retained_generation, candidate.frames))
                self._candidates.pop(index)
                self._check_budget()
                return dict(action='TRACE_PROMOTED', generation=self._retained_generation,
                            candidate_generation=candidate.candidate_generation, evicted=evicted)
        replaced = self._candidates.pop(0).candidate_generation if len(self._candidates) == 2 else None
        self._candidate_generation += 1
        self._candidates.append(ub.CandidateTrace(self._candidate_generation, forming))
        self._check_budget()
        return dict(action='TRACE_CANDIDATE_CREATED' if replaced is None else 'TRACE_CANDIDATE_REPLACED',
                    generation=None, candidate_generation=self._candidate_generation, evicted=replaced)

    @property
    def candidate_generation(self):
        return self._candidates[-1].candidate_generation if self._candidates else None

    def resources(self):
        retained, candidate, forming = 4*len(self._retained_many), 4*len(self._candidates), len(self._forming)
        return dict(retained_frames=retained, candidate_frames=candidate, forming_frames=forming,
                    trace_frames=retained+candidate+forming, hint_frames=len(self._hints))

    def _check_budget(self):
        tu.need(len(self._candidates)<=2 and len(self._retained_many)<=2 and
                self.resources()['trace_frames']<=20 and len(self._hints)<=2, 'TRACE_FRAME_BUDGET_INVALID')

    def close_owner(self):
        super().close_owner()
        self._candidates.clear()

    def evidence(self):
        result=super().evidence()
        result['candidates']=tuple((c.candidate_generation,c.frames) for c in self._candidates)
        return result

    def hint(self, frame):
        self._check(frame)
        if self._hints:
            tu.need(frame.segment==self._hint_segment and frame.ordinal>self._hints[-1].ordinal,'HINT_ORDER_INVALID')
        else:
            self._hint_segment=frame.segment
        tu.need(len(self._hints)<2,'HINT_BUFFER_INVALID')
        self._hints.append(frame)
        if len(self._hints)==1:
            self._check_budget()
            return None
        hint=tuple(self._hints)
        self._hints.clear()
        self._hint_segment=None
        sources=[('retained',t.generation,t.frames) for t in self._retained_many]
        sources.extend(('candidate',c.candidate_generation,c.frames) for c in self._candidates)
        matches=[]
        for role,generation,frames in sources:
            for offset in range(3):
                if frames[offset].values==hint[0].values and frames[offset+1].values==hint[1].values:
                    matches.append(dict(role=role,generation=generation,formation=frames[0].segment,
                                        ordinals=[f.ordinal for f in frames],offset=offset))
        decision=('ABSTAIN_NO_MATCH' if not matches else 'ABSTAIN_AMBIGUOUS' if len(matches)>1
                  else 'PROVISIONAL_CANDIDATE_MATCH' if matches[0]['role']=='candidate' else 'CONFIRMED_RETAINED_MATCH')
        self._check_budget()
        return dict(decision=decision,matches=matches)
