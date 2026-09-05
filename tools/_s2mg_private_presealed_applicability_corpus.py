"""One-shot presealed corpus for learned slot applicability evidence."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
from threading import Lock

import numpy as np


SCHEMA = "s2mg.presealed-slot-applicability-corpus.v1"
PLAN_ID = "s2mg-slot-applicability-corpus-20260905-01"
SOURCE_SEED = "s2mg-neutral-source-seed-20260905-v1"
PLAN_ENABLED = False

WIDTH = 1920
HEIGHT = 1080
CHANNELS = 3
GRID_ROWS = 8
GRID_COLUMNS = 12
MASK_A_SEED = "s2lz-open-set-mask-a-20260905-v1"
MASK_B_SEED = "s2lz-open-set-mask-b-20260905-v1"
SOURCE_CLOCK_ID = "s2mg-visual-source-clock"
TICKS_PER_EVENT = 100_000_000
MAX_PAIR_GAP_TICKS = 100_000_000

UINT32_MAX = 4_294_967_295
UINT64_MAX = 18_446_744_073_709_551_615
MAX_IDENTIFIER_BYTES = 96
MAX_FLOAT_TOKEN_BYTES = 32
MAX_PLAN_BYTES = 262_144
MAX_ASSIGNED_ENTRY_BYTES = 8_192
MAX_SLOT_EVIDENCE_BYTES = 40_960
MAX_ENVELOPE_BYTES = 12_288
MAX_FORMATION_RECEIPT_BYTES = 12_288
MAX_ERROR_RECEIPT_BYTES = 4_096
MAX_EXTENDED_MEMORY_STATE_BYTES = 262_144

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{7,95}$")
_LOCK = Lock()
_USED = False


class S2MGCorpusError(RuntimeError):
    """The S2-MG source plan cannot be sealed exactly once."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MGCorpusError(message)


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
    _require(_IDENTIFIER.fullmatch(source_id) is not None, "source id differs")
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


_FAMILY_LAYOUT_POOL = (
    ((-260, -160), (140, -220), (-120, 220), (260, 140)),
    ((-280, -80), (-40, -220), (220, -40), (80, 240)),
    ((-220, -240), (220, -120), (-260, 120), (160, 240)),
    ((-300, -180), (0, -60), (260, -200), (120, 240)),
    ((-240, -200), (240, -200), (-80, 80), (200, 220)),
    ((-300, 80), (-80, -240), (160, -80), (280, 220)),
)

_TRAIN_TRANSFORMS = (
    (0, 0, 120, 224),
    (-180, 0, 120, 224),
    (180, 0, 120, 224),
    (0, 0, 140, 224),
)

_HOLDOUT_TRANSFORMS = (
    (0, -140, 120, 224),
    (0, 140, 120, 176),
)


def _selected_layouts() -> tuple[tuple[tuple[int, int], ...], ...]:
    ranked = sorted(
        enumerate(_FAMILY_LAYOUT_POOL),
        key=lambda item: (
            hashlib.sha256(
                f"{SOURCE_SEED}|family-layout|{item[0]}".encode("ascii")
            ).hexdigest(),
            item[0],
        ),
    )
    return tuple(item[1] for item in ranked[:2])


