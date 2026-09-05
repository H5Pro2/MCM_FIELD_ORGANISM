"""One-shot receptor and direct PPB materialization of the presealed S2-MG plan."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from threading import Lock

from mcm_field_organism._ppb1_reference import (
    advance_ppb1_bank,
    initial_ppb1_bank_state,
    normalized_mean_l1_distance,
)
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.receptor_contract import ReceptorContactFrame
from tools import _s2jw_default_live_profile as live_profile
from tools import _s2ly_private_two_view_projection as form_projection
from tools import _s2mg_private_presealed_applicability_corpus as corpus


SCHEMA = "s2mh.s2mg-receptor-ppb-materialization.v1"
MATERIALIZATION_ID = "s2mh-s2mg-receptor-ppb-materialization-20260905-01"
EXPECTED_PLAN_ID = "s2mg-slot-applicability-corpus-20260905-01"
EXPECTED_PLAN_DIGEST = "ff2d0f6955e1a8b60d3a4784626b2239c61459c4a75bb12b5f4b972278c50f33"
EXPECTED_PLAN_FILE_SHA256 = "02d0834a64a762ad3c9751564d3c650ca7dbe6c6c1e9b6aeb7c171682620ae45"
EXPECTED_CORPUS_SOURCE_SHA256 = "3ed54b65d6eea6d72c5b03b883d25c884ff29fa7482c6451aa8d9a491993a639"
EXPECTED_VISUAL_CONFIG_DIGEST = "fe8b06bad66204dec3e7c80cb24bb73d740544eba23af9a8c9e1da3d3c5d9fec"

SUCCESS = "S2ME_SLOT_APPLICABILITY_HISTORY_LOW_MATERIALIZABILITY_CONFIRMED"
NOT_MATERIALIZABLE = "S2ME_SLOT_APPLICABILITY_HISTORY_NOT_MATERIALIZABLE"
NOT_EVALUABLE = "NOT_EVALUABLE"
MATERIALIZATION_ENABLED = False

MAX_RESULT_BYTES = 262_144
_LOCK = Lock()
_USED = False


class S2MHMaterializationError(RuntimeError):
    """The sealed source, receptor, or PPB binding differs."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MHMaterializationError(message)


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    data = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return data + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_plan(plan_path: Path, corpus_source_path: Path) -> dict[str, object]:
    _require(plan_path.is_file(), "presealed plan is absent")
    _require(corpus_source_path.is_file(), "presealed corpus source is absent")
    _require(_file_sha256(plan_path) == EXPECTED_PLAN_FILE_SHA256, "plan file hash differs")
    _require(
        _file_sha256(corpus_source_path) == EXPECTED_CORPUS_SOURCE_SHA256,
        "presealed corpus source hash differs",
    )
    plan = json.loads(plan_path.read_text(encoding="ascii"))
    _require(type(plan) is dict, "plan form differs")
    body = dict(plan)
    bound_digest = body.pop("plan_digest", None)
    _require(
        plan.get("schema") == corpus.SCHEMA
        and plan.get("plan_id") == EXPECTED_PLAN_ID
        and bound_digest == EXPECTED_PLAN_DIGEST
        and _digest(body) == EXPECTED_PLAN_DIGEST,
        "plan digest differs",
    )
    source_root = plan.get("source_root")
    execution_root = plan.get("execution_root")
    mask_root = plan.get("mask_root")
    decision_rule = plan.get("decision_rule")
    _require(type(source_root) is dict, "source root differs")
    _require(type(execution_root) is dict, "execution root differs")
    _require(type(mask_root) is dict, "mask root differs")
    _require(type(decision_rule) is dict, "decision rule differs")
    _require(
        execution_root.get("event_count") == 19
        and len(execution_root.get("formation_events", [])) == 19
        and execution_root.get("receptor_calls") == 0
        and execution_root.get("ppb_calls") == 0
        and execution_root.get("memory_calls") == 0
        and execution_root.get("context_calls") == 0
        and execution_root.get("field_calls") == 0,
        "execution root count or call binding differs",
    )
    _require(
        decision_rule
        == {
            "required_start_chain": ["CREATED", "MATCHED", "MATCHED"],
            "minimum_distinct_visual_values_digests": 2,
            "minimum_distinct_form_descriptor_digests": 2,
            "failure_status": NOT_MATERIALIZABLE,
            "corpus_change_retry_or_threshold_change_allowed": False,
        },
        "decision rule differs",
    )
    return plan


