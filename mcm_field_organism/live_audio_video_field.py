"""Explicit hardware bridge for one finite auditory-visual field contact."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, fields, replace
import math
from queue import Queue
import time
from typing import Callable

from .auditory_baselines import AuditoryProbeConfig
from .audio_video_neutral_field_runtime import (
    CapturedAudioVideoNeutralFieldRun,
    _advance_captured_audio_video_sequences,
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
from .neutral_field_session import NeutralFieldSessionResult
from .receptor_time_alignment import (
    CapturedReceptorTimeAudit,
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
    capture_timed_audio_video_receptor_sequences,
    capture_timed_audio_video_receptors,
)
from .receptor_contract import (
    CommonFieldTime,
    from_auditory_receptor_state,
    from_visual_receptor_state,
)
from .common_receptor_window import (
    CapturedCommonReceptorWindowAudit,
    build_common_receptor_windows,
    capture_audio_video_in_common_windows,
)
from .shared_mcm_field import SharedMCMFieldSnapshot, restore_shared_mcm_field


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


@dataclass(frozen=True, slots=True)
class LiveAudioVideoNeutralSessionResult:
    """Reduced result of several live windows in one continuing field."""

    camera_startup: CameraStartupSummary
    field_session: NeutralFieldSessionResult
    camera_capture_frame_count: int
    audio_overflow_count: int
    checkpoint_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.camera_startup, CameraStartupSummary):
            raise FiniteAudioVideoFieldError(
                "live neutral session requires camera startup evidence"
            )
        if not isinstance(self.field_session, NeutralFieldSessionResult):
            raise FiniteAudioVideoFieldError(
                "live neutral session requires one continued field result"
            )
        for role in (
            "camera_capture_frame_count",
            "audio_overflow_count",
            "checkpoint_count",
        ):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise FiniteAudioVideoFieldError(
                    f"{role} must be a non-negative integer"
                )
        if self.checkpoint_count >= self.field_session.window_count:
            raise FiniteAudioVideoFieldError(
                "checkpoints may only occur between completed field windows"
            )


@dataclass(frozen=True, slots=True)
class LiveFieldWindowObservation:
    """Compact passive reading of one completed live field window."""

    window_index: int
    window_start_tick: int
    window_end_tick: int
    auditory_receptor_count: int
    visual_receptor_count: int
    source_support_count: int
    activation_min: float
    activation_max: float
    activation_absolute_mean: float
    active_activation_count: int
    afterimage_min: float
    afterimage_max: float
    afterimage_absolute_mean: float
    active_afterimage_count: int
    field_digest: str
    exact_baseline_activation_max_error: float
    exact_baseline_afterimage_max_error: float
    exact_baseline_digest_matches: bool
    checkpoint_restored: bool

    def __post_init__(self) -> None:
        integer_roles = (
            "window_index",
            "window_start_tick",
            "window_end_tick",
            "auditory_receptor_count",
            "visual_receptor_count",
            "source_support_count",
            "active_activation_count",
            "active_afterimage_count",
        )
        for role in integer_roles:
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise FiniteAudioVideoFieldError(
                    f"{role} must be a non-negative integer"
                )
        if self.window_end_tick <= self.window_start_tick:
            raise FiniteAudioVideoFieldError(
                "live field observation requires an advancing organism window"
            )
        if (
            self.auditory_receptor_count + self.visual_receptor_count
            != self.source_support_count
        ):
            raise FiniteAudioVideoFieldError(
                "modal receptor counts must equal unique source supports"
            )
        for role in (
            "activation_min",
            "activation_max",
            "activation_absolute_mean",
            "afterimage_min",
            "afterimage_max",
            "afterimage_absolute_mean",
            "exact_baseline_activation_max_error",
            "exact_baseline_afterimage_max_error",
        ):
            value = float(getattr(self, role))
            if not math.isfinite(value) or (
                role.startswith("exact_baseline_") and value < 0.0
            ):
                raise FiniteAudioVideoFieldError(f"{role} must be finite")
        if not isinstance(self.field_digest, str) or not self.field_digest:
            raise FiniteAudioVideoFieldError(
                "live field observation requires a field digest"
            )
        if not isinstance(self.exact_baseline_digest_matches, bool):
            raise FiniteAudioVideoFieldError(
                "exact_baseline_digest_matches must be boolean"
            )
        if not isinstance(self.checkpoint_restored, bool):
            raise FiniteAudioVideoFieldError(
                "checkpoint_restored must be boolean"
            )


LiveFieldWindowObserver = Callable[[LiveFieldWindowObservation], object]


def _observe_live_field_window(
    window_index: int,
    captured: CapturedAudioVideoNeutralFieldRun,
    exact_baseline: CapturedAudioVideoNeutralFieldRun,
    *,
    checkpoint_restored: bool,
) -> LiveFieldWindowObservation:
    all_frames = tuple(
        timed_frame
        for sequence in captured.receptor_sequences
        for timed_frame in sequence.frames
    )
    counts = {
        sequence.modality_id: len(sequence.frames)
        for sequence in captured.receptor_sequences
    }
    neurons = captured.field_run.field.layer.neurons
    activation = tuple(float(neuron.activation) for neuron in neurons)
    afterimage = tuple(float(neuron.afterimage) for neuron in neurons)
    baseline_neurons = exact_baseline.field_run.field.layer.neurons
    if tuple(neuron.neuron_id for neuron in baseline_neurons) != tuple(
        neuron.neuron_id for neuron in neurons
    ):
        raise FiniteAudioVideoFieldError(
            "exact live baseline must preserve the field neuron identities"
        )
    baseline_activation = tuple(
        float(neuron.activation) for neuron in baseline_neurons
    )
    baseline_afterimage = tuple(
        float(neuron.afterimage) for neuron in baseline_neurons
    )
    return LiveFieldWindowObservation(
        window_index=window_index,
        window_start_tick=min(
            item.field_time.window_start_tick for item in all_frames
        ),
        window_end_tick=max(
            item.field_time.window_end_tick for item in all_frames
        ),
        auditory_receptor_count=counts["auditory"],
        visual_receptor_count=counts["visual"],
        source_support_count=captured.field_run.source_support_count,
        activation_min=min(activation),
        activation_max=max(activation),
        activation_absolute_mean=(
            sum(abs(value) for value in activation) / len(activation)
        ),
        active_activation_count=sum(value != 0.0 for value in activation),
        afterimage_min=min(afterimage),
        afterimage_max=max(afterimage),
        afterimage_absolute_mean=(
            sum(abs(value) for value in afterimage) / len(afterimage)
        ),
        active_afterimage_count=sum(value != 0.0 for value in afterimage),
        field_digest=captured.field_run.field.snapshot().digest(),
        exact_baseline_activation_max_error=max(
            abs(actual - expected)
            for actual, expected in zip(
                activation,
                baseline_activation,
                strict=True,
            )
        ),
        exact_baseline_afterimage_max_error=max(
            abs(actual - expected)
            for actual, expected in zip(
                afterimage,
                baseline_afterimage,
                strict=True,
            )
        ),
        exact_baseline_digest_matches=(
            captured.field_run.field.snapshot().digest()
            == exact_baseline.field_run.field.snapshot().digest()
        ),
        checkpoint_restored=checkpoint_restored,
    )


def _capture_live_receptor_windows(
    audio_source: SoundDeviceInputSource,
    video_source: OpenCVVideoFrameSource,
    auditory_path: BroadbandHearingPath,
    visual_receptor: LocalChannelGridReceptor,
    *,
    window_seconds: float,
    window_count: int,
    preparation_lead_seconds: float = 0.1,
):
    """Yield reduced common windows while both hardware readers stay active."""

    try:
        duration = float(window_seconds)
    except (TypeError, ValueError) as exc:
        raise FiniteAudioVideoFieldError(
            "live receptor window duration must be finite and positive"
        ) from exc
    if (
        isinstance(window_seconds, bool)
        or not math.isfinite(duration)
        or duration <= 0.0
        or duration > 10.0
    ):
        raise FiniteAudioVideoFieldError(
            "live receptor window duration must be finite and positive"
        )
    width_ticks = round(duration * 1_000_000_000.0)
    lead_ticks = round(preparation_lead_seconds * 1_000_000_000.0)
    if width_ticks <= 0 or lead_ticks <= 0:
        raise FiniteAudioVideoFieldError(
            "live receptor windows require positive durations"
        )
    anchor_tick = time.monotonic_ns() + lead_ticks
    horizon_tick = anchor_tick + window_count * width_ticks
    messages: Queue[tuple[str, str, object]] = Queue()

    def wait_for_anchor() -> None:
        while True:
            remaining = anchor_tick - time.monotonic_ns()
            if remaining <= 0:
                return
            time.sleep(min(remaining / 1_000_000_000.0, 0.001))

    def target_window(end_tick: int) -> int | None:
        if end_tick <= anchor_tick or end_tick > horizon_tick:
            return None
        return min(
            window_count - 1,
            (end_tick - anchor_tick - 1) // width_ticks,
        )

    def capture_auditory() -> None:
        try:
            wait_for_anchor()
            while True:
                samples, start_tick, end_tick = audio_source.read_timed_frame()
                state = auditory_path.push(samples)
                window_index = target_window(end_tick)
                if state is not None and window_index is not None:
                    messages.put(
                        (
                            "frame",
                            "auditory",
                            (
                                window_index,
                                OrganismTimedReceptorFrame(
                                    from_auditory_receptor_state(state),
                                    CommonFieldTime(
                                        "organism.monotonic_ns",
                                        start_tick,
                                        end_tick,
                                    ),
                                ),
                            ),
                        )
                    )
                messages.put(("progress", "auditory", end_tick))
                if end_tick >= horizon_tick:
                    return
        except Exception as exc:
            messages.put(("error", "auditory", exc))

    def capture_visual() -> None:
        frame_index = 0
        try:
            wait_for_anchor()
            while True:
                start_tick = time.monotonic_ns()
                frame = video_source.read_frame()
                state = visual_receptor.analyze(frame, frame_index=frame_index)
                end_tick = time.monotonic_ns()
                window_index = target_window(end_tick)
                if window_index is not None:
                    messages.put(
                        (
                            "frame",
                            "visual",
                            (
                                window_index,
                                OrganismTimedReceptorFrame(
                                    from_visual_receptor_state(state),
                                    CommonFieldTime(
                                        "organism.monotonic_ns",
                                        start_tick,
                                        end_tick,
                                    ),
                                ),
                            ),
                        )
                    )
                messages.put(("progress", "visual", end_tick))
                frame_index += 1
                if end_tick >= horizon_tick:
                    return
        except Exception as exc:
            messages.put(("error", "visual", exc))

    buckets = tuple(
        {"auditory": [], "visual": []}
        for _ in range(window_count)
    )
    progress = {"auditory": anchor_tick, "visual": anchor_tick}
    next_window = 0
    with ThreadPoolExecutor(max_workers=2) as receptor_executor:
        receptor_executor.submit(capture_auditory)
        receptor_executor.submit(capture_visual)
        while next_window < window_count:
            kind, modality_id, payload = messages.get()
            if kind == "error":
                raise FiniteAudioVideoFieldError(
                    f"continuous {modality_id} receptor capture failed"
                ) from payload
            if kind == "frame":
                window_index, timed_frame = payload
                buckets[window_index][modality_id].append(timed_frame)
            elif kind == "progress":
                progress[modality_id] = int(payload)
            while (
                next_window < window_count
                and min(progress.values())
                >= anchor_tick + (next_window + 1) * width_ticks
            ):
                window = buckets[next_window]
                if not window["auditory"] or not window["visual"]:
                    raise FiniteAudioVideoFieldError(
                        "every live field window requires both receptor modalities"
                    )
                yield tuple(
                    ReceptorTimeSequence(
                        modality_id,
                        (
                            auditory_path.geometry_id
                            if modality_id == "auditory"
                            else visual_receptor.config.geometry_id
                        ),
                        "organism.monotonic_ns",
                        tuple(window[modality_id]),
                    )
                    for modality_id in ("auditory", "visual")
                )
                next_window += 1


def _live_visual_receptor(
    requested: VisualGridConfig,
    startup: CameraStartupSummary,
) -> LocalChannelGridReceptor:
    observed = startup.observed_frames_per_second
    available = (
        startup.reported_frames_per_second
        if observed is None
        else min(startup.reported_frames_per_second, observed)
    )
    effective_rate = float(
        max(1, round(min(requested.frames_per_second, available)))
    )
    return LocalChannelGridReceptor(
        replace(requested, frames_per_second=effective_rate)
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

    auditory_path = BroadbandHearingPath(
        LogSpectralReceptor(auditory_config)
    )
    with OpenCVVideoFrameSource(
        device_index=camera_device,
        config=visual_config,
        startup_frame_count=camera_startup_frames,
    ) as video_source:
        startup = video_source.prepare()
        visual_receptor = _live_visual_receptor(visual_config, startup)
        visual_exact = duration * visual_receptor.config.frames_per_second
        visual_frame_count = round(visual_exact)
        if not math.isclose(
            visual_exact,
            visual_frame_count,
            rel_tol=0.0,
            abs_tol=1e-10,
        ):
            raise FiniteAudioVideoFieldError(
                "duration_seconds must contain whole observed visual frames"
            )
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
    auditory_path = BroadbandHearingPath(
        LogSpectralReceptor(auditory_config)
    )
    with OpenCVVideoFrameSource(
        device_index=camera_device,
        config=visual_config,
        startup_frame_count=camera_startup_frames,
    ) as video_source:
        startup = video_source.prepare()
        visual_receptor = _live_visual_receptor(visual_config, startup)
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
    auditory_path = BroadbandHearingPath(LogSpectralReceptor(auditory_config))
    with OpenCVVideoFrameSource(
        device_index=camera_device,
        config=visual_config,
        startup_frame_count=camera_startup_frames,
    ) as video_source:
        startup = video_source.prepare()
        visual_receptor = _live_visual_receptor(visual_config, startup)
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


def capture_live_audio_video_neutral_session(
    *,
    camera_device: int,
    audio_device: int | str,
    field_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig | None = None,
    window_seconds: float = 1.0,
    window_count: int = 3,
    max_windows: int = 10,
    checkpoint_between_windows: bool = True,
    camera_startup_frames: int = 10,
    window_observer: LiveFieldWindowObserver | None = None,
) -> LiveAudioVideoNeutralSessionResult:
    """Keep receptors open while one field continues through bounded windows."""

    if (
        isinstance(window_count, bool)
        or not isinstance(window_count, int)
        or window_count < 1
        or isinstance(max_windows, bool)
        or not isinstance(max_windows, int)
        or max_windows < 1
        or window_count > max_windows
    ):
        raise FiniteAudioVideoFieldError(
            "window_count must stay within the explicit positive maximum"
        )
    try:
        live_window_seconds = float(window_seconds)
    except (TypeError, ValueError) as exc:
        raise FiniteAudioVideoFieldError(
            "window_seconds must be finite and within the bounded live horizon"
        ) from exc
    if (
        isinstance(window_seconds, bool)
        or not math.isfinite(live_window_seconds)
        or live_window_seconds <= 0.0
        or live_window_seconds > 10.0
    ):
        raise FiniteAudioVideoFieldError(
            "window_seconds must be finite and within the bounded live horizon"
        )
    if not isinstance(checkpoint_between_windows, bool):
        raise FiniteAudioVideoFieldError(
            "checkpoint_between_windows must be boolean"
        )
    if window_observer is not None and not callable(window_observer):
        raise FiniteAudioVideoFieldError(
            "window_observer must be callable when provided"
        )

    visual_config = VisualGridConfig()
    auditory_config = LogSpectralConfig()
    auditory_source_config = AuditoryProbeConfig(
        sample_rate=auditory_config.sample_rate,
        frame_size=auditory_config.hop_size,
    )
    auditory_path = BroadbandHearingPath(LogSpectralReceptor(auditory_config))
    current = None
    source_support_count = 0
    checkpoint_count = 0

    with OpenCVVideoFrameSource(
        device_index=camera_device,
        config=visual_config,
        startup_frame_count=camera_startup_frames,
    ) as video_source:
        startup = video_source.prepare()
        visual_receptor = _live_visual_receptor(visual_config, startup)
        with SoundDeviceInputSource(
            device=audio_device,
            config=auditory_source_config,
        ) as audio_source:
            for index, sequences in enumerate(
                _capture_live_receptor_windows(
                    audio_source,
                    video_source,
                    auditory_path,
                    visual_receptor,
                    window_seconds=live_window_seconds,
                    window_count=window_count,
                )
            ):
                checkpoint_after = (
                    checkpoint_between_windows and index + 1 < window_count
                )
                baseline_initial = (
                    None
                    if current is None or window_observer is None
                    else restore_shared_mcm_field(
                        SharedMCMFieldSnapshot.from_json(
                            current.snapshot().to_json()
                        )
                    )
                )
                captured = _advance_captured_audio_video_sequences(
                    sequences,
                    visual_receptor,
                    field_config,
                    afterimage_config=afterimage_config,
                    initial_field=current,
                )
                current = captured.field_run.field
                if checkpoint_after:
                    encoded = current.snapshot().to_json()
                    current = restore_shared_mcm_field(
                        SharedMCMFieldSnapshot.from_json(encoded)
                    )
                    checkpoint_count += 1
                source_support_count += captured.field_run.source_support_count
                if window_observer is not None:
                    exact_baseline = _advance_captured_audio_video_sequences(
                        sequences,
                        visual_receptor,
                        field_config,
                        afterimage_config=afterimage_config,
                        initial_field=baseline_initial,
                    )
                    window_observer(
                        _observe_live_field_window(
                            index,
                            captured,
                            exact_baseline,
                            checkpoint_restored=checkpoint_after,
                        )
                    )
            audio_overflow_count = audio_source.overflow_count
            camera_capture_frame_count = video_source.capture_frames_read

    return LiveAudioVideoNeutralSessionResult(
        startup,
        NeutralFieldSessionResult(
            field=current,
            window_count=window_count,
            source_support_count=source_support_count,
        ),
        camera_capture_frame_count,
        audio_overflow_count,
        checkpoint_count,
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
    auditory_path = BroadbandHearingPath(LogSpectralReceptor(auditory_config))
    with OpenCVVideoFrameSource(
        device_index=camera_device,
        config=visual_config,
        startup_frame_count=camera_startup_frames,
    ) as video_source:
        startup = video_source.prepare()
        visual_receptor = _live_visual_receptor(visual_config, startup)
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
            LiveAudioVideoNeutralSessionResult,
            LiveFieldWindowObservation,
        )
        for item in fields(cls)
    )
