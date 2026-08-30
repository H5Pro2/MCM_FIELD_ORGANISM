"""Private, pure S2-GB projection of validated read-only memory findings."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from tools import _retention_capacity_read_only as read_only
from tools import _s2fs_b4_tspm1_private_coordinator as coordinator


S2GB_SCHEMA = "s2gb.perceptual-context-bundle.v1"
S2GA_CONTRACT_DIGEST = (
    "9a72752f241d6ff74517b119b535cb60ba15c830ec231af1378604d06ed25b72"
)
ROLES = ("B4_RECENT", "TSPM_FAST", "TSPM_SLOW")
ROLE_STATUSES = ("AVAILABLE_COMPLETE", "AVAILABLE_PARTIAL", "ABSENT_VALID")
SEQUENCE_STATUSES = ("AVAILABLE", "NOT_REQUESTED", "ABSENT_VALID")
MAX_CANDIDATES = 3
MAX_COMPONENTS = 4
MAX_VALUES = 78
MAX_SEQUENCE_REFERENCES = 9

S2GB_INVALID_TYPE_OR_SCHEMA = "S2GB_INVALID_TYPE_OR_SCHEMA"
S2GB_SOURCE_BINDING_INVALID = "S2GB_SOURCE_BINDING_INVALID"
S2GB_PROBE_MISMATCH = "S2GB_PROBE_MISMATCH"
S2GB_STATE_DIGEST_MISMATCH = "S2GB_STATE_DIGEST_MISMATCH"
S2GB_EVIDENCE_INVALID = "S2GB_EVIDENCE_INVALID"
S2GB_DIMENSION_INVALID = "S2GB_DIMENSION_INVALID"
S2GB_DUPLICATE_SOURCE = "S2GB_DUPLICATE_SOURCE"
S2GB_CAPACITY_EXCEEDED = "S2GB_CAPACITY_EXCEEDED"
S2GB_DIGEST_MISMATCH = "S2GB_DIGEST_MISMATCH"
S2GB_READ_ONLY_VIOLATION = "S2GB_READ_ONLY_VIOLATION"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,126}[a-z0-9]$")


class S2GBProjectionError(RuntimeError):
    """One terminal, fail-closed S2-GB projection error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise S2GBProjectionError(code, message)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _identifier(value: object, role: str) -> str:
    _require(
        isinstance(value, str) and _IDENTIFIER.fullmatch(value) is not None,
        S2GB_EVIDENCE_INVALID,
        f"{role} is not a canonical technical identifier",
    )
    return value


def _number(value: object, role: str) -> float:
    _require(
        type(value) in (int, float) and math.isfinite(float(value)),
        S2GB_EVIDENCE_INVALID,
        f"{role} is not one finite numeric value",
    )
    return float(value)


def _nonnegative_number(value: object, role: str) -> float:
    normalized = _number(value, role)
    _require(normalized >= 0.0, S2GB_EVIDENCE_INVALID, f"{role} is negative")
    return normalized


def _nonnegative_int(value: object, role: str) -> int:
    _require(
        type(value) is int and value >= 0,
        S2GB_EVIDENCE_INVALID,
        f"{role} is not an exact nonnegative integer",
    )
    return value


def _values(values: object, dimension: int, role: str) -> tuple[float, ...]:
    _require(
        type(values) is tuple and len(values) == dimension,
        S2GB_DIMENSION_INVALID,
        f"{role} must be one exact {dimension}-value tuple",
    )
    _require(
        all(type(value) in (int, float) for value in values),
        S2GB_DIMENSION_INVALID,
        f"{role} contains a nonnumeric or boolean value",
    )
    normalized = tuple(float(value) for value in values)
    _require(
        all(math.isfinite(value) and -1.0 <= value <= 1.0 for value in normalized),
        S2GB_DIMENSION_INVALID,
        f"{role} contains a nonfinite or out-of-range value",
    )
    return normalized


def _optional_distances(values: object, length: int, role: str) -> tuple[float, ...] | None:
    if values is None:
        return None
    _require(type(values) is tuple and len(values) == length, S2GB_EVIDENCE_INVALID, role)
    return tuple(_nonnegative_number(value, role) for value in values)


