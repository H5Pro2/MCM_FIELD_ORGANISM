"""Private S1-CW lazy inventory for all 72 amplitude observations."""

from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Callable, Mapping

from .e1_cue_amplitude_curve_contract import E1CueAmplitudeCurveContract
from .e1_cue_amplitude_curve_execution import (
    E1CueAmplitudeObservation,
    run_e1_cue_amplitude_observation,
)
from .e1_partial_cue_runners import E1PartialCueRunnerInputs
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .shared_mcm_field import SharedMCMField


class E1CueAmplitudeRunnerInventoryError(ValueError):
    """Raised when the S1-CW inventory leaves the S1-CU contract."""


E1CueAmplitudeRunner = Callable[[], E1CueAmplitudeObservation]
E1CueAmplitudeRunnerKey = tuple[str, str, str, float]


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _keys(
    contract: E1CueAmplitudeCurveContract,
) -> tuple[E1CueAmplitudeRunnerKey, ...]:
    return tuple(
        (model, history, side, amplitude)
        for model in contract.model_arms
        for history in contract.history_arms
        for side in contract.cue_sides
        for amplitude in contract.amplitudes
    )


def _state_payload(inputs: E1PartialCueRunnerInputs) -> dict[str, object]:
    arms = inputs.world_arms
    return {
        "left-g4": tuple(item.binding for item in arms.left_g4_state.edge_bindings),
        "right-g4": tuple(item.binding for item in arms.right_g4_state.edge_bindings),
        "neutral": tuple(item.binding for item in arms.neutral_state.edge_bindings),
        "edge_inventory_digest": arms.neutral_state.edge_inventory_digest,
        "b1-static-h8": tuple(
            (
                item.first_neuron_id,
                item.second_neuron_id,
                item.rate_per_second,
            )
            for item in inputs.b1_static_h8_adapter.edge_rates
        ),
    }


def build_e1_cue_amplitude_runner_inventory(
    contract: E1CueAmplitudeCurveContract,
    initial_field: SharedMCMField,
    inputs: E1PartialCueRunnerInputs,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> tuple[Mapping[E1CueAmplitudeRunnerKey, E1CueAmplitudeRunner], str]:
    """Bind all 72 amplitude roles without invoking a runner or compositor."""

    if not isinstance(contract, E1CueAmplitudeCurveContract):
        raise E1CueAmplitudeRunnerInventoryError("amplitude inventory needs its contract")
    if not isinstance(initial_field, SharedMCMField) or (
        initial_field.layer.tick != 0
        or initial_field.last_distribution is not None
        or initial_field.substrate is not None
    ):
        raise E1CueAmplitudeRunnerInventoryError("amplitude inventory needs a fresh field")
    if not isinstance(inputs, E1PartialCueRunnerInputs):
        raise E1CueAmplitudeRunnerInventoryError("amplitude inventory needs runner inputs")
    if substrate_config != NeutralLocalFieldSubstrateConfig(1.0):
        raise E1CueAmplitudeRunnerInventoryError("amplitude inventory S contract changed")
    if afterimage_config != NeutralFastAfterimageConfig(0.5):
        raise E1CueAmplitudeRunnerInventoryError("amplitude inventory H contract changed")
    if (
        inputs.world_arms.neutral_state.edge_inventory_digest
        != inputs.b1_static_h8_adapter.edge_inventory_digest
    ):
        raise E1CueAmplitudeRunnerInventoryError("amplitude inventory geometries differ")

    ordered_keys = _keys(contract)
    inventory: dict[E1CueAmplitudeRunnerKey, E1CueAmplitudeRunner] = {}
    for model, history, side, amplitude in ordered_keys:
        def runner(
            model: str = model,
            history: str = history,
            side: str = side,
            amplitude: float = amplitude,
        ) -> E1CueAmplitudeObservation:
            return run_e1_cue_amplitude_observation(
                contract,
                initial_field,
                inputs,
                model,
                history,
                side,
                amplitude,
                substrate_config,
                afterimage_config,
            )

        inventory[(model, history, side, amplitude)] = runner
    if tuple(inventory) != ordered_keys or len(inventory) != 72:
        raise E1CueAmplitudeRunnerInventoryError("amplitude inventory is incomplete")
    digest = _digest(
        {
            "inventory": "s1-cw.e1-cue-amplitude.lazy.v1",
            "contract_digest": contract.digest(),
            "keys": ordered_keys,
            "field_geometry": initial_field.layer.digest(),
            "states": _state_payload(inputs),
            "response_time_seconds": substrate_config.response_time_seconds,
            "afterimage_time_seconds": afterimage_config.time_constant_seconds,
            "runner": "run_e1_cue_amplitude_observation",
        }
    )
    return MappingProxyType(inventory), digest
