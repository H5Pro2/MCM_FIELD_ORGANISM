"""Open receptor boundary for continuous organism self-contact.

This module does not synthesize noise or interpret internal measurements.
It only converts completed, local, normalized measurements into the same
neutral receptor contract used by external sensors.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable

from .receptor_contract import (
    ReceptorContactFrame,
    ReceptorContractError,
    technical_identifier,
)


class EndogenousReceptorError(ValueError):
    """Raised when an endogenous contact violates the open receptor boundary."""


def _identifier(value: object, role: str) -> str:
    try:
        return technical_identifier(value, role)
    except ReceptorContractError as exc:
        raise EndogenousReceptorError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class EndogenousReceptorSurface:
    """Stateless technical surface for measured or controlled self-contact."""

    source_id: str
    geometry_id: str
    carrier_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        source_id = _identifier(self.source_id, "source_id")
        geometry_id = _identifier(self.geometry_id, "geometry_id")
        carriers = tuple(self.carrier_ids)
        if not carriers or len(set(carriers)) != len(carriers):
            raise EndogenousReceptorError(
                "endogenous carrier identities must be non-empty and unique"
            )
        for carrier_id in carriers:
            _identifier(carrier_id, "carrier_id")
        object.__setattr__(self, "source_id", source_id)
        object.__setattr__(self, "geometry_id", geometry_id)
        object.__setattr__(self, "carrier_ids", carriers)

    @property
    def modality_id(self) -> str:
        return f"endogenous.{self.source_id}"

    def complete_contact(
        self,
        values: Iterable[float],
        *,
        snapshot_id: str,
        clock_id: str,
        window_start_tick: int,
        window_end_tick: int,
    ) -> ReceptorContactFrame:
        """Complete one measurement without retaining or generating values."""

        try:
            return ReceptorContactFrame(
                modality_id=self.modality_id,
                geometry_id=self.geometry_id,
                snapshot_id=snapshot_id,
                clock_id=clock_id,
                window_start_tick=window_start_tick,
                window_end_tick=window_end_tick,
                carrier_ids=self.carrier_ids,
                values=tuple(values),
            )
        except ReceptorContractError as exc:
            raise EndogenousReceptorError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class EndogenousContactGap:
    """One observed gap; no missing value is fabricated or held."""

    previous_end_tick: int
    next_start_tick: int

    def __post_init__(self) -> None:
        if (
            isinstance(self.previous_end_tick, bool)
            or isinstance(self.next_start_tick, bool)
            or not isinstance(self.previous_end_tick, int)
            or not isinstance(self.next_start_tick, int)
            or self.previous_end_tick < 0
            or self.next_start_tick <= self.previous_end_tick
        ):
            raise EndogenousReceptorError(
                "endogenous contact gap must be a positive tick interval"
            )


@dataclass(frozen=True, slots=True)
class EndogenousContactContinuityAudit:
    """Passive observation of one source sequence on its native clock."""

    modality_id: str
    geometry_id: str
    clock_id: str
    frame_count: int
    window_start_tick: int
    window_end_tick: int
    gaps: tuple[EndogenousContactGap, ...]

    def __post_init__(self) -> None:
        for role in ("modality_id", "geometry_id", "clock_id"):
            object.__setattr__(
                self,
                role,
                _identifier(getattr(self, role), role),
            )
        if (
            isinstance(self.frame_count, bool)
            or not isinstance(self.frame_count, int)
            or self.frame_count < 1
        ):
            raise EndogenousReceptorError("frame_count must be positive")
        if (
            isinstance(self.window_start_tick, bool)
            or isinstance(self.window_end_tick, bool)
            or not isinstance(self.window_start_tick, int)
            or not isinstance(self.window_end_tick, int)
            or self.window_start_tick < 0
            or self.window_end_tick <= self.window_start_tick
        ):
            raise EndogenousReceptorError(
                "audit ticks must form a positive non-negative interval"
            )
        gaps = tuple(self.gaps)
        if any(not isinstance(item, EndogenousContactGap) for item in gaps):
            raise EndogenousReceptorError(
                "gaps must contain endogenous contact gaps"
            )
        object.__setattr__(self, "gaps", gaps)

    @property
    def is_contiguous(self) -> bool:
        return not self.gaps


def audit_endogenous_contact_continuity(
    frames: Iterable[ReceptorContactFrame],
) -> EndogenousContactContinuityAudit:
    """Observe gaps without filling, holding, resampling, or interpreting them."""

    sequence = tuple(frames)
    if not sequence or any(
        not isinstance(item, ReceptorContactFrame) for item in sequence
    ):
        raise EndogenousReceptorError(
            "continuity audit requires completed receptor frames"
        )
    first = sequence[0]
    if not first.modality_id.startswith("endogenous."):
        raise EndogenousReceptorError(
            "continuity audit requires an endogenous receptor modality"
        )
    identity = (
        first.modality_id,
        first.geometry_id,
        first.clock_id,
        first.carrier_ids,
    )
    if any(
        (
            item.modality_id,
            item.geometry_id,
            item.clock_id,
            item.carrier_ids,
        )
        != identity
        for item in sequence
    ):
        raise EndogenousReceptorError(
            "one continuity audit requires one source, geometry, clock, and carrier set"
        )
    snapshots = [item.snapshot_id for item in sequence]
    if len(set(snapshots)) != len(snapshots):
        raise EndogenousReceptorError("endogenous snapshot identities must be unique")

    gaps = []
    for previous, current in zip(sequence, sequence[1:], strict=False):
        if current.window_start_tick < previous.window_end_tick:
            raise EndogenousReceptorError(
                "endogenous contact windows must not overlap or run backwards"
            )
        if current.window_start_tick > previous.window_end_tick:
            gaps.append(
                EndogenousContactGap(
                    previous.window_end_tick,
                    current.window_start_tick,
                )
            )

    return EndogenousContactContinuityAudit(
        modality_id=first.modality_id,
        geometry_id=first.geometry_id,
        clock_id=first.clock_id,
        frame_count=len(sequence),
        window_start_tick=first.window_start_tick,
        window_end_tick=sequence[-1].window_end_tick,
        gaps=tuple(gaps),
    )


def endogenous_receptor_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            EndogenousReceptorSurface,
            EndogenousContactGap,
            EndogenousContactContinuityAudit,
        )
        for item in fields(contract)
    )
