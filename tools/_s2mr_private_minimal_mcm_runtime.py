"""Thin private runtime over the qualified role-free perception stream."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from threading import Lock
from typing import TypeAlias

from tools import _s2lm_private_role_free_stream_processor as stream
from tools._s2kq_private_partial_cue_retrieval_336 import (
    PartialCueContextHypothesis336V1,
)
from tools._s2kz_private_auditory_partial_cue_retrieval_336 import (
    AuditoryPartialCueHypothesis48V1,
)


S2MR_SCHEMA = "s2mr.private.minimal-mcm-runtime-336.v1"
RUNTIME_STATES = ("OPEN", "CLOSED")
PERCEPTION_STATUSES = ("FIELD_CONTACT_RECORDED", "FIELD_CONTACT_FAILED")
MEMORY_STATUSES = ("FORMATION_COMMITTED", "FORMATION_FAILED", "READ_ONLY_UNCHANGED")
CONTEXT_STATUSES = (
    "NOT_REQUESTED",
    "CONTEXT_CANDIDATE_AVAILABLE",
    "ABSTAIN_INTERNAL_AMBIGUITY",
    "ABSTAIN_INTERNAL_CONFLICT",
    "ABSTAIN_AMBIGUOUS_CONTEXT",
    "ABSTAIN_NO_CONTEXT",
    "ABSTAIN_NO_APPLICABLE_CONTEXT",
    "SCAN_FAILED",
)
ABSTENTION_DECISIONS = CONTEXT_STATUSES[2:-1]
MAX_STEP_BYTES = 65_536
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{7,95}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2MRRuntimeError(ValueError):
    """The runtime configuration, lifecycle, or composition is invalid."""


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()


def _encoded_size(value: object) -> int:
    return len(
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    )


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MRRuntimeError(message)


def _valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


RuntimeHypothesis336V1: TypeAlias = (
    PartialCueContextHypothesis336V1 | AuditoryPartialCueHypothesis48V1
)


@dataclass(frozen=True, slots=True)
class MinimalMCMRuntimeConfig336V1:
    runtime_id: str
    max_event_count: int
    source_binding_digest: str
    component_binding_digest: str
    config_digest: str
    schema: str = S2MR_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "runtime_id": self.runtime_id,
            "max_event_count": self.max_event_count,
            "source_binding_digest": self.source_binding_digest,
            "component_binding_digest": self.component_binding_digest,
        }


def build_minimal_runtime_config(
    *,
    runtime_id: str,
    max_event_count: int,
    source_binding_digest: str,
    component_binding_digest: str,
) -> MinimalMCMRuntimeConfig336V1:
    _require(
        type(runtime_id) is str and _IDENTIFIER.fullmatch(runtime_id) is not None,
        "runtime id differs",
    )
    _require(type(max_event_count) is int and max_event_count > 0, "event budget differs")
    _require(
        _valid_digest(source_binding_digest) and _valid_digest(component_binding_digest),
        "runtime binding digest differs",
    )
    payload = {
        "schema": S2MR_SCHEMA,
        "runtime_id": runtime_id,
        "max_event_count": max_event_count,
        "source_binding_digest": source_binding_digest,
        "component_binding_digest": component_binding_digest,
    }
    return MinimalMCMRuntimeConfig336V1(
        runtime_id,
        max_event_count,
        source_binding_digest,
        component_binding_digest,
        _digest(payload),
    )


def _validate_config(value: object) -> MinimalMCMRuntimeConfig336V1:
    _require(type(value) is MinimalMCMRuntimeConfig336V1, "exact runtime config required")
    assert isinstance(value, MinimalMCMRuntimeConfig336V1)
    _require(value.schema == S2MR_SCHEMA, "runtime config schema differs")
    _require(
        type(value.runtime_id) is str and _IDENTIFIER.fullmatch(value.runtime_id) is not None,
        "runtime id differs",
    )
    _require(type(value.max_event_count) is int and value.max_event_count > 0, "event budget differs")
    _require(
        _valid_digest(value.source_binding_digest)
        and _valid_digest(value.component_binding_digest)
        and value.config_digest == _digest(value.payload_without_digest()),
        "runtime config binding differs",
    )
    return value


@dataclass(frozen=True, slots=True)
class MinimalMCMRuntimeSnapshot336V1:
    runtime_id: str
    status: str
    stream_state_digest: str
    field_state_digest: str
    memory_state_digest: str
    next_ordinal: int
    processed_event_count: int
    field_attempt_count: int
    memory_formation_attempt_count: int
    scan_attempt_count: int
    max_event_count: int
    config_digest: str
    snapshot_digest: str
    schema: str = S2MR_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "snapshot_digest"
        }


@dataclass(frozen=True, slots=True)
class MinimalMCMRuntimeStep336V1:
    event_digest: str
    prestate_digest: str
    poststate_digest: str
    perception_status: str
    memory_status: str
    context_status: str
    field_receipt_digest: str | None
    memory_receipt_digest: str | None
    scan_receipt_digest: str | None
    baseline_receipt_digest: str | None
    error_codes: tuple[str, ...]
    hypothesis: RuntimeHypothesis336V1 | None
    step_digest: str
    schema: str = S2MR_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "event_digest": self.event_digest,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "perception_status": self.perception_status,
            "memory_status": self.memory_status,
            "context_status": self.context_status,
            "field_receipt_digest": self.field_receipt_digest,
            "memory_receipt_digest": self.memory_receipt_digest,
            "scan_receipt_digest": self.scan_receipt_digest,
            "baseline_receipt_digest": self.baseline_receipt_digest,
            "error_codes": list(self.error_codes),
            "hypothesis_digest": None
            if self.hypothesis is None
            else self.hypothesis.hypothesis_digest,
        }


def _validate_hypothesis(
    value: object,
    *,
    event_type: str,
) -> RuntimeHypothesis336V1:
    expected = (
        PartialCueContextHypothesis336V1
        if event_type == "PARTIAL_VISUAL_CUE"
        else AuditoryPartialCueHypothesis48V1
    )
    _require(type(value) is expected, "scan hypothesis type differs")
    assert isinstance(
        value,
        (PartialCueContextHypothesis336V1, AuditoryPartialCueHypothesis48V1),
    )
    _require(
        _valid_digest(value.hypothesis_digest)
        and value.hypothesis_digest == _digest(value.payload_without_digest()),
        "scan hypothesis digest differs",
    )
    return value


def _compare_scans(
    result: stream.PerceptionStreamEventResultV1,
    *,
    event_type: str,
) -> tuple[str, RuntimeHypothesis336V1 | None, tuple[str, ...]]:
    if result.primary_scan is None or result.baseline_scan is None:
        return "SCAN_FAILED", None, ("SCAN_RESULT_INCOMPLETE",)
    primary = result.primary_scan
    baseline = result.baseline_scan
    if primary.decision != baseline.decision:
        return "SCAN_FAILED", None, ("SCAN_BASELINE_DECISION_MISMATCH",)
    if (primary.hypothesis is None) != (baseline.hypothesis is None):
        return "SCAN_FAILED", None, ("SCAN_BASELINE_HYPOTHESIS_MISMATCH",)
    if primary.hypothesis is None:
        if primary.decision not in ABSTENTION_DECISIONS:
            return "SCAN_FAILED", None, ("SCAN_DECISION_INVALID",)
        return primary.decision, None, ()

    try:
        primary_hypothesis = _validate_hypothesis(primary.hypothesis, event_type=event_type)
        baseline_hypothesis = _validate_hypothesis(baseline.hypothesis, event_type=event_type)
    except S2MRRuntimeError:
        return "SCAN_FAILED", None, ("SCAN_HYPOTHESIS_INVALID",)
    if primary.decision != "ADMIT_SINGLE_CONTEXT":
        return "SCAN_FAILED", None, ("SCAN_DECISION_INVALID",)
    if primary_hypothesis.payload_without_digest() != baseline_hypothesis.payload_without_digest():
        return "SCAN_FAILED", None, ("SCAN_BASELINE_HYPOTHESIS_MISMATCH",)
    return "CONTEXT_CANDIDATE_AVAILABLE", primary_hypothesis, ()


class MinimalMCMRuntime336:
    """Keep one finite S2-LM stream open across independently owned events."""

    def __init__(
        self,
        *,
        config: MinimalMCMRuntimeConfig336V1,
        processor: stream.RoleFreePerceptionStreamProcessor,
        initial_state: stream.PerceptionStreamStateV1,
    ) -> None:
        self._config = _validate_config(config)
        _require(
            type(processor) is stream.RoleFreePerceptionStreamProcessor,
            "exact stream processor required",
        )
        self._state = stream._validate_stream_state(initial_state)
        _require(self._state.status == "OPEN", "initial stream is closed")
        _require(self._state.processed_event_count == 0, "initial stream is not fresh")
        self._processor = processor
        self._status = "OPEN"
        self._lock = Lock()

    def _snapshot_for(
        self,
        state: stream.PerceptionStreamStateV1,
        *,
        status: str,
    ) -> MinimalMCMRuntimeSnapshot336V1:
        state = stream._validate_stream_state(state)
        _require(status in RUNTIME_STATES, "runtime status differs")
        payload = {
            "schema": S2MR_SCHEMA,
            "runtime_id": self._config.runtime_id,
            "status": status,
            "stream_state_digest": state.state_digest,
            "field_state_digest": state.field_state_digest,
            "memory_state_digest": state.memory_state_digest,
            "next_ordinal": state.next_ordinal,
            "processed_event_count": state.processed_event_count,
            "field_attempt_count": state.field_attempt_count,
            "memory_formation_attempt_count": state.memory_formation_attempt_count,
            "scan_attempt_count": state.scan_attempt_count,
            "max_event_count": self._config.max_event_count,
            "config_digest": self._config.config_digest,
        }
        return MinimalMCMRuntimeSnapshot336V1(
            self._config.runtime_id,
            status,
            state.state_digest,
            state.field_state_digest,
            state.memory_state_digest,
            state.next_ordinal,
            state.processed_event_count,
            state.field_attempt_count,
            state.memory_formation_attempt_count,
            state.scan_attempt_count,
            self._config.max_event_count,
            self._config.config_digest,
            _digest(payload),
        )

    def snapshot(self) -> MinimalMCMRuntimeSnapshot336V1:
        return self._snapshot_for(self._state, status=self._status)

    def close(self) -> MinimalMCMRuntimeSnapshot336V1:
        if not self._lock.acquire(blocking=False):
            raise S2MRRuntimeError("runtime is busy")
        try:
            _require(self._status == "OPEN", "runtime is closed")
            self._status = "CLOSED"
            return self.snapshot()
        finally:
            self._lock.release()

    def process_once(
        self,
        event: stream.PerceptionStreamEvent336V1,
    ) -> MinimalMCMRuntimeStep336V1:
        if not self._lock.acquire(blocking=False):
            raise S2MRRuntimeError("runtime is busy")
        try:
            _require(self._status == "OPEN", "runtime is closed")
            _require(type(event) is stream.PerceptionStreamEvent336V1, "exact stream event required")
            _require(
                event.event_digest == _digest(event.payload_without_digest()),
                "event digest differs",
            )
            _require(event.ordinal == self._state.next_ordinal, "event ordinal differs")
            _require(
                self._state.processed_event_count < self._config.max_event_count,
                "event budget exhausted",
            )

            prestate = self.snapshot()
            owner = stream.PerceptionEventOwner(
                f"s2mr-owner-{event.ordinal:06d}",
                self._state.state_digest,
                event.event_digest,
            )
            result = self._processor.process_once(
                state=self._state,
                event=event,
                owner=owner,
            )
            _require(
                type(result) is stream.PerceptionStreamEventResultV1
                and result.event_digest == event.event_digest
                and result.prestate_digest == self._state.state_digest,
                "stream result binding differs",
            )

            field_status = (
                "FIELD_CONTACT_RECORDED"
                if result.field_result is not None
                else "FIELD_CONTACT_FAILED"
            )
            extra_errors: tuple[str, ...] = ()
            hypothesis: RuntimeHypothesis336V1 | None = None
            if event.event_type == "COMPLETE_AV_PERCEPTION":
                memory_status = (
                    "FORMATION_COMMITTED"
                    if result.memory_result is not None
                    else "FORMATION_FAILED"
                )
                context_status = "NOT_REQUESTED"
                _require(
                    result.primary_scan is None and result.baseline_scan is None,
                    "complete perception unexpectedly scanned memory",
                )
            else:
                _require(result.memory_result is None, "partial cue formed memory")
                _require(
                    result.poststate.memory_state_digest == self._state.memory_state_digest,
                    "partial cue changed memory",
                )
                memory_status = "READ_ONLY_UNCHANGED"
                if any(code in result.error_codes for code in ("PRIMARY_SCAN_FAILED", "BASELINE_SCAN_FAILED")):
                    context_status = "SCAN_FAILED"
                else:
                    context_status, hypothesis, extra_errors = _compare_scans(
                        result,
                        event_type=event.event_type,
                    )

            errors = tuple(result.error_codes) + extra_errors
            poststate = self._snapshot_for(result.poststate, status="OPEN")
            temporary = MinimalMCMRuntimeStep336V1(
                event.event_digest,
                prestate.snapshot_digest,
                poststate.snapshot_digest,
                field_status,
                memory_status,
                context_status,
                None if result.field_result is None else result.field_result.receipt_digest,
                None if result.memory_result is None else result.memory_result.receipt_digest,
                None if result.primary_scan is None else result.primary_scan.receipt_digest,
                None if result.baseline_scan is None else result.baseline_scan.receipt_digest,
                errors,
                hypothesis,
                "",
            )
            payload = temporary.payload_without_digest()
            _require(_encoded_size(payload) < MAX_STEP_BYTES, "runtime step exceeds byte budget")
            step = MinimalMCMRuntimeStep336V1(
                temporary.event_digest,
                temporary.prestate_digest,
                temporary.poststate_digest,
                temporary.perception_status,
                temporary.memory_status,
                temporary.context_status,
                temporary.field_receipt_digest,
                temporary.memory_receipt_digest,
                temporary.scan_receipt_digest,
                temporary.baseline_receipt_digest,
                temporary.error_codes,
                temporary.hypothesis,
                _digest(payload),
            )
            self._state = result.poststate
            return step
        finally:
            self._lock.release()


__all__: tuple[str, ...] = ()
