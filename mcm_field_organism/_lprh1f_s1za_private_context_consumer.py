"""Private pure layer-bound LPRH-1F proposal consumer."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from ._lprh1_s1yn_private_local_handoff import LPRH1HandoffResult
from .field_step_time import MCMFieldStepTime
from .mcm_neuron_layer import (
    MCMNeuronDrive,
    MCMNeuronLayer,
    MCMNeuronOutput,
    MCMNeuronTransition,
    hold_state_baseline,
)
from .transient_neuron_input import (
    TransientLocalReceptorContact,
    TransientNeuronDockInput,
)


LPRH1F_SCHEMA_VERSION = "ppb1.s1za.lprh1f.private-layer-bound-consumer.v1"
LPRH1F_BASE_TRANSITION_ID = "mcm.neuron.hold-state-baseline.v1"

LPRH1F_INVALID_INPUT = "LPRH1F_INVALID_INPUT"
LPRH1F_PROVENANCE_MISMATCH = "LPRH1F_PROVENANCE_MISMATCH"
LPRH1F_CAUSAL_TIME_MISMATCH = "LPRH1F_CAUSAL_TIME_MISMATCH"
LPRH1F_LOCAL_MAPPING_MISMATCH = "LPRH1F_LOCAL_MAPPING_MISMATCH"
LPRH1F_DUPLICATE_FIELD_USE = "LPRH1F_DUPLICATE_FIELD_USE"
LPRH1F_BASE_OUTPUT_MISMATCH = "LPRH1F_BASE_OUTPUT_MISMATCH"
LPRH1F_ATOMIC_RESULT_REQUIRED = "LPRH1F_ATOMIC_RESULT_REQUIRED"
LPRH1F_FIELD_EXECUTION_BLOCKED = "LPRH1F_FIELD_EXECUTION_BLOCKED"

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_SOURCE_KINDS = {"CANDIDATE", "GENERIC", "NO_CONTEXT", "DIGEST_ONLY"}
_ARM_MATRIX = {
    "candidate.low": ("CANDIDATE", -0.5, 1, None),
    "candidate.high": ("CANDIDATE", 0.5, 1, None),
    "generic.low": ("GENERIC", -0.5, 1, "generic.low.source"),
    "generic.high": ("GENERIC", 0.5, 1, "generic.high.source"),
    "no-context.low": ("NO_CONTEXT", None, 0, None),
    "no-context.high": ("NO_CONTEXT", None, 0, None),
    "digest-only.low": ("DIGEST_ONLY", None, 0, "digest.low.source"),
    "digest-only.high": ("DIGEST_ONLY", None, 0, "digest.high.source"),
}


class LPRH1FConsumerError(ValueError):
    """One finite fail-closed private consumer violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise LPRH1FConsumerError(code, detail)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _valid_identifier(value: object) -> bool:
    return isinstance(value, str) and _IDENTIFIER.fullmatch(value) is not None


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _finite_field_value(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
        and abs(float(value)) <= 1.0
    )


def _step_payload(step: MCMFieldStepTime) -> dict[str, object]:
    return {
        "clock_id": step.clock_id,
        "start_tick": step.start_tick,
        "end_tick": step.end_tick,
        "ticks_per_second": step.ticks_per_second,
    }


def _contact_payload(contact: TransientLocalReceptorContact) -> dict[str, object]:
    return {
        "snapshot_id": contact.snapshot_id,
        "source_clock_id": contact.source_clock_id,
        "source_window_start_tick": contact.source_window_start_tick,
        "source_window_end_tick": contact.source_window_end_tick,
        "organism_clock_id": contact.organism_read_time.clock_id,
        "organism_window_start_tick": contact.organism_read_time.window_start_tick,
        "organism_window_end_tick": contact.organism_read_time.window_end_tick,
        "value": contact.value,
    }


def _transient_input_payload(
    value: TransientNeuronDockInput,
) -> dict[str, object]:
    return {
        "neuron_id": value.neuron_id,
        "dock_id": value.dock_id,
        "carrier_id": value.carrier_id,
        "step_time_payload": _step_payload(value.step_time),
        "ordered_contact_payloads": [
            _contact_payload(contact) for contact in value.contacts
        ],
    }


