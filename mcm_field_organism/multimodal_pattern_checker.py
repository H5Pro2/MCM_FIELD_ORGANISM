"""Passive checker for constellations emitted by the modular MCM distributor."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Callable, Iterable

from .mcm_distributor import DistributedMCMConstellation, MCMDistributionError, MCMFieldWindow


class TemporalRelation(str, Enum):
    SINGLE = "single"
    OVERLAP = "overlap"
    DISJOINT = "disjoint"


@dataclass(frozen=True, slots=True)
class MultimodalPatternResult:
    modality_ids: tuple[str, ...]
    dock_ids: tuple[str, ...]
    temporal_relation: TemporalRelation
    overlap_start_tick: int | None
    overlap_end_tick: int | None
    modality_digests: tuple[tuple[str, str], ...]
    carrier_count: int
    constellation_digest: str

    def canonical_payload(self) -> dict[str, object]:
        return {
            "modality_ids": list(self.modality_ids),
            "dock_ids": list(self.dock_ids),
            "temporal_relation": self.temporal_relation.value,
            "overlap_start_tick": self.overlap_start_tick,
            "overlap_end_tick": self.overlap_end_tick,
            "modality_digests": [list(item) for item in self.modality_digests],
            "carrier_count": self.carrier_count,
            "constellation_digest": self.constellation_digest,
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


Observer = Callable[[MultimodalPatternResult], object]


class MultimodalPatternChecker:
    def check(
        self,
        constellation: DistributedMCMConstellation,
        *,
        observer: Observer | None = None,
    ) -> MultimodalPatternResult:
        states = constellation.states
        if not states:
            raise MCMDistributionError("pattern check requires at least one distributed field state")
        if len(states) == 1:
            relation = TemporalRelation.SINGLE
            overlap_start = states[0].window_start_tick
            overlap_end = states[0].window_end_tick
        else:
            candidate_start = max(state.window_start_tick for state in states)
            candidate_end = min(state.window_end_tick for state in states)
            if candidate_start < candidate_end:
                relation = TemporalRelation.OVERLAP
                overlap_start = candidate_start
                overlap_end = candidate_end
            else:
                relation = TemporalRelation.DISJOINT
                overlap_start = None
                overlap_end = None

        result = MultimodalPatternResult(
            modality_ids=constellation.modality_ids,
            dock_ids=constellation.dock_ids,
            temporal_relation=relation,
            overlap_start_tick=overlap_start,
            overlap_end_tick=overlap_end,
            modality_digests=tuple((state.modality_id, state.digest()) for state in states),
            carrier_count=sum(len(state.carrier_ids) for state in states),
            constellation_digest=constellation.digest(),
        )
        before = result.digest()
        if observer is not None:
            observer(result)
        if result.digest() != before:
            raise MCMDistributionError("observer changed an immutable pattern result")
        return result


def global_sum_collision_baseline(states: Iterable[MCMFieldWindow]) -> tuple[float, ...]:
    field_states = tuple(states)
    if not field_states:
        return ()
    width = len(field_states[0].activation)
    if any(len(state.activation) != width for state in field_states):
        raise MCMDistributionError("global sum baseline requires equal activation geometry")
    return tuple(sum(state.activation[index] for state in field_states) for index in range(width))
