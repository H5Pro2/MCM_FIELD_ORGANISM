from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from tools.merge_public_av_local_adaptive_receptivity_cauchy_convergence_shards import (
    ALPHA_AXIS,
    CauchyConvergenceShardMergeError,
    MERGED_AUDIT_ID,
    OUTPUT,
    SHARD_AUDIT_ID,
    SHARD_PATHS,
    merge_payloads,
    merge_shard_files,
)


def _payload(alpha: float) -> dict:
    schemes = ("endpoint_energy", "midpoint_coupling")
    groups = []
    for duration in (2_000_000_000, 10_000_000_000, 20_000_000_000):
        results = []
        for scheme in schemes:
            results.append({
                "scheme": scheme,
                "runs": [
                    {"partition_count": count, "trace": [{}] * count}
                    for count in (20, 40, 80, 160)
                ],
                "successive_cauchy_comparisons": [
                    {"coarse_partition_count": coarse, "fine_partition_count": fine}
                    for coarse, fine in ((20, 40), (40, 80), (80, 160))
                ],
            })
        groups.append({
            "alpha_per_amplitude_second": alpha,
            "duration_ticks": duration,
            "start_layer_digest": f"layer-{alpha}",
            "start_snapshot_digest": f"snapshot-{alpha}",
            "scheme_results": results,
        })
    return {
        "audit_id": SHARD_AUDIT_ID,
        "source_id": "source",
        "alpha_axis": [alpha],
        "duration_ticks": [2_000_000_000, 10_000_000_000, 20_000_000_000],
        "partition_counts": [20, 40, 80, 160],
        "schemes": list(schemes),
        "fixed_leak_rate_per_second": 0.0,
        "groups": groups,
        "shard_axis": "alpha",
        "shard_value": alpha,
        "threshold_defined": False,
        "convergence_order_selected": False,
        "preferred_scheme_selected": False,
        "preferred_partition_selected": False,
        "memory_claim_allowed": False,
        "meaning_claim_allowed": False,
        "organization_claim_allowed": False,
        "ai_claim_allowed": False,
    }


class CauchyConvergenceShardMergeTests(unittest.TestCase):
    def test_paths_are_preregistered_without_running_merge(self) -> None:
        self.assertEqual(3, len(SHARD_PATHS))
        self.assertEqual(
            Path("reports/shards/public_av_local_adaptive_receptivity_"
                 "cauchy_convergence_alpha_0_50_v1.json"),
            SHARD_PATHS[1],
        )
        self.assertEqual(
            Path("reports/public_av_local_adaptive_receptivity_"
                 "cauchy_convergence_audit_v1.json"),
            OUTPUT,
        )

    def test_merge_is_complete_and_deterministically_ordered(self) -> None:
        payloads = [_payload(1.0), _payload(0.0), _payload(0.5)]
        merged = merge_payloads(payloads)
        self.assertEqual(MERGED_AUDIT_ID, merged["audit_id"])
        self.assertEqual(list(ALPHA_AXIS), merged["alpha_axis"])
        self.assertEqual(
            [(alpha, duration) for alpha in ALPHA_AXIS for duration in
             (2_000_000_000, 10_000_000_000, 20_000_000_000)],
            [(group["alpha_per_amplitude_second"], group["duration_ticks"])
             for group in merged["groups"]],
        )
        self.assertNotIn("shard_axis", merged)
        self.assertNotIn("shard_value", merged)
        self.assertFalse(merged["organization_claim_allowed"])

    def test_missing_duplicate_and_inconsistent_shards_are_rejected(self) -> None:
        with self.assertRaises(CauchyConvergenceShardMergeError):
            merge_payloads([_payload(0.0), _payload(0.5)])
        with self.assertRaises(CauchyConvergenceShardMergeError):
            merge_payloads([_payload(0.0), _payload(0.5), _payload(0.5)])
        inconsistent = _payload(1.0)
        inconsistent["partition_counts"] = [20, 40, 80]
        with self.assertRaises(CauchyConvergenceShardMergeError):
            merge_payloads([_payload(0.0), _payload(0.5), inconsistent])

    def test_invalid_input_does_not_create_or_replace_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for alpha in ALPHA_AXIS:
                path = root / f"{alpha}.json"
                path.write_text(json.dumps(_payload(alpha)), encoding="utf-8")
                paths.append(path)
            target = root / "report.json"
            target.write_text("existing", encoding="utf-8")
            paths[2].write_text("not-json", encoding="utf-8")
            with self.assertRaises(CauchyConvergenceShardMergeError):
                merge_shard_files(paths, target)
            self.assertEqual("existing", target.read_text(encoding="utf-8"))

    def test_valid_merge_writes_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for alpha in reversed(ALPHA_AXIS):
                path = root / f"{alpha}.json"
                path.write_text(json.dumps(_payload(alpha)), encoding="utf-8")
                paths.append(path)
            target = root / "nested" / "report.json"
            self.assertEqual(target, merge_shard_files(paths, target))
            merged = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(list(ALPHA_AXIS), merged["alpha_axis"])
            self.assertEqual([], list(target.parent.glob("*.tmp")))


if __name__ == "__main__":
    unittest.main()
