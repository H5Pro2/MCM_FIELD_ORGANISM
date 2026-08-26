"""Pure matched one-state retention baseline for G2/D3 checkpoints."""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
import math
from typing import Any

from .g2_d3_two_step_composition import (
    G2D3TwoStepCompositionRegistry,
    build_g2_d3_two_step_composition_registry,
)
from .kfs1_schema_validator import canonical_json_bytes, sha256_hex


STATE_SCHEMA_ID = "g2_d3_single_state_retention_state"
STATE_SCHEMA_VERSION = "s1oy.v1"
CONFIGURATION_SCHEMA_ID = "g2_d3_single_state_retention_configuration"
CONFIGURATION_SCHEMA_VERSION = "s1oy.v1"
EVENT_SCHEMA_ID = "g2_d3_model_neutral_continuation_event"
EVENT_SCHEMA_VERSION = "s1oy.v1"
RECEIPT_SCHEMA_ID = "g2_d3_matched_retention_baseline_receipt"
RECEIPT_SCHEMA_VERSION = "s1oy.v1"
BASELINE_CLASS_ID = "G2_D3_MATCHED_SINGLE_STATE_RETENTION_BASELINE"
EVENT_CLASS_ID = "G2_D3_FRESH_CONTINUATION"
UPDATE_RULE_ID = "ONE_STATIONARY_RETENTION_UPDATE_PER_FRESH_CONTINUATION"
BASELINE_STATUSES = ("THREE_CHECKPOINTS_EVALUATED", "not_computable")
BASELINE_PHASES = (
    "api_intake",
    "sequence_provenance_validation",
    "configuration_validation",
    "initial_state_validation",
    "cp0_readout",
    "event1_validation",
    "update1",
    "cp1_readout",
    "event2_validation",
    "update2",
    "cp2_readout",
    "component_evaluation",
    "persistence_guard",
    "baseline_receipt",
)
FAILURE_CODES = (
    "OY_SEQUENCE_PROVENANCE_INVALID",
    "OY_CONFIGURATION_INVALID",
    "OY_INITIAL_STATE_INVALID",
    "OY_CP0_READOUT_FAILED",
    "OY_EVENT1_INVALID",
    "OY_UPDATE1_FAILED",
    "OY_CP1_READOUT_FAILED",
    "OY_EVENT2_INVALID",
    "OY_UPDATE2_FAILED",
    "OY_CP2_READOUT_FAILED",
    "OY_COMPONENT_EVALUATION_FAILED",
)
COMPOSITION_CONTRACT_DIGEST = (
    "e68646a2d4a605ecdd36125dcd5f97cd849091d5af1bbcf1f587b1c01e1c2e06"
)
CANDIDATE_CHECKPOINT_CONTRACT_DIGEST = (
    "582e0fa653c8843cb56e848abc1ea34b1e97b455f8b0a130f22678afb555191f"
)
EVENT_CONTRACT_DIGEST = (
    "d9bfd11f5b1a555bceca419b5f5b6ccfcc1206b692881f0be4b1a29642cfb23a"
)
STATE_ANATOMY_CONTRACT_DIGEST = (
    "e886e77d6bec13dbbd462f0454b4758961f499ab28c85608cde068f695d349fb"
)
COMPARISON_CONTRACT_DIGEST = (
    "7b3818ca3e9ce2b2b1502399e52d69ca25a02247cca43f06b883633a61d28f0d"
)
BASELINE_CONTRACT_DIGEST = (
    "18ea29690ef7e62ae086c93b43dc3678f8ad5fed81aa1a0fde24983649d6f036"
)
EQUATION_CONTRACT_DIGEST = (
    "90ed790d33882b8fd7691f75d43ac39530c232712bb3a67766f07771ba82b84a"
)
CONFIGURATION_IDENTITY_DIGEST = (
    "658d726944639840ed5c6ff0db0f3b8c863567dfa1fbd7aa2bc0fb7ade25ceb8"
)
CONFIGURATION_INPUT_DIGEST = (
    "12e6d381c0dcc0f170c39453bde291152bc55499e0292edacb2d0a09c27e1d93"
)
EVENT_INPUT_DIGEST = (
    "dbffc12bef77155c2271d3990ebe1b8ae4d481ce6155bf8716b1f6e19128b30f"
)
EXPECTED_COMPARISON_DIGEST = (
    "5c8d3b60bbc205594974f632a878472bf628426dc914af72514cf7b42e8a86a5"
)
_NOT_COMPUTABLE = "not_computable"


