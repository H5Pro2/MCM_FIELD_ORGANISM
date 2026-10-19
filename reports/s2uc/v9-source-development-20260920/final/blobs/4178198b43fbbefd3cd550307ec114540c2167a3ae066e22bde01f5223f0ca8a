"""Private, bounded comparison between S2-TW and delayed exact promotion."""
from __future__ import annotations

from dataclasses import dataclass

from tools import _s2tu_retained_trace as tu
from tools import _s2tw_exact_confirmation as tw


TRACE_FRAMES = 4
TRACE_STORAGE_LIMIT = 12


@dataclass(frozen=True, slots=True)
class CandidateTrace:
    candidate_generation: int
    frames: tuple[tu.Frame, ...]


def _same_values(left: tuple[tu.Frame, ...], right: tuple[tu.Frame, ...]) -> bool:
    return tuple(frame.values for frame in left) == tuple(frame.values for frame in right)


def _disjoint_ordinals(left: tuple[tu.Frame, ...], right: tuple[tu.Frame, ...]) -> bool:
    return not ({frame.ordinal for frame in left} & {frame.ordinal for frame in right})


class ImmediateTwArm:
    """One forming segment plus the unchanged two-slot S2-TW store."""

    def __init__(self, profile: str, owner: str) -> None:
        self.store = tw.ExactConfirmationStore(profile, owner)
        self._forming_segment: str | None = None
        self._hint_segment: str | None = None

    def form(self, frame: tu.Frame) -> str:
        self._require_open()
        tu.need(not any(self.store._hints.values()), "HINT_BUFFER_PENDING")
        if self._forming_segment is None:
            self._forming_segment = frame.segment
        else:
            tu.need(frame.segment == self._forming_segment, "FORMATION_ORDER_INVALID")
        result = self.store.form(frame)
        self._check_budget()
        return result

    def close_segment(self, segment: str) -> dict[str, object]:
        self._require_open()
        tu.need(segment == self._forming_segment, "SEGMENT_INVALID")
        result = self.store.close_segment(segment)
        self._forming_segment = None
        self._check_budget()
        return result

    def hint(self, frame: tu.Frame) -> dict[str, object] | None:
        self._require_open()
        if self._hint_segment is None:
            self._hint_segment = frame.segment
        else:
            tu.need(frame.segment == self._hint_segment, "HINT_ORDER_INVALID")
        result = self.store.hint(frame)
        if result is not None:
            self._hint_segment = None
        self._check_budget()
        return result

    @property
    def inventory(self) -> tuple[int, ...]:
        return self.store.inventory

    def resources(self) -> dict[str, int]:
        forming = sum(len(frames) for frames in self.store._forming.values())
        hints = sum(len(frames) for frames in self.store._hints.values())
        return {
            "retained_frames": len(self.store.inventory) * TRACE_FRAMES,
            "candidate_frames": 0,
            "forming_frames": forming,
            "trace_frames": len(self.store.inventory) * TRACE_FRAMES + forming,
            "hint_frames": hints,
        }

    def close_owner(self) -> None:
        self.store.close_owner()
        self._forming_segment = None
        self._hint_segment = None

    def evidence(self) -> dict[str, object]:
        return {
            "profile": self.store.profile,
            "owner": self.store.owner,
            "closed": self.store._closed,
            "forming": tuple((segment, tuple(frames)) for segment, frames in sorted(self.store._forming.items()) if frames),
            "retained": tuple((trace.generation, trace.frames) for trace in self.store._retained),
            "hints": tuple((segment, tuple(frames)) for segment, frames in sorted(self.store._hints.items()) if frames),
        }

    def _require_open(self) -> None:
        tu.need(not self.store._closed, "FRAME_SCOPE_INVALID")

    def _check_budget(self) -> None:
        tu.need(self.resources()["trace_frames"] <= TRACE_STORAGE_LIMIT, "TRACE_FRAME_BUDGET_INVALID")


