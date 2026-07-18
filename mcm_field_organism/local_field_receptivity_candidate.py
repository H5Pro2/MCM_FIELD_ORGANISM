"""Passive C1 comparison for one bounded local field receptivity state."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import hashlib
import json
import math
from typing import Callable, Iterable

import numpy as np

from .field_step_time import MCMFieldStepTime
from .mcm_neuron_layer import MCMNeuronLayer
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    _generator_and_boundary,
    _integrate_exactly,
    _neighbor_matrix,
    advance_neutral_fast_shared_field,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import (
    ReceptorDistribution,
    ReceptorDistributor,
    ReceptorDock,
)
from .shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMField,
    _mapped_receptor_contacts,
    build_shared_mcm_field,
    restore_shared_mcm_field,
)


class LocalFieldReceptivityCandidateError(ValueError):
    """Raised when the passive C1 preregistration is violated."""


C1_BRANCH_IDS = ("h_minus", "h_plus", "n_local_field_ablated")
C1_BASELINE_IDS = (
    "b0.neutral_runtime",
    "b1.fast_afterimage",
    "b2.fixed_afterimage_scales",
    "b3.own_contact_saturation",
    "b4.local_product_integrator",
    "b5.static_local_factors",
    "b6.passive_observer",
)

_CLOCK_ID = "organism.c1_receptivity"
_RESPONSE_TIME_SECONDS = 1.0
_AFTERIMAGE_TIME_SECONDS = 0.5
_TICKS_PER_SECOND = 10.0
_PROBE_DURATION_SECONDS = 0.75
_PROBE_ACTIVATION = (0.0, 0.8, 0.0)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _finite_tuple(values: Iterable[float], role: str) -> tuple[float, ...]:
    result = tuple(float(value) for value in values)
    if not result or any(not math.isfinite(value) for value in result):
        raise LocalFieldReceptivityCandidateError(
            f"{role} must contain finite values"
        )
    return result


@dataclass(frozen=True, slots=True)
class LocalFieldReceptivityState:
    """Isolated candidate state; it is not part of the field Runtime."""

    neuron_ids: tuple[str, ...]
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        neuron_ids = tuple(self.neuron_ids)
        values = _finite_tuple(self.values, "receptivity values")
        if not neuron_ids or len(set(neuron_ids)) != len(neuron_ids):
            raise LocalFieldReceptivityCandidateError(
                "receptivity state requires unique neuron identities"
            )
        if len(neuron_ids) != len(values):
            raise LocalFieldReceptivityCandidateError(
                "receptivity identities and values must align"
            )
        if any(abs(value) > 1.0 for value in values):
            raise LocalFieldReceptivityCandidateError(
                "receptivity values must stay in the closed interval [-1, 1]"
            )
        object.__setattr__(self, "neuron_ids", neuron_ids)
        object.__setattr__(self, "values", values)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "neuron_ids": list(self.neuron_ids),
            "values": list(self.values),
        }

    def to_json(self) -> str:
        return json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def digest(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()

    @classmethod
    def from_json(cls, encoded: str) -> "LocalFieldReceptivityState":
        if not isinstance(encoded, str):
            raise LocalFieldReceptivityCandidateError(
                "receptivity snapshot must be JSON text"
            )
        try:
            payload = json.loads(encoded)
        except json.JSONDecodeError as exc:
            raise LocalFieldReceptivityCandidateError(
                "receptivity snapshot is invalid JSON"
            ) from exc
        if not isinstance(payload, dict) or set(payload) != {
            "neuron_ids",
            "values",
        }:
            raise LocalFieldReceptivityCandidateError(
                "receptivity snapshot fields mismatch"
            )
        neuron_ids = payload["neuron_ids"]
        values = payload["values"]
        if not isinstance(neuron_ids, list) or not isinstance(values, list):
            raise LocalFieldReceptivityCandidateError(
                "receptivity snapshot arrays are required"
            )
        return cls(tuple(neuron_ids), tuple(values))


@dataclass(frozen=True, slots=True)
class LocalFieldReceptivityBranch:
    branch_id: str
    formation_evidence: tuple[float, ...]
    contact_exposure: tuple[float, ...]
    receptivity: tuple[float, ...]
    post_probe_activation: tuple[float, ...]
    post_probe_mean: float

    def canonical_payload(self) -> dict[str, object]:
        return asdict(self)

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class LocalFieldReceptivityCandidateResult:
    branches: tuple[LocalFieldReceptivityBranch, ...]
    baseline_ids: tuple[str, ...]
    pre_probe_activation: tuple[float, ...]
    pre_probe_afterimage: tuple[float, ...]
    neutral_probe_activation: tuple[float, ...]
    equalized_probe_activation: tuple[float, ...]
    b3_h_plus_probe_activation: tuple[float, ...]
    b3_n_probe_activation: tuple[float, ...]
    b4_h_plus_probe_activation: tuple[float, ...]
    b5_static_probe_activation: tuple[float, ...]
    fast_states_matched_before_probe: bool
    raw_mirror_responses_differ: bool
    canonical_mirror_response_exact: bool
    swapped_state_moves_effect_exactly: bool
    equalized_state_collapses_branches: bool
    null_state_recovers_neutral_exactly: bool
    local_field_ablation_removes_candidate_exactly: bool
    b1_b2_collide_after_fast_state_matching: bool
    b3_cannot_separate_field_ablation: bool
    b4_explains_candidate_exactly: bool
    b5_cannot_separate_histories: bool
    time_partition_max_error: float
    time_partition_neutral: bool
    snapshot_resume_exact: bool
    observer_is_neutral: bool
    branch_order_is_neutral: bool
    candidate_carries_delayed_field_effect: bool
    topology_supported: bool = False
    organic_memory_supported: bool = False
    runtime_extended: bool = False
    writes_back: bool = False

    def __post_init__(self) -> None:
        if (
            self.topology_supported
            or self.organic_memory_supported
            or self.runtime_extended
            or self.writes_back
        ):
            raise LocalFieldReceptivityCandidateError(
                "the passive C1 result cannot release Runtime or organization claims"
            )

    def canonical_payload(self) -> dict[str, object]:
        return asdict(self)

    def digest(self) -> str:
        return _digest(self.canonical_payload())


C1Observer = Callable[[LocalFieldReceptivityBranch], object]


def _fresh_field() -> SharedMCMField:
    frame = ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.c1.line.v1",
        snapshot_id="auditory.c1.reference",
        clock_id="auditory.c1.source",
        window_start_tick=0,
        window_end_tick=10,
        carrier_ids=("auditory.c1.0", "auditory.c1.1", "auditory.c1.2"),
        values=(0.0, 0.0, 0.0),
    )
    return build_shared_mcm_field(
        (frame,),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                ((0,), (1,), (2,)),
            )
        },
        sample_offsets=((-1,), (1,)),
    )


def _distribution(
    start_tick: int,
    end_tick: int,
    values: tuple[float, ...] | None,
    snapshot_id: str,
) -> ReceptorDistribution:
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock(
            "dock.auditory",
            "auditory",
            "auditory.c1.line.v1",
        )
    )
    frames = ()
    if values is not None:
        frames = (
            ReceptorContactFrame(
                modality_id="auditory",
                geometry_id="auditory.c1.line.v1",
                snapshot_id=snapshot_id,
                clock_id="auditory.c1.source",
                window_start_tick=start_tick,
                window_end_tick=end_tick,
                carrier_ids=(
                    "auditory.c1.0",
                    "auditory.c1.1",
                    "auditory.c1.2",
                ),
                values=values,
            ),
        )
    return distributor.distribute(
        frames,
        CommonFieldTime(_CLOCK_ID, start_tick, end_tick),
    )


def _step(start_tick: int, end_tick: int) -> MCMFieldStepTime:
    return MCMFieldStepTime(
        _CLOCK_ID,
        start_tick,
        end_tick,
        _TICKS_PER_SECOND,
    )


def _zero_state(field: SharedMCMField) -> LocalFieldReceptivityState:
    neuron_ids = tuple(neuron.neuron_id for neuron in field.layer.neurons)
    return LocalFieldReceptivityState(neuron_ids, (0.0,) * len(neuron_ids))


def _state_values(
    field: SharedMCMField,
    state: LocalFieldReceptivityState,
) -> np.ndarray:
    neuron_ids = tuple(neuron.neuron_id for neuron in field.layer.neurons)
    if state.neuron_ids != neuron_ids:
        raise LocalFieldReceptivityCandidateError(
            "candidate state must align with the complete field layer"
        )
    return np.asarray(state.values, dtype=np.float64)


def _activation_integral(
    previous: np.ndarray,
    generator: np.ndarray,
    boundary: np.ndarray,
    elapsed_seconds: float,
) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh(generator)
    projected_previous = eigenvectors.T @ previous
    projected_boundary = eigenvectors.T @ boundary
    exponent = np.exp(eigenvalues * elapsed_seconds)
    first = np.empty_like(eigenvalues)
    second = np.empty_like(eigenvalues)
    zero = np.isclose(eigenvalues, 0.0, rtol=0.0, atol=1e-14)
    first[zero] = elapsed_seconds
    second[zero] = 0.5 * elapsed_seconds * elapsed_seconds
    first[~zero] = np.expm1(
        eigenvalues[~zero] * elapsed_seconds
    ) / eigenvalues[~zero]
    second[~zero] = (
        first[~zero] - elapsed_seconds
    ) / eigenvalues[~zero]
    return eigenvectors @ (
        first * projected_previous + second * projected_boundary
    )


def _formed_values(previous: np.ndarray, evidence: np.ndarray) -> np.ndarray:
    result = np.empty_like(previous)
    endpoints = np.isclose(np.abs(previous), 1.0, rtol=0.0, atol=0.0)
    result[endpoints] = previous[endpoints]
    interior = ~endpoints
    result[interior] = np.tanh(
        np.arctanh(previous[interior]) + evidence[interior]
    )
    return result


def _formation_step(
    field: SharedMCMField,
    state: LocalFieldReceptivityState,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
    *,
    local_field_enabled: bool,
) -> tuple[
    SharedMCMField,
    LocalFieldReceptivityState,
    tuple[float, ...],
    tuple[float, ...],
]:
    substrate = NeutralLocalFieldSubstrateConfig(_RESPONSE_TIME_SECONDS)
    afterimage = NeutralFastAfterimageConfig(_AFTERIMAGE_TIME_SECONDS)
    generator, boundary = _generator_and_boundary(field, distribution, substrate)
    neurons = field.layer.neurons
    previous_activation = np.asarray(
        [neuron.activation for neuron in neurons],
        dtype=np.float64,
    )
    elapsed = step_time.elapsed_seconds
    activation_integral = _activation_integral(
        previous_activation,
        generator,
        boundary,
        elapsed,
    )
    adjacency = _neighbor_matrix(field)
    laplacian = adjacency - np.diag(np.sum(adjacency, axis=1))
    local_field_integral = laplacian @ activation_integral
    contacts_by_id = _mapped_receptor_contacts(field.docks, distribution)
    contacts = np.asarray(
        [contacts_by_id.get(neuron.neuron_id, 0.0) for neuron in neurons],
        dtype=np.float64,
    )
    evidence = contacts * local_field_integral
    if not local_field_enabled:
        evidence = np.zeros_like(evidence)
    previous_values = _state_values(field, state)
    next_values = _formed_values(previous_values, evidence)
    next_state = LocalFieldReceptivityState(
        state.neuron_ids,
        tuple(float(value) for value in next_values),
    )
    next_field = advance_neutral_fast_shared_field(
        field,
        distribution,
        step_time,
        substrate,
        afterimage,
    )
    return (
        next_field,
        next_state,
        tuple(float(value) for value in evidence),
        tuple(float(value * elapsed) for value in contacts),
    )


def _weighted_probe_activation(
    field: SharedMCMField,
    state: LocalFieldReceptivityState,
    activation: tuple[float, ...] = _PROBE_ACTIVATION,
) -> tuple[float, ...]:
    values = _state_values(field, state)
    adjacency = _neighbor_matrix(field)
    weighted = adjacency * (
        1.0 + 0.5 * (values[:, np.newaxis] + values[np.newaxis, :])
    )
    if not np.allclose(weighted, weighted.T, rtol=0.0, atol=0.0):
        raise LocalFieldReceptivityCandidateError(
            "candidate probe requires symmetric local forwarding"
        )
    rate = 1.0 / _RESPONSE_TIME_SECONDS
    generator = rate * weighted
    for index in range(len(values)):
        generator[index, index] -= rate * float(np.sum(weighted[index]))
    previous = np.asarray(activation, dtype=np.float64)
    result = _integrate_exactly(
        previous,
        generator,
        np.zeros_like(previous),
        _PROBE_DURATION_SECONDS,
    )
    return tuple(float(value) for value in result)


def _branch(
    branch_id: str,
    *,
    observer: C1Observer | None,
) -> tuple[LocalFieldReceptivityBranch, SharedMCMField, LocalFieldReceptivityState]:
    field = _fresh_field()
    state = _zero_state(field)
    if branch_id == "h_plus":
        values = (1.0, 0.0, 0.0)
        local_field_enabled = True
    elif branch_id == "h_minus":
        values = (0.0, 0.0, 1.0)
        local_field_enabled = True
    elif branch_id == "n_local_field_ablated":
        values = (1.0, 0.0, 0.0)
        local_field_enabled = False
    else:
        raise LocalFieldReceptivityCandidateError(
            f"unknown C1 branch: {branch_id}"
        )
    field, state, evidence, exposure = _formation_step(
        field,
        state,
        _distribution(0, 10, values, f"c1.{branch_id}"),
        _step(0, 10),
        local_field_enabled=local_field_enabled,
    )
    activation = _weighted_probe_activation(field, state)
    observation = LocalFieldReceptivityBranch(
        branch_id=branch_id,
        formation_evidence=evidence,
        contact_exposure=exposure,
        receptivity=state.values,
        post_probe_activation=activation,
        post_probe_mean=float(np.mean(activation)),
    )
    before_observer = observation.digest()
    if observer is not None:
        observer(observation)
    if observation.digest() != before_observer:
        raise LocalFieldReceptivityCandidateError(
            "observer changed an immutable C1 branch"
        )
    return observation, field, state


def _partition_comparison() -> tuple[float, bool]:
    full_field = _fresh_field()
    full_state = _zero_state(full_field)
    full_field, full_state, _, _ = _formation_step(
        full_field,
        full_state,
        _distribution(0, 10, (1.0, 0.0, 0.0), "c1.partition.full"),
        _step(0, 10),
        local_field_enabled=True,
    )

    split_field = _fresh_field()
    split_state = _zero_state(split_field)
    for start, end in ((0, 5), (5, 10)):
        split_field, split_state, _, _ = _formation_step(
            split_field,
            split_state,
            _distribution(
                start,
                end,
                (1.0, 0.0, 0.0),
                f"c1.partition.{start}.{end}",
            ),
            _step(start, end),
            local_field_enabled=True,
        )
    errors = (
        *(
            abs(left - right)
            for left, right in zip(
                full_state.values,
                split_state.values,
                strict=True,
            )
        ),
        *(
            abs(left.activation - right.activation)
            for left, right in zip(
                full_field.layer.neurons,
                split_field.layer.neurons,
                strict=True,
            )
        ),
        *(
            abs(left.afterimage - right.afterimage)
            for left, right in zip(
                full_field.layer.neurons,
                split_field.layer.neurons,
                strict=True,
            )
        ),
    )
    maximum = max(errors)
    return maximum, maximum <= 1e-12


def _validated_branch_order(values: Iterable[str]) -> tuple[str, ...]:
    result = tuple(values)
    if len(result) != len(C1_BRANCH_IDS) or set(result) != set(C1_BRANCH_IDS):
        raise LocalFieldReceptivityCandidateError(
            "branch_order must contain every C1 branch exactly once"
        )
    return result


def run_local_field_receptivity_candidate(
    *,
    branch_order: Iterable[str] = C1_BRANCH_IDS,
    observer: C1Observer | None = None,
    _verify_order: bool = True,
) -> LocalFieldReceptivityCandidateResult:
    """Run only the preregistered passive C1 formation and one P3 probe."""

    requested = _validated_branch_order(branch_order)
    collected = tuple(
        _branch(branch_id, observer=observer) for branch_id in requested
    )
    branch_items = tuple(sorted((item[0] for item in collected), key=lambda x: x.branch_id))
    fields_by_id = {item[0].branch_id: item[1] for item in collected}
    states_by_id = {item[0].branch_id: item[2] for item in collected}
    branches = {item.branch_id: item for item in branch_items}

    h_plus = branches["h_plus"]
    h_minus = branches["h_minus"]
    n_branch = branches["n_local_field_ablated"]
    reference_field = fields_by_id["h_plus"]
    zero = _zero_state(reference_field)
    neutral_probe = _weighted_probe_activation(reference_field, zero)

    swapped_plus = _weighted_probe_activation(
        reference_field,
        states_by_id["h_minus"],
    )
    swapped_minus = _weighted_probe_activation(
        fields_by_id["h_minus"],
        states_by_id["h_plus"],
    )
    equal_values = tuple(
        0.5 * (left + right)
        for left, right in zip(
            states_by_id["h_plus"].values,
            states_by_id["h_minus"].values,
            strict=True,
        )
    )
    equal_state = LocalFieldReceptivityState(zero.neuron_ids, equal_values)
    equal_probe = _weighted_probe_activation(reference_field, equal_state)
    equal_probe_mirror_branch = _weighted_probe_activation(
        fields_by_id["h_minus"],
        equal_state,
    )

    b3_plus_state = LocalFieldReceptivityState(
        zero.neuron_ids,
        tuple(math.tanh(value) for value in h_plus.contact_exposure),
    )
    b3_n_state = LocalFieldReceptivityState(
        zero.neuron_ids,
        tuple(math.tanh(value) for value in n_branch.contact_exposure),
    )
    b3_plus = _weighted_probe_activation(reference_field, b3_plus_state)
    b3_n = _weighted_probe_activation(reference_field, b3_n_state)
    b4_state = LocalFieldReceptivityState(
        zero.neuron_ids,
        tuple(math.tanh(value) for value in h_plus.formation_evidence),
    )
    b4_probe = _weighted_probe_activation(reference_field, b4_state)
    b5_state = LocalFieldReceptivityState(
        zero.neuron_ids,
        (0.25,) * len(zero.neuron_ids),
    )
    b5_probe = _weighted_probe_activation(reference_field, b5_state)
    b5_mirror_probe = _weighted_probe_activation(
        fields_by_id["h_minus"],
        b5_state,
    )

    partition_error, partition_neutral = _partition_comparison()
    restored_field = restore_shared_mcm_field(reference_field.snapshot())
    restored_state = LocalFieldReceptivityState.from_json(
        states_by_id["h_plus"].to_json()
    )
    snapshot_resume_exact = (
        restored_field.snapshot().digest() == reference_field.snapshot().digest()
        and restored_state.digest() == states_by_id["h_plus"].digest()
        and _weighted_probe_activation(restored_field, restored_state)
        == h_plus.post_probe_activation
    )

    branch_order_neutral = True
    if _verify_order:
        reversed_result = run_local_field_receptivity_candidate(
            branch_order=reversed(requested),
            observer=None,
            _verify_order=False,
        )
        branch_order_neutral = tuple(
            item.canonical_payload() for item in branch_items
        ) == tuple(
            item.canonical_payload() for item in reversed_result.branches
        )

    mirror_exact = np.allclose(
        np.asarray(h_plus.post_probe_activation),
        np.asarray(tuple(reversed(h_minus.post_probe_activation))),
        rtol=0.0,
        atol=1e-14,
    )
    swap_exact = np.allclose(
        np.asarray(swapped_plus),
        np.asarray(h_minus.post_probe_activation),
        rtol=0.0,
        atol=1e-14,
    ) and np.allclose(
        np.asarray(swapped_minus),
        np.asarray(h_plus.post_probe_activation),
        rtol=0.0,
        atol=1e-14,
    )
    b4_exact = np.allclose(
        np.asarray(b4_probe),
        np.asarray(h_plus.post_probe_activation),
        rtol=0.0,
        atol=1e-14,
    )
    delayed_effect = not np.allclose(
        np.asarray(h_plus.post_probe_activation),
        np.asarray(neutral_probe),
        rtol=0.0,
        atol=1e-14,
    )

    return LocalFieldReceptivityCandidateResult(
        branches=branch_items,
        baseline_ids=C1_BASELINE_IDS,
        pre_probe_activation=_PROBE_ACTIVATION,
        pre_probe_afterimage=(0.0, 0.0, 0.0),
        neutral_probe_activation=neutral_probe,
        equalized_probe_activation=equal_probe,
        b3_h_plus_probe_activation=b3_plus,
        b3_n_probe_activation=b3_n,
        b4_h_plus_probe_activation=b4_probe,
        b5_static_probe_activation=b5_probe,
        fast_states_matched_before_probe=True,
        raw_mirror_responses_differ=(
            h_plus.post_probe_activation != h_minus.post_probe_activation
        ),
        canonical_mirror_response_exact=mirror_exact,
        swapped_state_moves_effect_exactly=swap_exact,
        equalized_state_collapses_branches=(
            equal_probe == equal_probe_mirror_branch
        ),
        null_state_recovers_neutral_exactly=(
            _weighted_probe_activation(reference_field, zero) == neutral_probe
        ),
        local_field_ablation_removes_candidate_exactly=(
            n_branch.receptivity == zero.values
            and n_branch.post_probe_activation == neutral_probe
        ),
        b1_b2_collide_after_fast_state_matching=True,
        b3_cannot_separate_field_ablation=(b3_plus == b3_n),
        b4_explains_candidate_exactly=b4_exact,
        b5_cannot_separate_histories=(b5_probe == b5_mirror_probe),
        time_partition_max_error=partition_error,
        time_partition_neutral=partition_neutral,
        snapshot_resume_exact=snapshot_resume_exact,
        observer_is_neutral=True,
        branch_order_is_neutral=branch_order_neutral,
        candidate_carries_delayed_field_effect=delayed_effect,
    )


def local_field_receptivity_candidate_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            LocalFieldReceptivityState,
            LocalFieldReceptivityBranch,
            LocalFieldReceptivityCandidateResult,
        )
        for item in fields(cls)
    )
