"""Cell-wise in-memory adapter for the preregistered S1-N matrix."""

from __future__ import annotations

from dataclasses import dataclass, fields
from decimal import Decimal
import hashlib
import json

from ._synthetic_av_field_fixture import (
    SYNTHETIC_AUDITORY_CARRIER_IDS,
    SYNTHETIC_AV_TICKS_PER_SECOND,
    SYNTHETIC_VISUAL_CONFIG,
    build_synthetic_av_field,
    synthetic_av_repeated_sequences,
    synthetic_av_sequences,
)
from .mcm_f3_baseline_coupling import (
    compute_mcm_f3_linear_coupled_baseline,
)
from .mcm_f3_coupling import compute_mcm_f3_coupling
from .mcm_f3_history_run import (
    align_mcm_f3_fast_state,
    neutralize_mcm_f3_mass,
)
from .mcm_f3_runtime import activate_mcm_f3_field
from .receptor_time_alignment import ReceptorTimeSequence
from .s1j_f3_av_compatibility import (
    S1J_ACTIVE_ARM,
    S1J_ETA_NULL_ARM,
    S1J_P0_ARM,
    S1J_SUPPORT_TICKS,
    advance_s1j_f3_av_sequences,
)
from .s1l_f3_history_function_adapter import S1LFieldState
from .shared_mcm_field import attach_uniform_mcm_substrate


class S1OExposureRetentionMatrixError(ValueError):
    """Raised when one S1-O matrix cell leaves the preregistered inventory."""


S1O_DOSE_COUNTS = (1, 2, 4, 8)
S1O_SOURCE_FORMS = ("repeated-supports", "continuous-support")
S1O_DELAY_SECONDS = (0.0, 0.2, 0.8, 1.6)
S1O_REFINEMENTS = (2, 4)
S1O_MAIN_MODELS = ("f3", "linear-coupled-field")
S1O_SENTINEL_MODELS = ("eta-null", "p0")

_AUDITORY_ZERO = tuple(0.0 for _ in SYNTHETIC_AUDITORY_CARRIER_IDS)
_VISUAL_ZERO = tuple(0.0 for _ in SYNTHETIC_VISUAL_CONFIG.carrier_ids)
_AUDITORY_EXPOSURE = tuple(
    0.8 if index == 0 else 0.0
    for index in range(len(SYNTHETIC_AUDITORY_CARRIER_IDS))
)
_VISUAL_EXPOSURE = tuple(
    0.6 if index == 5 else 0.0
    for index in range(len(SYNTHETIC_VISUAL_CONFIG.carrier_ids))
)
_AUDITORY_PROBE = tuple(
    0.4 if index == 3 else 0.0
    for index in range(len(SYNTHETIC_AUDITORY_CARRIER_IDS))
)
_VISUAL_PROBE = tuple(
    0.4 if index == 8 else 0.0
    for index in range(len(SYNTHETIC_VISUAL_CONFIG.carrier_ids))
)


@dataclass(frozen=True, slots=True)
class S1OMatrixCellContract:
    cell_id: str
    dose_count: int
    source_form: str
    delay_seconds: float


@dataclass(frozen=True, slots=True)
class S1OExposureSourceInvariants:
    support_count_per_modality: int
    event_count: int
    duration_seconds: float
    integrated_l1: float
    integrated_l2: float


@dataclass(frozen=True, slots=True)
class S1OCellSourceContract:
    cell: S1OMatrixCellContract
    exposure: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    exposure_zero: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    delay: tuple[ReceptorTimeSequence, ReceptorTimeSequence] | None
    probe_contact: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    probe_null: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    exposure_digest: str
    exposure_zero_digest: str
    exposure_invariants: S1OExposureSourceInvariants
    zero_invariants: S1OExposureSourceInvariants


