"""Private S1-CR lazy inventory for the 36 partial-cue observations."""

from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Callable, Mapping

from .e1_partial_cue_contract import E1PartialCueContract
from .e1_partial_cue_execution import E1PartialCueObservation, S1_CP_CUE_IDS
from .e1_partial_cue_runners import (
    E1PartialCueRunnerInputs,
    run_e1_partial_cue_observation,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .shared_mcm_field import SharedMCMField


class E1PartialCueRunnerInventoryError(ValueError):
    """Raised when the S1-CR lazy inventory leaves the S1-CO contract."""


E1PartialCueRunner = Callable[[], E1PartialCueObservation]
E1PartialCueRunnerKey = tuple[str, str, str]


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _keys(contract: E1PartialCueContract) -> tuple[E1PartialCueRunnerKey, ...]:
    return tuple(
        (model_id, history_id, cue_id)
        for model_id in contract.model_arms
        for history_id in contract.history_arms
        for cue_id in S1_CP_CUE_IDS
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


def build_e1_partial_cue_runner_inventory(
    contract: E1PartialCueContract,
    initial_field: SharedMCMField,
    inputs: E1PartialCueRunnerInputs,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> tuple[Mapping[E1PartialCueRunnerKey, E1PartialCueRunner], str]:
    """Bind all 36 cue roles without invoking a runner or compositor."""

    if not isinstance(contract, E1PartialCueContract):
        raise E1PartialCueRunnerInventoryError("cue inventory requires its contract")
    if not isinstance(initial_field, SharedMCMField) or (
        initial_field.layer.tick != 0
        or initial_field.last_distribution is not None
        or initial_field.substrate is not None
    ):
        raise E1PartialCueRunnerInventoryError("cue inventory requires one fresh field")
    if not isinstance(inputs, E1PartialCueRunnerInputs):
        raise E1PartialCueRunnerInventoryError("cue inventory requires runner inputs")
    if substrate_config != NeutralLocalFieldSubstrateConfig(1.0):
        raise E1PartialCueRunnerInventoryError("cue inventory S contract changed")
    if afterimage_config != NeutralFastAfterimageConfig(0.5):
        raise E1PartialCueRunnerInventoryError("cue inventory H contract changed")
    if (
        inputs.world_arms.neutral_state.edge_inventory_digest
        != inputs.b1_static_h8_adapter.edge_inventory_digest
    ):
        raise E1PartialCueRunnerInventoryError("cue inventory geometries differ")

    ordered_keys = _keys(contract)
    inventory: dict[E1PartialCueRunnerKey, E1PartialCueRunner] = {}
    for model_id, history_id, cue_id in ordered_keys:
        def runner(
            model_id: str = model_id,
            history_id: str = history_id,
            cue_id: str = cue_id,
        ) -> E1PartialCueObservation:
            return run_e1_partial_cue_observation(
                contract,
                initial_field,
                inputs,
                model_id,
                history_id,
                cue_id,
                substrate_config,
                afterimage_config,
            )

        inventory[(model_id, history_id, cue_id)] = runner
    if tuple(inventory) != ordered_keys or len(inventory) != 36:
        raise E1PartialCueRunnerInventoryError("cue inventory is incomplete or reordered")
    inventory_digest = _digest(
        {
            "inventory": "s1-cr.e1-partial-cue.lazy.v1",
            "contract_digest": contract.digest(),
            "keys": ordered_keys,
            "field_geometry": initial_field.layer.digest(),
            "states": _state_payload(inputs),
            "response_time_seconds": substrate_config.response_time_seconds,
            "afterimage_time_seconds": afterimage_config.time_constant_seconds,
            "runner": "run_e1_partial_cue_observation",
        }
    )
    return MappingProxyType(inventory), inventory_digest
