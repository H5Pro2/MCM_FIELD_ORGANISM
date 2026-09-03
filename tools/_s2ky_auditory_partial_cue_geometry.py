"""One-shot PCM geometry materialization for the static S2-KX contract."""

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


PLAN_PATH = Path("docs/S2KY_AUDITORY_PARTIAL_CUE_GEOMETRY_PLAN.json")
OUTPUT_ROOT = Path("reports/s2kx/s2ky-auditory-partial-cue-geometry-20260903-01")
OUTPUT_PATH = OUTPUT_ROOT / "materialization.json"
SUCCESS = "S2KY_AUDIO_PARTIAL_CUE_GEOMETRY_MATERIALIZED"
BLOCKED = "S2KX_AUDIO_PARTIAL_CUE_GEOMETRY_NOT_MATERIALIZABLE"
RECIPE_ROLES = (
    "U_UNIT",
    "V_UNIT",
    "CUE_LOW",
    "CANDIDATE_PLUS",
    "CANDIDATE_MINUS",
    "CANDIDATE_HIGH",
)


class S2KYMaterializationError(ValueError):
    """The sealed PCM geometry plan or its measured output is invalid."""


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


def _basis(frequency: int) -> tuple[float, ...]:
    return tuple(
        _f32(math.sin((2.0 * math.pi * frequency * index) / 48_000.0))
        for index in range(4_800)
    )


def _pcm_digest(values: tuple[float, ...]) -> str:
    return hashlib.sha256(np.asarray(values, dtype="<f4").tobytes()).hexdigest()


def _load_plan() -> dict[str, Any]:
    value = json.loads(PLAN_PATH.read_text(encoding="ascii"))
    if not isinstance(value, dict):
        raise S2KYMaterializationError("plan must be an object")
    if value.get("schema") != "s2ky.auditory-partial-cue-geometry-plan.v1":
        raise S2KYMaterializationError("plan schema differs")
    if value.get("success_status") != SUCCESS or value.get("failure_status") != BLOCKED:
        raise S2KYMaterializationError("plan status binding differs")
    if tuple(item["role"] for item in value.get("recipes", ())) != RECIPE_ROLES:
        raise S2KYMaterializationError("recipe registry differs")
    if len(value.get("relationship_classes", ())) != 8:
        raise S2KYMaterializationError("relationship registry differs")
    if value.get("execution_limits") != {
        "materialization_calls": 1,
        "pcm_windows": 6,
        "audio_hops": 60,
        "receptor_endpoints": 6,
        "memory_calls": 0,
        "slotscan_calls": 0,
        "context_calls": 0,
        "field_calls": 0,
        "parameter_searches": 0,
        "replacement_fixtures": 0,
    }:
        raise S2KYMaterializationError("execution limits differ")
    return value


def _recipes(plan: dict[str, Any]) -> dict[str, tuple[float, ...]]:
    coefficients = plan["coefficients"]
    expected = {
        "alpha_u": 0.49968934059143066,
        "alpha_hv": 0.37617719173431396,
        "alpha_plus_v": 0.564265787601471,
        "alpha_minus_v": 0.18808859586715698,
        "origin": "qualified-s2kf-fixed-24-over-25-plan",
    }
    if coefficients != expected:
        raise S2KYMaterializationError("sealed coefficients differ")
    u = _basis(100)
    v = _basis(8_000)
    low: list[float] = []
    plus: list[float] = []
    minus: list[float] = []
    high: list[float] = []
    for u_value, v_value in zip(u, v, strict=True):
        u_term = _f32(coefficients["alpha_u"] * u_value)
        high_term = _f32(coefficients["alpha_hv"] * v_value)
        plus_term = _f32(coefficients["alpha_plus_v"] * v_value)
        minus_term = _f32(coefficients["alpha_minus_v"] * v_value)
        low.append(u_term)
        plus.append(_f32(u_term + plus_term))
        minus.append(_f32(u_term + minus_term))
        high.append(high_term)
    result = {
        "U_UNIT": u,
        "V_UNIT": v,
        "CUE_LOW": tuple(low),
        "CANDIDATE_PLUS": tuple(plus),
        "CANDIDATE_MINUS": tuple(minus),
        "CANDIDATE_HIGH": tuple(high),
    }
    if tuple(result) != RECIPE_ROLES:
        raise S2KYMaterializationError("materialized recipe order differs")
    for role, values in result.items():
        if len(values) != 4_800 or any(not math.isfinite(item) or abs(item) > 1.0 for item in values):
            raise S2KYMaterializationError(f"PCM sample bounds differ for {role}")
    return result


