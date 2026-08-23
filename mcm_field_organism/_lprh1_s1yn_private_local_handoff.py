"""Private pure LPRH-1 local prototype handoff."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re

from ._ppb1_reference import (
    PPB1BankConfig,
    PPB1BankState,
    PPB1PrototypeSlot,
    _digest,
    _input_projection,
    _validate_state,
)
from ._ppb1_s1wu_read_only_perceptual_probe import (
    S1WUReadOnlyPerceptualFinding,
    _prototype_digest,
)
from ._ppb1_s1wq_perceptual_state_lifecycle import _state_identity_payload
from .field_step_time import MCMFieldStepTime
from .receptor_time_model import OrganismTimedReceptorFrame
from .shared_mcm_field import SharedFieldDock
from .transient_neuron_input import TransientNeuronInputSet


LPRH1_SCHEMA_VERSION = "ppb1.s1yn.lprh1.private-local-handoff.v1"

LPRH1_INVALID_INPUT = "LPRH1_INVALID_INPUT"
LPRH1_PROVENANCE_MISMATCH = "LPRH1_PROVENANCE_MISMATCH"
LPRH1_CAUSAL_TIME_MISMATCH = "LPRH1_CAUSAL_TIME_MISMATCH"
LPRH1_LOCAL_MAPPING_MISMATCH = "LPRH1_LOCAL_MAPPING_MISMATCH"
LPRH1_DUPLICATE_HANDOFF = "LPRH1_DUPLICATE_HANDOFF"
LPRH1_SLOT_NOT_STABLE = "LPRH1_SLOT_NOT_STABLE"
LPRH1_ATOMIC_RESULT_REQUIRED = "LPRH1_ATOMIC_RESULT_REQUIRED"
LPRH1_FIELD_EXECUTION_BLOCKED = "LPRH1_FIELD_EXECUTION_BLOCKED"

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class LPRH1HandoffError(ValueError):
    """One fail-closed private handoff violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise LPRH1HandoffError(code, detail)


def _valid_identifier(value: object) -> bool:
    return isinstance(value, str) and _IDENTIFIER.fullmatch(value) is not None


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _step_payload(step: MCMFieldStepTime) -> dict[str, object]:
    return {
        "clock_id": step.clock_id,
        "start_tick": step.start_tick,
        "end_tick": step.end_tick,
        "ticks_per_second": step.ticks_per_second,
    }


def _timed_probe_payload(timed: OrganismTimedReceptorFrame) -> dict[str, object]:
    return {
        "frame_probe_input_payload": _input_projection(timed.frame),
        "organism_clock_id": timed.field_time.clock_id,
        "organism_window_start_tick": timed.field_time.window_start_tick,
        "organism_window_end_tick": timed.field_time.window_end_tick,
    }


def _dock_payload(dock: SharedFieldDock) -> dict[str, object]:
    return {
        "dock_id": dock.dock_id,
        "modality_id": dock.dock_map.modality_id,
        "receptor_geometry_id": dock.dock_map.receptor_geometry_id,
        "ordered_pairs": [list(pair) for pair in dock.dock_map.pairs],
    }


def _receptor_input_payload(inputs: TransientNeuronInputSet) -> dict[str, object]:
    return {
        "step_time_payload": _step_payload(inputs.step_time),
        "ordered_neuron_inputs": [
            {
                "neuron_id": item.neuron_id,
                "dock_id": item.dock_id,
                "carrier_id": item.carrier_id,
                "ordered_contacts": [
                    {
                        "snapshot_id": contact.snapshot_id,
                        "source_clock_id": contact.source_clock_id,
                        "source_window_start_tick": contact.source_window_start_tick,
                        "source_window_end_tick": contact.source_window_end_tick,
                        "organism_clock_id": contact.organism_read_time.clock_id,
                        "organism_window_start_tick": contact.organism_read_time.window_start_tick,
                        "organism_window_end_tick": contact.organism_read_time.window_end_tick,
                        "value": contact.value,
                    }
                    for contact in item.contacts
                ],
            }
            for item in inputs.neuron_inputs
        ],
    }


