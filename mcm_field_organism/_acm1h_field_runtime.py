"""Private atomic ACM-1H integration for the four-node field corridor."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math

import numpy as np

from ._acm1h_reference import (
    ACM1H_NODE_IDS,
    ACM1HConfigRecord,
    ACM1HPrestateRecord,
    acm1h_edge_inventory_digest,
    run_acm1h_reference,
)
from .field_step_time import MCMFieldStepTime
from .mcm_neuron_layer import MCMNeuronDrive, MCMNeuronOutput
from .mcm_substrate_state import mcm_substrate_edge_inventory
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    _diffusion_generator,
    _generator_and_boundary,
    _integrate_activation_afterimage_with_spectrum,
    _step_duration,
    advance_neutral_fast_shared_field,
)
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import SharedMCMField, SharedMCMFieldError


ACM1H_FIELD_STATE_SCHEMA_ID = "acm1h-field-state-v1"


class ACM1HFieldRuntimeError(ValueError):
    """One fail-closed violation of the private ACM-1H field transaction."""


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _finite_z(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise ACM1HFieldRuntimeError(f"{role} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ACM1HFieldRuntimeError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or abs(result) > 1.0:
        raise ACM1HFieldRuntimeError(f"{role} must stay in [-1,1]")
    return result


def _field_digest(field: SharedMCMField) -> str:
    return _digest(
        {
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
            "substrate_digest": (
                None if field.substrate is None else field.substrate.digest()
            ),
            "development_digest": (
                None if field.development is None else field.development.digest()
            ),
        }
    )


def _geometry_digest(field: SharedMCMField) -> str:
    return _digest(
        {
            "field_id": field.field_id,
            "layer_id": field.layer.layer_id,
            "geometry_id": field.geometry_id,
            "nodes": [
                [neuron.neuron_id, list(neuron.position)]
                for neuron in field.layer.neurons
            ],
            "sample_offsets": [list(item) for item in field.layer.sample_offsets],
            "periodic_axes": [
                axis.canonical_payload() for axis in field.layer.periodic_axes
            ],
            "edges": [list(edge) for edge in mcm_substrate_edge_inventory(field.layer)],
        }
    )


def _validate_geometry(field: object) -> SharedMCMField:
    if not isinstance(field, SharedMCMField):
        raise ACM1HFieldRuntimeError("one SharedMCMField is required")
    if tuple(neuron.neuron_id for neuron in field.layer.neurons) != ACM1H_NODE_IDS:
        raise ACM1HFieldRuntimeError("ACM-1H requires node-a through node-d")
    if mcm_substrate_edge_inventory(field.layer) != (
        ("node-a", "node-b"),
        ("node-b", "node-c"),
        ("node-c", "node-d"),
    ):
        raise ACM1HFieldRuntimeError("ACM-1H requires the open four-node line")
    if field.substrate is not None or field.development is not None:
        raise ACM1HFieldRuntimeError(
            "the private ACM-1H corridor requires the neutral field projection"
        )
    return field


def _state_payload(
    *,
    configuration_digest: str,
    geometry_id: str,
    edge_inventory_digest: str,
    field_tick: int,
    field_time_endpoint: int,
    z_left: float,
    z_right: float,
) -> dict[str, object]:
    return {
        "schema_id": ACM1H_FIELD_STATE_SCHEMA_ID,
        "configuration_digest": configuration_digest,
        "geometry_id": geometry_id,
        "edge_inventory_digest": edge_inventory_digest,
        "field_tick": field_tick,
        "field_time_endpoint": field_time_endpoint,
        "z_left": z_left,
        "z_right": z_right,
    }


@dataclass(frozen=True, slots=True)
class ACM1HPrivateState:
    schema_id: str
    configuration_digest: str
    geometry_id: str
    edge_inventory_digest: str
    field_tick: int
    field_time_endpoint: int
    z_left: float
    z_right: float
    state_digest: str

    def __post_init__(self) -> None:
        if self.schema_id != ACM1H_FIELD_STATE_SCHEMA_ID:
            raise ACM1HFieldRuntimeError("private state schema differs")
        if (
            isinstance(self.field_tick, bool)
            or isinstance(self.field_time_endpoint, bool)
            or not isinstance(self.field_tick, int)
            or not isinstance(self.field_time_endpoint, int)
            or self.field_tick < 0
            or self.field_time_endpoint < 0
        ):
            raise ACM1HFieldRuntimeError("private state time roles are invalid")
        left = _finite_z(self.z_left, "z_left")
        right = _finite_z(self.z_right, "z_right")
        payload = _state_payload(
            configuration_digest=self.configuration_digest,
            geometry_id=self.geometry_id,
            edge_inventory_digest=self.edge_inventory_digest,
            field_tick=self.field_tick,
            field_time_endpoint=self.field_time_endpoint,
            z_left=left,
            z_right=right,
        )
        if self.state_digest != _digest(payload):
            raise ACM1HFieldRuntimeError("private state digest differs")
        object.__setattr__(self, "z_left", left)
        object.__setattr__(self, "z_right", right)


def _new_private_state(
    config: ACM1HConfigRecord,
    field: SharedMCMField,
    field_time_endpoint: int,
    motif_states: tuple[float, float],
) -> ACM1HPrivateState:
    left = _finite_z(motif_states[0], "z_left")
    right = _finite_z(motif_states[1], "z_right")
    payload = _state_payload(
        configuration_digest=config.digest(),
        geometry_id=field.geometry_id,
        edge_inventory_digest=acm1h_edge_inventory_digest(),
        field_tick=field.layer.tick,
        field_time_endpoint=field_time_endpoint,
        z_left=left,
        z_right=right,
    )
    return ACM1HPrivateState(
        **payload,
        state_digest=_digest(payload),
    )


def _carry_payload(
    field_digest: str,
    state: ACM1HPrivateState,
    geometry_digest: str,
) -> dict[str, object]:
    return {
        "field_digest": field_digest,
        "private_state_digest": state.state_digest,
        "configuration_digest": state.configuration_digest,
        "geometry_digest": geometry_digest,
        "edge_inventory_digest": state.edge_inventory_digest,
    }


@dataclass(frozen=True, slots=True)
class ACM1HFieldCarry:
    field: SharedMCMField
    private_state: ACM1HPrivateState
    field_digest: str
    private_state_digest: str
    configuration_digest: str
    geometry_digest: str
    edge_inventory_digest: str
    carry_digest: str

    def __post_init__(self) -> None:
        field = _validate_geometry(self.field)
        if not isinstance(self.private_state, ACM1HPrivateState):
            raise ACM1HFieldRuntimeError("carry requires one private state")
        state = self.private_state
        current_geometry_digest = _geometry_digest(field)
        if (
            self.field_digest != _field_digest(field)
            or self.private_state_digest != state.state_digest
            or self.configuration_digest != state.configuration_digest
            or self.geometry_digest != current_geometry_digest
            or self.edge_inventory_digest != state.edge_inventory_digest
            or state.geometry_id != field.geometry_id
            or state.field_tick != field.layer.tick
        ):
            raise ACM1HFieldRuntimeError("field/private carry bindings differ")
        if state.edge_inventory_digest != acm1h_edge_inventory_digest():
            raise ACM1HFieldRuntimeError("private edge inventory differs")
        expected_endpoint = (
            0
            if field.last_distribution is None
            else field.last_distribution.field_time.window_end_tick
        )
        if state.field_time_endpoint != expected_endpoint:
            raise ACM1HFieldRuntimeError("field/private carry time differs")
        if self.carry_digest != _digest(
            _carry_payload(self.field_digest, state, current_geometry_digest)
        ):
            raise ACM1HFieldRuntimeError("carry digest differs")


def _new_carry(
    field: SharedMCMField,
    state: ACM1HPrivateState,
) -> ACM1HFieldCarry:
    field_digest = _field_digest(field)
    geometry_digest = _geometry_digest(field)
    payload = _carry_payload(field_digest, state, geometry_digest)
    return ACM1HFieldCarry(
        field=field,
        private_state=state,
        field_digest=field_digest,
        private_state_digest=state.state_digest,
        configuration_digest=state.configuration_digest,
        geometry_digest=geometry_digest,
        edge_inventory_digest=state.edge_inventory_digest,
        carry_digest=_digest(payload),
    )


def build_acm1h_field_carry(
    field: object,
    config: object,
    *,
    motif_states: tuple[float, float] = (0.0, 0.0),
) -> ACM1HFieldCarry:
    """Bind one private in-memory state to an unchanged four-node field."""

    validated_field = _validate_geometry(field)
    if not isinstance(config, ACM1HConfigRecord):
        raise ACM1HFieldRuntimeError("validated ACM1HConfigRecord required")
    if not isinstance(motif_states, tuple) or len(motif_states) != 2:
        raise ACM1HFieldRuntimeError("exactly two motif states are required")
    endpoint = (
        0
        if validated_field.last_distribution is None
        else validated_field.last_distribution.field_time.window_end_tick
    )
    state = _new_private_state(config, validated_field, endpoint, motif_states)
    return _new_carry(validated_field, state)


def _advance_with_generator(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None,
    acm_generator: tuple[tuple[float, ...], ...],
) -> SharedMCMField:
    try:
        elapsed = _step_duration(distribution, step_time)
        neutral_generator, boundary = _generator_and_boundary(
            field, distribution, substrate_config
        )
        neutral_internal = _diffusion_generator(field, substrate_config)
        generator = (
            np.asarray(acm_generator, dtype=np.float64)
            + neutral_generator
            - neutral_internal
        )
        if generator.shape != (4, 4) or not np.array_equal(generator, generator.T):
            raise ACM1HFieldRuntimeError(
                "composed generator is not symmetric 4x4"
            )
        eigenvalues, eigenvectors = np.linalg.eigh(generator)
        neurons = field.layer.neurons
        leak_rate = (
            0.0
            if dissipation_config is None
            else dissipation_config.leak_rate_per_second
        )
        activation, afterimage = _integrate_activation_afterimage_with_spectrum(
            np.asarray([item.activation for item in neurons], dtype=np.float64),
            np.asarray([item.afterimage for item in neurons], dtype=np.float64),
            eigenvalues,
            eigenvectors,
            boundary,
            elapsed,
            afterimage_config.time_constant_seconds,
            leak_rate,
        )
        outputs = {
            neuron.neuron_id: MCMNeuronOutput(
                float(activation[index]), float(afterimage[index])
            )
            for index, neuron in enumerate(neurons)
        }

        def exact_acm1h_output(drive: MCMNeuronDrive) -> MCMNeuronOutput:
            return outputs[drive.previous.neuron_id]

        return field.advance(
            distribution,
            exact_acm1h_output,
            step_time=step_time,
        )
    except (
        ACM1HFieldRuntimeError,
        NeutralLocalFieldSubstrateError,
        SharedMCMFieldError,
        np.linalg.LinAlgError,
    ) as exc:
        raise ACM1HFieldRuntimeError(str(exc)) from exc


def advance_acm1h_four_node_field(
    carry: object,
    config: object,
    distribution: object,
    step_time: object,
    substrate_config: object,
    afterimage_config: object,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
) -> ACM1HFieldCarry:
    """Commit one field/z sibling proposal or publish no successor carry."""

    if not isinstance(carry, ACM1HFieldCarry):
        raise ACM1HFieldRuntimeError("one validated ACM1HFieldCarry is required")
    # Revalidate the complete immutable pair before deriving any proposal.
    ACM1HFieldCarry(
        **{item.name: getattr(carry, item.name) for item in fields(ACM1HFieldCarry)}
    )
    if not isinstance(config, ACM1HConfigRecord):
        raise ACM1HFieldRuntimeError("validated ACM1HConfigRecord required")
    if config.digest() != carry.configuration_digest:
        raise ACM1HFieldRuntimeError("configuration differs from the carry binding")
    if not isinstance(distribution, ReceptorDistribution):
        raise ACM1HFieldRuntimeError("one receptor distribution is required")
    if not isinstance(step_time, MCMFieldStepTime):
        raise ACM1HFieldRuntimeError("one MCMFieldStepTime is required")
    if not isinstance(substrate_config, NeutralLocalFieldSubstrateConfig):
        raise ACM1HFieldRuntimeError("one substrate configuration is required")
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise ACM1HFieldRuntimeError("one afterimage configuration is required")
    if dissipation_config is not None and not isinstance(
        dissipation_config, NeutralFieldDissipationConfig
    ):
        raise ACM1HFieldRuntimeError("dissipation configuration is invalid")
    if distribution.field_time.window_start_tick != carry.private_state.field_time_endpoint:
        raise ACM1HFieldRuntimeError("next interval does not start at the carry endpoint")
    if (
        carry.field.last_distribution is not None
        and distribution.field_time.clock_id
        != carry.field.last_distribution.field_time.clock_id
    ):
        raise ACM1HFieldRuntimeError("field clock differs from the carry history")
    try:
        _step_duration(distribution, step_time)
    except NeutralLocalFieldSubstrateError as exc:
        raise ACM1HFieldRuntimeError(str(exc)) from exc

    base_rate = 1.0 / substrate_config.response_time_seconds
    prestate = ACM1HPrestateRecord(
        field_id=carry.field.field_id,
        geometry_id=carry.field.geometry_id,
        node_ids=ACM1H_NODE_IDS,
        activations=tuple(
            neuron.activation for neuron in carry.field.layer.neurons
        ),
        edge_rates_per_second=(base_rate, base_rate, base_rate),
        motif_states=(
            carry.private_state.z_left,
            carry.private_state.z_right,
        ),
        edge_inventory_digest=carry.edge_inventory_digest,
        clock_id=step_time.clock_id,
        interval_start_tick=step_time.start_tick,
        interval_end_tick=step_time.end_tick,
    )
    decision = run_acm1h_reference(config, prestate, step_time)
    if decision.status != "COMPLETED" or decision.composition is None:
        raise ACM1HFieldRuntimeError(
            f"ACM-1H proposal failed: {decision.error_code}"
        )
    next_field = _advance_with_generator(
        carry.field,
        distribution,
        step_time,
        substrate_config,
        afterimage_config,
        dissipation_config,
        decision.composition.generator,
    )
    next_state = _new_private_state(
        config,
        next_field,
        step_time.end_tick,
        tuple(item.z_next for item in decision.motif_proposals),
    )
    return _new_carry(next_field, next_state)


def advance_acm1h_off_four_node_field(
    field: object,
    distribution: object,
    step_time: object,
    substrate_config: object,
    afterimage_config: object,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
) -> SharedMCMField:
    """Bypass ACM before private-state construction and use the neutral path."""

    validated_field = _validate_geometry(field)
    try:
        return advance_neutral_fast_shared_field(
            validated_field,
            distribution,
            step_time,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
    except NeutralLocalFieldSubstrateError as exc:
        raise ACM1HFieldRuntimeError(str(exc)) from exc