def _content_recipes() -> tuple[dict[str, object], ...]:
    layouts = _selected_layouts()
    known = []
    for family_index, layout in enumerate(layouts):
        base = family_index * 6
        for offset, (dx, dy, size, foreground) in enumerate(
            _TRAIN_TRANSFORMS + _HOLDOUT_TRANSFORMS,
            start=1,
        ):
            known.append(
                _shape_recipe(
                    f"input-{base + offset:03d}",
                    "FOUR_SQUARES",
                    layout,
                    translation_x=dx,
                    translation_y=dy,
                    size=size,
                    foreground=foreground,
                )
            )

    unknown = (
        _shape_recipe(
            "input-013",
            "FILLED_DIAMOND",
            translation_x=-90,
            translation_y=70,
            size=330,
            foreground=224,
        ),
        _shape_recipe(
            "input-014",
            "SQUARE_RING",
            translation_x=110,
            translation_y=-60,
            size=430,
            foreground=224,
            secondary_size=250,
        ),
        _shape_recipe(
            "input-015",
            "DIAGONAL_BAND",
            translation_x=-70,
            translation_y=-90,
            size=86,
            foreground=224,
        ),
        _shape_recipe(
            "input-016",
            "OFFSET_BARS",
            translation_x=90,
            translation_y=80,
            size=110,
            foreground=224,
        ),
    )
    intermediate = (
        _shape_recipe(
            "input-017",
            "FOUR_SQUARES",
            (layouts[0][0], layouts[0][1], layouts[1][2], layouts[1][3]),
        ),
        _shape_recipe(
            "input-018",
            "FOUR_SQUARES",
            (layouts[1][0], layouts[1][1], layouts[0][2], layouts[0][3]),
        ),
    )
    pressure = (
        _shape_recipe("input-019", "FILLED_DIAMOND", translation_x=-320, translation_y=-120, size=250, foreground=192),
        _shape_recipe("input-020", "FILLED_DIAMOND", translation_x=300, translation_y=100, size=290, foreground=208),
        _shape_recipe("input-021", "SQUARE_RING", translation_x=-280, translation_y=160, size=360, foreground=232, secondary_size=180),
        _shape_recipe("input-022", "SQUARE_RING", translation_x=260, translation_y=-140, size=500, foreground=176, secondary_size=300),
        _shape_recipe("input-023", "DIAGONAL_BAND", translation_x=-220, size=64, foreground=208),
        _shape_recipe("input-024", "DIAGONAL_BAND", translation_x=220, size=120, foreground=240),
        _shape_recipe("input-025", "OFFSET_BARS", translation_x=-180, translation_y=100, size=80, foreground=192),
        _shape_recipe("input-026", "OFFSET_BARS", translation_x=180, translation_y=-100, size=140, foreground=240),
        _shape_recipe(
            "input-027",
            "FOUR_SQUARES",
            ((-340, -260), (340, -260), (-340, 260), (340, 260)),
            size=90,
            foreground=200,
        ),
    )
    recipes = tuple(known) + unknown + intermediate + pressure
    _require(
        len(recipes) == 27
        and len({str(item["source_id"]) for item in recipes}) == 27,
        "source inventory differs",
    )
    return recipes


def _render_frame(recipe: dict[str, object]) -> np.ndarray:
    required = {
        "source_id",
        "generator_kind",
        "offsets",
        "translation_x",
        "translation_y",
        "size",
        "foreground",
        "secondary_size",
    }
    _require(type(recipe) is dict and set(recipe) == required, "source recipe differs")
    kind = recipe["generator_kind"]
    offsets = tuple(tuple(int(value) for value in item) for item in recipe["offsets"])
    dx = int(recipe["translation_x"])
    dy = int(recipe["translation_y"])
    size = int(recipe["size"])
    foreground = int(recipe["foreground"])
    secondary = int(recipe["secondary_size"])
    _require(
        kind
        in {
            "FOUR_SQUARES",
            "FILLED_DIAMOND",
            "SQUARE_RING",
            "DIAGONAL_BAND",
            "OFFSET_BARS",
        },
        "generator kind differs",
    )
    _require(size > 0 and 32 < foreground <= 255, "source shape differs")
    frame = np.full((HEIGHT, WIDTH, CHANNELS), 32, dtype=np.uint8)
    centre_x = WIDTH // 2 + dx
    centre_y = HEIGHT // 2 + dy
    if kind == "FOUR_SQUARES":
        _require(
            len(offsets) == 4 and all(len(item) == 2 for item in offsets),
            "square offsets differ",
        )
        half = size // 2
        rectangles = tuple(
            (
                centre_x + x - half,
                centre_y + y - half,
                centre_x + x + half,
                centre_y + y + half,
            )
            for x, y in offsets
        )
        _require(
            all(
                0 <= left < right <= WIDTH and 0 <= top < bottom <= HEIGHT
                for left, top, right, bottom in rectangles
            ),
            "square leaves frame",
        )
        for left, top, right, bottom in rectangles:
            frame[top:bottom, left:right, :] = foreground
    elif kind == "FILLED_DIAMOND":
        rows, columns = np.ogrid[:HEIGHT, :WIDTH]
        mask = np.abs(columns - centre_x) + np.abs(rows - centre_y) <= size
        frame[mask, :] = foreground
    elif kind == "SQUARE_RING":
        _require(0 < secondary < size, "ring dimensions differ")
        outer = size // 2
        inner = secondary // 2
        _require(
            0 <= centre_x - outer < centre_x + outer <= WIDTH
            and 0 <= centre_y - outer < centre_y + outer <= HEIGHT,
            "ring leaves frame",
        )
        frame[
            centre_y - outer : centre_y + outer,
            centre_x - outer : centre_x + outer,
            :,
        ] = foreground
        frame[
            centre_y - inner : centre_y + inner,
            centre_x - inner : centre_x + inner,
            :,
        ] = 32
    elif kind == "DIAGONAL_BAND":
        rows, columns = np.ogrid[:HEIGHT, :WIDTH]
        mask = (
            np.abs((columns - centre_x) - (rows - centre_y)) <= size // 2
        ) & (np.abs(columns - centre_x) <= 330) & (
            np.abs(rows - centre_y) <= 330
        )
        frame[mask, :] = foreground
    else:
        half = size // 2
        _require(
            0 <= centre_y - 260 < centre_y + 260 <= HEIGHT
            and 0 <= centre_x - 250 - half < centre_x - 250 + half <= WIDTH
            and 0 <= centre_y - half < centre_y + half <= HEIGHT
            and 0 <= centre_x + 40 < centre_x + 430 <= WIDTH,
            "bars leave frame",
        )
        frame[
            centre_y - 260 : centre_y + 260,
            centre_x - 250 - half : centre_x - 250 + half,
            :,
        ] = foreground
        frame[
            centre_y - half : centre_y + half,
            centre_x + 40 : centre_x + 430,
            :,
        ] = foreground
    frame.setflags(write=False)
    return frame


