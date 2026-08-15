"""Pure private DTS-1 edge-rate adapter and symmetric generator."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
import re

import numpy as np

from .dynamic_substrate_s1hi_resource_anatomy import DTS1ResourceAnatomy
from .mcm_neuron_layer import MCMNeuronLayer
from .mcm_substrate_state import (
    MCMSubstrateStateError,
    mcm_substrate_edge_inventory,
    mcm_substrate_edge_inventory_digest,
)
from .neutral_local_field_substrate import NeutralLocalFieldSubstrateConfig


class DTS1BackreactionError(ValueError):
    """Raised before output when the pure DTS-1 reader is invalid."""


S1_HT_IMPLEMENTATION_ID = "dynamic-substrate.pure-backreaction.s1ht.v1"
S1_HT_SOURCE_S1HS_CONTRACT_DIGEST = (
    "b78a9ecb18317f3bc39a6891380d466edb36bd4e575f6028d78e192a234bfb82"
)
S1_HT_DECISION = "DTS1_PURE_BACKREACTION_IMPLEMENTED_TECHNICALLY_ACCEPTED"
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _finite_positive(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise DTS1BackreactionError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DTS1BackreactionError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result <= 0.0:
        raise DTS1BackreactionError(f"{role} must be finite and positive")
    return result


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1BackreactionEdgeRate:
    """One symmetric positive rate on one canonical internal edge."""

    first_node_id: str
    second_node_id: str
    rate_per_second: float

    def __post_init__(self) -> None:
        if (
            not isinstance(self.first_node_id, str)
            or not self.first_node_id
            or not isinstance(self.second_node_id, str)
            or not self.second_node_id
            or self.first_node_id >= self.second_node_id
        ):
            raise DTS1BackreactionError(
                "backreaction edge endpoints must be nonempty and canonical"
            )
        object.__setattr__(
            self,
            "rate_per_second",
            _finite_positive(self.rate_per_second, "rate_per_second"),
        )

    @property
    def edge(self) -> tuple[str, str]:
        return (self.first_node_id, self.second_node_id)


@dataclass(frozen=True, slots=True)
class DTS1BackreactionResult:
    """Complete immutable edge-rate ledger for one reader arm."""

    backreaction_enabled: bool
    base_rate_per_second: float
    edge_rates: tuple[DTS1BackreactionEdgeRate, ...]
    edge_inventory_digest: str

    def __post_init__(self) -> None:
        if not isinstance(self.backreaction_enabled, bool):
            raise DTS1BackreactionError("backreaction_enabled must be boolean")
        base_rate = _finite_positive(
            self.base_rate_per_second,
            "base_rate_per_second",
        )
        object.__setattr__(self, "base_rate_per_second", base_rate)
        rates = tuple(self.edge_rates)
        if not rates or any(
            not isinstance(item, DTS1BackreactionEdgeRate) for item in rates
        ):
            raise DTS1BackreactionError(
                "backreaction result requires a nonempty edge-rate ledger"
            )
        edges = tuple(item.edge for item in rates)
        if len(set(edges)) != len(edges):
            raise DTS1BackreactionError("backreaction edge identities must be unique")
        if not isinstance(self.edge_inventory_digest, str) or not (
            _DIGEST_PATTERN.fullmatch(self.edge_inventory_digest)
        ):
            raise DTS1BackreactionError(
                "edge_inventory_digest must be one lowercase SHA-256 digest"
            )
        for item in rates:
            ratio = item.rate_per_second / base_rate
            if ratio < 1.0 or ratio > 2.0:
                raise DTS1BackreactionError(
                    "active edge rates must remain between r_0 and 2*r_0"
                )
            if not self.backreaction_enabled and item.rate_per_second != base_rate:
                raise DTS1BackreactionError(
                    "ablated edge rates must equal the exact base rate"
                )
        object.__setattr__(
            self,
            "edge_rates",
            tuple(sorted(rates, key=lambda item: item.edge)),
        )

    @property
    def edges(self) -> tuple[tuple[str, str], ...]:
        return tuple(item.edge for item in self.edge_rates)


@dataclass(frozen=True, slots=True)
class DTS1S1HTImplementationReceipt:
    implementation_id: str
    source_s1hs_contract_digest: str
    matrix_case_ids: tuple[str, ...]
    pure_adapter_implemented: bool
    pure_generator_implemented: bool
    existing_geometry_helpers_reused: bool
    resource_step_import_present: bool
    runtime_integration_present: bool
    material_rate_values_selected: bool
    research_execution_permitted: bool
    field_steps_executed: int
    functional_effect_proven: bool
    claims_permitted: bool
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "receipt_digest"
        }
        if (
            self.implementation_id != S1_HT_IMPLEMENTATION_ID
            or self.source_s1hs_contract_digest
            != S1_HT_SOURCE_S1HS_CONTRACT_DIGEST
            or self.matrix_case_ids
            != tuple(f"T{index:02d}" for index in range(1, 17))
            or any(
                value is not True
                for value in (
                    self.pure_adapter_implemented,
                    self.pure_generator_implemented,
                    self.existing_geometry_helpers_reused,
                )
            )
            or any(
                value is not False
                for value in (
                    self.resource_step_import_present,
                    self.runtime_integration_present,
                    self.material_rate_values_selected,
                    self.research_execution_permitted,
                    self.functional_effect_proven,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision != S1_HT_DECISION
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1BackreactionError("S1-HT implementation receipt weakened")


def build_dts1_s1ht_implementation_receipt() -> DTS1S1HTImplementationReceipt:
    """Return the static S1-HT receipt without computing any field rate."""

    values = {
        "implementation_id": S1_HT_IMPLEMENTATION_ID,
        "source_s1hs_contract_digest": S1_HT_SOURCE_S1HS_CONTRACT_DIGEST,
        "matrix_case_ids": tuple(f"T{index:02d}" for index in range(1, 17)),
        "pure_adapter_implemented": True,
        "pure_generator_implemented": True,
        "existing_geometry_helpers_reused": True,
        "resource_step_import_present": False,
        "runtime_integration_present": False,
        "material_rate_values_selected": False,
        "research_execution_permitted": False,
        "field_steps_executed": 0,
        "functional_effect_proven": False,
        "claims_permitted": False,
        "decision": S1_HT_DECISION,
    }
    return DTS1S1HTImplementationReceipt(
        **values,
        receipt_digest=_digest(values),
    )


def _layer_geometry(
    layer: MCMNeuronLayer,
) -> tuple[tuple[tuple[str, str], ...], str, tuple[str, ...]]:
    if not isinstance(layer, MCMNeuronLayer):
        raise DTS1BackreactionError("backreaction requires one MCM neuron layer")
    try:
        edges = mcm_substrate_edge_inventory(layer)
        digest = mcm_substrate_edge_inventory_digest(layer)
    except MCMSubstrateStateError as exc:
        raise DTS1BackreactionError(str(exc)) from exc
    node_ids = tuple(neuron.neuron_id for neuron in layer.neurons)
    return edges, digest, node_ids


def _validate_anatomy_for_layer(
    layer: MCMNeuronLayer,
    anatomy: DTS1ResourceAnatomy,
) -> tuple[tuple[tuple[str, str], ...], str]:
    if not isinstance(anatomy, DTS1ResourceAnatomy):
        raise DTS1BackreactionError(
            "backreaction requires one valid DTS-1 anatomy"
        )
    edges, digest, node_ids = _layer_geometry(layer)
    anatomy_nodes = tuple(item.node_id for item in anatomy.node_capacities)
    anatomy_edges = tuple(item.edge for item in anatomy.edge_resources)
    if anatomy_nodes != node_ids:
        raise DTS1BackreactionError(
            "anatomy nodes must match the complete layer node inventory"
        )
    if anatomy_edges != edges:
        raise DTS1BackreactionError(
            "anatomy edges must match the complete layer edge inventory"
        )
    if anatomy.edge_inventory_digest != digest:
        raise DTS1BackreactionError(
            "anatomy edge digest must match the existing layer geometry"
        )
    return edges, digest


def _validate_result_for_layer(
    layer: MCMNeuronLayer,
    result: DTS1BackreactionResult,
) -> None:
    if not isinstance(result, DTS1BackreactionResult):
        raise DTS1BackreactionError(
            "generator requires one DTS-1 backreaction result"
        )
    edges, digest, _ = _layer_geometry(layer)
    if result.edges != edges:
        raise DTS1BackreactionError(
            "edge-rate ledger must match the complete layer edge inventory"
        )
    if result.edge_inventory_digest != digest:
        raise DTS1BackreactionError(
            "edge-rate digest must match the existing layer geometry"
        )


def compute_dts1_edge_rates(
    layer: MCMNeuronLayer,
    anatomy: DTS1ResourceAnatomy,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    *,
    backreaction_enabled: bool,
) -> DTS1BackreactionResult:
    """Read one closed anatomy into symmetric internal edge rates."""

    if not isinstance(backreaction_enabled, bool):
        raise DTS1BackreactionError("backreaction_enabled must be boolean")
    if not isinstance(substrate_config, NeutralLocalFieldSubstrateConfig):
        raise DTS1BackreactionError(
            "backreaction requires one neutral field substrate configuration"
        )
    _, digest = _validate_anatomy_for_layer(layer, anatomy)
    base_rate = _finite_positive(
        1.0 / substrate_config.response_time_seconds,
        "base_rate_per_second",
    )
    capacities = {item.node_id: item.capacity for item in anatomy.node_capacities}
    rates = []
    for item in anatomy.edge_resources:
        first, second = item.edge
        endpoint_capacity = min(capacities[first], capacities[second])
        occupancy = (0.5 * item.conductive_bound) / endpoint_capacity
        if not math.isfinite(occupancy) or occupancy < 0.0 or occupancy > 1.0:
            raise DTS1BackreactionError(
                "conductive occupancy must remain within the S1-HR unit interval"
            )
        rate = base_rate if not backreaction_enabled else base_rate * (1.0 + occupancy)
        rates.append(DTS1BackreactionEdgeRate(first, second, rate))
    return DTS1BackreactionResult(
        backreaction_enabled=backreaction_enabled,
        base_rate_per_second=base_rate,
        edge_rates=tuple(rates),
        edge_inventory_digest=digest,
    )


def build_dts1_diffusion_generator(
    layer: MCMNeuronLayer,
    adapter_result: DTS1BackreactionResult,
) -> np.ndarray:
    """Build one symmetric internal generator without advancing any state."""

    _validate_result_for_layer(layer, adapter_result)
    index = {neuron.neuron_id: offset for offset, neuron in enumerate(layer.neurons)}
    generator = np.zeros((len(index), len(index)), dtype=np.float64)
    for item in adapter_result.edge_rates:
        first = index[item.first_node_id]
        second = index[item.second_node_id]
        rate = item.rate_per_second
        generator[first, second] += rate
        generator[second, first] += rate
        generator[first, first] -= rate
        generator[second, second] -= rate
    if not np.all(np.isfinite(generator)):
        raise DTS1BackreactionError("generator must contain only finite values")
    if not np.array_equal(generator, generator.T):
        raise DTS1BackreactionError("generator must be exactly symmetric")
    scale = max(1.0, float(np.max(np.abs(generator))))
    tolerance = 1e-12 * scale
    if not np.allclose(
        np.sum(generator, axis=1),
        0.0,
        rtol=0.0,
        atol=tolerance,
    ):
        raise DTS1BackreactionError("generator must have zero row sum")
    if float(np.max(np.linalg.eigvalsh(generator))) > tolerance:
        raise DTS1BackreactionError("generator must be negative semidefinite")
    return generator
