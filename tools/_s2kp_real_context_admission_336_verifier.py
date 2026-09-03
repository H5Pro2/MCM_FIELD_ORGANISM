"""Independent read-only verifier for one atomic S2-KP result."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


S2KP_RESULT_SCHEMA = "s2kp.real-context-admission-336-result.v1"
CASE_ORDER = ("R1", "R2", "R3", "R4", "R5", "R6")
HISTORY_LENGTHS = (15, 14, 2)
FORMATION_COUNT = 31
FULL_PROBE_COUNT = 5
MASKED_PROBE_COUNT = 6
ADMISSION_CALL_COUNT = 12
MAX_FUNCTIONAL_OPERATIONS = 96
_DIGEST = re.compile(r"^[0-9a-f]{64}$")

SOURCE_PATHS = (
    "mcm_field_organism/_ppb1_reference.py",
    "mcm_field_organism/_tspm1_private.py",
    "mcm_field_organism/_tspm1_s2dr_private_comparison.py",
    "mcm_field_organism/broadband_hearing_path.py",
    "mcm_field_organism/finite_video_path.py",
    "mcm_field_organism/log_spectral_receptor.py",
    "tools/_s2jw_default_live_profile.py",
    "tools/_s2jw_default_live_av_pairing.py",
    "tools/_s2jw_profiled_memory_ledger.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2jw_profiled_memory_read_only.py",
    "tools/_s2jx_default_live_memory_fixtures.py",
    "tools/_s2kj_validated_perceptual_finding_336.py",
    "tools/_s2kj_two_area_perceptual_context_336.py",
    "tools/_s2kn_private_two_area_context_admission_336.py",
    "tools/_s2kn_private_direct_two_area_admission_baseline.py",
    "tools/_s2kp_real_context_admission_336_fixtures.py",
    "tools/_s2kp_real_context_admission_336_runner.py",
    "tools/_s2kp_real_context_admission_336_verifier.py",
)

EXPECTED_CASES = {
    "R1": ("ADMIT_SINGLE_CONTEXT", "A_RECENT_APPLICABLE", "B_STABLE_ABSENT_VALID", 1, "A_RECENT"),
    "R2": ("ADMIT_SINGLE_CONTEXT", "A_RECENT_ABSENT_VALID", "B_STABLE_APPLICABLE", 1, "B_STABLE"),
    "R3": ("ABSTAIN_AMBIGUOUS_CONTEXT", "A_RECENT_APPLICABLE", "B_STABLE_APPLICABLE", 2, None),
    "R4": ("ABSTAIN_A_RECENT_INTERNAL_CONFLICT", "A_RECENT_INTERNAL_CONFLICT", "B_STABLE_ABSENT_VALID", 0, None),
    "R5": ("ABSTAIN_NO_CONTEXT", "A_RECENT_ABSENT_VALID", "B_STABLE_ABSENT_VALID", 0, None),
    "R6": ("ABSTAIN_NO_APPLICABLE_CONTEXT", "A_RECENT_NOT_APPLICABLE", "B_STABLE_ABSENT_VALID", 0, None),
}


@dataclass(frozen=True, slots=True)
class S2KPVerificationFinding:
    status: str
    functional_status: str | None
    issues: tuple[str, ...]
    record_digest: str | None


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)[:-1]).hexdigest()


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _contains_raw_data(value: object) -> bool:
    forbidden = {
        "raw_payload",
        "raw_bytes",
        "rgb_bytes",
        "pcm_samples",
        "image",
        "auditory_values",
        "visual_values",
        "av_values",
    }
    if isinstance(value, dict):
        return any(key in forbidden or _contains_raw_data(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_raw_data(item) for item in value)
    return False


def _semantic_tuple(value: object) -> tuple[object, ...] | None:
    if not isinstance(value, dict):
        return None
    return (
        value.get("decision"),
        value.get("a_status"),
        value.get("b_status"),
        value.get("public_candidate_count"),
        value.get("hypothesis_area"),
    )


def _evaluate(cases: object) -> dict[str, object] | None:
    if not isinstance(cases, list):
        return None
    by_id = {item.get("case_id"): item for item in cases if isinstance(item, dict)}
    claims: dict[str, bool] = {}
    for case_id in CASE_ORDER:
        case = by_id.get(case_id)
        primary = case.get("primary") if isinstance(case, dict) else None
        baseline = case.get("baseline") if isinstance(case, dict) else None
        claims[f"{case_id.lower()}_expected_decision"] = (
            _semantic_tuple(primary) == EXPECTED_CASES[case_id]
        )
        claims[f"{case_id.lower()}_baseline_equal"] = primary == baseline
        claims[f"{case_id.lower()}_read_only"] = (
            isinstance(case, dict)
            and case.get("read_only") is True
            and case.get("prestate_digest") == case.get("poststate_digest")
        )
    confirmed = len(cases) == 6 and set(by_id) == set(CASE_ORDER) and all(claims.values())
    return {
        "status": "S2KP_FUNCTION_CONFIRMED" if confirmed else "S2KP_FUNCTION_FALSIFIED",
        "claims": claims,
        "evaluation_digest": _digest(claims),
    }


def verify_s2kp_result(directory: Path, workspace_root: Path) -> S2KPVerificationFinding:
    issues: list[str] = []
    if not isinstance(directory, Path) or not directory.is_absolute():
        return S2KPVerificationFinding("NOT_EVALUABLE", None, ("directory is not one absolute Path",), None)
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
        return S2KPVerificationFinding("NOT_EVALUABLE", None, ("workspace_root is not one absolute Path",), None)
    if not directory.is_dir():
        return S2KPVerificationFinding("NOT_EVALUABLE", None, ("result directory is missing",), None)
    files = sorted(path.name for path in directory.iterdir())
    if files != ["result.json"]:
        issues.append("result directory anatomy differs")
    path = directory / "result.json"
    if not path.is_file():
        return S2KPVerificationFinding("NOT_EVALUABLE", None, tuple(issues + ["result is missing"]), None)
    try:
        record = json.loads(path.read_text(encoding="ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return S2KPVerificationFinding("NOT_EVALUABLE", None, tuple(issues + ["result is unreadable"]), None)
    if not isinstance(record, dict):
        return S2KPVerificationFinding("NOT_EVALUABLE", None, tuple(issues + ["result root differs"]), None)

    record_digest = record.get("record_digest")
    payload = {key: value for key, value in record.items() if key != "record_digest"}
    if not _valid_digest(record_digest) or record_digest != _digest(payload):
        issues.append("record digest differs")
    if record.get("schema") != S2KP_RESULT_SCHEMA or record.get("technical_status") != "RECORDING_COMPLETE":
        issues.append("result header differs")
    if _contains_raw_data(record) or record.get("raw_payload_retained") is not False:
        issues.append("raw receptor input was retained")

    hashes = record.get("source_hashes")
    if not isinstance(hashes, dict) or set(hashes) != set(SOURCE_PATHS):
        issues.append("source inventory differs")
    else:
        for relative in SOURCE_PATHS:
            source = workspace_root / relative
            if not source.is_file() or hashes.get(relative) != _file_digest(source):
                issues.append(f"source hash differs: {relative}")

    plan = record.get("plan")
    if not isinstance(plan, dict) or (
        plan.get("history_ids") != ["h00", "h01", "h02"]
        or plan.get("history_lengths") != list(HISTORY_LENGTHS)
        or plan.get("formation_count") != FORMATION_COUNT
        or plan.get("full_probe_count") != FULL_PROBE_COUNT
        or plan.get("masked_probe_count") != MASKED_PROBE_COUNT
        or plan.get("admission_call_count") != ADMISSION_CALL_COUNT
        or plan.get("maximum_functional_operations") != MAX_FUNCTIONAL_OPERATIONS
        or plan.get("context_fill") is not False
        or plan.get("field_effect") is not False
        or plan.get("automatic_mask_detection") is not False
    ):
        issues.append("execution plan differs")

    formations = record.get("formations")
    if not isinstance(formations, list) or len(formations) != FORMATION_COUNT:
        issues.append("formation inventory differs")
    else:
        grouped: dict[str, list[dict[str, object]]] = {"h00": [], "h01": [], "h02": []}
        for item in formations:
            if not isinstance(item, dict) or item.get("history_id") not in grouped:
                issues.append("formation record differs")
                continue
            grouped[item["history_id"]].append(item)  # type: ignore[index]
            if (
                item.get("owner_status") != "CONSUMED"
                or not all(
                    _valid_digest(item.get(key))
                    for key in ("input_digest", "prestate_digest", "poststate_digest", "receipt_digest", "result_digest")
                )
            ):
                issues.append("formation binding differs")
        for history_id, expected_length in zip(("h00", "h01", "h02"), HISTORY_LENGTHS, strict=True):
            rows = grouped[history_id]
            if len(rows) != expected_length or [row.get("ordinal") for row in rows] != list(range(1, expected_length + 1)):
                issues.append(f"history order differs: {history_id}")
            for earlier, later in zip(rows, rows[1:]):
                if earlier.get("poststate_digest") != later.get("prestate_digest"):
                    issues.append(f"history chain differs: {history_id}")

    cases = record.get("cases")
    if not isinstance(cases, list) or [item.get("case_id") for item in cases if isinstance(item, dict)] != list(CASE_ORDER):
        issues.append("case inventory differs")
    elif any(
        item.get("primary") != item.get("baseline")
        or item.get("read_only") is not True
        or item.get("prestate_digest") != item.get("poststate_digest")
        or not all(
            _valid_digest(item.get(key))
            for key in (
                "context_bundle_digest",
                "retrieval_source_digest",
                "masked_probe_digest",
                "primary_result_digest",
                "baseline_result_digest",
                "prestate_digest",
                "poststate_digest",
            )
        )
        for item in cases
    ):
        issues.append("case binding or baseline equality differs")
    else:
        for item in cases:
            retrieval = item.get("retrieval")
            source = retrieval.get("source") if isinstance(retrieval, dict) else None
            if (
                not isinstance(retrieval, dict)
                or not isinstance(source, dict)
                or source.get("pairing_digest") != item.get("retrieval_source_digest")
                or retrieval.get("context_bundle_digest") != item.get("context_bundle_digest")
                or retrieval.get("prestate_digest") != item.get("prestate_digest")
                or retrieval.get("poststate_digest") != item.get("poststate_digest")
                or not all(
                    _valid_digest(retrieval.get(key))
                    for key in (
                        "memory_probe_digest",
                        "finding_digest",
                        "validated_finding_digest",
                        "context_bundle_digest",
                        "prestate_digest",
                        "poststate_digest",
                    )
                )
            ):
                issues.append("full retrieval binding differs")

    expected_evaluation = _evaluate(cases)
    functional = record.get("functional_evaluation")
    if expected_evaluation is None or functional != expected_evaluation:
        issues.append("functional evaluation differs")

    if issues:
        return S2KPVerificationFinding("NOT_EVALUABLE", None, tuple(issues), record_digest if _valid_digest(record_digest) else None)
    return S2KPVerificationFinding(
        "RECORDING_COMPLETE",
        expected_evaluation["status"],  # type: ignore[index]
        (),
        record_digest,
    )


__all__: tuple[str, ...] = ()