@dataclass(frozen=True, slots=True)
class LPRH1LocalNeuronContext:
    neuron_id: str
    dock_id: str
    carrier_id: str
    prototype_value: float

    def __post_init__(self) -> None:
        _require(
            all(_valid_identifier(value) for value in (self.neuron_id, self.dock_id, self.carrier_id)),
            LPRH1_ATOMIC_RESULT_REQUIRED,
            "local context identities are invalid",
        )
        _require(
            not isinstance(self.prototype_value, bool)
            and isinstance(self.prototype_value, (int, float))
            and math.isfinite(float(self.prototype_value))
            and abs(float(self.prototype_value)) <= 1.0,
            LPRH1_ATOMIC_RESULT_REQUIRED,
            "local prototype value is outside the normalized domain",
        )
        object.__setattr__(self, "prototype_value", float(self.prototype_value))


@dataclass(frozen=True, slots=True)
class LPRH1TransientLocalPrototypeContext:
    handoff_id: str
    execution_id: str
    bank_config_digest: str
    bank_state_digest: str
    finding_digest: str
    selected_slot_id: str
    selected_prototype_digest: str
    probe_input_digest: str
    timed_probe_digest: str
    target_step_digest: str
    shared_dock_digest: str
    receptor_input_digest: str
    modality_id: str
    geometry_id: str
    carrier_ids: tuple[str, ...]
    prototype_values: tuple[float, ...]
    local_contexts: tuple[LPRH1LocalNeuronContext, ...]
    context_digest: str

    @property
    def schema_version(self) -> str:
        return LPRH1_SCHEMA_VERSION

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "handoff_id": self.handoff_id,
            "execution_id": self.execution_id,
            "bank_config_digest": self.bank_config_digest,
            "bank_state_digest": self.bank_state_digest,
            "finding_digest": self.finding_digest,
            "selected_slot_id": self.selected_slot_id,
            "selected_prototype_digest": self.selected_prototype_digest,
            "probe_input_digest": self.probe_input_digest,
            "timed_probe_digest": self.timed_probe_digest,
            "target_step_digest": self.target_step_digest,
            "shared_dock_digest": self.shared_dock_digest,
            "receptor_input_digest": self.receptor_input_digest,
            "modality_id": self.modality_id,
            "geometry_id": self.geometry_id,
            "carrier_ids": list(self.carrier_ids),
            "prototype_values": list(self.prototype_values),
            "local_contexts": [
                {
                    "neuron_id": item.neuron_id,
                    "dock_id": item.dock_id,
                    "carrier_id": item.carrier_id,
                    "prototype_value": item.prototype_value,
                }
                for item in self.local_contexts
            ],
        }

    def __post_init__(self) -> None:
        digest_values = (
            self.bank_config_digest,
            self.bank_state_digest,
            self.finding_digest,
            self.selected_prototype_digest,
            self.probe_input_digest,
            self.timed_probe_digest,
            self.target_step_digest,
            self.shared_dock_digest,
            self.receptor_input_digest,
        )
        _require(
            _valid_digest(self.handoff_id)
            and _valid_identifier(self.execution_id)
            and _valid_identifier(self.selected_slot_id)
            and all(_valid_digest(value) for value in digest_values)
            and _valid_identifier(self.modality_id)
            and _valid_identifier(self.geometry_id),
            LPRH1_ATOMIC_RESULT_REQUIRED,
            "context identity or one of nine foreign digests is invalid",
        )
        carriers = tuple(self.carrier_ids)
        values = tuple(float(value) for value in self.prototype_values)
        local = tuple(self.local_contexts)
        _require(
            carriers
            and len(set(carriers)) == len(carriers)
            and all(_valid_identifier(value) for value in carriers)
            and len(carriers) == len(values) == len(local)
            and all(isinstance(item, LPRH1LocalNeuronContext) for item in local),
            LPRH1_ATOMIC_RESULT_REQUIRED,
            "context carrier, value and local inventories do not align",
        )
        _require(
            all(math.isfinite(value) and abs(value) <= 1.0 for value in values),
            LPRH1_ATOMIC_RESULT_REQUIRED,
            "context values are outside the normalized domain",
        )
        _require(
            all(
                item.carrier_id == carriers[index]
                and item.prototype_value == values[index]
                for index, item in enumerate(local)
            ),
            LPRH1_ATOMIC_RESULT_REQUIRED,
            "local contexts do not match carrier and value order",
        )
        object.__setattr__(self, "carrier_ids", carriers)
        object.__setattr__(self, "prototype_values", values)
        object.__setattr__(self, "local_contexts", local)
        _require(
            _valid_digest(self.context_digest)
            and self.context_digest == _digest(self.payload_without_digest()),
            LPRH1_ATOMIC_RESULT_REQUIRED,
            "context digest does not bind the canonical payload",
        )


