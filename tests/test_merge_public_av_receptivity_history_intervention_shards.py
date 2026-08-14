from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

from tools.merge_public_av_receptivity_history_intervention_shards import (
    ALPHA_AXIS,
    ARM_IDS,
    DISABLED_FIELDS,
    GAP_DURATION_TICKS,
    MEASUREMENT_ROLES,
    MERGED_AUDIT_ID,
    OUTPUT,
    PARTITION_COUNT,
    ReceptivityHistoryInterventionShardMergeError,
    REPLICATION_EVENT_TIMELINE_DIGEST,
    REPLICATION_OUTPUT,
    REPLICATION_SHARD_PATHS,
    REPLICATION_SOURCE_END_TICK,
    REPLICATION_SOURCE_START_TICK,
    SCHEMES,
    SHARD_AUDIT_ID,
    SHARD_PATHS,
    merge_payloads,
    merge_shard_files,
)


def _receptivity(minimum=0.5, maximum=1.0):
    return {
        "minimum": minimum,
        "maximum": maximum,
        "mean": (minimum + maximum) / 2.0,
        "l2": 1.0,
        "linf": maximum,
    }


def _record(elapsed_ticks, receptivity=None):
    return {
        "elapsed_ticks": elapsed_ticks,
        "receptivity": receptivity or _receptivity(),
    }


