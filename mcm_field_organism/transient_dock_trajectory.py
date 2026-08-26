"""Transient lossless dock input for one bounded field proposal."""

from __future__ import annotations

from dataclasses import dataclass, fields

from .field_step_time import MCMFieldStepTime
from .receptor_contract import technical_identifier
from .receptor_proposal_handoff import (
    ReceptorProposalBatch,
    ReceptorProposalCompletionGroup,
)
from .receptor_time_model import OrganismTimedReceptorFrame
from .shared_mcm_field import SharedFieldDock


class TransientDockTrajectoryError(ValueError):
    """Raised when a proposal batch cannot remain lossless at field docks."""


@dataclass(frozen=True, slots=True)
class TransientDockFrame:
    """One completed reduced receptor state at its stable technical dock."""

    dock_id: str
    timed_frame: OrganismTimedReceptorFrame

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "dock_id",
            technical_identifier(self.dock_id, "dock_id"),
        )
        if not isinstance(self.timed_frame, OrganismTimedReceptorFrame):
            raise TransientDockTrajectoryError(
                "transient dock frame requires one timed receptor frame"
            )


@dataclass(frozen=True, slots=True)
class TransientDockCompletionGroup:
    """Unordered simultaneous completions without cross-dock fusion."""

    completion_tick: int
    dock_frames: tuple[TransientDockFrame, ...]

    def __post_init__(self) -> None:
        if (
            isinstance(self.completion_tick, bool)
            or not isinstance(self.completion_tick, int)
            or self.completion_tick < 0
        ):
            raise TransientDockTrajectoryError(
                "completion_tick must be a non-negative integer"
            )
        dock_frames = tuple(self.dock_frames)
        if not dock_frames or any(
            not isinstance(item, TransientDockFrame) for item in dock_frames
        ):
            raise TransientDockTrajectoryError(
                "completion group requires transient dock frames"
            )
        if any(
            item.timed_frame.field_time.window_end_tick != self.completion_tick
            for item in dock_frames
        ):
            raise TransientDockTrajectoryError(
                "dock frames must remain at their measured completion boundary"
            )
        dock_ids = [item.dock_id for item in dock_frames]
        if len(set(dock_ids)) != len(dock_ids):
            raise TransientDockTrajectoryError(
                "one completion group permits one state per dock"
            )
        object.__setattr__(
            self,
            "dock_frames",
            tuple(
                sorted(
                    dock_frames,
                    key=lambda item: (
                        item.dock_id,
                        item.timed_frame.frame.snapshot_id,
                    ),
                )
            ),
        )


@dataclass(frozen=True, slots=True)
class TransientDockTrajectory:
    """Lossless proposal input that is not part of persistent field state."""

    step_time: MCMFieldStepTime
    attached_dock_ids: tuple[str, ...]
    completion_groups: tuple[TransientDockCompletionGroup, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.step_time, MCMFieldStepTime):
            raise TransientDockTrajectoryError(
                "transient dock trajectory requires one proposal time span"
            )
        dock_ids = tuple(
            technical_identifier(item, "attached_dock_id")
            for item in self.attached_dock_ids
        )
        if not dock_ids or len(set(dock_ids)) != len(dock_ids):
            raise TransientDockTrajectoryError(
                "attached dock identities must be non-empty and unique"
            )
        groups = tuple(self.completion_groups)
        if any(
            not isinstance(group, TransientDockCompletionGroup)
            for group in groups
        ):
            raise TransientDockTrajectoryError(
                "trajectory groups must be completed dock groups"
            )
        ticks = [group.completion_tick for group in groups]
        if ticks != sorted(set(ticks)):
            raise TransientDockTrajectoryError(
                "completion groups must be strictly ordered"
            )
        if any(
            not (
                self.step_time.start_tick
                < group.completion_tick
                <= self.step_time.end_tick
            )
            for group in groups
        ):
            raise TransientDockTrajectoryError(
                "completion groups must stay inside the proposal time span"
            )
        all_frames = tuple(
            item for group in groups for item in group.dock_frames
        )
        if any(item.dock_id not in dock_ids for item in all_frames):
            raise TransientDockTrajectoryError(
                "trajectory contains a state for an unattached dock"
            )
        identities = [
            (item.dock_id, item.timed_frame.frame.snapshot_id)
            for item in all_frames
        ]
        if len(set(identities)) != len(identities):
            raise TransientDockTrajectoryError(
                "transient dock state identities must be unique"
            )
        object.__setattr__(self, "attached_dock_ids", tuple(sorted(dock_ids)))
        object.__setattr__(self, "completion_groups", groups)

    @property
    def event_count(self) -> int:
        return sum(len(group.dock_frames) for group in self.completion_groups)

    def frames_for_dock(
        self,
        dock_id: str,
    ) -> tuple[OrganismTimedReceptorFrame, ...]:
        dock_id = technical_identifier(dock_id, "dock_id")
        if dock_id not in self.attached_dock_ids:
            raise KeyError(dock_id)
        return tuple(
            item.timed_frame
            for group in self.completion_groups
            for item in group.dock_frames
            if item.dock_id == dock_id
        )


