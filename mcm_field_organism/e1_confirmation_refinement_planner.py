"""Private S1-EB1 completion-aligned r2/r4/r8 confirmation planner."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from typing import Iterable

from .e1_completion_aligned_refinement import (
    E1CompletionAlignedRefinementError,
    _handoff_digest,
    _refined_steps,
    _source_contact_evidence,
)
from .e1_refined_confirmation_contract import (
    E1RefinedConfirmationContract,
    S1_EB_REFINEMENTS,
)
from .field_step_time import MCMFieldStepTime
from .receptor_proposal_handoff import (
    ReceptorProposalHandoff,
    handoff_receptor_completion_groups,
)
from .receptor_time_model import ReceptorTimeSequence


class E1ConfirmationRefinementPlannerError(ValueError):
    """Raised when S1-EB1 changes source evidence or completion timing."""


S1_EB_CONTRACT_DIGEST = (
    "bccf552b7ea69cc083cf65ac0a7d3faacfe7939ff8c7d13c4614f1cf42d06fb4"
)


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class E1ConfirmationRefinementPlan:
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
        if (self.refinement_id, self.factor) not in S1_EB_REFINEMENTS:
            raise E1ConfirmationRefinementPlannerError(
                "S1-EB1 refinement identity changed"
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
            raise E1ConfirmationRefinementPlannerError(
                "S1-EB1 refined horizon or step count changed"
            )
        if any(
            previous.end_tick != current.start_tick
            or previous.clock_id != current.clock_id
            or previous.ticks_per_second != current.ticks_per_second
            for previous, current in zip(steps, steps[1:])
        ):
            raise E1ConfirmationRefinementPlannerError(
                "S1-EB1 steps are not contiguous on one clock"
            )
        if not isinstance(self.handoff, ReceptorProposalHandoff) or (
            self.handoff.completed_before_or_at_start_snapshot_ids
            or self.handoff.completed_after_horizon_snapshot_ids
            or self.handoff.assigned_event_count != self.handoff.source_event_count
            or self.handoff.every_in_horizon_event_assigned_once is not True
        ):
            raise E1ConfirmationRefinementPlannerError(
                "S1-EB1 changed receptor support assignment"
            )
        observed = tuple(
            group.completion_tick
            for batch in self.handoff.batches
            for group in batch.completion_groups
        )
        if observed != self.completion_ticks or any(
            tick not in {step.end_tick for step in steps} for tick in observed
        ):
            raise E1ConfirmationRefinementPlannerError(
                "S1-EB1 moved a receptor completion"
            )
        for role in ("source_contact_digest", "handoff_digest"):
            value = getattr(self, role)
            if len(value) != 64 or any(
                char not in "0123456789abcdef" for char in value
            ):
                raise E1ConfirmationRefinementPlannerError(
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
            raise E1ConfirmationRefinementPlannerError(
                "S1-EB1 source integral is invalid"
            )
        object.__setattr__(self, "proposal_steps", steps)

    def digest(self) -> str:
        return _digest(
            {
                "refinement_id": self.refinement_id,
                "factor": self.factor,
                "horizon": (self.horizon_start_tick, self.horizon_end_tick),
                "base_interval_count": self.base_interval_count,
                "steps": tuple(
                    (
                        item.clock_id,
                        item.start_tick,
                        item.end_tick,
                        item.ticks_per_second,
                    )
                    for item in self.proposal_steps
                ),
                "completion_ticks": self.completion_ticks,
                "source_contact_digest": self.source_contact_digest,
                "source_integrals": (
                    self.source_signed_integral,
                    self.source_absolute_integral,
                    self.source_quadratic_integral,
                ),
                "handoff_digest": self.handoff_digest,
            }
        )


@dataclass(frozen=True, slots=True)
class E1ConfirmationRefinementPlanSet:
    contract_digest: str
    plans: tuple[E1ConfirmationRefinementPlan, ...]
    source_contact_digest: str
    source_event_count: int
    completion_ticks: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.contract_digest != S1_EB_CONTRACT_DIGEST:
            raise E1ConfirmationRefinementPlannerError(
                "S1-EB1 contract binding changed"
            )
        plans = tuple(self.plans)
        if tuple((item.refinement_id, item.factor) for item in plans) != S1_EB_REFINEMENTS:
            raise E1ConfirmationRefinementPlannerError(
                "S1-EB1 requires ordered r2, r4, and r8 plans"
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
            raise E1ConfirmationRefinementPlannerError(
                "S1-EB1 refinements changed source, horizon, or integrals"
            )
        object.__setattr__(self, "plans", plans)

    def digest(self) -> str:
        return _digest(asdict(self))


def build_e1_confirmation_refinement_plans(
    contract: E1RefinedConfirmationContract,
    sequences: Iterable[ReceptorTimeSequence],
    *,
    horizon_start_tick: int,
    horizon_end_tick: int,
    ticks_per_second: float,
) -> E1ConfirmationRefinementPlanSet:
    """Build r2/r4/r8 plans without advancing an E1 or field state."""

    if not isinstance(contract, E1RefinedConfirmationContract) or (
        contract.digest() != S1_EB_CONTRACT_DIGEST
    ):
        raise E1ConfirmationRefinementPlannerError(
            "S1-EB1 requires the current S1-EB contract"
        )
    sequences_in = tuple(sequences)
    if not sequences_in or any(
        not isinstance(item, ReceptorTimeSequence) for item in sequences_in
    ):
        raise E1ConfirmationRefinementPlannerError(
            "S1-EB1 requires receptor time sequences"
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
        raise E1ConfirmationRefinementPlannerError(
            "S1-EB1 clock or horizon is invalid"
        )
    rate = float(ticks_per_second)
    if not math.isfinite(rate) or rate <= 0.0:
        raise E1ConfirmationRefinementPlannerError(
            "S1-EB1 clock rate is invalid"
        )
    completion_ticks = tuple(sorted({
        item.field_time.window_end_tick
        for sequence in sequences_in
        for item in sequence.frames
    }))
    if not completion_ticks or any(
        tick <= horizon_start_tick or tick > horizon_end_tick
        for tick in completion_ticks
    ):
        raise E1ConfirmationRefinementPlannerError(
            "S1-EB1 requires every completion inside the full horizon"
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
        for refinement_id, factor in S1_EB_REFINEMENTS:
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
        raise E1ConfirmationRefinementPlannerError(str(exc)) from exc
    return E1ConfirmationRefinementPlanSet(
        contract_digest=contract.digest(),
        plans=tuple(plans),
        source_contact_digest=source_digest,
        source_event_count=plans[0].handoff.source_event_count,
        completion_ticks=completion_ticks,
    )
