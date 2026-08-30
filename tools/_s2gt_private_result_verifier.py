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
COMPACT_FORMATION_RECEIPT_SCHEMA = "s2he.compact-composite-formation-receipt.v1"
COMPACT_S2GC_RECEIPT_SCHEMA = "s2he.compact-s2gc-projection-receipt.v1"
COMPACT_S2GI_RECEIPT_SCHEMA = "s2he.compact-s2gi-projection-receipt.v1"
COMPACT_FORMATION_MAX_ARTIFACT_BYTES = 2_801
COMPACT_S2GC_MAX_ARTIFACT_BYTES = 3_174
COMPACT_S2GI_MAX_ARTIFACT_BYTES = 2_977
S2FS_SCHEMA = "s2fs.b4-tspm1.private-coordinator.v1"
S2GB_SCHEMA = "s2gb.perceptual-context-bundle.v1"
S2GI_SCHEMA = "s2gi.two-area-context-bundle.v1"
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
COMPACT_FORMATION_RECEIPT_FIELDS = frozenset(
    {
        "schema", "execution_plan_digest", "source_digest",
        "receptor_receipt_artifact_digest", "config_digest",
        "owner_prestate_digest", "input_digest", "composite_prestate_digest",
        "composite_poststate_digest", "b4_event", "b4_slot_id",
        "b4_poststate_digest", "tspm_result_digest", "tspm_receipt_digest",
        "tspm_poststate_digest", "step_receipt_digest", "generation",
        "parent_state_digest", "last_input_digest", "ledger_operation",
        "ledger_counts", "resource_ledger_digest", "coordinator_owner_ids",
        "owner_authorized_digests", "owner_status", "owner_attempt_count",
        "owner_use_count", "owner_committed_result_digest",
        "owner_state_digest", "result_digest", "projection_digest",
    }
)
COMPACT_S2GC_RECEIPT_FIELDS = frozenset(
    {
        "schema", "execution_plan_digest", "source_finding_artifact_digest",
        "source_finding_digest", "contract_digest", "binding_digest",
        "config_digest", "composite_state_digest", "probe_digest",
        "source_digest", "role_statuses", "role_absence_reasons",
        "role_finding_digests", "candidate_digests", "component_roles",
        "component_digests", "component_source_digests",
        "component_values_digests", "component_native_distances",
        "component_functional_distances", "component_support_counts",
        "component_stable_flags", "component_last_selected_steps",
        "component_formation_indices", "sequence_status",
        "sequence_reference_digests", "sequence_digests", "ledger_counts",
        "resource_ledger_digest", "prestate_digest", "poststate_digest",
        "automatic_selection", "bundle_digest", "projection_digest",
    }
)
COMPACT_S2GI_RECEIPT_FIELDS = frozenset(
    {
        "schema", "execution_plan_digest", "source_s2gc_artifact_digest",
        "source_bundle_digest", "contract_digest", "binding_digest",
        "config_digest", "composite_state_digest", "probe_digest",
        "source_digest", "area_roles", "area_finding_digests",
        "a_recent_status", "a_recent_finding_digest", "a_fast_status",
        "a_fast_finding_digest", "a_sequence_status",
        "a_sequence_finding_digest", "b_stable_status", "b_candidate_digest",
        "b_component_digests", "b_values_digests", "b_source_digests",
        "ledger_counts", "source_ledger_digest", "resource_ledger_digest",
        "prestate_digest", "poststate_digest", "automatic_selection",
        "bundle_digest", "projection_digest",
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


def _compact_receipt(
    target: Path,
    row: dict[str, str],
    start: dict[str, object],
    manifest: dict[str, object],
    reservation: dict[str, object],
    fields: frozenset[str],
    maximum: int,
) -> tuple[dict[str, object] | None, list[str]]:
    errors: list[str] = []
    try:
        raw = target.read_bytes()
        artifact = json.loads(raw.decode("ascii"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None, [f"compact artifact is unreadable: {row['operation_id']}"]
    if (
        not isinstance(artifact, dict)
        or raw != _canonical(artifact) + b"\n"
        or len(raw) > maximum
        or len(raw) >= int(row["output_max_bytes"])
    ):
        return None, [f"compact artifact encoding differs: {row['operation_id']}"]
    if set(artifact) != {
        "schema", "operation_id", "owner_id", "reservation_digest",
        "start_event_digest", "artifact",
    }:
        return None, [f"compact artifact envelope differs: {row['operation_id']}"]
    body = artifact.get("artifact")
    receipt = body.get("result") if isinstance(body, dict) and set(body) == {"result"} else None
    if not isinstance(receipt, dict) or set(receipt) != fields:
        return None, [f"compact receipt shape differs: {row['operation_id']}"]
    if (
        artifact.get("schema") != "s2gt.private.append-only-recorder.v1"
        or artifact.get("operation_id") != row["operation_id"]
        or artifact.get("owner_id") != manifest.get("owner_id")
        or artifact.get("reservation_digest") != reservation.get("reservation_digest")
        or artifact.get("start_event_digest") != start.get("event_digest")
    ):
        errors.append(f"compact receipt parent binding differs: {row['operation_id']}")
    projection = dict(receipt)
    projection_digest = projection.pop("projection_digest", None)
    if projection_digest != _digest(projection):
        errors.append(f"compact projection digest differs: {row['operation_id']}")
    return receipt, errors


def _artifact_result(path: Path) -> dict[str, object] | None:
    try:
        artifact = _load_json(path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(artifact, dict):
        return None
    body = artifact.get("artifact")
    result = body.get("result") if isinstance(body, dict) else None
    return result if isinstance(result, dict) else None


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


def _validate_compact_formation_receipt(
    target: Path,
    row: dict[str, str],
    start: dict[str, object],
    manifest: dict[str, object],
    reservation: dict[str, object],
    previous_formation_artifact_digest: str | None,
) -> list[str]:
    receipt, errors = _compact_receipt(
        target, row, start, manifest, reservation,
        COMPACT_FORMATION_RECEIPT_FIELDS, COMPACT_FORMATION_MAX_ARTIFACT_BYTES,
    )
    if receipt is None:
        return errors
    payload = start.get("payload")
    if not isinstance(payload, dict):
        return errors + [f"formation START payload differs: {row['operation_id']}"]
    if (
        receipt.get("schema") != COMPACT_FORMATION_RECEIPT_SCHEMA
        or receipt.get("execution_plan_digest") != manifest.get("plan_digest")
        or receipt.get("source_digest") != payload.get("source_digest")
        or receipt.get("receptor_receipt_artifact_digest") != payload.get("receptor_receipt_digest")
        or receipt.get("composite_prestate_digest") != payload.get("prestate_digest")
        or payload.get("previous_formation_receipt_digest") != previous_formation_artifact_digest
    ):
        errors.append(f"formation source binding differs: {row['operation_id']}")
    digest_fields = COMPACT_FORMATION_RECEIPT_FIELDS - {
        "schema", "b4_event", "b4_slot_id", "generation", "ledger_operation",
        "ledger_counts", "coordinator_owner_ids", "owner_authorized_digests",
        "owner_status", "owner_attempt_count", "owner_use_count",
    }
    if any(not isinstance(receipt.get(name), str) or _DIGEST.fullmatch(receipt[name]) is None for name in digest_fields):
        errors.append(f"formation digest shape differs: {row['operation_id']}")
        return errors
    counts = receipt.get("ledger_counts")
    owner_ids = receipt.get("coordinator_owner_ids")
    authorized = receipt.get("owner_authorized_digests")
    generation = receipt.get("generation")
    if (
        not isinstance(counts, list) or len(counts) != 11
        or any(type(value) is not int or value < 0 for value in counts)
        or not isinstance(owner_ids, list) or len(owner_ids) != 3
        or any(not isinstance(value, str) or not value for value in owner_ids)
        or not isinstance(authorized, list) or len(authorized) != 3
        or any(not isinstance(value, str) or _DIGEST.fullmatch(value) is None for value in authorized)
        or type(generation) is not int or generation < 1
        or receipt.get("ledger_operation") != "FORMATION"
        or receipt.get("owner_status") != "CONSUMED"
        or receipt.get("owner_attempt_count") != 1
        or receipt.get("owner_use_count") != 1
        or receipt.get("b4_event") not in {"B4_APPENDED", "B4_EVICTED_AND_APPENDED"}
    ):
        errors.append(f"formation anatomy differs: {row['operation_id']}")
        return errors
    if (
        authorized[0] != receipt.get("config_digest")
        or authorized[1] != receipt.get("composite_prestate_digest")
        or authorized[2] != receipt.get("input_digest")
        or receipt.get("parent_state_digest") != receipt.get("composite_prestate_digest")
        or receipt.get("last_input_digest") != receipt.get("input_digest")
    ):
        errors.append(f"formation relational identity differs: {row['operation_id']}")

    ledger_payload = {
        "schema": S2FS_SCHEMA,
        "operation": "FORMATION",
        "common_projection_terms": counts[0],
        "b4_functional_write_words": counts[1],
        "b4_functional_distance_terms": counts[2],
        "tspm_functional_write_words": counts[3],
        "tspm_functional_distance_terms": counts[4],
        "coordinator_validation_terms": counts[5],
        "coordinator_digest_operations": counts[6],
        "coordinator_write_words": counts[7],
        "total_functional_write_words": counts[8],
        "total_functional_distance_terms": counts[9],
        "total_control_terms": counts[10],
    }
    poststate_payload = {
        "schema": S2FS_SCHEMA,
        "config_digest": receipt.get("config_digest"),
        "generation": generation,
        "parent_state_digest": receipt.get("parent_state_digest"),
        "last_input_digest": receipt.get("last_input_digest"),
        "b4_state_digest": receipt.get("b4_poststate_digest"),
        "tspm_state_digest": receipt.get("tspm_poststate_digest"),
    }
    step_payload = {
        "schema": S2FS_SCHEMA,
        "config_digest": receipt.get("config_digest"),
        "owner_prestate_digest": receipt.get("owner_prestate_digest"),
        "input_digest": receipt.get("input_digest"),
        "composite_prestate_digest": receipt.get("composite_prestate_digest"),
        "b4_event": receipt.get("b4_event"),
        "b4_slot_id": receipt.get("b4_slot_id"),
        "b4_poststate_digest": receipt.get("b4_poststate_digest"),
        "tspm_result_digest": receipt.get("tspm_result_digest"),
        "tspm_receipt_digest": receipt.get("tspm_receipt_digest"),
        "tspm_poststate_digest": receipt.get("tspm_poststate_digest"),
        "resource_ledger_digest": receipt.get("resource_ledger_digest"),
        "composite_poststate_digest": receipt.get("composite_poststate_digest"),
    }
    owner_payload = {
        "schema": S2FS_SCHEMA,
        "owner_id": owner_ids[0],
        "authorization_id": owner_ids[1],
        "consumption_id": owner_ids[2],
        "authorized_config_digest": authorized[0],
        "authorized_prestate_digest": authorized[1],
        "authorized_input_digest": authorized[2],
        "status": "CONSUMED",
        "attempt_count": 1,
        "use_count": 1,
        "committed_result_digest": receipt.get("owner_committed_result_digest"),
        "failure_code": None,
        "failure_digest": None,
    }
    owner_result_projection = dict(owner_payload)
    owner_result_projection.pop("committed_result_digest")
    result_payload = {
        "schema": S2FS_SCHEMA,
        "poststate_digest": receipt.get("composite_poststate_digest"),
        "receipt_digest": receipt.get("step_receipt_digest"),
        "resource_ledger_digest": receipt.get("resource_ledger_digest"),
        "owner_poststate_projection": owner_result_projection,
    }
    if (
        _digest(ledger_payload) != receipt.get("resource_ledger_digest")
        or _digest(poststate_payload) != receipt.get("composite_poststate_digest")
        or _digest(step_payload) != receipt.get("step_receipt_digest")
        or _digest(owner_payload) != receipt.get("owner_state_digest")
        or _digest(result_payload) != receipt.get("result_digest")
        or receipt.get("owner_committed_result_digest") != receipt.get("result_digest")
    ):
        errors.append(f"formation semantic digest differs: {row['operation_id']}")
    return errors


def _s2gc_expected_projection(
    source: dict[str, object],
    receipt: dict[str, object],
) -> dict[str, object] | None:
    b4 = source.get("b4_recent")
    fast = source.get("tspm_fast")
    slow = source.get("tspm_slow")
    if not isinstance(b4, dict) or (fast is not None and not isinstance(fast, dict)) or not isinstance(slow, list) or len(slow) != 2 or any(not isinstance(item, dict) for item in slow):
        return None

    component_records: list[dict[str, object]] = []
    role_records: list[dict[str, object]] = []

    def component(
        role: str,
        values: object,
        source_id: object,
        source_state_digest: object,
        native_distances: object,
        functional_distances: object,
        support_count: object,
        stable: object,
        last_selected_step: object,
        formation_index: object,
    ) -> dict[str, object] | None:
        if not isinstance(values, list) or not isinstance(source_id, str) or not isinstance(source_state_digest, str):
            return None
        source_payload = {
            "schema": S2GB_SCHEMA,
            "source_id": source_id,
            "source_state_digest": source_state_digest,
            "component_role": role,
        }
        payload = {
            "schema": S2GB_SCHEMA,
            "component_role": role,
            "values": values,
            "source_id": source_id,
            "source_digest": _digest(source_payload),
            "values_digest": _digest(values),
            "native_distances": native_distances,
            "functional_distances": functional_distances,
            "support_count": support_count,
            "stable": stable,
            "last_selected_step": last_selected_step,
            "formation_index": formation_index,
        }
        record = dict(payload)
        record["component_digest"] = _digest(payload)
        return record

    def role_record(role: str, status: str, components: list[dict[str, object]], reason: str | None) -> None:
        if components:
            cross_relation = "CROSS_MODAL_RELATION_NOT_REPRESENTED" if role == "TSPM_SLOW" else "JOINT_SOURCE_VALUES"
            candidate_payload = {
                "schema": S2GB_SCHEMA,
                "role": role,
                "component_digests": [item["component_digest"] for item in components],
                "cross_modal_relation": cross_relation,
            }
            candidate_digest: str | None = _digest(candidate_payload)
            component_records.extend(components)
        else:
            candidate_digest = None
        role_payload = {
            "schema": S2GB_SCHEMA,
            "role": role,
            "status": status,
            "candidate_digest": candidate_digest,
            "absence_reason": reason,
        }
        role_records.append(
            {
                "role": role,
                "status": status,
                "absence_reason": reason,
                "candidate_digest": candidate_digest,
                "finding_digest": _digest(role_payload),
            }
        )

    b4_selected = b4.get("selected")
    if isinstance(b4_selected, dict):
        record = component(
            "AV_JOINT", b4_selected.get("values"), b4_selected.get("slot_id"),
            b4.get("observed_state_digest"), None,
            [b4_selected.get("auditory_distance"), b4_selected.get("visual_distance")],
            None, None, None, b4_selected.get("formation_index"),
        )
        if record is None:
            return None
        role_record("B4_RECENT", "AVAILABLE_COMPLETE", [record], None)
    else:
        reason = "NO_OCCUPIED_SOURCE" if b4.get("occupied_slot_count") == 0 else "NO_FUNCTIONAL_MATCH"
        role_record("B4_RECENT", "ABSENT_VALID", [], reason)

    if isinstance(fast, dict):
        fast_values = fast.get("auditory_values")
        visual_values = fast.get("visual_values")
        if not isinstance(fast_values, list) or not isinstance(visual_values, list):
            return None
        record = component(
            "AV_JOINT", fast_values + visual_values, fast.get("slot_id"),
            fast.get("slot_digest"),
            [fast.get("auditory_distance"), fast.get("visual_distance")],
            [fast.get("auditory_distance"), fast.get("visual_distance")],
            fast.get("support_count"), None, fast.get("last_selected_step"), None,
        )
        if record is None:
            return None
        role_record("TSPM_FAST", "AVAILABLE_COMPLETE", [record], None)
    else:
        role_record("TSPM_FAST", "ABSENT_VALID", [], "NO_FUNCTIONAL_MATCH")

    slow_components: list[dict[str, object]] = []
    for finding, component_role in zip(slow, ("AUDITORY", "VISUAL")):
        if finding.get("functional_recognized") is not True:
            continue
        selected = finding.get("selected")
        if not isinstance(selected, dict) or selected.get("stable") is not True:
            return None
        record = component(
            component_role, selected.get("prototype_values"),
            f"{finding.get('bank_id')}.{selected.get('slot_id')}",
            finding.get("observed_bank_state_digest"),
            [selected.get("native_distance")], [selected.get("native_distance")],
            selected.get("support_count"), selected.get("stable"),
            selected.get("last_selected_step"), None,
        )
        if record is None:
            return None
        slow_components.append(record)
    if slow_components:
        status = "AVAILABLE_COMPLETE" if len(slow_components) == 2 else "AVAILABLE_PARTIAL"
        role_record("TSPM_SLOW", status, slow_components, None)
    else:
        role_record("TSPM_SLOW", "ABSENT_VALID", [], "NO_STABLE_SLOW_MATCH")

    sequence_status = receipt.get("sequence_status")
    sequence_references = receipt.get("sequence_reference_digests")
    if not isinstance(sequence_status, str) or not isinstance(sequence_references, list):
        return None
    sequence_evidence_payload = {
        "schema": S2GB_SCHEMA,
        "status": sequence_status,
        "observed_b4_state_digest": b4.get("observed_state_digest"),
        "probe_digest": source.get("probe_digest"),
        "reference_digests": sequence_references,
    }
    sequence_evidence_digest = _digest(sequence_evidence_payload)
    sequence_finding_payload = {
        "schema": S2GB_SCHEMA,
        "status": sequence_status,
        "reference_digests": sequence_references,
        "observed_b4_state_digest": b4.get("observed_state_digest"),
        "source_evidence_digest": sequence_evidence_digest,
    }
    sequence_finding_digest = _digest(sequence_finding_payload)
    candidates = [item["candidate_digest"] for item in role_records if item["candidate_digest"] is not None]
    return {
        "role_records": role_records,
        "component_records": component_records,
        "candidate_digests": candidates,
        "sequence_evidence_digest": sequence_evidence_digest,
        "sequence_finding_digest": sequence_finding_digest,
    }


def _validate_compact_s2gc_receipt(
    target: Path,
    source_target: Path,
    row: dict[str, str],
    start: dict[str, object],
    manifest: dict[str, object],
    reservation: dict[str, object],
    s2gi_start: dict[str, object] | None,
) -> list[str]:
    receipt, errors = _compact_receipt(
        target, row, start, manifest, reservation,
        COMPACT_S2GC_RECEIPT_FIELDS, COMPACT_S2GC_MAX_ARTIFACT_BYTES,
    )
    if receipt is None:
        return errors
    source = _artifact_result(source_target)
    payload = start.get("payload")
    source_artifact_digest = _file_digest(source_target) if source_target.is_file() else None
    if source is None or not isinstance(payload, dict):
        return errors + [f"S2-GC source artifact differs: {row['operation_id']}"]
    scalar_digests = (
        "execution_plan_digest", "source_finding_artifact_digest",
        "source_finding_digest", "contract_digest", "binding_digest",
        "config_digest", "composite_state_digest", "probe_digest",
        "source_digest", "resource_ledger_digest", "prestate_digest",
        "poststate_digest", "bundle_digest", "projection_digest",
    )
    digest_lists = (
        "role_finding_digests", "candidate_digests", "component_digests",
        "component_source_digests", "component_values_digests",
        "sequence_reference_digests", "sequence_digests",
    )
    component_lists = (
        "component_roles", "component_digests", "component_source_digests",
        "component_values_digests", "component_native_distances",
        "component_functional_distances", "component_support_counts",
        "component_stable_flags", "component_last_selected_steps",
        "component_formation_indices",
    )
    if (
        any(not isinstance(receipt.get(name), str) or _DIGEST.fullmatch(receipt[name]) is None for name in scalar_digests)
        or any(not isinstance(receipt.get(name), list) or any(not isinstance(value, str) or _DIGEST.fullmatch(value) is None for value in receipt[name]) for name in digest_lists)
        or any(not isinstance(receipt.get(name), list) for name in component_lists)
        or len({len(receipt[name]) for name in component_lists}) != 1
        or not isinstance(receipt.get("role_statuses"), list) or len(receipt["role_statuses"]) != 3
        or not isinstance(receipt.get("role_absence_reasons"), list) or len(receipt["role_absence_reasons"]) != 3
        or len(receipt.get("sequence_digests", [])) != 2
    ):
        return errors + [f"S2-GC digest or parallel-list shape differs: {row['operation_id']}"]
    if (
        receipt.get("schema") != COMPACT_S2GC_RECEIPT_SCHEMA
        or receipt.get("execution_plan_digest") != manifest.get("plan_digest")
        or receipt.get("source_finding_artifact_digest") != source_artifact_digest
        or receipt.get("source_finding_digest") != source.get("finding_digest")
        or payload.get("finding_digest") != receipt.get("source_finding_digest")
        or payload.get("finding_receipt_digest") != source_artifact_digest
        or receipt.get("composite_state_digest") != source.get("observed_state_digest")
        or receipt.get("probe_digest") != source.get("probe_digest")
        or receipt.get("prestate_digest") != source.get("prestate_digest")
        or receipt.get("poststate_digest") != source.get("poststate_digest")
        or receipt.get("prestate_digest") != receipt.get("poststate_digest")
        or receipt.get("prestate_digest") != receipt.get("composite_state_digest")
        or receipt.get("automatic_selection") is not None
    ):
        errors.append(f"S2-GC source binding differs: {row['operation_id']}")
    expected = _s2gc_expected_projection(source, receipt)
    if expected is None:
        return errors + [f"S2-GC parent materialization differs: {row['operation_id']}"]
    roles = expected["role_records"]
    components = expected["component_records"]
    if not isinstance(roles, list) or not isinstance(components, list):
        return errors + [f"S2-GC expected projection differs: {row['operation_id']}"]
    expected_lists = {
        "role_statuses": [item["status"] for item in roles],
        "role_absence_reasons": [item["absence_reason"] for item in roles],
        "role_finding_digests": [item["finding_digest"] for item in roles],
        "candidate_digests": expected["candidate_digests"],
        "component_roles": [item["component_role"] for item in components],
        "component_digests": [item["component_digest"] for item in components],
        "component_source_digests": [item["source_digest"] for item in components],
        "component_values_digests": [item["values_digest"] for item in components],
        "component_native_distances": [item["native_distances"] for item in components],
        "component_functional_distances": [item["functional_distances"] for item in components],
        "component_support_counts": [item["support_count"] for item in components],
        "component_stable_flags": [item["stable"] for item in components],
        "component_last_selected_steps": [item["last_selected_step"] for item in components],
        "component_formation_indices": [item["formation_index"] for item in components],
        "sequence_digests": [expected["sequence_evidence_digest"], expected["sequence_finding_digest"]],
    }
    if any(receipt.get(name) != value for name, value in expected_lists.items()):
        errors.append(f"S2-GC component or role projection differs: {row['operation_id']}")
    counts = receipt.get("ledger_counts")
    if not isinstance(counts, list) or len(counts) != 8 or any(type(value) is not int or value < 0 for value in counts):
        return errors + [f"S2-GC ledger anatomy differs: {row['operation_id']}"]
    b4 = source["b4_recent"]
    slow = source["tspm_slow"]
    if not isinstance(b4, dict) or not isinstance(slow, list) or any(not isinstance(item, dict) for item in slow):
        return errors + [f"S2-GC ledger source differs: {row['operation_id']}"]
    b4_candidates = b4.get("candidates")
    slow_slot_counts = [item.get("slots") for item in slow]
    if not isinstance(b4_candidates, list) or any(not isinstance(item, list) for item in slow_slot_counts):
        return errors + [f"S2-GC ledger source differs: {row['operation_id']}"]
    expected_counts = [
        2 + len(b4_candidates) + int(source.get("tspm_fast") is not None) + sum(len(item) for item in slow_slot_counts) + len(receipt.get("sequence_reference_digests", [])),
        8 + len(components) + len(receipt.get("sequence_reference_digests", [])),
        3,
        len(expected["candidate_digests"]),
        len(components),
        sum(26 if item["component_role"] == "AV_JOINT" else 8 if item["component_role"] == "AUDITORY" else 18 for item in components),
        len(receipt.get("sequence_reference_digests", [])),
        len(components) + len(expected["candidate_digests"]) + 6,
    ]
    ledger_payload = {
        "schema": S2GB_SCHEMA,
        "validated_evidence_records": counts[0],
        "validated_digest_count": counts[1],
        "role_projection_count": counts[2],
        "candidate_count": counts[3],
        "component_count": counts[4],
        "value_count": counts[5],
        "sequence_reference_count": counts[6],
        "digest_operation_count": counts[7],
    }
    bundle_payload = {
        "schema": S2GB_SCHEMA,
        "contract_digest": receipt.get("contract_digest"),
        "binding_digest": receipt.get("binding_digest"),
        "config_digest": receipt.get("config_digest"),
        "composite_state_digest": receipt.get("composite_state_digest"),
        "probe_digest": receipt.get("probe_digest"),
        "source_digest": receipt.get("source_digest"),
        "role_finding_digests": receipt.get("role_finding_digests"),
        "sequence_finding_digest": expected["sequence_finding_digest"],
        "resource_ledger_digest": receipt.get("resource_ledger_digest"),
        "prestate_digest": receipt.get("prestate_digest"),
        "poststate_digest": receipt.get("poststate_digest"),
        "automatic_selection": None,
    }
    if (
        counts != expected_counts
        or _digest(ledger_payload) != receipt.get("resource_ledger_digest")
        or _digest(bundle_payload) != receipt.get("bundle_digest")
        or receipt.get("contract_digest") != "9a72752f241d6ff74517b119b535cb60ba15c830ec231af1378604d06ed25b72"
    ):
        errors.append(f"S2-GC semantic digest differs: {row['operation_id']}")
    next_payload = s2gi_start.get("payload") if isinstance(s2gi_start, dict) else None
    if (
        not isinstance(next_payload, dict)
        or next_payload.get("bundle_digest") != receipt.get("bundle_digest")
        or next_payload.get("s2gc_receipt_digest") != _file_digest(target)
    ):
        errors.append(f"S2-GC successor binding differs: {row['operation_id']}")
    return errors


def _validate_compact_s2gi_receipt(
    target: Path,
    source_target: Path,
    row: dict[str, str],
    start: dict[str, object],
    manifest: dict[str, object],
    reservation: dict[str, object],
    arm_starts: tuple[dict[str, object], ...],
) -> list[str]:
    receipt, errors = _compact_receipt(
        target, row, start, manifest, reservation,
        COMPACT_S2GI_RECEIPT_FIELDS, COMPACT_S2GI_MAX_ARTIFACT_BYTES,
    )
    if receipt is None:
        return errors
    source = _artifact_result(source_target)
    payload = start.get("payload")
    source_artifact_digest = _file_digest(source_target) if source_target.is_file() else None
    if source is None or not isinstance(payload, dict):
        return errors + [f"S2-GI source artifact differs: {row['operation_id']}"]
    scalar_digests = (
        "execution_plan_digest", "source_s2gc_artifact_digest",
        "source_bundle_digest", "contract_digest", "binding_digest",
        "config_digest", "composite_state_digest", "probe_digest",
        "source_digest", "a_recent_finding_digest", "a_fast_finding_digest",
        "a_sequence_finding_digest", "source_ledger_digest",
        "resource_ledger_digest", "prestate_digest", "poststate_digest",
        "bundle_digest", "projection_digest",
    )
    digest_lists = (
        "area_finding_digests", "b_component_digests", "b_values_digests",
        "b_source_digests",
    )
    if (
        any(not isinstance(receipt.get(name), str) or _DIGEST.fullmatch(receipt[name]) is None for name in scalar_digests)
        or any(not isinstance(receipt.get(name), list) or any(not isinstance(value, str) or _DIGEST.fullmatch(value) is None for value in receipt[name]) for name in digest_lists)
        or len(receipt.get("area_finding_digests", [])) != 2
        or len(receipt.get("b_component_digests", [])) != len(receipt.get("b_values_digests", []))
        or len(receipt.get("b_component_digests", [])) != len(receipt.get("b_source_digests", []))
        or (receipt.get("b_candidate_digest") is not None and (not isinstance(receipt.get("b_candidate_digest"), str) or _DIGEST.fullmatch(receipt["b_candidate_digest"]) is None))
    ):
        return errors + [f"S2-GI digest or parallel-list shape differs: {row['operation_id']}"]
    source_roles = source.get("role_finding_digests")
    source_statuses = source.get("role_statuses")
    source_candidates = source.get("candidate_digests")
    source_component_digests = source.get("component_digests")
    source_value_digests = source.get("component_values_digests")
    source_source_digests = source.get("component_source_digests")
    source_sequence_digests = source.get("sequence_digests")
    source_counts = source.get("ledger_counts")
    if (
        not isinstance(source_roles, list) or len(source_roles) != 3
        or not isinstance(source_statuses, list) or len(source_statuses) != 3
        or not isinstance(source_candidates, list)
        or not isinstance(source_component_digests, list)
        or not isinstance(source_value_digests, list)
        or not isinstance(source_source_digests, list)
        or not isinstance(source_sequence_digests, list) or len(source_sequence_digests) != 2
        or not isinstance(source_counts, list) or len(source_counts) != 8
        or any(type(value) is not int or value < 0 for value in source_counts)
        or len(source_component_digests) != len(source_value_digests)
        or len(source_component_digests) != len(source_source_digests)
    ):
        return errors + [f"S2-GI parent projection differs: {row['operation_id']}"]
    prior_component_count = int(source_statuses[0] != "ABSENT_VALID") + int(source_statuses[1] != "ABSENT_VALID")
    b_component_digests = source_component_digests[prior_component_count:]
    b_value_digests = source_value_digests[prior_component_count:]
    b_source_digests = source_source_digests[prior_component_count:]
    candidate_index = int(source_statuses[0] != "ABSENT_VALID") + int(source_statuses[1] != "ABSENT_VALID")
    if source_statuses[2] == "ABSENT_VALID":
        b_candidate_digest = None
    elif candidate_index >= len(source_candidates):
        return errors + [f"S2-GI B candidate relation differs: {row['operation_id']}"]
    else:
        b_candidate_digest = source_candidates[candidate_index]

    area_a_payload = {
        "schema": S2GI_SCHEMA,
        "area": "A_RECENT",
        "recent_content_finding_digest": source_roles[0],
        "fast_internal_finding_digest": source_roles[1],
        "short_sequence_finding_digest": source_sequence_digests[1],
    }
    area_b_payload = {
        "schema": S2GI_SCHEMA,
        "area": "B_STABLE",
        "stable_content_finding_digest": source_roles[2],
    }
    area_digests = [_digest(area_a_payload), _digest(area_b_payload)]
    if (
        receipt.get("schema") != COMPACT_S2GI_RECEIPT_SCHEMA
        or receipt.get("execution_plan_digest") != manifest.get("plan_digest")
        or receipt.get("source_s2gc_artifact_digest") != source_artifact_digest
        or receipt.get("source_bundle_digest") != source.get("bundle_digest")
        or payload.get("bundle_digest") != source.get("bundle_digest")
        or payload.get("s2gc_receipt_digest") != source_artifact_digest
        or receipt.get("binding_digest") != source.get("binding_digest")
        or receipt.get("config_digest") != source.get("config_digest")
        or receipt.get("composite_state_digest") != source.get("composite_state_digest")
        or receipt.get("probe_digest") != source.get("probe_digest")
        or receipt.get("source_digest") != source.get("source_digest")
        or receipt.get("prestate_digest") != source.get("prestate_digest")
        or receipt.get("poststate_digest") != source.get("poststate_digest")
        or receipt.get("area_roles") != ["A_RECENT", "B_STABLE"]
        or receipt.get("area_finding_digests") != area_digests
        or receipt.get("a_recent_status") != source_statuses[0]
        or receipt.get("a_recent_finding_digest") != source_roles[0]
        or receipt.get("a_fast_status") != source_statuses[1]
        or receipt.get("a_fast_finding_digest") != source_roles[1]
        or receipt.get("a_sequence_status") != source.get("sequence_status")
        or receipt.get("a_sequence_finding_digest") != source_sequence_digests[1]
        or receipt.get("b_stable_status") != source_statuses[2]
        or receipt.get("b_candidate_digest") != b_candidate_digest
        or receipt.get("b_component_digests") != b_component_digests
        or receipt.get("b_values_digests") != b_value_digests
        or receipt.get("b_source_digests") != b_source_digests
        or receipt.get("source_ledger_digest") != source.get("resource_ledger_digest")
        or receipt.get("prestate_digest") != receipt.get("poststate_digest")
        or receipt.get("prestate_digest") != receipt.get("composite_state_digest")
        or receipt.get("automatic_selection") is not None
    ):
        errors.append(f"S2-GI source or area binding differs: {row['operation_id']}")
    counts = receipt.get("ledger_counts")
    if not isinstance(counts, list) or len(counts) != 8 or any(type(value) is not int or value < 0 for value in counts):
        return errors + [f"S2-GI ledger anatomy differs: {row['operation_id']}"]
    expected_counts = [1, 3, source_counts[3], source_counts[4], source_counts[5], source_counts[6], 2, 4]
    ledger_payload = {
        "schema": S2GI_SCHEMA,
        "validated_bundle_count": counts[0],
        "validated_role_count": counts[1],
        "candidate_reference_count": counts[2],
        "component_reference_count": counts[3],
        "value_reference_count": counts[4],
        "sequence_reference_count": counts[5],
        "area_projection_count": counts[6],
        "digest_operation_count": counts[7],
        "source_ledger_digest": receipt.get("source_ledger_digest"),
    }
    bundle_payload = {
        "schema": S2GI_SCHEMA,
        "contract_digest": receipt.get("contract_digest"),
        "source_bundle_digest": receipt.get("source_bundle_digest"),
        "binding_digest": receipt.get("binding_digest"),
        "config_digest": receipt.get("config_digest"),
        "composite_state_digest": receipt.get("composite_state_digest"),
        "probe_digest": receipt.get("probe_digest"),
        "source_digest": receipt.get("source_digest"),
        "area_finding_digests": receipt.get("area_finding_digests"),
        "resource_ledger_digest": receipt.get("resource_ledger_digest"),
        "prestate_digest": receipt.get("prestate_digest"),
        "poststate_digest": receipt.get("poststate_digest"),
        "automatic_selection": None,
    }
    if (
        counts != expected_counts
        or _digest(ledger_payload) != receipt.get("resource_ledger_digest")
        or _digest(bundle_payload) != receipt.get("bundle_digest")
        or receipt.get("contract_digest") != "379597b4705755c83f336dee7e42460d7fa608d9572cdda9dde00e8cc7977e13"
    ):
        errors.append(f"S2-GI semantic digest differs: {row['operation_id']}")
    artifact_digest = _file_digest(target)
    expected_arm_count = 2 if row["history"] in {"h01", "h02"} else 1
    if len(arm_starts) != expected_arm_count:
        errors.append(f"S2-GI successor count differs: {row['operation_id']}")
    for arm_start in arm_starts:
        arm_payload = arm_start.get("payload")
        if (
            not isinstance(arm_payload, dict)
            or arm_payload.get("context_bundle_digest") != receipt.get("bundle_digest")
            or arm_payload.get("context_receipt_digest") != artifact_digest
        ):
            errors.append(f"S2-GI successor binding differs: {row['operation_id']}")
            break
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

    starts_by_operation = {
        str(event.get("operation_id")): event
        for event in events
        if event.get("phase") == "START" and isinstance(event.get("operation_id"), str)
    }
    row_by_class_history = {
        (row["operation_class"], row["history"]): row for row in rows
    }
    arm_histories = {
        "h01": ("op-0125", "op-0126"),
        "h02": ("op-0127", "op-0128"),
        "h03": ("op-0130",),
        "h04": ("op-0129",),
    }
    previous_formation_artifacts: dict[str, str] = {}

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
        elif row["operation_class"] == "COMPOSITE_FORMATION":
            start = events[event_position - 1] if event_position > 0 else {}
            errors.extend(
                _validate_compact_formation_receipt(
                    target,
                    row,
                    start,
                    manifest,
                    reservation,
                    previous_formation_artifacts.get(row["history"]),
                )
            )
            if isinstance(artifact_digest, str):
                previous_formation_artifacts[row["history"]] = artifact_digest
        elif row["operation_class"] == "S2GC_PROJECTION":
            start = events[event_position - 1] if event_position > 0 else {}
            source_row = row_by_class_history.get(("COMPOSITE_READ_ONLY_PROBE", row["history"]))
            s2gi_row = row_by_class_history.get(("S2GI_PROJECTION", row["history"]))
            if source_row is None or s2gi_row is None:
                errors.append(f"S2-GC registry relation differs: {operation_id}")
            else:
                source_target = run_directory / source_row["target_path"].split("|")[0]
                errors.extend(
                    _validate_compact_s2gc_receipt(
                        target,
                        source_target,
                        row,
                        start,
                        manifest,
                        reservation,
                        starts_by_operation.get(s2gi_row["operation_id"]),
                    )
                )
        elif row["operation_class"] == "S2GI_PROJECTION":
            start = events[event_position - 1] if event_position > 0 else {}
            source_row = row_by_class_history.get(("S2GC_PROJECTION", row["history"]))
            if source_row is None:
                errors.append(f"S2-GI registry relation differs: {operation_id}")
            else:
                source_target = run_directory / source_row["target_path"].split("|")[0]
                arm_starts = tuple(
                    starts_by_operation[arm_id]
                    for arm_id in arm_histories[row["history"]]
                    if arm_id in starts_by_operation
                )
                errors.extend(
                    _validate_compact_s2gi_receipt(
                        target,
                        source_target,
                        row,
                        start,
                        manifest,
                        reservation,
                        arm_starts,
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
