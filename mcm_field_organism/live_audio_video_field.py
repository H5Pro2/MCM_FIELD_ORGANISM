"""Explicit hardware bridge for one finite auditory-visual field contact."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
import time

from .auditory_baselines import AuditoryProbeConfig
from .audio_video_neutral_field_runtime import (
    CapturedAudioVideoNeutralFieldRun,
    capture_audio_video_into_neutral_field,
)
from .broadband_hearing_path import BroadbandHearingPath
from .finite_audio_video_field_run import (
    FiniteAudioVideoFieldError,
    FiniteAudioVideoFieldResult,
    capture_finite_audio_video_field,
)
from .finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from .live_audio_adapter import SoundDeviceInputSource
from .live_video_adapter import CameraStartupSummary, OpenCVVideoFrameSource
from .log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_time_alignment import (
    CapturedReceptorTimeAudit,
    capture_timed_audio_video_receptors,
)
from .common_receptor_window import (
    CapturedCommonReceptorWindowAudit,
    build_common_receptor_windows,
    capture_audio_video_in_common_windows,
)


@dataclass(frozen=True, slots=True)
class LiveAudioVideoFieldResult:
    """Camera startup evidence plus one reduced shared-field result."""

    camera_startup: CameraStartupSummary
    field_run: FiniteAudioVideoFieldResult

    def __post_init__(self) -> None:
        if not isinstance(self.camera_startup, CameraStartupSummary):
            raise FiniteAudioVideoFieldError(
                "live result requires completed camera startup evidence"
            )
        if not isinstance(self.field_run, FiniteAudioVideoFieldResult):
            raise FiniteAudioVideoFieldError(
                "live result requires a completed audio-video field run"
            )


@dataclass(frozen=True, slots=True)
class LiveAudioVideoTimeAuditResult:
    """Camera startup evidence plus timestamped reduced receptor sequences."""

    camera_startup: CameraStartupSummary
    receptor_time_audit: CapturedReceptorTimeAudit

    def __post_init__(self) -> None:
        if not isinstance(self.camera_startup, CameraStartupSummary):
            raise FiniteAudioVideoFieldError(
                "live time audit requires completed camera startup evidence"
            )
        if not isinstance(self.receptor_time_audit, CapturedReceptorTimeAudit):
            raise FiniteAudioVideoFieldError(
                "live time audit requires completed reduced receptor sequences"
            )


@dataclass(frozen=True, slots=True)
class LiveCommonReceptorWindowAuditResult:
    """Camera startup evidence plus one predeclared-window occupancy audit."""

    camera_startup: CameraStartupSummary
    receptor_window_audit: CapturedCommonReceptorWindowAudit

    def __post_init__(self) -> None:
        if not isinstance(self.camera_startup, CameraStartupSummary):
            raise FiniteAudioVideoFieldError(
                "live window audit requires completed camera startup evidence"
            )
        if not isinstance(
            self.receptor_window_audit, CapturedCommonReceptorWindowAudit
        ):
            raise FiniteAudioVideoFieldError(
                "live window audit requires completed receptor window evidence"
            )


@dataclass(frozen=True, slots=True)
class LiveAudioVideoNeutralFieldResult:
    """Camera startup evidence plus one bounded real shared-field run."""

    camera_startup: CameraStartupSummary
    field_run: CapturedAudioVideoNeutralFieldRun
    camera_capture_frame_count: int
    audio_overflow_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.camera_startup, CameraStartupSummary):
            raise FiniteAudioVideoFieldError(
                "live neutral field run requires camera startup evidence"
            )
        if not isinstance(self.field_run, CapturedAudioVideoNeutralFieldRun):
            raise FiniteAudioVideoFieldError(
                "live neutral field run requires one completed field capture"
            )
        for role in ("camera_capture_frame_count", "audio_overflow_count"):
            value = getattr(self, role)
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
            ):
                raise FiniteAudioVideoFieldError(
                    f"{role} must be a non-negative integer"
                )
        visual_sequence = next(
            sequence
            for sequence in self.field_run.receptor_sequences
            if sequence.modality_id == "visual"
        )
        if self.camera_capture_frame_count != len(visual_sequence.frames):
            raise FiniteAudioVideoFieldError(
                "camera capture count must match every visual receptor state"
            )


def capture_live_audio_video_field(
    *,
    camera_device: int,
    audio_device: int | str,
    duration_seconds: float = 1.0,
    camera_startup_frames: int = 10,
) -> LiveAudioVideoFieldResult:
    """Open explicit devices and perform one finite concurrent field contact."""

    duration = float(duration_seconds)
    visual_config = VisualGridConfig()
    visual_exact = duration * visual_config.frames_per_second
    visual_frame_count = round(visual_exact)
    if not math.isclose(
        visual_exact,
        visual_frame_count,
        rel_tol=0.0,
        abs_tol=1e-10,
    ):
        raise FiniteAudioVideoFieldError(
            "duration_seconds must contain whole visual frames"
        )

    auditory_config = LogSpectralConfig()
    auditory_source_config = AuditoryProbeConfig(
        sample_rate=auditory_config.sample_rate,
        frame_size=auditory_config.hop_size,
    )
    auditory_exact = duration / auditory_config.hop_seconds
    if not math.isclose(
        auditory_exact,
        round(auditory_exact),
        rel_tol=0.0,
        abs_tol=1e-10,
    ):
        raise FiniteAudioVideoFieldError(
            "duration_seconds must contain whole auditory receptor chunks"
        )

    visual_receptor = LocalChannelGridReceptor(visual_config)
    auditory_path = BroadbandHearingPath(
        LogSpectralReceptor(auditory_config)
    )
    with OpenCVVideoFrameSource(
        device_index=camera_device,
        config=visual_config,
        startup_frame_count=camera_startup_frames,
    ) as video_source:
        startup = video_source.prepare()
        with SoundDeviceInputSource(
            device=audio_device,
            config=auditory_source_config,
        ) as audio_source:
            field_run = capture_finite_audio_video_field(
                audio_source,
                video_source,
                auditory_path,
                visual_receptor,
                duration_seconds=duration,
                video_frame_count=visual_frame_count,
            )
    return LiveAudioVideoFieldResult(startup, field_run)


def capture_live_audio_video_time_audit(
    *,
    camera_device: int,
    audio_device: int | str,
    nominal_duration_seconds: float = 1.0,
    camera_startup_frames: int = 10,
) -> LiveAudioVideoTimeAuditResult:
    """Measure every reduced audio-video state on one organism clock."""

    visual_config = VisualGridConfig()
    auditory_config = LogSpectralConfig()
    auditory_source_config = AuditoryProbeConfig(
        sample_rate=auditory_config.sample_rate,
        frame_size=auditory_config.hop_size,
    )
    visual_receptor = LocalChannelGridReceptor(visual_config)
    auditory_path = BroadbandHearingPath(
        LogSpectralReceptor(auditory_config)
    )
    with OpenCVVideoFrameSource(
        device_index=camera_device,
        config=visual_config,
        startup_frame_count=camera_startup_frames,
    ) as video_source:
        startup = video_source.prepare()
        with SoundDeviceInputSource(
            device=audio_device,
            config=auditory_source_config,
        ) as audio_source:
            audit = capture_timed_audio_video_receptors(
                audio_source,
                video_source,
                auditory_path,
                visual_receptor,
                nominal_duration_seconds=nominal_duration_seconds,
            )
    return LiveAudioVideoTimeAuditResult(startup, audit)


def capture_live_audio_video_into_neutral_field(
    *,
    camera_device: int,
    audio_device: int | str,
    field_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig | None = None,
    nominal_duration_seconds: float = 1.0,
    camera_startup_frames: int = 10,
) -> LiveAudioVideoNeutralFieldResult:
    """Open explicit devices and feed their native completions to one field."""

    visual_config = VisualGridConfig()
    auditory_config = LogSpectralConfig()
    auditory_source_config = AuditoryProbeConfig(
        sample_rate=auditory_config.sample_rate,
        frame_size=auditory_config.hop_size,
    )
    visual_receptor = LocalChannelGridReceptor(visual_config)
    auditory_path = BroadbandHearingPath(LogSpectralReceptor(auditory_config))
    with OpenCVVideoFrameSource(
        device_index=camera_device,
        config=visual_config,
        startup_frame_count=camera_startup_frames,
    ) as video_source:
        startup = video_source.prepare()
        with SoundDeviceInputSource(
            device=audio_device,
            config=auditory_source_config,
        ) as audio_source:
            field_run = capture_audio_video_into_neutral_field(
                audio_source,
                video_source,
                auditory_path,
                visual_receptor,
                field_config,
                afterimage_config=afterimage_config,
                nominal_duration_seconds=nominal_duration_seconds,
            )
            audio_overflow_count = audio_source.overflow_count
            camera_capture_frame_count = video_source.capture_frames_read
    return LiveAudioVideoNeutralFieldResult(
        startup,
        field_run,
        camera_capture_frame_count,
        audio_overflow_count,
    )


def capture_live_common_receptor_window_audit(
    *,
    camera_device: int,
    audio_device: int | str,
    window_seconds: float = 1.0,
    window_count: int = 3,
    camera_startup_frames: int = 10,
    preparation_lead_seconds: float = 0.25,
) -> LiveCommonReceptorWindowAuditResult:
    """Declare organism windows, then audit native live receptor occupancy."""

    width = float(window_seconds)
    lead = float(preparation_lead_seconds)
    if (
        not math.isfinite(width)
        or width <= 0.0
        or width > 10.0
        or not math.isfinite(lead)
        or lead <= 0.0
        or lead > 2.0
    ):
        raise FiniteAudioVideoFieldError(
            "window and preparation durations must be finite and positive"
        )
    if (
        isinstance(window_count, bool)
        or not isinstance(window_count, int)
        or window_count <= 0
    ):
        raise FiniteAudioVideoFieldError("window_count must be a positive integer")

    visual_config = VisualGridConfig()
    auditory_config = LogSpectralConfig()
    source_config = AuditoryProbeConfig(
        sample_rate=auditory_config.sample_rate,
        frame_size=auditory_config.hop_size,
    )
    visual_receptor = LocalChannelGridReceptor(visual_config)
    auditory_path = BroadbandHearingPath(LogSpectralReceptor(auditory_config))
    with OpenCVVideoFrameSource(
        device_index=camera_device,
        config=visual_config,
        startup_frame_count=camera_startup_frames,
    ) as video_source:
        startup = video_source.prepare()
        with SoundDeviceInputSource(
            device=audio_device,
            config=source_config,
        ) as audio_source:
            schedule = build_common_receptor_windows(
                anchor_tick=time.monotonic_ns() + int(lead * 1_000_000_000),
                window_width_ticks=int(width * 1_000_000_000),
                window_count=window_count,
            )
            audit = capture_audio_video_in_common_windows(
                audio_source,
                video_source,
                auditory_path,
                visual_receptor,
                schedule,
            )
    return LiveCommonReceptorWindowAuditResult(startup, audit)


def live_audio_video_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            LiveAudioVideoFieldResult,
            LiveAudioVideoTimeAuditResult,
            LiveCommonReceptorWindowAuditResult,
            LiveAudioVideoNeutralFieldResult,
        )
        for item in fields(cls)
    )