def _drive_payload(drive: MCMNeuronDrive) -> dict[str, object]:
    return {
        "previous_neuron_digest": drive.previous.digest(),
        "perception_canonical_payload": drive.perception.canonical_payload(),
        "step_time_canonical_payload_or_none": (
            None if drive.step_time is None else _step_payload(drive.step_time)
        ),
        "transient_receptor_input_canonical_payload_or_none": (
            None
            if drive.transient_receptor_input is None
            else _transient_input_payload(drive.transient_receptor_input)
        ),
    }


def _drive_digest(drive: MCMNeuronDrive) -> str:
    return _digest(_drive_payload(drive))


def _field_prestate_payload(source_layer: MCMNeuronLayer) -> dict[str, object]:
    first = source_layer.neurons[0]
    return {
        "layer_id": source_layer.layer_id,
        "field_id": first.field_id,
        "geometry_id": first.geometry_id,
        "source_tick": source_layer.tick,
        "ordered_previous_neuron_digests": [
            neuron.digest() for neuron in source_layer.neurons
        ],
    }


def _handoff_result_payload(result: LPRH1HandoffResult) -> dict[str, object]:
    return {
        "envelope_digest": result.envelope.envelope_digest,
        "handoff_receipt_digest": result.receipt.receipt_digest,
        "next_consumed_handoff_ids": list(result.next_consumed_handoff_ids),
    }


def _local_values_payload(
    values: tuple[tuple[str, str, str, float], ...],
) -> list[dict[str, object]]:
    return [
        {
            "neuron_id": neuron_id,
            "dock_id": dock_id,
            "carrier_id": carrier_id,
            "value": value,
        }
        for neuron_id, dock_id, carrier_id, value in values
    ]


def _generic_source_payload(
    source_id: str,
    values: tuple[tuple[str, str, str, float], ...],
) -> dict[str, object]:
    return {
        "generic_source_id": source_id,
        "ordered_local_values": _local_values_payload(values),
    }


@dataclass(frozen=True, slots=True)
class LPRH1FPreparedDrive:
    drive: MCMNeuronDrive
    base_output: MCMNeuronOutput
    drive_digest: str
    prepared_drive_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": LPRH1F_SCHEMA_VERSION,
            "drive_digest": self.drive_digest,
            "base_output_activation": self.base_output.activation,
            "base_output_afterimage": self.base_output.afterimage,
        }

    def __post_init__(self) -> None:
        _require(
            type(self.drive) is MCMNeuronDrive
            and type(self.base_output) is MCMNeuronOutput
            and _valid_digest(self.drive_digest)
            and self.drive_digest == _drive_digest(self.drive)
            and _finite_field_value(self.base_output.activation)
            and _finite_field_value(self.base_output.afterimage)
            and _valid_digest(self.prepared_drive_digest)
            and self.prepared_drive_digest == _digest(self.payload_without_digest()),
            LPRH1F_ATOMIC_RESULT_REQUIRED,
            "prepared drive does not bind its drive and base output",
        )


