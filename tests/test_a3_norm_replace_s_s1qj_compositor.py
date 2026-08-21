from __future__ import annotations

from dataclasses import fields, replace
import ast
import math
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mcm_field_organism import current_api
from mcm_field_organism.a3_norm_replace_s_compositor import (
    COMPLETED,
    CONTRACT_ID,
    FAILURE_CODES,
    NOT_COMPUTABLE,
    PHASES,
    STATUSES,
    A3NormReplaceSReceipt,
    A3NormReplaceSResult,
    advance_a3_norm_replace_s,
)
from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralLocalFieldSubstrateError,
    advance_neutral_fast_shared_field,
    advance_neutral_fast_shared_field_transient,
)
from mcm_field_organism.shared_mcm_field import SharedMCMField
from mcm_field_organism.w7m_capacity_function_matrix import (
    build_w7m_capacity_function_matrix_adapter,
)
from mcm_field_organism.w7n_capacity_function_baselines import (
    W7NCapacityFunctionBaselineError,
    W7NLocalBaselineState,
    advance_w7n_local_baseline,
)
from tests.a3_norm_replace_s_s1qj_fixtures import (
    A3NormFixture,
    build_sync_fixture,
    build_transient_fixture,
)


MODULE = "mcm_field_organism.a3_norm_replace_s_compositor"


def _run(fixture: A3NormFixture, **overrides) -> A3NormReplaceSResult:
    values = {
        "field": fixture.field,
        "distribution": fixture.distribution,
        "interval_input": fixture.interval_input,
        "neutral_substrate_config": fixture.substrate_config,
        "fast_afterimage_config": fixture.afterimage_config,
        "norm_spec": fixture.norm_spec,
        "norm_prestate": fixture.norm_prestate,
    }
    values.update(overrides)
    return advance_a3_norm_replace_s(**values)


def _expected(fixture: A3NormFixture):
    if isinstance(fixture.interval_input, MCMFieldStepTime):
        proposal = advance_neutral_fast_shared_field(
            fixture.field,
            fixture.distribution,
            fixture.interval_input,
            fixture.substrate_config,
            fixture.afterimage_config,
        )
        duration = fixture.interval_input.elapsed_seconds
    else:
        proposal = advance_neutral_fast_shared_field_transient(
            fixture.field,
            fixture.distribution,
            fixture.interval_input,
            fixture.substrate_config,
            fixture.afterimage_config,
        )
        duration = fixture.interval_input.step_time.elapsed_seconds
    norm = advance_w7n_local_baseline(
        fixture.norm_spec,
        fixture.norm_prestate,
        tuple(item.activation for item in proposal.layer.neurons),
        duration,
    )
    return proposal, norm


def _failure_code(result: A3NormReplaceSResult) -> str:
    if result.receipt.status != NOT_COMPUTABLE:
        raise AssertionError("expected NOT_COMPUTABLE result")
    return result.receipt.failure_codes[0]