@dataclass(frozen=True, slots=True)
class PerceptualContextProjectionBinding:
    config_digest: str
    composite_state_digest: str
    probe_digest: str
    probe_values_digest: str
    auditory_source_digest: str
    visual_source_digest: str
    auditory_geometry_id: str
    visual_geometry_id: str
    field_clock_id: str
    window_start: int
    window_end: int
    source_digest: str
    binding_digest: str
    schema: str = S2GB_SCHEMA

    def __post_init__(self) -> None:
        for value in (
            self.config_digest,
            self.composite_state_digest,
            self.probe_digest,
            self.probe_values_digest,
            self.auditory_source_digest,
            self.visual_source_digest,
        ):
            _require(_valid_digest(value), S2GB_SOURCE_BINDING_INVALID, "source digest differs")
        _identifier(self.auditory_geometry_id, "auditory_geometry_id")
        _identifier(self.visual_geometry_id, "visual_geometry_id")
        _identifier(self.field_clock_id, "field_clock_id")
        _require(
            type(self.window_start) is int
            and type(self.window_end) is int
            and 0 <= self.window_start < self.window_end,
            S2GB_SOURCE_BINDING_INVALID,
            "time window is invalid",
        )
        _require(
            self.schema == S2GB_SCHEMA
            and self.source_digest == _digest(self.source_payload())
            and self.binding_digest == _digest(self.payload_without_digest()),
            S2GB_SOURCE_BINDING_INVALID,
            "source provenance or binding digest differs",
        )

    def source_payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "config_digest": self.config_digest,
            "composite_state_digest": self.composite_state_digest,
            "probe_digest": self.probe_digest,
            "probe_values_digest": self.probe_values_digest,
            "auditory_source_digest": self.auditory_source_digest,
            "visual_source_digest": self.visual_source_digest,
            "auditory_geometry_id": self.auditory_geometry_id,
            "visual_geometry_id": self.visual_geometry_id,
            "field_clock_id": self.field_clock_id,
            "window_start": self.window_start,
            "window_end": self.window_end,
        }

    def payload_without_digest(self) -> dict[str, object]:
        return {
            **self.source_payload(),
            "source_digest": self.source_digest,
            "contract_digest": S2GA_CONTRACT_DIGEST,
        }

    @classmethod
    def build(
        cls,
        *,
        config_digest: str,
        composite_state_digest: str,
        probe_digest: str,
        probe_values_digest: str,
        auditory_source_digest: str,
        visual_source_digest: str,
        auditory_geometry_id: str,
        visual_geometry_id: str,
        field_clock_id: str,
        window_start: int,
        window_end: int,
    ) -> "PerceptualContextProjectionBinding":
        source_payload = {
            "schema": S2GB_SCHEMA,
            "config_digest": config_digest,
            "composite_state_digest": composite_state_digest,
            "probe_digest": probe_digest,
            "probe_values_digest": probe_values_digest,
            "auditory_source_digest": auditory_source_digest,
            "visual_source_digest": visual_source_digest,
            "auditory_geometry_id": auditory_geometry_id,
            "visual_geometry_id": visual_geometry_id,
            "field_clock_id": field_clock_id,
            "window_start": window_start,
            "window_end": window_end,
        }
        source_digest = _digest(source_payload)
        payload = {
            **source_payload,
            "source_digest": source_digest,
            "contract_digest": S2GA_CONTRACT_DIGEST,
        }
        return cls(
            config_digest,
            composite_state_digest,
            probe_digest,
            probe_values_digest,
            auditory_source_digest,
            visual_source_digest,
            auditory_geometry_id,
            visual_geometry_id,
            field_clock_id,
            window_start,
            window_end,
            source_digest,
            _digest(payload),
        )


@dataclass(frozen=True, slots=True)
class B4SequenceReference:
    formation_index: int
    slot_id: str
    slot_digest: str
    values_digest: str
    reference_digest: str
    schema: str = S2GB_SCHEMA

    def __post_init__(self) -> None:
        _require(type(self.formation_index) is int and self.formation_index > 0, S2GB_EVIDENCE_INVALID, "sequence index differs")
        _identifier(self.slot_id, "sequence slot_id")
        _require(_valid_digest(self.slot_digest) and _valid_digest(self.values_digest), S2GB_DIGEST_MISMATCH, "sequence digest differs")
        _require(self.schema == S2GB_SCHEMA and self.reference_digest == _digest(self.payload_without_digest()), S2GB_DIGEST_MISMATCH, "sequence reference digest differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "formation_index": self.formation_index,
            "slot_id": self.slot_id,
            "slot_digest": self.slot_digest,
            "values_digest": self.values_digest,
        }

    @classmethod
    def build(cls, formation_index: int, slot_id: str, slot_digest: str, values_digest: str) -> "B4SequenceReference":
        payload = {
            "schema": S2GB_SCHEMA,
            "formation_index": formation_index,
            "slot_id": slot_id,
            "slot_digest": slot_digest,
            "values_digest": values_digest,
        }
        return cls(formation_index, slot_id, slot_digest, values_digest, _digest(payload))


