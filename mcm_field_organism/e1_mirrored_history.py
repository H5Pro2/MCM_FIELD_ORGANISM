"""Controlled eight-contact mirrored E1 history producer."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import math

from .e1_coupled_fast_field import (
    E1CoupledFastFieldError,
    advance_e1_coupled_fast_shared_field,
)
from .e1_local_edge_plasticity import (
    E1LocalEdgePlasticityError,
    E1LocalEdgePlasticityState,
    validate_e1_state_for_layer,
)
from .field_step_time import MCMFieldStepTime
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import (
    DistributedReceptorContact,
    ReceptorDistribution,
)
from .shared_mcm_field import SharedMCMField


class E1MirroredHistoryError(ValueError):
    """Raised when the fixed mirrored E1 history corridor is invalid."""


E1_MIRRORED_HISTORY_INTERVALS = 8
E1_MIRRORED_HISTORY_TICKS_PER_INTERVAL = 10
E1_MIRRORED_HISTORY_TICKS_PER_SECOND = 10.0
_LEFT_CONTACT = (1.0, 0.0, 0.0)
_RIGHT_CONTACT = tuple(reversed(_LEFT_CONTACT))


@dataclass(frozen=True, slots=True)
class E1MirroredHistoryResult:
    """Two completed mirrored histories without any subsequent probe."""

    left_field: SharedMCMField
    right_field: SharedMCMField
    left_e1_state: E1LocalEdgePlasticityState
    right_e1_state: E1LocalEdgePlasticityState
    left_contact_energy: float
    right_contact_energy: float
    total_binding_difference: float
    maximum_mirror_binding_error: float

    def __post_init__(self) -> None:
        if not isinstance(self.left_field, SharedMCMField) or not isinstance(
            self.right_field, SharedMCMField
        ):
            raise E1MirroredHistoryError(
                "mirrored history result requires two completed fields"
            )
        if not isinstance(
            self.left_e1_state, E1LocalEdgePlasticityState
        ) or not isinstance(self.right_e1_state, E1LocalEdgePlasticityState):
            raise E1MirroredHistoryError(
                "mirrored history result requires two completed E1 states"
            )
        for role in (
            "left_contact_energy",
            "right_contact_energy",
            "total_binding_difference",
            "maximum_mirror_binding_error",
        ):
            value = getattr(self, role)
            if not math.isfinite(value) or value < 0.0:
                raise E1MirroredHistoryError(
                    f"{role} must be finite and nonnegative"
                )


def _three_node_corridor(field: SharedMCMField) -> tuple[str, ...]:
    if not isinstance(field, SharedMCMField):
        raise E1MirroredHistoryError(
            "mirrored history requires one shared initial field"
        )
    ordered = tuple(sorted(field.layer.neurons, key=lambda item: item.position))
    if len(ordered) != 3 or tuple(item.position for item in ordered) != (
        (0,),
        (1,),
        (2,),
    ):
        raise E1MirroredHistoryError(
            "first mirrored history corridor requires positions 0, 1, and 2"
        )
    if len(field.docks) != 1:
        raise E1MirroredHistoryError(
            "first mirrored history corridor requires one receptor dock"
        )
    dock_ids = set(field.docks[0].dock_map.neuron_ids)
    neuron_ids = tuple(item.neuron_id for item in ordered)
    if dock_ids != set(neuron_ids):
        raise E1MirroredHistoryError(
            "mirrored history dock must cover all three field neurons"
        )
    return neuron_ids


def _distribution_for_contact(
    field: SharedMCMField,
    position_neuron_ids: tuple[str, ...],
    values: tuple[float, ...],
    arm: str,
    interval_index: int,
) -> tuple[ReceptorDistribution, MCMFieldStepTime]:
    dock = field.docks[0]
    value_by_neuron = dict(zip(position_neuron_ids, values, strict=True))
    carrier_ids = dock.dock_map.carrier_ids
    neuron_by_carrier = dict(dock.dock_map.pairs)
    frame_values = tuple(
        value_by_neuron[neuron_by_carrier[carrier_id]]
        for carrier_id in carrier_ids
    )
    start = interval_index * E1_MIRRORED_HISTORY_TICKS_PER_INTERVAL
    end = start + E1_MIRRORED_HISTORY_TICKS_PER_INTERVAL
    frame = ReceptorContactFrame(
        modality_id=dock.dock_map.modality_id,
        geometry_id=dock.dock_map.receptor_geometry_id,
        snapshot_id=f"e1.history.{arm}.{interval_index}",
        clock_id=f"e1.history.{arm}.source",
        window_start_tick=start,
        window_end_tick=end,
        carrier_ids=carrier_ids,
        values=frame_values,
    )
    distribution = ReceptorDistribution(
        CommonFieldTime("e1.history.organism", start, end),
        (DistributedReceptorContact(dock.dock_id, frame),),
    )
    step_time = MCMFieldStepTime(
        "e1.history.organism",
        start,
        end,
        E1_MIRRORED_HISTORY_TICKS_PER_SECOND,
    )
    return distribution, step_time


def _mirror_edge_map(
    position_neuron_ids: tuple[str, ...],
) -> dict[tuple[str, str], tuple[str, str]]:
    mirrored_neuron = {
        position_neuron_ids[index]: position_neuron_ids[-1 - index]
        for index in range(len(position_neuron_ids))
    }
    result = {}
    for first, second in (
        (position_neuron_ids[0], position_neuron_ids[1]),
        (position_neuron_ids[1], position_neuron_ids[2]),
    ):
        mirrored = tuple(sorted((mirrored_neuron[first], mirrored_neuron[second])))
        result[tuple(sorted((first, second)))] = mirrored
    return result


def produce_e1_mirrored_histories(
    initial_field: SharedMCMField,
    initial_e1_state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
) -> E1MirroredHistoryResult:
    """Produce only the fixed left/right histories and their E1 end states."""

    position_neuron_ids = _three_node_corridor(initial_field)
    if not isinstance(initial_e1_state, E1LocalEdgePlasticityState):
        raise E1MirroredHistoryError(
            "mirrored history requires one initial E1 state"
        )
    try:
        validate_e1_state_for_layer(initial_field.layer, initial_e1_state)
    except E1LocalEdgePlasticityError as exc:
        raise E1MirroredHistoryError(str(exc)) from exc
    if any(item.binding != 0.0 for item in initial_e1_state.edge_bindings):
        raise E1MirroredHistoryError(
            "mirrored histories must begin with neutral E1 binding"
        )
    if not isinstance(substrate_config, NeutralLocalFieldSubstrateConfig):
        raise E1MirroredHistoryError(
            "mirrored history requires one substrate configuration"
        )
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise E1MirroredHistoryError(
            "mirrored history requires one afterimage configuration"
        )
    if dissipation_config is not None and not isinstance(
        dissipation_config, NeutralFieldDissipationConfig
    ):
        raise E1MirroredHistoryError(
            "mirrored history dissipation configuration is invalid"
        )

    left_field = copy.deepcopy(initial_field)
    right_field = copy.deepcopy(initial_field)
    left_state = copy.deepcopy(initial_e1_state)
    right_state = copy.deepcopy(initial_e1_state)
    left_energy = 0.0
    right_energy = 0.0
    try:
        for interval_index in range(E1_MIRRORED_HISTORY_INTERVALS):
            left_distribution, interval = _distribution_for_contact(
                left_field,
                position_neuron_ids,
                _LEFT_CONTACT,
                "left",
                interval_index,
            )
            right_distribution, right_interval = _distribution_for_contact(
                right_field,
                position_neuron_ids,
                _RIGHT_CONTACT,
                "right",
                interval_index,
            )
            left_result = advance_e1_coupled_fast_shared_field(
                left_field,
                left_state,
                left_distribution,
                interval,
                substrate_config,
                afterimage_config,
                dissipation_config,
                backreaction_enabled=True,
            )
            right_result = advance_e1_coupled_fast_shared_field(
                right_field,
                right_state,
                right_distribution,
                right_interval,
                substrate_config,
                afterimage_config,
                dissipation_config,
                backreaction_enabled=True,
            )
            left_field, left_state = left_result.field, left_result.e1_state
            right_field, right_state = right_result.field, right_result.e1_state
            left_energy += math.fsum(value * value for value in _LEFT_CONTACT)
            right_energy += math.fsum(value * value for value in _RIGHT_CONTACT)
    except E1CoupledFastFieldError as exc:
        raise E1MirroredHistoryError(str(exc)) from exc

    left_binding = {item.edge: item.binding for item in left_state.edge_bindings}
    right_binding = {item.edge: item.binding for item in right_state.edge_bindings}
    mirror_map = _mirror_edge_map(position_neuron_ids)
    mirror_error = max(
        abs(left_binding[edge] - right_binding[mirrored])
        for edge, mirrored in mirror_map.items()
    )
    total_difference = abs(
        math.fsum(left_binding.values()) - math.fsum(right_binding.values())
    )
    return E1MirroredHistoryResult(
        left_field=left_field,
        right_field=right_field,
        left_e1_state=left_state,
        right_e1_state=right_state,
        left_contact_energy=left_energy,
        right_contact_energy=right_energy,
        total_binding_difference=total_difference,
        maximum_mirror_binding_error=mirror_error,
    )