def _source_binding(recipe: dict[str, object]) -> dict[str, object]:
    frame = _render_frame(recipe)
    raw = frame.tobytes(order="C")
    payload = {
        "source_id": recipe["source_id"],
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "payload_bytes": len(raw),
        "rgb_value_sum": int(frame.sum(dtype=np.uint64)),
    }
    return {**payload, "source_binding_digest": _digest(payload)}


def _coordinate(position: int) -> tuple[int, int, int]:
    return (
        position // (GRID_COLUMNS * CHANNELS),
        (position % (GRID_COLUMNS * CHANNELS)) // CHANNELS,
        position % CHANNELS,
    )


def _distance_squared(left: int, right: int) -> int:
    lr, lc, lh = _coordinate(left)
    rr, rc, rh = _coordinate(right)
    return ((lr - rr) * 22) ** 2 + ((lc - rc) * 14) ** 2 + ((lh - rh) * 77) ** 2


def _farthest_order(candidates: tuple[int, ...], seed: str) -> tuple[int, ...]:
    ranks = {
        position: hashlib.sha256(f"{seed}|{position}".encode("ascii")).hexdigest()
        for position in candidates
    }
    remaining = set(candidates)
    first = min(remaining, key=lambda position: (ranks[position], position))
    selected = [first]
    remaining.remove(first)
    while remaining:
        chosen = min(
            remaining,
            key=lambda position: (
                -min(_distance_squared(position, prior) for prior in selected),
                ranks[position],
                position,
            ),
        )
        selected.append(chosen)
        remaining.remove(chosen)
    return tuple(selected)


def _mask_binding(mask_id: str, positions: tuple[int, ...], seed: str) -> dict[str, object]:
    coordinates = tuple(_coordinate(position) for position in positions)
    payload = {
        "mask_id": mask_id,
        "seed": seed,
        "positions": list(positions),
        "value_count": len(positions),
        "rows_represented": sorted({item[0] for item in coordinates}),
        "columns_represented": sorted({item[1] for item in coordinates}),
        "channel_counts": {
            str(channel): sum(item[2] == channel for item in coordinates)
            for channel in range(CHANNELS)
        },
        "unique_cell_count": len({(item[0], item[1]) for item in coordinates}),
    }
    return {**payload, "mask_digest": _digest(payload)}


def _mask_bindings() -> tuple[dict[str, object], ...]:
    all_positions = tuple(range(GRID_ROWS * GRID_COLUMNS * CHANNELS))
    first = _farthest_order(all_positions, MASK_A_SEED)[:96]
    remaining = tuple(position for position in all_positions if position not in set(first))
    second = _farthest_order(remaining, MASK_B_SEED)[:96]
    union = first + second
    _require(
        len(set(first)) == len(set(second)) == 96
        and set(first).isdisjoint(second)
        and len(set(union)) == 192,
        "mask inventory differs",
    )
    bindings = (
        _mask_binding("VIEW_A_96", first, MASK_A_SEED),
        _mask_binding("VIEW_B_96", second, MASK_B_SEED),
        _mask_binding("UNION_192", union, f"{MASK_A_SEED}+{MASK_B_SEED}"),
    )
    _require(
        all(
            item["rows_represented"] == list(range(GRID_ROWS))
            and item["columns_represented"] == list(range(GRID_COLUMNS))
            for item in bindings
        ),
        "mask coverage differs",
    )
    return bindings


