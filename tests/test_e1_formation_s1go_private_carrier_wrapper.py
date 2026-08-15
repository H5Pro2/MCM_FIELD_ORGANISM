from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from tests import (
    test_e1_formation_s1gk_fixed_adapter_real_wrapper_contract as contract_fixture,
)

from mcm_field_organism.e1_formation_s1gk_fixed_adapter_real_wrapper_contract import (
    prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract,
)
from mcm_field_organism.e1_formation_s1gl_private_fixed_adapter_wrapper import (
    E1FormationS1GLPrivateFixedAdapterWrapperError,
    build_e1_formation_s1gl_synthetic_only_gate,
)
from mcm_field_organism.e1_formation_s1gn_live_field_carrier import (
    advance_e1_formation_s1gn_live_field_carrier_synthetically,
)
from mcm_field_organism.e1_formation_s1go_private_carrier_wrapper import (
    E1FormationS1GOPrivateCarrierWrapperError,
    run_e1_formation_s1go_private_carrier_wrapper,
)


class E1FormationS1GOPrivateCarrierWrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = contract_fixture.E1FormationS1GKFixedAdapterRealWrapperContractTests
        source.setUpClass()
        cls.bridge = source.bridge
        cls.contract = prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract(
            source.bridge,
            source.integration,
        )

    def _run(self, **kwargs):
        return run_e1_formation_s1go_private_carrier_wrapper(
            self.contract,
            self.bridge,
            build_e1_formation_s1gl_synthetic_only_gate(),
            **kwargs,
        )

    def test_carrier_wrapper_consumes_all_six_arms_and_batches(self) -> None:
        result = self._run()
        self.assertEqual(
            (6, 2800, 2800, 660),
            (
                result.arm_count,
                result.carrier_transition_calls,
                result.accounted_field_steps,
                result.source_support_count,
            ),
        )
        self.assertEqual(
            (("r2", 400), ("r4", 800), ("r8", 1600)),
            result.refinement_step_counts,
        )
        self.assertTrue(result.all_batches_consumed_once_in_order)
        self.assertTrue(result.all_transitions_validated_by_shared_envelope)
        self.assertEqual(2800, len(result.transition_envelope_digests))
        self.assertEqual(
            "SIX_ARM_WRAPPER_SHARED_ENVELOPE_VALIDATED_"
            "SYNTHETIC_GATE_REMAINS_CLOSED",
            result.decision,
        )

    def test_terminal_carriers_hold_fresh_fields_and_zero_real_steps(
        self,
    ) -> None:
        result = self._run()
        self.assertEqual((6, 0), (
            result.terminal_carrier_count,
            result.actual_field_steps_executed,
        ))
        self.assertTrue(result.all_field_objects_carried_explicitly)
        self.assertTrue(result.all_terminal_carriers_complete)
        self.assertTrue(
            all(
                carrier.current_field is fresh.fresh_field
                for fresh, carrier in zip(
                    self.bridge.fresh_bindings,
                    result.terminal_carriers,
                    strict=True,
                )
            )
        )

    def test_outputs_are_read_from_carried_fields_and_bound_to_receipts(self) -> None:
        result = self._run()
        self.assertEqual((6, 6), (
            result.terminal_output_count,
            result.common_receipt_count,
        ))
        self.assertTrue(result.all_outputs_match_carried_field_vectors)
        self.assertTrue(result.all_outputs_and_receipts_bound)
        self.assertFalse(result.legacy_token_wrapper_called)
        self.assertFalse(result.real_batch_adapter_called)

    def test_preserves_fields_states_adapters_and_closed_claim_boundary(self) -> None:
        result = self._run()
        self.assertTrue(result.fresh_fields_preserved)
        self.assertTrue(result.source_states_preserved)
        self.assertTrue(result.fixed_adapters_preserved)
        self.assertTrue(result.atomic_return_complete)
        self.assertFalse(result.persistence_performed)
        self.assertFalse(result.claims_permitted)

    def test_transition_failure_returns_no_partial_aggregate(self) -> None:
        calls = []

        def failing_transition(fresh, batch, carrier):
            calls.append((fresh.binding_digest, batch.batch_index))
            if len(calls) == 17:
                raise RuntimeError("synthetic carrier failure")
            return advance_e1_formation_s1gn_live_field_carrier_synthetically(
                fresh,
                batch,
                carrier,
            )

        with self.assertRaisesRegex(
            E1FormationS1GOPrivateCarrierWrapperError,
            "no aggregate returned",
        ):
            self._run(carrier_transition=failing_transition)
        self.assertEqual(17, len(calls))

    def test_foreign_transition_and_open_gate_fail_closed(self) -> None:
        gate = build_e1_formation_s1gl_synthetic_only_gate()
        with self.assertRaises(E1FormationS1GLPrivateFixedAdapterWrapperError):
            replace(gate, real_field_execution_permitted=True)

        first_transition = None

        def stale_transition(fresh, batch, carrier):
            nonlocal first_transition
            result = advance_e1_formation_s1gn_live_field_carrier_synthetically(
                fresh,
                batch,
                carrier,
            )
            if first_transition is None:
                first_transition = result
                return result
            return first_transition

        with self.assertRaises(E1FormationS1GOPrivateCarrierWrapperError):
            self._run(carrier_transition=stale_transition)

    def test_wrapper_calls_no_legacy_token_wrapper_real_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            run_e1_formation_s1go_private_carrier_wrapper
        )
        for forbidden in (
            "run_e1_formation_s1gl_private_fixed_adapter_wrapper(",
            "build_e1_formation_s1gl_synthetic_batch_receipt(",
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)

    def test_wrapper_validates_transitions_through_shared_envelope(self) -> None:
        source = inspect.getsource(
            run_e1_formation_s1go_private_carrier_wrapper
        )
        self.assertIn(
            "bind_e1_formation_s1gq_carrier_transition_envelope(",
            source,
        )
        self.assertIn("synthetic-no-field-advance", source)
        self.assertNotIn(
            "isinstance(\n                    transition, "
            "E1FormationS1GNLiveFieldCarrierTransition",
            source,
        )


if __name__ == "__main__":
    unittest.main()
