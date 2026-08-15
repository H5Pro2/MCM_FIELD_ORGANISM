"""Private pure S1-JO common interval materializer."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
import hashlib
import json
import math
import re
from typing import Mapping

from .dynamic_substrate_dts1_common_boundary import (
    DTS1CommonBoundaryError,
    apply_dts1_common_sh_boundary,
)
from .dynamic_substrate_dts1_common_boundary_2n import (
    DTS1CommonBoundary2NError,
    apply_dts1_common_sh_boundary_2n,
)
from .dynamic_substrate_s1jh_finite_common_interval_fixture_contract import (
    S1_JH_SOURCE_FIXTURES,
)
from .dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    S1_JK_ENVELOPE_FIXTURES,
)
from .dynamic_substrate_s1jn_finite_materialization_schema_contract import (
    S1_JN_FIELD_IDENTITY_FIXTURES,
    S1_JN_PRIVATE_STATE_SCHEMAS,
    S1_JN_RECEPTOR_COMPLETION_FIXTURES,
    S1_JN_TECHNICAL_TEST_MATRIX,
    build_dts1_s1jn_finite_materialization_schema_contract,
)
from .field_step_time import MCMFieldStepTime, MCMFieldStepTimeError
from .mcm_neuron import MCMNeuronValidationError
from .mcm_neuron_layer import MCMNeuronLayerError
from .mcm_local_development_state import MCMLocalDevelopmentStateError
from .mcm_substrate_state import MCMSubstrateStateError
from .receptor_contract import (
    CommonFieldTime,
    ReceptorContactFrame,
    ReceptorContractError,
)
from .receptor_distributor import (
    DistributedReceptorContact,
    ReceptorDistribution,
    ReceptorDistributionError,
)
from .shared_mcm_field import SharedMCMField, SharedMCMFieldError


class DTS1CommonIntervalMaterializationError(ValueError):
    """Raised before output when pure common interval materialization fails."""


S1_JO_IMPLEMENTATION_ID = "dynamic-substrate.pure-common-interval-materializer.s1jo.v1"
S1_JO_SOURCE_S1JN_DIGEST = (
    "b0edec20c6d27d98ba8a523c3034d8890b01cfe514eede1d72d05c2e548dd281"
)
S1_JO_MATRIX_CASE_IDS = tuple(row[0] for row in S1_JN_TECHNICAL_TEST_MATRIX)
S1_JO_DECISION = "PRIVATE_PURE_COMMON_INTERVAL_MATERIALIZER_IMPLEMENTED_TECHNICALLY_ACCEPTED"
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_MODEL_ROLES = tuple(row[0] for row in S1_JN_PRIVATE_STATE_SCHEMAS)
_PRIVATE_KEYS = {row[0]: row[1] for row in S1_JN_PRIVATE_STATE_SCHEMAS}
_GEOMETRY_BY_NODE_IDS = {
    tuple(node_id for node_id, _position in row[5]): row
    for row in S1_JN_FIELD_IDENTITY_FIXTURES
}
_CONTACT_BY_GEOMETRY = {
    row[1]: row for row in S1_JN_RECEPTOR_COMPLETION_FIXTURES
}
_SOURCE_BY_DIGEST = {row[-1]: row for row in S1_JH_SOURCE_FIXTURES}
_ENVELOPE_ROWS = tuple(tuple(row) for row in S1_JK_ENVELOPE_FIXTURES)


def _canonicalize(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise DTS1CommonIntervalMaterializationError(
                "canonical payload numbers must be finite"
            )
        return 0.0 if value == 0.0 else value
    if isinstance(value, (tuple, list)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise DTS1CommonIntervalMaterializationError(
                "canonical payload mapping keys must be strings"
            )
        return {
            key: _canonicalize(value[key])
            for key in sorted(value)
        }
    raise DTS1CommonIntervalMaterializationError(
        "canonical payload contains a non-value object"
    )


def _digest(payload: object) -> str:
    encoded = json.dumps(
        _canonicalize(payload),
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _require_digest(value: object, role: str, *, allow_none: bool) -> str | None:
    if value is None and allow_none:
        return None
    if not isinstance(value, str) or not _DIGEST_PATTERN.fullmatch(value):
        raise DTS1CommonIntervalMaterializationError(
            f"{role} must be one lowercase SHA-256 digest"
        )
    return value


@dataclass(frozen=True, slots=True)
class DTS1CommonIntervalEnvelopeFixture:
    sequence_digest: str
    ordinal: int
    canonical_node_ids: tuple[str, ...]
    edge_inventory_digest: str
    prestate_directive: str
    prestate_source_digest: str
    receptor_contact: tuple[float, ...]
    step_time: tuple[str, int, int, float]
    checkpoint_after_interval: bool
    interval_digest: str

    def __post_init__(self) -> None:
        values = (
            self.sequence_digest,
            self.ordinal,
            tuple(self.canonical_node_ids),
            self.edge_inventory_digest,
            self.prestate_directive,
            self.prestate_source_digest,
            tuple(self.receptor_contact),
            tuple(self.step_time),
            self.checkpoint_after_interval,
            self.interval_digest,
        )
        if values not in _ENVELOPE_ROWS:
            raise DTS1CommonIntervalMaterializationError(
                "envelope fixture must equal one complete S1-JK registration"
            )
        object.__setattr__(self, "canonical_node_ids", values[2])
        object.__setattr__(self, "receptor_contact", values[6])
        object.__setattr__(self, "step_time", values[7])

    def canonical_payload(self) -> dict[str, object]:
        return {field.name: getattr(self, field.name) for field in fields(self)}


S1_JO_ENVELOPE_FIXTURES = tuple(
    DTS1CommonIntervalEnvelopeFixture(*row) for row in _ENVELOPE_ROWS
)
_FIXTURE_BY_DIGEST = {item.interval_digest: item for item in S1_JO_ENVELOPE_FIXTURES}
_PREDECESSOR_BY_DIGEST = {
    fixture.interval_digest: next(
        (
            candidate.interval_digest
            for candidate in S1_JO_ENVELOPE_FIXTURES
            if candidate.sequence_digest == fixture.sequence_digest
            and candidate.ordinal == fixture.ordinal - 1
        ),
        None,
    )
    for fixture in S1_JO_ENVELOPE_FIXTURES
}


def canonical_dts1_common_interval_envelope_fixtures(
) -> tuple[DTS1CommonIntervalEnvelopeFixture, ...]:
    """Return the 23 immutable fixtures without materializing an interval."""

    return S1_JO_ENVELOPE_FIXTURES


@dataclass(frozen=True, slots=True)
class DTS1CommonIntervalPrivateState:
    model_role: str
    payload: tuple[tuple[str, object], ...]

    def __post_init__(self) -> None:
        if self.model_role not in _MODEL_ROLES:
            raise DTS1CommonIntervalMaterializationError(
                "private state model role is not registered"
            )
        payload = tuple(self.payload)
        if any(not isinstance(row, tuple) or len(row) != 2 for row in payload):
            raise DTS1CommonIntervalMaterializationError(
                "private state payload must contain key-value pairs"
            )
        keys = tuple(row[0] for row in payload)
        if keys != _PRIVATE_KEYS[self.model_role]:
            raise DTS1CommonIntervalMaterializationError(
                "private state payload keys do not match the model role"
            )
        _canonicalize(dict(payload))
        object.__setattr__(self, "payload", payload)

    def canonical_payload(self) -> dict[str, object]:
        return {"model_role": self.model_role, "state": dict(self.payload)}


@dataclass(frozen=True, slots=True)
class DTS1CommonModelInvocation:
    materialized_field: SharedMCMField
    receptor_distribution: ReceptorDistribution
    step_time: MCMFieldStepTime
    geometry_digest: str

    def __post_init__(self) -> None:
        if not isinstance(self.materialized_field, SharedMCMField):
            raise DTS1CommonIntervalMaterializationError(
                "model invocation requires one complete field"
            )
        if not isinstance(self.receptor_distribution, ReceptorDistribution):
            raise DTS1CommonIntervalMaterializationError(
                "model invocation requires one complete distribution"
            )
        if not isinstance(self.step_time, MCMFieldStepTime):
            raise DTS1CommonIntervalMaterializationError(
                "model invocation requires one complete step time"
            )
        _require_digest(self.geometry_digest, "geometry_digest", allow_none=False)


@dataclass(frozen=True, slots=True)
class DTS1CommonIntervalIntegrityRecord:
    common_exposure_digest: str
    private_prestate_digest: str
    materialized_input_digest: str
    orchestration_control_digest: str

    def __post_init__(self) -> None:
        for field in fields(self):
            _require_digest(getattr(self, field.name), field.name, allow_none=False)


@dataclass(frozen=True, slots=True)
class DTS1CommonIntervalMaterialization:
    model_invocation: DTS1CommonModelInvocation
    integrity_record: DTS1CommonIntervalIntegrityRecord

    def __post_init__(self) -> None:
        if not isinstance(self.model_invocation, DTS1CommonModelInvocation):
            raise DTS1CommonIntervalMaterializationError(
                "materialization requires one complete model invocation"
            )
        if not isinstance(self.integrity_record, DTS1CommonIntervalIntegrityRecord):
            raise DTS1CommonIntervalMaterializationError(
                "materialization requires one complete integrity record"
            )


def _field_payload(field: SharedMCMField) -> dict[str, object]:
    return {
        "schema_id": "mcm.s1jn.complete-field.v1",
        "layer": {
            "layer_id": field.layer.layer_id,
            "sample_offsets": field.layer.sample_offsets,
            "periodic_axes": tuple(
                axis.canonical_payload() for axis in field.layer.periodic_axes
            ),
            "receptor_dock_ids": field.layer.docked_neuron_ids,
            "neurons": tuple(
                neuron.canonical_payload() for neuron in field.layer.neurons
            ),
        },
        "docks": tuple(
            {
                "dock_id": dock.dock_id,
                "modality_id": dock.dock_map.modality_id,
                "receptor_geometry_id": dock.dock_map.receptor_geometry_id,
                "pairs": dock.dock_map.pairs,
            }
            for dock in field.docks
        ),
        "last_distribution": (
            None
            if field.last_distribution is None
            else field.last_distribution.canonical_payload()
        ),
        "substrate": (
            None if field.substrate is None else field.substrate.canonical_payload()
        ),
        "development": (
            None
            if field.development is None
            else field.development.canonical_payload()
        ),
    }


def _validate_field_identity(
    field: SharedMCMField,
    model_role: str,
    fixture: DTS1CommonIntervalEnvelopeFixture,
) -> tuple[object, ...]:
    if not isinstance(field, SharedMCMField):
        raise DTS1CommonIntervalMaterializationError(
            "input_field must be one complete SharedMCMField"
        )
    identity = _GEOMETRY_BY_NODE_IDS.get(fixture.canonical_node_ids)
    if identity is None:
        raise DTS1CommonIntervalMaterializationError(
            "envelope node identities have no S1-JN field fixture"
        )
    neurons = tuple(sorted(field.layer.neurons, key=lambda item: item.position))
    actual_nodes = tuple((item.neuron_id, item.position) for item in neurons)
    docks = field.docks
    expected = (
        field.field_id == identity[1],
        field.layer.layer_id == identity[2],
        field.geometry_id == identity[3],
        all(item.modality_id == identity[4] for item in neurons),
        actual_nodes == identity[5],
        field.layer.sample_offsets == identity[6],
        field.layer.periodic_axes == identity[7],
        field.layer.docked_neuron_ids == identity[8],
        len(docks) == 1,
        len(docks) == 1 and docks[0].dock_id == identity[9],
        len(docks) == 1 and docks[0].dock_map.modality_id == identity[4],
        len(docks) == 1 and docks[0].dock_map.receptor_geometry_id == identity[10],
        len(docks) == 1 and docks[0].dock_map.pairs == identity[11],
    )
    if not all(expected):
        raise DTS1CommonIntervalMaterializationError(
            "input field identity does not equal the S1-JN geometry fixture"
        )
    if field.development is not None:
        raise DTS1CommonIntervalMaterializationError(
            "S1-JN materialization permits no embedded development state"
        )
    if model_role in ("B3", "B4", "B5", "B6"):
        if field.substrate is None:
            raise DTS1CommonIntervalMaterializationError(
                "F3 baseline field requires its private embedded M state"
            )
    elif field.substrate is not None:
        raise DTS1CommonIntervalMaterializationError(
            "DTS1, B1 and B2 fields permit no embedded M state"
        )
    return identity


def _validate_private_state(
    model_role: str,
    private_state: DTS1CommonIntervalPrivateState,
    field: SharedMCMField,
) -> None:
    if not isinstance(private_state, DTS1CommonIntervalPrivateState):
        raise DTS1CommonIntervalMaterializationError(
            "private_state must be one complete private state object"
        )
    if private_state.model_role != model_role:
        raise DTS1CommonIntervalMaterializationError(
            "private state role does not match model_role"
        )
    payload = dict(private_state.payload)
    if model_role in ("B3", "B4", "B5", "B6"):
        if field.substrate is None or payload["embedded_M_state_digest"] != field.substrate.digest():
            raise DTS1CommonIntervalMaterializationError(
                "embedded M digest does not match the complete input field"
            )


def _validate_provenance(
    fixture: DTS1CommonIntervalEnvelopeFixture,
    field: SharedMCMField,
    prior_envelope_digest: str | None,
    prior_output_digest: str | None,
) -> None:
    predecessor = _PREDECESSOR_BY_DIGEST[fixture.interval_digest]
    if fixture.ordinal == 1:
        if prior_envelope_digest is not None or prior_output_digest is not None:
            raise DTS1CommonIntervalMaterializationError(
                "ordinal one requires null prior provenance"
            )
        if field.layer.tick != 0 or field.last_distribution is not None:
            raise DTS1CommonIntervalMaterializationError(
                "ordinal one requires one fresh field"
            )
        for neuron in field.layer.neurons:
            if (
                neuron.activation != 0.0
                or neuron.afterimage != 0.0
                or neuron.perception.tick != 0
                or neuron.perception.receptor_contact != 0.0
                or neuron.perception.local_samples
            ):
                raise DTS1CommonIntervalMaterializationError(
                    "fresh field fast state and perception must be exact zero"
                )
        return
    if prior_envelope_digest != predecessor:
        raise DTS1CommonIntervalMaterializationError(
            "prior envelope digest does not match the same sequence predecessor"
        )
    _require_digest(prior_output_digest, "prior_output_digest", allow_none=False)
    if field.last_distribution is None:
        raise DTS1CommonIntervalMaterializationError(
            "noninitial field requires one completed prior distribution"
        )
    previous_time = field.last_distribution.field_time
    clock_id, start_tick, _end_tick, _rate = fixture.step_time
    if (
        previous_time.clock_id != clock_id
        or previous_time.window_end_tick != start_tick
    ):
        raise DTS1CommonIntervalMaterializationError(
            "carried field time does not meet the corrected interval boundary"
        )
    if (
        fixture.prestate_directive == "CARRY_PRIOR_SH"
        and fixture.prestate_source_digest != prior_envelope_digest
    ):
        raise DTS1CommonIntervalMaterializationError(
            "carry source digest does not equal the prior envelope digest"
        )


def _distribution_and_step(
    identity: tuple[object, ...],
    fixture: DTS1CommonIntervalEnvelopeFixture,
) -> tuple[ReceptorDistribution, MCMFieldStepTime]:
    contact = _CONTACT_BY_GEOMETRY[identity[0]]
    if tuple(contact[10]) != fixture.receptor_contact:
        raise DTS1CommonIntervalMaterializationError(
            "envelope contact does not match the receptor completion fixture"
        )
    clock_id, start_tick, end_tick, rate = fixture.step_time
    frame = ReceptorContactFrame(
        modality_id=contact[2],
        geometry_id=contact[3],
        snapshot_id=contact[5],
        clock_id=contact[6],
        window_start_tick=contact[7],
        window_end_tick=contact[8],
        carrier_ids=contact[9],
        values=contact[10],
    )
    distribution = ReceptorDistribution(
        CommonFieldTime(clock_id, start_tick, end_tick),
        (DistributedReceptorContact(contact[4], frame),),
    )
    return distribution, MCMFieldStepTime(clock_id, start_tick, end_tick, rate)


def _replace_initial_sh(
    field: SharedMCMField,
    source: tuple[object, ...],
) -> SharedMCMField:
    neurons = tuple(sorted(field.layer.neurons, key=lambda item: item.position))
    activation = source[2]
    afterimage = source[3]
    by_id = {
        neuron.neuron_id: (activation[index], afterimage[index])
        for index, neuron in enumerate(neurons)
    }
    updated = tuple(
        replace(
            neuron,
            activation=by_id[neuron.neuron_id][0],
            afterimage=by_id[neuron.neuron_id][1],
        )
        for neuron in field.layer.neurons
    )
    return replace(field, layer=replace(field.layer, neurons=updated))


def _materialized_field(
    field: SharedMCMField,
    fixture: DTS1CommonIntervalEnvelopeFixture,
) -> SharedMCMField:
    source = _SOURCE_BY_DIGEST.get(fixture.prestate_source_digest)
    directive = fixture.prestate_directive
    if directive == "CARRY_PRIOR_SH":
        return field
    if source is None:
        raise DTS1CommonIntervalMaterializationError(
            "prestate source digest is not a registered S1-JH fixture"
        )
    if directive == "INITIAL_REGISTERED_SH":
        if source[0] != "P_IE_INITIAL_SH":
            raise DTS1CommonIntervalMaterializationError(
                "initial directive source is not P_IE_INITIAL_SH"
            )
        return _replace_initial_sh(field, source)
    if directive == "APPLY_BOUNDARY_2N":
        if source[0] != "A_BOUNDARY_2N":
            raise DTS1CommonIntervalMaterializationError(
                "two-node boundary source role mismatch"
            )
        return apply_dts1_common_sh_boundary_2n(field, source[0])
    if directive == "APPLY_BOUNDARY_3N":
        if source[0] not in {"A_BOUNDARY", "B_BOUNDARY", "GAP_BOUNDARY", "PROBE_BOUNDARY"}:
            raise DTS1CommonIntervalMaterializationError(
                "three-node boundary source role mismatch"
            )
        return apply_dts1_common_sh_boundary(field, source[0])
    raise DTS1CommonIntervalMaterializationError(
        "prestate directive is not registered"
    )


def materialize_dts1_common_interval(
    envelope_fixture: DTS1CommonIntervalEnvelopeFixture,
    model_role: str,
    input_field: SharedMCMField,
    private_state: DTS1CommonIntervalPrivateState,
    prior_envelope_digest: str | None,
    prior_output_digest: str | None,
) -> DTS1CommonIntervalMaterialization:
    """Purely materialize one registered interval without calling a model."""

    try:
        if not isinstance(envelope_fixture, DTS1CommonIntervalEnvelopeFixture):
            raise DTS1CommonIntervalMaterializationError(
                "envelope_fixture must be one immutable registered fixture"
            )
        if _FIXTURE_BY_DIGEST.get(envelope_fixture.interval_digest) is not envelope_fixture:
            if envelope_fixture != _FIXTURE_BY_DIGEST.get(envelope_fixture.interval_digest):
                raise DTS1CommonIntervalMaterializationError(
                    "envelope fixture is not in the canonical registry"
                )
        if model_role not in _MODEL_ROLES:
            raise DTS1CommonIntervalMaterializationError(
                "model_role is not one of DTS1 or B1 through B6"
            )
        identity = _validate_field_identity(input_field, model_role, envelope_fixture)
        _validate_private_state(model_role, private_state, input_field)
        _validate_provenance(
            envelope_fixture,
            input_field,
            prior_envelope_digest,
            prior_output_digest,
        )
        distribution, step_time = _distribution_and_step(identity, envelope_fixture)
        source = _SOURCE_BY_DIGEST.get(envelope_fixture.prestate_source_digest)
        prestate_operation = (
            {"mode": "carry-current-S-H"}
            if envelope_fixture.prestate_directive == "CARRY_PRIOR_SH"
            else {
                "mode": "replace-S-H",
                "activation": source[2] if source is not None else None,
                "afterimage": source[3] if source is not None else None,
            }
        )
        common_exposure_payload = {
            "schema_id": "mcm.s1jm.common-exposure.v1",
            "geometry_digest": envelope_fixture.edge_inventory_digest,
            "prestate_operation": prestate_operation,
            "receptor_distribution_payload": distribution.canonical_payload(),
            "step_time_payload": {
                "clock_id": step_time.clock_id,
                "start_tick": step_time.start_tick,
                "end_tick": step_time.end_tick,
                "ticks_per_synthetic_time_unit": step_time.ticks_per_second,
            },
        }
        private_prestate_payload = {
            "schema_id": "mcm.s1jm.private-prestate.v1",
            "model_role": model_role,
            "complete_field_payload": _field_payload(input_field),
            "private_state_payload": private_state.canonical_payload(),
            "prior_envelope_digest": prior_envelope_digest,
            "prior_output_digest": prior_output_digest,
        }
        materialized = _materialized_field(input_field, envelope_fixture)
        materialized_input_payload = {
            "schema_id": "mcm.s1jm.materialized-model-input.v1",
            "materialized_field_payload": _field_payload(materialized),
            "receptor_distribution_payload": distribution.canonical_payload(),
            "step_time_payload": common_exposure_payload["step_time_payload"],
            "geometry_digest": envelope_fixture.edge_inventory_digest,
        }
        sidecar_digest = dict(private_state.payload).get(
            "candidate_sidecar_digest_or_null"
        )
        orchestration_control_payload = {
            "sequence_digest": envelope_fixture.sequence_digest,
            "ordinal": envelope_fixture.ordinal,
            "interval_digest": envelope_fixture.interval_digest,
            "checkpoint_after_interval": envelope_fixture.checkpoint_after_interval,
            "candidate_sidecar_digest": sidecar_digest,
        }
        invocation = DTS1CommonModelInvocation(
            materialized,
            distribution,
            step_time,
            envelope_fixture.edge_inventory_digest,
        )
        integrity = DTS1CommonIntervalIntegrityRecord(
            _digest(common_exposure_payload),
            _digest(private_prestate_payload),
            _digest(materialized_input_payload),
            _digest(orchestration_control_payload),
        )
        return DTS1CommonIntervalMaterialization(invocation, integrity)
    except DTS1CommonIntervalMaterializationError:
        raise
    except (
        DTS1CommonBoundaryError,
        DTS1CommonBoundary2NError,
        MCMFieldStepTimeError,
        MCMNeuronValidationError,
        MCMNeuronLayerError,
        MCMLocalDevelopmentStateError,
        MCMSubstrateStateError,
        ReceptorContractError,
        ReceptorDistributionError,
        SharedMCMFieldError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        raise DTS1CommonIntervalMaterializationError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class DTS1S1JOImplementationReceipt:
    implementation_id: str
    source_s1jn_digest: str
    matrix_case_ids: tuple[str, ...]
    canonical_envelope_fixture_count: int
    pure_materializer_implemented: bool
    exact_identity_and_provenance_validation_present: bool
    four_integrity_roles_separated: bool
    model_kernel_import_present: bool
    adapter_import_present: bool
    runtime_integration_present: bool
    baseline_models_executed: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    private_baseline_adapter_implementation_authorized_next_stage: bool
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "receipt_digest"
        }
        if (
            self.implementation_id != S1_JO_IMPLEMENTATION_ID
            or self.source_s1jn_digest != S1_JO_SOURCE_S1JN_DIGEST
            or self.matrix_case_ids != S1_JO_MATRIX_CASE_IDS
            or self.canonical_envelope_fixture_count != 23
            or self.pure_materializer_implemented is not True
            or self.exact_identity_and_provenance_validation_present is not True
            or self.four_integrity_roles_separated is not True
            or self.model_kernel_import_present is not False
            or self.adapter_import_present is not False
            or self.runtime_integration_present is not False
            or self.baseline_models_executed is not False
            or self.research_execution_permitted is not False
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.private_baseline_adapter_implementation_authorized_next_stage
            is not True
            or self.decision != S1_JO_DECISION
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1CommonIntervalMaterializationError(
                "S1-JO implementation receipt weakened"
            )


def build_dts1_s1jo_implementation_receipt() -> DTS1S1JOImplementationReceipt:
    """Return static S1-JO acceptance without materializing an interval."""

    source = build_dts1_s1jn_finite_materialization_schema_contract()
    values = {
        "implementation_id": S1_JO_IMPLEMENTATION_ID,
        "source_s1jn_digest": source.contract_digest,
        "matrix_case_ids": S1_JO_MATRIX_CASE_IDS,
        "canonical_envelope_fixture_count": len(S1_JO_ENVELOPE_FIXTURES),
        "pure_materializer_implemented": True,
        "exact_identity_and_provenance_validation_present": True,
        "four_integrity_roles_separated": True,
        "model_kernel_import_present": False,
        "adapter_import_present": False,
        "runtime_integration_present": False,
        "baseline_models_executed": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "private_baseline_adapter_implementation_authorized_next_stage": True,
        "decision": S1_JO_DECISION,
    }
    return DTS1S1JOImplementationReceipt(
        **values, receipt_digest=_digest(values)
    )
