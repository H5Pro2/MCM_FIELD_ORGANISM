"""One shared MCM field with multiple receptor docks and one neuron layer."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import re
from typing import Iterable, Mapping

from .field_step_time import MCMFieldStepTime
from .mcm_neuron import MCMFieldPerception, MCMFieldSample, MCMNeuron
from .mcm_neuron_layer import (
    MCMNeuronLayer,
    MCMNeuronTransition,
    PeriodicSamplingAxis,
)
from .mcm_local_development_state import (
    MCMLocalDevelopmentContract,
    MCMLocalDevelopmentState,
    MCMLocalDevelopmentStateError,
    build_zero_mcm_local_development,
)
from .mcm_substrate_state import (
    MCMSubstrateArmContract,
    MCMSubstrateState,
    MCMSubstrateStateError,
    build_uniform_mcm_substrate,
    mcm_substrate_edge_inventory_digest,
)
from .receptor_contract import (
    CommonFieldTime,
    ReceptorContactFrame,
    ReceptorNeuronDockMap,
)
from .receptor_distributor import (
    DistributedReceptorContact,
    ReceptorDistribution,
)
from .transient_neuron_input import (
    TransientNeuronDockInput,
    TransientNeuronInputSet,
)


NEUTRAL_SNAPSHOT_SCHEMA_VERSION = 1
F3_SNAPSHOT_SCHEMA_VERSION = 2
S1B_SNAPSHOT_SCHEMA_VERSION = 3
NEUTRAL_SNAPSHOT_ROOT_KEYS = (
    "schema_version",
    "layer",
    "docks",
    "last_distribution",
)
SNAPSHOT_REFERENCE_STATE_FIELDS = ("substrate", "development")


class SharedMCMFieldError(ValueError):
    """Raised when shared-field identities or causal steps do not align."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise SharedMCMFieldError(
            f"{role} must be a lowercase technical identifier"
        )
    return value


def _payload_mapping(
    value: object,
    role: str,
    keys: set[str],
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise SharedMCMFieldError(f"{role} must be an object")
    supplied = set(value)
    if supplied != keys:
        raise SharedMCMFieldError(
            f"{role} fields mismatch; missing={sorted(keys - supplied)}, "
            f"unknown={sorted(supplied - keys)}"
        )
    return value


def _payload_sequence(value: object, role: str) -> tuple[object, ...]:
    if not isinstance(value, (list, tuple)):
        raise SharedMCMFieldError(f"{role} must be an array")
    return tuple(value)


@dataclass(frozen=True, slots=True)
class ReceptorDockAnatomy:
    """Technical placement of one receptor surface in shared field coordinates."""

    modality_id: str
    dock_id: str
    positions: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "modality_id", _identifier(self.modality_id, "modality_id")
        )
        object.__setattr__(self, "dock_id", _identifier(self.dock_id, "dock_id"))
        positions = tuple(tuple(position) for position in self.positions)
        if not positions:
            raise SharedMCMFieldError("dock anatomy requires shared positions")
        dimension = len(positions[0])
        if dimension == 0 or any(len(position) != dimension for position in positions):
            raise SharedMCMFieldError(
                "all shared dock positions must use one non-empty dimension"
            )
        if len(set(positions)) != len(positions):
            raise SharedMCMFieldError("dock positions must be unique")
        object.__setattr__(self, "positions", positions)


@dataclass(frozen=True, slots=True)
class SharedFieldDock:
    """One receptor-to-neuron map inside the common field boundary."""

    dock_id: str
    dock_map: ReceptorNeuronDockMap

    def __post_init__(self) -> None:
        object.__setattr__(self, "dock_id", _identifier(self.dock_id, "dock_id"))
        if not isinstance(self.dock_map, ReceptorNeuronDockMap):
            raise SharedMCMFieldError(
                "shared field dock requires a receptor-neuron map"
            )


def _mapped_receptor_contacts(
    docks: tuple[SharedFieldDock, ...],
    distribution: ReceptorDistribution,
) -> dict[str, float]:
    contacts_by_dock = {item.dock_id: item.frame for item in distribution.contacts}
    expected_docks = {item.dock_id for item in docks}
    unknown_docks = set(contacts_by_dock) - expected_docks
    if unknown_docks:
        raise SharedMCMFieldError(
            f"world-contact distribution contains unknown docks: {sorted(unknown_docks)}"
        )

    receptor_contacts: dict[str, float] = {}
    for dock in docks:
        frame = contacts_by_dock.get(dock.dock_id)
        if frame is None:
            continue
        try:
            mapped = dock.dock_map.contacts_for(frame)
        except ValueError as exc:
            raise SharedMCMFieldError(
                f"receptor dock {dock.dock_id} rejected its frame: {exc}"
            ) from exc
        overlap = set(receptor_contacts) & set(mapped)
        if overlap:
            raise SharedMCMFieldError(
                f"multiple docks target the same neurons: {sorted(overlap)}"
            )
        receptor_contacts.update(mapped)
    return receptor_contacts


