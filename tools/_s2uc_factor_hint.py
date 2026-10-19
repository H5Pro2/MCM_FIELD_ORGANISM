"""Factor-bound hint only. Exact confirmation is inherited unchanged."""
import math
from tools._s2uc_provisional_hint import ProvisionalHintArm
from tools._s2uc_four_arm import tu


def component_equal(stored,incoming,exponent):
    try:
        return math.ldexp(stored,exponent)==incoming
    except OverflowError:
        return False


def factor_matches(frames,offset,hint,exponent):
    return all(component_equal(x,y,exponent) for j in range(2)
               for x,y in zip(frames[offset+j].values,hint[j].values))


class FactorHintArm(ProvisionalHintArm):
    def hint(self,frame):
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
        if self._candidate is not None:
            sources.append(('candidate',self._candidate.candidate_generation,self._candidate.frames))
        matches=[]
        for role,generation,frames in sources:
            for offset in range(3):
                factors=[math.ldexp(1.,e) for e in (-1,0,1) if factor_matches(frames,offset,hint,e)]
                if factors:
                    matches.append(dict(role=role,generation=generation,formation=frames[0].segment,
                                        ordinals=[f.ordinal for f in frames],offset=offset,factors=factors))
        self._check_budget()
        decision=('ABSTAIN_NO_MATCH' if not matches else 'ABSTAIN_AMBIGUOUS' if len(matches)>1
                  else 'PROVISIONAL_CANDIDATE_MATCH' if matches[0]['role']=='candidate' else 'CONFIRMED_RETAINED_MATCH')
        return dict(decision=decision,matches=matches)
