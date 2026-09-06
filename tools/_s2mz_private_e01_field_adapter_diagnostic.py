"""One direct S2-LO field-adapter diagnosis for qualified S2-MT event e01."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import traceback

from tools import _s2mt_private_transfer_runtime_runner as transfer


S2MZ_SCHEMA = "s2mz.private.e01-field-adapter-diagnostic.v1"
DIAGNOSTIC_ID = "s2mz-e01-field-adapter-diagnostic-20260906-01"
MAX_RESULT_BYTES = 131_072
SOURCE_PATHS = (
    "tools/_s2mz_private_e01_field_adapter_diagnostic.py",
    "tools/_s2mx_private_scaled_transfer_sources.py",
    "tools/_s2mt_private_transfer_runtime_runner.py",
    "tools/_s2lo_private_role_free_stream_runner.py",
    "tools/_s2lm_private_role_free_stream_processor.py",
    "tools/_s2jt_private_timed_field_projection.py",
    "mcm_field_organism/receptor_time_model.py",
    "mcm_field_organism/receptor_proposal_handoff.py",
    "mcm_field_organism/transient_dock_trajectory.py",
    "mcm_field_organism/transient_neuron_input.py",
    "mcm_field_organism/shared_mcm_field.py",
    "mcm_field_organism/neutral_local_field_substrate.py",
)


class S2MZDiagnosticError(RuntimeError):
    """The bounded e01 field diagnosis cannot be completed."""


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return encoded + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MZDiagnosticError(message)


def _source_hashes(workspace: Path) -> dict[str, str]:
    result = {}
    for relative in SOURCE_PATHS:
        path = workspace / relative
        _require(path.is_file(), f"bound source is absent: {relative}")
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _frame_projection(timed: object) -> dict[str, object]:
    frame = timed.frame
    values = tuple(float(value) for value in frame.values)
    return {
        "modality_id": frame.modality_id,
        "geometry_id": frame.geometry_id,
        "native_clock_id": frame.clock_id,
        "native_window_start_tick": frame.window_start_tick,
        "native_window_end_tick": frame.window_end_tick,
        "field_clock_id": timed.field_time.clock_id,
        "field_window_start_tick": timed.field_time.window_start_tick,
        "field_window_end_tick": timed.field_time.window_end_tick,
        "value_count": len(values),
        "values_digest": hashlib.sha256(
            json.dumps(list(values), allow_nan=False, separators=(",", ":")).encode("ascii")
        ).hexdigest(),
        "all_values_finite": all(math.isfinite(value) for value in values),
        "all_values_normalized": all(-1.0 <= value <= 1.0 for value in values),
    }


def _dock_projection(field: object) -> dict[str, object]:
    docks = []
    pair_keys = []
    for dock in field.docks:
        pairs = tuple(tuple(pair) for pair in dock.dock_map.pairs)
        pair_keys.extend((dock.dock_id, *pair) for pair in pairs)
        docks.append(
            {
                "dock_id": dock.dock_id,
                "modality_id": dock.dock_map.modality_id,
                "receptor_geometry_id": dock.dock_map.receptor_geometry_id,
                "pair_count": len(pairs),
                "pairs_digest": _digest([list(pair) for pair in pairs]),
            }
        )
    return {
        "dock_count": len(docks),
        "docks": docks,
        "total_pair_count": len(pair_keys),
        "unique_pair_count": len(set(pair_keys)),
        "all_pairs_unique": len(pair_keys) == len(set(pair_keys)),
        "expected_336_contacts_bound": len(pair_keys) == 336 and len(set(pair_keys)) == 336,
    }


def _post_field_projection(branch: object) -> dict[str, object]:
    poststate = branch.poststate
    field = poststate.field
    components = [
        {
            "neuron_id": neuron.neuron_id,
            "activation": neuron.activation,
            "afterimage": neuron.afterimage,
            "perception_tick": neuron.perception.tick,
            "receptor_contact": neuron.perception.receptor_contact,
            "local_samples": list(neuron.perception.local_samples),
        }
        for neuron in field.layer.neurons
    ]
    return {
        "status": "REACHED",
        "phase": poststate.phase,
        "step_count": poststate.step_count,
        "last_end_tick": poststate.last_end_tick,
        "field_component_digest": poststate.field_component_digest,
        "state_digest": poststate.state_digest,
        "component_count": len(components),
        "components_digest": _digest(components),
        "nonzero_activation_count": sum(item["activation"] != 0.0 for item in components),
        "nonzero_contact_count": sum(item["receptor_contact"] != 0.0 for item in components),
    }


def _exception_projection(exc: Exception) -> dict[str, object]:
    extracted = traceback.extract_tb(exc.__traceback__)
    relevant = [
        item
        for item in extracted
        if "mcm_field_organism" in item.filename or "_s2lo_private_role_free_stream_runner.py" in item.filename
    ]
    leaf = relevant[-1] if relevant else extracted[-1]
    if leaf.name in {"__post_init__", "_validate_timed_frame"} and "receptor_time_model" in leaf.filename:
        phase = "RECEPTOR_TIME_SEQUENCE_BINDING"
    elif "receptor_proposal_handoff" in leaf.filename:
        phase = "RECEPTOR_COMPLETION_HANDOFF"
    elif "transient_dock_trajectory" in leaf.filename:
        phase = "DOCK_TRAJECTORY_MAPPING"
    elif "transient_neuron_input" in leaf.filename:
        phase = "CONTACT_PROJECTION"
    elif "neutral_local_field_substrate" in leaf.filename or "shared_mcm_field" in leaf.filename:
        phase = "FIELD_ADVANCE"
    else:
        phase = "FIELD_ADAPTER"
    return {
        "exception_class": type(exc).__name__,
        "exception_module": type(exc).__module__,
        "message": str(exc),
        "phase": phase,
        "leaf_source": Path(leaf.filename).name,
        "leaf_function": leaf.name,
        "leaf_line": leaf.lineno,
    }


def _write_once(path: Path, payload: dict[str, object]) -> None:
    _require(not path.exists(), "diagnostic result already exists")
    path.parent.mkdir(parents=True, exist_ok=False)
    data = _canonical_bytes(payload, newline=True)
    _require(len(data) <= MAX_RESULT_BYTES, "diagnostic result exceeds byte budget")
    temporary = path.with_suffix(".tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise


def run_diagnostic(workspace: Path, output_path: Path) -> dict[str, object]:
    source_hashes = _source_hashes(workspace)
    plan = transfer.raw_source.build_presealed_plan()
    config = transfer.field_source._build_config()
    materialized = transfer._materialize_events(plan, config)
    _require(len(materialized) == 28, "qualified materialization count differs")
    e01 = materialized[0]
    _require(e01.spec.event_code == "e01" and e01.spec.ordinal == 1, "selected event differs")

    field_input = e01.field_input
    frames = tuple(field_input.timed_frames)
    frame_projections = tuple(_frame_projection(item) for item in frames)
    input_projection = {
        "exact_input_type": type(field_input) is transfer.field_source.S2LOFieldInputV1,
        "input_type": type(field_input).__name__,
        "perception_digest": field_input.perception_digest,
        "event_field_projection_digest": e01.perception_digest,
        "projection_digest_matches": field_input.perception_digest == e01.perception_digest,
        "start_tick": field_input.start_tick,
        "end_tick": field_input.end_tick,
        "positive_window": field_input.start_tick == 0 and field_input.end_tick > field_input.start_tick,
        "timed_frame_count": len(frames),
        "modalities": [item["modality_id"] for item in frame_projections],
        "timed_frames": list(frame_projections),
        "materialized_field_clock_matches_s2mt": all(
            item["field_clock_id"] == transfer.FIELD_CLOCK_ID for item in frame_projections
        ),
        "materialized_field_clock_matches_s2lo_adapter": all(
            item["field_clock_id"] == transfer.field_source.FIELD_CLOCK_ID for item in frame_projections
        ),
    }

    initial = transfer.field_source.initial_s2lo_field_state(field_input)
    initial_observation = transfer.field_source._field_observation(initial)
    initial_projection = {
        "phase": initial_observation["phase"],
        "field_component_digest": initial_observation["field_component_digest"],
        "last_end_tick": initial_observation["last_end_tick"],
        "step_count": initial_observation["step_count"],
        "state_digest": initial_observation["state_digest"],
        "pre_contact_payload_digest": _digest(initial_observation["pre_contact_payload"]),
        "exact_state_type": type(initial) is transfer.field_source.S2LOFieldStateV1,
    }
    docks = _dock_projection(initial.field)
    event = transfer._build_event(e01)
    event_projection = {
        "event_id": event.event_id,
        "ordinal": event.ordinal,
        "event_type": event.event_type,
        "field_projection_digest": event.field_projection_digest,
        "field_payload_is_selected_input": event.field_payload is field_input,
        "projection_digest_matches_input": event.field_projection_digest == field_input.perception_digest,
        "event_digest": event.event_digest,
    }

    adapter = transfer.field_source.build_s2lo_field_adapter()
    adapter_call_count = 0
    branch = None
    failure = None
    try:
        adapter_call_count += 1
        branch = adapter(initial, event)
    except Exception as exc:
        failure = _exception_projection(exc)

    post_field = (
        _post_field_projection(branch)
        if branch is not None
        else {
            "status": "NOT_REACHED",
            "field_values_checked": False,
            "reason": "direct field adapter raised before publishing a branch result",
        }
    )
    technical_status = (
        "S2MZ_FIELD_ADAPTER_SUCCEEDED"
        if branch is not None
        else "S2MZ_FIELD_ADAPTER_CAUSE_LOCALIZED"
    )
    payload: dict[str, object] = {
        "schema": S2MZ_SCHEMA,
        "diagnostic_id": DIAGNOSTIC_ID,
        "technical_status": technical_status,
        "source_hashes": source_hashes,
        "source_plan_digest": plan.plan_digest,
        "selected_materialized_event": "e01",
        "materialized_event_count": len(materialized),
        "used_event_count": 1,
        "input": input_projection,
        "initial_field": initial_projection,
        "dock_binding": docks,
        "event": event_projection,
        "direct_field_adapter_call_count": adapter_call_count,
        "original_exception": failure,
        "post_field": post_field,
        "execution_exclusions": {
            "s2mr_runtime_calls": 0,
            "memory_state_calls": 0,
            "context_calls": 0,
            "transfer_main_calls": 0,
        },
    }
    payload["record_digest"] = _digest(payload)
    _write_once(output_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_diagnostic(args.workspace.resolve(), args.output.resolve())
    print(
        json.dumps(
            {
                "diagnostic_id": result["diagnostic_id"],
                "technical_status": result["technical_status"],
                "exception": result["original_exception"],
                "record_digest": result["record_digest"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__: tuple[str, ...] = ()