def _analyze_window(values: tuple[float, ...]) -> dict[str, object]:
    config = LogSpectralConfig()
    path = BroadbandHearingPath(LogSpectralReceptor(config))
    state = None
    outputs = 0
    for hop in range(10):
        state = path.push(values[hop * 480 : (hop + 1) * 480])
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
        or any(not math.isfinite(item) for item in state.energy)
    ):
        raise S2KYMaterializationError("auditory receptor endpoint differs")
    values48 = tuple(state.energy)
    return {
        "pcm_digest": _pcm_digest(values),
        "pcm_min": min(values),
        "pcm_max": max(values),
        "receptor_digest": state.digest(),
        "values_digest": _digest(list(values48)),
        "values": list(values48),
        "nonzero_bands": [index for index, item in enumerate(values48) if item != 0.0],
        "input_hops": 10,
        "output_snapshots": 1,
    }


def _distance(left: list[float], right: list[float], indices: tuple[int, ...]) -> float:
    return sum(abs(left[index] - right[index]) for index in indices) / len(indices)


def _pair(
    measurements: dict[str, dict[str, object]],
    left: str,
    right: str,
    observed: tuple[int, ...],
    masked: tuple[int, ...],
) -> dict[str, object]:
    left_values = measurements[left]["values"]
    right_values = measurements[right]["values"]
    if not isinstance(left_values, list) or not isinstance(right_values, list):
        raise S2KYMaterializationError("measured values missing")
    observed_terms = [abs(left_values[index] - right_values[index]) for index in observed]
    masked_terms = [abs(left_values[index] - right_values[index]) for index in masked]
    full_terms = [abs(a - b) for a, b in zip(left_values, right_values, strict=True)]
    payload = {
        "left": left,
        "right": right,
        "observed_terms": observed_terms,
        "observed_l1": sum(observed_terms) / 24,
        "masked_terms": masked_terms,
        "masked_l1_diagnostic": sum(masked_terms) / 24,
        "full_terms": full_terms,
        "full_l1": sum(full_terms) / 48,
    }
    return {**payload, "pair_digest": _digest(payload)}


def _classify(
    specification: dict[str, Any],
    measurements: dict[str, dict[str, object]],
    observed: tuple[int, ...],
    fast_threshold: float,
    slow_threshold: float,
) -> dict[str, object]:
    cue = specification["cue"]

    def matches(roles: list[str], threshold: float) -> list[str]:
        cue_values = measurements[cue]["values"]
        if not isinstance(cue_values, list):
            raise S2KYMaterializationError("cue values missing")
        selected = []
        for role in roles:
            candidate = measurements[role]["values"]
            if not isinstance(candidate, list):
                raise S2KYMaterializationError("candidate values missing")
            if _distance(cue_values, candidate, observed) <= threshold:
                selected.append(role)
        return selected

    b4_matches = matches(specification["b4"], fast_threshold)
    fast_matches = matches(specification["fast"], fast_threshold)
    slow_matches = matches(specification["slow"], slow_threshold)
    expected = specification["expected"]
    if expected == "UNIQUE_A":
        passed = len(b4_matches) == 1 and not fast_matches and not slow_matches
    elif expected == "UNIQUE_B":
        passed = not b4_matches and not fast_matches and len(slow_matches) == 1
    elif expected == "PUBLIC_AMBIGUITY":
        passed = len(b4_matches) == 1 and not fast_matches and len(slow_matches) == 1
    elif expected == "A_BANK_AMBIGUITY":
        passed = len(b4_matches) == 2 and not fast_matches and not slow_matches
    elif expected == "A_INTERNAL_CONFLICT":
        passed = (
            len(b4_matches) == 1
            and len(fast_matches) == 1
            and not slow_matches
            and measurements[b4_matches[0]]["values_digest"]
            != measurements[fast_matches[0]]["values_digest"]
        )
    elif expected == "B_INTERNAL_AMBIGUITY":
        passed = not b4_matches and not fast_matches and len(slow_matches) == 2
    elif expected == "NO_CONTEXT":
        passed = not specification["b4"] and not specification["fast"] and not specification["slow"]
    elif expected == "NO_APPLICABLE_CONTEXT":
        passed = not b4_matches and not fast_matches and not slow_matches and bool(specification["slow"])
    else:
        raise S2KYMaterializationError("unknown relationship expectation")
    payload = {
        "class_id": specification["class_id"],
        "cue": cue,
        "expected": expected,
        "b4_inventory": specification["b4"],
        "fast_inventory": specification["fast"],
        "slow_inventory": specification["slow"],
        "b4_matches": b4_matches,
        "fast_matches": fast_matches,
        "slow_matches": slow_matches,
        "passed": passed,
    }
    return {**payload, "class_digest": _digest(payload)}


def _git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _write_once(payload: dict[str, object]) -> None:
    OUTPUT_ROOT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_ROOT.mkdir(exist_ok=False)
    temporary = OUTPUT_ROOT / "materialization.json.tmp"
    data = _json_bytes(payload) + b"\n"
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, OUTPUT_PATH)


