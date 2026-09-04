"""One-shot receptor-free materialization of the private S2-LS corpus plan."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
from threading import Lock

import numpy as np


SCHEMA = "s2ls.presealed-av-corpus-plan.v1"
PLAN_ID = "s2ls-presealed-av-corpus-plan-20260904-01"
MATERIALIZATION_ENABLED = False
VISUAL_WIDTH = 1_920
VISUAL_HEIGHT = 1_080
VISUAL_CHANNELS = 3
VISUAL_BYTE_COUNT = VISUAL_WIDTH * VISUAL_HEIGHT * VISUAL_CHANNELS
AUDIO_SAMPLE_RATE = 48_000
AUDIO_SAMPLE_COUNT = 4_800
AUDIO_BYTE_COUNT = AUDIO_SAMPLE_COUNT * 4
EVENT_DURATION_NS = 100_000_000
VISUAL_OBSERVED = tuple(range(32))
VISUAL_MASKED = tuple(range(32, 288))
AUDIO_OBSERVED = tuple(range(24))
AUDIO_MASKED = tuple(range(24, 48))

_LOCK = Lock()
_USED = False


class S2LSPlanError(RuntimeError):
    """The presealed corpus plan is invalid or already consumed."""


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


def _family_recipe(
    *,
    base_seed: str,
    variation_seed: str,
    period_a: int,
    period_b: int,
    phase_a: int,
    phase_b: int,
) -> dict[str, object]:
    return {
        "visual": {
            "algorithm": "SHAKE256_BASE_XOR_LOW_NIBBLE_V1",
            "base_seed": base_seed,
            "variation_seed": variation_seed,
            "byte_count": VISUAL_BYTE_COUNT,
        },
        "auditory": {
            "algorithm": "TWO_BINARY_SQUARES_PCM_F32LE_V1",
            "period_a": period_a,
            "period_b": period_b,
            "phase_a": phase_a,
            "phase_b": phase_b,
            "amplitude_a_f32_hex": struct.pack("<f", 0.28125).hex(),
            "amplitude_b_f32_hex": struct.pack("<f", 0.125).hex(),
            "sample_count": AUDIO_SAMPLE_COUNT,
            "sample_rate": AUDIO_SAMPLE_RATE,
        },
    }


def _pressure_recipe(index: int, period: int) -> dict[str, object]:
    return {
        "visual": {
            "algorithm": "SHAKE256_DIRECT_RGB8_V1",
            "seed": f"s2ls-pressure-visual-{index:02d}",
            "byte_count": VISUAL_BYTE_COUNT,
        },
        "auditory": {
            "algorithm": "ONE_BINARY_SQUARE_PCM_F32LE_V1",
            "period": period,
            "phase": index * 7,
            "amplitude_f32_hex": struct.pack("<f", 0.5).hex(),
            "sample_count": AUDIO_SAMPLE_COUNT,
            "sample_rate": AUDIO_SAMPLE_RATE,
        },
    }


_GROUP_01_RECIPES = (
    _family_recipe(base_seed="s2ls-base-01", variation_seed="s2ls-v-001", period_a=109, period_b=37, phase_a=0, phase_b=5),
    _family_recipe(base_seed="s2ls-base-01", variation_seed="s2ls-v-002", period_a=107, period_b=37, phase_a=7, phase_b=11),
    _family_recipe(base_seed="s2ls-base-01", variation_seed="s2ls-v-003", period_a=111, period_b=39, phase_a=14, phase_b=17),
    _family_recipe(base_seed="s2ls-base-01", variation_seed="s2ls-v-004", period_a=105, period_b=35, phase_a=21, phase_b=23),
    _family_recipe(base_seed="s2ls-base-01", variation_seed="s2ls-v-005", period_a=108, period_b=38, phase_a=4, phase_b=8),
    _family_recipe(base_seed="s2ls-base-01", variation_seed="s2ls-v-006", period_a=106, period_b=36, phase_a=18, phase_b=20),
)
_GROUP_02_RECIPES = (
    _family_recipe(base_seed="s2ls-base-02", variation_seed="s2ls-v-007", period_a=83, period_b=29, phase_a=0, phase_b=3),
    _family_recipe(base_seed="s2ls-base-02", variation_seed="s2ls-v-008", period_a=81, period_b=29, phase_a=5, phase_b=9),
    _family_recipe(base_seed="s2ls-base-02", variation_seed="s2ls-v-009", period_a=85, period_b=31, phase_a=12, phase_b=15),
    _family_recipe(base_seed="s2ls-base-02", variation_seed="s2ls-v-010", period_a=79, period_b=27, phase_a=19, phase_b=21),
    _family_recipe(base_seed="s2ls-base-02", variation_seed="s2ls-v-011", period_a=82, period_b=30, phase_a=3, phase_b=7),
    _family_recipe(base_seed="s2ls-base-02", variation_seed="s2ls-v-012", period_a=84, period_b=28, phase_a=16, phase_b=18),
)
_PRESSURE_PERIODS = (400, 300, 240, 160, 120, 80, 60, 40, 30)

CONTENT_RECIPES = tuple(
    (f"content-{index:03d}", recipe)
    for index, recipe in enumerate(
        (*_GROUP_01_RECIPES, *_GROUP_02_RECIPES), start=1
    )
) + tuple(
    (f"content-{index + 12:03d}", _pressure_recipe(index, period))
    for index, period in enumerate(_PRESSURE_PERIODS, start=1)
)

FORMATION_CONTENT_ORDER = (
    "content-001",
    "content-007",
    "content-002",
    "content-008",
    "content-003",
    "content-009",
    "content-004",
    "content-010",
    "content-013",
    "content-014",
    "content-015",
    "content-016",
    "content-017",
    "content-018",
    "content-019",
    "content-020",
    "content-021",
)
HOLDOUT_CONTENT_ORDER = (
    "content-005",
    "content-006",
    "content-011",
    "content-012",
)


def _visual_bytes(recipe: dict[str, object]) -> bytes:
    visual = recipe["visual"]
    algorithm = visual["algorithm"]
    if algorithm == "SHAKE256_BASE_XOR_LOW_NIBBLE_V1":
        base = np.frombuffer(
            hashlib.shake_256(str(visual["base_seed"]).encode("ascii")).digest(
                VISUAL_BYTE_COUNT
            ),
            dtype=np.uint8,
        )
        variation = np.frombuffer(
            hashlib.shake_256(str(visual["variation_seed"]).encode("ascii")).digest(
                VISUAL_BYTE_COUNT
            ),
            dtype=np.uint8,
        )
        return np.bitwise_xor(base, np.bitwise_and(variation, 15)).tobytes()
    if algorithm == "SHAKE256_DIRECT_RGB8_V1":
        return hashlib.shake_256(str(visual["seed"]).encode("ascii")).digest(
            VISUAL_BYTE_COUNT
        )
    raise S2LSPlanError("visual generator differs")


def _square(index: int, period: int, phase: int, amplitude: float) -> float:
    half = period // 2
    return amplitude if ((index + phase) // half) % 2 == 0 else -amplitude


def _audio_bytes(recipe: dict[str, object]) -> bytes:
    auditory = recipe["auditory"]
    algorithm = auditory["algorithm"]
    samples = np.empty(AUDIO_SAMPLE_COUNT, dtype="<f4")
    if algorithm == "TWO_BINARY_SQUARES_PCM_F32LE_V1":
        amplitude_a = struct.unpack("<f", bytes.fromhex(str(auditory["amplitude_a_f32_hex"])))[0]
        amplitude_b = struct.unpack("<f", bytes.fromhex(str(auditory["amplitude_b_f32_hex"])))[0]
        for index in range(AUDIO_SAMPLE_COUNT):
            samples[index] = _square(
                index,
                int(auditory["period_a"]),
                int(auditory["phase_a"]),
                amplitude_a,
            ) + _square(
                index,
                int(auditory["period_b"]),
                int(auditory["phase_b"]),
                amplitude_b,
            )
    elif algorithm == "ONE_BINARY_SQUARE_PCM_F32LE_V1":
        amplitude = struct.unpack("<f", bytes.fromhex(str(auditory["amplitude_f32_hex"])))[0]
        for index in range(AUDIO_SAMPLE_COUNT):
            samples[index] = _square(
                index,
                int(auditory["period"]),
                int(auditory["phase"]),
                amplitude,
            )
    else:
        raise S2LSPlanError("auditory generator differs")
    if not np.isfinite(samples).all() or float(np.max(np.abs(samples))) > 1.0:
        raise S2LSPlanError("PCM sample boundary differs")
    return samples.tobytes()


def _masked_visual_bytes(payload: bytes) -> bytes:
    frame = np.frombuffer(payload, dtype=np.uint8).reshape(
        VISUAL_HEIGHT, VISUAL_WIDTH, VISUAL_CHANNELS
    ).copy()
    for receptor_index in VISUAL_MASKED:
        cell_index, channel = divmod(receptor_index, VISUAL_CHANNELS)
        row, column = divmod(cell_index, 12)
        frame[
            row * 135 : (row + 1) * 135,
            column * 160 : (column + 1) * 160,
            channel,
        ] = 0
    return frame.tobytes()


def _content_inventory() -> tuple[tuple[dict[str, object], ...], dict[str, bytes], dict[str, bytes]]:
    records = []
    visual_payloads: dict[str, bytes] = {}
    audio_payloads: dict[str, bytes] = {}
    for content_id, recipe in CONTENT_RECIPES:
        visual = _visual_bytes(recipe)
        auditory = _audio_bytes(recipe)
        if len(visual) != VISUAL_BYTE_COUNT or len(auditory) != AUDIO_BYTE_COUNT:
            raise S2LSPlanError("canonical payload size differs")
        visual_payloads[content_id] = visual
        audio_payloads[content_id] = auditory
        records.append({
            "content_id": content_id,
            "recipe_digest": _digest(recipe),
            "visual_payload_sha256": _bytes_digest(visual),
            "visual_byte_count": len(visual),
            "auditory_payload_sha256": _bytes_digest(auditory),
            "auditory_byte_count": len(auditory),
        })
    return tuple(records), visual_payloads, audio_payloads


def _event(
    *,
    ordinal: int,
    event_kind: str,
    content_id: str,
    visual_payload_sha256: str | None,
    auditory_payload_sha256: str | None,
    mask_digest: str | None,
) -> dict[str, object]:
    start_ns = (ordinal - 1) * EVENT_DURATION_NS
    end_ns = ordinal * EVENT_DURATION_NS
    payload = {
        "event_id": f"event-{ordinal:03d}",
        "event_kind": event_kind,
        "content_id": content_id,
        "event_owner_id": f"s2ls-event-owner-{ordinal:03d}",
        "common_clock_id": "s2ls-common-av-clock",
        "common_start_ns": start_ns,
        "common_end_ns": end_ns,
        "visual_source_id": f"visual-source-{ordinal:03d}" if visual_payload_sha256 else None,
        "visual_source_clock_id": "s2ls-visual-native-clock" if visual_payload_sha256 else None,
        "visual_frame_index": 3 * (ordinal - 1) + 2 if visual_payload_sha256 else None,
        "visual_payload_sha256": visual_payload_sha256,
        "auditory_source_id": f"auditory-source-{ordinal:03d}" if auditory_payload_sha256 else None,
        "auditory_source_clock_id": "s2ls-auditory-native-clock" if auditory_payload_sha256 else None,
        "auditory_window_start_sample": (ordinal - 1) * AUDIO_SAMPLE_COUNT if auditory_payload_sha256 else None,
        "auditory_window_end_sample": ordinal * AUDIO_SAMPLE_COUNT if auditory_payload_sha256 else None,
        "auditory_payload_sha256": auditory_payload_sha256,
        "mask_digest": mask_digest,
    }
    return {**payload, "event_digest": _digest(payload)}


def _build_plan() -> dict[str, object]:
    inventory, visual_payloads, audio_payloads = _content_inventory()
    by_id = {item["content_id"]: item for item in inventory}

    visual_mask = {
        "schema": "s2ls.visual-receptor-position-mask.v1",
        "observed_positions": list(VISUAL_OBSERVED),
        "masked_positions": list(VISUAL_MASKED),
        "occlusion_byte": 0,
    }
    auditory_mask = {
        "schema": "s2ls.auditory-band-mask.v1",
        "observed_bands": list(AUDIO_OBSERVED),
        "masked_bands": list(AUDIO_MASKED),
    }
    visual_mask_digest = _digest(visual_mask)
    auditory_mask_digest = _digest(auditory_mask)

    events = []
    for ordinal, content_id in enumerate(FORMATION_CONTENT_ORDER, start=1):
        item = by_id[content_id]
        events.append(_event(
            ordinal=ordinal,
            event_kind="FULL_AV_FORMATION",
            content_id=content_id,
            visual_payload_sha256=str(item["visual_payload_sha256"]),
            auditory_payload_sha256=str(item["auditory_payload_sha256"]),
            mask_digest=None,
        ))

    cue_bindings = []
    ordinal = len(events) + 1
    for content_id in HOLDOUT_CONTENT_ORDER:
        visual_cue = _masked_visual_bytes(visual_payloads[content_id])
        visual_event = _event(
            ordinal=ordinal,
            event_kind="VISUAL_PARTIAL_CUE",
            content_id=content_id,
            visual_payload_sha256=_bytes_digest(visual_cue),
            auditory_payload_sha256=None,
            mask_digest=visual_mask_digest,
        )
        events.append(visual_event)
        cue_bindings.append({
            "event_id": visual_event["event_id"],
            "content_id": content_id,
            "modality": "VISUAL",
            "full_target_payload_sha256": by_id[content_id]["visual_payload_sha256"],
            "cue_payload_sha256": visual_event["visual_payload_sha256"],
        })
        ordinal += 1
        auditory_event = _event(
            ordinal=ordinal,
            event_kind="AUDITORY_PARTIAL_CUE",
            content_id=content_id,
            visual_payload_sha256=None,
            auditory_payload_sha256=_bytes_digest(audio_payloads[content_id]),
            mask_digest=auditory_mask_digest,
        )
        events.append(auditory_event)
        cue_bindings.append({
            "event_id": auditory_event["event_id"],
            "content_id": content_id,
            "modality": "AUDITORY",
            "full_target_payload_sha256": by_id[content_id]["auditory_payload_sha256"],
            "cue_payload_sha256": auditory_event["auditory_payload_sha256"],
        })
        ordinal += 1

    generation_root = {
        "schema": "s2ls.generator-root.v1",
        "generator_id": "s2ls-independent-fixed-generator-v1",
        "generator_has_receptor_inputs": False,
        "generator_has_memory_inputs": False,
        "generator_has_threshold_inputs": False,
        "content_recipes": [
            {"content_id": content_id, "recipe": recipe, "recipe_digest": _digest(recipe)}
            for content_id, recipe in CONTENT_RECIPES
        ],
        "content_inventory": list(inventory),
        "raw_payload_retained": False,
    }
    execution_root = {
        "schema": "s2ls.execution-root.v1",
        "event_count": len(events),
        "formation_event_count": len(FORMATION_CONTENT_ORDER),
        "partial_cue_event_count": len(cue_bindings),
        "events": events,
        "visual_mask": visual_mask,
        "visual_mask_digest": visual_mask_digest,
        "auditory_mask": auditory_mask,
        "auditory_mask_digest": auditory_mask_digest,
        "contains_family_roles": False,
        "contains_split_roles": False,
        "contains_expected_results": False,
    }
    evaluation_root = {
        "schema": "s2ls.evaluation-root.v1",
        "families": [
            {
                "family_id": "family-01",
                "training_content_ids": ["content-001", "content-002", "content-003", "content-004"],
                "holdout_content_ids": ["content-005", "content-006"],
            },
            {
                "family_id": "family-02",
                "training_content_ids": ["content-007", "content-008", "content-009", "content-010"],
                "holdout_content_ids": ["content-011", "content-012"],
            },
        ],
        "pressure_content_ids": [f"content-{index:03d}" for index in range(13, 22)],
        "cue_bindings": cue_bindings,
        "comparison_arms": [
            "ADAPTIVE_BANK",
            "FROZEN_FIRST_PROTOTYPE",
            "REPLAY_NEAREST_EXEMPLAR",
        ],
        "modalities_reported_separately": ["AUDITORY", "VISUAL"],
        "adaptive_win_required": False,
        "negative_results_are_evaluable": True,
    }
    roots = {
        "generation_root_digest": _digest(generation_root),
        "execution_root_digest": _digest(execution_root),
        "evaluation_root_digest": _digest(evaluation_root),
    }
    plan_payload = {
        "schema": SCHEMA,
        "plan_id": PLAN_ID,
        "status": "S2LS_PRESEALED_AV_CORPUS_PLAN_MATERIALIZED",
        "counts": {
            "families": 2,
            "training_variants_per_family": 4,
            "holdouts_per_family": 2,
            "pressure_events": 9,
            "formation_events": 17,
            "partial_cue_events": 8,
            "total_events": 25,
        },
        "roots": roots,
        "generation_root": generation_root,
        "execution_root": execution_root,
        "evaluation_root": evaluation_root,
        "receptor_calls": 0,
        "memory_calls": 0,
        "field_calls": 0,
        "context_calls": 0,
    }
    return {**plan_payload, "plan_digest": _digest(plan_payload)}


def materialize_plan_once(*, output_root: Path, plan_id: str) -> Path:
    global MATERIALIZATION_ENABLED, _USED
    if MATERIALIZATION_ENABLED is not True or plan_id != PLAN_ID:
        raise S2LSPlanError("plan materialization is not authorized")
    if _USED or not _LOCK.acquire(blocking=False):
        raise S2LSPlanError("plan materialization is consumed")
    _USED = True
    try:
        plan = _build_plan()
        target_dir = output_root / plan_id
        target_dir.mkdir(parents=True, exist_ok=False)
        target = target_dir / "presealed-corpus-plan.json"
        temporary = target_dir / ".presealed-corpus-plan.json.tmp"
        temporary.write_bytes(_canonical_bytes(plan, newline=True))
        temporary.replace(target)
        return target
    finally:
        MATERIALIZATION_ENABLED = False
        _LOCK.release()


assert len(CONTENT_RECIPES) == 21
assert len(FORMATION_CONTENT_ORDER) == 17
assert len(HOLDOUT_CONTENT_ORDER) == 4
assert set(FORMATION_CONTENT_ORDER).isdisjoint(HOLDOUT_CONTENT_ORDER)

__all__: tuple[str, ...] = ()
