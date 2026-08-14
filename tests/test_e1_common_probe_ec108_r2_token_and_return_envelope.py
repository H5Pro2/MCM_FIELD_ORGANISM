from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec108_r2_token_and_return_envelope import (
    E1CommonProbeEC108R2TokenAndReturnEnvelopeError,
    _build_e1_common_probe_ec108_synthetic_envelope,
    _build_e1_common_probe_ec108_synthetic_token,
    run_e1_common_probe_ec108_synthetic_lifecycle_fixture,
)


class E1CommonProbeEC108R2TokenAndReturnEnvelopeTests(unittest.TestCase):
    def test_token_is_synthetic_bound_and_single_use(self) -> None:
        token = _build_e1_common_probe_ec108_synthetic_token()
        self.assertEqual("synthetic-fixture", token.authorization_scope)
        self.assertEqual(3208, token.maximum_field_steps)
        self.assertFalse(token.consumed)
        token.consume()
        self.assertTrue(token.consumed)
        with self.assertRaises(E1CommonProbeEC108R2TokenAndReturnEnvelopeError):
            token.consume()

    def test_envelope_requires_consumed_token(self) -> None:
        token = _build_e1_common_probe_ec108_synthetic_token()
        with self.assertRaises(E1CommonProbeEC108R2TokenAndReturnEnvelopeError):
            _build_e1_common_probe_ec108_synthetic_envelope(token)

    def test_success_binds_result_receipt_and_authorization(self) -> None:
        lifecycle = run_e1_common_probe_ec108_synthetic_lifecycle_fixture()
        envelope = lifecycle.envelope
        self.assertIsNotNone(envelope)
        assert envelope is not None
        self.assertIs(envelope.result, envelope.producer_receipt.source_result)
        self.assertEqual(
            envelope.authorization_digest,
            envelope.producer_receipt.one_shot_authorization_digest,
        )
        self.assertEqual(0, lifecycle.adapter_calls)
        self.assertFalse(lifecycle.execution_permitted)

    def test_failure_phases_are_fail_closed(self) -> None:
        before = run_e1_common_probe_ec108_synthetic_lifecycle_fixture(
            "before-consume"
        )
        after = run_e1_common_probe_ec108_synthetic_lifecycle_fixture(
            "after-consume"
        )
        self.assertFalse(before.token_consumed)
        self.assertFalse(before.envelope_returned)
        self.assertTrue(after.token_consumed)
        self.assertFalse(after.envelope_returned)
        self.assertFalse(after.retry_permitted)

    def test_changed_envelope_fails_closed(self) -> None:
        lifecycle = run_e1_common_probe_ec108_synthetic_lifecycle_fixture()
        assert lifecycle.envelope is not None
        with self.assertRaises(E1CommonProbeEC108R2TokenAndReturnEnvelopeError):
            replace(lifecycle.envelope, field_steps_executed=3207)

    def test_fixture_does_not_call_coordinator_adapter_writer_or_decider(self) -> None:
        source = inspect.getsource(
            run_e1_common_probe_ec108_synthetic_lifecycle_fixture
        )
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_e1_common_probe_real_formation_receipt_adapter(",
            "build_e1_common_probe_real_fresh_field_adapter(",
            "run_e1_common_probe_real_probe_receipt_adapter(",
            "decide_common_probe_evidence(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
