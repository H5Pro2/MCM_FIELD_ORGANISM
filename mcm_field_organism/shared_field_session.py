"""Bounded multi-tick operation of one shared MCM field."""

from __future__ import annotations

from dataclasses import dataclass, fields
import re
from typing import Callable, Iterable

from .common_receptor_window import (
    CapturedCommonReceptorWindowAudit,
    audit_receptor_window_assignment,
)
from .mcm_neuron_layer import MCMNeuronTransition
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import (
    ReceptorDistribution,
    ReceptorDistributor,
    ReceptorDock,
)
from .shared_mcm_field import (
    SharedMCMField,
    SharedMCMFieldSnapshot,
)


class SharedFieldSessionError(ValueError):
    """Raised when a bounded shared-field session violates continuity."""


_DIGEST = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class SharedFieldSessionWindow:
    """One predeclared organism interval with completed reduced receptor frames."""

    field_time: CommonFieldTime
    frames: tuple[ReceptorContactFrame, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.field_time, CommonFieldTime):
            raise SharedFieldSessionError(
                "session window requires one common field time"
            )
        frames = tuple(self.frames)
        if not frames or any(
            not isinstance(frame, ReceptorContactFrame) for frame in frames
        ):
            raise SharedFieldSessionError(
                "session window requires completed receptor frames"
            )
        modalities = [frame.modality_id for frame in frames]
        if len(set(modalities)) != len(modalities):
            raise SharedFieldSessionError(
                "one session window permits one frame per modality"
            )
        object.__setattr__(
            self,
            "frames",
            tuple(sorted(frames, key=lambda frame: frame.modality_id)),
        )


@dataclass(frozen=True, slots=True)
class SharedFieldSessionStep:
    """One completed technical field step without interpretation."""

    step_index: int
    receptor_distribution: ReceptorDistribution
    field_state: SharedMCMFieldSnapshot

    def __post_init__(self) -> None:
        if (
            isinstance(self.step_index, bool)
            or not isinstance(self.step_index, int)
            or self.step_index < 0
        ):
            raise SharedFieldSessionError(
                "session step index must be non-negative"
            )
        if not isinstance(self.receptor_distribution, ReceptorDistribution):
            raise SharedFieldSessionError(
                "session step requires a receptor distribution"
            )
        if not isinstance(self.field_state, SharedMCMFieldSnapshot):
            raise SharedFieldSessionError(
                "session step requires a complete field state"
            )
        if self.field_state.last_distribution != self.receptor_distribution:
            raise SharedFieldSessionError(
                "session field state must retain its receptor distribution"
            )


@dataclass(frozen=True, slots=True)
class SharedFieldSessionResult:
    """Bounded technical progression through one unchanged shared field."""

    initial_layer_digest: str
    steps: tuple[SharedFieldSessionStep, ...]
    final_field: SharedMCMField

    def __post_init__(self) -> None:
        if (
            not isinstance(self.initial_layer_digest, str)
            or not _DIGEST.fullmatch(self.initial_layer_digest)
        ):
            raise SharedFieldSessionError(
                "session requires a canonical initial layer digest"
            )
        steps = tuple(self.steps)
        if not steps:
            raise SharedFieldSessionError("session requires at least one field step")
        if any(
            step.step_index != expected
            for expected, step in enumerate(steps)
        ):
            raise SharedFieldSessionError(
                "session step indices must be contiguous and start at zero"
            )
        if not isinstance(self.final_field, SharedMCMField):
            raise SharedFieldSessionError(
                "session requires one final shared field"
            )
        if self.final_field.snapshot() != steps[-1].field_state:
            raise SharedFieldSessionError(
                "session final field must match the final recorded state"
            )
        field_ids = {step.field_state.field_id for step in steps}
        layer_ids = {step.field_state.layer_id for step in steps}
        geometries = {step.field_state.geometry_id for step in steps}
        neuron_ids = {step.field_state.neuron_ids for step in steps}
        dock_maps = {step.field_state.dock_neuron_ids for step in steps}
        if any(
            len(values) != 1
            for values in (field_ids, layer_ids, geometries, neuron_ids, dock_maps)
        ):
            raise SharedFieldSessionError(
                "field, layer, geometry, neuron, and dock identities must stay fixed"
            )
        clocks = {
            step.receptor_distribution.field_time.clock_id for step in steps
        }
        if len(clocks) != 1:
            raise SharedFieldSessionError(
                "every session step must use one organism clock"
            )
        for earlier, later in zip(steps, steps[1:]):
            earlier_time = earlier.receptor_distribution.field_time
            later_time = later.receptor_distribution.field_time
            if earlier_time.window_end_tick != later_time.window_start_tick:
                raise SharedFieldSessionError(
                    "session field windows must be contiguous"
                )
            if later.field_state.tick != earlier.field_state.tick + 1:
                raise SharedFieldSessionError(
                    "session field ticks must advance exactly once per window"
                )
        object.__setattr__(self, "steps", steps)

    @property
    def step_count(self) -> int:
        return len(self.steps)