@dataclass(frozen=True, slots=True)
class LPRH1FPreparedDriveSet:
    execution_id: str
    source_layer_digest: str
    target_step: MCMFieldStepTime
    target_step_digest: str
    field_prestate_digest: str
    base_transition_id: str
    ordered_prepared_drives: tuple[LPRH1FPreparedDrive, ...]
    base_transition_call_count: int
    preparation_receipt_id: str
    prepared_drive_set_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": LPRH1F_SCHEMA_VERSION,
            "execution_id": self.execution_id,
            "source_layer_digest": self.source_layer_digest,
            "target_step_digest": self.target_step_digest,
            "field_prestate_digest": self.field_prestate_digest,
            "base_transition_id": self.base_transition_id,
            "ordered_prepared_drive_digests": [
                item.prepared_drive_digest for item in self.ordered_prepared_drives
            ],
            "base_transition_call_count": self.base_transition_call_count,
            "preparation_receipt_id": self.preparation_receipt_id,
        }

    def __post_init__(self) -> None:
        prepared = tuple(self.ordered_prepared_drives)
        drive_ids = [item.drive.previous.neuron_id for item in prepared]
        expected_receipt_id = _digest(
            {
                "schema_version": LPRH1F_SCHEMA_VERSION,
                "execution_id": self.execution_id,
                "source_layer_digest": self.source_layer_digest,
                "target_step_digest": self.target_step_digest,
                "field_prestate_digest": self.field_prestate_digest,
                "base_transition_id": self.base_transition_id,
                "ordered_drive_digests": [item.drive_digest for item in prepared],
            }
        )
        _require(
            _valid_identifier(self.execution_id)
            and _valid_digest(self.source_layer_digest)
            and type(self.target_step) is MCMFieldStepTime
            and _valid_digest(self.target_step_digest)
            and self.target_step_digest == _digest(_step_payload(self.target_step))
            and _valid_digest(self.field_prestate_digest)
            and self.base_transition_id == LPRH1F_BASE_TRANSITION_ID
            and prepared
            and all(type(item) is LPRH1FPreparedDrive for item in prepared)
            and drive_ids == sorted(set(drive_ids))
            and all(item.drive.step_time == self.target_step for item in prepared)
            and self.base_transition_call_count == len(prepared)
            and self.preparation_receipt_id == expected_receipt_id
            and _valid_digest(self.prepared_drive_set_digest)
            and self.prepared_drive_set_digest == _digest(self.payload_without_digest()),
            LPRH1F_ATOMIC_RESULT_REQUIRED,
            "prepared drive set identity, order, counter or digest is invalid",
        )
        object.__setattr__(self, "ordered_prepared_drives", prepared)


@dataclass(frozen=True, slots=True)
class LPRH1FSteeringInput:
    execution_id: str
    arm_id: str
    source_kind: str
    target_step_digest: str
    field_prestate_digest: str
    handoff_result: LPRH1HandoffResult | None
    handoff_result_digest: str | None
    generic_source_id: str | None
    ordered_local_values: tuple[tuple[str, str, str, float], ...]
    source_provenance_digest: str
    steering_input_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": LPRH1F_SCHEMA_VERSION,
            "execution_id": self.execution_id,
            "arm_id": self.arm_id,
            "source_kind": self.source_kind,
            "target_step_digest": self.target_step_digest,
            "field_prestate_digest": self.field_prestate_digest,
            "handoff_result_digest": self.handoff_result_digest,
            "generic_source_id": self.generic_source_id,
            "ordered_local_values": _local_values_payload(self.ordered_local_values),
            "source_provenance_digest": self.source_provenance_digest,
        }

    def __post_init__(self) -> None:
        try:
            local = tuple(
                (neuron_id, dock_id, carrier_id, float(value))
                for neuron_id, dock_id, carrier_id, value in self.ordered_local_values
            )
        except (TypeError, ValueError) as exc:
            raise LPRH1FConsumerError(
                LPRH1F_ATOMIC_RESULT_REQUIRED,
                "ordered local values are malformed",
            ) from exc
        identities = [(item[0], item[1], item[2]) for item in local]
        spec = _ARM_MATRIX.get(self.arm_id)
        _require(
            _valid_identifier(self.execution_id)
            and spec is not None
            and self.source_kind in _SOURCE_KINDS
            and self.source_kind == spec[0]
            and _valid_digest(self.target_step_digest)
            and _valid_digest(self.field_prestate_digest)
            and len(local) == spec[2]
            and identities == sorted(set(identities))
            and all(
                _valid_identifier(neuron_id)
                and _valid_identifier(dock_id)
                and _valid_identifier(carrier_id)
                and _finite_field_value(value)
                for neuron_id, dock_id, carrier_id, value in local
            ),
            LPRH1F_ATOMIC_RESULT_REQUIRED,
            "steering identity, source branch or local values are invalid",
        )
        expected_value = spec[1]
        _require(
            expected_value is None
            or (len(local) == 1 and local[0][3] == expected_value),
            LPRH1F_ATOMIC_RESULT_REQUIRED,
            "steering value differs from the finite arm matrix",
        )

        if self.source_kind in {"CANDIDATE", "NO_CONTEXT"}:
            _require(
                type(self.handoff_result) is LPRH1HandoffResult
                and self.generic_source_id is None,
                LPRH1F_ATOMIC_RESULT_REQUIRED,
                "handoff source branch requires exactly one handoff result",
            )
            assert self.handoff_result is not None
            expected_handoff_digest = _digest(
                _handoff_result_payload(self.handoff_result)
            )
            _require(
                self.handoff_result_digest == expected_handoff_digest
                and self.source_provenance_digest == expected_handoff_digest
                and self.handoff_result.receipt.execution_id == self.execution_id,
                LPRH1F_ATOMIC_RESULT_REQUIRED,
                "handoff source provenance is invalid",
            )
            if self.source_kind == "CANDIDATE":
                context = self.handoff_result.envelope.context
                _require(
                    context is not None
                    and self.handoff_result.envelope.no_context_receipt is None
                    and context.target_step_digest == self.target_step_digest
                    and local
                    == tuple(
                        (
                            item.neuron_id,
                            item.dock_id,
                            item.carrier_id,
                            item.prototype_value,
                        )
                        for item in context.local_contexts
                    ),
                    LPRH1F_ATOMIC_RESULT_REQUIRED,
                    "candidate values do not equal the handoff context",
                )
            else:
                no_context = self.handoff_result.envelope.no_context_receipt
                _require(
                    self.handoff_result.envelope.context is None
                    and no_context is not None
                    and no_context.target_step_digest == self.target_step_digest
                    and not local,
                    LPRH1F_ATOMIC_RESULT_REQUIRED,
                    "no-context arm requires an explicit no-context handoff",
                )
        else:
            _require(
                self.handoff_result is None
                and self.handoff_result_digest is None
                and self.generic_source_id == spec[3]
                and _valid_identifier(self.generic_source_id)
                and self.source_provenance_digest
                == _digest(_generic_source_payload(self.generic_source_id, local)),
                LPRH1F_ATOMIC_RESULT_REQUIRED,
                "generic or digest-only source provenance is invalid",
            )

        object.__setattr__(self, "ordered_local_values", local)
        _require(
            _valid_digest(self.source_provenance_digest)
            and _valid_digest(self.steering_input_digest)
            and self.steering_input_digest == _digest(self.payload_without_digest()),
            LPRH1F_ATOMIC_RESULT_REQUIRED,
            "steering input digest does not bind its canonical payload",
        )


