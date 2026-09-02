"""Independent read-only verifier for one S2-JX result file."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


S2JX_RESULT_SCHEMA = "s2jx.default-live-memory-result.v1"
FORMATION_SEQUENCE = (
    "X", "X", "X", "X", "Y", "Y", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"
)
PROBE_SEQUENCE = ("D9", "X", "Y")
FIXTURE_RECIPE_DIGEST = "de1871c8f9059ae6ef4b5b0aaabc967080e9f91eeee0bd2c2626ae061e4e054d"
EXPECTED_OPERATION_ROLES = tuple(
    role
    for phase in (("AV_PAIR", "B4_ARM", "TSPM_ARM", "COMPOSITE_VALIDATE"),) * 15
    for role in phase
) + tuple(
    role
    for phase in (("AV_PAIR", "B4_READ", "TSPM_READ", "READ_ONLY_VALIDATE"),) * 3
    for role in phase
)
SOURCE_PATHS = (
    "mcm_field_organism/_ppb1_reference.py",
    "mcm_field_organism/_tspm1_private.py",
    "mcm_field_organism/_tspm1_s2dr_private_comparison.py",
    "tools/_s2jw_default_live_profile.py",
    "tools/_s2jw_default_live_av_pairing.py",
    "tools/_s2jw_profiled_memory_ledger.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2jw_profiled_memory_read_only.py",
    "tools/_s2jx_default_live_memory_fixtures.py",
    "tools/_s2jx_default_live_memory_runner.py",
    "tools/_s2jx_default_live_memory_result_verifier.py",
)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")


@dataclass(frozen=True, slots=True)
class S2JXVerificationFinding:
    status: str
    run_id: str | None
    operation_count: int
    functional_status: str | None
    issues: tuple[str, ...]
    finding_digest: str


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


def _finding(
    status: str,
    run_id: str | None,
    operation_count: int,
    functional_status: str | None,
    issues: list[str],
) -> S2JXVerificationFinding:
    payload = {
        "status": status,
        "run_id": run_id,
        "operation_count": operation_count,
        "functional_status": functional_status,
        "issues": issues,
    }
    return S2JXVerificationFinding(
        status,
        run_id,
        operation_count,
        functional_status,
        tuple(issues),
        _digest(payload),
    )


def _raw_key_present(value: object) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str) and key in {
                "pixel_bytes",
                "pcm_bytes",
                "raw_bytes",
                "raw_payload",
            }:
                return True
            if _raw_key_present(child):
                return True
    elif isinstance(value, list):
        return any(_raw_key_present(item) for item in value)
    return False


def _evaluate(probes: object) -> dict[str, object] | None:
    if not isinstance(probes, list) or len(probes) != 3:
        return None
    by_label = {
        item.get("evaluation_label"): item
        for item in probes
        if isinstance(item, dict)
    }
    if set(by_label) != {"D9", "X", "Y"}:
        return None
    d9, x, y = by_label["D9"], by_label["X"], by_label["Y"]
    d9_b4 = d9.get("b4_selected")
    x_a = x.get("auditory_slow_selected")
    x_v = x.get("visual_slow_selected")
    claims = {
        "d9_is_b4_recent": isinstance(d9_b4, dict)
        and d9_b4.get("formation_index") == 15
        and d9_b4.get("mechanical_match") is True,
        "x_absent_from_b4": x.get("b4_selected") is None,
        "x_absent_from_fast": x.get("fast_selected") is None,
        "x_auditory_slow_support_3": isinstance(x_a, dict)
        and x_a.get("support") == 3
        and x_a.get("stable") is True
        and x_a.get("mechanical_match") is True,
        "x_visual_slow_support_3": isinstance(x_v, dict)
        and x_v.get("support") == 3
        and x_v.get("stable") is True
        and x_v.get("mechanical_match") is True,
        "y_absent_from_b4": y.get("b4_selected") is None,
        "y_absent_from_fast": y.get("fast_selected") is None,
        "y_no_public_auditory_slow": y.get("auditory_slow_selected") is None,
        "y_no_public_visual_slow": y.get("visual_slow_selected") is None,
        "all_probes_read_only": all(
            item.get("prestate_digest") == item.get("poststate_digest")
            for item in probes
        ),
    }
    return {
        "status": "S2JX_FUNCTION_CONFIRMED" if all(claims.values()) else "S2JX_FUNCTION_FALSIFIED",
        "claims": claims,
        "evaluation_digest": _digest(claims),
    }


def verify_s2jx_result(directory: Path, workspace_root: Path) -> S2JXVerificationFinding:
    issues: list[str] = []
    run_id: str | None = None
    operation_count = 0
    functional_status: str | None = None
    if not isinstance(directory, Path) or not directory.is_absolute():
        return _finding("NOT_EVALUABLE", None, 0, None, ["directory is not one absolute Path"])
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
        return _finding("NOT_EVALUABLE", None, 0, None, ["workspace_root is not one absolute Path"])
    result_path = directory / "result.json"
    if not directory.is_dir() or not result_path.is_file():
        return _finding("NOT_EVALUABLE", None, 0, None, ["atomic result file is missing"])
    if {item.name for item in directory.iterdir()} != {"result.json"}:
        issues.append("run directory contains an unregistered artifact")
    try:
        record = json.loads(result_path.read_text(encoding="ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _finding("NOT_EVALUABLE", None, 0, None, ["result is not canonical readable JSON"])
    if not isinstance(record, dict):
        return _finding("NOT_EVALUABLE", None, 0, None, ["result root is not an object"])
    run_value = record.get("run_id")
    run_id = run_value if isinstance(run_value, str) else None
    if run_id is None or _RUN_ID.fullmatch(run_id) is None or directory.name != run_id:
        issues.append("run identity differs")
    if record.get("schema") != S2JX_RESULT_SCHEMA:
        issues.append("result schema differs")
    stored_digest = record.get("record_digest")
    payload = dict(record)
    payload.pop("record_digest", None)
    if not isinstance(stored_digest, str) or stored_digest != _digest(payload):
        issues.append("record digest differs")
    if _raw_key_present(record):
        issues.append("raw payload is present")
    technical_status = record.get("technical_status")
    if technical_status == "NOT_EVALUABLE":
        return _finding("NOT_EVALUABLE", run_id, 0, None, issues or ["run recorded a technical failure"])
    if technical_status != "RECORDING_COMPLETE":
        issues.append("technical status differs")

    plan = record.get("plan")
    expected_plan = {
        "formation_sequence": list(FORMATION_SEQUENCE),
        "probe_sequence": list(PROBE_SEQUENCE),
        "formation_count": 15,
        "probe_count": 3,
        "top_level_operation_count": 72,
        "total_l1_terms": 43_680,
        "raw_payload_retained": False,
        "field_read": False,
        "context_selection": False,
        "compression_336_to_26": False,
    }
    if plan != expected_plan or record.get("fixture_recipe_digest") != FIXTURE_RECIPE_DIGEST:
        issues.append("bound plan or fixture recipe differs")

    source_hashes = record.get("source_hashes")
    if not isinstance(source_hashes, dict) or set(source_hashes) != set(SOURCE_PATHS):
        issues.append("source inventory differs")
    else:
        for relative in SOURCE_PATHS:
            path = workspace_root / relative
            if not path.is_file() or source_hashes.get(relative) != _file_digest(path):
                issues.append(f"source digest differs: {relative}")

    operations = record.get("operations")
    previous = None
    if not isinstance(operations, list) or len(operations) != 72:
        issues.append("operation count differs")
    else:
        operation_count = len(operations)
        for index, (item, role) in enumerate(zip(operations, EXPECTED_OPERATION_ROLES, strict=True), 1):
            if not isinstance(item, dict):
                issues.append(f"operation {index} is not an object")
                continue
            item_payload = dict(item)
            item_digest = item_payload.pop("operation_digest", None)
            if (
                item.get("operation_id") != f"s2jx-op-{index:03d}"
                or item.get("ordinal") != index
                or item.get("role") != role
                or item.get("parent_operation_digest") != previous
                or not isinstance(item_digest, str)
                or item_digest != _digest(item_payload)
            ):
                issues.append(f"operation chain differs at {index}")
            previous = item_digest
        if record.get("last_operation_digest") != previous:
            issues.append("last operation digest differs")

    formations = record.get("formation_evidence")
    if not isinstance(formations, list) or len(formations) != 15:
        issues.append("formation evidence count differs")
    else:
        for index, (item, label) in enumerate(zip(formations, FORMATION_SEQUENCE, strict=True), 1):
            state = item.get("state") if isinstance(item, dict) else None
            if (
                not isinstance(item, dict)
                or item.get("evaluation_label") != label
                or item.get("formation_index") != index
                or not isinstance(state, dict)
                or state.get("generation") != index
            ):
                issues.append(f"formation evidence differs at {index}")

    probes = record.get("probe_evidence")
    recomputed = _evaluate(probes)
    recorded_evaluation = record.get("functional_evaluation")
    if recomputed is None or recorded_evaluation != recomputed:
        issues.append("functional evaluation does not match recorded findings")
    elif isinstance(recorded_evaluation, dict):
        value = recorded_evaluation.get("status")
        functional_status = value if isinstance(value, str) else None
    final_state = record.get("final_state")
    final_digest = final_state.get("state_digest") if isinstance(final_state, dict) else None
    if not isinstance(probes, list) or any(
        not isinstance(item, dict)
        or item.get("prestate_digest") != final_digest
        or item.get("poststate_digest") != final_digest
        for item in probes
    ):
        issues.append("probe state identity differs")
    status = "RECORDING_COMPLETE" if not issues else "NOT_EVALUABLE"
    return _finding(status, run_id, operation_count, functional_status, issues)

