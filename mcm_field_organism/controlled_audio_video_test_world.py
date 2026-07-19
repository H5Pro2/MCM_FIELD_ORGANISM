"""Procedural audio-video worlds for repeatable contact with the shared field."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
from typing import Iterable

import numpy as np

from .broadband_hearing_path import BroadbandHearingPath
from .audio_video_neutral_field_runtime import (
    CapturedAudioVideoNeutralFieldRun,
    _advance_captured_audio_video_sequences,
    capture_audio_video_into_neutral_field,
)
from .finite_video_path import (
    LocalChannelGridReceptor,
    SyntheticVideoFrameSource,
    VisualGridConfig,
)
from .live_audio_adapter import SyntheticAudioFrameSource
from .log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import (
    CommonFieldTime,
    from_auditory_receptor_state,
    from_visual_receptor_state,
)
from .receptor_time_alignment import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


class ControlledTestWorldError(ValueError):
    """Raised when a procedural world violates the neutral source contract."""


@dataclass(frozen=True, slots=True)
class ControlledWorldPhase:
    phase_id: str
    duration_seconds: float
    auditory_frequency: float
    auditory_amplitude: float
    visual_origin: tuple[int, int]
    visual_velocity: tuple[int, int]
    visual_extent: tuple[int, int]
    visual_channels: tuple[int, int, int]

    def __post_init__(self) -> None:
        if not isinstance(self.phase_id, str) or not _IDENTIFIER.fullmatch(
            self.phase_id
        ):
            raise ControlledTestWorldError(
                "phase_id must be a lowercase technical identifier"
            )
        duration = float(self.duration_seconds)
        frequency = float(self.auditory_frequency)
        amplitude = float(self.auditory_amplitude)
        if not math.isfinite(duration) or duration <= 0.0:
            raise ControlledTestWorldError(
                "phase duration must be finite and greater than zero"
            )
        if not math.isfinite(frequency) or frequency < 0.0:
            raise ControlledTestWorldError(
                "auditory frequency must be finite and non-negative"
            )
        if not math.isfinite(amplitude) or amplitude < 0.0 or amplitude > 1.0:
            raise ControlledTestWorldError(
                "auditory amplitude must stay within 0..1"
            )
        if (frequency == 0.0) != (amplitude == 0.0):
            raise ControlledTestWorldError(
                "auditory frequency and amplitude must be zero together"
            )

        pairs = (
            ("visual_origin", self.visual_origin, True),
            ("visual_velocity", self.visual_velocity, True),
            ("visual_extent", self.visual_extent, False),
        )
        for role, values, allow_zero in pairs:
            values_out = tuple(values)
            if len(values_out) != 2 or any(
                isinstance(value, bool) or not isinstance(value, int)
                for value in values_out
            ):
                raise ControlledTestWorldError(
                    f"{role} must contain exactly two integers"
                )
            if not allow_zero and any(value <= 0 for value in values_out):
                raise ControlledTestWorldError(
                    "visual_extent values must be positive"
                )
            object.__setattr__(self, role, values_out)

        channels = tuple(self.visual_channels)
        if len(channels) != 3 or any(
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < 0
            or value > 255
            for value in channels
        ):
            raise ControlledTestWorldError(
                "visual_channels must contain three uint8-compatible values"
            )
        object.__setattr__(self, "duration_seconds", duration)
        object.__setattr__(self, "auditory_frequency", frequency)
        object.__setattr__(self, "auditory_amplitude", amplitude)
        object.__setattr__(self, "visual_channels", channels)


@dataclass(frozen=True, slots=True)
class ControlledAudioVideoTestWorld:
    world_id: str
    phases: tuple[ControlledWorldPhase, ...]
    audio_config: LogSpectralConfig
    visual_config: VisualGridConfig
    background_channels: tuple[int, int, int] = (16, 16, 16)

    def __post_init__(self) -> None:
        if not isinstance(self.world_id, str) or not _IDENTIFIER.fullmatch(
            self.world_id
        ):
            raise ControlledTestWorldError(
                "world_id must be a lowercase technical identifier"
            )
        phases = tuple(self.phases)
        if not phases or any(
            not isinstance(phase, ControlledWorldPhase) for phase in phases
        ):
            raise ControlledTestWorldError(
                "world requires at least one controlled phase"
            )
        if len({phase.phase_id for phase in phases}) != len(phases):
            raise ControlledTestWorldError("phase identifiers must be unique")
        if not isinstance(self.audio_config, LogSpectralConfig):
            raise ControlledTestWorldError(
                "world requires one logarithmic audio receptor configuration"
            )
        if not isinstance(self.visual_config, VisualGridConfig):
            raise ControlledTestWorldError(
                "world requires one visual receptor configuration"
            )
        background = tuple(self.background_channels)
        if len(background) != 3 or any(
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < 0
            or value > 255
            for value in background
        ):
            raise ControlledTestWorldError(
                "background_channels must contain three uint8-compatible values"
            )
        for phase in phases:
            audio_count = phase.duration_seconds / self.audio_config.hop_seconds
            video_count = (
                phase.duration_seconds * self.visual_config.frames_per_second
            )
            if not math.isclose(audio_count, round(audio_count), abs_tol=1e-10):
                raise ControlledTestWorldError(
                    "every phase must contain complete auditory hops"
                )
            if not math.isclose(video_count, round(video_count), abs_tol=1e-10):
                raise ControlledTestWorldError(
                    "every phase must contain complete visual frames"
                )
            if phase.auditory_frequency >= self.audio_config.sample_rate / 2.0:
                raise ControlledTestWorldError(
                    "auditory phase frequency must remain below Nyquist"
                )
            if any(
                extent > bound
                for extent, bound in zip(
                    phase.visual_extent,
                    (
                        self.visual_config.source_width,
                        self.visual_config.source_height,
                    ),
                )
            ):
                raise ControlledTestWorldError(
                    "visual phase extent must fit the source geometry"
                )
        object.__setattr__(self, "phases", phases)
        object.__setattr__(self, "background_channels", background)

    @property
    def duration_seconds(self) -> float:
        return sum(phase.duration_seconds for phase in self.phases)

    @property
    def audio_frame_count(self) -> int:
        return round(self.duration_seconds / self.audio_config.hop_seconds)

    @property
    def video_frame_count(self) -> int:
        return round(
            self.duration_seconds * self.visual_config.frames_per_second
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "world_id": self.world_id,
            "background_channels": list(self.background_channels),
            "audio_config": {
                "sample_rate": self.audio_config.sample_rate,
                "window_size": self.audio_config.window_size,
                "hop_size": self.audio_config.hop_size,
                "min_frequency": self.audio_config.min_frequency,
                "max_frequency": self.audio_config.max_frequency,
                "band_count": self.audio_config.band_count,
            },
            "visual_config": {
                "source_width": self.visual_config.source_width,
                "source_height": self.visual_config.source_height,
                "grid_columns": self.visual_config.grid_columns,
                "grid_rows": self.visual_config.grid_rows,
                "frames_per_second": self.visual_config.frames_per_second,
            },
            "phases": [
                {
                    "phase_id": phase.phase_id,
                    "duration_seconds": phase.duration_seconds,
                    "auditory_frequency": phase.auditory_frequency,
                    "auditory_amplitude": phase.auditory_amplitude,
                    "visual_origin": list(phase.visual_origin),
                    "visual_velocity": list(phase.visual_velocity),
                    "visual_extent": list(phase.visual_extent),
                    "visual_channels": list(phase.visual_channels),
                }
                for phase in self.phases
            ],
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def open_sources(
        self,
    ) -> tuple[
        SyntheticAudioFrameSource,
        SyntheticVideoFrameSource,
        BroadbandHearingPath,
        LocalChannelGridReceptor,
    ]:
        audio_frames: list[tuple[float, ...]] = []
        video_frames: list[np.ndarray] = []
        sample_cursor = 0
        visual_cursor = 0

        for phase in self.phases:
            audio_count = round(
                phase.duration_seconds / self.audio_config.hop_seconds
            )
            for _ in range(audio_count):
                samples = tuple(
                    0.0
                    if phase.auditory_amplitude == 0.0
                    else phase.auditory_amplitude
                    * math.sin(
                        2.0
                        * math.pi
                        * phase.auditory_frequency
                        * (sample_cursor + offset)
                        / self.audio_config.sample_rate
                    )
                    for offset in range(self.audio_config.hop_size)
                )
                audio_frames.append(samples)
                sample_cursor += self.audio_config.hop_size

            video_count = round(
                phase.duration_seconds * self.visual_config.frames_per_second
            )
            for local_index in range(video_count):
                frame = np.empty(
                    (
                        self.visual_config.source_height,
                        self.visual_config.source_width,
                        3,
                    ),
                    dtype=np.uint8,
                )
                frame[:, :] = self.background_channels
                width, height = phase.visual_extent
                origin_x, origin_y = phase.visual_origin
                velocity_x, velocity_y = phase.visual_velocity
                x = (origin_x + velocity_x * local_index) % (
                    self.visual_config.source_width - width + 1
                )
                y = (origin_y + velocity_y * local_index) % (
                    self.visual_config.source_height - height + 1
                )
                frame[y : y + height, x : x + width] = phase.visual_channels
                video_frames.append(frame)
                visual_cursor += 1

        if len(audio_frames) != self.audio_frame_count:
            raise ControlledTestWorldError(
                "generated auditory frame count violates the world schedule"
            )
        if visual_cursor != self.video_frame_count:
            raise ControlledTestWorldError(
                "generated visual frame count violates the world schedule"
            )
        return (
            SyntheticAudioFrameSource(tuple(audio_frames)),
            SyntheticVideoFrameSource(tuple(video_frames)),
            BroadbandHearingPath(
                LogSpectralReceptor(self.audio_config)
            ),
            LocalChannelGridReceptor(self.visual_config),
        )


def _base_configs() -> tuple[LogSpectralConfig, VisualGridConfig]:
    return (
        LogSpectralConfig(
            sample_rate=4000,
            window_size=400,
            hop_size=40,
            min_frequency=50.0,
            max_frequency=1500.0,
            band_count=12,
        ),
        VisualGridConfig(
            source_width=24,
            source_height=16,
            grid_columns=6,
            grid_rows=4,
            frames_per_second=10.0,
        ),
    )


def controlled_reentry_world_family(
) -> tuple[ControlledAudioVideoTestWorld, ControlledAudioVideoTestWorld]:
    """Return matched recurrence and changed-reentry worlds without semantics."""

    audio_config, visual_config = _base_configs()
    first = ControlledWorldPhase(
        "contact.0",
        1.0,
        320.0,
        0.25,
        (2, 3),
        (1, 0),
        (6, 5),
        (220, 70, 45),
    )
    gap = ControlledWorldPhase(
        "gap.0",
        1.0,
        0.0,
        0.0,
        (9, 5),
        (0, 0),
        (3, 3),
        (16, 16, 16),
    )
    repeated = ControlledWorldPhase(
        "contact.1",
        1.0,
        320.0,
        0.25,
        (2, 3),
        (1, 0),
        (6, 5),
        (220, 70, 45),
    )
    changed = ControlledWorldPhase(
        "contact.1",
        1.0,
        760.0,
        0.25,
        (15, 8),
        (-1, 0),
        (6, 5),
        (45, 120, 230),
    )
    return (
        ControlledAudioVideoTestWorld(
            "world.reentry.same",
            (first, gap, repeated),
            audio_config,
            visual_config,
        ),
        ControlledAudioVideoTestWorld(
            "world.reentry.changed",
            (first, gap, changed),
            audio_config,
            visual_config,
        ),
    )


def controlled_history_holdout_world_family(
) -> tuple[ControlledAudioVideoTestWorld, ControlledAudioVideoTestWorld]:
    """Return different-history worlds with one identical final probe."""

    same, changed = controlled_reentry_world_family()
    probe = ControlledWorldPhase(
        "probe.0",
        1.0,
        1120.0,
        0.2,
        (8, 2),
        (0, 1),
        (5, 6),
        (65, 210, 105),
    )
    return (
        ControlledAudioVideoTestWorld(
            "world.history.same",
            same.phases + (probe,),
            same.audio_config,
            same.visual_config,
            same.background_channels,
        ),
        ControlledAudioVideoTestWorld(
            "world.history.changed",
            changed.phases + (probe,),
            changed.audio_config,
            changed.visual_config,
            changed.background_channels,
        ),
    )


def run_controlled_test_world(
    world: ControlledAudioVideoTestWorld,
    field_config: NeutralLocalFieldSubstrateConfig,
    *,
    afterimage_config: NeutralFastAfterimageConfig | None = None,
) -> CapturedAudioVideoNeutralFieldRun:
    """Let one procedural world reach the unchanged shared-field runtime."""

    if not isinstance(world, ControlledAudioVideoTestWorld):
        raise ControlledTestWorldError(
            "controlled run requires one procedural audio-video world"
        )
    if not isinstance(field_config, NeutralLocalFieldSubstrateConfig):
        raise ControlledTestWorldError(
            "controlled run requires an explicit neutral field configuration"
        )
    sources = world.open_sources()
    return capture_audio_video_into_neutral_field(
        *sources,
        field_config,
        afterimage_config=afterimage_config,
        nominal_duration_seconds=world.duration_seconds,
    )


def _scheduled_phase_sequences(
    world: ControlledAudioVideoTestWorld,
    phase: ControlledWorldPhase,
    audio_source: SyntheticAudioFrameSource,
    video_source: SyntheticVideoFrameSource,
    auditory_path: BroadbandHearingPath,
    visual_receptor: LocalChannelGridReceptor,
    *,
    audio_frame_start: int,
    video_frame_start: int,
    clock_id: str,
    ticks_per_second: float,
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    audio_frames = []
    audio_count = round(phase.duration_seconds / world.audio_config.hop_seconds)
    for local_index in range(audio_count):
        frame_index = audio_frame_start + local_index
        state = auditory_path.push(audio_source.read_frame())
        if state is None:
            continue
        start = round(
            frame_index * world.audio_config.hop_seconds * ticks_per_second
        )
        end = round(
            (frame_index + 1)
            * world.audio_config.hop_seconds
            * ticks_per_second
        )
        audio_frames.append(
            OrganismTimedReceptorFrame(
                from_auditory_receptor_state(state),
                CommonFieldTime(clock_id, start, end),
            )
        )

    visual_frames = []
    video_count = round(
        phase.duration_seconds * world.visual_config.frames_per_second
    )
    frame_seconds = 1.0 / world.visual_config.frames_per_second
    for local_index in range(video_count):
        frame_index = video_frame_start + local_index
        state = visual_receptor.analyze(
            video_source.read_frame(),
            frame_index=frame_index,
        )
        start = round(frame_index * frame_seconds * ticks_per_second)
        end = round((frame_index + 1) * frame_seconds * ticks_per_second)
        visual_frames.append(
            OrganismTimedReceptorFrame(
                from_visual_receptor_state(state),
                CommonFieldTime(clock_id, start, end),
            )
        )
    return (
        ReceptorTimeSequence(
            "auditory",
            auditory_path.geometry_id,
            clock_id,
            tuple(audio_frames),
        ),
        ReceptorTimeSequence(
            "visual",
            visual_receptor.config.geometry_id,
            clock_id,
            tuple(visual_frames),
        ),
    )


def run_controlled_test_world_phases(
    world: ControlledAudioVideoTestWorld,
    field_config: NeutralLocalFieldSubstrateConfig,
    *,
    afterimage_config: NeutralFastAfterimageConfig | None = None,
    clock_id: str = "organism.controlled_world",
    ticks_per_second: float = 1_000_000.0,
) -> tuple[CapturedAudioVideoNeutralFieldRun, ...]:
    """Advance every world phase as one deterministic completed field tick."""

    if not isinstance(world, ControlledAudioVideoTestWorld):
        raise ControlledTestWorldError(
            "controlled phase run requires one procedural audio-video world"
        )
    if not isinstance(field_config, NeutralLocalFieldSubstrateConfig):
        raise ControlledTestWorldError(
            "controlled phase run requires an explicit field configuration"
        )
    rate = float(ticks_per_second)
    if not math.isfinite(rate) or rate <= 0.0:
        raise ControlledTestWorldError(
            "ticks_per_second must be finite and greater than zero"
        )
    if not isinstance(clock_id, str) or not clock_id:
        raise ControlledTestWorldError(
            "controlled phase run requires one named organism clock"
        )

    audio_source, video_source, auditory_path, visual_receptor = (
        world.open_sources()
    )
    runs = []
    field = None
    audio_cursor = 0
    video_cursor = 0
    for phase in world.phases:
        sequences = _scheduled_phase_sequences(
            world,
            phase,
            audio_source,
            video_source,
            auditory_path,
            visual_receptor,
            audio_frame_start=audio_cursor,
            video_frame_start=video_cursor,
            clock_id=clock_id,
            ticks_per_second=rate,
        )
        run = _advance_captured_audio_video_sequences(
            sequences,
            visual_receptor,
            field_config,
            afterimage_config=afterimage_config,
            initial_field=field,
            ticks_per_second=rate,
        )
        runs.append(run)
        field = run.field_run.field
        audio_cursor += round(
            phase.duration_seconds / world.audio_config.hop_seconds
        )
        video_cursor += round(
            phase.duration_seconds * world.visual_config.frames_per_second
        )
    return tuple(runs)


def controlled_test_world_public_roles() -> tuple[str, ...]:
    return (
        "world_id",
        "phases",
        "audio_config",
        "visual_config",
        "background_channels",
    )
