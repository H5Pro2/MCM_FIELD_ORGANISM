from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tests.test_merge_public_av_receptivity_history_intervention_shards import (
    _replication_payloads,
)
from tools.merge_public_av_receptivity_history_intervention_shards import (
    DISABLED_FIELDS,
    REPLICATION_EVENT_TIMELINE_DIGEST,
    merge_payloads,
)
from tools.validate_public_av_receptivity_history_interval_comparison import (
    AUDIT_STATEMENT_LIMIT,
    IntervalComparisonContractError,
    ORIGINAL_INPUT,
    ORIGINAL_INTERVAL,
    REPLICATION_INPUT,
    REPLICATION_INTERVAL,
    REPLICATION_SHARD_ARTIFACTS,
    comparison_input_paths,
    validate_comparison_contract,
    validate_replication_chain_files,
)
import tools.validate_public_av_receptivity_history_interval_comparison as contract


def _merged_pair() -> tuple[dict, dict]:
    original_payloads, _ = _replication_payloads()
    for payload in original_payloads:
        payload.pop("source_start_tick")
        payload.pop("source_end_tick")
        payload.pop("source_event_timeline_digest")
    original = merge_payloads(original_payloads)
    replication_payloads, _ = _replication_payloads()
    replication = merge_payloads(replication_payloads)
    replication["source_start_tick"] = REPLICATION_INTERVAL[0]
    replication["source_end_tick"] = REPLICATION_INTERVAL[1]
    replication["source_event_timeline_digest"] = REPLICATION_EVENT_TIMELINE_DIGEST
    for group in replication["groups"]:
        group["second_contact_event_timeline_digest"] = (
            REPLICATION_EVENT_TIMELINE_DIGEST
        )
        for arm in group["arms"]:
            arm["second_contact_event_timeline_digest"] = (
                REPLICATION_EVENT_TIMELINE_DIGEST
            )
    return original, replication


def _audit_files(root: Path):
    shard_payloads, digest = _replication_payloads()
    shard_paths = []
    artifacts = []
    for index, payload in enumerate(shard_payloads):
        path = root / f"shard-{index}.json"
        data = (json.dumps(payload, sort_keys=True) + "\n").encode()
        path.write_bytes(data)
        shard_paths.append(path)
        artifacts.append((path, len(data), hashlib.sha256(data).hexdigest()))

    original_payloads = copy.deepcopy(shard_payloads)
    for payload in original_payloads:
        payload.pop("source_start_tick")
        payload.pop("source_end_tick")
        payload.pop("source_event_timeline_digest")
    original = merge_payloads(original_payloads)
    replication = merge_payloads(
        shard_payloads,
        expected_source_interval=REPLICATION_INTERVAL,
        expected_event_timeline_digest=digest,
    )
    original_path = root / "original.json"
    replication_path = root / "replication.json"
    original_path.write_text(json.dumps(original), encoding="utf-8")
    replication_path.write_text(json.dumps(replication), encoding="utf-8")
    return artifacts, original_path, replication_path, digest


def _audit_patches(artifacts, original_path, replication_path, digest):
    return patch.multiple(
        contract,
        REPLICATION_SHARD_ARTIFACTS=tuple(artifacts),
        ORIGINAL_INPUT=original_path,
        REPLICATION_INPUT=replication_path,
        REPLICATION_EVENT_TIMELINE_DIGEST=digest,
    )


