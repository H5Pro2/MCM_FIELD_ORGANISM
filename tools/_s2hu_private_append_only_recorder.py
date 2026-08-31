"""Private append-only recorder for the bounded S2-HS conflict run."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re

from tools import _s2hu_private_fixture_registry as fixtures


RECORDER_SCHEMA = "s2hu.private.append-only-recorder.v1"
_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
TERMINAL_STATES = frozenset({"COMPLETE", "NOT_EVALUABLE", "START_BLOCKED"})


class S2HURecordingError(RuntimeError):
    """One registered fail-closed recording error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("ascii")


def canonical_digest(payload: object) -> str:
    return hashlib.sha256(canonical_bytes(payload).rstrip(b"\n")).hexdigest()


def _write_exclusive(path: Path, payload: object, maximum: int) -> tuple[str, int]:
    encoded = canonical_bytes(payload)
    if len(encoded) > maximum or len(encoded) > fixtures.MAX_INDIVIDUAL_ARTIFACT_BYTES:
        raise S2HURecordingError("HS-E008", "registered resource limit exceeded")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise S2HURecordingError("HS-E010", "exclusive publication failed") from error
    return hashlib.sha256(encoded).hexdigest(), len(encoded)


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    run_id: str
    owner_id: str
    fixture_digest: str
    execution_contract_digest: str
    registry_bundle_digest: str
    source_digests: tuple[tuple[str, str], ...]
    operation_count: int
    event_count: int
    maximum_success_bytes: int
    maximum_failure_bytes: int
    plan_digest: str
    schema: str = RECORDER_SCHEMA

    @classmethod
    def build(
        cls,
        run_id: str,
        owner_id: str,
        registry: fixtures.RegistryBundle,
        source_digests: tuple[tuple[str, str], ...],
    ) -> "ExecutionPlan":
        if (
            not isinstance(run_id, str)
            or not isinstance(owner_id, str)
            or _RUN_ID.fullmatch(run_id) is None
            or _RUN_ID.fullmatch(owner_id) is None
            or type(source_digests) is not tuple
            or not 1 <= len(source_digests) <= fixtures.MAX_SOURCE_DIGESTS
            or any(
                not isinstance(role, str)
                or not isinstance(digest, str)
                or _DIGEST.fullmatch(digest) is None
                for role, digest in source_digests
            )
            or len({role for role, _ in source_digests}) != len(source_digests)
        ):
            raise S2HURecordingError("HS-E003", "execution plan binding is invalid")
        payload = {
            "schema": RECORDER_SCHEMA,
            "run_id": run_id,
            "owner_id": owner_id,
            "fixture_digest": fixtures.EXECUTION_FIXTURE_DIGEST,
            "execution_contract_digest": fixtures.EXECUTION_CONTRACT_DIGEST,
            "registry_bundle_digest": registry.bundle_digest,
            "source_digests": source_digests,
            "operation_count": fixtures.SUCCESS_OPERATION_COUNT,
            "event_count": fixtures.SUCCESS_EVENT_COUNT,
            "maximum_success_bytes": fixtures.MAX_SUCCESS_PATH_BYTES,
            "maximum_failure_bytes": fixtures.MAX_FAILURE_PATH_BYTES,
        }
        return cls(
            run_id,
            owner_id,
            fixtures.EXECUTION_FIXTURE_DIGEST,
            fixtures.EXECUTION_CONTRACT_DIGEST,
            registry.bundle_digest,
            source_digests,
            fixtures.SUCCESS_OPERATION_COUNT,
            fixtures.SUCCESS_EVENT_COUNT,
            fixtures.MAX_SUCCESS_PATH_BYTES,
            fixtures.MAX_FAILURE_PATH_BYTES,
            canonical_digest(payload),
        )

    def payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "run_id": self.run_id,
            "owner_id": self.owner_id,
            "fixture_digest": self.fixture_digest,
            "execution_contract_digest": self.execution_contract_digest,
            "registry_bundle_digest": self.registry_bundle_digest,
            "source_digests": self.source_digests,
            "operation_count": self.operation_count,
            "event_count": self.event_count,
            "maximum_success_bytes": self.maximum_success_bytes,
            "maximum_failure_bytes": self.maximum_failure_bytes,
            "plan_digest": self.plan_digest,
        }


@dataclass(frozen=True, slots=True)
class StartBlocked:
    run_id: str
    owner_id: str
    error_code: str
    status: str = "START_BLOCKED"


