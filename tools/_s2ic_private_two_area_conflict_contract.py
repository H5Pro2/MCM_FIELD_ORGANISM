"""Private S2-IC data contract for the read-only two-area conflict signal."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
from typing import NoReturn

from tools import _s2gb_private_perceptual_context_bundle as context
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_masked_visual_context_consumer as probe_contract


S2IC_SCHEMA = "s2ic.two-area-conflict-signal.v1"
S2IB_CONTRACT_DIGEST = (
    "dca7ecfe8822f1fceb49381a7b4ced12c535b74e9eb5b4089c63bbaf4eb9a54d"
)

AREAS = ("A_RECENT", "B_STABLE")
FUNCTION_ROLES = ("SIGNAL", "DIRECT_BASELINE")
APPLICABILITY_STATUSES = ("APPLICABLE", "ABSENT_VALID", "VISIBLE_CONFLICT")
COMPARISON_STATUSES = ("NOT_PERFORMED", "EQUAL", "DIFFERENT")
RESULT_STATUSES = (
    "NO_CONTEXT",
    "NO_APPLICABLE_CONTEXT",
    "SINGLE_SOURCE",
    "CONSISTENT",
    "CONFLICT",
)
OWNER_STATES = ("READY", "CONSUMED", "FAILED")
OPERATIONS = ("O1", "O2", "O3", "O4", "O5", "O6")
DECISION_PATHS = (
    ("APPLICABLE", "APPLICABLE", "EQUAL", "CONSISTENT"),
    ("APPLICABLE", "APPLICABLE", "DIFFERENT", "CONFLICT"),
    ("APPLICABLE", "ABSENT_VALID", "NOT_PERFORMED", "SINGLE_SOURCE"),
    ("ABSENT_VALID", "APPLICABLE", "NOT_PERFORMED", "SINGLE_SOURCE"),
    ("ABSENT_VALID", "ABSENT_VALID", "NOT_PERFORMED", "NO_CONTEXT"),
    ("APPLICABLE", "VISIBLE_CONFLICT", "NOT_PERFORMED", "SINGLE_SOURCE"),
    ("VISIBLE_CONFLICT", "APPLICABLE", "NOT_PERFORMED", "SINGLE_SOURCE"),
    (
        "VISIBLE_CONFLICT",
        "VISIBLE_CONFLICT",
        "NOT_PERFORMED",
        "NO_APPLICABLE_CONTEXT",
    ),
    (
        "VISIBLE_CONFLICT",
        "ABSENT_VALID",
        "NOT_PERFORMED",
        "NO_APPLICABLE_CONTEXT",
    ),
    (
        "ABSENT_VALID",
        "VISIBLE_CONFLICT",
        "NOT_PERFORMED",
        "NO_APPLICABLE_CONTEXT",
    ),
)

ERROR_REGISTRY = {
    "S2HZ-E001": "TYPE_OR_SCHEMA_INVALID",
    "S2HZ-E002": "SOURCE_OR_DIGEST_INVALID",
    "S2HZ-E003": "OWNER_INVALID",
    "S2HZ-E004": "PROBE_OR_MASK_INVALID",
    "S2HZ-E005": "AREA_EVIDENCE_INVALID",
    "S2HZ-E006": "READ_ONLY_VIOLATION",
    "S2HZ-E007": "RESOURCE_BOUND_EXCEEDED",
    "S2HZ-E008": "ATOMICITY_OR_REUSE_VIOLATION",
}

ARTIFACT_LIMITS = {
    "owner": 768,
    "input": 1792,
    "applicability": 2048,
    "comparison": 1280,
    "ledger": 1536,
    "result": 2048,
    "receipt": 2048,
    "error_cause": 1024,
    "error_receipt": 1536,
}

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{7,95}$")


class S2ICContractError(RuntimeError):
    """One neutral, typed S2-IC contract failure."""

    def __init__(self, code: str, operation: str) -> None:
        message_id = ERROR_REGISTRY.get(code)
        if message_id is None or operation not in OPERATIONS:
            code = "S2HZ-E001"
            message_id = ERROR_REGISTRY[code]
            operation = "O1"
        super().__init__(f"{code}: {message_id}")
        self.code = code
        self.message_id = message_id
        self.operation = operation


def fail(code: str, operation: str) -> NoReturn:
    raise S2ICContractError(code, operation)


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


def _valid_digest_tuple(values: object) -> bool:
    return type(values) is tuple and all(valid_digest(value) for value in values)


def _valid_positions(values: object, allowed: tuple[int, ...]) -> bool:
    return (
        type(values) is tuple
        and all(type(value) is int and value in allowed for value in values)
        and len(set(values)) == len(values)
        and tuple(sorted(values)) == values
    )


def _valid_float_values(values: object, expected_length: int) -> bool:
    return (
        type(values) is tuple
        and len(values) == expected_length
        and all(
            type(value) is float and math.isfinite(value) and 0.0 <= value <= 1.0
            for value in values
        )
    )


def _check_size(payload: object, role: str, operation: str = "O5") -> None:
    require(role in ARTIFACT_LIMITS, "S2HZ-E001", operation)
    require(
        artifact_size(payload) <= ARTIFACT_LIMITS[role] < 4095,
        "S2HZ-E007",
        operation,
    )


def _check_schema_digest(
    schema: object,
    actual_digest: object,
    payload: object,
    role: str,
    digest_field: str,
    operation: str,
) -> None:
    require(schema == S2IC_SCHEMA, "S2HZ-E001", operation)
    require(valid_digest(actual_digest), "S2HZ-E002", operation)
    require(actual_digest == digest(payload), "S2HZ-E002", operation)
    full_payload = dict(payload) if type(payload) is dict else {}
    full_payload[digest_field] = actual_digest
    _check_size(full_payload, role, operation if operation == "O5" else "O5")


def mask_digest_for(probe: probe_contract.MaskedVisualProbe) -> str:
    return digest(
        {
            "visible_positions": list(probe.visible_positions),
            "masked_positions": list(probe.masked_positions),
        }
    )


@dataclass(frozen=True, slots=True)
class TwoAreaConflictSignalInput:
    invocation_id: str
    function_role: str
    probe_digest: str
    probe_source_digest: str
    mask_digest: str
    bundle_digest: str
    bundle_source_digest: str
    config_digest: str
    composite_state_digest: str
    bundle_prestate_digest: str
    bundle_poststate_digest: str
    a_area_finding_digest: str
    b_area_finding_digest: str
    input_digest: str
    schema: str = S2IC_SCHEMA

    def __post_init__(self) -> None:
        require(valid_identifier(self.invocation_id), "S2HZ-E001", "O1")
        require(self.function_role in FUNCTION_ROLES, "S2HZ-E001", "O1")
        require(
            all(
                valid_digest(value)
                for value in (
                    self.probe_digest,
                    self.probe_source_digest,
                    self.mask_digest,
                    self.bundle_digest,
                    self.bundle_source_digest,
                    self.config_digest,
                    self.composite_state_digest,
                    self.bundle_prestate_digest,
                    self.bundle_poststate_digest,
                    self.a_area_finding_digest,
                    self.b_area_finding_digest,
                )
            ),
            "S2HZ-E002",
            "O1",
        )
        require(
            self.bundle_prestate_digest
            == self.bundle_poststate_digest
            == self.composite_state_digest,
            "S2HZ-E006",
            "O1",
        )
        _check_schema_digest(
            self.schema,
            self.input_digest,
            self.payload_without_digest(),
            "input",
            "input_digest",
            "O1",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "invocation_id": self.invocation_id,
            "function_role": self.function_role,
            "probe_digest": self.probe_digest,
            "probe_source_digest": self.probe_source_digest,
            "mask_digest": self.mask_digest,
            "bundle_digest": self.bundle_digest,
            "bundle_source_digest": self.bundle_source_digest,
            "config_digest": self.config_digest,
            "composite_state_digest": self.composite_state_digest,
            "bundle_prestate_digest": self.bundle_prestate_digest,
            "bundle_poststate_digest": self.bundle_poststate_digest,
            "a_area_finding_digest": self.a_area_finding_digest,
            "b_area_finding_digest": self.b_area_finding_digest,
        }

    @classmethod
    def build(
        cls,
        invocation_id: str,
        function_role: str,
        probe: probe_contract.MaskedVisualProbe,
        bundle: two_area.TwoAreaContextBundle,
    ) -> "TwoAreaConflictSignalInput":
        require(type(bundle.area_findings) is tuple and len(bundle.area_findings) == 2, "S2HZ-E005", "O1")
        payload = {
            "schema": S2IC_SCHEMA,
            "invocation_id": invocation_id,
            "function_role": function_role,
            "probe_digest": probe.probe_digest,
            "probe_source_digest": probe.source_digest,
            "mask_digest": mask_digest_for(probe),
            "bundle_digest": bundle.bundle_digest,
            "bundle_source_digest": bundle.source_digest,
            "config_digest": bundle.config_digest,
            "composite_state_digest": bundle.composite_state_digest,
            "bundle_prestate_digest": bundle.prestate_digest,
            "bundle_poststate_digest": bundle.poststate_digest,
            "a_area_finding_digest": bundle.area_findings[0].finding_digest,
            "b_area_finding_digest": bundle.area_findings[1].finding_digest,
        }
        return cls(
            invocation_id,
            function_role,
            probe.probe_digest,
            probe.source_digest,
            payload["mask_digest"],
            bundle.bundle_digest,
            bundle.source_digest,
            bundle.config_digest,
            bundle.composite_state_digest,
            bundle.prestate_digest,
            bundle.poststate_digest,
            bundle.area_findings[0].finding_digest,
            bundle.area_findings[1].finding_digest,
            digest(payload),
        )


@dataclass(frozen=True, slots=True)
class TwoAreaConflictOwnerPrestate:
    owner_id: str
    invocation_id: str
    function_role: str
    input_digest: str
    state: str
    owner_prestate_digest: str
    schema: str = S2IC_SCHEMA

    def __post_init__(self) -> None:
        require(valid_identifier(self.owner_id), "S2HZ-E003", "O1")
        require(valid_identifier(self.invocation_id), "S2HZ-E003", "O1")
        require(self.function_role in FUNCTION_ROLES and self.state == "READY", "S2HZ-E003", "O1")
        require(valid_digest(self.input_digest), "S2HZ-E003", "O1")
        _check_schema_digest(
            self.schema,
            self.owner_prestate_digest,
            self.payload_without_digest(),
            "owner",
            "owner_prestate_digest",
            "O1",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "owner_id": self.owner_id,
            "invocation_id": self.invocation_id,
            "function_role": self.function_role,
            "input_digest": self.input_digest,
            "state": self.state,
        }

    @classmethod
    def build(cls, owner_id: str, signal_input: TwoAreaConflictSignalInput) -> "TwoAreaConflictOwnerPrestate":
        payload = {
            "schema": S2IC_SCHEMA,
            "owner_id": owner_id,
            "invocation_id": signal_input.invocation_id,
            "function_role": signal_input.function_role,
            "input_digest": signal_input.input_digest,
            "state": "READY",
        }
        return cls(
            owner_id,
            signal_input.invocation_id,
            signal_input.function_role,
            signal_input.input_digest,
            "READY",
            digest(payload),
        )


@dataclass(frozen=True, slots=True)
class TwoAreaConflictOwnerPoststate:
    owner_id: str
    invocation_id: str
    function_role: str
    input_digest: str
    prior_owner_digest: str
    terminal_binding_digest: str
    state: str
    owner_poststate_digest: str
    schema: str = S2IC_SCHEMA

    def __post_init__(self) -> None:
        require(valid_identifier(self.owner_id) and valid_identifier(self.invocation_id), "S2HZ-E003", "O6")
        require(self.function_role in FUNCTION_ROLES and self.state in ("CONSUMED", "FAILED"), "S2HZ-E003", "O6")
        require(
            all(valid_digest(value) for value in (self.input_digest, self.prior_owner_digest, self.terminal_binding_digest)),
            "S2HZ-E003",
            "O6",
        )
        _check_schema_digest(
            self.schema,
            self.owner_poststate_digest,
            self.payload_without_digest(),
            "owner",
            "owner_poststate_digest",
            "O6",
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
    def build(
        cls,
        prestate: TwoAreaConflictOwnerPrestate,
        state: str,
        terminal_binding_digest: str,
    ) -> "TwoAreaConflictOwnerPoststate":
        payload = {
            "schema": S2IC_SCHEMA,
            "owner_id": prestate.owner_id,
            "invocation_id": prestate.invocation_id,
            "function_role": prestate.function_role,
            "input_digest": prestate.input_digest,
            "prior_owner_digest": prestate.owner_prestate_digest,
            "terminal_binding_digest": terminal_binding_digest,
            "state": state,
        }
        return cls(
            prestate.owner_id,
            prestate.invocation_id,
            prestate.function_role,
            prestate.input_digest,
            prestate.owner_prestate_digest,
            terminal_binding_digest,
            state,
            digest(payload),
        )


class TwoAreaConflictSignalOwner:
    """One private atomic owner with immutable pre/post snapshots."""

    __slots__ = ("_prestate", "_poststate")

    def __init__(self, prestate: TwoAreaConflictOwnerPrestate) -> None:
        require(type(prestate) is TwoAreaConflictOwnerPrestate, "S2HZ-E003", "O1")
        prestate.__post_init__()
        self._prestate = prestate
        self._poststate: TwoAreaConflictOwnerPoststate | None = None

    @property
    def prestate(self) -> TwoAreaConflictOwnerPrestate:
        return self._prestate

    @property
    def poststate(self) -> TwoAreaConflictOwnerPoststate | None:
        return self._poststate

    @property
    def state(self) -> str:
        return "READY" if self._poststate is None else self._poststate.state

    def commit(self, poststate: TwoAreaConflictOwnerPoststate) -> None:
        require(self._poststate is None, "S2HZ-E008", "O6")
        require(type(poststate) is TwoAreaConflictOwnerPoststate, "S2HZ-E003", "O6")
        poststate.__post_init__()
        require(
            poststate.owner_id == self._prestate.owner_id
            and poststate.invocation_id == self._prestate.invocation_id
            and poststate.function_role == self._prestate.function_role
            and poststate.input_digest == self._prestate.input_digest
            and poststate.prior_owner_digest == self._prestate.owner_prestate_digest,
            "S2HZ-E003",
            "O6",
        )
        self._poststate = poststate


@dataclass(frozen=True, slots=True)
class AreaApplicabilityFinding:
    area: str
    status: str
    input_digest: str
    probe_digest: str
    bundle_digest: str
    area_finding_digest: str
    role_finding_digest: str
    candidate_digest: str | None
    component_digest: str | None
    component_source_digest: str | None
    visible_mismatch_positions: tuple[int, ...]
    masked_positions: tuple[int, ...]
    masked_values: tuple[float, ...]
    masked_values_digest: str | None
    finding_digest: str
    schema: str = S2IC_SCHEMA

    def __post_init__(self) -> None:
        require(self.area in AREAS and self.status in APPLICABILITY_STATUSES, "S2HZ-E005", "O2" if self.area == "A_RECENT" else "O3")
        operation = "O2" if self.area == "A_RECENT" else "O3"
        require(
            all(valid_digest(value) for value in (self.input_digest, self.probe_digest, self.bundle_digest, self.area_finding_digest, self.role_finding_digest)),
            "S2HZ-E002",
            operation,
        )
        optional_digests = (self.candidate_digest, self.component_digest, self.component_source_digest)
        require(all(value is None or valid_digest(value) for value in optional_digests), "S2HZ-E002", operation)
        require(_valid_positions(self.visible_mismatch_positions, probe_contract.VISIBLE_POSITIONS), "S2HZ-E005", operation)
        require(_valid_positions(self.masked_positions, probe_contract.MASKED_POSITIONS), "S2HZ-E005", operation)

        if self.status == "APPLICABLE":
            require(all(value is not None for value in optional_digests), "S2HZ-E005", operation)
            require(self.visible_mismatch_positions == (), "S2HZ-E005", operation)
            require(self.masked_positions == probe_contract.MASKED_POSITIONS, "S2HZ-E004", operation)
            require(_valid_float_values(self.masked_values, 9), "S2HZ-E005", operation)
            require(
                valid_digest(self.masked_values_digest)
                and self.masked_values_digest == digest(list(self.masked_values)),
                "S2HZ-E002",
                operation,
            )
        elif self.status == "VISIBLE_CONFLICT":
            require(all(value is not None for value in optional_digests), "S2HZ-E005", operation)
            require(1 <= len(self.visible_mismatch_positions) <= 9, "S2HZ-E005", operation)
            require(self.masked_positions == () and self.masked_values == () and self.masked_values_digest is None, "S2HZ-E005", operation)
        else:
            require(all(value is None for value in optional_digests), "S2HZ-E005", operation)
            require(self.visible_mismatch_positions == () and self.masked_positions == () and self.masked_values == () and self.masked_values_digest is None, "S2HZ-E005", operation)

        _check_schema_digest(
            self.schema,
            self.finding_digest,
            self.payload_without_digest(),
            "applicability",
            "finding_digest",
            operation,
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "area": self.area,
            "status": self.status,
            "input_digest": self.input_digest,
            "probe_digest": self.probe_digest,
            "bundle_digest": self.bundle_digest,
            "area_finding_digest": self.area_finding_digest,
            "role_finding_digest": self.role_finding_digest,
            "candidate_digest": self.candidate_digest,
            "component_digest": self.component_digest,
            "component_source_digest": self.component_source_digest,
            "visible_mismatch_positions": list(self.visible_mismatch_positions),
            "masked_positions": list(self.masked_positions),
            "masked_values": list(self.masked_values),
            "masked_values_digest": self.masked_values_digest,
        }

    @classmethod
    def build(
        cls,
        *,
        area: str,
        status: str,
        signal_input: TwoAreaConflictSignalInput,
        area_finding_digest: str,
        role_finding_digest: str,
        candidate_digest: str | None,
        component_digest: str | None,
        component_source_digest: str | None,
        visible_mismatch_positions: tuple[int, ...],
        masked_values: tuple[float, ...],
    ) -> "AreaApplicabilityFinding":
        masked_positions = probe_contract.MASKED_POSITIONS if status == "APPLICABLE" else ()
        values_digest = digest(list(masked_values)) if status == "APPLICABLE" else None
        payload = {
            "schema": S2IC_SCHEMA,
            "area": area,
            "status": status,
            "input_digest": signal_input.input_digest,
            "probe_digest": signal_input.probe_digest,
            "bundle_digest": signal_input.bundle_digest,
            "area_finding_digest": area_finding_digest,
            "role_finding_digest": role_finding_digest,
            "candidate_digest": candidate_digest,
            "component_digest": component_digest,
            "component_source_digest": component_source_digest,
            "visible_mismatch_positions": list(visible_mismatch_positions),
            "masked_positions": list(masked_positions),
            "masked_values": list(masked_values),
            "masked_values_digest": values_digest,
        }
        return cls(
            area,
            status,
            signal_input.input_digest,
            signal_input.probe_digest,
            signal_input.bundle_digest,
            area_finding_digest,
            role_finding_digest,
            candidate_digest,
            component_digest,
            component_source_digest,
            visible_mismatch_positions,
            masked_positions,
            masked_values,
            values_digest,
            digest(payload),
        )


@dataclass(frozen=True, slots=True)
class MaskedSupplementComparison:
    input_digest: str
    a_applicability_finding_digest: str
    b_applicability_finding_digest: str
    comparison_status: str
    a_masked_values_digest: str | None
    b_masked_values_digest: str | None
    differing_masked_positions: tuple[int, ...]
    comparison_digest: str
    schema: str = S2IC_SCHEMA

    def __post_init__(self) -> None:
        require(self.comparison_status in COMPARISON_STATUSES, "S2HZ-E001", "O4")
        require(all(valid_digest(value) for value in (self.input_digest, self.a_applicability_finding_digest, self.b_applicability_finding_digest)), "S2HZ-E002", "O4")
        require(_valid_positions(self.differing_masked_positions, probe_contract.MASKED_POSITIONS), "S2HZ-E005", "O4")
        if self.comparison_status == "NOT_PERFORMED":
            require(self.a_masked_values_digest is None and self.b_masked_values_digest is None and self.differing_masked_positions == (), "S2HZ-E005", "O4")
        else:
            require(valid_digest(self.a_masked_values_digest) and valid_digest(self.b_masked_values_digest), "S2HZ-E002", "O4")
            require((self.comparison_status == "EQUAL") == (self.differing_masked_positions == ()), "S2HZ-E005", "O4")
        _check_schema_digest(
            self.schema,
            self.comparison_digest,
            self.payload_without_digest(),
            "comparison",
            "comparison_digest",
            "O4",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "input_digest": self.input_digest,
            "a_applicability_finding_digest": self.a_applicability_finding_digest,
            "b_applicability_finding_digest": self.b_applicability_finding_digest,
            "comparison_status": self.comparison_status,
            "a_masked_values_digest": self.a_masked_values_digest,
            "b_masked_values_digest": self.b_masked_values_digest,
            "differing_masked_positions": list(self.differing_masked_positions),
        }

    @classmethod
    def build(
        cls,
        signal_input: TwoAreaConflictSignalInput,
        a_finding: AreaApplicabilityFinding,
        b_finding: AreaApplicabilityFinding,
        comparison_status: str,
        differing_positions: tuple[int, ...],
    ) -> "MaskedSupplementComparison":
        both = comparison_status != "NOT_PERFORMED"
        payload = {
            "schema": S2IC_SCHEMA,
            "input_digest": signal_input.input_digest,
            "a_applicability_finding_digest": a_finding.finding_digest,
            "b_applicability_finding_digest": b_finding.finding_digest,
            "comparison_status": comparison_status,
            "a_masked_values_digest": a_finding.masked_values_digest if both else None,
            "b_masked_values_digest": b_finding.masked_values_digest if both else None,
            "differing_masked_positions": list(differing_positions),
        }
        return cls(
            signal_input.input_digest,
            a_finding.finding_digest,
            b_finding.finding_digest,
            comparison_status,
            a_finding.masked_values_digest if both else None,
            b_finding.masked_values_digest if both else None,
            differing_positions,
            digest(payload),
        )


@dataclass(frozen=True, slots=True)
class TwoAreaConflictSignalLedger:
    input_validation_count: int
    probe_position_validation_count: int
    bundle_validation_count: int
    area_lookup_count: int
    area_finding_validation_count: int
    candidate_reference_count: int
    component_reference_count: int
    visible_compare_count: int
    masked_projection_count: int
    masked_value_reference_count: int
    cross_area_compare_count: int
    signal_binding_digest_validation_count: int
    new_digest_operation_count: int
    logical_operation_count: int
    published_success_object_count: int
    storage_or_learning_call_count: int
    ledger_digest: str
    schema: str = S2IC_SCHEMA

    def __post_init__(self) -> None:
        values = tuple(
            getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in ("ledger_digest", "schema")
        )
        require(all(type(value) is int and value >= 0 for value in values), "S2HZ-E007", "O5")
        p_count = self.candidate_reference_count
        k_count = self.masked_projection_count
        require(
            0 <= k_count <= p_count <= 2
            and self.input_validation_count == 1
            and self.probe_position_validation_count == 18
            and self.bundle_validation_count == 1
            and self.area_lookup_count == 2
            and self.area_finding_validation_count == 2
            and self.component_reference_count == p_count
            and self.visible_compare_count == 9 * p_count
            and self.masked_value_reference_count == 9 * k_count
            and self.cross_area_compare_count == (9 if k_count == 2 else 0)
            and self.signal_binding_digest_validation_count == 15 + 3 * p_count
            and self.new_digest_operation_count == 7 + k_count
            and self.logical_operation_count == 6
            and self.published_success_object_count == 3
            and self.storage_or_learning_call_count == 0,
            "S2HZ-E007",
            "O5",
        )
        _check_schema_digest(
            self.schema,
            self.ledger_digest,
            self.payload_without_digest(),
            "ledger",
            "ledger_digest",
            "O5",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "input_validation_count": self.input_validation_count,
            "probe_position_validation_count": self.probe_position_validation_count,
            "bundle_validation_count": self.bundle_validation_count,
            "area_lookup_count": self.area_lookup_count,
            "area_finding_validation_count": self.area_finding_validation_count,
            "candidate_reference_count": self.candidate_reference_count,
            "component_reference_count": self.component_reference_count,
            "visible_compare_count": self.visible_compare_count,
            "masked_projection_count": self.masked_projection_count,
            "masked_value_reference_count": self.masked_value_reference_count,
            "cross_area_compare_count": self.cross_area_compare_count,
            "signal_binding_digest_validation_count": self.signal_binding_digest_validation_count,
            "new_digest_operation_count": self.new_digest_operation_count,
            "logical_operation_count": self.logical_operation_count,
            "published_success_object_count": self.published_success_object_count,
            "storage_or_learning_call_count": self.storage_or_learning_call_count,
        }

    @classmethod
    def build(cls, present_count: int, applicable_count: int) -> "TwoAreaConflictSignalLedger":
        values = (
            1,
            18,
            1,
            2,
            2,
            present_count,
            present_count,
            9 * present_count,
            applicable_count,
            9 * applicable_count,
            9 if applicable_count == 2 else 0,
            15 + 3 * present_count,
            7 + applicable_count,
            6,
            3,
            0,
        )
        names = tuple(
            name for name in cls.__dataclass_fields__ if name not in ("ledger_digest", "schema")
        )
        payload = {"schema": S2IC_SCHEMA, **dict(zip(names, values, strict=True))}
        return cls(*values, digest(payload))


@dataclass(frozen=True, slots=True)
class TwoAreaConflictSignalResult:
    function_role: str
    status: str
    input_digest: str
    probe_digest: str
    bundle_digest: str
    a_applicability_finding_digest: str
    b_applicability_finding_digest: str
    comparison_digest: str
    present_areas: tuple[str, ...]
    applicable_areas: tuple[str, ...]
    differing_masked_positions: tuple[int, ...]
    selected_area: None
    recommended_area: None
    automatic_selection: None
    prestate_digest: str
    poststate_digest: str
    resource_ledger_digest: str
    result_digest: str
    schema: str = S2IC_SCHEMA

    def __post_init__(self) -> None:
        require(self.function_role in FUNCTION_ROLES and self.status in RESULT_STATUSES, "S2HZ-E001", "O5")
        require(all(valid_digest(value) for value in (self.input_digest, self.probe_digest, self.bundle_digest, self.a_applicability_finding_digest, self.b_applicability_finding_digest, self.comparison_digest, self.prestate_digest, self.poststate_digest, self.resource_ledger_digest)), "S2HZ-E002", "O5")
        require(self.prestate_digest == self.poststate_digest, "S2HZ-E006", "O5")
        require(type(self.present_areas) is tuple and tuple(area for area in AREAS if area in self.present_areas) == self.present_areas, "S2HZ-E005", "O5")
        require(type(self.applicable_areas) is tuple and tuple(area for area in AREAS if area in self.applicable_areas) == self.applicable_areas, "S2HZ-E005", "O5")
        require(set(self.applicable_areas).issubset(self.present_areas), "S2HZ-E005", "O5")
        require(_valid_positions(self.differing_masked_positions, probe_contract.MASKED_POSITIONS), "S2HZ-E005", "O5")
        require(self.selected_area is None and self.recommended_area is None and self.automatic_selection is None, "S2HZ-E005", "O5")
        _check_schema_digest(
            self.schema,
            self.result_digest,
            self.payload_without_digest(),
            "result",
            "result_digest",
            "O5",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "function_role": self.function_role,
            "status": self.status,
            "input_digest": self.input_digest,
            "probe_digest": self.probe_digest,
            "bundle_digest": self.bundle_digest,
            "a_applicability_finding_digest": self.a_applicability_finding_digest,
            "b_applicability_finding_digest": self.b_applicability_finding_digest,
            "comparison_digest": self.comparison_digest,
            "present_areas": list(self.present_areas),
            "applicable_areas": list(self.applicable_areas),
            "differing_masked_positions": list(self.differing_masked_positions),
            "selected_area": self.selected_area,
            "recommended_area": self.recommended_area,
            "automatic_selection": self.automatic_selection,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "resource_ledger_digest": self.resource_ledger_digest,
        }


@dataclass(frozen=True, slots=True)
class TwoAreaConflictSignalReceipt:
    invocation_id: str
    function_role: str
    owner_prestate_digest: str
    input_digest: str
    a_applicability_finding_digest: str
    b_applicability_finding_digest: str
    comparison_digest: str
    resource_ledger_digest: str
    result_digest: str
    owner_poststate_digest: str
    receipt_digest: str
    schema: str = S2IC_SCHEMA

    def __post_init__(self) -> None:
        require(valid_identifier(self.invocation_id) and self.function_role in FUNCTION_ROLES, "S2HZ-E001", "O6")
        require(_valid_digest_tuple((self.owner_prestate_digest, self.input_digest, self.a_applicability_finding_digest, self.b_applicability_finding_digest, self.comparison_digest, self.resource_ledger_digest, self.result_digest, self.owner_poststate_digest)), "S2HZ-E002", "O6")
        _check_schema_digest(
            self.schema,
            self.receipt_digest,
            self.payload_without_digest(),
            "receipt",
            "receipt_digest",
            "O6",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "invocation_id": self.invocation_id,
            "function_role": self.function_role,
            "owner_prestate_digest": self.owner_prestate_digest,
            "input_digest": self.input_digest,
            "a_applicability_finding_digest": self.a_applicability_finding_digest,
            "b_applicability_finding_digest": self.b_applicability_finding_digest,
            "comparison_digest": self.comparison_digest,
            "resource_ledger_digest": self.resource_ledger_digest,
            "result_digest": self.result_digest,
            "owner_poststate_digest": self.owner_poststate_digest,
        }


@dataclass(frozen=True, slots=True)
class TwoAreaConflictErrorCause:
    invocation_id: str
    function_role: str
    owner_prestate_digest: str
    input_digest: str
    failed_operation: str
    error_code: str
    message_id: str
    error_cause_digest: str
    schema: str = S2IC_SCHEMA

    def __post_init__(self) -> None:
        require(valid_identifier(self.invocation_id) and self.function_role in FUNCTION_ROLES, "S2HZ-E001", "O6")
        require(valid_digest(self.owner_prestate_digest) and valid_digest(self.input_digest), "S2HZ-E002", "O6")
        require(self.failed_operation in OPERATIONS and ERROR_REGISTRY.get(self.error_code) == self.message_id, "S2HZ-E001", "O6")
        _check_schema_digest(
            self.schema,
            self.error_cause_digest,
            self.payload_without_digest(),
            "error_cause",
            "error_cause_digest",
            "O6",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "invocation_id": self.invocation_id,
            "function_role": self.function_role,
            "owner_prestate_digest": self.owner_prestate_digest,
            "input_digest": self.input_digest,
            "failed_operation": self.failed_operation,
            "error_code": self.error_code,
            "message_id": self.message_id,
        }


@dataclass(frozen=True, slots=True)
class TwoAreaConflictErrorReceipt:
    invocation_id: str
    function_role: str
    owner_prestate_digest: str
    input_digest: str
    failed_operation: str
    error_code: str
    error_cause_digest: str
    owner_poststate_digest: str
    error_receipt_digest: str
    schema: str = S2IC_SCHEMA

    def __post_init__(self) -> None:
        require(valid_identifier(self.invocation_id) and self.function_role in FUNCTION_ROLES, "S2HZ-E001", "O6")
        require(self.failed_operation in OPERATIONS and self.error_code in ERROR_REGISTRY, "S2HZ-E001", "O6")
        require(_valid_digest_tuple((self.owner_prestate_digest, self.input_digest, self.error_cause_digest, self.owner_poststate_digest)), "S2HZ-E002", "O6")
        _check_schema_digest(
            self.schema,
            self.error_receipt_digest,
            self.payload_without_digest(),
            "error_receipt",
            "error_receipt_digest",
            "O6",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "invocation_id": self.invocation_id,
            "function_role": self.function_role,
            "owner_prestate_digest": self.owner_prestate_digest,
            "input_digest": self.input_digest,
            "failed_operation": self.failed_operation,
            "error_code": self.error_code,
            "error_cause_digest": self.error_cause_digest,
            "owner_poststate_digest": self.owner_poststate_digest,
        }


@dataclass(frozen=True, slots=True)
class TwoAreaConflictSignalCommit:
    result: TwoAreaConflictSignalResult
    receipt: TwoAreaConflictSignalReceipt
    owner_poststate: TwoAreaConflictOwnerPoststate


class S2ICSignalFailure(RuntimeError):
    """Atomic fail-closed publication containing no regular result."""

    def __init__(
        self,
        cause: TwoAreaConflictErrorCause,
        receipt: TwoAreaConflictErrorReceipt,
        owner_poststate: TwoAreaConflictOwnerPoststate,
    ) -> None:
        super().__init__(f"{cause.error_code}: {cause.message_id}")
        self.code = cause.error_code
        self.cause = cause
        self.receipt = receipt
        self.owner_poststate = owner_poststate


def validate_sources(
    signal_input: TwoAreaConflictSignalInput,
    owner: TwoAreaConflictSignalOwner,
    probe: probe_contract.MaskedVisualProbe,
    bundle: two_area.TwoAreaContextBundle,
    expected_role: str,
) -> tuple[str, str, str]:
    require(type(signal_input) is TwoAreaConflictSignalInput, "S2HZ-E001", "O1")
    require(type(owner) is TwoAreaConflictSignalOwner, "S2HZ-E003", "O1")
    require(type(probe) is probe_contract.MaskedVisualProbe, "S2HZ-E004", "O1")
    require(type(bundle) is two_area.TwoAreaContextBundle, "S2HZ-E005", "O1")
    require(expected_role in FUNCTION_ROLES and signal_input.function_role == expected_role, "S2HZ-E001", "O1")
    signal_input.__post_init__()
    try:
        probe.__post_init__()
    except probe_contract.S2GKConsumerError as error:
        source_code = error.code
        if "DIGEST" in source_code or "BINDING" in source_code:
            code = "S2HZ-E002"
        elif "CAPACITY" in source_code:
            code = "S2HZ-E007"
        elif "READ_ONLY" in source_code:
            code = "S2HZ-E006"
        elif any(token in source_code for token in ("PROBE", "MASK", "DIMENSION")):
            code = "S2HZ-E004"
        else:
            code = "S2HZ-E001"
        fail(code, "O1")
    require(probe.visible_positions == probe_contract.VISIBLE_POSITIONS and probe.masked_positions == probe_contract.MASKED_POSITIONS, "S2HZ-E004", "O1")
    require(mask_digest_for(probe) == signal_input.mask_digest, "S2HZ-E004", "O1")

    try:
        area_a, area_b = bundle.area_findings
        for finding in (area_a.recent_content, area_a.fast_internal, area_b.stable_content):
            if finding.candidate is not None:
                for component in finding.candidate.components:
                    component.__post_init__()
                finding.candidate.__post_init__()
            finding.__post_init__()
        for reference in area_a.short_sequence.references:
            reference.__post_init__()
        area_a.short_sequence.__post_init__()
        area_a.__post_init__()
        area_b.__post_init__()
        bundle.resource_ledger.__post_init__()
        bundle.__post_init__()
    except (context.S2GBProjectionError, two_area.S2GIProjectionError) as error:
        source_code = error.code
        if "DIGEST" in source_code or "BINDING" in source_code:
            code = "S2HZ-E002"
        elif "CAPACITY" in source_code:
            code = "S2HZ-E007"
        elif "READ_ONLY" in source_code:
            code = "S2HZ-E006"
        elif "ROLE" in source_code or "BUNDLE" in source_code or "EVIDENCE" in source_code:
            code = "S2HZ-E005"
        else:
            code = "S2HZ-E001"
        fail(code, "O1")

    require(
        signal_input.probe_digest == probe.probe_digest
        and signal_input.probe_source_digest == probe.source_digest
        and signal_input.bundle_digest == bundle.bundle_digest
        and signal_input.bundle_source_digest == bundle.source_digest
        and signal_input.config_digest == bundle.config_digest
        and signal_input.composite_state_digest == bundle.composite_state_digest
        and bundle.probe_digest == probe.probe_digest
        and signal_input.bundle_prestate_digest == bundle.prestate_digest
        and signal_input.bundle_poststate_digest == bundle.poststate_digest
        and signal_input.a_area_finding_digest == area_a.finding_digest
        and signal_input.b_area_finding_digest == area_b.finding_digest,
        "S2HZ-E002",
        "O1",
    )
    require(bundle.prestate_digest == bundle.poststate_digest == bundle.composite_state_digest, "S2HZ-E006", "O1")
    prestate = owner.prestate
    prestate.__post_init__()
    require(
        owner.state == "READY"
        and prestate.invocation_id == signal_input.invocation_id
        and prestate.function_role == signal_input.function_role
        and prestate.input_digest == signal_input.input_digest,
        "S2HZ-E003",
        "O1",
    )
    return bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest


def build_result(
    signal_input: TwoAreaConflictSignalInput,
    a_finding: AreaApplicabilityFinding,
    b_finding: AreaApplicabilityFinding,
    comparison: MaskedSupplementComparison,
    ledger: TwoAreaConflictSignalLedger,
    status: str,
) -> TwoAreaConflictSignalResult:
    present = tuple(item.area for item in (a_finding, b_finding) if item.status != "ABSENT_VALID")
    applicable = tuple(item.area for item in (a_finding, b_finding) if item.status == "APPLICABLE")
    payload = {
        "schema": S2IC_SCHEMA,
        "function_role": signal_input.function_role,
        "status": status,
        "input_digest": signal_input.input_digest,
        "probe_digest": signal_input.probe_digest,
        "bundle_digest": signal_input.bundle_digest,
        "a_applicability_finding_digest": a_finding.finding_digest,
        "b_applicability_finding_digest": b_finding.finding_digest,
        "comparison_digest": comparison.comparison_digest,
        "present_areas": list(present),
        "applicable_areas": list(applicable),
        "differing_masked_positions": list(comparison.differing_masked_positions),
        "selected_area": None,
        "recommended_area": None,
        "automatic_selection": None,
        "prestate_digest": signal_input.bundle_prestate_digest,
        "poststate_digest": signal_input.bundle_poststate_digest,
        "resource_ledger_digest": ledger.ledger_digest,
    }
    return TwoAreaConflictSignalResult(
        signal_input.function_role,
        status,
        signal_input.input_digest,
        signal_input.probe_digest,
        signal_input.bundle_digest,
        a_finding.finding_digest,
        b_finding.finding_digest,
        comparison.comparison_digest,
        present,
        applicable,
        comparison.differing_masked_positions,
        None,
        None,
        None,
        signal_input.bundle_prestate_digest,
        signal_input.bundle_poststate_digest,
        ledger.ledger_digest,
        digest(payload),
    )


def publish_success(
    owner: TwoAreaConflictSignalOwner,
    signal_input: TwoAreaConflictSignalInput,
    a_finding: AreaApplicabilityFinding,
    b_finding: AreaApplicabilityFinding,
    comparison: MaskedSupplementComparison,
    ledger: TwoAreaConflictSignalLedger,
    result: TwoAreaConflictSignalResult,
) -> TwoAreaConflictSignalCommit:
    require(owner.state == "READY", "S2HZ-E008", "O6")
    poststate = TwoAreaConflictOwnerPoststate.build(owner.prestate, "CONSUMED", result.result_digest)
    payload = {
        "schema": S2IC_SCHEMA,
        "invocation_id": signal_input.invocation_id,
        "function_role": signal_input.function_role,
        "owner_prestate_digest": owner.prestate.owner_prestate_digest,
        "input_digest": signal_input.input_digest,
        "a_applicability_finding_digest": a_finding.finding_digest,
        "b_applicability_finding_digest": b_finding.finding_digest,
        "comparison_digest": comparison.comparison_digest,
        "resource_ledger_digest": ledger.ledger_digest,
        "result_digest": result.result_digest,
        "owner_poststate_digest": poststate.owner_poststate_digest,
    }
    receipt = TwoAreaConflictSignalReceipt(
        signal_input.invocation_id,
        signal_input.function_role,
        owner.prestate.owner_prestate_digest,
        signal_input.input_digest,
        a_finding.finding_digest,
        b_finding.finding_digest,
        comparison.comparison_digest,
        ledger.ledger_digest,
        result.result_digest,
        poststate.owner_poststate_digest,
        digest(payload),
    )
    owner.commit(poststate)
    return TwoAreaConflictSignalCommit(result, receipt, poststate)


def publish_failure(
    owner: TwoAreaConflictSignalOwner,
    signal_input: TwoAreaConflictSignalInput,
    error: S2ICContractError,
) -> NoReturn:
    require(type(owner) is TwoAreaConflictSignalOwner and owner.state == "READY", "S2HZ-E008", "O6")
    prestate = owner.prestate
    payload = {
        "schema": S2IC_SCHEMA,
        "invocation_id": signal_input.invocation_id,
        "function_role": signal_input.function_role,
        "owner_prestate_digest": prestate.owner_prestate_digest,
        "input_digest": signal_input.input_digest,
        "failed_operation": error.operation,
        "error_code": error.code,
        "message_id": error.message_id,
    }
    cause = TwoAreaConflictErrorCause(
        signal_input.invocation_id,
        signal_input.function_role,
        prestate.owner_prestate_digest,
        signal_input.input_digest,
        error.operation,
        error.code,
        error.message_id,
        digest(payload),
    )
    poststate = TwoAreaConflictOwnerPoststate.build(prestate, "FAILED", cause.error_cause_digest)
    receipt_payload = {
        "schema": S2IC_SCHEMA,
        "invocation_id": signal_input.invocation_id,
        "function_role": signal_input.function_role,
        "owner_prestate_digest": prestate.owner_prestate_digest,
        "input_digest": signal_input.input_digest,
        "failed_operation": error.operation,
        "error_code": error.code,
        "error_cause_digest": cause.error_cause_digest,
        "owner_poststate_digest": poststate.owner_poststate_digest,
    }
    receipt = TwoAreaConflictErrorReceipt(
        signal_input.invocation_id,
        signal_input.function_role,
        prestate.owner_prestate_digest,
        signal_input.input_digest,
        error.operation,
        error.code,
        cause.error_cause_digest,
        poststate.owner_poststate_digest,
        digest(receipt_payload),
    )
    owner.commit(poststate)
    raise S2ICSignalFailure(cause, receipt, poststate)
