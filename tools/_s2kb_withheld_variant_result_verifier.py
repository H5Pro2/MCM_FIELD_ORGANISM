"""Independent read-only verifier for private S2-KB result files."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from tools._s2kb_withheld_variant_evaluator import evaluate_s2ka_evidence
from tools._s2kb_withheld_variant_fixtures import (
    CHECKPOINTS,
    FIXTURE_RECIPE_DIGEST,
    FORMATION_SEQUENCE,
    HOLDOUT_ROLES,
)
from tools._s2kb_withheld_variant_measurement import validate_preflight_payload


S2KB_VERIFICATION_SCHEMA = "s2kb.withheld-variant-verification.v1"
S2KB_RESULT_SCHEMA = "s2kb.withheld-variant-result.v1"
FUNCTIONAL_OPERATION_COUNT = 157
SOURCE_PATHS = (
    "mcm_field_organism/_ppb1_reference.py",
    "mcm_field_organism/_tspm1_private.py",
    "mcm_field_organism/_tspm1_s2dr_private_comparison.py",
    "tools/_s2jw_default_live_profile.py",
    "tools/_s2jw_default_live_av_pairing.py",
    "tools/_s2jw_profiled_memory_ledger.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2jw_profiled_memory_read_only.py",
    "tools/_s2kb_withheld_variant_fixtures.py",
    "tools/_s2kb_withheld_variant_measurement.py",
    "tools/_s2kb_withheld_variant_evaluator.py",
    "tools/_s2kb_withheld_variant_runner.py",
    "tools/_s2kb_withheld_variant_result_verifier.py",
)


class S2KBVerificationError(ValueError):
    """One persisted S2-KB result is incomplete or contradictory."""


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expected_roles() -> tuple[str, ...]:
    roles: list[str] = []
    checkpoints = {count for _, count in CHECKPOINTS}
    for formation_count in range(18):
        if formation_count in checkpoints:
            for _ in HOLDOUT_ROLES:
                roles.extend((
                    "AV_MATERIALIZE", "MEMORY_PROBE_BIND", "B4_READ", "TSPM_READ",
                    "READ_ONLY_VALIDATE", "FROZEN_BASELINE_READ",
                    "REPLAY_BASELINE_READ", "ADAPTIVE_BASELINE_READ",
                ))
        if formation_count == 17:
            break
        roles.extend((
            "AV_MATERIALIZE", "MEMORY_SOURCE_BIND", "B4_FORMATION",
            "TSPM_FORMATION", "COMPOSITE_VALIDATE",
        ))
        if 1 <= formation_count <= 7:
            roles.append("ADAPTIVE_BASELINE_UPDATE")
    roles.append("EVALUATE")
    if len(roles) != FUNCTIONAL_OPERATION_COUNT:
        raise S2KBVerificationError("internal operation registry differs")
    return tuple(roles)


EXPECTED_OPERATION_ROLES = _expected_roles()


@dataclass(frozen=True, slots=True)
class S2KBVerificationFindingV1:
    status: str
    operation_count: int
    functional_status: str | None
    result_digest: str
    finding_digest: str
    schema: str = S2KB_VERIFICATION_SCHEMA


def _validate_sources(value: object, workspace_root: Path) -> None:
    if not isinstance(value, dict) or set(value) != set(SOURCE_PATHS):
        raise S2KBVerificationError("source inventory differs")
    for relative in SOURCE_PATHS:
        if value[relative] != _file_digest(workspace_root / relative):
            raise S2KBVerificationError("source digest differs")


def _validate_plan(value: object) -> None:
    if not isinstance(value, dict):
        raise S2KBVerificationError("plan is missing")
    expected = {
        "formation_sequence": list(FORMATION_SEQUENCE),
        "checkpoints": [list(item) for item in CHECKPOINTS],
        "probe_roles": list(HOLDOUT_ROLES),
        "formation_count": 17,
        "probe_count": 8,
        "functional_operation_count": 157,
        "memory_operation_count": 100,
        "baseline_operation_count": 31,
        "memory_l1_limit": 133_344,
        "total_l1_limit": 156_864,
        "preflight_visual_analyses": 13,
        "preflight_audio_hops": 130,
        "preflight_raw_bytes": 81_120_000,
        "main_visual_analyses": 25,
        "main_audio_hops": 250,
        "main_raw_bytes": 156_000_000,
        "raw_payload_retained": False,
        "field_read": False,
        "context_used": False,
        "thresholds_changed": False,
    }
    if value != expected:
        raise S2KBVerificationError("execution plan differs")


def _validate_operations(value: object) -> None:
    if not isinstance(value, list) or len(value) != FUNCTIONAL_OPERATION_COUNT:
        raise S2KBVerificationError("operation count differs")
    previous = None
    for ordinal, (record, role) in enumerate(zip(value, EXPECTED_OPERATION_ROLES, strict=True), 1):
        if not isinstance(record, dict):
            raise S2KBVerificationError("operation form differs")
        payload = dict(record)
        stored = payload.pop("operation_digest", None)
        if (
            stored != _digest(payload)
            or payload.get("schema") != "s2kb.operation.v1"
            or payload.get("operation_id") != f"s2kb-op-{ordinal:03d}"
            or payload.get("ordinal") != ordinal
            or payload.get("role") != role
            or payload.get("parent_operation_digest") != previous
            or not isinstance(payload.get("evidence"), dict)
        ):
            raise S2KBVerificationError("operation chain differs")
        previous = stored


def _walk_has_raw(value: object) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = str(key).lower()
            if lowered in {"image", "frame", "pcm", "raw", "raw_bytes", "samples", "pixels"}:
                return True
            if _walk_has_raw(item):
                return True
    elif isinstance(value, list):
        return any(_walk_has_raw(item) for item in value)
    return False


def _validate_evidence(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise S2KBVerificationError("evidence is missing")
    if value.get("formation_roles") != list(FORMATION_SEQUENCE):
        raise S2KBVerificationError("formation sequence differs")
    if value.get("baseline_training_roles") != list(FORMATION_SEQUENCE):
        raise S2KBVerificationError("baseline training sequence differs")
    if any(role in HOLDOUT_ROLES for role in value["formation_roles"]):
        raise S2KBVerificationError("holdout leaked into memory training")
    if any(role in HOLDOUT_ROLES for role in value["baseline_training_roles"]):
        raise S2KBVerificationError("holdout leaked into baseline training")
    formations = value.get("formation_evidence")
    checkpoints = value.get("checkpoints")
    if not isinstance(formations, list) or len(formations) != 17:
        raise S2KBVerificationError("formation evidence differs")
    if not isinstance(checkpoints, list) or len(checkpoints) != 4:
        raise S2KBVerificationError("checkpoint evidence differs")
    for index, (item, role) in enumerate(zip(formations, FORMATION_SEQUENCE, strict=True), 1):
        if not isinstance(item, dict) or item.get("formation_index") != index or item.get("training_role") != role:
            raise S2KBVerificationError("formation evidence order differs")
    for item, (checkpoint_id, count) in zip(checkpoints, CHECKPOINTS, strict=True):
        if not isinstance(item, dict) or item.get("checkpoint_id") != checkpoint_id or item.get("formation_count") != count:
            raise S2KBVerificationError("checkpoint identity differs")
        probes = item.get("probes")
        if not isinstance(probes, list) or [probe.get("probe_role") for probe in probes if isinstance(probe, dict)] != list(HOLDOUT_ROLES):
            raise S2KBVerificationError("checkpoint probes differ")
        for probe in probes:
            if (
                not isinstance(probe, dict)
                or probe.get("prestate_digest") != probe.get("poststate_digest")
                or not isinstance(probe.get("baselines"), dict)
                or probe["baselines"].get("baseline_prestate_digest")
                != probe["baselines"].get("baseline_poststate_digest")
            ):
                raise S2KBVerificationError("probe is not read-only")
    if _walk_has_raw(value):
        raise S2KBVerificationError("raw source payload persisted")
    return value


def verify_result(result_path: Path, workspace_root: Path) -> S2KBVerificationFindingV1:
    if not isinstance(result_path, Path) or not result_path.is_absolute() or not result_path.is_file():
        raise S2KBVerificationError("result_path must be one existing absolute Path")
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
        raise S2KBVerificationError("workspace_root must be one absolute Path")
    try:
        value = json.loads(result_path.read_text(encoding="ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise S2KBVerificationError("result cannot be decoded") from exc
    if not isinstance(value, dict):
        raise S2KBVerificationError("result root differs")
    payload = dict(value)
    stored = payload.pop("record_digest", None)
    if stored != _digest(payload) or payload.get("schema") != S2KB_RESULT_SCHEMA:
        raise S2KBVerificationError("result digest or schema differs")
    _validate_sources(payload.get("source_hashes"), workspace_root)
    if payload.get("technical_status") != "RECORDING_COMPLETE":
        finding_payload = {
            "schema": S2KB_VERIFICATION_SCHEMA,
            "status": "NOT_EVALUABLE",
            "operation_count": int(payload.get("completed_operation_count", 0)),
            "functional_status": None,
            "result_digest": stored,
        }
        return S2KBVerificationFindingV1(**finding_payload, finding_digest=_digest(finding_payload))
    if payload.get("fixture_recipe_digest") != FIXTURE_RECIPE_DIGEST:
        raise S2KBVerificationError("fixture recipe differs")
    _validate_plan(payload.get("plan"))
    try:
        validate_preflight_payload(payload.get("preflight"))
    except Exception as exc:
        raise S2KBVerificationError("preflight evidence differs") from exc
    operations = payload.get("operations")
    _validate_operations(operations)
    if payload.get("last_operation_digest") != operations[-1]["operation_digest"]:
        raise S2KBVerificationError("terminal operation binding differs")
    evidence = _validate_evidence(payload.get("evidence"))
    evaluation = evaluate_s2ka_evidence(evidence)
    if evaluation != payload.get("functional_evaluation"):
        raise S2KBVerificationError("functional evaluation differs")
    finding_payload = {
        "schema": S2KB_VERIFICATION_SCHEMA,
        "status": "RECORDING_COMPLETE",
        "operation_count": len(operations),
        "functional_status": evaluation["status"],
        "result_digest": stored,
    }
    return S2KBVerificationFindingV1(**finding_payload, finding_digest=_digest(finding_payload))
