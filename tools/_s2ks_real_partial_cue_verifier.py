"""Independent read-only verifier for one atomic S2-KS result."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


S2KS_RESULT_SCHEMA = "s2ks.real-partial-cue-result.v1"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
CASE_ORDER = ("K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8")
HISTORY_LENGTHS = (15, 14, 2, 11, 17)
SOURCE_PATHS = (
    "mcm_field_organism/_ppb1_reference.py",
    "mcm_field_organism/_tspm1_private.py",
    "mcm_field_organism/broadband_hearing_path.py",
    "mcm_field_organism/finite_video_path.py",
    "mcm_field_organism/log_spectral_receptor.py",
    "tools/_s2jw_default_live_profile.py",
    "tools/_s2jw_default_live_av_pairing.py",
    "tools/_s2jw_profiled_memory_ledger.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2kq_private_partial_cue_retrieval_336.py",
    "tools/_s2kq_private_direct_slot_scan_baseline.py",
    "tools/_s2ks_real_partial_cue_fixtures.py",
    "tools/_s2ks_real_partial_cue_runner.py",
    "tools/_s2ks_real_partial_cue_verifier.py",
)
EXPECTED_CASES = {
    "K1": ("ADMIT_SINGLE_CONTEXT", "A_RECENT_APPLICABLE", "B_STABLE_NOT_APPLICABLE", "A_RECENT"),
    "K2": ("ADMIT_SINGLE_CONTEXT", "A_RECENT_NOT_APPLICABLE", "B_STABLE_APPLICABLE", "B_STABLE"),
    "K3": ("ABSTAIN_AMBIGUOUS_CONTEXT", "A_RECENT_APPLICABLE", "B_STABLE_APPLICABLE", None),
    "K4": ("ABSTAIN_INTERNAL_AMBIGUITY", "A_RECENT_INTERNAL_AMBIGUITY", "B_STABLE_ABSENT_VALID", None),
    "K5": ("ABSTAIN_INTERNAL_CONFLICT", "A_RECENT_INTERNAL_CONFLICT", "B_STABLE_NOT_APPLICABLE", None),
    "K6": ("ABSTAIN_INTERNAL_AMBIGUITY", "A_RECENT_NOT_APPLICABLE", "B_STABLE_INTERNAL_AMBIGUITY", None),
    "K7": ("ABSTAIN_NO_CONTEXT", "A_RECENT_ABSENT_VALID", "B_STABLE_ABSENT_VALID", None),
    "K8": ("ABSTAIN_NO_APPLICABLE_CONTEXT", "A_RECENT_NOT_APPLICABLE", "B_STABLE_NOT_APPLICABLE", None),
}


@dataclass(frozen=True, slots=True)
class S2KSVerificationFinding:
    status: str
    functional_status: str | None
    issues: tuple[str, ...]
    record_digest: str | None


def _bytes(value: object) -> bytes:
    return (json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_bytes(value)[:-1]).hexdigest()


def _valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _contains_raw(value: object) -> bool:
    forbidden = {"raw_payload", "raw_bytes", "rgb_bytes", "pcm_samples", "image", "visual_values", "auditory_values", "av_values", "target_values"}
    if isinstance(value, dict):
        return any(key in forbidden or _contains_raw(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_raw(item) for item in value)
    return False


def _semantic(value: object):
    if not isinstance(value, dict):
        return None
    return value.get("decision"), value.get("a_status"), value.get("b_status"), value.get("hypothesis_area")


def _verify_sources(record: dict[str, object], workspace_root: Path, issues: list[str]) -> None:
    sources = record.get("source_hashes")
    if not isinstance(sources, dict) or set(sources) != set(SOURCE_PATHS):
        issues.append("bound source set differs")
        return
    for relative, expected in sources.items():
        if type(relative) is not str or not _valid_digest(expected):
            issues.append("source binding malformed")
            continue
        path = workspace_root / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            issues.append(f"source hash differs: {relative}")


def _verify_main(record: dict[str, object], issues: list[str]) -> str | None:
    plan = record.get("plan")
    formations = record.get("formations")
    cases = record.get("cases")
    evaluation = record.get("functional_evaluation")
    if not isinstance(plan, dict) or (
        plan.get("history_lengths") != list(HISTORY_LENGTHS)
        or plan.get("formation_count") != 59 or plan.get("fresh_null_state_count") != 1
        or plan.get("masked_cue_count") != 8 or plan.get("full_probe_count") != 0
        or plan.get("primary_decision_count") != 8 or plan.get("baseline_decision_count") != 8
        or plan.get("maximum_comparisons_per_arm_case") != 800
        or plan.get("maximum_functional_operations") != 160
        or plan.get("context_fill") is not False or plan.get("field_effect") is not False
        or plan.get("automatic_choice") is not False
    ):
        issues.append("main plan differs")
    if not isinstance(formations, list) or len(formations) != 59:
        issues.append("formation count differs")
    else:
        prior = {}
        ordinals = {f"h0{index}": 0 for index in range(5)}
        for item in formations:
            if not isinstance(item, dict):
                issues.append("formation entry malformed")
                continue
            history = item.get("history_id")
            ordinal = item.get("ordinal")
            if history not in ordinals or ordinal != ordinals[history] + 1 or item.get("owner_status") != "CONSUMED":
                issues.append("formation order differs")
            elif history in prior and item.get("prestate_digest") != prior[history]:
                issues.append("formation chain differs")
            if history in ordinals:
                ordinals[history] = int(ordinal) if type(ordinal) is int else -1
                prior[history] = item.get("poststate_digest")
        if tuple(ordinals[key] for key in sorted(ordinals)) != HISTORY_LENGTHS:
            issues.append("per-history formation count differs")
    if not isinstance(cases, list) or len(cases) != 8 or [item.get("case_id") for item in cases if isinstance(item, dict)] != list(CASE_ORDER):
        issues.append("case order differs")
    else:
        claims = {}
        targets = evaluation.get("target_masked_value_digests") if isinstance(evaluation, dict) else None
        for case in cases:
            case_id = case["case_id"]
            primary = case.get("primary")
            direct = case.get("baseline")
            expected = EXPECTED_CASES[case_id]
            claims[f"{case_id.lower()}-decision"] = _semantic(primary) == expected
            claims[f"{case_id.lower()}-baseline"] = primary == direct
            claims[f"{case_id.lower()}-readonly"] = case.get("read_only") is True and case.get("prestate_digest") == case.get("poststate_digest")
            if isinstance(primary, dict):
                if primary.get("total_slot_scans") != 16 or not isinstance(primary.get("total_value_comparisons"), int) or primary["total_value_comparisons"] > 800:
                    issues.append(f"resource bound differs: {case_id}")
                if primary.get("memory_receptor_consumer_or_field_calls") != 0:
                    issues.append(f"read-only ledger differs: {case_id}")
            if expected[3] is not None:
                claims[f"{case_id.lower()}-target"] = isinstance(primary, dict) and isinstance(targets, dict) and primary.get("hypothesis_values_digest") == targets.get(case_id)
        expected_status = "S2KS_FUNCTION_CONFIRMED" if all(claims.values()) else "S2KS_FUNCTION_FALSIFIED"
        if not isinstance(evaluation, dict) or evaluation.get("claims") != claims or evaluation.get("status") != expected_status:
            issues.append("functional evaluation differs")
        return expected_status
    return None


def _verify_qualification(record: dict[str, object], issues: list[str]) -> None:
    plan = record.get("plan")
    cases = record.get("cases")
    if not isinstance(plan, dict) or plan != {"formation_count": 0, "masked_cue_count": 1, "primary_decision_count": 1, "baseline_decision_count": 1, "full_probe_count": 0}:
        issues.append("qualification plan differs")
    if record.get("formations") != [] or record.get("memory_formation_calls") != 0:
        issues.append("qualification formed memory")
    if (
        not isinstance(cases, list)
        or len(cases) != 1
        or not isinstance(cases[0], dict)
        or cases[0].get("primary") != cases[0].get("baseline")
        or cases[0].get("read_only") is not True
        or cases[0].get("prestate_digest") != cases[0].get("poststate_digest")
        or not _valid_digest(cases[0].get("cue_digest"))
    ):
        issues.append("qualification case differs")


def verify_s2ks_result(directory: Path, workspace_root: Path) -> S2KSVerificationFinding:
    if not isinstance(directory, Path) or not directory.is_absolute() or not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
        return S2KSVerificationFinding("NOT_EVALUABLE", None, ("absolute Path required",), None)
    issues = []
    if not directory.is_dir() or {item.name for item in directory.iterdir()} != {"result.json"}:
        return S2KSVerificationFinding("NOT_EVALUABLE", None, ("atomic result directory differs",), None)
    try:
        record = json.loads((directory / "result.json").read_text(encoding="ascii"))
    except Exception:
        return S2KSVerificationFinding("NOT_EVALUABLE", None, ("result parse failed",), None)
    if not isinstance(record, dict) or record.get("schema") != S2KS_RESULT_SCHEMA or record.get("technical_status") != "RECORDING_COMPLETE":
        issues.append("result envelope differs")
    stored_digest = record.get("record_digest")
    payload = {key: value for key, value in record.items() if key != "record_digest"}
    if not _valid_digest(stored_digest) or stored_digest != _digest(payload):
        issues.append("record digest differs")
    if _contains_raw(record) or record.get("raw_payload_retained") is not False:
        issues.append("raw or target payload retained")
    _verify_sources(record, workspace_root, issues)
    functional_status = None
    if record.get("mode") == "MAIN":
        functional_status = _verify_main(record, issues)
    elif record.get("mode") == "QUALIFICATION":
        _verify_qualification(record, issues)
    else:
        issues.append("result mode differs")
    return S2KSVerificationFinding("RECORDING_COMPLETE" if not issues else "NOT_EVALUABLE", functional_status if not issues else None, tuple(issues), stored_digest if _valid_digest(stored_digest) else None)


__all__: tuple[str, ...] = ()
