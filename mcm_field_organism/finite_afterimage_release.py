from __future__ import annotations

from dataclasses import dataclass, fields
import math


class FiniteAfterimageReleaseError(ValueError):
    """Raised when the local release candidate receives an invalid value."""


@dataclass(frozen=True)
class FiniteAfterimageReleaseConfig:
    time_scale_seconds: float
    release_exponent: float

    def __post_init__(self) -> None:
        if (
            not math.isfinite(self.time_scale_seconds)
            or self.time_scale_seconds <= 0.0
        ):
            raise FiniteAfterimageReleaseError(
                "time_scale_seconds must be finite and positive"
            )
        if (
            not math.isfinite(self.release_exponent)
            or not 0.0 < self.release_exponent < 1.0
        ):
            raise FiniteAfterimageReleaseError(
                "release_exponent must be finite and strictly between zero and one"
            )


def finite_afterimage_extinction_time(
    value: float,
    config: FiniteAfterimageReleaseConfig,
) -> float:
    """Return the exact unforced duration until the local value reaches zero."""
    if not math.isfinite(value):
        raise FiniteAfterimageReleaseError("value must be finite")
    if value == 0.0:
        return 0.0
    complement = 1.0 - config.release_exponent
    return (
        config.time_scale_seconds
        * abs(value) ** complement
        / complement
    )


def release_afterimage(
    value: float,
    elapsed_seconds: float,
    config: FiniteAfterimageReleaseConfig,
) -> float:
    """Advance one unforced local value without a tolerance or hidden state."""
    if not math.isfinite(value):
        raise FiniteAfterimageReleaseError("value must be finite")
    if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0.0:
        raise FiniteAfterimageReleaseError(
            "elapsed_seconds must be finite and non-negative"
        )
    if value == 0.0 or elapsed_seconds == 0.0:
        return value

    complement = 1.0 - config.release_exponent
    remaining = (
        abs(value) ** complement
        - complement * elapsed_seconds / config.time_scale_seconds
    )
    if remaining <= 0.0:
        return 0.0
    return math.copysign(remaining ** (1.0 / complement), value)


def finite_afterimage_release_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(FiniteAfterimageReleaseConfig))