def _preflight_sources(plan: dict[str, object]) -> tuple[tuple[str, object], ...]:
    source_root = plan["source_root"]
    assert isinstance(source_root, dict)
    recipes = source_root.get("recipes")
    bindings = source_root.get("source_bindings")
    _require(type(recipes) is list and len(recipes) == 27, "source recipe inventory differs")
    _require(type(bindings) is list and len(bindings) == 27, "source binding inventory differs")
    binding_by_id = {
        str(item["source_id"]): item
        for item in bindings
        if type(item) is dict and "source_id" in item
    }
    _require(len(binding_by_id) == 27, "source binding identifiers differ")

    frames: list[tuple[str, object]] = []
    confirmed: list[dict[str, object]] = []
    for recipe in recipes:
        _require(type(recipe) is dict, "source recipe form differs")
        source_id = str(recipe.get("source_id"))
        binding = binding_by_id.get(source_id)
        _require(type(binding) is dict, "source binding is absent")
        frame = corpus._render_frame(dict(recipe))
        raw = frame.tobytes(order="C")
        source_payload = {
            "source_id": source_id,
            "payload_sha256": hashlib.sha256(raw).hexdigest(),
            "payload_bytes": len(raw),
            "rgb_value_sum": int(frame.sum(dtype="uint64")),
        }
        _require(
            source_payload["payload_sha256"] == binding.get("payload_sha256")
            and source_payload["payload_bytes"] == binding.get("payload_bytes")
            and source_payload["rgb_value_sum"] == binding.get("rgb_value_sum")
            and _digest(source_payload) == binding.get("source_binding_digest"),
            "source payload binding differs",
        )
        frames.append((source_id, frame))
        confirmed.append(
            {
                "source_id": source_id,
                "payload_sha256": source_payload["payload_sha256"],
                "source_binding_digest": binding["source_binding_digest"],
            }
        )
    _require(len({item["payload_sha256"] for item in confirmed}) == 27, "payload digest inventory repeats")
    return tuple(frames)


def _union_mask(plan: dict[str, object]) -> dict[str, object]:
    mask_root = plan["mask_root"]
    assert isinstance(mask_root, dict)
    masks = mask_root.get("masks")
    _require(type(masks) is list and len(masks) == 3, "mask inventory differs")
    selected = [item for item in masks if type(item) is dict and item.get("mask_id") == "UNION_192"]
    _require(len(selected) == 1, "union mask differs")
    union = selected[0]
    positions = union.get("positions")
    _require(
        type(positions) is list
        and len(positions) == 192
        and len(set(positions)) == 192
        and all(type(item) is int and 0 <= item < 288 for item in positions),
        "union mask positions differ",
    )
    payload = dict(union)
    bound_digest = payload.pop("mask_digest", None)
    _require(_digest(payload) == bound_digest, "union mask digest differs")
    return union


