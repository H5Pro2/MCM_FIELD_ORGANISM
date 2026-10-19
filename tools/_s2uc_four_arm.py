"""Local synthetic counterprobe; existing reference classes remain untouched."""
from tools import _s2tu_retained_trace as tu
from tools import _s2tw_exact_confirmation as tw
from tools import _s2ub_candidate_confirmation as ub


class OneSlotStore(tw.ExactConfirmationStore):
    def close_segment(self, segment):
        # Existing exact-repeat/incomplete behavior, with only capacity reduced.
        result = super().close_segment(segment)
        if len(self._retained) > 1:
            result["evicted"] = self._retained.pop(0).generation
        return result


class ImmediateOneArm(ub.ImmediateTwArm):
    def __init__(self, profile, owner):
        super().__init__(profile, owner)
        self.store = OneSlotStore(profile, owner)


class CandidateTwoArm(ub.CandidateConfirmationArm):
    def __init__(self, profile, owner):
        super().__init__(profile, owner)
        self._retained_many = []

    def close_segment(self, segment):
        tu.need(not self._closed and segment == self._forming_segment, "SEGMENT_INVALID")
        forming = tuple(self._forming)
        self._forming.clear()
        self._forming_segment = None
        if len(forming) != ub.TRACE_FRAMES:
            self._check_budget()
            return dict(action="TRACE_DISCARDED_INCOMPLETE", generation=None, candidate_generation=None, evicted=None)
        for retained in self._retained_many:
            if ub._same_values(retained.frames, forming):
                self._check_budget()
                return dict(action="TRACE_CONFIRMED", generation=retained.generation,
                            candidate_generation=self.candidate_generation, evicted=None)
        if self._candidate is not None and ub._same_values(self._candidate.frames, forming):
            if not ub._disjoint_ordinals(self._candidate.frames, forming):
                self._check_budget()
                return dict(action="TRACE_CANDIDATE_OVERLAP_NOT_CONFIRMED", generation=None,
                            candidate_generation=self.candidate_generation, evicted=None)
            self._retained_generation += 1
            evicted = self._retained_many.pop(0).generation if len(self._retained_many) == 2 else None
            self._retained_many.append(tu.RetainedTrace(self._retained_generation, self._candidate.frames))
            promoted = self.candidate_generation
            self._candidate = None
            self._check_budget()
            return dict(action="TRACE_PROMOTED", generation=self._retained_generation,
                        candidate_generation=promoted, evicted=evicted)
        replaced = self.candidate_generation
        self._candidate_generation += 1
        self._candidate = ub.CandidateTrace(self._candidate_generation, forming)
        self._check_budget()
        return dict(action="TRACE_CANDIDATE_CREATED" if replaced is None else "TRACE_CANDIDATE_REPLACED",
                    generation=None, candidate_generation=self.candidate_generation, evicted=replaced)

    def hint(self, frame):
        self._check(frame)
        if self._hints:
            tu.need(frame.segment == self._hint_segment and frame.ordinal > self._hints[-1].ordinal, "HINT_ORDER_INVALID")
        else:
            self._hint_segment = frame.segment
        tu.need(len(self._hints) < 2, "HINT_BUFFER_INVALID")
        self._hints.append(frame)
        if len(self._hints) == 1:
            self._check_budget()
            return None
        hint = tuple(self._hints)
        self._hints.clear()
        self._hint_segment = None
        matches = [(trace.generation, offset) for trace in self._retained_many
                   for offset in range(3)
                   if trace.frames[offset].values == hint[0].values
                   and trace.frames[offset + 1].values == hint[1].values]
        self._check_budget()
        return dict(decision="ABSTAIN_NO_RETAINED_TRACE" if not matches else
                    "TRACE_MATCH" if len(matches) == 1 else "ABSTAIN_AMBIGUOUS_RETAINED_TRACE", matches=matches)

    @property
    def inventory(self):
        return tuple(trace.generation for trace in self._retained_many)

    def resources(self):
        retained = len(self._retained_many) * 4
        candidate = 0 if self._candidate is None else 4
        return dict(retained_frames=retained, candidate_frames=candidate,
                    forming_frames=len(self._forming), trace_frames=retained + candidate + len(self._forming),
                    hint_frames=len(self._hints))

    def _check_budget(self):
        tu.need(self.resources()["trace_frames"] <= 16, "TRACE_FRAME_BUDGET_INVALID")

    def close_owner(self):
        super().close_owner()
        self._retained_many.clear()

    def evidence(self):
        value = super().evidence()
        value["retained"] = tuple((trace.generation, trace.frames) for trace in self._retained_many)
        return value


ARMS = {"I1": ImmediateOneArm, "I2": ub.ImmediateTwArm,
        "B1": ub.CandidateConfirmationArm, "B2": CandidateTwoArm}


def retained(arm):
    if isinstance(arm, CandidateTwoArm):
        return tuple(arm._retained_many)
    if isinstance(arm, ub.ImmediateTwArm):
        return tuple(arm.store._retained)
    return () if arm._retained is None else (arm._retained,)
