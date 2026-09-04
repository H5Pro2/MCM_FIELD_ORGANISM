"""Presealed form corpus and coordinate-only visual masks for S2-LW."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from threading import Lock

import numpy as np


SCHEMA = "s2lw.presealed-spatial-mask-corpus.v1"
PLAN_ID = "s2lw-spatial-mask-corpus-20260905-01"
PLAN_ENABLED = False
WIDTH = 1920
HEIGHT = 1080
CHANNELS = 3
GRID_ROWS = 8
GRID_COLUMNS = 12
MASK_SEED = "s2lw-coordinate-mask-seed-20260905-v1"
MAX_PLAN_BYTES = 131_072

_LOCK = Lock()
_USED = False

_ARRANGEMENTS = (
    {"family_id": "family-01", "arrangement": "TRIANGLE_UP", "offsets": ((-180, 140), (180, 140), (0, -180))},
    {"family_id": "family-02", "arrangement": "TRIANGLE_DOWN", "offsets": ((-180, -140), (180, -140), (0, 180))},
    {"family_id": "family-03", "arrangement": "LINE_HORIZONTAL", "offsets": ((-240, 0), (0, 0), (240, 0))},
    {"family_id": "family-04", "arrangement": "LINE_VERTICAL", "offsets": ((0, -240), (0, 0), (0, 240))},
)

_VARIANTS = (
    {"variant_id": "v01", "variation": "BASE", "translation_x": 0, "translation_y": 0, "square_size": 140, "foreground": 224},
    {"variant_id": "v02", "variation": "POSITION_LEFT", "translation_x": -280, "translation_y": 0, "square_size": 140, "foreground": 224},
    {"variant_id": "v03", "variation": "POSITION_RIGHT", "translation_x": 280, "translation_y": 0, "square_size": 140, "foreground": 224},
    {"variant_id": "v04", "variation": "EDGE_UPPER", "translation_x": 0, "translation_y": -180, "square_size": 140, "foreground": 224},
    {"variant_id": "v05", "variation": "EDGE_LOWER", "translation_x": 0, "translation_y": 180, "square_size": 140, "foreground": 224},
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


class S2LWCorpusError(RuntimeError):
    """The private spatial-mask corpus cannot be materialized exactly."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LWCorpusError(message)


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    data = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return data + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _coordinate(position: int) -> tuple[int, int, int]:
    _require(type(position) is int and 0 <= position < GRID_ROWS * GRID_COLUMNS * CHANNELS, "mask position differs")
    return position // (GRID_COLUMNS * CHANNELS), (position % (GRID_COLUMNS * CHANNELS)) // CHANNELS, position % CHANNELS


def _seed_rank(position: int) -> str:
    return hashlib.sha256(f"{MASK_SEED}|{position}".encode("ascii")).hexdigest()


def _coordinate_distance_squared(left: int, right: int) -> int:
    left_row, left_column, left_channel = _coordinate(left)
    right_row, right_column, right_channel = _coordinate(right)
    return (
        ((left_row - right_row) * 22) ** 2
        + ((left_column - right_column) * 14) ** 2
        + ((left_channel - right_channel) * 77) ** 2
    )


def coordinate_only_order() -> tuple[int, ...]:
    remaining = set(range(GRID_ROWS * GRID_COLUMNS * CHANNELS))
    first = min(remaining, key=lambda position: (_seed_rank(position), position))
    selected = [first]
    remaining.remove(first)
    while remaining:
        next_position = min(
            remaining,
            key=lambda position: (
                -min(_coordinate_distance_squared(position, chosen) for chosen in selected),
                _seed_rank(position),
                position,
            ),
        )
        selected.append(next_position)
        remaining.remove(next_position)
    return tuple(selected)


def _mask_binding(mask_id: str, positions: tuple[int, ...], generation: str) -> dict[str, object]:
    _require(len(positions) == len(set(positions)) and all(0 <= item < 288 for item in positions), "mask inventory differs")
    coordinates = tuple(_coordinate(position) for position in positions)
    payload = {
        "mask_id": mask_id,
        "generation": generation,
        "seed": None if generation == "LEGACY_CONTIGUOUS" else MASK_SEED,
        "positions": list(positions),
        "value_count": len(positions),
        "rows_represented": sorted({item[0] for item in coordinates}),
        "columns_represented": sorted({item[1] for item in coordinates}),
        "channel_counts": {str(channel): sum(item[2] == channel for item in coordinates) for channel in range(CHANNELS)},
        "unique_cell_count": len({(item[0], item[1]) for item in coordinates}),
        "row_counts": {str(row): sum(item[0] == row for item in coordinates) for row in range(GRID_ROWS)},
        "column_counts": {str(column): sum(item[1] == column for item in coordinates) for column in range(GRID_COLUMNS)},
    }
    return {**payload, "mask_digest": _digest(payload)}


