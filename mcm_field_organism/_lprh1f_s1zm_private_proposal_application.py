"""Private source-bound LPRH-1F drive derivation and proposal application."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import math
import re

from ._lprh1f_s1za_private_context_consumer import (
    LPRH1FPreparedDriveSet,
    LPRH1FProposalResult,
    LPRH1F_SCHEMA_VERSION,
    _digest,
    _drive_digest,
    _field_prestate_payload,
    _step_payload,
    _transient_input_payload,
)
from .field_step_time import MCMFieldStepTime
from .mcm_neuron_layer import (
    MCMNeuronDrive,
    MCMNeuronLayer,
    MCMNeuronOutput,
)
from .transient_neuron_input import TransientNeuronDockInput


LPRH1F_S1ZM_SCHEMA_VERSION = "ppb1.s1zm.lprh1f.private-proposal-application.v1"

LPRH1F_DERIVATION_INVALID_TYPE = "D01_LPRH1F_DERIVATION_INVALID_TYPE"
LPRH1F_DERIVATION_SOURCE_LAYER_INVALID = (
    "D02_LPRH1F_DERIVATION_SOURCE_LAYER_INVALID"
)
LPRH1F_DERIVATION_CONTACT_MAPPING_INVALID = (
    "D03_LPRH1F_DERIVATION_CONTACT_MAPPING_INVALID"
)
LPRH1F_DERIVATION_TRANSIENT_MAPPING_INVALID = (
    "D04_LPRH1F_DERIVATION_TRANSIENT_MAPPING_INVALID"
)
LPRH1F_DERIVATION_BOUND_SOURCE_MISMATCH = (
    "D05_LPRH1F_DERIVATION_BOUND_SOURCE_MISMATCH"
)
LPRH1F_DERIVATION_PERCEPTION_OR_DRIVE_FAILURE = (
    "D06_LPRH1F_DERIVATION_PERCEPTION_OR_DRIVE_FAILURE"
)
LPRH1F_DERIVATION_INPUT_MUTATION = "D07_LPRH1F_DERIVATION_INPUT_MUTATION"
LPRH1F_DERIVATION_ATOMIC_RESULT_REQUIRED = (
    "D08_LPRH1F_DERIVATION_ATOMIC_RESULT_REQUIRED"
)

LPRH1F_APPLICATION_INVALID_TYPE_OR_LEDGER = (
    "LPRH1F_APPLICATION_INVALID_TYPE_OR_LEDGER"
)
LPRH1F_APPLICATION_SOURCE_LAYER_MISMATCH = (
    "LPRH1F_APPLICATION_SOURCE_LAYER_MISMATCH"
)
LPRH1F_APPLICATION_DOCK_INPUT_MISMATCH = (
    "LPRH1F_APPLICATION_DOCK_INPUT_MISMATCH"
)
LPRH1F_APPLICATION_DERIVED_SET_MISMATCH = (
    "LPRH1F_APPLICATION_DERIVED_SET_MISMATCH"
)
LPRH1F_APPLICATION_PREPARED_SET_MISMATCH = (
    "LPRH1F_APPLICATION_PREPARED_SET_MISMATCH"
)
LPRH1F_APPLICATION_PROPOSAL_MISMATCH = "LPRH1F_APPLICATION_PROPOSAL_MISMATCH"
LPRH1F_APPLICATION_DUPLICATE_USE = "LPRH1F_APPLICATION_DUPLICATE_USE"
LPRH1F_APPLICATION_CALLBACK_DRIVE_MISMATCH = (
    "LPRH1F_APPLICATION_CALLBACK_DRIVE_MISMATCH"
)
LPRH1F_APPLICATION_PROPOSAL_OUTPUT_MISMATCH = (
    "LPRH1F_APPLICATION_PROPOSAL_OUTPUT_MISMATCH"
)
LPRH1F_APPLICATION_SOURCE_MUTATION = "LPRH1F_APPLICATION_SOURCE_MUTATION"
LPRH1F_APPLICATION_ATOMIC_RESULT_REQUIRED = (
    "LPRH1F_APPLICATION_ATOMIC_RESULT_REQUIRED"
)

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class LPRH1FPrivateApplicationError(ValueError):
    """One finite fail-closed private derivation or application violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise LPRH1FPrivateApplicationError(code, detail)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _finite_contact(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
        and abs(float(value)) <= 1.0
    )