@dataclass(frozen=True)
class G2D3MatchedRetentionBaselineRegistry:
    state_schema_id: str
    state_schema_version: str
    configuration_schema_id: str
    configuration_schema_version: str
    event_schema_id: str
    event_schema_version: str
    baseline_receipt_schema_id: str
    baseline_receipt_schema_version: str
    baseline_class_id: str
    event_class_id: str
    update_rule_id: str
    baseline_statuses: tuple[str, ...]
    baseline_phases: tuple[str, ...]
    failure_codes: tuple[str, ...]
    accepted_composition_contract_digest: str
    accepted_candidate_checkpoint_contract_digest: str
    event_contract_digest: str
    state_anatomy_contract_digest: str
    comparison_contract_digest: str
    baseline_contract_digest: str


@dataclass(frozen=True)
class G2D3MatchedRetentionBaselineReceipt:
    receipt_schema_id: str
    receipt_schema_version: str
    baseline_class_id: str
    first_boundary_input_digest: str
    second_boundary_input_digest: str
    chain_role: str
    initial_state_input_bytes_digest: str
    configuration_input_bytes_digest: str
    continuation_event_input_bytes_digest: str
    cp0_state_input_bytes_digest: str
    cp0_state_record_digest: str
    cp0_value: float | str
    cp1_state_input_bytes_digest: str
    cp1_state_record_digest: str
    cp1_value: float | str
    cp2_state_input_bytes_digest: str
    cp2_state_record_digest: str
    cp2_value: float | str
    delta_cp1_cp0: float | str
    delta_cp2_cp1: float | str
    delta_cp2_cp0: float | str
    comparison_digest: str
    baseline_status: str
    validation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    accepted_composition_contract_digest: str
    accepted_event_contract_digest: str
    accepted_state_anatomy_contract_digest: str
    accepted_equation_contract_digest: str
    accepted_configuration_identity_digest: str
    baseline_contract_digest: str
    baseline_receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        payload = {item.name: getattr(self, item.name) for item in fields(self)}
        payload["completed_checks"] = list(self.completed_checks)
        payload["failure_reasons"] = list(self.failure_reasons)
        return payload


@dataclass(frozen=True)
class G2D3MatchedRetentionBaselineResult:
    checkpoint_values: tuple[float, float, float] | str
    receipt: G2D3MatchedRetentionBaselineReceipt


@dataclass(frozen=True)
class _RetentionState:
    retained_capacity: float
    raw_bytes: bytes
    input_digest: str
    record_digest: str


def build_g2_d3_matched_retention_baseline_registry() -> G2D3MatchedRetentionBaselineRegistry:
    return G2D3MatchedRetentionBaselineRegistry(
        state_schema_id=STATE_SCHEMA_ID,
        state_schema_version=STATE_SCHEMA_VERSION,
        configuration_schema_id=CONFIGURATION_SCHEMA_ID,
        configuration_schema_version=CONFIGURATION_SCHEMA_VERSION,
        event_schema_id=EVENT_SCHEMA_ID,
        event_schema_version=EVENT_SCHEMA_VERSION,
        baseline_receipt_schema_id=RECEIPT_SCHEMA_ID,
        baseline_receipt_schema_version=RECEIPT_SCHEMA_VERSION,
        baseline_class_id=BASELINE_CLASS_ID,
        event_class_id=EVENT_CLASS_ID,
        update_rule_id=UPDATE_RULE_ID,
        baseline_statuses=BASELINE_STATUSES,
        baseline_phases=BASELINE_PHASES,
        failure_codes=FAILURE_CODES,
        accepted_composition_contract_digest=COMPOSITION_CONTRACT_DIGEST,
        accepted_candidate_checkpoint_contract_digest=CANDIDATE_CHECKPOINT_CONTRACT_DIGEST,
        event_contract_digest=EVENT_CONTRACT_DIGEST,
        state_anatomy_contract_digest=STATE_ANATOMY_CONTRACT_DIGEST,
        comparison_contract_digest=COMPARISON_CONTRACT_DIGEST,
        baseline_contract_digest=BASELINE_CONTRACT_DIGEST,
    )


