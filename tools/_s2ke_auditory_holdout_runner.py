"""Closed-gate S2-KE runner reusing the finite S2-KB run shape."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re

from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2jw_profiled_memory_read_only as read_only
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits
from tools._s2kb_withheld_variant_measurement import state_slot_projection
from tools._s2ke_auditory_holdout_evaluator import S2KE_EVIDENCE_SCHEMA, evaluate_s2kc_evidence
from tools._s2ke_auditory_holdout_fixtures import CHECKPOINTS, FORMATION_SEQUENCE, GEOMETRY_BLOCKED, HOLDOUT_ROLES, S2KEFixtureStream
from tools._s2ke_auditory_holdout_measurement import advance_baselines, initial_baseline_state, materialize_start_gate_with_plan, probe_baselines, validate_start_gate


S2KE_RESULT_SCHEMA = "s2ke.auditory-holdout-result.v1"
MAIN_EXECUTION_ENABLED = False
AUTHORIZED_RUN_ID: str | None = None
FORMATION_COUNT = 17
PROBE_COUNT = 8
FUNCTIONAL_OPERATION_COUNT = 157
MEMORY_OPERATION_COUNT = 100
BASELINE_OPERATION_COUNT = 31
MEMORY_L1_LIMIT = 133_344
TOTAL_L1_LIMIT = 156_864
_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")
SOURCE_PATHS = (
    "mcm_field_organism/_ppb1_reference.py",
    "mcm_field_organism/_tspm1_private.py",
    "mcm_field_organism/_tspm1_s2dr_private_comparison.py",
    "mcm_field_organism/broadband_hearing_path.py",
    "mcm_field_organism/log_spectral_receptor.py",
    "tools/_s2jw_default_live_profile.py",
    "tools/_s2jw_default_live_av_pairing.py",
    "tools/_s2jw_profiled_memory_ledger.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2jw_profiled_memory_read_only.py",
    "tools/_s2ke_auditory_holdout_fixtures.py",
    "tools/_s2ke_auditory_holdout_measurement.py",
    "tools/_s2ke_auditory_holdout_evaluator.py",
    "tools/_s2ke_auditory_holdout_runner.py",
    "tools/_s2ke_auditory_holdout_result_verifier.py",
)


class S2KERunnerError(RuntimeError):
    pass


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True) + "\n").encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)[:-1]).hexdigest()


def source_hashes(workspace_root: Path) -> dict[str, str]:
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
        raise S2KERunnerError("workspace_root must be one absolute Path")
    result: dict[str, str] = {}
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        if not path.is_file():
            raise S2KERunnerError(f"bound source missing: {relative}")
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


@dataclass(slots=True)
class _OperationChain:
    records: list[dict[str, object]]
    previous_digest: str | None = None

    def append(self, role: str, evidence: dict[str, object]) -> None:
        ordinal = len(self.records) + 1
        payload = {"schema": "s2ke.operation.v1", "operation_id": f"s2ke-op-{ordinal:03d}", "ordinal": ordinal, "role": role, "parent_operation_digest": self.previous_digest, "evidence": evidence}
        record = {**payload, "operation_digest": _digest(payload)}
        self.records.append(record)
        self.previous_digest = record["operation_digest"]  # type: ignore[assignment]


def expected_operation_roles() -> tuple[str, ...]:
    roles: list[str] = []
    checkpoints = {count for _, count in CHECKPOINTS}
    for formation_count in range(FORMATION_COUNT + 1):
        if formation_count in checkpoints:
            for _ in HOLDOUT_ROLES:
                roles.extend(("AV_MATERIALIZE", "MEMORY_PROBE_BIND", "B4_READ", "TSPM_READ", "READ_ONLY_VALIDATE", "FROZEN_BASELINE_READ", "REPLAY_BASELINE_READ", "ADAPTIVE_BASELINE_READ"))
        if formation_count == FORMATION_COUNT:
            break
        roles.extend(("AV_MATERIALIZE", "MEMORY_SOURCE_BIND", "B4_FORMATION", "TSPM_FORMATION", "COMPOSITE_VALIDATE"))
        if 1 <= formation_count <= 7:
            roles.append("ADAPTIVE_BASELINE_UPDATE")
    roles.append("EVALUATE")
    if len(roles) != FUNCTIONAL_OPERATION_COUNT:
        raise S2KERunnerError("operation registry count differs")
    return tuple(roles)


EXPECTED_OPERATION_ROLES = expected_operation_roles()


def _selected(value: object | None, kind: str) -> dict[str, object] | None:
    if value is None:
        return None
    if kind == "b4":
        return {"slot_id": value.slot_id, "formation_index": value.formation_index, "auditory_distance": value.auditory_distance, "visual_distance": value.visual_distance, "mechanical_match": value.mechanical_match, "evidence_digest": value.entry_digest}  # type: ignore[attr-defined]
    if kind == "fast":
        return {"slot_id": value.slot_id, "support": value.support, "auditory_distance": value.auditory_distance, "visual_distance": value.visual_distance, "mechanical_match": value.mechanical_match, "evidence_digest": value.slot_digest}  # type: ignore[attr-defined]
    return {"slot_id": value.slot_id, "support": value.support, "stable": value.stable, "native_distance": value.native_distance, "mechanical_match": value.mechanical_match, "evidence_digest": value.slot_digest}  # type: ignore[attr-defined]


def _probe_summary(role: str, finding: read_only.S2JVReadOnlyFindingV1, baselines: dict[str, object]) -> dict[str, object]:
    return {"probe_role": role, "probe_digest": finding.probe_digest, "finding_digest": finding.finding_digest, "prestate_digest": finding.prestate_digest, "poststate_digest": finding.poststate_digest, "b4_selected": _selected(finding.b4_selected, "b4"), "fast_selected": _selected(finding.fast_selected, "fast"), "auditory_slow_selected": _selected(finding.auditory_slow_selected, "slow"), "visual_slow_selected": _selected(finding.visual_slow_selected, "slow"), "native_tspm_finding_digest": finding.native_tspm_finding_digest, "ledger_digest": finding.ledger.ledger_digest, "baselines": baselines}


def _atomic_write(path: Path, value: object) -> None:
    if path.exists():
        raise S2KERunnerError("result path already exists")
    pending = path.with_name(f".{path.name}.pending")
    if pending.exists():
        raise S2KERunnerError("pending result path already exists")
    with pending.open("xb") as handle:
        handle.write(_json_bytes(value))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(pending, path)


def _seal(payload: dict[str, object]) -> dict[str, object]:
    return {**payload, "record_digest": _digest(payload)}


def _plan() -> dict[str, object]:
    return {"formation_sequence": list(FORMATION_SEQUENCE), "checkpoints": [list(item) for item in CHECKPOINTS], "probe_roles": list(HOLDOUT_ROLES), "formation_count": 17, "probe_count": 8, "functional_operation_count": 157, "memory_operation_count": 100, "baseline_operation_count": 31, "memory_l1_limit": 133_344, "total_l1_limit": 156_864, "preflight_visual_analyses": 13, "preflight_audio_hops": 130, "preflight_raw_bytes": 81_120_000, "main_visual_analyses": 25, "main_audio_hops": 250, "main_raw_bytes": 156_000_000, "raw_payload_retained": False, "field_read": False, "context_used": False, "thresholds_changed": False}


def run_main_once(output_root: Path, workspace_root: Path, run_id: str) -> Path:
    if not MAIN_EXECUTION_ENABLED or AUTHORIZED_RUN_ID is None:
        raise S2KERunnerError("S2-KE main execution gate is closed")
    if run_id != AUTHORIZED_RUN_ID or _RUN_ID.fullmatch(run_id) is None:
        raise S2KERunnerError("run_id is not authorized")
    if not isinstance(output_root, Path) or not output_root.is_absolute():
        raise S2KERunnerError("output_root must be one absolute Path")
    output_root.mkdir(parents=True, exist_ok=True)
    directory = output_root / run_id
    directory.mkdir(exist_ok=False)
    result_path = directory / "result.json"
    hashes = source_hashes(workspace_root)
    operations = _OperationChain([])
    try:
        profile = build_s2jw_default_live_profile()
        preflight, pcm_plan = materialize_start_gate_with_plan(profile)
        validate_start_gate(preflight)
        if preflight["status"] == GEOMETRY_BLOCKED:
            payload = {"schema": S2KE_RESULT_SCHEMA, "run_id": run_id, "technical_status": GEOMETRY_BLOCKED, "source_hashes": hashes, "plan": _plan(), "preflight": preflight, "completed_operation_count": 0, "memory_calls": 0}
            _atomic_write(result_path, _seal(payload))
            return result_path
        limits = build_s2jv_ledger_limits(profile)
        config = coordinator.build_s2jv_coordinator_config(tspm_config=profile.tspm_config, b4_capacity=profile.b4_capacity, ledger_limits=limits)
        state = coordinator.initial_s2jv_composite_state(config)
        baseline_state = initial_baseline_state()
        initial_state_digest, initial_baseline_digest = state.state_digest, baseline_state.state_digest
        stream = S2KEFixtureStream(profile, pcm_plan, "s2ke-main-clock")
        block_index = formation_index = 0
        formations: list[dict[str, object]] = []
        checkpoint_evidence: list[dict[str, object]] = []

        def probe_checkpoint(checkpoint_id: str) -> None:
            nonlocal block_index
            probes = []
            for role in HOLDOUT_ROLES:
                fixture = stream.materialize(role, block_index)
                operations.append("AV_MATERIALIZE", {"block_index": block_index, "fixture_digest": fixture.fixture_digest})
                probe = coordinator.bind_s2jv_probe(config=config, source=fixture.pair)
                operations.append("MEMORY_PROBE_BIND", {"probe_digest": probe.probe_digest, "fixture_digest": fixture.fixture_digest})
                finding = read_only.probe_s2jv_composite_read_only(config=config, state=state, probe=probe)
                baselines = probe_baselines(baseline_state, fixture)
                operations.append("B4_READ", {"selected_digest": finding.b4_selected.entry_digest if finding.b4_selected else None})
                operations.append("TSPM_READ", {"finding_digest": finding.native_tspm_finding_digest})
                operations.append("READ_ONLY_VALIDATE", {"prestate_digest": finding.prestate_digest, "poststate_digest": finding.poststate_digest})
                operations.append("FROZEN_BASELINE_READ", {"finding_digest": baselines["finding_digest"], "arm": "frozen"})
                operations.append("REPLAY_BASELINE_READ", {"finding_digest": baselines["finding_digest"], "arm": "nearest"})
                operations.append("ADAPTIVE_BASELINE_READ", {"finding_digest": baselines["finding_digest"], "arm": "adaptive"})
                probes.append(_probe_summary(role, finding, baselines))
                block_index += 1
            checkpoint_evidence.append({"checkpoint_id": checkpoint_id, "formation_count": formation_index, "state_digest": state.state_digest, "baseline_state_digest": baseline_state.state_digest, "probes": probes})

        checkpoints = {count: checkpoint for checkpoint, count in CHECKPOINTS}
        probe_checkpoint(checkpoints[0])
        for role in FORMATION_SEQUENCE:
            formation_index += 1
            fixture = stream.materialize(role, block_index)
            operations.append("AV_MATERIALIZE", {"block_index": block_index, "fixture_digest": fixture.fixture_digest})
            source = coordinator.bind_s2jv_coordinator_input(config=config, source=fixture.pair)
            operations.append("MEMORY_SOURCE_BIND", {"input_digest": source.input_digest, "fixture_digest": fixture.fixture_digest})
            owner = coordinator.S2JVFormationOwner(f"s2ke-owner-{formation_index:02d}", f"s2ke-authorization-{formation_index:02d}", f"s2ke-consumption-{formation_index:02d}", config.config_digest, state.state_digest, source.input_digest)
            result = coordinator.advance_s2jv_atomic(config=config, prestate=state, source=source, owner=owner)
            operations.append("B4_FORMATION", {"event": result.receipt.b4_event, "slot_id": result.receipt.b4_slot_id})
            operations.append("TSPM_FORMATION", {"result_digest": result.receipt.tspm_result_digest})
            baseline_prestate = baseline_state.state_digest
            baseline_state = advance_baselines(baseline_state, fixture)
            state = result.poststate
            operations.append("COMPOSITE_VALIDATE", {"state_digest": state.state_digest, "receipt_digest": result.receipt.receipt_digest, "baseline_prestate_digest": baseline_prestate, "baseline_poststate_digest": baseline_state.state_digest})
            if 2 <= formation_index <= 8:
                operations.append("ADAPTIVE_BASELINE_UPDATE", {"formation_index": formation_index, "baseline_state_digest": baseline_state.state_digest, "adaptive_support": baseline_state.support})
            formations.append({"formation_index": formation_index, "training_role": role, "fixture_digest": fixture.fixture_digest, "input_digest": source.input_digest, "prestate_digest": result.receipt.composite_prestate_digest, "poststate_digest": state.state_digest, "receipt_digest": result.receipt.receipt_digest, "b4_event": result.receipt.b4_event, "tspm_result_digest": result.receipt.tspm_result_digest, "baseline_prestate_digest": baseline_prestate, "baseline_poststate_digest": baseline_state.state_digest})
            block_index += 1
            if formation_index in checkpoints:
                probe_checkpoint(checkpoints[formation_index])
        evidence = {"schema": S2KE_EVIDENCE_SCHEMA, "formation_roles": list(FORMATION_SEQUENCE), "baseline_training_roles": [item[0] for item in baseline_state.replay], "initial_state_digest": initial_state_digest, "initial_baseline_digest": initial_baseline_digest, "formation_evidence": formations, "checkpoints": checkpoint_evidence, "final_state": state_slot_projection(state), "final_baseline_state_digest": baseline_state.state_digest}
        evaluation = evaluate_s2kc_evidence(evidence)
        operations.append("EVALUATE", {"evidence_digest": _digest(evidence), "evaluation_digest": evaluation["evaluation_digest"]})
        if len(operations.records) != FUNCTIONAL_OPERATION_COUNT or block_index != 25:
            raise S2KERunnerError("bound operation or source count differs")
        payload = {"schema": S2KE_RESULT_SCHEMA, "run_id": run_id, "technical_status": "RECORDING_COMPLETE", "source_hashes": hashes, "plan": _plan(), "preflight": preflight, "operations": operations.records, "evidence": evidence, "functional_evaluation": evaluation, "last_operation_digest": operations.previous_digest}
        _atomic_write(result_path, _seal(payload))
        return result_path
    except Exception as exc:
        if not result_path.exists():
            _atomic_write(result_path, _seal({"schema": S2KE_RESULT_SCHEMA, "run_id": run_id, "technical_status": "NOT_EVALUABLE", "error_type": type(exc).__name__, "completed_operation_count": len(operations.records), "source_hashes": hashes}))
        raise