def _contact_mapping_payload(
    contacts: Mapping[str, float],
) -> list[list[object]]:
    return [[key, float(contacts[key])] for key in sorted(contacts)]


def _transient_mapping_payload(
    inputs: Mapping[str, TransientNeuronDockInput],
) -> list[list[object]]:
    return [[key, _transient_input_payload(inputs[key])] for key in sorted(inputs)]


def _proposal_result_digest(result: LPRH1FProposalResult) -> str:
    return _digest(result.payload_without_digest())


@dataclass(frozen=True, slots=True)
class LPRH1FDriveDerivationReceipt:
    source_layer_digest: str
    target_step_digest: str
    receptor_contact_mapping_digest: str
    transient_input_mapping_digest: str
    receptor_input_bundle_digest: str
    ordered_drive_digests: tuple[str, ...]
    derivation_call_count: int
    derivation_receipt_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": LPRH1F_S1ZM_SCHEMA_VERSION,
            "source_layer_digest": self.source_layer_digest,
            "target_step_digest": self.target_step_digest,
            "receptor_contact_mapping_digest": self.receptor_contact_mapping_digest,
            "transient_input_mapping_digest": self.transient_input_mapping_digest,
            "receptor_input_bundle_digest": self.receptor_input_bundle_digest,
            "ordered_drive_digests": list(self.ordered_drive_digests),
            "derivation_call_count": self.derivation_call_count,
            "receipt_kind": "PRIVATE_DRIVE_DERIVATION",
        }

    def __post_init__(self) -> None:
        drive_digests = tuple(self.ordered_drive_digests)
        _require(
            all(
                _valid_digest(value)
                for value in (
                    self.source_layer_digest,
                    self.target_step_digest,
                    self.receptor_contact_mapping_digest,
                    self.transient_input_mapping_digest,
                    self.receptor_input_bundle_digest,
                )
            )
            and drive_digests
            and all(_valid_digest(value) for value in drive_digests)
            and self.derivation_call_count == len(drive_digests)
            and _valid_digest(self.derivation_receipt_digest)
            and self.derivation_receipt_digest
            == _digest(self.payload_without_digest()),
            LPRH1F_DERIVATION_ATOMIC_RESULT_REQUIRED,
            "drive derivation receipt identity, count or digest is invalid",
        )
        object.__setattr__(self, "ordered_drive_digests", drive_digests)


@dataclass(frozen=True, slots=True)
class LPRH1FDerivedDriveSet:
    source_layer_digest: str
    target_step: MCMFieldStepTime
    target_step_digest: str
    receptor_contact_mapping_digest: str
    transient_input_mapping_digest: str
    receptor_input_bundle_digest: str
    ordered_drives: tuple[MCMNeuronDrive, ...]
    ordered_drive_digests: tuple[str, ...]
    derivation_call_count: int
    derivation_receipt: LPRH1FDriveDerivationReceipt
    derived_drive_set_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": LPRH1F_S1ZM_SCHEMA_VERSION,
            "source_layer_digest": self.source_layer_digest,
            "target_step_digest": self.target_step_digest,
            "receptor_contact_mapping_digest": self.receptor_contact_mapping_digest,
            "transient_input_mapping_digest": self.transient_input_mapping_digest,
            "receptor_input_bundle_digest": self.receptor_input_bundle_digest,
            "ordered_drive_digests": list(self.ordered_drive_digests),
            "derivation_call_count": self.derivation_call_count,
            "derivation_receipt_digest": (
                self.derivation_receipt.derivation_receipt_digest
            ),
        }

    def __post_init__(self) -> None:
        drives = tuple(self.ordered_drives)
        drive_digests = tuple(self.ordered_drive_digests)
        drive_ids = [drive.previous.neuron_id for drive in drives]
        receipt = self.derivation_receipt
        _require(
            type(self.target_step) is MCMFieldStepTime
            and _valid_digest(self.source_layer_digest)
            and self.target_step_digest == _digest(_step_payload(self.target_step))
            and all(
                _valid_digest(value)
                for value in (
                    self.receptor_contact_mapping_digest,
                    self.transient_input_mapping_digest,
                    self.receptor_input_bundle_digest,
                )
            )
            and drives
            and all(type(drive) is MCMNeuronDrive for drive in drives)
            and drive_ids == sorted(set(drive_ids))
            and drive_digests == tuple(_drive_digest(drive) for drive in drives)
            and self.derivation_call_count == len(drives)
            and type(receipt) is LPRH1FDriveDerivationReceipt
            and receipt.source_layer_digest == self.source_layer_digest
            and receipt.target_step_digest == self.target_step_digest
            and receipt.receptor_contact_mapping_digest
            == self.receptor_contact_mapping_digest
            and receipt.transient_input_mapping_digest
            == self.transient_input_mapping_digest
            and receipt.receptor_input_bundle_digest
            == self.receptor_input_bundle_digest
            and receipt.ordered_drive_digests == drive_digests
            and receipt.derivation_call_count == self.derivation_call_count
            and _valid_digest(self.derived_drive_set_digest)
            and self.derived_drive_set_digest == _digest(self.payload_without_digest()),
            LPRH1F_DERIVATION_ATOMIC_RESULT_REQUIRED,
            "derived drive set does not bind its drives and nested receipt",
        )
        object.__setattr__(self, "ordered_drives", drives)
        object.__setattr__(self, "ordered_drive_digests", drive_digests)