class IntervalComparisonContractTests(unittest.TestCase):
    def test_replication_chain_artifacts_and_statement_limit_are_fixed(self) -> None:
        self.assertEqual(4, len(REPLICATION_SHARD_ARTIFACTS))
        self.assertEqual(
            [5_643_788, 5_643_189, 5_642_798, 5_643_050],
            [size for _, size, _ in REPLICATION_SHARD_ARTIFACTS],
        )
        self.assertTrue(all(len(digest) == 64 for _, _, digest in REPLICATION_SHARD_ARTIFACTS))
        self.assertIn("no finding about field effect", AUDIT_STATEMENT_LIMIT)
        self.assertIn("consciousness, or AI", AUDIT_STATEMENT_LIMIT)

    def test_replication_chain_files_returns_success_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = _audit_files(Path(directory))
            with _audit_patches(*fixture):
                summary = validate_replication_chain_files()
        self.assertEqual(4, summary.shard_count)
        self.assertTrue(summary.replication_merge_matches_shards)
        self.assertTrue(summary.technical_interval_comparison_passed)
        self.assertFalse(summary.threshold_defined)
        self.assertFalse(summary.ranking_allowed)
        self.assertFalse(summary.selection_allowed)
        self.assertFalse(summary.research_claim_allowed)
        self.assertEqual(AUDIT_STATEMENT_LIMIT, summary.statement_limit)

    def test_replication_chain_files_rejects_missing_shard(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = _audit_files(Path(directory))
            fixture[0][0][0].unlink()
            with _audit_patches(*fixture):
                with self.assertRaises(IntervalComparisonContractError):
                    validate_replication_chain_files()

    def test_replication_chain_files_rejects_wrong_size(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = _audit_files(Path(directory))
            with fixture[0][0][0].open("ab") as handle:
                handle.write(b"x")
            with _audit_patches(*fixture):
                with self.assertRaises(IntervalComparisonContractError):
                    validate_replication_chain_files()

    def test_replication_chain_files_rejects_wrong_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = _audit_files(Path(directory))
            path = fixture[0][0][0]
            data = bytearray(path.read_bytes())
            data[-2] = ord(" ") if data[-2] != ord(" ") else ord("\t")
            path.write_bytes(data)
            with _audit_patches(*fixture):
                with self.assertRaises(IntervalComparisonContractError):
                    validate_replication_chain_files()

    def test_replication_chain_files_rejects_invalid_shard_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifacts, original_path, replication_path, digest = _audit_files(
                Path(directory)
            )
            path = artifacts[0][0]
            invalid = b"not-json"
            path.write_bytes(invalid)
            artifacts[0] = (
                path,
                len(invalid),
                hashlib.sha256(invalid).hexdigest(),
            )
            with _audit_patches(artifacts, original_path, replication_path, digest):
                with self.assertRaises(IntervalComparisonContractError):
                    validate_replication_chain_files()

    def test_replication_chain_files_rejects_merge_inequality(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifacts, original_path, replication_path, digest = _audit_files(
                Path(directory)
            )
            replication = json.loads(replication_path.read_text(encoding="utf-8"))
            replication["unexpected"] = True
            replication_path.write_text(json.dumps(replication), encoding="utf-8")
            with _audit_patches(artifacts, original_path, replication_path, digest):
                with self.assertRaises(IntervalComparisonContractError):
                    validate_replication_chain_files()

    def test_paths_and_intervals_are_fixed_and_separate(self) -> None:
        self.assertEqual((ORIGINAL_INPUT, REPLICATION_INPUT), comparison_input_paths())
        self.assertNotEqual(ORIGINAL_INPUT, REPLICATION_INPUT)
        self.assertEqual((0, 500_000_000), ORIGINAL_INTERVAL)
        self.assertEqual((500_000_000, 1_000_000_000), REPLICATION_INTERVAL)

    def test_contract_returns_only_technical_summaries(self) -> None:
        original, replication = validate_comparison_contract(*_merged_pair())
        self.assertEqual(12, original.group_count)
        self.assertEqual(3, original.arm_count_per_group)
        self.assertEqual(12, original.identity_control_count)
        self.assertEqual(original.group_count, replication.group_count)

    def test_different_internally_consistent_interval_event_counts_are_allowed(self) -> None:
        original, replication = _merged_pair()
        for group in original["groups"]:
            for arm in group["arms"]:
                arm["event_count"] -= 1
        original_summary, replication_summary = validate_comparison_contract(
            original, replication
        )
        self.assertNotEqual(
            original_summary.event_count_per_arm,
            replication_summary.event_count_per_arm,
        )

    def test_inconsistent_event_counts_within_one_interval_are_rejected(self) -> None:
        original, replication = _merged_pair()
        replication["groups"][0]["arms"][0]["event_count"] -= 1
        with self.assertRaises(IntervalComparisonContractError):
            validate_comparison_contract(original, replication)

    def test_replication_interval_and_digest_are_required(self) -> None:
        original, replication = _merged_pair()
        for field, value in (
            ("source_start_tick", 0),
            ("source_end_tick", 500_000_000),
            ("source_event_timeline_digest", "wrong"),
        ):
            changed = copy.deepcopy(replication)
            changed[field] = value
            with self.subTest(field=field):
                with self.assertRaises(IntervalComparisonContractError):
                    validate_comparison_contract(original, changed)

    def test_axes_counts_digests_and_identity_controls_are_required(self) -> None:
        original, replication = _merged_pair()
        mutations = []
        missing_group = copy.deepcopy(replication)
        missing_group["groups"].pop()
        mutations.append(missing_group)
        missing_arm = copy.deepcopy(replication)
        missing_arm["groups"][0]["arms"].pop()
        mutations.append(missing_arm)
        wrong_arm_digest = copy.deepcopy(replication)
        wrong_arm_digest["groups"][0]["arms"][0][
            "second_contact_event_timeline_digest"
        ] = "wrong"
        mutations.append(wrong_arm_digest)
        failed_identity = copy.deepcopy(replication)
        failed_identity["groups"][0]["identical_control_passed"] = False
        mutations.append(failed_identity)
        nonzero_identity = copy.deepcopy(replication)
        first_role = next(iter(nonzero_identity["groups"][0]["identical_control_final_linf"]))
        nonzero_identity["groups"][0]["identical_control_final_linf"][first_role] = 1.0
        mutations.append(nonzero_identity)
        for index, changed in enumerate(mutations):
            with self.subTest(index=index):
                with self.assertRaises(IntervalComparisonContractError):
                    validate_comparison_contract(original, changed)

    def test_claim_or_selection_release_is_rejected(self) -> None:
        original, replication = _merged_pair()
        for field in DISABLED_FIELDS:
            changed = copy.deepcopy(replication)
            changed[field] = True
            with self.subTest(field=field):
                with self.assertRaises(IntervalComparisonContractError):
                    validate_comparison_contract(original, changed)


if __name__ == "__main__":
    unittest.main()
