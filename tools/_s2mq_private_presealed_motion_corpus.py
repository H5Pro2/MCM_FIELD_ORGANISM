"""Private one-shot preseal for the S2-MQ visual pair corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

import numpy as np


WIDTH = 1920
HEIGHT = 1080
CHANNELS = 3
PRESEAL_ID = "s2mq-motion-corpus-preseal-20260905-01"
PAIR_IDS = tuple(f"s2mq-pair-{index:03d}" for index in range(1, 9))
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2MQPresealError(ValueError):
    """The S2-MQ corpus cannot be sealed in its bound form."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MQPresealError(message)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _frame_digest(frame: np.ndarray) -> str:
    _require(frame.shape == (HEIGHT, WIDTH, CHANNELS), "frame geometry differs")
    _require(frame.dtype == np.uint8 and frame.flags.c_contiguous, "frame representation differs")
    return hashlib.sha256(memoryview(frame).cast("B")).hexdigest()


def _recipe(
    *,
    background: tuple[int, int, int],
    shape: str,
    center: tuple[int, int],
    size: tuple[int, int],
    primary: tuple[int, int, int],
    secondary: tuple[int, int, int],
    texture_period: int,
    occluder: tuple[int, int, int, int] | None = None,
) -> dict[str, object]:
    return {
        "background": list(background),
        "shape": shape,
        "center": list(center),
        "size": list(size),
        "primary": list(primary),
        "secondary": list(secondary),
        "texture_period": texture_period,
        "occluder": None if occluder is None else list(occluder),
    }


FRAME_RECIPES: tuple[dict[str, object], ...] = (
    _recipe(background=(17, 29, 43), shape="RECT", center=(486, 352), size=(372, 248), primary=(234, 88, 54), secondary=(247, 211, 73), texture_period=11),
    _recipe(background=(17, 29, 43), shape="RECT", center=(523, 375), size=(372, 248), primary=(234, 88, 54), secondary=(247, 211, 73), texture_period=11),
    _recipe(background=(78, 82, 86), shape="RECT", center=(1382, 724), size=(506, 302), primary=(94, 98, 102), secondary=(94, 98, 102), texture_period=0),
    _recipe(background=(78, 82, 86), shape="RECT", center=(1349, 703), size=(506, 302), primary=(94, 98, 102), secondary=(94, 98, 102), texture_period=0),
    _recipe(background=(23, 31, 47), shape="RING", center=(574, 706), size=(356, 356), primary=(49, 221, 181), secondary=(236, 113, 201), texture_period=13),
    _recipe(background=(23, 31, 47), shape="CROSS", center=(607, 682), size=(356, 356), primary=(49, 221, 181), secondary=(236, 113, 201), texture_period=13),
    _recipe(background=(49, 52, 55), shape="RECT", center=(1326, 326), size=(430, 286), primary=(63, 66, 69), secondary=(63, 66, 69), texture_period=0),
    _recipe(background=(49, 52, 55), shape="DIAMOND", center=(1293, 350), size=(430, 286), primary=(63, 66, 69), secondary=(63, 66, 69), texture_period=0),
    _recipe(background=(14, 38, 35), shape="CROSS", center=(724, 504), size=(404, 332), primary=(242, 196, 57), secondary=(52, 188, 231), texture_period=9),
    _recipe(background=(14, 38, 35), shape="CROSS", center=(756, 525), size=(404, 332), primary=(242, 196, 57), secondary=(52, 188, 231), texture_period=9, occluder=(724, 386, 920, 664)),
    _recipe(background=(88, 90, 92), shape="RECT", center=(1262, 584), size=(520, 340), primary=(102, 104, 106), secondary=(102, 104, 106), texture_period=0),
    _recipe(background=(88, 90, 92), shape="RECT", center=(1230, 604), size=(520, 340), primary=(102, 104, 106), secondary=(102, 104, 106), texture_period=0, occluder=(1164, 430, 1426, 778)),
    _recipe(background=(9, 24, 44), shape="RING", center=(492, 486), size=(410, 410), primary=(248, 96, 62), secondary=(69, 228, 153), texture_period=10),
    _recipe(background=(62, 18, 35), shape="DIAMOND", center=(1478, 628), size=(452, 386), primary=(71, 166, 244), secondary=(240, 213, 66), texture_period=14),
    _recipe(background=(96, 99, 102), shape="RECT", center=(606, 766), size=(470, 290), primary=(110, 113, 116), secondary=(110, 113, 116), texture_period=0),
    _recipe(background=(72, 75, 78), shape="RING", center=(1406, 272), size=(390, 390), primary=(86, 89, 92), secondary=(86, 89, 92), texture_period=0),
)


