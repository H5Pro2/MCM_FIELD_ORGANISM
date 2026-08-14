from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from tools.merge_public_av_receptivity_history_intervention_shards import (
    ALPHA_AXIS,
    ARM_IDS,
    DISABLED_FIELDS,
    GAP_DURATION_TICKS,
    MERGED_AUDIT_ID,
    OUTPUT,
    REPLICATION_EVENT_TIMELINE_DIGEST,
    REPLICATION_OUTPUT,
    REPLICATION_SHARD_PATHS,
    REPLICATION_SOURCE_END_TICK,
    REPLICATION_SOURCE_START_TICK,
    SCHEMES,
    merge_payloads,
)


ORIGINAL_INPUT = OUTPUT
REPLICATION_INPUT = REPLICATION_OUTPUT
ORIGINAL_INTERVAL = (0, REPLICATION_SOURCE_START_TICK)
REPLICATION_INTERVAL = (
    REPLICATION_SOURCE_START_TICK,
    REPLICATION_SOURCE_END_TICK,
)
REPLICATION_SHARD_ARTIFACTS = (
    (REPLICATION_SHARD_PATHS[0], 5_643_788,
     "1d169283331184935f60127084f65267ac2688b88882ad531704eea4e038d3dd"),
    (REPLICATION_SHARD_PATHS[1], 5_643_189,
     "75c3e6c69048fce94dfaf9e15f67e3dabe7252de1348ff9e665f7910fa9d3f42"),
    (REPLICATION_SHARD_PATHS[2], 5_642_798,
     "52e83e8887bebf6bdc7196d1fba1391ddc5ad3f2813b80a24ff6de5a6647dd22"),
    (REPLICATION_SHARD_PATHS[3], 5_643_050,
     "51257462073b0c4b8eb41ba64f04e9f6fd8cc99bf1edeaebffadfe3d456fb967"),
)
AUDIT_STATEMENT_LIMIT = (
    "Technical replication-chain validation only; no finding about field effect, "
    "contact history, organization, memory, meaning, semantics, consciousness, or AI."
)


class IntervalComparisonContractError(ValueError):
    pass


@dataclass(frozen=True)
class TechnicalIntervalSummary:
    interval: tuple[int, int]
    group_count: int
    arm_count_per_group: int
    event_count_per_arm: int
    timeline_digest: str
    identity_control_count: int


@dataclass(frozen=True)
class ReplicationChainAuditSummary:
    shard_count: int
    replication_merge_matches_shards: bool
    technical_interval_comparison_passed: bool
    threshold_defined: bool
    ranking_allowed: bool
    selection_allowed: bool
    research_claim_allowed: bool
    statement_limit: str


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IntervalComparisonContractError(message)


def _group_key(group: dict) -> tuple[float, str, int]:
    return (
        float(group.get("alpha_per_amplitude_second")),
        group.get("scheme"),
        group.get("gap_ticks"),
    )


def _validate_payload(
    payload: dict,
    *,
    interval: tuple[int, int],
    legacy_original: bool,
) -> TechnicalIntervalSummary:
    _require(payload.get("audit_id") == MERGED_AUDIT_ID, "unexpected audit id")
    _require(payload.get("alpha_axis") == list(ALPHA_AXIS), "alpha axis differs")
    _require(payload.get("schemes") == list(SCHEMES), "scheme axis differs")
    for field in DISABLED_FIELDS:
        _require(payload.get(field) is False, f"{field} must remain disabled")

    if legacy_original:
        for field in (
            "source_start_tick",
            "source_end_tick",
            "source_event_timeline_digest",
        ):
            _require(field not in payload, f"legacy original unexpectedly defines {field}")
    else:
        _require(payload.get("source_start_tick") == interval[0], "source start differs")
        _require(payload.get("source_end_tick") == interval[1], "source end differs")
        _require(
            payload.get("source_event_timeline_digest")
            == REPLICATION_EVENT_TIMELINE_DIGEST,
            "replication source digest differs",
        )

    groups = payload.get("groups")
    expected_keys = [
        (alpha, scheme, gap)
        for alpha in ALPHA_AXIS
        for scheme in SCHEMES
        for gap in GAP_DURATION_TICKS
    ]
    _require(isinstance(groups, list), "groups are missing")
    _require([_group_key(group) for group in groups] == expected_keys,
             "group axes or order differ")

    digests = set()
    event_counts = set()
    identity_count = 0
    for group in groups:
        _require(group.get("identical_control_passed") is True,
                 "identity control did not pass")
        identity = group.get("identical_control_final_linf")
        _require(isinstance(identity, dict) and identity,
                 "identity values are missing")
        _require(all(value == 0.0 for value in identity.values()),
                 "identity values must be exactly zero")
        identity_count += 1

        digest = group.get("second_contact_event_timeline_digest")
        _require(isinstance(digest, str) and digest, "group digest is missing")
        digests.add(digest)
        arms = group.get("arms")
        _require(isinstance(arms, list), "group arms are missing")
        _require([arm.get("arm_id") for arm in arms] == list(ARM_IDS),
                 "arm coverage or order differs")
        for arm in arms:
            _require(arm.get("second_contact_event_timeline_digest") == digest,
                     "arm digest differs from group digest")
            count = arm.get("event_count")
            _require(isinstance(count, int) and not isinstance(count, bool) and count > 0,
                     "arm event count is invalid")
            event_counts.add(count)

    _require(len(digests) == 1, "interval contains multiple timeline digests")
    _require(len(event_counts) == 1, "arm event counts differ")
    digest = next(iter(digests))
    if not legacy_original:
        _require(digest == REPLICATION_EVENT_TIMELINE_DIGEST,
                 "replication group digest differs from source digest")
    return TechnicalIntervalSummary(
        interval=interval,
        group_count=len(groups),
        arm_count_per_group=len(ARM_IDS),
        event_count_per_arm=next(iter(event_counts)),
        timeline_digest=digest,
        identity_control_count=identity_count,
    )


