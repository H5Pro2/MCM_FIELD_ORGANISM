"""Focused S1-PB acceptance for matched retention baseline closure."""

from __future__ import annotations

import ast
from dataclasses import fields, replace
from pathlib import Path
import unittest

from mcm_field_organism.g2_d3_checkpoint_baseline_comparison import (
    CLOSURE_CONTRACT_DIGEST,
    COMPARISON_CONTRACT_DIGEST,
    COMPARISON_PHASES,
    FAILURE_CODES as COMPARATOR_FAILURE_CODES,
    G2D3CheckpointBaselineComparisonReceipt,
    build_g2_d3_checkpoint_baseline_comparison_registry,
    compare_g2_d3_candidate_and_retention_baseline,
)
from mcm_field_organism.g2_d3_halving_amount import build_g2_d3_halving_amount_registry
from mcm_field_organism.g2_d3_matched_retention_baseline import (
    BASELINE_CONTRACT_DIGEST,
    BASELINE_PHASES,
    FAILURE_CODES as BASELINE_FAILURE_CODES,
    G2D3MatchedRetentionBaselineReceipt,
    G2D3MatchedRetentionBaselineResult,
    build_g2_d3_matched_retention_baseline_registry,
    evaluate_g2_d3_matched_retention_baseline,
)
from mcm_field_organism.g2_d3_schema_validator import build_g2_d3_validation_registry
from mcm_field_organism.g2_d3_target_projection import build_g2_d3_target_commit_registry
from mcm_field_organism.g2_d3_transient_boundary_validator import (
    build_g2_d3_transient_boundary_registry,
)
from mcm_field_organism.g2_d3_two_step_composition import (
    build_g2_d3_two_step_composition_registry,
)
from mcm_field_organism.g2_d3_two_step_o3_checkpoints import (
    build_g2_d3_two_step_o3_checkpoint_registry,
    evaluate_g2_d3_two_step_o3_checkpoints,
)
from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1ow_o3_checkpoint_fixtures import (
    SEQUENCE_FAILURE_FIXTURES,
    VALID_CHECKPOINT_FIXTURES,
)
from tests.g2_d3_s1pb_retention_baseline_fixtures import (
    CONFIGURATION_RAW,
    CONTINUATION_EVENT_RAW,
    DEFENSIVE_BASELINE_CODES,
    DEFENSIVE_COMPARATOR_CODES,
    EXPECTED_CLOSURE_PAYLOAD_DIGEST,
    EXPECTED_COMPARISON_DIGEST,
    EXPECTED_COMPONENTS,
    EXPECTED_FAILURES,
    EXPECTED_STATE_INPUT_DIGESTS,
    EXPECTED_STATE_RECORD_DIGESTS,
    EXPECTED_VALUES,
    INITIAL_STATE_RAW,
    INPUT_DIGESTS,
    INVALID_BASELINE_FIXTURES,
    VALID_BASELINE_FIXTURES,
    fixture_input_digests,
)


class G2D3S1PBRetentionBaselineClosureAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).parents[1]
        cls.root = root
        cls.sources = {
            relative: (root / relative).read_text(encoding="utf-8")
            for relative in (
                "mcm_field_organism/g2_d3_matched_retention_baseline.py",
                "mcm_field_organism/g2_d3_checkpoint_baseline_comparison.py",
            )
        }
        cls.baseline_registry = build_g2_d3_matched_retention_baseline_registry()
        cls.comparison_registry = build_g2_d3_checkpoint_baseline_comparison_registry()
        cls.sequence_registry = build_g2_d3_two_step_composition_registry()
        cls.checkpoint_registry = build_g2_d3_two_step_o3_checkpoint_registry()
        cls.target_registry = build_g2_d3_target_commit_registry()
        cls.amount_registry = build_g2_d3_halving_amount_registry()
        cls.boundary_registry = build_g2_d3_transient_boundary_registry()
        cls.d3_registry = build_g2_d3_validation_registry()

    def evaluate_baseline(self, fixture):
        return evaluate_g2_d3_matched_retention_baseline(
            *fixture, self.baseline_registry, self.sequence_registry
        )

    def evaluate_candidate(self, fixture):
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

    def compare(self, candidate, baseline):
        return compare_g2_d3_candidate_and_retention_baseline(
            candidate, baseline, self.comparison_registry
        )

    def test_01_frozen_files_and_fixture_digests_are_exact(self) -> None:
        expected = {
            "mcm_field_organism/g2_d3_two_step_composition.py":
                "b364ae91ff91d45db32edc2081a9782869c46a82495e3cedcf8ffc21d555991f",
            "mcm_field_organism/g2_d3_two_step_o3_checkpoints.py":
                "effc8812845273bacc52eef23a0ba20feefc743b3b630c44f04488e860a10011",
            "tests/g2_d3_s1os_fixtures.py":
                "58cd3e4505657fc6b964cb0dbc370d22e94261e626e67f652d43670e22f79a41",
            "tests/test_g2_d3_s1os_two_step_composition.py":
                "f96527e4d7611a47c5e5cf1c083ed9d3db59ead3564ea6e2e0a81c379b4cbae6",
            "tests/g2_d3_s1ow_o3_checkpoint_fixtures.py":
                "673460adb87719668908ab8f2e58fb7fcafc8a5f8d3c47e4a450ae56233b4358",
            "tests/test_g2_d3_s1ow_o3_checkpoints.py":
                "96ca1e0f7c0a7e0f32a0e13ea5eb98418f8d0ee94c625b6e2a1f275823b2305a",
        }
        for relative, digest in expected.items():
            with self.subTest(relative=relative):
                self.assertEqual(digest, sha256_hex((self.root / relative).read_bytes()))
        self.assertEqual(INPUT_DIGESTS, fixture_input_digests())

    def test_02_registries_bind_schemas_phases_codes_and_contracts(self) -> None:
        baseline = self.baseline_registry
        comparison = self.comparison_registry
        self.assertEqual(BASELINE_PHASES, baseline.baseline_phases)
        self.assertEqual(BASELINE_FAILURE_CODES, baseline.failure_codes)
        self.assertEqual(BASELINE_CONTRACT_DIGEST, baseline.baseline_contract_digest)
        self.assertEqual(COMPARISON_PHASES, comparison.comparison_phases)
        self.assertEqual(COMPARATOR_FAILURE_CODES, comparison.failure_codes)
        self.assertEqual(COMPARISON_CONTRACT_DIGEST, comparison.comparison_contract_digest)
        self.assertEqual(CLOSURE_CONTRACT_DIGEST, comparison.closure_contract_digest)

    def test_03_xxx_has_exact_states_values_and_components(self) -> None:
        result = self.evaluate_baseline(VALID_BASELINE_FIXTURES["PA_V_XXX"])
        receipt = result.receipt
        self.assertEqual(EXPECTED_VALUES, result.checkpoint_values)
        self.assertEqual("OP_CHAIN_XXX", receipt.chain_role)
        self.assertEqual("valid", receipt.validation_status)
        self.assertEqual("THREE_CHECKPOINTS_EVALUATED", receipt.baseline_status)
        self.assertEqual(EXPECTED_STATE_INPUT_DIGESTS, self._state_input_digests(receipt))
        self.assertEqual(EXPECTED_STATE_RECORD_DIGESTS, self._state_record_digests(receipt))
        self.assertEqual(EXPECTED_COMPONENTS, self._components(receipt))
        self.assertEqual(EXPECTED_COMPARISON_DIGEST, receipt.comparison_digest)

    def test_04_yyy_matches_state_sequence_with_distinct_provenance(self) -> None:
        xxx = self.evaluate_baseline(VALID_BASELINE_FIXTURES["PA_V_XXX"])
        yyy = self.evaluate_baseline(VALID_BASELINE_FIXTURES["PA_V_YYY"])
        self.assertEqual(EXPECTED_VALUES, yyy.checkpoint_values)
        self.assertEqual("OP_CHAIN_YYY", yyy.receipt.chain_role)
        self.assertEqual(self._state_input_digests(xxx.receipt), self._state_input_digests(yyy.receipt))
        self.assertEqual(self._state_record_digests(xxx.receipt), self._state_record_digests(yyy.receipt))
        self.assertNotEqual(xxx.receipt.baseline_receipt_digest, yyy.receipt.baseline_receipt_digest)

    def test_05_update_core_is_stationary_token_identical_and_called_twice(self) -> None:
        tree = ast.parse(self.sources["mcm_field_organism/g2_d3_matched_retention_baseline.py"])
        evaluate = self._function(tree, "evaluate_g2_d3_matched_retention_baseline")
        update = self._function(tree, "_update_retained_capacity")
        self.assertEqual(2, self._call_count(evaluate, "_update_retained_capacity"))
        self.assertEqual(
            ["current", "retention_fraction", "continuation_event_raw_bytes"],
            [argument.arg for argument in update.args.args],
        )
        self.assertNotIn("chain_role", ast.dump(update))
        result = self.evaluate_baseline(VALID_BASELINE_FIXTURES["PA_V_XXX"])
        self.assertEqual(EXPECTED_VALUES, result.checkpoint_values)

    def test_06_baseline_receipt_is_passive_and_digest_closed(self) -> None:
        receipt = self.evaluate_baseline(VALID_BASELINE_FIXTURES["PA_V_XXX"]).receipt
        payload = receipt.canonical_payload()
        digest = payload.pop("baseline_receipt_digest")
        self.assertEqual(digest, sha256_hex(canonical_json_bytes(payload)))
        receipt_fields = {item.name for item in fields(G2D3MatchedRetentionBaselineReceipt)}
        for forbidden in (
            "initial_state_raw_bytes", "cp0_state_raw_bytes", "cp1_state_raw_bytes",
            "cp2_state_raw_bytes", "trace", "candidate_result", "candidate_receipt",
        ):
            self.assertNotIn(forbidden, receipt_fields)

    def test_07_crossed_provenance_stops_before_state_validation(self) -> None:
        receipt = self.evaluate_baseline(
            INVALID_BASELINE_FIXTURES["PA_I_PROVENANCE_CROSS"]
        ).receipt
        self.assertEqual(("OY_SEQUENCE_PROVENANCE_INVALID",), receipt.failure_reasons)
        self.assertEqual(
            ("api_intake", "sequence_provenance_validation", "persistence_guard", "baseline_receipt"),
            receipt.completed_checks,
        )

    def test_08_sealed_wrong_configuration_is_not_repaired(self) -> None:
        receipt = self.evaluate_baseline(
            INVALID_BASELINE_FIXTURES["PA_I_CONFIG_RETENTION_025"]
        ).receipt
        self.assertEqual(("OY_CONFIGURATION_INVALID",), receipt.failure_reasons)
        self.assertIn("configuration_validation", receipt.completed_checks)
        self.assertNotIn("initial_state_validation", receipt.completed_checks)
        self.assertEqual("not_computable", receipt.cp0_value)

    def test_09_negative_and_boolean_states_stop_before_cp0(self) -> None:
        for name in ("PA_I_STATE_NEGATIVE", "PA_I_STATE_BOOL"):
            with self.subTest(name=name):
                receipt = self.evaluate_baseline(INVALID_BASELINE_FIXTURES[name]).receipt
                self.assertEqual(("OY_INITIAL_STATE_INVALID",), receipt.failure_reasons)
                self.assertIn("initial_state_validation", receipt.completed_checks)
                self.assertNotIn("cp0_readout", receipt.completed_checks)

    def test_10_wrong_event_version_stops_before_first_update(self) -> None:
        receipt = self.evaluate_baseline(
            INVALID_BASELINE_FIXTURES["PA_I_EVENT_VERSION"]
        ).receipt
        self.assertEqual(("OY_EVENT1_INVALID",), receipt.failure_reasons)
        self.assertIn("event1_validation", receipt.completed_checks)
        self.assertNotIn("update1", receipt.completed_checks)
        self.assertEqual("not_computable", receipt.cp0_value)

    def test_11_external_errors_have_one_code_and_no_partial_values(self) -> None:
        self.assertEqual(5, len(INVALID_BASELINE_FIXTURES))
        for name, fixture in INVALID_BASELINE_FIXTURES.items():
            with self.subTest(name=name):
                result = self.evaluate_baseline(fixture)
                receipt = result.receipt
                self.assertEqual((EXPECTED_FAILURES[name],), receipt.failure_reasons)
                self.assertEqual("not_computable", result.checkpoint_values)
                self.assertEqual("not_computable", receipt.baseline_status)
                self.assertEqual(("not_computable",) * 3, self._state_input_digests(receipt))
                self.assertEqual(("not_computable",) * 3, self._components(receipt))

    def test_12_determinism_inputs_and_registries_are_immutable(self) -> None:
        fixture = VALID_BASELINE_FIXTURES["PA_V_XXX"]
        registries = (self.baseline_registry, self.sequence_registry)
        first = self.evaluate_baseline(fixture)
        second = self.evaluate_baseline(fixture)
        self.assertEqual(first, second)
        self.assertIs(fixture, VALID_BASELINE_FIXTURES["PA_V_XXX"])
        self.assertEqual(registries, (self.baseline_registry, self.sequence_registry))

    def test_13_wrong_api_types_registries_and_candidate_receipt_fail_early(self) -> None:
        first, second, state, event, configuration = VALID_BASELINE_FIXTURES["PA_V_XXX"]
        for values in (
            (bytes.fromhex(first), second, state, event, configuration),
            (first, bytes.fromhex(second), state, event, configuration),
            (first, second, bytearray(state), event, configuration),
            (first, second, state, bytearray(event), configuration),
            (first, second, state, event, bytearray(configuration)),
        ):
            with self.assertRaises(TypeError):
                evaluate_g2_d3_matched_retention_baseline(
                    *values, self.baseline_registry, self.sequence_registry
                )
        with self.assertRaises(ValueError):
            evaluate_g2_d3_matched_retention_baseline(
                first,
                second,
                state,
                event,
                configuration,
                replace(self.baseline_registry, state_schema_version="changed"),
                self.sequence_registry,
            )
        with self.assertRaises(TypeError):
            evaluate_g2_d3_matched_retention_baseline(
                first, second, state, event, configuration, self.baseline_registry, object()
            )
        candidate = self.evaluate_candidate(VALID_CHECKPOINT_FIXTURES["OV_V_XXX"])
        with self.assertRaises(TypeError):
            evaluate_g2_d3_matched_retention_baseline(
                first,
                second,
                candidate.receipt,
                event,
                configuration,
                self.baseline_registry,
                self.sequence_registry,
            )

    def test_14_all_codes_exist_without_defensive_fake_fixtures(self) -> None:
        self.assertEqual(11, len(BASELINE_FAILURE_CODES))
        self.assertEqual(7, len(DEFENSIVE_BASELINE_CODES))
        self.assertTrue(set(DEFENSIVE_BASELINE_CODES).issubset(BASELINE_FAILURE_CODES))
        self.assertEqual(5, len(COMPARATOR_FAILURE_CODES))
        self.assertEqual(2, len(DEFENSIVE_COMPARATOR_CODES))
        self.assertTrue(set(DEFENSIVE_COMPARATOR_CODES).issubset(COMPARATOR_FAILURE_CODES))
        baseline_source = self.sources["mcm_field_organism/g2_d3_matched_retention_baseline.py"]
        comparator_source = self.sources[
            "mcm_field_organism/g2_d3_checkpoint_baseline_comparison.py"
        ]
        for code in DEFENSIVE_BASELINE_CODES:
            self.assertIn(f'return fail("{code}")', baseline_source)
        for code in DEFENSIVE_COMPARATOR_CODES:
            self.assertIn(f'return fail("{code}")', comparator_source)

    def test_15_xxx_candidate_and_baseline_close_exactly(self) -> None:
        candidate = self.evaluate_candidate(VALID_CHECKPOINT_FIXTURES["OV_V_XXX"])
        baseline = self.evaluate_baseline(VALID_BASELINE_FIXTURES["PA_V_XXX"])
        result = self.compare(candidate, baseline)
        self._assert_closed(result, "OP_CHAIN_XXX")

    def test_16_yyy_candidate_and_baseline_close_with_separate_provenance(self) -> None:
        candidate = self.evaluate_candidate(VALID_CHECKPOINT_FIXTURES["OV_V_YYY"])
        baseline = self.evaluate_baseline(VALID_BASELINE_FIXTURES["PA_V_YYY"])
        result = self.compare(candidate, baseline)
        self._assert_closed(result, "OP_CHAIN_YYY")
        self.assertNotEqual(
            result.receipt.candidate_checkpoint_receipt_digest,
            result.receipt.baseline_receipt_digest,
        )

    def test_17_comparator_rejects_invalid_and_crossed_real_results(self) -> None:
        valid_candidate = self.evaluate_candidate(VALID_CHECKPOINT_FIXTURES["OV_V_XXX"])
        invalid_candidate = self.evaluate_candidate(
            SEQUENCE_FAILURE_FIXTURES["OV_I_FORMATION_DISABLED"]
        )
        valid_baseline = self.evaluate_baseline(VALID_BASELINE_FIXTURES["PA_V_XXX"])
        invalid_baseline = self.evaluate_baseline(
            INVALID_BASELINE_FIXTURES["PA_I_PROVENANCE_CROSS"]
        )
        yyy_baseline = self.evaluate_baseline(VALID_BASELINE_FIXTURES["PA_V_YYY"])
        cases = (
            (invalid_candidate, valid_baseline, "PA_CANDIDATE_RESULT_INVALID"),
            (valid_candidate, invalid_baseline, "PA_BASELINE_RESULT_INVALID"),
            (valid_candidate, yyy_baseline, "PA_CHAIN_PROVENANCE_MISMATCH"),
        )
        for candidate, baseline, code in cases:
            with self.subTest(code=code):
                result = self.compare(candidate, baseline)
                self.assertEqual("not_computable", result.closure_status)
                self.assertEqual("not_computable", result.residual_checkpoint_values)
                self.assertEqual("not_computable", result.residual_directed_components)
                self.assertEqual((code,), result.receipt.failure_reasons)

    def test_18_module_surfaces_are_isolated_and_nonpersistent(self) -> None:
        baseline_source = self.sources["mcm_field_organism/g2_d3_matched_retention_baseline.py"]
        comparator_source = self.sources[
            "mcm_field_organism/g2_d3_checkpoint_baseline_comparison.py"
        ]
        baseline_tree = ast.parse(baseline_source)
        comparator_tree = ast.parse(comparator_source)
        baseline_imports = self._imports(baseline_tree)
        comparator_imports = self._imports(comparator_tree)
        self.assertNotIn("g2_d3_two_step_o3_checkpoints", " ".join(baseline_imports))
        self.assertIn("g2_d3_two_step_o3_checkpoints", " ".join(comparator_imports))
        comparator_calls = {
            item.func.id for item in ast.walk(comparator_tree)
            if isinstance(item, ast.Call) and isinstance(item.func, ast.Name)
        }
        self.assertNotIn("evaluate_g2_d3_two_step_o3_checkpoints", comparator_calls)
        self.assertNotIn("evaluate_g2_d3_matched_retention_baseline", comparator_calls)
        for source in (baseline_source, comparator_source):
            lowered = source.lower()
            for forbidden in (
                "open(", "write_text", "write_bytes", "socket", "requests",
                "runtime", "runner", "audio", "video", "transfer",
            ):
                self.assertNotIn(forbidden, lowered)
        import mcm_field_organism.g2_d3_matched_retention_baseline as baseline_module
        import mcm_field_organism.g2_d3_checkpoint_baseline_comparison as comparison_module
        self.assertNotIn("_RetentionState", baseline_module.__all__)
        self.assertNotIn("_update_retained_capacity", baseline_module.__all__)
        self.assertNotIn("evaluate", " ".join(comparison_module.__all__))

    def _assert_closed(self, result, role: str) -> None:
        self.assertEqual("BASELINE_CLOSED_CURRENT_CHECKPOINT_VECTOR", result.closure_status)
        self.assertEqual((0.0, 0.0, 0.0), result.residual_checkpoint_values)
        self.assertEqual((0.0, 0.0, 0.0), result.residual_directed_components)
        receipt = result.receipt
        self.assertEqual(role, receipt.candidate_chain_role)
        self.assertEqual(role, receipt.baseline_chain_role)
        self.assertEqual(EXPECTED_CLOSURE_PAYLOAD_DIGEST, receipt.closure_payload_digest)
        self.assertEqual(COMPARISON_PHASES, receipt.completed_checks)
        payload = receipt.canonical_payload()
        digest = payload.pop("comparison_receipt_digest")
        self.assertEqual(digest, sha256_hex(canonical_json_bytes(payload)))
        receipt_fields = {item.name for item in fields(G2D3CheckpointBaselineComparisonReceipt)}
        for forbidden in ("candidate_result", "baseline_result", "raw_bytes", "trace"):
            self.assertNotIn(forbidden, receipt_fields)

    @staticmethod
    def _state_input_digests(receipt):
        return (
            receipt.cp0_state_input_bytes_digest,
            receipt.cp1_state_input_bytes_digest,
            receipt.cp2_state_input_bytes_digest,
        )

    @staticmethod
    def _state_record_digests(receipt):
        return (
            receipt.cp0_state_record_digest,
            receipt.cp1_state_record_digest,
            receipt.cp2_state_record_digest,
        )

    @staticmethod
    def _components(receipt):
        return (receipt.delta_cp1_cp0, receipt.delta_cp2_cp1, receipt.delta_cp2_cp0)

    @staticmethod
    def _function(tree: ast.AST, name: str) -> ast.FunctionDef:
        return next(
            item for item in ast.walk(tree)
            if isinstance(item, ast.FunctionDef) and item.name == name
        )

    @staticmethod
    def _call_count(node: ast.AST, name: str) -> int:
        return sum(
            1 for item in ast.walk(node)
            if isinstance(item, ast.Call)
            and isinstance(item.func, ast.Name)
            and item.func.id == name
        )

    @staticmethod
    def _imports(tree: ast.AST) -> list[str]:
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        return imported


if __name__ == "__main__":
    unittest.main()
