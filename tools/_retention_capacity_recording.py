"""Private append-only recording for the retention/capacity experiment.

This module records technical evidence. It does not evaluate memory function and
does not import receptor or memory code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Mapping


RECORDING_SCHEMA = "retention.capacity.private.recording.v1"
_RUN_ID = re.compile(r"^[a-z][a-z0-9_.-]*$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_EVENT_COUNTS = {
    "IMAGE_ANALYSIS_START": 316,
    "IMAGE_ANALYSIS_RESULT": 316,
    "STATE_OPERATION_START": 316,
    "STATE_OPERATION_RESULT": 316,
    "SEQUENCE_STATUS_START": 16,
    "SEQUENCE_STATUS_RESULT": 16,
}
EXPECTED_TOTAL_EVENTS = 1296


class RetentionRecordingError(RuntimeError):
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
        raise RetentionRecordingError("recording payload is not canonical JSON") from exc


def digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def file_digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def _write_new(path: Path, payload: object) -> str:
    raw = _json_bytes(payload) + b"\n"
    with path.open("xb") as handle:
        if handle.write(raw) != len(raw):
            raise RetentionRecordingError(f"short write: {path.name}")
        handle.flush()
        os.fsync(handle.fileno())
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class RecordingPlan:
    run_id: str
    experiment_id: str
    source_digests: tuple[tuple[str, str], ...]
    configuration_digest: str
    exposure_count: int = 146
    content_probe_count: int = 170
    sequence_status_count: int = 16
    image_analysis_count: int = 316
    event_count: int = 1296

    def __post_init__(self) -> None:
        if not _RUN_ID.fullmatch(self.run_id) or not _RUN_ID.fullmatch(self.experiment_id):
            raise RetentionRecordingError("run and experiment identities are invalid")
        if not _DIGEST.fullmatch(self.configuration_digest):
            raise RetentionRecordingError("configuration digest is invalid")
        sources = tuple(self.source_digests)
        if (
            not sources
            or len({role for role, _ in sources}) != len(sources)
            or any(not _RUN_ID.fullmatch(role) or not _DIGEST.fullmatch(value) for role, value in sources)
        ):
            raise RetentionRecordingError("source digest inventory is invalid")
        object.__setattr__(self, "source_digests", tuple(sorted(sources)))
        if (
            self.exposure_count,
            self.content_probe_count,
            self.sequence_status_count,
            self.image_analysis_count,
            self.event_count,
        ) != (146, 170, 16, 316, 1296):
            raise RetentionRecordingError("recording plan differs from bound scope")

    def payload(self) -> dict[str, object]:
        return {
            "schema": RECORDING_SCHEMA,
            "run_id": self.run_id,
            "experiment_id": self.experiment_id,
            "source_digests": dict(self.source_digests),
            "configuration_digest": self.configuration_digest,
            "expected_counts": {
                "exposures": self.exposure_count,
                "content_probes": self.content_probe_count,
                "sequence_statuses": self.sequence_status_count,
                "image_analyses": self.image_analysis_count,
                "events": self.event_count,
                "event_kinds": EXPECTED_EVENT_COUNTS,
            },
            "functional_assessment": None,
        }

    def plan_digest(self) -> str:
        return digest(self.payload())


class PrivateEvidenceRecorder:
    """Exclusive append-only journal with a terminal completion marker."""

    def __init__(self, output_root: Path, plan: RecordingPlan) -> None:
        if not isinstance(output_root, Path) or type(plan) is not RecordingPlan:
            raise RetentionRecordingError("exact output root and recording plan required")
        self.plan = plan
        self.directory = output_root / plan.run_id
        self.directory.mkdir(parents=True, exist_ok=False)
        self._partial_events = self.directory / "events.jsonl.partial"
        self._final_events = self.directory / "events.jsonl"
        self._handle = self._partial_events.open("xb")
        self._index = 0
        self._previous_digest: str | None = None
        self._counts = {kind: 0 for kind in EXPECTED_EVENT_COUNTS}
        self._terminal = False
        manifest = {
            **plan.payload(),
            "plan_digest": plan.plan_digest(),
            "recording_policy": {
                "overwrite": False,
                "automatic_retry": False,
                "partial_continuation": False,
                "functional_scoring": False,
                "completion_requires_marker": True,
            },
        }
        self.manifest_file_sha256 = _write_new(self.directory / "manifest.json", manifest)

    @property
    def event_count(self) -> int:
        return self._index

    @property
    def event_counts(self) -> dict[str, int]:
        return dict(self._counts)

    @property
    def event_tail_digest(self) -> str | None:
        return self._previous_digest

    def emit(self, kind: str, payload: Mapping[str, object]) -> str:
        if self._terminal or self._handle.closed:
            raise RetentionRecordingError("recorder is terminal")
        if kind not in EXPECTED_EVENT_COUNTS:
            raise RetentionRecordingError(f"unregistered event kind: {kind}")
        if type(payload) is not dict:
            raise RetentionRecordingError("event payload must be an exact dictionary")
        if self._counts[kind] >= EXPECTED_EVENT_COUNTS[kind]:
            raise RetentionRecordingError(f"event budget exhausted: {kind}")
        body = {
            "schema": RECORDING_SCHEMA,
            "run_id": self.plan.run_id,
            "plan_digest": self.plan.plan_digest(),
            "index": self._index,
            "previous_event_digest": self._previous_digest,
            "kind": kind,
            "payload": payload,
        }
        record = {**body, "event_digest": digest(body)}
        raw = _json_bytes(record) + b"\n"
        if self._handle.write(raw) != len(raw):
            raise RetentionRecordingError("short event write")
        self._handle.flush()
        os.fsync(self._handle.fileno())
        self._previous_digest = record["event_digest"]
        self._index += 1
        self._counts[kind] += 1
        return record["event_digest"]

    def finalize(self, summary: Mapping[str, object]) -> Path:
        if self._terminal or self._handle.closed:
            raise RetentionRecordingError("recorder is terminal")
        if type(summary) is not dict:
            raise RetentionRecordingError("summary must be an exact dictionary")
        if self._index != EXPECTED_TOTAL_EVENTS or self._counts != EXPECTED_EVENT_COUNTS:
            raise RetentionRecordingError("incomplete evidence cannot be completed")
        if self._previous_digest is None:
            raise RetentionRecordingError("event chain is empty")

        self._handle.flush()
        os.fsync(self._handle.fileno())
        self._handle.close()
        if self._final_events.exists():
            raise RetentionRecordingError("final event file already exists")
        os.rename(self._partial_events, self._final_events)
        events_file_sha256 = file_digest(self._final_events)

        result_body = {
            "schema": RECORDING_SCHEMA,
            "run_id": self.plan.run_id,
            "plan_digest": self.plan.plan_digest(),
            "technical_status": "RECORDED_UNEVALUATED",
            "functional_assessment": None,
            "observed_event_counts": self._counts,
            "event_tail_digest": self._previous_digest,
            "events_file_sha256": events_file_sha256,
            "summary": summary,
        }
        result = {**result_body, "result_digest": digest(result_body)}
        result_file_sha256 = _write_new(self.directory / "result.json", result)

        terminal_body = {
            "schema": RECORDING_SCHEMA,
            "run_id": self.plan.run_id,
            "plan_digest": self.plan.plan_digest(),
            "technical_status": "COMPLETE_RECORDING",
            "manifest_file_sha256": self.manifest_file_sha256,
            "events_file_sha256": events_file_sha256,
            "result_file_sha256": result_file_sha256,
            "result_digest": result["result_digest"],
            "event_tail_digest": self._previous_digest,
            "event_count": self._index,
        }
        terminal = {**terminal_body, "terminal_digest": digest(terminal_body)}
        terminal_file_sha256 = _write_new(self.directory / "terminal.json", terminal)
        marker = {
            "schema": RECORDING_SCHEMA,
            "run_id": self.plan.run_id,
            "terminal_digest": terminal["terminal_digest"],
            "terminal_file_sha256": terminal_file_sha256,
        }
        _write_new(self.directory / "COMPLETE", marker)
        self._terminal = True
        return self.directory

    def leave_not_evaluable(self) -> None:
        """Close a partial journal without manufacturing a completion marker."""

        if not self._handle.closed:
            self._handle.flush()
            os.fsync(self._handle.fileno())
            self._handle.close()
        self._terminal = True