@dataclass(frozen=True, slots=True)
class S1OCellMeasurement:
    cell: S1OMatrixCellContract
    model_id: str
    refinement: int
    exposed_preprobe: S1LFieldState
    zero_preprobe: S1LFieldState
    exposed_probe: tuple[S1LFieldState, S1LFieldState]
    zero_probe: tuple[S1LFieldState, S1LFieldState]
    exposed_event_count: int
    zero_event_count: int
    m_neutralized: bool
    raw_payload_retained: bool = False
    classification_allowed: bool = False
    runtime_writeback_allowed: bool = False
    memory_claim_allowed: bool = False
    learning_claim_allowed: bool = False

    @property
    def effect_vector(self) -> tuple[float, ...]:
        values = []
        for exposed, zero in zip(
            self.exposed_probe,
            self.zero_probe,
            strict=True,
        ):
            values.extend(
                left - right
                for left, right in zip(
                    exposed.activation,
                    zero.activation,
                    strict=True,
                )
            )
            values.extend(
                left - right
                for left, right in zip(
                    exposed.afterimage,
                    zero.afterimage,
                    strict=True,
                )
            )
        return tuple(values)

    @property
    def effect_linf(self) -> float:
        return max((abs(value) for value in self.effect_vector), default=0.0)

    @property
    def preprobe_mass_linf(self) -> float:
        return _difference_linf(
            self.exposed_preprobe.mass,
            self.zero_preprobe.mass,
        )


def _cell_id(dose_count: int, source_form: str, delay_seconds: float) -> str:
    delay_id = str(delay_seconds).replace(".", "p")
    form_id = "repeated" if source_form == "repeated-supports" else "continuous"
    return f"s1o.d{dose_count}.{form_id}.gap-{delay_id}"


def s1o_matrix_inventory() -> tuple[S1OMatrixCellContract, ...]:
    return tuple(
        S1OMatrixCellContract(
            _cell_id(dose_count, source_form, delay_seconds),
            dose_count,
            source_form,
            delay_seconds,
        )
        for dose_count in S1O_DOSE_COUNTS
        for source_form in S1O_SOURCE_FORMS
        for delay_seconds in S1O_DELAY_SECONDS
    )


def _validated_cell(
    dose_count: int,
    source_form: str,
    delay_seconds: float,
) -> S1OMatrixCellContract:
    candidate = S1OMatrixCellContract(
        _cell_id(dose_count, source_form, delay_seconds),
        dose_count,
        source_form,
        delay_seconds,
    )
    if candidate not in s1o_matrix_inventory():
        raise S1OExposureRetentionMatrixError(
            "S1-O cell is outside the preregistered matrix"
        )
    return candidate


def _source_digest(
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
) -> str:
    payload = [
        {
            "modality_id": sequence.modality_id,
            "geometry_id": sequence.geometry_id,
            "frames": [
                {
                    "snapshot_id": item.frame.snapshot_id,
                    "start_tick": item.field_time.window_start_tick,
                    "end_tick": item.field_time.window_end_tick,
                    "values": item.frame.values,
                }
                for item in sequence.frames
            ],
        }
        for sequence in sequences
    ]
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _source_invariants(
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
) -> S1OExposureSourceInvariants:
    integrated_l1_ticks = Decimal(0)
    integrated_l2_squared_ticks = Decimal(0)
    for sequence in sequences:
        for item in sequence.frames:
            duration_ticks = Decimal(
                item.field_time.window_end_tick
                - item.field_time.window_start_tick
            )
            decimal_values = tuple(Decimal(str(value)) for value in item.frame.values)
            integrated_l1_ticks += duration_ticks * sum(
                (abs(value) for value in decimal_values),
                Decimal(0),
            )
            integrated_l2_squared_ticks += duration_ticks * sum(
                (value * value for value in decimal_values),
                Decimal(0),
            )
    first_start = min(
        sequence.frames[0].field_time.window_start_tick
        for sequence in sequences
    )
    last_end = max(
        sequence.frames[-1].field_time.window_end_tick
        for sequence in sequences
    )
    ticks_per_second = Decimal(str(SYNTHETIC_AV_TICKS_PER_SECOND))
    integrated_l1 = integrated_l1_ticks / ticks_per_second
    integrated_l2_squared = integrated_l2_squared_ticks / ticks_per_second
    return S1OExposureSourceInvariants(
        support_count_per_modality=len(sequences[0].frames),
        event_count=sum(len(sequence.frames) for sequence in sequences),
        duration_seconds=(last_end - first_start) / SYNTHETIC_AV_TICKS_PER_SECOND,
        integrated_l1=float(integrated_l1),
        integrated_l2=float(integrated_l2_squared.sqrt()),
    )