def _receptor_materialization(
    frames: tuple[tuple[str, object], ...],
    plan: dict[str, object],
) -> tuple[dict[str, dict[str, object]], dict[str, tuple[float, ...]], dict[str, str]]:
    receptor = LocalChannelGridReceptor(VisualGridConfig())
    profile = live_profile.build_s2jw_default_live_profile()
    _require(profile.profile.visual_config.digest() == EXPECTED_VISUAL_CONFIG_DIGEST, "visual PPB config differs")
    union = _union_mask(plan)
    positions = tuple(union["positions"])
    mask_digest = str(union["mask_digest"])
    event_source_ids = {
        str(item["source_id"])
        for item in plan["execution_root"]["formation_events"]  # type: ignore[index]
    }

    records: dict[str, dict[str, object]] = {}
    values_by_source: dict[str, tuple[float, ...]] = {}
    descriptor_by_source: dict[str, str] = {}
    for frame_index, (source_id, frame) in enumerate(frames):
        state = receptor.analyze(frame, frame_index=frame_index)
        values = tuple(state.channel_values)
        _require(
            len(values) == 288
            and state.geometry_id == profile.profile.visual_config.geometry_id
            and tuple(state.carrier_ids) == profile.profile.visual_config.carrier_ids,
            "visual receptor state differs",
        )
        values_digest = _digest(list(values))
        descriptor_digest = None
        if source_id in event_source_ids:
            view = form_projection.bind_observed_view(
                values,
                "UNION_192",
                positions,
                mask_digest,
            )
            descriptor = form_projection.project_mask_conditioned_form(view)
            descriptor_digest = _digest(list(descriptor.values))
            descriptor_by_source[source_id] = descriptor_digest
        records[source_id] = {
            "source_id": source_id,
            "frame_index": frame_index,
            "receptor_state_digest": state.digest(),
            "visual_values_digest": values_digest,
            "form_descriptor_digest": descriptor_digest,
            "geometry_id": state.geometry_id,
            "carrier_inventory_digest": _digest(list(state.carrier_ids)),
        }
        values_by_source[source_id] = values
    _require(len(records) == 27 and len(values_by_source) == 27, "receptor endpoint count differs")
    _require(len(descriptor_by_source) == len(event_source_ids), "formation descriptor count differs")
    return records, values_by_source, descriptor_by_source


def _slot_digest(state: object, slot_id: str) -> str:
    slots = getattr(state, "slots")
    selected = [slot for slot in slots if slot.slot_id == slot_id]
    _require(len(selected) == 1 and selected[0].occupied, "selected slot is absent")
    return _digest(selected[0].canonical_payload())


def _ppb_materialization(
    plan: dict[str, object],
    receptor_records: dict[str, dict[str, object]],
    values_by_source: dict[str, tuple[float, ...]],
    descriptor_by_source: dict[str, str],
) -> tuple[list[dict[str, object]], list[dict[str, object]], object]:
    profile = live_profile.build_s2jw_default_live_profile()
    config = profile.profile.visual_config
    state = initial_ppb1_bank_state(config)
    events = plan["execution_root"]["formation_events"]  # type: ignore[index]
    _require(type(events) is list and len(events) == 19, "formation events differ")

    generation_by_slot: dict[str, str] = {}
    histories: dict[str, list[dict[str, object]]] = {}
    transitions: list[dict[str, object]] = []
    for expected_ordinal, event in enumerate(events, start=1):
        _require(type(event) is dict and event.get("ordinal") == expected_ordinal, "formation order differs")
        event_payload = dict(event)
        event_digest = event_payload.pop("event_digest", None)
        _require(_digest(event_payload) == event_digest, "formation event digest differs")
        source_id = str(event["source_id"])
        receptor_record = receptor_records[source_id]
        frame = ReceptorContactFrame(
            modality_id="visual",
            geometry_id=config.geometry_id,
            snapshot_id=str(event["event_id"]),
            clock_id=str(event["source_clock_id"]),
            window_start_tick=int(event["window_start_tick"]),
            window_end_tick=int(event["window_end_tick"]),
            carrier_ids=config.carrier_ids,
            values=values_by_source[source_id],
        )
        prestate_digest = state.digest()
        occupied_distances = [
            normalized_mean_l1_distance(frame.values, slot.prototype_values)
            for slot in state.slots
            if slot.occupied
        ]
        nearest_prestate_distance = min(occupied_distances) if occupied_distances else None
        result = advance_ppb1_bank(config, state, frame)
        readout = result.readout
        _require(readout.prestate_digest == prestate_digest, "PPB prestate binding differs")
        if readout.event in {"CREATED", "REPLACED"}:
            generation_payload = {
                "schema": "s2me.slot-generation.v1",
                "bank_id": config.bank_id,
                "bank_config_digest": config.digest(),
                "slot_id": readout.slot_id,
                "creation_event": readout.event,
                "ppb_prestate_digest": readout.prestate_digest,
                "ppb_input_digest": readout.input_digest,
                "ppb_transition_result_digest": readout.digest(),
                "ppb_poststate_digest": readout.poststate_digest,
                "accepted_step": result.poststate.accepted_step_count,
            }
            generation_digest = _digest(generation_payload)
            generation_by_slot[readout.slot_id] = generation_digest
            histories[generation_digest] = []
        else:
            _require(readout.slot_id in generation_by_slot, "matched slot generation is absent")
            generation_digest = generation_by_slot[readout.slot_id]
        record = {
            "ordinal": expected_ordinal,
            "event_id": event["event_id"],
            "event_digest": event_digest,
            "source_id": source_id,
            "source_binding_digest": event["source_binding_digest"],
            "receptor_state_digest": receptor_record["receptor_state_digest"],
            "visual_values_digest": receptor_record["visual_values_digest"],
            "form_descriptor_digest": descriptor_by_source[source_id],
            "ppb_event": readout.event,
            "slot_id": readout.slot_id,
            "match_distance": readout.match_distance,
            "nearest_prestate_distance": nearest_prestate_distance,
            "support_count": readout.support_count,
            "stabilized": readout.stabilized,
            "slot_generation_digest": generation_digest,
            "ppb_prestate_digest": readout.prestate_digest,
            "ppb_input_digest": readout.input_digest,
            "ppb_transition_result_digest": readout.digest(),
            "selected_slot_digest": _slot_digest(result.poststate, readout.slot_id),
            "ppb_poststate_digest": readout.poststate_digest,
        }
        record["transition_record_digest"] = _digest(record)
        transitions.append(record)
        histories[generation_digest].append(record)
        state = result.poststate

    generation_rows: list[dict[str, object]] = []
    for generation_digest, history in histories.items():
        events_for_generation = [str(item["ppb_event"]) for item in history]
        values_digests = {str(item["visual_values_digest"]) for item in history[:3]}
        descriptor_digests = {str(item["form_descriptor_digest"]) for item in history[:3]}
        qualifies = (
            events_for_generation[:3] == ["CREATED", "MATCHED", "MATCHED"]
            and len(values_digests) >= 2
            and len(descriptor_digests) >= 2
        )
        generation_rows.append(
            {
                "slot_generation_digest": generation_digest,
                "slot_id": history[0]["slot_id"],
                "creation_event": history[0]["ppb_event"],
                "transition_ordinals": [item["ordinal"] for item in history],
                "transition_events": events_for_generation,
                "support_counts": [item["support_count"] for item in history],
                "distinct_first_three_visual_values_digests": len(values_digests),
                "distinct_first_three_form_descriptor_digests": len(descriptor_digests),
                "required_chain_qualified": qualifies,
            }
        )
    return transitions, generation_rows, state


