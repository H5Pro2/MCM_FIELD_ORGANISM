"""Cell-wise in-memory adapter for the preregistered S1-Q matrix."""

from __future__ import annotations

from dataclasses import dataclass, fields

from ._synthetic_av_field_fixture import (
    SYNTHETIC_AUDITORY_CARRIER_IDS,
    SYNTHETIC_AV_TICKS_PER_SECOND,
    SYNTHETIC_VISUAL_CONFIG,
    synthetic_av_repeated_sequences,
    synthetic_av_sequences,
)
from .receptor_time_alignment import ReceptorTimeSequence
from .s1j_f3_av_compatibility import S1J_SUPPORT_TICKS
from .s1l_f3_history_function_adapter import S1LFieldState
from .s1o_exposure_retention_matrix import (
    S1OCellSourceContract,
    S1OExposureSourceInvariants,
    _exposure_sequences,
    _model,
    _run_cell_path,
    _source_digest,
    _source_invariants,
)


class S1RPhaseSeparationMatrixError(ValueError):
    """Raised when one S1-R cell leaves the preregistered contract."""


S1R_DOSE_COUNTS = (1, 8)
S1R_SOURCE_FORMS = ("repeated-supports", "continuous-support")
S1R_DELAY_SECONDS = (0.0, 0.025, 0.05, 0.1, 0.2, 0.4, 0.8, 1.6)
S1R_PHASE_BOUNDARY_SECONDS = 0.2
S1R_REFINEMENTS = (2, 4)
S1R_MAIN_MODELS = ("f3", "linear-coupled-field")
S1R_SENTINEL_MODELS = ("eta-null", "p0")
S1R_SENTINEL_DELAYS = (0.0, 0.2, 1.6)

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
class S1RMatrixCellContract:
    cell_id: str
    dose_count: int
    source_form: str
    delay_seconds: float


@dataclass(frozen=True, slots=True)
class S1RCellSourceContract:
    cell: S1RMatrixCellContract
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
class S1RCellMeasurement:
    cell: S1RMatrixCellContract
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
    field_time_claim_allowed: bool = False

    @property
    def preprobe_mass_vector(self) -> tuple[float, ...]:
        return tuple(
            exposed - zero
            for exposed, zero in zip(
                self.exposed_preprobe.mass,
                self.zero_preprobe.mass,
                strict=True,
            )
        )

    @property
    def preprobe_mass_linf(self) -> float:
        return max(
            (abs(value) for value in self.preprobe_mass_vector),
            default=0.0,
        )

    @property
    def probe_effect_vector(self) -> tuple[float, ...]:
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
    def probe_effect_linf(self) -> float:
        return max(
            (abs(value) for value in self.probe_effect_vector),
            default=0.0,
        )


def _delay_id(delay_seconds: float) -> str:
    return format(delay_seconds, ".3f").replace(".", "p")


def _cell_id(dose_count: int, source_form: str, delay_seconds: float) -> str:
    form_id = "repeated" if source_form == "repeated-supports" else "continuous"
    return f"s1r.d{dose_count}.{form_id}.gap-{_delay_id(delay_seconds)}"


def s1r_matrix_inventory() -> tuple[S1RMatrixCellContract, ...]:
    return tuple(
        S1RMatrixCellContract(
            _cell_id(dose_count, source_form, delay_seconds),
            dose_count,
            source_form,
            delay_seconds,
        )
        for dose_count in S1R_DOSE_COUNTS
        for source_form in S1R_SOURCE_FORMS
        for delay_seconds in S1R_DELAY_SECONDS
    )


def _validated_cell(
    dose_count: int,
    source_form: str,
    delay_seconds: float,
) -> S1RMatrixCellContract:
    candidate = S1RMatrixCellContract(
        _cell_id(dose_count, source_form, delay_seconds),
        dose_count,
        source_form,
        delay_seconds,
    )
    if candidate not in s1r_matrix_inventory():
        raise S1RPhaseSeparationMatrixError(
            "S1-R cell is outside the preregistered matrix"
        )
    return candidate


def _delay_sequences(
    phase_id: str,
    start_tick: int,
    delay_ticks: int,
):
    if delay_ticks == 0:
        return None
    end_tick = start_tick + delay_ticks
    if delay_ticks < S1J_SUPPORT_TICKS:
        return synthetic_av_sequences(
            phase_id,
            start_tick,
            end_tick,
            _AUDITORY_ZERO,
            _VISUAL_ZERO,
        )
    return synthetic_av_repeated_sequences(
        phase_id,
        start_tick,
        end_tick,
        S1J_SUPPORT_TICKS,
        _AUDITORY_ZERO,
        _VISUAL_ZERO,
    )


def build_s1r_cell_source_contract(
    dose_count: int,
    source_form: str,
    delay_seconds: float,
) -> S1RCellSourceContract:
    """Build one fixed S1-Q source contract without starting a field path."""

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
    delay = _delay_sequences(
        f"{cell.cell_id}.delay",
        exposure_end,
        delay_ticks,
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
    return S1RCellSourceContract(
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


def run_s1r_matrix_cell(
    model_id: str,
    dose_count: int,
    source_form: str,
    delay_seconds: float,
    refinement: int,
    *,
    m_neutralized: bool = False,
) -> S1RCellMeasurement:
    """Run one S1-Q cell in memory without classifying the matrix."""

    if refinement not in S1R_REFINEMENTS:
        raise S1RPhaseSeparationMatrixError(
            "S1-R refinement must be 2 or 4"
        )
    if model_id == "linear-coupled-field" and refinement != 4:
        raise S1RPhaseSeparationMatrixError(
            "S1-R linear baseline is bound to refinement 4"
        )
    if model_id in S1R_SENTINEL_MODELS and refinement != 4:
        raise S1RPhaseSeparationMatrixError(
            "S1-R sentinel controls are bound to refinement 4"
        )
    if m_neutralized and model_id != "f3":
        raise S1RPhaseSeparationMatrixError(
            "S1-R M neutralization is bound only to F3"
        )
    if model_id not in S1R_MAIN_MODELS + S1R_SENTINEL_MODELS:
        raise S1RPhaseSeparationMatrixError("unknown S1-R model arm")

    source = build_s1r_cell_source_contract(
        dose_count,
        source_form,
        delay_seconds,
    )
    arm, calculator = _model(model_id)
    compatible_source = S1OCellSourceContract(
        cell=source.cell,
        exposure=source.exposure,
        exposure_zero=source.exposure_zero,
        delay=source.delay,
        probe_contact=source.probe_contact,
        probe_null=source.probe_null,
        exposure_digest=source.exposure_digest,
        exposure_zero_digest=source.exposure_zero_digest,
        exposure_invariants=source.exposure_invariants,
        zero_invariants=source.zero_invariants,
    )
    exposed = _run_cell_path(
        compatible_source,
        source.exposure,
        arm,
        calculator,
        refinement,
        neutralized=m_neutralized,
    )
    zero = _run_cell_path(
        compatible_source,
        source.exposure_zero,
        arm,
        calculator,
        refinement,
        neutralized=m_neutralized,
    )
    return S1RCellMeasurement(
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


def s1r_phase_separation_matrix_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            S1RMatrixCellContract,
            S1RCellSourceContract,
            S1RCellMeasurement,
        )
        for item in fields(cls)
    )
