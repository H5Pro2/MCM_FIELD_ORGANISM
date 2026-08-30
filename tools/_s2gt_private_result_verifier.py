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
COMPACT_RECEPTOR_RECEIPT_SCHEMA = "s2gy.private.compact-receptor-receipt.v1"
COMPACT_RECEPTOR_MAX_ARTIFACT_BYTES = 2_765
RECEPTOR_OPERATION_CLASSES = frozenset(
    {
        "FORMATION_RECEPTOR_ANALYSIS",
        "CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS",
        "CONSUMER_RECEPTOR_ANALYSIS",
    }
)
COMPACT_RECEPTOR_RECEIPT_FIELDS = frozenset(
    {
        "schema",
        "operation_id",
        "operation_index",
        "operation_class",
        "source_role",
        "source_id",
        "history_id",
        "source_ordinal",
        "execution_plan_digest",
        "manifest_artifact_digest",
        "registry_bundle_digest",
        "fixture_set_digest",
        "coordinator_config_digest",
        "visual_fixture_id",
        "auditory_fixture_id",
        "auditory_dimension",
        "visual_dimension",
        "av_dimension",
        "auditory_geometry_id",
        "visual_geometry_id",
        "auditory_snapshot_id",
        "visual_snapshot_id",
        "auditory_source_clock_id",
        "visual_source_clock_id",
        "field_clock_id",
        "source_window_start_tick",
        "source_window_end_tick",
        "field_window_start_tick",
        "field_window_end_tick",
        "raw_image_sha256",
        "raw_payload_retained",
        "auditory_values_digest",
        "visual_values_digest",
        "av_projection_digest",
        "auditory_input_projection_digest",
        "visual_input_projection_digest",
        "auditory_timed_frame_provenance_digest",
        "visual_timed_frame_provenance_digest",
        "envelope_digest",
        "tspm_source_digest",
        "bound_source_digest",
        "source_digest",
    }
)
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


def _registries(
    workspace_root: Path,
) -> tuple[tuple[dict[str, str], ...], tuple[dict[str, str], ...], str]:
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
    return rows, all_rows["error_code"], _digest(bundle_payload)


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


