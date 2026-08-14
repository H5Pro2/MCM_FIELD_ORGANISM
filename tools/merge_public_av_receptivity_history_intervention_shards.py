from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import tempfile


ALPHA_AXIS = (0.5, 1.0)
SCHEMES = ("endpoint_energy", "midpoint_coupling")
GAP_DURATION_TICKS = (2_000_000_000, 10_000_000_000, 20_000_000_000)
PARTITION_COUNT = 320
ARM_IDS = (
    "carried_receptivity",
    "reset_receptivity",
    "identical_carried_control",
)
MEASUREMENT_ROLES = ("activation", "afterimage", "local_energy", "receptivity")
SHARD_AUDIT_ID = (
    "public.av.nasa-earthrise.receptivity-history-intervention-"
    "alpha-scheme-shard.v1"
)
MERGED_AUDIT_ID = (
    "public.av.nasa-earthrise.receptivity-history-intervention.v1"
)
SHARD_PATHS = tuple(
    Path("reports/shards")
    / (
        "public_av_receptivity_history_intervention_"
        f"alpha_{f'{alpha:.2f}'.replace('.', '_')}_scheme_{scheme}_v1.json"
    )
    for alpha in ALPHA_AXIS
    for scheme in SCHEMES
)
OUTPUT = Path("reports/public_av_receptivity_history_intervention_v1.json")
REPLICATION_SOURCE_START_TICK = 500_000_000
REPLICATION_SOURCE_END_TICK = 1_000_000_000
REPLICATION_EVENT_TIMELINE_DIGEST = (
    "2bea5826788efdc8f213c99bbf66c1e4b314bcb823da7a97c7b18cf976eb0dd7"
)
REPLICATION_INTERVAL_SLUG = (
    f"source_ticks_{REPLICATION_SOURCE_START_TICK}_{REPLICATION_SOURCE_END_TICK}"
)
REPLICATION_SHARD_PATHS = tuple(
    Path("reports/shards")
    / (
        "public_av_receptivity_history_intervention_"
        f"alpha_{f'{alpha:.2f}'.replace('.', '_')}_scheme_{scheme}_"
        f"{REPLICATION_INTERVAL_SLUG}_v1.json"
    )
    for alpha in ALPHA_AXIS
    for scheme in SCHEMES
)
REPLICATION_OUTPUT = Path(
    "reports/public_av_receptivity_history_intervention_"
    f"{REPLICATION_INTERVAL_SLUG}_v1.json"
)
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
    "intervention_changes_receptivity_initialization_only",
)


class ReceptivityHistoryInterventionShardMergeError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReceptivityHistoryInterventionShardMergeError(message)


def _finite_nonnegative(value) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0.0
    )


def _validate_receptivity(metrics, context: str) -> None:
    _require(isinstance(metrics, dict), f"{context} receptivity is missing")
    minimum = metrics.get("minimum")
    maximum = metrics.get("maximum")
    _require(_finite_nonnegative(minimum) and _finite_nonnegative(maximum),
             f"{context} receptivity bounds must be finite")
    _require(0.25 <= minimum <= maximum <= 1.0,
             f"{context} receptivity bounds are invalid")


def _validate_role_differences(values, context: str) -> None:
    _require(isinstance(values, dict) and tuple(values) == MEASUREMENT_ROLES,
             f"{context} roles are inconsistent")
    _require(all(_finite_nonnegative(values[role]) for role in MEASUREMENT_ROLES),
             f"{context} values must be finite and nonnegative")