@dataclass(frozen=True, slots=True)
class LPRH1FLocalProposalOutput:
    neuron_id: str
    arm_id: str
    prepared_drive_digest: str
    base_activation: float
    base_afterimage: float
    steering_value: float | None
    output_activation: float
    output_afterimage: float
    output_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": LPRH1F_SCHEMA_VERSION,
            "neuron_id": self.neuron_id,
            "arm_id": self.arm_id,
            "prepared_drive_digest": self.prepared_drive_digest,
            "base_activation": self.base_activation,
            "base_afterimage": self.base_afterimage,
            "steering_value": self.steering_value,
            "output_activation": self.output_activation,
            "output_afterimage": self.output_afterimage,
        }

    def __post_init__(self) -> None:
        numeric = (
            self.base_activation,
            self.base_afterimage,
            self.output_activation,
            self.output_afterimage,
        )
        _require(
            _valid_identifier(self.neuron_id)
            and self.arm_id in _ARM_MATRIX
            and _valid_digest(self.prepared_drive_digest)
            and all(_finite_field_value(value) for value in numeric)
            and (
                self.steering_value is None
                or _finite_field_value(self.steering_value)
            ),
            LPRH1F_ATOMIC_RESULT_REQUIRED,
            "local proposal output values are invalid",
        )
        expected_activation = (
            self.base_activation
            if self.steering_value is None
            else (self.base_activation + self.steering_value) * 0.5
        )
        _require(
            self.output_activation == expected_activation
            and self.output_afterimage == self.base_afterimage
            and _valid_digest(self.output_digest)
            and self.output_digest == _digest(self.payload_without_digest()),
            LPRH1F_ATOMIC_RESULT_REQUIRED,
            "local proposal output is invalid",
        )