class A3NormReplaceSS1QJCompositorTests(unittest.TestCase):
    def test_01_module_type_status_and_error_code_surface(self) -> None:
        self.assertEqual("a3-norm-replace-s/s1qi.v1", CONTRACT_ID)
        self.assertEqual((COMPLETED, NOT_COMPUTABLE), STATUSES)
        self.assertEqual(14, len(FAILURE_CODES))
        self.assertEqual(14, len(set(FAILURE_CODES)))
        self.assertEqual(10, len(PHASES))
        self.assertEqual(
            ("field", "next_norm_state", "receipt"),
            tuple(item.name for item in fields(A3NormReplaceSResult)),
        )
        self.assertEqual("receipt_digest", fields(A3NormReplaceSReceipt)[-1].name)

    def test_02_canonical_fresh_fixtures_are_deterministic(self) -> None:
        for builder in (build_sync_fixture, build_transient_fixture):
            first = builder()
            second = builder()
            self.assertEqual(first.field.layer.digest(), second.field.layer.digest())
            self.assertEqual(first.distribution.digest(), second.distribution.digest())
            self.assertEqual(first.interval_input, second.interval_input)
            self.assertEqual(first.norm_spec, second.norm_spec)
            self.assertEqual(first.norm_prestate, second.norm_prestate)

    def test_03_valid_synchronous_replace_s_step(self) -> None:
        result = _run(build_sync_fixture())
        self.assertEqual(COMPLETED, result.receipt.status)
        self.assertIsInstance(result.field, SharedMCMField)
        self.assertIsInstance(result.next_norm_state, W7NLocalBaselineState)
        self.assertEqual("sync", result.receipt.interval_kind)

    def test_04_valid_transient_replace_s_step(self) -> None:
        result = _run(build_transient_fixture())
        self.assertEqual(COMPLETED, result.receipt.status)
        self.assertIsInstance(result.field, SharedMCMField)
        self.assertIsInstance(result.next_norm_state, W7NLocalBaselineState)
        self.assertEqual("transient", result.receipt.interval_kind)

    def test_05_complete_signed_s_replacement_matches_existing_norm(self) -> None:
        for fixture in (build_sync_fixture(), build_transient_fixture()):
            with self.subTest(kind=type(fixture.interval_input).__name__):
                _, expected_norm = _expected(fixture)
                result = _run(fixture)
                self.assertEqual(
                    expected_norm.output,
                    tuple(item.activation for item in result.field.layer.neurons),
                )
                self.assertEqual(expected_norm.state, result.next_norm_state)

    def test_06_h_perception_docks_and_identities_are_bit_equal_to_a1(self) -> None:
        fixture = build_sync_fixture()
        proposal, _ = _expected(fixture)
        result = _run(fixture)
        self.assertEqual(proposal.docks, result.field.docks)
        self.assertEqual(proposal.last_distribution, result.field.last_distribution)
        for expected, actual in zip(
            proposal.layer.neurons, result.field.layer.neurons, strict=True
        ):
            self.assertEqual(expected.afterimage, actual.afterimage)
            self.assertEqual(expected.perception, actual.perception)
            self.assertEqual(expected.neuron_id, actual.neuron_id)
            self.assertEqual(expected.position, actual.position)

    def test_07_exactly_one_field_time_advance_for_both_interval_forms(self) -> None:
        for fixture in (build_sync_fixture(), build_transient_fixture()):
            result = _run(fixture)
            self.assertEqual(fixture.field.layer.tick + 1, result.field.layer.tick)
            self.assertEqual(1, result.receipt.field_time_advance_count)
            self.assertEqual(fixture.distribution, result.field.last_distribution)

    def test_08_final_field_and_norm_state_form_the_next_carry(self) -> None:
        first_fixture = build_sync_fixture()
        first = _run(first_fixture)
        second_fixture = build_sync_fixture(
            field=first.field,
            norm_prestate=first.next_norm_state,
            start_tick=10,
            values=(-0.2, 0.5, 0.1),
        )
        second = _run(second_fixture)
        self.assertEqual(COMPLETED, second.receipt.status)
        self.assertEqual(first.field.layer.tick + 1, second.field.layer.tick)
        self.assertEqual(
            first.receipt.final_field_digest,
            second.receipt.input_field_digest,
        )
        self.assertEqual(
            first.receipt.norm_next_state_digest,
            second.receipt.norm_prestate_digest,
        )

    def test_09_result_and_receipt_digests_are_deterministic(self) -> None:
        fixture = build_sync_fixture()
        first = _run(fixture)
        second = _run(fixture)
        self.assertEqual(first.receipt, second.receipt)
        self.assertEqual(first.receipt.receipt_digest, second.receipt.receipt_digest)
        self.assertEqual(first.receipt.final_field_digest, second.receipt.final_field_digest)

    def test_10_zero_state_and_zero_contact_produce_complete_zero_output(self) -> None:
        fixture = build_sync_fixture(values=(0.0, 0.0, 0.0))
        result = _run(fixture)
        self.assertEqual(COMPLETED, result.receipt.status)
        self.assertEqual((0.0, 0.0, 0.0), result.next_norm_state.latent)
        self.assertEqual(
            (0.0, 0.0, 0.0),
            tuple(item.activation for item in result.field.layer.neurons),
        )

    def test_11_common_geometry_permutation_has_no_list_position_semantics(self) -> None:
        fixture = build_sync_fixture()
        original = _run(fixture)
        reversed_field = SharedMCMField(
            replace(
                fixture.field.layer,
                neurons=tuple(reversed(fixture.field.layer.neurons)),
            ),
            fixture.field.docks,
        )
        reversed_fixture = build_sync_fixture(
            field=reversed_field,
            norm_prestate=W7NLocalBaselineState(
                "norm", tuple(reversed(fixture.norm_prestate.latent))
            ),
        )
        permuted = _run(reversed_fixture)
        original_by_id = {
            item.neuron_id: item.activation for item in original.field.layer.neurons
        }
        permuted_by_id = {
            item.neuron_id: item.activation for item in permuted.field.layer.neurons
        }
        self.assertEqual(set(original_by_id), set(permuted_by_id))
        for neuron_id in original_by_id:
            self.assertAlmostEqual(
                original_by_id[neuron_id], permuted_by_id[neuron_id], places=12
            )

    def test_12_remote_norm_load_changes_local_scale_without_edge_transfer(self) -> None:
        fixture = build_sync_fixture(values=(0.8, 0.0, 0.0))
        unloaded = _run(fixture)
        loaded = _run(
            fixture,
            norm_prestate=W7NLocalBaselineState("norm", (0.0, 0.0, 0.8)),
        )
        unloaded_first = unloaded.field.layer.neurons[0].activation
        loaded_first = loaded.field.layer.neurons[0].activation
        self.assertNotEqual(unloaded_first, loaded_first)
        self.assertLess(abs(loaded_first), abs(unloaded_first))

    def test_13_internal_a1_proposal_is_not_published(self) -> None:
        result = _run(build_sync_fixture())
        result_roles = {item.name for item in fields(result)}
        receipt_roles = {item.name for item in fields(result.receipt)}
        self.assertNotIn("a1_proposal", result_roles)
        self.assertNotIn("norm_output", result_roles)
        self.assertIn("a1_proposal_digest", receipt_roles)
        self.assertIn("norm_output_digest", receipt_roles)

    def test_14_module_has_no_forbidden_import_export_or_side_effect(self) -> None:
        source_path = Path(__file__).parents[1] / "mcm_field_organism" / (
            "a3_norm_replace_s_compositor.py"
        )
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        forbidden_fragments = (
            "runner",
            "orchestrator",
            "runtime",
            "media",
            "dynamic_substrate",
            "mcm_substrate_state",
            "mcm_local_development_state",
        )
        self.assertFalse(
            any(fragment in module for module in imported for fragment in forbidden_fragments)
        )
        self.assertNotIn("open(", source)
        self.assertNotIn("write_text", source)
        self.assertNotIn("write_bytes", source)
        self.assertFalse(hasattr(current_api, "advance_a3_norm_replace_s"))

    def test_15_mutation_classes_01_to_05_fail_with_exact_codes(self) -> None:
        fixture = build_sync_fixture()
        active_field = build_sync_fixture().norm_spec
        changed_spec = replace(fixture.norm_spec, equation_contract="changed")
        cases = (
            (_run(fixture, field=object()), "QI_INPUT_TYPE_INVALID"),
            (
                _run(
                    fixture,
                    field=build_w7m_capacity_function_matrix_adapter().initial_field,
                ),
                "QI_FIELD_ROLE_INVALID",
            ),
            (
                _run(
                    fixture,
                    interval_input=MCMFieldStepTime(
                        "organism.test", 0, 9, 10.0
                    ),
                ),
                "QI_DISTRIBUTION_OR_INTERVAL_INVALID",
            ),
            (_run(fixture, norm_spec=changed_spec), "QI_CONFIGURATION_INVALID"),
            (
                _run(
                    fixture,
                    norm_prestate=W7NLocalBaselineState("leak", (0.0, 0.0, 0.0)),
                ),
                "QI_NORM_PRESTATE_INVALID",
            ),
        )
        self.assertEqual("norm", active_field.model_id)
        for result, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(expected, _failure_code(result))

    def test_16_mutation_classes_06_to_10_fail_with_exact_codes(self) -> None:
        fixture = build_sync_fixture()
        geometry = _run(
            fixture,
            norm_prestate=W7NLocalBaselineState("norm", (0.0, 0.0)),
        )
        with patch(
            f"{MODULE}.advance_neutral_fast_shared_field",
            side_effect=NeutralLocalFieldSubstrateError("controlled"),
        ):
            a1_failed = _run(fixture)
        with patch(f"{MODULE}.advance_neutral_fast_shared_field", return_value=fixture.field):
            a1_invalid = _run(fixture)
        with patch(
            f"{MODULE}.advance_w7n_local_baseline",
            side_effect=W7NCapacityFunctionBaselineError("controlled"),
        ):
            norm_failed = _run(fixture)
        with patch(
            f"{MODULE}.advance_w7n_local_baseline",
            return_value=SimpleNamespace(
                state=W7NLocalBaselineState("norm", (0.0, 0.0, 0.0)),
                output=(math.nan, 0.0, 0.0),
            ),
        ):
            norm_invalid = _run(fixture)
        cases = (
            (geometry, "QI_GEOMETRY_OR_ORDER_MISMATCH"),
            (a1_failed, "QI_A1_ADVANCE_FAILED"),
            (a1_invalid, "QI_A1_PROPOSAL_INVALID"),
            (norm_failed, "QI_NORM_ADVANCE_FAILED"),
            (norm_invalid, "QI_NORM_OUTPUT_INVALID"),
        )
        for result, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(expected, _failure_code(result))

    def test_17_mutation_classes_11_to_14_fail_with_exact_codes(self) -> None:
        fixture = build_sync_fixture()
        with patch(f"{MODULE}._materialize_replace_s", side_effect=ValueError("controlled")):
            replacement = _run(fixture)
        with patch(f"{MODULE}._final_identity_valid", return_value=False):
            identity = _run(fixture)
        with patch(f"{MODULE}._field_time_advance_count", return_value=2):
            time_count = _run(fixture)
        with patch(f"{MODULE}._atomic_output_valid", return_value=False):
            atomic = _run(fixture)
        cases = (
            (replacement, "QI_S_REPLACEMENT_FAILED"),
            (identity, "QI_H_OR_PROVENANCE_CHANGED"),
            (time_count, "QI_FIELD_TIME_CARDINALITY_FAILED"),
            (atomic, "QI_ATOMIC_OUTPUT_FAILED"),
        )
        for result, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(expected, _failure_code(result))

    def test_18_not_computable_is_always_an_atomic_pair_without_partial_output(self) -> None:
        fixture = build_sync_fixture()
        failures = (
            _run(fixture, field=object()),
            _run(
                fixture,
                norm_prestate=W7NLocalBaselineState("norm", (0.0, 0.0)),
            ),
        )
        for result in failures:
            self.assertEqual(NOT_COMPUTABLE, result.field)
            self.assertEqual(NOT_COMPUTABLE, result.next_norm_state)
            self.assertEqual(NOT_COMPUTABLE, result.receipt.status)
            self.assertTrue(result.receipt.failure_codes)


if __name__ == "__main__":
    unittest.main()