def _event_timeline_digest(timeline: list[dict]) -> str:
    return hashlib.sha256(
        json.dumps(timeline, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _validate_event_timeline(group: dict) -> str:
    timeline = group.get("second_contact_event_timeline")
    _require(isinstance(timeline, list) and timeline,
             "second-contact event timeline is missing")
    _require(all(set(event) == {"sequence_index", "sensor_path", "elapsed_ticks"}
                 for event in timeline), "event timeline fields are invalid")
    _require([event["sequence_index"] for event in timeline]
             == list(range(len(timeline))), "event sequence indexes are invalid")
    _require(all(isinstance(event["sensor_path"], str) and event["sensor_path"]
                 for event in timeline), "event sensor paths are invalid")
    _require(all(isinstance(event["elapsed_ticks"], int)
                 and not isinstance(event["elapsed_ticks"], bool)
                 and 0 < event["elapsed_ticks"] <= group["arms"][0]["trace"][-1]["elapsed_ticks"]
                 for event in timeline), "event elapsed ticks are invalid")
    order = [(event["elapsed_ticks"], event["sensor_path"])
             for event in timeline]
    _require(order == sorted(order), "event timeline order is invalid")
    digest = _event_timeline_digest(timeline)
    _require(group.get("second_contact_event_timeline_digest") == digest,
             "group event timeline digest differs")
    arm_digests = [arm.get("second_contact_event_timeline_digest")
                   for arm in group["arms"]]
    _require(len(arm_digests) == len(ARM_IDS)
             and all(value == digest for value in arm_digests),
             "arm event timeline digests differ")
    _require(group.get("arm_event_timeline_digests_identical") is True,
             "arm event timeline digest identity must remain true")
    _require(all(arm.get("event_count") == len(timeline)
                 for arm in group["arms"]),
             "arm event counts differ from event timeline")
    return digest


def _validate_trace_onsets(group: dict) -> None:
    onsets = group.get("trace_onset_intervals")
    field_roles = MEASUREMENT_ROLES[:-1]
    _require(isinstance(onsets, dict) and tuple(onsets) == field_roles,
             "trace onset roles are inconsistent")
    trace = group["carried_to_reset_trace"]
    timeline = group["second_contact_event_timeline"]
    for role in field_roles:
        onset = onsets[role]
        _require(isinstance(onset, dict), f"{role} trace onset is missing")
        index = onset.get("trace_index")
        _require(isinstance(index, int) and not isinstance(index, bool)
                 and 0 <= index < len(trace), f"{role} trace onset index is invalid")
        start = 0 if index == 0 else trace[index - 1]["elapsed_ticks"]
        end = trace[index]["elapsed_ticks"]
        expected_events = [event["sequence_index"] for event in timeline
                           if start < event["elapsed_ticks"] <= end]
        _require(onset.get("interval_start_elapsed_ticks") == start
                 and onset.get("interval_end_elapsed_ticks") == end
                 and onset.get("event_sequence_indices") == expected_events,
                 f"{role} trace onset interval is inconsistent")
        _require(all(point["carried_to_reset_linf"][role] == 0.0
                     for point in trace[:index])
                 and trace[index]["carried_to_reset_linf"][role] != 0.0,
                 f"{role} trace onset is not exact")


def _validate_group(group: dict, alpha: float, scheme: str) -> None:
    _require(group.get("alpha_per_amplitude_second") == alpha,
             "group alpha mismatch")
    _require(group.get("scheme") == scheme, "group scheme mismatch")
    gap_ticks = group.get("gap_ticks")
    _require(gap_ticks in GAP_DURATION_TICKS, "unexpected gap duration")
    _require(group.get("partition_count") == PARTITION_COUNT, "partition mismatch")
    _require(group.get("intervention") ==
             "reset_receptivity_only_before_second_contact",
             "unexpected intervention")
    for field in (
        "field_start_shared_between_arms",
        "sensor_events_and_time_axis_shared_between_arms",
        "active_update_rule_shared_between_arms",
        "identical_control_passed",
    ):
        _require(group.get(field) is True, f"{field} must remain true")

    gap_trace = group.get("gap_trace")
    _require(isinstance(gap_trace, list) and len(gap_trace) == PARTITION_COUNT,
             "gap trace length mismatch")
    gap_elapsed = [record.get("elapsed_ticks") for record in gap_trace]
    _require(gap_elapsed == sorted(gap_elapsed)
             and len(set(gap_elapsed)) == PARTITION_COUNT,
             "gap trace time order is inconsistent")
    _require(gap_elapsed[-1] == gap_ticks, "gap trace does not end at its duration")

    arms = group.get("arms")
    _require(isinstance(arms, list)
             and [arm.get("arm_id") for arm in arms] == list(ARM_IDS),
             "arm order or membership is inconsistent")
    carried, reset, control = arms
    for field in ("start_layer_digest", "start_snapshot_digest"):
        _require(carried.get(field) and carried.get(field) == reset.get(field)
                 == control.get(field), f"arm starts differ: {field}")
    _require(carried.get("event_count") == reset.get("event_count")
             == control.get("event_count"), "second-contact event counts differ")
    _require(carried.get("start_receptivity") == control.get("start_receptivity"),
             "carried and control receptivity starts differ")
    _require(carried.get("start_receptivity") != reset.get("start_receptivity"),
             "reset intervention is absent")

    contact_elapsed = None
    for arm in arms:
        _validate_receptivity(arm.get("start_receptivity"),
                               f"{arm.get('arm_id')} start")
        trace = arm.get("trace")
        _require(isinstance(trace, list) and len(trace) == PARTITION_COUNT,
                 "arm trace length mismatch")
        elapsed = [record.get("elapsed_ticks") for record in trace]
        _require(elapsed == sorted(elapsed) and len(set(elapsed)) == PARTITION_COUNT,
                 "arm trace time order is inconsistent")
        if contact_elapsed is None:
            contact_elapsed = elapsed
        _require(elapsed == contact_elapsed, "arm time axes differ")
        for record in trace:
            _validate_receptivity(record.get("receptivity"),
                                   f"{arm.get('arm_id')} trace")
        _validate_receptivity(arm.get("final", {}).get("receptivity"),
                               f"{arm.get('arm_id')} final")

    _require(carried.get("trace") == control.get("trace"),
             "identical control trace differs")
    _require(carried.get("final") == control.get("final"),
             "identical control final state differs")
    _validate_role_differences(group.get("identical_control_final_linf"),
                               "identical-control final differences")
    _require(all(group["identical_control_final_linf"][role] == 0.0
                 for role in MEASUREMENT_ROLES),
             "identical-control final differences must be exactly zero")

    start = group.get("carried_to_reset_start_linf")
    _validate_role_differences(start, "carried-to-reset start differences")
    _require(all(start[role] == 0.0 for role in MEASUREMENT_ROLES[:-1]),
             "field starts must remain identical")
    _require(start["receptivity"] > 0.0,
             "reset intervention must change receptivity initialization")

    differences = group.get("carried_to_reset_trace")
    _require(isinstance(differences, list) and len(differences) == PARTITION_COUNT,
             "difference trace length mismatch")
    _require([record.get("elapsed_ticks") for record in differences] == contact_elapsed,
             "difference trace time axis is inconsistent")
    for record in differences:
        _validate_role_differences(record.get("carried_to_reset_linf"),
                                   "carried-to-reset trace differences")
    _validate_event_timeline(group)
    _validate_trace_onsets(group)


def _validate_shard(payload: dict) -> tuple[float, str]:
    _require(payload.get("audit_id") == SHARD_AUDIT_ID, "unexpected shard audit id")
    _require(payload.get("shard_axes") == ["alpha", "scheme"],
             "unexpected shard axes")
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
    _require(payload.get("arm_ids") == list(ARM_IDS),
             "arm metadata is inconsistent")
    _require(payload.get("measurement_roles") == list(MEASUREMENT_ROLES),
             "measurement roles are inconsistent")
    _require(payload.get("intervention_changes_receptivity_initialization_only")
             is True, "intervention isolation must remain registered")
    for field in DISABLED_FIELDS:
        _require(payload.get(field) is False, f"{field} must remain disabled")

    groups = payload.get("groups")
    _require(isinstance(groups, list) and len(groups) == len(GAP_DURATION_TICKS),
             "each shard must contain one group per gap duration")
    _require([group.get("gap_ticks") for group in groups]
             == list(GAP_DURATION_TICKS),
             "group gap order or membership is inconsistent")
    for group in groups:
        _validate_group(group, alpha, scheme)
        _require(group["arms"][0]["trace"][-1]["elapsed_ticks"]
                 == payload.get("contact_ticks"),
                 "arm trace does not end at contact duration")
    return alpha, scheme


def merge_payloads(
    payloads: list[dict],
    *,
    expected_source_interval: tuple[int, int] | None = None,
    expected_event_timeline_digest: str | None = None,
) -> dict:
    _require(
        (expected_source_interval is None)
        == (expected_event_timeline_digest is None),
        "source interval and event timeline digest must be specified together",
    )
    expected = tuple((alpha, scheme) for alpha in ALPHA_AXIS for scheme in SCHEMES)
    _require(len(payloads) == len(expected), "exactly four shards are required")
    by_axes = {}
    for payload in payloads:
        axes = _validate_shard(payload)
        _require(axes not in by_axes, "duplicate alpha-scheme shard")
        by_axes[axes] = payload
    _require(tuple(sorted(by_axes, key=lambda item: (
        item[0], SCHEMES.index(item[1])
    ))) == expected, "alpha-scheme shards are incomplete")

    reference = by_axes[expected[0]]
    for axes in expected[1:]:
        for field in COMMON_FIELDS:
            _require(by_axes[axes].get(field) == reference.get(field),
                     f"common metadata differs: {field}")
    event_digests = {
        group["second_contact_event_timeline_digest"]
        for payload in by_axes.values() for group in payload["groups"]
    }
    _require(len(event_digests) == 1,
             "second-contact event timelines differ across shards")
    if expected_source_interval is not None:
        expected_start, expected_end = expected_source_interval
        _require(expected_start < expected_end, "source interval is invalid")
        for payload in by_axes.values():
            _require(
                payload.get("source_start_tick") == expected_start,
                "source start tick differs",
            )
            _require(
                payload.get("source_end_tick") == expected_end,
                "source end tick differs",
            )
            _require(
                payload.get("source_event_timeline_digest")
                == expected_event_timeline_digest,
                "source event timeline digest differs",
            )
        _require(
            event_digests == {expected_event_timeline_digest},
            "group event timeline digest differs from source digest",
        )
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


def merge_shard_files(
    paths=SHARD_PATHS,
    output: Path = OUTPUT,
    *,
    expected_source_interval: tuple[int, int] | None = None,
    expected_event_timeline_digest: str | None = None,
) -> Path:
    paths = tuple(Path(path) for path in paths)
    _require(len(paths) == len(SHARD_PATHS), "exactly four shard paths are required")
    _require(len(set(paths)) == len(paths), "duplicate shard path")
    output = Path(output)
    input_paths = {path.resolve() for path in paths}
    _require(output.resolve() not in input_paths, "output path collides with a shard path")
    payloads = []
    for path in paths:
        _require(path.is_file(), f"missing shard: {path}")
        try:
            payloads.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as exc:
            raise ReceptivityHistoryInterventionShardMergeError(
                f"invalid shard: {path}"
            ) from exc
    payload = merge_payloads(
        payloads,
        expected_source_interval=expected_source_interval,
        expected_event_timeline_digest=expected_event_timeline_digest,
    )

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


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--replication-interval",
        action="store_true",
        help="merge the fixed audited source interval [500000000, 1000000000)",
    )
    return parser


def main(argv=None) -> int:
    args = _parser().parse_args(argv)
    if args.replication_interval:
        output = merge_shard_files(
            REPLICATION_SHARD_PATHS,
            REPLICATION_OUTPUT,
            expected_source_interval=(
                REPLICATION_SOURCE_START_TICK,
                REPLICATION_SOURCE_END_TICK,
            ),
            expected_event_timeline_digest=REPLICATION_EVENT_TIMELINE_DIGEST,
        )
    else:
        output = merge_shard_files()
    print(output.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
