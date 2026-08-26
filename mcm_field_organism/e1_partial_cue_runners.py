"""Private S1-CQ isolated E1, P0 and static-B1 cue runners."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import math

from .e1_frozen_history_probe import advance_fixed_e1_adapter_probe
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_mirrored_history import produce_e1_mirrored_histories
from .e1_partial_cue_contract import E1PartialCueContract
from .e1_partial_cue_execution import (
    E1PartialCueObservation,
    E1PartialCueWorldArms,
    S1_CP_CUE_IDS,
    build_e1_partial_cue_world_arms,
)
from .e1_weighted_field_adapter import (
    E1WeightedFieldAdapterResult,
    compute_e1_weighted_edge_rates,
)
from .field_step_time import MCMFieldStepTime
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import DistributedReceptorContact, ReceptorDistribution
from .shared_mcm_field import SharedMCMField


class E1PartialCueRunnerError(ValueError):
    """Raised when one isolated S1-CQ cue arm leaves its contract."""


@dataclass(frozen=True, slots=True)
class E1PartialCueRunnerInputs:
    world_arms: E1PartialCueWorldArms
    b1_static_h8_adapter: E1WeightedFieldAdapterResult

    def __post_init__(self) -> None:
        if not isinstance(self.world_arms, E1PartialCueWorldArms):
            raise E1PartialCueRunnerError("cue runner inputs require world arms")
        if not isinstance(self.b1_static_h8_adapter, E1WeightedFieldAdapterResult):
            raise E1PartialCueRunnerError("cue runner inputs require one H8 adapter")


def build_e1_partial_cue_runner_inputs(
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> E1PartialCueRunnerInputs:
    """Build state arms and one left-H8 adapter without applying a cue."""

    arms = build_e1_partial_cue_world_arms(
        initial_field, initial_state, substrate_config, afterimage_config
    )
    history = produce_e1_mirrored_histories(
        initial_field, initial_state, substrate_config, afterimage_config
    )
    adapter = compute_e1_weighted_edge_rates(
        initial_field.layer,
        history.left_e1_state,
        substrate_config,
        backreaction_enabled=True,
    )
    return E1PartialCueRunnerInputs(arms, adapter)


def _position_ids(field: SharedMCMField) -> tuple[str, ...]:
    ordered = tuple(sorted(field.layer.neurons, key=lambda item: item.position))
    if (
        len(ordered) != 3
        or tuple(item.position for item in ordered) != ((0,), (1,), (2,))
        or len(field.docks) != 1
        or field.layer.tick != 0
        or field.last_distribution is not None
        or field.substrate is not None
    ):
        raise E1PartialCueRunnerError("cue runner requires one fresh three-node field")
    return tuple(item.neuron_id for item in ordered)


def _cue_values(contract: E1PartialCueContract, cue_id: str) -> tuple[float, ...]:
    values = {
        "left-full": contract.left_full_cue,
        "right-full": contract.right_full_cue,
        "left-partial": contract.left_partial_cue,
        "right-partial": contract.right_partial_cue,
    }
    if cue_id not in values:
        raise E1PartialCueRunnerError("unknown cue identity")
    return values[cue_id]


def _distribution(
    field: SharedMCMField,
    position_ids: tuple[str, ...],
    values: tuple[float, ...],
    snapshot_id: str,
    start: int,
    end: int,
    ticks_per_second: float,
) -> tuple[ReceptorDistribution, MCMFieldStepTime]:
    dock = field.docks[0]
    value_by_neuron = dict(zip(position_ids, values, strict=True))
    neuron_by_carrier = dict(dock.dock_map.pairs)
    frame = ReceptorContactFrame(
        modality_id=dock.dock_map.modality_id,
        geometry_id=dock.dock_map.receptor_geometry_id,
        snapshot_id=snapshot_id,
        clock_id="s1-cq.cue.source",
        window_start_tick=start,
        window_end_tick=end,
        carrier_ids=dock.dock_map.carrier_ids,
        values=tuple(
            value_by_neuron[neuron_by_carrier[carrier_id]]
            for carrier_id in dock.dock_map.carrier_ids
        ),
    )
    return (
        ReceptorDistribution(
            CommonFieldTime("s1-cq.cue.organism", start, end),
            (DistributedReceptorContact(dock.dock_id, frame),),
        ),
        MCMFieldStepTime("s1-cq.cue.organism", start, end, ticks_per_second),
    )


def _advance_partition(
    initial_field: SharedMCMField,
    adapter: E1WeightedFieldAdapterResult | None,
    values: tuple[float, ...],
    parts: int,
    identity: str,
    contract: E1PartialCueContract,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> SharedMCMField:
    if parts not in (2, 4):
        raise E1PartialCueRunnerError("cue runner supports only n=2 and n=4")
    field = copy.deepcopy(initial_field)
    position_ids = _position_ids(field)
    total_ticks = int(contract.cue_interval_seconds * contract.ticks_per_second)
    width = total_ticks // parts
    for index in range(parts):
        start = index * width
        end = start + width
        distribution, step = _distribution(
            field,
            position_ids,
            values,
            f"s1-cq.{identity}.n{parts}.{index}",
            start,
            end,
            contract.ticks_per_second,
        )
        if adapter is None:
            field = advance_neutral_fast_shared_field(
                field, distribution, step, substrate_config, afterimage_config
            )
        else:
            field = advance_fixed_e1_adapter_probe(
                field,
                adapter,
                distribution,
                step,
                substrate_config,
                afterimage_config,
            )
    return field


def _values(field: SharedMCMField, role: str) -> tuple[float, float, float]:
    result = tuple(
        float(getattr(item, role))
        for item in sorted(field.layer.neurons, key=lambda item: item.position)
    )
    if len(result) != 3 or any(not math.isfinite(value) for value in result):
        raise E1PartialCueRunnerError("cue runner produced invalid field values")
    return result


def _difference(
    first: tuple[float, float, float], second: tuple[float, float, float]
) -> tuple[float, float, float]:
    return tuple(a - b for a, b in zip(first, second, strict=True))


def run_e1_partial_cue_observation(
    contract: E1PartialCueContract,
    initial_field: SharedMCMField,
    inputs: E1PartialCueRunnerInputs,
    model_id: str,
    history_id: str,
    cue_id: str,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> E1PartialCueObservation:
    """Run one isolated model/history/cue observation, never a full matrix."""

    if contract.execution_permitted or contract.executed:
        raise E1PartialCueRunnerError("S1-CQ requires the static S1-CO contract")
    _position_ids(initial_field)
    if model_id not in contract.model_arms or history_id not in contract.history_arms:
        raise E1PartialCueRunnerError("unknown cue runner arm")
    if cue_id not in S1_CP_CUE_IDS:
        raise E1PartialCueRunnerError("unknown cue identity")
    values = _cue_values(contract, cue_id)
    state_by_history = {
        "left-g4": inputs.world_arms.left_g4_state,
        "right-g4": inputs.world_arms.right_g4_state,
        "neutral": inputs.world_arms.neutral_state,
    }
    if model_id == "e1":
        adapter = compute_e1_weighted_edge_rates(
            initial_field.layer,
            state_by_history[history_id],
            substrate_config,
            backreaction_enabled=True,
        )
    elif model_id == "b1-static-h8":
        adapter = inputs.b1_static_h8_adapter
    else:
        adapter = None
    identity = f"{model_id}.{history_id}.{cue_id}"
    p0_n2 = _advance_partition(
        initial_field, None, values, 2, identity + ".p0", contract,
        substrate_config, afterimage_config,
    )
    p0_n4 = _advance_partition(
        initial_field, None, values, 4, identity + ".p0", contract,
        substrate_config, afterimage_config,
    )
    active_n2 = _advance_partition(
        initial_field, adapter, values, 2, identity, contract,
        substrate_config, afterimage_config,
    )
    active_n4 = _advance_partition(
        initial_field, adapter, values, 4, identity, contract,
        substrate_config, afterimage_config,
    )
    return E1PartialCueObservation(
        model_id,
        history_id,
        cue_id,
        _difference(_values(active_n4, "activation"), _values(p0_n4, "activation")),
        _difference(_values(active_n4, "afterimage"), _values(p0_n4, "afterimage")),
        _difference(_values(active_n2, "activation"), _values(p0_n2, "activation")),
        _difference(_values(active_n2, "afterimage"), _values(p0_n2, "afterimage")),
        active_n2.layer.tick == 2 and active_n4.layer.tick == 4,
        initial_field.layer.tick == 0
        and initial_field.last_distribution is None
        and state_by_history[history_id] in (
            inputs.world_arms.left_g4_state,
            inputs.world_arms.right_g4_state,
            inputs.world_arms.neutral_state,
        ),
    )