def _materialize(plan: dict[str, object]) -> dict[str, object]:
    frames = _preflight_sources(plan)
    preflight_payload = {
        "plan_file_sha256": EXPECTED_PLAN_FILE_SHA256,
        "plan_digest": EXPECTED_PLAN_DIGEST,
        "payload_count": len(frames),
        "payload_sha256_by_source": {
            source_id: hashlib.sha256(frame.tobytes(order="C")).hexdigest()
            for source_id, frame in frames
        },
        "completed_before_first_receptor_call": True,
    }
    preflight_digest = _digest(preflight_payload)

    receptor_records, values_by_source, descriptor_by_source = _receptor_materialization(frames, plan)
    del frames
    transitions, generations, final_state = _ppb_materialization(
        plan,
        receptor_records,
        values_by_source,
        descriptor_by_source,
    )
    qualified = [item for item in generations if item["required_chain_qualified"]]
    status = SUCCESS if qualified else NOT_MATERIALIZABLE
    result_payload = {
        "schema": SCHEMA,
        "materialization_id": MATERIALIZATION_ID,
        "plan_id": EXPECTED_PLAN_ID,
        "plan_digest": EXPECTED_PLAN_DIGEST,
        "plan_file_sha256": EXPECTED_PLAN_FILE_SHA256,
        "corpus_source_sha256": EXPECTED_CORPUS_SOURCE_SHA256,
        "status": status,
        "preflight": {**preflight_payload, "preflight_digest": preflight_digest},
        "receptor_states": [receptor_records[source_id] for source_id in sorted(receptor_records)],
        "ppb_transitions": transitions,
        "slot_generations": generations,
        "qualified_slot_generation_digests": [
            item["slot_generation_digest"] for item in qualified
        ],
        "final_ppb_state_digest": final_state.digest(),
        "final_ppb_slots": [
            {
                "slot_id": slot.slot_id,
                "occupied": slot.occupied,
                "support_count": slot.support_count,
                "last_selected_step": slot.last_selected_step,
                "slot_digest": _digest(slot.canonical_payload()),
                "slot_generation_digest": next(
                    (
                        item["slot_generation_digest"]
                        for item in reversed(generations)
                        if item["slot_id"] == slot.slot_id
                    ),
                    None,
                ),
            }
            for slot in final_state.slots
        ],
        "counts": {
            "source_payloads_preconfirmed": 27,
            "visual_receptor_calls": 27,
            "visual_receptor_states": len(receptor_records),
            "formation_descriptors": len(descriptor_by_source),
            "ppb_calls": len(transitions),
            "ppb_transitions": len(transitions),
            "slot_generations": len(generations),
            "qualified_slot_generations": len(qualified),
            "holdout_evaluations": 0,
            "memory_coordinator_calls": 0,
            "envelope_calls": 0,
            "context_calls": 0,
            "field_calls": 0,
        },
        "holdout_evaluation_performed": False,
        "source_regenerations": 0,
        "source_reorderings": 0,
        "seed_changes": 0,
        "threshold_changes": 0,
        "raw_payload_retained": False,
        "actual_b4_tspm_coordinator_used": False,
        "static_fast_trigger_audit_required_if_positive": status == SUCCESS,
    }
    return {**result_payload, "result_digest": _digest(result_payload)}


