"""Focused S1-PG acceptance for the passive intervention validator."""

from __future__ import annotations

import ast
from dataclasses import replace
import json
from pathlib import Path
import unittest

from mcm_field_organism.g2_d3_free_blocked_intervention_validator import (
    FAILURE_CODES,
    VALIDATION_PHASES,
    build_g2_d3_free_blocked_intervention_registry,
    validate_g2_d3_free_blocked_intervention,
)
from mcm_field_organism.g2_d3_schema_validator import (
    build_g2_d3_validation_registry,
    validate_g2_d3_anatomy_record,
)
from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1nr_fixtures import D3_V_MIXED
from tests.g2_d3_s1pg_free_blocked_intervention_fixtures import (
    BLOCKED_HELD_POST,
    EVENT_IDENTITY,
    FIXTURE_MANIFEST,
    FREE_AVAILABLE_POST,
    INVALID_ANATOMY_INPUTS,
    POSITIVE_INPUT_DIGESTS,
    POSITIVE_INPUTS,
    PRESTATE,
    SEMANTIC_EXPECTED,
    SEMANTIC_MUTATIONS,
)


class G2D3S1PGAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = build_g2_d3_free_blocked_intervention_registry()
        cls.anatomy_registry = build_g2_d3_validation_registry()

    def _validate(self, inputs=POSITIVE_INPUTS):
        return validate_g2_d3_free_blocked_intervention(
            *inputs,
            self.registry,
            self.anatomy_registry,
        )

    def test_01_registry_contract_and_public_surface_are_exact(self) -> None:
        self.assertEqual("S1_PE_G2_D3_FREE_BLOCKED_PAIR_V1", self.registry.fixture_id)
        self.assertEqual(0.125, self.registry.transfer_amount)
        self.assertEqual(
            "5d91f9c6c5d07cf098bfc9bb9e10131025d2e177795b6ab583b595ad75a244c1",
            self.registry.validator_contract_digest,
        )
        self.assertEqual(VALIDATION_PHASES, self.registry.validation_phases)
        self.assertEqual(18, len(FAILURE_CODES))

    def test_02_five_positive_input_digests_are_exact(self) -> None:
        self.assertEqual(POSITIVE_INPUT_DIGESTS, tuple(sha256_hex(item) for item in POSITIVE_INPUTS))
        self.assertEqual(POSITIVE_INPUT_DIGESTS[0], self.registry.prestate_input_bytes_digest)
        self.assertEqual(POSITIVE_INPUT_DIGESTS[4], self.registry.fixture_manifest_input_bytes_digest)

    def test_03_three_anatomy_records_are_individually_valid(self) -> None:
        for raw in POSITIVE_INPUTS[:3]:
            with self.subTest(digest=sha256_hex(raw)):
                receipt = validate_g2_d3_anatomy_record(raw, self.anatomy_registry)
                self.assertEqual("valid", receipt.validation_status)
                self.assertEqual((), receipt.failure_reasons)
        self.assertEqual(D3_V_MIXED, FREE_AVAILABLE_POST)

    def test_04_event_and_fixture_digests_are_canonical(self) -> None:
        for raw, digest_key in (
            (EVENT_IDENTITY, "event_identity_digest"),
            (FIXTURE_MANIFEST, "fixture_digest"),
        ):
            with self.subTest(digest_key=digest_key):
                value = json.loads(raw)
                declared = value.pop(digest_key)
                self.assertEqual(declared, sha256_hex(canonical_json_bytes(value)))
                value[digest_key] = declared
                self.assertEqual(raw, canonical_json_bytes(value))

    def test_05_positive_pair_receipt_is_complete_and_valid(self) -> None:
        receipt = self._validate()
        self.assertEqual("valid", receipt.validation_status)
        self.assertEqual((), receipt.failure_reasons)
        self.assertEqual(VALIDATION_PHASES, receipt.completed_checks)
        self.assertEqual(POSITIVE_INPUT_DIGESTS[:3], (
            receipt.prestate_input_bytes_digest,
            receipt.free_available_input_bytes_digest,
            receipt.blocked_held_input_bytes_digest,
        ))

    def test_06_resource_values_and_transfers_are_exact(self) -> None:
        pre, free_post, blocked_post = (json.loads(item) for item in POSITIVE_INPUTS[:3])
        self.assertEqual((0.375, 0.25, 0.25, 0.125), tuple(pre[key] for key in (
            "free", "bound_unconfigured", "bound_configured", "blocked"
        )))
        self.assertEqual((0.5, 0.25, 0.25, 0.0), tuple(free_post[key] for key in (
            "free", "bound_unconfigured", "bound_configured", "blocked"
        )))
        self.assertEqual((0.25, 0.25, 0.25, 0.25), tuple(blocked_post[key] for key in (
            "free", "bound_unconfigured", "bound_configured", "blocked"
        )))
        self.assertEqual(0.125, free_post["free"] - pre["free"])
        self.assertEqual(0.125, blocked_post["blocked"] - pre["blocked"])

    def test_07_seventeen_semantic_mutations_have_single_exact_codes(self) -> None:
        self.assertEqual(17, len(SEMANTIC_MUTATIONS))
        self.assertEqual(set(SEMANTIC_MUTATIONS), set(SEMANTIC_EXPECTED))
        for name, inputs in SEMANTIC_MUTATIONS.items():
            with self.subTest(name=name):
                receipt = self._validate(inputs)
                self.assertEqual("invalid", receipt.validation_status)
                self.assertEqual(SEMANTIC_EXPECTED[name], receipt.failure_reasons)

    def test_08_invalid_anatomy_record_has_single_wrapper_code(self) -> None:
        receipt = self._validate(INVALID_ANATOMY_INPUTS)
        self.assertEqual("invalid", receipt.validation_status)
        self.assertEqual(("PE_ANATOMY_RECORD_INVALID",), receipt.failure_reasons)

    def test_09_failures_are_sorted_unique_and_deterministic(self) -> None:
        inputs = SEMANTIC_MUTATIONS["local_conservation"]
        first = self._validate(inputs)
        second = self._validate(inputs)
        self.assertEqual(tuple(sorted(set(first.failure_reasons))), first.failure_reasons)
        self.assertEqual(first, second)

    def test_10_inputs_and_registries_remain_unchanged(self) -> None:
        inputs = POSITIVE_INPUTS
        registry = self.registry
        anatomy_registry = self.anatomy_registry
        self._validate(inputs)
        self.assertIs(inputs, POSITIVE_INPUTS)
        self.assertEqual(registry, self.registry)
        self.assertEqual(anatomy_registry, self.anatomy_registry)
        with self.assertRaises(ValueError):
            validate_g2_d3_free_blocked_intervention(
                *inputs,
                replace(registry, transfer_amount=0.25),
                anatomy_registry,
            )

    def test_11_wrong_api_types_fail_without_receipt(self) -> None:
        with self.assertRaises(TypeError):
            validate_g2_d3_free_blocked_intervention(
                bytearray(PRESTATE),
                *POSITIVE_INPUTS[1:],
                self.registry,
                self.anatomy_registry,
            )
        with self.assertRaises(TypeError):
            validate_g2_d3_free_blocked_intervention(
                *POSITIVE_INPUTS,
                object(),
                self.anatomy_registry,
            )

    def test_12_no_partial_commit_or_state_output_surface_exists(self) -> None:
        receipt = self._validate()
        payload = receipt.canonical_payload()
        self.assertFalse(any("raw_bytes" in key or "commit" in key for key in payload))
        self.assertIn("PD_PARTIAL_COMMIT_ATTEMPT", FAILURE_CODES)

    def test_13_candidate_records_contain_no_intervention_metadata(self) -> None:
        forbidden = {
            "arm_id",
            "blocked_held_arm_id",
            "causal_source_id",
            "fixture_id",
            "free_available_arm_id",
            "intervention_role",
            "transfer_amount",
        }
        for raw in POSITIVE_INPUTS[:3]:
            self.assertFalse(forbidden & json.loads(raw).keys())

    def test_14_digest_roles_and_receipt_digest_are_separate(self) -> None:
        receipt = self._validate()
        digest_values = {
            receipt.prestate_input_bytes_digest,
            receipt.free_available_input_bytes_digest,
            receipt.blocked_held_input_bytes_digest,
            receipt.event_identity_input_bytes_digest,
            receipt.fixture_manifest_input_bytes_digest,
            receipt.prestate_record_digest,
            receipt.free_available_record_digest,
            receipt.blocked_held_record_digest,
            receipt.event_identity_digest,
            receipt.fixture_digest,
            receipt.validator_contract_digest,
            receipt.validation_receipt_digest,
        }
        self.assertEqual(12, len(digest_values))
        payload = receipt.canonical_payload()
        digest = payload.pop("validation_receipt_digest")
        self.assertEqual(digest, sha256_hex(canonical_json_bytes(payload)))

    def test_15_import_surface_is_isolated(self) -> None:
        source_path = Path(__file__).parents[1] / "mcm_field_organism" / "g2_d3_free_blocked_intervention_validator.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        imported_surface = " ".join(imported).lower()
        for forbidden in (
            "g2_d3_admissibility",
            "g2_d3_two_step",
            "runner",
            "audio",
            "video",
            "browser",
            "socket",
            "requests",
        ):
            self.assertNotIn(forbidden, imported_surface)
        self.assertNotIn("validate_g2_d3_f1_pair", source)
        self.assertNotIn("open(", source.lower())


if __name__ == "__main__":
    unittest.main()
