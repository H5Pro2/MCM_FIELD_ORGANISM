"""Presealed prospective visual open-set corpus for S2-LZ."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from threading import Lock

import numpy as np


SCHEMA = "s2lz.presealed-open-set-corpus.v1"
PLAN_ID = "s2lz-open-set-corpus-20260905-01"
PLAN_ENABLED = False
WIDTH = 1920
HEIGHT = 1080
CHANNELS = 3
GRID_ROWS = 8
GRID_COLUMNS = 12
MASK_A_SEED = "s2lz-open-set-mask-a-20260905-v1"
MASK_B_SEED = "s2lz-open-set-mask-b-20260905-v1"
MAX_PAIR_GAP_TICKS = 1
MAX_PLAN_BYTES = 262_144

_LOCK = Lock()
_USED = False

_FAMILIES = (
    ("known-family-01", ((-180, -180), (180, -180), (-180, 180), (180, 180))),
    ("known-family-02", ((0, -240), (0, 240), (-240, 0), (240, 0))),
    ("known-family-03", ((-300, 0), (-100, 0), (100, 0), (300, 0))),
    ("known-family-04", ((0, -300), (0, -100), (0, 100), (0, 300))),
)

_KNOWN_VARIANTS = (
    ("reference-01", 0, 0, 120, 224),
    ("reference-02", -180, 0, 120, 224),
    ("reference-03", 180, 0, 120, 224),
    ("reference-04", 0, 0, 140, 224),
    ("holdout-01", 0, -140, 120, 224),
    ("holdout-02", 0, 140, 120, 176),
)


def _shape_recipe(
    source_id: str,
    generator_kind: str,
    offsets: tuple[tuple[int, int], ...] = (),
    *,
    translation_x: int = 0,
    translation_y: int = 0,
    size: int = 120,
    foreground: int = 224,
    secondary_size: int = 0,
) -> dict[str, object]:
    return {
        "source_id": source_id,
        "generator_kind": generator_kind,
        "offsets": offsets,
        "translation_x": translation_x,
        "translation_y": translation_y,
        "size": size,
        "foreground": foreground,
        "secondary_size": secondary_size,
    }


_KNOWN_RECIPES = tuple(
    _shape_recipe(
        f"source-{family_index * 6 + variant_index + 1:03d}",
        "FOUR_SQUARES",
        offsets,
        translation_x=dx,
        translation_y=dy,
        size=size,
        foreground=foreground,
    )
    for family_index, (_, offsets) in enumerate(_FAMILIES)
    for variant_index, (_, dx, dy, size, foreground) in enumerate(_KNOWN_VARIANTS)
)

_UNKNOWN_RECIPES = (
    _shape_recipe("source-025", "FILLED_DIAMOND", size=330, foreground=224),
    _shape_recipe("source-026", "SQUARE_RING", size=430, foreground=224, secondary_size=250),
    _shape_recipe("source-027", "DIAGONAL_BAND", size=86, foreground=224),
    _shape_recipe("source-028", "OFFSET_BARS", size=110, foreground=224),
)

_INTERMEDIATE_RECIPES = (
    _shape_recipe("source-029", "FOUR_SQUARES", ((-180, -180), (180, 180), (0, -240), (0, 240))),
    _shape_recipe("source-030", "FOUR_SQUARES", ((-180, 180), (180, -180), (-240, 0), (240, 0))),
    _shape_recipe("source-031", "FOUR_SQUARES", ((-300, 0), (300, 0), (0, -300), (0, 300))),
    _shape_recipe("source-032", "FOUR_SQUARES", ((-180, -180), (-180, 180), (0, -240), (0, 240))),
)

CONTENT_RECIPES = _KNOWN_RECIPES + _UNKNOWN_RECIPES + _INTERMEDIATE_RECIPES


class S2LZCorpusError(RuntimeError):
    """The prospective open-set corpus cannot be materialized exactly."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LZCorpusError(message)


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    data = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return data + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _coordinate(position: int) -> tuple[int, int, int]:
    return position // (GRID_COLUMNS * CHANNELS), (position % (GRID_COLUMNS * CHANNELS)) // CHANNELS, position % CHANNELS


def _distance_squared(left: int, right: int) -> int:
    lr, lc, lh = _coordinate(left)
    rr, rc, rh = _coordinate(right)
    return ((lr - rr) * 22) ** 2 + ((lc - rc) * 14) ** 2 + ((lh - rh) * 77) ** 2


def _farthest_order(candidates: tuple[int, ...], seed: str) -> tuple[int, ...]:
    ranks = {position: hashlib.sha256(f"{seed}|{position}".encode("ascii")).hexdigest() for position in candidates}
    remaining = set(candidates)
    first = min(remaining, key=lambda position: (ranks[position], position))
    selected = [first]
    remaining.remove(first)
    while remaining:
        chosen = min(
            remaining,
            key=lambda position: (-min(_distance_squared(position, prior) for prior in selected), ranks[position], position),
        )
        selected.append(chosen)
        remaining.remove(chosen)
    return tuple(selected)


