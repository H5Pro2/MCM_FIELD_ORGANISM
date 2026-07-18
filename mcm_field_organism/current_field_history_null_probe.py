"""Passive history-null probe through the current shared-field runtime."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .mcm_neuron_layer import receptor_projection_baseline
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import ReceptorDistributor, ReceptorDock
from .shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMField,
    build_shared_mcm_field,
)


@dataclass(frozen=True, slots=True)
class CurrentFieldHistoryNullBranch:
    branch_id: str
    history: tuple[float, ...]
    terminal_layer_digest: str
    first_alignment_layer_digest: str
    second_alignment_layer_digest: str
    probe_layer_digest: str
    first_alignment_activation: tuple[float, ...]
    first_alignment_afterimage: tuple[float, ...]
    second_alignment_activation: tuple[float, ...]
    second_alignment_afterimage: tuple[float, ...]
    probe_activation: tuple[float, ...]
    probe_afterimage: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class CurrentFieldHistoryNullProbeResult:
    first_branch: CurrentFieldHistoryNullBranch
    second_branch: CurrentFieldHistoryNullBranch
    histories_distinct: bool
    history_contact_multisets_equal: bool
    terminal_full_states_distinct: bool
    first_alignment_fast_vectors_equal: bool
    first_alignment_full_states_equal: bool
    second_alignment_full_states_equal: bool
    identical_probe_full_states_equal: bool
    functional_difference_observed: bool
    manual_state_copy_used: bool
    new_history_carrier_added: bool
    observer_writeback_performed: bool
    runtime_candidate_released: bool


_SAMPLE_OFFSETS = ((0, -1), (0, 1))
_AUDITORY_GEOMETRY = "auditory.null.v1"
_VISUAL_GEOMETRY = "visual.null.v1"
_CLOCK_ID = "organism.history_null"


def _frame(
    modality_id: str,
    geometry_id: str,
    value: float,
    *,
    branch_id: str,
    step: int,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=modality_id,
        geometry_id=geometry_id,
        snapshot_id=f"{branch_id}.{modality_id}.snapshot.{step}",
        clock_id=f"{modality_id}.source",
        window_start_tick=step * 10,
        window_end_tick=(step + 1) * 10,
        carrier_ids=(f"{modality_id}.carrier.0",),
        values=(value,),
    )


def _reference_frames() -> tuple[ReceptorContactFrame, ...]:
    return (
        _frame(
            "auditory",
            _AUDITORY_GEOMETRY,
            0.0,
            branch_id="reference",
            step=0,
        ),
        _frame(
            "visual",
            _VISUAL_GEOMETRY,
            0.0,
            branch_id="reference",
            step=0,
        ),
    )


def _new_field_and_distributor() -> tuple[SharedMCMField, ReceptorDistributor]:
    references = _reference_frames()
    anatomies = {
        "auditory": ReceptorDockAnatomy(
            modality_id="auditory",
            dock_id="dock.auditory",
            positions=((0, 0),),
        ),
        "visual": ReceptorDockAnatomy(
            modality_id="visual",
            dock_id="dock.visual",
            positions=((0, 1),),
        ),
    }
    field = build_shared_mcm_field(
        references,
        anatomies,
        sample_offsets=_SAMPLE_OFFSETS,
    )
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock(
            "dock.auditory",
            "auditory",
            _AUDITORY_GEOMETRY,
        )
    )
    distributor.attach(
        ReceptorDock(
            "dock.visual",
            "visual",
            _VISUAL_GEOMETRY,
        )
    )
    return field, distributor


def _advance(
    field: SharedMCMField,
    distributor: ReceptorDistributor,
    *,
    branch_id: str,
    step: int,
    auditory: float,
    visual: float,
) -> SharedMCMField:
    frames = (
        _frame(
            "auditory",
            _AUDITORY_GEOMETRY,
            auditory,
            branch_id=branch_id,
            step=step,
        ),
        _frame(
            "visual",
            _VISUAL_GEOMETRY,
            visual,
            branch_id=branch_id,
            step=step,
        ),
    )
    distribution = distributor.distribute(
        frames,
        CommonFieldTime(_CLOCK_ID, step * 10, (step + 1) * 10),
    )
    return field.advance(distribution, receptor_projection_baseline)


def _run_branch(
    branch_id: str,
    history: tuple[float, ...],
) -> CurrentFieldHistoryNullBranch:
    field, distributor = _new_field_and_distributor()
    step = 0
    for contact in history:
        field = _advance(
            field,
            distributor,
            branch_id=branch_id,
            step=step,
            auditory=contact,
            visual=0.3,
        )
        step += 1
    terminal_digest = field.layer.digest()

    field = _advance(
        field,
        distributor,
        branch_id=branch_id,
        step=step,
        auditory=0.0,
        visual=0.0,
    )
    first_alignment_digest = field.layer.digest()
    first_alignment_snapshot = field.snapshot()
    step += 1

    field = _advance(
        field,
        distributor,
        branch_id=branch_id,
        step=step,
        auditory=0.0,
        visual=0.0,
    )
    second_alignment_digest = field.layer.digest()
    second_alignment_snapshot = field.snapshot()
    step += 1

    field = _advance(
        field,
        distributor,
        branch_id=branch_id,
        step=step,
        auditory=0.6,
        visual=0.4,
    )
    probe_snapshot = field.snapshot()

    return CurrentFieldHistoryNullBranch(
        branch_id=branch_id,
        history=history,
        terminal_layer_digest=terminal_digest,
        first_alignment_layer_digest=first_alignment_digest,
        second_alignment_layer_digest=second_alignment_digest,
        probe_layer_digest=field.layer.digest(),
        first_alignment_activation=first_alignment_snapshot.activation,
        first_alignment_afterimage=first_alignment_snapshot.afterimage,
        second_alignment_activation=second_alignment_snapshot.activation,
        second_alignment_afterimage=second_alignment_snapshot.afterimage,
        probe_activation=probe_snapshot.activation,
        probe_afterimage=probe_snapshot.afterimage,
    )


def run_current_field_history_null_probe(
) -> CurrentFieldHistoryNullProbeResult:
    """Compare two independent history branches without adding field state."""

    first_history = (0.2, 0.8, 0.5)
    second_history = (0.5, 0.8, 0.2)
    first = _run_branch("branch.first", first_history)
    second = _run_branch("branch.second", second_history)
    first_fast = (
        first.first_alignment_activation,
        first.first_alignment_afterimage,
    )
    second_fast = (
        second.first_alignment_activation,
        second.first_alignment_afterimage,
    )
    probe_equal = first.probe_layer_digest == second.probe_layer_digest

    return CurrentFieldHistoryNullProbeResult(
        first_branch=first,
        second_branch=second,
        histories_distinct=first_history != second_history,
        history_contact_multisets_equal=(
            tuple(sorted(first_history)) == tuple(sorted(second_history))
        ),
        terminal_full_states_distinct=(
            first.terminal_layer_digest != second.terminal_layer_digest
        ),
        first_alignment_fast_vectors_equal=first_fast == second_fast,
        first_alignment_full_states_equal=(
            first.first_alignment_layer_digest
            == second.first_alignment_layer_digest
        ),
        second_alignment_full_states_equal=(
            first.second_alignment_layer_digest
            == second.second_alignment_layer_digest
        ),
        identical_probe_full_states_equal=probe_equal,
        functional_difference_observed=not probe_equal,
        manual_state_copy_used=False,
        new_history_carrier_added=False,
        observer_writeback_performed=False,
        runtime_candidate_released=False,
    )


def current_field_history_null_probe_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            CurrentFieldHistoryNullBranch,
            CurrentFieldHistoryNullProbeResult,
        )
        for item in fields(contract)
    )