def validate_comparison_contract(
    original: dict,
    replication: dict,
) -> tuple[TechnicalIntervalSummary, TechnicalIntervalSummary]:
    _require(ORIGINAL_INPUT != REPLICATION_INPUT, "input paths must remain distinct")
    _require(ORIGINAL_INTERVAL[1] == REPLICATION_INTERVAL[0],
             "source intervals must be adjacent")
    _require(ORIGINAL_INTERVAL[0] < ORIGINAL_INTERVAL[1],
             "original interval is invalid")
    _require(REPLICATION_INTERVAL[0] < REPLICATION_INTERVAL[1],
             "replication interval is invalid")
    original_summary = _validate_payload(
        original, interval=ORIGINAL_INTERVAL, legacy_original=True
    )
    replication_summary = _validate_payload(
        replication, interval=REPLICATION_INTERVAL, legacy_original=False
    )
    _require(
        (
            original_summary.group_count,
            original_summary.arm_count_per_group,
            original_summary.identity_control_count,
        )
        == (
            replication_summary.group_count,
            replication_summary.arm_count_per_group,
            replication_summary.identity_control_count,
        ),
        "technical counts differ between intervals",
    )
    return original_summary, replication_summary


def comparison_input_paths() -> tuple[Path, Path]:
    return ORIGINAL_INPUT, REPLICATION_INPUT


def validate_replication_chain_files() -> ReplicationChainAuditSummary:
    shard_payloads = []
    for path, expected_size, expected_digest in REPLICATION_SHARD_ARTIFACTS:
        _require(path.is_file(), f"replication shard is missing: {path}")
        data = path.read_bytes()
        _require(len(data) == expected_size, f"replication shard size differs: {path}")
        _require(
            hashlib.sha256(data).hexdigest() == expected_digest,
            f"replication shard digest differs: {path}",
        )
        try:
            shard_payloads.append(json.loads(data))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise IntervalComparisonContractError(
                f"replication shard is not valid JSON: {path}"
            ) from exc

    _require(ORIGINAL_INPUT.is_file(), f"original merge is missing: {ORIGINAL_INPUT}")
    _require(
        REPLICATION_INPUT.is_file(),
        f"replication merge is missing: {REPLICATION_INPUT}",
    )
    try:
        original = json.loads(ORIGINAL_INPUT.read_bytes())
        replication = json.loads(REPLICATION_INPUT.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntervalComparisonContractError("merge input is not valid JSON") from exc

    reconstructed = merge_payloads(
        shard_payloads,
        expected_source_interval=REPLICATION_INTERVAL,
        expected_event_timeline_digest=REPLICATION_EVENT_TIMELINE_DIGEST,
    )
    _require(reconstructed == replication, "replication merge differs from shards")
    validate_comparison_contract(original, replication)
    return ReplicationChainAuditSummary(
        shard_count=len(shard_payloads),
        replication_merge_matches_shards=True,
        technical_interval_comparison_passed=True,
        threshold_defined=False,
        ranking_allowed=False,
        selection_allowed=False,
        research_claim_allowed=False,
        statement_limit=AUDIT_STATEMENT_LIMIT,
    )
