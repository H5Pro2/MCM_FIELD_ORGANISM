"""Minimal private one-shot runner for real S2-KP 336-value admission cases."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re

from tools import _s2kj_two_area_perceptual_context_336 as context_projection
from tools import _s2kj_validated_perceptual_finding_336 as finding_binding
from tools import _s2kn_private_direct_two_area_admission_baseline as direct_baseline
from tools import _s2kn_private_two_area_context_admission_336 as admission
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2jw_profiled_memory_read_only as read_only
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits
from tools._s2kp_real_context_admission_336_fixtures import (
    CASE_ORDER,
    FORMATION_COUNT,
    FULL_PROBE_COUNT,
    HISTORIES,
    MASKED_PROBE_COUNT,
    S2KPFixtureStream,
    S2KPSourceSummaryV1,
    assert_strictly_later,
    masked_visual_values,
)


S2KP_RESULT_SCHEMA = "s2kp.real-context-admission-336-result.v1"
AUTHORIZED_RUN_ID = "s2kp-real-context-admission-336-20260903-01"
MAIN_EXECUTION_ENABLED = False
CASE_COUNT = 6
ADMISSION_CALL_COUNT = 12
MAX_FUNCTIONAL_OPERATIONS = 96
_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")

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


class S2KPRunnerError(RuntimeError):
    """The bounded run cannot produce one complete atomic result."""


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


def source_hashes(workspace_root: Path) -> dict[str, str]:
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
        raise S2KPRunnerError("workspace_root must be one absolute Path")
    result: dict[str, str] = {}
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        if not path.is_file():
            raise S2KPRunnerError(f"bound source missing: {relative}")
        result[relative] = _file_digest(path)
    return result


def _source_summary(value: S2KPSourceSummaryV1) -> dict[str, object]:
    return {
        "history_id": value.history_id,
        "recipe_id": value.recipe_id,
        "block_index": value.block_index,
        "pairing_digest": value.pairing_digest,
        "visual_payload_digest": value.visual_payload_digest,
        "auditory_payload_digest": value.auditory_payload_digest,
        "visual_values_digest": value.visual_values_digest,
        "auditory_values_digest": value.auditory_values_digest,
        "overlap_start_tick": value.overlap_start_tick,
        "overlap_end_tick": value.overlap_end_tick,
    }


def _semantic(result: admission.ControlledContextAdmission336V1) -> dict[str, object]:
    return {
        "decision": result.decision,
        "a_status": result.a_recent.status,
        "b_status": result.b_stable.status,
        "public_candidate_count": result.public_candidate_count,
        "hypothesis_area": None if result.hypothesis is None else result.hypothesis.area,
        "hypothesis_values_digest": None
        if result.hypothesis is None
        else result.hypothesis.candidate_values_digest,
        "hypothesis_provenance_count": 0
        if result.hypothesis is None
        else len(result.hypothesis.provenance_candidate_digests),
    }


def _advance_history(
    *,
    history_id: str,
    sequence: tuple[str, ...],
    stream: S2KPFixtureStream,
    config: coordinator.S2JVCoordinatorConfigV1,
) -> tuple[coordinator.S2JVCompositeStateV1, list[dict[str, object]]]:
    state = coordinator.initial_s2jv_composite_state(config)
    records: list[dict[str, object]] = []
    for ordinal, recipe_id in enumerate(sequence, start=1):
        pair, source = stream.materialize(recipe_id)
        bound = coordinator.bind_s2jv_coordinator_input(config=config, source=pair)
        owner = coordinator.S2JVFormationOwner(
            f"s2kp-{history_id}-owner-{ordinal:03d}",
            f"s2kp-{history_id}-auth-{ordinal:03d}",
            f"s2kp-{history_id}-consume-{ordinal:03d}",
            config.config_digest,
            state.state_digest,
            bound.input_digest,
        )
        prestate_digest = state.state_digest
        result = coordinator.advance_s2jv_atomic(
            config=config,
            prestate=state,
            source=bound,
            owner=owner,
        )
        state = result.poststate
        records.append(
            {
                "history_id": history_id,
                "ordinal": ordinal,
                "recipe_id": recipe_id,
                "source": _source_summary(source),
                "input_digest": bound.input_digest,
                "prestate_digest": prestate_digest,
                "poststate_digest": state.state_digest,
                "receipt_digest": result.receipt.receipt_digest,
                "result_digest": result.result_digest,
                "owner_status": result.owner_poststate.status,
                "b4_event": result.receipt.b4_event,
            }
        )
    if state.generation != len(sequence):
        raise S2KPRunnerError("history generation differs")
    return state, records


def _full_context(
    *,
    state: coordinator.S2JVCompositeStateV1,
    pair: object,
    source: S2KPSourceSummaryV1,
    config: coordinator.S2JVCoordinatorConfigV1,
) -> tuple[context_projection.TwoAreaPerceptualContext336, dict[str, object]]:
    prestate_digest = state.state_digest
    probe = coordinator.bind_s2jv_probe(config=config, source=pair)  # type: ignore[arg-type]
    finding = read_only.probe_s2jv_composite_read_only(
        config=config,
        state=state,
        probe=probe,
    )
    validated = finding_binding.bind_validated_perceptual_finding_336(
        config=config,
        state=state,
        probe=probe,
        finding=finding,
    )
    context = context_projection.project_two_area_perceptual_context_336(validated)
    if not (
        prestate_digest
        == state.state_digest
        == finding.prestate_digest
        == finding.poststate_digest
        == context.prestate_digest
        == context.poststate_digest
    ):
        raise S2KPRunnerError("full context probe changed memory")
    evidence = {
        "source": _source_summary(source),
        "memory_probe_digest": probe.probe_digest,
        "finding_digest": finding.finding_digest,
        "validated_finding_digest": validated.binding_digest,
        "context_bundle_digest": context.bundle_digest,
        "prestate_digest": prestate_digest,
        "poststate_digest": state.state_digest,
    }
    return context, evidence


def _run_case(
    *,
    case_id: str,
    state: coordinator.S2JVCompositeStateV1,
    context: context_projection.TwoAreaPerceptualContext336,
    retrieval_source: S2KPSourceSummaryV1,
    retrieval_evidence: dict[str, object],
    masked_pair: object,
    masked_source: S2KPSourceSummaryV1,
) -> dict[str, object]:
    assert_strictly_later(retrieval_source, masked_source)
    if (
        retrieval_evidence.get("context_bundle_digest") != context.bundle_digest
        or retrieval_evidence.get("source") != _source_summary(retrieval_source)
    ):
        raise S2KPRunnerError("retrieval evidence differs from context")
    masked_probe = admission.build_masked_admission_probe_336(
        source_digest=masked_source.pairing_digest,
        config_digest=context.config_digest,
        values=masked_visual_values(masked_pair),  # type: ignore[arg-type]
    )
    before = (
        state.state_digest,
        context.bundle_digest,
        masked_probe.probe_digest,
    )
    primary = admission.form_two_area_context_admission_336(context, masked_probe)
    direct = direct_baseline.form_direct_two_area_admission_baseline_336(context, masked_probe)
    after = (
        state.state_digest,
        context.bundle_digest,
        masked_probe.probe_digest,
    )
    if before != after or _semantic(primary) != _semantic(direct):
        raise S2KPRunnerError("admission or direct baseline relation differs")
    return {
        "case_id": case_id,
        "history_id": retrieval_source.history_id,
        "context_bundle_digest": context.bundle_digest,
        "retrieval_source_digest": retrieval_source.pairing_digest,
        "retrieval": retrieval_evidence,
        "masked_source": _source_summary(masked_source),
        "masked_probe_digest": masked_probe.probe_digest,
        "primary_result_digest": primary.result_digest,
        "baseline_result_digest": direct.result_digest,
        "primary": _semantic(primary),
        "baseline": _semantic(direct),
        "prestate_digest": before[0],
        "poststate_digest": after[0],
        "read_only": before == after,
    }


def evaluate_case_evidence(cases: list[dict[str, object]]) -> dict[str, object]:
    by_id = {item.get("case_id"): item for item in cases}
    claims: dict[str, bool] = {}
    for case_id in CASE_ORDER:
        case = by_id.get(case_id)
        expected = EXPECTED_CASES[case_id]
        semantic = case.get("primary") if isinstance(case, dict) else None
        baseline_semantic = case.get("baseline") if isinstance(case, dict) else None
        actual = (
            semantic.get("decision"),
            semantic.get("a_status"),
            semantic.get("b_status"),
            semantic.get("public_candidate_count"),
            semantic.get("hypothesis_area"),
        ) if isinstance(semantic, dict) else None
        claims[f"{case_id.lower()}_expected_decision"] = actual == expected
        claims[f"{case_id.lower()}_baseline_equal"] = semantic == baseline_semantic
        claims[f"{case_id.lower()}_read_only"] = (
            isinstance(case, dict)
            and case.get("read_only") is True
            and case.get("prestate_digest") == case.get("poststate_digest")
        )
    confirmed = len(cases) == CASE_COUNT and all(claims.values())
    return {
        "status": "S2KP_FUNCTION_CONFIRMED" if confirmed else "S2KP_FUNCTION_FALSIFIED",
        "claims": claims,
        "evaluation_digest": _digest(claims),
    }


def _sealed_result(payload: dict[str, object]) -> dict[str, object]:
    return {**payload, "record_digest": _digest(payload)}


def _atomic_write(path: Path, value: object) -> None:
    if path.exists():
        raise S2KPRunnerError("result path already exists")
    pending = path.with_name(f".{path.name}.pending")
    if pending.exists():
        raise S2KPRunnerError("pending result path already exists")
    data = _json_bytes(value)
    with pending.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(pending, path)


def _build_config() -> coordinator.S2JVCoordinatorConfigV1:
    profile = build_s2jw_default_live_profile()
    return coordinator.build_s2jv_coordinator_config(
        tspm_config=profile.tspm_config,
        b4_capacity=profile.b4_capacity,
        ledger_limits=build_s2jv_ledger_limits(profile),
    )


def _execute_bound_cases() -> tuple[list[dict[str, object]], list[dict[str, object]], str]:
    config = _build_config()
    profile = config.profile

    streams = {history_id: S2KPFixtureStream(profile, history_id) for history_id in HISTORIES}
    states: dict[str, coordinator.S2JVCompositeStateV1] = {}
    formations: list[dict[str, object]] = []
    for history_id, sequence in HISTORIES.items():
        states[history_id], history_records = _advance_history(
            history_id=history_id,
            sequence=sequence,
            stream=streams[history_id],
            config=config,
        )
        formations.extend(history_records)

    contexts: dict[str, context_projection.TwoAreaPerceptualContext336] = {}
    context_evidence: dict[str, dict[str, object]] = {}
    context_sources: dict[str, S2KPSourceSummaryV1] = {}

    def bind_context(key: str, history_id: str, recipe_id: str) -> None:
        pair, source = streams[history_id].materialize(recipe_id)
        context, evidence = _full_context(
            state=states[history_id],
            pair=pair,
            source=source,
            config=config,
        )
        contexts[key] = context
        context_evidence[key] = evidence
        context_sources[key] = source

    bind_context("d9", "h00", "D9")
    pair, source = streams["h00"].materialize("D9")
    cases = [
        _run_case(
            case_id="R1",
            state=states["h00"],
            context=contexts["d9"],
            retrieval_source=context_sources["d9"],
            retrieval_evidence=context_evidence["d9"],
            masked_pair=pair,
            masked_source=source,
        )
    ]

    bind_context("x", "h00", "X")
    pair, source = streams["h00"].materialize("X")
    cases.append(
        _run_case(
            case_id="R2",
            state=states["h00"],
            context=contexts["x"],
            retrieval_source=context_sources["x"],
            retrieval_evidence=context_evidence["x"],
            masked_pair=pair,
            masked_source=source,
        )
    )

    bind_context("y", "h00", "Y")
    pair, source = streams["h00"].materialize("Y")
    cases.append(
        _run_case(
            case_id="R5",
            state=states["h00"],
            context=contexts["y"],
            retrieval_source=context_sources["y"],
            retrieval_evidence=context_evidence["y"],
            masked_pair=pair,
            masked_source=source,
        )
    )

    pair, source = streams["h00"].materialize("D9_VISIBLE_MISMATCH")
    cases.append(
        _run_case(
            case_id="R6",
            state=states["h00"],
            context=contexts["d9"],
            retrieval_source=context_sources["d9"],
            retrieval_evidence=context_evidence["d9"],
            masked_pair=pair,
            masked_source=source,
        )
    )

    bind_context("a0", "h01", "A0")
    pair, source = streams["h01"].materialize("A0")
    cases.append(
        _run_case(
            case_id="R3",
            state=states["h01"],
            context=contexts["a0"],
            retrieval_source=context_sources["a0"],
            retrieval_evidence=context_evidence["a0"],
            masked_pair=pair,
            masked_source=source,
        )
    )

    bind_context("c1", "h02", "C1")
    pair, source = streams["h02"].materialize("C1")
    cases.append(
        _run_case(
            case_id="R4",
            state=states["h02"],
            context=contexts["c1"],
            retrieval_source=context_sources["c1"],
            retrieval_evidence=context_evidence["c1"],
            masked_pair=pair,
            masked_source=source,
        )
    )
    cases.sort(key=lambda item: CASE_ORDER.index(item["case_id"]))
    if len(formations) != FORMATION_COUNT or len(contexts) != FULL_PROBE_COUNT or len(cases) != MASKED_PROBE_COUNT:
        raise S2KPRunnerError("bound execution counts differ")
    return formations, cases, config.config_digest


def _neutral_pipeline_once() -> dict[str, object]:
    config = _build_config()
    stream = S2KPFixtureStream(config.profile, "n00")
    state, _ = _advance_history(
        history_id="n00",
        sequence=("B0",),
        stream=stream,
        config=config,
    )
    pair, retrieval = stream.materialize("B0")
    context, retrieval_evidence = _full_context(
        state=state,
        pair=pair,
        source=retrieval,
        config=config,
    )
    masked_pair, masked = stream.materialize("B0")
    result = _run_case(
        case_id="R1",
        state=state,
        context=context,
        retrieval_source=retrieval,
        retrieval_evidence=retrieval_evidence,
        masked_pair=masked_pair,
        masked_source=masked,
    )
    return result


def run_main_once(output_root: Path, workspace_root: Path, run_id: str) -> Path:
    if not MAIN_EXECUTION_ENABLED:
        raise S2KPRunnerError("S2-KP main execution gate is closed")
    if run_id != AUTHORIZED_RUN_ID or _RUN_ID.fullmatch(run_id) is None:
        raise S2KPRunnerError("run_id is not the bound S2-KP run")
    if not isinstance(output_root, Path) or not output_root.is_absolute():
        raise S2KPRunnerError("output_root must be one absolute Path")
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
        raise S2KPRunnerError("workspace_root must be one absolute Path")
    output_root.mkdir(parents=True, exist_ok=True)
    directory = output_root / run_id
    directory.mkdir(exist_ok=False)
    formations, cases, config_digest = _execute_bound_cases()
    evaluation = evaluate_case_evidence(cases)
    payload = {
        "schema": S2KP_RESULT_SCHEMA,
        "run_id": run_id,
        "technical_status": "RECORDING_COMPLETE",
        "source_hashes": source_hashes(workspace_root),
        "config_digest": config_digest,
        "plan": {
            "history_ids": list(HISTORIES),
            "history_lengths": [len(HISTORIES[item]) for item in HISTORIES],
            "formation_count": FORMATION_COUNT,
            "full_probe_count": FULL_PROBE_COUNT,
            "masked_probe_count": MASKED_PROBE_COUNT,
            "admission_call_count": ADMISSION_CALL_COUNT,
            "maximum_functional_operations": MAX_FUNCTIONAL_OPERATIONS,
            "context_fill": False,
            "field_effect": False,
            "automatic_mask_detection": False,
        },
        "formations": formations,
        "cases": cases,
        "functional_evaluation": evaluation,
        "raw_payload_retained": False,
    }
    result = _sealed_result(payload)
    _atomic_write(directory / "result.json", result)
    return directory


__all__: tuple[str, ...] = ()