@dataclass(frozen=True, slots=True)
class LPRH1FProposalSet:
    execution_id: str
    arm_id: str
    target_step_digest: str
    field_prestate_digest: str
    prepared_drive_set_digest: str
    steering_input_digest: str
    ordered_outputs: tuple[LPRH1FLocalProposalOutput, ...]
    proposal_set_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": LPRH1F_SCHEMA_VERSION,
            "execution_id": self.execution_id,
            "arm_id": self.arm_id,
            "target_step_digest": self.target_step_digest,
            "field_prestate_digest": self.field_prestate_digest,
            "prepared_drive_set_digest": self.prepared_drive_set_digest,
            "steering_input_digest": self.steering_input_digest,
            "ordered_output_digests": [
                item.output_digest for item in self.ordered_outputs
            ],
        }

    def __post_init__(self) -> None:
        outputs = tuple(self.ordered_outputs)
        neuron_ids = [item.neuron_id for item in outputs]
        _require(
            _valid_identifier(self.execution_id)
            and self.arm_id in _ARM_MATRIX
            and all(
                _valid_digest(value)
                for value in (
                    self.target_step_digest,
                    self.field_prestate_digest,
                    self.prepared_drive_set_digest,
                    self.steering_input_digest,
                )
            )
            and outputs
            and all(type(item) is LPRH1FLocalProposalOutput for item in outputs)
            and neuron_ids == sorted(set(neuron_ids))
            and all(item.arm_id == self.arm_id for item in outputs)
            and _valid_digest(self.proposal_set_digest)
            and self.proposal_set_digest == _digest(self.payload_without_digest()),
            LPRH1F_ATOMIC_RESULT_REQUIRED,
            "proposal set identity, order or digest is invalid",
        )
        object.__setattr__(self, "ordered_outputs", outputs)


@dataclass(frozen=True, slots=True)
class LPRH1FProposalResult:
    field_use_id: str
    receipt_id: str
    proposal_set: LPRH1FProposalSet
    consumed_field_use_ids_before: tuple[str, ...]
    consumed_field_use_ids_after: tuple[str, ...]
    consumer_call_count: int
    mapped_steering_call_count: int
    consumer_base_transition_call_count: int
    partial_output_count: int
    retry_count: int
    field_step_count: int
    result_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": LPRH1F_SCHEMA_VERSION,
            "field_use_id": self.field_use_id,
            "receipt_id": self.receipt_id,
            "proposal_set_digest": self.proposal_set.proposal_set_digest,
            "consumed_field_use_ids_before": list(self.consumed_field_use_ids_before),
            "consumed_field_use_ids_after": list(self.consumed_field_use_ids_after),
            "consumer_call_count": self.consumer_call_count,
            "mapped_steering_call_count": self.mapped_steering_call_count,
            "consumer_base_transition_call_count": self.consumer_base_transition_call_count,
            "partial_output_count": self.partial_output_count,
            "retry_count": self.retry_count,
            "field_step_count": self.field_step_count,
        }

    def __post_init__(self) -> None:
        before = tuple(self.consumed_field_use_ids_before)
        after = tuple(self.consumed_field_use_ids_after)
        _require(
            type(self.proposal_set) is LPRH1FProposalSet,
            LPRH1F_ATOMIC_RESULT_REQUIRED,
            "proposal result requires one complete proposal set",
        )
        expected_receipt_id = _digest(
            {
                "schema_version": LPRH1F_SCHEMA_VERSION,
                "field_use_id": self.field_use_id,
                "receipt_kind": "FIELD_PROPOSAL_CONSUMPTION",
            }
        )
        expected_field_use_id = _digest(
            {
                "schema_version": LPRH1F_SCHEMA_VERSION,
                "execution_id": self.proposal_set.execution_id,
                "arm_id": self.proposal_set.arm_id,
                "target_step_digest": self.proposal_set.target_step_digest,
                "field_prestate_digest": self.proposal_set.field_prestate_digest,
                "prepared_drive_set_digest": self.proposal_set.prepared_drive_set_digest,
                "steering_input_digest": self.proposal_set.steering_input_digest,
            }
        )
        _require(
            _valid_digest(self.field_use_id)
            and self.field_use_id == expected_field_use_id
            and self.receipt_id == expected_receipt_id
            and before == tuple(sorted(set(before)))
            and all(_valid_digest(value) for value in before)
            and self.field_use_id not in before
            and after == tuple(sorted((*before, self.field_use_id)))
            and self.consumer_call_count == 1
            and self.mapped_steering_call_count
            == sum(
                item.steering_value is not None
                for item in self.proposal_set.ordered_outputs
            )
            and self.consumer_base_transition_call_count == 0
            and self.partial_output_count == self.retry_count == self.field_step_count == 0
            and _valid_digest(self.result_digest)
            and self.result_digest == _digest(self.payload_without_digest()),
            LPRH1F_ATOMIC_RESULT_REQUIRED,
            "proposal result identity, ledger, counters or digest is invalid",
        )
        object.__setattr__(self, "consumed_field_use_ids_before", before)
        object.__setattr__(self, "consumed_field_use_ids_after", after)


