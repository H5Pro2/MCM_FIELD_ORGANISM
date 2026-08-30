"""Independent stdlib-only read-only verifier for one S2-GT run directory."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import hashlib
import json
from pathlib import Path
import re


VERIFIER_SCHEMA = "s2gt.private.result-verifier.v1"
EXPECTED_REGISTRIES = (
    ("operation", "docs/S2GR_OPERATION_REGISTRY.csv", "8b900da51f6a8921c5231679570f0aa3e188d56b9bd5507f989038a354787d05"),
    ("failure_operation", "docs/S2GR_FAILURE_OPERATION_REGISTRY.csv", "f6d201e3c1f5bd91f244a065ef8e97129f39a829c3c50b74b0a697460793c721"),
    ("error_code", "docs/S2GR_ERROR_CODE_REGISTRY.csv", "a6db907bf9065fd6a7afcf631441c5eda5b8993db01972bb533a8cefa5ac2e09"),
    ("failure_path", "docs/S2GR_FAILURE_PATH_BUDGET_REGISTRY.csv", "fcebc195aeb3ebc51879d9b5eb3657fe59e3f9df6339892ffff1375325597024"),
)
EXPECTED_FIXTURE_DIGEST = "0e9f26180b1f392a10fa727a5f320d2a2f2be1da8dc686cc4f82534a56d3a789"
EXPECTED_SUCCESS_OPERATIONS = 139
EXPECTED_SUCCESS_EVENTS = 278
MAX_SUCCESS_BYTES = 2_009_088
MAX_RUN_BYTES = 2_045_952
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class VerificationFinding:
    status: str
    run_id: str | None
    operation_count: int
    event_count: int
    byte_count: int
    last_event_digest: str | None
    errors: tuple[str, ...]
    finding_digest: str
    schema: str = VERIFIER_SCHEMA


def _canonical(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def _digest(payload: object) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _file_digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(131_072), b""):
            hasher.update(block)
    return hasher.hexdigest()


def _load_json(path: Path) -> object:
    with path.open("r", encoding="ascii") as handle:
        return json.load(handle)


def _registries(workspace_root: Path) -> tuple[tuple[dict[str, str], ...], str]:
    all_rows: dict[str, tuple[dict[str, str], ...]] = {}
    sources: list[tuple[str, str]] = []
    for role, relative_path, expected_digest in EXPECTED_REGISTRIES:
        path = workspace_root / relative_path
        actual_digest = _file_digest(path)
        if actual_digest != expected_digest:
            raise ValueError(f"{role} registry digest differs")
        with path.open("r", encoding="utf-8", newline="") as handle:
            all_rows[role] = tuple(dict(row) for row in csv.DictReader(handle))
        sources.append((role, actual_digest))
    rows = all_rows["operation"]
    if len(rows) != EXPECTED_SUCCESS_OPERATIONS or len(all_rows["failure_operation"]) != 3 or len(all_rows["error_code"]) != 16 or len(all_rows["failure_path"]) != 140:
        raise ValueError("operation registry count differs")
    bundle_payload = {
        "schema": "s2gt.private.functional-run.v1",
        "sources": sources,
        "counts": [139, 278, 140, 16],
        "budgets": [MAX_SUCCESS_BYTES, MAX_RUN_BYTES],
    }
    return rows, _digest(bundle_payload)


def _finding(status: str, run_id: str | None, operation_count: int, event_count: int, byte_count: int, last_event_digest: str | None, errors: list[str]) -> VerificationFinding:
    payload = {
        "schema": VERIFIER_SCHEMA,
        "status": status,
        "run_id": run_id,
        "operation_count": operation_count,
        "event_count": event_count,
        "byte_count": byte_count,
        "last_event_digest": last_event_digest,
        "errors": errors,
    }
    return VerificationFinding(status, run_id, operation_count, event_count, byte_count, last_event_digest, tuple(errors), _digest(payload))


def verify_run_read_only(workspace_root: Path, run_directory: Path) -> VerificationFinding:
    """Verify stored bytes only; no project module or state function is imported."""

    errors: list[str] = []
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute() or not isinstance(run_directory, Path) or not run_directory.is_absolute():
        return _finding("NOT_EVALUABLE", None, 0, 0, 0, None, ["absolute pathlib.Path inputs required"])
    try:
        rows, registry_bundle_digest = _registries(workspace_root)
        manifest = _load_json(run_directory / "manifest.json")
        reservation = _load_json(run_directory / "reservation.json")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return _finding("NOT_EVALUABLE", None, 0, 0, 0, None, [type(error).__name__])

    run_id = manifest.get("run_id") if isinstance(manifest, dict) else None
    if not isinstance(manifest, dict) or not isinstance(reservation, dict):
        return _finding("NOT_EVALUABLE", None, 0, 0, 0, None, ["manifest or reservation shape differs"])
    if "evaluation_plan_digest" in json.dumps(manifest, sort_keys=True) or "evaluation_plan_digest" in json.dumps(reservation, sort_keys=True):
        errors.append("evaluation root leaked into execution preparation")
    if manifest.get("operation_count") != 139 or manifest.get("event_count") != 278:
        errors.append("manifest operation or event count differs")
    unsigned_manifest = dict(manifest)
    supplied_plan_digest = unsigned_manifest.pop("plan_digest", None)
    if supplied_plan_digest != _digest(unsigned_manifest):
        errors.append("execution plan digest differs")
    unsigned_reservation = dict(reservation)
    supplied_reservation_digest = unsigned_reservation.pop("reservation_digest", None)
    if supplied_reservation_digest != _digest(unsigned_reservation):
        errors.append("reservation digest differs")
    if manifest.get("fixture_digest") != EXPECTED_FIXTURE_DIGEST or manifest.get("registry_bundle_digest") != registry_bundle_digest:
        errors.append("fixture or registry bundle binding differs")
    if manifest.get("maximum_success_bytes") != MAX_SUCCESS_BYTES or manifest.get("maximum_run_bytes") != MAX_RUN_BYTES:
        errors.append("manifest budget differs")
    if reservation.get("run_id") != run_id or reservation.get("owner_id") != manifest.get("owner_id"):
        errors.append("reservation owner binding differs")

    for role_path, expected in manifest.get("source_digests", []):
        matches = [path for path in workspace_root.rglob(Path(role_path).name)]
        if len(matches) != 1 or _file_digest(matches[0]) != expected:
            errors.append(f"source digest differs: {role_path}")

    journal = run_directory / "journal/operations.jsonl"
    events: list[dict[str, object]] = []
    try:
        with journal.open("r", encoding="ascii") as handle:
            for line in handle:
                event = json.loads(line)
                if not isinstance(event, dict):
                    raise ValueError
                events.append(event)
    except (OSError, ValueError, json.JSONDecodeError):
        errors.append("event journal is unreadable")

    previous = "0" * 64
    for index, event in enumerate(events, 1):
        supplied = event.get("event_digest")
        unsigned = dict(event)
        unsigned.pop("event_digest", None)
        if event.get("event_index") != index or event.get("previous_event_digest") != previous or supplied != _digest(unsigned):
            errors.append(f"event chain differs at {index}")
            break
        previous = str(supplied)

    complete_path = run_directory / "terminal/complete/COMPLETE"
    failed_path = run_directory / "terminal/failure/NOT_EVALUABLE"
    complete = complete_path.is_file()
    failed = failed_path.is_file()
    if complete == failed:
        errors.append("exactly one terminal path required")

    operation_count = 0
    if complete:
        if len(events) != EXPECTED_SUCCESS_EVENTS:
            errors.append("success event count differs")
        for index, row in enumerate(rows):
            start_position = index * 2
            result_position = start_position + 1
            if result_position >= len(events):
                errors.append(f"missing events for {row['operation_id']}")
                break
            start, result = events[start_position], events[result_position]
            if start.get("phase") != "START" or result.get("phase") != "RESULT" or start.get("operation_id") != row["operation_id"] or result.get("operation_id") != row["operation_id"]:
                errors.append(f"operation event pair differs: {row['operation_id']}")
                break
            operation_count += 1
        if operation_count == 139:
            evaluation_touch = events[262]
            if evaluation_touch.get("operation_id") != "op-0132":
                errors.append("evaluation roots meet before op-0132")
            for event in events[:262]:
                if "evaluation_plan_digest" in json.dumps(event, sort_keys=True):
                    errors.append("evaluation root leaked before op-0132")
                    break

    for event in events:
        if event.get("phase") != "RESULT":
            continue
        payload = event.get("payload")
        if not isinstance(payload, dict):
            errors.append("result payload shape differs")
            continue
        artifact_digest = payload.get("artifact_digest")
        operation_id = event.get("operation_id")
        if not isinstance(operation_id, str) or not operation_id.startswith("op-"):
            continue
        row = rows[int(operation_id[3:]) - 1]
        target = run_directory / row["target_path"].split("|")[0]
        if operation_id == "op-0001":
            continue
        if not target.is_file() or not isinstance(artifact_digest, str) or _file_digest(target) != artifact_digest:
            errors.append(f"artifact binding differs: {operation_id}")

    byte_count = sum(path.stat().st_size for path in run_directory.rglob("*") if path.is_file())
    maximum = MAX_SUCCESS_BYTES if complete else MAX_RUN_BYTES
    if byte_count > maximum:
        errors.append("recorded byte budget exceeded")
    if complete and events and events[-1].get("operation_id") != "op-0139":
        errors.append("completion operation differs")

    status = "RECORDING_COMPLETE" if complete and not errors else "NOT_EVALUABLE"
    return _finding(status, run_id if isinstance(run_id, str) else None, operation_count, len(events), byte_count, previous if events else None, errors)


__all__: tuple[str, ...] = ()