@dataclass(frozen=True, slots=True)
class LPRH1NoContextReceipt:
    handoff_id: str
    receipt_id: str
    execution_id: str
    reason: str
    bank_state_digest: str
    finding_digest: str
    probe_input_digest: str
    timed_probe_digest: str
    target_step_digest: str
    receptor_input_digest: str
    receipt_digest: str

    @property
    def schema_version(self) -> str:
        return LPRH1_SCHEMA_VERSION

    @property
    def receipt_kind(self) -> str:
        return "NO_CONTEXT_SOURCE"

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "handoff_id": self.handoff_id,
            "receipt_id": self.receipt_id,
            "receipt_kind": self.receipt_kind,
            "execution_id": self.execution_id,
            "reason": self.reason,
            "bank_state_digest": self.bank_state_digest,
            "finding_digest": self.finding_digest,
            "probe_input_digest": self.probe_input_digest,
            "timed_probe_digest": self.timed_probe_digest,
            "target_step_digest": self.target_step_digest,
            "receptor_input_digest": self.receptor_input_digest,
        }

    def __post_init__(self) -> None:
        expected_receipt_id = _digest(
            {
                "schema_version": self.schema_version,
                "handoff_id": self.handoff_id,
                "receipt_kind": self.receipt_kind,
            }
        )
        _require(
            _valid_digest(self.handoff_id)
            and _valid_digest(self.receipt_id)
            and _valid_identifier(self.execution_id)
            and self.reason == "UNRECOGNIZED"
            and self.receipt_id == expected_receipt_id
            and all(
                _valid_digest(value)
                for value in (
                    self.bank_state_digest,
                    self.finding_digest,
                    self.probe_input_digest,
                    self.timed_probe_digest,
                    self.target_step_digest,
                    self.receptor_input_digest,
                )
            )
            and _valid_digest(self.receipt_digest)
            and self.receipt_digest == _digest(self.payload_without_digest()),
            LPRH1_ATOMIC_RESULT_REQUIRED,
            "no-context receipt is invalid",
        )


@dataclass(frozen=True, slots=True)
class LPRH1DualInputEnvelope:
    target_step_digest: str
    receptor_input_digest: str
    receptor_input_set: TransientNeuronInputSet
    context: LPRH1TransientLocalPrototypeContext | None
    no_context_receipt: LPRH1NoContextReceipt | None
    envelope_digest: str

    @property
    def schema_version(self) -> str:
        return LPRH1_SCHEMA_VERSION

    @property
    def handoff_id(self) -> str:
        child = self.context if self.context is not None else self.no_context_receipt
        if child is None:
            raise LPRH1HandoffError(LPRH1_ATOMIC_RESULT_REQUIRED, "envelope child is missing")
        return child.handoff_id

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "handoff_id": self.handoff_id,
            "target_step_digest": self.target_step_digest,
            "receptor_input_digest": self.receptor_input_digest,
            "context_digest": None if self.context is None else self.context.context_digest,
            "no_context_receipt_digest": None if self.no_context_receipt is None else self.no_context_receipt.receipt_digest,
        }

    def __post_init__(self) -> None:
        _require(
            isinstance(self.receptor_input_set, TransientNeuronInputSet)
            and _valid_digest(self.target_step_digest)
            and _valid_digest(self.receptor_input_digest)
            and self.target_step_digest == _digest(_step_payload(self.receptor_input_set.step_time))
            and self.receptor_input_digest == _digest(_receptor_input_payload(self.receptor_input_set))
            and ((self.context is None) != (self.no_context_receipt is None)),
            LPRH1_ATOMIC_RESULT_REQUIRED,
            "envelope requires one receptor input and exactly one result child",
        )
        _require(
            _valid_digest(self.envelope_digest)
            and self.envelope_digest == _digest(self.payload_without_digest()),
            LPRH1_ATOMIC_RESULT_REQUIRED,
            "envelope digest does not bind the canonical payload",
        )


