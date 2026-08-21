"""Common public four-node fresh field factory; no private role runtime."""

from __future__ import annotations

import hashlib
import json
from typing import Mapping

from .four_node_fresh_manifest import FourNodeFreshManifest
from .mcm_neuron import MCMFieldPerception, MCMNeuron
from .mcm_neuron_layer import MCMNeuronLayer, PeriodicSamplingAxis
from .receptor_contract import ReceptorNeuronDockMap
from .shared_mcm_field import SharedFieldDock, SharedMCMField


class FourNodeFreshFactoryError(ValueError):
    """Raised when the registered public fresh field cannot be reproduced."""


def _fail(code: str, detail: str) -> None:
    raise FourNodeFreshFactoryError(f"{code}: {detail}")


def _mapping(value: object, role: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        _fail("FRESH_FACTORY_PUBLIC_FIELD_INVALID", f"{role} is not a mapping")
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
