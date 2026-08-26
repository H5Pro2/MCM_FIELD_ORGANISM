from __future__ import annotations

from dataclasses import fields, replace
import ast
import hashlib
import json
import math
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.m1_parallel_leak_replace_s_compositor import (
    COMPLETED,
    CONTRACT_ID,
    FAILURE_CODES,
    GAP_CHECKPOINTS_SECONDS,
    NOT_COMPUTABLE,
    PHASES,
    READOUT_ID,
    SOURCE_S1QQ_DIGEST,
    STATUSES,
    TRACE_ORDER,
    M1ParallelLeakBankState,
    M1ParallelLeakConfiguration,
    M1ParallelLeakReplaceSReceipt,
    M1ParallelLeakReplaceSResult,
    advance_m1_parallel_leak_replace_s,
    build_registered_m1_parallel_leak_configuration,
    build_zero_m1_parallel_leak_bank,
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
from tests.m1_parallel_leak_replace_s_s1qs_fixtures import (
    M1ParallelLeakFixture,
    build_sync_fixture,
    build_transient_fixture,
)


MODULE = "mcm_field_organism.m1_parallel_leak_replace_s_compositor"


def _run(
    fixture: M1ParallelLeakFixture, **overrides
) -> M1ParallelLeakReplaceSResult:
    values = {
        "field": fixture.field,
        "distribution": fixture.distribution,
        "interval_input": fixture.interval_input,
        "neutral_substrate_config": fixture.substrate_config,
        "fast_afterimage_config": fixture.afterimage_config,
        "m1_configuration": fixture.m1_configuration,
        "m1_prestate": fixture.m1_prestate,
    }
    values.update(overrides)
    return advance_m1_parallel_leak_replace_s(**values)


def _expected(fixture: M1ParallelLeakFixture):
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
    evidence = tuple(item.activation for item in proposal.layer.neurons)
    fast = advance_w7n_local_baseline(
        fixture.m1_configuration.fast_spec,
        fixture.m1_prestate.fast_state,
        evidence,
        duration,
    )
    slow = advance_w7n_local_baseline(
        fixture.m1_configuration.slow_spec,
        fixture.m1_prestate.slow_state,
        evidence,
        duration,
    )
    mean = tuple(
        (fast_value + slow_value) / 2.0
        for fast_value, slow_value in zip(fast.output, slow.output, strict=True)
    )
    return proposal, fast, slow, mean


def _failure_code(result: M1ParallelLeakReplaceSResult) -> str:
    if result.receipt.status != NOT_COMPUTABLE:
        raise AssertionError("expected NOT_COMPUTABLE result")
    return result.receipt.failure_codes[0]


class M1ParallelLeakReplaceSS1QSCompositorTests(unittest.TestCase):
    def test_01_module_type_status_phase_and_error_surface(self) -> None:
        self.assertEqual("m1-parallel-leak-replace-s/s1qr.v1", CONTRACT_ID)
        self.assertEqual((COMPLETED, NOT_COMPUTABLE), STATUSES)
        self.assertEqual(16, len(FAILURE_CODES))
        self.assertEqual(16, len(set(FAILURE_CODES)))
        self.assertEqual(12, len(PHASES))
        self.assertEqual(("FAST", "SLOW"), TRACE_ORDER)
        self.assertEqual("pointwise-equal-mean/v1", READOUT_ID)
        self.assertEqual(
            ("field", "next_m1_state", "receipt"),
            tuple(item.name for item in fields(M1ParallelLeakReplaceSResult)),
        )
        self.assertEqual(
            "receipt_digest", fields(M1ParallelLeakReplaceSReceipt)[-1].name
        )

    def test_02_exact_s1qq_configuration_payload_and_digest(self) -> None:
        configuration = build_registered_m1_parallel_leak_configuration()
        encoded = json.dumps(
            configuration.registration_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(SOURCE_S1QQ_DIGEST, hashlib.sha256(encoded).hexdigest())
        self.assertEqual(SOURCE_S1QQ_DIGEST, configuration.source_registration_digest)
        self.assertEqual((1.0, 4.0, 8.0), GAP_CHECKPOINTS_SECONDS)
        self.assertEqual(
            (("time_constant_seconds", 1.0),),
            configuration.fast_spec.parameter_bindings,
        )
        self.assertEqual(
            (("time_constant_seconds", 4.0),),
            configuration.slow_spec.parameter_bindings,
        )

    def test_03_deterministic_distinct_zero_fresh_states(self) -> None:
        configuration = build_registered_m1_parallel_leak_configuration()
        first = build_zero_m1_parallel_leak_bank(configuration, 3)
        second = build_zero_m1_parallel_leak_bank(configuration, 3)
        self.assertEqual(first, second)
        self.assertIsNot(first.fast_state, first.slow_state)
        self.assertEqual((0.0, 0.0, 0.0), first.fast_state.latent)
        self.assertEqual((0.0, 0.0, 0.0), first.slow_state.latent)

    def test_04_valid_synchronous_m1_step(self) -> None:
        result = _run(build_sync_fixture())
        self.assertEqual(COMPLETED, result.receipt.status)
        self.assertIsInstance(result.field, SharedMCMField)
        self.assertIsInstance(result.next_m1_state, M1ParallelLeakBankState)
        self.assertEqual("sync", result.receipt.interval_kind)

    def test_05_valid_transient_m1_step(self) -> None:
        result = _run(build_transient_fixture())
        self.assertEqual(COMPLETED, result.receipt.status)
        self.assertIsInstance(result.field, SharedMCMField)
        self.assertIsInstance(result.next_m1_state, M1ParallelLeakBankState)
        self.assertEqual("transient", result.receipt.interval_kind)

    def test_06_fast_trace_matches_existing_w7n_leak_exactly(self) -> None:
        for fixture in (build_sync_fixture(), build_transient_fixture()):
            with self.subTest(kind=type(fixture.interval_input).__name__):
                _, expected_fast, _, _ = _expected(fixture)
                result = _run(fixture)
                self.assertEqual(
                    expected_fast.state, result.next_m1_state.fast_state
                )

    def test_07_slow_trace_matches_existing_w7n_leak_exactly(self) -> None:
        for fixture in (build_sync_fixture(), build_transient_fixture()):
            with self.subTest(kind=type(fixture.interval_input).__name__):
                _, _, expected_slow, _ = _expected(fixture)
                result = _run(fixture)
                self.assertEqual(
                    expected_slow.state, result.next_m1_state.slow_state
                )

    def test_08_pointwise_equal_mean_is_exact_and_range_preserving(self) -> None:
        fixture = build_sync_fixture(values=(0.8, -0.4, 0.2))
        _, _, _, expected_mean = _expected(fixture)
        result = _run(fixture)
        actual = tuple(item.activation for item in result.field.layer.neurons)
        self.assertEqual(expected_mean, actual)
        self.assertTrue(all(-1.0 <= value <= 1.0 for value in actual))
        self.assertTrue(result.receipt.equal_mean_confirmed)

    def test_09_signed_s_is_completely_replaced_by_mean(self) -> None:
        fixture = build_sync_fixture(values=(0.8, -0.4, 0.2))
        proposal, _, _, expected_mean = _expected(fixture)
        result = _run(fixture)
        self.assertEqual(
            expected_mean,
            tuple(item.activation for item in result.field.layer.neurons),
        )
        self.assertNotEqual(
            tuple(item.activation for item in proposal.layer.neurons),
            expected_mean,
        )
        self.assertTrue(result.receipt.s_replacement_confirmed)

    def test_10_a1_h_provenance_and_one_time_advance_are_preserved(self) -> None:
        for fixture in (build_sync_fixture(), build_transient_fixture()):
            proposal, _, _, _ = _expected(fixture)
            result = _run(fixture)
            self.assertEqual(proposal.docks, result.field.docks)
            self.assertEqual(proposal.last_distribution, result.field.last_distribution)
            self.assertEqual(fixture.field.layer.tick + 1, result.field.layer.tick)
            self.assertEqual(1, result.receipt.field_time_advance_count)
            for expected, actual in zip(
                proposal.layer.neurons, result.field.layer.neurons, strict=True
            ):
                self.assertEqual(expected.afterimage, actual.afterimage)
                self.assertEqual(expected.perception, actual.perception)
                self.assertEqual(expected.neuron_id, actual.neuron_id)
                self.assertEqual(expected.position, actual.position)

    def test_11_field_bank_carry_and_digests_are_deterministic(self) -> None:
        fixture = build_sync_fixture()
        first = _run(fixture)
        duplicate = _run(fixture)
        self.assertEqual(first.receipt, duplicate.receipt)
        self.assertEqual(first.receipt.receipt_digest, duplicate.receipt.receipt_digest)
        second_fixture = build_sync_fixture(
            field=first.field,
            m1_prestate=first.next_m1_state,
            start_tick=10,
            values=(-0.2, 0.5, 0.1),
        )
        second = _run(second_fixture)
        self.assertEqual(COMPLETED, second.receipt.status)
        self.assertEqual(
            first.receipt.final_field_digest, second.receipt.input_field_digest
        )
        self.assertEqual(
            first.receipt.m1_next_state_digest,
            second.receipt.m1_prestate_digest,
        )

    def test_12_remote_private_load_does_not_change_local_output(self) -> None:
        fixture = build_sync_fixture(values=(0.8, 0.0, 0.0))
        unloaded = _run(fixture)
        loaded_state = M1ParallelLeakBankState(
            W7NLocalBaselineState("leak", (0.0, 0.0, 0.8)),
            W7NLocalBaselineState("leak", (0.0, 0.0, -0.6)),
        )
        loaded = _run(fixture, m1_prestate=loaded_state)
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
        reversed_state = M1ParallelLeakBankState(
            W7NLocalBaselineState(
                "leak", tuple(reversed(fixture.m1_prestate.fast_state.latent))
            ),
            W7NLocalBaselineState(
                "leak", tuple(reversed(fixture.m1_prestate.slow_state.latent))
            ),
        )
        permuted = _run(
            build_sync_fixture(
                field=reversed_field,
                m1_prestate=reversed_state,
            )
        )
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

    def test_14_s1qq_gap_reference_rejects_one_fixed_exponential(self) -> None:
        configuration = build_registered_m1_parallel_leak_configuration()
        fast_state = W7NLocalBaselineState("leak", (1.0,))
        slow_state = W7NLocalBaselineState("leak", (1.0,))
        means = []
        for duration in (1.0, 3.0, 4.0):
            fast = advance_w7n_local_baseline(
                configuration.fast_spec, fast_state, (0.0,), duration
            )
            slow = advance_w7n_local_baseline(
                configuration.slow_spec, slow_state, (0.0,), duration
            )
            fast_state = fast.state
            slow_state = slow.state
            means.append((fast.output[0] + slow.output[0]) / 2.0)
        expected = (
            0.5733401121214237,
            0.19309754003008825,
            0.06783537293225761,
        )
        for actual, reference in zip(means, expected, strict=True):
            self.assertAlmostEqual(reference, actual, places=15)
        tau_1_4 = -3.0 / math.log(means[1] / means[0])
        tau_4_8 = -4.0 / math.log(means[2] / means[1])
        self.assertAlmostEqual(2.7566342538378557, tau_1_4, places=14)
        self.assertAlmostEqual(3.8236835782814316, tau_4_8, places=14)
        self.assertNotEqual(tau_1_4, tau_4_8)

    def test_15_private_import_export_and_closed_branch_boundaries(self) -> None:
        root = Path(__file__).parents[1] / "mcm_field_organism"
        source = (root / "m1_parallel_leak_replace_s_compositor.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source)
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
                    "local_synaptic_memory_candidate",
                    "passive_synaptic_memory_comparison",
                    "dynamic_substrate",
                    "runner",
                    "orchestrator",
                    "current_api",
                )
            )
        )
        self.assertIn("local_state_replace_s_compositor_core", source)
        self.assertFalse(
            hasattr(current_api, "advance_m1_parallel_leak_replace_s")
        )
        self.assertFalse(
            hasattr(mcm_field_organism, "advance_m1_parallel_leak_replace_s")
        )

    def test_16_mutation_classes_01_to_05_fail_with_exact_codes(self) -> None:
        fixture = build_sync_fixture()
        invalid_configuration = replace(
            fixture.m1_configuration, readout_id="unregistered-readout"
        )
        aliased_state = M1ParallelLeakBankState(
            fixture.m1_prestate.fast_state,
            fixture.m1_prestate.fast_state,
        )
        cases = (
            (_run(fixture, field=object()), "QR_INPUT_TYPE_INVALID"),
            (
                _run(
                    fixture,
                    field=build_w7m_capacity_function_matrix_adapter().initial_field,
                ),
                "QR_FIELD_ROLE_INVALID",
            ),
            (
                _run(
                    fixture,
                    interval_input=MCMFieldStepTime(
                        "organism.test", 0, 9, 10.0
                    ),
                ),
                "QR_DISTRIBUTION_OR_INTERVAL_INVALID",
            ),
            (
                _run(fixture, m1_configuration=invalid_configuration),
                "QR_CONFIGURATION_INVALID",
            ),
            (
                _run(fixture, m1_prestate=aliased_state),
                "QR_M1_PRESTATE_INVALID",
            ),
        )
        for result, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(expected, _failure_code(result))

    def test_17_mutation_classes_06_to_10_fail_with_exact_codes(self) -> None:
        fixture = build_sync_fixture()
        short_state = M1ParallelLeakBankState(
            W7NLocalBaselineState("leak", (0.0, 0.0)),
            W7NLocalBaselineState("leak", (0.0, 0.0)),
        )
        geometry = _run(fixture, m1_prestate=short_state)
        with patch(
            f"{MODULE}.advance_neutral_fast_shared_field",
            side_effect=NeutralLocalFieldSubstrateError("controlled"),
        ):
            a1_failure = _run(fixture)
        with patch(f"{MODULE}._a1_proposal_valid", return_value=False):
            a1_invalid = _run(fixture)

        def fail_fast(spec, state, evidence, duration):
            if spec.equation_id == "baseline.m1.fast-local-leak.v1":
                raise W7NCapacityFunctionBaselineError("controlled fast")
            return advance_w7n_local_baseline(spec, state, evidence, duration)

        def fail_slow(spec, state, evidence, duration):
            if spec.equation_id == "baseline.m1.slow-local-leak.v1":
                raise W7NCapacityFunctionBaselineError("controlled slow")
            return advance_w7n_local_baseline(spec, state, evidence, duration)

        with patch(f"{MODULE}.advance_w7n_local_baseline", side_effect=fail_fast):
            fast_failure = _run(fixture)
        with patch(f"{MODULE}.advance_w7n_local_baseline", side_effect=fail_slow):
            slow_failure = _run(fixture)
        cases = (
            (geometry, "QR_GEOMETRY_OR_ORDER_MISMATCH"),
            (a1_failure, "QR_A1_ADVANCE_FAILED"),
            (a1_invalid, "QR_A1_PROPOSAL_INVALID"),
            (fast_failure, "QR_FAST_ADVANCE_FAILED"),
            (slow_failure, "QR_SLOW_ADVANCE_FAILED"),
        )
        for result, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(expected, _failure_code(result))

    def test_18_mutation_classes_11_to_16_fail_with_exact_codes(self) -> None:
        fixture = build_sync_fixture()

        def invalid_slow(spec, state, evidence, duration):
            if spec.equation_id == "baseline.m1.slow-local-leak.v1":
                return SimpleNamespace(state=state, output=(math.nan,) * 3)
            return advance_w7n_local_baseline(spec, state, evidence, duration)

        with patch(
            f"{MODULE}.advance_w7n_local_baseline", side_effect=invalid_slow
        ):
            trace_pair = _run(fixture)
        with patch(f"{MODULE}._mean_output", return_value=(2.0, 2.0, 2.0)):
            mean = _run(fixture)
        with patch(
            f"{MODULE}._materialize_replace_s", side_effect=ValueError("controlled")
        ):
            replacement = _run(fixture)
        with patch(f"{MODULE}._final_identity_valid", return_value=False):
            identity = _run(fixture)
        with patch(f"{MODULE}._field_time_advance_count", return_value=2):
            time_count = _run(fixture)
        with patch(f"{MODULE}._atomic_output_valid", return_value=False):
            atomic = _run(fixture)
        cases = (
            (trace_pair, "QR_TRACE_PAIR_INVALID"),
            (mean, "QR_MEAN_READOUT_INVALID"),
            (replacement, "QR_S_REPLACEMENT_FAILED"),
            (identity, "QR_H_OR_PROVENANCE_CHANGED"),
            (time_count, "QR_FIELD_TIME_CARDINALITY_FAILED"),
            (atomic, "QR_ATOMIC_OUTPUT_FAILED"),
        )
        for result, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(expected, _failure_code(result))

    def test_19_not_computable_is_atomic_without_partial_output(self) -> None:
        fixture = build_sync_fixture()
        failures = (
            _run(fixture, field=object()),
            _run(
                fixture,
                m1_prestate=M1ParallelLeakBankState(
                    W7NLocalBaselineState("leak", (0.0, 0.0)),
                    W7NLocalBaselineState("leak", (0.0, 0.0)),
                ),
            ),
        )
        for result in failures:
            self.assertEqual(NOT_COMPUTABLE, result.field)
            self.assertEqual(NOT_COMPUTABLE, result.next_m1_state)
            self.assertEqual(NOT_COMPUTABLE, result.receipt.status)
            self.assertTrue(result.receipt.failure_codes)

    def test_20_both_traces_receive_same_evidence_duration_without_cross_read(self) -> None:
        fixture = build_sync_fixture()
        records = []

        def record(spec, state, evidence, duration):
            result = advance_w7n_local_baseline(spec, state, evidence, duration)
            records.append((spec, state, evidence, duration, result))
            return result

        with patch(f"{MODULE}.advance_w7n_local_baseline", side_effect=record):
            result = _run(fixture)
        self.assertEqual(COMPLETED, result.receipt.status)
        self.assertEqual(2, len(records))
        self.assertIs(records[0][2], records[1][2])
        self.assertEqual(records[0][3], records[1][3])
        self.assertIs(records[0][1], fixture.m1_prestate.fast_state)
        self.assertIs(records[1][1], fixture.m1_prestate.slow_state)
        self.assertIsNot(records[1][1], records[0][4].state)


if __name__ == "__main__":
    unittest.main()