def _schema_contract() -> dict[str, object]:
    generation_fields = (
        "schema",
        "bank_id",
        "bank_config_digest",
        "slot_id",
        "creation_event",
        "ppb_prestate_digest",
        "ppb_input_digest",
        "ppb_transition_result_digest",
        "ppb_poststate_digest",
        "accepted_step",
    )
    payload = {
        "canonical_serialization": "ASCII_JSON_SORT_KEYS_COMPACT_NO_NAN_V1",
        "identifier_pattern": _IDENTIFIER.pattern,
        "limits": {
            "identifier_bytes": MAX_IDENTIFIER_BYTES,
            "digest_bytes": 64,
            "uint32_max": UINT32_MAX,
            "uint64_max": UINT64_MAX,
            "canonical_float_token_bytes": MAX_FLOAT_TOKEN_BYTES,
            "descriptor_dimension": 144,
            "entry_capacity_per_slot": 4,
            "visual_slot_capacity": 4,
        },
        "slot_generation": {
            "schema": "s2me.slot-generation.v1",
            "ordered_fields": list(generation_fields),
            "creation_events": ["CREATED", "REPLACED"],
            "digest_rule": "SHA256_CANONICAL_PAYLOAD_WITHOUT_EVIDENCE_FIELDS",
            "forbidden_fields": [
                "evidence_digest",
                "entry_digest",
                "centroid_digest",
                "radius",
                "future_transition_digest",
            ],
        },
        "assigned_entry": {
            "schema": "s2me.assigned-form-evidence.v1",
            "ordered_fields": [
                "schema",
                "slot_id",
                "slot_generation_digest",
                "ppb_accepted_step",
                "ppb_transition",
                "formation_receipt_digest",
                "ppb_input_digest",
                "visual_values_digest",
                "source_clock_id",
                "source_window_start_tick",
                "source_window_end_tick",
                "profile_digest",
                "geometry_digest",
                "union_mask_digest",
                "descriptor_schema_digest",
                "descriptor_values",
                "descriptor_values_digest",
                "previous_entry_digest",
                "entry_digest",
            ],
            "maximum_canonical_bytes": MAX_ASSIGNED_ENTRY_BYTES,
        },
        "slot_evidence": {
            "schema": "s2me.slot-applicability-evidence.v1",
            "ordered_fields": [
                "schema",
                "slot_id",
                "slot_generation_digest",
                "slot_digest",
                "prototype_digest",
                "support_count",
                "retained_entries",
                "first_retained_step",
                "last_retained_step",
                "generation_formation_count",
                "evidence_status",
                "evidence_digest",
            ],
            "fifo_rule": "LAST_FOUR_MATCHED_OR_CREATED_FORMATIONS_IN_STEP_ORDER",
            "maximum_canonical_bytes": MAX_SLOT_EVIDENCE_BYTES,
        },
        "learned_envelope": {
            "schema": "s2me.learned-slot-envelope.v1",
            "ordered_fields": [
                "schema",
                "slot_id",
                "slot_generation_digest",
                "slot_digest",
                "evidence_digest",
                "evidence_count",
                "centroid_values",
                "centroid_digest",
                "training_distances",
                "radius",
                "envelope_digest",
            ],
            "centroid_rule": "COMPONENTWISE_MATH_FSUM_DIVIDE_BY_COUNT_BINARY64",
            "radius_rule": "MAX_TRAINING_MEAN_L1_WITHOUT_MARGIN",
            "maximum_canonical_bytes": MAX_ENVELOPE_BYTES,
        },
        "formation_receipt": {
            "schema": "s2me.applicability-formation-receipt.v1",
            "ordered_fields": [
                "schema",
                "owner_id",
                "formation_input_digest",
                "base_memory_prestate_digest",
                "base_memory_poststate_digest",
                "evidence_prestate_digest",
                "evidence_poststate_digest",
                "selected_visual_slot_id",
                "slot_generation_digest",
                "ppb_transition_result_digest",
                "assigned_entry_digest",
                "combined_poststate_digest",
                "receipt_digest",
            ],
            "maximum_canonical_bytes": MAX_FORMATION_RECEIPT_BYTES,
        },
        "error_receipt": {
            "schema": "s2me.applicability-error-receipt.v1",
            "maximum_canonical_bytes": MAX_ERROR_RECEIPT_BYTES,
            "partial_memory_poststate_allowed": False,
        },
        "extended_memory_state": {
            "schema": "s2me.slot-applicability-memory-state.v1",
            "maximum_canonical_bytes": MAX_EXTENDED_MEMORY_STATE_BYTES,
            "maximum_numeric_float64_bytes": 18_432,
        },
    }
    return {**payload, "schema_contract_digest": _digest(payload)}


