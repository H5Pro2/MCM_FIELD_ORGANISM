"""Private atomic coordinator for the existing B4 and TSPM-1 states.

The module adds no storage mechanism, history, runner, persistence, public
export, or field path. One validated receptor source is projected once and
fed to two unchanged private operators. Candidate states remain local until
their complete composite relation has been validated.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
from threading import Lock

from mcm_field_organism import _tspm1_private as tspm1
from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison
from mcm_field_organism._ppb1_active_receptor_batch_binding import (
    PPB1ActiveReceptorBatchEnvelope,
    PPB1ActiveReceptorTimedFrameBinding,
)
from tools import _retention_capacity_read_only as read_only


S2FS_SCHEMA = "s2fs.b4-tspm1.private-coordinator.v1"
B4_CAPACITY = 9
AUDITORY_DIMENSION = 8
VISUAL_DIMENSION = 18
AV_DIMENSION = AUDITORY_DIMENSION + VISUAL_DIMENSION

S2FS_INVALID_TYPE_OR_SCHEMA = "S2FS_INVALID_TYPE_OR_SCHEMA"
S2FS_CONFIG_MISMATCH = "S2FS_CONFIG_MISMATCH"
S2FS_INPUT_BINDING_INVALID = "S2FS_INPUT_BINDING_INVALID"
S2FS_PRESTATE_INVALID = "S2FS_PRESTATE_INVALID"
S2FS_OWNER_AUTHORIZATION_MISMATCH = "S2FS_OWNER_AUTHORIZATION_MISMATCH"
S2FS_OWNER_TERMINAL = "S2FS_OWNER_TERMINAL"
S2FS_OWNER_BUSY = "S2FS_OWNER_BUSY"
S2FS_B4_CANDIDATE_FAILED = "S2FS_B4_CANDIDATE_FAILED"
S2FS_TSPM_CANDIDATE_FAILED = "S2FS_TSPM_CANDIDATE_FAILED"
S2FS_RELATION_MISMATCH = "S2FS_RELATION_MISMATCH"
S2FS_RESOURCE_LEDGER_INVALID = "S2FS_RESOURCE_LEDGER_INVALID"
S2FS_READ_ONLY_VIOLATION = "S2FS_READ_ONLY_VIOLATION"

_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,126}[a-z0-9]$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_OWNER_TERMINAL_STATES = {"CONSUMED", "FAILED"}

# Existing per-arm functional ceilings from the bound retention runner.
_B4_FUNCTIONAL_WRITE_WORDS = 293
_B4_FUNCTIONAL_DISTANCE_TERMS = 234
_TSPM_FUNCTIONAL_WRITE_WORDS = 293
_TSPM_FUNCTIONAL_DISTANCE_TERMS = 234

# Coordinator work is counted independently of the two arm ceilings.
_FORMATION_COORDINATOR_VALIDATION_TERMS = 18
_FORMATION_COORDINATOR_DIGEST_OPERATIONS = 10
_FORMATION_COORDINATOR_WRITE_WORDS = 31
_READ_COORDINATOR_VALIDATION_TERMS = 14
_READ_COORDINATOR_DIGEST_OPERATIONS = 8
_READ_COORDINATOR_WRITE_WORDS = 14


class S2FSCoordinatorError(RuntimeError):
    """One private coordinator contract violation."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise S2FSCoordinatorError(code, message)


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
        S2FS_INVALID_TYPE_OR_SCHEMA,
        f"{role} is not a canonical private identifier",
    )
    return value


def _exact_nonnegative(value: object, role: str) -> int:
    _require(
        type(value) is int and value >= 0,
        S2FS_INVALID_TYPE_OR_SCHEMA,
        f"{role} must be an exact nonnegative integer",
    )
    return value


def _values(values: object, length: int, role: str) -> tuple[float, ...]:
    _require(
        type(values) is tuple and len(values) == length,
        S2FS_INPUT_BINDING_INVALID,
        f"{role} requires one exact {length}-value tuple",
    )
    _require(
        all(type(value) in (int, float) for value in values),
        S2FS_INPUT_BINDING_INVALID,
        f"{role} contains a nonnumeric or boolean value",
    )
    normalized = tuple(float(value) for value in values)
    _require(
        all(math.isfinite(value) and -1.0 <= value <= 1.0 for value in normalized),
        S2FS_INPUT_BINDING_INVALID,
        f"{role} contains a nonfinite or out-of-range value",
    )
    return normalized


def _b4_digest(state: comparison._B4State) -> str:
    return _digest(comparison._canonical(state))


@dataclass(frozen=True, slots=True)
class B4TSPM1CoordinatorConfig:
    tspm_config: tspm1.TSPM1ConfigBinding
    b4_capacity: int
    auditory_dimension: int
    visual_dimension: int
    config_digest: str
    schema: str = S2FS_SCHEMA

    def __post_init__(self) -> None:
        _require(
            self.schema == S2FS_SCHEMA
            and type(self.tspm_config) is tspm1.TSPM1ConfigBinding
            and self.b4_capacity == B4_CAPACITY
            and self.auditory_dimension == AUDITORY_DIMENSION
            and self.visual_dimension == VISUAL_DIMENSION
            and self.config_digest == _digest(self.payload_without_digest()),
            S2FS_CONFIG_MISMATCH,
            "coordinator config is incomplete or digest inconsistent",
        )
        tspm1._validate_config(self.tspm_config)

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "tspm_config_binding_digest": self.tspm_config.config_binding_digest,
            "b4_capacity": self.b4_capacity,
            "auditory_dimension": self.auditory_dimension,
            "visual_dimension": self.visual_dimension,
        }


def build_coordinator_config(
    tspm_config: tspm1.TSPM1ConfigBinding,
) -> B4TSPM1CoordinatorConfig:
    _require(
        type(tspm_config) is tspm1.TSPM1ConfigBinding,
        S2FS_INVALID_TYPE_OR_SCHEMA,
        "one exact TSPM-1 config is required",
    )
    payload = {
        "schema": S2FS_SCHEMA,
        "tspm_config_binding_digest": tspm_config.config_binding_digest,
        "b4_capacity": B4_CAPACITY,
        "auditory_dimension": AUDITORY_DIMENSION,
        "visual_dimension": VISUAL_DIMENSION,
    }
    return B4TSPM1CoordinatorConfig(
        tspm_config,
        B4_CAPACITY,
        AUDITORY_DIMENSION,
        VISUAL_DIMENSION,
        _digest(payload),
    )