def _payload(alpha: float, scheme: str) -> dict:
    groups = []
    contact_ticks = 500_000_000
    contact_step = contact_ticks // PARTITION_COUNT
    event_ticks = [10_000_000 * (index + 1) for index in range(15)]
    event_ticks.extend((200_000_000, 201_562_500))
    event_ticks.extend(
        210_000_000 + 5_000_000 * index for index in range(39)
    )
    event_timeline = [
        {
            "sequence_index": index,
            "sensor_path": "auditory" if index % 2 == 0 else "visual",
            "elapsed_ticks": elapsed_ticks,
        }
        for index, elapsed_ticks in enumerate(event_ticks)
    ]
    event_timeline.sort(key=lambda event: (
        event["elapsed_ticks"], event["sensor_path"]
    ))
    for index, event in enumerate(event_timeline):
        event["sequence_index"] = index
    event_digest = hashlib.sha256(
        json.dumps(event_timeline, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    for gap in GAP_DURATION_TICKS:
        gap_step = gap // PARTITION_COUNT
        carried_start = _receptivity(0.5, 0.9)
        reset_start = _receptivity(0.6, 1.0)
        carried_trace = [
            _record(contact_step * (index + 1)) for index in range(PARTITION_COUNT)
        ]
        carried_final = _record(contact_ticks)
        arms = []
        for arm_id in ARM_IDS:
            is_reset = arm_id == "reset_receptivity"
            arms.append({
                "arm_id": arm_id,
                "event_count": 56,
                "second_contact_event_timeline_digest": event_digest,
                "start_layer_digest": f"layer-{alpha}-{scheme}-{gap}",
                "start_snapshot_digest": f"snapshot-{alpha}-{scheme}-{gap}",
                "start_receptivity": reset_start if is_reset else carried_start,
                "trace": copy.deepcopy(carried_trace),
                "final": copy.deepcopy(carried_final),
            })
        groups.append({
            "alpha_per_amplitude_second": alpha,
            "scheme": scheme,
            "gap_ticks": gap,
            "partition_count": PARTITION_COUNT,
            "intervention": "reset_receptivity_only_before_second_contact",
            "field_start_shared_between_arms": True,
            "sensor_events_and_time_axis_shared_between_arms": True,
            "active_update_rule_shared_between_arms": True,
            "identical_control_passed": True,
            "second_contact_event_timeline": copy.deepcopy(event_timeline),
            "second_contact_event_timeline_digest": event_digest,
            "arm_event_timeline_digests_identical": True,
            "gap_trace": [
                {"elapsed_ticks": gap_step * (index + 1)}
                for index in range(PARTITION_COUNT)
            ],
            "arms": arms,
            "identical_control_final_linf": {
                role: 0.0 for role in MEASUREMENT_ROLES
            },
            "carried_to_reset_start_linf": {
                role: 0.1 if role == "receptivity" else 0.0
                for role in MEASUREMENT_ROLES
            },
            "carried_to_reset_trace": [
                {
                    "elapsed_ticks": contact_step * (index + 1),
                    "carried_to_reset_linf": {
                        role: (
                            0.0
                            if role in ("activation", "local_energy") and index < 127
                            or role == "afterimage" and index < 128
                            else 0.1
                        )
                        for role in MEASUREMENT_ROLES
                    },
                }
                for index in range(PARTITION_COUNT)
            ],
            "trace_onset_intervals": {
                "activation": {
                    "trace_index": 127,
                    "interval_start_elapsed_ticks": contact_step * 127,
                    "interval_end_elapsed_ticks": contact_step * 128,
                    "event_sequence_indices": [15],
                },
                "afterimage": {
                    "trace_index": 128,
                    "interval_start_elapsed_ticks": contact_step * 128,
                    "interval_end_elapsed_ticks": contact_step * 129,
                    "event_sequence_indices": [16],
                },
                "local_energy": {
                    "trace_index": 127,
                    "interval_start_elapsed_ticks": contact_step * 127,
                    "interval_end_elapsed_ticks": contact_step * 128,
                    "event_sequence_indices": [15],
                },
            },
        })
    payload = {
        "audit_id": SHARD_AUDIT_ID,
        "source_id": "source",
        "alpha_axis": [alpha],
        "schemes": [scheme],
        "gap_duration_ticks": list(GAP_DURATION_TICKS),
        "partition_count": PARTITION_COUNT,
        "contact_ticks": contact_ticks,
        "arm_ids": list(ARM_IDS),
        "measurement_roles": list(MEASUREMENT_ROLES),
        "intervention_changes_receptivity_initialization_only": True,
        "groups": groups,
        "shard_axes": ["alpha", "scheme"],
        "shard_values": {"alpha": alpha, "scheme": scheme},
    }
    for field in DISABLED_FIELDS:
        payload[field] = False
    return payload


def _all_payloads():
    return [_payload(alpha, scheme) for alpha in ALPHA_AXIS for scheme in SCHEMES]


def _replication_payloads():
    payloads = _all_payloads()
    digest = payloads[0]["groups"][0]["second_contact_event_timeline_digest"]
    for payload in payloads:
        payload["source_start_tick"] = REPLICATION_SOURCE_START_TICK
        payload["source_end_tick"] = REPLICATION_SOURCE_END_TICK
        payload["source_event_timeline_digest"] = digest
    return payloads, digest


class ReceptivityHistoryInterventionShardMergeTests(unittest.TestCase):
    def test_paths_target_and_complete_stable_order_are_fixed(self) -> None:
        self.assertEqual(4, len(SHARD_PATHS))
        self.assertEqual(
            Path("reports/public_av_receptivity_history_intervention_v1.json"),
            OUTPUT,
        )
        self.assertEqual(4, len(REPLICATION_SHARD_PATHS))
        self.assertTrue(all(
            "source_ticks_500000000_1000000000" in path.name
            for path in REPLICATION_SHARD_PATHS
        ))
        self.assertNotEqual(OUTPUT, REPLICATION_OUTPUT)
        self.assertIn(
            "source_ticks_500000000_1000000000", REPLICATION_OUTPUT.name
        )
        payloads = _all_payloads()
        source_group = payloads[0]["groups"][0]
        merged = merge_payloads(list(reversed(payloads)))
        self.assertEqual(MERGED_AUDIT_ID, merged["audit_id"])
        self.assertEqual(list(ALPHA_AXIS), merged["alpha_axis"])
        self.assertEqual(list(SCHEMES), merged["schemes"])
        expected = [
            (alpha, scheme, gap)
            for alpha in ALPHA_AXIS for scheme in SCHEMES for gap in GAP_DURATION_TICKS
        ]
        self.assertEqual(expected, [
            (group["alpha_per_amplitude_second"], group["scheme"], group["gap_ticks"])
            for group in merged["groups"]
        ])
        self.assertNotIn("shard_axes", merged)
        self.assertNotIn("shard_values", merged)
        self.assertEqual(12, len(merged["groups"]))
        merged_group = merged["groups"][0]
        for field in (
            "second_contact_event_timeline",
            "second_contact_event_timeline_digest",
            "arm_event_timeline_digests_identical",
            "trace_onset_intervals",
        ):
            self.assertEqual(source_group[field], merged_group[field])
        for field in DISABLED_FIELDS:
            self.assertFalse(merged[field])

    def test_missing_duplicate_and_unexpected_axes_are_rejected(self) -> None:
        with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
            merge_payloads(_all_payloads()[:-1])
        duplicate = _all_payloads()
        duplicate[-1] = _payload(0.5, "endpoint_energy")
        with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
            merge_payloads(duplicate)
        unexpected = _all_payloads()
        unexpected[0]["alpha_axis"] = [2.0]
        unexpected[0]["shard_values"]["alpha"] = 2.0
        with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
            merge_payloads(unexpected)

    def test_common_metadata_difference_is_rejected(self) -> None:
        payloads = _all_payloads()
        payloads[-1]["source_id"] = "other"
        with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
            merge_payloads(payloads)

    def test_replication_source_contract_is_required_and_exact(self) -> None:
        payloads, digest = _replication_payloads()
        merged = merge_payloads(
            payloads,
            expected_source_interval=(
                REPLICATION_SOURCE_START_TICK,
                REPLICATION_SOURCE_END_TICK,
            ),
            expected_event_timeline_digest=digest,
        )
        self.assertEqual(REPLICATION_SOURCE_START_TICK, merged["source_start_tick"])
        self.assertEqual(REPLICATION_SOURCE_END_TICK, merged["source_end_tick"])
        self.assertEqual(digest, merged["source_event_timeline_digest"])

        cases = ("mixed_interval", "wrong_digest", "missing_metadata")
        for case in cases:
            broken, digest = _replication_payloads()
            if case == "mixed_interval":
                broken[-1]["source_start_tick"] = 0
            elif case == "wrong_digest":
                broken[-1]["source_event_timeline_digest"] = "broken"
            else:
                del broken[-1]["source_end_tick"]
            with self.subTest(case=case):
                with self.assertRaises(
                    ReceptivityHistoryInterventionShardMergeError
                ):
                    merge_payloads(
                        broken,
                        expected_source_interval=(
                            REPLICATION_SOURCE_START_TICK,
                            REPLICATION_SOURCE_END_TICK,
                        ),
                        expected_event_timeline_digest=digest,
                    )

    def test_replication_digest_is_fixed(self) -> None:
        self.assertEqual(
            "2bea5826788efdc8f213c99bbf66c1e4b314bcb823da7a97c7b18cf976eb0dd7",
            REPLICATION_EVENT_TIMELINE_DIGEST,
        )

    def test_broken_identical_control_is_rejected(self) -> None:
        payloads = _all_payloads()
        payloads[0]["groups"][0]["arms"][2]["trace"][0]["receptivity"][
            "minimum"
        ] = 0.6
        with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
            merge_payloads(payloads)

    def test_receptivity_bound_violation_is_rejected(self) -> None:
        payloads = _all_payloads()
        payloads[0]["groups"][0]["arms"][1]["trace"][0]["receptivity"][
            "minimum"
        ] = 0.2
        with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
            merge_payloads(payloads)

    def test_nonfinite_difference_is_rejected(self) -> None:
        payloads = _all_payloads()
        payloads[0]["groups"][0]["carried_to_reset_trace"][0][
            "carried_to_reset_linf"
        ]["activation"] = math.inf
        with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
            merge_payloads(payloads)

    def test_event_timeline_digest_and_fields_are_revalidated(self) -> None:
        payloads = _all_payloads()
        payloads[0]["groups"][0]["second_contact_event_timeline"][0][
            "raw_payload"
        ] = "forbidden"
        with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
            merge_payloads(payloads)
        payloads = _all_payloads()
        payloads[0]["groups"][0]["second_contact_event_timeline_digest"] = "broken"
        with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
            merge_payloads(payloads)

    def test_event_order_and_cross_shard_equality_are_revalidated(self) -> None:
        payloads = _all_payloads()
        timeline = payloads[0]["groups"][0]["second_contact_event_timeline"]
        timeline[0], timeline[1] = timeline[1], timeline[0]
        with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
            merge_payloads(payloads)
        payloads = _all_payloads()
        group = payloads[-1]["groups"][-1]
        group["second_contact_event_timeline"][0]["sensor_path"] = "tactile"
        digest = hashlib.sha256(json.dumps(
            group["second_contact_event_timeline"], sort_keys=True,
            separators=(",", ":"),
        ).encode()).hexdigest()
        group["second_contact_event_timeline_digest"] = digest
        for arm in group["arms"]:
            arm["second_contact_event_timeline_digest"] = digest
        with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
            merge_payloads(payloads)

    def test_onset_interval_and_receptivity_separation_are_revalidated(self) -> None:
        payloads = _all_payloads()
        payloads[0]["groups"][0]["trace_onset_intervals"]["activation"][
            "event_sequence_indices"
        ] = []
        with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
            merge_payloads(payloads)
        payloads = _all_payloads()
        payloads[0]["groups"][0]["trace_onset_intervals"]["receptivity"] = None
        with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
            merge_payloads(payloads)

    def test_enabled_claim_or_selection_is_rejected(self) -> None:
        for field in DISABLED_FIELDS:
            payloads = _all_payloads()
            payloads[0][field] = True
            with self.subTest(field=field):
                with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
                    merge_payloads(payloads)

    def test_invalid_input_preserves_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for index, payload in enumerate(_all_payloads()):
                path = root / f"{index}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                paths.append(path)
            paths[-1].write_text("invalid", encoding="utf-8")
            target = root / "report.json"
            target.write_text("existing", encoding="utf-8")
            with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
                merge_shard_files(paths, target)
            self.assertEqual("existing", target.read_text(encoding="utf-8"))

    def test_output_collision_is_rejected_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for index, payload in enumerate(_all_payloads()):
                path = root / f"{index}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                paths.append(path)
            original = paths[0].read_text(encoding="utf-8")
            with self.assertRaises(ReceptivityHistoryInterventionShardMergeError):
                merge_shard_files(paths, paths[0])
            self.assertEqual(original, paths[0].read_text(encoding="utf-8"))

    def test_synthetic_merge_uses_atomic_temporary_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for index, payload in enumerate(reversed(_all_payloads())):
                path = root / f"{index}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                paths.append(path)
            target = root / "nested" / "report.json"
            self.assertEqual(target, merge_shard_files(paths, target))
            merged = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(MERGED_AUDIT_ID, merged["audit_id"])
            self.assertEqual([], list(target.parent.glob("*.tmp")))


if __name__ == "__main__":
    unittest.main()