def _validate_api(
    first_boundary_input_digest: str,
    second_boundary_input_digest: str,
    initial_state_raw_bytes: bytes,
    continuation_event_raw_bytes: bytes,
    configuration_raw_bytes: bytes,
    baseline_registry: G2D3MatchedRetentionBaselineRegistry,
    sequence_registry: G2D3TwoStepCompositionRegistry,
) -> None:
    for name, value in (
        ("first_boundary_input_digest", first_boundary_input_digest),
        ("second_boundary_input_digest", second_boundary_input_digest),
    ):
        if type(value) is not str:
            raise TypeError(f"{name} must be str")
    for name, value in (
        ("initial_state_raw_bytes", initial_state_raw_bytes),
        ("continuation_event_raw_bytes", continuation_event_raw_bytes),
        ("configuration_raw_bytes", configuration_raw_bytes),
    ):
        if type(value) is not bytes:
            raise TypeError(f"{name} must be bytes")
    if type(baseline_registry) is not G2D3MatchedRetentionBaselineRegistry:
        raise TypeError("baseline_registry must be G2D3MatchedRetentionBaselineRegistry")
    if baseline_registry != build_g2_d3_matched_retention_baseline_registry():
        raise ValueError("baseline_registry does not match the bound S1-OY registry")
    if type(sequence_registry) is not G2D3TwoStepCompositionRegistry:
        raise TypeError("sequence_registry must be G2D3TwoStepCompositionRegistry")
    if sequence_registry != build_g2_d3_two_step_composition_registry():
        raise ValueError("sequence_registry does not match the bound S1-OQ registry")