def _failure(plan_path: Path, stage: str) -> dict[str, object]:
    payload = {
        "schema": SCHEMA,
        "materialization_id": MATERIALIZATION_ID,
        "plan_id": EXPECTED_PLAN_ID,
        "plan_digest": EXPECTED_PLAN_DIGEST,
        "status": NOT_EVALUABLE,
        "technical_failure_stage": stage,
        "plan_file_sha256": _file_sha256(plan_path) if plan_path.is_file() else None,
        "holdout_evaluation_performed": False,
        "source_regenerations": 0,
        "source_reorderings": 0,
        "seed_changes": 0,
        "threshold_changes": 0,
        "raw_payload_retained": False,
        "memory_coordinator_calls": 0,
        "envelope_calls": 0,
        "context_calls": 0,
        "field_calls": 0,
    }
    return {**payload, "result_digest": _digest(payload)}


def materialize_once(
    *,
    workspace_root: Path,
    output_root: Path,
    plan_path: Path,
    materialization_id: str,
) -> Path:
    global MATERIALIZATION_ENABLED, _USED
    _require(MATERIALIZATION_ENABLED is True, "materialization gate is closed")
    _require(materialization_id == MATERIALIZATION_ID, "materialization id differs")
    _require(
        isinstance(workspace_root, Path)
        and workspace_root.is_absolute()
        and isinstance(output_root, Path)
        and output_root.is_absolute()
        and isinstance(plan_path, Path)
        and plan_path.is_absolute(),
        "absolute pathlib paths are required",
    )
    _require(not _USED and _LOCK.acquire(blocking=False), "materialization is consumed")
    _USED = True
    try:
        stage = "PLAN_PREFLIGHT"
        try:
            corpus_source_path = workspace_root / "tools" / "_s2mg_private_presealed_applicability_corpus.py"
            plan = _validate_plan(plan_path, corpus_source_path)
            stage = "SOURCE_PREFLIGHT_OR_RECEPTOR_PPB"
            result = _materialize(plan)
        except Exception:
            result = _failure(plan_path, stage)
        target_dir = output_root / materialization_id
        target_dir.mkdir(parents=True, exist_ok=False)
        target = target_dir / "materialization.json"
        temporary = target_dir / ".materialization.json.tmp"
        data = _canonical_bytes(result, newline=True)
        _require(len(data) <= MAX_RESULT_BYTES, "materialization result exceeds bound")
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, target)
        except Exception:
            if temporary.exists():
                temporary.unlink()
            raise
        return target
    finally:
        MATERIALIZATION_ENABLED = False
        _LOCK.release()


__all__: tuple[str, ...] = ()