@dataclass(frozen=True, slots=True)
class LPRH1HandoffReceipt:
    handoff_id: str
    receipt_id: str
    execution_id: str
    result_role: str
    envelope_digest: str
    source_object_digests: tuple[str, ...]
    consumed_handoff_ids_before: tuple[str, ...]
    consumed_handoff_ids_after: tuple[str, ...]
    extraction_attempt_count: int
    retry_count: int
    partial_output_count: int
    state_call_count: int
    probe_call_count: int
    field_call_count: int
    receipt_digest: str

    @property
    def schema_version(self) -> str:
        return LPRH1_SCHEMA_VERSION

    @property
    def receipt_kind(self) -> str:
        return "HANDOFF_RESULT"

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "handoff_id": self.handoff_id,
            "receipt_id": self.receipt_id,
            "receipt_kind": self.receipt_kind,
            "execution_id": self.execution_id,
            "result_role": self.result_role,
            "envelope_digest": self.envelope_digest,
            "source_object_digests": list(self.source_object_digests),
            "consumed_handoff_ids_before": list(self.consumed_handoff_ids_before),
            "consumed_handoff_ids_after": list(self.consumed_handoff_ids_after),
            "extraction_attempt_count": self.extraction_attempt_count,
            "retry_count": self.retry_count,
            "partial_output_count": self.partial_output_count,
            "state_call_count": self.state_call_count,
            "probe_call_count": self.probe_call_count,
            "field_call_count": self.field_call_count,
        }

    def __post_init__(self) -> None:
        before = tuple(self.consumed_handoff_ids_before)
        after = tuple(self.consumed_handoff_ids_after)
        sources = tuple(self.source_object_digests)
        expected_receipt_id = _digest(
            {
                "schema_version": self.schema_version,
                "handoff_id": self.handoff_id,
                "receipt_kind": self.receipt_kind,
                "result_role": self.result_role,
            }
        )
        _require(
            _valid_digest(self.handoff_id)
            and _valid_digest(self.receipt_id)
            and _valid_identifier(self.execution_id)
            and self.result_role in {"CONTEXT", "NO_CONTEXT"}
            and self.receipt_id == expected_receipt_id
            and _valid_digest(self.envelope_digest)
            and len(sources) == 8
            and all(_valid_digest(value) for value in sources)
            and before == tuple(sorted(set(before)))
            and all(_valid_digest(value) for value in before)
            and after == tuple(sorted((*before, self.handoff_id)))
            and self.extraction_attempt_count == 1
            and self.retry_count == self.partial_output_count == 0
            and self.state_call_count == self.probe_call_count == self.field_call_count == 0,
            LPRH1_ATOMIC_RESULT_REQUIRED,
            "handoff receipt identity, ledger or call budget is invalid",
        )
        object.__setattr__(self, "source_object_digests", sources)
        object.__setattr__(self, "consumed_handoff_ids_before", before)
        object.__setattr__(self, "consumed_handoff_ids_after", after)
        _require(
            _valid_digest(self.receipt_digest)
            and self.receipt_digest == _digest(self.payload_without_digest()),
            LPRH1_ATOMIC_RESULT_REQUIRED,
            "handoff receipt digest does not bind the canonical payload",
        )