@dataclass(frozen=True, slots=True)
class ValidatedB4ShortSequenceEvidence:
    status: str
    observed_b4_state_digest: str
    probe_digest: str
    references: tuple[B4SequenceReference, ...]
    evidence_digest: str
    schema: str = S2GB_SCHEMA

    def __post_init__(self) -> None:
        _require(self.status in SEQUENCE_STATUSES, S2GB_EVIDENCE_INVALID, "sequence status differs")
        _require(_valid_digest(self.observed_b4_state_digest) and _valid_digest(self.probe_digest), S2GB_DIGEST_MISMATCH, "sequence binding differs")
        _require(type(self.references) is tuple and all(type(item) is B4SequenceReference for item in self.references), S2GB_INVALID_TYPE_OR_SCHEMA, "sequence references differ")
        _require(len(self.references) <= MAX_SEQUENCE_REFERENCES, S2GB_CAPACITY_EXCEEDED, "too many sequence references")
        indexes = tuple(item.formation_index for item in self.references)
        _require(indexes == tuple(sorted(set(indexes))), S2GB_EVIDENCE_INVALID, "sequence order is ambiguous")
        _require((self.status == "AVAILABLE") == bool(self.references), S2GB_EVIDENCE_INVALID, "sequence status and references differ")
        _require(self.schema == S2GB_SCHEMA and self.evidence_digest == _digest(self.payload_without_digest()), S2GB_DIGEST_MISMATCH, "sequence evidence digest differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "status": self.status,
            "observed_b4_state_digest": self.observed_b4_state_digest,
            "probe_digest": self.probe_digest,
            "reference_digests": [item.reference_digest for item in self.references],
        }

    @classmethod
    def build(cls, status: str, observed_b4_state_digest: str, probe_digest: str, references: tuple[B4SequenceReference, ...] = ()) -> "ValidatedB4ShortSequenceEvidence":
        payload = {
            "schema": S2GB_SCHEMA,
            "status": status,
            "observed_b4_state_digest": observed_b4_state_digest,
            "probe_digest": probe_digest,
            "reference_digests": [item.reference_digest for item in references],
        }
        return cls(status, observed_b4_state_digest, probe_digest, references, _digest(payload))


@dataclass(frozen=True, slots=True)
class PerceptualContextComponent:
    component_role: str
    values: tuple[float, ...]
    source_id: str
    source_digest: str
    values_digest: str
    native_distances: tuple[float, ...] | None
    functional_distances: tuple[float, ...]
    support_count: int | None
    stable: bool | None
    last_selected_step: int | None
    formation_index: int | None
    component_digest: str
    schema: str = S2GB_SCHEMA

    def __post_init__(self) -> None:
        dimensions = {"AV_JOINT": 26, "AUDITORY": 8, "VISUAL": 18}
        _require(self.component_role in dimensions, S2GB_INVALID_TYPE_OR_SCHEMA, "component role differs")
        normalized = _values(self.values, dimensions[self.component_role], "component values")
        _identifier(self.source_id, "component source_id")
        _require(_valid_digest(self.source_digest) and self.values_digest == _digest(list(normalized)), S2GB_DIGEST_MISMATCH, "component source or values digest differs")
        distance_length = 2 if self.component_role == "AV_JOINT" else 1
        _optional_distances(self.native_distances, distance_length, "native distances differ")
        _require(type(self.functional_distances) is tuple and len(self.functional_distances) == distance_length, S2GB_EVIDENCE_INVALID, "functional distances differ")
        tuple(_nonnegative_number(value, "functional distance") for value in self.functional_distances)
        for value, role in ((self.support_count, "support_count"), (self.last_selected_step, "last_selected_step"), (self.formation_index, "formation_index")):
            if value is not None:
                _require(type(value) is int and value > 0, S2GB_EVIDENCE_INVALID, f"{role} differs")
        _require(self.stable is None or type(self.stable) is bool, S2GB_EVIDENCE_INVALID, "stable flag differs")
        _require(self.schema == S2GB_SCHEMA and self.component_digest == _digest(self.payload_without_digest()), S2GB_DIGEST_MISMATCH, "component digest differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "component_role": self.component_role,
            "values": list(self.values),
            "source_id": self.source_id,
            "source_digest": self.source_digest,
            "values_digest": self.values_digest,
            "native_distances": None if self.native_distances is None else list(self.native_distances),
            "functional_distances": list(self.functional_distances),
            "support_count": self.support_count,
            "stable": self.stable,
            "last_selected_step": self.last_selected_step,
            "formation_index": self.formation_index,
        }