@dataclass(frozen=True, slots=True)
class B4TSPM1CompositeState:
    config_digest: str
    generation: int
    parent_state_digest: str | None
    last_input_digest: str | None
    b4_state: comparison._B4State
    tspm_state: tspm1.TSPM1CompositeState
    state_digest: str
    schema: str = S2FS_SCHEMA

    def __post_init__(self) -> None:
        generation = _exact_nonnegative(self.generation, "generation")
        initial_lineage = self.parent_state_digest is None and self.last_input_digest is None
        advanced_lineage = _valid_digest(self.parent_state_digest) and _valid_digest(
            self.last_input_digest
        )
        _require(
            self.schema == S2FS_SCHEMA
            and _valid_digest(self.config_digest)
            and type(self.b4_state) is comparison._B4State
            and type(self.tspm_state) is tspm1.TSPM1CompositeState
            and self.b4_state.accepted_count == generation
            and self.tspm_state.generation == generation
            and self.tspm_state.fast_state.accepted_exposure_count == generation
            and ((generation == 0 and initial_lineage) or (generation > 0 and advanced_lineage))
            and self.state_digest == _digest(self.payload_without_digest()),
            S2FS_PRESTATE_INVALID,
            "composite state identity, lineage, or generation is invalid",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "config_digest": self.config_digest,
            "generation": self.generation,
            "parent_state_digest": self.parent_state_digest,
            "last_input_digest": self.last_input_digest,
            "b4_state_digest": _b4_digest(self.b4_state),
            "tspm_state_digest": self.tspm_state.composite_state_digest,
        }


def _make_composite_state(
    config: B4TSPM1CoordinatorConfig,
    generation: int,
    parent_digest: str | None,
    input_digest: str | None,
    b4_state: comparison._B4State,
    tspm_state: tspm1.TSPM1CompositeState,
) -> B4TSPM1CompositeState:
    payload = {
        "schema": S2FS_SCHEMA,
        "config_digest": config.config_digest,
        "generation": generation,
        "parent_state_digest": parent_digest,
        "last_input_digest": input_digest,
        "b4_state_digest": _b4_digest(b4_state),
        "tspm_state_digest": tspm_state.composite_state_digest,
    }
    return B4TSPM1CompositeState(
        config.config_digest,
        generation,
        parent_digest,
        input_digest,
        b4_state,
        tspm_state,
        _digest(payload),
    )


def initial_composite_state(
    config: B4TSPM1CoordinatorConfig,
) -> B4TSPM1CompositeState:
    binding = _validate_config(config)
    b4_state = comparison._B4State(
        0,
        tuple(
            comparison._FIFOEntry(f"b4.slot.{index:03d}", False, (), None)
            for index in range(B4_CAPACITY)
        ),
    )
    tspm_state = tspm1.initial_tspm1_composite_state(binding.tspm_config)
    return _make_composite_state(binding, 0, None, None, b4_state, tspm_state)


def _source_payload(
    config_digest: str,
    envelope_digest: str,
    auditory_digest: str,
    visual_digest: str,
    tspm_source_digest: str,
    values_digest: str,
    *,
    role: str,
) -> dict[str, object]:
    return {
        "schema": S2FS_SCHEMA,
        "role": role,
        "config_digest": config_digest,
        "envelope_digest": envelope_digest,
        "auditory_timed_frame_digest": auditory_digest,
        "visual_timed_frame_digest": visual_digest,
        "tspm_source_digest": tspm_source_digest,
        "values_digest": values_digest,
    }


@dataclass(frozen=True, slots=True)
class B4TSPM1BoundInput:
    config_digest: str
    envelope: PPB1ActiveReceptorBatchEnvelope
    auditory: PPB1ActiveReceptorTimedFrameBinding
    visual: PPB1ActiveReceptorTimedFrameBinding
    tspm_exposure: tspm1.TSPM1BoundExposure
    auditory_values: tuple[float, ...]
    visual_values: tuple[float, ...]
    av_values: tuple[float, ...]
    values_digest: str
    input_digest: str
    schema: str = S2FS_SCHEMA

    def __post_init__(self) -> None:
        auditory = _values(self.auditory_values, AUDITORY_DIMENSION, "auditory input")
        visual = _values(self.visual_values, VISUAL_DIMENSION, "visual input")
        payload = _source_payload(
            self.config_digest,
            self.envelope.envelope_digest,
            self.auditory.timed_frame_provenance_digest,
            self.visual.timed_frame_provenance_digest,
            self.tspm_exposure.exposure_digest,
            self.values_digest,
            role="FORMATION",
        )
        _require(
            self.schema == S2FS_SCHEMA
            and _valid_digest(self.config_digest)
            and type(self.envelope) is PPB1ActiveReceptorBatchEnvelope
            and type(self.auditory) is PPB1ActiveReceptorTimedFrameBinding
            and type(self.visual) is PPB1ActiveReceptorTimedFrameBinding
            and type(self.tspm_exposure) is tspm1.TSPM1BoundExposure
            and self.tspm_exposure.envelope is self.envelope
            and self.tspm_exposure.auditory is self.auditory
            and self.tspm_exposure.visual is self.visual
            and self.av_values == auditory + visual
            and self.values_digest == _digest(list(self.av_values))
            and self.input_digest == _digest(payload),
            S2FS_INPUT_BINDING_INVALID,
            "formation input does not bind one common receptor source",
        )