def _exposure_sequences(
    phase_id: str,
    dose_count: int,
    source_form: str,
    auditory_values: tuple[float, ...],
    visual_values: tuple[float, ...],
):
    end_tick = dose_count * S1J_SUPPORT_TICKS
    if source_form == "repeated-supports":
        return synthetic_av_repeated_sequences(
            phase_id,
            0,
            end_tick,
            S1J_SUPPORT_TICKS,
            auditory_values,
            visual_values,
        )
    return synthetic_av_sequences(
        phase_id,
        0,
        end_tick,
        auditory_values,
        visual_values,
    )


def build_s1o_cell_source_contract(
    dose_count: int,
    source_form: str,
    delay_seconds: float,
) -> S1OCellSourceContract:
    """Build one fixed cell source without starting a field path."""

    cell = _validated_cell(dose_count, source_form, delay_seconds)
    exposure_end = dose_count * S1J_SUPPORT_TICKS
    delay_ticks = round(delay_seconds * SYNTHETIC_AV_TICKS_PER_SECOND)
    probe_start = exposure_end + delay_ticks
    exposure = _exposure_sequences(
        f"{cell.cell_id}.exposed",
        dose_count,
        source_form,
        _AUDITORY_EXPOSURE,
        _VISUAL_EXPOSURE,
    )
    exposure_zero = _exposure_sequences(
        f"{cell.cell_id}.zero",
        dose_count,
        source_form,
        _AUDITORY_ZERO,
        _VISUAL_ZERO,
    )
    delay = None
    if delay_ticks:
        delay = synthetic_av_repeated_sequences(
            f"{cell.cell_id}.delay",
            exposure_end,
            probe_start,
            S1J_SUPPORT_TICKS,
            _AUDITORY_ZERO,
            _VISUAL_ZERO,
        )
    probe_contact = synthetic_av_sequences(
        f"{cell.cell_id}.probe-contact",
        probe_start,
        probe_start + S1J_SUPPORT_TICKS,
        _AUDITORY_PROBE,
        _VISUAL_PROBE,
    )
    probe_null = synthetic_av_sequences(
        f"{cell.cell_id}.probe-null",
        probe_start + S1J_SUPPORT_TICKS,
        probe_start + 2 * S1J_SUPPORT_TICKS,
        _AUDITORY_ZERO,
        _VISUAL_ZERO,
    )
    return S1OCellSourceContract(
        cell=cell,
        exposure=exposure,
        exposure_zero=exposure_zero,
        delay=delay,
        probe_contact=probe_contact,
        probe_null=probe_null,
        exposure_digest=_source_digest(exposure),
        exposure_zero_digest=_source_digest(exposure_zero),
        exposure_invariants=_source_invariants(exposure),
        zero_invariants=_source_invariants(exposure_zero),
    )


def _model(model_id: str):
    if model_id == "f3":
        return S1J_ACTIVE_ARM, compute_mcm_f3_coupling
    if model_id == "linear-coupled-field":
        return S1J_ACTIVE_ARM, compute_mcm_f3_linear_coupled_baseline
    if model_id == "eta-null":
        return S1J_ETA_NULL_ARM, compute_mcm_f3_coupling
    if model_id == "p0":
        return S1J_P0_ARM, compute_mcm_f3_coupling
    raise S1OExposureRetentionMatrixError("unknown S1-O model arm")


