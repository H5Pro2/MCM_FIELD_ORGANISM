"""Local 2K/1R arm; only retained capacity and total limit differ from K2."""
from tools._s2uc_two_candidates import TwoCandidateArm, tu, ub


class TwoCandidateOneRetainedArm(TwoCandidateArm):
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
                evicted = self._retained_many.pop(0).generation if len(self._retained_many) == 1 else None
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

    def _check_budget(self):
        tu.need(len(self._candidates)<=2 and len(self._retained_many)<=1 and
                self.resources()['trace_frames']<=16 and len(self._hints)<=2, 'TRACE_FRAME_BUDGET_INVALID')