@dataclass(frozen=True, slots=True)
class B4TSPM1BoundProbe:
    config_digest: str
    envelope: PPB1ActiveReceptorBatchEnvelope
    auditory: PPB1ActiveReceptorTimedFrameBinding
    visual: PPB1ActiveReceptorTimedFrameBinding
    tspm_probe: tspm1.TSPM1BoundProbe
    auditory_values: tuple[float, ...]
    visual_values: tuple[float, ...]
    av_values: tuple[float, ...]
    values_digest: str
    probe_digest: str
    schema: str = S2FS_SCHEMA

    def __post_init__(self) -> None:
        auditory = _values(self.auditory_values, AUDITORY_DIMENSION, "auditory probe")
        visual = _values(self.visual_values, VISUAL_DIMENSION, "visual probe")
        payload = _source_payload(
            self.config_digest,
            self.envelope.envelope_digest,
            self.auditory.timed_frame_provenance_digest,
            self.visual.timed_frame_provenance_digest,
            self.tspm_probe.probe_digest,
            self.values_digest,
            role="READ_ONLY",
        )
        _require(
            self.schema == S2FS_SCHEMA
            and _valid_digest(self.config_digest)
            and type(self.envelope) is PPB1ActiveReceptorBatchEnvelope
            and type(self.auditory) is PPB1ActiveReceptorTimedFrameBinding
            and type(self.visual) is PPB1ActiveReceptorTimedFrameBinding
            and type(self.tspm_probe) is tspm1.TSPM1BoundProbe
            and self.tspm_probe.envelope is self.envelope
            and self.tspm_probe.auditory is self.auditory
            and self.tspm_probe.visual is self.visual
            and self.av_values == auditory + visual
            and self.values_digest == _digest(list(self.av_values))
            and self.probe_digest == _digest(payload),
            S2FS_INPUT_BINDING_INVALID,
            "read-only probe does not bind one common receptor source",
        )


def _bound_values(
    auditory: PPB1ActiveReceptorTimedFrameBinding,
    visual: PPB1ActiveReceptorTimedFrameBinding,
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...], str]:
    auditory_values = _values(
        auditory.timed_frame.frame.values,
        AUDITORY_DIMENSION,
        "auditory receptor values",
    )
    visual_values = _values(
        visual.timed_frame.frame.values,
        VISUAL_DIMENSION,
        "visual receptor values",
    )
    av_values = auditory_values + visual_values
    return auditory_values, visual_values, av_values, _digest(list(av_values))


def bind_coordinator_input(
    config: B4TSPM1CoordinatorConfig,
    envelope: PPB1ActiveReceptorBatchEnvelope,
    auditory: PPB1ActiveReceptorTimedFrameBinding,
    visual: PPB1ActiveReceptorTimedFrameBinding,
) -> B4TSPM1BoundInput:
    binding = _validate_config(config)
    exposure = tspm1.bind_tspm1_exposure(
        binding.tspm_config,
        envelope,
        auditory,
        visual,
    )
    auditory_values, visual_values, av_values, values_digest = _bound_values(
        auditory,
        visual,
    )
    payload = _source_payload(
        binding.config_digest,
        envelope.envelope_digest,
        auditory.timed_frame_provenance_digest,
        visual.timed_frame_provenance_digest,
        exposure.exposure_digest,
        values_digest,
        role="FORMATION",
    )
    return B4TSPM1BoundInput(
        binding.config_digest,
        envelope,
        auditory,
        visual,
        exposure,
        auditory_values,
        visual_values,
        av_values,
        values_digest,
        _digest(payload),
    )


def bind_coordinator_probe(
    config: B4TSPM1CoordinatorConfig,
    envelope: PPB1ActiveReceptorBatchEnvelope,
    auditory: PPB1ActiveReceptorTimedFrameBinding,
    visual: PPB1ActiveReceptorTimedFrameBinding,
) -> B4TSPM1BoundProbe:
    binding = _validate_config(config)
    probe = tspm1.bind_tspm1_probe(
        binding.tspm_config,
        envelope,
        auditory,
        visual,
    )
    auditory_values, visual_values, av_values, values_digest = _bound_values(
        auditory,
        visual,
    )
    payload = _source_payload(
        binding.config_digest,
        envelope.envelope_digest,
        auditory.timed_frame_provenance_digest,
        visual.timed_frame_provenance_digest,
        probe.probe_digest,
        values_digest,
        role="READ_ONLY",
    )
    return B4TSPM1BoundProbe(
        binding.config_digest,
        envelope,
        auditory,
        visual,
        probe,
        auditory_values,
        visual_values,
        av_values,
        values_digest,
        _digest(payload),
    )


@dataclass(frozen=True, slots=True)
class B4TSPM1ResourceLedger:
    operation: str
    common_projection_terms: int
    b4_functional_write_words: int
    b4_functional_distance_terms: int
    tspm_functional_write_words: int
    tspm_functional_distance_terms: int
    coordinator_validation_terms: int
    coordinator_digest_operations: int
    coordinator_write_words: int
    total_functional_write_words: int
    total_functional_distance_terms: int
    total_control_terms: int
    ledger_digest: str
    schema: str = S2FS_SCHEMA

    def __post_init__(self) -> None:
        numeric = (
            self.common_projection_terms,
            self.b4_functional_write_words,
            self.b4_functional_distance_terms,
            self.tspm_functional_write_words,
            self.tspm_functional_distance_terms,
            self.coordinator_validation_terms,
            self.coordinator_digest_operations,
            self.coordinator_write_words,
            self.total_functional_write_words,
            self.total_functional_distance_terms,
            self.total_control_terms,
        )
        _require(
            self.schema == S2FS_SCHEMA
            and self.operation in {"FORMATION", "READ_ONLY"}
            and all(type(value) is int and value >= 0 for value in numeric)
            and self.common_projection_terms == AV_DIMENSION
            and self.total_functional_write_words
            == self.b4_functional_write_words
            + self.tspm_functional_write_words
            + self.coordinator_write_words
            and self.total_functional_distance_terms
            == self.b4_functional_distance_terms
            + self.tspm_functional_distance_terms
            and self.total_control_terms
            == self.common_projection_terms
            + self.coordinator_validation_terms
            + self.coordinator_digest_operations
            and self.ledger_digest == _digest(self.payload_without_digest()),
            S2FS_RESOURCE_LEDGER_INVALID,
            "resource ledger is incomplete or arithmetically inconsistent",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "operation": self.operation,
            "common_projection_terms": self.common_projection_terms,
            "b4_functional_write_words": self.b4_functional_write_words,
            "b4_functional_distance_terms": self.b4_functional_distance_terms,
            "tspm_functional_write_words": self.tspm_functional_write_words,
            "tspm_functional_distance_terms": self.tspm_functional_distance_terms,
            "coordinator_validation_terms": self.coordinator_validation_terms,
            "coordinator_digest_operations": self.coordinator_digest_operations,
            "coordinator_write_words": self.coordinator_write_words,
            "total_functional_write_words": self.total_functional_write_words,
            "total_functional_distance_terms": self.total_functional_distance_terms,
            "total_control_terms": self.total_control_terms,
        }


