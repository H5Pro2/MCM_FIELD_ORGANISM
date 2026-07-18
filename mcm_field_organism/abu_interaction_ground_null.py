"""Passive A-B-U ground-null matrix through the unchanged neutral runtime."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
import hashlib
import json
from typing import Iterable

from .field_step_time import MCMFieldStepTime
from .mcm_neuron_layer import MCMNeuronLayer
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
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
    build_shared_mcm_field,
    restore_shared_mcm_field,
)


class ABUInteractionGroundNullError(ValueError):
    """Raised when the ground run leaves the preregistered matrix."""


@dataclass(frozen=True, slots=True)
class ABUGroundBranch:
    branch_id: str
    pre_first_alignment_activation: tuple[float, ...]
    pre_first_alignment_afterimage: tuple[float, ...]
    pre_probe_alignment_activation: tuple[float, ...]
    pre_probe_alignment_afterimage: tuple[float, ...]
    probe_response: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class ABUSolutionComparison:
    challenge_id: str
    no_a_response: tuple[float, ...]
    prior_a_response: tuple[float, ...]
    response_max_error: float


@dataclass(frozen=True, slots=True)
class ABURebindingComparison:
    challenge_id: str
    no_a_then_b_response: tuple[float, ...]
    prior_a_then_b_response: tuple[float, ...]
    response_max_error: float


@dataclass(frozen=True, slots=True)
class ABUInteractionGroundNullResult:
    branches: tuple[ABUGroundBranch, ...]
    interaction_ab: tuple[float, ...]
    interaction_ub: tuple[float, ...]
    interaction_ab_max: float
    interaction_ub_max: float
    u_effect_at_b_before_alignment: float
    histories_distinct_before_alignment: bool
    probe_responses_equal_after_matching: bool
    neutral_baseline_rebuild_exact: bool
    solutions: tuple[ABUSolutionComparison, ...]
    rebindings: tuple[ABURebindingComparison, ...]
    coarse_fine_max_error: float
    reflection_max_error: float
    translation_max_error: float
    neuron_order_max_error: float
    branch_order_exact: bool
    snapshot_resume_exact: bool
    observer_writeback_performed: bool
    persistent_state_added: bool
    runtime_candidate_released: bool

    def canonical_payload(self) -> dict[str, object]:
        return {
            item.name: _canonical_value(getattr(self, item.name))
            for item in fields(self)
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


_CLOCK_ID = "organism.abu_ground_null"
_GEOMETRY_ID = "abu.line.v1"
_MODALITY_ID = "technical"
_DOCK_ID = "dock.technical"
_TICKS_PER_SECOND = 10
_SUBSTRATE = NeutralLocalFieldSubstrateConfig(1.0)
_AFTERIMAGE = NeutralFastAfterimageConfig(0.5)
_PRIMARY_BRANCH_IDS = (
    "Y00",
    "Y10",
    "Y01",
    "Y11",
    "Z00",
    "Z10",
    "Z01",
    "Z11",
)


def _canonical_value(value: object) -> object:
    if hasattr(value, "__dataclass_fields__"):
        return {
            item.name: _canonical_value(getattr(value, item.name))
            for item in fields(value)  # type: ignore[arg-type]
        }
    if isinstance(value, tuple):
        return [_canonical_value(item) for item in value]
    return value


def _frame(
    values: tuple[float, ...],
    *,
    start_tick: int,
    end_tick: int,
    snapshot_id: str,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=_MODALITY_ID,
        geometry_id=_GEOMETRY_ID,
        snapshot_id=snapshot_id.lower(),
        clock_id="technical.source",
        window_start_tick=start_tick,
        window_end_tick=end_tick,
        carrier_ids=tuple(
            f"technical.carrier.{index}" for index in range(len(values))
        ),
        values=values,
    )


def _new_field(width: int, *, reverse_neurons: bool = False) -> SharedMCMField:
    if width < 8:
        raise ABUInteractionGroundNullError("A-B-U world requires at least 8 positions")
    zero = (0.0,) * width
    reference = _frame(
        zero,
        start_tick=0,
        end_tick=_TICKS_PER_SECOND,
        snapshot_id="reference",
    )
    field = build_shared_mcm_field(
        (reference,),
        {
            _MODALITY_ID: ReceptorDockAnatomy(
                _MODALITY_ID,
                _DOCK_ID,
                tuple((index,) for index in range(width)),
            )
        },
        sample_offsets=((-1,), (1,)),
        geometry_id="organism.abu_ground_null.v1",
    )
    if not reverse_neurons:
        return field
    return SharedMCMField(
        layer=MCMNeuronLayer(
            layer_id=field.layer.layer_id,
            neurons=tuple(reversed(field.layer.neurons)),
            sample_offsets=field.layer.sample_offsets,
            periodic_axes=field.layer.periodic_axes,
            receptor_dock_ids=field.layer.docked_neuron_ids,
        ),
        docks=field.docks,
    )


def _distributor() -> ReceptorDistributor:
    result = ReceptorDistributor()
    result.attach(ReceptorDock(_DOCK_ID, _MODALITY_ID, _GEOMETRY_ID))
    return result


def _distribution(
    distributor: ReceptorDistributor,
    width: int,
    *,
    start_tick: int,
    end_tick: int,
    snapshot_id: str,
    values: tuple[float, ...] | None,
) -> ReceptorDistribution:
    time = CommonFieldTime(_CLOCK_ID, start_tick, end_tick)
    if values is None:
        return ReceptorDistribution(time, ())
    if len(values) != width:
        raise ABUInteractionGroundNullError("contact vector must match field width")
    return distributor.distribute(
        (
            _frame(
                values,
                start_tick=start_tick,
                end_tick=end_tick,
                snapshot_id=snapshot_id,
            ),
        ),
        time,
    )


def _advance(
    field: SharedMCMField,
    distributor: ReceptorDistributor,
    *,
    start_tick: int,
    end_tick: int,
    snapshot_id: str,
    values: tuple[float, ...] | None,
) -> SharedMCMField:
    distribution = _distribution(
        distributor,
        len(field.layer.neurons),
        start_tick=start_tick,
        end_tick=end_tick,
        snapshot_id=snapshot_id,
        values=values,
    )
    return advance_neutral_fast_shared_field(
        field,
        distribution,
        MCMFieldStepTime(
            _CLOCK_ID,
            start_tick,
            end_tick,
            float(_TICKS_PER_SECOND),
        ),
        _SUBSTRATE,
        _AFTERIMAGE,
    )


def _run_seconds(
    field: SharedMCMField,
    distributor: ReceptorDistributor,
    *,
    start_tick: int,
    seconds: int,
    values: tuple[float, ...] | None,
    label: str,
    parts_per_second: int,
) -> tuple[SharedMCMField, int]:
    if parts_per_second not in (1, 10):
        raise ABUInteractionGroundNullError("ground run supports 1 or 10 parts/second")
    tick = start_tick
    part_ticks = _TICKS_PER_SECOND // parts_per_second
    for part in range(seconds * parts_per_second):
        end_tick = tick + part_ticks
        field = _advance(
            field,
            distributor,
            start_tick=tick,
            end_tick=end_tick,
            snapshot_id=f"{label}.{part}",
            values=values,
        )
        tick = end_tick
    return field, tick


def _contact(width: int, values: dict[int, float]) -> tuple[float, ...]:
    result = [0.0] * width
    for position, value in values.items():
        if position < 0 or position >= width:
            raise ABUInteractionGroundNullError("world block left the field geometry")
        result[position] = value
    return tuple(result)


def _run_block(
    field: SharedMCMField,
    distributor: ReceptorDistributor,
    pair: tuple[int, int] | None,
    *,
    start_tick: int,
    label: str,
    parts_per_second: int,
) -> tuple[SharedMCMField, int]:
    width = len(field.layer.neurons)
    stages: tuple[tuple[float, ...] | None, ...]
    if pair is None:
        stages = (None, None, None, None)
    else:
        p, q = pair
        stages = (
            _contact(width, {p: 1.0}),
            _contact(width, {p: 1.0, q: 1.0}),
            _contact(width, {q: 1.0}),
            None,
        )
    tick = start_tick
    for index, values in enumerate(stages):
        field, tick = _run_seconds(
            field,
            distributor,
            start_tick=tick,
            seconds=1,
            values=values,
            label=f"{label}.stage.{index}",
            parts_per_second=parts_per_second,
        )
    return field, tick


def _field_vectors(field: SharedMCMField) -> tuple[tuple[float, ...], tuple[float, ...]]:
    ordered = sorted(field.layer.neurons, key=lambda neuron: neuron.position)
    return (
        tuple(neuron.activation for neuron in ordered),
        tuple(neuron.afterimage for neuron in ordered),
    )


def _match_fast_state(
    field: SharedMCMField,
    activation: tuple[float, ...],
    afterimage: tuple[float, ...],
) -> SharedMCMField:
    by_position = {
        neuron.position: (activation[index], afterimage[index])
        for index, neuron in enumerate(sorted(field.layer.neurons, key=lambda item: item.position))
    }
    neurons = tuple(
        replace(
            neuron,
            activation=by_position[neuron.position][0],
            afterimage=by_position[neuron.position][1],
        )
        for neuron in field.layer.neurons
    )
    return SharedMCMField(
        layer=MCMNeuronLayer(
            layer_id=field.layer.layer_id,
            neurons=neurons,
            sample_offsets=field.layer.sample_offsets,
            periodic_axes=field.layer.periodic_axes,
            receptor_dock_ids=field.layer.docked_neuron_ids,
        ),
        docks=field.docks,
        last_distribution=field.last_distribution,
    )


def _probe_vector(width: int, shift: int, mirror: bool) -> tuple[float, ...]:
    values = _contact(width, {shift + 2: 1.0, shift + 3: -1.0})
    return tuple(reversed(values)) if mirror else values


def _pair(pair: tuple[int, int], width: int, shift: int, mirror: bool) -> tuple[int, int]:
    shifted = (pair[0] + shift, pair[1] + shift)
    if not mirror:
        return shifted
    return tuple(width - 1 - value for value in shifted)  # type: ignore[return-value]


def _probe(
    field: SharedMCMField,
    distributor: ReceptorDistributor,
    *,
    tick: int,
    shift: int,
    mirror: bool,
    parts_per_second: int,
) -> SharedMCMField:
    width = len(field.layer.neurons)
    field = _match_fast_state(
        field,
        _probe_vector(width, shift, mirror),
        (0.0,) * width,
    )
    part_count = 1 if parts_per_second == 1 else 5
    part_ticks = 5 // part_count
    for part in range(part_count):
        field = _advance(
            field,
            distributor,
            start_tick=tick,
            end_tick=tick + part_ticks,
            snapshot_id=f"probe.{part}",
            values=None,
        )
        tick += part_ticks
    return field


def _canonical_vector(
    values: tuple[float, ...],
    *,
    mirror: bool,
) -> tuple[float, ...]:
    return tuple(reversed(values)) if mirror else values


def _run_primary(
    *,
    parts_per_second: int = 1,
    mirror: bool = False,
    width: int = 8,
    shift: int = 0,
    reverse_neurons: bool = False,
    restore_after_phases: bool = False,
    branch_order: Iterable[str] = _PRIMARY_BRANCH_IDS,
) -> tuple[ABUGroundBranch, ...]:
    order = tuple(branch_order)
    if set(order) != set(_PRIMARY_BRANCH_IDS) or len(order) != len(_PRIMARY_BRANCH_IDS):
        raise ABUInteractionGroundNullError("primary branch order must be complete")
    pair_a = _pair((1, 2), width, shift, mirror)
    pair_b = _pair((2, 3), width, shift, mirror)
    pair_u = _pair((5, 6), width, shift, mirror)
    definitions = {
        "Y00": (None, None),
        "Y10": (pair_a, None),
        "Y01": (None, pair_b),
        "Y11": (pair_a, pair_b),
        "Z00": (None, None),
        "Z10": (pair_u, None),
        "Z01": (None, pair_b),
        "Z11": (pair_u, pair_b),
    }
    observations = []
    for branch_id in order:
        field = _new_field(width, reverse_neurons=reverse_neurons)
        distributor = _distributor()
        tick = 0
        first, second = definitions[branch_id]
        field, tick = _run_block(
            field,
            distributor,
            first,
            start_tick=tick,
            label=f"{branch_id}.first",
            parts_per_second=parts_per_second,
        )
        pre_first = _field_vectors(field)
        if restore_after_phases:
            field = restore_shared_mcm_field(field.snapshot())
        field = _match_fast_state(field, (0.0,) * width, (0.0,) * width)
        field, tick = _run_block(
            field,
            distributor,
            second,
            start_tick=tick,
            label=f"{branch_id}.second",
            parts_per_second=parts_per_second,
        )
        pre_probe = _field_vectors(field)
        if restore_after_phases:
            field = restore_shared_mcm_field(field.snapshot())
        field = _probe(
            field,
            distributor,
            tick=tick,
            shift=shift,
            mirror=mirror,
            parts_per_second=parts_per_second,
        )
        response = _canonical_vector(_field_vectors(field)[0], mirror=mirror)
        observations.append(
            ABUGroundBranch(
                branch_id=branch_id,
                pre_first_alignment_activation=_canonical_vector(pre_first[0], mirror=mirror),
                pre_first_alignment_afterimage=_canonical_vector(pre_first[1], mirror=mirror),
                pre_probe_alignment_activation=_canonical_vector(pre_probe[0], mirror=mirror),
                pre_probe_alignment_afterimage=_canonical_vector(pre_probe[1], mirror=mirror),
                probe_response=response,
            )
        )
    return tuple(sorted(observations, key=lambda item: item.branch_id))


def _interaction(
    by_id: dict[str, ABUGroundBranch],
    prefix: str,
) -> tuple[float, ...]:
    a00 = by_id[f"{prefix}00"].probe_response
    a10 = by_id[f"{prefix}10"].probe_response
    a01 = by_id[f"{prefix}01"].probe_response
    a11 = by_id[f"{prefix}11"].probe_response
    return tuple(
        (v11 - v10) - (v01 - v00)
        for v00, v10, v01, v11 in zip(a00, a10, a01, a11, strict=True)
    )


def _max_error(first: tuple[float, ...], second: tuple[float, ...]) -> float:
    return max((abs(left - right) for left, right in zip(first, second, strict=True)), default=0.0)


def _run_challenge(
    challenge_id: str,
    *,
    prior_a: bool,
    rebinding: bool,
) -> tuple[float, ...]:
    field = _new_field(8)
    distributor = _distributor()
    tick = 0
    field, tick = _run_block(
        field,
        distributor,
        (1, 2) if prior_a else None,
        start_tick=tick,
        label=f"{challenge_id}.history",
        parts_per_second=1,
    )
    if challenge_id == "D0":
        field, tick = _run_seconds(
            field,
            distributor,
            start_tick=tick,
            seconds=16,
            values=None,
            label="D0.absence",
            parts_per_second=1,
        )
    elif challenge_id == "D1":
        for repeat in range(2):
            field, tick = _run_block(
                field,
                distributor,
                (3, 4),
                start_tick=tick,
                label=f"D1.alternative.{repeat}",
                parts_per_second=1,
            )
    else:
        raise ABUInteractionGroundNullError("unknown solution challenge")
    field = _match_fast_state(field, (0.0,) * 8, (0.0,) * 8)
    if rebinding:
        field, tick = _run_block(
            field,
            distributor,
            (2, 3),
            start_tick=tick,
            label=f"{challenge_id}.rebinding",
            parts_per_second=1,
        )
    return _field_vectors(
        _probe(
            field,
            distributor,
            tick=tick,
            shift=0,
            mirror=False,
            parts_per_second=1,
        )
    )[0]


def _translated(values: tuple[float, ...], shift: int) -> tuple[float, ...]:
    width = len(values)
    return tuple(values[(index + shift) % width] for index in range(width))


def _solution_comparisons() -> tuple[ABUSolutionComparison, ...]:
    result = []
    for challenge in ("D0", "D1"):
        no_a = _run_challenge(challenge, prior_a=False, rebinding=False)
        prior_a = _run_challenge(challenge, prior_a=True, rebinding=False)
        result.append(
            ABUSolutionComparison(
                challenge_id=challenge,
                no_a_response=no_a,
                prior_a_response=prior_a,
                response_max_error=_max_error(no_a, prior_a),
            )
        )
    return tuple(result)


def _rebinding_comparisons() -> tuple[ABURebindingComparison, ...]:
    result = []
    for challenge in ("D0", "D1"):
        no_a = _run_challenge(challenge, prior_a=False, rebinding=True)
        prior_a = _run_challenge(challenge, prior_a=True, rebinding=True)
        result.append(
            ABURebindingComparison(
                challenge_id=challenge,
                no_a_then_b_response=no_a,
                prior_a_then_b_response=prior_a,
                response_max_error=_max_error(no_a, prior_a),
            )
        )
    return tuple(result)


def run_abu_interaction_ground_null() -> ABUInteractionGroundNullResult:
    """Execute only the preregistered current-runtime technical ground null."""

    branches = _run_primary()
    by_id = {item.branch_id: item for item in branches}
    interaction_ab = _interaction(by_id, "Y")
    interaction_ub = _interaction(by_id, "Z")
    u_effect = max(
        abs(
            by_id["Z10"].pre_first_alignment_activation[index]
            - by_id["Z00"].pre_first_alignment_activation[index]
        )
        for index in (2, 3)
    )

    solutions = _solution_comparisons()
    rebindings = _rebinding_comparisons()

    fine = _run_primary(parts_per_second=10)
    mirrored = _run_primary(mirror=True)
    reversed_neurons = _run_primary(reverse_neurons=True)
    reversed_branches = _run_primary(branch_order=reversed(_PRIMARY_BRANCH_IDS))
    resumed = _run_primary(restore_after_phases=True)
    base_wide = _run_primary(width=64, shift=16)
    shifted_wide = _run_primary(width=64, shift=32)

    fine_by_id = {item.branch_id: item for item in fine}
    mirrored_by_id = {item.branch_id: item for item in mirrored}
    reversed_neurons_by_id = {item.branch_id: item for item in reversed_neurons}
    base_wide_by_id = {item.branch_id: item for item in base_wide}
    shifted_wide_by_id = {item.branch_id: item for item in shifted_wide}
    coarse_fine_error = max(
        _max_error(item.probe_response, fine_by_id[item.branch_id].probe_response)
        for item in branches
    )
    reflection_error = max(
        _max_error(item.probe_response, mirrored_by_id[item.branch_id].probe_response)
        for item in branches
    )
    neuron_order_error = max(
        _max_error(item.probe_response, reversed_neurons_by_id[item.branch_id].probe_response)
        for item in branches
    )
    translation_error = max(
        _max_error(
            _translated(base_wide_by_id[branch_id].probe_response, 16),
            _translated(shifted_wide_by_id[branch_id].probe_response, 32),
        )
        for branch_id in _PRIMARY_BRANCH_IDS
    )

    rebuilt = _run_primary()
    return ABUInteractionGroundNullResult(
        branches=branches,
        interaction_ab=interaction_ab,
        interaction_ub=interaction_ub,
        interaction_ab_max=max(abs(value) for value in interaction_ab),
        interaction_ub_max=max(abs(value) for value in interaction_ub),
        u_effect_at_b_before_alignment=u_effect,
        histories_distinct_before_alignment=(
            by_id["Y10"].pre_first_alignment_activation
            != by_id["Y00"].pre_first_alignment_activation
            and by_id["Z10"].pre_first_alignment_activation
            != by_id["Z00"].pre_first_alignment_activation
        ),
        probe_responses_equal_after_matching=(
            len(
                {
                    (item.probe_response,)
                    for item in branches
                }
            )
            == 1
        ),
        neutral_baseline_rebuild_exact=(branches == rebuilt),
        solutions=solutions,
        rebindings=rebindings,
        coarse_fine_max_error=coarse_fine_error,
        reflection_max_error=reflection_error,
        translation_max_error=translation_error,
        neuron_order_max_error=neuron_order_error,
        branch_order_exact=(branches == reversed_branches),
        snapshot_resume_exact=(branches == resumed),
        observer_writeback_performed=False,
        persistent_state_added=False,
        runtime_candidate_released=False,
    )


def abu_interaction_ground_null_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            ABUGroundBranch,
            ABUSolutionComparison,
            ABURebindingComparison,
            ABUInteractionGroundNullResult,
        )
        for item in fields(contract)
    )
