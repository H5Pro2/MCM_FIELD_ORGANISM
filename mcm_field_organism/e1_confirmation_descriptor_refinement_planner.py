"""Private S1-EC4 refinement planner bound to the S1-EC3 descriptor."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Iterable

from .e1_completion_aligned_refinement import (
    E1CompletionAlignedRefinementError,
    _handoff_digest,
    _refined_steps,
    _source_contact_evidence,
)
from .e1_confirmation_refinement_planner import E1ConfirmationRefinementPlan
from .e1_confirmation_research_corridor import (
    E1ConfirmationResearchCorridorDescriptor,
)
from .e1_refined_confirmation_contract import S1_EB_REFINEMENTS, _digest
from .receptor_proposal_handoff import handoff_receptor_completion_groups
from .receptor_time_model import ReceptorTimeSequence


class E1ConfirmationDescriptorRefinementPlannerError(ValueError):
    """Raised when an S1-EC4 plan changes descriptor-bound evidence."""


@dataclass(frozen=True, slots=True)
class E1ConfirmationDescriptorRefinementPlanSet:
    research_descriptor_digest: str
    plans: tuple[E1ConfirmationRefinementPlan, ...]
    source_contact_digest: str
    source_event_count: int
    completion_ticks: tuple[int, ...]

    def __post_init__(self) -> None:
        if (
            len(self.research_descriptor_digest) != 64
            or any(
                char not in "0123456789abcdef"
                for char in self.research_descriptor_digest
            )
        ):
            raise E1ConfirmationDescriptorRefinementPlannerError(
                "S1-EC4 descriptor digest is not SHA-256"
            )
        plans = tuple(self.plans)
        if tuple((item.refinement_id, item.factor) for item in plans) != S1_EB_REFINEMENTS:
            raise E1ConfirmationDescriptorRefinementPlannerError(
                "S1-EC4 requires ordered r2, r4, and r8 plans"
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
            raise E1ConfirmationDescriptorRefinementPlannerError(
                "S1-EC4 refinements changed source, horizon, or integrals"
            )
        object.__setattr__(self, "plans", plans)

    def digest(self) -> str:
        return _digest(asdict(self))


def build_e1_confirmation_descriptor_refinement_plans(
    descriptor: E1ConfirmationResearchCorridorDescriptor,
    sequences: Iterable[ReceptorTimeSequence],
    *,
    horizon_start_tick: int,
    horizon_end_tick: int,
    ticks_per_second: float,
) -> E1ConfirmationDescriptorRefinementPlanSet:
    """Build descriptor-bound plans without consulting any run target path."""

    if not isinstance(descriptor, E1ConfirmationResearchCorridorDescriptor):
        raise E1ConfirmationDescriptorRefinementPlannerError(
            "S1-EC4 requires one S1-EC3 research descriptor"
        )
    sequences_in = tuple(sequences)
    if not sequences_in or any(
        not isinstance(item, ReceptorTimeSequence) for item in sequences_in
    ):
        raise E1ConfirmationDescriptorRefinementPlannerError(
            "S1-EC4 requires receptor time sequences"
        )
    clock_ids = {item.clock_id for item in sequences_in}
    if len(clock_ids) != 1 or (
        isinstance(horizon_start_tick, bool)
        or isinstance(horizon_end_tick, bool)
        or not isinstance(horizon_start_tick, int)
        or not isinstance(horizon_end_tick, int)
        or horizon_start_tick < 0
        or horizon_end_tick <= horizon_start_tick
    ):
        raise E1ConfirmationDescriptorRefinementPlannerError(
            "S1-EC4 clock or horizon is invalid"
        )
    rate = float(ticks_per_second)
    if not math.isfinite(rate) or rate <= 0.0:
        raise E1ConfirmationDescriptorRefinementPlannerError(
            "S1-EC4 clock rate is invalid"
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
        raise E1ConfirmationDescriptorRefinementPlannerError(
            "S1-EC4 requires every completion inside the full horizon"
        )
    boundaries = (horizon_start_tick,) + completion_ticks
    if boundaries[-1] != horizon_end_tick:
        boundaries += (horizon_end_tick,)
    source_digest, signed, absolute, quadratic = _source_contact_evidence(
        sequences_in, rate
    )
    clock_id = next(iter(clock_ids))
    plans = []
    try:
        for refinement_id, factor in descriptor.refinements:
            steps = _refined_steps(clock_id, rate, boundaries, factor)
            handoff = handoff_receptor_completion_groups(sequences_in, steps)
            plans.append(
                E1ConfirmationRefinementPlan(
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
    except (E1CompletionAlignedRefinementError, ValueError) as exc:
        raise E1ConfirmationDescriptorRefinementPlannerError(str(exc)) from exc
    return E1ConfirmationDescriptorRefinementPlanSet(
        research_descriptor_digest=descriptor.digest(),
        plans=tuple(plans),
        source_contact_digest=source_digest,
        source_event_count=plans[0].handoff.source_event_count,
        completion_ticks=completion_ticks,
    )
