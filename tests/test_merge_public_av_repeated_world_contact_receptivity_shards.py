from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.merge_public_av_repeated_world_contact_receptivity_shards import (
    ALPHA_AXIS,
    ARM_IDS,
    DISABLED_FIELDS,
    GAP_DURATION_TICKS,
    MEASUREMENT_ROLES,
    MERGED_AUDIT_ID,
    OUTPUT,
    PARTITION_COUNT,
    RepeatedWorldContactShardMergeError,
    SCHEMES,
    SHARD_AUDIT_ID,
    SHARD_PATHS,
    merge_payloads,
    merge_shard_files,
)


def _state(receptivity=None):
    return {"receptivity": receptivity or {"minimum": 0.5, "maximum": 1.0}}


def _payload(alpha: float, scheme: str) -> dict:
    groups = []
    for gap in GAP_DURATION_TICKS:
        start_receptivity = {"minimum": 0.5, "maximum": 1.0}
        arms = [{
            "arm_id": arm_id,
            "event_count": 56,
            "start_layer_digest": f"layer-{alpha}-{scheme}-{gap}",
            "start_snapshot_digest": f"snapshot-{alpha}-{scheme}-{gap}",
            "start_receptivity": start_receptivity,
            "final": _state(start_receptivity if arm_id == ARM_IDS[1] else None),
        } for arm_id in ARM_IDS]
        groups.append({
            "alpha_per_amplitude_second": alpha,
            "scheme": scheme,
            "gap_ticks": gap,
            "partition_count": PARTITION_COUNT,
            "gap_trace": [
                {"elapsed_ticks": gap // PARTITION_COUNT * (index + 1)}
                for index in range(PARTITION_COUNT)
            ],
            "arms": arms,
            "adaptive_to_frozen_linf": {role: 0.0 for role in MEASUREMENT_ROLES},
        })
    payload = {
        "audit_id": SHARD_AUDIT_ID,
        "source_id": "source",
        "alpha_axis": [alpha],
        "schemes": [scheme],
        "gap_duration_ticks": list(GAP_DURATION_TICKS),
        "partition_count": PARTITION_COUNT,
        "contact_ticks": 500_000_000,
        "arm_ids": list(ARM_IDS),
        "measurement_roles": list(MEASUREMENT_ROLES),
        "second_contact_sensor_events_identical": True,
        "second_contact_start_shared_between_arms": True,
        "frozen_baseline_uses_carried_receptivity_for_input_scaling": True,
        "frozen_baseline_updates_receptivity": False,
        "groups": groups,
        "shard_axes": ["alpha", "scheme"],
        "shard_values": {"alpha": alpha, "scheme": scheme},
    }
    for field in DISABLED_FIELDS:
        payload[field] = False
    return payload


def _all_payloads():
    return [_payload(alpha, scheme) for alpha in ALPHA_AXIS for scheme in SCHEMES]


class RepeatedWorldContactShardMergeTests(unittest.TestCase):
    def test_paths_and_target_are_preregistered(self) -> None:
        self.assertEqual(4, len(SHARD_PATHS))
        self.assertEqual(
            Path("reports/shards/public_av_repeated_world_contact_receptivity_"
                 "alpha_0_50_scheme_endpoint_energy_v1.json"),
            SHARD_PATHS[0],
        )
        self.assertEqual(
            Path("reports/public_av_repeated_world_contact_receptivity_v1.json"),
            OUTPUT,
        )

    def test_merge_is_complete_and_deterministically_ordered(self) -> None:
        merged = merge_payloads(list(reversed(_all_payloads())))
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
        self.assertFalse(merged["organization_claim_allowed"])

    def test_missing_duplicate_and_inconsistent_shards_are_rejected(self) -> None:
        with self.assertRaises(RepeatedWorldContactShardMergeError):
            merge_payloads(_all_payloads()[:-1])
        duplicate = _all_payloads()
        duplicate[-1] = _payload(0.5, "endpoint_energy")
        with self.assertRaises(RepeatedWorldContactShardMergeError):
            merge_payloads(duplicate)
        inconsistent = _all_payloads()
        inconsistent[-1]["groups"][0]["gap_trace"] = []
        with self.assertRaises(RepeatedWorldContactShardMergeError):
            merge_payloads(inconsistent)

    def test_arm_start_baseline_and_claim_inconsistencies_are_rejected(self) -> None:
        differing_start = _all_payloads()
        differing_start[0]["groups"][0]["arms"][1]["start_layer_digest"] = "other"
        with self.assertRaises(RepeatedWorldContactShardMergeError):
            merge_payloads(differing_start)
        changed_frozen = _all_payloads()
        changed_frozen[0]["groups"][0]["arms"][1]["final"]["receptivity"] = {
            "minimum": 0.6, "maximum": 1.0
        }
        with self.assertRaises(RepeatedWorldContactShardMergeError):
            merge_payloads(changed_frozen)
        enabled_claim = _all_payloads()
        enabled_claim[0]["memory_claim_allowed"] = True
        with self.assertRaises(RepeatedWorldContactShardMergeError):
            merge_payloads(enabled_claim)

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
            with self.assertRaises(RepeatedWorldContactShardMergeError):
                merge_shard_files(paths, target)
            self.assertEqual("existing", target.read_text(encoding="utf-8"))

    def test_valid_merge_uses_atomic_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for index, payload in enumerate(reversed(_all_payloads())):
                path = root / f"{index}.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                paths.append(path)
            target = root / "nested" / "report.json"
            self.assertEqual(target, merge_shard_files(paths, target))
            self.assertEqual(list(ALPHA_AXIS), json.loads(
                target.read_text(encoding="utf-8")
            )["alpha_axis"])
            self.assertEqual([], list(target.parent.glob("*.tmp")))


if __name__ == "__main__":
    unittest.main()