def _validated_transient_inputs(
    docks: tuple[SharedFieldDock, ...],
    distribution: ReceptorDistribution,
    transient_inputs: TransientNeuronInputSet,
) -> dict[str, TransientNeuronDockInput]:
    if not isinstance(transient_inputs, TransientNeuronInputSet):
        raise SharedMCMFieldError(
            "transient field input must be one complete neuron input set"
        )

    expected_anatomy = {
        neuron_id: (dock.dock_id, carrier_id)
        for dock in docks
        for carrier_id, neuron_id in dock.dock_map.pairs
    }
    supplied = {
        item.neuron_id: item for item in transient_inputs.neuron_inputs
    }
    if set(supplied) != set(expected_anatomy):
        raise SharedMCMFieldError(
            "transient field input must match every shared dock neuron; "
            f"missing={sorted(set(expected_anatomy) - set(supplied))}, "
            f"unknown={sorted(set(supplied) - set(expected_anatomy))}"
        )
    for neuron_id, item in supplied.items():
        expected = expected_anatomy[neuron_id]
        if (item.dock_id, item.carrier_id) != expected:
            raise SharedMCMFieldError(
                f"transient input anatomy mismatch for neuron {neuron_id}"
            )

    field_time = distribution.field_time
    step_time = transient_inputs.step_time
    if (
        step_time.clock_id != field_time.clock_id
        or step_time.start_tick != field_time.window_start_tick
        or step_time.end_tick != field_time.window_end_tick
    ):
        raise SharedMCMFieldError(
            "transient input time must equal the distributed field interval"
        )
    return supplied


