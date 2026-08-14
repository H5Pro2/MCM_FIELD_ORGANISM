"""In-memory adapter for the preregistered S1-K technical comparison."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math

from ._synthetic_av_field_fixture import (
    SYNTHETIC_AUDITORY_CARRIER_IDS,
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
from .shared_mcm_field import (
    SharedMCMField,
    attach_uniform_mcm_substrate,
)


class S1LF3HistoryFunctionError(ValueError):
    """Raised when the in-memory S1-L adapter leaves its fixed contract."""


S1L_REFINEMENTS = (1, 2, 4)
S1L_ABSOLUTE_FLOOR = 1e-12
S1L_LINEAR_EQUIVALENCE_LIMIT = 0.05
S1L_MASS_TOLERANCE = 1e-12
S1L_HISTORY_SUPPORT_COUNT = 4
S1L_SETTLE_SUPPORT_COUNT = 2

_AUDITORY_ZERO = tuple(0.0 for _ in SYNTHETIC_AUDITORY_CARRIER_IDS)
_VISUAL_ZERO = tuple(0.0 for _ in SYNTHETIC_VISUAL_CONFIG.carrier_ids)


@dataclass(frozen=True, slots=True)
class S1LSourceInvariants:
    support_count: int
    event_count: int
    value_multiset: tuple[float, ...]
    l1_amplitude: float
    l2_amplitude: float


@dataclass(frozen=True, slots=True)
class S1LSourceContract:
    history_a: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    history_b: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    settle: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    probe_contact: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    probe_null: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    history_a_digest: str
    history_b_digest: str
    probe_digest: str
    history_a_invariants: S1LSourceInvariants
    history_b_invariants: S1LSourceInvariants


@dataclass(frozen=True, slots=True)
class S1LFieldState:
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    mass: tuple[float, ...]

    def digest(self) -> str:
        payload = json.dumps(
            {
                "activation": self.activation,
                "afterimage": self.afterimage,
                "mass": self.mass,
            },
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class S1LModelPairMeasurement:
    model_id: str
    refinement: int
    preprobe_a: S1LFieldState
    preprobe_b: S1LFieldState
    probe_a: tuple[S1LFieldState, S1LFieldState]
    probe_b: tuple[S1LFieldState, S1LFieldState]
    source_event_count_per_path: int
    neutralized: bool
    raw_payload_retained: bool = False
    decision_allowed: bool = False
    memory_claim_allowed: bool = False
    learning_claim_allowed: bool = False

    @property
    def preprobe_mass_linf(self) -> float:
        return _linf(self.preprobe_a.mass, self.preprobe_b.mass)

    @property
    def probe_effect_linf(self) -> float:
        return max(
            max(
                _linf(first.activation, second.activation),
                _linf(first.afterimage, second.afterimage),
            )
            for first, second in zip(self.probe_a, self.probe_b, strict=True)
        )


@dataclass(frozen=True, slots=True)
class S1LRebindMeasurement:
    refinement: int
    rebound_preprobe: S1LFieldState
    fresh_preprobe: S1LFieldState
    rebound_probe: tuple[S1LFieldState, S1LFieldState]
    fresh_probe: tuple[S1LFieldState, S1LFieldState]
    raw_payload_retained: bool = False
    decision_allowed: bool = False

    @property
    def maximum_state_linf(self) -> float:
        pairs = (
            (self.rebound_preprobe, self.fresh_preprobe),
            *zip(self.rebound_probe, self.fresh_probe, strict=True),
        )
        return max(
            max(
                _linf(first.activation, second.activation),
                _linf(first.afterimage, second.afterimage),
                _linf(first.mass, second.mass),
            )
            for first, second in pairs
        )


def _values(auditory_index: int, visual_index: int):
    auditory = tuple(
        0.8 if index == auditory_index else 0.0
        for index in range(len(SYNTHETIC_AUDITORY_CARRIER_IDS))
    )
    visual = tuple(
        0.6 if index == visual_index else 0.0
        for index in range(len(SYNTHETIC_VISUAL_CONFIG.carrier_ids))
    )
    return auditory, visual


def _source_digest(
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
) -> str:
    payload = []
    for sequence in sequences:
        payload.append(
            {
                "modality_id": sequence.modality_id,
                "geometry_id": sequence.geometry_id,
                "frames": [
                    {
                        "snapshot_id": item.frame.snapshot_id,
                        "start_tick": item.field_time.window_start_tick,
                        "end_tick": item.field_time.window_end_tick,
                        "carrier_ids": item.frame.carrier_ids,
                        "values": item.frame.values,
                    }
                    for item in sequence.frames
                ],
            }
        )
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _source_invariants(
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
) -> S1LSourceInvariants:
    values = tuple(
        value
        for sequence in sequences
        for item in sequence.frames
        for value in item.frame.values
    )
    return S1LSourceInvariants(
        support_count=sum(len(sequence.frames) for sequence in sequences),
        event_count=sum(len(sequence.frames) for sequence in sequences),
        value_multiset=tuple(sorted(values)),
        l1_amplitude=math.fsum(abs(value) for value in values),
        l2_amplitude=math.sqrt(math.fsum(value * value for value in values)),
    )


def build_s1l_source_contract(
    *,
    start_tick: int = 0,
    phase_prefix: str = "s1l",
) -> S1LSourceContract:
    """Build the fixed reduced AV sources without raw media payloads."""

    history_end = start_tick + S1L_HISTORY_SUPPORT_COUNT * S1J_SUPPORT_TICKS
    settle_end = history_end + S1L_SETTLE_SUPPORT_COUNT * S1J_SUPPORT_TICKS
    probe_contact_end = settle_end + S1J_SUPPORT_TICKS
    probe_end = probe_contact_end + S1J_SUPPORT_TICKS
    auditory_a, visual_a = _values(0, 5)
    auditory_b, visual_b = _values(7, 12)
    history_a = synthetic_av_repeated_sequences(
        f"{phase_prefix}.history-a",
        start_tick,
        history_end,
        S1J_SUPPORT_TICKS,
        auditory_a,
        visual_a,
    )
    history_b = synthetic_av_repeated_sequences(
        f"{phase_prefix}.history-b",
        start_tick,
        history_end,
        S1J_SUPPORT_TICKS,
        auditory_b,
        visual_b,
    )
    settle = synthetic_av_repeated_sequences(
        f"{phase_prefix}.settle",
        history_end,
        settle_end,
        S1J_SUPPORT_TICKS,
        _AUDITORY_ZERO,
        _VISUAL_ZERO,
    )
    probe_auditory = tuple(
        0.4 if index == 3 else 0.0
        for index in range(len(SYNTHETIC_AUDITORY_CARRIER_IDS))
    )
    probe_visual = tuple(
        0.4 if index == 8 else 0.0
        for index in range(len(SYNTHETIC_VISUAL_CONFIG.carrier_ids))
    )
    probe_contact = synthetic_av_sequences(
        f"{phase_prefix}.probe-contact",
        settle_end,
        probe_contact_end,
        probe_auditory,
        probe_visual,
    )
    probe_null = synthetic_av_sequences(
        f"{phase_prefix}.probe-null",
        probe_contact_end,
        probe_end,
        _AUDITORY_ZERO,
        _VISUAL_ZERO,
    )
    return S1LSourceContract(
        history_a=history_a,
        history_b=history_b,
        settle=settle,
        probe_contact=probe_contact,
        probe_null=probe_null,
        history_a_digest=_source_digest(history_a),
        history_b_digest=_source_digest(history_b),
        probe_digest=_source_digest(probe_contact),
        history_a_invariants=_source_invariants(history_a),
        history_b_invariants=_source_invariants(history_b),
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
    raise S1LF3HistoryFunctionError("unknown S1-L model arm")


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


def _state(field: SharedMCMField) -> S1LFieldState:
    if field.substrate is None:
        raise S1LF3HistoryFunctionError("S1-L state lost M")
    snapshot = field.snapshot()
    return S1LFieldState(
        activation=snapshot.activation,
        afterimage=snapshot.afterimage,
        mass=snapshot.substrate_mass,
    )


def _linf(first: tuple[float, ...], second: tuple[float, ...]) -> float:
    return max(
        (abs(left - right) for left, right in zip(first, second, strict=True)),
        default=0.0,
    )


def _run_path(
    history,
    source: S1LSourceContract,
    model_id: str,
    refinement: int,
    *,
    neutralized: bool,
):
    arm, calculator = _model(model_id)
    field = _initial_field(history, arm)
    event_count = 0
    for sequences in (history, source.settle):
        advanced = _advance(field, sequences, calculator, refinement)
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


def run_s1l_model_pair(
    model_id: str,
    refinement: int,
    *,
    neutralized: bool = False,
) -> S1LModelPairMeasurement:
    """Compose one A/B model pair without making a research decision."""

    if refinement not in S1L_REFINEMENTS:
        raise S1LF3HistoryFunctionError("S1-L refinement must be 1, 2, or 4")
    if neutralized and model_id != "f3":
        raise S1LF3HistoryFunctionError(
            "S1-L M neutralization is bound only to the F3 control copy"
        )
    source = build_s1l_source_contract()
    path_a = _run_path(
        source.history_a,
        source,
        model_id,
        refinement,
        neutralized=neutralized,
    )
    path_b = _run_path(
        source.history_b,
        source,
        model_id,
        refinement,
        neutralized=neutralized,
    )
    if path_a[2] != path_b[2]:
        raise S1LF3HistoryFunctionError("S1-L A/B event budgets differ")
    return S1LModelPairMeasurement(
        model_id=model_id,
        refinement=refinement,
        preprobe_a=path_a[0],
        preprobe_b=path_b[0],
        probe_a=path_a[1],
        probe_b=path_b[1],
        source_event_count_per_path=path_a[2],
        neutralized=neutralized,
    )


def run_s1l_rebind_control(refinement: int = 4) -> S1LRebindMeasurement:
    """Compose the external-neutralization rebind control in memory."""

    if refinement not in S1L_REFINEMENTS:
        raise S1LF3HistoryFunctionError("S1-L refinement must be 1, 2, or 4")
    source = build_s1l_source_contract()
    field = _initial_field(source.history_a, S1J_ACTIVE_ARM)
    for sequences in (source.history_a, source.settle):
        field = _advance(
            field,
            sequences,
            compute_mcm_f3_coupling,
            refinement,
        ).field
    rebound = neutralize_mcm_f3_mass(align_mcm_f3_fast_state(field))

    shifted = build_s1l_source_contract(
        start_tick=6 * S1J_SUPPORT_TICKS,
        phase_prefix="s1l.rebind",
    )
    fresh = _initial_field(shifted.history_b, S1J_ACTIVE_ARM)
    fresh_fill = synthetic_av_repeated_sequences(
        "s1l.rebind.fresh-fill",
        0,
        6 * S1J_SUPPORT_TICKS,
        S1J_SUPPORT_TICKS,
        _AUDITORY_ZERO,
        _VISUAL_ZERO,
    )
    fresh = _advance(
        fresh,
        fresh_fill,
        compute_mcm_f3_coupling,
        refinement,
    ).field

    for sequences in (shifted.history_b, shifted.settle):
        rebound = _advance(
            rebound,
            sequences,
            compute_mcm_f3_coupling,
            refinement,
        ).field
        fresh = _advance(
            fresh,
            sequences,
            compute_mcm_f3_coupling,
            refinement,
        ).field
    rebound = align_mcm_f3_fast_state(rebound)
    fresh = align_mcm_f3_fast_state(fresh)
    rebound_preprobe = _state(rebound)
    fresh_preprobe = _state(fresh)
    rebound_probe = []
    fresh_probe = []
    for sequences in (shifted.probe_contact, shifted.probe_null):
        rebound = _advance(
            rebound,
            sequences,
            compute_mcm_f3_coupling,
            refinement,
        ).field
        fresh = _advance(
            fresh,
            sequences,
            compute_mcm_f3_coupling,
            refinement,
        ).field
        rebound_probe.append(_state(rebound))
        fresh_probe.append(_state(fresh))
    return S1LRebindMeasurement(
        refinement=refinement,
        rebound_preprobe=rebound_preprobe,
        fresh_preprobe=fresh_preprobe,
        rebound_probe=tuple(rebound_probe),
        fresh_probe=tuple(fresh_probe),
    )


def s1l_f3_history_function_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            S1LSourceInvariants,
            S1LSourceContract,
            S1LFieldState,
            S1LModelPairMeasurement,
            S1LRebindMeasurement,
        )
        for item in fields(cls)
    )
