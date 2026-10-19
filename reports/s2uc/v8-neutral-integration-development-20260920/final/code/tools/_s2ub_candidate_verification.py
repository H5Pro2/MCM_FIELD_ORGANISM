"""Independent direct replay for the private S2-UA candidate rule."""
from __future__ import annotations

from tools import _s2tu_retained_trace as tu


def replay(groups: tuple[tuple[tu.Frame, ...], ...]) -> dict[str, object]:
    """Recompute promotion and one-slot FIFO without using the productive arm."""
    candidate: tuple[int, tuple[tu.Frame, ...]] | None = None
    retained: tuple[int, tuple[tu.Frame, ...]] | None = None
    next_candidate = 0
    next_retained = 0
    transitions: list[dict[str, object]] = []
    for frames in groups:
        if len(frames) != 4:
            raise ValueError("TRACE_LENGTH_INVALID")
        values = tuple(frame.values for frame in frames)
        if retained is not None and tuple(frame.values for frame in retained[1]) == values:
            transitions.append({"action": "TRACE_CONFIRMED", "generation": retained[0], "candidate_generation": None if candidate is None else candidate[0], "evicted": None})
        elif candidate is not None and tuple(frame.values for frame in candidate[1]) == values:
            if {frame.ordinal for frame in candidate[1]} & {frame.ordinal for frame in frames}:
                transitions.append({"action": "TRACE_CANDIDATE_OVERLAP_NOT_CONFIRMED", "generation": None, "candidate_generation": candidate[0], "evicted": None})
            else:
                next_retained += 1
                evicted = None if retained is None else retained[0]
                retained = (next_retained, candidate[1])
                transitions.append({"action": "TRACE_PROMOTED", "generation": next_retained, "candidate_generation": candidate[0], "evicted": evicted})
                candidate = None
        else:
            replaced = None if candidate is None else candidate[0]
            next_candidate += 1
            candidate = (next_candidate, frames)
            transitions.append({"action": "TRACE_CANDIDATE_CREATED" if replaced is None else "TRACE_CANDIDATE_REPLACED", "generation": None, "candidate_generation": next_candidate, "evicted": replaced})
    return {
        "transitions": transitions,
        "inventory": () if retained is None else (retained[0],),
        "candidate_generation": None if candidate is None else candidate[0],
        "retained": retained,
        "candidate": candidate,
    }


def hint(retained: tuple[int, tuple[tu.Frame, ...]] | None, frames: tuple[tu.Frame, tu.Frame]) -> dict[str, object]:
    """Recompute all three ordered hint offsets from retained data only."""
    matches = [] if retained is None else [
        (retained[0], offset)
        for offset in range(3)
        if retained[1][offset].values == frames[0].values
        and retained[1][offset + 1].values == frames[1].values
    ]
    decision = "ABSTAIN_NO_RETAINED_TRACE" if not matches else "TRACE_MATCH" if len(matches) == 1 else "ABSTAIN_AMBIGUOUS_RETAINED_TRACE"
    return {"decision": decision, "matches": matches}


def require_equal(observed: dict[str, object], expected: dict[str, object], code: str) -> None:
    if observed != expected:
        raise ValueError(code)
