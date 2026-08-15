from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

import tests.test_e1_formation_s1gx_deterministic_single_batch_target as target_fixture

from mcm_field_organism.e1_formation_s1gy_single_batch_total_preflight import (
    E1FormationS1GYSingleBatchTotalPreflightError,
    S1_GY_IMPLEMENTATION_BLOCKERS,
    prepare_e1_formation_s1gy_single_batch_total_preflight,
)


class E1FormationS1GYSingleBatchTotalPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = target_fixture.E1FormationS1GXDeterministicSingleBatchTargetTests
        source.setUpClass()
        cls.bridge = source.bridge
        cls.gate = source.gate
        cls.target = source()._select()

    def _prepare(self):
        return prepare_e1_formation_s1gy_single_batch_total_preflight(
            self.bridge,
            self.gate,
            self.target,
        )

    def test_all_twelve_static_gates_pass_for_exact_target(self) -> None:
        preflight = self._prepare()
        self.assertEqual(12, len(preflight.static_gates))
        self.assertTrue(all(value for _, value in preflight.static_gates))
        self.assertTrue(preflight.static_contracts_complete)
        self.assertEqual(
            ("r2", "fixed-adapter-ab", 0),
            (preflight.refinement_id, preflight.role_id, preflight.batch_index),
        )

    def test_preflight_preserves_one_call_and_step_scope(self) -> None:
        preflight = self._prepare()
        self.assertEqual((1, 1), (
            preflight.maximum_adapter_calls,
            preflight.maximum_field_steps,
        ))
        self.assertEqual(self.target.target_digest, preflight.target_digest)
        self.assertEqual(
            self.target.selected_carrier_digest,
            preflight.carrier_digest,
        )

    def test_five_implementation_blockers_are_reported_not_hidden(self) -> None:
        preflight = self._prepare()
        self.assertEqual(S1_GY_IMPLEMENTATION_BLOCKERS, preflight.implementation_blockers)
        self.assertEqual(5, len(preflight.implementation_blockers))
        self.assertFalse(preflight.implementation_ready)
        self.assertFalse(preflight.authorization_request_ready)

    def test_no_authorization_token_receipt_builder_or_adapter_is_present(self) -> None:
        preflight = self._prepare()
        self.assertFalse(preflight.authorization_present)
        self.assertFalse(preflight.real_token_present)
        self.assertFalse(preflight.receipt_factory_present)
        self.assertFalse(preflight.transition_builder_present)
        self.assertFalse(preflight.real_adapter_present)

    def test_preflight_does_not_execute_persist_or_claim(self) -> None:
        preflight = self._prepare()
        self.assertFalse(preflight.transition_created)
        self.assertEqual((0, 0), (
            preflight.adapter_calls,
            preflight.field_steps_executed,
        ))
        self.assertFalse(preflight.persistence_performed)
        self.assertFalse(preflight.claims_permitted)
        self.assertEqual(
            "STATIC_SINGLE_BATCH_PREFLIGHT_PASSES_"
            "IMPLEMENTATION_COMPONENTS_MISSING",
            preflight.decision,
        )

    def test_tampering_with_readiness_fails_closed(self) -> None:
        preflight = self._prepare()
        with self.assertRaises(E1FormationS1GYSingleBatchTotalPreflightError):
            replace(preflight, implementation_ready=True)
        with self.assertRaises(E1FormationS1GYSingleBatchTotalPreflightError):
            replace(preflight, authorization_request_ready=True)

    def test_preflight_calls_no_transition_adapter_kernel_token_or_writer(self) -> None:
        source = inspect.getsource(
            prepare_e1_formation_s1gy_single_batch_total_preflight
        )
        for forbidden in (
            "advance_e1_formation_s1gn_live_field_carrier_synthetically(",
            "bind_e1_formation_s1gq_carrier_transition_envelope(",
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "issue_e1_formation_s1gt_synthetic_single_use_token(",
            ".consume(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