def materialize_once() -> dict[str, object]:
    plan = _load_plan()
    observed = tuple(plan["profile"]["observed_bands"])
    masked = tuple(plan["profile"]["masked_bands"])
    if observed != tuple(range(24)) or masked != tuple(range(24, 48)):
        raise S2KYMaterializationError("band plan differs")
    recipes = _recipes(plan)
    measurements = {role: _analyze_window(recipes[role]) for role in RECIPE_ROLES}
    pairs: dict[str, dict[str, object]] = {}
    for gate in plan["distance_gates"]:
        key = f'{gate["left"]}::{gate["right"]}'
        pairs.setdefault(key, _pair(measurements, gate["left"], gate["right"], observed, masked))
    gate_results = []
    for gate in plan["distance_gates"]:
        pair = pairs[f'{gate["left"]}::{gate["right"]}']
        actual = pair[gate["metric"]]
        passed = isinstance(actual, float) and gate["minimum"] <= actual <= gate["maximum"]
        gate_results.append({**gate, "actual": actual, "passed": passed})

    fast_checks = []
    for check in plan["fast_and_checks"]:
        key = f'{check["left"]}::{check["right"]}'
        pairs.setdefault(key, _pair(measurements, check["left"], check["right"], observed, masked))
        auditory_distance = pairs[key]["full_l1"]
        actual = (
            isinstance(auditory_distance, float)
            and auditory_distance <= plan["profile"]["fast_auditory_threshold"]
            and check["visual_distance"] <= plan["profile"]["fast_visual_threshold"]
        )
        fast_checks.append({**check, "auditory_distance": auditory_distance, "actual_match": actual, "passed": actual is check["expected_match"]})

    classes = [
        _classify(
            item,
            measurements,
            observed,
            plan["profile"]["fast_auditory_threshold"],
            plan["profile"]["auditory_slow_threshold"],
        )
        for item in plan["relationship_classes"]
    ]
    u_values = measurements["U_UNIT"]["values"]
    v_values = measurements["V_UNIT"]["values"]
    if not isinstance(u_values, list) or not isinstance(v_values, list):
        raise S2KYMaterializationError("basis values missing")
    overlap = {
        "u_nonzero_bands": measurements["U_UNIT"]["nonzero_bands"],
        "v_nonzero_bands": measurements["V_UNIT"]["nonzero_bands"],
        "joint_nonzero_bands": [index for index in range(48) if u_values[index] != 0.0 and v_values[index] != 0.0],
        "observed_v_mean_abs": sum(abs(v_values[index]) for index in observed) / 24,
        "masked_u_mean_abs": sum(abs(u_values[index]) for index in masked) / 24,
        "full_minimum_overlap_l1": sum(min(abs(a), abs(b)) for a, b in zip(u_values, v_values, strict=True)) / 48,
        "used_as_pass_condition": False,
    }
    passed = all(item["passed"] for item in gate_results) and all(item["passed"] for item in fast_checks) and all(item["passed"] for item in classes)
    status = SUCCESS if passed else BLOCKED
    body: dict[str, object] = {
        "schema": "s2ky.auditory-partial-cue-geometry-result.v1",
        "run_id": plan["run_id"],
        "status": status,
        "plan_sha256": _file_digest(PLAN_PATH),
        "source_commit": _git_head(),
        "source_hashes": {
            "mcm_field_organism/log_spectral_receptor.py": _file_digest(Path("mcm_field_organism/log_spectral_receptor.py")),
            "mcm_field_organism/broadband_hearing_path.py": _file_digest(Path("mcm_field_organism/broadband_hearing_path.py")),
            "tools/_s2ky_auditory_partial_cue_geometry.py": _file_digest(Path("tools/_s2ky_auditory_partial_cue_geometry.py")),
        },
        "profile": plan["profile"],
        "coefficients": plan["coefficients"],
        "measurements": measurements,
        "pair_measurements": list(pairs.values()),
        "distance_gate_results": gate_results,
        "filterbank_overlap": overlap,
        "fast_and_checks": fast_checks,
        "relationship_classes": classes,
        "counters": {
            "materialization_calls": 1,
            "pcm_windows": len(measurements),
            "audio_hops": 10 * len(measurements),
            "receptor_endpoints": len(measurements),
            "relationship_classes": len(classes),
            "memory_calls": 0,
            "slotscan_calls": 0,
            "context_calls": 0,
            "field_calls": 0,
            "parameter_searches": 0,
            "replacement_fixtures": 0,
        },
    }
    body["result_digest"] = _digest(body)
    _write_once(body)
    return body


def main() -> int:
    try:
        result = materialize_once()
    except Exception as exc:
        print(f"S2KY_EXECUTION_ERROR:{type(exc).__name__}", file=sys.stderr)
        return 2
    print(result["status"])
    print(result["result_digest"])
    return 0 if result["status"] == SUCCESS else 1


if __name__ == "__main__":
    raise SystemExit(main())