class AppendOnlyRunRecorder:
    """Record exactly one registry-ordered run without invoking project logic."""

    def __init__(
        self,
        run_directory: Path,
        plan: ExecutionPlan,
        registry: fixtures.RegistryBundle,
        reservation_digest: str,
    ) -> None:
        self.run_directory = run_directory
        self.plan = plan
        self.registry = registry
        self.reservation_digest = reservation_digest
        self.state = "ACTIVE"
        self.next_operation_index = 1
        self.event_count = 0
        self.byte_count = 0
        self.previous_event_digest = "0" * 64
        self.pending_start: tuple[str, str] | None = None
        self.result_digests: dict[str, str] = {}
        self._journal_path = run_directory / "journal" / "operations.jsonl"

    @classmethod
    def reserve(
        cls,
        output_root: Path,
        plan: ExecutionPlan,
        registry: fixtures.RegistryBundle,
    ) -> "AppendOnlyRunRecorder | StartBlocked":
        if not isinstance(output_root, Path) or not output_root.is_absolute():
            return StartBlocked(plan.run_id, plan.owner_id, "HS-E001")
        run_directory = output_root / plan.run_id
        try:
            run_directory.mkdir(parents=False, exist_ok=False)
        except (FileExistsError, FileNotFoundError, PermissionError):
            return StartBlocked(plan.run_id, plan.owner_id, "HS-E001")
        reservation_core = {
            "schema": RECORDER_SCHEMA,
            "run_id": plan.run_id,
            "owner_id": plan.owner_id,
            "plan_digest": plan.plan_digest,
            "registry_bundle_digest": registry.bundle_digest,
            "state": "ACTIVE",
        }
        reservation_digest = canonical_digest(reservation_core)
        recorder = cls(run_directory, plan, registry, reservation_digest)
        try:
            for path in (
                run_directory / "journal",
                run_directory / "receipts",
                run_directory / "evidence",
                run_directory / "evaluation",
                run_directory / "terminal" / "complete",
                run_directory / "terminal" / "failure",
            ):
                path.mkdir(parents=True, exist_ok=False)
            row = registry.rows[0]
            recorder.start(
                row.operation_id,
                {"plan_digest": plan.plan_digest, "reservation_digest": reservation_digest},
            )
            recorder.finish(
                row.operation_id,
                {
                    "result": {
                        **reservation_core,
                        "reservation_digest": reservation_digest,
                    }
                },
            )
        except Exception as error:
            try:
                recorder.fail("HS-E010", registry.rows[recorder.next_operation_index - 1].operation_id)
            except Exception as close_error:
                raise S2HURecordingError(
                    "HS-E010", "reserved run could not be closed fail-closed"
                ) from close_error
            raise S2HURecordingError("HS-E010", "reservation publication failed") from error
        return recorder

    def current_row(self) -> fixtures.OperationRow:
        if not 1 <= self.next_operation_index <= len(self.registry.rows):
            raise S2HURecordingError("HS-E002", "operation registry exhausted")
        return self.registry.rows[self.next_operation_index - 1]

    def _append_event(
        self,
        phase: str,
        row: fixtures.OperationRow,
        payload: dict[str, object],
    ) -> str:
        event = {
            "schema": RECORDER_SCHEMA,
            "event_index": self.event_count + 1,
            "phase": phase,
            "operation_id": row.operation_id,
            "operation_index": row.index,
            "operation_class": row.operation_class,
            "owner_id": self.plan.owner_id,
            "reservation_digest": self.reservation_digest,
            "previous_event_digest": self.previous_event_digest,
            "payload": payload,
        }
        event_digest = canonical_digest(event)
        event["event_digest"] = event_digest
        encoded = canonical_bytes(event)
        if len(encoded) > fixtures.MAX_EVENT_BYTES:
            raise S2HURecordingError("HS-E008", "event resource limit exceeded")
        with self._journal_path.open("ab") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        self.event_count += 1
        self.byte_count += len(encoded)
        self.previous_event_digest = event_digest
        if self.byte_count > fixtures.MAX_FAILURE_PATH_BYTES:
            raise S2HURecordingError("HS-E008", "run resource limit exceeded")
        return event_digest

    def start(
        self,
        operation_id: str,
        payload: dict[str, object],
        *,
        external_parent_digest: str | None = None,
    ) -> str:
        if self.state in TERMINAL_STATES or self.pending_start is not None:
            raise S2HURecordingError("HS-E012", "terminal or overlapping operation")
        row = self.current_row()
        if operation_id != row.operation_id or self.state != row.required_state:
            raise S2HURecordingError("HS-E002", "operation or state binding differs")
        internal_parents = tuple(
            self.result_digests[parent]
            for parent in row.parent_operations
            if parent.startswith("hs-op-")
        )
        requires_external = "external-evaluation-plan-seal" in row.parent_operations
        if requires_external != (external_parent_digest is not None):
            raise S2HURecordingError("HS-E004", "external evaluation parent differs")
        if external_parent_digest is not None and _DIGEST.fullmatch(external_parent_digest) is None:
            raise S2HURecordingError("HS-E004", "external evaluation digest differs")
        digest = self._append_event(
            "START",
            row,
            {
                "internal_parent_result_digests": internal_parents,
                "external_parent_digest": external_parent_digest,
                "input": payload,
            },
        )
        self.pending_start = (operation_id, digest)
        return digest

    def finish(self, operation_id: str, artifact: dict[str, object]) -> str:
        row = self.current_row()
        if self.pending_start is None or self.pending_start[0] != operation_id:
            raise S2HURecordingError("HS-E007", "result has no matching start")
        envelope = {
            "schema": RECORDER_SCHEMA,
            "operation_id": operation_id,
            "owner_id": self.plan.owner_id,
            "reservation_digest": self.reservation_digest,
            "start_event_digest": self.pending_start[1],
            "artifact": artifact,
        }
        target = self.run_directory / row.target_path
        artifact_digest, artifact_bytes = _write_exclusive(
            target,
            envelope,
            min(row.output_max_bytes, fixtures.MAX_INDIVIDUAL_ARTIFACT_BYTES),
        )
        result_event_digest = self._append_event(
            "RESULT",
            row,
            {"artifact_digest": artifact_digest, "artifact_bytes": artifact_bytes},
        )
        self.byte_count += artifact_bytes
        self.result_digests[operation_id] = artifact_digest
        self.state = row.success_state
        self.pending_start = None
        self.next_operation_index += 1
        return result_event_digest

    def fail(self, error_code: str, failed_operation_id: str) -> None:
        if self.state in TERMINAL_STATES:
            raise S2HURecordingError("HS-E012", "terminal run cannot fail again")
        if error_code not in fixtures.ERROR_CODES:
            error_code = "HS-E009"
        row = self.current_row()
        if row.operation_id != failed_operation_id:
            raise S2HURecordingError("HS-E002", "failed operation differs")
        if self.pending_start is None:
            self.start(failed_operation_id, {"precheck_failed": True})
        self._append_event(
            "RESULT",
            row,
            {"status": "FAILED", "error_code": error_code, "artifact_published": False},
        )
        self.pending_start = None
        self.state = "FAILING"
        partial_digest = canonical_digest(
            {
                "result_digests": sorted(self.result_digests.items()),
                "last_event_digest": self.previous_event_digest,
            }
        )
        synthetic = (
            ("hs-err-001", "failure/receipt.json", "FAILING"),
            ("hs-err-002", "terminal/failure/NOT_EVALUABLE", "NOT_EVALUABLE"),
        )
        for offset, (operation_id, target, success_state) in enumerate(synthetic, 1):
            failure_row = fixtures.OperationRow(
                60 + offset,
                operation_id,
                "FAIL",
                "FAILURE_CLOSE",
                row.history_id,
                row.case_id,
                (row.operation_id,) if offset == 1 else ("hs-err-001",),
                "run_owner",
                "S2HSTerminalFinding",
                target,
                1_024,
                "FAILING",
                success_state,
            )
            start = self._append_event(
                "START",
                failure_row,
                {"error_code": error_code, "failed_operation_id": failed_operation_id},
            )
            payload = {
                "schema": RECORDER_SCHEMA,
                "status": "NOT_EVALUABLE",
                "error_code": error_code,
                "failed_operation_id": failed_operation_id,
                "owner_id": self.plan.owner_id,
                "reservation_digest": self.reservation_digest,
                "partial_state_digest": partial_digest,
                "prior_failure_artifact_digest": self.result_digests.get("hs-err-001"),
            }
            artifact_digest, artifact_bytes = _write_exclusive(
                self.run_directory / target, payload, 1_024
            )
            self._append_event(
                "RESULT",
                failure_row,
                {
                    "start_event_digest": start,
                    "artifact_digest": artifact_digest,
                    "artifact_bytes": artifact_bytes,
                },
            )
            self.byte_count += artifact_bytes
            self.result_digests[operation_id] = artifact_digest
            self.state = success_state
        if self.event_count > fixtures.MAX_FAILURE_EVENT_COUNT:
            raise S2HURecordingError("HS-E008", "failure event limit exceeded")


__all__: tuple[str, ...] = ()
