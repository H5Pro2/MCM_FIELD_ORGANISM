"""Private S1-DL loader and synthetic seven-arm transfer compositor."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Callable

import numpy as np

from .e1_frozen_state_transfer_contract import (
    E1FrozenStateTransferContract,
    S1_DK_ARMS,
    build_e1_frozen_state_transfer_contract,
)
from .e1_frozen_transient_probe import (
    FrozenTransientE1ProbeResult,
    advance_fixed_e1_adapter_fast_shared_field_transient,
    advance_frozen_e1_fast_shared_field_transient,
)
from .e1_local_edge_plasticity import (
    E1EdgeBinding,
    E1LocalEdgePlasticityContract,
    E1LocalEdgePlasticityError,
    E1LocalEdgePlasticityState,
)
from .e1_weighted_field_adapter import E1WeightedFieldAdapterResult
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import SharedMCMField
from .transient_neuron_input import TransientNeuronInputSet


class E1FrozenStateTransferError(ValueError):
    """Raised when the S1-DL loading or synthetic arm boundary is violated."""


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _state_payload(state: E1LocalEdgePlasticityState) -> dict[str, object]:
    contract = state.contract
    return {
        "contract": {
            "contract_id": contract.contract_id,
            "node_capacity": contract.node_capacity,
            "binding_rate_per_second": contract.binding_rate_per_second,
            "release_rate_per_second": contract.release_rate_per_second,
            "backreaction_gain": contract.backreaction_gain,
        },
        "edge_bindings": [
            {
                "first_neuron_id": item.first_neuron_id,
                "second_neuron_id": item.second_neuron_id,
                "binding": item.binding,
            }
            for item in state.edge_bindings
        ],
        "edge_inventory_digest": state.edge_inventory_digest,
    }


def _load_state(payload: object, role: str) -> E1LocalEdgePlasticityState:
    if not isinstance(payload, dict):
        raise E1FrozenStateTransferError(f"{role} payload is invalid")
    try:
        contract_payload = payload["contract"]
        bindings_payload = payload["edge_bindings"]
        if not isinstance(contract_payload, dict) or not isinstance(
            bindings_payload, list
        ):
            raise TypeError
        contract = E1LocalEdgePlasticityContract(
            contract_id=contract_payload["contract_id"],
            node_capacity=contract_payload["node_capacity"],
            binding_rate_per_second=contract_payload["binding_rate_per_second"],
            release_rate_per_second=contract_payload["release_rate_per_second"],
            backreaction_gain=contract_payload["backreaction_gain"],
        )
        state = E1LocalEdgePlasticityState(
            contract=contract,
            edge_bindings=tuple(
                E1EdgeBinding(
                    first_neuron_id=item["first_neuron_id"],
                    second_neuron_id=item["second_neuron_id"],
                    binding=item["binding"],
                )
                for item in bindings_payload
            ),
            edge_inventory_digest=payload["edge_inventory_digest"],
        )
    except (KeyError, TypeError, E1LocalEdgePlasticityError) as exc:
        raise E1FrozenStateTransferError(f"{role} payload is invalid") from exc
    if _state_payload(state) != payload:
        raise E1FrozenStateTransferError(
            f"{role} payload changed during typed reconstruction"
        )
    return state


@dataclass(frozen=True, slots=True)
class LoadedE1FrozenStates:
    """Canonical states loaded for inspection, never for S1-DL execution."""

    contract: E1FrozenStateTransferContract
    b_ab: E1LocalEdgePlasticityState
    b_ba: E1LocalEdgePlasticityState

    def __post_init__(self) -> None:
        if not isinstance(self.contract, E1FrozenStateTransferContract):
            raise E1FrozenStateTransferError("loaded states require S1-DK contract")
        if _digest(_state_payload(self.b_ab)) != self.contract.b_ab_digest:
            raise E1FrozenStateTransferError("loaded b_AB digest changed")
        if _digest(_state_payload(self.b_ba)) != self.contract.b_ba_digest:
            raise E1FrozenStateTransferError("loaded b_BA digest changed")
        if (
            self.b_ab.contract != self.b_ba.contract
            or self.b_ab.edges != self.b_ba.edges
            or self.b_ab.edge_inventory_digest != self.b_ba.edge_inventory_digest
        ):
            raise E1FrozenStateTransferError("loaded state inventories differ")
        if self.contract.probe_execution_permitted is not False:
            raise E1FrozenStateTransferError("canonical S1-DL probe must stay locked")


def load_e1_frozen_states(
    history_report_path: Path,
) -> LoadedE1FrozenStates:
    """Load the digest-bound states without constructing or running a probe."""

    path = Path(history_report_path)
    contract = build_e1_frozen_state_transfer_contract(path)
    try:
        report = json.loads(path.read_text(encoding="ascii"))
        result = report["result"]
        left_payload = result["b_ab"]
        right_payload = result["b_ba"]
    except (KeyError, TypeError, json.JSONDecodeError, UnicodeError) as exc:
        raise E1FrozenStateTransferError("history report state payload is invalid") from exc
    return LoadedE1FrozenStates(
        contract=contract,
        b_ab=_load_state(left_payload, "b_AB"),
        b_ba=_load_state(right_payload, "b_BA"),
    )


@dataclass(frozen=True, slots=True)
class SyntheticE1FrozenStateSource:
    """Explicitly synthetic state pair accepted by the S1-DL compositor."""

    provenance: str
    b_ab: E1LocalEdgePlasticityState
    b_ba: E1LocalEdgePlasticityState

    def __post_init__(self) -> None:
        if self.provenance != "synthetic-s1dl-only":
            raise E1FrozenStateTransferError("state source is not synthetic")
        if not isinstance(self.b_ab, E1LocalEdgePlasticityState) or not isinstance(
            self.b_ba, E1LocalEdgePlasticityState
        ):
            raise E1FrozenStateTransferError("synthetic source requires two E1 states")
        if (
            self.b_ab.contract != self.b_ba.contract
            or self.b_ab.edges != self.b_ba.edges
            or self.b_ab.edge_inventory_digest != self.b_ba.edge_inventory_digest
        ):
            raise E1FrozenStateTransferError("synthetic state inventories differ")


@dataclass(frozen=True, slots=True)
class E1FrozenStateTransferArmResult:
    arm_id: str
    field: SharedMCMField
    frozen_state: E1LocalEdgePlasticityState | None
    applied_adapter: E1WeightedFieldAdapterResult | None

    def __post_init__(self) -> None:
        if self.arm_id not in S1_DK_ARMS:
            raise E1FrozenStateTransferError("unknown S1-DL arm")
        if not isinstance(self.field, SharedMCMField):
            raise E1FrozenStateTransferError("S1-DL arm requires one field")
        if self.arm_id == "p0":
            if self.frozen_state is not None or self.applied_adapter is not None:
                raise E1FrozenStateTransferError("P0 cannot carry E1 roles")
        elif not isinstance(self.frozen_state, E1LocalEdgePlasticityState):
            raise E1FrozenStateTransferError("E1 arm requires one frozen state")
        elif not isinstance(self.applied_adapter, E1WeightedFieldAdapterResult):
            raise E1FrozenStateTransferError("E1 arm requires one applied adapter")


def _field_vector(field: SharedMCMField, role: str) -> np.ndarray:
    if role == "s":
        return np.asarray(
            [item.activation for item in field.layer.neurons], dtype=np.float64
        )
    return np.asarray(
        [item.afterimage for item in field.layer.neurons], dtype=np.float64
    )


def _distance(first: SharedMCMField, second: SharedMCMField, role: str) -> float:
    values = np.abs(_field_vector(first, role) - _field_vector(second, role))
    result = float(np.max(values)) if values.size else 0.0
    if not math.isfinite(result):
        raise E1FrozenStateTransferError("S1-DL field distance is non-finite")
    return result


def _fresh_field_digest(field: SharedMCMField) -> str:
    if field.last_distribution is not None:
        raise E1FrozenStateTransferError("S1-DL arm field is not fresh")
    return _digest(
        {
            "layer_digest": field.layer.digest(),
            "docks": [
                {
                    "dock_id": dock.dock_id,
                    "modality_id": dock.dock_map.modality_id,
                    "geometry_id": dock.dock_map.receptor_geometry_id,
                    "pairs": dock.dock_map.pairs,
                }
                for dock in field.docks
            ],
            "last_distribution": None,
            "substrate": None if field.substrate is None else "present",
            "development": None if field.development is None else "present",
        }
    )


@dataclass(frozen=True, slots=True)
class E1FrozenStateTransferResult:
    """Technical synthetic result without research decision or claim role."""

    arms: tuple[E1FrozenStateTransferArmResult, ...]
    initial_field_digest: str
    d_active_s: float
    d_active_h: float
    d_ablation: float
    d_fixed_adapter: float
    frozen_state_change: float

    def __post_init__(self) -> None:
        if tuple(item.arm_id for item in self.arms) != S1_DK_ARMS:
            raise E1FrozenStateTransferError("S1-DL result arm order changed")
        if (
            not isinstance(self.initial_field_digest, str)
            or len(self.initial_field_digest) != 64
            or any(
                char not in "0123456789abcdef"
                for char in self.initial_field_digest
            )
        ):
            raise E1FrozenStateTransferError("initial field digest is invalid")
        for role in (
            "d_active_s",
            "d_active_h",
            "d_ablation",
            "d_fixed_adapter",
            "frozen_state_change",
        ):
            value = getattr(self, role)
            if not isinstance(value, float) or not math.isfinite(value) or value < 0.0:
                raise E1FrozenStateTransferError(f"{role} is invalid")
        if self.d_ablation != 0.0:
            raise E1FrozenStateTransferError("P0/AB0/BA0 identity failed")
        if self.d_fixed_adapter != 0.0:
            raise E1FrozenStateTransferError("active/fixed adapter identity failed")
        if self.frozen_state_change != 0.0:
            raise E1FrozenStateTransferError("frozen E1 state changed")

    def by_id(self, arm_id: str) -> E1FrozenStateTransferArmResult:
        for item in self.arms:
            if item.arm_id == arm_id:
                return item
        raise E1FrozenStateTransferError("unknown S1-DL result arm")


def run_synthetic_e1_frozen_state_transfer_arms(
    source: SyntheticE1FrozenStateSource,
    field_factory: Callable[[], SharedMCMField],
    distribution: ReceptorDistribution,
    transient_inputs: TransientNeuronInputSet,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
) -> E1FrozenStateTransferResult:
    """Run all seven arms only for an explicitly synthetic state source."""

    if not isinstance(source, SyntheticE1FrozenStateSource):
        raise E1FrozenStateTransferError(
            "S1-DL compositor accepts only a synthetic state source"
        )
    if not callable(field_factory):
        raise E1FrozenStateTransferError("S1-DL requires a fresh field factory")
    fields = tuple(field_factory() for _ in S1_DK_ARMS)
    if any(not isinstance(item, SharedMCMField) for item in fields):
        raise E1FrozenStateTransferError("field factory returned an invalid field")
    if len({id(item) for item in fields}) != len(fields):
        raise E1FrozenStateTransferError("each S1-DL arm requires a fresh field")
    initial_digests = tuple(_fresh_field_digest(item) for item in fields)
    if len(set(initial_digests)) != 1:
        raise E1FrozenStateTransferError("S1-DL initial fields are not identical")

    p0 = advance_neutral_fast_shared_field_transient(
        fields[0], distribution, transient_inputs, substrate_config,
        afterimage_config, dissipation_config,
    )
    ab0 = advance_frozen_e1_fast_shared_field_transient(
        fields[1], source.b_ab, distribution, transient_inputs,
        substrate_config, afterimage_config, dissipation_config,
        backreaction_enabled=False,
    )
    ba0 = advance_frozen_e1_fast_shared_field_transient(
        fields[2], source.b_ba, distribution, transient_inputs,
        substrate_config, afterimage_config, dissipation_config,
        backreaction_enabled=False,
    )
    ab1 = advance_frozen_e1_fast_shared_field_transient(
        fields[3], source.b_ab, distribution, transient_inputs,
        substrate_config, afterimage_config, dissipation_config,
        backreaction_enabled=True,
    )
    ba1 = advance_frozen_e1_fast_shared_field_transient(
        fields[4], source.b_ba, distribution, transient_inputs,
        substrate_config, afterimage_config, dissipation_config,
        backreaction_enabled=True,
    )
    abf = advance_fixed_e1_adapter_fast_shared_field_transient(
        fields[5], ab1.applied_adapter, distribution, transient_inputs,
        substrate_config, afterimage_config, dissipation_config,
    )
    baf = advance_fixed_e1_adapter_fast_shared_field_transient(
        fields[6], ba1.applied_adapter, distribution, transient_inputs,
        substrate_config, afterimage_config, dissipation_config,
    )
    if ab0.e1_state is not source.b_ab or ab1.e1_state is not source.b_ab:
        raise E1FrozenStateTransferError("b_AB was not kept as the exact object")
    if ba0.e1_state is not source.b_ba or ba1.e1_state is not source.b_ba:
        raise E1FrozenStateTransferError("b_BA was not kept as the exact object")

    arms = (
        E1FrozenStateTransferArmResult("p0", p0, None, None),
        E1FrozenStateTransferArmResult("ab0", ab0.field, source.b_ab, ab0.applied_adapter),
        E1FrozenStateTransferArmResult("ba0", ba0.field, source.b_ba, ba0.applied_adapter),
        E1FrozenStateTransferArmResult("ab1", ab1.field, source.b_ab, ab1.applied_adapter),
        E1FrozenStateTransferArmResult("ba1", ba1.field, source.b_ba, ba1.applied_adapter),
        E1FrozenStateTransferArmResult("abf", abf, source.b_ab, ab1.applied_adapter),
        E1FrozenStateTransferArmResult("baf", baf, source.b_ba, ba1.applied_adapter),
    )
    d_ablation = max(
        _distance(p0, ab0.field, role)
        for role in ("s", "h")
    )
    d_ablation = max(
        d_ablation,
        *(_distance(p0, ba0.field, role) for role in ("s", "h")),
    )
    d_fixed_adapter = max(
        *(_distance(ab1.field, abf, role) for role in ("s", "h")),
        *(_distance(ba1.field, baf, role) for role in ("s", "h")),
    )
    return E1FrozenStateTransferResult(
        arms=arms,
        initial_field_digest=initial_digests[0],
        d_active_s=_distance(ab1.field, ba1.field, "s"),
        d_active_h=_distance(ab1.field, ba1.field, "h"),
        d_ablation=d_ablation,
        d_fixed_adapter=d_fixed_adapter,
        frozen_state_change=0.0,
    )
