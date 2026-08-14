from __future__ import annotations

import json
from pathlib import Path
import tempfile


ALPHA_AXIS = (0.5, 1.0)
DURATION_TICKS = (2_000_000_000, 10_000_000_000, 20_000_000_000)
PARTITION_COUNTS = (80, 160, 320)
SCHEMES = ("endpoint_energy", "midpoint_coupling")
CAUCHY_PAIRS = ((80, 160), (160, 320))
SHARD_AUDIT_ID = (
    "public.av.nasa-earthrise.local-adaptive-receptivity-"
    "cauchy-320-confirmation-alpha-shard.v1"
)
MERGED_AUDIT_ID = (
    "public.av.nasa-earthrise.local-adaptive-receptivity-"
    "cauchy-320-confirmation.v1"
)
SHARD_PATHS = tuple(
    Path("reports/shards")
    / (
        "public_av_local_adaptive_receptivity_cauchy_320_confirmation_"
        f"alpha_{f'{alpha:.2f}'.replace('.', '_')}_v1.json"
    )
    for alpha in ALPHA_AXIS
)
OUTPUT = Path(
    "reports/public_av_local_adaptive_receptivity_"
    "cauchy_320_confirmation_v1.json"
)
DISABLED_FIELDS = (
    "threshold_defined",
    "convergence_order_selected",
    "preferred_scheme_selected",
    "preferred_partition_selected",
    "memory_claim_allowed",
    "meaning_claim_allowed",
    "organization_claim_allowed",
    "ai_claim_allowed",
)
COMMON_FIELDS = (
    "source_id",
    "duration_ticks",
    "partition_counts",
    "schemes",
    "fixed_leak_rate_per_second",
)


class Cauchy320ConfirmationShardMergeError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Cauchy320ConfirmationShardMergeError(message)


def _validate_group(group: dict, alpha: float) -> None:
    _require(group.get("alpha_per_amplitude_second") == alpha, "group alpha mismatch")
    _require(group.get("duration_ticks") in DURATION_TICKS, "unexpected duration")
    results = group.get("scheme_results")
    _require(isinstance(results, list), "scheme results are required")
    _require([result.get("scheme") for result in results] == list(SCHEMES),
             "scheme order or membership is inconsistent")
    for result in results:
        runs = result.get("runs")
        _require(isinstance(runs, list), "partition runs are required")
        _require([run.get("partition_count") for run in runs] == list(PARTITION_COUNTS),
                 "partition order or membership is inconsistent")
        for run in runs:
            _require(len(run.get("trace", ())) == run["partition_count"],
                     "trace length does not match partition count")
        comparisons = result.get("successive_cauchy_comparisons")
        _require(isinstance(comparisons, list), "Cauchy comparisons are required")
        pairs = [
            (item.get("coarse_partition_count"), item.get("fine_partition_count"))
            for item in comparisons
        ]
        _require(pairs == list(CAUCHY_PAIRS), "Cauchy pairs are inconsistent")


def _validate_shard(payload: dict) -> float:
    _require(payload.get("audit_id") == SHARD_AUDIT_ID, "unexpected shard audit id")
    _require(payload.get("shard_axis") == "alpha", "unexpected shard axis")
    axis = payload.get("alpha_axis")
    _require(isinstance(axis, list) and len(axis) == 1,
             "each shard must contain exactly one alpha")
    alpha = float(axis[0])
    _require(alpha in ALPHA_AXIS, "unexpected alpha shard")
    _require(payload.get("shard_value") == alpha, "shard value and alpha differ")
    _require(payload.get("duration_ticks") == list(DURATION_TICKS),
             "duration axis is inconsistent")
    _require(payload.get("partition_counts") == list(PARTITION_COUNTS),
             "partition axis is inconsistent")
    _require(payload.get("schemes") == list(SCHEMES), "scheme axis is inconsistent")
    for field in DISABLED_FIELDS:
        _require(payload.get(field) is False, f"{field} must remain disabled")

    groups = payload.get("groups")
    _require(isinstance(groups, list) and len(groups) == len(DURATION_TICKS),
             "each shard must contain one group per duration")
    _require([group.get("duration_ticks") for group in groups] == list(DURATION_TICKS),
             "group duration order or membership is inconsistent")
    for group in groups:
        _validate_group(group, alpha)
    _require(len({group.get("start_layer_digest") for group in groups}) == 1,
             "start layer state differs across durations")
    _require(len({group.get("start_snapshot_digest") for group in groups}) == 1,
             "start snapshot state differs across durations")
    _require(groups[0].get("start_layer_digest"), "start layer digest is required")
    _require(groups[0].get("start_snapshot_digest"), "start snapshot digest is required")
    return alpha


def merge_payloads(payloads: list[dict]) -> dict:
    _require(len(payloads) == len(ALPHA_AXIS), "exactly two shards are required")
    by_alpha = {}
    for payload in payloads:
        alpha = _validate_shard(payload)
        _require(alpha not in by_alpha, "duplicate alpha shard")
        by_alpha[alpha] = payload
    _require(tuple(sorted(by_alpha)) == ALPHA_AXIS, "alpha shards are incomplete")

    reference = by_alpha[ALPHA_AXIS[0]]
    for field in COMMON_FIELDS:
        _require(by_alpha[ALPHA_AXIS[1]].get(field) == reference.get(field),
                 f"common metadata differs: {field}")
    merged = {
        key: value for key, value in reference.items()
        if key not in {"groups", "alpha_axis", "shard_axis", "shard_value"}
    }
    merged["audit_id"] = MERGED_AUDIT_ID
    merged["alpha_axis"] = list(ALPHA_AXIS)
    merged["groups"] = [
        group
        for alpha in ALPHA_AXIS
        for group in sorted(by_alpha[alpha]["groups"], key=lambda item: item["duration_ticks"])
    ]
    return merged


def merge_shard_files(paths=SHARD_PATHS, output: Path = OUTPUT) -> Path:
    paths = tuple(Path(path) for path in paths)
    _require(len(paths) == len(ALPHA_AXIS), "exactly two shard paths are required")
    _require(len(set(paths)) == len(paths), "duplicate shard path")
    payloads = []
    for path in paths:
        _require(path.is_file(), f"missing shard: {path}")
        try:
            payloads.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            raise Cauchy320ConfirmationShardMergeError(f"invalid shard: {path}") from exc
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
