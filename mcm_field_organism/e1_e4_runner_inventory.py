"""Private S1-CL lazy runner inventory without E4 composition or evaluation."""

from __future__ import annotations

import hashlib
import json
from types import MappingProxyType
from typing import Callable, Mapping

from .e1_e4_e1_runners import run_e1_e4_e1_b0_b1_models
from .e1_e4_execution import (
    E1_E4_CONTINUITY_ANCHORS,
    E1_E4_EXECUTION_MODEL_IDS,
    E1E4ModelRun,
    preflight_e1_e4_runners,
)
from .e1_e4_f3_runners import build_e1_e4_f3_runner
from .e1_e4_s2_oracle_runners import (
    build_e1_e4_oracle_g_run,
    run_e1_e4_s2_b2_model,
)
from .e1_local_edge_plasticity import (
    E1LocalEdgePlasticityError,
    E1LocalEdgePlasticityState,
    validate_e1_state_for_layer,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .shared_mcm_field import SharedMCMField


class E1E4RunnerInventoryError(ValueError):
    """Raised when the lazy S1-CL inventory leaves the S1-CG contract."""


E1E4Runner = Callable[[], E1E4ModelRun]
E1E4AnchorSupplier = Callable[[], tuple[tuple[str, float], ...]]


def _digest(value: object) -> str:
    encoded = json.dumps(
        value, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _validate_inputs(
    initial_field: SharedMCMField,
    initial_e1_state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> None:
    if not isinstance(initial_field, SharedMCMField):
        raise E1E4RunnerInventoryError("E4 inventory requires one shared field")
    if (
        initial_field.layer.tick != 0
        or initial_field.last_distribution is not None
        or initial_field.substrate is not None
    ):
        raise E1E4RunnerInventoryError("E4 inventory requires one fresh field")
    if substrate_config != NeutralLocalFieldSubstrateConfig(1.0):
        raise E1E4RunnerInventoryError("E4 inventory S response contract changed")
    if afterimage_config != NeutralFastAfterimageConfig(0.5):
        raise E1E4RunnerInventoryError("E4 inventory H time contract changed")
    try:
        validate_e1_state_for_layer(initial_field.layer, initial_e1_state)
    except E1LocalEdgePlasticityError as exc:
        raise E1E4RunnerInventoryError(str(exc)) from exc
    if any(item.binding != 0.0 for item in initial_e1_state.edge_bindings):
        raise E1E4RunnerInventoryError("E4 inventory requires neutral initial E1")


def build_e1_e4_runner_inventory(
    initial_field: SharedMCMField,
    initial_e1_state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> tuple[
    Mapping[str, E1E4Runner],
    E1E4AnchorSupplier,
    str,
]:
    """Bind all lazy runner roles and preflight them without execution."""

    _validate_inputs(
        initial_field,
        initial_e1_state,
        substrate_config,
        afterimage_config,
    )
    cache: dict[str, object] = {}

    def e1_group():
        if "e1_group" not in cache:
            runs, anchors = run_e1_e4_e1_b0_b1_models(
                initial_field,
                initial_e1_state,
                substrate_config,
                afterimage_config,
            )
            cache["e1_group"] = {item.model_id: item for item in runs}
            cache["anchors"] = anchors
        return cache["e1_group"]

    def grouped_runner(model_id: str) -> E1E4Runner:
        def runner() -> E1E4ModelRun:
            group = e1_group()
            if not isinstance(group, dict) or model_id not in group:
                raise E1E4RunnerInventoryError("E1 grouped runner is incomplete")
            result = group[model_id]
            if not isinstance(result, E1E4ModelRun):
                raise E1E4RunnerInventoryError("E1 grouped runner result is invalid")
            return result

        return runner

    def s2_runner() -> E1E4ModelRun:
        if "b2" not in cache:
            cache["b2"] = run_e1_e4_s2_b2_model(
                initial_field, substrate_config, afterimage_config
            )
        result = cache["b2"]
        if not isinstance(result, E1E4ModelRun):
            raise E1E4RunnerInventoryError("S2 grouped runner result is invalid")
        return result

    f3_runners = {
        model_id: build_e1_e4_f3_runner(
            model_id,
            initial_field,
            substrate_config,
            afterimage_config,
        )
        for model_id in ("b3", "b4", "b5", "b6")
    }

    def oracle_runner() -> E1E4ModelRun:
        if "oracle-g" not in cache:
            group = e1_group()
            if not isinstance(group, dict) or "e1" not in group:
                raise E1E4RunnerInventoryError("ORACLE-G E1 source is unavailable")
            cache["oracle-g"] = build_e1_e4_oracle_g_run(group["e1"])
        result = cache["oracle-g"]
        if not isinstance(result, E1E4ModelRun):
            raise E1E4RunnerInventoryError("ORACLE-G runner result is invalid")
        return result

    inventory: dict[str, E1E4Runner] = {
        "e1": grouped_runner("e1"),
        "b0": grouped_runner("b0"),
        "b1": grouped_runner("b1"),
        "b2": s2_runner,
        **f3_runners,
        "oracle-g": oracle_runner,
    }
    if tuple(inventory) != E1_E4_EXECUTION_MODEL_IDS:
        raise E1E4RunnerInventoryError("E4 inventory order changed")
    preflight_e1_e4_runners(inventory)

    def continuity_anchor_supplier() -> tuple[tuple[str, float], ...]:
        e1_group()
        anchors = cache.get("anchors")
        if not isinstance(anchors, tuple):
            raise E1E4RunnerInventoryError("E4 continuity anchors are unavailable")
        if tuple(name for name, _ in anchors) != tuple(
            name for name, _ in E1_E4_CONTINUITY_ANCHORS
        ):
            raise E1E4RunnerInventoryError("E4 continuity anchor order changed")
        return anchors

    inventory_digest = _digest(
        {
            "contract": "s1-cl.lazy-runner-inventory.v1",
            "models": E1_E4_EXECUTION_MODEL_IDS,
            "factories": {
                "e1": "run_e1_e4_e1_b0_b1_models:e1",
                "b0": "run_e1_e4_e1_b0_b1_models:b0",
                "b1": "run_e1_e4_e1_b0_b1_models:b1",
                "b2": "run_e1_e4_s2_b2_model",
                "b3": "run_e1_e4_f3_model:local-leaky",
                "b4": "run_e1_e4_f3_model:linear-coupled-field",
                "b5": "run_e1_e4_f3_model:f3-candidate",
                "b6": "run_e1_e4_f3_model:w7-n.const-v",
                "oracle-g": "build_e1_e4_oracle_g_run",
            },
            "field_geometry": initial_field.layer.digest(),
            "e1_geometry": initial_e1_state.edge_inventory_digest,
            "e1_contract": {
                "contract_id": initial_e1_state.contract.contract_id,
                "node_capacity": initial_e1_state.contract.node_capacity,
                "binding_rate_per_second": (
                    initial_e1_state.contract.binding_rate_per_second
                ),
                "release_rate_per_second": (
                    initial_e1_state.contract.release_rate_per_second
                ),
                "backreaction_gain": initial_e1_state.contract.backreaction_gain,
            },
            "response_time_seconds": substrate_config.response_time_seconds,
            "afterimage_time_seconds": afterimage_config.time_constant_seconds,
            "anchor_names": tuple(name for name, _ in E1_E4_CONTINUITY_ANCHORS),
        }
    )
    return MappingProxyType(inventory), continuity_anchor_supplier, inventory_digest