EVALUATION_ROLES: tuple[tuple[str, str, str], ...] = (
    (PAIR_IDS[0], "CONTINUATION", "STRUCTURE_RICH"),
    (PAIR_IDS[1], "CONTINUATION", "EDGE_POOR"),
    (PAIR_IDS[2], "FORM_CHANGE", "STRUCTURE_RICH"),
    (PAIR_IDS[3], "FORM_CHANGE", "EDGE_POOR"),
    (PAIR_IDS[4], "PARTIAL_OCCLUSION", "STRUCTURE_RICH"),
    (PAIR_IDS[5], "PARTIAL_OCCLUSION", "EDGE_POOR"),
    (PAIR_IDS[6], "SCENE_CUT", "STRUCTURE_RICH"),
    (PAIR_IDS[7], "SCENE_CUT", "EDGE_POOR"),
)


def _validate_triplet(value: object, role: str) -> tuple[int, int, int]:
    _require(type(value) is list and len(value) == 3, f"{role} differs")
    result = tuple(value)
    _require(all(type(item) is int and 0 <= item <= 255 for item in result), f"{role} domain differs")
    return result  # type: ignore[return-value]


def render_frame(recipe: dict[str, object]) -> np.ndarray:
    """Render one literal source recipe without importing project perception code."""
    _require(type(recipe) is dict, "recipe form differs")
    background = _validate_triplet(recipe.get("background"), "background")
    primary = _validate_triplet(recipe.get("primary"), "primary")
    secondary = _validate_triplet(recipe.get("secondary"), "secondary")
    shape = recipe.get("shape")
    _require(shape in {"RECT", "CROSS", "RING", "DIAMOND"}, "shape differs")
    center = recipe.get("center")
    size = recipe.get("size")
    _require(type(center) is list and len(center) == 2 and all(type(item) is int for item in center), "center differs")
    _require(type(size) is list and len(size) == 2 and all(type(item) is int and item > 0 for item in size), "size differs")
    cx, cy = center
    sx, sy = size
    _require(0 < cx < WIDTH and 0 < cy < HEIGHT and 0 < sx < WIDTH and 0 < sy < HEIGHT, "shape bounds differ")
    period = recipe.get("texture_period")
    _require(type(period) is int and period >= 0, "texture period differs")

    frame = np.empty((HEIGHT, WIDTH, CHANNELS), dtype=np.uint8)
    frame[:, :] = background
    yy, xx = np.ogrid[:HEIGHT, :WIDTH]
    dx = np.abs(xx - cx)
    dy = np.abs(yy - cy)
    half_x = sx / 2.0
    half_y = sy / 2.0
    if shape == "RECT":
        mask = (dx <= half_x) & (dy <= half_y)
    elif shape == "CROSS":
        mask = ((dx <= half_x * 0.28) & (dy <= half_y)) | ((dx <= half_x) & (dy <= half_y * 0.28))
    elif shape == "RING":
        radius = np.sqrt((dx / half_x) ** 2 + (dy / half_y) ** 2)
        mask = (radius <= 1.0) & (radius >= 0.56)
    else:
        mask = (dx / half_x + dy / half_y) <= 1.0

    if period == 0:
        frame[mask] = primary
    else:
        checker = ((xx // period + yy // period) % 2) == 0
        frame[mask & checker] = primary
        frame[mask & ~checker] = secondary

    occluder = recipe.get("occluder")
    if occluder is not None:
        _require(type(occluder) is list and len(occluder) == 4, "occluder differs")
        left, top, right, bottom = occluder
        _require(all(type(item) is int for item in occluder), "occluder coordinate differs")
        _require(0 <= left < right <= WIDTH and 0 <= top < bottom <= HEIGHT, "occluder bounds differ")
        frame[top:bottom, left:right] = background
    return np.ascontiguousarray(frame)


def corpus_plan_without_payloads() -> dict[str, object]:
    frames = tuple(
        {
            "frame_id": f"s2mq-frame-{index:03d}",
            "recipe": recipe,
        }
        for index, recipe in enumerate(FRAME_RECIPES, start=1)
    )
    return {
        "schema": "s2mq.presealed-source-plan.v1",
        "preseal_id": PRESEAL_ID,
        "geometry": {"width": WIDTH, "height": HEIGHT, "channels": CHANNELS, "pixel_format": "RGB8"},
        "renderer": "S2MQ_LITERAL_GEOMETRIC_RENDERER_V1",
        "frame_count": 16,
        "frames": list(frames),
    }


def materialize_source_plan() -> dict[str, object]:
    base = corpus_plan_without_payloads()
    frames_out: list[dict[str, object]] = []
    for item in base["frames"]:
        _require(type(item) is dict, "frame plan differs")
        frame = render_frame(item["recipe"])
        frames_out.append({**item, "payload_sha256": _frame_digest(frame), "payload_bytes": int(frame.nbytes)})
        del frame
    return {**base, "frames": frames_out, "frame_set_digest": _digest(frames_out)}


def _atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    _require(not path.exists(), f"refusing to overwrite {path.name}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    _require(not temporary.exists(), f"temporary path already exists for {path.name}")
    temporary.write_bytes(_canonical_bytes(payload) + b"\n")
    temporary.replace(path)


def preseal(output_root: Path, contract_sha256: str) -> dict[str, object]:
    _require(isinstance(output_root, Path), "output root type differs")
    _require(_DIGEST.fullmatch(contract_sha256) is not None, "contract digest differs")
    _require(not output_root.exists(), "preseal output root already exists")
    output_root.mkdir(parents=True, exist_ok=False)

    source_plan = materialize_source_plan()
    frame_items = source_plan["frames"]
    _require(type(frame_items) is list and len(frame_items) == 16, "frame inventory differs")
    pairs: list[dict[str, object]] = []
    for pair_index, pair_id in enumerate(PAIR_IDS):
        first = frame_items[pair_index * 2]
        second = frame_items[pair_index * 2 + 1]
        start = pair_index * 100
        pairs.append(
            {
                "pair_id": pair_id,
                "frame_0_id": first["frame_id"],
                "frame_1_id": second["frame_id"],
                "frame_0_payload_digest": first["payload_sha256"],
                "frame_1_payload_digest": second["payload_sha256"],
                "visual_source_clock_id": f"s2mq-visual-clock-{pair_index + 1:03d}",
                "frame_0_window_start_tick": start,
                "frame_0_window_end_tick": start + 1,
                "frame_1_window_start_tick": start + 2,
                "frame_1_window_end_tick": start + 3,
            }
        )
    execution_plan = {
        "schema": "s2mq.role-free-execution-plan.v1",
        "preseal_id": PRESEAL_ID,
        "pair_count": 8,
        "pairs": pairs,
        "evaluation_roles_available": False,
        "s2mp_parameters_mutable": False,
    }
    evaluation_plan = {
        "schema": "s2mq.separate-evaluation-plan.v1",
        "preseal_id": PRESEAL_ID,
        "pair_count": 8,
        "roles": [
            {"pair_id": pair_id, "case_role": role, "structure_stratum": stratum}
            for pair_id, role, stratum in EVALUATION_ROLES
        ],
        "object_identity_claimed": False,
    }
    source_path = Path(__file__).resolve()
    receipt = {
        "schema": "s2mq.preseal-receipt.v1",
        "preseal_id": PRESEAL_ID,
        "contract_sha256": contract_sha256,
        "preseal_source_path": str(source_path),
        "preseal_source_sha256": _file_digest(source_path),
        "source_plan_digest": _digest(source_plan),
        "execution_plan_digest": _digest(execution_plan),
        "evaluation_plan_digest": _digest(evaluation_plan),
        "pixel_analysis_calls": 0,
        "receptor_calls": 0,
        "pose_form_calls": 0,
        "s2mp_calls": 0,
        "memory_calls": 0,
        "context_calls": 0,
        "field_calls": 0,
    }
    _atomic_write_json(output_root / "source_plan.json", source_plan)
    _atomic_write_json(output_root / "execution_plan.json", execution_plan)
    _atomic_write_json(output_root / "evaluation_plan.json", evaluation_plan)
    _atomic_write_json(output_root / "preseal_receipt.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--contract-sha256", required=True)
    args = parser.parse_args()
    receipt = preseal(args.output_root, args.contract_sha256)
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__: tuple[str, ...] = ()
