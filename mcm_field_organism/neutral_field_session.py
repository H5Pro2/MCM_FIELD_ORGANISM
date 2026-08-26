"""Bounded continuation of the current asynchronous shared-field runtime."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Callable, Iterable

from .field_step_time import MCMFieldStepTime
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_time_model import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField, SharedMCMFieldSnapshot


class NeutralFieldSessionError(ValueError):
    """Raised when a continued field session would lose its causal boundary."""


@dataclass(frozen=True, slots=True)
class NeutralFieldSessionWindow:
    receptor_sequences: tuple[ReceptorTimeSequence, ...]
    proposal_steps: tuple[MCMFieldStepTime, ...]

    def __post_init__(self) -> None:
        sequences = tuple(self.receptor_sequences)
        steps = tuple(self.proposal_steps)
        if not sequences or any(
            not isinstance(item, ReceptorTimeSequence) for item in sequences
        ):
            raise NeutralFieldSessionError(
                "session window requires receptor time sequences"
            )
        if not steps or any(not isinstance(item, MCMFieldStepTime) for item in steps):
            raise NeutralFieldSessionError(
                "session window requires physical proposal steps"
            )
        clocks = {item.clock_id for item in sequences}
        clocks.update(item.clock_id for item in steps)
        if len(clocks) != 1:
            raise NeutralFieldSessionError(
                "session window requires one organism clock"
            )
        for earlier, later in zip(steps, steps[1:]):
            if earlier.end_tick != later.start_tick:
                raise NeutralFieldSessionError(
                    "session window proposal steps must be contiguous"
                )
        object.__setattr__(self, "receptor_sequences", sequences)
        object.__setattr__(self, "proposal_steps", steps)

    @property
    def clock_id(self) -> str:
        return self.proposal_steps[0].clock_id

    @property
    def start_tick(self) -> int:
        return self.proposal_steps[0].start_tick

    @property
    def end_tick(self) -> int:
        return self.proposal_steps[-1].end_tick


@dataclass(frozen=True, slots=True)
class NeutralFieldSessionResult:
    field: SharedMCMField
    window_count: int
    source_support_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.field, SharedMCMField):
            raise NeutralFieldSessionError(
                "session result requires one shared MCM field"
            )
        for role in ("window_count", "source_support_count"):
            value = getattr(self, role)
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 1
            ):
                raise NeutralFieldSessionError(
                    f"{role} must be a positive integer"
                )


NeutralFieldSessionObserver = Callable[[int, SharedMCMFieldSnapshot], None]


def run_neutral_field_session(
    initial_field: SharedMCMField,
    windows: Iterable[NeutralFieldSessionWindow],
    field_config: NeutralLocalFieldSubstrateConfig,
    *,
    afterimage_config: NeutralFastAfterimageConfig | None = None,
    max_windows: int,
    observer: NeutralFieldSessionObserver | None = None,
) -> NeutralFieldSessionResult:
    """Continue one field through complete windows without retaining histories."""
    if not isinstance(initial_field, SharedMCMField):
        raise NeutralFieldSessionError(
            "session requires one initial shared MCM field"
        )
    if not isinstance(field_config, NeutralLocalFieldSubstrateConfig):
        raise NeutralFieldSessionError(
            "session requires one explicit field configuration"
        )
    if afterimage_config is not None and not isinstance(
        afterimage_config,
        NeutralFastAfterimageConfig,
    ):
        raise NeutralFieldSessionError(
            "session requires an explicit fast afterimage configuration"
        )
    if (
        isinstance(max_windows, bool)
        or not isinstance(max_windows, int)
        or max_windows < 1
    ):
        raise NeutralFieldSessionError("max_windows must be a positive integer")
    if observer is not None and not callable(observer):
        raise NeutralFieldSessionError("session observer must be callable")

    windows_in = tuple(windows)
    if not windows_in or any(
        not isinstance(item, NeutralFieldSessionWindow) for item in windows_in
    ):
        raise NeutralFieldSessionError(
            "session requires bounded field windows"
        )
    if len(windows_in) > max_windows:
        raise NeutralFieldSessionError(
            "session window count exceeds the explicit maximum"
        )
    for earlier, later in zip(windows_in, windows_in[1:]):
        if (
            earlier.clock_id != later.clock_id
            or earlier.end_tick != later.start_tick
        ):
            raise NeutralFieldSessionError(
                "session windows must be contiguous on one organism clock"
            )
    if initial_field.last_distribution is not None:
        previous = initial_field.last_distribution.field_time
        first = windows_in[0]
        if (
            previous.clock_id != first.clock_id
            or previous.window_end_tick != first.start_tick
        ):
            raise NeutralFieldSessionError(
                "resumed session must continue at the serialized field boundary"
            )

    current = initial_field
    support_count = 0
    for index, window in enumerate(windows_in):
        try:
            run = run_neutral_asynchronous_field(
                current,
                window.receptor_sequences,
                window.proposal_steps,
                field_config,
                afterimage_config=afterimage_config,
            )
        except ValueError as exc:
            raise NeutralFieldSessionError(
                f"session window {index} failed: {exc}"
            ) from exc
        current = run.field
        support_count += run.source_support_count
        if observer is not None:
            snapshot = current.snapshot()
            before = snapshot.digest()
            observer(index, snapshot)
            if snapshot.digest() != before:
                raise NeutralFieldSessionError(
                    "session observer changed the immutable field snapshot"
                )

    return NeutralFieldSessionResult(
        field=current,
        window_count=len(windows_in),
        source_support_count=support_count,
    )


def neutral_field_session_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (NeutralFieldSessionWindow, NeutralFieldSessionResult)
        for item in fields(cls)
    )
