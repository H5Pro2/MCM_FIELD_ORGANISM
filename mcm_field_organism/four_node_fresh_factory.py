"""Four-node public field and private fresh-role value factories."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Mapping

from .dynamic_substrate_s1hi_resource_anatomy import (
    DTS1EdgeResource,
    DTS1NodeCapacity,
    DTS1ResourceAnatomy,
)
from .four_node_fresh_manifest import FourNodeFreshManifest
from .local_state_replace_s_compositor_core import geometry_digest
from .m1_parallel_leak_replace_s_compositor import (
    M1ParallelLeakBankState,
    build_registered_m1_parallel_leak_configuration,
    build_zero_m1_parallel_leak_bank,
)
from .m2_bounded_buffer_replace_s_compositor import (
    M2BoundedBufferState,
    build_empty_m2_buffer,
    build_registered_m2_configuration,
)
from .mcm_neuron import MCMFieldPerception, MCMNeuron
from .mcm_neuron_layer import MCMNeuronLayer, PeriodicSamplingAxis
from .mcm_substrate_state import (
    MCMSubstrateState,
    mcm_substrate_edge_inventory,
    mcm_substrate_edge_inventory_digest,
)
from .receptor_contract import ReceptorNeuronDockMap
from .shared_mcm_field import SharedFieldDock, SharedMCMField
from .w7m_capacity_function_matrix import build_w7m_capacity_function_matrix_adapter
from .w7n_capacity_function_baselines import (
    W7NLocalBaselineState,
    build_zero_w7n_local_baseline,
)


class FourNodeFreshFactoryError(ValueError):
    """Raised when the registered public fresh field cannot be reproduced."""


@dataclass(frozen=True, slots=True)
class FourNodeFixedAdapterEdgeRate:
    first_node_id: str
    second_node_id: str
    rate_per_second: float


@dataclass(frozen=True, slots=True)
class FourNodeFixedAdapterState:
    base_rate_per_second: float
    backreaction_enabled: bool
    edge_inventory_digest: str
    edge_rates: tuple[FourNodeFixedAdapterEdgeRate, ...]


@dataclass(frozen=True, slots=True)
class FourNodeIntegratorEntry:
    node_id: str
    value: float


@dataclass(frozen=True, slots=True)
class FourNodeIntegratorState:
    entries: tuple[FourNodeIntegratorEntry, ...]


@dataclass(frozen=True, slots=True)
class FourNodeSubstrateFreshState:
    substrate: MCMSubstrateState
    registered_edge_inventory_digest: str
    native_edge_inventory_digest: str
    frozen_spec_digest_or_none: str | None


@dataclass(frozen=True, slots=True)
class FourNodeM4Rates:
    binding_rate: float
    recovery_rate: float
    turnover_rate: float


@dataclass(frozen=True, slots=True)
class FourNodeM4FreshState:
    anatomy: DTS1ResourceAnatomy
    rates: FourNodeM4Rates
    registered_edge_inventory_digest: str
    anatomy_edge_inventory_digest: str
    candidate_sidecar_digest_or_none: str | None


@dataclass(frozen=True, slots=True)
class FourNodePrivateFreshState:
    model_role: str
    configuration_binding: str
    native_state: object
    registered_state_payload: Mapping[str, object]
    registered_edge_inventory_digest_or_none: str | None = None
    native_edge_inventory_digest_or_none: str | None = None
    registered_geometry_digest_or_none: str | None = None
    native_geometry_digest_or_none: str | None = None


@dataclass(frozen=True, slots=True)
class FourNodeFreshBundle:
    public_field: SharedMCMField
    model_role: str
    private_state_or_none: FourNodePrivateFreshState | None
    stateless_marker_or_none: str | None
    registered_private_digest_or_none: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.public_field, SharedMCMField):
            _fail("FRESH_FACTORY_PUBLIC_FIELD_INVALID", "bundle requires public field")
        stateless = self.private_state_or_none is None
        if stateless != (self.stateless_marker_or_none is not None):
            _fail("FRESH_FACTORY_PRIVATE_STATE_INVALID", "bundle state-marker split differs")
        if stateless != (self.registered_private_digest_or_none is None):
            _fail("FRESH_FACTORY_PRIVATE_STATE_INVALID", "bundle digest split differs")


_MODEL_ROLES = (
    "A0_CURRENT_CONTACT",
    "A1_FAST_SH",
    "A2_B1_FIXED_ADAPTER",
    "A2_B2_INTEGRATOR",
    "A2_B3_LOCAL_LEAKY",
    "A2_B4_LINEAR_COUPLED",
    "A2_B5_F3_FULL",
    "A2_B6_CONST_V",
    "A3_NORM",
    "M1_PARALLEL_LEAK",
    "M2_DELAY",
    "M2_REPLAY",
    "M4_DTS1_T1",
    "M5_DIRECT",
)
_SUBSTRATE_ROLES = frozenset(
    {
        "A2_B3_LOCAL_LEAKY",
        "A2_B4_LINEAR_COUPLED",
        "A2_B5_F3_FULL",
        "A2_B6_CONST_V",
    }
)


def _fail(code: str, detail: str) -> None:
    raise FourNodeFreshFactoryError(f"{code}: {detail}")


def _mapping(value: object, role: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        _fail("FRESH_FACTORY_PUBLIC_FIELD_INVALID", f"{role} is not a mapping")
    return value


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    return value


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _public_projection(
    field: SharedMCMField,
    physical_geometry_digest: str,
) -> dict[str, object]:
    return {
        "initial_field_tick": field.layer.neurons[0].tick,
        "last_distribution": None,
        "nodes": [
            {
                "H": neuron.afterimage,
                "S": neuron.activation,
                "local_samples": [],
                "node_id": neuron.neuron_id,
                "perception_tick": neuron.perception.tick,
                "receptor_contact": neuron.perception.receptor_contact,
            }
            for neuron in field.layer.neurons
        ],
        "physical_geometry_digest": physical_geometry_digest,
        "schema_id": "mcm.s1rj.public-fresh-projection.4n.v1",
    }


def build_four_node_public_fresh_field(
    manifest: FourNodeFreshManifest,
) -> SharedMCMField:
    """Build the common tick-zero field without advancing any equation."""

    if not isinstance(manifest, FourNodeFreshManifest):
        _fail("FRESH_FACTORY_PUBLIC_FIELD_INVALID", "validated manifest required")
    try:
        geometry_record = _mapping(manifest.physical_geometry, "physical geometry")
        geometry = _mapping(geometry_record["payload"], "physical geometry payload")
        public_record = _mapping(
            manifest.public_fresh_projection,
            "public fresh projection",
        )
        public = _mapping(public_record["payload"], "public fresh projection payload")
        public_nodes = {
            row["node_id"]: row
            for value in public["nodes"]  # type: ignore[union-attr]
            for row in (_mapping(value, "public fresh node"),)
        }
        neurons = tuple(
            MCMNeuron(
                neuron_id=node["node_id"],
                field_id=geometry["field_id"],
                modality_id=geometry["modality_id"],
                geometry_id=geometry["geometry_id"],
                position=tuple(node["position"]),  # type: ignore[arg-type]
                activation=public_nodes[node["node_id"]]["S"],
                afterimage=public_nodes[node["node_id"]]["H"],
                perception=MCMFieldPerception(
                    tick=public_nodes[node["node_id"]]["perception_tick"],
                    receptor_contact=public_nodes[node["node_id"]]["receptor_contact"],
                    local_samples=(),
                ),
            )
            for value in geometry["nodes"]  # type: ignore[union-attr]
            for node in (_mapping(value, "physical geometry node"),)
        )
        periodic_axes = tuple(
            PeriodicSamplingAxis(**dict(_mapping(value, "periodic axis")))
            for value in geometry["periodic_axes"]  # type: ignore[union-attr]
        )
        layer = MCMNeuronLayer(
            layer_id=geometry["layer_id"],
            neurons=neurons,
            sample_offsets=tuple(
                tuple(offset) for offset in geometry["sample_offsets"]  # type: ignore[union-attr]
            ),
            periodic_axes=periodic_axes,
            receptor_dock_ids=tuple(neuron.neuron_id for neuron in neurons),
        )
        dock_payload = _mapping(geometry["dock"], "physical geometry dock")
        dock = SharedFieldDock(
            dock_id=dock_payload["dock_id"],
            dock_map=ReceptorNeuronDockMap(
                modality_id=geometry["modality_id"],
                receptor_geometry_id=dock_payload["receptor_geometry_id"],
                pairs=tuple(
                    tuple(pair) for pair in dock_payload["carrier_pairs"]  # type: ignore[union-attr]
                ),
            ),
        )
        field = SharedMCMField(layer=layer, docks=(dock,))
    except FourNodeFreshFactoryError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        _fail("FRESH_FACTORY_PUBLIC_FIELD_INVALID", str(exc))

    projection = _public_projection(field, geometry_record["digest"])  # type: ignore[arg-type]
    if _digest(projection) != public_record["digest"]:
        _fail(
            "FRESH_FACTORY_PUBLIC_PROJECTION_MISMATCH",
            "materialized field differs from registered projection",
        )
    return field


def _registered_edges(manifest: FourNodeFreshManifest) -> tuple[tuple[str, str], ...]:
    edge_record = _mapping(manifest.root["edge_inventory"], "edge inventory")
    payload = _mapping(edge_record["payload"], "edge inventory payload")
    return tuple(
        (row["first_node_id"], row["second_node_id"])
        for value in payload["edges"]  # type: ignore[union-attr]
        for row in (_mapping(value, "edge inventory row"),)
    )


def _private_record(
    manifest: FourNodeFreshManifest,
    model_role: str,
) -> Mapping[str, object]:
    records = tuple(
        row
        for value in manifest.root["private_fresh_states"]  # type: ignore[union-attr]
        for row in (_mapping(value, "private fresh record"),)
        if row["model_role"] == model_role
    )
    if len(records) != 1:
        _fail("FRESH_FACTORY_MODEL_ROLE_INVALID", "private model role is not unique")
    return records[0]


def _stateless_marker(manifest: FourNodeFreshManifest, model_role: str) -> str:
    records = tuple(
        row
        for value in manifest.root["stateless_markers"]  # type: ignore[union-attr]
        for row in (_mapping(value, "stateless marker"),)
        if row["model_role"] == model_role
    )
    if len(records) != 1 or not isinstance(records[0]["state_marker"], str):
        _fail("FRESH_FACTORY_MODEL_ROLE_INVALID", "stateless model role is not unique")
    return records[0]["state_marker"]  # type: ignore[return-value]


def _edge_bridge(
    manifest: FourNodeFreshManifest,
    field: SharedMCMField,
) -> tuple[str, str]:
    registered = _registered_edges(manifest)
    native = mcm_substrate_edge_inventory(field.layer)
    if registered != native:
        _fail("FRESH_FACTORY_EDGE_BRIDGE_INVALID", "registered and native edges differ")
    geometry = _mapping(manifest.physical_geometry["payload"], "physical geometry")
    registered_digest = geometry["edge_inventory_digest"]
    native_digest = mcm_substrate_edge_inventory_digest(field.layer)
    if not isinstance(registered_digest, str) or not isinstance(native_digest, str):
        _fail("FRESH_FACTORY_EDGE_BRIDGE_INVALID", "edge digest role is invalid")
    return registered_digest, native_digest


def _build_b1(state: Mapping[str, object]) -> FourNodeFixedAdapterState:
    return FourNodeFixedAdapterState(
        base_rate_per_second=state["base_rate_per_second"],  # type: ignore[arg-type]
        backreaction_enabled=state["backreaction_enabled"],  # type: ignore[arg-type]
        edge_inventory_digest=state["edge_inventory_digest"],  # type: ignore[arg-type]
        edge_rates=tuple(
            FourNodeFixedAdapterEdgeRate(
                row["first_node_id"],  # type: ignore[arg-type]
                row["second_node_id"],  # type: ignore[arg-type]
                row["rate_per_second"],  # type: ignore[arg-type]
            )
            for value in state["edge_rates"]  # type: ignore[union-attr]
            for row in (_mapping(value, "B1 edge rate"),)
        ),
    )


def _build_b2(state: Mapping[str, object]) -> FourNodeIntegratorState:
    return FourNodeIntegratorState(
        tuple(
            FourNodeIntegratorEntry(row["node_id"], row["value"])  # type: ignore[arg-type]
            for value in state["entries"]  # type: ignore[union-attr]
            for row in (_mapping(value, "B2 entry"),)
        )
    )


def _build_substrate(
    state: Mapping[str, object],
    registered_edge_digest: str,
    native_edge_digest: str,
) -> FourNodeSubstrateFreshState:
    mass_values = state["masses"]
    if not isinstance(mass_values, (tuple, list)) or len(mass_values) != 4:
        _fail("FRESH_FACTORY_PRIVATE_STATE_INVALID", "B3-B6 require four masses")
    expected_node_ids = ("node-a", "node-b", "node-c", "node-d")
    native_masses = []
    for value, expected_node_id in zip(mass_values, expected_node_ids, strict=True):
        registered_mass = _mapping(value, "B3-B6 registered mass")
        if set(registered_mass) != {"node_id", "mass"}:
            _fail(
                "FRESH_FACTORY_PRIVATE_STATE_INVALID",
                "B3-B6 registered mass fields differ",
            )
        if (
            registered_mass["node_id"] != expected_node_id
            or registered_mass["mass"] != 0.25
        ):
            _fail(
                "FRESH_FACTORY_PRIVATE_STATE_INVALID",
                "B3-B6 registered mass identity or value differs",
            )
        native_masses.append(
            {
                "neuron_id": registered_mass["node_id"],
                "mass": registered_mass["mass"],
            }
        )
    native_payload = {
        "arm": state["arm"],
        "masses": native_masses,
        "edge_inventory_digest": native_edge_digest,
    }
    substrate = MCMSubstrateState.from_payload(native_payload)
    return FourNodeSubstrateFreshState(
        substrate,
        registered_edge_digest,
        native_edge_digest,
        state["frozen_spec_digest_or_null"],  # type: ignore[arg-type]
    )


def _registered_w7_state(model_id: str) -> W7NLocalBaselineState:
    adapter = build_w7m_capacity_function_matrix_adapter()
    specs = tuple(spec for spec in adapter.baselines if spec.model_id == model_id)
    if len(specs) != 1:
        _fail("FRESH_FACTORY_PRIVATE_STATE_INVALID", f"W7 spec {model_id} is not unique")
    return build_zero_w7n_local_baseline(specs[0], 4)


def _build_m4(state: Mapping[str, object]) -> FourNodeM4FreshState:
    anatomy = DTS1ResourceAnatomy(
        node_capacities=tuple(
            DTS1NodeCapacity(row["node_id"], row["capacity"])  # type: ignore[arg-type]
            for value in state["node_capacities"]  # type: ignore[union-attr]
            for row in (_mapping(value, "M4 node capacity"),)
        ),
        edge_resources=tuple(
            DTS1EdgeResource(
                row["first_node_id"],  # type: ignore[arg-type]
                row["second_node_id"],  # type: ignore[arg-type]
                row["conductive_bound"],  # type: ignore[arg-type]
                row["refractory"],  # type: ignore[arg-type]
            )
            for value in state["edge_resources"]  # type: ignore[union-attr]
            for row in (_mapping(value, "M4 edge resource"),)
        ),
    )
    rates = _mapping(state["rates"], "M4 rates")
    return FourNodeM4FreshState(
        anatomy=anatomy,
        rates=FourNodeM4Rates(
            rates["binding_rate"],  # type: ignore[arg-type]
            rates["recovery_rate"],  # type: ignore[arg-type]
            rates["turnover_rate"],  # type: ignore[arg-type]
        ),
        registered_edge_inventory_digest=state["edge_inventory_digest"],  # type: ignore[arg-type]
        anatomy_edge_inventory_digest=anatomy.edge_inventory_digest,
        candidate_sidecar_digest_or_none=state["candidate_sidecar_digest_or_null"],  # type: ignore[arg-type]
    )


def _state_projection(private: FourNodePrivateFreshState) -> dict[str, object]:
    native = private.native_state
    role = private.model_role
    if isinstance(native, FourNodeFixedAdapterState):
        return {
            "backreaction_enabled": native.backreaction_enabled,
            "base_rate_per_second": native.base_rate_per_second,
            "edge_inventory_digest": native.edge_inventory_digest,
            "edge_rates": [
                {
                    "first_node_id": item.first_node_id,
                    "rate_per_second": item.rate_per_second,
                    "second_node_id": item.second_node_id,
                }
                for item in native.edge_rates
            ],
        }
    if isinstance(native, FourNodeIntegratorState):
        return {
            "entries": [
                {"node_id": item.node_id, "value": item.value}
                for item in native.entries
            ]
        }
    if isinstance(native, FourNodeSubstrateFreshState):
        return {
            "arm": native.substrate.arm.canonical_payload(),
            "edge_inventory_digest": native.registered_edge_inventory_digest,
            "frozen_spec_digest_or_null": native.frozen_spec_digest_or_none,
            "masses": [
                {"mass": item.mass, "node_id": item.neuron_id}
                for item in native.substrate.masses
            ],
        }
    if isinstance(native, W7NLocalBaselineState):
        return {"latent": list(native.latent), "model_id": native.model_id}
    if isinstance(native, M1ParallelLeakBankState):
        return {
            "fast_state": {
                "latent": list(native.fast_state.latent),
                "model_id": native.fast_state.model_id,
            },
            "slow_state": {
                "latent": list(native.slow_state.latent),
                "model_id": native.slow_state.model_id,
            },
            "trace_order": ["FAST", "SLOW"],
        }
    if isinstance(native, M2BoundedBufferState):
        if private.registered_geometry_digest_or_none is None:
            _fail("FRESH_FACTORY_PRIVATE_STATE_INVALID", "M2 registered geometry missing")
        return {
            "geometry_digest": private.registered_geometry_digest_or_none,
            "mode_id": native.mode_id,
            "neuron_order": list(native.neuron_order),
            "records": [],
            "replay_cursor": native.replay_cursor,
            "replay_phase": native.replay_phase,
        }
    if isinstance(native, FourNodeM4FreshState):
        return {
            "candidate_sidecar_digest_or_null": native.candidate_sidecar_digest_or_none,
            "edge_inventory_digest": native.registered_edge_inventory_digest,
            "edge_resources": [
                {
                    "conductive_bound": item.conductive_bound,
                    "first_node_id": item.first_node_id,
                    "refractory": item.refractory,
                    "second_node_id": item.second_node_id,
                }
                for item in native.anatomy.edge_resources
            ],
            "node_capacities": [
                {"capacity": item.capacity, "node_id": item.node_id}
                for item in native.anatomy.node_capacities
            ],
            "rates": {
                "binding_rate": native.rates.binding_rate,
                "recovery_rate": native.rates.recovery_rate,
                "turnover_rate": native.rates.turnover_rate,
            },
        }
    _fail("FRESH_FACTORY_PRIVATE_STATE_INVALID", f"no projection for {role}")


def _build_private_state(
    manifest: FourNodeFreshManifest,
    field: SharedMCMField,
    model_role: str,
    record: Mapping[str, object],
) -> FourNodePrivateFreshState:
    payload = _mapping(record["payload"], "private fresh payload")
    state = _mapping(payload["state_payload"], "private state payload")
    configuration = payload["configuration_binding"]
    if not isinstance(configuration, str):
        _fail("FRESH_FACTORY_PRIVATE_STATE_INVALID", "configuration binding is invalid")

    registered_edge = native_edge = None
    registered_geometry = native_geometry = None
    if model_role == "A2_B1_FIXED_ADAPTER":
        native_state: object = _build_b1(state)
    elif model_role == "A2_B2_INTEGRATOR":
        native_state = _build_b2(state)
    elif model_role in _SUBSTRATE_ROLES:
        registered_edge, native_edge = _edge_bridge(manifest, field)
        native_state = _build_substrate(state, registered_edge, native_edge)
    elif model_role == "A3_NORM":
        native_state = _registered_w7_state("norm")
    elif model_role == "M1_PARALLEL_LEAK":
        m1_configuration = build_registered_m1_parallel_leak_configuration()
        if m1_configuration.source_registration_digest != configuration:
            _fail("FRESH_FACTORY_PRIVATE_STATE_INVALID", "M1 configuration differs")
        native_state = build_zero_m1_parallel_leak_bank(m1_configuration, 4)
    elif model_role in {"M2_DELAY", "M2_REPLAY"}:
        mode = "DELAY" if model_role == "M2_DELAY" else "REPLAY"
        m2_configuration = build_registered_m2_configuration(mode)
        if m2_configuration.source_registration_digest != configuration:
            _fail("FRESH_FACTORY_PRIVATE_STATE_INVALID", "M2 configuration differs")
        native_state = build_empty_m2_buffer(m2_configuration, field)
        registered_geometry = state["geometry_digest"]  # type: ignore[assignment]
        native_geometry = geometry_digest(field)
        if native_state.geometry_digest != native_geometry:
            _fail("FRESH_FACTORY_PRIVATE_STATE_INVALID", "M2 native geometry differs")
    elif model_role == "M4_DTS1_T1":
        registered_edge, _ = _edge_bridge(manifest, field)
        native_state = _build_m4(state)
        if tuple(item.edge for item in native_state.anatomy.edge_resources) != _registered_edges(manifest):
            _fail("FRESH_FACTORY_EDGE_BRIDGE_INVALID", "M4 anatomy edges differ")
        native_edge = native_state.anatomy_edge_inventory_digest
    elif model_role == "M5_DIRECT":
        native_state = _registered_w7_state("leak")
    else:
        _fail("FRESH_FACTORY_MODEL_ROLE_INVALID", "stateful model role is unknown")

    private = FourNodePrivateFreshState(
        model_role=model_role,
        configuration_binding=configuration,
        native_state=native_state,
        registered_state_payload=state,
        registered_edge_inventory_digest_or_none=registered_edge,
        native_edge_inventory_digest_or_none=native_edge,
        registered_geometry_digest_or_none=registered_geometry,
        native_geometry_digest_or_none=native_geometry,
    )
    projection = _state_projection(private)
    if projection != _plain(state):
        _fail("FRESH_FACTORY_PRIVATE_STATE_INVALID", f"{model_role} state roundtrip differs")
    roundtrip = _plain(payload)
    if not isinstance(roundtrip, dict):
        _fail("FRESH_FACTORY_PRIVATE_STATE_INVALID", "private payload roundtrip is invalid")
    roundtrip["state_payload"] = projection
    if _digest(roundtrip) != record["digest"]:
        _fail("FRESH_FACTORY_PRIVATE_DIGEST_MISMATCH", f"{model_role} digest differs")
    return private


def build_four_node_role_fresh_bundle(
    manifest: FourNodeFreshManifest,
    model_role: str,
) -> FourNodeFreshBundle:
    """Build one isolated public field and its exact role-private fresh value."""

    if not isinstance(manifest, FourNodeFreshManifest):
        _fail("FRESH_FACTORY_PUBLIC_FIELD_INVALID", "validated manifest required")
    if model_role not in _MODEL_ROLES:
        _fail("FRESH_FACTORY_MODEL_ROLE_INVALID", "model role is not registered")
    field = build_four_node_public_fresh_field(manifest)
    if model_role in _MODEL_ROLES[:2]:
        return FourNodeFreshBundle(
            field,
            model_role,
            None,
            _stateless_marker(manifest, model_role),
            None,
        )
    try:
        record = _private_record(manifest, model_role)
        private = _build_private_state(manifest, field, model_role, record)
    except FourNodeFreshFactoryError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        _fail("FRESH_FACTORY_PRIVATE_STATE_INVALID", str(exc))
    digest = record["digest"]
    if not isinstance(digest, str):
        _fail("FRESH_FACTORY_PRIVATE_DIGEST_MISMATCH", "private digest is invalid")
    return FourNodeFreshBundle(field, model_role, private, None, digest)