def prepare_lprh1f_base_drive_set(
    execution_id: str,
    source_layer: MCMNeuronLayer,
    target_step: MCMFieldStepTime,
    field_prestate_digest: str,
    ordered_drives: tuple[MCMNeuronDrive, ...],
    base_transition: MCMNeuronTransition,
    base_transition_id: str,
) -> LPRH1FPreparedDriveSet:
    """Prepare one immutable OFF output per layer-bound drive."""

    _require(
        _valid_identifier(execution_id)
        and type(source_layer) is MCMNeuronLayer
        and type(target_step) is MCMFieldStepTime
        and _valid_digest(field_prestate_digest)
        and type(ordered_drives) is tuple
        and ordered_drives
        and all(type(item) is MCMNeuronDrive for item in ordered_drives)
        and callable(base_transition)
        and isinstance(base_transition_id, str),
        LPRH1F_INVALID_INPUT,
        "prepare input types or identities are invalid",
    )

    source_layer_digest = source_layer.digest()
    drive_digests = tuple(_drive_digest(drive) for drive in ordered_drives)
    layer_neurons = source_layer.neurons
    drive_ids = [drive.previous.neuron_id for drive in ordered_drives]
    _require(
        len(ordered_drives) == len(layer_neurons)
        and drive_ids == sorted(set(drive_ids))
        and all(
            drive.previous is layer_neuron
            and drive.previous.digest() == layer_neuron.digest()
            and drive.previous.field_id == layer_neurons[0].field_id
            and drive.previous.geometry_id == layer_neurons[0].geometry_id
            and drive.previous.tick == source_layer.tick
            for drive, layer_neuron in zip(
                ordered_drives, layer_neurons, strict=True
            )
        ),
        LPRH1F_PROVENANCE_MISMATCH,
        "drives do not bind exactly to the ordered source layer neurons",
    )
    _require(
        all(
            drive.perception.tick == source_layer.tick + 1
            and drive.step_time == target_step
            for drive in ordered_drives
        ),
        LPRH1F_CAUSAL_TIME_MISMATCH,
        "drive perception or step time differs from the target",
    )
    derived_prestate_digest = _digest(_field_prestate_payload(source_layer))
    _require(
        field_prestate_digest == derived_prestate_digest
        and base_transition_id == LPRH1F_BASE_TRANSITION_ID
        and base_transition is hold_state_baseline,
        LPRH1F_PROVENANCE_MISMATCH,
        "field prestate or registered base transition provenance differs",
    )

    prepared_items: list[LPRH1FPreparedDrive] = []
    try:
        for drive, drive_digest in zip(ordered_drives, drive_digests, strict=True):
            output = base_transition(drive)
            _require(
                type(output) is MCMNeuronOutput
                and _finite_field_value(output.activation)
                and _finite_field_value(output.afterimage)
                and output.activation == drive.previous.activation
                and output.afterimage == drive.previous.afterimage,
                LPRH1F_BASE_OUTPUT_MISMATCH,
                "base transition output differs from hold-state",
            )
            payload = {
                "schema_version": LPRH1F_SCHEMA_VERSION,
                "drive_digest": drive_digest,
                "base_output_activation": output.activation,
                "base_output_afterimage": output.afterimage,
            }
            prepared_items.append(
                LPRH1FPreparedDrive(
                    drive=drive,
                    base_output=output,
                    drive_digest=drive_digest,
                    prepared_drive_digest=_digest(payload),
                )
            )
    except LPRH1FConsumerError:
        raise
    except Exception as exc:
        raise LPRH1FConsumerError(
            LPRH1F_BASE_OUTPUT_MISMATCH,
            "registered base transition failed",
        ) from exc

    _require(
        source_layer.digest() == source_layer_digest
        and tuple(_drive_digest(drive) for drive in ordered_drives) == drive_digests,
        LPRH1F_ATOMIC_RESULT_REQUIRED,
        "source layer or drive changed during preparation",
    )
    prepared = tuple(prepared_items)
    target_step_digest = _digest(_step_payload(target_step))
    receipt_id = _digest(
        {
            "schema_version": LPRH1F_SCHEMA_VERSION,
            "execution_id": execution_id,
            "source_layer_digest": source_layer_digest,
            "target_step_digest": target_step_digest,
            "field_prestate_digest": field_prestate_digest,
            "base_transition_id": base_transition_id,
            "ordered_drive_digests": list(drive_digests),
        }
    )
    values = {
        "execution_id": execution_id,
        "source_layer_digest": source_layer_digest,
        "target_step": target_step,
        "target_step_digest": target_step_digest,
        "field_prestate_digest": field_prestate_digest,
        "base_transition_id": base_transition_id,
        "ordered_prepared_drives": prepared,
        "base_transition_call_count": len(prepared),
        "preparation_receipt_id": receipt_id,
    }
    payload = {
        "schema_version": LPRH1F_SCHEMA_VERSION,
        "execution_id": execution_id,
        "source_layer_digest": source_layer_digest,
        "target_step_digest": target_step_digest,
        "field_prestate_digest": field_prestate_digest,
        "base_transition_id": base_transition_id,
        "ordered_prepared_drive_digests": [
            item.prepared_drive_digest for item in prepared
        ],
        "base_transition_call_count": len(prepared),
        "preparation_receipt_id": receipt_id,
    }
    return LPRH1FPreparedDriveSet(
        **values,
        prepared_drive_set_digest=_digest(payload),
    )