def _validate_compact_receptor_receipt(
    target: Path,
    row: dict[str, str],
    start: dict[str, object],
    result: dict[str, object],
    next_start: dict[str, object] | None,
    manifest: dict[str, object],
    reservation: dict[str, object],
    registry_bundle_digest: str,
) -> list[str]:
    errors: list[str] = []
    try:
        raw = target.read_bytes()
        artifact = json.loads(raw.decode("ascii"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return [f"compact receptor receipt is unreadable: {row['operation_id']}"]
    if (
        not isinstance(artifact, dict)
        or raw != _canonical(artifact) + b"\n"
        or len(raw) > COMPACT_RECEPTOR_MAX_ARTIFACT_BYTES
        or len(raw) >= int(row["output_max_bytes"])
    ):
        errors.append(f"compact receptor artifact encoding differs: {row['operation_id']}")
        return errors
    if set(artifact) != {
        "schema",
        "operation_id",
        "owner_id",
        "reservation_digest",
        "start_event_digest",
        "artifact",
    }:
        errors.append(f"compact receptor artifact envelope differs: {row['operation_id']}")
        return errors
    body = artifact.get("artifact")
    receipt = body.get("result") if isinstance(body, dict) and set(body) == {"result"} else None
    if not isinstance(receipt, dict) or set(receipt) != COMPACT_RECEPTOR_RECEIPT_FIELDS:
        errors.append(f"compact receptor receipt shape differs: {row['operation_id']}")
        return errors

    if (
        artifact.get("schema") != "s2gt.private.append-only-recorder.v1"
        or artifact.get("operation_id") != row["operation_id"]
        or artifact.get("owner_id") != manifest.get("owner_id")
        or artifact.get("reservation_digest") != reservation.get("reservation_digest")
        or artifact.get("start_event_digest") != start.get("event_digest")
    ):
        errors.append(f"compact receptor parent binding differs: {row['operation_id']}")

    operation_class = row["operation_class"]
    if operation_class == "FORMATION_RECEPTOR_ANALYSIS":
        source_role = "FORMATION"
        ordinal = int(row["source_ordinal"])
        expected_source_id = f"s2gt.{row['history']}.formation.{ordinal:02d}"
        expected_window = (ordinal - 1, ordinal)
    elif operation_class == "CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS":
        source_role = "READ_ONLY"
        expected_source_id = f"s2gt.{row['history']}.probe.full.01"
        expected_window = (13, 14)
    else:
        source_role = "READ_ONLY"
        expected_source_id = "s2gt.shared.consumer.01"
        expected_window = (14, 15)
    if (
        receipt.get("schema") != COMPACT_RECEPTOR_RECEIPT_SCHEMA
        or receipt.get("operation_id") != row["operation_id"]
        or receipt.get("operation_index") != int(row["index"])
        or receipt.get("operation_class") != operation_class
        or receipt.get("source_role") != source_role
        or receipt.get("source_id") != expected_source_id
        or receipt.get("history_id") != row["history"]
        or receipt.get("source_ordinal") != row["source_ordinal"]
    ):
        errors.append(f"compact receptor operation binding differs: {row['operation_id']}")
    if (
        receipt.get("execution_plan_digest") != manifest.get("plan_digest")
        or receipt.get("manifest_artifact_digest") != _file_digest(target.parent.parent / "manifest.json")
        or receipt.get("registry_bundle_digest") != registry_bundle_digest
        or receipt.get("fixture_set_digest") != manifest.get("fixture_digest")
    ):
        errors.append(f"compact receptor source root differs: {row['operation_id']}")
    if (
        receipt.get("auditory_dimension") != 8
        or receipt.get("visual_dimension") != 18
        or receipt.get("av_dimension") != 26
        or receipt.get("auditory_geometry_id") != "auditory.log8.50-3000.w800.h80.v1"
        or receipt.get("visual_geometry_id") != "visual.grid3x2.channels3.source120x80.v1"
        or receipt.get("auditory_snapshot_id") != expected_source_id + ".auditory"
        or receipt.get("visual_snapshot_id") != expected_source_id + ".visual"
        or receipt.get("auditory_source_clock_id") != "s2gt.auditory.clock"
        or receipt.get("visual_source_clock_id") != "s2gt.visual.clock"
        or receipt.get("field_clock_id") != "s2gt.field.clock"
        or (
            receipt.get("source_window_start_tick"),
            receipt.get("source_window_end_tick"),
        )
        != expected_window
        or (
            receipt.get("field_window_start_tick"),
            receipt.get("field_window_end_tick"),
        )
        != expected_window
        or receipt.get("raw_payload_retained") is not False
    ):
        errors.append(f"compact receptor anatomy differs: {row['operation_id']}")
    digest_fields = COMPACT_RECEPTOR_RECEIPT_FIELDS - {
        "schema",
        "operation_id",
        "operation_index",
        "operation_class",
        "source_role",
        "source_id",
        "history_id",
        "source_ordinal",
        "visual_fixture_id",
        "auditory_fixture_id",
        "auditory_dimension",
        "visual_dimension",
        "av_dimension",
        "auditory_geometry_id",
        "visual_geometry_id",
        "auditory_snapshot_id",
        "visual_snapshot_id",
        "auditory_source_clock_id",
        "visual_source_clock_id",
        "field_clock_id",
        "source_window_start_tick",
        "source_window_end_tick",
        "field_window_start_tick",
        "field_window_end_tick",
        "raw_payload_retained",
    }
    if any(
        not isinstance(receipt.get(field), str)
        or _DIGEST.fullmatch(receipt[field]) is None
        for field in digest_fields
    ):
        errors.append(f"compact receptor digest shape differs: {row['operation_id']}")
    expected_source_digest = _digest(
        {
            "schema": "s2gt.private.runner.v1",
            "source_id": expected_source_id,
            "role": source_role,
            "visual_fixture_id": receipt.get("visual_fixture_id"),
            "auditory_fixture_id": receipt.get("auditory_fixture_id"),
            "window": list(expected_window),
            "raw_sha256": receipt.get("raw_image_sha256"),
            "bound_digest": receipt.get("bound_source_digest"),
        }
    )
    if receipt.get("source_digest") != expected_source_digest:
        errors.append(f"compact receptor source digest differs: {row['operation_id']}")

    result_payload = result.get("payload")
    artifact_digest = (
        result_payload.get("artifact_digest") if isinstance(result_payload, dict) else None
    )
    next_payload = next_start.get("payload") if isinstance(next_start, dict) else None
    if (
        not isinstance(next_payload, dict)
        or next_start.get("phase") != "START"
        or next_start.get("operation_id") != row["successor"]
        or next_start.get("previous_event_digest") != result.get("event_digest")
        or next_payload.get("receptor_receipt_digest") != artifact_digest
        or next_payload.get("source_digest") != receipt.get("source_digest")
    ):
        errors.append(f"compact receptor successor binding differs: {row['operation_id']}")
    return errors


def _validate_failure_code_binding(
    run_directory: Path,
    events: list[dict[str, object]],
    operation_rows: tuple[dict[str, str], ...],
    error_code_rows: tuple[dict[str, str], ...],
    manifest: dict[str, object],
    reservation: dict[str, object],
) -> list[str]:
    errors: list[str] = []
    failed_results = tuple(
        event
        for event in events
        if event.get("phase") == "RESULT"
        and isinstance(event.get("operation_id"), str)
        and str(event["operation_id"]).startswith("op-")
        and isinstance(event.get("payload"), dict)
        and event["payload"].get("status") == "FAILED"
    )
    if len(failed_results) != 1:
        return ["exactly one failed registered operation required"]

    failed_result = failed_results[0]
    failed_operation_id = str(failed_result["operation_id"])
    try:
        failed_row = operation_rows[int(failed_operation_id[3:]) - 1]
    except (ValueError, IndexError):
        return ["failed operation registry binding differs"]
    payload = failed_result["payload"]
    error_code = payload.get("error_code")
    matches = tuple(row for row in error_code_rows if row["error_code"] == error_code)
    if len(matches) != 1:
        errors.append("failure error code is not registered")
        return errors
    error_row = matches[0]
    failed_phase = payload.get("failed_phase")
    if (
        failed_operation_id != failed_row["operation_id"]
        or failed_phase not in error_row["allowed_phase"].split("|")
        or error_row["failure_successor"] != "err-0001"
        or payload.get("artifact_published") is not False
    ):
        errors.append("failure code phase or successor binding differs")

    try:
        receipt = _load_json(run_directory / "failure/run-failure.json")
    except (OSError, json.JSONDecodeError):
        return errors + ["failure receipt is unreadable"]
    required_fields = {
        "error_code",
        "failure_path_id",
        "failed_operation_id",
        "failed_operation_index",
        "failed_operation_class",
        "failed_phase",
        "owner_id",
        "reservation_digest",
        "last_valid_event_digest",
        "last_event_digest",
        "partial_state_digest",
        "artifact_published",
        "status",
    }
    if not isinstance(receipt, dict) or set(receipt) != required_fields:
        return errors + ["failure receipt shape differs"]
    if (
        receipt.get("error_code") != error_code
        or receipt.get("failure_path_id") != payload.get("failure_path_id")
        or receipt.get("failed_operation_id") != failed_operation_id
        or receipt.get("failed_operation_index") != int(failed_row["index"])
        or receipt.get("failed_operation_class") != failed_row["operation_class"]
        or receipt.get("failed_phase") != failed_phase
        or receipt.get("owner_id") != manifest.get("owner_id")
        or receipt.get("reservation_digest") != reservation.get("reservation_digest")
        or receipt.get("last_event_digest") != failed_result.get("event_digest")
        or receipt.get("artifact_published") is not False
        or receipt.get("status") != "NOT_EVALUABLE"
    ):
        errors.append("failure receipt relational binding differs")
    for field in (
        "last_valid_event_digest",
        "last_event_digest",
        "partial_state_digest",
    ):
        if (
            not isinstance(receipt.get(field), str)
            or _DIGEST.fullmatch(receipt[field]) is None
        ):
            errors.append(f"failure receipt digest differs: {field}")
    if any(key in receipt for key in ("message", "message_id", "case_id", "target_values")):
        errors.append("dynamic failure content leaked into receipt")
    return errors


def verify_run_read_only(workspace_root: Path, run_directory: Path) -> VerificationFinding:
    """Verify stored bytes only; no project module or state function is imported."""

    errors: list[str] = []
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute() or not isinstance(run_directory, Path) or not run_directory.is_absolute():
        return _finding("NOT_EVALUABLE", None, 0, 0, 0, None, ["absolute pathlib.Path inputs required"])
    try:
        rows, error_code_rows, registry_bundle_digest = _registries(workspace_root)
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
    if failed:
        errors.extend(
            _validate_failure_code_binding(
                run_directory,
                events,
                rows,
                error_code_rows,
                manifest,
                reservation,
            )
        )

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

    for event_position, event in enumerate(events):
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
            continue
        if payload.get("artifact_bytes") != target.stat().st_size:
            errors.append(f"artifact byte binding differs: {operation_id}")
        if row["operation_class"] in RECEPTOR_OPERATION_CLASSES:
            start = events[event_position - 1] if event_position > 0 else {}
            next_start = (
                events[event_position + 1]
                if event_position + 1 < len(events)
                else None
            )
            errors.extend(
                _validate_compact_receptor_receipt(
                    target,
                    row,
                    start,
                    event,
                    next_start,
                    manifest,
                    reservation,
                    registry_bundle_digest,
                )
            )

    byte_count = sum(path.stat().st_size for path in run_directory.rglob("*") if path.is_file())
    maximum = MAX_SUCCESS_BYTES if complete else MAX_RUN_BYTES
    if byte_count > maximum:
        errors.append("recorded byte budget exceeded")
    if complete and events and events[-1].get("operation_id") != "op-0139":
        errors.append("completion operation differs")

    status = "RECORDING_COMPLETE" if complete and not errors else "NOT_EVALUABLE"
    return _finding(status, run_id if isinstance(run_id, str) else None, operation_count, len(events), byte_count, previous if events else None, errors)


__all__: tuple[str, ...] = ()