def _make_resource_ledger(operation: str) -> B4TSPM1ResourceLedger:
    if operation == "FORMATION":
        values = (
            AV_DIMENSION,
            _B4_FUNCTIONAL_WRITE_WORDS,
            _B4_FUNCTIONAL_DISTANCE_TERMS,
            _TSPM_FUNCTIONAL_WRITE_WORDS,
            _TSPM_FUNCTIONAL_DISTANCE_TERMS,
            _FORMATION_COORDINATOR_VALIDATION_TERMS,
            _FORMATION_COORDINATOR_DIGEST_OPERATIONS,
            _FORMATION_COORDINATOR_WRITE_WORDS,
        )
    elif operation == "READ_ONLY":
        values = (
            AV_DIMENSION,
            0,
            _B4_FUNCTIONAL_DISTANCE_TERMS,
            0,
            _TSPM_FUNCTIONAL_DISTANCE_TERMS,
            _READ_COORDINATOR_VALIDATION_TERMS,
            _READ_COORDINATOR_DIGEST_OPERATIONS,
            _READ_COORDINATOR_WRITE_WORDS,
        )
    else:
        raise S2FSCoordinatorError(
            S2FS_RESOURCE_LEDGER_INVALID,
            "unknown resource operation",
        )
    common, b4_write, b4_distance, tspm_write, tspm_distance, checks, digests, output = values
    payload = {
        "schema": S2FS_SCHEMA,
        "operation": operation,
        "common_projection_terms": common,
        "b4_functional_write_words": b4_write,
        "b4_functional_distance_terms": b4_distance,
        "tspm_functional_write_words": tspm_write,
        "tspm_functional_distance_terms": tspm_distance,
        "coordinator_validation_terms": checks,
        "coordinator_digest_operations": digests,
        "coordinator_write_words": output,
        "total_functional_write_words": b4_write + tspm_write + output,
        "total_functional_distance_terms": b4_distance + tspm_distance,
        "total_control_terms": common + checks + digests,
    }
    return B4TSPM1ResourceLedger(
        operation,
        common,
        b4_write,
        b4_distance,
        tspm_write,
        tspm_distance,
        checks,
        digests,
        output,
        payload["total_functional_write_words"],  # type: ignore[arg-type]
        payload["total_functional_distance_terms"],  # type: ignore[arg-type]
        payload["total_control_terms"],  # type: ignore[arg-type]
        _digest(payload),
    )


@dataclass(frozen=True, slots=True)
class B4TSPM1StepReceipt:
    config_digest: str
    owner_prestate_digest: str
    input_digest: str
    composite_prestate_digest: str
    b4_event: str
    b4_slot_id: str
    b4_poststate_digest: str
    tspm_result_digest: str
    tspm_receipt_digest: str
    tspm_poststate_digest: str
    resource_ledger_digest: str
    composite_poststate_digest: str
    receipt_digest: str
    schema: str = S2FS_SCHEMA

    def __post_init__(self) -> None:
        _identifier(self.b4_slot_id, "b4_slot_id")
        digests = (
            self.config_digest,
            self.owner_prestate_digest,
            self.input_digest,
            self.composite_prestate_digest,
            self.b4_poststate_digest,
            self.tspm_result_digest,
            self.tspm_receipt_digest,
            self.tspm_poststate_digest,
            self.resource_ledger_digest,
            self.composite_poststate_digest,
        )
        _require(
            self.schema == S2FS_SCHEMA
            and self.b4_event in {"B4_APPENDED", "B4_EVICTED_AND_APPENDED"}
            and all(_valid_digest(value) for value in digests)
            and self.receipt_digest == _digest(self.payload_without_digest()),
            S2FS_RELATION_MISMATCH,
            "step receipt is incomplete or digest inconsistent",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "config_digest": self.config_digest,
            "owner_prestate_digest": self.owner_prestate_digest,
            "input_digest": self.input_digest,
            "composite_prestate_digest": self.composite_prestate_digest,
            "b4_event": self.b4_event,
            "b4_slot_id": self.b4_slot_id,
            "b4_poststate_digest": self.b4_poststate_digest,
            "tspm_result_digest": self.tspm_result_digest,
            "tspm_receipt_digest": self.tspm_receipt_digest,
            "tspm_poststate_digest": self.tspm_poststate_digest,
            "resource_ledger_digest": self.resource_ledger_digest,
            "composite_poststate_digest": self.composite_poststate_digest,
        }


@dataclass(frozen=True, slots=True)
class B4TSPM1CoordinatorOwnerSnapshot:
    owner_id: str
    authorization_id: str
    consumption_id: str
    authorized_config_digest: str
    authorized_prestate_digest: str
    authorized_input_digest: str
    status: str
    attempt_count: int
    use_count: int
    committed_result_digest: str | None
    failure_code: str | None
    failure_digest: str | None
    owner_state_digest: str
    schema: str = S2FS_SCHEMA

    def __post_init__(self) -> None:
        for role in ("owner_id", "authorization_id", "consumption_id"):
            _identifier(getattr(self, role), role)
        authorized = (
            self.authorized_config_digest,
            self.authorized_prestate_digest,
            self.authorized_input_digest,
        )
        if self.status == "AUTHORIZED":
            shape = (
                self.attempt_count == 0
                and self.use_count == 0
                and self.committed_result_digest is None
                and self.failure_code is None
                and self.failure_digest is None
            )
        elif self.status == "CONSUMED":
            shape = (
                self.attempt_count == 1
                and self.use_count == 1
                and _valid_digest(self.committed_result_digest)
                and self.failure_code is None
                and self.failure_digest is None
            )
        else:
            shape = (
                self.status == "FAILED"
                and self.attempt_count == 1
                and self.use_count == 0
                and self.committed_result_digest is None
                and isinstance(self.failure_code, str)
                and bool(self.failure_code)
                and _valid_digest(self.failure_digest)
            )
        _require(
            self.schema == S2FS_SCHEMA
            and all(_valid_digest(value) for value in authorized)
            and shape
            and self.owner_state_digest == _digest(self.payload_without_digest()),
            S2FS_RELATION_MISMATCH,
            "owner snapshot is invalid",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "owner_id": self.owner_id,
            "authorization_id": self.authorization_id,
            "consumption_id": self.consumption_id,
            "authorized_config_digest": self.authorized_config_digest,
            "authorized_prestate_digest": self.authorized_prestate_digest,
            "authorized_input_digest": self.authorized_input_digest,
            "status": self.status,
            "attempt_count": self.attempt_count,
            "use_count": self.use_count,
            "committed_result_digest": self.committed_result_digest,
            "failure_code": self.failure_code,
            "failure_digest": self.failure_digest,
        }

    def result_projection(self) -> dict[str, object]:
        payload = self.payload_without_digest()
        payload.pop("committed_result_digest")
        return payload


