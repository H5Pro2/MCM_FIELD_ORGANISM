from __future__ import annotations

from dataclasses import fields, replace
import ast
import math
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.m5_direct_replace_s_compositor import (
    COMPLETED,
    CONTRACT_ID,
    FAILURE_CODES,
    NOT_COMPUTABLE,
    PHASES,
    STATUSES,
    M5DirectReplaceSReceipt,
    M5DirectReplaceSResult,
    advance_m5_direct_replace_s,
)
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
from tests.m5_direct_replace_s_s1qn_fixtures import (
    M5DirectFixture,
    build_sync_fixture,
    build_transient_fixture,
)


MODULE = "mcm_field_organism.m5_direct_replace_s_compositor"


def _run(fixture: M5DirectFixture, **overrides) -> M5DirectReplaceSResult:
    values = {
        "field": fixture.field,
        "distribution": fixture.distribution,
        "interval_input": fixture.interval_input,
        "neutral_substrate_config": fixture.substrate_config,
        "fast_afterimage_config": fixture.afterimage_config,
        "leak_spec": fixture.leak_spec,
        "m5_prestate": fixture.m5_prestate,
    }
    values.update(overrides)
    return advance_m5_direct_replace_s(**values)


def _expected(fixture: M5DirectFixture):
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
    direct = advance_w7n_local_baseline(
        fixture.leak_spec,
        fixture.m5_prestate,
        tuple(item.activation for item in proposal.layer.neurons),
        duration,
    )
    return proposal, direct


def _failure_code(result: M5DirectReplaceSResult) -> str:
    if result.receipt.status != NOT_COMPUTABLE:
        raise AssertionError("expected NOT_COMPUTABLE result")
    return result.receipt.failure_codes[0]