@dataclass(frozen=True, slots=True)
class LPRH1FPrivateLayerApplicationReceipt:
    layer_application_id: str
    source_layer_digest: str
    next_layer_digest: str
    derived_drive_set_digest: str
    derivation_receipt_digest: str
    prepared_drive_set_digest: str
    proposal_result_digest: str
    target_step_digest: str
    receptor_input_bundle_digest: str
    callback_count: int
    consumed_layer_application_ids_before: tuple[str, ...]
    consumed_layer_application_ids_after: tuple[str, ...]
    application_receipt_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": LPRH1F_S1ZM_SCHEMA_VERSION,
            "layer_application_id": self.layer_application_id,
            "source_layer_digest": self.source_layer_digest,
            "next_layer_digest": self.next_layer_digest,
            "derived_drive_set_digest": self.derived_drive_set_digest,
            "derivation_receipt_digest": self.derivation_receipt_digest,
            "prepared_drive_set_digest": self.prepared_drive_set_digest,
            "proposal_result_digest": self.proposal_result_digest,
            "target_step_digest": self.target_step_digest,
            "receptor_input_bundle_digest": self.receptor_input_bundle_digest,
            "callback_count": self.callback_count,
            "consumed_layer_application_ids_before": list(
                self.consumed_layer_application_ids_before
            ),
            "consumed_layer_application_ids_after": list(
                self.consumed_layer_application_ids_after
            ),
            "receipt_kind": "PRIVATE_LAYER_APPLICATION",
        }

    def __post_init__(self) -> None:
        before = tuple(self.consumed_layer_application_ids_before)
        after = tuple(self.consumed_layer_application_ids_after)
        digest_values = (
            self.layer_application_id,
            self.source_layer_digest,
            self.next_layer_digest,
            self.derived_drive_set_digest,
            self.derivation_receipt_digest,
            self.prepared_drive_set_digest,
            self.proposal_result_digest,
            self.target_step_digest,
            self.receptor_input_bundle_digest,
        )
        _require(
            all(_valid_digest(value) for value in digest_values)
            and before == tuple(sorted(set(before)))
            and all(_valid_digest(value) for value in before)
            and self.layer_application_id not in before
            and after == tuple(sorted((*before, self.layer_application_id)))
            and self.callback_count > 0
            and _valid_digest(self.application_receipt_digest)
            and self.application_receipt_digest
            == _digest(self.payload_without_digest()),
            LPRH1F_APPLICATION_ATOMIC_RESULT_REQUIRED,
            "application receipt identity, ledger, counter or digest is invalid",
        )
        object.__setattr__(self, "consumed_layer_application_ids_before", before)
        object.__setattr__(self, "consumed_layer_application_ids_after", after)