@dataclass(frozen=True, slots=True)
class B4TSPM1StepResult:
    poststate: B4TSPM1CompositeState
    receipt: B4TSPM1StepReceipt
    resource_ledger: B4TSPM1ResourceLedger
    owner_poststate: B4TSPM1CoordinatorOwnerSnapshot
    result_digest: str
    schema: str = S2FS_SCHEMA

    def __post_init__(self) -> None:
        _require(
            self.schema == S2FS_SCHEMA
            and type(self.poststate) is B4TSPM1CompositeState
            and type(self.receipt) is B4TSPM1StepReceipt
            and type(self.resource_ledger) is B4TSPM1ResourceLedger
            and type(self.owner_poststate) is B4TSPM1CoordinatorOwnerSnapshot
            and self.owner_poststate.status == "CONSUMED"
            and self.owner_poststate.committed_result_digest == self.result_digest
            and self.result_digest == _digest(self.payload_without_digest()),
            S2FS_RELATION_MISMATCH,
            "step result is incomplete or digest inconsistent",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "poststate_digest": self.poststate.state_digest,
            "receipt_digest": self.receipt.receipt_digest,
            "resource_ledger_digest": self.resource_ledger.ledger_digest,
            "owner_poststate_projection": self.owner_poststate.result_projection(),
        }


def _snapshot(owner: B4TSPM1CoordinatorOwner) -> B4TSPM1CoordinatorOwnerSnapshot:
    payload = {
        "schema": S2FS_SCHEMA,
        "owner_id": owner._owner_id,
        "authorization_id": owner._authorization_id,
        "consumption_id": owner._consumption_id,
        "authorized_config_digest": owner._authorized_config_digest,
        "authorized_prestate_digest": owner._authorized_prestate_digest,
        "authorized_input_digest": owner._authorized_input_digest,
        "status": owner._status,
        "attempt_count": owner._attempt_count,
        "use_count": owner._use_count,
        "committed_result_digest": owner._committed_result_digest,
        "failure_code": owner._failure_code,
        "failure_digest": owner._failure_digest,
    }
    return B4TSPM1CoordinatorOwnerSnapshot(
        owner._owner_id,
        owner._authorization_id,
        owner._consumption_id,
        owner._authorized_config_digest,
        owner._authorized_prestate_digest,
        owner._authorized_input_digest,
        owner._status,
        owner._attempt_count,
        owner._use_count,
        owner._committed_result_digest,
        owner._failure_code,
        owner._failure_digest,
        _digest(payload),
    )


def _validate_config(config: object) -> B4TSPM1CoordinatorConfig:
    _require(
        type(config) is B4TSPM1CoordinatorConfig,
        S2FS_INVALID_TYPE_OR_SCHEMA,
        "one exact coordinator config is required",
    )
    _require(
        config.config_digest == _digest(config.payload_without_digest()),
        S2FS_CONFIG_MISMATCH,
        "coordinator config digest changed",
    )
    tspm1._validate_config(config.tspm_config)
    return config


def _validate_state(
    config: B4TSPM1CoordinatorConfig,
    state: object,
) -> B4TSPM1CompositeState:
    _require(
        type(state) is B4TSPM1CompositeState,
        S2FS_INVALID_TYPE_OR_SCHEMA,
        "one exact composite state is required",
    )
    _require(
        state.config_digest == config.config_digest
        and state.state_digest == _digest(state.payload_without_digest())
        and state.generation == state.b4_state.accepted_count
        and state.generation == state.tspm_state.generation
        and state.generation == state.tspm_state.fast_state.accepted_exposure_count,
        S2FS_PRESTATE_INVALID,
        "composite state relation or config binding changed",
    )
    read_only._validate_b4_state(state.b4_state)
    tspm1._validate_composite_state(config.tspm_config, state.tspm_state)
    return state


def _validate_input(
    config: B4TSPM1CoordinatorConfig,
    source: object,
) -> B4TSPM1BoundInput:
    _require(
        type(source) is B4TSPM1BoundInput,
        S2FS_INPUT_BINDING_INVALID,
        "one exact bound input is required",
    )
    auditory_values, visual_values, av_values, values_digest = _bound_values(
        source.auditory,
        source.visual,
    )
    _require(
        source.config_digest == config.config_digest
        and source.tspm_exposure.config_binding_digest
        == config.tspm_config.config_binding_digest
        and source.tspm_exposure.envelope is source.envelope
        and source.tspm_exposure.auditory is source.auditory
        and source.tspm_exposure.visual is source.visual
        and source.auditory_values == auditory_values
        and source.visual_values == visual_values
        and source.av_values == av_values
        and source.values_digest == values_digest
        and source.input_digest
        == _digest(
            _source_payload(
                source.config_digest,
                source.envelope.envelope_digest,
                source.auditory.timed_frame_provenance_digest,
                source.visual.timed_frame_provenance_digest,
                source.tspm_exposure.exposure_digest,
                source.values_digest,
                role="FORMATION",
            )
        ),
        S2FS_INPUT_BINDING_INVALID,
        "bound input config or digest changed",
    )
    tspm1._validate_bound_source_provenance(config.tspm_config, source.tspm_exposure)
    tspm1._validate_bound_source_geometry(config.tspm_config, source.tspm_exposure)
    return source


