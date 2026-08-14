"""Paired local-contrast characterization under synthetic AV backgrounds."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math

from ._synthetic_av_field_fixture import (
    SYNTHETIC_AUDITORY_CARRIER_IDS,
    SYNTHETIC_VISUAL_CONFIG,
    run_synthetic_av_load_recovery,
)
from .field_load_recovery_characterization import FIELD_LOAD_BASELINE_IDS
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
)
from .shared_mcm_field import SharedMCMFieldSnapshot


FIELD_BACKGROUND_CONTRAST_MODALITY_IDS = ("auditory", "visual")
FIELD_BACKGROUND_LEVELS = (0.0, 0.5, 0.9)
FIELD_BACKGROUND_CONTRAST_DELTA = 0.1
FIELD_BACKGROUND_LOAD_DURATIONS_SECONDS = (0.1, 1.0, 4.0)
_SUPPORT_SECONDS = 0.1
_CONTRAST_INDEX = 4
_TOLERANCE = 1e-12


class FieldBackgroundContrastCharacterizationError(ValueError):
    """Raised when the fixed paired contrast matrix is inconsistent."""


def _finite_nonnegative(value: object, role: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise FieldBackgroundContrastCharacterizationError(
            f"{role} must be finite and non-negative"
        )
    return result


@dataclass(frozen=True, slots=True)
class FieldBackgroundContrastObservation:
    baseline_id: str
    contrast_modality_id: str
    background_level: float
    contrast_delta: float
    applied_background_level: float
    applied_contrast_level: float
    applied_contrast_delta: float
    load_duration_seconds: float
    field_neuron_count: int
    paired_source_event_count: int
    background_field_linf: float
    contrast_field_linf: float
    contrast_delta_l1: float
    contrast_delta_linf: float
    local_contrast_delta_abs: float
    cross_modal_delta_linf: float
    afterimage_delta_linf: float
    original_contrast_transfer_linf: float
    writes_back: bool = False
    adaptive_regulation_applied: bool = False

    def __post_init__(self) -> None:
        if self.baseline_id not in FIELD_LOAD_BASELINE_IDS:
            raise FieldBackgroundContrastCharacterizationError("unknown baseline")
        if self.contrast_modality_id not in FIELD_BACKGROUND_CONTRAST_MODALITY_IDS:
            raise FieldBackgroundContrastCharacterizationError("unknown modality")
        if self.background_level not in FIELD_BACKGROUND_LEVELS:
            raise FieldBackgroundContrastCharacterizationError(
                "unknown background level"
            )
        if self.load_duration_seconds not in FIELD_BACKGROUND_LOAD_DURATIONS_SECONDS:
            raise FieldBackgroundContrastCharacterizationError(
                "unknown load duration"
            )
        for role in (
            "contrast_delta",
            "applied_background_level",
            "applied_contrast_level",
            "applied_contrast_delta",
            "background_field_linf",
            "contrast_field_linf",
            "contrast_delta_l1",
            "contrast_delta_linf",
            "local_contrast_delta_abs",
            "cross_modal_delta_linf",
            "afterimage_delta_linf",
            "original_contrast_transfer_linf",
        ):
            object.__setattr__(self, role, _finite_nonnegative(getattr(self, role), role))
        expected_background, expected_contrast = _applied_levels(
            self.baseline_id,
            self.background_level,
        )
        if (
            self.contrast_delta != FIELD_BACKGROUND_CONTRAST_DELTA
            or self.applied_background_level != expected_background
            or self.applied_contrast_level != expected_contrast
            or self.applied_contrast_delta != expected_contrast - expected_background
        ):
            raise FieldBackgroundContrastCharacterizationError(
                "fixed contrast input differs from baseline definition"
            )
        expected_events = 4 * round(
            self.load_duration_seconds / _SUPPORT_SECONDS
        )
        if self.field_neuron_count != 26:
            raise FieldBackgroundContrastCharacterizationError(
                "shared AV field neuron inventory changed"
            )
        if self.paired_source_event_count != expected_events:
            raise FieldBackgroundContrastCharacterizationError(
                "paired source event inventory is inconsistent"
            )
        if not math.isclose(
            self.local_contrast_delta_abs,
            self.contrast_delta_linf,
            rel_tol=0.0,
            abs_tol=_TOLERANCE,
        ):
            raise FieldBackgroundContrastCharacterizationError(
                "local contrast does not account for paired Linf difference"
            )
        expected_transfer = self.contrast_delta_linf / self.contrast_delta
        if not math.isclose(
            self.original_contrast_transfer_linf,
            expected_transfer,
            rel_tol=0.0,
            abs_tol=1e-15,
        ):
            raise FieldBackgroundContrastCharacterizationError(
                "contrast transfer is inconsistent"
            )
        if self.writes_back or self.adaptive_regulation_applied:
            raise FieldBackgroundContrastCharacterizationError(
                "passive characterization cannot regulate the field"
            )


@dataclass(frozen=True, slots=True)
class FieldBackgroundContrastCharacterization:
    observations: tuple[FieldBackgroundContrastObservation, ...]
    baseline_ids: tuple[str, ...]
    modality_ids: tuple[str, ...]
    background_levels: tuple[float, ...]
    contrast_delta: float
    unmodified_max_background_delta_error: float
    fixed_gain_max_background_delta_error: float
    fixed_leaky_max_background_delta_error: float
    unmodified_contrast_retained: bool
    static_clipping_high_background_contrast_lost: bool
    characterization_decision: str
    writes_back: bool = False
    adaptive_regulation_applied: bool = False

    def __post_init__(self) -> None:
        observations = tuple(self.observations)
        expected_keys = {
            (baseline, modality, background, duration)
            for baseline in FIELD_LOAD_BASELINE_IDS
            for modality in FIELD_BACKGROUND_CONTRAST_MODALITY_IDS
            for background in FIELD_BACKGROUND_LEVELS
            for duration in FIELD_BACKGROUND_LOAD_DURATIONS_SECONDS
        }
        actual_keys = {
            (
                item.baseline_id,
                item.contrast_modality_id,
                item.background_level,
                item.load_duration_seconds,
            )
            for item in observations
        }
        if len(observations) != len(expected_keys) or actual_keys != expected_keys:
            raise FieldBackgroundContrastCharacterizationError(
                "paired contrast matrix is incomplete"
            )
        canonical = tuple(
            sorted(
                observations,
                key=lambda item: (
                    item.baseline_id,
                    item.contrast_modality_id,
                    item.background_level,
                    item.load_duration_seconds,
                ),
            )
        )
        if observations != canonical:
            raise FieldBackgroundContrastCharacterizationError(
                "observations must use canonical order"
            )
        if (
            tuple(self.baseline_ids) != FIELD_LOAD_BASELINE_IDS
            or tuple(self.modality_ids) != FIELD_BACKGROUND_CONTRAST_MODALITY_IDS
            or tuple(self.background_levels) != FIELD_BACKGROUND_LEVELS
            or self.contrast_delta != FIELD_BACKGROUND_CONTRAST_DELTA
        ):
            raise FieldBackgroundContrastCharacterizationError(
                "characterization inventory changed"
            )
        errors = {
            baseline: _max_background_delta_error(observations, baseline)
            for baseline in (
                "unmodified",
                "fixed_gain_0_5",
                "fixed_leaky_1_0",
            )
        }
        if (
            self.unmodified_max_background_delta_error != errors["unmodified"]
            or self.fixed_gain_max_background_delta_error
            != errors["fixed_gain_0_5"]
            or self.fixed_leaky_max_background_delta_error
            != errors["fixed_leaky_1_0"]
        ):
            raise FieldBackgroundContrastCharacterizationError(
                "background invariance summary is inconsistent"
            )
        unmodified_retained = (
            errors["unmodified"] <= _TOLERANCE
            and all(
                item.contrast_delta_linf > _TOLERANCE
                for item in observations
                if item.baseline_id == "unmodified"
            )
        )
        clipping_lost = all(
            item.contrast_delta_linf <= _TOLERANCE
            for item in observations
            if item.baseline_id == "static_clip_0_5"
            and item.background_level >= 0.5
        )
        if (
            self.unmodified_contrast_retained != unmodified_retained
            or self.static_clipping_high_background_contrast_lost != clipping_lost
        ):
            raise FieldBackgroundContrastCharacterizationError(
                "contrast decision summary is inconsistent"
            )
        expected_decision = (
            "UNMODIFIED_FIELD_CONTRAST_RETAINED_ACROSS_BOUND_BACKGROUNDS"
            if unmodified_retained
            else "UNMODIFIED_FIELD_CONTRAST_LOSS_OBSERVED"
        )
        if self.characterization_decision != expected_decision:
            raise FieldBackgroundContrastCharacterizationError(
                "characterization decision is inconsistent"
            )
        if self.writes_back or self.adaptive_regulation_applied:
            raise FieldBackgroundContrastCharacterizationError(
                "characterization cannot release regulation"
            )
        object.__setattr__(self, "observations", observations)

    @property
    def observation_count(self) -> int:
        return len(self.observations)


def _applied_levels(baseline_id: str, background: float) -> tuple[float, float]:
    contrast = background + FIELD_BACKGROUND_CONTRAST_DELTA
    if baseline_id == "fixed_gain_0_5":
        return background * 0.5, contrast * 0.5
    if baseline_id == "static_clip_0_5":
        return min(background, 0.5), min(contrast, 0.5)
    return background, contrast


def _input_values(
    modality_id: str,
    background: float,
    contrast: float,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    auditory = [background] * len(SYNTHETIC_AUDITORY_CARRIER_IDS)
    visual = [background] * len(SYNTHETIC_VISUAL_CONFIG.carrier_ids)
    target = auditory if modality_id == "auditory" else visual
    target[_CONTRAST_INDEX] = contrast
    return tuple(auditory), tuple(visual)


def _delta_values(
    background: SharedMCMFieldSnapshot,
    contrast: SharedMCMFieldSnapshot,
    role: str,
) -> tuple[float, ...]:
    if background.neuron_ids != contrast.neuron_ids:
        raise FieldBackgroundContrastCharacterizationError(
            "paired field neuron identities differ"
        )
    return tuple(
        right - left
        for left, right in zip(
            getattr(background, role),
            getattr(contrast, role),
            strict=True,
        )
    )


def _run_observation(
    baseline_id: str,
    modality_id: str,
    background: float,
    duration: float,
) -> FieldBackgroundContrastObservation:
    applied_background, applied_contrast = _applied_levels(baseline_id, background)
    background_values = _input_values(
        modality_id,
        applied_background,
        applied_background,
    )
    contrast_values = _input_values(
        modality_id,
        applied_background,
        applied_contrast,
    )
    afterimage = None
    dissipation = None
    if baseline_id == "fixed_leaky_1_0":
        afterimage = NeutralFastAfterimageConfig(1.0)
        dissipation = NeutralFieldDissipationConfig(1.0)
    background_snapshot, _, background_events = run_synthetic_av_load_recovery(
        "background",
        *background_values,
        duration,
        0.0,
        support_seconds=_SUPPORT_SECONDS,
        afterimage_config=afterimage,
        dissipation_config=dissipation,
    )
    contrast_snapshot, _, contrast_events = run_synthetic_av_load_recovery(
        "contrast",
        *contrast_values,
        duration,
        0.0,
        support_seconds=_SUPPORT_SECONDS,
        afterimage_config=afterimage,
        dissipation_config=dissipation,
    )
    activation_delta = _delta_values(
        background_snapshot,
        contrast_snapshot,
        "activation",
    )
    afterimage_delta = _delta_values(
        background_snapshot,
        contrast_snapshot,
        "afterimage",
    )
    target_id = f"organism.mcm_field.{modality_id}.n{_CONTRAST_INDEX}"
    target_index = background_snapshot.neuron_ids.index(target_id)
    cross_marker = ".visual." if modality_id == "auditory" else ".auditory."
    cross_delta = tuple(
        value
        for neuron_id, value in zip(
            background_snapshot.neuron_ids,
            activation_delta,
            strict=True,
        )
        if cross_marker in neuron_id
    )
    delta_linf = max(abs(value) for value in activation_delta)
    return FieldBackgroundContrastObservation(
        baseline_id=baseline_id,
        contrast_modality_id=modality_id,
        background_level=background,
        contrast_delta=FIELD_BACKGROUND_CONTRAST_DELTA,
        applied_background_level=applied_background,
        applied_contrast_level=applied_contrast,
        applied_contrast_delta=applied_contrast - applied_background,
        load_duration_seconds=duration,
        field_neuron_count=len(background_snapshot.neuron_ids),
        paired_source_event_count=background_events + contrast_events,
        background_field_linf=max(abs(value) for value in background_snapshot.activation),
        contrast_field_linf=max(abs(value) for value in contrast_snapshot.activation),
        contrast_delta_l1=math.fsum(abs(value) for value in activation_delta),
        contrast_delta_linf=delta_linf,
        local_contrast_delta_abs=abs(activation_delta[target_index]),
        cross_modal_delta_linf=max((abs(value) for value in cross_delta), default=0.0),
        afterimage_delta_linf=max(abs(value) for value in afterimage_delta),
        original_contrast_transfer_linf=delta_linf / FIELD_BACKGROUND_CONTRAST_DELTA,
    )


def _max_background_delta_error(
    observations: tuple[FieldBackgroundContrastObservation, ...],
    baseline_id: str,
) -> float:
    errors = []
    for modality in FIELD_BACKGROUND_CONTRAST_MODALITY_IDS:
        for duration in FIELD_BACKGROUND_LOAD_DURATIONS_SECONDS:
            group = tuple(
                item
                for item in observations
                if item.baseline_id == baseline_id
                and item.contrast_modality_id == modality
                and item.load_duration_seconds == duration
            )
            reference = next(
                item.contrast_delta_linf
                for item in group
                if item.background_level == 0.0
            )
            errors.extend(abs(item.contrast_delta_linf - reference) for item in group)
    return max(errors, default=0.0)


def run_field_background_contrast_characterization(
) -> FieldBackgroundContrastCharacterization:
    """Run the fixed paired matrix without adaptive sensitivity changes."""

    observations = tuple(
        _run_observation(baseline, modality, background, duration)
        for baseline in FIELD_LOAD_BASELINE_IDS
        for modality in FIELD_BACKGROUND_CONTRAST_MODALITY_IDS
        for background in FIELD_BACKGROUND_LEVELS
        for duration in FIELD_BACKGROUND_LOAD_DURATIONS_SECONDS
    )
    errors = {
        baseline: _max_background_delta_error(observations, baseline)
        for baseline in ("unmodified", "fixed_gain_0_5", "fixed_leaky_1_0")
    }
    unmodified_retained = (
        errors["unmodified"] <= _TOLERANCE
        and all(
            item.contrast_delta_linf > _TOLERANCE
            for item in observations
            if item.baseline_id == "unmodified"
        )
    )
    clipping_lost = all(
        item.contrast_delta_linf <= _TOLERANCE
        for item in observations
        if item.baseline_id == "static_clip_0_5" and item.background_level >= 0.5
    )
    return FieldBackgroundContrastCharacterization(
        observations=observations,
        baseline_ids=FIELD_LOAD_BASELINE_IDS,
        modality_ids=FIELD_BACKGROUND_CONTRAST_MODALITY_IDS,
        background_levels=FIELD_BACKGROUND_LEVELS,
        contrast_delta=FIELD_BACKGROUND_CONTRAST_DELTA,
        unmodified_max_background_delta_error=errors["unmodified"],
        fixed_gain_max_background_delta_error=errors["fixed_gain_0_5"],
        fixed_leaky_max_background_delta_error=errors["fixed_leaky_1_0"],
        unmodified_contrast_retained=unmodified_retained,
        static_clipping_high_background_contrast_lost=clipping_lost,
        characterization_decision=(
            "UNMODIFIED_FIELD_CONTRAST_RETAINED_ACROSS_BOUND_BACKGROUNDS"
            if unmodified_retained
            else "UNMODIFIED_FIELD_CONTRAST_LOSS_OBSERVED"
        ),
    )


def field_background_contrast_characterization_json_value(
    result: FieldBackgroundContrastCharacterization,
) -> dict[str, object]:
    if not isinstance(result, FieldBackgroundContrastCharacterization):
        raise FieldBackgroundContrastCharacterizationError(
            "JSON projection requires a paired contrast result"
        )
    return asdict(result)


def field_background_contrast_characterization_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            FieldBackgroundContrastObservation,
            FieldBackgroundContrastCharacterization,
        )
        for item in fields(contract)
    )
