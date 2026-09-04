"""Presealed visual shape corpus without receptor or project-function imports."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from threading import Lock

import numpy as np


SCHEMA = "s2lt.presealed-visual-structure-corpus.v1"
PLAN_ID = "s2lt-visual-structure-corpus-20260904-01"
PLAN_ENABLED = False
WIDTH = 1920
HEIGHT = 1080
CHANNELS = 3
BACKGROUND = 32
FOREGROUND = 224
SQUARE_SIZE = 140
CENTRE_OFFSET = 220
MAX_PLAN_BYTES = 65_536

_LOCK = Lock()
_USED = False

_VARIANTS = (
    (-36, -24),
    (-12, 18),
    (12, -18),
    (36, 24),
    (-28, 30),
    (28, -30),
)

CONTENT_RECIPES = tuple(
    {
        "content_id": f"frame-{index + 1:03d}",
        "arrangement": arrangement,
        "translation_x": translation[0],
        "translation_y": translation[1],
    }
    for index, (arrangement, translation) in enumerate(
        tuple(("HORIZONTAL", item) for item in _VARIANTS)
        + tuple(("VERTICAL", item) for item in _VARIANTS)
    )
)


class S2LTCorpusError(RuntimeError):
    """The private visual corpus cannot be materialized exactly."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LTCorpusError(message)


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    data = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return data + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def render_frame(recipe: dict[str, object]) -> np.ndarray:
    _require(type(recipe) is dict and set(recipe) == {"content_id", "arrangement", "translation_x", "translation_y"}, "recipe differs")
    arrangement = recipe["arrangement"]
    _require(arrangement in {"HORIZONTAL", "VERTICAL"}, "arrangement differs")
    dx = recipe["translation_x"]
    dy = recipe["translation_y"]
    _require(type(dx) is int and type(dy) is int, "translation differs")
    centre_x = WIDTH // 2 + dx
    centre_y = HEIGHT // 2 + dy
    if arrangement == "HORIZONTAL":
        centres = ((centre_x - CENTRE_OFFSET, centre_y), (centre_x + CENTRE_OFFSET, centre_y))
    else:
        centres = ((centre_x, centre_y - CENTRE_OFFSET), (centre_x, centre_y + CENTRE_OFFSET))
    frame = np.full((HEIGHT, WIDTH, CHANNELS), BACKGROUND, dtype=np.uint8)
    half = SQUARE_SIZE // 2
    for x, y in centres:
        left, right = x - half, x + half
        top, bottom = y - half, y + half
        _require(0 <= left < right <= WIDTH and 0 <= top < bottom <= HEIGHT, "shape leaves frame")
        frame[top:bottom, left:right, :] = FOREGROUND
    frame.setflags(write=False)
    return frame


def _source_binding(recipe: dict[str, object]) -> dict[str, object]:
    frame = render_frame(recipe)
    raw = frame.tobytes(order="C")
    foreground_values = int(np.count_nonzero(frame == FOREGROUND))
    background_values = int(np.count_nonzero(frame == BACKGROUND))
    _require(foreground_values == 2 * SQUARE_SIZE * SQUARE_SIZE * CHANNELS, "foreground count differs")
    _require(foreground_values + background_values == WIDTH * HEIGHT * CHANNELS, "histogram count differs")
    histogram = {str(BACKGROUND): background_values, str(FOREGROUND): foreground_values}
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
    _require(len({item["payload_sha256"] for item in bindings}) == len(bindings) == 12, "source digests are not unique")
    _require(len({item["histogram_digest"] for item in bindings}) == 1, "brightness histograms differ")
    _require(len({item["rgb_value_sum"] for item in bindings}) == 1, "brightness sums differ")
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
            "generator": "TWO_EQUAL_SQUARES_ARRANGEMENT_V1",
            "background": BACKGROUND,
            "foreground": FOREGROUND,
            "square_size": SQUARE_SIZE,
            "centre_offset": CENTRE_OFFSET,
            "recipes": list(CONTENT_RECIPES),
            "source_bindings": list(bindings),
        },
        "evaluation_root": {
            "families": [
                {
                    "family_id": "family-01",
                    "training_content_ids": [f"frame-{index:03d}" for index in range(1, 5)],
                    "holdout_content_ids": ["frame-005", "frame-006"],
                },
                {
                    "family_id": "family-02",
                    "training_content_ids": [f"frame-{index:03d}" for index in range(7, 11)],
                    "holdout_content_ids": ["frame-011", "frame-012"],
                },
            ],
            "representations": [
                {"representation_id": "BLOCK_MEAN_12X8_RGB", "dimension": 288, "role": "CURRENT_BASELINE"},
                {"representation_id": "SUBBLOCK_MEAN_24X24_RGB", "dimension": 1728, "role": "PRIVATE_COMPARATOR"},
                {"representation_id": "LOCAL_GRADIENT_12X8_RGB_XY", "dimension": 576, "role": "PRIVATE_COMPARATOR"},
            ],
            "metrics": [
                "NORMALIZED_MEAN_L1",
                "MIN_CROSS_MINUS_MAX_WITHIN_MARGIN",
                "NEAREST_TRAINING_CENTROID_HOLDOUT_CLASSIFICATION",
            ],
            "acceptance_rule": {
                "all_holdouts_nearest_own_centroid": True,
                "minimum_cross_training_distance_exceeds_maximum_within_training_distance": True,
                "result_controls_source_inclusion": False,
            },
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