@dataclass(frozen=True, slots=True)
class PerceptualContextCandidate:
    role: str
    components: tuple[PerceptualContextComponent, ...]
    cross_modal_relation: str
    candidate_digest: str
    schema: str = S2GB_SCHEMA

    def __post_init__(self) -> None:
        _require(self.role in ROLES and type(self.components) is tuple, S2GB_INVALID_TYPE_OR_SCHEMA, "candidate role differs")
        _require(all(type(item) is PerceptualContextComponent for item in self.components), S2GB_INVALID_TYPE_OR_SCHEMA, "candidate component differs")
        expected_count = 2 if self.role == "TSPM_SLOW" and len(self.components) == 2 else 1
        _require(len(self.components) == expected_count, S2GB_EVIDENCE_INVALID, "candidate component anatomy differs")
        if self.role == "TSPM_SLOW":
            _require(tuple(item.component_role for item in self.components) in (("AUDITORY",), ("VISUAL",), ("AUDITORY", "VISUAL")), S2GB_EVIDENCE_INVALID, "Slow modality anatomy differs")
            _require(self.cross_modal_relation == "CROSS_MODAL_RELATION_NOT_REPRESENTED", S2GB_EVIDENCE_INVALID, "Slow relation was invented")
        else:
            _require(tuple(item.component_role for item in self.components) == ("AV_JOINT",), S2GB_EVIDENCE_INVALID, "joint candidate anatomy differs")
            _require(self.cross_modal_relation == "JOINT_SOURCE_VALUES", S2GB_EVIDENCE_INVALID, "joint relation differs")
        _require(self.schema == S2GB_SCHEMA and self.candidate_digest == _digest(self.payload_without_digest()), S2GB_DIGEST_MISMATCH, "candidate digest differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "role": self.role,
            "component_digests": [item.component_digest for item in self.components],
            "cross_modal_relation": self.cross_modal_relation,
        }


@dataclass(frozen=True, slots=True)
class PerceptualContextRoleFinding:
    role: str
    status: str
    candidate: PerceptualContextCandidate | None
    absence_reason: str | None
    finding_digest: str
    schema: str = S2GB_SCHEMA

    def __post_init__(self) -> None:
        _require(self.role in ROLES and self.status in ROLE_STATUSES, S2GB_INVALID_TYPE_OR_SCHEMA, "role finding differs")
        if self.status == "ABSENT_VALID":
            _require(self.candidate is None and self.absence_reason in {"NO_FUNCTIONAL_MATCH", "NO_STABLE_SLOW_MATCH", "NO_OCCUPIED_SOURCE"}, S2GB_EVIDENCE_INVALID, "valid absence is not transparent")
        else:
            _require(type(self.candidate) is PerceptualContextCandidate and self.candidate.role == self.role and self.absence_reason is None, S2GB_EVIDENCE_INVALID, "available role lacks its candidate")
            _require((self.status == "AVAILABLE_PARTIAL") == (self.role == "TSPM_SLOW" and len(self.candidate.components) == 1), S2GB_EVIDENCE_INVALID, "partial status differs")
        _require(self.schema == S2GB_SCHEMA and self.finding_digest == _digest(self.payload_without_digest()), S2GB_DIGEST_MISMATCH, "role finding digest differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "role": self.role,
            "status": self.status,
            "candidate_digest": None if self.candidate is None else self.candidate.candidate_digest,
            "absence_reason": self.absence_reason,
        }


@dataclass(frozen=True, slots=True)
class B4ShortSequenceFinding:
    status: str
    references: tuple[B4SequenceReference, ...]
    observed_b4_state_digest: str
    source_evidence_digest: str
    finding_digest: str
    schema: str = S2GB_SCHEMA

    def __post_init__(self) -> None:
        _require(self.status in SEQUENCE_STATUSES and type(self.references) is tuple, S2GB_INVALID_TYPE_OR_SCHEMA, "sequence finding differs")
        _require(len(self.references) <= MAX_SEQUENCE_REFERENCES and all(type(item) is B4SequenceReference for item in self.references), S2GB_CAPACITY_EXCEEDED, "sequence finding exceeds capacity")
        _require(_valid_digest(self.observed_b4_state_digest) and _valid_digest(self.source_evidence_digest), S2GB_DIGEST_MISMATCH, "sequence source digest differs")
        _require(self.schema == S2GB_SCHEMA and self.finding_digest == _digest(self.payload_without_digest()), S2GB_DIGEST_MISMATCH, "sequence finding digest differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "status": self.status,
            "reference_digests": [item.reference_digest for item in self.references],
            "observed_b4_state_digest": self.observed_b4_state_digest,
            "source_evidence_digest": self.source_evidence_digest,
        }


@dataclass(frozen=True, slots=True)
class PerceptualContextResourceLedger:
    validated_evidence_records: int
    validated_digest_count: int
    role_projection_count: int
    candidate_count: int
    component_count: int
    value_count: int
    sequence_reference_count: int
    digest_operation_count: int
    ledger_digest: str
    schema: str = S2GB_SCHEMA

    def __post_init__(self) -> None:
        numeric = (
            self.validated_evidence_records,
            self.validated_digest_count,
            self.role_projection_count,
            self.candidate_count,
            self.component_count,
            self.value_count,
            self.sequence_reference_count,
            self.digest_operation_count,
        )
        _require(all(type(value) is int and value >= 0 for value in numeric), S2GB_EVIDENCE_INVALID, "ledger count differs")
        _require(self.role_projection_count == 3 and self.candidate_count <= MAX_CANDIDATES and self.component_count <= MAX_COMPONENTS and self.value_count <= MAX_VALUES and self.sequence_reference_count <= MAX_SEQUENCE_REFERENCES, S2GB_CAPACITY_EXCEEDED, "bundle ledger exceeds a bound")
        _require(self.schema == S2GB_SCHEMA and self.ledger_digest == _digest(self.payload_without_digest()), S2GB_DIGEST_MISMATCH, "ledger digest differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "validated_evidence_records": self.validated_evidence_records,
            "validated_digest_count": self.validated_digest_count,
            "role_projection_count": self.role_projection_count,
            "candidate_count": self.candidate_count,
            "component_count": self.component_count,
            "value_count": self.value_count,
            "sequence_reference_count": self.sequence_reference_count,
            "digest_operation_count": self.digest_operation_count,
        }