@dataclass(frozen=True, slots=True)
class LPRH1HandoffResult:
    envelope: LPRH1DualInputEnvelope
    receipt: LPRH1HandoffReceipt
    next_consumed_handoff_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        child = self.envelope.context or self.envelope.no_context_receipt
        _require(
            isinstance(self.envelope, LPRH1DualInputEnvelope)
            and isinstance(self.receipt, LPRH1HandoffReceipt)
            and self.envelope.envelope_digest == self.receipt.envelope_digest
            and self.envelope.handoff_id == self.receipt.handoff_id
            and child is not None
            and child.execution_id == self.receipt.execution_id
            and self.next_consumed_handoff_ids == self.receipt.consumed_handoff_ids_after
            and self.receipt.result_role == ("CONTEXT" if self.envelope.context is not None else "NO_CONTEXT"),
            LPRH1_ATOMIC_RESULT_REQUIRED,
            "atomic result links do not agree",
        )


def _build_context(
    *,
    handoff_id: str,
    execution_id: str,
    config: PPB1BankConfig,
    state_digest: str,
    finding: S1WUReadOnlyPerceptualFinding,
    selected_slot: PPB1PrototypeSlot,
    probe_digest: str,
    timed_digest: str,
    target_digest: str,
    dock: SharedFieldDock,
    dock_digest: str,
    receptor_digest: str,
) -> LPRH1TransientLocalPrototypeContext:
    neuron_by_carrier = dict(dock.dock_map.pairs)
    local = tuple(
        LPRH1LocalNeuronContext(
            neuron_id=neuron_by_carrier[carrier],
            dock_id=dock.dock_id,
            carrier_id=carrier,
            prototype_value=value,
        )
        for carrier, value in zip(config.carrier_ids, selected_slot.prototype_values, strict=True)
    )
    values = {
        "handoff_id": handoff_id,
        "execution_id": execution_id,
        "bank_config_digest": config.digest(),
        "bank_state_digest": state_digest,
        "finding_digest": finding.finding_digest,
        "selected_slot_id": selected_slot.slot_id,
        "selected_prototype_digest": finding.selected_prototype_digest,
        "probe_input_digest": probe_digest,
        "timed_probe_digest": timed_digest,
        "target_step_digest": target_digest,
        "shared_dock_digest": dock_digest,
        "receptor_input_digest": receptor_digest,
        "modality_id": config.modality_id,
        "geometry_id": config.geometry_id,
        "carrier_ids": config.carrier_ids,
        "prototype_values": selected_slot.prototype_values,
        "local_contexts": local,
    }
    payload = {
        "schema_version": LPRH1_SCHEMA_VERSION,
        **values,
        "carrier_ids": list(config.carrier_ids),
        "prototype_values": list(selected_slot.prototype_values),
        "local_contexts": [
            {
                "neuron_id": item.neuron_id,
                "dock_id": item.dock_id,
                "carrier_id": item.carrier_id,
                "prototype_value": item.prototype_value,
            }
            for item in local
        ],
    }
    return LPRH1TransientLocalPrototypeContext(**values, context_digest=_digest(payload))


