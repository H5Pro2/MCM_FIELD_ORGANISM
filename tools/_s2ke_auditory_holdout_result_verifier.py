"""Independent read-only verifier for private S2-KE result files."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from tools._s2ke_auditory_holdout_evaluator import evaluate_s2kc_evidence
from tools._s2ke_auditory_holdout_fixtures import CHECKPOINTS, FORMATION_SEQUENCE, GEOMETRY_BLOCKED, HOLDOUT_ROLES
from tools._s2ke_auditory_holdout_measurement import validate_start_gate
from tools._s2ke_auditory_holdout_runner import EXPECTED_OPERATION_ROLES, FUNCTIONAL_OPERATION_COUNT, S2KE_RESULT_SCHEMA, SOURCE_PATHS, _plan


S2KE_VERIFICATION_SCHEMA = "s2ke.auditory-holdout-verification.v1"


class S2KEVerificationError(ValueError):
    pass


def _json_bytes(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


@dataclass(frozen=True, slots=True)
class S2KEVerificationFindingV1:
    status: str
    operation_count: int
    functional_status: str | None
    result_digest: str
    finding_digest: str
    schema: str = S2KE_VERIFICATION_SCHEMA


def _validate_sources(value: object, workspace_root: Path) -> None:
    if not isinstance(value, dict) or set(value) != set(SOURCE_PATHS):
        raise S2KEVerificationError("source inventory differs")
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        if not path.is_file() or value[relative] != hashlib.sha256(path.read_bytes()).hexdigest():
            raise S2KEVerificationError("source digest differs")


def _validate_operations(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list) or len(value) != FUNCTIONAL_OPERATION_COUNT:
        raise S2KEVerificationError("operation count differs")
    previous = None
    for ordinal, (record, role) in enumerate(zip(value, EXPECTED_OPERATION_ROLES, strict=True), 1):
        if not isinstance(record, dict):
            raise S2KEVerificationError("operation form differs")
        payload = dict(record)
        stored = payload.pop("operation_digest", None)
        if (
            stored != _digest(payload)
            or payload.get("schema") != "s2ke.operation.v1"
            or payload.get("operation_id") != f"s2ke-op-{ordinal:03d}"
            or payload.get("ordinal") != ordinal
            or payload.get("role") != role
            or payload.get("parent_operation_digest") != previous
            or not isinstance(payload.get("evidence"), dict)
        ):
            raise S2KEVerificationError("operation chain differs")
        previous = stored
    return value


def _walk_has_raw(value: object) -> bool:
    if isinstance(value, dict):
        return any(str(key).lower() in {"image", "frame", "pcm", "raw", "raw_bytes", "samples", "pixels"} or _walk_has_raw(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_walk_has_raw(item) for item in value)
    return False


def _validate_evidence(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or value.get("formation_roles") != list(FORMATION_SEQUENCE) or value.get("baseline_training_roles") != list(FORMATION_SEQUENCE):
        raise S2KEVerificationError("evidence sequence differs")
    if any(role in HOLDOUT_ROLES for role in value["formation_roles"]):
        raise S2KEVerificationError("holdout entered training")
    formations, checkpoints = value.get("formation_evidence"), value.get("checkpoints")
    if not isinstance(formations, list) or len(formations) != 17 or not isinstance(checkpoints, list) or len(checkpoints) != 4:
        raise S2KEVerificationError("evidence inventory differs")
    for index, (item, role) in enumerate(zip(formations, FORMATION_SEQUENCE, strict=True), 1):
        if not isinstance(item, dict) or item.get("formation_index") != index or item.get("training_role") != role:
            raise S2KEVerificationError("formation evidence differs")
    for item, (checkpoint_id, count) in zip(checkpoints, CHECKPOINTS, strict=True):
        probes = item.get("probes") if isinstance(item, dict) else None
        if not isinstance(item, dict) or item.get("checkpoint_id") != checkpoint_id or item.get("formation_count") != count or not isinstance(probes, list) or [probe.get("probe_role") for probe in probes if isinstance(probe, dict)] != list(HOLDOUT_ROLES):
            raise S2KEVerificationError("checkpoint evidence differs")
        for probe in probes:
            baselines = probe.get("baselines") if isinstance(probe, dict) else None
            if not isinstance(probe, dict) or probe.get("prestate_digest") != probe.get("poststate_digest") or not isinstance(baselines, dict) or baselines.get("prestate_digest") != baselines.get("poststate_digest"):
                raise S2KEVerificationError("probe is not read-only")
    if _walk_has_raw(value):
        raise S2KEVerificationError("raw payload persisted")
    return value


def verify_result(result_path: Path, workspace_root: Path) -> S2KEVerificationFindingV1:
    if not isinstance(result_path, Path) or not result_path.is_absolute() or not result_path.is_file():
        raise S2KEVerificationError("result_path must be one existing absolute Path")
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
        raise S2KEVerificationError("workspace_root must be one absolute Path")
    try:
        value = json.loads(result_path.read_text(encoding="ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise S2KEVerificationError("result cannot be decoded") from exc
    if not isinstance(value, dict):
        raise S2KEVerificationError("result root differs")
    payload = dict(value)
    stored = payload.pop("record_digest", None)
    if stored != _digest(payload) or payload.get("schema") != S2KE_RESULT_SCHEMA:
        raise S2KEVerificationError("result digest or schema differs")
    _validate_sources(payload.get("source_hashes"), workspace_root)
    if payload.get("plan") != _plan():
        raise S2KEVerificationError("execution plan differs")
    try:
        preflight = validate_start_gate(payload.get("preflight"))
    except Exception as exc:
        raise S2KEVerificationError("start gate differs") from exc
    status = payload.get("technical_status")
    if status == GEOMETRY_BLOCKED:
        if preflight.get("status") != GEOMETRY_BLOCKED or payload.get("completed_operation_count") != 0 or payload.get("memory_calls") != 0 or any(key in payload for key in ("operations", "evidence", "functional_evaluation")):
            raise S2KEVerificationError("geometry stop lifecycle differs")
        finding = {"schema": S2KE_VERIFICATION_SCHEMA, "status": GEOMETRY_BLOCKED, "operation_count": 0, "functional_status": None, "result_digest": stored}
        return S2KEVerificationFindingV1(**finding, finding_digest=_digest(finding))
    if status != "RECORDING_COMPLETE" or preflight.get("status") == GEOMETRY_BLOCKED:
        finding = {"schema": S2KE_VERIFICATION_SCHEMA, "status": "NOT_EVALUABLE", "operation_count": int(payload.get("completed_operation_count", 0)), "functional_status": None, "result_digest": stored}
        return S2KEVerificationFindingV1(**finding, finding_digest=_digest(finding))
    operations = _validate_operations(payload.get("operations"))
    if payload.get("last_operation_digest") != operations[-1]["operation_digest"]:
        raise S2KEVerificationError("terminal operation binding differs")
    evidence = _validate_evidence(payload.get("evidence"))
    evaluation = evaluate_s2kc_evidence(evidence)
    if evaluation != payload.get("functional_evaluation"):
        raise S2KEVerificationError("functional evaluation differs")
    finding = {"schema": S2KE_VERIFICATION_SCHEMA, "status": "RECORDING_COMPLETE", "operation_count": len(operations), "functional_status": evaluation["status"], "result_digest": stored}
    return S2KEVerificationFindingV1(**finding, finding_digest=_digest(finding))