def coordinate_only_masks() -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    all_positions = tuple(range(GRID_ROWS * GRID_COLUMNS * CHANNELS))
    first = _farthest_order(all_positions, MASK_A_SEED)[:96]
    first_set = set(first)
    second = _farthest_order(tuple(position for position in all_positions if position not in first_set), MASK_B_SEED)[:96]
    union = first + second
    _require(len(set(first)) == len(set(second)) == 96 and set(first).isdisjoint(second), "two-view masks overlap")
    _require(len(set(union)) == 192, "union mask differs")
    return first, second, union


def _mask_binding(mask_id: str, positions: tuple[int, ...], seed: str) -> dict[str, object]:
    coordinates = tuple(_coordinate(position) for position in positions)
    payload = {
        "mask_id": mask_id,
        "seed": seed,
        "positions": list(positions),
        "value_count": len(positions),
        "rows_represented": sorted({item[0] for item in coordinates}),
        "columns_represented": sorted({item[1] for item in coordinates}),
        "channel_counts": {str(channel): sum(item[2] == channel for item in coordinates) for channel in range(CHANNELS)},
        "unique_cell_count": len({(item[0], item[1]) for item in coordinates}),
    }
    return {**payload, "mask_digest": _digest(payload)}


def render_frame(recipe: dict[str, object]) -> np.ndarray:
    required = {"source_id", "generator_kind", "offsets", "translation_x", "translation_y", "size", "foreground", "secondary_size"}
    _require(type(recipe) is dict and set(recipe) == required, "source recipe differs")
    kind = recipe["generator_kind"]
    offsets = tuple(tuple(item) for item in recipe["offsets"])
    dx, dy, size = int(recipe["translation_x"]), int(recipe["translation_y"]), int(recipe["size"])
    foreground, secondary = int(recipe["foreground"]), int(recipe["secondary_size"])
    _require(kind in {"FOUR_SQUARES", "FILLED_DIAMOND", "SQUARE_RING", "DIAGONAL_BAND", "OFFSET_BARS"}, "generator kind differs")
    _require(size > 0 and 32 < foreground <= 255, "source shape differs")
    frame = np.full((HEIGHT, WIDTH, CHANNELS), 32, dtype=np.uint8)
    centre_x, centre_y = WIDTH // 2 + dx, HEIGHT // 2 + dy
    if kind == "FOUR_SQUARES":
        _require(len(offsets) == 4 and all(len(item) == 2 for item in offsets), "square offsets differ")
        half = size // 2
        rectangles = tuple((centre_x + int(x) - half, centre_y + int(y) - half, centre_x + int(x) + half, centre_y + int(y) + half) for x, y in offsets)
        _require(all(0 <= left < right <= WIDTH and 0 <= top < bottom <= HEIGHT for left, top, right, bottom in rectangles), "square leaves frame")
        for left, top, right, bottom in rectangles:
            frame[top:bottom, left:right, :] = foreground
    elif kind == "FILLED_DIAMOND":
        rows, columns = np.ogrid[:HEIGHT, :WIDTH]
        mask = np.abs(columns - centre_x) + np.abs(rows - centre_y) <= size
        frame[mask, :] = foreground
    elif kind == "SQUARE_RING":
        _require(0 < secondary < size, "ring dimensions differ")
        outer, inner = size // 2, secondary // 2
        frame[centre_y - outer:centre_y + outer, centre_x - outer:centre_x + outer, :] = foreground
        frame[centre_y - inner:centre_y + inner, centre_x - inner:centre_x + inner, :] = 32
    elif kind == "DIAGONAL_BAND":
        rows, columns = np.ogrid[:HEIGHT, :WIDTH]
        mask = (np.abs((columns - centre_x) - (rows - centre_y)) <= size // 2) & (np.abs(columns - centre_x) <= 330) & (np.abs(rows - centre_y) <= 330)
        frame[mask, :] = foreground
    else:
        half = size // 2
        frame[centre_y - 260:centre_y + 260, centre_x - 250 - half:centre_x - 250 + half, :] = foreground
        frame[centre_y - half:centre_y + half, centre_x + 40:centre_x + 430, :] = foreground
    frame.setflags(write=False)
    return frame


def _source_binding(recipe: dict[str, object]) -> dict[str, object]:
    frame = render_frame(recipe)
    raw = frame.tobytes(order="C")
    payload = {
        "source_id": recipe["source_id"],
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "payload_bytes": len(raw),
        "rgb_value_sum": int(frame.sum(dtype=np.uint64)),
    }
    return {**payload, "source_binding_digest": _digest(payload)}


def _case_specs() -> tuple[dict[str, object], ...]:
    compatible_sources = tuple(f"source-{index:03d}" for index in (5, 6, 11, 12, 17, 18, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32))
    cases = [
        {"case_id": f"case-{index + 1:03d}", "view_a_source_id": source_id, "view_b_source_id": source_id}
        for index, source_id in enumerate(compatible_sources)
    ]
    incompatible_pairs = (("source-005", "source-011"), ("source-011", "source-017"), ("source-017", "source-023"), ("source-023", "source-005"))
    cases.extend(
        {"case_id": f"case-{index + 17:03d}", "view_a_source_id": left, "view_b_source_id": right}
        for index, (left, right) in enumerate(incompatible_pairs)
    )
    return tuple(cases)


def build_presealed_plan() -> dict[str, object]:
    mask_a, mask_b, union = coordinate_only_masks()
    masks = (
        _mask_binding("VIEW_A_96", mask_a, MASK_A_SEED),
        _mask_binding("VIEW_B_96", mask_b, MASK_B_SEED),
        _mask_binding("UNION_192", union, f"{MASK_A_SEED}+{MASK_B_SEED}"),
    )
    _require(all(mask["rows_represented"] == list(range(8)) and mask["columns_represented"] == list(range(12)) for mask in masks), "mask coverage differs")
    bindings = tuple(_source_binding(recipe) for recipe in CONTENT_RECIPES)
    _require(len(bindings) == 32 and len({item["payload_sha256"] for item in bindings}) == 32, "source inventory differs")
    binding_by_source = {str(item["source_id"]): item for item in bindings}
    reference_groups = tuple(
        {"model_id": f"model-{family_index + 1:02d}", "reference_source_ids": [f"source-{family_index * 6 + offset:03d}" for offset in range(1, 5)]}
        for family_index in range(4)
    )
    cases = _case_specs()
    observations = []
    for index, case in enumerate(cases):
        for ordinal, (mask_id, source_key) in enumerate((("VIEW_A_96", "view_a_source_id"), ("VIEW_B_96", "view_b_source_id"))):
            source_id = str(case[source_key])
            item = {
                "observation_id": f"observation-{index * 2 + ordinal + 1:03d}",
                "case_id": case["case_id"],
                "source_id": source_id,
                "mask_id": mask_id,
                "tick": index * 2 + ordinal + 1,
                "payload_sha256": binding_by_source[source_id]["payload_sha256"],
            }
            observations.append({**item, "observation_digest": _digest(item)})
    execution_cases = []
    for case in cases:
        payload = {
            **case,
            "maximum_tick_gap": MAX_PAIR_GAP_TICKS,
            "compatibility_rule": "SAME_SOURCE_ID_AND_PAYLOAD_DIGEST_WITHIN_TICK_GAP",
        }
        execution_cases.append({**payload, "case_plan_digest": _digest(payload)})
    evaluation_cases = []
    for case_index, case in enumerate(cases):
        if case_index < 8:
            expected_kind = "KNOWN_HOLDOUT"
            expected_model_id = f"model-{case_index // 2 + 1:02d}"
        elif case_index < 12:
            expected_kind = "UNKNOWN_FORM"
            expected_model_id = None
        elif case_index < 16:
            expected_kind = "AMBIGUOUS_INTERMEDIATE"
            expected_model_id = None
        else:
            expected_kind = "INCOMPATIBLE_PAIR"
            expected_model_id = None
        evaluation_cases.append({"case_id": case["case_id"], "expected_kind": expected_kind, "expected_model_id": expected_model_id})
    payload = {
        "schema": SCHEMA,
        "plan_id": PLAN_ID,
        "source_contract": {"format": "RGB8", "width": WIDTH, "height": HEIGHT, "channels": CHANNELS, "raw_payload_retained": False},
        "generation_root": {
            "generator": "PRESEALED_GEOMETRIC_OPEN_SET_V1",
            "recipes": [{**recipe, "offsets": [list(item) for item in recipe["offsets"]]} for recipe in CONTENT_RECIPES],
            "source_bindings": list(bindings),
            "receptor_or_distance_available": False,
        },
        "mask_root": {
            "algorithm": "DISJOINT_INTEGER_FARTHEST_POINT_WITH_SHA256_SEED_TIES_V1",
            "masks": list(masks),
            "image_values_or_evaluation_roles_available": False,
        },
        "execution_root": {
            "reference_groups": list(reference_groups),
            "calibration_rule": "PER_MODEL_MAX_REFERENCE_TO_REFERENCE_CENTROID_MEAN_L1",
            "admission_rule": "EXACTLY_ONE_MODEL_WITH_DISTANCE_NOT_GREATER_THAN_ITS_PRETEST_CALIBRATION_RADIUS",
            "cases": execution_cases,
            "observations": observations,
            "evaluation_roles_available": False,
        },
        "evaluation_root": {"cases": evaluation_cases, "controls_source_mask_or_calibration": False},
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
