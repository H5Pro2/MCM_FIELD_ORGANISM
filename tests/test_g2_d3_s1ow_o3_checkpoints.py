"""Focused S1-OW acceptance for read-only two-step O3 checkpoints."""

from __future__ import annotations

import ast
from dataclasses import fields, replace
from pathlib import Path
import unittest

from mcm_field_organism.g2_d3_admissibility import (
    evaluate_g2_d3_local_admissible_engagement,
)
from mcm_field_organism.g2_d3_halving_amount import (
    build_g2_d3_halving_amount_registry,
)
from mcm_field_organism.g2_d3_schema_validator import build_g2_d3_validation_registry
from mcm_field_organism.g2_d3_target_projection import (
    build_g2_d3_target_commit_registry,
)
from mcm_field_organism.g2_d3_transient_boundary_validator import (
    build_g2_d3_transient_boundary_registry,
)
from mcm_field_organism.g2_d3_two_step_composition import (
    build_g2_d3_two_step_composition_registry,
)
from mcm_field_organism.g2_d3_two_step_o3_checkpoints import (
    CHECKPOINT_CLASS_ID,
    CHECKPOINT_CONTRACT_DIGEST,
    CHECKPOINT_PHASES,
    CHECKPOINT_ROLES,
    COMPARISON_DIGEST,
    FAILURE_CODES,
    G2D3TwoStepO3CheckpointReceipt,
    G2D3TwoStepO3CheckpointResult,
    build_g2_d3_two_step_o3_checkpoint_registry,
    evaluate_g2_d3_two_step_o3_checkpoints,
)
from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1nr_fixtures import D3_V_C0, D3_V_MIXED
from tests.g2_d3_s1om_fixtures import D3_OL_SECOND_TARGET
from tests.g2_d3_s1ow_o3_checkpoint_fixtures import (
    DEFENSIVE_CODES,
    EXPECTED_CHAIN_ROLES,
    EXPECTED_COMPARISON_DIGEST,
    EXPECTED_COMPONENTS,
    EXPECTED_VALUES,
    SEQUENCE_FAILURE_FIXTURES,
    VALID_CHECKPOINT_FIXTURES,
)


