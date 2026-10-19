"""B2-V: only hint retrieval changes; no additional memory state."""
from tools._s2uc_four_arm import CandidateTwoArm, tu


class ProvisionalHintArm(CandidateTwoArm):
    def hint(self, frame):
        self._check(frame)
        if self._hints:
            tu.need(frame.segment == self._hint_segment and frame.ordinal > self._hints[-1].ordinal,
                    'HINT_ORDER_INVALID')
        else:
            self._hint_segment = frame.segment
        tu.need(len(self._hints) < 2, 'HINT_BUFFER_INVALID')
        self._hints.append(frame)
        if len(self._hints) == 1:
            self._check_budget()
            return None
        hint = tuple(self._hints)
        self._hints.clear()
        self._hint_segment = None
        matches = []
        sources = [('retained', trace.generation, trace.frames) for trace in self._retained_many]
        if self._candidate is not None:
            sources.append(('candidate', self._candidate.candidate_generation, self._candidate.frames))
        for role, generation, frames in sources:
            for offset in range(3):
                if frames[offset].values == hint[0].values and frames[offset+1].values == hint[1].values:
                    matches.append(dict(role=role, generation=generation, formation=frames[0].segment,
                                        ordinals=[f.ordinal for f in frames], offset=offset))
        decision = ('ABSTAIN_NO_MATCH' if not matches else 'ABSTAIN_AMBIGUOUS' if len(matches) > 1
                    else 'PROVISIONAL_CANDIDATE_MATCH' if matches[0]['role'] == 'candidate'
                    else 'CONFIRMED_RETAINED_MATCH')
        self._check_budget()
        return dict(decision=decision, matches=matches)
