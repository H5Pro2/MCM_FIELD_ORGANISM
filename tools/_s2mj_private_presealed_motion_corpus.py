"""One-shot source and evaluation preseal for S2-MJ."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from threading import Lock

import numpy as np


SCHEMA = "s2mj.presealed-motion-corpus.v1"
PLAN_ID = "s2mj-motion-corpus-preseal-20260905-01"
PLAN_ENABLED = False

WIDTH = 1920
HEIGHT = 1080
CHANNELS = 3
FRAME_BYTES = WIDTH * HEIGHT * CHANNELS
WINDOW_TICKS = 33_333_333
MAX_PLAN_BYTES = 262_144

_LOCK = Lock()
_USED = False


class S2MJPresealError(RuntimeError):
    """The S2-MJ corpus cannot be sealed as requested."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MJPresealError(message)


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


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


_RECIPES: tuple[dict[str, object], ...] = (
    {"frame_id": "frame-001", "pair_id": "pair-001", "ordinal": 0, "background": (18, 30, 42), "kind": "PANEL", "center": (620, 500), "size": (420, 280), "colors": ((224, 72, 48), (248, 188, 64)), "phase": 0, "occluder": None},
    {"frame_id": "frame-002", "pair_id": "pair-001", "ordinal": 1, "background": (18, 30, 42), "kind": "PANEL", "center": (648, 514), "size": (420, 280), "colors": ((224, 72, 48), (248, 188, 64)), "phase": 0, "occluder": None},
    {"frame_id": "frame-003", "pair_id": "pair-002", "ordinal": 0, "background": (28, 20, 44), "kind": "RING", "center": (1280, 520), "size": (390, 310), "colors": ((72, 208, 232), (184, 248, 224)), "phase": 1, "occluder": None},
    {"frame_id": "frame-004", "pair_id": "pair-002", "ordinal": 1, "background": (28, 20, 44), "kind": "RING", "center": (1248, 540), "size": (390, 310), "colors": ((72, 208, 232), (184, 248, 224)), "phase": 1, "occluder": None},
    {"frame_id": "frame-005", "pair_id": "pair-003", "ordinal": 0, "background": (18, 30, 42), "kind": "PANEL", "center": (620, 500), "size": (420, 280), "colors": ((224, 72, 48), (248, 188, 64)), "phase": 0, "occluder": None},
    {"frame_id": "frame-006", "pair_id": "pair-003", "ordinal": 1, "background": (18, 30, 42), "kind": "CROSS", "center": (648, 514), "size": (420, 280), "colors": ((224, 72, 48), (248, 188, 64)), "phase": 0, "occluder": None},
    {"frame_id": "frame-007", "pair_id": "pair-004", "ordinal": 0, "background": (28, 20, 44), "kind": "RING", "center": (1280, 520), "size": (390, 310), "colors": ((72, 208, 232), (184, 248, 224)), "phase": 1, "occluder": None},
    {"frame_id": "frame-008", "pair_id": "pair-004", "ordinal": 1, "background": (28, 20, 44), "kind": "DIAMOND", "center": (1248, 540), "size": (390, 310), "colors": ((72, 208, 232), (184, 248, 224)), "phase": 1, "occluder": None},
    {"frame_id": "frame-009", "pair_id": "pair-005", "ordinal": 0, "background": (18, 30, 42), "kind": "PANEL", "center": (620, 500), "size": (420, 280), "colors": ((224, 72, 48), (248, 188, 64)), "phase": 0, "occluder": None},
    {"frame_id": "frame-010", "pair_id": "pair-005", "ordinal": 1, "background": (18, 30, 42), "kind": "PANEL", "center": (648, 514), "size": (420, 280), "colors": ((224, 72, 48), (248, 188, 64)), "phase": 0, "occluder": (640, 390, 860, 650, (18, 30, 42))},
    {"frame_id": "frame-011", "pair_id": "pair-006", "ordinal": 0, "background": (28, 20, 44), "kind": "RING", "center": (1280, 520), "size": (390, 310), "colors": ((72, 208, 232), (184, 248, 224)), "phase": 1, "occluder": None},
    {"frame_id": "frame-012", "pair_id": "pair-006", "ordinal": 1, "background": (28, 20, 44), "kind": "RING", "center": (1248, 540), "size": (390, 310), "colors": ((72, 208, 232), (184, 248, 224)), "phase": 1, "occluder": (1050, 430, 1280, 720, (28, 20, 44))},
    {"frame_id": "frame-013", "pair_id": "pair-007", "ordinal": 0, "background": (18, 30, 42), "kind": "PANEL", "center": (620, 500), "size": (420, 280), "colors": ((224, 72, 48), (248, 188, 64)), "phase": 0, "occluder": None},
    {"frame_id": "frame-014", "pair_id": "pair-007", "ordinal": 1, "background": (86, 18, 24), "kind": "DIAMOND", "center": (1430, 300), "size": (560, 420), "colors": ((44, 220, 116), (80, 112, 248)), "phase": 3, "occluder": None},
    {"frame_id": "frame-015", "pair_id": "pair-008", "ordinal": 0, "background": (28, 20, 44), "kind": "RING", "center": (1280, 520), "size": (390, 310), "colors": ((72, 208, 232), (184, 248, 224)), "phase": 1, "occluder": None},
    {"frame_id": "frame-016", "pair_id": "pair-008", "ordinal": 1, "background": (12, 74, 30), "kind": "CROSS", "center": (430, 760), "size": (620, 360), "colors": ((244, 216, 48), (196, 52, 232)), "phase": 4, "occluder": None},
)