def _formation_events(bindings: dict[str, dict[str, object]]) -> tuple[dict[str, object], ...]:
    source_order = (
        "input-001",
        "input-007",
        "input-002",
        "input-008",
        "input-003",
        "input-009",
        "input-004",
        "input-010",
        "input-001",
        "input-007",
        "input-019",
        "input-020",
        "input-021",
        "input-022",
        "input-023",
        "input-024",
        "input-025",
        "input-026",
        "input-027",
    )
    events = []
    for ordinal, source_id in enumerate(source_order, start=1):
        start = (ordinal - 1) * TICKS_PER_EVENT
        payload = {
            "event_id": f"event-{ordinal:03d}",
            "ordinal": ordinal,
            "event_type": "FULL_VISUAL_FORMATION",
            "source_id": source_id,
            "source_binding_digest": bindings[source_id]["source_binding_digest"],
            "source_payload_sha256": bindings[source_id]["payload_sha256"],
            "source_clock_id": SOURCE_CLOCK_ID,
            "window_start_tick": start,
            "window_end_tick": start + TICKS_PER_EVENT,
        }
        events.append({**payload, "event_digest": _digest(payload)})
    return tuple(events)


def _case_plan(bindings: dict[str, dict[str, object]]) -> tuple[dict[str, object], ...]:
    compatible = (
        "input-005",
        "input-006",
        "input-011",
        "input-012",
        "input-013",
        "input-014",
        "input-015",
        "input-016",
        "input-017",
        "input-018",
    )
    pairs = tuple((source_id, source_id) for source_id in compatible) + (
        ("input-005", "input-011"),
        ("input-006", "input-012"),
    )
    cases = []
    for ordinal, (left, right) in enumerate(pairs, start=1):
        payload = {
            "case_id": f"case-{ordinal:03d}",
            "view_a_source_id": left,
            "view_b_source_id": right,
            "view_a_payload_sha256": bindings[left]["payload_sha256"],
            "view_b_payload_sha256": bindings[right]["payload_sha256"],
            "maximum_tick_gap": MAX_PAIR_GAP_TICKS,
            "compatibility_rule": "SAME_SOURCE_AND_PAYLOAD_WITH_FORWARD_TIME",
        }
        cases.append({**payload, "case_plan_digest": _digest(payload)})
    return tuple(cases)


def _evaluation_root() -> dict[str, object]:
    rows = []
    for ordinal in range(1, 3):
        rows.append(
            {
                "case_id": f"case-{ordinal:03d}",
                "evaluation_kind": "KNOWN_HOLDOUT",
                "expected_family_id": "evaluation-family-01",
            }
        )
    for ordinal in range(3, 5):
        rows.append(
            {
                "case_id": f"case-{ordinal:03d}",
                "evaluation_kind": "KNOWN_HOLDOUT",
                "expected_family_id": "evaluation-family-02",
            }
        )
    for ordinal in range(5, 9):
        rows.append(
            {
                "case_id": f"case-{ordinal:03d}",
                "evaluation_kind": "UNKNOWN_FORM",
                "expected_family_id": None,
            }
        )
    for ordinal in range(9, 11):
        rows.append(
            {
                "case_id": f"case-{ordinal:03d}",
                "evaluation_kind": "AMBIGUOUS_INTERMEDIATE",
                "expected_family_id": None,
            }
        )
    for ordinal in range(11, 13):
        rows.append(
            {
                "case_id": f"case-{ordinal:03d}",
                "evaluation_kind": "INCOMPATIBLE_PAIR",
                "expected_family_id": None,
            }
        )
    payload = {
        "families": [
            {
                "family_id": "evaluation-family-01",
                "training_source_ids": [f"input-{index:03d}" for index in range(1, 5)],
                "holdout_source_ids": ["input-005", "input-006"],
            },
            {
                "family_id": "evaluation-family-02",
                "training_source_ids": [f"input-{index:03d}" for index in range(7, 11)],
                "holdout_source_ids": ["input-011", "input-012"],
            },
        ],
        "unknown_source_ids": [f"input-{index:03d}" for index in range(13, 17)],
        "ambiguous_source_ids": ["input-017", "input-018"],
        "pressure_source_ids": [f"input-{index:03d}" for index in range(19, 28)],
        "cases": rows,
        "available_to_execution": False,
    }
    return {**payload, "evaluation_root_digest": _digest(payload)}