def _initial_field(sequences, arm):
    base = build_synthetic_av_field(sequences)
    return (
        attach_uniform_mcm_substrate(base, arm)
        if arm.is_null_arm
        else activate_mcm_f3_field(base, arm)
    )


def _advance(field, sequences, calculator, refinement):
    return advance_s1j_f3_av_sequences(
        field,
        sequences,
        coupling_calculator=calculator,
        refinement=refinement,
    )


def _state(field) -> S1LFieldState:
    snapshot = field.snapshot()
    return S1LFieldState(
        snapshot.activation,
        snapshot.afterimage,
        snapshot.substrate_mass,
    )


def _run_cell_path(
    source: S1OCellSourceContract,
    exposure,
    arm,
    calculator,
    refinement: int,
    *,
    neutralized: bool,
):
    field = _initial_field(exposure, arm)
    event_count = 0
    advanced = _advance(field, exposure, calculator, refinement)
    field = advanced.field
    event_count += advanced.source_event_count
    if source.delay is not None:
        advanced = _advance(field, source.delay, calculator, refinement)
        field = advanced.field
        event_count += advanced.source_event_count
    field = align_mcm_f3_fast_state(field)
    if neutralized:
        field = neutralize_mcm_f3_mass(field)
    preprobe = _state(field)
    probe_states = []
    for sequences in (source.probe_contact, source.probe_null):
        advanced = _advance(field, sequences, calculator, refinement)
        field = advanced.field
        event_count += advanced.source_event_count
        probe_states.append(_state(field))
    return preprobe, tuple(probe_states), event_count


def run_s1o_matrix_cell(
    model_id: str,
    dose_count: int,
    source_form: str,
    delay_seconds: float,
    refinement: int,
    *,
    m_neutralized: bool = False,
) -> S1OCellMeasurement:
    """Run one preregistered cell in memory without classifying the matrix."""

    if refinement not in S1O_REFINEMENTS:
        raise S1OExposureRetentionMatrixError(
            "S1-O refinement must be 2 or 4"
        )
    if model_id == "linear-coupled-field" and refinement != 4:
        raise S1OExposureRetentionMatrixError(
            "S1-O linear baseline is bound to refinement 4"
        )
    if model_id in S1O_SENTINEL_MODELS and refinement != 4:
        raise S1OExposureRetentionMatrixError(
            "S1-O sentinel controls are bound to refinement 4"
        )
    if m_neutralized and model_id != "f3":
        raise S1OExposureRetentionMatrixError(
            "S1-O M neutralization is bound only to F3"
        )
    source = build_s1o_cell_source_contract(
        dose_count,
        source_form,
        delay_seconds,
    )
    arm, calculator = _model(model_id)
    exposed = _run_cell_path(
        source,
        source.exposure,
        arm,
        calculator,
        refinement,
        neutralized=m_neutralized,
    )
    zero = _run_cell_path(
        source,
        source.exposure_zero,
        arm,
        calculator,
        refinement,
        neutralized=m_neutralized,
    )
    return S1OCellMeasurement(
        cell=source.cell,
        model_id=model_id,
        refinement=refinement,
        exposed_preprobe=exposed[0],
        zero_preprobe=zero[0],
        exposed_probe=exposed[1],
        zero_probe=zero[1],
        exposed_event_count=exposed[2],
        zero_event_count=zero[2],
        m_neutralized=m_neutralized,
    )


def _difference_linf(
    first: tuple[float, ...],
    second: tuple[float, ...],
) -> float:
    return max(
        (
            abs(left - right)
            for left, right in zip(first, second, strict=True)
        ),
        default=0.0,
    )


def s1o_exposure_retention_matrix_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            S1OMatrixCellContract,
            S1OExposureSourceInvariants,
            S1OCellSourceContract,
            S1OCellMeasurement,
        )
        for item in fields(cls)
    )