class CandidateConfirmationArm:
    """One forming trace, one candidate, and one retained trace; hints are read-only."""

    def __init__(self, profile: str, owner: str) -> None:
        self.profile, self.owner = profile, owner
        self._forming: list[tu.Frame] = []
        self._forming_segment: str | None = None
        self._candidate: CandidateTrace | None = None
        self._retained: tu.RetainedTrace | None = None
        self._hints: list[tu.Frame] = []
        self._hint_segment: str | None = None
        self._candidate_generation = 0
        self._retained_generation = 0
        self._closed = False

    def _check(self, frame: tu.Frame) -> None:
        tu.need(not self._closed and frame.profile == self.profile and frame.owner == self.owner, "FRAME_SCOPE_INVALID")

    def form(self, frame: tu.Frame) -> str:
        self._check(frame)
        tu.need(not self._hints, "HINT_BUFFER_PENDING")
        if self._forming:
            tu.need(frame.segment == self._forming_segment and frame.ordinal > self._forming[-1].ordinal, "FORMATION_ORDER_INVALID")
        else:
            self._forming_segment = frame.segment
        tu.need(len(self._forming) < TRACE_FRAMES, "FORMATION_CAPACITY_INVALID")
        self._forming.append(frame)
        self._check_budget()
        return "TRACE_COMPLETE" if len(self._forming) == TRACE_FRAMES else "TRACE_FORMING"

    def close_segment(self, segment: str) -> dict[str, object]:
        tu.need(not self._closed and segment == self._forming_segment, "SEGMENT_INVALID")
        forming = tuple(self._forming)
        self._forming.clear()
        self._forming_segment = None
        if len(forming) != TRACE_FRAMES:
            self._check_budget()
            return {"action": "TRACE_DISCARDED_INCOMPLETE", "generation": None, "candidate_generation": None, "evicted": None}
        if self._retained is not None and _same_values(self._retained.frames, forming):
            self._check_budget()
            return {"action": "TRACE_CONFIRMED", "generation": self._retained.generation, "candidate_generation": self.candidate_generation, "evicted": None}
        if self._candidate is not None and _same_values(self._candidate.frames, forming):
            if not _disjoint_ordinals(self._candidate.frames, forming):
                self._check_budget()
                return {"action": "TRACE_CANDIDATE_OVERLAP_NOT_CONFIRMED", "generation": None, "candidate_generation": self._candidate.candidate_generation, "evicted": None}
            self._retained_generation += 1
            evicted = None if self._retained is None else self._retained.generation
            self._retained = tu.RetainedTrace(self._retained_generation, self._candidate.frames)
            promoted = self._candidate.candidate_generation
            self._candidate = None
            self._check_budget()
            return {"action": "TRACE_PROMOTED", "generation": self._retained.generation, "candidate_generation": promoted, "evicted": evicted}
        replaced = None if self._candidate is None else self._candidate.candidate_generation
        self._candidate_generation += 1
        self._candidate = CandidateTrace(self._candidate_generation, forming)
        self._check_budget()
        return {"action": "TRACE_CANDIDATE_CREATED" if replaced is None else "TRACE_CANDIDATE_REPLACED", "generation": None, "candidate_generation": self._candidate_generation, "evicted": replaced}

    def hint(self, frame: tu.Frame) -> dict[str, object] | None:
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
        matches = [] if self._retained is None else [
            (self._retained.generation, offset)
            for offset in range(TRACE_FRAMES - 1)
            if self._retained.frames[offset].values == hint[0].values
            and self._retained.frames[offset + 1].values == hint[1].values
        ]
        decision = "ABSTAIN_NO_RETAINED_TRACE" if not matches else "TRACE_MATCH" if len(matches) == 1 else "ABSTAIN_AMBIGUOUS_RETAINED_TRACE"
        self._check_budget()
        return {"decision": decision, "matches": matches}

    @property
    def inventory(self) -> tuple[int, ...]:
        return () if self._retained is None else (self._retained.generation,)

    @property
    def candidate_generation(self) -> int | None:
        return None if self._candidate is None else self._candidate.candidate_generation

    def resources(self) -> dict[str, int]:
        retained = 0 if self._retained is None else TRACE_FRAMES
        candidate = 0 if self._candidate is None else TRACE_FRAMES
        return {
            "retained_frames": retained,
            "candidate_frames": candidate,
            "forming_frames": len(self._forming),
            "trace_frames": retained + candidate + len(self._forming),
            "hint_frames": len(self._hints),
        }

    def close_owner(self) -> None:
        self._forming.clear()
        self._hints.clear()
        self._candidate = None
        self._retained = None
        self._closed = True

    def evidence(self) -> dict[str, object]:
        return {
            "profile": self.profile,
            "owner": self.owner,
            "closed": self._closed,
            "forming": tuple(self._forming),
            "candidate": None if self._candidate is None else (self._candidate.candidate_generation, self._candidate.frames),
            "retained": None if self._retained is None else (self._retained.generation, self._retained.frames),
            "hints": tuple(self._hints),
        }

    def _check_budget(self) -> None:
        tu.need(self.resources()["trace_frames"] <= TRACE_STORAGE_LIMIT, "TRACE_FRAME_BUDGET_INVALID")
