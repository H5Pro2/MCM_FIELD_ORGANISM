"""Private model-neutral helpers for one atomic local-state field composition."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from typing import Callable

from .field_step_time import MCMFieldStepTime
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import SharedMCMField
from .transient_neuron_input import TransientNeuronInputSet


_SyncAdvance = Callable[
    [
        SharedMCMField,
        ReceptorDistribution,
        MCMFieldStepTime,
        NeutralLocalFieldSubstrateConfig,
        NeutralFastAfterimageConfig,
        NeutralFieldDissipationConfig | None,
    ],
    SharedMCMField,
]
_TransientAdvance = Callable[
    [
        SharedMCMField,
        ReceptorDistribution,
        TransientNeuronInputSet,
        NeutralLocalFieldSubstrateConfig,
        NeutralFastAfterimageConfig,
        NeutralFieldDissipationConfig | None,
    ],
    SharedMCMField,
]


def canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def field_payload(field: SharedMCMField) -> dict[str, object]:
    return {
        "layer_digest": field.layer.digest(),
        "docks": [
            {
                "dock_id": dock.dock_id,
                "modality_id": dock.dock_map.modality_id,
                "receptor_geometry_id": dock.dock_map.receptor_geometry_id,
                "pairs": [list(pair) for pair in dock.dock_map.pairs],
            }
            for dock in field.docks
        ],
        "last_distribution_digest": (
            None
            if field.last_distribution is None
            else field.last_distribution.digest()
        ),
        "substrate_present": field.substrate is not None,
        "development_present": field.development is not None,
    }


def field_digest(field: SharedMCMField) -> str:
    return canonical_digest(field_payload(field))


def geometry_digest(field: SharedMCMField) -> str:
    return canonical_digest(
        {
            "field_id": field.field_id,
            "geometry_id": field.geometry_id,
            "layer_id": field.layer.layer_id,
            "nodes": [
                {
                    "neuron_id": neuron.neuron_id,
                    "position": list(neuron.position),
                    "modality_id": neuron.modality_id,
                }
                for neuron in field.layer.neurons
            ],
            "sample_offsets": [list(item) for item in field.layer.sample_offsets],
            "periodic_axes": [
                item.canonical_payload() for item in field.layer.periodic_axes
            ],
        }
    )


def interval_payload(
    interval_input: MCMFieldStepTime | TransientNeuronInputSet,
) -> dict[str, object]:
    step = (
        interval_input
        if isinstance(interval_input, MCMFieldStepTime)
        else interval_input.step_time
    )
    payload: dict[str, object] = {
        "kind": "sync" if isinstance(interval_input, MCMFieldStepTime) else "transient",
        "step_time": {
            "clock_id": step.clock_id,
            "start_tick": step.start_tick,
            "end_tick": step.end_tick,
            "ticks_per_second": step.ticks_per_second,
        },
    }
    if isinstance(interval_input, TransientNeuronInputSet):
        payload["neuron_inputs"] = [
            {
                "neuron_id": item.neuron_id,
                "dock_id": item.dock_id,
                "carrier_id": item.carrier_id,
                "contacts": [
                    {
                        "snapshot_id": contact.snapshot_id,
                        "source_clock_id": contact.source_clock_id,
                        "source_window_start_tick": contact.source_window_start_tick,
                        "source_window_end_tick": contact.source_window_end_tick,
                        "read_clock_id": contact.organism_read_time.clock_id,
                        "read_start_tick": contact.organism_read_time.window_start_tick,
                        "read_end_tick": contact.organism_read_time.window_end_tick,
                        "value": contact.value,
                    }
                    for contact in item.contacts
                ],
            }
            for item in interval_input.neuron_inputs
        ]
    return payload


def interval_matches(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    interval_input: MCMFieldStepTime | TransientNeuronInputSet,
) -> bool:
    step = (
        interval_input
        if isinstance(interval_input, MCMFieldStepTime)
        else interval_input.step_time
    )
    current = distribution.field_time
    if (
        step.clock_id != current.clock_id
        or step.start_tick != current.window_start_tick
        or step.end_tick != current.window_end_tick
    ):
        return False
    if isinstance(interval_input, TransientNeuronInputSet):
        if distribution.contacts:
            return False
        actual = {item.neuron_id for item in interval_input.neuron_inputs}
        if actual != set(field.layer.docked_neuron_ids):
            return False
    return True


def advance_fast_proposal(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    interval_input: MCMFieldStepTime | TransientNeuronInputSet,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None,
    sync_advance: _SyncAdvance,
    transient_advance: _TransientAdvance,
) -> SharedMCMField:
    if isinstance(interval_input, MCMFieldStepTime):
        return sync_advance(
            field,
            distribution,
            interval_input,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
    return transient_advance(
        field,
        distribution,
        interval_input,
        substrate_config,
        afterimage_config,
        dissipation_config,
    )


def fast_proposal_valid(
    before: SharedMCMField,
    proposal: object,
    distribution: ReceptorDistribution,
) -> bool:
    if not isinstance(proposal, SharedMCMField):
        return False
    if proposal.substrate is not None or proposal.development is not None:
        return False
    if proposal.layer.tick != before.layer.tick + 1:
        return False
    if proposal.last_distribution != distribution:
        return False
    if proposal.docks != before.docks:
        return False
    before_nodes = tuple(
        (item.neuron_id, item.position, item.field_id, item.geometry_id)
        for item in before.layer.neurons
    )
    proposal_nodes = tuple(
        (item.neuron_id, item.position, item.field_id, item.geometry_id)
        for item in proposal.layer.neurons
    )
    return before_nodes == proposal_nodes


def materialize_replace_s(
    proposal: SharedMCMField,
    output: tuple[float, ...],
) -> SharedMCMField:
    neurons = tuple(
        replace(neuron, activation=value)
        for neuron, value in zip(proposal.layer.neurons, output, strict=True)
    )
    return SharedMCMField(
        replace(proposal.layer, neurons=neurons),
        proposal.docks,
        proposal.last_distribution,
    )


def final_identity_valid(
    proposal: SharedMCMField,
    final: object,
    output: tuple[float, ...],
) -> bool:
    if not isinstance(final, SharedMCMField):
        return False
    if final.substrate is not None or final.development is not None:
        return False
    if final.docks != proposal.docks or final.last_distribution != proposal.last_distribution:
        return False
    if final.layer.layer_id != proposal.layer.layer_id:
        return False
    if final.layer.sample_offsets != proposal.layer.sample_offsets:
        return False
    if final.layer.periodic_axes != proposal.layer.periodic_axes:
        return False
    if len(final.layer.neurons) != len(proposal.layer.neurons):
        return False
    for proposed, completed, expected_s in zip(
        proposal.layer.neurons, final.layer.neurons, output, strict=True
    ):
        if completed.activation != expected_s:
            return False
        if replace(completed, activation=proposed.activation) != proposed:
            return False
    return True


def field_time_advance_count(before: SharedMCMField, final: SharedMCMField) -> int:
    return final.layer.tick - before.layer.tick
