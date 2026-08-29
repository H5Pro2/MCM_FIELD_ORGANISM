"""Independent read-only verifier for private S2-FV result directories.

The verifier imports no recorder, runner, receptor, memory, coordinator,
field, or S2-FU evaluator module. It verifies technical completeness only.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


VERIFIER_SCHEMA = "s2fv.private.result-verifier.v1"
RECORDING_SCHEMA = "s2fv.private.recording.v1"
EVIDENCE_PACKAGE_SCHEMA = "s2fv.private.evidence-package.v1"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_EXPECTED_OPERATION_COUNTS = {
    "RECEPTOR_ANALYSIS": 24,
    "FORMATION": 54,
    "COMPONENT_IDENTITY": 18,
    "SEQUENCE_PROBE": 1,
    "CONTENT_PROBE": 6,
}
_EXPECTED_EVENT_COUNTS = {
    f"{operation}_{phase}": count
    for operation, count in _EXPECTED_OPERATION_COUNTS.items()
    for phase in ("START", "RESULT")
}
_EXPECTED_FILES = {
    "manifest.json",
    "events.jsonl",
    "evidence.json",
    "terminal.json",
    "COMPLETE",
}


@dataclass(frozen=True, slots=True)
class S2FVResultVerificationFinding:
    status: str
    run_id: str | None
    operation_count: int
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
    operation_count: int,
    event_count: int,
    counts: dict[str, int],
    issues: list[str],
) -> S2FVResultVerificationFinding:
    payload = {
        "schema": VERIFIER_SCHEMA,
        "status": status,
        "run_id": run_id,
        "operation_count": operation_count,
        "event_count": event_count,
        "event_counts": dict(sorted(counts.items())),
        "issues": list(issues),
    }
    return S2FVResultVerificationFinding(
        status,
        run_id,
        operation_count,
        event_count,
        tuple(sorted(counts.items())),
        tuple(issues),
        _digest(payload),
    )


def _plan_projection(manifest: dict[str, object]) -> dict[str, object]:
    return {
        key: manifest[key]
        for key in (
            "schema",
            "run_id",
            "experiment_id",
            "source_digests",
            "configuration_digest",
            "fixture_digest",
            "expected_counts",
            "functional_assessment",
        )
        if key in manifest
    }


def verify_s2fv_result(directory: Path) -> S2FVResultVerificationFinding:
    """Verify one completed directory without invoking experiment functions."""

    issues: list[str] = []
    counts = {kind: 0 for kind in _EXPECTED_EVENT_COUNTS}
    operation_count = 0
    event_count = 0
    run_id: str | None = None
    if not isinstance(directory, Path) or not directory.is_dir():
        return _finding(
            "NOT_EVALUABLE",
            None,
            0,
            0,
            counts,
            ["result directory is unavailable"],
        )
    if {path.name for path in directory.iterdir()} != _EXPECTED_FILES:
        issues.append("result file inventory is incomplete or contains unexpected files")
    try:
        manifest = _read_json(directory / "manifest.json")
        evidence = _read_json(directory / "evidence.json")
        terminal = _read_json(directory / "terminal.json")
        marker = _read_json(directory / "COMPLETE")
        if not all(type(item) is dict for item in (manifest, evidence, terminal, marker)):
            raise ValueError("top-level result records must be dictionaries")
        manifest = manifest  # type: ignore[assignment]
        evidence = evidence  # type: ignore[assignment]
        terminal = terminal  # type: ignore[assignment]
        marker = marker  # type: ignore[assignment]
        run_id_value = manifest.get("run_id")
        run_id = run_id_value if isinstance(run_id_value, str) else None
        if manifest.get("schema") != RECORDING_SCHEMA:
            issues.append("manifest schema differs")
        plan_digest = manifest.get("plan_digest")
        if plan_digest != _digest(_plan_projection(manifest)):
            issues.append("plan digest differs")
        expected = manifest.get("expected_counts")
        if type(expected) is not dict:
            issues.append("manifest count binding is absent")
        elif (
            expected.get("receptor_analyses") != 24
            or expected.get("formations") != 54
            or expected.get("component_identities") != 18
            or expected.get("sequence_probes") != 1
            or expected.get("content_probes") != 6
            or expected.get("operations") != 103
            or expected.get("events") != 206
            or expected.get("operation_kinds") != _EXPECTED_OPERATION_COUNTS
            or expected.get("event_kinds") != _EXPECTED_EVENT_COUNTS
        ):
            issues.append("manifest count binding differs")
        if manifest.get("functional_assessment") is not None:
            issues.append("manifest contains functional assessment")

        previous: str | None = None
        pending_start: dict[str, object] | None = None
        seen_operation_ids: set[str] = set()
        formation_sources: dict[int, dict[str, str]] = {}
        identity_steps: set[int] = set()
        content_arms: dict[str, set[str]] = {}
        sequence_result_count = 0
        with (directory / "events.jsonl").open(
            "r", encoding="ascii", newline=""
        ) as handle:
            for line in handle:
                event = json.loads(line)
                if type(event) is not dict:
                    issues.append("event is not a dictionary")
                    break
                kind = event.get("kind")
                payload = event.get("payload")
                if kind not in counts or type(payload) is not dict:
                    issues.append("event kind or payload is invalid")
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
                if not _valid_digest(event_digest) or event_digest != _digest(
                    _without(event, "event_digest")
                ):
                    issues.append("event digest differs")
                    break
                if not isinstance(payload.get("operation_id"), str) or (
                    type(payload.get("operation_index")) is not int
                ):
                    issues.append("operation identity is invalid")
                    break
                if not _valid_digest(payload.get("source_digest")):
                    issues.append("operation source digest is invalid")
                    break
                if kind.endswith("_START"):
                    if pending_start is not None:
                        issues.append("operation start is not followed by its result")
                        break
                    if payload.get("operation_index") != operation_count:
                        issues.append("operation index is discontinuous")
                        break
                    if payload.get("operation_id") in seen_operation_ids:
                        issues.append("operation identity is reused")
                        break
                    seen_operation_ids.add(payload["operation_id"])
                    pending_start = {
                        "kind": kind,
                        "event_digest": event_digest,
                        "operation_id": payload.get("operation_id"),
                        "operation_index": payload.get("operation_index"),
                        "source_digest": payload.get("source_digest"),
                    }
                else:
                    expected_start_kind = f"{kind[:-7]}_START"
                    if (
                        pending_start is None
                        or pending_start["kind"] != expected_start_kind
                        or payload.get("start_event_digest")
                        != pending_start["event_digest"]
                        or payload.get("operation_id")
                        != pending_start["operation_id"]
                        or payload.get("operation_index")
                        != pending_start["operation_index"]
                        or payload.get("source_digest")
                        != pending_start["source_digest"]
                    ):
                        issues.append("START/RESULT operation binding differs")
                        break
                    if kind in {"SEQUENCE_PROBE_RESULT", "CONTENT_PROBE_RESULT"} and (
                        payload.get("prestate_digest")
                        != payload.get("poststate_digest")
                    ):
                        issues.append("read-only probe changed state")
                        break
                    if kind == "FORMATION_RESULT":
                        step = payload.get("step")
                        arm = payload.get("arm")
                        if type(step) is not int or arm not in {"COMPOSITE", "B4", "TSPM1"}:
                            issues.append("formation step or arm is invalid")
                            break
                        formation_sources.setdefault(step, {})[arm] = payload["source_digest"]
                    elif kind == "COMPONENT_IDENTITY_RESULT":
                        step = payload.get("step")
                        if type(step) is not int or payload.get("identity_valid") is not True:
                            issues.append("component identity result is invalid")
                            break
                        identity_steps.add(step)
                    elif kind == "SEQUENCE_PROBE_RESULT":
                        if (
                            payload.get("tspm_sequence_status")
                            != "NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE"
                            or payload.get("automatic_view_selection") is not None
                        ):
                            issues.append("sequence result crosses its view boundary")
                            break
                        sequence_result_count += 1
                    elif kind == "CONTENT_PROBE_RESULT":
                        arm = payload.get("arm")
                        fixture_id = payload.get("probe_fixture_id")
                        if (
                            arm not in {"COMPOSITE", "B4", "TSPM1"}
                            or not isinstance(fixture_id, str)
                            or payload.get("automatic_view_selection") is not None
                        ):
                            issues.append("content result crosses its view boundary")
                            break
                        content_arms.setdefault(fixture_id, set()).add(arm)
                    pending_start = None
                    operation_count += 1
                previous = event_digest
                counts[kind] += 1
                event_count += 1
        if pending_start is not None:
            issues.append("terminal operation has no result")
        if (
            counts != _EXPECTED_EVENT_COUNTS
            or event_count != 206
            or operation_count != 103
        ):
            issues.append("event or operation inventory is incomplete")
        if len(seen_operation_ids) != 103:
            issues.append("operation identity inventory is incomplete")
        if (
            set(formation_sources) != set(range(1, 19))
            or any(
                set(arms) != {"COMPOSITE", "B4", "TSPM1"}
                or len(set(arms.values())) != 1
                for arms in formation_sources.values()
            )
        ):
            issues.append("formation arms do not share one source per step")
        if identity_steps != set(range(1, 19)):
            issues.append("component identity inventory is incomplete")
        if sequence_result_count != 1:
            issues.append("sequence result inventory differs")
        if len(content_arms) != 2 or any(
            arms != {"COMPOSITE", "B4", "TSPM1"}
            for arms in content_arms.values()
        ):
            issues.append("content arm inventory differs")

        if _file_digest(directory / "events.jsonl") != evidence.get(
            "events_file_sha256"
        ):
            issues.append("event file digest differs")
        if (
            evidence.get("schema") != EVIDENCE_PACKAGE_SCHEMA
            or evidence.get("technical_status") != "RECORDED_UNEVALUATED"
            or evidence.get("functional_assessment") is not None
            or evidence.get("observed_event_counts") != _EXPECTED_EVENT_COUNTS
            or evidence.get("event_tail_digest") != previous
            or evidence.get("plan_digest") != plan_digest
        ):
            issues.append("evidence package projection differs")
        if evidence.get("evidence_digest") != _digest(
            _without(evidence, "evidence_digest")
        ):
            issues.append("evidence package digest differs")
        payload = evidence.get("evidence")
        if type(payload) is not dict:
            issues.append("nested evidence payload is invalid")
        elif (
            payload.get("schema") != EVIDENCE_PACKAGE_SCHEMA
            or payload.get("functional_assessment") is not None
            or payload.get("operation_count") != 103
            or payload.get("event_count") != 206
            or payload.get("automatic_view_selection") is not None
            or payload.get("tspm_sequence_status")
            != "NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE"
        ):
            issues.append("nested evidence scope differs")

        if (
            terminal.get("technical_status") != "COMPLETE_RECORDING"
            or terminal.get("event_count") != 206
            or terminal.get("event_tail_digest") != previous
            or terminal.get("plan_digest") != plan_digest
        ):
            issues.append("terminal record is incomplete")
        if terminal.get("terminal_digest") != _digest(
            _without(terminal, "terminal_digest")
        ):
            issues.append("terminal digest differs")
        if terminal.get("manifest_file_sha256") != _file_digest(
            directory / "manifest.json"
        ):
            issues.append("manifest file digest differs")
        if terminal.get("events_file_sha256") != _file_digest(
            directory / "events.jsonl"
        ):
            issues.append("terminal event file digest differs")
        if terminal.get("evidence_file_sha256") != _file_digest(
            directory / "evidence.json"
        ):
            issues.append("terminal evidence file digest differs")
        if terminal.get("evidence_digest") != evidence.get("evidence_digest"):
            issues.append("terminal evidence binding differs")
        if marker.get("terminal_digest") != terminal.get("terminal_digest"):
            issues.append("completion marker terminal binding differs")
        if marker.get("terminal_file_sha256") != _file_digest(
            directory / "terminal.json"
        ):
            issues.append("completion marker file binding differs")
        if any(
            record.get("run_id") != run_id
            for record in (evidence, terminal, marker)
        ):
            issues.append("run identity differs across records")
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        TypeError,
        ValueError,
        KeyError,
    ) as exc:
        issues.append(f"evidence cannot be read completely: {type(exc).__name__}")

    status = "RECORDING_COMPLETE" if not issues else "NOT_EVALUABLE"
    return _finding(status, run_id, operation_count, event_count, counts, issues)