SharedFieldSessionObserver = Callable[[SharedFieldSessionStep], None]


def session_windows_from_common_receptor_capture(
    capture: CapturedCommonReceptorWindowAudit,
) -> tuple[SharedFieldSessionWindow, ...]:
    """Accept only complete, unambiguous captured states as field windows."""

    if not isinstance(capture, CapturedCommonReceptorWindowAudit):
        raise SharedFieldSessionError(
            "session window bridge requires a common receptor capture"
        )
    current_audit = audit_receptor_window_assignment(
        capture.sequences,
        capture.schedule,
    )
    if current_audit != capture.audit:
        raise SharedFieldSessionError(
            "captured receptor audit must match its sequences and schedule"
        )
    if (
        not current_audit.every_window_has_exactly_one_state_per_modality
        or current_audit.crossing_snapshot_ids
        or current_audit.outside_snapshot_ids
    ):
        raise SharedFieldSessionError(
            "every captured window must contain exactly one complete state "
            "per modality and no crossing or outside state"
        )

    frames_by_identity = {}
    for sequence in capture.sequences:
        for timed_frame in sequence.frames:
            identity = (sequence.modality_id, timed_frame.frame.snapshot_id)
            if identity in frames_by_identity:
                raise SharedFieldSessionError(
                    "captured receptor state identities must be unique"
                )
            frames_by_identity[identity] = timed_frame.frame

    frames_by_window = {
        window.window_index: [] for window in capture.schedule.windows
    }
    for assignment in current_audit.assignments:
        identity = (assignment.modality_id, assignment.snapshot_id)
        try:
            captured_frame = frames_by_identity[identity]
            frames_by_window[assignment.window_index].append(captured_frame)
        except (KeyError, IndexError) as exc:
            raise SharedFieldSessionError(
                "captured receptor assignment does not resolve exactly"
            ) from exc

    expected_modalities = set(current_audit.modality_ids)
    windows_out = []
    for window in capture.schedule.windows:
        frames = tuple(frames_by_window[window.window_index])
        if (
            len(frames) != len(expected_modalities)
            or {frame.modality_id for frame in frames} != expected_modalities
        ):
            raise SharedFieldSessionError(
                "captured receptor assignment is incomplete or ambiguous"
            )
        windows_out.append(SharedFieldSessionWindow(window.field_time, frames))
    return tuple(windows_out)


def _distributor_for(field: SharedMCMField) -> ReceptorDistributor:
    distributor = ReceptorDistributor()
    for dock in field.docks:
        distributor.attach(
            ReceptorDock(
                dock_id=dock.dock_id,
                modality_id=dock.dock_map.modality_id,
                receptor_geometry_id=dock.dock_map.receptor_geometry_id,
            )
        )
    return distributor