def render_frame(recipe: dict[str, object]) -> np.ndarray:
    required = {
        "content_id", "family_id", "arrangement", "offsets", "variant_id", "variation",
        "translation_x", "translation_y", "square_size", "foreground",
    }
    _require(type(recipe) is dict and set(recipe) == required, "recipe differs")
    offsets = tuple(tuple(item) for item in recipe["offsets"])
    _require(len(offsets) == 3 and all(len(item) == 2 for item in offsets), "arrangement offsets differ")
    dx, dy = recipe["translation_x"], recipe["translation_y"]
    size, foreground = recipe["square_size"], recipe["foreground"]
    _require(all(type(item) is int for item in (dx, dy, size, foreground)), "numeric recipe differs")
    _require(size > 0 and size % 2 == 0 and 32 < foreground <= 255, "shape recipe differs")
    frame = np.full((HEIGHT, WIDTH, CHANNELS), 32, dtype=np.uint8)
    half = size // 2
    rectangles = []
    for offset_x, offset_y in offsets:
        centre_x = WIDTH // 2 + dx + int(offset_x)
        centre_y = HEIGHT // 2 + dy + int(offset_y)
        rectangle = (centre_x - half, centre_y - half, centre_x + half, centre_y + half)
        _require(0 <= rectangle[0] < rectangle[2] <= WIDTH and 0 <= rectangle[1] < rectangle[3] <= HEIGHT, "shape leaves frame")
        rectangles.append(rectangle)
    for index, left in enumerate(rectangles):
        for right in rectangles[index + 1:]:
            _require(left[2] <= right[0] or right[2] <= left[0] or left[3] <= right[1] or right[3] <= left[1], "shape components overlap")
    for left, top, right, bottom in rectangles:
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
    order = coordinate_only_order()
    _require(len(order) == 288 and len(set(order)) == 288, "coordinate ordering differs")
    masks = (
        _mask_binding("TOP_ROW_32", tuple(range(32)), "LEGACY_CONTIGUOUS"),
        _mask_binding("SPATIAL_SEEDED_32", order[:32], "SEEDED_FARTHEST_POINT_PREFIX"),
        _mask_binding("SPATIAL_SEEDED_96", order[:96], "SEEDED_FARTHEST_POINT_PREFIX"),
    )
    _require(set(masks[1]["positions"]).issubset(masks[2]["positions"]), "distributed masks are not nested")
    bindings = tuple(_source_binding(recipe) for recipe in CONTENT_RECIPES)
    _require(len(bindings) == 32 and len({item["payload_sha256"] for item in bindings}) == 32, "source inventory differs")
    by_content = {item["content_id"]: item for item in bindings}
    paired_variants = []
    for variant_index, variant in enumerate(_VARIANTS):
        ids = tuple(f"frame-{family_index * len(_VARIANTS) + variant_index + 1:03d}" for family_index in range(4))
        selected = tuple(by_content[content_id] for content_id in ids)
        _require(len({item["histogram_digest"] for item in selected}) == 1, "paired brightness histogram differs")
        _require(len({item["rgb_value_sum"] for item in selected}) == 1, "paired brightness sum differs")
        paired_variants.append({"variant_id": variant["variant_id"], "content_ids": list(ids)})
    payload = {
        "schema": SCHEMA,
        "plan_id": PLAN_ID,
        "source_contract": {"format": "RGB8", "width": WIDTH, "height": HEIGHT, "channels": CHANNELS, "raw_payload_retained": False},
        "generation_root": {
            "generator": "THREE_SQUARES_FOUR_ARRANGEMENTS_V1",
            "recipes": [{**recipe, "offsets": [list(item) for item in recipe["offsets"]]} for recipe in CONTENT_RECIPES],
            "source_bindings": list(bindings),
        },
        "mask_root": {
            "coordinate_system": "VISUAL_GRID_8X12_RGB_FLAT_ROW_COLUMN_CHANNEL",
            "ordering_algorithm": "INTEGER_NORMALIZED_FARTHEST_POINT_WITH_SHA256_SEED_TIES_V1",
            "integer_axis_scales": {"row": 22, "column": 14, "channel": 77},
            "seed": MASK_SEED,
            "coordinate_order_digest": _digest(list(order)),
            "masks": list(masks),
            "image_values_available_to_mask_generation": False,
            "evaluation_roles_available_to_mask_generation": False,
        },
        "evaluation_root": {
            "families": [
                {"family_id": family["family_id"], "content_ids": [f"frame-{family_index * 8 + variant_index + 1:03d}" for variant_index in range(8)]}
                for family_index, family in enumerate(_ARRANGEMENTS)
            ],
            "paired_variants": paired_variants,
            "diagnostic_thresholds": {"visual_slow": 0.01, "fast": 0.2},
            "result_controls_source_or_mask_inclusion": False,
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
