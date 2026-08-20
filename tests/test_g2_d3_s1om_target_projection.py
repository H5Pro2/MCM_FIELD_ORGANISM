"""Focused S1-OM acceptance for pure G2/D3 target projection."""

from __future__ import annotations

import ast
from dataclasses import fields, replace
from fractions import Fraction
import json
from pathlib import Path
import unittest

from mcm_field_organism.g2_d3_halving_amount import build_g2_d3_halving_amount_registry
from mcm_field_organism.g2_d3_schema_validator import build_g2_d3_validation_registry
from mcm_field_organism.g2_d3_target_projection import (
    G2D3TargetProjectionReceipt,
    PROJECTOR_CONTRACT_DIGEST,
    build_g2_d3_target_commit_registry,
    project_g2_d3_conservative_target,
)
from mcm_field_organism.g2_d3_transient_boundary_validator import (
    build_g2_d3_transient_boundary_registry,
)
from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1om_fixtures import (
    BOUND_DIGESTS,
    D3_OL_SECOND_TARGET,
    EXPECTED_TARGETS,
    NEGATIVE_FIXTURES,
    NEGATIVE_INPUT_DIGESTS,
    NULL_FIXTURE_NAMES,
    OL_V_MIXED_XX_BOUNDARY,
    POSITIVE_FIXTURES,
    POSITIVE_INPUT_DIGESTS,
    fixture_input_digests,
    record,
)


