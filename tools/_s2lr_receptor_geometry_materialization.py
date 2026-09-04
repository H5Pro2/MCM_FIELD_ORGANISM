"""One-shot receptor-only materialization for the corrected S2-LR geometry."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import struct
from threading import Lock

import numpy as np

from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor


SCHEMA = "s2lr.receptor-geometry-materialization.v1"
AUTHORIZED_MATERIALIZATION_ID = "s2lr-materialization-not-authorized"
MATERIALIZATION_ENABLED = False
SUCCESS = "S2LR_VARIATION_GEOMETRY_MATERIALIZED"
BLOCKED = "S2LR_VARIATION_GEOMETRY_NOT_MATERIALIZABLE"
AUDITORY_SLOW_THRESHOLD = 0.02
VISUAL_SLOW_THRESHOLD = 0.01
FAST_THRESHOLD = 0.2
UPDATE_RATE = 0.05
OBSERVED_AUDIO = tuple(range(24))
MASKED_AUDIO = tuple(range(24, 48))
OBSERVED_VISUAL = tuple(range(32))
MASKED_VISUAL = tuple(range(32, 288))

FORMATION_SEQUENCE = (
    "F_PLUS", "G_PLUS", "W", "F_PLUS", "G_PLUS", "W",
    "F_MINUS", "G_MINUS", "W",
    "F_MINUS", "G_MINUS", "F_MINUS", "G_MINUS", "F_MINUS", "G_MINUS",
    "F_MINUS", "G_MINUS", "F_MINUS", "G_MINUS",
    "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9",
)

_AUDIO_TARGETS = {
    "center_mean_l1": 0.009,
    "persistent_mean_l1": 0.015,
    "variation_mean_l1": 0.0051,
}
_AUDIO_BASES = {
    "F": {"center_square_period": 960, "persistent_sine_hz": 8_000, "variation_sine_hz": 12_000},
    "G": {"center_square_period": 240, "persistent_sine_hz": 9_000, "variation_sine_hz": 15_000},
}
_PRESSURE_PERIODS = (400, 300, 240, 160, 120, 80, 60, 40, 30)
_VISUAL_RECIPES = {
    "F_PLUS": (0, 132, 130),
    "F_MINUS": (0, 132, 126),
    "F_H": (0, 128, 128),
    "G_PLUS": (255, 68, 66),
    "G_MINUS": (255, 68, 62),
    "G_H": (255, 64, 64),
    "W": (32, 32, 32),
    "Q07_TARGET": (0, 129, 129),
    "Q08_TARGET": (1, 136, 136),
}
_RECIPE = {
    "schema": SCHEMA,
    "formation_sequence": list(FORMATION_SEQUENCE),
    "audio_targets": _AUDIO_TARGETS,
    "audio_bases": _AUDIO_BASES,
    "visual_recipes": {key: list(value) for key, value in _VISUAL_RECIPES.items()},
    "q09_observed_byte": 128,
    "q10_formula": "float32(0.5*F_H_sample + 0.5*G_H_sample)",
    "pressure_audio": {
        "waveform": "float32 square",
        "amplitude": 0.5,
        "periods": list(_PRESSURE_PERIODS),
    },
    "pressure_visual_ordinals": list(range(2, 11)),
    "thresholds": {"auditory_slow": 0.02, "visual_slow": 0.01, "fast": 0.2},
}
RECIPE_DIGEST = hashlib.sha256(
    json.dumps(_RECIPE, sort_keys=True, separators=(",", ":")).encode("ascii")
).hexdigest()

_LOCK = Lock()
_USED = False


class S2LRMaterializationError(RuntimeError):
    """The one-shot materialization boundary is invalid or consumed."""


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


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def _pcm_digest(values: tuple[float, ...]) -> str:
    return hashlib.sha256(np.asarray(values, dtype="<f4").tobytes()).hexdigest()


def _mean_l1(
    left: tuple[float, ...],
    right: tuple[float, ...],
    indexes: tuple[int, ...] | None = None,
) -> float:
    positions = tuple(range(len(left))) if indexes is None else indexes
    if len(left) != len(right) or not positions:
        raise S2LRMaterializationError("distance dimensions differ")
    return sum(abs(left[index] - right[index]) for index in positions) / len(positions)


def _analyze_audio(window: tuple[float, ...]) -> tuple[float, ...]:
    if (
        len(window) != 4_800
        or any(not math.isfinite(value) or abs(value) > 1.0 for value in window)
    ):
        raise S2LRMaterializationError("PCM sample boundary differs")
    path = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
    state = None
    for hop in range(10):
        state = path.push(window[hop * 480 : (hop + 1) * 480])
    if (
        state is None
        or state.snapshot_index != 0
        or state.window_start_sample != 0
        or state.window_end_sample != 4_800
        or len(state.energy) != 48
    ):
        raise S2LRMaterializationError("auditory receptor endpoint differs")
    return tuple(state.energy)


def _sine_basis(frequency: int) -> tuple[float, ...]:
    return tuple(
        _f32(math.sin((2.0 * math.pi * frequency * index) / 48_000.0))
        for index in range(4_800)
    )


def _square_basis(period: int) -> tuple[float, ...]:
    half = period // 2
    return tuple(1.0 if (index // half) % 2 == 0 else -1.0 for index in range(4_800))


def _scaled_coefficient(target: float, basis_values: tuple[float, ...]) -> float:
    mean = sum(abs(value) for value in basis_values) / len(basis_values)
    if not math.isfinite(mean) or mean <= 0.0:
        raise S2LRMaterializationError("audio basis norm differs")
    return _f32(target / mean)


def _audio_family(role: str) -> tuple[dict[str, tuple[float, ...]], dict[str, object]]:
    spec = _AUDIO_BASES[role]
    center_basis = _square_basis(spec["center_square_period"])
    persistent_basis = _sine_basis(spec["persistent_sine_hz"])
    variation_basis = _sine_basis(spec["variation_sine_hz"])
    center_values = _analyze_audio(center_basis)
    persistent_values = _analyze_audio(persistent_basis)
    variation_values = _analyze_audio(variation_basis)
    center_coefficient = _scaled_coefficient(_AUDIO_TARGETS["center_mean_l1"], center_values)
    persistent_coefficient = _scaled_coefficient(
        _AUDIO_TARGETS["persistent_mean_l1"], persistent_values
    )
    variation_coefficient = _scaled_coefficient(
        _AUDIO_TARGETS["variation_mean_l1"], variation_values
    )
    plus = []
    minus = []
    holdout = []
    for center, persistent, variation in zip(
        center_basis, persistent_basis, variation_basis, strict=True
    ):
        center_term = _f32(center_coefficient * center)
        persistent_term = _f32(persistent_coefficient * persistent)
        variation_term = _f32(variation_coefficient * variation)
        base = _f32(center_term + persistent_term)
        plus.append(_f32(base + variation_term))
        minus.append(_f32(base - variation_term))
        holdout.append(center_term)
    windows = {
        f"{role}_PLUS": tuple(plus),
        f"{role}_MINUS": tuple(minus),
        f"{role}_H": tuple(holdout),
    }
    evidence = {
        "bases": spec,
        "basis_value_digests": {
            "center": _digest(list(center_values)),
            "persistent": _digest(list(persistent_values)),
            "variation": _digest(list(variation_values)),
        },
        "coefficients": {
            "center": center_coefficient,
            "persistent": persistent_coefficient,
            "variation": variation_coefficient,
        },
        "coefficient_f32_hex": {
            "center": struct.pack("<f", center_coefficient).hex(),
            "persistent": struct.pack("<f", persistent_coefficient).hex(),
            "variation": struct.pack("<f", variation_coefficient).hex(),
        },
        "sample_extrema": {
            key: [min(value), max(value)] for key, value in windows.items()
        },
    }
    return windows, evidence


def _pressure_pcm(period: int) -> tuple[float, ...]:
    half = period // 2
    return tuple(
        _f32(0.5 if (index // half) % 2 == 0 else -0.5)
        for index in range(4_800)
    )


def _visual_grid(recipe: str) -> np.ndarray:
    grid = np.zeros((8, 12, 3), dtype=np.uint8)
    flat = grid.reshape(-1)
    if recipe in _VISUAL_RECIPES:
        observed, masked_first, masked_second = _VISUAL_RECIPES[recipe]
        flat[:32] = observed
        flat[32:160] = masked_first
        flat[160:] = masked_second
    elif recipe == "Q09":
        flat[:32] = 128
    elif recipe.startswith("D"):
        ordinal = int(recipe[1:]) + 1
        for index in range(288):
            flat[index] = 255 if (index + ordinal) % 11 in {1, 3, 4, 5, 9} else 0
    else:
        raise S2LRMaterializationError("visual recipe differs")
    return grid


def _visual_image(recipe: str, *, cue: bool = False) -> np.ndarray:
    grid = _visual_grid(recipe)
    if cue:
        grid.reshape(-1)[32:] = 0
    return np.repeat(np.repeat(grid, 135, axis=0), 160, axis=1)


def _analyze_visual(image: np.ndarray, frame_index: int) -> tuple[float, ...]:
    state = LocalChannelGridReceptor(VisualGridConfig()).analyze(image, frame_index=frame_index)
    values = tuple(state.channel_values)
    if len(values) != 288:
        raise S2LRMaterializationError("visual receptor dimension differs")
    return values


def _prototype_chain(
    plus: tuple[float, ...], minus: tuple[float, ...]
) -> tuple[tuple[float, ...], ...]:
    prototype = plus
    result = [prototype]
    for _ in range(6):
        prototype = tuple(
            (1.0 - UPDATE_RATE) * previous + UPDATE_RATE * current
            for previous, current in zip(prototype, minus, strict=True)
        )
        result.append(prototype)
    return tuple(result)


def _relation(name: str, value: bool, details: dict[str, object]) -> dict[str, object]:
    payload = {"name": name, "passed": bool(value), "details": details}
    return {**payload, "relation_digest": _digest(payload)}


def _materialize() -> dict[str, object]:
    f_windows, f_plan = _audio_family("F")
    g_windows, g_plan = _audio_family("G")
    windows = {**f_windows, **g_windows, "W": (0.0,) * 4_800}
    windows.update({
        f"D{index}": _pressure_pcm(period)
        for index, period in enumerate(_PRESSURE_PERIODS, start=1)
    })
    windows["Q10"] = tuple(
        _f32(_f32(0.5 * left) + _f32(0.5 * right))
        for left, right in zip(windows["F_H"], windows["G_H"], strict=True)
    )
    samples_valid = all(
        all(math.isfinite(sample) and abs(sample) <= 1.0 for sample in window)
        for window in windows.values()
    )
    if not samples_valid:
        payload = {
            "schema": SCHEMA,
            "materialization_id": AUTHORIZED_MATERIALIZATION_ID,
            "status": BLOCKED,
            "reason": "PCM_SAMPLE_BOUND_EXCEEDED",
            "fixture_recipe_digest": RECIPE_DIGEST,
            "family_audio_plans": {"F": f_plan, "G": g_plan},
            "receptor_calls": 6,
            "memory_calls": 0,
            "field_calls": 0,
            "context_calls": 0,
            "fixture_searches": 0,
        }
        return {**payload, "result_digest": _digest(payload)}

    audio_values = {role: _analyze_audio(window) for role, window in windows.items()}
    visual_roles = (
        "F_PLUS", "F_MINUS", "F_H", "G_PLUS", "G_MINUS", "G_H", "W",
        "Q07_TARGET", "Q08_TARGET", "Q09",
        "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9",
    )
    visual_images = {
        role: _visual_image(role, cue=role == "Q09") for role in visual_roles
    }
    visual_values = {
        role: _analyze_visual(image, index)
        for index, (role, image) in enumerate(visual_images.items())
    }
    visual_cue_images = {
        "Q01": _visual_image("F_H", cue=True),
        "Q03": _visual_image("G_H", cue=True),
        "Q05": _visual_image("W", cue=True),
        "Q07": _visual_image("Q07_TARGET", cue=True),
        "Q08": _visual_image("Q08_TARGET", cue=True),
        "Q09": _visual_image("Q09", cue=True),
    }
    visual_cues = {
        role: _analyze_visual(image, 100 + index)
        for index, (role, image) in enumerate(visual_cue_images.items())
    }

    f_audio_chain = _prototype_chain(audio_values["F_PLUS"], audio_values["F_MINUS"])
    g_audio_chain = _prototype_chain(audio_values["G_PLUS"], audio_values["G_MINUS"])
    f_visual_chain = _prototype_chain(visual_values["F_PLUS"], visual_values["F_MINUS"])
    g_visual_chain = _prototype_chain(visual_values["G_PLUS"], visual_values["G_MINUS"])
    f_audio_final, g_audio_final = f_audio_chain[-1], g_audio_chain[-1]
    f_visual_final, g_visual_final = f_visual_chain[-1], g_visual_chain[-1]

    relations = []
    for family, values, chain, threshold in (
        ("F_AUDIO", audio_values, f_audio_chain, AUDITORY_SLOW_THRESHOLD),
        ("G_AUDIO", audio_values, g_audio_chain, AUDITORY_SLOW_THRESHOLD),
    ):
        prefix = family[0]
        plus = values[f"{prefix}_PLUS"]
        minus = values[f"{prefix}_MINUS"]
        holdout = values[f"{prefix}_H"]
        distances = {
            "training_pair": _mean_l1(plus, minus),
            "holdout_plus": _mean_l1(holdout, plus),
            "holdout_minus": _mean_l1(holdout, minus),
            "holdout_adaptive": _mean_l1(holdout, chain[-1]),
            "max_update_pre_distance": max(_mean_l1(item, minus) for item in chain[:-1]),
        }
        relations.append(_relation(
            f"{family}_HOLDOUT_AND_UPDATE",
            distances["training_pair"] <= threshold
            and distances["holdout_plus"] > threshold
            and distances["holdout_minus"] > threshold
            and distances["holdout_adaptive"] <= threshold
            and distances["max_update_pre_distance"] <= threshold,
            distances,
        ))
    for family, values, chain in (
        ("F_VISUAL", visual_values, f_visual_chain),
        ("G_VISUAL", visual_values, g_visual_chain),
    ):
        prefix = family[0]
        plus = values[f"{prefix}_PLUS"]
        minus = values[f"{prefix}_MINUS"]
        holdout = values[f"{prefix}_H"]
        distances = {
            "training_pair": _mean_l1(plus, minus),
            "holdout_plus": _mean_l1(holdout, plus),
            "holdout_minus": _mean_l1(holdout, minus),
            "holdout_adaptive": _mean_l1(holdout, chain[-1]),
            "max_update_pre_distance": max(_mean_l1(item, minus) for item in chain[:-1]),
        }
        relations.append(_relation(
            f"{family}_HOLDOUT_AND_UPDATE",
            distances["training_pair"] <= VISUAL_SLOW_THRESHOLD
            and distances["holdout_plus"] > VISUAL_SLOW_THRESHOLD
            and distances["holdout_minus"] > VISUAL_SLOW_THRESHOLD
            and distances["holdout_adaptive"] <= VISUAL_SLOW_THRESHOLD
            and distances["max_update_pre_distance"] <= VISUAL_SLOW_THRESHOLD,
            distances,
        ))

    cross_audio = [
        _mean_l1(left, right)
        for left in (*f_audio_chain, audio_values["F_PLUS"], audio_values["F_MINUS"])
        for right in (*g_audio_chain, audio_values["G_PLUS"], audio_values["G_MINUS"])
    ]
    cross_visual = [
        _mean_l1(left, right)
        for left in (*f_visual_chain, visual_values["F_PLUS"], visual_values["F_MINUS"])
        for right in (*g_visual_chain, visual_values["G_PLUS"], visual_values["G_MINUS"])
    ]
    relations.append(_relation(
        "F_G_TRAINING_AND_PROTOTYPE_SEPARATION",
        min(cross_audio) > AUDITORY_SLOW_THRESHOLD
        and min(cross_visual) > FAST_THRESHOLD,
        {
            "minimum_auditory_slow_separation": min(cross_audio),
            "minimum_visual_slow_separation": min(cross_visual),
            "minimum_visual_fast_separation": min(cross_visual),
        },
    ))
    holdout_cross = {
        "f_holdout_to_g_audio": _mean_l1(audio_values["F_H"], g_audio_final),
        "g_holdout_to_f_audio": _mean_l1(audio_values["G_H"], f_audio_final),
        "f_holdout_to_g_visual": _mean_l1(visual_values["F_H"], g_visual_final),
        "g_holdout_to_f_visual": _mean_l1(visual_values["G_H"], f_visual_final),
    }
    relations.append(_relation(
        "HOLDOUT_FAMILY_SELECTIVITY",
        holdout_cross["f_holdout_to_g_audio"] > AUDITORY_SLOW_THRESHOLD
        and holdout_cross["g_holdout_to_f_audio"] > AUDITORY_SLOW_THRESHOLD
        and holdout_cross["f_holdout_to_g_visual"] > VISUAL_SLOW_THRESHOLD
        and holdout_cross["g_holdout_to_f_visual"] > VISUAL_SLOW_THRESHOLD,
        holdout_cross,
    ))

    q_audio = {
        "q02_f": _mean_l1(audio_values["F_H"], f_audio_final, OBSERVED_AUDIO),
        "q02_g": _mean_l1(audio_values["F_H"], g_audio_final, OBSERVED_AUDIO),
        "q04_g": _mean_l1(audio_values["G_H"], g_audio_final, OBSERVED_AUDIO),
        "q04_f": _mean_l1(audio_values["G_H"], f_audio_final, OBSERVED_AUDIO),
        "q10_f": _mean_l1(audio_values["Q10"], f_audio_final, OBSERVED_AUDIO),
        "q10_g": _mean_l1(audio_values["Q10"], g_audio_final, OBSERVED_AUDIO),
        "f_g": _mean_l1(f_audio_final, g_audio_final, OBSERVED_AUDIO),
        "q10_masked_fg_distance": _mean_l1(f_audio_final, g_audio_final, MASKED_AUDIO),
        "q06_f": _mean_l1(audio_values["W"], f_audio_final, OBSERVED_AUDIO),
        "q06_g": _mean_l1(audio_values["W"], g_audio_final, OBSERVED_AUDIO),
    }
    pressure_audio_values = tuple(audio_values[f"D{index}"] for index in range(1, 10))
    pressure_cue_distances = {
        cue_name: [
            _mean_l1(pressure, cue, OBSERVED_AUDIO)
            for pressure in pressure_audio_values
        ]
        for cue_name, cue in {
            "q02": audio_values["F_H"],
            "q04": audio_values["G_H"],
            "q06": audio_values["W"],
            "q10": audio_values["Q10"],
        }.items()
    }
    relations.append(_relation(
        "AUDITORY_Q02_Q04_Q06_Q10",
        q_audio["q02_f"] <= AUDITORY_SLOW_THRESHOLD < q_audio["q02_g"]
        and q_audio["q04_g"] <= AUDITORY_SLOW_THRESHOLD < q_audio["q04_f"]
        and AUDITORY_SLOW_THRESHOLD < q_audio["f_g"] <= 2 * AUDITORY_SLOW_THRESHOLD
        and q_audio["q10_f"] <= AUDITORY_SLOW_THRESHOLD
        and q_audio["q10_g"] <= AUDITORY_SLOW_THRESHOLD
        and q_audio["q10_masked_fg_distance"] > 0.0
        and q_audio["q06_f"] > AUDITORY_SLOW_THRESHOLD
        and q_audio["q06_g"] > AUDITORY_SLOW_THRESHOLD
        and min(
            distance
            for distances in pressure_cue_distances.values()
            for distance in distances
        ) > FAST_THRESHOLD,
        {**q_audio, "pressure_cue_distances": pressure_cue_distances},
    ))

    def exact_observed(candidate: tuple[float, ...], cue: tuple[float, ...]) -> bool:
        return all(candidate[index] == cue[index] for index in OBSERVED_VISUAL)

    q_visual = {
        "q01_f": exact_observed(f_visual_final, visual_cues["Q01"]),
        "q01_g": exact_observed(g_visual_final, visual_cues["Q01"]),
        "q03_f": exact_observed(f_visual_final, visual_cues["Q03"]),
        "q03_g": exact_observed(g_visual_final, visual_cues["Q03"]),
        "q05_f": exact_observed(f_visual_final, visual_cues["Q05"]),
        "q05_g": exact_observed(g_visual_final, visual_cues["Q05"]),
        "q07_f": exact_observed(f_visual_final, visual_cues["Q07"]),
        "q07_g": exact_observed(g_visual_final, visual_cues["Q07"]),
        "q08_f": exact_observed(f_visual_final, visual_cues["Q08"]),
        "q08_g": exact_observed(g_visual_final, visual_cues["Q08"]),
        "q09_f": exact_observed(f_visual_final, visual_cues["Q09"]),
        "q09_g": exact_observed(g_visual_final, visual_cues["Q09"]),
        "q07_full_distance": _mean_l1(visual_values["Q07_TARGET"], f_visual_final),
        "q08_full_distance": _mean_l1(visual_values["Q08_TARGET"], f_visual_final),
    }
    q_visual["q07_inside_reserve"] = VISUAL_SLOW_THRESHOLD - q_visual["q07_full_distance"]
    q_visual["q08_outside_reserve"] = q_visual["q08_full_distance"] - VISUAL_SLOW_THRESHOLD
    pressure_values = tuple(visual_values[f"D{index}"] for index in range(1, 10))
    pressure_cue_matches = {
        cue_name: sum(exact_observed(pressure, cue) for pressure in pressure_values)
        for cue_name, cue in visual_cues.items()
    }
    relations.append(_relation(
        "VISUAL_Q01_Q03_Q05_Q07_Q08_Q09",
        q_visual["q01_f"] and not q_visual["q01_g"]
        and q_visual["q03_g"] and not q_visual["q03_f"]
        and not q_visual["q05_f"] and not q_visual["q05_g"]
        and q_visual["q07_f"] and not q_visual["q07_g"]
        and not q_visual["q08_f"] and not q_visual["q08_g"]
        and not q_visual["q09_f"] and not q_visual["q09_g"]
        and q_visual["q07_inside_reserve"] > 0.0
        and q_visual["q08_outside_reserve"] > 0.0
        and all(count == 0 for count in pressure_cue_matches.values()),
        {**q_visual, "pressure_observed_matches": pressure_cue_matches},
    ))

    training_visual = tuple(
        visual_values[role] for role in ("F_PLUS", "F_MINUS", "G_PLUS", "G_MINUS", "W")
    )
    pressure_pair_distances = [
        _mean_l1(pressure_values[left], pressure_values[right])
        for left in range(9) for right in range(left + 1, 9)
    ]
    pressure_training_distances = [
        _mean_l1(pressure, training)
        for pressure in pressure_values for training in training_visual
    ]
    auditory_family_and_weak = (
        *f_audio_chain,
        *g_audio_chain,
        audio_values["F_PLUS"],
        audio_values["F_MINUS"],
        audio_values["G_PLUS"],
        audio_values["G_MINUS"],
        audio_values["W"],
    )
    pressure_audio_pair_distances = [
        _mean_l1(pressure_audio_values[left], pressure_audio_values[right])
        for left in range(9) for right in range(left + 1, 9)
    ]
    pressure_audio_training_distances = [
        _mean_l1(pressure, training)
        for pressure in pressure_audio_values
        for training in auditory_family_and_weak
    ]
    relations.append(_relation(
        "PRESSURE_FAST_AND_SLOW_SEPARATION",
        min(pressure_pair_distances) > FAST_THRESHOLD
        and min(pressure_training_distances) > FAST_THRESHOLD
        and min(pressure_audio_pair_distances) > AUDITORY_SLOW_THRESHOLD
        and min(pressure_audio_training_distances) > AUDITORY_SLOW_THRESHOLD,
        {
            "minimum_pressure_pair_visual": min(pressure_pair_distances),
            "minimum_pressure_training_visual": min(pressure_training_distances),
            "minimum_pressure_pair_auditory": min(pressure_audio_pair_distances),
            "minimum_pressure_training_auditory": min(pressure_audio_training_distances),
            "pressure_count": 9,
        },
    ))

    w_auditory_distances = [
        _mean_l1(audio_values["W"], candidate)
        for candidate in (*f_audio_chain, *g_audio_chain)
    ]
    w_visual_distances = [
        _mean_l1(visual_values["W"], candidate)
        for candidate in (*f_visual_chain, *g_visual_chain)
    ]
    w_distances = {
        "minimum_auditory_family": min(w_auditory_distances),
        "minimum_visual_family": min(w_visual_distances),
    }
    relations.append(_relation(
        "WEAK_TRACE_SEPARATION",
        w_distances["minimum_auditory_family"] > AUDITORY_SLOW_THRESHOLD
        and w_distances["minimum_visual_family"] > VISUAL_SLOW_THRESHOLD,
        w_distances,
    ))

    passed = all(item["passed"] for item in relations)
    reason = None if passed else next(item["name"] for item in relations if not item["passed"])
    payload = {
        "schema": SCHEMA,
        "materialization_id": AUTHORIZED_MATERIALIZATION_ID,
        "status": SUCCESS if passed else BLOCKED,
        "reason": reason,
        "fixture_recipe_digest": RECIPE_DIGEST,
        "formation_count": len(FORMATION_SEQUENCE),
        "training_role_counts": {
            "F": sum(role.startswith("F_") for role in FORMATION_SEQUENCE),
            "G": sum(role.startswith("G_") for role in FORMATION_SEQUENCE),
            "W": FORMATION_SEQUENCE.count("W"),
            "pressure": sum(role.startswith("D") for role in FORMATION_SEQUENCE),
        },
        "family_audio_plans": {"F": f_plan, "G": g_plan},
        "audio_fixture_digests": {
            role: {"pcm": _pcm_digest(window), "values": _digest(list(audio_values[role]))}
            for role, window in windows.items()
        },
        "visual_fixture_digests": {
            role: {
                "rgb": hashlib.sha256(visual_images[role].tobytes(order="C")).hexdigest(),
                "values": _digest(list(visual_values[role])),
            }
            for role in visual_roles
        },
        "visual_cue_digests": {
            role: {
                "rgb": hashlib.sha256(image.tobytes(order="C")).hexdigest(),
                "values": _digest(list(visual_cues[role])),
            }
            for role, image in visual_cue_images.items()
        },
        "prototype_digests": {
            "F_AUDITORY": [_digest(list(value)) for value in f_audio_chain],
            "G_AUDITORY": [_digest(list(value)) for value in g_audio_chain],
            "F_VISUAL": [_digest(list(value)) for value in f_visual_chain],
            "G_VISUAL": [_digest(list(value)) for value in g_visual_chain],
        },
        "relations": relations,
        "source_counts": {
            "audio_basis_endpoints": 6,
            "audio_fixture_endpoints": len(audio_values),
            "visual_fixture_endpoints": len(visual_values),
            "visual_cue_endpoints": len(visual_cues),
        },
        "raw_payload_retained": False,
        "receptor_calls": 6 + len(audio_values) + len(visual_values) + len(visual_cues),
        "memory_calls": 0,
        "field_calls": 0,
        "context_calls": 0,
        "fixture_searches": 0,
        "parameter_adjustments": 0,
    }
    return {**payload, "result_digest": _digest(payload)}


def run_materialization_once(*, output_root: Path, materialization_id: str) -> Path:
    global MATERIALIZATION_ENABLED, _USED
    if MATERIALIZATION_ENABLED is not True:
        raise S2LRMaterializationError("materialization gate is closed")
    if materialization_id != AUTHORIZED_MATERIALIZATION_ID:
        raise S2LRMaterializationError("materialization id is not authorized")
    if _USED or not _LOCK.acquire(blocking=False):
        raise S2LRMaterializationError("materialization is consumed")
    _USED = True
    try:
        result = _materialize()
        target_dir = output_root / materialization_id
        target_dir.mkdir(parents=True, exist_ok=False)
        target = target_dir / "materialization.json"
        temporary = target_dir / ".materialization.json.tmp"
        temporary.write_bytes(_canonical_bytes(result, newline=True))
        temporary.replace(target)
        return target
    finally:
        MATERIALIZATION_ENABLED = False
        _LOCK.release()


assert len(FORMATION_SEQUENCE) == 28
assert sum(role.startswith("F_") for role in FORMATION_SEQUENCE) == 8
assert sum(role.startswith("G_") for role in FORMATION_SEQUENCE) == 8
assert FORMATION_SEQUENCE.count("W") == 3
assert sum(role.startswith("D") for role in FORMATION_SEQUENCE) == 9

__all__: tuple[str, ...] = ()
