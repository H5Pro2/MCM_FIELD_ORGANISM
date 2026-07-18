"""Passive elapsed-time contract for one atomic MCM field proposal."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

from .receptor_contract import technical_identifier


class MCMFieldStepTimeError(ValueError):
    """Raised when an atomic field-step interval is not physically ordered."""


@dataclass(frozen=True, slots=True)
class MCMFieldStepTime:
    """Measured duration available to a transition, without update mechanics."""

    clock_id: str
    start_tick: int
    end_tick: int
    ticks_per_second: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "clock_id",
            technical_identifier(self.clock_id, "clock_id"),
        )
        if (
            isinstance(self.start_tick, bool)
            or isinstance(self.end_tick, bool)
            or not isinstance(self.start_tick, int)
            or not isinstance(self.end_tick, int)
            or self.start_tick < 0
            or self.end_tick <= self.start_tick
        ):
            raise MCMFieldStepTimeError(
                "field-step ticks must form one positive ordered interval"
            )
        rate = float(self.ticks_per_second)
        if not math.isfinite(rate) or rate <= 0.0:
            raise MCMFieldStepTimeError(
                "ticks_per_second must be finite and greater than zero"
            )
        object.__setattr__(self, "ticks_per_second", rate)

    @property
    def elapsed_ticks(self) -> int:
        return self.end_tick - self.start_tick

    @property
    def elapsed_seconds(self) -> float:
        return self.elapsed_ticks / self.ticks_per_second


def field_step_time_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(MCMFieldStepTime))
