from __future__ import annotations

import json
import math
from pathlib import Path
import tempfile


ALPHA_AXIS = (0.5, 1.0)
SCHEMES = ("endpoint_energy", "midpoint_coupling")
GAP_DURATION_TICKS = (2_000_000_000, 10_000_000_000, 20_000_000_000)
PARTITION_COUNT = 320
ARM_IDS = ("continued_adaptive", "frozen_receptivity_baseline")
MEASUREMENT_ROLES = ("activation", "afterimage", "local_energy", "receptivity")
SHARD_AUDIT_ID = (
    "public.av.nasa-earthrise.repeated-world-contact-"
    "adaptive-receptivity-alpha-scheme-shard.v1"
)
MERGED_AUDIT_ID = (
    "public.av.nasa-earthrise.repeated-world-contact-adaptive-receptivity.v1"
)
SHARD_PATHS = tuple(
    Path("reports/shards")
    / (
        "public_av_repeated_world_contact_receptivity_"
        f"alpha_{f'{alpha:.2f}'.replace('.', '_')}_scheme_{scheme}_v1.json"
    )
    for alpha in ALPHA_AXIS
    for scheme in SCHEMES
)
OUTPUT = Path("reports/public_av_repeated_world_contact_receptivity_v1.json")
DISABLED_FIELDS = (
    "threshold_defined",
    "preferred_scheme_selected",
    "preferred_alpha_selected",
    "memory_claim_allowed",
    "meaning_claim_allowed",
    "organization_claim_allowed",
    "consciousness_claim_allowed",
    "ai_claim_allowed",
)
COMMON_FIELDS = (
    "source_id",
    "gap_duration_ticks",
    "partition_count",
    "contact_ticks",
    "arm_ids",
    "measurement_roles",
    "second_contact_sensor_events_identical",
    "second_contact_start_shared_between_arms",
    "frozen_baseline_uses_carried_receptivity_for_input_scaling",
    "frozen_baseline_updates_receptivity",
)


class RepeatedWorldContactShardMergeError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RepeatedWorldContactShardMergeError(message)


def _validate_group(group: dict, alpha: float, scheme: str) -> None:
    _require(group.get("alpha_per_amplitude_second") == alpha, "group alpha mismatch")
    _require(group.get("scheme") == scheme, "group scheme mismatch")
    gap_ticks = group.get("gap_ticks")
    _require(gap_ticks in GAP_DURATION_TICKS, "unexpected gap duration")
    _require(group.get("partition_count") == PARTITION_COUNT, "partition mismatch")
    trace = group.get("gap_trace")
    _require(isinstance(trace, list) and len(trace) == PARTITION_COUNT,
             "gap trace length mismatch")
    elapsed = [record.get("elapsed_ticks") for record in trace]
    _require(elapsed == sorted(elapsed) and len(set(elapsed)) == PARTITION_COUNT,
             "gap trace time order is inconsistent")
    _require(elapsed[-1] == gap_ticks, "gap trace does not end at its duration")

    arms = group.get("arms")
    _require(isinstance(arms, list) and [arm.get("arm_id") for arm in arms] == list(ARM_IDS),
             "arm order or membership is inconsistent")
    for field in ("start_layer_digest", "start_snapshot_digest", "start_receptivity"):
        _require(arms[0].get(field) == arms[1].get(field),
                 f"second-contact arm starts differ: {field}")
    _require(arms[0].get("start_layer_digest"), "start layer digest is required")
    _require(arms[0].get("start_snapshot_digest"), "start snapshot digest is required")
    frozen_final = arms[1].get("final", {}).get("receptivity")
    _require(arms[1].get("start_receptivity") == frozen_final,
             "frozen receptivity changed during second contact")
    _require(arms[0].get("event_count") == arms[1].get("event_count"),
             "second-contact event counts differ")

    differences = group.get("adaptive_to_frozen_linf")
    _require(isinstance(differences, dict) and tuple(differences) == MEASUREMENT_ROLES,
             "end-difference roles are inconsistent")
    _require(all(isinstance(value, (int, float)) and math.isfinite(value) and value >= 0.0
                 for value in differences.values()),
             "end differences must be finite and nonnegative")