def materialize_lprh1_local_handoff(
    execution_id: str,
    config: PPB1BankConfig,
    state: PPB1BankState,
    finding: S1WUReadOnlyPerceptualFinding,
    timed_probe: OrganismTimedReceptorFrame,
    target_step: MCMFieldStepTime,
    shared_dock: SharedFieldDock,
    receptor_input_set: TransientNeuronInputSet,
    consumed_handoff_ids: tuple[str, ...],
) -> LPRH1HandoffResult:
    """Materialize one private context or explicit no-context result atomically."""

    _require(
        _valid_identifier(execution_id)
        and isinstance(config, PPB1BankConfig)
        and isinstance(state, PPB1BankState)
        and isinstance(finding, S1WUReadOnlyPerceptualFinding)
        and isinstance(timed_probe, OrganismTimedReceptorFrame)
        and isinstance(target_step, MCMFieldStepTime)
        and isinstance(shared_dock, SharedFieldDock)
        and isinstance(receptor_input_set, TransientNeuronInputSet)
        and isinstance(consumed_handoff_ids, tuple)
        and consumed_handoff_ids == tuple(sorted(set(consumed_handoff_ids)))
        and all(_valid_digest(value) for value in consumed_handoff_ids),
        LPRH1_INVALID_INPUT,
        "input types, execution identity or consumed ledger are invalid",
    )

    config_digest = config.digest()
    state_digest = state.digest()
    probe_digest = _digest(_input_projection(timed_probe.frame))
    timed_digest = _digest(_timed_probe_payload(timed_probe))
    target_digest = _digest(_step_payload(target_step))
    dock_digest = _digest(_dock_payload(shared_dock))
    receptor_digest = _digest(_receptor_input_payload(receptor_input_set))
    source_digests = (
        config_digest,
        state_digest,
        finding.finding_digest,
        probe_digest,
        timed_digest,
        target_digest,
        dock_digest,
        receptor_digest,
    )

    _require(
        state.bank_id == config.bank_id
        and state.config_digest == config_digest
        and len(state.slots) == config.capacity
        and finding.bank_id == config.bank_id
        and finding.modality_id == config.modality_id
        and finding.bank_config_digest == config_digest
        and finding.observed_bank_state_digest == state_digest
        and finding.state_identity_digest == _digest(_state_identity_payload(state))
        and finding.probe_input_digest == probe_digest,
        LPRH1_PROVENANCE_MISMATCH,
        "config, state, finding or original probe provenance differs",
    )
    try:
        _validate_state(config, state)
    except ValueError as exc:
        raise LPRH1HandoffError(
            LPRH1_PROVENANCE_MISMATCH,
            "bank state does not satisfy its bound config",
        ) from exc
    _require(
        target_step.clock_id == timed_probe.field_time.clock_id
        and target_step.start_tick == timed_probe.field_time.window_end_tick
        and receptor_input_set.step_time == target_step,
        LPRH1_CAUSAL_TIME_MISMATCH,
        "probe, target step and receptor input are not causally adjacent",
    )
    _require(
        timed_probe.frame.modality_id == config.modality_id
        and timed_probe.frame.geometry_id == config.geometry_id
        and timed_probe.frame.carrier_ids == config.carrier_ids
        and shared_dock.dock_map.modality_id == config.modality_id
        and shared_dock.dock_map.receptor_geometry_id == config.geometry_id
        and set(shared_dock.dock_map.carrier_ids) == set(config.carrier_ids)
        and all(
            any(
                item.neuron_id == neuron_id
                and item.dock_id == shared_dock.dock_id
                and item.carrier_id == carrier_id
                for item in receptor_input_set.neuron_inputs
            )
            for carrier_id, neuron_id in shared_dock.dock_map.pairs
        ),
        LPRH1_LOCAL_MAPPING_MISMATCH,
        "probe, config and shared dock anatomy differ",
    )

    handoff_id = _digest(
        {
            "schema_version": LPRH1_SCHEMA_VERSION,
            "execution_id": execution_id,
            "bank_config_digest": config_digest,
            "bank_state_digest": state_digest,
            "finding_digest": finding.finding_digest,
            "timed_probe_digest": timed_digest,
            "target_step_digest": target_digest,
            "shared_dock_digest": dock_digest,
            "receptor_input_digest": receptor_digest,
        }
    )
    _require(
        handoff_id not in consumed_handoff_ids,
        LPRH1_DUPLICATE_HANDOFF,
        "derived handoff identity was already consumed",
    )

    selected_slot = None
    if finding.recognized:
        selected_slot = next(
            (slot for slot in state.slots if slot.slot_id == finding.selected_slot_id),
            None,
        )
        _require(
            selected_slot is not None
            and selected_slot.occupied
            and selected_slot.support_count is not None
            and selected_slot.support_count >= config.stable_after
            and finding.selected_prototype_digest == _prototype_digest(selected_slot.prototype_values),
            LPRH1_SLOT_NOT_STABLE,
            "recognized finding does not bind one stable selected slot",
        )

    if selected_slot is not None:
        context = _build_context(
            handoff_id=handoff_id,
            execution_id=execution_id,
            config=config,
            state_digest=state_digest,
            finding=finding,
            selected_slot=selected_slot,
            probe_digest=probe_digest,
            timed_digest=timed_digest,
            target_digest=target_digest,
            dock=shared_dock,
            dock_digest=dock_digest,
            receptor_digest=receptor_digest,
        )
        no_context = None
        result_role = "CONTEXT"
    else:
        context = None
        result_role = "NO_CONTEXT"
        no_context_receipt_id = _digest(
            {
                "schema_version": LPRH1_SCHEMA_VERSION,
                "handoff_id": handoff_id,
                "receipt_kind": "NO_CONTEXT_SOURCE",
            }
        )
        no_context_values = {
            "handoff_id": handoff_id,
            "receipt_id": no_context_receipt_id,
            "execution_id": execution_id,
            "reason": "UNRECOGNIZED",
            "bank_state_digest": state_digest,
            "finding_digest": finding.finding_digest,
            "probe_input_digest": probe_digest,
            "timed_probe_digest": timed_digest,
            "target_step_digest": target_digest,
            "receptor_input_digest": receptor_digest,
        }
        no_context_payload = {
            "schema_version": LPRH1_SCHEMA_VERSION,
            **no_context_values,
            "receipt_kind": "NO_CONTEXT_SOURCE",
        }
        no_context = LPRH1NoContextReceipt(
            **no_context_values,
            receipt_digest=_digest(no_context_payload),
        )

    envelope_values = {
        "target_step_digest": target_digest,
        "receptor_input_digest": receptor_digest,
        "receptor_input_set": receptor_input_set,
        "context": context,
        "no_context_receipt": no_context,
    }
    envelope_payload = {
        "schema_version": LPRH1_SCHEMA_VERSION,
        "handoff_id": handoff_id,
        "target_step_digest": target_digest,
        "receptor_input_digest": receptor_digest,
        "context_digest": None if context is None else context.context_digest,
        "no_context_receipt_digest": None if no_context is None else no_context.receipt_digest,
    }
    envelope = LPRH1DualInputEnvelope(
        **envelope_values,
        envelope_digest=_digest(envelope_payload),
    )
    after = tuple(sorted((*consumed_handoff_ids, handoff_id)))
    receipt_id = _digest(
        {
            "schema_version": LPRH1_SCHEMA_VERSION,
            "handoff_id": handoff_id,
            "receipt_kind": "HANDOFF_RESULT",
            "result_role": result_role,
        }
    )
    receipt_values = {
        "handoff_id": handoff_id,
        "receipt_id": receipt_id,
        "execution_id": execution_id,
        "result_role": result_role,
        "envelope_digest": envelope.envelope_digest,
        "source_object_digests": source_digests,
        "consumed_handoff_ids_before": consumed_handoff_ids,
        "consumed_handoff_ids_after": after,
        "extraction_attempt_count": 1,
        "retry_count": 0,
        "partial_output_count": 0,
        "state_call_count": 0,
        "probe_call_count": 0,
        "field_call_count": 0,
    }
    receipt_payload = {
        "schema_version": LPRH1_SCHEMA_VERSION,
        **receipt_values,
        "receipt_kind": "HANDOFF_RESULT",
        "source_object_digests": list(source_digests),
        "consumed_handoff_ids_before": list(consumed_handoff_ids),
        "consumed_handoff_ids_after": list(after),
    }
    receipt = LPRH1HandoffReceipt(
        **receipt_values,
        receipt_digest=_digest(receipt_payload),
    )

    _require(
        config.digest() == config_digest
        and state.digest() == state_digest
        and finding.finding_digest == source_digests[2]
        and _digest(_input_projection(timed_probe.frame)) == probe_digest
        and _digest(_dock_payload(shared_dock)) == dock_digest
        and _digest(_receptor_input_payload(receptor_input_set)) == receptor_digest,
        LPRH1_ATOMIC_RESULT_REQUIRED,
        "one source changed during handoff materialization",
    )
    return LPRH1HandoffResult(envelope, receipt, after)
