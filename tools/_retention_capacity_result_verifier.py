"""Read-only verifier for retention/capacity result directories.

The verifier intentionally imports no receptor, B4, TSPM-1, or PPB-1 code.
It validates recording completeness and integrity, not functional success.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


VERIFIER_SCHEMA = "retention.capacity.private.result-verifier.v1"
RECORDING_SCHEMA = "retention.capacity.private.recording.v1"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_EXPECTED_EVENT_COUNTS = {
    "IMAGE_ANALYSIS_START": 316,
    "IMAGE_ANALYSIS_RESULT": 316,
    "STATE_OPERATION_START": 316,
    "STATE_OPERATION_RESULT": 316,
    "SEQUENCE_STATUS_START": 16,
    "SEQUENCE_STATUS_RESULT": 16,
}
_EXPECTED_FILES = {"manifest.json", "events.jsonl", "result.json", "terminal.json", "COMPLETE"}


@dataclass(frozen=True, slots=True)
class ResultVerificationFinding:
    status: str
    run_id: str | None
    event_count: int
    event_counts: tuple[tuple[str, int], ...]
    issues: tuple[str, ...]
    finding_digest: str
    schema: str = VERIFIER_SCHEMA


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _file_digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def _read_json(path: Path) -> object:
    with path.open("r", encoding="ascii", newline="") as handle:
        return json.load(handle)


def _without(record: dict[str, object], key: str) -> dict[str, object]:
    return {name: value for name, value in record.items() if name != key}


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _finding(
    status: str,
    run_id: str | None,
    event_count: int,
    counts: dict[str, int],
    issues: list[str],
) -> ResultVerificationFinding:
    payload = {
        "schema": VERIFIER_SCHEMA,
        "status": status,
        "run_id": run_id,
        "event_count": event_count,
        "event_counts": dict(sorted(counts.items())),
        "issues": list(issues),
    }
    return ResultVerificationFinding(
        status,
        run_id,
        event_count,
        tuple(sorted(counts.items())),
        tuple(issues),
        _digest(payload),
    )


def verify_recorded_result(directory: Path) -> ResultVerificationFinding:
    """Verify persisted evidence without invoking any experiment operation."""

    issues: list[str] = []
    counts = {kind: 0 for kind in _EXPECTED_EVENT_COUNTS}
    event_count = 0
    run_id: str | None = None
    if not isinstance(directory, Path) or not directory.is_dir():
        return _finding("NOT_EVALUABLE", None, 0, counts, ["result directory is unavailable"])
    if {path.name for path in directory.iterdir()} != _EXPECTED_FILES:
        issues.append("result file inventory is incomplete or contains unexpected files")
    try:
        manifest = _read_json(directory / "manifest.json")
        result = _read_json(directory / "result.json")
        terminal = _read_json(directory / "terminal.json")
        marker = _read_json(directory / "COMPLETE")
        if not all(type(item) is dict for item in (manifest, result, terminal, marker)):
            raise ValueError("top-level result records must be dictionaries")
        manifest = manifest  # type: ignore[assignment]
        result = result  # type: ignore[assignment]
        terminal = terminal  # type: ignore[assignment]
        marker = marker  # type: ignore[assignment]
        run_id_value = manifest.get("run_id")
        run_id = run_id_value if isinstance(run_id_value, str) else None
        if manifest.get("schema") != RECORDING_SCHEMA:
            issues.append("manifest schema differs")
        plan_digest = manifest.get("plan_digest")
        # The manifest adds recording_policy after plan binding, so validate the
        # plan digest against the exact plan projection instead of the full file.
        plan_projection = {
            key: manifest[key]
            for key in (
                "schema",
                "run_id",
                "experiment_id",
                "source_digests",
                "configuration_digest",
                "expected_counts",
                "functional_assessment",
            )
            if key in manifest
        }
        expected_plan = _digest(plan_projection)
        if plan_digest != expected_plan:
            issues.append("plan digest differs")
        expected_counts = manifest.get("expected_counts")
        if type(expected_counts) is not dict or expected_counts.get("events") != 1296:
            issues.append("manifest event budget differs")
        elif expected_counts.get("event_kinds") != _EXPECTED_EVENT_COUNTS:
            issues.append("manifest event-kind budgets differ")

        previous: str | None = None
        with (directory / "events.jsonl").open("r", encoding="ascii", newline="") as handle:
            for line in handle:
                event = json.loads(line)
                if type(event) is not dict:
                    issues.append("event is not a dictionary")
                    break
                kind = event.get("kind")
                if kind not in counts:
                    issues.append("event kind is unregistered")
                    break
                if event.get("index") != event_count:
                    issues.append("event index is discontinuous")
                    break
                if event.get("previous_event_digest") != previous:
                    issues.append("event digest chain is discontinuous")
                    break
                if event.get("run_id") != run_id or event.get("plan_digest") != plan_digest:
                    issues.append("event source binding differs")
                    break
                event_digest = event.get("event_digest")
                if not _valid_digest(event_digest) or event_digest != _digest(_without(event, "event_digest")):
                    issues.append("event digest differs")
                    break
                if kind == "STATE_OPERATION_RESULT":
                    payload = event.get("payload")
                    if type(payload) is not dict:
                        issues.append("state result payload is invalid")
                        break
                    if payload.get("operation") == "CONTENT_PROBE" and (
                        payload.get("prestate_digest") != payload.get("poststate_digest")
                    ):
                        issues.append("read-only probe changed state")
                        break
                previous = event_digest
                counts[kind] += 1
                event_count += 1

        if counts != _EXPECTED_EVENT_COUNTS or event_count != 1296:
            issues.append("event inventory is incomplete")
        if _file_digest(directory / "events.jsonl") != result.get("events_file_sha256"):
            issues.append("event file digest differs")
        if result.get("technical_status") != "RECORDED_UNEVALUATED" or result.get("functional_assessment") is not None:
            issues.append("result improperly evaluates function")
        if result.get("result_digest") != _digest(_without(result, "result_digest")):
            issues.append("result digest differs")
        if result.get("observed_event_counts") != _EXPECTED_EVENT_COUNTS or result.get("event_tail_digest") != previous:
            issues.append("result event projection differs")
        if terminal.get("technical_status") != "COMPLETE_RECORDING" or terminal.get("event_count") != 1296:
            issues.append("terminal record is incomplete")
        if terminal.get("terminal_digest") != _digest(_without(terminal, "terminal_digest")):
            issues.append("terminal digest differs")
        if terminal.get("manifest_file_sha256") != _file_digest(directory / "manifest.json"):
            issues.append("manifest file digest differs")
        if terminal.get("events_file_sha256") != _file_digest(directory / "events.jsonl"):
            issues.append("terminal event file digest differs")
        if terminal.get("result_file_sha256") != _file_digest(directory / "result.json"):
            issues.append("terminal result file digest differs")
        if marker.get("terminal_digest") != terminal.get("terminal_digest"):
            issues.append("completion marker terminal binding differs")
        if marker.get("terminal_file_sha256") != _file_digest(directory / "terminal.json"):
            issues.append("completion marker file binding differs")
        if any(record.get("run_id") != run_id for record in (result, terminal, marker)):
            issues.append("run identity differs across records")
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
        issues.append(f"evidence cannot be read completely: {type(exc).__name__}")

    status = "RECORDING_COMPLETE" if not issues else "NOT_EVALUABLE"
    return _finding(status, run_id, event_count, counts, issues)
