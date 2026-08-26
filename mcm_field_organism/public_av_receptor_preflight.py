"""Observer-side compatibility preflight before any public AV receptor run."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
from pathlib import Path

import numpy as np

from .finite_video_path import VisualGridConfig
from .log_spectral_receptor import LogSpectralConfig
from .public_av_container_source import (
    PUBLIC_MEDIA_CLOCK_ID,
    decode_audited_public_av_sources,
)
from .public_av_interval_audit import run_public_av_interval_audit
from .public_media_source_contract import PublicMediaSourceContract


class PublicAVReceptorPreflightError(ValueError):
    """Raised when a compatibility preflight crosses the receptor boundary."""


@dataclass(frozen=True, slots=True)
class PublicAVReceptorPreflight:
    source_id: str
    clock_id: str
    source_audit_accepted: bool
    interval_audit_repeatable: bool
    interval_audit_gap_free: bool
    audio_sample_rate_matches: bool
    audio_frame_size_matches: bool
    audio_samples_finite: bool
    audio_samples_within_domain: bool
    video_shape_matches: bool
    video_dtype_matches: bool
    video_frames_immutable: bool
    receptor_prerequisites_met: bool
    receptor_run_allowed: bool = False
    field_run_allowed: bool = False
    raw_payload_retained: bool = False

    def __post_init__(self) -> None:
        if not self.source_id or self.clock_id != PUBLIC_MEDIA_CLOCK_ID:
            raise PublicAVReceptorPreflightError("invalid public source identity or clock")
        boolean_roles = tuple(
            item.name
            for item in fields(self)
            if item.name not in {"source_id", "clock_id"}
        )
        if any(not isinstance(getattr(self, role), bool) for role in boolean_roles):
            raise PublicAVReceptorPreflightError("preflight outcomes must be boolean")
        prerequisites = all(
            getattr(self, role)
            for role in (
                "source_audit_accepted",
                "interval_audit_repeatable",
                "interval_audit_gap_free",
                "audio_sample_rate_matches",
                "audio_frame_size_matches",
                "audio_samples_finite",
                "audio_samples_within_domain",
                "video_shape_matches",
                "video_dtype_matches",
                "video_frames_immutable",
            )
        )
        if self.receptor_prerequisites_met != prerequisites:
            raise PublicAVReceptorPreflightError("prerequisite aggregate is inconsistent")
        if self.receptor_run_allowed or self.field_run_allowed or self.raw_payload_retained:
            raise PublicAVReceptorPreflightError(
                "preflight cannot release receptors, fields, or raw payloads"
            )


def run_public_av_receptor_preflight(
    path: Path,
    contract: PublicMediaSourceContract,
    auditory_config: LogSpectralConfig,
    visual_config: VisualGridConfig,
    *,
    duration_seconds: float = 0.5,
    start_tick: int = 0,
) -> PublicAVReceptorPreflight:
    """Check source/config compatibility without constructing either receptor."""

    interval = run_public_av_interval_audit(
        path,
        contract,
        duration_seconds=duration_seconds,
        start_tick=start_tick,
    )
    sources = decode_audited_public_av_sources(
        path,
        contract,
        duration_seconds=duration_seconds,
        start_tick=start_tick,
        audio_frame_samples=auditory_config.hop_size,
    )
    samples, _, _ = sources.audio.read_timed_frame()
    frame, _, _ = sources.video.read_timed_frame()
    audio_values = np.asarray(samples, dtype=np.float64)
    expected_shape = (
        visual_config.source_height,
        visual_config.source_width,
        3,
    )
    outcomes = {
        "source_audit_accepted": sources.source_audit.accepted,
        "interval_audit_repeatable": interval.repeatable,
        "interval_audit_gap_free": (
            interval.audio.gap_count == 0 and interval.video.gap_count == 0
        ),
        "audio_sample_rate_matches": sources.sample_rate == auditory_config.sample_rate,
        "audio_frame_size_matches": len(samples) == auditory_config.hop_size,
        "audio_samples_finite": bool(np.all(np.isfinite(audio_values))),
        "audio_samples_within_domain": bool(np.all(np.abs(audio_values) <= 1.0)),
        "video_shape_matches": frame.shape == expected_shape,
        "video_dtype_matches": frame.dtype == np.uint8,
        "video_frames_immutable": not frame.flags.writeable,
    }
    return PublicAVReceptorPreflight(
        source_id=sources.source_audit.source_id,
        clock_id=sources.clock_id,
        **outcomes,
        receptor_prerequisites_met=all(outcomes.values()),
    )


def public_av_receptor_preflight_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(PublicAVReceptorPreflight))