@dataclass(frozen=True, slots=True)
class LPRH1FPrivateAppliedLayerResult:
    next_layer: MCMNeuronLayer
    application_receipt: LPRH1FPrivateLayerApplicationReceipt
    next_consumed_layer_application_ids: tuple[str, ...]
    applied_result_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": LPRH1F_S1ZM_SCHEMA_VERSION,
            "next_layer_digest": self.next_layer.digest(),
            "application_receipt_digest": (
                self.application_receipt.application_receipt_digest
            ),
            "next_consumed_layer_application_ids": list(
                self.next_consumed_layer_application_ids
            ),
        }

    def __post_init__(self) -> None:
        _require(
            type(self.next_layer) is MCMNeuronLayer
            and type(self.application_receipt)
            is LPRH1FPrivateLayerApplicationReceipt
            and self.next_layer.digest()
            == self.application_receipt.next_layer_digest
            and self.next_consumed_layer_application_ids
            == self.application_receipt.consumed_layer_application_ids_after
            and _valid_digest(self.applied_result_digest)
            and self.applied_result_digest == _digest(self.payload_without_digest()),
            LPRH1F_APPLICATION_ATOMIC_RESULT_REQUIRED,
            "applied layer result does not bind its layer, receipt and ledger",
        )


def derive_lprh1f_drives_for_layer_step(
    source_layer: MCMNeuronLayer,
    receptor_contacts: Mapping[str, float],
    target_step: MCMFieldStepTime,
    transient_receptor_inputs: Mapping[str, TransientNeuronDockInput],
) -> LPRH1FDerivedDriveSet:
    """Derive each exact layer drive once without advancing the layer."""

    _require(
        type(source_layer) is MCMNeuronLayer
        and type(target_step) is MCMFieldStepTime
        and isinstance(receptor_contacts, Mapping)
        and isinstance(transient_receptor_inputs, Mapping),
        LPRH1F_DERIVATION_INVALID_TYPE,
        "derivation requires exact layer and step types plus two mappings",
    )
    try:
        source_before = source_layer.digest()
        target_before = _digest(_step_payload(target_step))
    except Exception as exc:
        raise LPRH1FPrivateApplicationError(
            LPRH1F_DERIVATION_SOURCE_LAYER_INVALID,
            "source layer or target step cannot be canonically bound",
        ) from exc

    docked_ids = set(source_layer.docked_neuron_ids)
    try:
        contact_keys = set(receptor_contacts)
        contact_payload_before = _contact_mapping_payload(receptor_contacts)
    except Exception as exc:
        raise LPRH1FPrivateApplicationError(
            LPRH1F_DERIVATION_CONTACT_MAPPING_INVALID,
            "receptor contact mapping cannot be canonically captured",
        ) from exc
    _require(
        contact_keys == docked_ids
        and all(_finite_contact(value) for _, value in contact_payload_before),
        LPRH1F_DERIVATION_CONTACT_MAPPING_INVALID,
        "receptor contacts must exactly and finitely cover docked neurons",
    )

    try:
        transient_keys = set(transient_receptor_inputs)
        transient_payload_before = _transient_mapping_payload(
            transient_receptor_inputs
        )
    except Exception as exc:
        raise LPRH1FPrivateApplicationError(
            LPRH1F_DERIVATION_TRANSIENT_MAPPING_INVALID,
            "transient input mapping cannot be canonically captured",
        ) from exc
    _require(
        transient_keys == docked_ids
        and all(
            type(transient_receptor_inputs[key]) is TransientNeuronDockInput
            and transient_receptor_inputs[key].neuron_id == key
            and transient_receptor_inputs[key].step_time == target_step
            for key in transient_keys
        ),
        LPRH1F_DERIVATION_TRANSIENT_MAPPING_INVALID,
        "transient inputs must exactly cover docks and share key and target step",
    )
    _require(
        type(source_layer)._perception_for is MCMNeuronLayer._perception_for,
        LPRH1F_DERIVATION_BOUND_SOURCE_MISMATCH,
        "drive derivation source differs from bound MCMNeuronLayer._perception_for",
    )

    position_map = {neuron.position: neuron for neuron in source_layer.neurons}
    drives: list[MCMNeuronDrive] = []
    try:
        for neuron in source_layer.neurons:
            perception = source_layer._perception_for(
                neuron,
                position_map,
                receptor_contacts,
            )
            drives.append(
                MCMNeuronDrive(
                    previous=neuron,
                    perception=perception,
                    step_time=target_step,
                    transient_receptor_input=transient_receptor_inputs[
                        neuron.neuron_id
                    ],
                )
            )
    except LPRH1FPrivateApplicationError:
        raise
    except Exception as exc:
        raise LPRH1FPrivateApplicationError(
            LPRH1F_DERIVATION_PERCEPTION_OR_DRIVE_FAILURE,
            "bound perception or drive construction failed",
        ) from exc

    try:
        unchanged = (
            source_layer.digest() == source_before
            and _digest(_step_payload(target_step)) == target_before
            and _contact_mapping_payload(receptor_contacts)
            == contact_payload_before
            and _transient_mapping_payload(transient_receptor_inputs)
            == transient_payload_before
        )
    except Exception as exc:
        raise LPRH1FPrivateApplicationError(
            LPRH1F_DERIVATION_INPUT_MUTATION,
            "one derivation input cannot be recaptured after derivation",
        ) from exc
    _require(
        unchanged,
        LPRH1F_DERIVATION_INPUT_MUTATION,
        "one derivation input changed during the call",
    )

    ordered_drives = tuple(drives)
    ordered_drive_digests = tuple(_drive_digest(drive) for drive in ordered_drives)
    contact_mapping_digest = _digest(contact_payload_before)
    transient_mapping_digest = _digest(transient_payload_before)
    target_step_digest = target_before
    receptor_input_bundle_digest = _digest(
        {
            "source_layer_digest": source_before,
            "target_step_digest": target_step_digest,
            "ordered_receptor_contacts_neuron_id_value": contact_payload_before,
            "ordered_transient_receptor_input_digests": [
                _digest(item[1]) for item in transient_payload_before
            ],
        }
    )
    receipt_values = {
        "source_layer_digest": source_before,
        "target_step_digest": target_step_digest,
        "receptor_contact_mapping_digest": contact_mapping_digest,
        "transient_input_mapping_digest": transient_mapping_digest,
        "receptor_input_bundle_digest": receptor_input_bundle_digest,
        "ordered_drive_digests": ordered_drive_digests,
        "derivation_call_count": len(ordered_drives),
    }
    receipt_payload = {
        "schema_version": LPRH1F_S1ZM_SCHEMA_VERSION,
        **receipt_values,
        "ordered_drive_digests": list(ordered_drive_digests),
        "receipt_kind": "PRIVATE_DRIVE_DERIVATION",
    }
    receipt = LPRH1FDriveDerivationReceipt(
        **receipt_values,
        derivation_receipt_digest=_digest(receipt_payload),
    )
    set_values = {
        "source_layer_digest": source_before,
        "target_step": target_step,
        "target_step_digest": target_step_digest,
        "receptor_contact_mapping_digest": contact_mapping_digest,
        "transient_input_mapping_digest": transient_mapping_digest,
        "receptor_input_bundle_digest": receptor_input_bundle_digest,
        "ordered_drives": ordered_drives,
        "ordered_drive_digests": ordered_drive_digests,
        "derivation_call_count": len(ordered_drives),
        "derivation_receipt": receipt,
    }
    set_payload = {
        "schema_version": LPRH1F_S1ZM_SCHEMA_VERSION,
        "source_layer_digest": source_before,
        "target_step_digest": target_step_digest,
        "receptor_contact_mapping_digest": contact_mapping_digest,
        "transient_input_mapping_digest": transient_mapping_digest,
        "receptor_input_bundle_digest": receptor_input_bundle_digest,
        "ordered_drive_digests": list(ordered_drive_digests),
        "derivation_call_count": len(ordered_drives),
        "derivation_receipt_digest": receipt.derivation_receipt_digest,
    }
    return LPRH1FDerivedDriveSet(
        **set_values,
        derived_drive_set_digest=_digest(set_payload),
    )