@dataclass(frozen=True, slots=True)
class PerceptualContextBundle:
    contract_digest: str
    binding_digest: str
    config_digest: str
    composite_state_digest: str
    probe_digest: str
    source_digest: str
    role_findings: tuple[PerceptualContextRoleFinding, ...]
    sequence_finding: B4ShortSequenceFinding
    resource_ledger: PerceptualContextResourceLedger
    prestate_digest: str
    poststate_digest: str
    automatic_selection: None
    bundle_digest: str
    schema: str = S2GB_SCHEMA

    def __post_init__(self) -> None:
        _require(type(self.role_findings) is tuple and len(self.role_findings) == 3 and tuple(item.role for item in self.role_findings) == ROLES, S2GB_CAPACITY_EXCEEDED, "bundle roles or candidate capacity differ")
        candidates = tuple(item.candidate for item in self.role_findings if item.candidate is not None)
        _require(len(candidates) <= MAX_CANDIDATES, S2GB_CAPACITY_EXCEEDED, "more than three candidates")
        _require(type(self.sequence_finding) is B4ShortSequenceFinding and type(self.resource_ledger) is PerceptualContextResourceLedger, S2GB_INVALID_TYPE_OR_SCHEMA, "bundle evidence differs")
        _require(self.automatic_selection is None, S2GB_EVIDENCE_INVALID, "automatic selection is forbidden")
        _require(self.prestate_digest == self.poststate_digest == self.composite_state_digest, S2GB_READ_ONLY_VIOLATION, "bundle source state changed")
        _require(self.contract_digest == S2GA_CONTRACT_DIGEST and all(_valid_digest(value) for value in (self.binding_digest, self.config_digest, self.composite_state_digest, self.probe_digest, self.source_digest)), S2GB_DIGEST_MISMATCH, "bundle binding differs")
        _require(self.schema == S2GB_SCHEMA and self.bundle_digest == _digest(self.payload_without_digest()), S2GB_DIGEST_MISMATCH, "bundle digest differs")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "contract_digest": self.contract_digest,
            "binding_digest": self.binding_digest,
            "config_digest": self.config_digest,
            "composite_state_digest": self.composite_state_digest,
            "probe_digest": self.probe_digest,
            "source_digest": self.source_digest,
            "role_finding_digests": [item.finding_digest for item in self.role_findings],
            "sequence_finding_digest": self.sequence_finding.finding_digest,
            "resource_ledger_digest": self.resource_ledger.ledger_digest,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "automatic_selection": self.automatic_selection,
        }


def _component(
    role: str,
    values: tuple[float, ...],
    source_id: str,
    source_state_digest: str,
    native_distances: tuple[float, ...] | None,
    functional_distances: tuple[float, ...],
    support_count: int | None,
    stable: bool | None,
    last_selected_step: int | None,
    formation_index: int | None,
) -> PerceptualContextComponent:
    source_payload = {
        "schema": S2GB_SCHEMA,
        "source_id": source_id,
        "source_state_digest": source_state_digest,
        "component_role": role,
    }
    source_digest = _digest(source_payload)
    values_digest = _digest(list(values))
    payload = {
        "schema": S2GB_SCHEMA,
        "component_role": role,
        "values": list(values),
        "source_id": source_id,
        "source_digest": source_digest,
        "values_digest": values_digest,
        "native_distances": None if native_distances is None else list(native_distances),
        "functional_distances": list(functional_distances),
        "support_count": support_count,
        "stable": stable,
        "last_selected_step": last_selected_step,
        "formation_index": formation_index,
    }
    return PerceptualContextComponent(
        role,
        values,
        source_id,
        source_digest,
        values_digest,
        native_distances,
        functional_distances,
        support_count,
        stable,
        last_selected_step,
        formation_index,
        _digest(payload),
    )


def _candidate(role: str, components: tuple[PerceptualContextComponent, ...]) -> PerceptualContextCandidate:
    relation = "CROSS_MODAL_RELATION_NOT_REPRESENTED" if role == "TSPM_SLOW" else "JOINT_SOURCE_VALUES"
    payload = {
        "schema": S2GB_SCHEMA,
        "role": role,
        "component_digests": [item.component_digest for item in components],
        "cross_modal_relation": relation,
    }
    return PerceptualContextCandidate(role, components, relation, _digest(payload))


