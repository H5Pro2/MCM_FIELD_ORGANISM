"""Explicit hardware bridge for one finite auditory-visual field contact."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

from .auditory_baselines import AuditoryProbeConfig
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
from .receptor_time_alignment import (
    CapturedReceptorTimeAudit,
    capture_timed_audio_video_receptors,
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


def live_audio_video_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            LiveAudioVideoFieldResult,
            LiveAudioVideoTimeAuditResult,
        )
        for item in fields(cls)
    )
