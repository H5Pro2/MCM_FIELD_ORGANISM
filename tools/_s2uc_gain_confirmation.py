"""Factor-bound confirmation only, with explicit ambiguous-source abstention."""
import math
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools._s2uc_four_arm import tu, ub


def component_equal(stored, incoming, exponent):
    try:
        return math.ldexp(stored, exponent) == incoming
    except OverflowError:
        return False


def scaled_equal(stored, incoming, exponent):
    return all(component_equal(x,y,exponent)
               for left,right in zip(stored,incoming) for x,y in zip(left.values,right.values))


class GainConfirmationArm(ProvisionalHintArm):
    def close_segment(self, segment):
        tu.need(not self._closed and segment==self._forming_segment,'SEGMENT_INVALID')
        forming=tuple(self._forming)
        self._forming.clear()
        self._forming_segment=None
        base=dict(generation=None,candidate_generation=None,evicted=None)
        if len(forming)!=4:
            return dict(action='TRACE_DISCARDED_INCOMPLETE',**base,matches=[])
        sources=[('retained',t.generation,t.frames) for t in self._retained_many]
        if self._candidate is not None:
            sources.append(('candidate',self._candidate.candidate_generation,self._candidate.frames))
        matches=[]
        for role,generation,frames in sources:
            factors=[math.ldexp(1.,e) for e in (0,-1,1) if scaled_equal(frames,forming,e)]
            if factors:
                matches.append(dict(role=role,generation=generation,formation=frames[0].segment,
                                    ordinals=[f.ordinal for f in frames],factors=factors))
        if len(matches)>1:
            self._check_budget()
            return dict(action='ABSTAIN_AMBIGUOUS_CONFIRMATION',**base,matches=matches)
        if matches:
            match=matches[0]
            if match['role']=='retained':
                return dict(action='TRACE_CONFIRMED',generation=match['generation'],
                            candidate_generation=self.candidate_generation,evicted=None,matches=matches)
            if not ub._disjoint_ordinals(self._candidate.frames,forming):
                return dict(action='TRACE_CANDIDATE_OVERLAP_NOT_CONFIRMED',generation=None,
                            candidate_generation=self.candidate_generation,evicted=None,matches=matches)
            self._retained_generation+=1
            evicted=self._retained_many.pop(0).generation if len(self._retained_many)==2 else None
            self._retained_many.append(tu.RetainedTrace(self._retained_generation,self._candidate.frames))
            promoted=self.candidate_generation
            self._candidate=None
            self._check_budget()
            return dict(action='TRACE_PROMOTED',generation=self._retained_generation,
                        candidate_generation=promoted,evicted=evicted,matches=matches)
        replaced=self.candidate_generation
        self._candidate_generation+=1
        self._candidate=ub.CandidateTrace(self._candidate_generation,forming)
        self._check_budget()
        return dict(action='TRACE_CANDIDATE_CREATED' if replaced is None else 'TRACE_CANDIDATE_REPLACED',
                    generation=None,candidate_generation=self.candidate_generation,evicted=replaced,matches=[])