def run_shared_mcm_field_session(
    initial_field: SharedMCMField,
    windows: Iterable[SharedFieldSessionWindow],
    transition: MCMNeuronTransition,
    *,
    max_steps: int,
    observer: SharedFieldSessionObserver | None = None,
) -> SharedFieldSessionResult:
    """Advance one field through bounded contiguous completed receptor windows."""

    if not isinstance(initial_field, SharedMCMField):
        raise SharedFieldSessionError(
            "session requires one initial shared MCM field"
        )
    if not callable(transition):
        raise SharedFieldSessionError(
            "session transition must be supplied explicitly"
        )
    if (
        isinstance(max_steps, bool)
        or not isinstance(max_steps, int)
        or max_steps <= 0
    ):
        raise SharedFieldSessionError("max_steps must be a positive integer")
    if observer is not None and not callable(observer):
        raise SharedFieldSessionError("session observer must be callable")

    windows_out = tuple(windows)
    if not windows_out or any(
        not isinstance(window, SharedFieldSessionWindow)
        for window in windows_out
    ):
        raise SharedFieldSessionError(
            "session requires completed session windows"
        )
    if len(windows_out) > max_steps:
        raise SharedFieldSessionError(
            "session window count exceeds the explicit maximum"
        )

    expected_modalities = {
        dock.dock_map.modality_id for dock in initial_field.docks
    }
    clock_ids = {window.field_time.clock_id for window in windows_out}
    if len(clock_ids) != 1:
        raise SharedFieldSessionError(
            "every session window must use one organism clock"
        )
    for window in windows_out:
        if {frame.modality_id for frame in window.frames} != expected_modalities:
            raise SharedFieldSessionError(
                "every session window must contain every attached modality"
            )
    for earlier, later in zip(windows_out, windows_out[1:]):
        if (
            earlier.field_time.window_end_tick
            != later.field_time.window_start_tick
        ):
            raise SharedFieldSessionError(
                "session windows must be contiguous"
            )
    if initial_field.last_distribution is not None:
        previous_time = initial_field.last_distribution.field_time
        first_time = windows_out[0].field_time
        if first_time.clock_id != previous_time.clock_id:
            raise SharedFieldSessionError(
                "resumed session must keep the organism clock"
            )
        if first_time.window_start_tick != previous_time.window_end_tick:
            raise SharedFieldSessionError(
                "resumed session must continue at the previous window boundary"
            )

    distributor = _distributor_for(initial_field)
    initial_layer_digest = initial_field.layer.digest()
    current = initial_field
    steps = []
    for step_index, window in enumerate(windows_out):
        try:
            distribution = distributor.distribute(
                window.frames,
                window.field_time,
            )
            current = current.advance(distribution, transition)
        except ValueError as exc:
            raise SharedFieldSessionError(
                f"session step {step_index} failed: {exc}"
            ) from exc
        step = SharedFieldSessionStep(
            step_index=step_index,
            receptor_distribution=distribution,
            field_state=current.snapshot(),
        )
        if observer is not None:
            before = step.field_state.digest()
            observer(step)
            if step.field_state.digest() != before:
                raise SharedFieldSessionError(
                    "session observer changed the immutable field state"
                )
        steps.append(step)
    return SharedFieldSessionResult(
        initial_layer_digest=initial_layer_digest,
        steps=tuple(steps),
        final_field=current,
    )


def run_captured_shared_mcm_field_session(
    initial_field: SharedMCMField,
    capture: CapturedCommonReceptorWindowAudit,
    transition: MCMNeuronTransition,
    *,
    max_steps: int,
    observer: SharedFieldSessionObserver | None = None,
) -> SharedFieldSessionResult:
    """Run one bounded field session from strictly accepted captured windows."""

    return run_shared_mcm_field_session(
        initial_field,
        session_windows_from_common_receptor_capture(capture),
        transition,
        max_steps=max_steps,
        observer=observer,
    )


def shared_field_session_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            SharedFieldSessionWindow,
            SharedFieldSessionStep,
            SharedFieldSessionResult,
        )
        for item in fields(cls)
    )
