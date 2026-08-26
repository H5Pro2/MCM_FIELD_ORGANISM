from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "docs"
    / "S1WG_PPB1_PRODUKTIONSINTEGRATIONSDELTA_VERTRAG_V1.json"
)
EXPECTED_CONTRACT_DIGEST = (
    "c220857ae7974ed4ad7aa60676dc66c67574cd3dc94cf879b26cf220ade3e84b"
)
EXPECTED_BLOCKERS = (
    "PRODUCTION_RESOURCE_OBSERVER_NOT_WIRED",
    "PRODUCTION_AUTHORIZATION_INSTANTIATION_LOCKED",
    "PRODUCTION_LOCK_TERMINAL_WRITERS_NOT_WIRED",
    "PRIVATE_REAL_PRODUCER_NOT_BOUND",
    "PRODUCTION_ARTIFACT_PATH_NOT_WIRED",
    "PRODUCTION_ENTRYPOINT_HARD_BLOCKED",
)


def load_contract() -> dict[str, object]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


class PPB1S1WGProductionIntegrationDeltaContractTests(unittest.TestCase):
    def test_contract_digest_is_canonical(self) -> None:
        payload = load_contract()
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(
            EXPECTED_CONTRACT_DIGEST,
            hashlib.sha256(encoded).hexdigest(),
        )

    def test_parent_preflight_plan_and_resource_budget_are_exact(self) -> None:
        payload = load_contract()
        self.assertEqual(
            "bdd1f9652ac2cd094d794c4a589a2eeae90ca5357f5ccf34863f1368e99c96af",
            payload["parent_preflight_digest"],
        )
        self.assertEqual(528, payload["case_count"])
        self.assertEqual(75808, payload["maximum_registered_call_count"])
        self.assertEqual(2 * 1024**3, payload["minimum_free_memory_bytes"])
        self.assertEqual(1024**3, payload["minimum_free_disk_bytes"])
        self.assertEqual(
            "data/generated/ppb1/one_shot",
            payload["production_artifact_root"],
        )

    def test_exact_six_blockers_have_unique_roles_and_stops(self) -> None:
        deltas = load_contract()["integration_deltas"]
        self.assertEqual(EXPECTED_BLOCKERS, tuple(item["blocker"] for item in deltas))
        self.assertEqual(6, len({item["required_role"] for item in deltas}))
        self.assertTrue(all(item["precondition"] for item in deltas))
        self.assertTrue(all(item["integration"] for item in deltas))
        self.assertTrue(all(item["stop"] for item in deltas))

    def test_h0_and_h1_to_h7_orders_are_exact(self) -> None:
        payload = load_contract()
        self.assertEqual(
            (
                "H0A_VALIDATE_CONTRACT_PLAN_PLATFORM_AND_SOURCE_DIGESTS",
                "H0B_VALIDATE_EXACT_PRODUCTION_ROOT_SAME_VOLUME_AND_ATOMIC_CAPABILITY",
                "H0C_OBSERVE_IMMEDIATE_MEMORY_AND_DISK_AND_BUILD_RESOURCE_GATE",
                "H0D_VALIDATE_EXACT_FRESH_AUTHORIZATION_AND_UNUSED_EXECUTION_ID",
                "H0E_REVALIDATE_LOCK_SUCCESS_ERROR_AND_TEMP_PATHS_FREE",
            ),
            tuple(payload["h0_order"]),
        )
        self.assertEqual(
            tuple(f"H{index}" for index in range(1, 8)),
            tuple(item.split("_", 1)[0] for item in payload["h1_to_h7_order"]),
        )

    def test_generic_or_prior_authorization_is_explicitly_rejected(self) -> None:
        policy = load_contract()["authorization_policy"]
        self.assertTrue(policy["fresh_execution_id_required"])
        self.assertTrue(policy["immediate_resource_gate_digest_required"])
        self.assertTrue(
            policy["authorization_consumed_before_first_producer_resolution"]
        )
        self.assertFalse(policy["retry_permitted"])
        self.assertFalse(policy["generic_commands_are_authorization"])
        self.assertFalse(policy["prior_authorizations_are_reusable"])
        self.assertFalse(policy["template_alone_is_authorization"])

    def test_producer_is_structurally_dominated_by_h1_lock(self) -> None:
        payload = load_contract()
        producer = next(
            item
            for item in payload["integration_deltas"]
            if item["blocker"] == "PRIVATE_REAL_PRODUCER_NOT_BOUND"
        )
        self.assertEqual(
            "H1_DURABLE_LOCK_EXISTS_AND_AUTHORIZATION_IS_CONSUMED",
            producer["precondition"],
        )
        self.assertIn(
            "NO_PRODUCER_IMPORT_OR_RESOLUTION_BEFORE_DURABLE_H1_LOCK",
            payload["coordinator_rules"],
        )
        self.assertIn(
            "PRODUCER_RESOLUTION_DOMINATED_BY_SUCCESSFUL_H1_LOCK",
            payload["implementation_acceptance"],
        )

    def test_lock_terminal_and_partial_result_rules_are_closed(self) -> None:
        rules = set(load_contract()["coordinator_rules"])
        self.assertTrue(
            {
                "LOCK_IS_NEVER_REMOVED_OR_REWRITTEN",
                "SUCCESS_AND_ERROR_ARE_MUTUALLY_EXCLUSIVE",
                "TERMINAL_PUBLICATION_MUST_NOT_REPLACE_AN_EXISTING_TARGET",
                "NO_PARTIAL_MATRIX_COMPOSITION_OR_EVALUATION_ARTIFACT",
                "ANY_FAILURE_AFTER_H1_PUBLISHES_ONLY_TERMINAL_ERROR_AND_FORBIDS_RETRY",
            }.issubset(rules)
        )

    def test_contract_remains_static_and_execution_free(self) -> None:
        prohibitions = set(load_contract()["current_prohibitions"])
        self.assertEqual(
            {
                "NO_COORDINATOR_IMPLEMENTATION",
                "NO_AUTHORIZATION_INSTANTIATION",
                "NO_RESOURCE_OBSERVATION",
                "NO_FILESYSTEM_WRITE",
                "NO_PRIVATE_REAL_PRODUCER_RESOLUTION_OR_CALL",
                "NO_REGISTERED_MATRIX_PATH",
                "NO_PRODUCTION_ARTIFACT",
                "NO_FIELD_OR_MEDIA_RUNTIME",
            },
            prohibitions,
        )


if __name__ == "__main__":
    unittest.main()