class M5DirectReplaceSS1QNCompositorTests(unittest.TestCase):
    def test_01_module_type_status_phase_and_error_surface(self) -> None:
        self.assertEqual("m5-direct-replace-s/s1qm.v1", CONTRACT_ID)
        self.assertEqual((COMPLETED, NOT_COMPUTABLE), STATUSES)
        self.assertEqual(14, len(FAILURE_CODES))
        self.assertEqual(14, len(set(FAILURE_CODES)))
        self.assertEqual(10, len(PHASES))
        self.assertEqual(
            ("field", "next_m5_state", "receipt"),
            tuple(item.name for item in fields(M5DirectReplaceSResult)),
        )
        self.assertEqual("receipt_digest", fields(M5DirectReplaceSReceipt)[-1].name)

    def test_02_canonical_fresh_fixtures_are_deterministic(self) -> None:
        for builder in (build_sync_fixture, build_transient_fixture):
            first = builder()
            second = builder()
            self.assertEqual(first.field.layer.digest(), second.field.layer.digest())
            self.assertEqual(first.distribution.digest(), second.distribution.digest())
            self.assertEqual(first.interval_input, second.interval_input)
            self.assertEqual(first.leak_spec, second.leak_spec)
            self.assertEqual(first.m5_prestate, second.m5_prestate)

    def test_03_valid_synchronous_m5_direct_step(self) -> None:
        result = _run(build_sync_fixture())
        self.assertEqual(COMPLETED, result.receipt.status)
        self.assertIsInstance(result.field, SharedMCMField)
        self.assertIsInstance(result.next_m5_state, W7NLocalBaselineState)
        self.assertEqual("sync", result.receipt.interval_kind)

    def test_04_valid_transient_m5_direct_step(self) -> None:
        result = _run(build_transient_fixture())
        self.assertEqual(COMPLETED, result.receipt.status)
        self.assertIsInstance(result.field, SharedMCMField)
        self.assertIsInstance(result.next_m5_state, W7NLocalBaselineState)
        self.assertEqual("transient", result.receipt.interval_kind)

    def test_05_output_matches_the_existing_w7n_leak_kernel_exactly(self) -> None:
        for fixture in (build_sync_fixture(), build_transient_fixture()):
            with self.subTest(kind=type(fixture.interval_input).__name__):
                _, expected = _expected(fixture)
                result = _run(fixture)
                self.assertEqual(expected.state, result.next_m5_state)
                self.assertEqual(
                    expected.output,
                    tuple(item.activation for item in result.field.layer.neurons),
                )

    def test_06_signed_s_is_replaced_without_an_additional_readout(self) -> None:
        result = _run(build_sync_fixture(values=(0.8, -0.4, 0.2)))
        final_s = tuple(item.activation for item in result.field.layer.neurons)
        self.assertEqual(result.next_m5_state.latent, final_s)
        self.assertTrue(result.receipt.state_output_identity_confirmed)
        self.assertTrue(result.receipt.s_replacement_confirmed)
        self.assertTrue(any(value < 0.0 for value in final_s))
        self.assertTrue(any(value > 0.0 for value in final_s))

    def test_07_h_perception_docks_and_identities_are_bit_equal_to_a1(self) -> None:
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

    def test_08_exactly_one_field_time_advance_for_both_interval_forms(self) -> None:
        for fixture in (build_sync_fixture(), build_transient_fixture()):
            result = _run(fixture)
            self.assertEqual(fixture.field.layer.tick + 1, result.field.layer.tick)
            self.assertEqual(1, result.receipt.field_time_advance_count)
            self.assertEqual(fixture.distribution, result.field.last_distribution)

    def test_09_final_field_and_m5_state_form_the_next_carry(self) -> None:
        first_fixture = build_sync_fixture()
        first = _run(first_fixture)
        second_fixture = build_sync_fixture(
            field=first.field,
            m5_prestate=first.next_m5_state,
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
            first.receipt.m5_next_state_digest,
            second.receipt.m5_prestate_digest,
        )

    def test_10_result_and_receipt_digests_are_deterministic(self) -> None:
        fixture = build_sync_fixture()
        first = _run(fixture)
        second = _run(fixture)
        self.assertEqual(first.receipt, second.receipt)
        self.assertEqual(first.receipt.receipt_digest, second.receipt.receipt_digest)
        self.assertEqual(first.receipt.final_field_digest, second.receipt.final_field_digest)

    def test_11_zero_state_and_zero_contact_produce_complete_zero_output(self) -> None:
        fixture = build_sync_fixture(values=(0.0, 0.0, 0.0))
        result = _run(fixture)
        self.assertEqual(COMPLETED, result.receipt.status)
        self.assertEqual((0.0, 0.0, 0.0), result.next_m5_state.latent)
        self.assertEqual(
            (0.0, 0.0, 0.0),
            tuple(item.activation for item in result.field.layer.neurons),
        )

    def test_12_remote_private_load_does_not_change_unchanged_local_output(self) -> None:
        fixture = build_sync_fixture(values=(0.8, 0.0, 0.0))
        unloaded = _run(fixture)
        loaded = _run(
            fixture,
            m5_prestate=W7NLocalBaselineState("leak", (0.0, 0.0, 0.8)),
        )
        self.assertEqual(
            unloaded.field.layer.neurons[0].activation,
            loaded.field.layer.neurons[0].activation,
        )
        self.assertNotEqual(
            unloaded.field.layer.neurons[2].activation,
            loaded.field.layer.neurons[2].activation,
        )

    def test_13_common_geometry_permutation_has_no_list_position_semantics(self) -> None:
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
            m5_prestate=W7NLocalBaselineState(
                "leak", tuple(reversed(fixture.m5_prestate.latent))
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

    def test_14_private_core_and_refactor_boundaries_remain_model_neutral(self) -> None:
        root = Path(__file__).parents[1] / "mcm_field_organism"
        core_source = (root / "local_state_replace_s_compositor_core.py").read_text(
            encoding="utf-8"
        )
        lowered = core_source.lower()
        for forbidden in ("norm", "m5", "receipt", "failure_code", "status"):
            self.assertNotIn(forbidden, lowered)
        tree = ast.parse(core_source)
        imported = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }
        self.assertFalse(
            any(
                fragment in module
                for module in imported
                for fragment in (
                    "w7n_capacity",
                    "w7m_capacity",
                    "runner",
                    "orchestrator",
                    "dynamic_substrate",
                )
            )
        )
        a3_source = (root / "a3_norm_replace_s_compositor.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("local_state_replace_s_compositor_core", a3_source)
        self.assertFalse(hasattr(current_api, "advance_m5_direct_replace_s"))
        self.assertFalse(hasattr(mcm_field_organism, "advance_m5_direct_replace_s"))

    def test_15_mutation_classes_01_to_05_fail_with_exact_codes(self) -> None:
        fixture = build_sync_fixture()
        specs = {
            item.model_id: item
            for item in build_w7m_capacity_function_matrix_adapter().baselines
        }
        cases = (
            (_run(fixture, field=object()), "QM_INPUT_TYPE_INVALID"),
            (
                _run(
                    fixture,
                    field=build_w7m_capacity_function_matrix_adapter().initial_field,
                ),
                "QM_FIELD_ROLE_INVALID",
            ),
            (
                _run(
                    fixture,
                    interval_input=MCMFieldStepTime(
                        "organism.test", 0, 9, 10.0
                    ),
                ),
                "QM_DISTRIBUTION_OR_INTERVAL_INVALID",
            ),
            (_run(fixture, leak_spec=specs["norm"]), "QM_CONFIGURATION_INVALID"),
            (
                _run(
                    fixture,
                    m5_prestate=W7NLocalBaselineState("norm", (0.0, 0.0, 0.0)),
                ),
                "QM_M5_PRESTATE_INVALID",
            ),
        )
        for result, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(expected, _failure_code(result))

    def test_16_mutation_classes_06_to_10_fail_with_exact_codes(self) -> None:
        fixture = build_sync_fixture()
        geometry = _run(
            fixture,
            m5_prestate=W7NLocalBaselineState("leak", (0.0, 0.0)),
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
            leak_failed = _run(fixture)
        with patch(
            f"{MODULE}.advance_w7n_local_baseline",
            return_value=SimpleNamespace(
                state=W7NLocalBaselineState("leak", (0.0, 0.0, 0.0)),
                output=(math.nan, 0.0, 0.0),
            ),
        ):
            direct_invalid = _run(fixture)
        cases = (
            (geometry, "QM_GEOMETRY_OR_ORDER_MISMATCH"),
            (a1_failed, "QM_A1_ADVANCE_FAILED"),
            (a1_invalid, "QM_A1_PROPOSAL_INVALID"),
            (leak_failed, "QM_LEAK_ADVANCE_FAILED"),
            (direct_invalid, "QM_DIRECT_OUTPUT_INVALID"),
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
            (replacement, "QM_S_REPLACEMENT_FAILED"),
            (identity, "QM_H_OR_PROVENANCE_CHANGED"),
            (time_count, "QM_FIELD_TIME_CARDINALITY_FAILED"),
            (atomic, "QM_ATOMIC_OUTPUT_FAILED"),
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
                m5_prestate=W7NLocalBaselineState("leak", (0.0, 0.0)),
            ),
        )
        for result in failures:
            self.assertEqual(NOT_COMPUTABLE, result.field)
            self.assertEqual(NOT_COMPUTABLE, result.next_m5_state)
            self.assertEqual(NOT_COMPUTABLE, result.receipt.status)
            self.assertTrue(result.receipt.failure_codes)


if __name__ == "__main__":
    unittest.main()
