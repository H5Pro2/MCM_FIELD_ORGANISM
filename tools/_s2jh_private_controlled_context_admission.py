"""Private read-only admission of an already classified two-area context."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import NoReturn

from tools import _s2ic_private_two_area_conflict_contract as signal_contract


S2JH_SCHEMA = "s2jh.controlled-context-admission.v1"
S2JG_CONTRACT_DIGEST = (
    "5bde38988b0203cbcf1173e14620ea9bdf372e7f22c7a0f3f682946d0ad426af"
)

FUNCTION_ROLES = ("ADMISSION", "DIRECT_TABLE_BASELINE")
DECISIONS = ("ALLOW_CONTEXT", "PROCEED_WITHOUT_CONTEXT")
REASONS = (
    "UNIQUE_APPLICABLE_CONTEXT",
    "EQUIVALENT_CONTEXTS",
    "CONFLICT_WITHHELD",
    "CONTEXT_ABSENT",
    "CONTEXT_INAPPLICABLE",
)
OWNER_STATES = ("READY", "CONSUMED", "FAILED")
OPERATIONS = ("J1", "J2", "J3", "J4")
ERROR_REGISTRY = {
    "S2JH-E001": "TYPE_OR_SCHEMA_INVALID",
    "S2JH-E002": "SOURCE_OR_DIGEST_INVALID",
    "S2JH-E003": "OWNER_INVALID",
    "S2JH-E004": "SIGNAL_EVIDENCE_INVALID",
    "S2JH-E005": "READ_ONLY_VIOLATION",
    "S2JH-E006": "RESOURCE_OR_REUSE_VIOLATION",
}

ARTIFACT_LIMITS = {
    "input": 2304,
    "owner": 1536,
    "ledger": 1280,
    "result": 2560,
    "receipt": 2048,
}
MAX_LOGICAL_OPERATIONS = 4
MAX_SUCCESS_ARTIFACT_BYTES = 11264

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{7,95}$")


class S2JHAdmissionError(RuntimeError):
    """One neutral typed S2-JH contract error."""

    def __init__(self, code: str, operation: str) -> None:
        message_id = ERROR_REGISTRY.get(code)
        if message_id is None or operation not in OPERATIONS:
            code = "S2JH-E001"
            operation = "J1"
            message_id = ERROR_REGISTRY[code]
        super().__init__(f"{code}: {message_id}")
        self.code = code
        self.message_id = message_id
        self.operation = operation


def fail(code: str, operation: str) -> NoReturn:
    raise S2JHAdmissionError(code, operation)


def require(condition: bool, code: str, operation: str) -> None:
    if not condition:
        fail(code, operation)


def canonical_bytes(payload: object, *, newline: bool = False) -> bytes:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")
    return encoded + (b"\n" if newline else b"")


def digest(payload: object) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def artifact_size(payload: object) -> int:
    return len(canonical_bytes(payload, newline=True))


def valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def valid_identifier(value: object) -> bool:
    return type(value) is str and _IDENTIFIER.fullmatch(value) is not None


def _check_size(payload: object, role: str, operation: str) -> None:
    require(role in ARTIFACT_LIMITS, "S2JH-E001", operation)
    require(
        artifact_size(payload) <= ARTIFACT_LIMITS[role] < 4095,
        "S2JH-E006",
        operation,
    )


def _check_digest(
    actual: object,
    payload: dict[str, object],
    role: str,
    digest_field: str,
    operation: str,
) -> None:
    require(valid_digest(actual) and actual == digest(payload), "S2JH-E002", operation)
    _check_size({**payload, digest_field: actual}, role, operation)


@dataclass(frozen=True, slots=True)
class ControlledContextAdmissionInput:
    invocation_id: str
    function_role: str
    contract_digest: str
    signal_input_digest: str
    signal_result_digest: str
    signal_receipt_digest: str
    signal_owner_poststate_digest: str
    source_signal_status: str
    probe_digest: str
    probe_source_digest: str
    bundle_digest: str
    bundle_source_digest: str
    config_digest: str
    composite_state_digest: str
    a_applicability_finding_digest: str
    b_applicability_finding_digest: str
    comparison_digest: str
    input_digest: str
    schema: str = S2JH_SCHEMA

    def __post_init__(self) -> None:
        require(self.schema == S2JH_SCHEMA, "S2JH-E001", "J1")
        require(valid_identifier(self.invocation_id), "S2JH-E001", "J1")
        require(self.function_role in FUNCTION_ROLES, "S2JH-E001", "J1")
        require(self.contract_digest == S2JG_CONTRACT_DIGEST, "S2JH-E002", "J1")
        require(
            self.source_signal_status in signal_contract.RESULT_STATUSES,
            "S2JH-E004",
            "J1",
        )
        require(
            all(
                valid_digest(value)
                for value in (
                    self.signal_input_digest,
                    self.signal_result_digest,
                    self.signal_receipt_digest,
                    self.signal_owner_poststate_digest,
                    self.probe_digest,
                    self.probe_source_digest,
                    self.bundle_digest,
                    self.bundle_source_digest,
                    self.config_digest,
                    self.composite_state_digest,
                    self.a_applicability_finding_digest,
                    self.b_applicability_finding_digest,
                    self.comparison_digest,
                )
            ),
            "S2JH-E002",
            "J1",
        )
        _check_digest(
            self.input_digest,
            self.payload_without_digest(),
            "input",
            "input_digest",
            "J1",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "invocation_id": self.invocation_id,
            "function_role": self.function_role,
            "contract_digest": self.contract_digest,
            "signal_input_digest": self.signal_input_digest,
            "signal_result_digest": self.signal_result_digest,
            "signal_receipt_digest": self.signal_receipt_digest,
            "signal_owner_poststate_digest": self.signal_owner_poststate_digest,
            "source_signal_status": self.source_signal_status,
            "probe_digest": self.probe_digest,
            "probe_source_digest": self.probe_source_digest,
            "bundle_digest": self.bundle_digest,
            "bundle_source_digest": self.bundle_source_digest,
            "config_digest": self.config_digest,
            "composite_state_digest": self.composite_state_digest,
            "a_applicability_finding_digest": self.a_applicability_finding_digest,
            "b_applicability_finding_digest": self.b_applicability_finding_digest,
            "comparison_digest": self.comparison_digest,
        }

    @classmethod
    def build(
        cls,
        invocation_id: str,
        function_role: str,
        signal_input: signal_contract.TwoAreaConflictSignalInput,
        signal_commit: signal_contract.TwoAreaConflictSignalCommit,
    ) -> "ControlledContextAdmissionInput":
        result = signal_commit.result
        payload = {
            "schema": S2JH_SCHEMA,
            "invocation_id": invocation_id,
            "function_role": function_role,
            "contract_digest": S2JG_CONTRACT_DIGEST,
            "signal_input_digest": signal_input.input_digest,
            "signal_result_digest": result.result_digest,
            "signal_receipt_digest": signal_commit.receipt.receipt_digest,
            "signal_owner_poststate_digest": signal_commit.owner_poststate.owner_poststate_digest,
            "source_signal_status": result.status,
            "probe_digest": signal_input.probe_digest,
            "probe_source_digest": signal_input.probe_source_digest,
            "bundle_digest": signal_input.bundle_digest,
            "bundle_source_digest": signal_input.bundle_source_digest,
            "config_digest": signal_input.config_digest,
            "composite_state_digest": signal_input.composite_state_digest,
            "a_applicability_finding_digest": result.a_applicability_finding_digest,
            "b_applicability_finding_digest": result.b_applicability_finding_digest,
            "comparison_digest": result.comparison_digest,
        }
        return cls(
            invocation_id,
            function_role,
            S2JG_CONTRACT_DIGEST,
            signal_input.input_digest,
            result.result_digest,
            signal_commit.receipt.receipt_digest,
            signal_commit.owner_poststate.owner_poststate_digest,
            result.status,
            signal_input.probe_digest,
            signal_input.probe_source_digest,
            signal_input.bundle_digest,
            signal_input.bundle_source_digest,
            signal_input.config_digest,
            signal_input.composite_state_digest,
            result.a_applicability_finding_digest,
            result.b_applicability_finding_digest,
            result.comparison_digest,
            digest(payload),
        )


@dataclass(frozen=True, slots=True)
class ContextAdmissionOwnerState:
    owner_id: str
    invocation_id: str
    function_role: str
    input_digest: str
    prior_owner_digest: str | None
    terminal_binding_digest: str | None
    state: str
    owner_state_digest: str
    schema: str = S2JH_SCHEMA

    def __post_init__(self) -> None:
        operation = "J1" if self.state == "READY" else "J4"
        require(self.schema == S2JH_SCHEMA, "S2JH-E001", operation)
        require(
            valid_identifier(self.owner_id) and valid_identifier(self.invocation_id),
            "S2JH-E003",
            operation,
        )
        require(self.function_role in FUNCTION_ROLES, "S2JH-E003", operation)
        require(valid_digest(self.input_digest), "S2JH-E003", operation)
        require(self.state in OWNER_STATES, "S2JH-E003", operation)
        if self.state == "READY":
            require(
                self.prior_owner_digest is None and self.terminal_binding_digest is None,
                "S2JH-E003",
                operation,
            )
        else:
            require(
                valid_digest(self.prior_owner_digest)
                and valid_digest(self.terminal_binding_digest),
                "S2JH-E003",
                operation,
            )
        _check_digest(
            self.owner_state_digest,
            self.payload_without_digest(),
            "owner",
            "owner_state_digest",
            operation,
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "owner_id": self.owner_id,
            "invocation_id": self.invocation_id,
            "function_role": self.function_role,
            "input_digest": self.input_digest,
            "prior_owner_digest": self.prior_owner_digest,
            "terminal_binding_digest": self.terminal_binding_digest,
            "state": self.state,
        }

    @classmethod
    def ready(
        cls,
        owner_id: str,
        admission_input: ControlledContextAdmissionInput,
    ) -> "ContextAdmissionOwnerState":
        payload = {
            "schema": S2JH_SCHEMA,
            "owner_id": owner_id,
            "invocation_id": admission_input.invocation_id,
            "function_role": admission_input.function_role,
            "input_digest": admission_input.input_digest,
            "prior_owner_digest": None,
            "terminal_binding_digest": None,
            "state": "READY",
        }
        return cls(
            owner_id,
            admission_input.invocation_id,
            admission_input.function_role,
            admission_input.input_digest,
            None,
            None,
            "READY",
            digest(payload),
        )

    @classmethod
    def terminal(
        cls,
        prestate: "ContextAdmissionOwnerState",
        state: str,
        terminal_binding_digest: str,
    ) -> "ContextAdmissionOwnerState":
        payload = {
            "schema": S2JH_SCHEMA,
            "owner_id": prestate.owner_id,
            "invocation_id": prestate.invocation_id,
            "function_role": prestate.function_role,
            "input_digest": prestate.input_digest,
            "prior_owner_digest": prestate.owner_state_digest,
            "terminal_binding_digest": terminal_binding_digest,
            "state": state,
        }
        return cls(
            prestate.owner_id,
            prestate.invocation_id,
            prestate.function_role,
            prestate.input_digest,
            prestate.owner_state_digest,
            terminal_binding_digest,
            state,
            digest(payload),
        )


class ContextAdmissionOwner:
    """Atomic one-shot owner for one admission or baseline decision."""

    __slots__ = ("_prestate", "_poststate")

    def __init__(self, prestate: ContextAdmissionOwnerState) -> None:
        require(
            type(prestate) is ContextAdmissionOwnerState and prestate.state == "READY",
            "S2JH-E003",
            "J1",
        )
        prestate.__post_init__()
        self._prestate = prestate
        self._poststate: ContextAdmissionOwnerState | None = None

    @property
    def prestate(self) -> ContextAdmissionOwnerState:
        return self._prestate

    @property
    def poststate(self) -> ContextAdmissionOwnerState | None:
        return self._poststate

    @property
    def state(self) -> str:
        return "READY" if self._poststate is None else self._poststate.state

    def commit(self, poststate: ContextAdmissionOwnerState) -> None:
        require(self._poststate is None, "S2JH-E006", "J4")
        require(type(poststate) is ContextAdmissionOwnerState, "S2JH-E003", "J4")
        poststate.__post_init__()
        require(
            poststate.prior_owner_digest == self._prestate.owner_state_digest
            and poststate.owner_id == self._prestate.owner_id
            and poststate.invocation_id == self._prestate.invocation_id
            and poststate.function_role == self._prestate.function_role
            and poststate.input_digest == self._prestate.input_digest,
            "S2JH-E003",
            "J4",
        )
        self._poststate = poststate


@dataclass(frozen=True, slots=True)
class ContextAdmissionLedger:
    input_validation_count: int
    signal_artifact_validation_count: int
    state_digest_validation_count: int
    decision_table_lookup_count: int
    admitted_role_reference_count: int
    supplement_digest_reference_count: int
    new_digest_operation_count: int
    logical_operation_count: int
    published_success_object_count: int
    memory_receptor_or_field_call_count: int
    ledger_digest: str
    schema: str = S2JH_SCHEMA

    def __post_init__(self) -> None:
        require(self.schema == S2JH_SCHEMA, "S2JH-E001", "J3")
        values = tuple(
            getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in ("ledger_digest", "schema")
        )
        require(all(type(value) is int and value >= 0 for value in values), "S2JH-E006", "J3")
        role_count = self.admitted_role_reference_count
        require(
            self.input_validation_count == 1
            and self.signal_artifact_validation_count == 7
            and self.state_digest_validation_count == 2
            and self.decision_table_lookup_count == 1
            and 0 <= role_count <= 2
            and self.supplement_digest_reference_count == role_count
            and self.new_digest_operation_count == 4 + (1 if role_count else 0)
            and self.logical_operation_count == MAX_LOGICAL_OPERATIONS
            and self.published_success_object_count == 3
            and self.memory_receptor_or_field_call_count == 0,
            "S2JH-E006",
            "J3",
        )
        _check_digest(
            self.ledger_digest,
            self.payload_without_digest(),
            "ledger",
            "ledger_digest",
            "J3",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "input_validation_count": self.input_validation_count,
            "signal_artifact_validation_count": self.signal_artifact_validation_count,
            "state_digest_validation_count": self.state_digest_validation_count,
            "decision_table_lookup_count": self.decision_table_lookup_count,
            "admitted_role_reference_count": self.admitted_role_reference_count,
            "supplement_digest_reference_count": self.supplement_digest_reference_count,
            "new_digest_operation_count": self.new_digest_operation_count,
            "logical_operation_count": self.logical_operation_count,
            "published_success_object_count": self.published_success_object_count,
            "memory_receptor_or_field_call_count": self.memory_receptor_or_field_call_count,
        }

    @classmethod
    def build(cls, admitted_role_count: int) -> "ContextAdmissionLedger":
        values = (
            1,
            7,
            2,
            1,
            admitted_role_count,
            admitted_role_count,
            4 + (1 if admitted_role_count else 0),
            MAX_LOGICAL_OPERATIONS,
            3,
            0,
        )
        names = tuple(
            name for name in cls.__dataclass_fields__ if name not in ("ledger_digest", "schema")
        )
        payload = {"schema": S2JH_SCHEMA, **dict(zip(names, values, strict=True))}
        return cls(*values, digest(payload))


@dataclass(frozen=True, slots=True)
class ControlledPerceptualContextAdmission:
    function_role: str
    contract_digest: str
    decision: str
    source_signal_status: str
    admitted_role: str | None
    equivalent_role_set_digest: str | None
    common_supplement_digest: str | None
    admitted_context_binding_digest: str | None
    reason: str
    input_digest: str
    signal_result_digest: str
    signal_receipt_digest: str
    probe_digest: str
    bundle_digest: str
    composite_state_digest: str
    prestate_digest: str
    poststate_digest: str
    resource_ledger_digest: str
    selected_area: None
    ranking: None
    merged_context_digest: None
    result_digest: str
    schema: str = S2JH_SCHEMA

    def __post_init__(self) -> None:
        require(self.schema == S2JH_SCHEMA, "S2JH-E001", "J3")
        require(self.function_role in FUNCTION_ROLES, "S2JH-E001", "J3")
        require(self.contract_digest == S2JG_CONTRACT_DIGEST, "S2JH-E002", "J3")
        require(self.decision in DECISIONS and self.reason in REASONS, "S2JH-E004", "J3")
        require(self.source_signal_status in signal_contract.RESULT_STATUSES, "S2JH-E004", "J3")
        require(
            all(
                valid_digest(value)
                for value in (
                    self.input_digest,
                    self.signal_result_digest,
                    self.signal_receipt_digest,
                    self.probe_digest,
                    self.bundle_digest,
                    self.composite_state_digest,
                    self.prestate_digest,
                    self.poststate_digest,
                    self.resource_ledger_digest,
                )
            ),
            "S2JH-E002",
            "J3",
        )
        require(self.prestate_digest == self.poststate_digest == self.composite_state_digest, "S2JH-E005", "J3")
        require(self.selected_area is None and self.ranking is None and self.merged_context_digest is None, "S2JH-E004", "J3")
        if self.source_signal_status == "SINGLE_SOURCE":
            require(
                self.decision == "ALLOW_CONTEXT"
                and self.reason == "UNIQUE_APPLICABLE_CONTEXT"
                and self.admitted_role in signal_contract.AREAS
                and self.equivalent_role_set_digest is None
                and valid_digest(self.common_supplement_digest)
                and valid_digest(self.admitted_context_binding_digest),
                "S2JH-E004",
                "J3",
            )
        elif self.source_signal_status == "CONSISTENT":
            require(
                self.decision == "ALLOW_CONTEXT"
                and self.reason == "EQUIVALENT_CONTEXTS"
                and self.admitted_role is None
                and valid_digest(self.equivalent_role_set_digest)
                and valid_digest(self.common_supplement_digest)
                and valid_digest(self.admitted_context_binding_digest),
                "S2JH-E004",
                "J3",
            )
        else:
            expected_reason = {
                "CONFLICT": "CONFLICT_WITHHELD",
                "NO_CONTEXT": "CONTEXT_ABSENT",
                "NO_APPLICABLE_CONTEXT": "CONTEXT_INAPPLICABLE",
            }.get(self.source_signal_status)
            require(
                self.decision == "PROCEED_WITHOUT_CONTEXT"
                and self.reason == expected_reason
                and self.admitted_role is None
                and self.equivalent_role_set_digest is None
                and self.common_supplement_digest is None
                and self.admitted_context_binding_digest is None,
                "S2JH-E004",
                "J3",
            )
        _check_digest(
            self.result_digest,
            self.payload_without_digest(),
            "result",
            "result_digest",
            "J3",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "function_role": self.function_role,
            "contract_digest": self.contract_digest,
            "decision": self.decision,
            "source_signal_status": self.source_signal_status,
            "admitted_role": self.admitted_role,
            "equivalent_role_set_digest": self.equivalent_role_set_digest,
            "common_supplement_digest": self.common_supplement_digest,
            "admitted_context_binding_digest": self.admitted_context_binding_digest,
            "reason": self.reason,
            "input_digest": self.input_digest,
            "signal_result_digest": self.signal_result_digest,
            "signal_receipt_digest": self.signal_receipt_digest,
            "probe_digest": self.probe_digest,
            "bundle_digest": self.bundle_digest,
            "composite_state_digest": self.composite_state_digest,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "resource_ledger_digest": self.resource_ledger_digest,
            "selected_area": self.selected_area,
            "ranking": self.ranking,
            "merged_context_digest": self.merged_context_digest,
        }


@dataclass(frozen=True, slots=True)
class ContextAdmissionReceipt:
    invocation_id: str
    function_role: str
    owner_prestate_digest: str
    input_digest: str
    signal_result_digest: str
    resource_ledger_digest: str
    result_digest: str
    owner_poststate_digest: str
    receipt_digest: str
    schema: str = S2JH_SCHEMA

    def __post_init__(self) -> None:
        require(self.schema == S2JH_SCHEMA, "S2JH-E001", "J4")
        require(valid_identifier(self.invocation_id) and self.function_role in FUNCTION_ROLES, "S2JH-E001", "J4")
        require(
            all(
                valid_digest(value)
                for value in (
                    self.owner_prestate_digest,
                    self.input_digest,
                    self.signal_result_digest,
                    self.resource_ledger_digest,
                    self.result_digest,
                    self.owner_poststate_digest,
                )
            ),
            "S2JH-E002",
            "J4",
        )
        _check_digest(
            self.receipt_digest,
            self.payload_without_digest(),
            "receipt",
            "receipt_digest",
            "J4",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "invocation_id": self.invocation_id,
            "function_role": self.function_role,
            "owner_prestate_digest": self.owner_prestate_digest,
            "input_digest": self.input_digest,
            "signal_result_digest": self.signal_result_digest,
            "resource_ledger_digest": self.resource_ledger_digest,
            "result_digest": self.result_digest,
            "owner_poststate_digest": self.owner_poststate_digest,
        }


@dataclass(frozen=True, slots=True)
class ControlledContextAdmissionCommit:
    result: ControlledPerceptualContextAdmission
    receipt: ContextAdmissionReceipt
    owner_poststate: ContextAdmissionOwnerState


class S2JHAdmissionFailure(RuntimeError):
    """Fail-closed terminal failure with no regular admission result."""

    def __init__(self, error: S2JHAdmissionError, owner_poststate: ContextAdmissionOwnerState) -> None:
        super().__init__(str(error))
        self.code = error.code
        self.operation = error.operation
        self.owner_poststate = owner_poststate


def _expected_signal_status(
    a_finding: signal_contract.AreaApplicabilityFinding,
    b_finding: signal_contract.AreaApplicabilityFinding,
    comparison: signal_contract.MaskedSupplementComparison,
) -> str:
    present_count = sum(item.status != "ABSENT_VALID" for item in (a_finding, b_finding))
    applicable_count = sum(item.status == "APPLICABLE" for item in (a_finding, b_finding))
    if present_count == 0:
        return "NO_CONTEXT"
    if applicable_count == 0:
        return "NO_APPLICABLE_CONTEXT"
    if applicable_count == 1:
        return "SINGLE_SOURCE"
    require(comparison.comparison_status in ("EQUAL", "DIFFERENT"), "S2JH-E004", "J1")
    return "CONSISTENT" if comparison.comparison_status == "EQUAL" else "CONFLICT"


def validate_admission_sources(
    admission_input: ControlledContextAdmissionInput,
    signal_input: signal_contract.TwoAreaConflictSignalInput,
    signal_commit: signal_contract.TwoAreaConflictSignalCommit,
    a_finding: signal_contract.AreaApplicabilityFinding,
    b_finding: signal_contract.AreaApplicabilityFinding,
    comparison: signal_contract.MaskedSupplementComparison,
    owner: ContextAdmissionOwner,
    expected_role: str,
) -> None:
    require(type(admission_input) is ControlledContextAdmissionInput, "S2JH-E001", "J1")
    require(type(signal_input) is signal_contract.TwoAreaConflictSignalInput, "S2JH-E001", "J1")
    require(type(signal_commit) is signal_contract.TwoAreaConflictSignalCommit, "S2JH-E001", "J1")
    require(type(a_finding) is signal_contract.AreaApplicabilityFinding, "S2JH-E004", "J1")
    require(type(b_finding) is signal_contract.AreaApplicabilityFinding, "S2JH-E004", "J1")
    require(type(comparison) is signal_contract.MaskedSupplementComparison, "S2JH-E004", "J1")
    require(type(owner) is ContextAdmissionOwner, "S2JH-E003", "J1")
    require(expected_role in FUNCTION_ROLES and admission_input.function_role == expected_role, "S2JH-E001", "J1")

    admission_input.__post_init__()
    try:
        signal_input.__post_init__()
        a_finding.__post_init__()
        b_finding.__post_init__()
        comparison.__post_init__()
        signal_commit.result.__post_init__()
        signal_commit.receipt.__post_init__()
        signal_commit.owner_poststate.__post_init__()
    except signal_contract.S2ICContractError as error:
        if error.code == "S2HZ-E002":
            fail("S2JH-E002", "J1")
        if error.code == "S2HZ-E006":
            fail("S2JH-E005", "J1")
        fail("S2JH-E004", "J1")

    result = signal_commit.result
    receipt = signal_commit.receipt
    signal_owner = signal_commit.owner_poststate
    expected_present = tuple(item.area for item in (a_finding, b_finding) if item.status != "ABSENT_VALID")
    expected_applicable = tuple(item.area for item in (a_finding, b_finding) if item.status == "APPLICABLE")
    require(signal_input.function_role == "SIGNAL" and result.function_role == "SIGNAL", "S2JH-E004", "J1")
    require(a_finding.area == "A_RECENT" and b_finding.area == "B_STABLE", "S2JH-E004", "J1")
    require(
        a_finding.input_digest == b_finding.input_digest == comparison.input_digest == signal_input.input_digest
        and a_finding.probe_digest == b_finding.probe_digest == signal_input.probe_digest
        and a_finding.bundle_digest == b_finding.bundle_digest == signal_input.bundle_digest
        and comparison.a_applicability_finding_digest == a_finding.finding_digest
        and comparison.b_applicability_finding_digest == b_finding.finding_digest,
        "S2JH-E002",
        "J1",
    )
    require(
        result.input_digest == signal_input.input_digest
        and result.probe_digest == signal_input.probe_digest
        and result.bundle_digest == signal_input.bundle_digest
        and result.a_applicability_finding_digest == a_finding.finding_digest
        and result.b_applicability_finding_digest == b_finding.finding_digest
        and result.comparison_digest == comparison.comparison_digest
        and result.present_areas == expected_present
        and result.applicable_areas == expected_applicable
        and result.differing_masked_positions == comparison.differing_masked_positions
        and result.status == _expected_signal_status(a_finding, b_finding, comparison),
        "S2JH-E004",
        "J1",
    )
    require(
        receipt.invocation_id == signal_input.invocation_id
        and receipt.function_role == "SIGNAL"
        and receipt.input_digest == signal_input.input_digest
        and receipt.a_applicability_finding_digest == a_finding.finding_digest
        and receipt.b_applicability_finding_digest == b_finding.finding_digest
        and receipt.comparison_digest == comparison.comparison_digest
        and receipt.resource_ledger_digest == result.resource_ledger_digest
        and receipt.result_digest == result.result_digest
        and receipt.owner_prestate_digest == signal_owner.prior_owner_digest
        and receipt.owner_poststate_digest == signal_owner.owner_poststate_digest,
        "S2JH-E002",
        "J1",
    )
    require(
        signal_owner.invocation_id == signal_input.invocation_id
        and signal_owner.function_role == "SIGNAL"
        and signal_owner.input_digest == signal_input.input_digest
        and signal_owner.state == "CONSUMED"
        and signal_owner.terminal_binding_digest == result.result_digest,
        "S2JH-E002",
        "J1",
    )
    require(
        admission_input.signal_input_digest == signal_input.input_digest
        and admission_input.signal_result_digest == result.result_digest
        and admission_input.signal_receipt_digest == receipt.receipt_digest
        and admission_input.signal_owner_poststate_digest == signal_owner.owner_poststate_digest
        and admission_input.source_signal_status == result.status
        and admission_input.probe_digest == signal_input.probe_digest
        and admission_input.probe_source_digest == signal_input.probe_source_digest
        and admission_input.bundle_digest == signal_input.bundle_digest
        and admission_input.bundle_source_digest == signal_input.bundle_source_digest
        and admission_input.config_digest == signal_input.config_digest
        and admission_input.composite_state_digest == signal_input.composite_state_digest
        and admission_input.a_applicability_finding_digest == a_finding.finding_digest
        and admission_input.b_applicability_finding_digest == b_finding.finding_digest
        and admission_input.comparison_digest == comparison.comparison_digest,
        "S2JH-E002",
        "J1",
    )
    require(
        result.prestate_digest
        == result.poststate_digest
        == signal_input.bundle_prestate_digest
        == signal_input.bundle_poststate_digest
        == signal_input.composite_state_digest,
        "S2JH-E005",
        "J1",
    )
    owner.prestate.__post_init__()
    require(
        owner.state == "READY"
        and owner.prestate.invocation_id == admission_input.invocation_id
        and owner.prestate.function_role == expected_role
        and owner.prestate.input_digest == admission_input.input_digest,
        "S2JH-E003",
        "J1",
    )


def build_admission_result(
    admission_input: ControlledContextAdmissionInput,
    signal_commit: signal_contract.TwoAreaConflictSignalCommit,
    decision: str,
    reason: str,
    admitted_role: str | None,
    equivalent_role_set_digest: str | None,
    common_supplement_digest: str | None,
    admitted_context_binding_digest: str | None,
    ledger: ContextAdmissionLedger,
) -> ControlledPerceptualContextAdmission:
    result = signal_commit.result
    payload = {
        "schema": S2JH_SCHEMA,
        "function_role": admission_input.function_role,
        "contract_digest": S2JG_CONTRACT_DIGEST,
        "decision": decision,
        "source_signal_status": result.status,
        "admitted_role": admitted_role,
        "equivalent_role_set_digest": equivalent_role_set_digest,
        "common_supplement_digest": common_supplement_digest,
        "admitted_context_binding_digest": admitted_context_binding_digest,
        "reason": reason,
        "input_digest": admission_input.input_digest,
        "signal_result_digest": result.result_digest,
        "signal_receipt_digest": signal_commit.receipt.receipt_digest,
        "probe_digest": result.probe_digest,
        "bundle_digest": result.bundle_digest,
        "composite_state_digest": admission_input.composite_state_digest,
        "prestate_digest": result.prestate_digest,
        "poststate_digest": result.poststate_digest,
        "resource_ledger_digest": ledger.ledger_digest,
        "selected_area": None,
        "ranking": None,
        "merged_context_digest": None,
    }
    return ControlledPerceptualContextAdmission(
        admission_input.function_role,
        S2JG_CONTRACT_DIGEST,
        decision,
        result.status,
        admitted_role,
        equivalent_role_set_digest,
        common_supplement_digest,
        admitted_context_binding_digest,
        reason,
        admission_input.input_digest,
        result.result_digest,
        signal_commit.receipt.receipt_digest,
        result.probe_digest,
        result.bundle_digest,
        admission_input.composite_state_digest,
        result.prestate_digest,
        result.poststate_digest,
        ledger.ledger_digest,
        None,
        None,
        None,
        digest(payload),
    )


def publish_success(
    owner: ContextAdmissionOwner,
    admission_input: ControlledContextAdmissionInput,
    ledger: ContextAdmissionLedger,
    result: ControlledPerceptualContextAdmission,
) -> ControlledContextAdmissionCommit:
    require(owner.state == "READY", "S2JH-E006", "J4")
    poststate = ContextAdmissionOwnerState.terminal(owner.prestate, "CONSUMED", result.result_digest)
    payload = {
        "schema": S2JH_SCHEMA,
        "invocation_id": admission_input.invocation_id,
        "function_role": admission_input.function_role,
        "owner_prestate_digest": owner.prestate.owner_state_digest,
        "input_digest": admission_input.input_digest,
        "signal_result_digest": admission_input.signal_result_digest,
        "resource_ledger_digest": ledger.ledger_digest,
        "result_digest": result.result_digest,
        "owner_poststate_digest": poststate.owner_state_digest,
    }
    receipt = ContextAdmissionReceipt(
        admission_input.invocation_id,
        admission_input.function_role,
        owner.prestate.owner_state_digest,
        admission_input.input_digest,
        admission_input.signal_result_digest,
        ledger.ledger_digest,
        result.result_digest,
        poststate.owner_state_digest,
        digest(payload),
    )
    owner.commit(poststate)
    return ControlledContextAdmissionCommit(result, receipt, poststate)


def publish_failure(
    owner: ContextAdmissionOwner,
    admission_input: ControlledContextAdmissionInput,
    error: S2JHAdmissionError,
) -> NoReturn:
    require(type(owner) is ContextAdmissionOwner and owner.state == "READY", "S2JH-E006", "J4")
    failure_digest = digest(
        {
            "schema": S2JH_SCHEMA,
            "input_digest": admission_input.input_digest,
            "owner_prestate_digest": owner.prestate.owner_state_digest,
            "error_code": error.code,
            "operation": error.operation,
        }
    )
    poststate = ContextAdmissionOwnerState.terminal(owner.prestate, "FAILED", failure_digest)
    owner.commit(poststate)
    raise S2JHAdmissionFailure(error, poststate)


def _decision_projection(
    signal_commit: signal_contract.TwoAreaConflictSignalCommit,
    a_finding: signal_contract.AreaApplicabilityFinding,
    b_finding: signal_contract.AreaApplicabilityFinding,
) -> tuple[str, str, str | None, str | None, str | None, str | None]:
    status = signal_commit.result.status
    if status == "SINGLE_SOURCE":
        finding = a_finding if a_finding.status == "APPLICABLE" else b_finding
        require(finding.status == "APPLICABLE" and valid_digest(finding.masked_values_digest), "S2JH-E004", "J2")
        context_binding = digest(
            {
                "schema": S2JH_SCHEMA,
                "binding_kind": "UNIQUE_APPLICABLE_CONTEXT",
                "area": finding.area,
                "finding_digest": finding.finding_digest,
                "candidate_digest": finding.candidate_digest,
                "masked_values_digest": finding.masked_values_digest,
            }
        )
        return (
            "ALLOW_CONTEXT",
            "UNIQUE_APPLICABLE_CONTEXT",
            finding.area,
            None,
            finding.masked_values_digest,
            context_binding,
        )
    if status == "CONSISTENT":
        require(
            a_finding.status == b_finding.status == "APPLICABLE"
            and a_finding.masked_values_digest == b_finding.masked_values_digest
            and valid_digest(a_finding.masked_values_digest),
            "S2JH-E004",
            "J2",
        )
        common_digest = a_finding.masked_values_digest
        role_set_digest = digest(
            {
                "schema": S2JH_SCHEMA,
                "binding_kind": "UNORDERED_EQUIVALENT_ROLE_SET",
                "role_finding_pairs": sorted(
                    (
                        (a_finding.area, a_finding.finding_digest),
                        (b_finding.area, b_finding.finding_digest),
                    )
                ),
            }
        )
        equivalence_binding = digest(
            {
                "schema": S2JH_SCHEMA,
                "binding_kind": "UNORDERED_EQUIVALENT_CONTEXTS",
                "equivalent_role_set_digest": role_set_digest,
                "common_masked_values_digest": common_digest,
            }
        )
        return (
            "ALLOW_CONTEXT",
            "EQUIVALENT_CONTEXTS",
            None,
            role_set_digest,
            common_digest,
            equivalence_binding,
        )
    if status == "CONFLICT":
        return "PROCEED_WITHOUT_CONTEXT", "CONFLICT_WITHHELD", None, None, None, None
    if status == "NO_CONTEXT":
        return "PROCEED_WITHOUT_CONTEXT", "CONTEXT_ABSENT", None, None, None, None
    require(status == "NO_APPLICABLE_CONTEXT", "S2JH-E004", "J2")
    return "PROCEED_WITHOUT_CONTEXT", "CONTEXT_INAPPLICABLE", None, None, None, None


def form_controlled_context_admission(
    admission_input: ControlledContextAdmissionInput,
    signal_input: signal_contract.TwoAreaConflictSignalInput,
    signal_commit: signal_contract.TwoAreaConflictSignalCommit,
    a_finding: signal_contract.AreaApplicabilityFinding,
    b_finding: signal_contract.AreaApplicabilityFinding,
    comparison: signal_contract.MaskedSupplementComparison,
    owner: ContextAdmissionOwner,
) -> ControlledContextAdmissionCommit:
    """Admit only unique or proven-equivalent context without choosing a winner."""

    if type(owner) is not ContextAdmissionOwner or owner.state != "READY":
        fail("S2JH-E006", "J1")
    try:
        before = (
            signal_input.input_digest,
            signal_commit.result.result_digest,
            signal_commit.receipt.receipt_digest,
            signal_commit.owner_poststate.owner_poststate_digest,
            a_finding.finding_digest,
            b_finding.finding_digest,
            comparison.comparison_digest,
            signal_commit.result.prestate_digest,
            signal_commit.result.poststate_digest,
        )
        validate_admission_sources(
            admission_input,
            signal_input,
            signal_commit,
            a_finding,
            b_finding,
            comparison,
            owner,
            "ADMISSION",
        )
        projection = _decision_projection(signal_commit, a_finding, b_finding)
        admitted_count = 2 if projection[3] is not None else (1 if projection[2] is not None else 0)
        ledger = ContextAdmissionLedger.build(admitted_count)
        after = (
            signal_input.input_digest,
            signal_commit.result.result_digest,
            signal_commit.receipt.receipt_digest,
            signal_commit.owner_poststate.owner_poststate_digest,
            a_finding.finding_digest,
            b_finding.finding_digest,
            comparison.comparison_digest,
            signal_commit.result.prestate_digest,
            signal_commit.result.poststate_digest,
        )
        require(before == after, "S2JH-E005", "J3")
        result = build_admission_result(
            admission_input,
            signal_commit,
            *projection,
            ledger,
        )
        return publish_success(owner, admission_input, ledger, result)
    except S2JHAdmissionFailure:
        raise
    except S2JHAdmissionError as error:
        publish_failure(owner, admission_input, error)
    except Exception as error:
        publish_failure(owner, admission_input, S2JHAdmissionError("S2JH-E001", "J1"))
        raise AssertionError("unreachable") from error


__all__: tuple[str, ...] = ()