def materialize_lprh1f_proposal(
    prepared_drive_set: LPRH1FPreparedDriveSet,
    steering_input: LPRH1FSteeringInput,
    consumed_field_use_ids: tuple[str, ...],
) -> LPRH1FProposalResult:
    """Materialize one complete private proposal set without a field step."""

    _require(
        type(prepared_drive_set) is LPRH1FPreparedDriveSet
        and type(steering_input) is LPRH1FSteeringInput
        and type(consumed_field_use_ids) is tuple
        and consumed_field_use_ids == tuple(sorted(set(consumed_field_use_ids)))
        and all(_valid_digest(value) for value in consumed_field_use_ids),
        LPRH1F_INVALID_INPUT,
        "consumer input types or prior field-use ledger are invalid",
    )
    _require(
        prepared_drive_set.execution_id == steering_input.execution_id
        and prepared_drive_set.target_step_digest
        == steering_input.target_step_digest
        and prepared_drive_set.field_prestate_digest
        == steering_input.field_prestate_digest,
        LPRH1F_PROVENANCE_MISMATCH,
        "prepared set and steering source provenance differ",
    )

    local_by_neuron: dict[str, tuple[str, str, float]] = {}
    for neuron_id, dock_id, carrier_id, value in steering_input.ordered_local_values:
        matches = [
            item
            for item in prepared_drive_set.ordered_prepared_drives
            if item.drive.previous.neuron_id == neuron_id
            and item.drive.transient_receptor_input is not None
            and item.drive.transient_receptor_input.dock_id == dock_id
            and item.drive.transient_receptor_input.carrier_id == carrier_id
        ]
        _require(
            len(matches) == 1 and neuron_id not in local_by_neuron,
            LPRH1F_LOCAL_MAPPING_MISMATCH,
            "local steering value does not map exactly once",
        )
        local_by_neuron[neuron_id] = (dock_id, carrier_id, value)

    field_use_id = _digest(
        {
            "schema_version": LPRH1F_SCHEMA_VERSION,
            "execution_id": prepared_drive_set.execution_id,
            "arm_id": steering_input.arm_id,
            "target_step_digest": prepared_drive_set.target_step_digest,
            "field_prestate_digest": prepared_drive_set.field_prestate_digest,
            "prepared_drive_set_digest": prepared_drive_set.prepared_drive_set_digest,
            "steering_input_digest": steering_input.steering_input_digest,
        }
    )
    _require(
        field_use_id not in consumed_field_use_ids,
        LPRH1F_DUPLICATE_FIELD_USE,
        "derived field-use identity was already consumed",
    )

    outputs: list[LPRH1FLocalProposalOutput] = []
    for prepared in prepared_drive_set.ordered_prepared_drives:
        base = prepared.base_output
        _require(
            prepared.drive_digest == _drive_digest(prepared.drive)
            and base.activation == prepared.drive.previous.activation
            and base.afterimage == prepared.drive.previous.afterimage,
            LPRH1F_BASE_OUTPUT_MISMATCH,
            "prepared base output no longer matches its drive",
        )
        mapped = local_by_neuron.get(prepared.drive.previous.neuron_id)
        steering_value = None if mapped is None else mapped[2]
        output_activation = (
            base.activation
            if steering_value is None
            else (base.activation + steering_value) * 0.5
        )
        output_afterimage = base.afterimage
        output_values = {
            "neuron_id": prepared.drive.previous.neuron_id,
            "arm_id": steering_input.arm_id,
            "prepared_drive_digest": prepared.prepared_drive_digest,
            "base_activation": base.activation,
            "base_afterimage": base.afterimage,
            "steering_value": steering_value,
            "output_activation": output_activation,
            "output_afterimage": output_afterimage,
        }
        output_payload = {
            "schema_version": LPRH1F_SCHEMA_VERSION,
            **output_values,
        }
        outputs.append(
            LPRH1FLocalProposalOutput(
                **output_values,
                output_digest=_digest(output_payload),
            )
        )

    ordered_outputs = tuple(outputs)
    proposal_values = {
        "execution_id": prepared_drive_set.execution_id,
        "arm_id": steering_input.arm_id,
        "target_step_digest": prepared_drive_set.target_step_digest,
        "field_prestate_digest": prepared_drive_set.field_prestate_digest,
        "prepared_drive_set_digest": prepared_drive_set.prepared_drive_set_digest,
        "steering_input_digest": steering_input.steering_input_digest,
        "ordered_outputs": ordered_outputs,
    }
    proposal_payload = {
        "schema_version": LPRH1F_SCHEMA_VERSION,
        "execution_id": prepared_drive_set.execution_id,
        "arm_id": steering_input.arm_id,
        "target_step_digest": prepared_drive_set.target_step_digest,
        "field_prestate_digest": prepared_drive_set.field_prestate_digest,
        "prepared_drive_set_digest": prepared_drive_set.prepared_drive_set_digest,
        "steering_input_digest": steering_input.steering_input_digest,
        "ordered_output_digests": [item.output_digest for item in ordered_outputs],
    }
    proposal_set = LPRH1FProposalSet(
        **proposal_values,
        proposal_set_digest=_digest(proposal_payload),
    )
    after = tuple(sorted((*consumed_field_use_ids, field_use_id)))
    receipt_id = _digest(
        {
            "schema_version": LPRH1F_SCHEMA_VERSION,
            "field_use_id": field_use_id,
            "receipt_kind": "FIELD_PROPOSAL_CONSUMPTION",
        }
    )
    result_values = {
        "field_use_id": field_use_id,
        "receipt_id": receipt_id,
        "proposal_set": proposal_set,
        "consumed_field_use_ids_before": consumed_field_use_ids,
        "consumed_field_use_ids_after": after,
        "consumer_call_count": 1,
        "mapped_steering_call_count": len(local_by_neuron),
        "consumer_base_transition_call_count": 0,
        "partial_output_count": 0,
        "retry_count": 0,
        "field_step_count": 0,
    }
    result_payload = {
        "schema_version": LPRH1F_SCHEMA_VERSION,
        "field_use_id": field_use_id,
        "receipt_id": receipt_id,
        "proposal_set_digest": proposal_set.proposal_set_digest,
        "consumed_field_use_ids_before": list(consumed_field_use_ids),
        "consumed_field_use_ids_after": list(after),
        "consumer_call_count": 1,
        "mapped_steering_call_count": len(local_by_neuron),
        "consumer_base_transition_call_count": 0,
        "partial_output_count": 0,
        "retry_count": 0,
        "field_step_count": 0,
    }
    return LPRH1FProposalResult(
        **result_values,
        result_digest=_digest(result_payload),
    )
