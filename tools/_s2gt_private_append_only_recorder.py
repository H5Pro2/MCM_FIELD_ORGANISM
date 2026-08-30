"""Private append-only S2-GT recorder with exclusive terminal paths."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

from tools import _s2gt_private_fixture_registry as fixtures


RECORDER_SCHEMA = "s2gt.private.append-only-recorder.v1"
TERMINAL_STATES = ("COMPLETE", "NOT_EVALUABLE", "START_BLOCKED")
ACTIVE_STATES = ("ACTIVE", "EXECUTION_SEALED", "EVALUATING", "COMPLETING", "FAILING")
_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")


class S2GTRecordingError(RuntimeError):
    """One fail-closed recording error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _canonical_bytes(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def _digest(payload: object) -> str:
    return hashlib.sha256(_canonical_bytes(payload).rstrip(b"\n")).hexdigest()


def _exclusive_json(path: Path, payload: object, maximum: int) -> tuple[str, int]:
    encoded = _canonical_bytes(payload)
    if len(encoded) > maximum:
        raise S2GTRecordingError("E008", "registered resource limit was exceeded")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise S2GTRecordingError("E013", "exclusive artifact publication failed") from error
    return hashlib.sha256(encoded).hexdigest(), len(encoded)


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    run_id: str
    owner_id: str
    fixture_digest: str
    registry_bundle_digest: str
    source_digests: tuple[tuple[str, str], ...]
    operation_count: int
    event_count: int
    maximum_success_bytes: int
    maximum_run_bytes: int
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
        if _RUN_ID.fullmatch(run_id) is None or _RUN_ID.fullmatch(owner_id) is None:
            raise S2GTRecordingError("E003", "run owner binding is invalid")
        payload = {
            "schema": RECORDER_SCHEMA,
            "run_id": run_id,
            "owner_id": owner_id,
            "fixture_digest": fixtures.FIXTURE_SET_DIGEST,
            "registry_bundle_digest": registry.bundle_digest,
            "source_digests": source_digests,
            "operation_count": fixtures.SUCCESS_OPERATION_COUNT,
            "event_count": fixtures.SUCCESS_EVENT_COUNT,
            "maximum_success_bytes": fixtures.MAX_SUCCESS_PATH_BYTES,
            "maximum_run_bytes": fixtures.MAX_RUN_PATH_BYTES,
        }
        return cls(run_id, owner_id, fixtures.FIXTURE_SET_DIGEST, registry.bundle_digest, source_digests, 139, 278, fixtures.MAX_SUCCESS_PATH_BYTES, fixtures.MAX_RUN_PATH_BYTES, _digest(payload))

    def payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "run_id": self.run_id,
            "owner_id": self.owner_id,
            "fixture_digest": self.fixture_digest,
            "registry_bundle_digest": self.registry_bundle_digest,
            "source_digests": self.source_digests,
            "operation_count": self.operation_count,
            "event_count": self.event_count,
            "maximum_success_bytes": self.maximum_success_bytes,
            "maximum_run_bytes": self.maximum_run_bytes,
            "plan_digest": self.plan_digest,
        }


@dataclass(frozen=True, slots=True)
class StartBlocked:
    run_id: str
    owner_id: str
    error_code: str
    status: str = "START_BLOCKED"


