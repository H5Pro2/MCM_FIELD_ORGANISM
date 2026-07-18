"""Passive comparison of two temporal receptor-to-field architecture carriers."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .field_step_time import MCMFieldStepTime
from .mcm_neuron_layer import receptor_projection_baseline
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import ReceptorDistributor, ReceptorDock
from .receptor_proposal_handoff_audit import (
    ReceptorProposalBatch,
    handoff_receptor_completion_groups,
)
from .receptor_time_alignment import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from .shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMFieldError,
    build_shared_mcm_field,
)


@dataclass(frozen=True, slots=True)
class TemporalProposalCarrierEvidence:
    dense_event_count: int
    sparse_event_count: int
    same_horizon: bool
    same_constant_contact_values: bool
    same_contact_endpoint: bool
    both_sequences_losslessly_carried: bool
    payload_cardinality_equal: bool
    current_field_accepts_temporal_batch: bool
    field_state_unchanged_after_rejection: bool


@dataclass(frozen=True, slots=True)
class AsynchronousLocalEffectEvidence:
    dense_complete_field_advance_count: int
    sparse_complete_field_advance_count: int
    final_contact_activation_equal: bool
    complete_advance_count_equal: bool
    distributor_anatomy_unchanged: bool
    separate_local_effect_entrypoint_available: bool


@dataclass(frozen=True, slots=True)
class TemporalInputArchitectureAuditResult:
    temporal_proposal_carrier: TemporalProposalCarrierEvidence
    asynchronous_local_effect: AsynchronousLocalEffectEvidence
    temporal_carrier_rate_neutral_without_rule: bool
    asynchronous_effect_rate_neutral_without_rule: bool
    runtime_candidate_released: bool


def _frame(snapshot_index: int) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.receptor.v1",
        snapshot_id=f"auditory.snapshot.{snapshot_index}",
        clock_id="auditory.source",
        window_start_tick=snapshot_index,
        window_end_tick=snapshot_index + 1,
        carrier_ids=("auditory.carrier.0",),
        values=(0.5,),
    )


def _sequence(completion_ticks: tuple[int, ...]) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        "auditory",
        "auditory.receptor.v1",
        "organism.test",
        tuple(
            OrganismTimedReceptorFrame(
                _frame(index),
                CommonFieldTime(
                    "organism.test",
                    completion_tick - 1,
                    completion_tick,
                ),
            )
            for index, completion_tick in enumerate(completion_ticks)
        ),
    )


def _distributor() -> ReceptorDistributor:
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock(
            "dock.auditory",
            "auditory",
            "auditory.receptor.v1",
        )
    )
    return distributor


def _field(reference: ReceptorContactFrame):
    return build_shared_mcm_field(
        (reference,),
        {
            "auditory": ReceptorDockAnatomy(
                modality_id="auditory",
                dock_id="dock.auditory",
                positions=((0,),),
            )
        },
        sample_offsets=((-1,), (1,)),
    )


def _batch(sequence: ReceptorTimeSequence) -> ReceptorProposalBatch:
    handoff = handoff_receptor_completion_groups(
        (sequence,),
        (MCMFieldStepTime("organism.test", 0, 10, 10.0),),
    )
    return handoff.batches[0]


def _serial_field(sequence: ReceptorTimeSequence):
    field = _field(sequence.frames[0].frame)
    distributor = _distributor()
    anatomy_before = distributor.docks
    for item in sequence.frames:
        distribution = distributor.distribute((item.frame,), item.field_time)
        field = field.advance(distribution, receptor_projection_baseline)
    return field, anatomy_before == distributor.docks


def run_temporal_input_architecture_audit() -> TemporalInputArchitectureAuditResult:
    """Compare carriers while leaving both architecture branches closed."""

    dense = _sequence(tuple(range(1, 11)))
    sparse = _sequence((5, 10))
    dense_batch = _batch(dense)
    sparse_batch = _batch(sparse)

    untouched_field = _field(dense.frames[0].frame)
    digest_before = untouched_field.layer.digest()
    batch_error = ""
    try:
        untouched_field.advance(  # type: ignore[arg-type]
            dense_batch,
            receptor_projection_baseline,
        )
    except SharedMCMFieldError as exc:
        batch_error = str(exc)
    digest_after = untouched_field.layer.digest()

    dense_serial, dense_anatomy_unchanged = _serial_field(dense)
    sparse_serial, sparse_anatomy_unchanged = _serial_field(sparse)
    dense_activation = dense_serial.layer.neurons[0].activation
    sparse_activation = sparse_serial.layer.neurons[0].activation

    temporal = TemporalProposalCarrierEvidence(
        dense_event_count=dense_batch.event_count,
        sparse_event_count=sparse_batch.event_count,
        same_horizon=(
            dense_batch.step_time.start_tick == sparse_batch.step_time.start_tick
            and dense_batch.step_time.end_tick == sparse_batch.step_time.end_tick
        ),
        same_constant_contact_values=(
            {value for item in dense.frames for value in item.frame.values}
            == {value for item in sparse.frames for value in item.frame.values}
            == {0.5}
        ),
        same_contact_endpoint=(
            dense.frames[-1].frame.values == sparse.frames[-1].frame.values
        ),
        both_sequences_losslessly_carried=(
            dense_batch.event_count == len(dense.frames)
            and sparse_batch.event_count == len(sparse.frames)
        ),
        payload_cardinality_equal=(
            dense_batch.event_count == sparse_batch.event_count
        ),
        current_field_accepts_temporal_batch=not bool(batch_error),
        field_state_unchanged_after_rejection=digest_before == digest_after,
    )
    asynchronous = AsynchronousLocalEffectEvidence(
        dense_complete_field_advance_count=dense_serial.layer.tick,
        sparse_complete_field_advance_count=sparse_serial.layer.tick,
        final_contact_activation_equal=dense_activation == sparse_activation,
        complete_advance_count_equal=(
            dense_serial.layer.tick == sparse_serial.layer.tick
        ),
        distributor_anatomy_unchanged=(
            dense_anatomy_unchanged and sparse_anatomy_unchanged
        ),
        separate_local_effect_entrypoint_available=hasattr(
            type(untouched_field),
            "apply_receptor_event",
        ),
    )
    return TemporalInputArchitectureAuditResult(
        temporal_proposal_carrier=temporal,
        asynchronous_local_effect=asynchronous,
        temporal_carrier_rate_neutral_without_rule=(
            temporal.payload_cardinality_equal
        ),
        asynchronous_effect_rate_neutral_without_rule=(
            asynchronous.complete_advance_count_equal
        ),
        runtime_candidate_released=False,
    )


def temporal_input_architecture_audit_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            TemporalProposalCarrierEvidence,
            AsynchronousLocalEffectEvidence,
            TemporalInputArchitectureAuditResult,
        )
        for item in fields(contract)
    )
