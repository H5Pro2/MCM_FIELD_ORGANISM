"""Presealed shape corpus for a private pose/form comparison."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from threading import Lock

import numpy as np


SCHEMA = "s2lv.presealed-pose-form-corpus.v1"
PLAN_ID = "s2lv-pose-form-corpus-20260905-01"
PLAN_ENABLED = False
WIDTH = 1920
HEIGHT = 1080
CHANNELS = 3
BACKGROUND = 32
MAX_PLAN_BYTES = 131_072
VISIBLE_POSITIONS = tuple(range(32))
MASKED_POSITIONS = tuple(range(32, 288))
S2KQ_SCHEMA = "s2kq.private.partial-cue-retrieval-336.v1"

_LOCK = Lock()
_USED = False

_ARRANGEMENTS = (
    {"family_id": "family-01", "arrangement": "HORIZONTAL", "offsets": ((-220, 0), (220, 0))},
    {"family_id": "family-02", "arrangement": "VERTICAL", "offsets": ((0, -220), (0, 220))},
    {"family_id": "family-03", "arrangement": "DIAGONAL_DOWN", "offsets": ((-156, -156), (156, 156))},
    {"family_id": "family-04", "arrangement": "DIAGONAL_UP", "offsets": ((-156, 156), (156, -156))},
)

_VARIANTS = (
    {"variant_id": "v01", "variation": "BASE", "translation_x": 0, "translation_y": 0, "square_size": 140, "foreground": 224},
    {"variant_id": "v02", "variation": "POSITION_LEFT", "translation_x": -300, "translation_y": 0, "square_size": 140, "foreground": 224},
    {"variant_id": "v03", "variation": "POSITION_RIGHT", "translation_x": 300, "translation_y": 0, "square_size": 140, "foreground": 224},
    {"variant_id": "v04", "variation": "EDGE_UPPER", "translation_x": 0, "translation_y": -210, "square_size": 140, "foreground": 224},
    {"variant_id": "v05", "variation": "EDGE_LOWER", "translation_x": 0, "translation_y": 210, "square_size": 140, "foreground": 224},
    {"variant_id": "v06", "variation": "SIZE_SMALL", "translation_x": 0, "translation_y": 0, "square_size": 100, "foreground": 224},
    {"variant_id": "v07", "variation": "SIZE_LARGE", "translation_x": 0, "translation_y": 0, "square_size": 180, "foreground": 224},
    {"variant_id": "v08", "variation": "CONTRAST_LOW", "translation_x": 0, "translation_y": 0, "square_size": 140, "foreground": 160},
)

CONTENT_RECIPES = tuple(
    {
        "content_id": f"frame-{family_index * len(_VARIANTS) + variant_index + 1:03d}",
        "family_id": family["family_id"],
        "arrangement": family["arrangement"],
        "offsets": family["offsets"],
        **variant,
    }
    for family_index, family in enumerate(_ARRANGEMENTS)
    for variant_index, variant in enumerate(_VARIANTS)
)


class S2LVCorpusError(RuntimeError):
    """The private pose/form corpus cannot be materialized exactly."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LVCorpusError(message)


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    data = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return data + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def render_frame(recipe: dict[str, object]) -> np.ndarray:
    required = {
        "content_id", "family_id", "arrangement", "offsets", "variant_id", "variation",
        "translation_x", "translation_y", "square_size", "foreground",
    }
    _require(type(recipe) is dict and set(recipe) == required, "recipe differs")
    offsets = tuple(tuple(item) for item in recipe["offsets"])
    _require(len(offsets) == 2 and all(len(item) == 2 for item in offsets), "arrangement offsets differ")
    dx, dy = recipe["translation_x"], recipe["translation_y"]
    size, foreground = recipe["square_size"], recipe["foreground"]
    _require(all(type(item) is int for item in (dx, dy, size, foreground)), "numeric recipe differs")
    _require(size > 0 and size % 2 == 0 and BACKGROUND < foreground <= 255, "shape recipe differs")
    frame = np.full((HEIGHT, WIDTH, CHANNELS), BACKGROUND, dtype=np.uint8)
    half = size // 2
    for offset_x, offset_y in offsets:
        _require(type(offset_x) is int and type(offset_y) is int, "offset type differs")
        centre_x = WIDTH // 2 + dx + offset_x
        centre_y = HEIGHT // 2 + dy + offset_y
        left, right = centre_x - half, centre_x + half
        top, bottom = centre_y - half, centre_y + half
        _require(0 <= left < right <= WIDTH and 0 <= top < bottom <= HEIGHT, "shape leaves frame")
        frame[top:bottom, left:right, :] = foreground
    frame.setflags(write=False)
    return frame


def _source_binding(recipe: dict[str, object]) -> dict[str, object]:
    frame = render_frame(recipe)
    raw = frame.tobytes(order="C")
    unique, counts = np.unique(frame, return_counts=True)
    histogram = {str(int(value)): int(count) for value, count in zip(unique, counts, strict=True)}
    return {
        "content_id": recipe["content_id"],
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "payload_bytes": len(raw),
        "rgb_value_sum": int(frame.sum(dtype=np.uint64)),
        "histogram": histogram,
        "histogram_digest": _digest(histogram),
    }