def _plan() -> dict[str, object]:
    recipes = _content_recipes()
    source_bindings = tuple(_source_binding(item) for item in recipes)
    _require(
        len({str(item["payload_sha256"]) for item in source_bindings}) == len(source_bindings),
        "source payloads are not unique",
    )
    bindings = {str(item["source_id"]): item for item in source_bindings}
    masks = _mask_bindings()
    schema_contract = _schema_contract()
    events = _formation_events(bindings)
    cases = _case_plan(bindings)
    evaluation = _evaluation_root()
    payload = {
        "schema": SCHEMA,
        "plan_id": PLAN_ID,
        "source_root": {
            "source_seed": SOURCE_SEED,
            "generator": "PRESEALED_GEOMETRIC_OPEN_SET_V1_COMPATIBLE",
            "family_layout_selection": "TWO_LOWEST_SHA256_SEED_RANKS_FROM_LITERAL_POOL",
            "family_layout_pool_digest": _digest(
                [[list(point) for point in layout] for layout in _FAMILY_LAYOUT_POOL]
            ),
            "training_transforms": [list(item) for item in _TRAIN_TRANSFORMS],
            "holdout_transforms": [list(item) for item in _HOLDOUT_TRANSFORMS],
            "recipes": [
                {**item, "offsets": [list(point) for point in item["offsets"]]}
                for item in recipes
            ],
            "source_bindings": list(source_bindings),
            "source_contract": {
                "format": "RGB8",
                "width": WIDTH,
                "height": HEIGHT,
                "channels": CHANNELS,
                "payload_bytes": WIDTH * HEIGHT * CHANNELS,
                "raw_payload_retained": False,
            },
            "receptor_distance_or_ppb_available": False,
        },
        "mask_root": {
            "algorithm": "DISJOINT_INTEGER_FARTHEST_POINT_WITH_SHA256_SEED_TIES_V1",
            "masks": list(masks),
            "image_values_or_evaluation_roles_available": False,
        },
        "execution_root": {
            "formation_events": list(events),
            "cases": list(cases),
            "event_count": len(events),
            "case_count": len(cases),
            "evaluation_roles_available": False,
            "receptor_calls": 0,
            "distance_calls": 0,
            "ppb_calls": 0,
            "memory_calls": 0,
            "context_calls": 0,
            "field_calls": 0,
        },
        "slot_evidence_schema_root": schema_contract,
        "evaluation_root": evaluation,
        "decision_rule": {
            "required_start_chain": ["CREATED", "MATCHED", "MATCHED"],
            "minimum_distinct_visual_values_digests": 2,
            "minimum_distinct_form_descriptor_digests": 2,
            "failure_status": "S2ME_SLOT_APPLICABILITY_HISTORY_NOT_MATERIALIZABLE",
            "corpus_change_retry_or_threshold_change_allowed": False,
        },
    }
    return {**payload, "plan_digest": _digest(payload)}


def materialize_plan_once(output_root: Path, *, plan_id: str) -> Path:
    global PLAN_ENABLED, _USED
    _require(PLAN_ENABLED is True and plan_id == PLAN_ID, "plan is not authorized")
    _require(isinstance(output_root, Path) and output_root.is_absolute(), "output root differs")
    _require(not _USED and _LOCK.acquire(blocking=False), "plan materialization is consumed")
    _USED = True
    try:
        record = _plan()
        run_dir = output_root / plan_id
        run_dir.mkdir(parents=True, exist_ok=False)
        target = run_dir / "presealed-plan.json"
        temporary = run_dir / ".presealed-plan.json.tmp"
        data = _canonical_bytes(record, newline=True)
        _require(len(data) <= MAX_PLAN_BYTES, "plan exceeds canonical byte limit")
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
