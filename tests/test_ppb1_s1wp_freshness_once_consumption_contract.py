from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "docs"
    / "S1WP_PPB1_FRISCHE_EINMALIGKEITS_UND_VERBRAUCHSVERTRAG_V1.json"
)
EXPECTED_CONTRACT_DIGEST = (
    "905d7cb4da886a2e7d819938ebcae4108863f027dee6bbbf2c4823eb5c167850"
)


def load_contract():
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


class PPB1S1WPFreshnessOnceConsumptionContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        payload = load_contract()
        encoded = json.dumps(
            payload,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(
            EXPECTED_CONTRACT_DIGEST,
            hashlib.sha256(encoded).hexdigest(),
        )

    def test_parent_digests_and_static_scope_are_exact(self) -> None:
        contract = load_contract()
        self.assertEqual(
            "ab96a2bf9965fd6f31550a45817e77db6fd1d90a02dcb481ae4fdc078d4c9374",
            contract["parent_s1wo_preflight_digest"],
        )
        self.assertEqual(
            "c220857ae7974ed4ad7aa60676dc66c67574cd3dc94cf879b26cf220ade3e84b",
            contract["parent_s1wg_contract_digest"],
        )
        self.assertEqual(
            "STATIC_CONTRACT_ONLY_NO_IMPLEMENTATION_OR_EXECUTION",
            contract["scope"],
        )

    def test_freshness_is_causal_and_never_clock_based(self) -> None:
        binding = load_contract()["freshness_binding"]
        self.assertEqual(
            "CAUSAL_DIGEST_ADJACENCY_NOT_CLOCK_TIME",
            binding["basis"],
        )
        self.assertEqual(7, len(binding["required_before_h1"]))
        self.assertEqual(
            {
                "SYSTEM_TIME",
                "WALL_CLOCK_AGE",
                "FILE_MODIFICATION_TIME",
                "PRIOR_AUTHORIZATION_TEXT_WITH_NEW_EXECUTION_ID",
                "PRIOR_RESOURCE_GATE_DIGEST",
            },
            set(binding["forbidden_freshness_sources"]),
        )

    def test_state_machine_has_only_two_positive_transitions(self) -> None:
        machine = load_contract()["state_machine"]
        self.assertEqual(7, len(machine["states"]))
        self.assertEqual(
            (
                ("F0_UNSEEN", "F1_FRESH_H0D_VALIDATED_UNCONSUMED"),
                (
                    "F1_FRESH_H0D_VALIDATED_UNCONSUMED",
                    "F2_H1_LOCK_COMMITTED_AUTHORIZATION_CONSUMED",
                ),
            ),
            tuple(
                (transition["from"], transition["to"])
                for transition in machine["allowed_transitions"]
            ),
        )
        self.assertIn(
            "ANY_SECOND_H1_ATTEMPT_FOR_THE_SAME_EXECUTION_ID",
            machine["forbidden_transitions"],
        )

    def test_execution_id_and_authorization_are_never_reusable(self) -> None:
        binding = load_contract()["single_use_binding"]
        for role in (
            "same_authorization_text_reusable",
            "same_authorization_digest_reusable",
            "same_execution_id_reusable",
            "retry_permitted",
            "cleanup_reenables_execution_id",
        ):
            self.assertFalse(binding[role])

    def test_h1_lock_is_the_only_atomic_consumption_commit(self) -> None:
        commit = load_contract()["h1_atomic_consumption"]
        self.assertEqual(
            "EXCLUSIVE_CREATE_NO_REPLACE_DURABLE_CANONICAL_LOCK",
            commit["operation"],
        )
        self.assertEqual(
            "FULL_CANONICAL_H1_LOCK_DURABLY_VISIBLE",
            commit["single_commit_point"],
        )
        self.assertEqual(8, len(commit["lock_payload_must_bind"]))
        self.assertFalse(commit["separate_consumption_marker_allowed"])
        self.assertFalse(commit["lock_rewrite_allowed"])
        self.assertFalse(commit["lock_removal_allowed"])
        self.assertFalse(commit["h2_before_commit_allowed"])

    def test_reuse_stale_conflict_and_partial_states_fail_closed(self) -> None:
        rules = load_contract()["fail_closed_rules"]
        self.assertEqual(6, len(rules))
        decisions = {rule["decision"] for rule in rules}
        self.assertTrue(
            {
                "FB_REUSE_BLOCKED",
                "FB_STALE_BLOCKED",
                "FB_CONFLICT_BLOCKED",
                "FB_AMBIGUOUS_OR_PARTIAL_H1_BLOCKED",
            }.issubset(decisions)
        )
        self.assertTrue(
            all(
                "NO_RETRY" in rule["required_action"]
                for rule in rules
            )
        )

    def test_exact_six_production_blockers_remain(self) -> None:
        self.assertEqual(
            [
                "PRODUCTION_RESOURCE_OBSERVER_NOT_WIRED",
                "PRODUCTION_AUTHORIZATION_INSTANTIATION_LOCKED",
                "PRODUCTION_LOCK_TERMINAL_WRITERS_NOT_WIRED",
                "PRIVATE_REAL_PRODUCER_NOT_BOUND",
                "PRODUCTION_ARTIFACT_PATH_NOT_WIRED",
                "PRODUCTION_ENTRYPOINT_HARD_BLOCKED",
            ],
            load_contract()["production_blockers"],
        )

    def test_comparison_direction_and_equal_budget_remain_binding(self) -> None:
        comparison = load_contract()["comparison_direction"]
        self.assertTrue(comparison["equal_budget_required"])
        self.assertTrue(comparison["equal_capacity_required"])
        self.assertTrue(comparison["equal_later_probe_required"])
        self.assertEqual(
            [
                "NO_MEMORY",
                "REPLAY_OR_RAW_DATA_ACCESS",
                "SIMPLE_STATIC_PROTOTYPE_BANK_OR_VECTOR_QUANTIZATION",
                "MOVING_STATISTIC_OR_REVERBERATION",
                "ATTRACTOR_OR_HOPFIELD_STYLE",
                "BOUNDED_DYNAMIC_RESERVOIR_STATE",
            ],
            comparison["baselines"],
        )

    def test_all_implementation_execution_and_claim_paths_are_prohibited(self) -> None:
        prohibitions = set(load_contract()["current_prohibitions"])
        self.assertEqual(9, len(prohibitions))
        self.assertTrue(
            {
                "NO_RUNTIME_OR_ADAPTER_IMPLEMENTATION",
                "NO_RECEIPT_ADAPTER_OR_COORDINATOR_EXECUTION",
                "NO_PPB1_PRODUCTION",
                "NO_REAL_FIELD_OR_MEDIA_RUN",
                "NO_COMPARISON_DECISION",
                "NO_MEMORY_OR_FIELD_CAUSATION_CLAIM",
            }.issubset(prohibitions)
        )


if __name__ == "__main__":
    unittest.main()
