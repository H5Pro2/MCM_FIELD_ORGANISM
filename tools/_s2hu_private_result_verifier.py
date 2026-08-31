"""Independent stdlib-only read-only verifier for one S2-HU run."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import hashlib
import json
from pathlib import Path
import re


VERIFIER_SCHEMA = "s2hu.private.result-verifier.v1"
RECORDER_SCHEMA = "s2hu.private.append-only-recorder.v1"
REGISTRY_RELATIVE_PATH = "docs/S2HS_OPERATION_REGISTRY.csv"
REGISTRY_SHA256 = "31df0a4aada81b0b6fdf451c18072c8a2c18bf883f266a822f3c57b189b3b2fa"
SUCCESS_OPERATION_COUNT = 60
SUCCESS_EVENT_COUNT = 120
MAX_EVENT_BYTES = 1_536
MAX_INDIVIDUAL_BYTES = 4_096
MAX_SUCCESS_BYTES = 321_046
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_RECEIPT_LIMITS = {
    "S2HSRunPreparationReceipt": 1_536,
    "S2HSSourceManifestReceipt": 3_584,
    "S2HSMaskedProbeReceipt": 1_280,
    "S2HSHistoryInitialReceipt": 1_280,
    "S2HSReceptorReceipt": 2_765,
    "S2HSFormationReceipt": 2_801,
    "S2HSReadOnlyReceipt": 2_048,
    "S2HSS2GCProjectionReceipt": 3_174,
    "S2HSS2GIProjectionReceipt": 2_978,
    "S2HSHistoryEvidenceReceipt": 2_048,
    "S2HSRoleBindingReceipt": 1_792,
    "S2HSArmReceipt": 2_560,
    "S2HSCaseEvidenceReceipt": 1_536,
    "S2HSExecutionEvidencePackage": 1_792,
    "S2HSEvaluationRunBinding": 1_024,
    "S2HSEvaluationFinding": 1_536,
    "S2HSAggregateFinding": 1_280,
    "S2HSTerminalFinding": 1_024,
    "S2HSCompletionMarker": 1_024,
}

_V0 = (
    1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0,
    0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0,
)
_V1 = (
    1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0,
    0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0,
)
EXPECTED_CASE_VALUES = (
    ("c01", _V0),
    ("c02", _V1),
    ("c03", _V1),
    ("c04", _V0),
)


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


def _canonical_bytes(payload: object, *, newline: bool = False) -> bytes:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return encoded + (b"\n" if newline else b"")


def _digest(payload: object) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _file_digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(131_072), b""):
            hasher.update(block)
    return hasher.hexdigest()


def expected_evaluation_root(workspace_root: Path) -> dict[str, object]:
    """Return the independent expected evaluation root, never execution data."""

    verifier_path = workspace_root / "tools/_s2hu_private_result_verifier.py"
    source_digests = (("tools/_s2hu_private_result_verifier.py", _file_digest(verifier_path)),)
    bindings = []
    for case_id, values in EXPECTED_CASE_VALUES:
        binding_payload = {
            "schema": "s2hs.evaluation-case-binding.v1",
            "case_id": case_id,
            "expected_visual_values": values,
        }
        bindings.append((case_id, values, _digest(binding_payload)))
    seal_payload = {
        "schema": "s2hs.evaluation-plan-seal.v1",
        "plan_id": "s2hs-evaluation-plan-01",
        "case_binding_digests": tuple(item[2] for item in bindings),
        "evaluation_source_digests": source_digests,
    }
    return {
        "plan_id": "s2hs-evaluation-plan-01",
        "case_bindings": tuple(bindings),
        "evaluation_source_digests": source_digests,
        "seal_digest": _digest(seal_payload),
    }


def _finding(
    status: str,
    run_id: str | None,
    operation_count: int,
    event_count: int,
    byte_count: int,
    last_event_digest: str | None,
    errors: list[str],
) -> VerificationFinding:
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
    return VerificationFinding(
        status,
        run_id,
        operation_count,
        event_count,
        byte_count,
        last_event_digest,
        tuple(errors),
        _digest(payload),
    )


def _load_registry(workspace_root: Path) -> tuple[dict[str, str], ...]:
    path = workspace_root / REGISTRY_RELATIVE_PATH
    if _file_digest(path) != REGISTRY_SHA256:
        raise ValueError("operation registry digest differs")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = tuple(dict(row) for row in csv.DictReader(handle))
    if len(rows) != 60:
        raise ValueError("operation registry count differs")
    return rows


def _target(index: int, case_id: str) -> str:
    if index == 1:
        return "reservation.json"
    if index == 2:
        return "manifest.json"
    if index == 52:
        return "evidence/execution.json"
    if index == 53:
        return "evaluation/binding.json"
    if 54 <= index <= 57:
        return f"evaluation/{case_id}.json"
    if index == 58:
        return "evaluation/aggregate.json"
    if index == 59:
        return "terminal/prepared.json"
    if index == 60:
        return "terminal/complete/COMPLETE"
    return f"receipts/hs-op-{index:03d}.json"


def _load_artifact(path: Path) -> tuple[dict[str, object] | None, int, str | None]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("ascii"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None, 0, None
    if not isinstance(value, dict) or raw != _canonical_bytes(value, newline=True):
        return None, len(raw), hashlib.sha256(raw).hexdigest()
    return value, len(raw), hashlib.sha256(raw).hexdigest()


def _artifact_result(value: dict[str, object] | None) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    artifact = value.get("artifact")
    if not isinstance(artifact, dict):
        return None
    result = artifact.get("result")
    return result if isinstance(result, dict) else None


def verify_run_read_only(
    workspace_root: Path, run_directory: Path
) -> VerificationFinding:
    errors: list[str] = []
    if (
        not isinstance(workspace_root, Path)
        or not workspace_root.is_absolute()
        or not isinstance(run_directory, Path)
        or not run_directory.is_absolute()
    ):
        return _finding("NOT_EVALUABLE", None, 0, 0, 0, None, ["path boundary differs"])
    try:
        rows = _load_registry(workspace_root)
    except (OSError, ValueError) as error:
        return _finding("NOT_EVALUABLE", None, 0, 0, 0, None, [str(error)])

    reservation, reservation_bytes, reservation_file_digest = _load_artifact(
        run_directory / "reservation.json"
    )
    manifest, manifest_bytes, manifest_file_digest = _load_artifact(
        run_directory / "manifest.json"
    )
    reservation_result = _artifact_result(reservation)
    manifest_result = _artifact_result(manifest)
    run_id = None
    if isinstance(reservation_result, dict):
        value = reservation_result.get("run_id")
        run_id = value if isinstance(value, str) else None
    if reservation_result is None or manifest_result is None:
        errors.append("reservation or manifest is unreadable")

    events: list[dict[str, object]] = []
    journal_path = run_directory / "journal/operations.jsonl"
    journal_bytes = 0
    try:
        with journal_path.open("rb") as handle:
            for raw in handle:
                journal_bytes += len(raw)
                if len(raw) > MAX_EVENT_BYTES:
                    errors.append("event exceeds bound")
                    continue
                try:
                    event = json.loads(raw.decode("ascii"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    errors.append("journal contains an unreadable event")
                    continue
                if not isinstance(event, dict) or raw != _canonical_bytes(event, newline=True):
                    errors.append("event is not canonical")
                    continue
                events.append(event)
    except OSError:
        errors.append("journal is missing")

    prior = "0" * 64
    for index, event in enumerate(events, 1):
        projection = dict(event)
        event_digest = projection.pop("event_digest", None)
        if (
            event.get("event_index") != index
            or event.get("previous_event_digest") != prior
            or event_digest != _digest(projection)
        ):
            errors.append(f"event chain differs at {index}")
        if isinstance(event_digest, str):
            prior = event_digest
    if len(events) != SUCCESS_EVENT_COUNT:
        errors.append("event count differs")

    complete_path = run_directory / "terminal/complete/COMPLETE"
    failure_path = run_directory / "terminal/failure/NOT_EVALUABLE"
    if failure_path.is_file() and not complete_path.exists():
        failure_receipt, _, _ = _load_artifact(run_directory / "failure/receipt.json")
        failure_terminal, _, _ = _load_artifact(failure_path)
        errors = [
            item
            for item in errors
            if item not in {"event count differs", "reservation or manifest is unreadable"}
        ]
        if len(events) > 124 or len(events) < 6 or len(events) % 2:
            errors.append("failure event anatomy differs")
        expected_tail = ("hs-err-001", "hs-err-001", "hs-err-002", "hs-err-002")
        if tuple(event.get("operation_id") for event in events[-4:]) != expected_tail:
            errors.append("failure closure tail differs")
        if (
            not isinstance(failure_receipt, dict)
            or failure_receipt.get("status") != "NOT_EVALUABLE"
            or not isinstance(failure_terminal, dict)
            or failure_terminal.get("status") != "NOT_EVALUABLE"
        ):
            errors.append("failure closure artifact differs")
        total = sum(
            path.stat().st_size
            for path in run_directory.rglob("*")
            if path.is_file()
        )
        if total > 328_214:
            errors.append("failure path exceeds total budget")
        return _finding(
            "NOT_EVALUABLE",
            run_id,
            max(0, (len(events) - 4) // 2),
            len(events),
            total,
            prior if events else None,
            errors,
        )
    if failure_path.exists() and complete_path.exists():
        errors.append("success and failure terminals coexist")

    execution_plan = (
        manifest_result.get("execution_plan")
        if isinstance(manifest_result, dict)
        else None
    )
    if not isinstance(execution_plan, dict):
        errors.append("execution plan is absent from manifest")
    else:
        source_digests = execution_plan.get("source_digests")
        if not isinstance(source_digests, list):
            errors.append("execution source bindings differ")
        else:
            for item in source_digests:
                if not isinstance(item, list) or len(item) != 2:
                    errors.append("execution source binding shape differs")
                    continue
                relative, expected_digest = item
                if (
                    not isinstance(relative, str)
                    or not isinstance(expected_digest, str)
                    or ".." in Path(relative).parts
                    or relative == "tools/_s2hu_private_result_verifier.py"
                ):
                    errors.append("execution source role is invalid")
                    continue
                source_path = workspace_root / relative
                try:
                    actual_digest = _file_digest(source_path)
                except OSError:
                    errors.append(f"execution source is missing: {relative}")
                    continue
                if actual_digest != expected_digest:
                    errors.append(f"execution source digest differs: {relative}")

    artifacts: dict[str, dict[str, object]] = {}
    artifact_digests: dict[str, str] = {}
    artifact_bytes = reservation_bytes + manifest_bytes
    for index, row in enumerate(rows, 1):
        operation_id = row["operation_id"]
        target = run_directory / _target(index, row.get("case_id", ""))
        value, size, digest = _load_artifact(target)
        if index not in (1, 2):
            artifact_bytes += size
        if value is None or digest is None:
            errors.append(f"artifact is missing or noncanonical: {operation_id}")
            continue
        receipt_limit = _RECEIPT_LIMITS.get(row.get("receipt_type", ""), 0)
        if size > MAX_INDIVIDUAL_BYTES or not receipt_limit or size > receipt_limit:
            errors.append(f"artifact exceeds registry ceiling: {operation_id}")
        artifacts[operation_id] = value
        artifact_digests[operation_id] = digest
        if (
            not isinstance(execution_plan, dict)
            or value.get("owner_id") != execution_plan.get("owner_id")
            or not isinstance(reservation_result, dict)
            or value.get("reservation_digest")
            != reservation_result.get("reservation_digest")
        ):
            errors.append(f"artifact owner or reservation differs: {operation_id}")
        start_index = (index - 1) * 2
        if start_index + 1 >= len(events):
            continue
        start, result = events[start_index], events[start_index + 1]
        if (
            start.get("phase") != "START"
            or result.get("phase") != "RESULT"
            or start.get("operation_id") != operation_id
            or result.get("operation_id") != operation_id
            or value.get("operation_id") != operation_id
            or value.get("start_event_digest") != start.get("event_digest")
            or not isinstance(result.get("payload"), dict)
            or result["payload"].get("artifact_digest") != digest
        ):
            errors.append(f"operation pair or artifact binding differs: {operation_id}")
        start_payload = start.get("payload")
        if isinstance(start_payload, dict):
            parents = start_payload.get("internal_parent_result_digests")
            expected_parents = tuple(
                artifact_digests[parent]
                for parent in row["parent_operations"].split("|")
                if parent.startswith("hs-op-") and parent in artifact_digests
            )
            normalized_parents = tuple(parents) if isinstance(parents, list) else parents
            if normalized_parents != expected_parents:
                errors.append(f"parent binding differs: {operation_id}")

    total_bytes = journal_bytes + artifact_bytes
    if total_bytes > MAX_SUCCESS_BYTES:
        errors.append("success path exceeds total budget")
    if reservation_file_digest != artifact_digests.get("hs-op-001"):
        errors.append("reservation artifact digest differs")
    if manifest_file_digest != artifact_digests.get("hs-op-002"):
        errors.append("manifest artifact digest differs")

    expected_root = expected_evaluation_root(workspace_root)
    op53 = _artifact_result(artifacts.get("hs-op-053"))
    op52 = _artifact_result(artifacts.get("hs-op-052"))
    if (
        op52 is None
        or op52.get("evaluation_plan_digest") is not None
        or op53 is None
        or op53.get("evaluation_plan_digest") != expected_root["seal_digest"]
    ):
        errors.append("execution/evaluation root separation differs")
    if len(events) >= 105:
        op53_start = events[104]
        payload = op53_start.get("payload")
        if not isinstance(payload, dict) or payload.get("external_parent_digest") != expected_root["seal_digest"]:
            errors.append("evaluation parent is not independently bound")

    expected_by_case = dict(EXPECTED_CASE_VALUES)
    for offset, case_id in enumerate(("c01", "c02", "c03", "c04"), 54):
        finding = _artifact_result(artifacts.get(f"hs-op-{offset:03d}"))
        case_evidence = _artifact_result(
            artifacts.get({"c01": "hs-op-039", "c02": "hs-op-043", "c03": "hs-op-047", "c04": "hs-op-051"}[case_id])
        )
        if finding is None or case_evidence is None:
            errors.append(f"evaluation evidence missing: {case_id}")
            continue
        output = tuple(case_evidence.get("consumer_output", ()))
        baseline_output = tuple(case_evidence.get("baseline_output", ()))
        expected = expected_by_case[case_id]
        if (
            finding.get("expected_values_digest") != _digest(list(expected))
            or finding.get("consumer_matches_expected") != (output == expected)
            or finding.get("baseline_matches_expected") != (baseline_output == expected)
            or finding.get("consumer_equals_baseline") != (output == baseline_output)
        ):
            errors.append(f"evaluation projection differs: {case_id}")

    for operation_id in ("hs-op-016", "hs-op-032"):
        finding = _artifact_result(artifacts.get(operation_id))
        if finding is None or finding.get("prestate_digest") != finding.get("poststate_digest"):
            errors.append(f"read-only finding differs: {operation_id}")
    for operation_id in ("hs-op-037", "hs-op-038", "hs-op-041", "hs-op-042", "hs-op-045", "hs-op-046", "hs-op-049", "hs-op-050"):
        finding = _artifact_result(artifacts.get(operation_id))
        if finding is None or finding.get("prestate_digest") != finding.get("poststate_digest"):
            errors.append(f"read-only arm differs: {operation_id}")

    marker = _artifact_result(artifacts.get("hs-op-060"))
    if marker is None or marker.get("status") != "COMPLETE" or marker.get("operation_count") != 60 or marker.get("event_count") != 120:
        errors.append("completion marker differs")
    status = "RECORDING_COMPLETE" if not errors else "NOT_EVALUABLE"
    return _finding(
        status,
        run_id,
        len(artifacts),
        len(events),
        total_bytes,
        prior if events else None,
        errors,
    )


__all__: tuple[str, ...] = ()