def _render(recipe: dict[str, object]) -> np.ndarray:
    frame = np.empty((HEIGHT, WIDTH, CHANNELS), dtype=np.uint8)
    frame[:, :, :] = np.asarray(recipe["background"], dtype=np.uint8)
    center_x, center_y = (int(value) for value in recipe["center"])
    width, height = (int(value) for value in recipe["size"])
    rows, columns = np.ogrid[:HEIGHT, :WIDTH]
    offset_x = columns - center_x
    offset_y = rows - center_y
    kind = str(recipe["kind"])
    if kind == "PANEL":
        mask = (np.abs(offset_x) <= width // 2) & (np.abs(offset_y) <= height // 2)
    elif kind == "CROSS":
        mask = (
            ((np.abs(offset_x) <= width // 7) & (np.abs(offset_y) <= height // 2))
            | ((np.abs(offset_y) <= height // 7) & (np.abs(offset_x) <= width // 2))
        )
    elif kind == "RING":
        outer = (np.abs(offset_x) <= width // 2) & (np.abs(offset_y) <= height // 2)
        inner = (np.abs(offset_x) < width // 4) & (np.abs(offset_y) < height // 4)
        mask = outer & ~inner
    elif kind == "DIAMOND":
        mask = (np.abs(offset_x) * height + np.abs(offset_y) * width) <= (width * height // 2)
    else:
        raise S2MJPresealError("generator kind differs")
    phase = int(recipe["phase"])
    texture = (((columns // 12) + (rows // 12) + phase) & 1) == 0
    first, second = recipe["colors"]
    frame[mask & texture, :] = np.asarray(first, dtype=np.uint8)
    frame[mask & ~texture, :] = np.asarray(second, dtype=np.uint8)
    occluder = recipe["occluder"]
    if occluder is not None:
        left, top, right, bottom, color = occluder
        _require(0 <= left < right <= WIDTH and 0 <= top < bottom <= HEIGHT, "occluder differs")
        frame[top:bottom, left:right, :] = np.asarray(color, dtype=np.uint8)
    _require(frame.shape == (HEIGHT, WIDTH, CHANNELS), "frame shape differs")
    _require(frame.dtype == np.uint8 and frame.flags.c_contiguous, "frame type differs")
    frame.setflags(write=False)
    return frame


def _frame_binding(recipe: dict[str, object]) -> dict[str, object]:
    frame = _render(recipe)
    payload = frame.tobytes(order="C")
    _require(len(payload) == FRAME_BYTES, "frame byte count differs")
    ordinal = int(recipe["ordinal"])
    pair_number = int(str(recipe["pair_id"]).split("-")[1])
    start = ((pair_number - 1) * 2 + ordinal) * WINDOW_TICKS
    body = {
        "frame_id": recipe["frame_id"],
        "pair_id": recipe["pair_id"],
        "pair_ordinal": ordinal,
        "pixel_format": "RGB8",
        "width": WIDTH,
        "height": HEIGHT,
        "channels": CHANNELS,
        "payload_bytes": len(payload),
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "visual_source_clock_id": f"s2mj-clock-{pair_number:03d}",
        "window_start_tick": start,
        "window_end_tick": start + WINDOW_TICKS,
    }
    del payload
    del frame
    return {**body, "frame_binding_digest": _digest(body)}


def _source_plan(bindings: tuple[dict[str, object], ...]) -> dict[str, object]:
    body = {
        "schema": "s2mj.presealed-motion-source-plan.v1",
        "plan_id": PLAN_ID,
        "generator_id": "s2mj-literal-shape-motion-source-v1",
        "generator_rules_frozen": True,
        "frame_count": 16,
        "pair_count": 8,
        "raw_payload_retained": False,
        "receptor_flow_memory_context_field_calls": 0,
        "recipes": [
            {
                **recipe,
                "background": list(recipe["background"]),
                "center": list(recipe["center"]),
                "size": list(recipe["size"]),
                "colors": [list(value) for value in recipe["colors"]],
                "occluder": (
                    None
                    if recipe["occluder"] is None
                    else [
                        *recipe["occluder"][:4],
                        list(recipe["occluder"][4]),
                    ]
                ),
            }
            for recipe in _RECIPES
        ],
        "frame_bindings": list(bindings),
    }
    return {**body, "source_plan_digest": _digest(body)}


def _execution_plan(bindings: tuple[dict[str, object], ...]) -> dict[str, object]:
    by_pair: dict[str, list[dict[str, object]]] = {}
    for binding in bindings:
        by_pair.setdefault(str(binding["pair_id"]), []).append(binding)
    pairs = []
    for pair_id in sorted(by_pair):
        pair_frames = sorted(by_pair[pair_id], key=lambda value: int(value["pair_ordinal"]))
        _require(len(pair_frames) == 2, "pair cardinality differs")
        first, second = pair_frames
        _require(first["visual_source_clock_id"] == second["visual_source_clock_id"], "pair clock differs")
        _require(int(second["window_start_tick"]) >= int(first["window_end_tick"]), "pair time differs")
        body = {
            "pair_id": pair_id,
            "frame_0_id": first["frame_id"],
            "frame_1_id": second["frame_id"],
            "frame_0_binding_digest": first["frame_binding_digest"],
            "frame_1_binding_digest": second["frame_binding_digest"],
            "visual_source_clock_id": first["visual_source_clock_id"],
            "frame_0_window_start_tick": first["window_start_tick"],
            "frame_0_window_end_tick": first["window_end_tick"],
            "frame_1_window_start_tick": second["window_start_tick"],
            "frame_1_window_end_tick": second["window_end_tick"],
        }
        pairs.append({**body, "pair_source_digest": _digest(body)})
    body = {
        "schema": "s2mj.presealed-motion-execution-plan.v1",
        "plan_id": PLAN_ID,
        "pair_count": 8,
        "frame_count": 16,
        "pairs": pairs,
        "evaluation_roles_available": False,
        "generator_parameters_available_to_measurement": False,
        "flow_calls": 0,
        "receptor_calls": 0,
        "memory_calls": 0,
        "context_calls": 0,
        "field_calls": 0,
    }
    return {**body, "execution_plan_digest": _digest(body)}


def _evaluation_plan() -> dict[str, object]:
    rows = (
        ("pair-001", "comparison-group-01", "CONTINUED_MOTION"),
        ("pair-002", "comparison-group-02", "CONTINUED_MOTION"),
        ("pair-003", "comparison-group-01", "FORM_CHANGE"),
        ("pair-004", "comparison-group-02", "FORM_CHANGE"),
        ("pair-005", "comparison-group-01", "PARTIAL_OCCLUSION"),
        ("pair-006", "comparison-group-02", "PARTIAL_OCCLUSION"),
        ("pair-007", "comparison-group-01", "SCENE_CUT"),
        ("pair-008", "comparison-group-02", "SCENE_CUT"),
    )
    cases = []
    for pair_id, group_id, role in rows:
        body = {"pair_id": pair_id, "comparison_group_id": group_id, "evaluation_role": role}
        cases.append({**body, "evaluation_case_digest": _digest(body)})
    body = {
        "schema": "s2mj.presealed-motion-evaluation-plan.v1",
        "plan_id": PLAN_ID,
        "cases": cases,
        "case_count": 8,
        "available_to_execution": False,
        "binding_time": "AFTER_COMPLETE_EXECUTION_EVIDENCE_ONLY",
        "ordinal_rules": [
            "CONTINUED_CYCLE_LT_FORM_CHANGE_AND_SCENE_CUT",
            "CONTINUED_WARPED_RGB_LT_FORM_CHANGE_AND_SCENE_CUT",
            "OCCLUSION_RGB_P95_GT_CONTINUED_RGB_P95",
            "SCENE_CUT_NOT_EQUAL_OR_BETTER_THAN_CONTINUED_ON_BOTH_CORE_METRICS",
        ],
        "numeric_match_threshold": None,
        "object_identity_claimed": False,
    }
    return {**body, "evaluation_plan_digest": _digest(body)}


def _atomic_json(path: Path, value: object) -> None:
    data = _canonical_bytes(value, newline=True)
    _require(len(data) <= MAX_PLAN_BYTES, "artifact exceeds byte limit")
    temporary = path.with_name(f".{path.name}.tmp")
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


def preseal_once(output_root: Path, *, plan_id: str) -> Path:
    global PLAN_ENABLED, _USED
    _require(PLAN_ENABLED is True and plan_id == PLAN_ID, "plan is not authorized")
    _require(isinstance(output_root, Path) and output_root.is_absolute(), "output root differs")
    _require(not _USED and _LOCK.acquire(blocking=False), "preseal is consumed")
    _USED = True
    try:
        run_dir = output_root / plan_id
        run_dir.mkdir(parents=True, exist_ok=False)
        bindings = tuple(_frame_binding(recipe) for recipe in _RECIPES)
        _require(len(bindings) == 16, "frame count differs")
        _require(len({str(value["frame_id"]) for value in bindings}) == 16, "frame ids are not unique")
        source = _source_plan(bindings)
        execution = _execution_plan(bindings)
        evaluation = _evaluation_plan()
        paths = {
            "source": run_dir / "source-plan.json",
            "execution": run_dir / "execution-plan.json",
            "evaluation": run_dir / "evaluation-plan.json",
        }
        _atomic_json(paths["source"], source)
        _atomic_json(paths["execution"], execution)
        _atomic_json(paths["evaluation"], evaluation)
        receipt_body = {
            "schema": SCHEMA,
            "plan_id": PLAN_ID,
            "source_plan_digest": source["source_plan_digest"],
            "source_plan_file_sha256": _file_digest(paths["source"]),
            "execution_plan_digest": execution["execution_plan_digest"],
            "execution_plan_file_sha256": _file_digest(paths["execution"]),
            "evaluation_plan_digest": evaluation["evaluation_plan_digest"],
            "evaluation_plan_file_sha256": _file_digest(paths["evaluation"]),
            "frame_count": 16,
            "pair_count": 8,
            "raw_payload_files": 0,
            "flow_calls": 0,
            "receptor_calls": 0,
            "memory_calls": 0,
            "context_calls": 0,
            "field_calls": 0,
        }
        receipt = {**receipt_body, "preseal_receipt_digest": _digest(receipt_body)}
        _atomic_json(run_dir / "preseal-receipt.json", receipt)
        marker = _digest(receipt)
        (run_dir / "SEALED").write_text(marker + "\n", encoding="ascii", newline="\n")
        return run_dir
    finally:
        PLAN_ENABLED = False
        _LOCK.release()


__all__: tuple[str, ...] = ()