def build_presealed_plan() -> dict[str, object]:
    bindings = tuple(_source_binding(recipe) for recipe in CONTENT_RECIPES)
    _require(len(bindings) == 32 and len({item["payload_sha256"] for item in bindings}) == 32, "source inventory differs")
    by_content = {item["content_id"]: item for item in bindings}
    paired_variants = []
    for variant_index, variant in enumerate(_VARIANTS):
        ids = tuple(f"frame-{family_index * len(_VARIANTS) + variant_index + 1:03d}" for family_index in range(4))
        variant_bindings = tuple(by_content[content_id] for content_id in ids)
        _require(len({item["histogram_digest"] for item in variant_bindings}) == 1, "paired brightness histogram differs")
        _require(len({item["rgb_value_sum"] for item in variant_bindings}) == 1, "paired brightness sum differs")
        paired_variants.append({"variant_id": variant["variant_id"], "content_ids": list(ids)})
    mask_payload = {
        "schema": S2KQ_SCHEMA,
        "visible_positions": list(VISIBLE_POSITIONS),
        "masked_positions": list(MASKED_POSITIONS),
    }
    payload = {
        "schema": SCHEMA,
        "plan_id": PLAN_ID,
        "source_contract": {
            "format": "RGB8",
            "width": WIDTH,
            "height": HEIGHT,
            "channels": CHANNELS,
            "raw_payload_retained": False,
        },
        "generation_root": {
            "generator": "TWO_SQUARES_FOUR_ARRANGEMENTS_V1",
            "background": BACKGROUND,
            "recipes": [
                {**recipe, "offsets": [list(item) for item in recipe["offsets"]]}
                for recipe in CONTENT_RECIPES
            ],
            "source_bindings": list(bindings),
        },
        "evaluation_root": {
            "families": [
                {
                    "family_id": family["family_id"],
                    "content_ids": [f"frame-{family_index * len(_VARIANTS) + variant_index + 1:03d}" for variant_index in range(8)],
                }
                for family_index, family in enumerate(_ARRANGEMENTS)
            ],
            "paired_variants": paired_variants,
            "representations": [
                {"representation_id": "BLOCK_MEAN_12X8_RGB", "dimension": 288, "role": "UNCHANGED_BASELINE"},
                {"representation_id": "POSE_V1", "role": "CURRENT_SPATIAL_STATE"},
                {"representation_id": "FORM_DESCRIPTOR_12X12_V1", "dimension": 144, "role": "READ_ONLY_CANDIDATE"},
                {"representation_id": "LOCAL_GRADIENT_12X8_RGB_XY", "dimension": 576, "role": "DIAGNOSTIC_ONLY"},
            ],
            "projection_contract": {
                "input": "BLOCK_MEAN_12X8_RGB",
                "background": "CHANNELWISE_BORDER_MEDIAN",
                "activation": "MEAN_ABSOLUTE_CHANNEL_DEVIATION",
                "support": "STRICTLY_POSITIVE_ACTIVATION",
                "pose": "MASS_CENTROID_BBOX_AND_WEIGHTED_RMS",
                "form_translation": "ACTIVE_BBOX_CENTER_TO_CANONICAL_CENTER",
                "form_scale": "ISOTROPIC_MAX_ACTIVE_BBOX_SPAN",
                "form_projection": "BILINEAR_SPLAT_12X12",
                "form_normalization": "UNIT_TOTAL_MASS",
                "labels_available_to_projection": False,
                "thresholds_used_by_projection": False,
            },
            "fixed_visual_mask": {
                "visible_positions": list(VISIBLE_POSITIONS),
                "masked_positions": list(MASKED_POSITIONS),
                "mask_plan_digest": _digest(mask_payload),
            },
            "diagnostic_thresholds": {"visual_slow": 0.01, "fast": 0.2},
            "result_controls_source_inclusion": False,
        },
        "forbidden_calls": {"memory": 0, "context": 0, "field": 0},
    }
    return {**payload, "plan_digest": _digest(payload)}


def materialize_plan_once(output_root: Path, *, plan_id: str) -> Path:
    global PLAN_ENABLED, _USED
    _require(PLAN_ENABLED is True and plan_id == PLAN_ID, "plan materialization is not authorized")
    _require(not _USED and _LOCK.acquire(blocking=False), "plan materialization is already consumed")
    _USED = True
    try:
        record = build_presealed_plan()
        run_dir = output_root / plan_id
        run_dir.mkdir(parents=True, exist_ok=False)
        target = run_dir / "presealed-plan.json"
        temporary = run_dir / ".presealed-plan.json.tmp"
        data = _canonical_bytes(record, newline=True)
        _require(len(data) <= MAX_PLAN_BYTES, "plan exceeds bounded envelope")
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
        PLAN_ENABLED = False
        _LOCK.release()


__all__: tuple[str, ...] = ()
