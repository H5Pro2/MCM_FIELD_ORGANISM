"""Candidate-open passive comparison of coarse and fine field observations."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
from typing import Callable, Iterable

from .field_step_time import MCMFieldStepTime
from .mcm_neuron_layer import MCMNeuronTransition
from .passive_field_controls import (
    PassiveDriveRole,
    PassiveDriveRoleMask,
    PassiveLocalTransition,
    adapt_passive_local_transition,
    all_passive_drive_roles,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff_audit import (
    ReceptorProposalBatch,
    ReceptorProposalHandoff,
    handoff_receptor_completion_groups,
)
from .receptor_time_alignment import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class PassiveFieldSegmentationError(ValueError):
    """Raised when two passive observation branches are not comparable."""


FieldFactory = Callable[[], SharedMCMField]
TransitionFactory = Callable[[], MCMNeuronTransition]
BoundaryDistributionFactory = Callable[[ReceptorProposalBatch], ReceptorDistribution]


@dataclass(frozen=True, slots=True)
class PassiveNeuronEndpoint:
    """Fast local field state without technical observation counters."""

    neuron_id: str
    activation: float
    afterimage: float


@dataclass(frozen=True, slots=True)
class PassiveFieldEndpoint:
    """Comparable physical endpoint of one passive branch."""

    neurons: tuple[PassiveNeuronEndpoint, ...]


@dataclass(frozen=True, slots=True)
class PassiveSegmentationStep:
    """One observed proposal result with its unreduced event count."""

    step_index: int
    step_time: MCMFieldStepTime
    event_count: int
    modality_event_counts: tuple[tuple[str, int], ...]
    technical_layer_tick: int
    endpoint: PassiveFieldEndpoint


@dataclass(frozen=True, slots=True)
class PassiveSegmentationBranch:
    """One independently rebuilt branch for one explicit segmentation."""

    segmentation_id: str
    initial_field_digest: str
    source_event_count: int
    assigned_event_count: int
    every_event_assigned_once: bool
    steps: tuple[PassiveSegmentationStep, ...]
    endpoint: PassiveFieldEndpoint


@dataclass(frozen=True, slots=True)
class PassiveFieldSegmentationComparison:
    """Technical comparison result without candidate interpretation."""

    coarse: PassiveSegmentationBranch
    fine: PassiveSegmentationBranch
    coarse_reproducible: bool
    fine_reproducible: bool
    endpoints_equal: bool


@dataclass(frozen=True, slots=True)
class PassiveFieldRoleAblation:
    """One local role removal compared with the complete passive view."""

    role: PassiveDriveRole
    comparison: PassiveFieldSegmentationComparison
    coarse_endpoint_changed: bool
    fine_endpoint_changed: bool


@dataclass(frozen=True, slots=True)
class PassiveFieldRoleAblationComparison:
    """Complete local view plus every independent single-role ablation."""

    reference: PassiveFieldSegmentationComparison
    ablations: tuple[PassiveFieldRoleAblation, ...]


def contact_free_boundary_distribution(
    batch: ReceptorProposalBatch,
) -> ReceptorDistribution:
    """Represent one observation boundary without a fabricated scalar contact."""

    if not isinstance(batch, ReceptorProposalBatch):
        raise PassiveFieldSegmentationError(
            "contact-free boundary requires one receptor proposal batch"
        )
    return ReceptorDistribution(
        CommonFieldTime(
            batch.step_time.clock_id,
            batch.step_time.start_tick,
            batch.step_time.end_tick,
        ),
        (),
    )


def _steps(
    values: Iterable[MCMFieldStepTime],
    role: str,
) -> tuple[MCMFieldStepTime, ...]:
    result = tuple(values)
    if not result or any(not isinstance(item, MCMFieldStepTime) for item in result):
        raise PassiveFieldSegmentationError(
            f"{role} requires explicit field observation spans"
        )
    return result


def _endpoint(field: SharedMCMField) -> PassiveFieldEndpoint:
    return PassiveFieldEndpoint(
        neurons=tuple(
            PassiveNeuronEndpoint(
                neuron_id=neuron.neuron_id,
                activation=neuron.activation,
                afterimage=neuron.afterimage,
            )
            for neuron in sorted(
                field.layer.neurons,
                key=lambda item: item.neuron_id,
            )
        )
    )


def _initial_field(field_factory: FieldFactory) -> SharedMCMField:
    if not callable(field_factory):
        raise PassiveFieldSegmentationError("field_factory must be callable")
    field = field_factory()
    if not isinstance(field, SharedMCMField):
        raise PassiveFieldSegmentationError(
            "field_factory must return one shared MCM field"
        )
    if field.last_distribution is not None:
        raise PassiveFieldSegmentationError(
            "every passive branch must start from one fresh shared MCM field"
        )
    return field


def _initial_field_digest(field: SharedMCMField) -> str:
    payload = {
        "layer_digest": field.layer.digest(),
        "docks": [
            {
                "dock_id": dock.dock_id,
                "modality_id": dock.dock_map.modality_id,
                "receptor_geometry_id": dock.dock_map.receptor_geometry_id,
                "pairs": [list(pair) for pair in dock.dock_map.pairs],
            }
            for dock in field.docks
        ],
    }
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _run_branch(
    segmentation_id: str,
    handoff: ReceptorProposalHandoff,
    field_factory: FieldFactory,
    transition_factory: TransitionFactory,
    distribution_factory: BoundaryDistributionFactory,
) -> PassiveSegmentationBranch:
    field = _initial_field(field_factory)
    initial_digest = _initial_field_digest(field)
    transition = transition_factory()
    if not callable(transition):
        raise PassiveFieldSegmentationError(
            "transition_factory must return one explicit transition"
        )
    traces = []
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(batch, field.docks)
        local_inputs = project_transient_docks_to_neuron_inputs(
            trajectory,
            field.docks,
        )
        distribution = distribution_factory(batch)
        if not isinstance(distribution, ReceptorDistribution):
            raise PassiveFieldSegmentationError(
                "distribution_factory must return one receptor distribution"
            )
        try:
            field = field.advance(
                distribution,
                transition,
                transient_neuron_inputs=local_inputs,
            )
        except ValueError as exc:
            raise PassiveFieldSegmentationError(
                f"passive {segmentation_id} branch failed: {exc}"
            ) from exc
        traces.append(
            PassiveSegmentationStep(
                step_index=batch.batch_index,
                step_time=batch.step_time,
                event_count=batch.event_count,
                modality_event_counts=batch.modality_event_counts,
                technical_layer_tick=field.layer.tick,
                endpoint=_endpoint(field),
            )
        )
    return PassiveSegmentationBranch(
        segmentation_id=segmentation_id,
        initial_field_digest=initial_digest,
        source_event_count=handoff.source_event_count,
        assigned_event_count=handoff.assigned_event_count,
        every_event_assigned_once=handoff.every_in_horizon_event_assigned_once,
        steps=tuple(traces),
        endpoint=_endpoint(field),
    )


def compare_passive_field_segmentations(
    sequences: Iterable[ReceptorTimeSequence],
    coarse_steps: Iterable[MCMFieldStepTime],
    fine_steps: Iterable[MCMFieldStepTime],
    *,
    field_factory: FieldFactory,
    transition_factory: TransitionFactory,
    distribution_factory: BoundaryDistributionFactory,
) -> PassiveFieldSegmentationComparison:
    """Run one explicit transition over the same history without selecting it."""

    sequences_in = tuple(sequences)
    coarse_steps_in = _steps(coarse_steps, "coarse segmentation")
    fine_steps_in = _steps(fine_steps, "fine segmentation")
    coarse_horizon = (
        coarse_steps_in[0].clock_id,
        coarse_steps_in[0].start_tick,
        coarse_steps_in[-1].end_tick,
        coarse_steps_in[0].ticks_per_second,
    )
    fine_horizon = (
        fine_steps_in[0].clock_id,
        fine_steps_in[0].start_tick,
        fine_steps_in[-1].end_tick,
        fine_steps_in[0].ticks_per_second,
    )
    if coarse_horizon != fine_horizon:
        raise PassiveFieldSegmentationError(
            "coarse and fine segmentations must cover the same organism horizon"
        )
    if not callable(transition_factory) or not callable(distribution_factory):
        raise PassiveFieldSegmentationError(
            "transition and distribution factories must be callable"
        )

    coarse_handoff = handoff_receptor_completion_groups(
        sequences_in,
        coarse_steps_in,
    )
    fine_handoff = handoff_receptor_completion_groups(
        sequences_in,
        fine_steps_in,
    )
    if (
        not coarse_handoff.every_in_horizon_event_assigned_once
        or not fine_handoff.every_in_horizon_event_assigned_once
        or coarse_handoff.assigned_event_count != fine_handoff.assigned_event_count
    ):
        raise PassiveFieldSegmentationError(
            "both segmentations must assign the same source events exactly once"
        )

    coarse = _run_branch(
        "coarse",
        coarse_handoff,
        field_factory,
        transition_factory,
        distribution_factory,
    )
    coarse_replay = _run_branch(
        "coarse",
        coarse_handoff,
        field_factory,
        transition_factory,
        distribution_factory,
    )
    fine = _run_branch(
        "fine",
        fine_handoff,
        field_factory,
        transition_factory,
        distribution_factory,
    )
    fine_replay = _run_branch(
        "fine",
        fine_handoff,
        field_factory,
        transition_factory,
        distribution_factory,
    )
    initial_digests = {
        coarse.initial_field_digest,
        coarse_replay.initial_field_digest,
        fine.initial_field_digest,
        fine_replay.initial_field_digest,
    }
    if len(initial_digests) != 1:
        raise PassiveFieldSegmentationError(
            "every passive branch must rebuild the same initial field"
        )
    return PassiveFieldSegmentationComparison(
        coarse=coarse,
        fine=fine,
        coarse_reproducible=coarse == coarse_replay,
        fine_reproducible=fine == fine_replay,
        endpoints_equal=coarse.endpoint == fine.endpoint,
    )


def compare_passive_field_role_ablations(
    sequences: Iterable[ReceptorTimeSequence],
    coarse_steps: Iterable[MCMFieldStepTime],
    fine_steps: Iterable[MCMFieldStepTime],
    *,
    field_factory: FieldFactory,
    passive_transition_factory: Callable[[], PassiveLocalTransition],
    distribution_factory: BoundaryDistributionFactory,
) -> PassiveFieldRoleAblationComparison:
    """Run the full local view and every single-role removal independently."""

    if not callable(passive_transition_factory):
        raise PassiveFieldSegmentationError(
            "passive_transition_factory must be callable"
        )
    sequences_in = tuple(sequences)
    coarse_steps_in = tuple(coarse_steps)
    fine_steps_in = tuple(fine_steps)

    def transition_factory(
        roles: PassiveDriveRoleMask,
    ) -> TransitionFactory:
        def build() -> MCMNeuronTransition:
            transition = passive_transition_factory()
            if not callable(transition):
                raise PassiveFieldSegmentationError(
                    "passive_transition_factory must return one transition"
                )
            return adapt_passive_local_transition(transition, roles)

        return build

    complete_roles = all_passive_drive_roles()
    reference = compare_passive_field_segmentations(
        sequences_in,
        coarse_steps_in,
        fine_steps_in,
        field_factory=field_factory,
        transition_factory=transition_factory(complete_roles),
        distribution_factory=distribution_factory,
    )
    ablations = []
    for role in PassiveDriveRole:
        comparison = compare_passive_field_segmentations(
            sequences_in,
            coarse_steps_in,
            fine_steps_in,
            field_factory=field_factory,
            transition_factory=transition_factory(
                complete_roles.without(role)
            ),
            distribution_factory=distribution_factory,
        )
        ablations.append(
            PassiveFieldRoleAblation(
                role=role,
                comparison=comparison,
                coarse_endpoint_changed=(
                    comparison.coarse.endpoint != reference.coarse.endpoint
                ),
                fine_endpoint_changed=(
                    comparison.fine.endpoint != reference.fine.endpoint
                ),
            )
        )
    return PassiveFieldRoleAblationComparison(
        reference=reference,
        ablations=tuple(ablations),
    )


def passive_field_segmentation_comparison_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            PassiveNeuronEndpoint,
            PassiveFieldEndpoint,
            PassiveSegmentationStep,
            PassiveSegmentationBranch,
            PassiveFieldSegmentationComparison,
            PassiveFieldRoleAblation,
            PassiveFieldRoleAblationComparison,
        )
        for item in fields(contract)
    )
