"""Deterministic raw AV sources sealed without receptor or memory imports."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import struct

import numpy as np


S2MT_SOURCE_SCHEMA = "s2mt.private.presealed-transfer-sources.v1"
SAMPLE_RATE = 48_000
SAMPLE_COUNT = 4_800
FRAME_WIDTH = 1_920
FRAME_HEIGHT = 1_080
GRID_COLUMNS = 12
GRID_ROWS = 8
CHANNEL_COUNT = 3

RECIPE_IDS = tuple(f"n{index:02d}" for index in range(13))
FORMATION_SEQUENCE = (
    "n00", "n01", "n02", "n00", "n01", "n02", "n00", "n01", "n02",
    "n00", "n01", "n03", "n04", "n05", "n06", "n07", "n08", "n09",
    "n10", "n11",
)
CUE_SEQUENCE = (
    ("n00", "AUDITORY"),
    ("n00", "VISUAL"),
    ("n01", "AUDITORY"),
    ("n01", "VISUAL"),
    ("n02", "AUDITORY"),
    ("n02", "VISUAL"),
    ("n12", "AUDITORY"),
    ("n12", "VISUAL"),
)
FREQUENCIES_HZ = (
    80, 180, 400, 760, 920, 1_100, 1_300,
    1_520, 1_760, 2_020, 2_300, 2_620, 20,
)
VISUAL_SEEDS = tuple(f"s2mt-visual-seed-{index:02d}" for index in range(13))
VISUAL_VISIBLE_POSITIONS = tuple(range(32))


class S2MTSourceError(ValueError):
    """A presealed recipe, raw payload, or plan relation is invalid."""


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def _recipe_index(recipe_id: str) -> int:
    if recipe_id not in RECIPE_IDS:
        raise S2MTSourceError("raw recipe id differs")
    return int(recipe_id[1:])


def _grid_values(recipe_id: str) -> np.ndarray:
    index = _recipe_index(recipe_id)
    bits: list[int] = []
    block = 0
    while len(bits) < GRID_ROWS * GRID_COLUMNS * CHANNEL_COUNT:
        digest = hashlib.sha256(f"{VISUAL_SEEDS[index]}:{block:03d}".encode("ascii")).digest()
        for byte in digest:
            bits.extend(255 if byte & (1 << shift) else 0 for shift in range(8))
        block += 1
    return np.asarray(bits[: GRID_ROWS * GRID_COLUMNS * CHANNEL_COUNT], dtype=np.uint8).reshape(
        GRID_ROWS,
        GRID_COLUMNS,
        CHANNEL_COUNT,
    )


def visual_frame(recipe_id: str, *, partial: bool) -> np.ndarray:
    grid = _grid_values(recipe_id)
    if partial:
        flattened = grid.reshape(-1).copy()
        visible = set(VISUAL_VISIBLE_POSITIONS)
        for position in range(len(flattened)):
            if position not in visible:
                flattened[position] = 0
        grid = flattened.reshape(GRID_ROWS, GRID_COLUMNS, CHANNEL_COUNT)
    frame = np.repeat(
        np.repeat(grid, FRAME_HEIGHT // GRID_ROWS, axis=0),
        FRAME_WIDTH // GRID_COLUMNS,
        axis=1,
    )
    if frame.shape != (FRAME_HEIGHT, FRAME_WIDTH, CHANNEL_COUNT) or frame.dtype != np.uint8:
        raise S2MTSourceError("visual payload form differs")
    frame.setflags(write=False)
    return frame


def audio_window(recipe_id: str) -> tuple[float, ...]:
    frequency = FREQUENCIES_HZ[_recipe_index(recipe_id)]
    amplitude = _f32(0.8500000238418579)
    values = tuple(
        _f32(amplitude * math.sin((2.0 * math.pi * frequency * index) / SAMPLE_RATE))
        for index in range(SAMPLE_COUNT)
    )
    if len(values) != SAMPLE_COUNT or any(not math.isfinite(value) or abs(value) > 1.0 for value in values):
        raise S2MTSourceError("auditory payload form differs")
    return values


def _visual_digest(recipe_id: str, *, partial: bool) -> str:
    return hashlib.sha256(visual_frame(recipe_id, partial=partial).tobytes(order="C")).hexdigest()


def _audio_digest(recipe_id: str) -> str:
    return hashlib.sha256(np.asarray(audio_window(recipe_id), dtype="<f4").tobytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class S2MTRawRecipeV1:
    recipe_id: str
    visual_seed: str
    audio_frequency_hz: int
    visual_payload_digest: str
    auditory_payload_digest: str
    partial_visual_payload_digest: str
    recipe_digest: str
    schema: str = S2MT_SOURCE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "recipe_digest"
        }


@dataclass(frozen=True, slots=True)
class PresealedAVCorpusPlanV1:
    plan_id: str
    recipes: tuple[S2MTRawRecipeV1, ...]
    formation_sequence: tuple[str, ...]
    cue_sequence: tuple[tuple[str, str], ...]
    event_count: int
    plan_digest: str
    schema: str = S2MT_SOURCE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "plan_id": self.plan_id,
            "recipe_digests": [item.recipe_digest for item in self.recipes],
            "formation_sequence": list(self.formation_sequence),
            "cue_sequence": [list(item) for item in self.cue_sequence],
            "event_count": self.event_count,
        }


def build_presealed_plan() -> PresealedAVCorpusPlanV1:
    recipes = []
    for index, recipe_id in enumerate(RECIPE_IDS):
        temporary = S2MTRawRecipeV1(
            recipe_id,
            VISUAL_SEEDS[index],
            FREQUENCIES_HZ[index],
            _visual_digest(recipe_id, partial=False),
            _audio_digest(recipe_id),
            _visual_digest(recipe_id, partial=True),
            "",
        )
        recipes.append(
            S2MTRawRecipeV1(
                temporary.recipe_id,
                temporary.visual_seed,
                temporary.audio_frequency_hz,
                temporary.visual_payload_digest,
                temporary.auditory_payload_digest,
                temporary.partial_visual_payload_digest,
                _digest(temporary.payload_without_digest()),
            )
        )
    payload = {
        "schema": S2MT_SOURCE_SCHEMA,
        "plan_id": "s2mt-presealed-transfer-plan",
        "recipe_digests": [item.recipe_digest for item in recipes],
        "formation_sequence": list(FORMATION_SEQUENCE),
        "cue_sequence": [list(item) for item in CUE_SEQUENCE],
        "event_count": len(FORMATION_SEQUENCE) + len(CUE_SEQUENCE),
    }
    return PresealedAVCorpusPlanV1(
        payload["plan_id"],
        tuple(recipes),
        FORMATION_SEQUENCE,
        CUE_SEQUENCE,
        payload["event_count"],
        _digest(payload),
    )


def verified_visual_frame(
    plan: PresealedAVCorpusPlanV1,
    recipe_id: str,
    *,
    partial: bool,
) -> np.ndarray:
    if type(plan) is not PresealedAVCorpusPlanV1 or plan.plan_digest != _digest(plan.payload_without_digest()):
        raise S2MTSourceError("presealed plan differs")
    recipe = plan.recipes[_recipe_index(recipe_id)]
    frame = visual_frame(recipe_id, partial=partial)
    actual = hashlib.sha256(frame.tobytes(order="C")).hexdigest()
    expected = recipe.partial_visual_payload_digest if partial else recipe.visual_payload_digest
    if actual != expected:
        raise S2MTSourceError("visual payload differs from presealed digest")
    return frame


def verified_audio_window(
    plan: PresealedAVCorpusPlanV1,
    recipe_id: str,
) -> tuple[float, ...]:
    if type(plan) is not PresealedAVCorpusPlanV1 or plan.plan_digest != _digest(plan.payload_without_digest()):
        raise S2MTSourceError("presealed plan differs")
    recipe = plan.recipes[_recipe_index(recipe_id)]
    values = audio_window(recipe_id)
    actual = hashlib.sha256(np.asarray(values, dtype="<f4").tobytes()).hexdigest()
    if actual != recipe.auditory_payload_digest:
        raise S2MTSourceError("auditory payload differs from presealed digest")
    return values


assert len(FORMATION_SEQUENCE) == 20
assert len(CUE_SEQUENCE) == 8
assert len(set(RECIPE_IDS)) == 13

__all__: tuple[str, ...] = ()
