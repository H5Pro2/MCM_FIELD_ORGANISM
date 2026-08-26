"""Preregistered technical two-stage causal check for the S1-B L state."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Iterable

from .field_step_time import MCMFieldStepTime
from .mcm_local_development_state import MCMLocalDevelopmentContract
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_time_model import ReceptorTimeSequence
from .s1b_asynchronous_field_runtime import run_s1b_asynchronous_field
from .s1b_reciprocal_accommodation import (
    neutralize_mcm_local_development,
    swap_mcm_local_development,
)
from .shared_mcm_field import SharedMCMField


class S1BCausalTwoStageError(ValueError):
    """Raised when the preregistered causal comparison becomes ambiguous."""


_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_TOLERANCE = 1e-12
_ACTIVE_RATE = 0.25
_CAPACITY_RATIO = 8.0
_DECISIONS = {
    "STOP_NONINFORMATIVE_FORMATION",
    "NO_DETECTABLE_L_CAUSAL_EFFECT_IN_THIS_CONTRACT",
    "LOCAL_L_STATE_CAUSALLY_ALTERS_LATER_S_TRAJECTORY_IN_S1B_REFERENCE",
}


def _finite(value: object, role: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise S1BCausalTwoStageError(f"{role} must be finite")
    return number


@dataclass(frozen=True, slots=True)
class S1BCausalProbeSample:
    """One passive S/H/L observation at a probe completion."""

    completion_tick: int
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    development: tuple[float, ...]

    def __post_init__(self) -> None:
        if isinstance(self.completion_tick, bool) or not isinstance(
            self.completion_tick,
            int,
        ):
            raise S1BCausalTwoStageError("probe completion tick must be an integer")
        vectors = (
            tuple(self.activation),
            tuple(self.afterimage),
            tuple(self.development),
        )
        if not vectors[0] or any(len(item) != len(vectors[0]) for item in vectors):
            raise S1BCausalTwoStageError(
                "probe sample requires complete co-located S/H/L vectors"
            )
        for role, values in zip(
            ("activation", "afterimage", "development"),
            vectors,
            strict=True,
        ):
            normalized = tuple(_finite(value, role) for value in values)
            if any(abs(value) > 1.0 + _TOLERANCE for value in normalized):
                raise S1BCausalTwoStageError(
                    f"probe {role} values must remain normalized"
                )
            object.__setattr__(self, role, normalized)


@dataclass(frozen=True, slots=True)
class S1BCausalProbeTrace:
    """Immutable passive trajectory for one preregistered probe arm."""

    arm_id: str
    samples: tuple[S1BCausalProbeSample, ...]
    end_snapshot_digest: str
    end_fast_projection_digest: str

    def __post_init__(self) -> None:
        if self.arm_id not in {"retained", "neutralized", "swapped", "null"}:
            raise S1BCausalTwoStageError("unknown causal probe arm")
        samples = tuple(self.samples)
        if not samples or any(
            not isinstance(sample, S1BCausalProbeSample) for sample in samples
        ):
            raise S1BCausalTwoStageError("causal probe trace requires samples")
        ticks = tuple(sample.completion_tick for sample in samples)
        if tuple(sorted(ticks)) != ticks or len(set(ticks)) != len(ticks):
            raise S1BCausalTwoStageError(
                "causal probe trace requires unique ordered completion ticks"
            )
        if not _DIGEST.fullmatch(self.end_snapshot_digest) or not _DIGEST.fullmatch(
            self.end_fast_projection_digest
        ):
            raise S1BCausalTwoStageError("causal probe digest is invalid")
        object.__setattr__(self, "samples", samples)


@dataclass(frozen=True, slots=True)
class S1BCausalTwoStageResult:
    """Scalar-only result of the preregistered W6-D technical comparison."""

    technical_decision: str
    tolerance: float
    l_a_linf: float
    l_b_linf: float
    l_ab_linf: float
    d_rn_s: float
    d_rx_s: float
    d_xn_s: float
    d_rn_h: float
    d_rx_h: float
    fast_r_n_equal: bool
    fast_r_x_equal: bool
    null_formation_equal: bool
    null_probe_equal: bool | None
    formation_support_count_a: int
    formation_support_count_b: int
    probe_support_count: int
    formation_digest_a: str
    formation_digest_b: str
    formation_digest_null: str
    traces: tuple[S1BCausalProbeTrace, ...]

    def __post_init__(self) -> None:
        if self.technical_decision not in _DECISIONS:
            raise S1BCausalTwoStageError("unknown causal two-stage decision")
        if self.tolerance != _TOLERANCE:
            raise S1BCausalTwoStageError("causal tolerance is fixed")
        for role in (
            "l_a_linf",
            "l_b_linf",
            "l_ab_linf",
            "d_rn_s",
            "d_rx_s",
            "d_xn_s",
            "d_rn_h",
            "d_rx_h",
        ):
            if _finite(getattr(self, role), role) < 0.0:
                raise S1BCausalTwoStageError(f"{role} must be nonnegative")
        for role in (
            "formation_support_count_a",
            "formation_support_count_b",
        ):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise S1BCausalTwoStageError(f"{role} must be positive")
        if (
            isinstance(self.probe_support_count, bool)
            or not isinstance(self.probe_support_count, int)
            or self.probe_support_count < 0
        ):
            raise S1BCausalTwoStageError("probe support count is invalid")
        for role in (
            "formation_digest_a",
            "formation_digest_b",
            "formation_digest_null",
        ):
            if not _DIGEST.fullmatch(getattr(self, role)):
                raise S1BCausalTwoStageError(f"{role} is invalid")
        traces = tuple(self.traces)
        if any(not isinstance(trace, S1BCausalProbeTrace) for trace in traces):
            raise S1BCausalTwoStageError("causal result traces are invalid")
        if self.technical_decision == "STOP_NONINFORMATIVE_FORMATION":
            if traces or self.probe_support_count != 0 or self.null_probe_equal is not None:
                raise S1BCausalTwoStageError(
                    "noninformative formation must stop before the probe"
                )
        else:
            if tuple(trace.arm_id for trace in traces) != (
                "retained",
                "neutralized",
                "swapped",
                "null",
            ):
                raise S1BCausalTwoStageError(
                    "causal result requires all four ordered probe traces"
                )
            if self.probe_support_count < 1 or self.null_probe_equal is not True:
                raise S1BCausalTwoStageError(
                    "completed causal result requires one valid null probe"
                )
        object.__setattr__(self, "traces", traces)


def _sequence_shape(
    sequences: tuple[ReceptorTimeSequence, ...],
) -> tuple[object, ...]:
    return tuple(
        (
            sequence.modality_id,
            sequence.geometry_id,
            sequence.clock_id,
            tuple(
                (
                    timed.frame.carrier_ids,
                    len(timed.frame.values),
                    timed.field_time.window_start_tick,
                    timed.field_time.window_end_tick,
                )
                for timed in sequence.frames
            ),
        )
        for sequence in sequences
    )


def _geometry_shape(
    sequences: tuple[ReceptorTimeSequence, ...],
) -> tuple[object, ...]:
    return tuple(
        (
            sequence.modality_id,
            sequence.geometry_id,
            tuple(
                (timed.frame.carrier_ids, len(timed.frame.values))
                for timed in sequence.frames
            )[:1],
        )
        for sequence in sequences
    )


def _linf(values: Iterable[float]) -> float:
    values_in = tuple(abs(float(value)) for value in values)
    return max(values_in, default=0.0)


def _vector_distance(first: Iterable[float], second: Iterable[float]) -> float:
    first_in = tuple(first)
    second_in = tuple(second)
    if len(first_in) != len(second_in):
        raise S1BCausalTwoStageError("causal vectors must have equal length")
    return _linf(a - b for a, b in zip(first_in, second_in, strict=True))


def _trace_distance(
    first: S1BCausalProbeTrace,
    second: S1BCausalProbeTrace,
    role: str,
) -> float:
    first_ticks = tuple(sample.completion_tick for sample in first.samples)
    second_ticks = tuple(sample.completion_tick for sample in second.samples)
    if first_ticks != second_ticks:
        raise S1BCausalTwoStageError("probe arms require identical observer support")
    return max(
        _vector_distance(getattr(a, role), getattr(b, role))
        for a, b in zip(first.samples, second.samples, strict=True)
    )


def _probe_trace(
    arm_id: str,
    field: SharedMCMField,
    sequences: tuple[ReceptorTimeSequence, ...],
    steps: tuple[MCMFieldStepTime, ...],
    field_config: NeutralLocalFieldSubstrateConfig,
    contract: MCMLocalDevelopmentContract,
    afterimage_config: NeutralFastAfterimageConfig,
) -> tuple[S1BCausalProbeTrace, int]:
    samples: list[S1BCausalProbeSample] = []

    def observe(tick: int, activation: object, afterimage: object, local: object) -> None:
        samples.append(
            S1BCausalProbeSample(
                tick,
                tuple(float(value) for value in activation),  # type: ignore[union-attr]
                tuple(float(value) for value in afterimage),  # type: ignore[union-attr]
                tuple(float(value) for value in local),  # type: ignore[union-attr]
            )
        )

    run = run_s1b_asynchronous_field(
        field,
        sequences,
        steps,
        field_config,
        contract,
        afterimage_config=afterimage_config,
        observer=observe,
    )
    return (
        S1BCausalProbeTrace(
            arm_id,
            tuple(samples),
            run.field.snapshot().digest(),
            run.field.snapshot().fast_state_projection_digest(),
        ),
        run.source_support_count,
    )


def _validate_contracts(
    initial_field: SharedMCMField,
    history_a: tuple[ReceptorTimeSequence, ...],
    history_b: tuple[ReceptorTimeSequence, ...],
    probe: tuple[ReceptorTimeSequence, ...],
    history_steps: tuple[MCMFieldStepTime, ...],
    probe_steps: tuple[MCMFieldStepTime, ...],
    field_config: NeutralLocalFieldSubstrateConfig,
    active_contract: MCMLocalDevelopmentContract,
    null_contract: MCMLocalDevelopmentContract,
    afterimage_config: NeutralFastAfterimageConfig,
) -> None:
    if not isinstance(initial_field, SharedMCMField):
        raise S1BCausalTwoStageError("causal check requires one initial field")
    if (
        initial_field.substrate is not None
        or initial_field.development is not None
        or initial_field.last_distribution is not None
        or any(
            neuron.activation != 0.0 or neuron.afterimage != 0.0
            for neuron in initial_field.layer.neurons
        )
    ):
        raise S1BCausalTwoStageError(
            "causal check requires one untouched neutral initial field"
        )
    if not history_a or not history_b or not probe:
        raise S1BCausalTwoStageError("causal check requires H_A, H_B and P")
    if _sequence_shape(history_a) != _sequence_shape(history_b):
        raise S1BCausalTwoStageError(
            "H_A and H_B require identical geometry and temporal support"
        )
    if _geometry_shape(history_a) != _geometry_shape(probe):
        raise S1BCausalTwoStageError(
            "formation and probe require one receptor geometry"
        )
    if not history_steps or not probe_steps:
        raise S1BCausalTwoStageError("causal check requires two nonempty stages")
    if not isinstance(field_config, NeutralLocalFieldSubstrateConfig) or (
        field_config.response_time_seconds != 1.0
    ):
        raise S1BCausalTwoStageError("W6-D field response is fixed at 1.0 s")
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig) or (
        afterimage_config.time_constant_seconds != 0.5
    ):
        raise S1BCausalTwoStageError("W6-D afterimage time is fixed at 0.5 s")
    if (
        not isinstance(active_contract, MCMLocalDevelopmentContract)
        or active_contract.capacity_ratio != _CAPACITY_RATIO
        or active_contract.coupling_rate_per_second != _ACTIVE_RATE
    ):
        raise S1BCausalTwoStageError("W6-D active L contract is fixed")
    if (
        not isinstance(null_contract, MCMLocalDevelopmentContract)
        or null_contract.equation_id != active_contract.equation_id
        or null_contract.capacity_ratio != _CAPACITY_RATIO
        or not null_contract.is_null_arm
    ):
        raise S1BCausalTwoStageError("W6-D null L contract is fixed")


def run_s1b_causal_two_stage(
    initial_field: SharedMCMField,
    history_a_sequences: Iterable[ReceptorTimeSequence],
    history_b_sequences: Iterable[ReceptorTimeSequence],
    probe_sequences: Iterable[ReceptorTimeSequence],
    history_steps: Iterable[MCMFieldStepTime],
    probe_steps: Iterable[MCMFieldStepTime],
    field_config: NeutralLocalFieldSubstrateConfig,
    active_contract: MCMLocalDevelopmentContract,
    null_contract: MCMLocalDevelopmentContract,
    afterimage_config: NeutralFastAfterimageConfig,
) -> S1BCausalTwoStageResult:
    """Execute only the preregistered W6-D comparison on reduced inputs."""

    history_a = tuple(history_a_sequences)
    history_b = tuple(history_b_sequences)
    probe = tuple(probe_sequences)
    history_steps_in = tuple(history_steps)
    probe_steps_in = tuple(probe_steps)
    _validate_contracts(
        initial_field,
        history_a,
        history_b,
        probe,
        history_steps_in,
        probe_steps_in,
        field_config,
        active_contract,
        null_contract,
        afterimage_config,
    )

    try:
        formation_a = run_s1b_asynchronous_field(
            initial_field,
            history_a,
            history_steps_in,
            field_config,
            active_contract,
            afterimage_config=afterimage_config,
        )
        formation_b = run_s1b_asynchronous_field(
            initial_field,
            history_b,
            history_steps_in,
            field_config,
            active_contract,
            afterimage_config=afterimage_config,
        )
        formation_null = run_s1b_asynchronous_field(
            initial_field,
            history_a,
            history_steps_in,
            field_config,
            null_contract,
            afterimage_config=afterimage_config,
        )
        neutral_formation = run_neutral_asynchronous_field(
            initial_field,
            history_a,
            history_steps_in,
            field_config,
            afterimage_config=afterimage_config,
        )
    except ValueError as exc:
        raise S1BCausalTwoStageError(str(exc)) from exc

    field_a = formation_a.field
    field_b = formation_b.field
    field_null = formation_null.field
    l_a = field_a.development.dispositions
    l_b = field_b.development.dispositions
    l_a_linf = _linf(l_a)
    l_b_linf = _linf(l_b)
    l_ab_linf = _vector_distance(l_a, l_b)
    null_formation_equal = (
        field_null.snapshot().fast_state_projection_digest()
        == neutral_formation.field.snapshot().digest()
    )
    if not null_formation_equal:
        raise S1BCausalTwoStageError(
            "STOP_TECHNICAL_INVALID: null formation differs from neutral runtime"
        )

    base = {
        "tolerance": _TOLERANCE,
        "l_a_linf": l_a_linf,
        "l_b_linf": l_b_linf,
        "l_ab_linf": l_ab_linf,
        "fast_r_n_equal": True,
        "fast_r_x_equal": True,
        "null_formation_equal": True,
        "formation_support_count_a": formation_a.source_support_count,
        "formation_support_count_b": formation_b.source_support_count,
        "formation_digest_a": field_a.snapshot().digest(),
        "formation_digest_b": field_b.snapshot().digest(),
        "formation_digest_null": field_null.snapshot().digest(),
    }
    if l_a_linf <= _TOLERANCE or l_ab_linf <= _TOLERANCE:
        return S1BCausalTwoStageResult(
            technical_decision="STOP_NONINFORMATIVE_FORMATION",
            d_rn_s=0.0,
            d_rx_s=0.0,
            d_xn_s=0.0,
            d_rn_h=0.0,
            d_rx_h=0.0,
            null_probe_equal=None,
            probe_support_count=0,
            traces=(),
            **base,
        )

    retained = field_a
    neutralized = neutralize_mcm_local_development(field_a)
    swapped, _ = swap_mcm_local_development(field_a, field_b)
    retained_fast = retained.snapshot().fast_state_projection_digest()
    fast_r_n_equal = (
        retained_fast == neutralized.snapshot().fast_state_projection_digest()
    )
    fast_r_x_equal = (
        retained_fast == swapped.snapshot().fast_state_projection_digest()
    )
    if not fast_r_n_equal or not fast_r_x_equal:
        raise S1BCausalTwoStageError(
            "STOP_TECHNICAL_INVALID: L intervention changed the fast field"
        )

    try:
        retained_trace, probe_count = _probe_trace(
            "retained",
            retained,
            probe,
            probe_steps_in,
            field_config,
            active_contract,
            afterimage_config,
        )
        neutralized_trace, neutralized_count = _probe_trace(
            "neutralized",
            neutralized,
            probe,
            probe_steps_in,
            field_config,
            active_contract,
            afterimage_config,
        )
        swapped_trace, swapped_count = _probe_trace(
            "swapped",
            swapped,
            probe,
            probe_steps_in,
            field_config,
            active_contract,
            afterimage_config,
        )
        null_trace, null_count = _probe_trace(
            "null",
            field_null,
            probe,
            probe_steps_in,
            field_config,
            null_contract,
            afterimage_config,
        )
        neutral_probe = run_neutral_asynchronous_field(
            neutral_formation.field,
            probe,
            probe_steps_in,
            field_config,
            afterimage_config=afterimage_config,
        )
    except ValueError as exc:
        raise S1BCausalTwoStageError(str(exc)) from exc
    if len({probe_count, neutralized_count, swapped_count, null_count}) != 1:
        raise S1BCausalTwoStageError(
            "STOP_TECHNICAL_INVALID: probe support differs between arms"
        )
    null_probe_equal = (
        null_trace.end_fast_projection_digest
        == neutral_probe.field.snapshot().digest()
    )
    if not null_probe_equal:
        raise S1BCausalTwoStageError(
            "STOP_TECHNICAL_INVALID: null probe differs from neutral runtime"
        )

    d_rn_s = _trace_distance(retained_trace, neutralized_trace, "activation")
    d_rx_s = _trace_distance(retained_trace, swapped_trace, "activation")
    d_xn_s = _trace_distance(swapped_trace, neutralized_trace, "activation")
    d_rn_h = _trace_distance(retained_trace, neutralized_trace, "afterimage")
    d_rx_h = _trace_distance(retained_trace, swapped_trace, "afterimage")
    decision = (
        "NO_DETECTABLE_L_CAUSAL_EFFECT_IN_THIS_CONTRACT"
        if max(d_rn_s, d_rx_s, d_xn_s) <= _TOLERANCE
        else "LOCAL_L_STATE_CAUSALLY_ALTERS_LATER_S_TRAJECTORY_IN_S1B_REFERENCE"
    )
    return S1BCausalTwoStageResult(
        technical_decision=decision,
        d_rn_s=d_rn_s,
        d_rx_s=d_rx_s,
        d_xn_s=d_xn_s,
        d_rn_h=d_rn_h,
        d_rx_h=d_rx_h,
        fast_r_n_equal=fast_r_n_equal,
        fast_r_x_equal=fast_r_x_equal,
        null_probe_equal=True,
        probe_support_count=probe_count,
        traces=(
            retained_trace,
            neutralized_trace,
            swapped_trace,
            null_trace,
        ),
        **{key: value for key, value in base.items() if not key.startswith("fast_r_")},
    )