def _is_sha256_hex(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _parse_canonical_object(raw_bytes: bytes) -> dict[str, Any] | None:
    try:
        value = json.loads(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if type(value) is not dict or canonical_json_bytes(value) != raw_bytes:
        return None
    return value


def _validate_configuration(raw_bytes: bytes) -> tuple[float, float] | None:
    if sha256_hex(raw_bytes) != CONFIGURATION_INPUT_DIGEST:
        return None
    record = _parse_canonical_object(raw_bytes)
    if record is None or set(record) != {
        "baseline_class_id",
        "configuration_record_digest",
        "configuration_schema_id",
        "configuration_schema_version",
        "initial_retained_capacity",
        "retention_fraction_per_fresh_continuation",
        "update_rule_id",
    }:
        return None
    payload = {key: value for key, value in record.items() if key != "configuration_record_digest"}
    if record["configuration_record_digest"] != sha256_hex(canonical_json_bytes(payload)):
        return None
    if (
        record["baseline_class_id"] != BASELINE_CLASS_ID
        or record["configuration_schema_id"] != CONFIGURATION_SCHEMA_ID
        or record["configuration_schema_version"] != CONFIGURATION_SCHEMA_VERSION
        or record["update_rule_id"] != UPDATE_RULE_ID
        or type(record["initial_retained_capacity"]) is not float
        or type(record["retention_fraction_per_fresh_continuation"]) is not float
        or record["initial_retained_capacity"] != 0.5
        or record["retention_fraction_per_fresh_continuation"] != 0.5
    ):
        return None
    return record["initial_retained_capacity"], record["retention_fraction_per_fresh_continuation"]


def _validate_state(raw_bytes: bytes, expected_value: float | None = None) -> _RetentionState | None:
    record = _parse_canonical_object(raw_bytes)
    if record is None or set(record) != {
        "baseline_class_id",
        "retained_capacity",
        "state_record_digest",
        "state_schema_id",
        "state_schema_version",
        "state_status",
    }:
        return None
    payload = {key: value for key, value in record.items() if key != "state_record_digest"}
    record_digest = sha256_hex(canonical_json_bytes(payload))
    value = record["retained_capacity"]
    if (
        record["state_record_digest"] != record_digest
        or record["baseline_class_id"] != BASELINE_CLASS_ID
        or record["state_schema_id"] != STATE_SCHEMA_ID
        or record["state_schema_version"] != STATE_SCHEMA_VERSION
        or record["state_status"] != "valid"
        or type(value) is not float
        or not math.isfinite(value)
        or value < 0.0
        or (expected_value is not None and value != expected_value)
    ):
        return None
    return _RetentionState(value, raw_bytes, sha256_hex(raw_bytes), record_digest)


def _validate_event(raw_bytes: bytes) -> bool:
    if sha256_hex(raw_bytes) != EVENT_INPUT_DIGEST:
        return False
    record = _parse_canonical_object(raw_bytes)
    return record == {
        "event_class_id": EVENT_CLASS_ID,
        "event_schema_id": EVENT_SCHEMA_ID,
        "event_schema_version": EVENT_SCHEMA_VERSION,
    }


def _build_state(retained_capacity: float) -> _RetentionState:
    payload = {
        "baseline_class_id": BASELINE_CLASS_ID,
        "retained_capacity": retained_capacity,
        "state_schema_id": STATE_SCHEMA_ID,
        "state_schema_version": STATE_SCHEMA_VERSION,
        "state_status": "valid",
    }
    record_digest = sha256_hex(canonical_json_bytes(payload))
    raw_bytes = canonical_json_bytes({**payload, "state_record_digest": record_digest})
    state = _validate_state(raw_bytes, retained_capacity)
    if state is None:
        raise ValueError("constructed retention state is invalid")
    return state


def _update_retained_capacity(
    current: _RetentionState,
    retention_fraction: float,
    continuation_event_raw_bytes: bytes,
) -> _RetentionState | None:
    if not _validate_event(continuation_event_raw_bytes):
        return None
    next_value = retention_fraction * current.retained_capacity
    if not math.isfinite(next_value) or next_value < 0.0:
        return None
    return _build_state(next_value)


def _build_receipt(
    *,
    first_digest: str,
    second_digest: str,
    chain_role: str,
    initial_digest: str,
    configuration_digest: str,
    event_digest: str,
    states: tuple[_RetentionState, _RetentionState, _RetentionState] | None,
    values: tuple[float, float, float] | None,
    components: tuple[float, float, float] | None,
    comparison_digest: str,
    status: str,
    completed: list[str],
    failures: tuple[str, ...],
) -> G2D3MatchedRetentionBaselineReceipt:
    state_input_digests = (
        tuple(state.input_digest for state in states)
        if states is not None else (_NOT_COMPUTABLE,) * 3
    )
    state_record_digests = (
        tuple(state.record_digest for state in states)
        if states is not None else (_NOT_COMPUTABLE,) * 3
    )
    public_values = values if values is not None else (_NOT_COMPUTABLE,) * 3
    public_components = components if components is not None else (_NOT_COMPUTABLE,) * 3
    payload = {
        "receipt_schema_id": RECEIPT_SCHEMA_ID,
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "baseline_class_id": BASELINE_CLASS_ID,
        "first_boundary_input_digest": first_digest,
        "second_boundary_input_digest": second_digest,
        "chain_role": chain_role,
        "initial_state_input_bytes_digest": initial_digest,
        "configuration_input_bytes_digest": configuration_digest,
        "continuation_event_input_bytes_digest": event_digest,
        "cp0_state_input_bytes_digest": state_input_digests[0],
        "cp0_state_record_digest": state_record_digests[0],
        "cp0_value": public_values[0],
        "cp1_state_input_bytes_digest": state_input_digests[1],
        "cp1_state_record_digest": state_record_digests[1],
        "cp1_value": public_values[1],
        "cp2_state_input_bytes_digest": state_input_digests[2],
        "cp2_state_record_digest": state_record_digests[2],
        "cp2_value": public_values[2],
        "delta_cp1_cp0": public_components[0],
        "delta_cp2_cp1": public_components[1],
        "delta_cp2_cp0": public_components[2],
        "comparison_digest": comparison_digest,
        "baseline_status": status,
        "validation_status": "invalid" if failures else "valid",
        "completed_checks": completed,
        "failure_reasons": list(failures),
        "accepted_composition_contract_digest": COMPOSITION_CONTRACT_DIGEST,
        "accepted_event_contract_digest": EVENT_CONTRACT_DIGEST,
        "accepted_state_anatomy_contract_digest": STATE_ANATOMY_CONTRACT_DIGEST,
        "accepted_equation_contract_digest": EQUATION_CONTRACT_DIGEST,
        "accepted_configuration_identity_digest": CONFIGURATION_IDENTITY_DIGEST,
        "baseline_contract_digest": BASELINE_CONTRACT_DIGEST,
    }
    receipt_digest = sha256_hex(canonical_json_bytes(payload))
    return G2D3MatchedRetentionBaselineReceipt(
        **{
            **payload,
            "completed_checks": tuple(completed),
            "failure_reasons": failures,
            "baseline_receipt_digest": receipt_digest,
        }
    )


def evaluate_g2_d3_matched_retention_baseline(
    first_boundary_input_digest: str,
    second_boundary_input_digest: str,
    initial_state_raw_bytes: bytes,
    continuation_event_raw_bytes: bytes,
    configuration_raw_bytes: bytes,
    baseline_registry: G2D3MatchedRetentionBaselineRegistry,
    sequence_registry: G2D3TwoStepCompositionRegistry,
) -> G2D3MatchedRetentionBaselineResult:
    """Evaluate one matched retention state over two identical events."""

    _validate_api(
        first_boundary_input_digest,
        second_boundary_input_digest,
        initial_state_raw_bytes,
        continuation_event_raw_bytes,
        configuration_raw_bytes,
        baseline_registry,
        sequence_registry,
    )
    completed = ["api_intake"]
    chain_role = _NOT_COMPUTABLE
    initial_digest = sha256_hex(initial_state_raw_bytes)
    configuration_digest = sha256_hex(configuration_raw_bytes)
    event_digest = sha256_hex(continuation_event_raw_bytes)

    def fail(code: str) -> G2D3MatchedRetentionBaselineResult:
        completed.extend(("persistence_guard", "baseline_receipt"))
        receipt = _build_receipt(
            first_digest=first_boundary_input_digest,
            second_digest=second_boundary_input_digest,
            chain_role=chain_role,
            initial_digest=initial_digest,
            configuration_digest=configuration_digest,
            event_digest=event_digest,
            states=None,
            values=None,
            components=None,
            comparison_digest=_NOT_COMPUTABLE,
            status=_NOT_COMPUTABLE,
            completed=completed,
            failures=(code,),
        )
        return G2D3MatchedRetentionBaselineResult(_NOT_COMPUTABLE, receipt)

    chain = next(
        (
            item for item in sequence_registry.chain_records
            if item.first_boundary_input_digest == first_boundary_input_digest
            and item.second_boundary_input_digest == second_boundary_input_digest
        ),
        None,
    )
    completed.append("sequence_provenance_validation")
    if (
        chain is None
        or not _is_sha256_hex(first_boundary_input_digest)
        or not _is_sha256_hex(second_boundary_input_digest)
    ):
        return fail("OY_SEQUENCE_PROVENANCE_INVALID")
    chain_role = chain.chain_role

    configuration = _validate_configuration(configuration_raw_bytes)
    completed.append("configuration_validation")
    if configuration is None:
        return fail("OY_CONFIGURATION_INVALID")
    initial_value, retention_fraction = configuration

    cp0 = _validate_state(initial_state_raw_bytes, initial_value)
    completed.append("initial_state_validation")
    if cp0 is None:
        return fail("OY_INITIAL_STATE_INVALID")
    completed.append("cp0_readout")
    if cp0.retained_capacity != 0.5:
        return fail("OY_CP0_READOUT_FAILED")

    completed.append("event1_validation")
    if not _validate_event(continuation_event_raw_bytes):
        return fail("OY_EVENT1_INVALID")
    cp1 = _update_retained_capacity(cp0, retention_fraction, continuation_event_raw_bytes)
    completed.append("update1")
    if cp1 is None:
        return fail("OY_UPDATE1_FAILED")
    completed.append("cp1_readout")
    if cp1.retained_capacity != 0.25:
        return fail("OY_CP1_READOUT_FAILED")

    completed.append("event2_validation")
    if not _validate_event(continuation_event_raw_bytes):
        return fail("OY_EVENT2_INVALID")
    cp2 = _update_retained_capacity(cp1, retention_fraction, continuation_event_raw_bytes)
    completed.append("update2")
    if cp2 is None:
        return fail("OY_UPDATE2_FAILED")
    completed.append("cp2_readout")
    if cp2.retained_capacity != 0.125:
        return fail("OY_CP2_READOUT_FAILED")

    values = (cp0.retained_capacity, cp1.retained_capacity, cp2.retained_capacity)
    components = (values[1] - values[0], values[2] - values[1], values[2] - values[0])
    comparison_payload = {
        "checkpoint_values": list(values),
        "directed_components": list(components),
    }
    comparison_digest = sha256_hex(canonical_json_bytes(comparison_payload))
    completed.append("component_evaluation")
    if (
        values != (0.5, 0.25, 0.125)
        or components != (-0.25, -0.125, -0.375)
        or comparison_digest != EXPECTED_COMPARISON_DIGEST
    ):
        return fail("OY_COMPONENT_EVALUATION_FAILED")

    completed.extend(("persistence_guard", "baseline_receipt"))
    receipt = _build_receipt(
        first_digest=first_boundary_input_digest,
        second_digest=second_boundary_input_digest,
        chain_role=chain_role,
        initial_digest=initial_digest,
        configuration_digest=configuration_digest,
        event_digest=event_digest,
        states=(cp0, cp1, cp2),
        values=values,
        components=components,
        comparison_digest=comparison_digest,
        status="THREE_CHECKPOINTS_EVALUATED",
        completed=completed,
        failures=(),
    )
    return G2D3MatchedRetentionBaselineResult(values, receipt)


__all__ = (
    "STATE_SCHEMA_ID",
    "STATE_SCHEMA_VERSION",
    "CONFIGURATION_SCHEMA_ID",
    "CONFIGURATION_SCHEMA_VERSION",
    "EVENT_SCHEMA_ID",
    "EVENT_SCHEMA_VERSION",
    "RECEIPT_SCHEMA_ID",
    "RECEIPT_SCHEMA_VERSION",
    "BASELINE_CLASS_ID",
    "EVENT_CLASS_ID",
    "UPDATE_RULE_ID",
    "BASELINE_STATUSES",
    "BASELINE_PHASES",
    "FAILURE_CODES",
    "COMPOSITION_CONTRACT_DIGEST",
    "CANDIDATE_CHECKPOINT_CONTRACT_DIGEST",
    "EVENT_CONTRACT_DIGEST",
    "STATE_ANATOMY_CONTRACT_DIGEST",
    "COMPARISON_CONTRACT_DIGEST",
    "BASELINE_CONTRACT_DIGEST",
    "EQUATION_CONTRACT_DIGEST",
    "CONFIGURATION_IDENTITY_DIGEST",
    "G2D3MatchedRetentionBaselineRegistry",
    "G2D3MatchedRetentionBaselineReceipt",
    "G2D3MatchedRetentionBaselineResult",
    "build_g2_d3_matched_retention_baseline_registry",
    "evaluate_g2_d3_matched_retention_baseline",
)
