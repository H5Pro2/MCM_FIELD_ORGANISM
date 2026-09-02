"""Minimal one-shot runner for the bound S2-JX 336-value memory function."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2jw_profiled_memory_read_only as read_only
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits
from tools._s2jx_default_live_memory_fixtures import (
    FORMATION_SEQUENCE,
    PROBE_SEQUENCE,
    S2JV_FIXTURE_RECIPE_DIGEST,
    S2JXFixtureStream,
)


S2JX_RESULT_SCHEMA = "s2jx.default-live-memory-result.v1"
AUTHORIZED_RUN_ID = "s2jx-default-live-memory-20260902-01"
MAIN_EXECUTION_ENABLED = False
FORMATION_COUNT = 15
PROBE_COUNT = 3
TOP_LEVEL_OPERATION_COUNT = 72
TOTAL_L1_TERMS = 43_680
_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")

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


class S2JXRunnerError(RuntimeError):
    """The one-shot run cannot produce one complete technical record."""


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
        raise S2JXRunnerError("workspace_root must be one absolute Path")
    result = {}
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        if not path.is_file():
            raise S2JXRunnerError(f"bound source missing: {relative}")
        result[relative] = _file_digest(path)
    return result


@dataclass(slots=True)
class _OperationChain:
    records: list[dict[str, object]]
    previous_digest: str | None = None

    def append(self, role: str, evidence: dict[str, object]) -> None:
        ordinal = len(self.records) + 1
        payload = {
            "schema": "s2jx.operation.v1",
            "operation_id": f"s2jx-op-{ordinal:03d}",
            "ordinal": ordinal,
            "role": role,
            "parent_operation_digest": self.previous_digest,
            "evidence": evidence,
        }
        record = {**payload, "operation_digest": _digest(payload)}
        self.records.append(record)
        self.previous_digest = record["operation_digest"]  # type: ignore[assignment]


def _ppb_slot_summary(slot: object) -> dict[str, object]:
    payload = slot.canonical_payload()  # type: ignore[attr-defined]
    return {
        "slot_id": payload["slot_id"],
        "occupied": payload["occupied"],
        "support": payload["support_count"],
        "last_selected_step": payload["last_selected_step"],
        "slot_digest": _digest(payload),
    }


def _state_summary(state: coordinator.S2JVCompositeStateV1) -> dict[str, object]:
    b4 = [
        {
            "slot_id": entry.slot_id,
            "formation_index": entry.formation_index,
            "entry_digest": _digest(
                {
                    "slot_id": entry.slot_id,
                    "formation_index": entry.formation_index,
                    "values_digest": _digest(list(entry.values)),
                }
            ),
        }
        for entry in state.b4_state.entries
        if entry.occupied
    ]
    fast = [
        {
            "slot_id": slot.slot_id,
            "support": slot.support_count,
            "last_selected_step": slot.last_selected_step,
            "consolidation_count": slot.consolidation_count,
            "slot_digest": slot.digest(),
        }
        for slot in state.tspm_state.fast_state.slots
        if slot.occupied
    ]
    return {
        "generation": state.generation,
        "state_digest": state.state_digest,
        "b4": b4,
        "fast": fast,
        "auditory_slow": [
            _ppb_slot_summary(slot)
            for slot in state.tspm_state.auditory_ppb1_state.slots
            if slot.occupied
        ],
        "visual_slow": [
            _ppb_slot_summary(slot)
            for slot in state.tspm_state.visual_ppb1_state.slots
            if slot.occupied
        ],
    }


def _observation(value: object | None, kind: str) -> dict[str, object] | None:
    if value is None:
        return None
    if kind == "b4":
        return {
            "slot_id": value.slot_id,  # type: ignore[attr-defined]
            "formation_index": value.formation_index,  # type: ignore[attr-defined]
            "auditory_distance": value.auditory_distance,  # type: ignore[attr-defined]
            "visual_distance": value.visual_distance,  # type: ignore[attr-defined]
            "mechanical_match": value.mechanical_match,  # type: ignore[attr-defined]
            "evidence_digest": value.entry_digest,  # type: ignore[attr-defined]
        }
    if kind == "fast":
        return {
            "slot_id": value.slot_id,  # type: ignore[attr-defined]
            "support": value.support,  # type: ignore[attr-defined]
            "last_selected_step": value.last_selected_step,  # type: ignore[attr-defined]
            "auditory_distance": value.auditory_distance,  # type: ignore[attr-defined]
            "visual_distance": value.visual_distance,  # type: ignore[attr-defined]
            "mechanical_match": value.mechanical_match,  # type: ignore[attr-defined]
            "evidence_digest": value.slot_digest,  # type: ignore[attr-defined]
        }
    return {
        "modality_id": value.modality_id,  # type: ignore[attr-defined]
        "slot_id": value.slot_id,  # type: ignore[attr-defined]
        "support": value.support,  # type: ignore[attr-defined]
        "stable": value.stable,  # type: ignore[attr-defined]
        "native_distance": value.native_distance,  # type: ignore[attr-defined]
        "mechanical_match": value.mechanical_match,  # type: ignore[attr-defined]
        "evidence_digest": value.slot_digest,  # type: ignore[attr-defined]
    }


def _finding_summary(label: str, finding: read_only.S2JVReadOnlyFindingV1) -> dict[str, object]:
    return {
        "evaluation_label": label,
        "probe_digest": finding.probe_digest,
        "finding_digest": finding.finding_digest,
        "native_tspm_finding_digest": finding.native_tspm_finding_digest,
        "prestate_digest": finding.prestate_digest,
        "poststate_digest": finding.poststate_digest,
        "b4_selected": _observation(finding.b4_selected, "b4"),
        "fast_selected": _observation(finding.fast_selected, "fast"),
        "auditory_slow_selected": _observation(finding.auditory_slow_selected, "slow"),
        "visual_slow_selected": _observation(finding.visual_slow_selected, "slow"),
        "auditory_slow_observations": [
            _observation(item, "slow") for item in finding.auditory_slow_observations
        ],
        "visual_slow_observations": [
            _observation(item, "slow") for item in finding.visual_slow_observations
        ],
        "ledger_digest": finding.ledger.ledger_digest,
    }


def evaluate_probe_evidence(probes: list[dict[str, object]]) -> dict[str, object]:
    by_label = {item.get("evaluation_label"): item for item in probes}
    d9 = by_label.get("D9", {})
    x = by_label.get("X", {})
    y = by_label.get("Y", {})
    d9_b4 = d9.get("b4_selected") if isinstance(d9, dict) else None
    x_a = x.get("auditory_slow_selected") if isinstance(x, dict) else None
    x_v = x.get("visual_slow_selected") if isinstance(x, dict) else None
    claims = {
        "d9_is_b4_recent": isinstance(d9_b4, dict)
        and d9_b4.get("formation_index") == 15
        and d9_b4.get("mechanical_match") is True,
        "x_absent_from_b4": isinstance(x, dict) and x.get("b4_selected") is None,
        "x_absent_from_fast": isinstance(x, dict) and x.get("fast_selected") is None,
        "x_auditory_slow_support_3": isinstance(x_a, dict)
        and x_a.get("support") == 3
        and x_a.get("stable") is True
        and x_a.get("mechanical_match") is True,
        "x_visual_slow_support_3": isinstance(x_v, dict)
        and x_v.get("support") == 3
        and x_v.get("stable") is True
        and x_v.get("mechanical_match") is True,
        "y_absent_from_b4": isinstance(y, dict) and y.get("b4_selected") is None,
        "y_absent_from_fast": isinstance(y, dict) and y.get("fast_selected") is None,
        "y_no_public_auditory_slow": isinstance(y, dict)
        and y.get("auditory_slow_selected") is None,
        "y_no_public_visual_slow": isinstance(y, dict)
        and y.get("visual_slow_selected") is None,
        "all_probes_read_only": len(probes) == 3
        and all(item.get("prestate_digest") == item.get("poststate_digest") for item in probes),
    }
    confirmed = all(claims.values())
    return {
        "status": "S2JX_FUNCTION_CONFIRMED" if confirmed else "S2JX_FUNCTION_FALSIFIED",
        "claims": claims,
        "evaluation_digest": _digest(claims),
    }


def _atomic_write(path: Path, value: object) -> None:
    if path.exists():
        raise S2JXRunnerError("result path already exists")
    pending = path.with_name(f".{path.name}.pending")
    if pending.exists():
        raise S2JXRunnerError("pending result path already exists")
    data = _json_bytes(value)
    with pending.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(pending, path)


def _sealed_result(payload: dict[str, object]) -> dict[str, object]:
    return {**payload, "record_digest": _digest(payload)}


def run_main_once(output_root: Path, workspace_root: Path, run_id: str) -> Path:
    if not MAIN_EXECUTION_ENABLED:
        raise S2JXRunnerError("S2-JX main execution gate is closed")
    if run_id != AUTHORIZED_RUN_ID or _RUN_ID.fullmatch(run_id) is None:
        raise S2JXRunnerError("run_id is not the single authorized S2-JX run")
    if not isinstance(output_root, Path) or not output_root.is_absolute():
        raise S2JXRunnerError("output_root must be one absolute Path")
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
        raise S2JXRunnerError("workspace_root must be one absolute Path")
    output_root.mkdir(parents=True, exist_ok=True)
    directory = output_root / run_id
    directory.mkdir(exist_ok=False)
    result_path = directory / "result.json"
    hashes = source_hashes(workspace_root)
    operations = _OperationChain([])
    try:
        profile = build_s2jw_default_live_profile()
        limits = build_s2jv_ledger_limits(profile)
        if (
            limits.plan_formation_count,
            limits.plan_probe_count,
            limits.plan_top_level_operations,
            limits.plan_total_l1_terms,
        ) != (FORMATION_COUNT, PROBE_COUNT, TOP_LEVEL_OPERATION_COUNT, TOTAL_L1_TERMS):
            raise S2JXRunnerError("profile-derived plan limits differ")
        config = coordinator.build_s2jv_coordinator_config(
            tspm_config=profile.tspm_config,
            b4_capacity=profile.b4_capacity,
            ledger_limits=limits,
        )
        state = coordinator.initial_s2jv_composite_state(config)
        stream = S2JXFixtureStream(profile)
        formations: list[dict[str, object]] = []
        for block_index, label in enumerate(FORMATION_SEQUENCE):
            pair = stream.materialize(label, block_index)
            operations.append(
                "AV_PAIR",
                {
                    "pairing_digest": pair.pairing_digest,
                    "auditory_payload_digest": pair.plan.auditory_payload_digest,
                    "visual_payload_digest": pair.plan.visual_payload_digest,
                    "auditory_values_digest": pair.plan.auditory_values_digest,
                    "visual_values_digest": pair.plan.visual_values_digest,
                },
            )
            bound = coordinator.bind_s2jv_coordinator_input(config=config, source=pair)
            owner = coordinator.S2JVFormationOwner(
                f"s2jx-owner-{block_index:02d}",
                f"s2jx-authorization-{block_index:02d}",
                f"s2jx-consumption-{block_index:02d}",
                config.config_digest,
                state.state_digest,
                bound.input_digest,
            )
            result = coordinator.advance_s2jv_atomic(
                config=config,
                prestate=state,
                source=bound,
                owner=owner,
            )
            operations.append(
                "B4_ARM",
                {
                    "event": result.receipt.b4_event,
                    "slot_id": result.receipt.b4_slot_id,
                    "poststate_digest": result.receipt.b4_poststate_digest,
                },
            )
            operations.append(
                "TSPM_ARM",
                {
                    "result_digest": result.receipt.tspm_result_digest,
                    "poststate_digest": result.receipt.tspm_poststate_digest,
                },
            )
            state = result.poststate
            summary = _state_summary(state)
            operations.append(
                "COMPOSITE_VALIDATE",
                {
                    "receipt_digest": result.receipt.receipt_digest,
                    "result_digest": result.result_digest,
                    "ledger_digest": result.ledger.ledger_digest,
                    "state_digest": state.state_digest,
                    "owner_status": result.owner_poststate.status,
                },
            )
            formations.append(
                {
                    "evaluation_label": label,
                    "formation_index": block_index + 1,
                    "pairing_digest": pair.pairing_digest,
                    "input_digest": bound.input_digest,
                    "receipt_digest": result.receipt.receipt_digest,
                    "state": summary,
                }
            )

        final_state_digest = state.state_digest
        probes: list[dict[str, object]] = []
        for offset, label in enumerate(PROBE_SEQUENCE):
            block_index = FORMATION_COUNT + offset
            pair = stream.materialize(label, block_index)
            operations.append(
                "AV_PAIR",
                {
                    "pairing_digest": pair.pairing_digest,
                    "auditory_payload_digest": pair.plan.auditory_payload_digest,
                    "visual_payload_digest": pair.plan.visual_payload_digest,
                    "auditory_values_digest": pair.plan.auditory_values_digest,
                    "visual_values_digest": pair.plan.visual_values_digest,
                },
            )
            probe = coordinator.bind_s2jv_probe(config=config, source=pair)
            finding = read_only.probe_s2jv_composite_read_only(
                config=config,
                state=state,
                probe=probe,
            )
            summary = _finding_summary(label, finding)
            operations.append(
                "B4_READ",
                {
                    "probe_digest": probe.probe_digest,
                    "selected": summary["b4_selected"],
                },
            )
            operations.append(
                "TSPM_READ",
                {
                    "probe_digest": probe.probe_digest,
                    "fast_selected": summary["fast_selected"],
                    "auditory_slow_selected": summary["auditory_slow_selected"],
                    "visual_slow_selected": summary["visual_slow_selected"],
                    "native_finding_digest": finding.native_tspm_finding_digest,
                },
            )
            operations.append(
                "READ_ONLY_VALIDATE",
                {
                    "finding_digest": finding.finding_digest,
                    "prestate_digest": finding.prestate_digest,
                    "poststate_digest": finding.poststate_digest,
                    "ledger_digest": finding.ledger.ledger_digest,
                },
            )
            probes.append(summary)

        if len(operations.records) != TOP_LEVEL_OPERATION_COUNT:
            raise S2JXRunnerError("top-level operation count differs")
        if state.state_digest != final_state_digest:
            raise S2JXRunnerError("read-only probes changed the memory state")
        evaluation = evaluate_probe_evidence(probes)
        payload: dict[str, object] = {
            "schema": S2JX_RESULT_SCHEMA,
            "run_id": run_id,
            "technical_status": "RECORDING_COMPLETE",
            "source_hashes": hashes,
            "profile_binding_digest": profile.binding_digest,
            "fixture_recipe_digest": S2JV_FIXTURE_RECIPE_DIGEST,
            "plan": {
                "formation_sequence": list(FORMATION_SEQUENCE),
                "probe_sequence": list(PROBE_SEQUENCE),
                "formation_count": FORMATION_COUNT,
                "probe_count": PROBE_COUNT,
                "top_level_operation_count": TOP_LEVEL_OPERATION_COUNT,
                "total_l1_terms": TOTAL_L1_TERMS,
                "raw_payload_retained": False,
                "field_read": False,
                "context_selection": False,
                "compression_336_to_26": False,
            },
            "operations": operations.records,
            "formation_evidence": formations,
            "final_state": _state_summary(state),
            "probe_evidence": probes,
            "functional_evaluation": evaluation,
            "last_operation_digest": operations.previous_digest,
        }
        _atomic_write(result_path, _sealed_result(payload))
        return result_path
    except Exception as exc:
        if not result_path.exists():
            failure = {
                "schema": S2JX_RESULT_SCHEMA,
                "run_id": run_id,
                "technical_status": "NOT_EVALUABLE",
                "error_type": type(exc).__name__,
                "completed_operation_count": len(operations.records),
                "last_operation_digest": operations.previous_digest,
                "source_hashes": hashes,
            }
            _atomic_write(result_path, _sealed_result(failure))
        raise