class G2D3S1OMAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.target_registry = build_g2_d3_target_commit_registry()
        cls.amount_registry = build_g2_d3_halving_amount_registry()
        cls.boundary_registry = build_g2_d3_transient_boundary_registry()
        cls.d3_registry = build_g2_d3_validation_registry()

    def project(self, fixture):
        boundary_raw, source_raw, formation_enabled = fixture
        return project_g2_d3_conservative_target(
            boundary_raw,
            source_raw,
            formation_enabled,
            self.target_registry,
            self.amount_registry,
            self.boundary_registry,
            self.d3_registry,
        )

    def test_01_fixture_and_target_digests_are_bound(self) -> None:
        self.assertEqual(10, len(POSITIVE_FIXTURES))
        for name, fixture in POSITIVE_FIXTURES.items():
            with self.subTest(name=name):
                self.assertEqual(POSITIVE_INPUT_DIGESTS[name], fixture_input_digests(fixture))
        for name, fixture in NEGATIVE_FIXTURES.items():
            with self.subTest(name=name):
                self.assertEqual(NEGATIVE_INPUT_DIGESTS[name], fixture_input_digests(fixture))
        mixed_boundary = json.loads(OL_V_MIXED_XX_BOUNDARY)
        self.assertEqual(BOUND_DIGESTS["mixed_boundary_record"], mixed_boundary["boundary_record_digest"])
        first = record(EXPECTED_TARGETS["OL_V_XX_ON"])
        second = record(D3_OL_SECOND_TARGET)
        self.assertEqual(BOUND_DIGESTS["first_target_resource"], first["resource_account_digest"])
        self.assertEqual(BOUND_DIGESTS["first_target_projection"], first["aggregate_projection_digest"])
        self.assertEqual(BOUND_DIGESTS["first_target_record"], first["anatomy_record_digest"])
        self.assertEqual(BOUND_DIGESTS["first_target_input"], sha256_hex(EXPECTED_TARGETS["OL_V_XX_ON"]))
        self.assertEqual(BOUND_DIGESTS["second_target_resource"], second["resource_account_digest"])
        self.assertEqual(BOUND_DIGESTS["second_target_projection"], second["aggregate_projection_digest"])
        self.assertEqual(BOUND_DIGESTS["second_target_record"], second["anatomy_record_digest"])
        self.assertEqual(BOUND_DIGESTS["second_target_input"], sha256_hex(D3_OL_SECOND_TARGET))

    def test_02_ten_valid_controls_have_exact_status_and_target(self) -> None:
        for name, fixture in POSITIVE_FIXTURES.items():
            with self.subTest(name=name):
                result = self.project(fixture)
                expected_status = "NO_CHANGE" if name in NULL_FIXTURE_NAMES else "PROJECTED"
                self.assertEqual("valid", result.receipt.evaluation_status)
                self.assertEqual((), result.receipt.failure_reasons)
                self.assertEqual(expected_status, result.receipt.projection_status)
                self.assertEqual(EXPECTED_TARGETS[name], result.target_d3_raw_bytes)

    def test_03_seven_null_paths_preserve_source_byte_objects(self) -> None:
        self.assertEqual(7, len(NULL_FIXTURE_NAMES))
        for name in NULL_FIXTURE_NAMES:
            with self.subTest(name=name):
                fixture = POSITIVE_FIXTURES[name]
                result = self.project(fixture)
                self.assertIs(fixture[1], result.target_d3_raw_bytes)
                self.assertEqual(sha256_hex(fixture[1]), result.receipt.target_d3_input_bytes_digest)

    def test_04_xx_and_yy_targets_are_bit_identical(self) -> None:
        xx = self.project(POSITIVE_FIXTURES["OL_V_XX_ON"])
        yy = self.project(POSITIVE_FIXTURES["OL_V_YY_ON"])
        self.assertEqual(EXPECTED_TARGETS["OL_V_XX_ON"], xx.target_d3_raw_bytes)
        self.assertEqual(xx.target_d3_raw_bytes, yy.target_d3_raw_bytes)
        self.assertEqual(xx.receipt.target_anatomy_record_digest, yy.receipt.target_anatomy_record_digest)

    def test_05_second_fresh_continuation_has_exact_target(self) -> None:
        result = self.project(POSITIVE_FIXTURES["OL_V_MIXED_XX_ON"])
        target = record(result.target_d3_raw_bytes)
        self.assertEqual(0.125, result.receipt.computed_repartition_amount)
        self.assertEqual((0.125, 0.375), (target["bound_unconfigured"], target["bound_configured"]))
        self.assertEqual(D3_OL_SECOND_TARGET, result.target_d3_raw_bytes)

    def test_06_positive_targets_preserve_roles_and_exact_identity(self) -> None:
        for name in ("OL_V_XX_ON", "OL_V_YY_ON", "OL_V_MIXED_XX_ON"):
            with self.subTest(name=name):
                fixture = POSITIVE_FIXTURES[name]
                source = record(fixture[1])
                result = self.project(fixture)
                target = record(result.target_d3_raw_bytes)
                for key in (
                    "schema_id", "schema_version", "candidate_class_id", "geometry_digest",
                    "field_reference_digest", "edge_id", "carrier_a_id", "carrier_b_id",
                    "capacity", "free", "blocked",
                ):
                    self.assertEqual(source[key], target[key])
                source_bound = Fraction.from_float(source["bound_unconfigured"]) + Fraction.from_float(source["bound_configured"])
                target_bound = Fraction.from_float(target["bound_unconfigured"]) + Fraction.from_float(target["bound_configured"])
                self.assertEqual(source_bound, target_bound)
                self.assertEqual(source["aggregate_projection_digest"], target["aggregate_projection_digest"])
                self.assertNotEqual(source["resource_account_digest"], target["resource_account_digest"])
                self.assertNotEqual(source["anatomy_record_digest"], target["anatomy_record_digest"])

    def test_07_five_amount_failures_are_single_gated(self) -> None:
        self.assertEqual(5, len(NEGATIVE_FIXTURES))
        for name, fixture in NEGATIVE_FIXTURES.items():
            with self.subTest(name=name):
                result = self.project(fixture)
                self.assertEqual("not_computable", result.target_d3_raw_bytes)
                self.assertEqual("invalid", result.receipt.evaluation_status)
                self.assertEqual("not_computable", result.receipt.projection_status)
                self.assertEqual(("OK_PROJECTION_AMOUNT_EVALUATION_FAILED",), result.receipt.failure_reasons)

    def test_08_digest_roles_and_receipt_digest_are_separate(self) -> None:
        result = self.project(POSITIVE_FIXTURES["OL_V_XX_ON"])
        receipt = result.receipt
        digests = {
            receipt.boundary_input_bytes_digest,
            receipt.source_d3_input_bytes_digest,
            receipt.amount_evaluation_receipt_digest,
            receipt.source_anatomy_record_digest,
            receipt.target_d3_input_bytes_digest,
            receipt.target_anatomy_record_digest,
            receipt.target_validation_receipt_digest,
            receipt.projector_contract_digest,
            receipt.projection_receipt_digest,
        }
        self.assertEqual(9, len(digests))
        self.assertEqual(PROJECTOR_CONTRACT_DIGEST, receipt.projector_contract_digest)
        payload = receipt.canonical_payload()
        digest = payload.pop("projection_receipt_digest")
        self.assertEqual(digest, sha256_hex(canonical_json_bytes(payload)))

    def test_09_same_inputs_produce_identical_results(self) -> None:
        first = self.project(POSITIVE_FIXTURES["OL_V_XX_ON"])
        second = self.project(POSITIVE_FIXTURES["OL_V_XX_ON"])
        self.assertEqual(first, second)
        self.assertEqual(first.receipt.canonical_payload(), second.receipt.canonical_payload())

    def test_10_inputs_and_registries_remain_unchanged(self) -> None:
        fixture = POSITIVE_FIXTURES["OL_V_XX_ON"]
        original = (
            self.target_registry,
            self.amount_registry,
            self.boundary_registry,
            self.d3_registry,
        )
        self.project(fixture)
        self.assertIs(fixture[0], POSITIVE_FIXTURES["OL_V_XX_ON"][0])
        self.assertIs(fixture[1], POSITIVE_FIXTURES["OL_V_XX_ON"][1])
        self.assertEqual(original, (self.target_registry, self.amount_registry, self.boundary_registry, self.d3_registry))

    def test_11_wrong_api_inputs_and_receipts_fail_before_result(self) -> None:
        boundary_raw, source_raw, enabled = POSITIVE_FIXTURES["OL_V_XX_ON"]
        tail = (self.target_registry, self.amount_registry, self.boundary_registry, self.d3_registry)
        with self.assertRaises(TypeError):
            project_g2_d3_conservative_target(bytearray(boundary_raw), source_raw, enabled, *tail)
        with self.assertRaises(TypeError):
            project_g2_d3_conservative_target(boundary_raw, bytearray(source_raw), enabled, *tail)
        with self.assertRaises(TypeError):
            project_g2_d3_conservative_target(boundary_raw, source_raw, 1, *tail)
        with self.assertRaises(ValueError):
            project_g2_d3_conservative_target(
                boundary_raw, source_raw, enabled,
                replace(self.target_registry, projection_receipt_schema_version="changed"),
                self.amount_registry, self.boundary_registry, self.d3_registry,
            )
        valid = self.project(POSITIVE_FIXTURES["OL_V_XX_ON"])
        with self.assertRaises(TypeError):
            project_g2_d3_conservative_target(
                valid.receipt, source_raw, enabled, *tail
            )

    def test_12_module_surface_has_no_commit_or_runtime_path(self) -> None:
        source_path = Path(__file__).parents[1] / "mcm_field_organism" / "g2_d3_target_projection.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = []
        functions = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
            elif isinstance(node, ast.FunctionDef):
                functions.add(node.name)
        self.assertNotIn("verify_and_commit_g2_d3_projected_target", functions)
        imported_surface = " ".join(imported).lower()
        for forbidden in (
            "admissibility", "field", "transfer", "runner", "audio", "video",
            "browser", "socket", "requests",
        ):
            self.assertNotIn(forbidden, imported_surface)
        lowered = source.lower()
        self.assertNotIn("open(", lowered)
        self.assertNotIn("write_text", lowered)
        self.assertNotIn("write_bytes", lowered)
        receipt_fields = {item.name for item in fields(G2D3TargetProjectionReceipt)}
        for forbidden_field in ("current_d3_raw_bytes", "commit_status", "field_state", "o3_value"):
            self.assertNotIn(forbidden_field, receipt_fields)


if __name__ == "__main__":
    unittest.main()