class AppendOnlyRunRecorder:
    """Records one registry-ordered run; it never invokes project functions."""

    def __init__(self, run_directory: Path, plan: ExecutionPlan, registry: fixtures.RegistryBundle, reservation_digest: str) -> None:
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
        if type(output_root) is not Path or not output_root.is_absolute():
            return StartBlocked(plan.run_id, plan.owner_id, "E001")
        run_directory = output_root / plan.run_id
        try:
            run_directory.mkdir(parents=False, exist_ok=False)
        except (FileExistsError, FileNotFoundError, PermissionError):
            return StartBlocked(plan.run_id, plan.owner_id, "E001")
        reservation_payload = {
            "schema": RECORDER_SCHEMA,
            "run_id": plan.run_id,
            "owner_id": plan.owner_id,
            "plan_digest": plan.plan_digest,
            "registry_bundle_digest": registry.bundle_digest,
            "state": "ACTIVE",
        }
        reservation_digest = _digest(reservation_payload)
        reservation_payload["reservation_digest"] = reservation_digest
        recorder = cls(run_directory, plan, registry, reservation_digest)
        try:
            (run_directory / "journal").mkdir(exist_ok=False)
            (run_directory / "receipts").mkdir(exist_ok=False)
            (run_directory / "evidence").mkdir(exist_ok=False)
            (run_directory / "evaluation").mkdir(exist_ok=False)
            (run_directory / "terminal" / "complete").mkdir(parents=True, exist_ok=False)
            (run_directory / "terminal" / "failure").mkdir(parents=True, exist_ok=False)
            row = registry.operation_rows[0]
            start_digest = recorder._append_event(
                "START",
                row,
                {"plan_digest": plan.plan_digest, "reservation_digest": reservation_digest},
            )
            recorder.pending_start = ("op-0001", start_digest)
            digest_a, bytes_a = _exclusive_json(run_directory / "reservation.json", reservation_payload, 8_192)
            digest_b, bytes_b = _exclusive_json(run_directory / "manifest.json", plan.payload(), 12_288)
            result_digest = recorder._append_event(
                "RESULT",
                row,
                {
                    "start_event_digest": start_digest,
                    "reservation_artifact_digest": digest_a,
                    "manifest_artifact_digest": digest_b,
                    "artifact_bytes": bytes_a + bytes_b,
                },
            )
            recorder.byte_count += bytes_a + bytes_b
            recorder.result_digests["reservation"] = digest_a
            recorder.result_digests["manifest"] = digest_b
            recorder.result_digests["op-0001"] = result_digest
            recorder.pending_start = None
            recorder.next_operation_index = 2
        except Exception:
            recorder.state = "FAILING"
            try:
                recorder.state = "ACTIVE"
                recorder.fail("E013", "op-0001")
            except Exception as error:
                raise S2GTRecordingError(
                    "E013",
                    "post-reservation failure could not be closed",
                ) from error
        return recorder

    def _row(self) -> dict[str, str]:
        if self.next_operation_index > len(self.registry.operation_rows):
            raise S2GTRecordingError("E002", "operation registry binding is invalid")
        return self.registry.operation_rows[self.next_operation_index - 1]

    def _append_event(self, phase: str, row: dict[str, str], payload: dict[str, object]) -> str:
        event = {
            "schema": RECORDER_SCHEMA,
            "event_index": self.event_count + 1,
            "phase": phase,
            "operation_id": row["operation_id"],
            "operation_index": int(row["index"]),
            "operation_class": row["operation_class"],
            "owner_id": self.plan.owner_id,
            "reservation_digest": self.reservation_digest,
            "previous_event_digest": self.previous_event_digest,
            "payload": payload,
        }
        event_digest = _digest(event)
        event["event_digest"] = event_digest
        encoded = _canonical_bytes(event)
        if len(encoded) > 4_096:
            raise S2GTRecordingError("E008", "registered resource limit was exceeded")
        with self._journal_path.open("ab") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        self.event_count += 1
        self.byte_count += len(encoded)
        self.previous_event_digest = event_digest
        if self.byte_count > fixtures.MAX_RUN_PATH_BYTES:
            raise S2GTRecordingError("E008", "registered resource limit was exceeded")
        return event_digest

    def start(self, operation_id: str, payload: dict[str, object]) -> str:
        if self.state in TERMINAL_STATES or self.pending_start is not None:
            raise S2GTRecordingError("E014", "terminal state transition is invalid")
        row = self._row()
        if operation_id != row["operation_id"] or self.state != row["required_state"]:
            raise S2GTRecordingError("E002", "operation registry binding is invalid")
        digest = self._append_event("START", row, payload)
        self.pending_start = (operation_id, digest)
        return digest

    def finish(self, operation_id: str, artifact: dict[str, object]) -> str:
        row = self._row()
        if self.pending_start is None or self.pending_start[0] != operation_id:
            raise S2GTRecordingError("E009", "operation result is invalid")
        artifact_payload = {
            "schema": RECORDER_SCHEMA,
            "operation_id": operation_id,
            "owner_id": self.plan.owner_id,
            "reservation_digest": self.reservation_digest,
            "start_event_digest": self.pending_start[1],
            "artifact": artifact,
        }
        target = self.run_directory / row["target_path"].split("|")[0]
        artifact_digest, artifact_bytes = _exclusive_json(target, artifact_payload, int(row["output_max_bytes"]))
        result_event_digest = self._append_event("RESULT", row, {"artifact_digest": artifact_digest, "artifact_bytes": artifact_bytes})
        self.byte_count += artifact_bytes
        self.result_digests[operation_id] = artifact_digest
        self.state = row["success_state"]
        self.pending_start = None
        self.next_operation_index += 1
        return result_event_digest

    def fail(self, error_code: str, failed_operation_id: str) -> None:
        """Publish exactly one registered three-operation failure closure."""

        if self.state in TERMINAL_STATES:
            raise S2GTRecordingError("E014", "terminal state transition is invalid")
        allowed = {row["error_code"]: row for row in self.registry.error_code_rows}
        if error_code not in allowed or error_code == "E001":
            raise S2GTRecordingError("E002", "operation registry binding is invalid")
        error_row = allowed[error_code]
        if self.state not in error_row["allowed_phase"].split("|"):
            raise S2GTRecordingError("E002", "error phase binding is invalid")
        current_row = self._row()
        if current_row["operation_id"] != failed_operation_id:
            raise S2GTRecordingError("E002", "failed operation binding is invalid")
        failure_paths = tuple(
            row
            for row in self.registry.failure_path_rows
            if row["failed_operation"] == failed_operation_id
            and row["allowed_phase"] != "PRE_RESERVATION"
        )
        if len(failure_paths) != 1:
            raise S2GTRecordingError("E002", "failure path binding is invalid")
        failure_path_id = failure_paths[0]["failure_path_id"]
        if self.pending_start is None:
            start_digest = self._append_event(
                "START",
                current_row,
                {"failure_path_id": failure_path_id, "precheck_failed": True},
            )
            self.pending_start = (failed_operation_id, start_digest)
        if self.pending_start[0] != failed_operation_id:
            raise S2GTRecordingError("E002", "failed START binding is invalid")
        self._append_event(
            "RESULT",
            current_row,
            {
                "start_event_digest": self.pending_start[1],
                "status": "FAILED",
                "error_code": error_code,
                "failure_path_id": failure_path_id,
                "artifact_published": False,
            },
        )
        self.pending_start = None
        self.state = "FAILING"
        last_digest = self.previous_event_digest
        partial_digest = _digest({"results": sorted(self.result_digests.items()), "last_event_digest": last_digest})
        payloads = (
            {"error_code": error_code, "failure_path_id": failure_path_id, "failed_operation_id": failed_operation_id, "last_event_digest": last_digest, "partial_state_digest": partial_digest},
            {"error_code": error_code, "status": "NOT_EVALUABLE", "failure_receipt_digest": "bound-by-prior-result"},
            {"status": "NOT_EVALUABLE", "failure_terminal_digest": "bound-by-prior-result"},
        )
        for index, (row, payload) in enumerate(zip(self.registry.failure_operation_rows, payloads), 1):
            synthetic = {
                "operation_id": row["operation_id"],
                "index": str(index),
                "operation_class": row["operation_class"],
                "required_state": "FAILING",
                "success_state": row["success_state"],
                "target_path": row["target_path"],
                "output_max_bytes": row["output_max_bytes"],
            }
            self._append_event("START", synthetic, payload)
            target = self.run_directory / row["target_path"]
            artifact_digest, artifact_bytes = _exclusive_json(target, payload, int(row["output_max_bytes"]))
            self._append_event("RESULT", synthetic, {"artifact_digest": artifact_digest, "artifact_bytes": artifact_bytes})
            self.byte_count += artifact_bytes
            self.state = row["success_state"]
        if self.state != "NOT_EVALUABLE":
            raise S2GTRecordingError("E014", "terminal state transition is invalid")


__all__: tuple[str, ...] = ()
