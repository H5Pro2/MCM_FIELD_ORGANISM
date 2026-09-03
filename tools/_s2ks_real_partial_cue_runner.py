"""Small closed runner for the bounded S2-KS real partial-cue experiment."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re

from tools import _s2kq_private_direct_slot_scan_baseline as baseline
from tools import _s2kq_private_partial_cue_retrieval_336 as retrieval
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits
from tools._s2ks_real_partial_cue_fixtures import (
    CASE_EXECUTION, CASE_ORDER, FORMATION_COUNT, HISTORIES,
    S2KSFormationStream, S2KSMaskedSourceReceiptV1,
    evaluation_target_masked_values, materialize_masked_cue,
)


S2KS_RESULT_SCHEMA = "s2ks.real-partial-cue-result.v1"
MAIN_EXECUTION_ENABLED = False
AUTHORIZED_RUN_ID = "s2ks-real-partial-cue-336-20260903-02"
MASKED_CUE_COUNT = 8
PRIMARY_DECISION_COUNT = 8
BASELINE_DECISION_COUNT = 8
MAX_COMPARISONS_PER_ARM_CASE = 800
MAX_FUNCTIONAL_OPERATIONS = 160
_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")

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
EVALUATION_TARGETS = {
    "K1": "D9", "K2": "X", "K3": "A0", "K4": "C1",
    "K5": "FT", "K6": "S0", "K7": "S0", "K8": "D9",
}

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


class S2KSRunnerError(RuntimeError):
    """The closed runner cannot produce one complete atomic result."""


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)[:-1]).hexdigest()


def source_hashes(workspace_root: Path) -> dict[str, str]:
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
        raise S2KSRunnerError("workspace_root must be one absolute Path")
    result = {}
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        if not path.is_file():
            raise S2KSRunnerError(f"bound source missing: {relative}")
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _build_config() -> coordinator.S2JVCoordinatorConfigV1:
    profile = build_s2jw_default_live_profile()
    return coordinator.build_s2jv_coordinator_config(
        tspm_config=profile.tspm_config,
        b4_capacity=profile.b4_capacity,
        ledger_limits=build_s2jv_ledger_limits(profile),
    )


def _source_record(source: object) -> dict[str, object]:
    return {name: getattr(source, name) for name in (
        "history_id", "source_id", "ordinal", "pairing_digest",
        "visual_payload_digest", "auditory_payload_digest",
        "visual_values_digest", "auditory_values_digest",
        "overlap_start_tick", "overlap_end_tick",
    )}


def _masked_source_record(source: S2KSMaskedSourceReceiptV1) -> dict[str, object]:
    return {name: getattr(source, name) for name in (
        "history_id", "cue_id", "ordinal", "occluded_rgb_digest",
        "occluded_receptor_values_digest", "visible_values_digest",
        "mask_digest", "window_start_tick", "window_end_tick",
        "visual_source_clock_id", "visual_window_start_tick", "visual_window_end_tick",
    )}


def _semantic(value: retrieval.PartialCueRetrievalResult336V1) -> dict[str, object]:
    return {
        "decision": value.decision,
        "a_status": value.a_recent.status,
        "b_status": value.b_stable.status,
        "public_candidate_count": value.public_candidate_count,
        "hypothesis_area": None if value.hypothesis is None else value.hypothesis.area,
        "hypothesis_values_digest": None if value.hypothesis is None else _digest(list(value.hypothesis.proposed_values)),
        "total_slot_scans": value.resource_ledger.total_slot_scan_count,
        "total_value_comparisons": value.resource_ledger.total_value_comparison_count,
        "memory_receptor_consumer_or_field_calls": value.resource_ledger.memory_receptor_consumer_or_field_call_count,
    }


def _advance_history(history_id: str, config: coordinator.S2JVCoordinatorConfigV1):
    stream = S2KSFormationStream(config.profile, history_id)
    state = coordinator.initial_s2jv_composite_state(config)
    records = []
    for ordinal, recipe_id in enumerate(HISTORIES[history_id], start=1):
        pair, source = stream.materialize(recipe_id)
        bound = coordinator.bind_s2jv_coordinator_input(config=config, source=pair)
        owner = coordinator.S2JVFormationOwner(
            f"s2ks-{history_id}-owner-{ordinal:03d}",
            f"s2ks-{history_id}-auth-{ordinal:03d}",
            f"s2ks-{history_id}-consume-{ordinal:03d}",
            config.config_digest, state.state_digest, bound.input_digest,
        )
        before = state.state_digest
        result = coordinator.advance_s2jv_atomic(config=config, prestate=state, source=bound, owner=owner)
        state = result.poststate
        records.append({
            "history_id": history_id, "ordinal": ordinal, "recipe_id": recipe_id,
            "source": _source_record(source), "input_digest": bound.input_digest,
            "prestate_digest": before, "poststate_digest": state.state_digest,
            "formation_receipt_digest": result.receipt.receipt_digest,
            "formation_result_digest": result.result_digest,
            "owner_status": result.owner_poststate.status,
        })
    if state.generation != len(HISTORIES[history_id]):
        raise S2KSRunnerError("history generation differs")
    return state, records, stream.next_ordinal


def _run_case(*, case_id: str, state: coordinator.S2JVCompositeStateV1,
              config: coordinator.S2JVCoordinatorConfigV1, cue_ordinal: int,
              visible_recipe_id: str) -> dict[str, object]:
    history_id = CASE_EXECUTION[case_id][0]
    cue, source = materialize_masked_cue(
        profile=config.profile, history_id=history_id, cue_id=f"cue-{case_id.lower()}",
        ordinal=cue_ordinal, visible_recipe_id=visible_recipe_id,
        config_digest=config.config_digest,
    )
    before = state.state_digest
    primary = retrieval.form_partial_cue_retrieval_336(config=config, state=state, cue=cue)
    direct = baseline.form_direct_partial_cue_slot_scan_baseline_336(config=config, state=state, cue=cue)
    after = state.state_digest
    primary_semantic = _semantic(primary)
    baseline_semantic = _semantic(direct)
    return {
        "case_id": case_id, "history_id": history_id,
        "masked_source": _masked_source_record(source), "cue_digest": cue.cue_digest,
        "primary_result_digest": primary.result_digest, "baseline_result_digest": direct.result_digest,
        "primary": primary_semantic, "baseline": baseline_semantic,
        "prestate_digest": before, "poststate_digest": after,
        "read_only": before == after == primary.prestate_digest == primary.poststate_digest == direct.prestate_digest == direct.poststate_digest,
    }


def evaluate_cases(cases: list[dict[str, object]]) -> dict[str, object]:
    by_id = {item.get("case_id"): item for item in cases}
    claims = {}
    targets = {}
    for case_id in CASE_ORDER:
        case = by_id.get(case_id)
        semantic = case.get("primary") if isinstance(case, dict) else None
        direct = case.get("baseline") if isinstance(case, dict) else None
        expected = EXPECTED_CASES[case_id]
        actual = None if not isinstance(semantic, dict) else (
            semantic.get("decision"), semantic.get("a_status"),
            semantic.get("b_status"), semantic.get("hypothesis_area"),
        )
        target_digest = _digest(list(evaluation_target_masked_values(EVALUATION_TARGETS[case_id])))
        targets[case_id] = target_digest
        claims[f"{case_id.lower()}-decision"] = actual == expected
        claims[f"{case_id.lower()}-baseline"] = semantic == direct
        claims[f"{case_id.lower()}-readonly"] = isinstance(case, dict) and case.get("read_only") is True and case.get("prestate_digest") == case.get("poststate_digest")
        if expected[3] is not None:
            claims[f"{case_id.lower()}-target"] = isinstance(semantic, dict) and semantic.get("hypothesis_values_digest") == target_digest
    status = "S2KS_FUNCTION_CONFIRMED" if len(cases) == 8 and all(claims.values()) else "S2KS_FUNCTION_FALSIFIED"
    return {"status": status, "claims": claims, "target_masked_value_digests": targets, "evaluation_digest": _digest({"claims": claims, "targets": targets})}


def _execute_main() -> tuple[list[dict[str, object]], list[dict[str, object]], str]:
    config = _build_config()
    states = {}
    next_ordinals = {}
    formations = []
    for history_id in HISTORIES:
        states[history_id], records, next_ordinals[history_id] = _advance_history(history_id, config)
        formations.extend(records)
    states["null"] = coordinator.initial_s2jv_composite_state(config)
    next_ordinals["null"] = 0
    cases = []
    per_history_cues = {key: 0 for key in next_ordinals}
    for case_id in CASE_ORDER:
        history_id, visible_recipe = CASE_EXECUTION[case_id]
        ordinal = next_ordinals[history_id] + per_history_cues[history_id]
        cases.append(_run_case(case_id=case_id, state=states[history_id], config=config, cue_ordinal=ordinal, visible_recipe_id=visible_recipe))
        per_history_cues[history_id] += 1
    if len(formations) != 59 or len(cases) != 8:
        raise S2KSRunnerError("main execution count differs")
    return formations, cases, config.config_digest


def _sealed(payload: dict[str, object]) -> dict[str, object]:
    return {**payload, "record_digest": _digest(payload)}


def write_atomic_result(directory: Path, record: dict[str, object]) -> Path:
    if not isinstance(directory, Path) or not directory.is_absolute() or directory.exists():
        raise S2KSRunnerError("result directory must be one new absolute Path")
    directory.mkdir(parents=True, exist_ok=False)
    target = directory / "result.json"
    pending = directory / ".result.json.pending"
    data = _json_bytes(record)
    with pending.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(pending, target)
    return target


def neutral_qualification_record(workspace_root: Path) -> dict[str, object]:
    config = _build_config()
    state = coordinator.initial_s2jv_composite_state(config)
    cue, source = materialize_masked_cue(
        profile=config.profile, history_id="neutral", cue_id="cue-neutral",
        ordinal=0, visible_recipe_id="S0", config_digest=config.config_digest,
    )
    primary = retrieval.form_partial_cue_retrieval_336(config=config, state=state, cue=cue)
    direct = baseline.form_direct_partial_cue_slot_scan_baseline_336(config=config, state=state, cue=cue)
    case = {
        "case_id": "N1", "history_id": "neutral", "masked_source": _masked_source_record(source),
        "cue_digest": cue.cue_digest, "primary_result_digest": primary.result_digest,
        "baseline_result_digest": direct.result_digest, "primary": _semantic(primary),
        "baseline": _semantic(direct), "prestate_digest": state.state_digest,
        "poststate_digest": state.state_digest, "read_only": True,
    }
    payload = {
        "schema": S2KS_RESULT_SCHEMA, "mode": "QUALIFICATION",
        "run_id": "s2ks-neutral-runner-qualification",
        "technical_status": "RECORDING_COMPLETE", "source_hashes": source_hashes(workspace_root),
        "config_digest": config.config_digest,
        "plan": {"formation_count": 0, "masked_cue_count": 1, "primary_decision_count": 1, "baseline_decision_count": 1, "full_probe_count": 0},
        "formations": [], "cases": [case], "functional_evaluation": None,
        "raw_payload_retained": False, "memory_formation_calls": 0,
    }
    return _sealed(payload)


def run_main_once(output_root: Path, workspace_root: Path, run_id: str) -> Path:
    global MAIN_EXECUTION_ENABLED
    if not MAIN_EXECUTION_ENABLED:
        raise S2KSRunnerError("S2-KS main execution gate is closed")
    try:
        if run_id != AUTHORIZED_RUN_ID or _RUN_ID.fullmatch(run_id) is None:
            raise S2KSRunnerError("run_id is not the bound S2-KS run")
        if not isinstance(output_root, Path) or not output_root.is_absolute():
            raise S2KSRunnerError("output_root must be one absolute Path")
        if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
            raise S2KSRunnerError("workspace_root must be one absolute Path")
        formations, cases, config_digest = _execute_main()
        evaluation = evaluate_cases(cases)
        payload = {
            "schema": S2KS_RESULT_SCHEMA, "mode": "MAIN", "run_id": run_id,
            "technical_status": "RECORDING_COMPLETE", "source_hashes": source_hashes(workspace_root),
            "config_digest": config_digest,
            "plan": {
                "history_ids": list(HISTORIES), "history_lengths": [len(HISTORIES[key]) for key in HISTORIES],
                "fresh_null_state_count": 1, "formation_count": FORMATION_COUNT,
                "masked_cue_count": MASKED_CUE_COUNT, "full_probe_count": 0,
                "primary_decision_count": PRIMARY_DECISION_COUNT,
                "baseline_decision_count": BASELINE_DECISION_COUNT,
                "maximum_comparisons_per_arm_case": MAX_COMPARISONS_PER_ARM_CASE,
                "maximum_functional_operations": MAX_FUNCTIONAL_OPERATIONS,
                "context_fill": False, "field_effect": False, "automatic_choice": False,
            },
            "formations": formations, "cases": cases, "functional_evaluation": evaluation,
            "raw_payload_retained": False,
        }
        directory = output_root / run_id
        write_atomic_result(directory, _sealed(payload))
        return directory
    finally:
        MAIN_EXECUTION_ENABLED = False


__all__: tuple[str, ...] = ()
