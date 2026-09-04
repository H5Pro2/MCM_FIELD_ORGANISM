"""Private role-free orchestration for one bounded perception stream."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from threading import Lock
from typing import Callable


S2LM_SCHEMA = "s2lm.role-free-perception-stream.v1"
EVENT_TYPES = (
    "COMPLETE_AV_PERCEPTION",
    "PARTIAL_VISUAL_CUE",
    "PARTIAL_AUDITORY_CUE",
)
OWNER_STATES = ("READY", "PROCESSING", "CONSUMED", "FAILED")
STREAM_STATES = ("OPEN", "CLOSED")
BRANCHES = ("FIELD", "MEMORY")
SCAN_ROLES = ("PRIMARY", "DIRECT_BASELINE")
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{7,95}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2LMStreamError(ValueError):
    """One event, owner, branch result, or stream relation is invalid."""


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


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LMStreamError(message)


def _identifier(value: object, role: str) -> str:
    _require(type(value) is str and _IDENTIFIER.fullmatch(value) is not None, f"{role} differs")
    return value


def _valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


@dataclass(frozen=True, slots=True)
class PerceptionStreamEvent336V1:
    event_id: str
    ordinal: int
    event_type: str
    source_digest: str
    perception_digest: str
    field_projection_digest: str
    operation_projection_digest: str
    field_payload: object
    operation_payload: object
    event_digest: str
    schema: str = S2LM_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "event_id": self.event_id,
            "ordinal": self.ordinal,
            "event_type": self.event_type,
            "source_digest": self.source_digest,
            "perception_digest": self.perception_digest,
            "field_projection_digest": self.field_projection_digest,
            "operation_projection_digest": self.operation_projection_digest,
        }


def build_perception_stream_event(
    *,
    event_id: str,
    ordinal: int,
    event_type: str,
    source_digest: str,
    perception_digest: str,
    field_projection_digest: str,
    operation_projection_digest: str,
    field_payload: object,
    operation_payload: object,
) -> PerceptionStreamEvent336V1:
    _identifier(event_id, "event_id")
    _require(type(ordinal) is int and ordinal > 0, "event ordinal differs")
    _require(event_type in EVENT_TYPES, "event type differs")
    _require(
        all(
            _valid_digest(value)
            for value in (
                source_digest,
                perception_digest,
                field_projection_digest,
                operation_projection_digest,
            )
        ),
        "event digest binding differs",
    )
    _require(field_payload is not None and operation_payload is not None, "event payload is absent")
    _require(
        perception_digest == field_projection_digest == operation_projection_digest,
        "field and operation projections do not share one perception",
    )
    payload = {
        "schema": S2LM_SCHEMA,
        "event_id": event_id,
        "ordinal": ordinal,
        "event_type": event_type,
        "source_digest": source_digest,
        "perception_digest": perception_digest,
        "field_projection_digest": field_projection_digest,
        "operation_projection_digest": operation_projection_digest,
    }
    return PerceptionStreamEvent336V1(
        event_id,
        ordinal,
        event_type,
        source_digest,
        perception_digest,
        field_projection_digest,
        operation_projection_digest,
        field_payload,
        operation_payload,
        _digest(payload),
    )


@dataclass(frozen=True, slots=True)
class PerceptionStreamStateV1:
    stream_id: str
    next_ordinal: int
    status: str
    field_state: object
    field_state_digest: str
    memory_state: object
    memory_state_digest: str
    last_event_digest: str | None
    processed_event_count: int
    field_attempt_count: int
    memory_formation_attempt_count: int
    scan_attempt_count: int
    state_digest: str
    schema: str = S2LM_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "stream_id": self.stream_id,
            "next_ordinal": self.next_ordinal,
            "status": self.status,
            "field_state_digest": self.field_state_digest,
            "memory_state_digest": self.memory_state_digest,
            "last_event_digest": self.last_event_digest,
            "processed_event_count": self.processed_event_count,
            "field_attempt_count": self.field_attempt_count,
            "memory_formation_attempt_count": self.memory_formation_attempt_count,
            "scan_attempt_count": self.scan_attempt_count,
        }


def initial_perception_stream_state(
    *,
    stream_id: str,
    field_state: object,
    field_state_digest: str,
    memory_state: object,
    memory_state_digest: str,
) -> PerceptionStreamStateV1:
    _identifier(stream_id, "stream_id")
    _require(field_state is not None and memory_state is not None, "initial state is absent")
    _require(
        _valid_digest(field_state_digest) and _valid_digest(memory_state_digest),
        "initial state digest differs",
    )
    payload = {
        "schema": S2LM_SCHEMA,
        "stream_id": stream_id,
        "next_ordinal": 1,
        "status": "OPEN",
        "field_state_digest": field_state_digest,
        "memory_state_digest": memory_state_digest,
        "last_event_digest": None,
        "processed_event_count": 0,
        "field_attempt_count": 0,
        "memory_formation_attempt_count": 0,
        "scan_attempt_count": 0,
    }
    return PerceptionStreamStateV1(
        stream_id,
        1,
        "OPEN",
        field_state,
        field_state_digest,
        memory_state,
        memory_state_digest,
        None,
        0,
        0,
        0,
        0,
        _digest(payload),
    )


def _validate_stream_state(value: object) -> PerceptionStreamStateV1:
    _require(type(value) is PerceptionStreamStateV1, "exact stream state required")
    assert isinstance(value, PerceptionStreamStateV1)
    _identifier(value.stream_id, "stream_id")
    _require(value.status in STREAM_STATES, "stream status differs")
    _require(
        type(value.next_ordinal) is int
        and value.next_ordinal == value.processed_event_count + 1
        and all(
            type(item) is int and item >= 0
            for item in (
                value.processed_event_count,
                value.field_attempt_count,
                value.memory_formation_attempt_count,
                value.scan_attempt_count,
            )
        ),
        "stream counters differ",
    )
    _require(
        _valid_digest(value.field_state_digest)
        and _valid_digest(value.memory_state_digest)
        and (value.last_event_digest is None or _valid_digest(value.last_event_digest)),
        "stream digest binding differs",
    )
    _require(value.state_digest == _digest(value.payload_without_digest()), "stream digest differs")
    return value


@dataclass(frozen=True, slots=True)
class PerceptionEventOwnerSnapshotV1:
    owner_id: str
    authorized_stream_digest: str
    authorized_event_digest: str
    status: str
    attempt_count: int
    use_count: int
    failure_codes: tuple[str, ...]
    snapshot_digest: str
    schema: str = S2LM_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "owner_id": self.owner_id,
            "authorized_stream_digest": self.authorized_stream_digest,
            "authorized_event_digest": self.authorized_event_digest,
            "status": self.status,
            "attempt_count": self.attempt_count,
            "use_count": self.use_count,
            "failure_codes": list(self.failure_codes),
        }


class PerceptionEventOwner:
    """One-use authority for exactly one stream event."""

    def __init__(self, owner_id: str, stream_digest: str, event_digest: str) -> None:
        self._owner_id = _identifier(owner_id, "owner_id")
        _require(_valid_digest(stream_digest) and _valid_digest(event_digest), "owner binding differs")
        self._stream_digest = stream_digest
        self._event_digest = event_digest
        self._status = "READY"
        self._attempt_count = 0
        self._use_count = 0
        self._failure_codes: tuple[str, ...] = ()
        self._lock = Lock()

    def snapshot(self) -> PerceptionEventOwnerSnapshotV1:
        payload = {
            "schema": S2LM_SCHEMA,
            "owner_id": self._owner_id,
            "authorized_stream_digest": self._stream_digest,
            "authorized_event_digest": self._event_digest,
            "status": self._status,
            "attempt_count": self._attempt_count,
            "use_count": self._use_count,
            "failure_codes": list(self._failure_codes),
        }
        return PerceptionEventOwnerSnapshotV1(
            self._owner_id,
            self._stream_digest,
            self._event_digest,
            self._status,
            self._attempt_count,
            self._use_count,
            self._failure_codes,
            _digest(payload),
        )

    def _begin(self, state: PerceptionStreamStateV1, event: PerceptionStreamEvent336V1) -> None:
        if not self._lock.acquire(blocking=False):
            raise S2LMStreamError("event owner is busy")
        if self._status != "READY":
            self._lock.release()
            raise S2LMStreamError("event owner is terminal")
        self._attempt_count = 1
        if state.state_digest != self._stream_digest or event.event_digest != self._event_digest:
            self._status = "FAILED"
            self._failure_codes = ("OWNER_BINDING_FAILED",)
            self._lock.release()
            raise S2LMStreamError("event owner binding differs")
        self._status = "PROCESSING"

    def _finish(self, errors: tuple[str, ...]) -> PerceptionEventOwnerSnapshotV1:
        _require(self._status == "PROCESSING", "event owner is not processing")
        self._failure_codes = errors
        self._status = "FAILED" if errors else "CONSUMED"
        self._use_count = 0 if errors else 1
        snapshot = self.snapshot()
        self._lock.release()
        return snapshot


@dataclass(frozen=True, slots=True)
class StreamBranchResultV1:
    branch: str
    input_digest: str
    prestate_digest: str
    poststate: object
    poststate_digest: str
    receipt_digest: str
    schema: str = S2LM_SCHEMA


@dataclass(frozen=True, slots=True)
class StreamScanResultV1:
    scan_role: str
    input_digest: str
    prestate_digest: str
    poststate_digest: str
    decision: str
    hypothesis_digest: str | None
    receipt_digest: str
    schema: str = S2LM_SCHEMA


@dataclass(frozen=True, slots=True)
class PerceptionStreamEventResultV1:
    event_digest: str
    prestate_digest: str
    poststate: PerceptionStreamStateV1
    field_result: StreamBranchResultV1 | None
    memory_result: StreamBranchResultV1 | None
    primary_scan: StreamScanResultV1 | None
    baseline_scan: StreamScanResultV1 | None
    error_codes: tuple[str, ...]
    owner_poststate: PerceptionEventOwnerSnapshotV1
    result_digest: str
    schema: str = S2LM_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "event_digest": self.event_digest,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate.state_digest,
            "field_receipt_digest": None if self.field_result is None else self.field_result.receipt_digest,
            "memory_receipt_digest": None if self.memory_result is None else self.memory_result.receipt_digest,
            "primary_scan_receipt_digest": None if self.primary_scan is None else self.primary_scan.receipt_digest,
            "baseline_scan_receipt_digest": None if self.baseline_scan is None else self.baseline_scan.receipt_digest,
            "error_codes": list(self.error_codes),
            "owner_poststate_digest": self.owner_poststate.snapshot_digest,
        }


FieldAdapter = Callable[[object, PerceptionStreamEvent336V1], StreamBranchResultV1]
MemoryAdapter = Callable[[object, PerceptionStreamEvent336V1], StreamBranchResultV1]
ScanAdapter = Callable[[object, PerceptionStreamEvent336V1], StreamScanResultV1]


@dataclass(frozen=True, slots=True)
class AuditoryCueOperationV1:
    cue: object
    band_plan: object


def build_s2jw_memory_adapter(config: object) -> MemoryAdapter:
    """Bind the existing atomic S2-JW coordinator without changing its mechanics."""

    from tools import _s2jw_profiled_memory_coordinator as memory

    def advance(state: object, event: PerceptionStreamEvent336V1) -> StreamBranchResultV1:
        source = event.operation_payload
        bound = memory.bind_s2jv_coordinator_input(config=config, source=source)
        owner = memory.S2JVFormationOwner(
            f"s2lm-memory-owner-{event.ordinal:06d}",
            f"s2lm-memory-authorize-{event.ordinal:06d}",
            f"s2lm-memory-consume-{event.ordinal:06d}",
            config.config_digest,
            state.state_digest,
            bound.input_digest,
        )
        result = memory.advance_s2jv_atomic(
            config=config,
            prestate=state,
            source=bound,
            owner=owner,
        )
        return StreamBranchResultV1(
            "MEMORY",
            event.operation_projection_digest,
            state.state_digest,
            result.poststate,
            result.poststate.state_digest,
            result.receipt.receipt_digest,
        )

    return advance


def build_s2kq_visual_scan_adapter(config: object, *, baseline: bool) -> ScanAdapter:
    """Bind the qualified visual production scan or its independent baseline."""

    from tools import _s2kq_private_direct_slot_scan_baseline as direct
    from tools import _s2kq_private_partial_cue_retrieval_336 as production

    def scan(state: object, event: PerceptionStreamEvent336V1) -> StreamScanResultV1:
        function = (
            direct.form_direct_partial_cue_slot_scan_baseline_336
            if baseline
            else production.form_partial_cue_retrieval_336
        )
        result = function(config=config, state=state, cue=event.operation_payload)
        return StreamScanResultV1(
            "DIRECT_BASELINE" if baseline else "PRIMARY",
            event.operation_projection_digest,
            result.prestate_digest,
            result.poststate_digest,
            result.decision,
            None if result.hypothesis is None else result.hypothesis.hypothesis_digest,
            result.result_digest,
        )

    return scan


def build_s2kz_auditory_scan_adapter(config: object, *, baseline: bool) -> ScanAdapter:
    """Bind the qualified auditory production scan or its independent baseline."""

    from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as production
    from tools import _s2kz_private_direct_auditory_slot_scan_baseline as direct

    def scan(state: object, event: PerceptionStreamEvent336V1) -> StreamScanResultV1:
        operation = event.operation_payload
        _require(type(operation) is AuditoryCueOperationV1, "auditory cue operation differs")
        function = (
            direct.form_direct_auditory_slot_scan_baseline_336
            if baseline
            else production.form_auditory_partial_cue_retrieval_336
        )
        result = function(
            config=config,
            state=state,
            cue=operation.cue,
            band_plan=operation.band_plan,
        )
        return StreamScanResultV1(
            "DIRECT_BASELINE" if baseline else "PRIMARY",
            event.operation_projection_digest,
            result.prestate_digest,
            result.poststate_digest,
            result.decision,
            None if result.hypothesis is None else result.hypothesis.hypothesis_digest,
            result.result_digest,
        )

    return scan


def _validate_branch(
    value: object,
    *,
    branch: str,
    input_digest: str,
    prestate_digest: str,
) -> StreamBranchResultV1:
    _require(type(value) is StreamBranchResultV1, "exact branch result required")
    assert isinstance(value, StreamBranchResultV1)
    _require(
        value.schema == S2LM_SCHEMA
        and value.branch == branch
        and value.input_digest == input_digest
        and value.prestate_digest == prestate_digest
        and value.poststate is not None
        and _valid_digest(value.poststate_digest)
        and _valid_digest(value.receipt_digest),
        "branch result binding differs",
    )
    return value


def _validate_scan(
    value: object,
    *,
    role: str,
    input_digest: str,
    memory_digest: str,
) -> StreamScanResultV1:
    _require(type(value) is StreamScanResultV1, "exact scan result required")
    assert isinstance(value, StreamScanResultV1)
    _require(
        value.schema == S2LM_SCHEMA
        and value.scan_role == role
        and value.input_digest == input_digest
        and value.prestate_digest == memory_digest
        and value.poststate_digest == memory_digest
        and type(value.decision) is str
        and bool(value.decision)
        and (value.hypothesis_digest is None or _valid_digest(value.hypothesis_digest))
        and _valid_digest(value.receipt_digest),
        "scan result or read-only binding differs",
    )
    return value


class RoleFreePerceptionStreamProcessor:
    """Route one event while keeping field and memory failures isolated."""

    def __init__(
        self,
        *,
        field_adapter: FieldAdapter,
        memory_adapter: MemoryAdapter,
        visual_scan: ScanAdapter,
        visual_baseline: ScanAdapter,
        auditory_scan: ScanAdapter,
        auditory_baseline: ScanAdapter,
    ) -> None:
        adapters = (
            field_adapter,
            memory_adapter,
            visual_scan,
            visual_baseline,
            auditory_scan,
            auditory_baseline,
        )
        _require(all(callable(item) for item in adapters), "stream adapters must be callable")
        self._field = field_adapter
        self._memory = memory_adapter
        self._visual_scan = visual_scan
        self._visual_baseline = visual_baseline
        self._auditory_scan = auditory_scan
        self._auditory_baseline = auditory_baseline

    def process_once(
        self,
        *,
        state: PerceptionStreamStateV1,
        event: PerceptionStreamEvent336V1,
        owner: PerceptionEventOwner,
    ) -> PerceptionStreamEventResultV1:
        state = _validate_stream_state(state)
        _require(state.status == "OPEN", "stream is closed")
        _require(type(event) is PerceptionStreamEvent336V1, "exact stream event required")
        _require(event.event_digest == _digest(event.payload_without_digest()), "event digest differs")
        _require(event.ordinal == state.next_ordinal, "event ordinal differs from stream")
        _require(type(owner) is PerceptionEventOwner, "exact event owner required")
        owner._begin(state, event)

        errors: list[str] = []
        field_result = None
        memory_result = None
        primary_scan = None
        baseline_scan = None

        try:
            try:
                field_result = _validate_branch(
                    self._field(state.field_state, event),
                    branch="FIELD",
                    input_digest=event.field_projection_digest,
                    prestate_digest=state.field_state_digest,
                )
            except Exception:
                errors.append("FIELD_BRANCH_FAILED")

            if event.event_type == "COMPLETE_AV_PERCEPTION":
                try:
                    memory_result = _validate_branch(
                        self._memory(state.memory_state, event),
                        branch="MEMORY",
                        input_digest=event.operation_projection_digest,
                        prestate_digest=state.memory_state_digest,
                    )
                except Exception:
                    errors.append("MEMORY_BRANCH_FAILED")
            else:
                scan = self._visual_scan if event.event_type == "PARTIAL_VISUAL_CUE" else self._auditory_scan
                baseline = (
                    self._visual_baseline
                    if event.event_type == "PARTIAL_VISUAL_CUE"
                    else self._auditory_baseline
                )
                try:
                    primary_scan = _validate_scan(
                        scan(state.memory_state, event),
                        role="PRIMARY",
                        input_digest=event.operation_projection_digest,
                        memory_digest=state.memory_state_digest,
                    )
                except Exception:
                    errors.append("PRIMARY_SCAN_FAILED")
                try:
                    baseline_scan = _validate_scan(
                        baseline(state.memory_state, event),
                        role="DIRECT_BASELINE",
                        input_digest=event.operation_projection_digest,
                        memory_digest=state.memory_state_digest,
                    )
                except Exception:
                    errors.append("BASELINE_SCAN_FAILED")

            next_payload = {
                "schema": S2LM_SCHEMA,
                "stream_id": state.stream_id,
                "next_ordinal": state.next_ordinal + 1,
                "status": "OPEN",
                "field_state_digest": (
                    state.field_state_digest if field_result is None else field_result.poststate_digest
                ),
                "memory_state_digest": (
                    state.memory_state_digest if memory_result is None else memory_result.poststate_digest
                ),
                "last_event_digest": event.event_digest,
                "processed_event_count": state.processed_event_count + 1,
                "field_attempt_count": state.field_attempt_count + 1,
                "memory_formation_attempt_count": state.memory_formation_attempt_count
                + (1 if event.event_type == "COMPLETE_AV_PERCEPTION" else 0),
                "scan_attempt_count": state.scan_attempt_count
                + (0 if event.event_type == "COMPLETE_AV_PERCEPTION" else 2),
            }
            poststate = PerceptionStreamStateV1(
                state.stream_id,
                state.next_ordinal + 1,
                "OPEN",
                state.field_state if field_result is None else field_result.poststate,
                next_payload["field_state_digest"],
                state.memory_state if memory_result is None else memory_result.poststate,
                next_payload["memory_state_digest"],
                event.event_digest,
                state.processed_event_count + 1,
                state.field_attempt_count + 1,
                state.memory_formation_attempt_count
                + (1 if event.event_type == "COMPLETE_AV_PERCEPTION" else 0),
                state.scan_attempt_count + (0 if event.event_type == "COMPLETE_AV_PERCEPTION" else 2),
                _digest(next_payload),
            )
            owner_poststate = owner._finish(tuple(errors))
            temporary = PerceptionStreamEventResultV1(
                event.event_digest,
                state.state_digest,
                poststate,
                field_result,
                memory_result,
                primary_scan,
                baseline_scan,
                tuple(errors),
                owner_poststate,
                "",
            )
            return PerceptionStreamEventResultV1(
                event.event_digest,
                state.state_digest,
                poststate,
                field_result,
                memory_result,
                primary_scan,
                baseline_scan,
                tuple(errors),
                owner_poststate,
                _digest(temporary.payload_without_digest()),
            )
        except Exception:
            if owner.snapshot().status == "PROCESSING":
                owner._finish(("PROCESSOR_RELATION_FAILED",))
            raise


__all__: tuple[str, ...] = ()
