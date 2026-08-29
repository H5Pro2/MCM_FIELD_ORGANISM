"""Append-only technical recording for the locked private S2-FV runner.

This module records evidence but never imports or evaluates receptor, memory,
coordinator, field, or S2-FU evaluator code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Mapping


RECORDING_SCHEMA = "s2fv.private.recording.v1"
EVIDENCE_PACKAGE_SCHEMA = "s2fv.private.evidence-package.v1"
_RUN_ID = re.compile(r"^[a-z][a-z0-9_.-]*$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_OPERATION_COUNTS = {
    "RECEPTOR_ANALYSIS": 24,
    "FORMATION": 54,
    "COMPONENT_IDENTITY": 18,
    "SEQUENCE_PROBE": 1,
    "CONTENT_PROBE": 6,
}
EXPECTED_EVENT_COUNTS = {
    f"{operation}_{phase}": count
    for operation, count in EXPECTED_OPERATION_COUNTS.items()
    for phase in ("START", "RESULT")
}
EXPECTED_OPERATION_TOTAL = 103
EXPECTED_EVENT_TOTAL = 206


class S2FVRecordingError(RuntimeError):
    """One fail-closed recording boundary violation."""


def _canonical(value: object) -> object:
    if is_dataclass(value):
        return _canonical(asdict(value))
    if isinstance(value, Mapping):
        return {
            str(key): _canonical(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    return value


def _json_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            _canonical(value),
            allow_nan=False,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    except (TypeError, ValueError) as exc:
        raise S2FVRecordingError("recording payload is not canonical JSON") from exc


def digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def file_digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def _publish_new(path: Path, payload: object) -> str:
    partial = path.with_name(f"{path.name}.partial")
    if path.exists() or partial.exists():
        raise S2FVRecordingError(f"publication target already exists: {path.name}")
    raw = _json_bytes(payload) + b"\n"
    with partial.open("xb") as handle:
        if handle.write(raw) != len(raw):
            raise S2FVRecordingError(f"short write: {path.name}")
        handle.flush()
        os.fsync(handle.fileno())
    if path.exists():
        raise S2FVRecordingError(f"publication target appeared: {path.name}")
    os.rename(partial, path)
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class S2FVRecordingPlan:
    run_id: str
    experiment_id: str
    source_digests: tuple[tuple[str, str], ...]
    configuration_digest: str
    fixture_digest: str
    receptor_analysis_count: int = 24
    formation_count: int = 54
    component_identity_count: int = 18
    sequence_probe_count: int = 1
    content_probe_count: int = 6
    operation_count: int = 103
    event_count: int = 206

    def __post_init__(self) -> None:
        if not _RUN_ID.fullmatch(self.run_id) or not _RUN_ID.fullmatch(
            self.experiment_id
        ):
            raise S2FVRecordingError("run and experiment identities are invalid")
        if not _DIGEST.fullmatch(self.configuration_digest) or not _DIGEST.fullmatch(
            self.fixture_digest
        ):
            raise S2FVRecordingError("configuration or fixture digest is invalid")
        sources = tuple(self.source_digests)
        if (
            not sources
            or len({role for role, _ in sources}) != len(sources)
            or any(
                not _RUN_ID.fullmatch(role) or not _DIGEST.fullmatch(value)
                for role, value in sources
            )
        ):
            raise S2FVRecordingError("source digest inventory is invalid")
        object.__setattr__(self, "source_digests", tuple(sorted(sources)))
        observed = (
            self.receptor_analysis_count,
            self.formation_count,
            self.component_identity_count,
            self.sequence_probe_count,
            self.content_probe_count,
            self.operation_count,
            self.event_count,
        )
        if observed != (24, 54, 18, 1, 6, 103, 206):
            raise S2FVRecordingError("recording plan differs from bound S2-FV scope")

    def payload(self) -> dict[str, object]:
        return {
            "schema": RECORDING_SCHEMA,
            "run_id": self.run_id,
            "experiment_id": self.experiment_id,
            "source_digests": dict(self.source_digests),
            "configuration_digest": self.configuration_digest,
            "fixture_digest": self.fixture_digest,
            "expected_counts": {
                "receptor_analyses": self.receptor_analysis_count,
                "formations": self.formation_count,
                "component_identities": self.component_identity_count,
                "sequence_probes": self.sequence_probe_count,
                "content_probes": self.content_probe_count,
                "operations": self.operation_count,
                "events": self.event_count,
                "operation_kinds": EXPECTED_OPERATION_COUNTS,
                "event_kinds": EXPECTED_EVENT_COUNTS,
            },
            "functional_assessment": None,
        }

    def plan_digest(self) -> str:
        return digest(self.payload())


class S2FVAppendOnlyRecorder:
    """Exclusive event journal and non-overwriting completion publication."""

    def __init__(self, output_root: Path, plan: S2FVRecordingPlan) -> None:
        if not isinstance(output_root, Path) or type(plan) is not S2FVRecordingPlan:
            raise S2FVRecordingError("exact output root and recording plan required")
        self.plan = plan
        self.directory = output_root / plan.run_id
        self.directory.mkdir(parents=True, exist_ok=False)
        self._partial_events = self.directory / "events.jsonl.partial"
        self._final_events = self.directory / "events.jsonl"
        self._event_index = 0
        self._previous_digest: str | None = None
        self._counts = {kind: 0 for kind in EXPECTED_EVENT_COUNTS}
        self._terminal = False
        manifest = {
            **plan.payload(),
            "plan_digest": plan.plan_digest(),
            "recording_policy": {
                "append_only": True,
                "overwrite": False,
                "automatic_retry": False,
                "partial_continuation": False,
                "functional_scoring": False,
                "completion_requires_terminal_and_marker": True,
            },
        }
        self.manifest_file_sha256 = _publish_new(
            self.directory / "manifest.json", manifest
        )
        self._handle = self._partial_events.open("xb")

    @property
    def event_count(self) -> int:
        return self._event_index

    @property
    def event_counts(self) -> dict[str, int]:
        return dict(self._counts)

    @property
    def event_tail_digest(self) -> str | None:
        return self._previous_digest

    def emit(self, kind: str, payload: Mapping[str, object]) -> str:
        if self._terminal or self._handle.closed:
            raise S2FVRecordingError("recorder is terminal")
        if kind not in EXPECTED_EVENT_COUNTS:
            raise S2FVRecordingError(f"unregistered event kind: {kind}")
        if type(payload) is not dict:
            raise S2FVRecordingError("event payload must be an exact dictionary")
        if self._counts[kind] >= EXPECTED_EVENT_COUNTS[kind]:
            raise S2FVRecordingError(f"event budget exhausted: {kind}")
        body = {
            "schema": RECORDING_SCHEMA,
            "run_id": self.plan.run_id,
            "plan_digest": self.plan.plan_digest(),
            "index": self._event_index,
            "previous_event_digest": self._previous_digest,
            "kind": kind,
            "payload": payload,
        }
        record = {**body, "event_digest": digest(body)}
        raw = _json_bytes(record) + b"\n"
        if self._handle.write(raw) != len(raw):
            raise S2FVRecordingError("short event write")
        self._handle.flush()
        os.fsync(self._handle.fileno())
        self._previous_digest = record["event_digest"]
        self._event_index += 1
        self._counts[kind] += 1
        return record["event_digest"]

    def finalize(self, evidence_payload: Mapping[str, object]) -> Path:
        if self._terminal or self._handle.closed:
            raise S2FVRecordingError("recorder is terminal")
        if type(evidence_payload) is not dict:
            raise S2FVRecordingError("evidence payload must be an exact dictionary")
        if evidence_payload.get("schema") != EVIDENCE_PACKAGE_SCHEMA:
            raise S2FVRecordingError("evidence package schema differs")
        if evidence_payload.get("functional_assessment") is not None:
            raise S2FVRecordingError("recorder cannot publish functional assessment")
        if (
            self._event_index != EXPECTED_EVENT_TOTAL
            or self._counts != EXPECTED_EVENT_COUNTS
            or self._previous_digest is None
        ):
            raise S2FVRecordingError("incomplete evidence cannot be completed")

        self._handle.flush()
        os.fsync(self._handle.fileno())
        self._handle.close()
        if self._final_events.exists():
            raise S2FVRecordingError("final event file already exists")
        os.rename(self._partial_events, self._final_events)
        events_file_sha256 = file_digest(self._final_events)

        evidence_body = {
            "schema": EVIDENCE_PACKAGE_SCHEMA,
            "run_id": self.plan.run_id,
            "plan_digest": self.plan.plan_digest(),
            "technical_status": "RECORDED_UNEVALUATED",
            "functional_assessment": None,
            "observed_event_counts": self._counts,
            "event_tail_digest": self._previous_digest,
            "events_file_sha256": events_file_sha256,
            "evidence": evidence_payload,
        }
        evidence = {
            **evidence_body,
            "evidence_digest": digest(evidence_body),
        }
        evidence_file_sha256 = _publish_new(
            self.directory / "evidence.json", evidence
        )

        terminal_body = {
            "schema": RECORDING_SCHEMA,
            "run_id": self.plan.run_id,
            "plan_digest": self.plan.plan_digest(),
            "technical_status": "COMPLETE_RECORDING",
            "manifest_file_sha256": self.manifest_file_sha256,
            "events_file_sha256": events_file_sha256,
            "evidence_file_sha256": evidence_file_sha256,
            "evidence_digest": evidence["evidence_digest"],
            "event_tail_digest": self._previous_digest,
            "event_count": self._event_index,
        }
        terminal = {
            **terminal_body,
            "terminal_digest": digest(terminal_body),
        }
        terminal_file_sha256 = _publish_new(
            self.directory / "terminal.json", terminal
        )
        marker = {
            "schema": RECORDING_SCHEMA,
            "run_id": self.plan.run_id,
            "terminal_digest": terminal["terminal_digest"],
            "terminal_file_sha256": terminal_file_sha256,
        }
        _publish_new(self.directory / "COMPLETE", marker)
        self._terminal = True
        return self.directory

    def leave_not_evaluable(self, error_code: str) -> None:
        """Close a partial journal without creating successful completion."""

        if self._terminal:
            return
        if not self._handle.closed:
            self._handle.flush()
            os.fsync(self._handle.fileno())
            self._handle.close()
        failure = {
            "schema": RECORDING_SCHEMA,
            "run_id": self.plan.run_id,
            "plan_digest": self.plan.plan_digest(),
            "technical_status": "NOT_EVALUABLE",
            "error_code": error_code,
            "recorded_event_count": self._event_index,
            "event_tail_digest": self._previous_digest,
            "completion_marker_created": False,
        }
        try:
            _publish_new(self.directory / "NOT_EVALUABLE.json", failure)
        finally:
            self._terminal = True