def _b4_sequence_slot_digest(
    observed_b4_state_digest: str,
    observation: read_only.B4SlotObservation,
) -> str:
    return _digest(
        {
            "schema": S2GB_SCHEMA,
            "observed_b4_state_digest": observed_b4_state_digest,
            "slot_id": observation.slot_id,
            "formation_index": observation.formation_index,
            "values_digest": _digest(list(observation.values)),
        }
    )


def _role_finding(role: str, status: str, candidate: PerceptualContextCandidate | None, absence_reason: str | None) -> PerceptualContextRoleFinding:
    payload = {
        "schema": S2GB_SCHEMA,
        "role": role,
        "status": status,
        "candidate_digest": None if candidate is None else candidate.candidate_digest,
        "absence_reason": absence_reason,
    }
    return PerceptualContextRoleFinding(role, status, candidate, absence_reason, _digest(payload))


def _validate_finding(binding: PerceptualContextProjectionBinding, finding: coordinator.B4TSPM1ReadOnlyFinding) -> None:
    _require(type(finding) is coordinator.B4TSPM1ReadOnlyFinding and finding.schema == coordinator.S2FS_SCHEMA, S2GB_INVALID_TYPE_OR_SCHEMA, "exact validated S2-FS finding required")
    _require(finding.finding_digest == coordinator._digest(finding.payload_without_digest()), S2GB_DIGEST_MISMATCH, "read-only finding digest differs")
    _require(finding.probe_digest == binding.probe_digest, S2GB_PROBE_MISMATCH, "probe binding differs")
    _require(finding.observed_state_digest == binding.composite_state_digest and finding.prestate_digest == finding.poststate_digest == binding.composite_state_digest, S2GB_STATE_DIGEST_MISMATCH, "composite state binding differs")
    _require(finding.roles == ROLES, S2GB_EVIDENCE_INVALID, "role set differs")
    _require(type(finding.resource_ledger) is coordinator.B4TSPM1ResourceLedger and finding.resource_ledger.operation == "READ_ONLY", S2GB_EVIDENCE_INVALID, "read-only ledger differs")

    b4 = finding.b4_recent
    _require(type(b4) is read_only.B4ContentFinding and b4.prestate_digest == b4.poststate_digest == b4.observed_state_digest, S2GB_READ_ONLY_VIOLATION, "B4 source state changed")
    _require(b4.probe_values_digest == binding.probe_values_digest and b4.occupied_slot_count == len(b4.candidates) <= MAX_SEQUENCE_REFERENCES, S2GB_EVIDENCE_INVALID, "B4 probe or capacity differs")
    _require(b4.recognized == (b4.selected is not None), S2GB_EVIDENCE_INVALID, "B4 decision differs")
    source_ids: list[str] = []
    for item in b4.candidates:
        _require(type(item) is read_only.B4SlotObservation, S2GB_INVALID_TYPE_OR_SCHEMA, "B4 observation type differs")
        _identifier(item.slot_id, "B4 slot_id")
        _values(item.values, 26, "B4 values")
        _require(type(item.formation_index) is int and item.formation_index > 0 and type(item.functional_match) is bool, S2GB_EVIDENCE_INVALID, "B4 lifecycle differs")
        _nonnegative_number(item.auditory_distance, "B4 auditory distance")
        _nonnegative_number(item.visual_distance, "B4 visual distance")
        source_ids.append(item.slot_id)
    _require(len(source_ids) == len(set(source_ids)), S2GB_DUPLICATE_SOURCE, "duplicate B4 source")
    if b4.selected is not None:
        _require(type(b4.selected) is read_only.B4SlotObservation and b4.selected in b4.candidates and b4.selected.functional_match, S2GB_EVIDENCE_INVALID, "B4 selected source differs")

    if finding.tspm_fast is not None:
        fast = finding.tspm_fast
        _identifier(fast.slot_id, "Fast slot_id")
        _require(_valid_digest(fast.slot_digest), S2GB_DIGEST_MISMATCH, "Fast slot digest differs")
        _values(fast.auditory_values, 8, "Fast auditory values")
        _values(fast.visual_values, 18, "Fast visual values")
        _require(fast.functional_match and type(fast.native_match) is bool and type(fast.support_count) is int and fast.support_count > 0 and type(fast.last_selected_step) is int and fast.last_selected_step > 0 and type(fast.consolidation_count) is int and fast.consolidation_count >= 0, S2GB_EVIDENCE_INVALID, "Fast lifecycle or decision differs")
        _nonnegative_number(fast.auditory_distance, "Fast auditory distance")
        _nonnegative_number(fast.visual_distance, "Fast visual distance")

    slow = finding.tspm_slow
    _require(type(slow) is tuple and len(slow) == 2 and tuple(item.modality_id for item in slow) == ("auditory", "visual"), S2GB_EVIDENCE_INVALID, "Slow modality order differs")
    slow_sources: list[str] = []
    for item, dimension in zip(slow, (8, 18)):
        _require(type(item) is read_only.SlowBankFinding, S2GB_INVALID_TYPE_OR_SCHEMA, "Slow finding type differs")
        _identifier(item.bank_id, "Slow bank_id")
        _require(_valid_digest(item.observed_bank_state_digest), S2GB_DIGEST_MISMATCH, "Slow bank digest differs")
        _require(item.occupied_slot_count == len(item.slots) and 0 <= item.eligible_slot_count <= item.occupied_slot_count, S2GB_EVIDENCE_INVALID, "Slow capacity differs")
        _require(
            type(item.functional_recognized) is bool
            and (not item.functional_recognized or (item.selected is not None and item.selected.stable)),
            S2GB_EVIDENCE_INVALID,
            "Slow functional decision differs",
        )
        for slot in item.slots:
            _identifier(slot.slot_id, "Slow slot_id")
            _require(_valid_digest(slot.slot_digest), S2GB_DIGEST_MISMATCH, "Slow slot digest differs")
            _values(slot.prototype_values, dimension, "Slow prototype values")
            _require(type(slot.support_count) is int and slot.support_count > 0 and type(slot.last_selected_step) is int and slot.last_selected_step > 0 and type(slot.stable) is bool, S2GB_EVIDENCE_INVALID, "Slow lifecycle differs")
            _nonnegative_number(slot.native_distance, "Slow distance")
        if item.selected is not None:
            _require(item.selected in item.slots, S2GB_EVIDENCE_INVALID, "Slow selected source differs")
            slow_sources.append(f"{item.bank_id}/{item.selected.slot_id}")
    selected_sources = ([b4.selected.slot_id] if b4.selected is not None else []) + ([finding.tspm_fast.slot_id] if finding.tspm_fast is not None else []) + slow_sources
    _require(len(selected_sources) == len(set(selected_sources)), S2GB_DUPLICATE_SOURCE, "one selected source is duplicated")