@dataclass(frozen=True, slots=True)
class SharedMCMFieldSnapshot:
    """Serializable current runtime state, not organic memory or a pattern store."""

    schema_version: int
    layer: MCMNeuronLayer
    docks: tuple[SharedFieldDock, ...]
    last_distribution: ReceptorDistribution
    substrate: MCMSubstrateState | None = None
    development: MCMLocalDevelopmentState | None = None

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version
            not in (
                NEUTRAL_SNAPSHOT_SCHEMA_VERSION,
                F3_SNAPSHOT_SCHEMA_VERSION,
                S1B_SNAPSHOT_SCHEMA_VERSION,
            )
        ):
            raise SharedMCMFieldError("unsupported shared field snapshot schema")
        if not isinstance(self.layer, MCMNeuronLayer):
            raise SharedMCMFieldError("snapshot requires one complete neuron layer")
        docks = tuple(self.docks)
        if not docks or any(not isinstance(dock, SharedFieldDock) for dock in docks):
            raise SharedMCMFieldError("snapshot requires complete shared field docks")
        if not isinstance(self.last_distribution, ReceptorDistribution):
            raise SharedMCMFieldError(
                "snapshot requires the last completed receptor distribution"
            )
        if (
            self.schema_version == NEUTRAL_SNAPSHOT_SCHEMA_VERSION
            and self.substrate is not None
        ):
            raise SharedMCMFieldError(
                "snapshot schema 1 cannot contain a substrate state"
            )
        if self.schema_version == F3_SNAPSHOT_SCHEMA_VERSION and not isinstance(
            self.substrate, MCMSubstrateState
        ):
            raise SharedMCMFieldError(
                "snapshot schema 2 requires one complete substrate state"
            )
        if self.schema_version in (
            NEUTRAL_SNAPSHOT_SCHEMA_VERSION,
            F3_SNAPSHOT_SCHEMA_VERSION,
        ) and self.development is not None:
            raise SharedMCMFieldError(
                "snapshot schemas 1 and 2 cannot contain a development state"
            )
        if self.schema_version == S1B_SNAPSHOT_SCHEMA_VERSION:
            if self.substrate is not None:
                raise SharedMCMFieldError(
                    "snapshot schema 3 keeps M and L states separate"
                )
            if not isinstance(self.development, MCMLocalDevelopmentState):
                raise SharedMCMFieldError(
                    "snapshot schema 3 requires one complete development state"
                )
        SharedMCMField(
            self.layer,
            docks,
            self.last_distribution,
            substrate=self.substrate,
            development=self.development,
        )
        object.__setattr__(self, "docks", tuple(sorted(docks, key=lambda item: item.dock_id)))

    @property
    def field_id(self) -> str:
        return self.layer.neurons[0].field_id

    @property
    def layer_id(self) -> str:
        return self.layer.layer_id

    @property
    def geometry_id(self) -> str:
        return self.layer.neurons[0].geometry_id

    @property
    def clock_id(self) -> str:
        return self.last_distribution.field_time.clock_id

    @property
    def window_start_tick(self) -> int:
        return self.last_distribution.field_time.window_start_tick

    @property
    def window_end_tick(self) -> int:
        return self.last_distribution.field_time.window_end_tick

    @property
    def tick(self) -> int:
        return self.layer.tick

    @property
    def neuron_ids(self) -> tuple[str, ...]:
        return tuple(neuron.neuron_id for neuron in self.layer.neurons)

    @property
    def activation(self) -> tuple[float, ...]:
        return tuple(neuron.activation for neuron in self.layer.neurons)

    @property
    def afterimage(self) -> tuple[float, ...]:
        return tuple(neuron.afterimage for neuron in self.layer.neurons)

    @property
    def substrate_mass(self) -> tuple[float, ...] | None:
        if self.substrate is None:
            return None
        return tuple(item.mass for item in self.substrate.masses)

    @property
    def development_values(self) -> tuple[float, ...] | None:
        if self.development is None:
            return None
        return self.development.dispositions

    @property
    def dock_neuron_ids(self) -> tuple[tuple[str, tuple[str, ...]], ...]:
        return tuple(
            (dock.dock_id, dock.dock_map.neuron_ids) for dock in self.docks
        )

    def canonical_payload(self) -> dict[str, object]:
        payload = {
            "schema_version": self.schema_version,
            "layer": {
                "layer_id": self.layer.layer_id,
                "sample_offsets": [
                    list(offset) for offset in self.layer.sample_offsets
                ],
                "periodic_axes": [
                    axis.canonical_payload() for axis in self.layer.periodic_axes
                ],
                "receptor_dock_ids": list(self.layer.docked_neuron_ids),
                "neurons": [
                    neuron.canonical_payload() for neuron in self.layer.neurons
                ],
            },
            "docks": [
                {
                    "dock_id": dock.dock_id,
                    "modality_id": dock.dock_map.modality_id,
                    "receptor_geometry_id": dock.dock_map.receptor_geometry_id,
                    "pairs": [list(pair) for pair in dock.dock_map.pairs],
                }
                for dock in self.docks
            ],
            "last_distribution": self.last_distribution.canonical_payload(),
        }
        if self.schema_version == F3_SNAPSHOT_SCHEMA_VERSION:
            if self.substrate is None:
                raise SharedMCMFieldError(
                    "snapshot schema 2 requires its substrate payload"
                )
            payload["substrate"] = self.substrate.canonical_payload()
        if self.schema_version == S1B_SNAPSHOT_SCHEMA_VERSION:
            if self.development is None:
                raise SharedMCMFieldError(
                    "snapshot schema 3 requires its development payload"
                )
            payload["development"] = self.development.canonical_payload()
        return payload

    def fast_state_projection_payload(self) -> dict[str, object]:
        """Project any snapshot onto the complete historical schema-1 state."""

        payload = self.canonical_payload()
        payload["schema_version"] = 1
        payload.pop("substrate", None)
        payload.pop("development", None)
        return payload

    def fast_state_projection_digest(self) -> str:
        encoded = json.dumps(
            self.fast_state_projection_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_json(self) -> str:
        return json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def digest(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()

    @classmethod
    def from_json(cls, encoded: str | bytes) -> "SharedMCMFieldSnapshot":
        if isinstance(encoded, bytes):
            try:
                encoded = encoded.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise SharedMCMFieldError("snapshot bytes must be UTF-8") from exc
        if not isinstance(encoded, str):
            raise SharedMCMFieldError("snapshot JSON must be text or UTF-8 bytes")
        try:
            payload = json.loads(encoded)
        except json.JSONDecodeError as exc:
            raise SharedMCMFieldError("snapshot JSON is invalid") from exc
        try:
            if not isinstance(payload, Mapping):
                raise SharedMCMFieldError("snapshot must be an object")
            schema_version = payload.get("schema_version")
            if (
                isinstance(schema_version, bool)
                or not isinstance(schema_version, int)
                or schema_version
                not in (
                    NEUTRAL_SNAPSHOT_SCHEMA_VERSION,
                    F3_SNAPSHOT_SCHEMA_VERSION,
                    S1B_SNAPSHOT_SCHEMA_VERSION,
                )
            ):
                raise SharedMCMFieldError(
                    "unsupported shared field snapshot schema"
                )
            root_keys = set(NEUTRAL_SNAPSHOT_ROOT_KEYS)
            if schema_version == F3_SNAPSHOT_SCHEMA_VERSION:
                root_keys.add("substrate")
            if schema_version == S1B_SNAPSHOT_SCHEMA_VERSION:
                root_keys.add("development")
            root = _payload_mapping(
                payload,
                "snapshot",
                root_keys,
            )
            layer_payload = _payload_mapping(
                root["layer"],
                "snapshot layer",
                {
                    "layer_id",
                    "sample_offsets",
                    "periodic_axes",
                    "receptor_dock_ids",
                    "neurons",
                },
            )
            neurons = []
            for neuron_value in _payload_sequence(
                layer_payload["neurons"], "snapshot neurons"
            ):
                neuron_payload = _payload_mapping(
                    neuron_value,
                    "snapshot neuron",
                    {
                        "neuron_id",
                        "field_id",
                        "modality_id",
                        "geometry_id",
                        "position",
                        "activation",
                        "afterimage",
                        "perception",
                    },
                )
                perception_payload = _payload_mapping(
                    neuron_payload["perception"],
                    "snapshot perception",
                    {"tick", "receptor_contact", "local_samples"},
                )
                samples = []
                for sample_value in _payload_sequence(
                    perception_payload["local_samples"],
                    "snapshot local samples",
                ):
                    sample_payload = _payload_mapping(
                        sample_value,
                        "snapshot local sample",
                        {
                            "sample_id",
                            "source_field_id",
                            "source_tick",
                            "relative_position",
                            "activation",
                            "afterimage",
                        },
                    )
                    samples.append(
                        MCMFieldSample(
                            sample_id=sample_payload["sample_id"],
                            source_field_id=sample_payload["source_field_id"],
                            source_tick=sample_payload["source_tick"],
                            relative_position=tuple(
                                _payload_sequence(
                                    sample_payload["relative_position"],
                                    "sample relative position",
                                )
                            ),
                            activation=sample_payload["activation"],
                            afterimage=sample_payload["afterimage"],
                        )
                    )
                neurons.append(
                    MCMNeuron(
                        neuron_id=neuron_payload["neuron_id"],
                        field_id=neuron_payload["field_id"],
                        modality_id=neuron_payload["modality_id"],
                        geometry_id=neuron_payload["geometry_id"],
                        position=tuple(
                            _payload_sequence(
                                neuron_payload["position"], "neuron position"
                            )
                        ),
                        activation=neuron_payload["activation"],
                        afterimage=neuron_payload["afterimage"],
                        perception=MCMFieldPerception(
                            tick=perception_payload["tick"],
                            receptor_contact=perception_payload["receptor_contact"],
                            local_samples=tuple(samples),
                        ),
                    )
                )
            axes = []
            for axis_value in _payload_sequence(
                layer_payload["periodic_axes"], "snapshot periodic axes"
            ):
                axis_payload = _payload_mapping(
                    axis_value,
                    "snapshot periodic axis",
                    {"axis_index", "origin", "size"},
                )
                axes.append(PeriodicSamplingAxis(**axis_payload))
            layer = MCMNeuronLayer(
                layer_id=layer_payload["layer_id"],
                neurons=tuple(neurons),
                sample_offsets=tuple(
                    tuple(_payload_sequence(offset, "snapshot sample offset"))
                    for offset in _payload_sequence(
                        layer_payload["sample_offsets"], "snapshot sample offsets"
                    )
                ),
                periodic_axes=tuple(axes),
                receptor_dock_ids=tuple(
                    _payload_sequence(
                        layer_payload["receptor_dock_ids"],
                        "snapshot receptor dock neuron ids",
                    )
                ),
            )

            docks = []
            for dock_value in _payload_sequence(root["docks"], "snapshot docks"):
                dock_payload = _payload_mapping(
                    dock_value,
                    "snapshot dock",
                    {
                        "dock_id",
                        "modality_id",
                        "receptor_geometry_id",
                        "pairs",
                    },
                )
                docks.append(
                    SharedFieldDock(
                        dock_id=dock_payload["dock_id"],
                        dock_map=ReceptorNeuronDockMap(
                            modality_id=dock_payload["modality_id"],
                            receptor_geometry_id=dock_payload[
                                "receptor_geometry_id"
                            ],
                            pairs=tuple(
                                tuple(_payload_sequence(pair, "snapshot dock pair"))
                                for pair in _payload_sequence(
                                    dock_payload["pairs"], "snapshot dock pairs"
                                )
                            ),
                        ),
                    )
                )

            distribution_payload = _payload_mapping(
                root["last_distribution"],
                "snapshot distribution",
                {"field_time", "contacts"},
            )
            time_payload = _payload_mapping(
                distribution_payload["field_time"],
                "snapshot field time",
                {"clock_id", "window_start_tick", "window_end_tick"},
            )
            contacts = []
            for contact_value in _payload_sequence(
                distribution_payload["contacts"], "snapshot contacts"
            ):
                contact_payload = _payload_mapping(
                    contact_value,
                    "snapshot contact",
                    {
                        "dock_id",
                        "modality_id",
                        "geometry_id",
                        "snapshot_id",
                        "source_clock_id",
                        "source_window_start_tick",
                        "source_window_end_tick",
                        "carrier_ids",
                        "values",
                    },
                )
                contacts.append(
                    DistributedReceptorContact(
                        dock_id=contact_payload["dock_id"],
                        frame=ReceptorContactFrame(
                            modality_id=contact_payload["modality_id"],
                            geometry_id=contact_payload["geometry_id"],
                            snapshot_id=contact_payload["snapshot_id"],
                            clock_id=contact_payload["source_clock_id"],
                            window_start_tick=contact_payload[
                                "source_window_start_tick"
                            ],
                            window_end_tick=contact_payload[
                                "source_window_end_tick"
                            ],
                            carrier_ids=tuple(
                                _payload_sequence(
                                    contact_payload["carrier_ids"],
                                    "snapshot carrier ids",
                                )
                            ),
                            values=tuple(
                                _payload_sequence(
                                    contact_payload["values"],
                                    "snapshot receptor values",
                                )
                            ),
                        ),
                    )
                )
            distribution = ReceptorDistribution(
                field_time=CommonFieldTime(**time_payload),
                contacts=tuple(contacts),
            )
            substrate = (
                None
                if schema_version != 2
                else MCMSubstrateState.from_payload(root["substrate"])
            )
            development = (
                None
                if schema_version != 3
                else MCMLocalDevelopmentState.from_payload(root["development"])
            )
            return cls(
                schema_version=schema_version,
                layer=layer,
                docks=tuple(docks),
                last_distribution=distribution,
                substrate=substrate,
                development=development,
            )
        except SharedMCMFieldError:
            raise
        except (KeyError, TypeError, ValueError) as exc:
            raise SharedMCMFieldError(
                f"snapshot payload violates the runtime contract: {exc}"
            ) from exc


@dataclass(frozen=True, slots=True)
class SharedMCMField:
    """One organism field; all receptor docks drive one synchronous layer."""

    layer: MCMNeuronLayer
    docks: tuple[SharedFieldDock, ...]
    last_distribution: ReceptorDistribution | None = None
    substrate: MCMSubstrateState | None = None
    development: MCMLocalDevelopmentState | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.layer, MCMNeuronLayer):
            raise SharedMCMFieldError("shared field requires one MCM neuron layer")
        docks = tuple(self.docks)
        if not docks or any(not isinstance(item, SharedFieldDock) for item in docks):
            raise SharedMCMFieldError("shared field requires receptor docks")
        dock_ids = [item.dock_id for item in docks]
        modalities = [item.dock_map.modality_id for item in docks]
        if len(set(dock_ids)) != len(dock_ids):
            raise SharedMCMFieldError("shared field dock identities must be unique")
        if len(set(modalities)) != len(modalities):
            raise SharedMCMFieldError("shared field modalities must be unique")
        mapped_ids = [
            neuron_id
            for item in docks
            for neuron_id in item.dock_map.neuron_ids
        ]
        layer_ids = {neuron.neuron_id for neuron in self.layer.neurons}
        if len(set(mapped_ids)) != len(mapped_ids):
            raise SharedMCMFieldError("one neuron cannot receive multiple docks")
        if set(mapped_ids) != set(self.layer.docked_neuron_ids):
            raise SharedMCMFieldError(
                "shared layer receptor contacts must match all dock maps"
            )
        if not set(mapped_ids).issubset(layer_ids):
            raise SharedMCMFieldError("dock map contains an unknown field neuron")
        if len({neuron.field_id for neuron in self.layer.neurons}) != 1:
            raise SharedMCMFieldError("all neurons must belong to the same field")
        if self.substrate is not None:
            if not isinstance(self.substrate, MCMSubstrateState):
                raise SharedMCMFieldError(
                    "shared field substrate must be one complete M state"
                )
            expected_ids = tuple(
                neuron.neuron_id for neuron in self.layer.neurons
            )
            if self.substrate.neuron_ids != expected_ids:
                raise SharedMCMFieldError(
                    "substrate masses must match every field neuron exactly"
                )
            try:
                expected_edge_digest = mcm_substrate_edge_inventory_digest(
                    self.layer
                )
            except MCMSubstrateStateError as exc:
                raise SharedMCMFieldError(str(exc)) from exc
            if self.substrate.edge_inventory_digest != expected_edge_digest:
                raise SharedMCMFieldError(
                    "substrate edge inventory does not match field geometry"
                )
        if self.development is not None:
            if self.substrate is not None:
                raise SharedMCMFieldError(
                    "the first L corridor keeps M and L states separate"
                )
            if not isinstance(self.development, MCMLocalDevelopmentState):
                raise SharedMCMFieldError(
                    "shared field development must be one complete L state"
                )
            expected_ids = tuple(
                neuron.neuron_id for neuron in self.layer.neurons
            )
            if self.development.neuron_ids != expected_ids:
                raise SharedMCMFieldError(
                    "development values must match every field neuron exactly"
                )
        if self.last_distribution is not None:
            if not isinstance(self.last_distribution, ReceptorDistribution):
                raise SharedMCMFieldError(
                    "last_distribution must be a completed receptor distribution"
                )
            if self.layer.tick == 0:
                raise SharedMCMFieldError(
                    "an initial field cannot have a completed distribution"
                )
            mapped_contacts = _mapped_receptor_contacts(
                tuple(docks),
                self.last_distribution,
            )
            for neuron in self.layer.neurons:
                expected_contact = mapped_contacts.get(neuron.neuron_id)
                if neuron.perception.receptor_contact != expected_contact:
                    raise SharedMCMFieldError(
                        "last distribution does not match current neuron perception"
                    )
        object.__setattr__(self, "docks", tuple(sorted(docks, key=lambda item: item.dock_id)))

    @property
    def field_id(self) -> str:
        return self.layer.neurons[0].field_id

    @property
    def geometry_id(self) -> str:
        return self.layer.neurons[0].geometry_id

    def advance(
        self,
        distribution: ReceptorDistribution,
        transition: MCMNeuronTransition,
        *,
        step_time: MCMFieldStepTime | None = None,
        transient_neuron_inputs: TransientNeuronInputSet | None = None,
    ) -> "SharedMCMField":
        if self.development is not None:
            raise SharedMCMFieldError(
                "development coupling requires the dedicated S1-B runtime"
            )
        if (
            self.substrate is not None
            and not self.substrate.arm.is_null_arm
        ):
            raise SharedMCMFieldError(
                "active substrate coupling requires the dedicated F3 runtime"
            )
        if not isinstance(distribution, ReceptorDistribution):
            raise SharedMCMFieldError(
                "world contact must arrive through the receptor distributor"
            )
        if self.last_distribution is not None:
            previous_time = self.last_distribution.field_time
            current_time = distribution.field_time
            if current_time.clock_id != previous_time.clock_id:
                raise SharedMCMFieldError("organism clock cannot change")
            if current_time.window_end_tick <= previous_time.window_end_tick:
                raise SharedMCMFieldError("common field time must advance")

        receptor_contacts = _mapped_receptor_contacts(self.docks, distribution)
        if step_time is not None:
            if not isinstance(step_time, MCMFieldStepTime):
                raise SharedMCMFieldError(
                    "step_time must be one explicit MCM field step"
                )
            field_time = distribution.field_time
            if (
                step_time.clock_id != field_time.clock_id
                or step_time.start_tick != field_time.window_start_tick
                or step_time.end_tick != field_time.window_end_tick
            ):
                raise SharedMCMFieldError(
                    "step_time must match the distributed organism interval"
                )

        local_inputs = None
        if transient_neuron_inputs is not None:
            local_inputs = _validated_transient_inputs(
                self.docks,
                distribution,
                transient_neuron_inputs,
            )
            transient_step_time = transient_neuron_inputs.step_time
            if step_time is not None and step_time != transient_step_time:
                raise SharedMCMFieldError(
                    "explicit and transient step_time must be identical"
                )
            step_time = transient_step_time

        try:
            next_layer = self.layer.advance(
                receptor_contacts,
                transition,
                allow_missing_contacts=True,
                step_time=step_time,
                transient_receptor_inputs=local_inputs,
            )
        except ValueError as exc:
            raise SharedMCMFieldError(f"shared neuron layer advance failed: {exc}") from exc
        return SharedMCMField(
            next_layer,
            self.docks,
            distribution,
            substrate=self.substrate,
            development=self.development,
        )

    def snapshot(self) -> SharedMCMFieldSnapshot:
        if self.last_distribution is None:
            raise SharedMCMFieldError(
                "shared field has no completed receptor-driven state"
            )
        return SharedMCMFieldSnapshot(
            schema_version=(
                S1B_SNAPSHOT_SCHEMA_VERSION
                if self.development is not None
                else (
                    NEUTRAL_SNAPSHOT_SCHEMA_VERSION
                    if self.substrate is None
                    else F3_SNAPSHOT_SCHEMA_VERSION
                )
            ),
            layer=self.layer,
            docks=self.docks,
            last_distribution=self.last_distribution,
            substrate=self.substrate,
            development=self.development,
        )


def restore_shared_mcm_field(
    snapshot: SharedMCMFieldSnapshot,
) -> SharedMCMField:
    """Restore only the serialized runtime state, without adding field behavior."""

    if not isinstance(snapshot, SharedMCMFieldSnapshot):
        raise SharedMCMFieldError(
            "shared field restoration requires a validated field snapshot"
        )
    independent = SharedMCMFieldSnapshot.from_json(snapshot.to_json())
    restored = SharedMCMField(
        layer=independent.layer,
        docks=independent.docks,
        last_distribution=independent.last_distribution,
        substrate=independent.substrate,
        development=independent.development,
    )
    if restored.snapshot().digest() != snapshot.digest():
        raise SharedMCMFieldError("restored shared field differs from its snapshot")
    return restored


def attach_uniform_mcm_substrate(
    field: SharedMCMField,
    arm: MCMSubstrateArmContract,
) -> SharedMCMField:
    """Attach the explicit uniform scheme-A M reference to one field."""

    if not isinstance(field, SharedMCMField):
        raise SharedMCMFieldError(
            "substrate attachment requires one shared MCM field"
        )
    if field.substrate is not None:
        raise SharedMCMFieldError("shared field already contains a substrate")
    if field.development is not None:
        raise SharedMCMFieldError(
            "the first L corridor keeps M and L states separate"
        )
    if not isinstance(arm, MCMSubstrateArmContract):
        raise SharedMCMFieldError(
            "substrate attachment requires one fixed arm contract"
        )
    if not arm.is_null_arm:
        raise SharedMCMFieldError(
            "scheme A can attach only the exact null substrate arm"
        )
    try:
        substrate = build_uniform_mcm_substrate(field.layer, arm)
    except MCMSubstrateStateError as exc:
        raise SharedMCMFieldError(str(exc)) from exc
    return SharedMCMField(
        layer=field.layer,
        docks=field.docks,
        last_distribution=field.last_distribution,
        substrate=substrate,
    )


def attach_zero_mcm_local_development(
    field: SharedMCMField,
    contract: MCMLocalDevelopmentContract,
) -> SharedMCMField:
    """Attach the explicit zero L state without changing the fast field."""

    if not isinstance(field, SharedMCMField):
        raise SharedMCMFieldError(
            "development attachment requires one shared MCM field"
        )
    if field.substrate is not None or field.development is not None:
        raise SharedMCMFieldError(
            "development attachment requires a field without M or L state"
        )
    if not isinstance(contract, MCMLocalDevelopmentContract):
        raise SharedMCMFieldError(
            "development attachment requires one fixed nature contract"
        )
    try:
        development = build_zero_mcm_local_development(field.layer, contract)
    except MCMLocalDevelopmentStateError as exc:
        raise SharedMCMFieldError(str(exc)) from exc
    return SharedMCMField(
        layer=field.layer,
        docks=field.docks,
        last_distribution=field.last_distribution,
        development=development,
    )


def migrate_shared_mcm_field_snapshot_to_schema2(
    snapshot: SharedMCMFieldSnapshot,
    arm: MCMSubstrateArmContract,
) -> SharedMCMFieldSnapshot:
    """Explicitly add the uniform null M reference to one schema-1 snapshot."""

    if not isinstance(snapshot, SharedMCMFieldSnapshot):
        raise SharedMCMFieldError(
            "snapshot migration requires one validated field snapshot"
        )
    if snapshot.schema_version != 1 or snapshot.substrate is not None:
        raise SharedMCMFieldError(
            "only a historical schema-1 snapshot can migrate to schema 2"
        )
    migrated = attach_uniform_mcm_substrate(
        SharedMCMField(
            layer=snapshot.layer,
            docks=snapshot.docks,
            last_distribution=snapshot.last_distribution,
        ),
        arm,
    )
    result = migrated.snapshot()
    if result.fast_state_projection_digest() != snapshot.digest():
        raise SharedMCMFieldError(
            "schema-2 migration changed the historical fast field projection"
        )
    return result


def build_shared_mcm_field(
    reference_frames: Iterable[ReceptorContactFrame],
    anatomies: Mapping[str, ReceptorDockAnatomy],
    *,
    sample_offsets: Iterable[Iterable[int]],
    field_id: str = "organism.mcm_field",
    layer_id: str = "organism.mcm_layer",
    geometry_id: str = "organism.shared.v1",
) -> SharedMCMField:
    """Build one layer in one shared geometry without modality partitions."""

    field_id = _identifier(field_id, "field_id")
    layer_id = _identifier(layer_id, "layer_id")
    geometry_id = _identifier(geometry_id, "geometry_id")
    frames = tuple(reference_frames)
    if not frames:
        raise SharedMCMFieldError("shared field requires reference receptor frames")
    frame_by_modality = {frame.modality_id: frame for frame in frames}
    if len(frame_by_modality) != len(frames):
        raise SharedMCMFieldError("reference modalities must be unique")
    anatomy_by_modality = dict(anatomies)
    if set(frame_by_modality) != set(anatomy_by_modality):
        raise SharedMCMFieldError(
            "dock anatomies must match the reference receptor modalities"
        )

    local_dimensions = {
        len(anatomy.positions[0]) for anatomy in anatomy_by_modality.values()
    }
    if len(local_dimensions) != 1:
        raise SharedMCMFieldError(
            "all receptor docks must expose one compatible local dimension"
        )
    dimension = next(iter(local_dimensions))
    shared_offsets = tuple(tuple(offset) for offset in sample_offsets)
    if not shared_offsets:
        raise SharedMCMFieldError(
            "shared field requires explicit local sample offsets"
        )
    if any(len(offset) != dimension for offset in shared_offsets):
        raise SharedMCMFieldError(
            "shared field sample offsets must match the field dimension"
        )

    neurons = []
    shared_docks = []
    shared_positions: set[tuple[int, ...]] = set()
    for modality_id in sorted(frame_by_modality):
        frame = frame_by_modality[modality_id]
        anatomy = anatomy_by_modality[modality_id]
        if anatomy.modality_id != modality_id:
            raise SharedMCMFieldError("dock anatomy modality mismatch")
        if len(anatomy.positions) != len(frame.carrier_ids):
            raise SharedMCMFieldError(
                "one shared field position is required per receptor carrier"
            )
        overlap = shared_positions & set(anatomy.positions)
        if overlap:
            raise SharedMCMFieldError(
                f"receptor docks overlap in shared field positions: {sorted(overlap)}"
            )
        shared_positions.update(anatomy.positions)
        neuron_ids = tuple(
            f"{field_id}.{modality_id}.n{index}"
            for index in range(len(frame.carrier_ids))
        )
        for neuron_id, shared_position in zip(
            neuron_ids, anatomy.positions, strict=True
        ):
            neurons.append(
                MCMNeuron(
                    neuron_id=neuron_id,
                    field_id=field_id,
                    modality_id="organism",
                    geometry_id=geometry_id,
                    position=shared_position,
                    activation=0.0,
                    afterimage=0.0,
                    perception=MCMFieldPerception(
                        tick=0,
                        receptor_contact=0.0,
                        local_samples=(),
                    ),
                )
            )
        shared_docks.append(
            SharedFieldDock(
                dock_id=anatomy.dock_id,
                dock_map=ReceptorNeuronDockMap(
                    modality_id=modality_id,
                    receptor_geometry_id=frame.geometry_id,
                    pairs=tuple(
                        zip(frame.carrier_ids, neuron_ids, strict=True)
                    ),
                ),
            )
        )

    layer = MCMNeuronLayer(
        layer_id=layer_id,
        neurons=tuple(neurons),
        sample_offsets=shared_offsets,
    )
    return SharedMCMField(layer=layer, docks=tuple(shared_docks))


def shared_mcm_field_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            ReceptorDockAnatomy,
            SharedFieldDock,
            SharedMCMFieldSnapshot,
            SharedMCMField,
        )
        for item in fields(cls)
    )