class G2D3S1OWO3CheckpointAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).parents[1]
        cls.sources = {
            relative: (root / relative).read_text(encoding="utf-8")
            for relative in (
                "mcm_field_organism/g2_d3_two_step_composition.py",
                "mcm_field_organism/g2_d3_two_step_o3_checkpoints.py",
            )
        }
        cls.checkpoint_registry = build_g2_d3_two_step_o3_checkpoint_registry()
        cls.sequence_registry = build_g2_d3_two_step_composition_registry()
        cls.target_registry = build_g2_d3_target_commit_registry()
        cls.amount_registry = build_g2_d3_halving_amount_registry()
        cls.boundary_registry = build_g2_d3_transient_boundary_registry()
        cls.d3_registry = build_g2_d3_validation_registry()

    def evaluate(self, fixture):
        first, second, initial, enabled = fixture
        return evaluate_g2_d3_two_step_o3_checkpoints(
            first,
            second,
            initial,
            enabled,
            self.checkpoint_registry,
            self.sequence_registry,
            self.target_registry,
            self.amount_registry,
            self.boundary_registry,
            self.d3_registry,
        )

    def test_01_frozen_regression_file_digests_are_unchanged(self) -> None:
        root = Path(__file__).parents[1]
        expected = {
            "mcm_field_organism/g2_d3_admissibility.py":
                "00ac323fdf26a68b7b86c751c5c7fe8d4a2456aee0e76fca41499e959202a96e",
            "tests/g2_d3_s1os_fixtures.py":
                "58cd3e4505657fc6b964cb0dbc370d22e94261e626e67f652d43670e22f79a41",
            "tests/test_g2_d3_s1os_two_step_composition.py":
                "f96527e4d7611a47c5e5cf1c083ed9d3db59ead3564ea6e2e0a81c379b4cbae6",
        }
        for relative, digest in expected.items():
            with self.subTest(relative=relative):
                self.assertEqual(digest, sha256_hex((root / relative).read_bytes()))

    def test_02_registry_records_and_contract_digests_are_bound(self) -> None:
        registry = self.checkpoint_registry
        self.assertEqual(CHECKPOINT_CLASS_ID, registry.checkpoint_class_id)
        self.assertEqual(CHECKPOINT_ROLES, registry.checkpoint_roles)
        self.assertEqual(CHECKPOINT_PHASES, registry.checkpoint_phases)
        self.assertEqual(FAILURE_CODES, registry.failure_codes)
        self.assertEqual(CHECKPOINT_CONTRACT_DIGEST, registry.checkpoint_contract_digest)
        self.assertEqual(3, len(registry.checkpoint_records))
        self.assertEqual((0, 1, 2), tuple(item.checkpoint_position for item in registry.checkpoint_records))
        self.assertEqual(EXPECTED_VALUES, tuple(item.expected_o3_value for item in registry.checkpoint_records))
        self.assertEqual(
            (
                "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
                "2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
                "a0e9a2468571ab2a3c437f8d436958b5c0eef886ad1e7f3d2b4ce54d278e7bab",
            ),
            tuple(item.d3_input_bytes_digest for item in registry.checkpoint_records),
        )

    def test_03_xxx_has_exact_role_values_and_o3_receipts(self) -> None:
        result = self.evaluate(VALID_CHECKPOINT_FIXTURES["OV_V_XXX"])
        receipt = result.receipt
        self.assertEqual(EXPECTED_VALUES, result.checkpoint_values)
        self.assertEqual(EXPECTED_CHAIN_ROLES["OV_V_XXX"], receipt.chain_role)
        self.assertEqual("THREE_CHECKPOINTS_EVALUATED", receipt.checkpoint_status)
        self.assertEqual("valid", receipt.validation_status)
        self.assertEqual((), receipt.failure_reasons)
        self.assertNotIn(
            "not_computable",
            (receipt.cp0_o3_receipt_digest, receipt.cp1_o3_receipt_digest, receipt.cp2_o3_receipt_digest),
        )

    def test_04_yyy_matches_vector_but_has_distinct_provenance(self) -> None:
        xxx = self.evaluate(VALID_CHECKPOINT_FIXTURES["OV_V_XXX"])
        yyy = self.evaluate(VALID_CHECKPOINT_FIXTURES["OV_V_YYY"])
        self.assertEqual(EXPECTED_VALUES, yyy.checkpoint_values)
        self.assertEqual(EXPECTED_CHAIN_ROLES["OV_V_YYY"], yyy.receipt.chain_role)
        self.assertEqual(xxx.receipt.comparison_digest, yyy.receipt.comparison_digest)
        self.assertEqual(EXPECTED_COMPARISON_DIGEST, yyy.receipt.comparison_digest)
        self.assertNotEqual(
            xxx.receipt.checkpoint_receipt_digest,
            yyy.receipt.checkpoint_receipt_digest,
        )

    def test_05_o3_receipts_match_direct_read_only_evaluations(self) -> None:
        expected_receipts = tuple(
            evaluate_g2_d3_local_admissible_engagement(raw_bytes, self.d3_registry)
            for raw_bytes in (D3_V_C0, D3_V_MIXED, D3_OL_SECOND_TARGET)
        )
        expected_digests = tuple(item.admissibility_receipt_digest for item in expected_receipts)
        for name, fixture in VALID_CHECKPOINT_FIXTURES.items():
            with self.subTest(name=name):
                receipt = self.evaluate(fixture).receipt
                self.assertEqual(
                    expected_digests,
                    (
                        receipt.cp0_o3_receipt_digest,
                        receipt.cp1_o3_receipt_digest,
                        receipt.cp2_o3_receipt_digest,
                    ),
                )

    def test_06_components_and_halving_identities_are_exact(self) -> None:
        receipt = self.evaluate(VALID_CHECKPOINT_FIXTURES["OV_V_XXX"]).receipt
        components = (
            receipt.delta_cp1_cp0,
            receipt.delta_cp2_cp1,
            receipt.delta_cp2_cp0,
        )
        self.assertEqual(EXPECTED_COMPONENTS, components)
        self.assertEqual(receipt.cp0_value / 2, receipt.cp1_value)
        self.assertEqual(receipt.cp1_value / 2, receipt.cp2_value)
        self.assertEqual(COMPARISON_DIGEST, receipt.comparison_digest)

    def test_07_passive_receipt_is_closed_and_digest_is_reconstructable(self) -> None:
        receipt = self.evaluate(VALID_CHECKPOINT_FIXTURES["OV_V_XXX"]).receipt
        payload = receipt.canonical_payload()
        digest = payload.pop("checkpoint_receipt_digest")
        self.assertEqual(digest, sha256_hex(canonical_json_bytes(payload)))
        receipt_fields = {item.name for item in fields(G2D3TwoStepO3CheckpointReceipt)}
        for forbidden in (
            "initial_d3_raw_bytes",
            "intermediate_d3_raw_bytes",
            "final_d3_raw_bytes",
            "execution_trace",
            "composition_receipt",
            "o3_receipt",
        ):
            self.assertNotIn(forbidden, receipt_fields)

    def test_08_all_sequence_failures_suppress_the_complete_vector(self) -> None:
        self.assertEqual(7, len(SEQUENCE_FAILURE_FIXTURES))
        for name, fixture in SEQUENCE_FAILURE_FIXTURES.items():
            with self.subTest(name=name):
                result = self.evaluate(fixture)
                receipt = result.receipt
                self.assertEqual("not_computable", result.checkpoint_values)
                self.assertEqual("not_computable", receipt.checkpoint_status)
                self.assertEqual("invalid", receipt.validation_status)
                self.assertEqual(("OU_TWO_STEP_EXECUTION_FAILED",), receipt.failure_reasons)
                self.assertEqual(
                    ("not_computable",) * 6,
                    (
                        receipt.cp0_value,
                        receipt.cp1_value,
                        receipt.cp2_value,
                        receipt.delta_cp1_cp0,
                        receipt.delta_cp2_cp1,
                        receipt.delta_cp2_cp0,
                    ),
                )

    def test_09_sequence_failure_completed_checks_stop_before_o3(self) -> None:
        for name, fixture in SEQUENCE_FAILURE_FIXTURES.items():
            with self.subTest(name=name):
                receipt = self.evaluate(fixture).receipt
                self.assertEqual(
                    ("api_intake", "two_step_execution", "persistence_guard", "checkpoint_receipt"),
                    receipt.completed_checks,
                )
                self.assertEqual(
                    ("not_computable",) * 3,
                    (
                        receipt.cp0_o3_receipt_digest,
                        receipt.cp1_o3_receipt_digest,
                        receipt.cp2_o3_receipt_digest,
                    ),
                )

    def test_10_determinism_inputs_and_registries_are_immutable(self) -> None:
        fixture = VALID_CHECKPOINT_FIXTURES["OV_V_XXX"]
        registries = (
            self.checkpoint_registry,
            self.sequence_registry,
            self.target_registry,
            self.amount_registry,
            self.boundary_registry,
            self.d3_registry,
        )
        first = self.evaluate(fixture)
        second = self.evaluate(fixture)
        self.assertEqual(first, second)
        self.assertIs(fixture, VALID_CHECKPOINT_FIXTURES["OV_V_XXX"])
        self.assertEqual(
            registries,
            (
                self.checkpoint_registry,
                self.sequence_registry,
                self.target_registry,
                self.amount_registry,
                self.boundary_registry,
                self.d3_registry,
            ),
        )

    def test_11_wrong_types_registries_and_receipts_fail_before_result(self) -> None:
        first, second, initial, enabled = VALID_CHECKPOINT_FIXTURES["OV_V_XXX"]
        registries = (
            self.checkpoint_registry,
            self.sequence_registry,
            self.target_registry,
            self.amount_registry,
            self.boundary_registry,
            self.d3_registry,
        )
        for inputs in (
            (bytearray(first), second, initial, enabled),
            (first, bytearray(second), initial, enabled),
            (first, second, bytearray(initial), enabled),
            (first, second, initial, 1),
        ):
            with self.assertRaises(TypeError):
                evaluate_g2_d3_two_step_o3_checkpoints(*inputs, *registries)
        with self.assertRaises(ValueError):
            evaluate_g2_d3_two_step_o3_checkpoints(
                first,
                second,
                initial,
                enabled,
                replace(self.checkpoint_registry, receipt_schema_version="changed"),
                *registries[1:],
            )
        for index in range(1, 6):
            altered = list(registries)
            altered[index] = object()
            with self.assertRaises(TypeError):
                evaluate_g2_d3_two_step_o3_checkpoints(
                    first, second, initial, enabled, *altered
                )
        valid = self.evaluate(VALID_CHECKPOINT_FIXTURES["OV_V_XXX"])
        with self.assertRaises(TypeError):
            evaluate_g2_d3_two_step_o3_checkpoints(
                valid.receipt, second, initial, enabled, *registries
            )

    def test_12_all_codes_exist_without_defensive_fake_fixtures(self) -> None:
        self.assertEqual(7, len(FAILURE_CODES))
        self.assertEqual(FAILURE_CODES, self.checkpoint_registry.failure_codes)
        self.assertEqual(6, len(DEFENSIVE_CODES))
        self.assertTrue(set(DEFENSIVE_CODES).issubset(FAILURE_CODES))
        source = self._source("mcm_field_organism/g2_d3_two_step_o3_checkpoints.py")
        for code in DEFENSIVE_CODES:
            self.assertIn(f'"{code}"', source)
        self.assertIn("return fail(failure_codes[index])", source)
        self.assertTrue(
            all(name.startswith("OV_I_") for name in SEQUENCE_FAILURE_FIXTURES)
        )

    def test_13_public_paths_share_only_the_private_executor(self) -> None:
        composition_tree = ast.parse(
            self._source("mcm_field_organism/g2_d3_two_step_composition.py")
        )
        checkpoint_tree = ast.parse(
            self._source("mcm_field_organism/g2_d3_two_step_o3_checkpoints.py")
        )
        compose = self._function(composition_tree, "compose_g2_d3_two_step_continuation")
        evaluate = self._function(checkpoint_tree, "evaluate_g2_d3_two_step_o3_checkpoints")
        self.assertEqual(1, self._call_count(compose, "_execute_g2_d3_two_step"))
        self.assertEqual(1, self._call_count(evaluate, "_execute_g2_d3_two_step"))
        self.assertEqual(0, self._call_count(evaluate, "compose_g2_d3_two_step_continuation"))

    def test_14_private_trace_is_not_public_or_persisted(self) -> None:
        import mcm_field_organism.g2_d3_two_step_composition as composition_module
        import mcm_field_organism.g2_d3_two_step_o3_checkpoints as checkpoint_module

        self.assertNotIn("_G2D3TwoStepExecutionTrace", composition_module.__all__)
        self.assertNotIn("_execute_g2_d3_two_step", composition_module.__all__)
        self.assertNotIn("trace", " ".join(checkpoint_module.__all__).lower())
        result_fields = {item.name for item in fields(G2D3TwoStepO3CheckpointResult)}
        self.assertEqual({"checkpoint_values", "receipt"}, result_fields)
        lowered = self._source("mcm_field_organism/g2_d3_two_step_o3_checkpoints.py").lower()
        for forbidden in ("global ", "cache", "write_text", "write_bytes", "open("):
            self.assertNotIn(forbidden, lowered)

    def test_15_valid_order_contains_all_phases_and_checkpoint_identities(self) -> None:
        receipt = self.evaluate(VALID_CHECKPOINT_FIXTURES["OV_V_XXX"]).receipt
        self.assertEqual(CHECKPOINT_PHASES, receipt.completed_checks)
        records = self.checkpoint_registry.checkpoint_records
        self.assertEqual(
            tuple(item.d3_input_bytes_digest for item in records),
            (
                receipt.cp0_d3_input_bytes_digest,
                receipt.cp1_d3_input_bytes_digest,
                receipt.cp2_d3_input_bytes_digest,
            ),
        )
        self.assertEqual(
            tuple(item.anatomy_record_digest for item in records),
            (
                receipt.cp0_anatomy_record_digest,
                receipt.cp1_anatomy_record_digest,
                receipt.cp2_anatomy_record_digest,
            ),
        )

    def test_16_modules_have_no_runtime_field_io_or_network_path(self) -> None:
        for relative in (
            "mcm_field_organism/g2_d3_two_step_composition.py",
            "mcm_field_organism/g2_d3_two_step_o3_checkpoints.py",
        ):
            with self.subTest(relative=relative):
                source = self._source(relative)
                tree = ast.parse(source)
                imported = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported.extend(alias.name for alias in node.names)
                    elif isinstance(node, ast.ImportFrom):
                        imported.append(node.module or "")
                imported_surface = " ".join(imported).lower()
                for forbidden in (
                    "field", "runtime", "transfer", "runner", "audio", "video",
                    "browser", "socket", "requests", "pathlib",
                ):
                    self.assertNotIn(forbidden, imported_surface)
                lowered = source.lower()
                self.assertNotIn("open(", lowered)
                self.assertNotIn("write_text", lowered)
                self.assertNotIn("write_bytes", lowered)

    @classmethod
    def _source(cls, relative: str) -> str:
        return cls.sources[relative]

    @staticmethod
    def _function(tree: ast.AST, name: str) -> ast.FunctionDef:
        return next(
            node for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == name
        )

    @staticmethod
    def _call_count(node: ast.AST, name: str) -> int:
        return sum(
            1 for item in ast.walk(node)
            if isinstance(item, ast.Call)
            and isinstance(item.func, ast.Name)
            and item.func.id == name
        )


if __name__ == "__main__":
    unittest.main()
