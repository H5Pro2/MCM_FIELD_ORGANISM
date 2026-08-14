"""In-memory W7-B R8/C8 discrimination against linear trace baselines."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

import numpy as np

from .audio_video_field_geometry import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .mcm_local_development_state import MCMLocalDevelopmentContract
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    _diffusion_generator,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff import handoff_receptor_completion_groups
from .s2_reference_baselines import (
    S2ReferenceState,
    _matrix_exponential,
    apply_s2_reference_point_contacts,
)
from .s2_reference_runner import (
    advance_s2_controlled_receptor_batch,
    advance_s2c11_r8c8_world,
    equalize_fast_state_for_probe,
    measure_s2c11_r8c8_pair,
    observe_s2c11_r8c8_probe,
)
from .s2_reference_worlds import (
    S2PreparedProbePlan,
    S2PreparedR8C8Plan,
    prepare_s2c4_probe_plan,
    prepare_s2c11_r8c8_receptor_plans,
)
from .shared_mcm_field import (
    SharedMCMField,
    attach_zero_mcm_local_development,
    build_shared_mcm_field,
)
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import (
    TransientNeuronInputSet,
    project_transient_docks_to_neuron_inputs,
)


class W7BLinearHistoryDiscriminationError(ValueError):
    """Raised when the bounded W7-B technical comparison is invalid."""


_TOLERANCE = 2e-12
_EQUATION_ID = "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1"
_DECISIONS = {
    "NO_R8_C8_EFFECT_IN_LINEAR_REFERENCE",
    "REFERENCE_IMPLEMENTATION_MISMATCH",
    "LINEAR_RECIPROCAL_TRACE_SUFFICIENT",
}


@dataclass(frozen=True, slots=True)
class _StateSample:
    tick: int
    state: S2ReferenceState


@dataclass(frozen=True, slots=True)
class W7BLinearHistoryDiscriminationResult:
    """Scalar-only technical result; no field trajectory is retained."""

    technical_decision: str
    tolerance: float
    r8_plan_digest: str
    c8_plan_digest: str
    probe_plan_digest: str
    formation_support_count_r8: int
    formation_support_count_c8: int
    probe_support_count: int
    l_pair_b1: float
    l_pair_b2: float
    d_pair_b0: float
    d_pair_b1: float
    d_pair_b2: float
    b2_reference_error: float
    b0_exact: bool
    b1_no_feedback_effect: bool
    b2_production_reproduced: bool
    finite_scalars: bool
    raw_trajectories_retained: bool = False
    report_written: bool = False
    browser_started: bool = False

    def __post_init__(self) -> None:
        if self.technical_decision not in _DECISIONS or self.tolerance != _TOLERANCE:
            raise W7BLinearHistoryDiscriminationError("invalid W7-B decision contract")
        for role in ("r8_plan_digest", "c8_plan_digest", "probe_plan_digest"):
            value = getattr(self, role)
            if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
                raise W7BLinearHistoryDiscriminationError(f"invalid {role}")
        for role in (
            "formation_support_count_r8",
            "formation_support_count_c8",
            "probe_support_count",
        ):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise W7BLinearHistoryDiscriminationError(f"invalid {role}")
        for role in (
            "l_pair_b1",
            "l_pair_b2",
            "d_pair_b0",
            "d_pair_b1",
            "d_pair_b2",
            "b2_reference_error",
        ):
            value = float(getattr(self, role))
            if not math.isfinite(value) or value < 0.0:
                raise W7BLinearHistoryDiscriminationError(f"invalid {role}")
            object.__setattr__(self, role, value)
        controls = (
            self.b0_exact,
            self.b1_no_feedback_effect,
            self.b2_production_reproduced,
            self.finite_scalars,
        )
        if any(value is not True for value in controls):
            raise W7BLinearHistoryDiscriminationError("W7-B technical controls failed")
        if self.raw_trajectories_retained or self.report_written or self.browser_started:
            raise W7BLinearHistoryDiscriminationError("W7-B crossed its in-memory boundary")

    def canonical_payload(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        return hashlib.sha256(encoded).hexdigest()


def _initial_field(plan: S2PreparedR8C8Plan) -> SharedMCMField:
    frames = tuple(sequence.frames[0].frame for sequence in plan.receptor_sequences)
    return build_shared_mcm_field(
        frames,
        audio_video_dock_anatomies(
            auditory_carrier_count=len(frames[0].carrier_ids),
            visual_grid_columns=6,
            visual_grid_rows=4,
        ),
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )


def _inputs_for_plan(
    field: SharedMCMField,
    sequences: tuple[object, object],
    steps: tuple[object, ...],
) -> tuple[TransientNeuronInputSet, ...]:
    handoff = handoff_receptor_completion_groups(sequences, steps)
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
    ):
        raise W7BLinearHistoryDiscriminationError("W7-B receptor handoff is incomplete")
    return tuple(
        project_transient_docks_to_neuron_inputs(
            map_proposal_batch_to_transient_docks(batch, field.docks),
            field.docks,
        )
        for batch in handoff.batches
    )


def _events(
    transient_inputs: TransientNeuronInputSet,
    neuron_index: dict[str, int],
) -> tuple[tuple[int, tuple[tuple[int, float, float], ...]], ...]:
    grouped: dict[int, list[tuple[int, float, float]]] = {}
    rate = transient_inputs.step_time.ticks_per_second
    for item in transient_inputs.neuron_inputs:
        index = neuron_index[item.neuron_id]
        for contact in item.contacts:
            duration = (
                contact.organism_read_time.window_end_tick
                - contact.organism_read_time.window_start_tick
            ) / rate
            grouped.setdefault(contact.completion_tick, []).append(
                (index, duration, contact.value)
            )
    return tuple((tick, tuple(values)) for tick, values in sorted(grouped.items()))


def _advance_reference_batches(
    model_id: str,
    state: S2ReferenceState,
    inputs: tuple[TransientNeuronInputSet, ...],
    generator: np.ndarray,
    neuron_index: dict[str, int],
    transition_cache: dict[float, np.ndarray],
) -> tuple[S2ReferenceState, tuple[_StateSample, ...]]:
    samples: list[_StateSample] = []

    def advance_free(elapsed: float) -> None:
        nonlocal state
        if elapsed == 0.0:
            return
        transition = transition_cache.get(elapsed)
        if transition is None:
            count = len(state.activation)
            identity = np.eye(count, dtype=np.float64)
            zero = np.zeros((count, count), dtype=np.float64)
            tracking = 2.0
            local_rate = 0.25 / 8.0
            if model_id == "b1":
                s_s, s_l = generator, zero
            elif model_id == "b2":
                s_s = generator - 0.25 * identity
                s_l = 0.25 * identity
            else:
                raise W7BLinearHistoryDiscriminationError(
                    "W7-B reference permits only B1 or B2"
                )
            matrix = np.block(
                [
                    [s_s, zero, s_l],
                    [tracking * identity, -tracking * identity, zero],
                    [local_rate * identity, zero, -local_rate * identity],
                ]
            )
            transition = _matrix_exponential(matrix * elapsed)
            transition_cache[elapsed] = transition
        values = transition @ np.concatenate(
            (
                np.asarray(state.activation, dtype=np.float64),
                np.asarray(state.afterimage, dtype=np.float64),
                np.asarray(state.development, dtype=np.float64),
            )
        )
        count = len(state.activation)
        state = S2ReferenceState(
            tuple(values[:count]),
            tuple(values[count : 2 * count]),
            tuple(values[2 * count :]),
        )

    for transient_inputs in inputs:
        step = transient_inputs.step_time
        current_tick = step.start_tick
        for completion_tick, contacts in _events(transient_inputs, neuron_index):
            elapsed = (completion_tick - current_tick) / step.ticks_per_second
            advance_free(elapsed)
            state = apply_s2_reference_point_contacts(
                state,
                contacts,
                response_time_seconds=1.0,
            )
            samples.append(_StateSample(completion_tick, state))
            current_tick = completion_tick
        remaining = (step.end_tick - current_tick) / step.ticks_per_second
        if remaining > 0.0:
            advance_free(remaining)
            samples.append(_StateSample(step.end_tick, state))
    return state, tuple(samples)


def _production_b2(
    plan: S2PreparedR8C8Plan,
    probe: S2PreparedProbePlan,
) -> tuple[
    S2ReferenceState,
    tuple[_StateSample, ...],
    S2ReferenceState,
    tuple[_StateSample, ...],
    tuple[TransientNeuronInputSet, ...],
    tuple[TransientNeuronInputSet, ...],
    np.ndarray,
    dict[str, int],
]:
    base = _initial_field(plan)
    generator = _diffusion_generator(base, NeutralLocalFieldSubstrateConfig(1.0))
    neuron_index = {
        neuron.neuron_id: index for index, neuron in enumerate(base.layer.neurons)
    }
    formation_inputs = _inputs_for_plan(
        base,
        plan.receptor_sequences,
        plan.proposal_steps,
    )
    field = attach_zero_mcm_local_development(
        base,
        MCMLocalDevelopmentContract(_EQUATION_ID, 8.0, 0.25),
    )
    formation_samples: list[_StateSample] = []
    for transient_inputs in formation_inputs:
        distribution = ReceptorDistribution(
            CommonFieldTime(
                transient_inputs.step_time.clock_id,
                transient_inputs.step_time.start_tick,
                transient_inputs.step_time.end_tick,
            ),
            (),
        )

        def observe(tick: int, activation: object, afterimage: object, local: object) -> None:
            formation_samples.append(
                _StateSample(
                    tick,
                    S2ReferenceState(tuple(activation), tuple(afterimage), tuple(local)),
                )
            )

        field = advance_s2_controlled_receptor_batch(
            "b2",
            field,
            distribution,
            transient_inputs,
            NeutralLocalFieldSubstrateConfig(1.0),
            NeutralFastAfterimageConfig(0.5),
            _state_observer=observe,
        ).field
    formation_state = S2ReferenceState(
        tuple(item.activation for item in field.layer.neurons),
        tuple(item.afterimage for item in field.layer.neurons),
        field.development.dispositions,
    )
    field = equalize_fast_state_for_probe(field)
    probe_inputs = _inputs_for_plan(
        field,
        probe.receptor_sequences,
        (probe.proposal_step,),
    )
    probe_samples: list[_StateSample] = []
    for transient_inputs in probe_inputs:
        distribution = ReceptorDistribution(
            CommonFieldTime(
                transient_inputs.step_time.clock_id,
                transient_inputs.step_time.start_tick,
                transient_inputs.step_time.end_tick,
            ),
            (),
        )

        def observe_probe(tick: int, activation: object, afterimage: object, local: object) -> None:
            probe_samples.append(
                _StateSample(
                    tick,
                    S2ReferenceState(tuple(activation), tuple(afterimage), tuple(local)),
                )
            )

        field = advance_s2_controlled_receptor_batch(
            "b2",
            field,
            distribution,
            transient_inputs,
            NeutralLocalFieldSubstrateConfig(1.0),
            NeutralFastAfterimageConfig(0.5),
            _state_observer=observe_probe,
        ).field
    probe_state = S2ReferenceState(
        tuple(item.activation for item in field.layer.neurons),
        tuple(item.afterimage for item in field.layer.neurons),
        field.development.dispositions,
    )
    return (
        formation_state,
        tuple(formation_samples),
        probe_state,
        tuple(probe_samples),
        formation_inputs,
        probe_inputs,
        generator,
        neuron_index,
    )


def _zero_state(size: int) -> S2ReferenceState:
    zero = (0.0,) * size
    return S2ReferenceState(zero, zero, zero)


def _equalized(state: S2ReferenceState) -> S2ReferenceState:
    zero = (0.0,) * len(state.activation)
    return S2ReferenceState(zero, zero, state.development)


def _state_error(first: S2ReferenceState, second: S2ReferenceState) -> float:
    return max(
        abs(left - right)
        for first_values, second_values in zip(
            (first.activation, first.afterimage, first.development),
            (second.activation, second.afterimage, second.development),
            strict=True,
        )
        for left, right in zip(first_values, second_values, strict=True)
    )


def _trace_error(
    first: tuple[_StateSample, ...],
    second: tuple[_StateSample, ...],
) -> float:
    if tuple(item.tick for item in first) != tuple(item.tick for item in second):
        raise W7BLinearHistoryDiscriminationError("W7-B trace support differs")
    return max(
        _state_error(left.state, right.state)
        for left, right in zip(first, second, strict=True)
    )


def _local_distance(first: S2ReferenceState, second: S2ReferenceState) -> float:
    return max(
        abs(left - right)
        for left, right in zip(first.development, second.development, strict=True)
    )


def _fast_trace_distance(
    first: tuple[_StateSample, ...],
    second: tuple[_StateSample, ...],
) -> float:
    if tuple(item.tick for item in first) != tuple(item.tick for item in second):
        raise W7BLinearHistoryDiscriminationError("W7-B probe support differs")
    return max(
        abs(left - right)
        for first_sample, second_sample in zip(first, second, strict=True)
        for first_values, second_values in (
            (first_sample.state.activation, second_sample.state.activation),
            (first_sample.state.afterimage, second_sample.state.afterimage),
        )
        for left, right in zip(first_values, second_values, strict=True)
    )


def _reference_arm(
    model_id: str,
    formation_inputs: tuple[TransientNeuronInputSet, ...],
    probe_inputs: tuple[TransientNeuronInputSet, ...],
    generator: np.ndarray,
    neuron_index: dict[str, int],
    transition_cache: dict[float, np.ndarray],
) -> tuple[S2ReferenceState, tuple[_StateSample, ...], tuple[_StateSample, ...]]:
    formation, formation_trace = _advance_reference_batches(
        model_id,
        _zero_state(len(neuron_index)),
        formation_inputs,
        generator,
        neuron_index,
        transition_cache,
    )
    _, probe_trace = _advance_reference_batches(
        model_id,
        _equalized(formation),
        probe_inputs,
        generator,
        neuron_index,
        transition_cache,
    )
    return formation, formation_trace, probe_trace


def run_w7b_linear_history_discrimination() -> W7BLinearHistoryDiscriminationResult:
    """Run only the bounded in-memory W7-B technical comparison."""

    r8_plan, c8_plan = prepare_s2c11_r8c8_receptor_plans()
    probe = prepare_s2c4_probe_plan()

    r8_b0 = advance_s2c11_r8c8_world(r8_plan, "b0")
    c8_b0 = advance_s2c11_r8c8_world(c8_plan, "b0")
    d_pair_b0 = measure_s2c11_r8c8_pair(
        observe_s2c11_r8c8_probe(r8_b0, probe),
        observe_s2c11_r8c8_probe(c8_b0, probe),
    ).d_pair

    r8_prod = _production_b2(r8_plan, probe)
    c8_prod = _production_b2(c8_plan, probe)
    (
        r8_prod_formation,
        r8_prod_formation_trace,
        r8_prod_probe,
        r8_prod_probe_trace,
        r8_formation_inputs,
        r8_probe_inputs,
        r8_generator,
        r8_index,
    ) = r8_prod
    (
        c8_prod_formation,
        c8_prod_formation_trace,
        c8_prod_probe,
        c8_prod_probe_trace,
        c8_formation_inputs,
        c8_probe_inputs,
        c8_generator,
        c8_index,
    ) = c8_prod

    b1_transition_cache: dict[float, np.ndarray] = {}
    b2_transition_cache: dict[float, np.ndarray] = {}
    r8_b1, _, r8_b1_probe = _reference_arm(
        "b1", r8_formation_inputs, r8_probe_inputs, r8_generator, r8_index,
        b1_transition_cache,
    )
    c8_b1, _, c8_b1_probe = _reference_arm(
        "b1", c8_formation_inputs, c8_probe_inputs, c8_generator, c8_index,
        b1_transition_cache,
    )
    r8_b2, r8_b2_formation_trace, r8_b2_probe = _reference_arm(
        "b2", r8_formation_inputs, r8_probe_inputs, r8_generator, r8_index,
        b2_transition_cache,
    )
    c8_b2, c8_b2_formation_trace, c8_b2_probe = _reference_arm(
        "b2", c8_formation_inputs, c8_probe_inputs, c8_generator, c8_index,
        b2_transition_cache,
    )

    l_pair_b1 = _local_distance(r8_b1, c8_b1)
    l_pair_b2 = _local_distance(r8_prod_formation, c8_prod_formation)
    d_pair_b1 = _fast_trace_distance(r8_b1_probe, c8_b1_probe)
    d_pair_b2 = _fast_trace_distance(r8_prod_probe_trace, c8_prod_probe_trace)
    b2_reference_error = max(
        _state_error(r8_prod_formation, r8_b2),
        _state_error(c8_prod_formation, c8_b2),
        _state_error(r8_prod_probe, r8_b2_probe[-1].state),
        _state_error(c8_prod_probe, c8_b2_probe[-1].state),
        _trace_error(r8_prod_formation_trace, r8_b2_formation_trace),
        _trace_error(c8_prod_formation_trace, c8_b2_formation_trace),
        _trace_error(r8_prod_probe_trace, r8_b2_probe),
        _trace_error(c8_prod_probe_trace, c8_b2_probe),
    )

    reproduction = _production_b2(r8_plan, probe)
    b2_reproduced = (
        reproduction[0] == r8_prod_formation
        and reproduction[1] == r8_prod_formation_trace
        and reproduction[2] == r8_prod_probe
        and reproduction[3] == r8_prod_probe_trace
    )
    scalars = (
        l_pair_b1,
        l_pair_b2,
        d_pair_b0,
        d_pair_b1,
        d_pair_b2,
        b2_reference_error,
    )
    finite_scalars = all(math.isfinite(value) and value >= 0.0 for value in scalars)
    if b2_reference_error > _TOLERANCE:
        decision = "REFERENCE_IMPLEMENTATION_MISMATCH"
    elif l_pair_b2 <= _TOLERANCE or d_pair_b2 <= _TOLERANCE:
        decision = "NO_R8_C8_EFFECT_IN_LINEAR_REFERENCE"
    else:
        decision = "LINEAR_RECIPROCAL_TRACE_SUFFICIENT"
    return W7BLinearHistoryDiscriminationResult(
        technical_decision=decision,
        tolerance=_TOLERANCE,
        r8_plan_digest=r8_plan.digest(),
        c8_plan_digest=c8_plan.digest(),
        probe_plan_digest=probe.digest(),
        formation_support_count_r8=r8_plan.source_support_count,
        formation_support_count_c8=c8_plan.source_support_count,
        probe_support_count=len(r8_prod_probe_trace),
        l_pair_b1=l_pair_b1,
        l_pair_b2=l_pair_b2,
        d_pair_b0=d_pair_b0,
        d_pair_b1=d_pair_b1,
        d_pair_b2=d_pair_b2,
        b2_reference_error=b2_reference_error,
        b0_exact=d_pair_b0 == 0.0,
        b1_no_feedback_effect=d_pair_b1 <= _TOLERANCE,
        b2_production_reproduced=b2_reproduced,
        finite_scalars=finite_scalars,
    )