def _validate_shard(payload: dict) -> tuple[float, str]:
    _require(payload.get("audit_id") == SHARD_AUDIT_ID, "unexpected shard audit id")
    _require(payload.get("shard_axes") == ["alpha", "scheme"], "unexpected shard axes")
    alpha_axis = payload.get("alpha_axis")
    scheme_axis = payload.get("schemes")
    _require(isinstance(alpha_axis, list) and len(alpha_axis) == 1,
             "each shard must contain one alpha")
    _require(isinstance(scheme_axis, list) and len(scheme_axis) == 1,
             "each shard must contain one scheme")
    alpha = float(alpha_axis[0])
    scheme = scheme_axis[0]
    _require(alpha in ALPHA_AXIS, "unexpected alpha shard")
    _require(scheme in SCHEMES, "unexpected scheme shard")
    _require(payload.get("shard_values") == {"alpha": alpha, "scheme": scheme},
             "shard values differ from shard axes")
    _require(payload.get("gap_duration_ticks") == list(GAP_DURATION_TICKS),
             "gap-duration axis is inconsistent")
    _require(payload.get("partition_count") == PARTITION_COUNT,
             "partition count is inconsistent")
    _require(payload.get("arm_ids") == list(ARM_IDS), "arm metadata is inconsistent")
    _require(payload.get("measurement_roles") == list(MEASUREMENT_ROLES),
             "measurement roles are inconsistent")
    for field in DISABLED_FIELDS:
        _require(payload.get(field) is False, f"{field} must remain disabled")
    _require(payload.get("second_contact_sensor_events_identical") is True,
             "sensor-event identity must remain registered")
    _require(payload.get("second_contact_start_shared_between_arms") is True,
             "shared second-contact start must remain registered")
    _require(payload.get("frozen_baseline_updates_receptivity") is False,
             "frozen baseline must not update receptivity")

    groups = payload.get("groups")
    _require(isinstance(groups, list) and len(groups) == len(GAP_DURATION_TICKS),
             "each shard must contain one group per gap duration")
    _require([group.get("gap_ticks") for group in groups] == list(GAP_DURATION_TICKS),
             "group gap order or membership is inconsistent")
    for group in groups:
        _validate_group(group, alpha, scheme)
    return alpha, scheme


def merge_payloads(payloads: list[dict]) -> dict:
    expected = tuple((alpha, scheme) for alpha in ALPHA_AXIS for scheme in SCHEMES)
    _require(len(payloads) == len(expected), "exactly four shards are required")
    by_axes = {}
    for payload in payloads:
        axes = _validate_shard(payload)
        _require(axes not in by_axes, "duplicate alpha-scheme shard")
        by_axes[axes] = payload
    _require(tuple(sorted(by_axes, key=lambda item: (item[0], SCHEMES.index(item[1])))) == expected,
             "alpha-scheme shards are incomplete")

    reference = by_axes[expected[0]]
    for axes in expected[1:]:
        for field in COMMON_FIELDS:
            _require(by_axes[axes].get(field) == reference.get(field),
                     f"common metadata differs: {field}")
    merged = {
        key: value for key, value in reference.items()
        if key not in {"groups", "alpha_axis", "schemes", "shard_axes", "shard_values"}
    }
    merged["audit_id"] = MERGED_AUDIT_ID
    merged["alpha_axis"] = list(ALPHA_AXIS)
    merged["schemes"] = list(SCHEMES)
    merged["groups"] = [
        group
        for axes in expected
        for group in sorted(by_axes[axes]["groups"], key=lambda item: item["gap_ticks"])
    ]
    return merged


def merge_shard_files(paths=SHARD_PATHS, output: Path = OUTPUT) -> Path:
    paths = tuple(Path(path) for path in paths)
    _require(len(paths) == len(SHARD_PATHS), "exactly four shard paths are required")
    _require(len(set(paths)) == len(paths), "duplicate shard path")
    payloads = []
    for path in paths:
        _require(path.is_file(), f"missing shard: {path}")
        try:
            payloads.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            raise RepeatedWorldContactShardMergeError(f"invalid shard: {path}") from exc
    payload = merge_payloads(payloads)

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=output.parent, delete=False,
            prefix=f"{output.name}.", suffix=".tmp",
        ) as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            temporary = Path(handle.name)
        temporary.replace(output)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return output


def main() -> int:
    output = merge_shard_files()
    print(output.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