def apply_lprh1f_proposal_once(
    source_layer: MCMNeuronLayer,
    derived_drive_set: LPRH1FDerivedDriveSet,
    prepared_drive_set: LPRH1FPreparedDriveSet,
    proposal_result: LPRH1FProposalResult,
    receptor_contacts: Mapping[str, float],
    transient_receptor_inputs: Mapping[str, TransientNeuronDockInput],
    consumed_layer_application_ids: tuple[str, ...],
) -> LPRH1FPrivateAppliedLayerResult:
    """Apply one complete private proposal through one atomic layer advance."""

    _require(
        type(source_layer) is MCMNeuronLayer
        and type(derived_drive_set) is LPRH1FDerivedDriveSet
        and type(prepared_drive_set) is LPRH1FPreparedDriveSet
        and type(proposal_result) is LPRH1FProposalResult
        and isinstance(receptor_contacts, Mapping)
        and isinstance(transient_receptor_inputs, Mapping)
        and type(consumed_layer_application_ids) is tuple
        and consumed_layer_application_ids
        == tuple(sorted(set(consumed_layer_application_ids)))
        and all(_valid_digest(value) for value in consumed_layer_application_ids),
        LPRH1F_APPLICATION_INVALID_TYPE_OR_LEDGER,
        "application types or prior application ledger are invalid",
    )

    source_before = source_layer.digest()
    proposal_before = _proposal_result_digest(proposal_result)
    prepared_before = _digest(prepared_drive_set.payload_without_digest())
    derived_before = _digest(derived_drive_set.payload_without_digest())
    try:
        contact_payload_before = _contact_mapping_payload(receptor_contacts)
        transient_payload_before = _transient_mapping_payload(
            transient_receptor_inputs
        )
    except Exception as exc:
        raise LPRH1FPrivateApplicationError(
            LPRH1F_APPLICATION_DOCK_INPUT_MISMATCH,
            "application input mappings cannot be canonically captured",
        ) from exc

    _require(
        source_before == derived_drive_set.source_layer_digest
        == prepared_drive_set.source_layer_digest,
        LPRH1F_APPLICATION_SOURCE_LAYER_MISMATCH,
        "source layer differs from derived or prepared drive source",
    )
    _require(
        _digest(contact_payload_before)
        == derived_drive_set.receptor_contact_mapping_digest
        and _digest(transient_payload_before)
        == derived_drive_set.transient_input_mapping_digest,
        LPRH1F_APPLICATION_DOCK_INPUT_MISMATCH,
        "application input bundle differs from drive derivation",
    )
    prepared = prepared_drive_set.ordered_prepared_drives
    derived = derived_drive_set.ordered_drives
    _require(
        len(prepared) == len(derived) == len(source_layer.neurons)
        and prepared_drive_set.target_step == derived_drive_set.target_step
        and prepared_drive_set.target_step_digest
        == derived_drive_set.target_step_digest
        and all(
            item.drive is drive
            and item.drive_digest == drive_digest
            and drive.previous is source_neuron
            for item, drive, drive_digest, source_neuron in zip(
                prepared,
                derived,
                derived_drive_set.ordered_drive_digests,
                source_layer.neurons,
                strict=True,
            )
        ),
        LPRH1F_APPLICATION_DERIVED_SET_MISMATCH,
        "derived set does not exactly bind prepared drives and source neurons",
    )
    proposal = proposal_result.proposal_set
    outputs = proposal.ordered_outputs
    _require(
        proposal.prepared_drive_set_digest
        == prepared_drive_set.prepared_drive_set_digest
        and proposal.target_step_digest == prepared_drive_set.target_step_digest
        and proposal.field_prestate_digest
        == prepared_drive_set.field_prestate_digest
        == _digest(_field_prestate_payload(source_layer))
        and len(outputs) == len(prepared)
        and all(
            output.neuron_id == item.drive.previous.neuron_id
            and output.prepared_drive_digest == item.prepared_drive_digest
            for output, item in zip(outputs, prepared, strict=True)
        ),
        LPRH1F_APPLICATION_PROPOSAL_MISMATCH,
        "proposal does not exactly bind the prepared source and output order",
    )

    application_id = _digest(
        {
            "schema_version": LPRH1F_S1ZM_SCHEMA_VERSION,
            "source_layer_digest": source_before,
            "prepared_drive_set_digest": prepared_drive_set.prepared_drive_set_digest,
            "proposal_result_digest": proposal_result.result_digest,
            "target_step_digest": derived_drive_set.target_step_digest,
            "receptor_input_bundle_digest": (
                derived_drive_set.receptor_input_bundle_digest
            ),
        }
    )
    _require(
        application_id not in consumed_layer_application_ids,
        LPRH1F_APPLICATION_DUPLICATE_USE,
        "derived private layer application identity was already consumed",
    )

    callback_index = 0

    def transition(callback_drive: MCMNeuronDrive) -> MCMNeuronOutput:
        nonlocal callback_index
        _require(
            callback_index < len(derived),
            LPRH1F_APPLICATION_CALLBACK_DRIVE_MISMATCH,
            "layer emitted more callback drives than derived",
        )
        expected_drive = derived[callback_index]
        expected_prepared = prepared[callback_index]
        _require(
            callback_drive.previous is expected_drive.previous
            and _drive_digest(callback_drive)
            == derived_drive_set.ordered_drive_digests[callback_index]
            == expected_prepared.drive_digest,
            LPRH1F_APPLICATION_CALLBACK_DRIVE_MISMATCH,
            "callback drive differs from derived and prepared drive",
        )
        output = outputs[callback_index]
        _require(
            output.neuron_id == callback_drive.previous.neuron_id
            and output.prepared_drive_digest
            == expected_prepared.prepared_drive_digest,
            LPRH1F_APPLICATION_PROPOSAL_OUTPUT_MISMATCH,
            "proposal output lookup differs from callback drive",
        )
        callback_index += 1
        return MCMNeuronOutput(output.output_activation, output.output_afterimage)

    try:
        next_layer = source_layer.advance(
            receptor_contacts,
            transition,
            step_time=derived_drive_set.target_step,
            transient_receptor_inputs=transient_receptor_inputs,
        )
    except LPRH1FPrivateApplicationError:
        raise
    except Exception as exc:
        raise LPRH1FPrivateApplicationError(
            LPRH1F_APPLICATION_ATOMIC_RESULT_REQUIRED,
            "single layer application failed without a complete result",
        ) from exc
    _require(
        callback_index == len(derived),
        LPRH1F_APPLICATION_CALLBACK_DRIVE_MISMATCH,
        "layer emitted fewer callback drives than derived",
    )

    try:
        unchanged = (
            source_layer.digest() == source_before
            and _proposal_result_digest(proposal_result) == proposal_before
            and _digest(prepared_drive_set.payload_without_digest())
            == prepared_before
            and _digest(derived_drive_set.payload_without_digest()) == derived_before
            and _contact_mapping_payload(receptor_contacts)
            == contact_payload_before
            and _transient_mapping_payload(transient_receptor_inputs)
            == transient_payload_before
        )
    except Exception as exc:
        raise LPRH1FPrivateApplicationError(
            LPRH1F_APPLICATION_SOURCE_MUTATION,
            "one application source cannot be recaptured",
        ) from exc
    _require(
        unchanged,
        LPRH1F_APPLICATION_SOURCE_MUTATION,
        "one application source changed during the layer step",
    )

    after = tuple(sorted((*consumed_layer_application_ids, application_id)))
    receipt_values = {
        "layer_application_id": application_id,
        "source_layer_digest": source_before,
        "next_layer_digest": next_layer.digest(),
        "derived_drive_set_digest": derived_drive_set.derived_drive_set_digest,
        "derivation_receipt_digest": (
            derived_drive_set.derivation_receipt.derivation_receipt_digest
        ),
        "prepared_drive_set_digest": prepared_drive_set.prepared_drive_set_digest,
        "proposal_result_digest": proposal_result.result_digest,
        "target_step_digest": derived_drive_set.target_step_digest,
        "receptor_input_bundle_digest": (
            derived_drive_set.receptor_input_bundle_digest
        ),
        "callback_count": callback_index,
        "consumed_layer_application_ids_before": consumed_layer_application_ids,
        "consumed_layer_application_ids_after": after,
    }
    receipt_payload = {
        "schema_version": LPRH1F_S1ZM_SCHEMA_VERSION,
        **receipt_values,
        "consumed_layer_application_ids_before": list(
            consumed_layer_application_ids
        ),
        "consumed_layer_application_ids_after": list(after),
        "receipt_kind": "PRIVATE_LAYER_APPLICATION",
    }
    receipt = LPRH1FPrivateLayerApplicationReceipt(
        **receipt_values,
        application_receipt_digest=_digest(receipt_payload),
    )
    result_values = {
        "next_layer": next_layer,
        "application_receipt": receipt,
        "next_consumed_layer_application_ids": after,
    }
    result_payload = {
        "schema_version": LPRH1F_S1ZM_SCHEMA_VERSION,
        "next_layer_digest": next_layer.digest(),
        "application_receipt_digest": receipt.application_receipt_digest,
        "next_consumed_layer_application_ids": list(after),
    }
    return LPRH1FPrivateAppliedLayerResult(
        **result_values,
        applied_result_digest=_digest(result_payload),
    )