def project_perceptual_context_bundle(
    binding: PerceptualContextProjectionBinding,
    finding: coordinator.B4TSPM1ReadOnlyFinding,
    sequence_evidence: ValidatedB4ShortSequenceEvidence,
) -> PerceptualContextBundle:
    """Project one validated finding without storage access or state changes."""

    _require(type(binding) is PerceptualContextProjectionBinding, S2GB_INVALID_TYPE_OR_SCHEMA, "exact projection binding required")
    _require(type(sequence_evidence) is ValidatedB4ShortSequenceEvidence, S2GB_INVALID_TYPE_OR_SCHEMA, "exact sequence evidence required")
    _validate_finding(binding, finding)
    _require(sequence_evidence.observed_b4_state_digest == finding.b4_recent.observed_state_digest, S2GB_STATE_DIGEST_MISMATCH, "sequence state differs")
    _require(sequence_evidence.probe_digest == binding.probe_digest, S2GB_PROBE_MISMATCH, "sequence probe differs")
    b4_sources = {
        (item.slot_id, item.formation_index): item for item in finding.b4_recent.candidates
    }
    for reference in sequence_evidence.references:
        source = b4_sources.get((reference.slot_id, reference.formation_index))
        _require(source is not None, S2GB_EVIDENCE_INVALID, "sequence reference has no current B4 source")
        _require(
            reference.values_digest == _digest(list(source.values))
            and reference.slot_digest
            == _b4_sequence_slot_digest(
                finding.b4_recent.observed_state_digest,
                source,
            ),
            S2GB_DIGEST_MISMATCH,
            "sequence reference does not bind its current B4 source",
        )

    b4_selected = finding.b4_recent.selected
    if b4_selected is None:
        b4_role = _role_finding("B4_RECENT", "ABSENT_VALID", None, "NO_OCCUPIED_SOURCE" if finding.b4_recent.occupied_slot_count == 0 else "NO_FUNCTIONAL_MATCH")
    else:
        component = _component("AV_JOINT", b4_selected.values, b4_selected.slot_id, finding.b4_recent.observed_state_digest, None, (b4_selected.auditory_distance, b4_selected.visual_distance), None, None, None, b4_selected.formation_index)
        b4_role = _role_finding("B4_RECENT", "AVAILABLE_COMPLETE", _candidate("B4_RECENT", (component,)), None)

    fast = finding.tspm_fast
    if fast is None:
        fast_role = _role_finding("TSPM_FAST", "ABSENT_VALID", None, "NO_FUNCTIONAL_MATCH")
    else:
        component = _component("AV_JOINT", fast.auditory_values + fast.visual_values, fast.slot_id, fast.slot_digest, (fast.auditory_distance, fast.visual_distance), (fast.auditory_distance, fast.visual_distance), fast.support_count, None, fast.last_selected_step, None)
        fast_role = _role_finding("TSPM_FAST", "AVAILABLE_COMPLETE", _candidate("TSPM_FAST", (component,)), None)

    slow_components = []
    for slow_finding, component_role in zip(finding.tspm_slow, ("AUDITORY", "VISUAL")):
        if not slow_finding.functional_recognized:
            continue
        selected = slow_finding.selected
        _require(selected is not None and selected.stable, S2GB_EVIDENCE_INVALID, "Slow recognized source is incomplete")
        source_id = f"{slow_finding.bank_id}.{selected.slot_id}"
        slow_components.append(_component(component_role, selected.prototype_values, source_id, slow_finding.observed_bank_state_digest, (selected.native_distance,), (selected.native_distance,), selected.support_count, selected.stable, selected.last_selected_step, None))
    if slow_components:
        status = "AVAILABLE_COMPLETE" if len(slow_components) == 2 else "AVAILABLE_PARTIAL"
        slow_role = _role_finding("TSPM_SLOW", status, _candidate("TSPM_SLOW", tuple(slow_components)), None)
    else:
        slow_role = _role_finding("TSPM_SLOW", "ABSENT_VALID", None, "NO_STABLE_SLOW_MATCH")

    role_findings = (b4_role, fast_role, slow_role)
    candidates = tuple(item.candidate for item in role_findings if item.candidate is not None)
    components = tuple(component for candidate in candidates for component in candidate.components)
    _require(len(candidates) <= MAX_CANDIDATES and len(components) <= MAX_COMPONENTS, S2GB_CAPACITY_EXCEEDED, "candidate or component bound exceeded")
    value_count = sum(len(item.values) for item in components)
    _require(value_count <= MAX_VALUES, S2GB_CAPACITY_EXCEEDED, "value bound exceeded")

    sequence_payload = {
        "schema": S2GB_SCHEMA,
        "status": sequence_evidence.status,
        "reference_digests": [item.reference_digest for item in sequence_evidence.references],
        "observed_b4_state_digest": sequence_evidence.observed_b4_state_digest,
        "source_evidence_digest": sequence_evidence.evidence_digest,
    }
    sequence_finding = B4ShortSequenceFinding(sequence_evidence.status, sequence_evidence.references, sequence_evidence.observed_b4_state_digest, sequence_evidence.evidence_digest, _digest(sequence_payload))
    evidence_records = 2 + len(finding.b4_recent.candidates) + (1 if finding.tspm_fast is not None else 0) + sum(len(item.slots) for item in finding.tspm_slow) + len(sequence_evidence.references)
    digest_count = 8 + len(components) + len(sequence_evidence.references)
    digest_operations = len(components) + len(candidates) + 3 + 1 + 1 + 1
    ledger_payload = {
        "schema": S2GB_SCHEMA,
        "validated_evidence_records": evidence_records,
        "validated_digest_count": digest_count,
        "role_projection_count": 3,
        "candidate_count": len(candidates),
        "component_count": len(components),
        "value_count": value_count,
        "sequence_reference_count": len(sequence_evidence.references),
        "digest_operation_count": digest_operations,
    }
    ledger = PerceptualContextResourceLedger(evidence_records, digest_count, 3, len(candidates), len(components), value_count, len(sequence_evidence.references), digest_operations, _digest(ledger_payload))
    payload = {
        "schema": S2GB_SCHEMA,
        "contract_digest": S2GA_CONTRACT_DIGEST,
        "binding_digest": binding.binding_digest,
        "config_digest": binding.config_digest,
        "composite_state_digest": binding.composite_state_digest,
        "probe_digest": binding.probe_digest,
        "source_digest": binding.source_digest,
        "role_finding_digests": [item.finding_digest for item in role_findings],
        "sequence_finding_digest": sequence_finding.finding_digest,
        "resource_ledger_digest": ledger.ledger_digest,
        "prestate_digest": finding.prestate_digest,
        "poststate_digest": finding.poststate_digest,
        "automatic_selection": None,
    }
    bundle = PerceptualContextBundle(S2GA_CONTRACT_DIGEST, binding.binding_digest, binding.config_digest, binding.composite_state_digest, binding.probe_digest, binding.source_digest, role_findings, sequence_finding, ledger, finding.prestate_digest, finding.poststate_digest, None, _digest(payload))
    _require(
        finding.finding_digest == coordinator._digest(finding.payload_without_digest())
        and binding.binding_digest == _digest(binding.payload_without_digest())
        and sequence_evidence.evidence_digest == _digest(sequence_evidence.payload_without_digest()),
        S2GB_READ_ONLY_VIOLATION,
        "projection input changed during bundle construction",
    )
    return bundle


__all__: tuple[str, ...] = ()
