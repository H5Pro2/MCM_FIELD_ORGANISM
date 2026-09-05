"""One receptor-only compatibility audit for the presealed S2-MT audio corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

import numpy as np

from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from tools import _s2mt_private_presealed_transfer_sources as sources


AUDIT_SCHEMA = "s2mw.private.audio-receptor-compatibility-audit.v1"
AUDIT_ID = "s2mw-audio-receptor-compatibility-20260905-01"
SOURCE_SHA256 = "ae808ad2a9f206bac45210f5f121e232e72da76b22e0b2bf7c599cc57e479f15"
RECEPTOR_SHA256 = "26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0"
SLOW_THRESHOLD = 0.02
FAST_THRESHOLD = 0.2
OBSERVED_BANDS = tuple(range(24))
TRAINING_RECIPES = ("n00", "n01", "n02")
AUDITORY_CUE_RECIPES = ("n00", "n01", "n02", "n12")
EXPECTED_CUE_MATCHES = {
    "n00": ("n00",),
    "n01": ("n01",),
    "n02": ("n02",),
    "n12": (),
}


class S2MWAuditError(RuntimeError):
    """The receptor-only audit cannot produce a valid result."""


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return encoded + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MWAuditError(message)


def _distance(first: tuple[float, ...], second: tuple[float, ...]) -> float:
    _require(len(first) == len(second) and len(first) > 0, "distance dimensions differ")
    return math.fsum(abs(left - right) for left, right in zip(first, second, strict=True)) / len(first)


def _values_digest(values: tuple[float, ...]) -> str:
    return hashlib.sha256(np.asarray(values, dtype="<f8").tobytes(order="C")).hexdigest()


def _f32_hex(value: float) -> str:
    return struct.pack("<f", value).hex()


def _analyze(
    receptor: LogSpectralReceptor,
    samples: tuple[float, ...],
) -> tuple[float, ...]:
    values = receptor.analyze(samples)
    _require(len(values) == 48, "receptor output dimension differs")
    _require(all(math.isfinite(value) and value >= 0.0 for value in values), "receptor output is invalid")
    return values


def _recipe_projection(
    recipe_id: str,
    frequency_hz: int,
    input_digest: str,
    values: tuple[float, ...],
    channel_ids: tuple[str, ...],
) -> dict[str, object]:
    maximum = max(values)
    maximum_bands = tuple(index for index, value in enumerate(values) if value == maximum)
    exceeded = tuple(index for index, value in enumerate(values) if value > 1.0)
    return {
        "recipe_id": recipe_id,
        "frequency_hz": frequency_hz,
        "input_digest": input_digest,
        "receptor_values": list(values),
        "receptor_values_digest": _values_digest(values),
        "maximum": maximum,
        "maximum_bands": [
            {"index": index, "channel_id": channel_ids[index], "value": values[index]}
            for index in maximum_bands
        ],
        "bands_over_one": [
            {"index": index, "channel_id": channel_ids[index], "value": values[index]}
            for index in exceeded
        ],
        "within_receptor_contact_domain": not exceeded,
    }


def _pairwise_distances(
    original: dict[str, tuple[float, ...]],
    scaled: dict[str, tuple[float, ...]],
) -> list[dict[str, object]]:
    result = []
    recipe_ids = tuple(sources.RECIPE_IDS)
    for left_index, left in enumerate(recipe_ids):
        for right in recipe_ids[left_index + 1 :]:
            original_distance = _distance(original[left], original[right])
            scaled_distance = _distance(scaled[left], scaled[right])
            result.append(
                {
                    "left": left,
                    "right": right,
                    "original_full_48_distance": original_distance,
                    "scaled_full_48_distance": scaled_distance,
                    "scaled_within_slow_threshold": scaled_distance <= SLOW_THRESHOLD,
                    "scaled_within_fast_threshold": scaled_distance <= FAST_THRESHOLD,
                }
            )
    _require(len(result) == 78, "pairwise distance count differs")
    return result


def _cue_distances(values: dict[str, tuple[float, ...]]) -> list[dict[str, object]]:
    result = []
    for cue_recipe in AUDITORY_CUE_RECIPES:
        cue = tuple(values[cue_recipe][index] for index in OBSERVED_BANDS)
        matches = []
        distances = {}
        for candidate_recipe in TRAINING_RECIPES:
            candidate = tuple(values[candidate_recipe][index] for index in OBSERVED_BANDS)
            distance = _distance(cue, candidate)
            distances[candidate_recipe] = distance
            if distance <= SLOW_THRESHOLD:
                matches.append(candidate_recipe)
        result.append(
            {
                "cue_recipe_id": cue_recipe,
                "observed_band_count": len(OBSERVED_BANDS),
                "distances": distances,
                "matching_training_recipes": matches,
                "expected_matching_training_recipes": list(EXPECTED_CUE_MATCHES[cue_recipe]),
                "matches_expectation": tuple(matches) == EXPECTED_CUE_MATCHES[cue_recipe],
            }
        )
    _require(len(result) == 4, "auditory cue distance count differs")
    return result


def _atomic_write(path: Path, payload: dict[str, object]) -> None:
    _require(not path.exists(), "audit result already exists")
    path.parent.mkdir(parents=True, exist_ok=False)
    temporary = path.with_suffix(".tmp")
    temporary.write_bytes(_canonical_bytes(payload, newline=True))
    temporary.replace(path)


def run_audit(output_path: Path) -> dict[str, object]:
    workspace = Path(__file__).resolve().parents[1]
    source_path = workspace / "tools" / "_s2mt_private_presealed_transfer_sources.py"
    receptor_path = workspace / "mcm_field_organism" / "log_spectral_receptor.py"
    source_hash = _file_sha256(source_path)
    receptor_hash = _file_sha256(receptor_path)
    _require(source_hash == SOURCE_SHA256, "presealed source module differs")
    _require(receptor_hash == RECEPTOR_SHA256, "audio receptor module differs")

    plan = sources.build_presealed_plan()
    config = LogSpectralConfig()
    receptor = LogSpectralReceptor(config)
    _require(tuple(sources.RECIPE_IDS) == tuple(item.recipe_id for item in plan.recipes), "recipe order differs")

    original_samples: dict[str, tuple[float, ...]] = {}
    original_values: dict[str, tuple[float, ...]] = {}
    original_records = []
    for recipe in plan.recipes:
        samples = sources.verified_audio_window(plan, recipe.recipe_id)
        input_digest = hashlib.sha256(np.asarray(samples, dtype="<f4").tobytes(order="C")).hexdigest()
        _require(input_digest == recipe.auditory_payload_digest, "original audio digest differs")
        values = _analyze(receptor, samples)
        original_samples[recipe.recipe_id] = samples
        original_values[recipe.recipe_id] = values
        original_records.append(
            _recipe_projection(
                recipe.recipe_id,
                recipe.audio_frequency_hz,
                input_digest,
                values,
                receptor.channel_ids,
            )
        )

    global_maximum = max(max(values) for values in original_values.values())
    _require(global_maximum > 1.0, "original receptor outputs unexpectedly fit the contact domain")
    reciprocal_f32 = np.float32(1.0 / global_maximum)
    factor_f32 = np.nextafter(reciprocal_f32, np.float32(0.0), dtype=np.float32)
    factor = float(factor_f32)
    _require(0.0 < factor < 1.0, "derived common input factor is invalid")

    scaled_values: dict[str, tuple[float, ...]] = {}
    scaled_records = []
    for recipe in plan.recipes:
        original = np.asarray(original_samples[recipe.recipe_id], dtype="<f4")
        scaled_array = np.multiply(original, factor_f32, dtype=np.float32)
        _require(np.all(np.isfinite(scaled_array)) and np.all(np.abs(scaled_array) <= 1.0), "scaled PCM is invalid")
        scaled_samples = tuple(float(value) for value in scaled_array)
        scaled_input_digest = hashlib.sha256(scaled_array.astype("<f4", copy=False).tobytes(order="C")).hexdigest()
        values = _analyze(receptor, scaled_samples)
        scaled_values[recipe.recipe_id] = values
        scaled_records.append(
            _recipe_projection(
                recipe.recipe_id,
                recipe.audio_frequency_hz,
                scaled_input_digest,
                values,
                receptor.channel_ids,
            )
        )

    pairwise = _pairwise_distances(original_values, scaled_values)
    cue_distances = _cue_distances(scaled_values)
    first_three_pairs = tuple(
        item
        for item in pairwise
        if item["left"] in TRAINING_RECIPES and item["right"] in TRAINING_RECIPES
    )
    normalized = all(record["within_receptor_contact_domain"] for record in scaled_records)
    training_slow_separated = len(first_three_pairs) == 3 and all(
        item["scaled_full_48_distance"] > SLOW_THRESHOLD for item in first_three_pairs
    )
    cue_geometry_preserved = all(item["matches_expectation"] for item in cue_distances)
    materializable = normalized and training_slow_separated and cue_geometry_preserved

    config_payload = {
        "sample_rate": config.sample_rate,
        "window_size": config.window_size,
        "hop_size": config.hop_size,
        "min_frequency": config.min_frequency,
        "max_frequency": config.max_frequency,
        "band_count": config.band_count,
        "channel_ids": list(receptor.channel_ids),
    }
    payload: dict[str, object] = {
        "schema": AUDIT_SCHEMA,
        "audit_id": AUDIT_ID,
        "technical_status": (
            "S2MT_AUDIO_RECEPTOR_COMPATIBILITY_MATERIALIZABLE"
            if materializable
            else "S2MT_AUDIO_RECEPTOR_COMPATIBILITY_NOT_MATERIALIZABLE"
        ),
        "source_bindings": {
            "source_module_sha256": source_hash,
            "receptor_module_sha256": receptor_hash,
            "presealed_plan_digest": plan.plan_digest,
            "original_audio_payload_digests": {
                item.recipe_id: item.auditory_payload_digest for item in plan.recipes
            },
            "receptor_config": config_payload,
            "receptor_config_digest": _digest(config_payload),
        },
        "execution_bounds": {
            "recipe_count": len(plan.recipes),
            "original_receptor_analyses": len(original_records),
            "derived_factor_count": 1,
            "scaled_receptor_analyses": len(scaled_records),
            "memory_calls": 0,
            "field_calls": 0,
            "context_calls": 0,
            "runtime_calls": 0,
        },
        "original_outputs": original_records,
        "global_original_maximum": global_maximum,
        "common_input_scaling": {
            "derivation": "nextafter(float32(1/global_original_maximum),float32(0))",
            "factor": factor,
            "factor_float32_le_hex": _f32_hex(factor),
            "sample_operation": "float32(original_sample)*float32(factor)->float32",
            "clipping": False,
            "output_normalization": False,
        },
        "scaled_outputs": scaled_records,
        "distances": {
            "slow_threshold": SLOW_THRESHOLD,
            "fast_threshold": FAST_THRESHOLD,
            "observed_bands": list(OBSERVED_BANDS),
            "all_recipe_pairs": pairwise,
            "bound_auditory_cues": cue_distances,
        },
        "decision": {
            "all_scaled_outputs_within_contact_domain": normalized,
            "first_three_training_recipes_slow_separated": training_slow_separated,
            "bound_auditory_cue_geometry_preserved": cue_geometry_preserved,
            "common_factor_satisfies_normal_form_and_audio_geometry": materializable,
            "third_transfer_run_authorized": False,
        },
    }
    payload["record_digest"] = _digest(payload)
    _atomic_write(output_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_audit(args.output.resolve())
    print(
        json.dumps(
            {
                "audit_id": result["audit_id"],
                "technical_status": result["technical_status"],
                "record_digest": result["record_digest"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__: tuple[str, ...] = ()