def _validate_batch(batch: ReceptorProposalBatch) -> None:
    if not isinstance(batch, ReceptorProposalBatch):
        raise TransientDockTrajectoryError(
            "trajectory requires one receptor proposal batch"
        )
    if (
        isinstance(batch.batch_index, bool)
        or not isinstance(batch.batch_index, int)
        or batch.batch_index < 0
        or not isinstance(batch.step_time, MCMFieldStepTime)
    ):
        raise TransientDockTrajectoryError("proposal batch roles are invalid")
    groups = tuple(batch.completion_groups)
    if any(
        not isinstance(group, ReceptorProposalCompletionGroup)
        for group in groups
    ):
        raise TransientDockTrajectoryError(
            "proposal batch contains an invalid completion group"
        )
    completion_ticks = [group.completion_tick for group in groups]
    if completion_ticks != sorted(set(completion_ticks)) or any(
        not (
            batch.step_time.start_tick
            < completion_tick
            <= batch.step_time.end_tick
        )
        for completion_tick in completion_ticks
    ):
        raise TransientDockTrajectoryError(
            "proposal completion groups must be ordered inside their time span"
        )
    observed_counts: dict[str, int] = {}
    for group in groups:
        timed_frames = tuple(group.timed_frames)
        if not timed_frames or any(
            not isinstance(item, OrganismTimedReceptorFrame)
            for item in timed_frames
        ):
            raise TransientDockTrajectoryError(
                "proposal completion group requires timed receptor frames"
            )
        if any(
            item.field_time.window_end_tick != group.completion_tick
            for item in timed_frames
        ):
            raise TransientDockTrajectoryError(
                "proposal states must remain at their completion boundary"
            )
        for item in timed_frames:
            observed_counts[item.frame.modality_id] = (
                observed_counts.get(item.frame.modality_id, 0) + 1
            )
    declared_counts = dict(batch.modality_event_counts)
    try:
        declared_modalities_are_valid = all(
            technical_identifier(modality_id, "modality_id") == modality_id
            for modality_id in declared_counts
        )
    except ValueError as exc:
        raise TransientDockTrajectoryError(
            "proposal modality identities must be technical identifiers"
        ) from exc
    if (
        len(declared_counts) != len(batch.modality_event_counts)
        or not declared_modalities_are_valid
        or any(
            isinstance(count, bool)
            or not isinstance(count, int)
            or count < 0
            for count in declared_counts.values()
        )
        or any(
            observed_counts.get(modality_id, 0) != count
            for modality_id, count in declared_counts.items()
        )
        or any(modality_id not in declared_counts for modality_id in observed_counts)
    ):
        raise TransientDockTrajectoryError(
            "proposal modality counts must match every completed state"
        )


def map_proposal_batch_to_transient_docks(
    batch: ReceptorProposalBatch,
    docks: tuple[SharedFieldDock, ...],
) -> TransientDockTrajectory:
    """Map a complete batch to stable docks without reading or reducing it."""

    _validate_batch(batch)
    docks_in = tuple(docks)
    if not docks_in or any(
        not isinstance(dock, SharedFieldDock) for dock in docks_in
    ):
        raise TransientDockTrajectoryError(
            "trajectory mapping requires shared field docks"
        )
    dock_ids = [dock.dock_id for dock in docks_in]
    modalities = [dock.dock_map.modality_id for dock in docks_in]
    if len(set(dock_ids)) != len(dock_ids) or len(set(modalities)) != len(modalities):
        raise TransientDockTrajectoryError(
            "shared field dock and modality identities must be unique"
        )
    by_modality = {
        dock.dock_map.modality_id: dock for dock in docks_in
    }

    groups_out = []
    for group in batch.completion_groups:
        dock_frames = []
        for timed_frame in group.timed_frames:
            dock = by_modality.get(timed_frame.frame.modality_id)
            if dock is None:
                raise TransientDockTrajectoryError(
                    "proposal contains a state for an unattached modality"
                )
            try:
                dock.dock_map.contacts_for(timed_frame.frame)
            except ValueError as exc:
                raise TransientDockTrajectoryError(
                    f"dock {dock.dock_id} rejected its receptor state: {exc}"
                ) from exc
            dock_frames.append(TransientDockFrame(dock.dock_id, timed_frame))
        groups_out.append(
            TransientDockCompletionGroup(group.completion_tick, tuple(dock_frames))
        )
    return TransientDockTrajectory(
        step_time=batch.step_time,
        attached_dock_ids=tuple(dock_ids),
        completion_groups=tuple(groups_out),
    )


def transient_dock_trajectory_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            TransientDockFrame,
            TransientDockCompletionGroup,
            TransientDockTrajectory,
        )
        for item in fields(contract)
    )
