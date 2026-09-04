"""One-shot receptor materialization of the exact presealed S2-LS corpus."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from threading import Lock

import numpy as np

from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from tools import _s2ls_private_presealed_av_corpus_plan as corpus


SCHEMA = "s2ls.corpus-receptor-materialization.v1"
MATERIALIZATION_ID = "s2ls-corpus-receptor-materialization-20260904-01"
EXPECTED_PLAN_ID = "s2ls-presealed-av-corpus-plan-20260904-01"
EXPECTED_PLAN_DIGEST = "1ad42964295cce44b87f6c3d02479983878ca7c403eee21440783fe3326e661a"
MATERIALIZATION_ENABLED = False
SUCCESS = "S2LS_RECEPTOR_GEOMETRY_MATERIALIZED"
NOT_EVALUABLE = "NOT_EVALUABLE"

_LOCK = Lock()
_USED = False


class S2LSReceptorMaterializationError(RuntimeError):
    """A technical source, plan, time, form, or digest binding is invalid."""


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    payload = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return payload + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _bytes_digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _mean_l1(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right) or not left:
        raise S2LSReceptorMaterializationError("distance dimensions differ")
    return sum(abs(a - b) for a, b in zip(left, right, strict=True)) / len(left)


def _indexed_mean_l1(
    left: tuple[float, ...],
    right: tuple[float, ...],
    positions: tuple[int, ...],
) -> float:
    if len(left) != len(right) or not positions:
        raise S2LSReceptorMaterializationError("indexed distance dimensions differ")
    return sum(abs(left[index] - right[index]) for index in positions) / len(positions)


def _validate_plan(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise S2LSReceptorMaterializationError("presealed plan is absent")
    plan = json.loads(path.read_text(encoding="ascii"))
    if not isinstance(plan, dict):
        raise S2LSReceptorMaterializationError("presealed plan form differs")
    body = dict(plan)
    bound_digest = body.pop("plan_digest", None)
    if (
        plan.get("schema") != "s2ls.presealed-av-corpus-plan.v1"
        or plan.get("plan_id") != EXPECTED_PLAN_ID
        or bound_digest != EXPECTED_PLAN_DIGEST
        or _digest(body) != EXPECTED_PLAN_DIGEST
    ):
        raise S2LSReceptorMaterializationError("presealed plan digest differs")
    roots = plan.get("roots")
    if not isinstance(roots, dict):
        raise S2LSReceptorMaterializationError("presealed root binding differs")
    for role in ("generation", "execution", "evaluation"):
        root = plan.get(f"{role}_root")
        if not isinstance(root, dict) or _digest(root) != roots.get(f"{role}_root_digest"):
            raise S2LSReceptorMaterializationError(f"{role} root digest differs")
    counts = plan.get("counts")
    if counts != {
        "families": 2,
        "training_variants_per_family": 4,
        "holdouts_per_family": 2,
        "pressure_events": 9,
        "formation_events": 17,
        "partial_cue_events": 8,
        "total_events": 25,
    }:
        raise S2LSReceptorMaterializationError("presealed plan counts differ")
    return plan


def _analyze_audio(payload: bytes, expected_digest: str) -> dict[str, object]:
    if len(payload) != corpus.AUDIO_BYTE_COUNT:
        raise S2LSReceptorMaterializationError("PCM byte count differs")
    if _bytes_digest(payload) != expected_digest:
        raise S2LSReceptorMaterializationError("PCM digest differs before receptor")
    samples_array = np.frombuffer(payload, dtype="<f4")
    if (
        samples_array.shape != (corpus.AUDIO_SAMPLE_COUNT,)
        or not np.isfinite(samples_array).all()
        or float(np.max(np.abs(samples_array))) > 1.0
    ):
        raise S2LSReceptorMaterializationError("PCM form differs")
    samples = tuple(float(value) for value in samples_array)
    path = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
    state = None
    for hop_index in range(10):
        if _bytes_digest(payload) != expected_digest:
            raise S2LSReceptorMaterializationError("PCM digest changed before receptor hop")
        state = path.push(samples[hop_index * 480 : (hop_index + 1) * 480])
    if (
        state is None
        or state.snapshot_index != 0
        or state.window_start_sample != 0
        or state.window_end_sample != corpus.AUDIO_SAMPLE_COUNT
        or len(state.energy) != 48
        or any(not math.isfinite(value) for value in state.energy)
    ):
        raise S2LSReceptorMaterializationError("auditory receptor state differs")
    values = tuple(state.energy)
    return {
        "modality": "AUDITORY",
        "geometry_id": state.geometry_id,
        "local_snapshot_index": state.snapshot_index,
        "local_window_start_sample": state.window_start_sample,
        "local_window_end_sample": state.window_end_sample,
        "carrier_ids": list(state.carrier_ids),
        "values": list(values),
        "values_digest": _digest(list(values)),
        "receptor_state_digest": state.digest(),
        "contact": state.contact.value,
        "payload_sha256_verified_before_each_hop": True,
        "receptor_hop_calls": 10,
    }


def _analyze_visual(
    payload: bytes,
    expected_digest: str,
    analysis_ordinal: int,
) -> dict[str, object]:
    if len(payload) != corpus.VISUAL_BYTE_COUNT:
        raise S2LSReceptorMaterializationError("RGB byte count differs")
    if _bytes_digest(payload) != expected_digest:
        raise S2LSReceptorMaterializationError("RGB digest differs before receptor")
    image = np.frombuffer(payload, dtype=np.uint8).reshape(
        corpus.VISUAL_HEIGHT,
        corpus.VISUAL_WIDTH,
        corpus.VISUAL_CHANNELS,
    )
    receptor = LocalChannelGridReceptor(VisualGridConfig())
    if _bytes_digest(payload) != expected_digest:
        raise S2LSReceptorMaterializationError("RGB digest changed before receptor call")
    state = receptor.analyze(image, frame_index=analysis_ordinal)
    if len(state.channel_values) != 288 or any(
        not math.isfinite(value) for value in state.channel_values
    ):
        raise S2LSReceptorMaterializationError("visual receptor state differs")
    values = tuple(state.channel_values)
    return {
        "modality": "VISUAL",
        "geometry_id": state.geometry_id,
        "analysis_ordinal": analysis_ordinal,
        "carrier_ids": list(state.carrier_ids),
        "values": list(values),
        "values_digest": _digest(list(values)),
        "receptor_state_digest": state.digest(),
        "contact": state.contact.value,
        "payload_sha256_verified_before_call": True,
        "receptor_frame_calls": 1,
    }


def _source_bound_state(
    *,
    content_id: str,
    payload_sha256: str,
    state: dict[str, object],
    generation_root_digest: str,
) -> dict[str, object]:
    payload = {
        "schema": "s2ls.source-bound-receptor-state.v1",
        "content_id": content_id,
        "modality": state["modality"],
        "payload_sha256": payload_sha256,
        "values_digest": state["values_digest"],
        "receptor_state_digest": state["receptor_state_digest"],
        "generation_root_digest": generation_root_digest,
    }
    return {**payload, "source_bound_state_digest": _digest(payload)}


def _event_binding(
    event: dict[str, object],
    auditory: dict[str, object] | None,
    visual: dict[str, object] | None,
    execution_root_digest: str,
) -> dict[str, object]:
    payload = {
        "schema": "s2ls.event-receptor-binding.v1",
        "event_id": event["event_id"],
        "event_digest": event["event_digest"],
        "event_kind": event["event_kind"],
        "content_id": event["content_id"],
        "event_owner_id": event["event_owner_id"],
        "common_clock_id": event["common_clock_id"],
        "common_start_ns": event["common_start_ns"],
        "common_end_ns": event["common_end_ns"],
        "visual_source_id": event["visual_source_id"],
        "visual_source_clock_id": event["visual_source_clock_id"],
        "visual_frame_index": event["visual_frame_index"],
        "visual_source_bound_state_digest": (
            visual["source_bound_state_digest"] if visual is not None else None
        ),
        "auditory_source_id": event["auditory_source_id"],
        "auditory_source_clock_id": event["auditory_source_clock_id"],
        "auditory_window_start_sample": event["auditory_window_start_sample"],
        "auditory_window_end_sample": event["auditory_window_end_sample"],
        "auditory_source_bound_state_digest": (
            auditory["source_bound_state_digest"] if auditory is not None else None
        ),
        "mask_digest": event["mask_digest"],
        "execution_root_digest": execution_root_digest,
    }
    return {**payload, "event_receptor_binding_digest": _digest(payload)}


def _materialize(plan: dict[str, object]) -> dict[str, object]:
    generation = plan["generation_root"]
    execution = plan["execution_root"]
    roots = plan["roots"]
    recipes = generation["content_recipes"]
    inventory = {
        item["content_id"]: item for item in generation["content_inventory"]
    }
    if len(recipes) != 21 or len(inventory) != 21:
        raise S2LSReceptorMaterializationError("content inventory differs")

    visual_states: dict[str, dict[str, object]] = {}
    auditory_states: dict[str, dict[str, object]] = {}
    source_bindings: dict[str, dict[str, dict[str, object]]] = {}
    cue_visual_states: dict[str, dict[str, object]] = {}
    cue_visual_bindings: dict[str, dict[str, object]] = {}

    visual_cue_events = {
        event["content_id"]: event
        for event in execution["events"]
        if event["event_kind"] == "VISUAL_PARTIAL_CUE"
    }

    for analysis_ordinal, recipe_entry in enumerate(recipes):
        content_id = recipe_entry["content_id"]
        recipe = recipe_entry["recipe"]
        item = inventory.get(content_id)
        if (
            item is None
            or recipe_entry["recipe_digest"] != item["recipe_digest"]
            or _digest(recipe) != item["recipe_digest"]
        ):
            raise S2LSReceptorMaterializationError("content recipe binding differs")

        visual_payload = corpus._visual_bytes(recipe)
        auditory_payload = corpus._audio_bytes(recipe)
        visual_digest = _bytes_digest(visual_payload)
        auditory_digest = _bytes_digest(auditory_payload)
        if (
            visual_digest != item["visual_payload_sha256"]
            or auditory_digest != item["auditory_payload_sha256"]
        ):
            raise S2LSReceptorMaterializationError("generated source digest differs")

        visual_state = _analyze_visual(
            visual_payload, visual_digest, analysis_ordinal
        )
        auditory_state = _analyze_audio(auditory_payload, auditory_digest)
        visual_states[content_id] = visual_state
        auditory_states[content_id] = auditory_state
        source_bindings[content_id] = {
            "VISUAL": _source_bound_state(
                content_id=content_id,
                payload_sha256=visual_digest,
                state=visual_state,
                generation_root_digest=roots["generation_root_digest"],
            ),
            "AUDITORY": _source_bound_state(
                content_id=content_id,
                payload_sha256=auditory_digest,
                state=auditory_state,
                generation_root_digest=roots["generation_root_digest"],
            ),
        }

        cue_event = visual_cue_events.get(content_id)
        if cue_event is not None:
            cue_payload = corpus._masked_visual_bytes(visual_payload)
            cue_digest = _bytes_digest(cue_payload)
            if cue_digest != cue_event["visual_payload_sha256"]:
                raise S2LSReceptorMaterializationError("visual cue digest differs")
            cue_state = _analyze_visual(
                cue_payload,
                cue_digest,
                int(cue_event["visual_frame_index"]),
            )
            cue_visual_states[content_id] = cue_state
            cue_visual_bindings[content_id] = _source_bound_state(
                content_id=content_id,
                payload_sha256=cue_digest,
                state=cue_state,
                generation_root_digest=roots["generation_root_digest"],
            )

        del visual_payload
        del auditory_payload

    content_ids = tuple(sorted(inventory))
    pairwise_distances = []
    for left_index, left_id in enumerate(content_ids):
        for right_id in content_ids[left_index + 1 :]:
            payload = {
                "left_content_id": left_id,
                "right_content_id": right_id,
                "auditory_mean_l1": _mean_l1(
                    tuple(auditory_states[left_id]["values"]),
                    tuple(auditory_states[right_id]["values"]),
                ),
                "visual_mean_l1": _mean_l1(
                    tuple(visual_states[left_id]["values"]),
                    tuple(visual_states[right_id]["values"]),
                ),
            }
            pairwise_distances.append({**payload, "distance_digest": _digest(payload)})

    cue_distances = []
    for event in execution["events"]:
        if event["event_kind"] == "VISUAL_PARTIAL_CUE":
            cue_values = tuple(cue_visual_states[event["content_id"]]["values"])
            for candidate_id in content_ids:
                candidate = tuple(visual_states[candidate_id]["values"])
                payload = {
                    "event_id": event["event_id"],
                    "modality": "VISUAL",
                    "candidate_content_id": candidate_id,
                    "observed_mean_l1": _indexed_mean_l1(
                        cue_values, candidate, corpus.VISUAL_OBSERVED
                    ),
                    "observed_exact_mismatch_count": sum(
                        cue_values[index] != candidate[index]
                        for index in corpus.VISUAL_OBSERVED
                    ),
                }
                cue_distances.append({**payload, "distance_digest": _digest(payload)})
        elif event["event_kind"] == "AUDITORY_PARTIAL_CUE":
            cue_values = tuple(auditory_states[event["content_id"]]["values"])
            for candidate_id in content_ids:
                candidate = tuple(auditory_states[candidate_id]["values"])
                payload = {
                    "event_id": event["event_id"],
                    "modality": "AUDITORY",
                    "candidate_content_id": candidate_id,
                    "observed_mean_l1": _indexed_mean_l1(
                        cue_values, candidate, corpus.AUDIO_OBSERVED
                    ),
                }
                cue_distances.append({**payload, "distance_digest": _digest(payload)})

    event_bindings = []
    for event in execution["events"]:
        content_id = event["content_id"]
        if event["event_kind"] == "FULL_AV_FORMATION":
            auditory = source_bindings[content_id]["AUDITORY"]
            visual = source_bindings[content_id]["VISUAL"]
        elif event["event_kind"] == "VISUAL_PARTIAL_CUE":
            auditory = None
            visual = cue_visual_bindings[content_id]
        elif event["event_kind"] == "AUDITORY_PARTIAL_CUE":
            auditory = source_bindings[content_id]["AUDITORY"]
            visual = None
        else:
            raise S2LSReceptorMaterializationError("event kind differs")
        event_bindings.append(_event_binding(
            event,
            auditory,
            visual,
            roots["execution_root_digest"],
        ))

    evidence_payload = {
        "schema": SCHEMA,
        "materialization_id": MATERIALIZATION_ID,
        "plan_id": plan["plan_id"],
        "plan_digest": plan["plan_digest"],
        "roots": roots,
        "status": SUCCESS,
        "content_receptor_states": [
            {
                "content_id": content_id,
                "auditory": auditory_states[content_id],
                "visual": visual_states[content_id],
                "source_bindings": source_bindings[content_id],
            }
            for content_id in content_ids
        ],
        "visual_cue_receptor_states": [
            {
                "content_id": content_id,
                "state": cue_visual_states[content_id],
                "source_binding": cue_visual_bindings[content_id],
            }
            for content_id in sorted(cue_visual_states)
        ],
        "event_receptor_bindings": event_bindings,
        "pairwise_full_distances": pairwise_distances,
        "partial_cue_distances": cue_distances,
        "counts": {
            "content_sources": len(content_ids),
            "auditory_states": len(auditory_states),
            "visual_full_states": len(visual_states),
            "visual_cue_states": len(cue_visual_states),
            "event_bindings": len(event_bindings),
            "pairwise_distance_rows": len(pairwise_distances),
            "partial_cue_distance_rows": len(cue_distances),
            "auditory_receptor_hop_calls": 10 * len(auditory_states),
            "auditory_receptor_endpoints": len(auditory_states),
            "visual_receptor_calls": len(visual_states) + len(cue_visual_states),
        },
        "distance_acceptance_gate_used": False,
        "source_replacements": 0,
        "source_regenerations": 0,
        "source_scalings": 0,
        "raw_payload_retained": False,
        "memory_calls": 0,
        "field_calls": 0,
        "context_calls": 0,
    }
    return {**evidence_payload, "evidence_digest": _digest(evidence_payload)}


def _failure(plan_path: Path, code: str) -> dict[str, object]:
    payload = {
        "schema": SCHEMA,
        "materialization_id": MATERIALIZATION_ID,
        "plan_id": EXPECTED_PLAN_ID,
        "plan_digest": EXPECTED_PLAN_DIGEST,
        "status": NOT_EVALUABLE,
        "technical_error_code": code,
        "plan_path_sha256": (
            _bytes_digest(plan_path.read_bytes()) if plan_path.is_file() else None
        ),
        "distance_acceptance_gate_used": False,
        "source_replacements": 0,
        "source_regenerations": 0,
        "source_scalings": 0,
        "raw_payload_retained": False,
        "memory_calls": 0,
        "field_calls": 0,
        "context_calls": 0,
    }
    return {**payload, "evidence_digest": _digest(payload)}


def materialize_receptors_once(
    *,
    plan_path: Path,
    output_root: Path,
    materialization_id: str,
) -> Path:
    global MATERIALIZATION_ENABLED, _USED
    if MATERIALIZATION_ENABLED is not True or materialization_id != MATERIALIZATION_ID:
        raise S2LSReceptorMaterializationError("materialization is not authorized")
    if _USED or not _LOCK.acquire(blocking=False):
        raise S2LSReceptorMaterializationError("materialization is consumed")
    _USED = True
    try:
        try:
            plan = _validate_plan(plan_path)
            evidence = _materialize(plan)
        except (S2LSReceptorMaterializationError, ValueError, TypeError, json.JSONDecodeError) as exc:
            evidence = _failure(plan_path, type(exc).__name__)
        target_dir = output_root / materialization_id
        target_dir.mkdir(parents=True, exist_ok=False)
        target = target_dir / "receptor-materialization.json"
        temporary = target_dir / ".receptor-materialization.json.tmp"
        temporary.write_bytes(_canonical_bytes(evidence, newline=True))
        temporary.replace(target)
        return target
    finally:
        MATERIALIZATION_ENABLED = False
        _LOCK.release()


__all__: tuple[str, ...] = ()
