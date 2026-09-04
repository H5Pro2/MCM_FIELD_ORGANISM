"""Small closed runner for the bounded S2-LD auditory partial-cue run."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re

from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as retrieval
from tools import _s2kz_private_direct_auditory_slot_scan_baseline as baseline
from tools import _s2lg_private_ppb_transition_evaluation as transition_evaluation
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits
from tools._s2ld_auditory_partial_cue_fixtures import (
    CASE_EXECUTION,
    CASE_ORDER,
    FORMATION_COUNT,
    HISTORIES,
    S2LDCueSourceReceiptV1,
    S2LDFormationSourceReceiptV1,
    S2LDSourceStream,
)


S2LD_RESULT_SCHEMA = "s2ld.auditory-partial-cue-result.v1"
MAIN_EXECUTION_ENABLED = False
AUTHORIZED_RUN_ID = "s2ld-real-auditory-partial-cue-336-20260904-01"
QUALIFICATION_ID = "s2ld-runner-qualification-20260904-01"
FORMATION_COUNT_BOUND = 30
MASKED_CUE_COUNT = 6
PRIMARY_DECISION_COUNT = 6
BASELINE_DECISION_COUNT = 6
MAX_COMPARISONS_PER_ARM_CASE = 528
MAIN_FUNCTIONAL_OPERATION_COUNT = 85
MAIN_FUNCTIONAL_OPERATION_LIMIT = 96
MAX_RESULT_BYTES = 1_048_576
_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")

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


class S2LDRunnerError(RuntimeError):
    """The closed runner cannot produce one complete atomic result."""


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


def _sealed(payload: dict[str, object]) -> dict[str, object]:
    return {**payload, "record_digest": _digest(payload)}


def source_hashes(workspace_root: Path) -> dict[str, str]:
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
        raise S2LDRunnerError("workspace_root must be one absolute Path")
    result = {}
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        if not path.is_file():
            raise S2LDRunnerError(f"bound source missing: {relative}")
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _build_config() -> coordinator.S2JVCoordinatorConfigV1:
    profile = build_s2jw_default_live_profile()
    return coordinator.build_s2jv_coordinator_config(
        tspm_config=profile.tspm_config,
        b4_capacity=profile.b4_capacity,
        ledger_limits=build_s2jv_ledger_limits(profile),
    )


def _formation_source_record(source: S2LDFormationSourceReceiptV1) -> dict[str, object]:
    return {
        name: getattr(source, name)
        for name in source.__dataclass_fields__
    }


def _cue_source_record(source: S2LDCueSourceReceiptV1) -> dict[str, object]:
    return {
        name: getattr(source, name)
        for name in source.__dataclass_fields__
    }


def _semantic(value: retrieval.AuditoryPartialCueRetrievalResultV1) -> dict[str, object]:
    return {
        "bank_statuses": [scan.status for scan in value.bank_scans],
        "eligible_counts": [scan.eligible_count for scan in value.bank_scans],
        "match_counts": [scan.match_count for scan in value.bank_scans],
        "matched_slot_digests": [list(scan.matched_slot_digests) for scan in value.bank_scans],
        "a_status": value.a_recent.status,
        "b_status": value.b_stable_auditory.status,
        "public_candidate_count": value.public_candidate_count,
        "decision": value.decision,
        "hypothesis_area": None if value.hypothesis is None else value.hypothesis.area,
        "hypothesis_values_digest": None
        if value.hypothesis is None
        else _digest(list(value.hypothesis.proposed_values)),
        "total_slot_scans": value.resource_ledger.total_slot_scan_count,
        "total_value_comparisons": value.resource_ledger.total_value_comparison_count,
        "memory_receptor_consumer_context_or_field_calls": (
            value.resource_ledger.memory_receptor_consumer_context_or_field_call_count
        ),
    }


def _capture_lc02_ppb_step(
    prestate: coordinator.S2JVCompositeStateV1,
    poststate: coordinator.S2JVCompositeStateV1,
    auditory_input: tuple[float, ...],
) -> tuple[tuple[float, ...], str, int]:
    before = prestate.tspm_state.auditory_ppb1_state
    after = poststate.tspm_state.auditory_ppb1_state
    if after.accepted_step_count != before.accepted_step_count + 1:
        raise S2LDRunnerError("LC02 PPB step count differs")
    selected = tuple(
        slot for slot in after.slots if slot.last_selected_step == after.accepted_step_count
    )
    if len(selected) != 1 or selected[0].support_count is None:
        raise S2LDRunnerError("LC02 PPB selected slot differs")
    prior = tuple(slot for slot in before.slots if slot.slot_id == selected[0].slot_id)
    if len(prior) != 1:
        raise S2LDRunnerError("LC02 PPB prior slot differs")
    event = "MATCHED" if prior[0].occupied else "CREATED"
    return auditory_input, event, selected[0].support_count


def _lc02_transition_record(
    *,
    ppb_steps: tuple[tuple[tuple[float, ...], str, int], ...],
    recorded_final_values: tuple[float, ...],
    recorded_hypothesis_values: tuple[float, ...],
    observed_cue_values: tuple[float, ...],
) -> dict[str, object]:
    if type(ppb_steps) is not tuple or len(ppb_steps) != 3:
        raise S2LDRunnerError("LC02 requires exactly three PPB transition steps")
    result = transition_evaluation.derive_and_evaluate_lc02(
        ppb_inputs=tuple(step[0] for step in ppb_steps),
        event_chain=tuple(step[1] for step in ppb_steps),
        support_chain=tuple(step[2] for step in ppb_steps),
        recorded_final_values=recorded_final_values,
        recorded_hypothesis_values=recorded_hypothesis_values,
        observed_cue_values=observed_cue_values,
    )
    payload = {
        "schema": "s2lh.lc02-transition-integration.v1",
        "event_chain": list(result.event_chain),
        "support_chain": list(result.support_chain),
        "support_count": result.support_chain[-1],
        "ordered_chain_digest": result.ordered_chain_digest,
        "transition_step_digests": [step.step_digest for step in result.steps],
        "prototype_full_digest": result.recorded_final_full_digest,
        "hypothesis_masked_digest": result.recorded_hypothesis_masked_digest,
        "prototype_transition_integrity": result.transition_integrity_status,
        "observed_l1_distance": result.observed_l1_distance,
        "slow_threshold": result.slow_threshold,
        "functional_observed_band_match": result.functional_match_status,
        "transition_evaluation_digest": result.evaluation_digest,
    }
    return {**payload, "integration_digest": _digest(payload)}


def _advance_history(
    history_id: str,
    config: coordinator.S2JVCoordinatorConfigV1,
) -> tuple[
    coordinator.S2JVCompositeStateV1,
    list[dict[str, object]],
    S2LDSourceStream,
    tuple[tuple[tuple[float, ...], str, int], ...],
]:
    stream = S2LDSourceStream(config.profile, history_id)
    state = coordinator.initial_s2jv_composite_state(config)
    records: list[dict[str, object]] = []
    lc02_steps: list[tuple[tuple[float, ...], str, int]] = []
    for ordinal, role in enumerate(HISTORIES[history_id], start=1):
        pair, source = stream.materialize_formation(role)
        bound = coordinator.bind_s2jv_coordinator_input(config=config, source=pair)
        owner = coordinator.S2JVFormationOwner(
            f"s2ld-{history_id}-owner-{ordinal:03d}",
            f"s2ld-{history_id}-auth-{ordinal:03d}",
            f"s2ld-{history_id}-consume-{ordinal:03d}",
            config.config_digest,
            state.state_digest,
            bound.input_digest,
        )
        prestate = state
        before = prestate.state_digest
        result = coordinator.advance_s2jv_atomic(
            config=config,
            prestate=state,
            source=bound,
            owner=owner,
        )
        state = result.poststate
        if history_id == "h-b" and role == "P" and ordinal in (2, 3, 4):
            lc02_steps.append(
                _capture_lc02_ppb_step(prestate, state, bound.auditory_values)
            )
        records.append(
            {
                "history_id": history_id,
                "ordinal": ordinal,
                "source": _formation_source_record(source),
                "input_digest": bound.input_digest,
                "prestate_digest": before,
                "poststate_digest": state.state_digest,
                "formation_receipt_digest": result.receipt.receipt_digest,
                "formation_result_digest": result.result_digest,
                "owner_status": result.owner_poststate.status,
            }
        )
    if state.generation != len(HISTORIES[history_id]):
        raise S2LDRunnerError("history generation differs")
    return state, records, stream, tuple(lc02_steps)


def _run_case(
    *,
    case_id: str,
    state: coordinator.S2JVCompositeStateV1,
    stream: S2LDSourceStream,
    config: coordinator.S2JVCoordinatorConfigV1,
    lc02_steps: tuple[tuple[tuple[float, ...], str, int], ...] = (),
) -> dict[str, object]:
    _, cue_role = CASE_EXECUTION[case_id]
    plan = retrieval.build_auditory_band_plan_48()
    cue, source = stream.materialize_cue(
        cue_id=f"s2ld-cue-{case_id.lower()}-{stream.next_ordinal + 1:03d}",
        cue_role=cue_role,
        config_digest=config.config_digest,
        band_plan=plan,
    )
    before = state.state_digest
    primary = retrieval.form_auditory_partial_cue_retrieval_336(
        config=config,
        state=state,
        cue=cue,
        band_plan=plan,
    )
    direct = baseline.form_direct_auditory_slot_scan_baseline_336(
        config=config,
        state=state,
        cue=cue,
        band_plan=plan,
    )
    transition_record = None
    if case_id == "LC02":
        slow_matches = tuple(
            record for record in primary.bank_scans[2].records if record.observed_match
        )
        if len(slow_matches) != 1 or primary.hypothesis is None:
            raise S2LDRunnerError("LC02 does not contain one stable auditory match")
        matched = slow_matches[0]
        slots = tuple(
            slot
            for slot in state.tspm_state.auditory_ppb1_state.slots
            if slot.slot_id == matched.slot_id
        )
        observed = tuple(cue.values[index] for index in range(24))
        if (
            len(slots) != 1
            or not slots[0].occupied
            or slots[0].support_count != matched.stable_support
            or retrieval.digest(slots[0].canonical_payload()) != matched.slot_digest
            or any(type(value) not in (int, float) for value in observed)
        ):
            raise S2LDRunnerError("LC02 stable slot binding differs")
        transition_record = _lc02_transition_record(
            ppb_steps=lc02_steps,
            recorded_final_values=slots[0].prototype_values,
            recorded_hypothesis_values=primary.hypothesis.proposed_values,
            observed_cue_values=tuple(float(value) for value in observed),
        )
    after = state.state_digest
    return {
        "case_id": case_id,
        "history_id": CASE_EXECUTION[case_id][0],
        "cue_source": _cue_source_record(source),
        "cue_digest": cue.cue_digest,
        "primary_result_digest": primary.result_digest,
        "baseline_result_digest": direct.result_digest,
        "primary": _semantic(primary),
        "baseline": _semantic(direct),
        "prototype_transition_evaluation": transition_record,
        "prestate_digest": before,
        "poststate_digest": after,
        "read_only": (
            before
            == after
            == primary.prestate_digest
            == primary.poststate_digest
            == direct.prestate_digest
            == direct.poststate_digest
        ),
    }


def evaluate_cases(cases: list[dict[str, object]]) -> dict[str, object]:
    by_id = {item.get("case_id"): item for item in cases}
    claims: dict[str, bool] = {}
    for case_id in CASE_ORDER:
        case = by_id.get(case_id)
        primary = case.get("primary") if isinstance(case, dict) else None
        direct = case.get("baseline") if isinstance(case, dict) else None
        expected = EXPECTED_CASES[case_id]
        actual = None
        if isinstance(primary, dict):
            actual = (
                primary.get("decision"),
                primary.get("a_status"),
                primary.get("b_status"),
                primary.get("hypothesis_area"),
            )
        claims[f"{case_id.lower()}-decision"] = actual == expected
        claims[f"{case_id.lower()}-baseline"] = primary == direct
        claims[f"{case_id.lower()}-readonly"] = (
            isinstance(case, dict)
            and case.get("read_only") is True
            and case.get("prestate_digest") == case.get("poststate_digest")
        )
        if case_id in EXPECTED_HYPOTHESIS_VALUE_DIGESTS:
            claims[f"{case_id.lower()}-hypothesis"] = (
                isinstance(primary, dict)
                and primary.get("hypothesis_values_digest")
                == EXPECTED_HYPOTHESIS_VALUE_DIGESTS[case_id]
            )
        if case_id == "LC02":
            transition = case.get("prototype_transition_evaluation") if isinstance(case, dict) else None
            claims["lc02-prototype-transition-integrity"] = (
                isinstance(transition, dict)
                and transition.get("support_count") == 3
                and transition.get("prototype_full_digest") == LC02_FINAL_PROTOTYPE_DIGEST
                and transition.get("hypothesis_masked_digest")
                == EXPECTED_HYPOTHESIS_VALUE_DIGESTS["LC02"]
                and transition.get("prototype_transition_integrity")
                == transition_evaluation.INTEGRITY_VALID
            )
            claims["lc02-functional-observed-band-match"] = (
                isinstance(transition, dict)
                and transition.get("functional_observed_band_match")
                == transition_evaluation.FUNCTIONAL_MATCH
            )
    status = (
        "S2LD_FUNCTION_CONFIRMED"
        if len(cases) == len(CASE_ORDER) and all(claims.values())
        else "S2LD_FUNCTION_FALSIFIED"
    )
    payload = {"status": status, "claims": claims}
    return {**payload, "evaluation_digest": _digest(payload)}


def _execute_main() -> tuple[list[dict[str, object]], list[dict[str, object]], str]:
    config = _build_config()
    states: dict[str, coordinator.S2JVCompositeStateV1] = {}
    streams: dict[str, S2LDSourceStream] = {}
    lc02_steps: tuple[tuple[tuple[float, ...], str, int], ...] = ()
    formations: list[dict[str, object]] = []
    for history_id in HISTORIES:
        states[history_id], records, streams[history_id], captured = _advance_history(
            history_id, config
        )
        if history_id == "h-b":
            lc02_steps = captured
        formations.extend(records)
    states["h-null"] = coordinator.initial_s2jv_composite_state(config)
    streams["h-null"] = S2LDSourceStream(config.profile, "h-null")
    cases = [
        _run_case(
            case_id=case_id,
            state=states[CASE_EXECUTION[case_id][0]],
            stream=streams[CASE_EXECUTION[case_id][0]],
            config=config,
            lc02_steps=lc02_steps if case_id == "LC02" else (),
        )
        for case_id in CASE_ORDER
    ]
    if len(formations) != FORMATION_COUNT_BOUND or len(cases) != MASKED_CUE_COUNT:
        raise S2LDRunnerError("main execution count differs")
    return formations, cases, config.config_digest


def _plan(mode: str) -> dict[str, object]:
    if mode == "QUALIFICATION":
        return {
            "fresh_memory_state_count": 1,
            "formation_count": 0,
            "masked_cue_count": 1,
            "full_probe_count": 0,
            "primary_decision_count": 1,
            "baseline_decision_count": 1,
            "functional_operation_count": 5,
        }
    return {
        "history_ids": list(HISTORIES) + ["h-null"],
        "history_lengths": [len(HISTORIES[key]) for key in HISTORIES] + [0],
        "fresh_memory_state_count": 5,
        "formation_count": FORMATION_COUNT_BOUND,
        "masked_cue_count": MASKED_CUE_COUNT,
        "full_probe_count": 0,
        "primary_decision_count": PRIMARY_DECISION_COUNT,
        "baseline_decision_count": BASELINE_DECISION_COUNT,
        "maximum_comparisons_per_arm_case": MAX_COMPARISONS_PER_ARM_CASE,
        "functional_operation_count": MAIN_FUNCTIONAL_OPERATION_COUNT,
        "maximum_functional_operations": MAIN_FUNCTIONAL_OPERATION_LIMIT,
        "context_fill": False,
        "field_effect": False,
        "automatic_choice": False,
    }


def neutral_qualification_record(workspace_root: Path) -> dict[str, object]:
    config = _build_config()
    state = coordinator.initial_s2jv_composite_state(config)
    stream = S2LDSourceStream(config.profile, "h-neutral")
    case = _run_case(case_id="LC06", state=state, stream=stream, config=config)
    case["case_id"] = "N01"
    case["history_id"] = "h-neutral"
    payload = {
        "schema": S2LD_RESULT_SCHEMA,
        "mode": "QUALIFICATION",
        "run_id": QUALIFICATION_ID,
        "technical_status": "RECORDING_COMPLETE",
        "source_hashes": source_hashes(workspace_root),
        "config_digest": config.config_digest,
        "plan": _plan("QUALIFICATION"),
        "formations": [],
        "cases": [case],
        "functional_evaluation": None,
        "raw_payload_retained": False,
        "memory_formation_calls": 0,
    }
    return _sealed(payload)


def write_atomic_result(directory: Path, record: dict[str, object]) -> Path:
    if not isinstance(directory, Path) or not directory.is_absolute() or directory.exists():
        raise S2LDRunnerError("result directory must be one new absolute Path")
    data = _json_bytes(record)
    if len(data) > MAX_RESULT_BYTES:
        raise S2LDRunnerError("result size exceeds the bounded atomic envelope")
    directory.mkdir(parents=True, exist_ok=False)
    pending = directory / ".result.json.pending"
    target = directory / "result.json"
    with pending.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(pending, target)
    return target


def run_main_once(output_root: Path, workspace_root: Path, run_id: str) -> Path:
    global MAIN_EXECUTION_ENABLED
    if not MAIN_EXECUTION_ENABLED:
        raise S2LDRunnerError("S2-LD main execution gate is closed")
    try:
        if run_id != AUTHORIZED_RUN_ID or _RUN_ID.fullmatch(run_id) is None:
            raise S2LDRunnerError("run_id is not the bound S2-LD run")
        if not isinstance(output_root, Path) or not output_root.is_absolute():
            raise S2LDRunnerError("output_root must be one absolute Path")
        if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
            raise S2LDRunnerError("workspace_root must be one absolute Path")
        sources = source_hashes(workspace_root)
        try:
            formations, cases, config_digest = _execute_main()
            evaluation = evaluate_cases(cases)
            technical_status = "RECORDING_COMPLETE"
            failure_code = None
        except Exception:
            formations, cases, config_digest = [], [], _build_config().config_digest
            evaluation = None
            technical_status = "NOT_EVALUABLE"
            failure_code = "S2LD_EXECUTION_FAILED"
        payload = {
            "schema": S2LD_RESULT_SCHEMA,
            "mode": "MAIN",
            "run_id": run_id,
            "technical_status": technical_status,
            "failure_code": failure_code,
            "source_hashes": sources,
            "config_digest": config_digest,
            "plan": _plan("MAIN"),
            "formations": formations,
            "cases": cases,
            "functional_evaluation": evaluation,
            "raw_payload_retained": False,
        }
        directory = output_root / run_id
        write_atomic_result(directory, _sealed(payload))
        return directory
    finally:
        MAIN_EXECUTION_ENABLED = False


__all__: tuple[str, ...] = ()
