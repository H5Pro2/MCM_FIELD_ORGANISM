"""Independent read-only verifier for one atomic S2-LD result."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


S2LD_RESULT_SCHEMA = "s2ld.auditory-partial-cue-result.v1"
MAX_RESULT_BYTES = 1_048_576
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
CASE_ORDER = ("LC01", "LC02", "LC03", "LC04", "LC05", "LC06")
HISTORY_IDS = ("h-a", "h-b", "h-ab", "h-ambig", "h-null")
HISTORY_LENGTHS = (1, 13, 14, 2, 0)
EXPECTED_CASES = {
    "LC01": ("ADMIT_SINGLE_CONTEXT", "A_RECENT_APPLICABLE", "B_STABLE_AUDITORY_ABSENT_VALID", "A_RECENT"),
    "LC02": ("ADMIT_SINGLE_CONTEXT", "A_RECENT_NOT_APPLICABLE", "B_STABLE_AUDITORY_APPLICABLE", "B_STABLE_AUDITORY"),
    "LC03": ("ABSTAIN_NO_APPLICABLE_CONTEXT", "A_RECENT_NOT_APPLICABLE", "B_STABLE_AUDITORY_NOT_APPLICABLE", None),
    "LC04": ("ABSTAIN_AMBIGUOUS_CONTEXT", "A_RECENT_APPLICABLE", "B_STABLE_AUDITORY_APPLICABLE", None),
    "LC05": ("ABSTAIN_INTERNAL_AMBIGUITY", "A_RECENT_INTERNAL_AMBIGUITY", "B_STABLE_AUDITORY_ABSENT_VALID", None),
    "LC06": ("ABSTAIN_NO_CONTEXT", "A_RECENT_ABSENT_VALID", "B_STABLE_AUDITORY_ABSENT_VALID", None),
}
EXPECTED_HYPOTHESIS_VALUE_DIGESTS = {
    "LC01": "4c875a43ffd3a802a74d4b5eadfc188907f43ef09676bba9fdbad3018008c97a",
    "LC02": "8408f2f4452b64cd8bf53847b91de8d8a34d29f64191c344cf8684726974191e",
}
LC02_FINAL_PROTOTYPE_DIGEST = "24c77fb0e9c027798884e33f28b8b14f0d4fde9723142a6937ab3546b203bd3e"
LC02_EVENT_CHAIN = ("CREATED", "MATCHED", "MATCHED")
LC02_SUPPORT_CHAIN = (1, 2, 3)
LC02_STEP_DIGESTS = (
    "8366a9c9724e4e0d499861af119a08f41bceb4786f594f5bac67218efe6c8616",
    "d4ac37bbb42b05f807daf7b824ac348a2dc4a2a5774948058c2c4ec1b0d48fbb",
    "91e820202c8a600bb20676166570ff9526a808d461694615ed4ea982ff70336a",
)
LC02_ORDERED_CHAIN_DIGEST = "f59a4fe5cfd1a1104af5491ee1234d2f367d55541bb4297510f7de49174424cc"
LC02_TRANSITION_EVALUATION_DIGEST = "67ba9c6e5703a52574617a13413e36727e3ec5b8fa8389e236b1299c76cfa99e"
LC02_OBSERVED_L1_DISTANCE = 7.036867813342526e-11
SOURCE_PATHS = (
    "docs/S2LC_AUDITIVER_MEMORY_SECHS_FALL_ZUSTANDSSPUR.md",
    "docs/S2LB_D_FAR_PCM_MATERIALISIERUNGSPLAN.json",
    "reports/s2kx/s2ky-auditory-partial-cue-geometry-20260903-01/materialization.json",
    "reports/s2kx/s2lb-d-far-pcm-materialization-20260904-01/materialization.json",
    "mcm_field_organism/_ppb1_reference.py",
    "mcm_field_organism/_tspm1_private.py",
    "mcm_field_organism/broadband_hearing_path.py",
    "mcm_field_organism/finite_video_path.py",
    "mcm_field_organism/log_spectral_receptor.py",
    "tools/_s2jw_default_live_profile.py",
    "tools/_s2jw_default_live_av_pairing.py",
    "tools/_s2jw_profiled_memory_ledger.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2jx_default_live_memory_fixtures.py",
    "tools/_s2kz_private_auditory_partial_cue_retrieval_336.py",
    "tools/_s2kz_private_direct_auditory_slot_scan_baseline.py",
    "tools/_s2ld_auditory_partial_cue_fixtures.py",
    "tools/_s2lg_private_ppb_transition_evaluation.py",
    "tools/_s2ld_auditory_partial_cue_runner.py",
    "tools/_s2ld_auditory_partial_cue_verifier.py",
)


@dataclass(frozen=True, slots=True)
class S2LDVerificationFinding:
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
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)[:-1]).hexdigest()


def _valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _contains_raw(value: object) -> bool:
    forbidden = {
        "raw_payload",
        "raw_bytes",
        "rgb_bytes",
        "pcm_samples",
        "image",
        "auditory_values",
        "visual_values",
        "av_values",
        "target_values",
        "observed_values",
        "proposed_values",
    }
    if isinstance(value, dict):
        return any(key in forbidden or _contains_raw(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_raw(item) for item in value)
    return False


def _semantic(value: object) -> tuple[object, object, object, object] | None:
    if not isinstance(value, dict):
        return None
    return (
        value.get("decision"),
        value.get("a_status"),
        value.get("b_status"),
        value.get("hypothesis_area"),
    )


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


def _verify_case_common(case: object, issues: list[str]) -> None:
    if not isinstance(case, dict):
        issues.append("case malformed")
        return
    primary = case.get("primary")
    direct = case.get("baseline")
    cue_source = case.get("cue_source")
    if (
        primary != direct
        or case.get("read_only") is not True
        or case.get("prestate_digest") != case.get("poststate_digest")
        or not _valid_digest(case.get("cue_digest"))
        or not isinstance(cue_source, dict)
        or cue_source.get("cue_digest") != case.get("cue_digest")
        or cue_source.get("auditory_source_clock_id") != "audio.sample"
        or not _valid_digest(cue_source.get("receipt_digest"))
        or cue_source.get("receipt_digest")
        != _digest({key: value for key, value in cue_source.items() if key != "receipt_digest"})
    ):
        issues.append("case binding or read-only relation differs")
    if isinstance(primary, dict):
        if (
            primary.get("total_slot_scans") != 20
            or type(primary.get("total_value_comparisons")) is not int
            or primary["total_value_comparisons"] > 528
            or primary.get("memory_receptor_consumer_context_or_field_calls") != 0
        ):
            issues.append("case resource bound differs")


def _verify_lc02_transition(value: object, issues: list[str]) -> tuple[bool, bool]:
    if not isinstance(value, dict):
        issues.append("LC02 transition evaluation missing")
        return False, False
    expected_keys = {
        "schema",
        "event_chain",
        "support_chain",
        "support_count",
        "ordered_chain_digest",
        "transition_step_digests",
        "prototype_full_digest",
        "hypothesis_masked_digest",
        "prototype_transition_integrity",
        "observed_l1_distance",
        "slow_threshold",
        "functional_observed_band_match",
        "transition_evaluation_digest",
        "integration_digest",
    }
    payload = {key: item for key, item in value.items() if key != "integration_digest"}
    envelope_valid = (
        set(value) == expected_keys
        and value.get("schema") == "s2lh.lc02-transition-integration.v1"
        and _valid_digest(value.get("integration_digest"))
        and value.get("integration_digest") == _digest(payload)
        and value.get("event_chain") == list(LC02_EVENT_CHAIN)
        and value.get("support_chain") == list(LC02_SUPPORT_CHAIN)
        and value.get("support_count") == 3
        and value.get("ordered_chain_digest") == LC02_ORDERED_CHAIN_DIGEST
        and value.get("transition_step_digests") == list(LC02_STEP_DIGESTS)
        and value.get("transition_evaluation_digest")
        == LC02_TRANSITION_EVALUATION_DIGEST
    )
    if not envelope_valid:
        issues.append("LC02 transition chain or integration digest differs")
    integrity = (
        envelope_valid
        and value.get("prototype_full_digest") == LC02_FINAL_PROTOTYPE_DIGEST
        and value.get("hypothesis_masked_digest")
        == EXPECTED_HYPOTHESIS_VALUE_DIGESTS["LC02"]
        and value.get("prototype_transition_integrity")
        == "PPB_TRANSITION_INTEGRITY_VALID"
    )
    functional = (
        envelope_valid
        and value.get("observed_l1_distance") == LC02_OBSERVED_L1_DISTANCE
        and value.get("slow_threshold") == 0.02
        and value.get("functional_observed_band_match")
        == "FUNCTIONAL_OBSERVED_L1_MATCH"
    )
    if not integrity:
        issues.append("LC02 prototype transition integrity differs")
    if not functional:
        issues.append("LC02 functional observed-band match differs")
    return integrity, functional


def _verify_main(record: dict[str, object], issues: list[str]) -> str | None:
    plan = record.get("plan")
    formations = record.get("formations")
    cases = record.get("cases")
    evaluation = record.get("functional_evaluation")
    expected_plan = {
        "history_ids": list(HISTORY_IDS),
        "history_lengths": list(HISTORY_LENGTHS),
        "fresh_memory_state_count": 5,
        "formation_count": 30,
        "masked_cue_count": 6,
        "full_probe_count": 0,
        "primary_decision_count": 6,
        "baseline_decision_count": 6,
        "maximum_comparisons_per_arm_case": 528,
        "functional_operation_count": 85,
        "maximum_functional_operations": 96,
        "context_fill": False,
        "field_effect": False,
        "automatic_choice": False,
    }
    if plan != expected_plan:
        issues.append("main plan differs")
    if not isinstance(formations, list) or len(formations) != 30:
        issues.append("formation count differs")
    else:
        expected_ordinals = dict(zip(HISTORY_IDS[:4], (0, 0, 0, 0), strict=True))
        prior: dict[str, object] = {}
        for item in formations:
            if not isinstance(item, dict):
                issues.append("formation entry malformed")
                continue
            history_id = item.get("history_id")
            ordinal = item.get("ordinal")
            source = item.get("source")
            if (
                history_id not in expected_ordinals
                or ordinal != expected_ordinals.get(history_id, -1) + 1
                or item.get("owner_status") != "CONSUMED"
                or not isinstance(source, dict)
                or source.get("history_id") != history_id
                or source.get("ordinal") != ordinal
                or not _valid_digest(source.get("receipt_digest"))
                or source.get("receipt_digest")
                != _digest({key: value for key, value in source.items() if key != "receipt_digest"})
            ):
                issues.append("formation order or source differs")
            elif history_id in prior and item.get("prestate_digest") != prior[history_id]:
                issues.append("formation state chain differs")
            if history_id in expected_ordinals and type(ordinal) is int:
                expected_ordinals[history_id] = ordinal
                prior[history_id] = item.get("poststate_digest")
        if tuple(expected_ordinals[key] for key in HISTORY_IDS[:4]) != HISTORY_LENGTHS[:4]:
            issues.append("per-history formation count differs")
    if (
        not isinstance(cases, list)
        or len(cases) != 6
        or [case.get("case_id") for case in cases if isinstance(case, dict)] != list(CASE_ORDER)
    ):
        issues.append("case order differs")
        return None
    claims: dict[str, bool] = {}
    for case in cases:
        _verify_case_common(case, issues)
        case_id = case["case_id"]
        primary = case.get("primary")
        claims[f"{case_id.lower()}-decision"] = _semantic(primary) == EXPECTED_CASES[case_id]
        claims[f"{case_id.lower()}-baseline"] = primary == case.get("baseline")
        claims[f"{case_id.lower()}-readonly"] = (
            case.get("read_only") is True
            and case.get("prestate_digest") == case.get("poststate_digest")
        )
        if case_id in EXPECTED_HYPOTHESIS_VALUE_DIGESTS:
            claims[f"{case_id.lower()}-hypothesis"] = (
                isinstance(primary, dict)
                and primary.get("hypothesis_values_digest")
                == EXPECTED_HYPOTHESIS_VALUE_DIGESTS[case_id]
            )
        if case_id == "LC02":
            integrity, functional = _verify_lc02_transition(
                case.get("prototype_transition_evaluation"), issues
            )
            claims["lc02-prototype-transition-integrity"] = integrity
            claims["lc02-functional-observed-band-match"] = functional
        elif case.get("prototype_transition_evaluation") is not None:
            issues.append("non-LC02 case carries prototype transition evaluation")
    expected_status = "S2LD_FUNCTION_CONFIRMED" if all(claims.values()) else "S2LD_FUNCTION_FALSIFIED"
    expected_evaluation = {
        "status": expected_status,
        "claims": claims,
        "evaluation_digest": _digest({"status": expected_status, "claims": claims}),
    }
    if evaluation != expected_evaluation:
        issues.append("functional evaluation differs")
    return expected_status


def _verify_qualification(record: dict[str, object], issues: list[str]) -> None:
    expected_plan = {
        "fresh_memory_state_count": 1,
        "formation_count": 0,
        "masked_cue_count": 1,
        "full_probe_count": 0,
        "primary_decision_count": 1,
        "baseline_decision_count": 1,
        "functional_operation_count": 5,
    }
    cases = record.get("cases")
    if record.get("plan") != expected_plan:
        issues.append("qualification plan differs")
    if record.get("formations") != [] or record.get("memory_formation_calls") != 0:
        issues.append("qualification formed memory")
    if not isinstance(cases, list) or len(cases) != 1:
        issues.append("qualification case count differs")
        return
    case = cases[0]
    _verify_case_common(case, issues)
    if not isinstance(case, dict) or case.get("case_id") != "N01" or _semantic(case.get("primary")) != (
        "ABSTAIN_NO_CONTEXT",
        "A_RECENT_ABSENT_VALID",
        "B_STABLE_AUDITORY_ABSENT_VALID",
        None,
    ):
        issues.append("qualification semantic differs")
    if isinstance(case, dict) and case.get("prototype_transition_evaluation") is not None:
        issues.append("qualification case carries prototype transition evaluation")


def verify_s2ld_result(directory: Path, workspace_root: Path) -> S2LDVerificationFinding:
    if (
        not isinstance(directory, Path)
        or not directory.is_absolute()
        or not isinstance(workspace_root, Path)
        or not workspace_root.is_absolute()
    ):
        return S2LDVerificationFinding("NOT_EVALUABLE", None, ("absolute Path required",), None)
    if not directory.is_dir() or {item.name for item in directory.iterdir()} != {"result.json"}:
        return S2LDVerificationFinding("NOT_EVALUABLE", None, ("atomic result directory differs",), None)
    target = directory / "result.json"
    if target.stat().st_size > MAX_RESULT_BYTES:
        return S2LDVerificationFinding("NOT_EVALUABLE", None, ("result size exceeds bound",), None)
    try:
        record = json.loads(target.read_text(encoding="ascii"))
    except Exception:
        return S2LDVerificationFinding("NOT_EVALUABLE", None, ("result parse failed",), None)
    issues: list[str] = []
    if not isinstance(record, dict) or record.get("schema") != S2LD_RESULT_SCHEMA:
        return S2LDVerificationFinding("NOT_EVALUABLE", None, ("result envelope differs",), None)
    stored_digest = record.get("record_digest")
    payload = {key: value for key, value in record.items() if key != "record_digest"}
    if not _valid_digest(stored_digest) or stored_digest != _digest(payload):
        issues.append("record digest differs")
    if _contains_raw(record) or record.get("raw_payload_retained") is not False:
        issues.append("raw or target payload retained")
    _verify_sources(record, workspace_root, issues)
    technical_status = record.get("technical_status")
    functional_status = None
    if technical_status == "NOT_EVALUABLE":
        if record.get("mode") != "MAIN" or record.get("functional_evaluation") is not None:
            issues.append("technical failure envelope differs")
        return S2LDVerificationFinding("NOT_EVALUABLE", None, tuple(issues), stored_digest if _valid_digest(stored_digest) else None)
    if technical_status != "RECORDING_COMPLETE":
        issues.append("technical status differs")
    if record.get("mode") == "MAIN":
        functional_status = _verify_main(record, issues)
    elif record.get("mode") == "QUALIFICATION":
        _verify_qualification(record, issues)
    else:
        issues.append("result mode differs")
    return S2LDVerificationFinding(
        "RECORDING_COMPLETE" if not issues else "NOT_EVALUABLE",
        functional_status if not issues else None,
        tuple(issues),
        stored_digest if _valid_digest(stored_digest) else None,
    )


__all__: tuple[str, ...] = ()