def _validate_probe(
    config: B4TSPM1CoordinatorConfig,
    source: object,
) -> B4TSPM1BoundProbe:
    _require(
        type(source) is B4TSPM1BoundProbe,
        S2FS_INPUT_BINDING_INVALID,
        "one exact bound probe is required",
    )
    auditory_values, visual_values, av_values, values_digest = _bound_values(
        source.auditory,
        source.visual,
    )
    _require(
        source.config_digest == config.config_digest
        and source.tspm_probe.config_binding_digest
        == config.tspm_config.config_binding_digest
        and source.tspm_probe.envelope is source.envelope
        and source.tspm_probe.auditory is source.auditory
        and source.tspm_probe.visual is source.visual
        and source.auditory_values == auditory_values
        and source.visual_values == visual_values
        and source.av_values == av_values
        and source.values_digest == values_digest
        and source.probe_digest
        == _digest(
            _source_payload(
                source.config_digest,
                source.envelope.envelope_digest,
                source.auditory.timed_frame_provenance_digest,
                source.visual.timed_frame_provenance_digest,
                source.tspm_probe.probe_digest,
                source.values_digest,
                role="READ_ONLY",
            )
        ),
        S2FS_INPUT_BINDING_INVALID,
        "bound probe config or digest changed",
    )
    tspm1._validate_bound_source_provenance(config.tspm_config, source.tspm_probe)
    tspm1._validate_bound_source_geometry(config.tspm_config, source.tspm_probe)
    return source


def _advance_b4_candidate(
    state: comparison._B4State,
    source: B4TSPM1BoundInput,
) -> tuple[comparison._B4State, dict[str, object], tuple[int, int]]:
    return comparison._advance_b4(
        state,
        source.av_values,
        state.accepted_count + 1,
    )


def _advance_tspm_candidate(
    config: B4TSPM1CoordinatorConfig,
    state: tspm1.TSPM1CompositeState,
    source: B4TSPM1BoundInput,
    owner_id: str,
    authorization_id: str,
    consumption_id: str,
) -> tspm1.TSPM1StepResult:
    owner = tspm1.TSPM1CoordinatorOwner(
        f"{owner_id}.tspm",
        f"{authorization_id}.tspm",
        f"{consumption_id}.tspm",
        config.tspm_config.config_binding_digest,
        state.composite_state_digest,
        source.tspm_exposure.exposure_digest,
    )
    return owner.consume_once(config.tspm_config, state, source.tspm_exposure)


def _make_receipt(
    config: B4TSPM1CoordinatorConfig,
    owner_prestate_digest: str,
    source: B4TSPM1BoundInput,
    prestate: B4TSPM1CompositeState,
    b4_event: dict[str, object],
    b4_poststate: comparison._B4State,
    tspm_result: tspm1.TSPM1StepResult,
    ledger: B4TSPM1ResourceLedger,
    poststate: B4TSPM1CompositeState,
) -> B4TSPM1StepReceipt:
    event = b4_event.get("event")
    slot_id = b4_event.get("slot_id")
    _require(
        isinstance(event, str) and isinstance(slot_id, str),
        S2FS_RELATION_MISMATCH,
        "B4 candidate event is incomplete",
    )
    payload = {
        "schema": S2FS_SCHEMA,
        "config_digest": config.config_digest,
        "owner_prestate_digest": owner_prestate_digest,
        "input_digest": source.input_digest,
        "composite_prestate_digest": prestate.state_digest,
        "b4_event": event,
        "b4_slot_id": slot_id,
        "b4_poststate_digest": _b4_digest(b4_poststate),
        "tspm_result_digest": tspm_result.result_digest,
        "tspm_receipt_digest": tspm_result.receipt.receipt_digest,
        "tspm_poststate_digest": tspm_result.poststate.composite_state_digest,
        "resource_ledger_digest": ledger.ledger_digest,
        "composite_poststate_digest": poststate.state_digest,
    }
    return B4TSPM1StepReceipt(
        config.config_digest,
        owner_prestate_digest,
        source.input_digest,
        prestate.state_digest,
        event,
        slot_id,
        payload["b4_poststate_digest"],  # type: ignore[arg-type]
        tspm_result.result_digest,
        tspm_result.receipt.receipt_digest,
        tspm_result.poststate.composite_state_digest,
        ledger.ledger_digest,
        poststate.state_digest,
        _digest(payload),
    )


def _validate_candidates(
    config: B4TSPM1CoordinatorConfig,
    prestate: B4TSPM1CompositeState,
    source: B4TSPM1BoundInput,
    b4_poststate: object,
    b4_event: object,
    b4_native_cost: object,
    tspm_result: object,
) -> tuple[
    comparison._B4State,
    dict[str, object],
    tuple[int, int],
    tspm1.TSPM1StepResult,
]:
    _require(
        type(b4_poststate) is comparison._B4State
        and type(b4_event) is dict
        and type(b4_native_cost) is tuple
        and len(b4_native_cost) == 2
        and all(type(value) is int and value >= 0 for value in b4_native_cost)
        and type(tspm_result) is tspm1.TSPM1StepResult,
        S2FS_RELATION_MISMATCH,
        "candidate types or native cost form are invalid",
    )
    read_only._validate_b4_state(b4_poststate)
    tspm1._validate_step_result_relations(
        config.tspm_config,
        prestate.tspm_state,
        source.tspm_exposure,
        tspm_result,
    )
    _require(
        b4_poststate.accepted_count == prestate.generation + 1
        and tspm_result.poststate.generation == prestate.generation + 1,
        S2FS_RELATION_MISMATCH,
        "candidate generations diverge",
    )
    return b4_poststate, b4_event, b4_native_cost, tspm_result


def _validate_receipt(
    config: B4TSPM1CoordinatorConfig,
    owner_prestate_digest: str,
    source: B4TSPM1BoundInput,
    prestate: B4TSPM1CompositeState,
    b4_event: dict[str, object],
    b4_poststate: comparison._B4State,
    tspm_result: tspm1.TSPM1StepResult,
    ledger: B4TSPM1ResourceLedger,
    poststate: B4TSPM1CompositeState,
    receipt: object,
) -> B4TSPM1StepReceipt:
    _require(
        type(receipt) is B4TSPM1StepReceipt,
        S2FS_RELATION_MISMATCH,
        "one exact step receipt is required",
    )
    expected = _make_receipt(
        config,
        owner_prestate_digest,
        source,
        prestate,
        b4_event,
        b4_poststate,
        tspm_result,
        ledger,
        poststate,
    )
    _require(
        receipt == expected,
        S2FS_RELATION_MISMATCH,
        "step receipt does not match source, candidates, ledger, and poststate",
    )
    return receipt


