"""Private S1-DT planner for completion-aligned E1 time refinement."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Iterable

from .e1_refined_world_formation_contract import S1_DS_REFINEMENTS
from .field_step_time import MCMFieldStepTime
from .receptor_proposal_handoff import (
    ReceptorProposalHandoff,
    handoff_receptor_completion_groups,
)
from .receptor_time_model import ReceptorTimeSequence


class E1CompletionAlignedRefinementError(ValueError):
    """Raised when a refinement would alter time or receptor evidence."""


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _source_contact_evidence(
    sequences: tuple[ReceptorTimeSequence, ...],
    ticks_per_second: float,
) -> tuple[str, float, float, float]:
    payload = []
    signed_terms = []
    absolute_terms = []
    quadratic_terms = []
    for sequence in sequences:
        for item in sequence.frames:
            duration = (
                item.field_time.window_end_tick
                - item.field_time.window_start_tick
            ) / ticks_per_second
            values = tuple(item.frame.values)
            payload.append(
                (
                    sequence.modality_id,
                    item.frame.snapshot_id,
                    item.field_time.window_start_tick,
                    item.field_time.window_end_tick,
                    tuple(item.frame.carrier_ids),
                    values,
                )
            )
            signed_terms.extend(duration * value for value in values)
            absolute_terms.extend(duration * abs(value) for value in values)
            quadratic_terms.extend(duration * value * value for value in values)
    return (
        _digest(sorted(payload, key=repr)),
        math.fsum(signed_terms),
        math.fsum(absolute_terms),
        math.fsum(quadratic_terms),
    )


def _handoff_digest(handoff: ReceptorProposalHandoff) -> str:
    return _digest(
        {
            "clock_id": handoff.clock_id,
            "modality_ids": handoff.modality_ids,
            "source_event_count": handoff.source_event_count,
            "assigned_event_count": handoff.assigned_event_count,
            "assigned_once": handoff.every_in_horizon_event_assigned_once,
            "assignments": [
                (
                    group.completion_tick,
                    tuple(
                        (item.frame.modality_id, item.frame.snapshot_id)
                        for item in group.timed_frames
                    ),
                )
                for batch in handoff.batches
                for group in batch.completion_groups
            ],
        }
    )


@dataclass(frozen=True, slots=True)
class E1CompletionAlignedRefinementPlan:
    refinement_id: str
    factor: int
    horizon_start_tick: int
    horizon_end_tick: int
    base_interval_count: int
    proposal_steps: tuple[MCMFieldStepTime, ...]
    handoff: ReceptorProposalHandoff
    completion_ticks: tuple[int, ...]
    source_contact_digest: str
    source_signed_integral: float
    source_absolute_integral: float
    source_quadratic_integral: float
    handoff_digest: str

    def __post_init__(self) -> None:
        if (self.refinement_id, self.factor) not in S1_DS_REFINEMENTS:
            raise E1CompletionAlignedRefinementError(
                "S1-DT refinement identity changed"
            )
        steps = tuple(self.proposal_steps)
        if (
            self.horizon_start_tick < 0
            or self.horizon_end_tick <= self.horizon_start_tick
            or self.base_interval_count < 1
            or len(steps) != self.base_interval_count * self.factor
            or not steps
            or steps[0].start_tick != self.horizon_start_tick
            or steps[-1].end_tick != self.horizon_end_tick
        ):
            raise E1CompletionAlignedRefinementError(
                "S1-DT refined horizon or step count changed"
            )
        if any(
            previous.end_tick != current.start_tick
            or previous.clock_id != current.clock_id
            or previous.ticks_per_second != current.ticks_per_second
            for previous, current in zip(steps, steps[1:])
        ):
            raise E1CompletionAlignedRefinementError(
                "S1-DT steps must remain contiguous on one clock"
            )
        if not isinstance(self.handoff, ReceptorProposalHandoff):
            raise E1CompletionAlignedRefinementError(
                "S1-DT requires one receptor handoff"
            )
        if (
            self.handoff.completed_before_or_at_start_snapshot_ids
            or self.handoff.completed_after_horizon_snapshot_ids
            or self.handoff.assigned_event_count
            != self.handoff.source_event_count
            or self.handoff.every_in_horizon_event_assigned_once is not True
        ):
            raise E1CompletionAlignedRefinementError(
                "S1-DT changed receptor support assignment"
            )
        observed_ticks = tuple(
            group.completion_tick
            for batch in self.handoff.batches
            for group in batch.completion_groups
        )
        if observed_ticks != self.completion_ticks or any(
            tick not in {step.end_tick for step in steps}
            for tick in observed_ticks
        ):
            raise E1CompletionAlignedRefinementError(
                "S1-DT moved a receptor completion"
            )
        for role in ("source_contact_digest", "handoff_digest"):
            value = getattr(self, role)
            if len(value) != 64 or any(
                char not in "0123456789abcdef" for char in value
            ):
                raise E1CompletionAlignedRefinementError(
                    f"{role} is not SHA-256"
                )
        if any(
            not math.isfinite(value)
            for value in (
                self.source_signed_integral,
                self.source_absolute_integral,
                self.source_quadratic_integral,
            )
        ) or self.source_absolute_integral < 0.0 or self.source_quadratic_integral < 0.0:
            raise E1CompletionAlignedRefinementError(
                "S1-DT source integral is invalid"
            )
        object.__setattr__(self, "proposal_steps", steps)

    def digest(self) -> str:
        return _digest(
            {
                "refinement_id": self.refinement_id,
                "factor": self.factor,
                "horizon": [self.horizon_start_tick, self.horizon_end_tick],
                "base_interval_count": self.base_interval_count,
                "steps": [
                    (
                        item.clock_id,
                        item.start_tick,
                        item.end_tick,
                        item.ticks_per_second,
                    )
                    for item in self.proposal_steps
                ],
                "completion_ticks": self.completion_ticks,
                "source_contact_digest": self.source_contact_digest,
                "source_integrals": [
                    self.source_signed_integral,
                    self.source_absolute_integral,
                    self.source_quadratic_integral,
                ],
                "handoff_digest": self.handoff_digest,
            }
        )


@dataclass(frozen=True, slots=True)
class E1CompletionAlignedRefinementPlanSet:
    plans: tuple[E1CompletionAlignedRefinementPlan, ...]
    source_contact_digest: str
    source_event_count: int
    completion_ticks: tuple[int, ...]

    def __post_init__(self) -> None:
        plans = tuple(self.plans)
        if tuple((item.refinement_id, item.factor) for item in plans) != (
            S1_DS_REFINEMENTS
        ):
            raise E1CompletionAlignedRefinementError(
                "S1-DT requires ordered r1, r2, and r4 plans"
            )
        first = plans[0]
        if self.source_event_count < 1 or any(
            item.source_contact_digest != self.source_contact_digest
            or item.handoff.source_event_count != self.source_event_count
            or item.completion_ticks != self.completion_ticks
            or item.horizon_start_tick != first.horizon_start_tick
            or item.horizon_end_tick != first.horizon_end_tick
            or item.source_signed_integral != first.source_signed_integral
            or item.source_absolute_integral != first.source_absolute_integral
            or item.source_quadratic_integral != first.source_quadratic_integral
            for item in plans
        ):
            raise E1CompletionAlignedRefinementError(
                "S1-DT refinements changed source, horizon, or contact integral"
            )
        object.__setattr__(self, "plans", plans)

    def digest(self) -> str:
        return _digest(
            {
                "plan_digests": [item.digest() for item in self.plans],
                "source_contact_digest": self.source_contact_digest,
                "source_event_count": self.source_event_count,
                "completion_ticks": self.completion_ticks,
            }
        )


def _refined_steps(
    clock_id: str,
    ticks_per_second: float,
    boundaries: tuple[int, ...],
    factor: int,
) -> tuple[MCMFieldStepTime, ...]:
    steps = []
    for start_tick, end_tick in zip(boundaries, boundaries[1:]):
        elapsed = end_tick - start_tick
        if elapsed % factor:
            raise E1CompletionAlignedRefinementError(
                "completion interval is not exactly divisible by refinement"
            )
        width = elapsed // factor
        steps.extend(
            MCMFieldStepTime(
                clock_id,
                start_tick + index * width,
                start_tick + (index + 1) * width,
                ticks_per_second,
            )
            for index in range(factor)
        )
    return tuple(steps)


def build_e1_completion_aligned_refinement_plans(
    sequences: Iterable[ReceptorTimeSequence],
    *,
    horizon_start_tick: int,
    horizon_end_tick: int,
    ticks_per_second: float,
) -> E1CompletionAlignedRefinementPlanSet:
    """Plan r1/r2/r4 without advancing an E1 or field state."""

    sequences_in = tuple(sequences)
    if not sequences_in or any(
        not isinstance(item, ReceptorTimeSequence) for item in sequences_in
    ):
        raise E1CompletionAlignedRefinementError(
            "S1-DT requires receptor time sequences"
        )
    clock_ids = {item.clock_id for item in sequences_in}
    if len(clock_ids) != 1:
        raise E1CompletionAlignedRefinementError(
            "S1-DT sequences must share one organism clock"
        )
    if (
        isinstance(horizon_start_tick, bool)
        or isinstance(horizon_end_tick, bool)
        or not isinstance(horizon_start_tick, int)
        or not isinstance(horizon_end_tick, int)
        or horizon_start_tick < 0
        or horizon_end_tick <= horizon_start_tick
    ):
        raise E1CompletionAlignedRefinementError(
            "S1-DT horizon is invalid"
        )
    rate = float(ticks_per_second)
    if not math.isfinite(rate) or rate <= 0.0:
        raise E1CompletionAlignedRefinementError(
            "S1-DT clock rate is invalid"
        )
    completion_ticks = tuple(
        sorted(
            {
                item.field_time.window_end_tick
                for sequence in sequences_in
                for item in sequence.frames
            }
        )
    )
    if not completion_ticks or any(
        tick <= horizon_start_tick or tick > horizon_end_tick
        for tick in completion_ticks
    ):
        raise E1CompletionAlignedRefinementError(
            "S1-DT requires every completion inside the full horizon"
        )
    boundaries = (horizon_start_tick,) + completion_ticks
    if boundaries[-1] != horizon_end_tick:
        boundaries += (horizon_end_tick,)
    source_digest, signed, absolute, quadratic = _source_contact_evidence(
        sequences_in, rate
    )
    plans = []
    clock_id = next(iter(clock_ids))
    for refinement_id, factor in S1_DS_REFINEMENTS:
        steps = _refined_steps(clock_id, rate, boundaries, factor)
        try:
            handoff = handoff_receptor_completion_groups(sequences_in, steps)
        except ValueError as exc:
            raise E1CompletionAlignedRefinementError(str(exc)) from exc
        plans.append(
            E1CompletionAlignedRefinementPlan(
                refinement_id=refinement_id,
                factor=factor,
                horizon_start_tick=horizon_start_tick,
                horizon_end_tick=horizon_end_tick,
                base_interval_count=len(boundaries) - 1,
                proposal_steps=steps,
                handoff=handoff,
                completion_ticks=completion_ticks,
                source_contact_digest=source_digest,
                source_signed_integral=signed,
                source_absolute_integral=absolute,
                source_quadratic_integral=quadratic,
                handoff_digest=_handoff_digest(handoff),
            )
        )
    return E1CompletionAlignedRefinementPlanSet(
        plans=tuple(plans),
        source_contact_digest=source_digest,
        source_event_count=plans[0].handoff.source_event_count,
        completion_ticks=completion_ticks,
    )
