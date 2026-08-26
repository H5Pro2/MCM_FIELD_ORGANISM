"""Device-neutral organism-time models for reduced receptor states."""

from __future__ import annotations

from dataclasses import dataclass

from .receptor_contract import CommonFieldTime, ReceptorContactFrame


class ReceptorTimeAlignmentError(ValueError):
    """Raised when reduced receptor states cannot share one organism clock."""


@dataclass(frozen=True, slots=True)
class OrganismTimedReceptorFrame:
    """One reduced receptor state measured on the organism clock."""

    frame: ReceptorContactFrame
    field_time: CommonFieldTime

    def __post_init__(self) -> None:
        if not isinstance(self.frame, ReceptorContactFrame):
            raise ReceptorTimeAlignmentError(
                "timed receptor state requires a reduced receptor frame"
            )
        if not isinstance(self.field_time, CommonFieldTime):
            raise ReceptorTimeAlignmentError(
                "timed receptor state requires one organism-clock interval"
            )


@dataclass(frozen=True, slots=True)
class ReceptorTimeSequence:
    """Ordered reduced states from one receptor geometry."""

    modality_id: str
    geometry_id: str
    clock_id: str
    frames: tuple[OrganismTimedReceptorFrame, ...]

    def __post_init__(self) -> None:
        frames_in = tuple(self.frames)
        if not frames_in:
            raise ReceptorTimeAlignmentError(
                "receptor time sequence cannot be empty"
            )
        if any(
            item.frame.modality_id != self.modality_id
            or item.frame.geometry_id != self.geometry_id
            or item.field_time.clock_id != self.clock_id
            for item in frames_in
        ):
            raise ReceptorTimeAlignmentError(
                "sequence identity must match every timed receptor state"
            )
        snapshot_ids = [item.frame.snapshot_id for item in frames_in]
        if len(set(snapshot_ids)) != len(snapshot_ids):
            raise ReceptorTimeAlignmentError(
                "receptor sequence snapshot identities must be unique"
            )
        for earlier, later in zip(frames_in, frames_in[1:]):
            if (
                later.field_time.window_start_tick
                < earlier.field_time.window_end_tick
            ):
                raise ReceptorTimeAlignmentError(
                    "one receptor sequence cannot overlap or move backwards"
                )
        object.__setattr__(self, "frames", frames_in)
