"""One-shot receptor-only materialization of the sealed S2-LB D_FAR role."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
from typing import Any

import numpy as np

from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor


PLAN_PATH = Path("docs/S2LB_D_FAR_PCM_MATERIALISIERUNGSPLAN.json")
OUTPUT_ROOT = Path("reports/s2kx/s2lb-d-far-pcm-materialization-20260904-01")
OUTPUT_PATH = OUTPUT_ROOT / "materialization.json"
SUCCESS = "S2LB_D_FAR_PCM_MATERIALIZED"
BLOCKED = "S2LB_D_FAR_PCM_NOT_MATERIALIZABLE"


class S2LBMaterializationError(ValueError):
    """The sealed one-role plan or its source bindings are invalid."""


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def _git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _load_plan() -> dict[str, Any]:
    plan = json.loads(PLAN_PATH.read_text(encoding="ascii"))
    if not isinstance(plan, dict):
        raise S2LBMaterializationError("plan must be an object")
    if plan.get("schema") != "s2lb.d-far-pcm-materialization-plan.v1":
        raise S2LBMaterializationError("plan schema differs")
    if (
        plan.get("role") != "D_FAR"
        or plan.get("success_status") != SUCCESS
        or plan.get("failure_status") != BLOCKED
    ):
        raise S2LBMaterializationError("plan role or status differs")
    expected_limits = {
        "materialization_calls": 1,
        "pcm_windows": 1,
        "audio_hops": 10,
        "receptor_endpoints": 1,
        "distance_pairs": 2,
        "visual_target_relations": 9,
        "visual_companion_relations": 36,
        "memory_calls": 0,
        "slotscan_calls": 0,
        "context_calls": 0,
        "field_calls": 0,
        "parameter_searches": 0,
        "replacement_fixtures": 0,
    }
    if plan.get("execution_limits") != expected_limits:
        raise S2LBMaterializationError("execution limits differ")
    return plan


def _validate_sources(plan: dict[str, Any]) -> dict[str, str]:
    bindings = plan["source_bindings"]
    paths = {
        "s2ky_materialization": Path(bindings["s2ky_materialization_path"]),
        "visual_fixture_source": Path(bindings["visual_fixture_source_path"]),
        "receptor_source": Path("mcm_field_organism/log_spectral_receptor.py"),
        "hearing_path_source": Path("mcm_field_organism/broadband_hearing_path.py"),
    }
    actual = {role: _file_digest(path) for role, path in paths.items()}
    expected = {
        "s2ky_materialization": bindings["s2ky_materialization_sha256"],
        "visual_fixture_source": bindings["visual_fixture_source_sha256"],
        "receptor_source": bindings["receptor_source_sha256"],
        "hearing_path_source": bindings["hearing_path_source_sha256"],
    }
    if actual != expected:
        raise S2LBMaterializationError("source digest binding differs")
    return actual


def _materialize_pcm(plan: dict[str, Any]) -> tuple[float, ...]:
    recipe = plan["recipe"]
    expected = {
        "waveform": "logarithmic-square-chirp",
        "start_frequency_hz": 50.0,
        "end_frequency_hz": 890.0,
        "duration_seconds": 0.1,
        "initial_phase_radians_formula": "pi/7",
        "instantaneous_frequency_formula": "f0*(f1/f0)^(t/T)",
        "phase_formula": "pi/7 + 2*pi*f0*T/log(f1/f0)*((f1/f0)^(t/T)-1)",
        "sample_formula": "float32(scale if sin(phase(n/48000)) >= 0 else -scale)",
        "scale_float32": 0.9800000190734863,
        "clipping": False,
        "normalization": False,
    }
    if recipe != expected:
        raise S2LBMaterializationError("sealed PCM recipe differs")
    f0 = recipe["start_frequency_hz"]
    f1 = recipe["end_frequency_hz"]
    duration = recipe["duration_seconds"]
    ratio = f1 / f0
    phase_scale = 2.0 * math.pi * f0 * duration / math.log(ratio)
    initial_phase = math.pi / 7.0
    scale = _f32(recipe["scale_float32"])
    samples = []
    for index in range(4_800):
        t = index / 48_000.0
        phase = initial_phase + phase_scale * (ratio ** (t / duration) - 1.0)
        samples.append(_f32(scale if math.sin(phase) >= 0.0 else -scale))
    result = tuple(samples)
    if (
        len(result) != 4_800
        or min(result) != -scale
        or max(result) != scale
        or any(not math.isfinite(value) or abs(value) > 1.0 for value in result)
    ):
        raise S2LBMaterializationError("PCM sample bounds differ")
    return result


def _analyze_pcm(samples: tuple[float, ...]) -> dict[str, object]:
    path = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
    state = None
    outputs = 0
    for hop in range(10):
        state = path.push(samples[hop * 480 : (hop + 1) * 480])
        outputs += int(state is not None)
    if (
        state is None
        or outputs != 1
        or path.input_chunks != 10
        or path.snapshot_count != 1
        or state.snapshot_index != 0
        or state.window_start_sample != 0
        or state.window_end_sample != 4_800
        or len(state.energy) != 48
        or any(not math.isfinite(value) for value in state.energy)
    ):
        raise S2LBMaterializationError("auditory receptor endpoint differs")
    values = tuple(state.energy)
    return {
        "pcm_sha256": hashlib.sha256(np.asarray(samples, dtype="<f4").tobytes()).hexdigest(),
        "pcm_min": min(samples),
        "pcm_max": max(samples),
        "receptor_state_digest": state.digest(),
        "values_digest": _digest(list(values)),
        "values": list(values),
        "input_hops": 10,
        "output_snapshots": 1,
    }


def _mean_l1(left: list[float], right: list[float], indices: tuple[int, ...]) -> float:
    return sum(abs(left[index] - right[index]) for index in indices) / len(indices)


def _distance_evidence(
    plan: dict[str, Any],
    d_values: list[float],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    source_path = Path(plan["source_bindings"]["s2ky_materialization_path"])
    source = json.loads(source_path.read_text(encoding="ascii"))
    if source.get("status") != plan["source_bindings"]["s2ky_required_status"]:
        raise S2LBMaterializationError("S2-KY source status differs")
    observed = tuple(plan["profile"]["observed_bands"])
    full = tuple(range(48))
    results = []
    for gate in plan["distance_gates"]:
        reference = gate["reference"]
        reference_values = source["measurements"][reference]["values"]
        observed_distance = _mean_l1(d_values, reference_values, observed)
        full_distance = _mean_l1(d_values, reference_values, full)
        payload = {
            "left": "D_FAR",
            "right": reference,
            "observed_mean_l1_24": observed_distance,
            "full_mean_l1_48": full_distance,
            "minimum_exclusive": gate["minimum_exclusive"],
            "fast_threshold": plan["profile"]["fast_auditory_threshold"],
            "safety_margin_over_fast_threshold": observed_distance
            - plan["profile"]["fast_auditory_threshold"],
            "passed": observed_distance > gate["minimum_exclusive"],
        }
        results.append({**payload, "pair_digest": _digest(payload)})
    source_projection = {
        "schema": source["schema"],
        "run_id": source["run_id"],
        "status": source["status"],
        "result_digest": source["result_digest"],
        "cue_low_values_digest": source["measurements"]["CUE_LOW"]["values_digest"],
        "candidate_high_values_digest": source["measurements"]["CANDIDATE_HIGH"]["values_digest"],
    }
    return results, {**source_projection, "projection_digest": _digest(source_projection)}


def _visual_values(ordinal: int) -> tuple[float, ...]:
    active = {1, 3, 4, 5, 9}
    return tuple(1.0 if (index + ordinal) % 11 in active else 0.0 for index in range(288))


def _visual_pressure_evidence(plan: dict[str, Any]) -> dict[str, object]:
    pressure = plan["visual_pressure"]
    if (
        pressure["target_ordinal"] != 0
        or pressure["companion_ordinals"] != list(range(2, 11))
        or pressure["active_residues"] != [1, 3, 4, 5, 9]
        or pressure["modulus"] != 11
        or pressure["dimension"] != 288
    ):
        raise S2LBMaterializationError("visual pressure binding differs")
    target = _visual_values(0)
    companions = {
        role: _visual_values(ordinal)
        for role, ordinal in zip(
            pressure["companion_roles"], pressure["companion_ordinals"], strict=True
        )
    }
    target_relations = []
    for role, values in companions.items():
        distance = _mean_l1(list(target), list(values), tuple(range(288)))
        payload = {
            "left": "X",
            "right": role,
            "auditory_distance": None,
            "visual_distance": distance,
            "native_fast_match": False,
            "passed": distance > pressure["minimum_visual_distance_exclusive"],
        }
        target_relations.append({**payload, "relation_digest": _digest(payload)})
    companion_relations = []
    roles = tuple(companions)
    for left_index, left in enumerate(roles):
        for right in roles[left_index + 1 :]:
            distance = _mean_l1(
                list(companions[left]), list(companions[right]), tuple(range(288))
            )
            native_match = (
                0.0 <= plan["profile"]["fast_auditory_threshold"]
                and distance <= plan["profile"]["fast_visual_threshold"]
            )
            payload = {
                "left": left,
                "right": right,
                "auditory_distance": 0.0,
                "visual_distance": distance,
                "native_fast_match": native_match,
                "passed": not native_match,
            }
            companion_relations.append({**payload, "relation_digest": _digest(payload)})
    return {
        "target_values_digest": _digest(list(target)),
        "companion_value_digests": {
            role: _digest(list(values)) for role, values in companions.items()
        },
        "target_relations": target_relations,
        "companion_relations": companion_relations,
        "minimum_target_distance": min(item["visual_distance"] for item in target_relations),
        "minimum_companion_distance": min(
            item["visual_distance"] for item in companion_relations
        ),
        "all_nine_pressure_formations_separate": all(
            item["passed"] for item in target_relations + companion_relations
        ),
    }


def _write_once(payload: dict[str, object]) -> None:
    OUTPUT_ROOT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_ROOT.mkdir(exist_ok=False)
    temporary = OUTPUT_ROOT / "materialization.json.tmp"
    with temporary.open("xb") as handle:
        handle.write(_json_bytes(payload) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, OUTPUT_PATH)


def materialize_once() -> dict[str, object]:
    plan = _load_plan()
    source_hashes = _validate_sources(plan)
    samples = _materialize_pcm(plan)
    measurement = _analyze_pcm(samples)
    values = measurement["values"]
    if not isinstance(values, list):
        raise S2LBMaterializationError("D_FAR receptor values missing")
    distance_evidence, source_projection = _distance_evidence(plan, values)
    visual_pressure = _visual_pressure_evidence(plan)
    passed = all(item["passed"] for item in distance_evidence) and bool(
        visual_pressure["all_nine_pressure_formations_separate"]
    )
    status = SUCCESS if passed else BLOCKED
    body: dict[str, object] = {
        "schema": "s2lb.d-far-pcm-materialization-result.v1",
        "run_id": plan["run_id"],
        "status": status,
        "source_commit": _git_head(),
        "plan_sha256": _file_digest(PLAN_PATH),
        "source_hashes": source_hashes,
        "role": "D_FAR",
        "profile": plan["profile"],
        "recipe": plan["recipe"],
        "measurement": measurement,
        "reference_source": source_projection,
        "distance_evidence": distance_evidence,
        "visual_pressure_evidence": visual_pressure,
        "raw_pcm_retained": False,
        "counters": plan["execution_limits"],
    }
    body["result_digest"] = _digest(body)
    _write_once(body)
    return body


def main() -> int:
    try:
        result = materialize_once()
    except Exception as exc:
        print(f"S2LB_EXECUTION_ERROR:{type(exc).__name__}", file=sys.stderr)
        return 2
    print(result["status"])
    print(result["result_digest"])
    return 0 if result["status"] == SUCCESS else 1


if __name__ == "__main__":
    raise SystemExit(main())