def _validate_step_result(
    config: B4TSPM1CoordinatorConfig,
    prestate: B4TSPM1CompositeState,
    source: B4TSPM1BoundInput,
    result: object,
) -> B4TSPM1StepResult:
    _require(
        type(result) is B4TSPM1StepResult,
        S2FS_RELATION_MISMATCH,
        "one exact composite step result is required",
    )
    _validate_state(config, result.poststate)
    _require(
        result.receipt.config_digest == config.config_digest
        and result.receipt.input_digest == source.input_digest
        and result.receipt.composite_prestate_digest == prestate.state_digest
        and result.receipt.b4_poststate_digest == _b4_digest(result.poststate.b4_state)
        and result.receipt.tspm_poststate_digest
        == result.poststate.tspm_state.composite_state_digest
        and result.receipt.resource_ledger_digest == result.resource_ledger.ledger_digest
        and result.receipt.composite_poststate_digest == result.poststate.state_digest
        and result.owner_poststate.authorized_config_digest == config.config_digest
        and result.owner_poststate.authorized_prestate_digest == prestate.state_digest
        and result.owner_poststate.authorized_input_digest == source.input_digest,
        S2FS_RELATION_MISMATCH,
        "step result relation is incomplete or manipulated",
    )
    return result


class B4TSPM1CoordinatorOwner:
    """Private authority for exactly one atomic dual-state formation step."""

    def __init__(
        self,
        owner_id: str,
        authorization_id: str,
        consumption_id: str,
        authorized_config_digest: str,
        authorized_prestate_digest: str,
        authorized_input_digest: str,
    ) -> None:
        self._owner_id = _identifier(owner_id, "owner_id")
        self._authorization_id = _identifier(authorization_id, "authorization_id")
        self._consumption_id = _identifier(consumption_id, "consumption_id")
        _require(
            all(
                _valid_digest(value)
                for value in (
                    authorized_config_digest,
                    authorized_prestate_digest,
                    authorized_input_digest,
                )
            ),
            S2FS_OWNER_AUTHORIZATION_MISMATCH,
            "owner requires config, prestate, and input digests",
        )
        self._authorized_config_digest = authorized_config_digest
        self._authorized_prestate_digest = authorized_prestate_digest
        self._authorized_input_digest = authorized_input_digest
        self._status = "AUTHORIZED"
        self._attempt_count = 0
        self._use_count = 0
        self._committed_result_digest: str | None = None
        self._failure_code: str | None = None
        self._failure_digest: str | None = None
        self._lock = Lock()

    def snapshot(self) -> B4TSPM1CoordinatorOwnerSnapshot:
        with self._lock:
            _require(
                self._status != "IN_PROGRESS",
                S2FS_OWNER_BUSY,
                "owner snapshot is unavailable during a step",
            )
            return _snapshot(self)

    def consume_once(
        self,
        config: B4TSPM1CoordinatorConfig,
        prestate: B4TSPM1CompositeState,
        source: B4TSPM1BoundInput,
    ) -> B4TSPM1StepResult:
        if not self._lock.acquire(blocking=False):
            raise S2FSCoordinatorError(S2FS_OWNER_BUSY, "coordinator owner is busy")
        try:
            if self._status in _OWNER_TERMINAL_STATES:
                raise S2FSCoordinatorError(
                    S2FS_OWNER_TERMINAL,
                    f"coordinator owner is terminal: {self._status}",
                )
            owner_prestate_digest = _snapshot(self).owner_state_digest
            self._status = "IN_PROGRESS"
            self._attempt_count = 1
            phase = "PREVALIDATION"
            try:
                binding = _validate_config(config)
                state = _validate_state(binding, prestate)
                bound = _validate_input(binding, source)
                _require(
                    binding.config_digest == self._authorized_config_digest
                    and state.state_digest == self._authorized_prestate_digest
                    and bound.input_digest == self._authorized_input_digest,
                    S2FS_OWNER_AUTHORIZATION_MISMATCH,
                    "owner authorization does not match call inputs",
                )
                tspm1._validate_bound_source_time(
                    state.tspm_state.fast_state,
                    bound.tspm_exposure,
                    strictly_later=True,
                )

                phase = "B4"
                b4_poststate, b4_event, b4_native_cost = _advance_b4_candidate(
                    state.b4_state,
                    bound,
                )
                phase = "TSPM"
                tspm_result = _advance_tspm_candidate(
                    binding,
                    state.tspm_state,
                    bound,
                    self._owner_id,
                    self._authorization_id,
                    self._consumption_id,
                )
                phase = "RELATION"
                b4_poststate, b4_event, b4_native_cost, tspm_result = (
                    _validate_candidates(
                        binding,
                        state,
                        bound,
                        b4_poststate,
                        b4_event,
                        b4_native_cost,
                        tspm_result,
                    )
                )
                ledger = _make_resource_ledger("FORMATION")
                poststate = _make_composite_state(
                    binding,
                    state.generation + 1,
                    state.state_digest,
                    bound.input_digest,
                    b4_poststate,
                    tspm_result.poststate,
                )
                receipt = _make_receipt(
                    binding,
                    owner_prestate_digest,
                    bound,
                    state,
                    b4_event,
                    b4_poststate,
                    tspm_result,
                    ledger,
                    poststate,
                )
                receipt = _validate_receipt(
                    binding,
                    owner_prestate_digest,
                    bound,
                    state,
                    b4_event,
                    b4_poststate,
                    tspm_result,
                    ledger,
                    poststate,
                    receipt,
                )
                owner_projection = {
                    "schema": S2FS_SCHEMA,
                    "owner_id": self._owner_id,
                    "authorization_id": self._authorization_id,
                    "consumption_id": self._consumption_id,
                    "authorized_config_digest": self._authorized_config_digest,
                    "authorized_prestate_digest": self._authorized_prestate_digest,
                    "authorized_input_digest": self._authorized_input_digest,
                    "status": "CONSUMED",
                    "attempt_count": 1,
                    "use_count": 1,
                    "failure_code": None,
                    "failure_digest": None,
                }
                result_payload = {
                    "schema": S2FS_SCHEMA,
                    "poststate_digest": poststate.state_digest,
                    "receipt_digest": receipt.receipt_digest,
                    "resource_ledger_digest": ledger.ledger_digest,
                    "owner_poststate_projection": owner_projection,
                }
                result_digest = _digest(result_payload)
                self._status = "CONSUMED"
                self._use_count = 1
                self._committed_result_digest = result_digest
                result = B4TSPM1StepResult(
                    poststate,
                    receipt,
                    ledger,
                    _snapshot(self),
                    result_digest,
                )
                return _validate_step_result(binding, state, bound, result)
            except Exception as exc:
                if self._status == "CONSUMED":
                    self._status = "IN_PROGRESS"
                    self._use_count = 0
                    self._committed_result_digest = None
                if isinstance(exc, S2FSCoordinatorError):
                    failure_code = exc.code
                elif phase == "B4":
                    failure_code = S2FS_B4_CANDIDATE_FAILED
                elif phase == "TSPM":
                    failure_code = S2FS_TSPM_CANDIDATE_FAILED
                elif phase == "PREVALIDATION":
                    failure_code = S2FS_PRESTATE_INVALID
                else:
                    failure_code = S2FS_RELATION_MISMATCH
                self._status = "FAILED"
                self._use_count = 0
                self._committed_result_digest = None
                self._failure_code = failure_code
                self._failure_digest = _digest(
                    {
                        "schema": S2FS_SCHEMA,
                        "owner_id": self._owner_id,
                        "failure_code": failure_code,
                        "exception_type": type(exc).__name__,
                        "phase": phase,
                    }
                )
                if isinstance(exc, S2FSCoordinatorError):
                    raise
                raise S2FSCoordinatorError(
                    failure_code,
                    f"atomic coordinator stopped during {phase}",
                ) from exc
        finally:
            self._lock.release()


