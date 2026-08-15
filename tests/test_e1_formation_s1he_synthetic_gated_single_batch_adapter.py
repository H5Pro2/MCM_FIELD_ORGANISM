from __future__ import annotations

import inspect
import unittest

import tests.test_e1_formation_s1ha_pure_real_transition_builder as field_fixture
import tests.test_e1_formation_s1hb_external_owner_origin_bridge as bridge_fixture

from mcm_field_organism.e1_formation_s1hb_external_owner_origin_bridge import (
    bind_e1_formation_s1hb_external_owner_authorization,
)
from mcm_field_organism.e1_formation_s1hc_real_single_use_token import (
    issue_e1_formation_s1hc_real_single_use_token,
)
from mcm_field_organism.e1_formation_s1he_synthetic_gated_single_batch_adapter import (
    E1FormationS1HESyntheticGatedSingleBatchAdapterError,
    build_e1_formation_s1he_synthetic_adapter_gate,
    run_e1_formation_s1he_gated_single_batch_adapter_synthetically,
)
from mcm_field_organism.e1_refined_formation_runner import _digest


class E1FormationS1HESyntheticGatedSingleBatchAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        field = field_fixture.E1FormationS1HAPureRealTransitionBuilderTests
        field.setUpClass()
        bridge = bridge_fixture.E1FormationS1HBExternalOwnerOriginBridgeTests
        bridge.setUpClass()
        cls.bridge_source = bridge
        cls.gate = bridge.gate
        cls.target = bridge.target
        cls.fresh = cls.target.selected_fresh_binding
        cls.batch = cls.target.selected_batch
        cls.carrier = cls.target.selected_initial_carrier
        cls.next_field = field.next_field
        cls.message = bridge.message
        cls.synthetic_gate = build_e1_formation_s1he_synthetic_adapter_gate()

    def setUp(self) -> None:
        unique = _digest((self.id(),))
        event = self.bridge_source._event(
            fresh_single_use_nonce_digest=unique,
            host_attestation_digest=_digest(("host", unique)),
        )
        self.authorization = bind_e1_formation_s1hb_external_owner_authorization(
            self.message,
            event,
            self.gate,
            self.target,
            origin_verifier=lambda _event: True,
        )
        self.token = issue_e1_formation_s1hc_real_single_use_token(
            self.authorization,
            self.gate,
            self.target,
        )

    def tearDown(self) -> None:
        if not self.token.retired:
            self.token.retire("real-attempt-failure")

    def _run(self, kernel):
        return run_e1_formation_s1he_gated_single_batch_adapter_synthetically(
            self.authorization,
            self.token,
            self.gate,
            self.target,
            self.fresh,
            self.batch,
            self.carrier,
            self.synthetic_gate,
            synthetic_kernel=kernel,
        )

    def test_complete_atomic_flow_returns_receipt_transition_and_envelope(self) -> None:
        observations = []

        def kernel(field, adapter, distribution, transient_inputs):
            observations.append((self.token.status, field, adapter))
            self.assertEqual(
                self.batch.step_time.start_tick,
                distribution.field_time.window_start_tick,
            )
            self.assertEqual(self.batch.step_time, transient_inputs.step_time)
            return self.next_field

        result = self._run(kernel)
        self.assertEqual("consumed", observations[0][0])
        self.assertEqual("real-field-advance", result.envelope.transition_kind)
        self.assertEqual(result.receipt.next_field_digest, result.transition.next_field_digest)
        self.assertTrue(result.atomic_complete_return)

    def test_token_is_consumed_before_kernel_and_retired_after_result(self) -> None:
        seen = []

        def kernel(*_args):
            seen.append(self.token.status)
            return self.next_field

        result = self._run(kernel)
        self.assertEqual(["consumed"], seen)
        self.assertTrue(self.token.retired)
        self.assertEqual("real-attempt-success", self.token.outcome)
        self.assertTrue(result.token_retired_after_complete_result)

    def test_kernel_failure_retires_token_and_returns_no_result(self) -> None:
        def failing_kernel(*_args):
            self.assertEqual("consumed", self.token.status)
            raise RuntimeError("synthetic failure")

        with self.assertRaisesRegex(
            E1FormationS1HESyntheticGatedSingleBatchAdapterError,
            "no partial result",
        ):
            self._run(failing_kernel)
        self.assertTrue(self.token.retired)
        self.assertEqual("real-attempt-failure", self.token.outcome)

    def test_wrong_field_output_fails_and_retires(self) -> None:
        with self.assertRaises(E1FormationS1HESyntheticGatedSingleBatchAdapterError):
            self._run(lambda *_args: self.carrier.current_field)
        self.assertTrue(self.token.retired)
        self.assertEqual("real-attempt-failure", self.token.outcome)

    def test_production_kernel_name_is_rejected_before_call(self) -> None:
        calls = []

        def forbidden(*_args):
            calls.append(True)
            return self.next_field

        forbidden.__name__ = "advance_fixed_e1_adapter_fast_shared_field_transient"
        with self.assertRaises(E1FormationS1HESyntheticGatedSingleBatchAdapterError):
            self._run(forbidden)
        self.assertEqual([], calls)
        self.assertTrue(self.token.retired)

    def test_result_reports_no_production_or_new_field_computation(self) -> None:
        result = self._run(lambda *_args: self.next_field)
        self.assertEqual(1, result.injected_kernel_calls)
        self.assertEqual(1, result.structural_field_steps)
        self.assertEqual(0, result.production_kernel_calls)
        self.assertEqual(0, result.newly_computed_field_steps)
        self.assertFalse(result.retry_permitted)
        self.assertFalse(result.persistence_performed)
        self.assertFalse(result.claims_permitted)

    def test_module_calls_no_production_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            run_e1_formation_s1he_gated_single_batch_adapter_synthetically
        )
        for forbidden in (
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
