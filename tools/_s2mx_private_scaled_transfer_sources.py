"""Prospective S2-MT sources with one pre-receptor PCM input scale."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import struct

import numpy as np

from tools import _s2mt_private_presealed_transfer_sources as base_sources


S2MT_SOURCE_SCHEMA = "s2mt.private.presealed-scaled-transfer-sources.v2"
AUDIO_INPUT_SCALE_DECIMAL = "0.989912331104279"
AUDIO_INPUT_SCALE = float(np.float32(float(AUDIO_INPUT_SCALE_DECIMAL)))
AUDIO_INPUT_SCALE_F32_HEX = "e56a7d3f"
BASE_SOURCE_SHA256 = "ae808ad2a9f206bac45210f5f121e232e72da76b22e0b2bf7c599cc57e479f15"
S2MW_EVIDENCE_FILE_SHA256 = "b1ca1ad9d11e29c6d5b547d166741f1afbf40fb3e8f240ea6eb07d3f4e7d87ef"
S2MW_EVIDENCE_RECORD_DIGEST = "5ecd4b166c7393a867ae2c52f2460a514e720ed30d20fd790984de82640ff674"
S2MW_EVIDENCE_DIRECTORY_ID = "s2mw-audio-receptor-compatibility-20260906-02"
S2MW_EMBEDDED_AUDIT_ID = "s2mw-audio-receptor-compatibility-20260905-01"

SAMPLE_RATE = base_sources.SAMPLE_RATE
SAMPLE_COUNT = base_sources.SAMPLE_COUNT
FRAME_WIDTH = base_sources.FRAME_WIDTH
FRAME_HEIGHT = base_sources.FRAME_HEIGHT
GRID_COLUMNS = base_sources.GRID_COLUMNS
GRID_ROWS = base_sources.GRID_ROWS
CHANNEL_COUNT = base_sources.CHANNEL_COUNT
RECIPE_IDS = base_sources.RECIPE_IDS
FORMATION_SEQUENCE = base_sources.FORMATION_SEQUENCE
CUE_SEQUENCE = base_sources.CUE_SEQUENCE
FREQUENCIES_HZ = base_sources.FREQUENCIES_HZ
VISUAL_SEEDS = base_sources.VISUAL_SEEDS
VISUAL_VISIBLE_POSITIONS = base_sources.VISUAL_VISIBLE_POSITIONS


class S2MTScaledSourceError(ValueError):
    """A scaled source plan or payload binding is invalid."""


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


def _recipe_index(recipe_id: str) -> int:
    if recipe_id not in RECIPE_IDS:
        raise S2MTScaledSourceError("scaled recipe id differs")
    return int(recipe_id[1:])


def _scale_f32() -> np.float32:
    value = np.float32(AUDIO_INPUT_SCALE)
    if struct.pack("<f", float(value)).hex() != AUDIO_INPUT_SCALE_F32_HEX:
        raise S2MTScaledSourceError("audio input scale encoding differs")
    return value


def visual_frame(recipe_id: str, *, partial: bool) -> np.ndarray:
    return base_sources.visual_frame(recipe_id, partial=partial)


def audio_window(recipe_id: str) -> tuple[float, ...]:
    original = np.asarray(base_sources.audio_window(recipe_id), dtype="<f4")
    scaled = np.multiply(original, _scale_f32(), dtype=np.float32)
    if (
        scaled.shape != (SAMPLE_COUNT,)
        or scaled.dtype != np.float32
        or not np.all(np.isfinite(scaled))
        or np.any(np.abs(scaled) > 1.0)
    ):
        raise S2MTScaledSourceError("scaled auditory payload form differs")
    return tuple(float(value) for value in scaled)


def _scaled_audio_digest(recipe_id: str) -> str:
    return hashlib.sha256(np.asarray(audio_window(recipe_id), dtype="<f4").tobytes(order="C")).hexdigest()


@dataclass(frozen=True, slots=True)
class S2MTScaledRawRecipeV2:
    recipe_id: str
    visual_seed: str
    audio_frequency_hz: int
    base_recipe_digest: str
    base_auditory_payload_digest: str
    visual_payload_digest: str
    auditory_payload_digest: str
    partial_visual_payload_digest: str
    audio_input_scale: float
    recipe_digest: str
    schema: str = S2MT_SOURCE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "recipe_digest"
        }


@dataclass(frozen=True, slots=True)
class PresealedAVCorpusPlanV2:
    plan_id: str
    base_plan_digest: str
    audio_input_scale: float
    audio_input_scale_f32_hex: str
    compatibility_evidence_directory_id: str
    compatibility_evidence_embedded_audit_id: str
    compatibility_evidence_file_sha256: str
    compatibility_evidence_record_digest: str
    recipes: tuple[S2MTScaledRawRecipeV2, ...]
    formation_sequence: tuple[str, ...]
    cue_sequence: tuple[tuple[str, str], ...]
    event_count: int
    plan_digest: str
    schema: str = S2MT_SOURCE_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "plan_id": self.plan_id,
            "base_plan_digest": self.base_plan_digest,
            "audio_input_scale": self.audio_input_scale,
            "audio_input_scale_f32_hex": self.audio_input_scale_f32_hex,
            "compatibility_evidence_directory_id": self.compatibility_evidence_directory_id,
            "compatibility_evidence_embedded_audit_id": self.compatibility_evidence_embedded_audit_id,
            "compatibility_evidence_file_sha256": self.compatibility_evidence_file_sha256,
            "compatibility_evidence_record_digest": self.compatibility_evidence_record_digest,
            "recipe_digests": [item.recipe_digest for item in self.recipes],
            "formation_sequence": list(self.formation_sequence),
            "cue_sequence": [list(item) for item in self.cue_sequence],
            "event_count": self.event_count,
        }


def build_presealed_plan() -> PresealedAVCorpusPlanV2:
    base_plan = base_sources.build_presealed_plan()
    scale = float(_scale_f32())
    recipes = []
    for base_recipe in base_plan.recipes:
        temporary = S2MTScaledRawRecipeV2(
            base_recipe.recipe_id,
            base_recipe.visual_seed,
            base_recipe.audio_frequency_hz,
            base_recipe.recipe_digest,
            base_recipe.auditory_payload_digest,
            base_recipe.visual_payload_digest,
            _scaled_audio_digest(base_recipe.recipe_id),
            base_recipe.partial_visual_payload_digest,
            scale,
            "",
        )
        recipes.append(
            S2MTScaledRawRecipeV2(
                temporary.recipe_id,
                temporary.visual_seed,
                temporary.audio_frequency_hz,
                temporary.base_recipe_digest,
                temporary.base_auditory_payload_digest,
                temporary.visual_payload_digest,
                temporary.auditory_payload_digest,
                temporary.partial_visual_payload_digest,
                temporary.audio_input_scale,
                _digest(temporary.payload_without_digest()),
            )
        )
    payload = {
        "schema": S2MT_SOURCE_SCHEMA,
        "plan_id": "s2mt-presealed-scaled-transfer-plan-v2",
        "base_plan_digest": base_plan.plan_digest,
        "audio_input_scale": scale,
        "audio_input_scale_f32_hex": AUDIO_INPUT_SCALE_F32_HEX,
        "compatibility_evidence_directory_id": S2MW_EVIDENCE_DIRECTORY_ID,
        "compatibility_evidence_embedded_audit_id": S2MW_EMBEDDED_AUDIT_ID,
        "compatibility_evidence_file_sha256": S2MW_EVIDENCE_FILE_SHA256,
        "compatibility_evidence_record_digest": S2MW_EVIDENCE_RECORD_DIGEST,
        "recipe_digests": [item.recipe_digest for item in recipes],
        "formation_sequence": list(FORMATION_SEQUENCE),
        "cue_sequence": [list(item) for item in CUE_SEQUENCE],
        "event_count": len(FORMATION_SEQUENCE) + len(CUE_SEQUENCE),
    }
    return PresealedAVCorpusPlanV2(
        payload["plan_id"],
        payload["base_plan_digest"],
        payload["audio_input_scale"],
        payload["audio_input_scale_f32_hex"],
        payload["compatibility_evidence_directory_id"],
        payload["compatibility_evidence_embedded_audit_id"],
        payload["compatibility_evidence_file_sha256"],
        payload["compatibility_evidence_record_digest"],
        tuple(recipes),
        FORMATION_SEQUENCE,
        CUE_SEQUENCE,
        payload["event_count"],
        _digest(payload),
    )


def _validated_plan(plan: object) -> PresealedAVCorpusPlanV2:
    if type(plan) is not PresealedAVCorpusPlanV2:
        raise S2MTScaledSourceError("scaled source plan type differs")
    if plan.plan_digest != _digest(plan.payload_without_digest()):
        raise S2MTScaledSourceError("scaled source plan digest differs")
    if (
        tuple(item.recipe_id for item in plan.recipes) != RECIPE_IDS
        or any(item.recipe_digest != _digest(item.payload_without_digest()) for item in plan.recipes)
        or any(item.audio_input_scale != float(_scale_f32()) for item in plan.recipes)
    ):
        raise S2MTScaledSourceError("scaled recipe binding differs")
    if (
        plan.audio_input_scale != float(_scale_f32())
        or plan.audio_input_scale_f32_hex != AUDIO_INPUT_SCALE_F32_HEX
        or plan.compatibility_evidence_directory_id != S2MW_EVIDENCE_DIRECTORY_ID
        or plan.compatibility_evidence_embedded_audit_id != S2MW_EMBEDDED_AUDIT_ID
        or plan.compatibility_evidence_file_sha256 != S2MW_EVIDENCE_FILE_SHA256
        or plan.compatibility_evidence_record_digest != S2MW_EVIDENCE_RECORD_DIGEST
    ):
        raise S2MTScaledSourceError("scaled source plan binding differs")
    return plan


def verified_visual_frame(
    plan: PresealedAVCorpusPlanV2,
    recipe_id: str,
    *,
    partial: bool,
) -> np.ndarray:
    validated = _validated_plan(plan)
    recipe = validated.recipes[_recipe_index(recipe_id)]
    frame = visual_frame(recipe_id, partial=partial)
    actual = hashlib.sha256(frame.tobytes(order="C")).hexdigest()
    expected = recipe.partial_visual_payload_digest if partial else recipe.visual_payload_digest
    if actual != expected:
        raise S2MTScaledSourceError("visual payload differs from scaled plan")
    return frame


def verified_audio_window(
    plan: PresealedAVCorpusPlanV2,
    recipe_id: str,
) -> tuple[float, ...]:
    validated = _validated_plan(plan)
    recipe = validated.recipes[_recipe_index(recipe_id)]
    values = audio_window(recipe_id)
    actual = hashlib.sha256(np.asarray(values, dtype="<f4").tobytes(order="C")).hexdigest()
    if actual != recipe.auditory_payload_digest:
        raise S2MTScaledSourceError("auditory payload differs from scaled plan")
    return values


assert math.isfinite(AUDIO_INPUT_SCALE) and 0.0 < AUDIO_INPUT_SCALE < 1.0
assert struct.pack("<f", float(np.float32(AUDIO_INPUT_SCALE))).hex() == AUDIO_INPUT_SCALE_F32_HEX
assert len(RECIPE_IDS) == 13
assert len(FORMATION_SEQUENCE) == 20
assert len(CUE_SEQUENCE) == 8

__all__: tuple[str, ...] = ()