@dataclass(frozen=True, slots=True)
class B4TSPM1ReadOnlyFinding:
    observed_state_digest: str
    probe_digest: str
    roles: tuple[str, str, str]
    b4_recent: read_only.B4ContentFinding
    tspm_fast: read_only.FastSlotObservation | None
    tspm_slow: tuple[read_only.SlowBankFinding, read_only.SlowBankFinding]
    resource_ledger: B4TSPM1ResourceLedger
    prestate_digest: str
    poststate_digest: str
    finding_digest: str
    schema: str = S2FS_SCHEMA

    def __post_init__(self) -> None:
        _require(
            self.schema == S2FS_SCHEMA
            and self.roles == ("B4_RECENT", "TSPM_FAST", "TSPM_SLOW")
            and type(self.b4_recent) is read_only.B4ContentFinding
            and (
                self.tspm_fast is None
                or type(self.tspm_fast) is read_only.FastSlotObservation
            )
            and type(self.tspm_slow) is tuple
            and len(self.tspm_slow) == 2
            and all(type(item) is read_only.SlowBankFinding for item in self.tspm_slow)
            and type(self.resource_ledger) is B4TSPM1ResourceLedger
            and self.resource_ledger.operation == "READ_ONLY"
            and self.prestate_digest == self.poststate_digest
            and self.observed_state_digest == self.prestate_digest
            and self.finding_digest == _digest(self.payload_without_digest()),
            S2FS_READ_ONLY_VIOLATION,
            "read-only finding is incomplete, prioritized, or state-changing",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "observed_state_digest": self.observed_state_digest,
            "probe_digest": self.probe_digest,
            "roles": list(self.roles),
            "b4_recent_prestate_digest": self.b4_recent.prestate_digest,
            "b4_recent_poststate_digest": self.b4_recent.poststate_digest,
            "tspm_fast_slot_digest": (
                self.tspm_fast.slot_digest if self.tspm_fast is not None else None
            ),
            "tspm_slow_bank_digests": [
                item.observed_bank_state_digest for item in self.tspm_slow
            ],
            "resource_ledger_digest": self.resource_ledger.ledger_digest,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
        }


def probe_composite_read_only(
    config: B4TSPM1CoordinatorConfig,
    state: B4TSPM1CompositeState,
    probe: B4TSPM1BoundProbe,
) -> B4TSPM1ReadOnlyFinding:
    binding = _validate_config(config)
    composite = _validate_state(binding, state)
    bound = _validate_probe(binding, probe)
    tspm1._validate_bound_source_time(
        composite.tspm_state.fast_state,
        bound.tspm_probe,
        strictly_later=True,
    )
    before = composite.state_digest
    b4_finding = read_only.probe_b4_content_read_only(
        composite.b4_state,
        bound.av_values,
    )
    tspm_finding = read_only.probe_tspm1_content_read_only(
        binding.tspm_config,
        composite.tspm_state,
        bound.tspm_probe,
    )
    after = composite.state_digest
    _require(
        before == after
        and b4_finding.prestate_digest == b4_finding.poststate_digest
        and tspm_finding.prestate_digest == tspm_finding.poststate_digest,
        S2FS_READ_ONLY_VIOLATION,
        "one read-only arm changed its source state",
    )
    ledger = _make_resource_ledger("READ_ONLY")
    roles = ("B4_RECENT", "TSPM_FAST", "TSPM_SLOW")
    payload = {
        "schema": S2FS_SCHEMA,
        "observed_state_digest": before,
        "probe_digest": bound.probe_digest,
        "roles": list(roles),
        "b4_recent_prestate_digest": b4_finding.prestate_digest,
        "b4_recent_poststate_digest": b4_finding.poststate_digest,
        "tspm_fast_slot_digest": (
            tspm_finding.functional_fast_selected.slot_digest
            if tspm_finding.functional_fast_selected is not None
            else None
        ),
        "tspm_slow_bank_digests": [
            tspm_finding.auditory_slow.observed_bank_state_digest,
            tspm_finding.visual_slow.observed_bank_state_digest,
        ],
        "resource_ledger_digest": ledger.ledger_digest,
        "prestate_digest": before,
        "poststate_digest": after,
    }
    return B4TSPM1ReadOnlyFinding(
        before,
        bound.probe_digest,
        roles,
        b4_finding,
        tspm_finding.functional_fast_selected,
        (tspm_finding.auditory_slow, tspm_finding.visual_slow),
        ledger,
        before,
        after,
        _digest(payload),
    )
