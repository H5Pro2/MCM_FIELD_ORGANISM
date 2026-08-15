from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

import tests.test_e1_formation_s1gy_single_batch_total_preflight as preflight_fixture

from mcm_field_organism.e1_formation_s1gz_real_path_implementation_plan import (
    E1FormationS1GZRealPathImplementationPlanError,
    S1_GZ_IMPLEMENTATION_SEQUENCE,
    S1_GZ_RUNTIME_SEQUENCE,
    build_e1_formation_s1gz_real_path_implementation_plan,
)


class E1FormationS1GZRealPathImplementationPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = preflight_fixture.E1FormationS1GYSingleBatchTotalPreflightTests
        source.setUpClass()
        cls.preflight = source()._prepare()

    def _build(self):
        return build_e1_formation_s1gz_real_path_implementation_plan(
            self.preflight
        )

    def test_all_ten_plan_checks_pass(self) -> None:
        plan = self._build()
        self.assertEqual(10, len(plan.checks))
        self.assertTrue(all(value for _, value in plan.checks))
        self.assertEqual(self.preflight.preflight_digest, plan.source_s1gy_preflight_digest)
        self.assertEqual(self.preflight.target_digest, plan.target_digest)

    def test_implementation_sequence_covers_five_components_once(self) -> None:
        plan = self._build()
        self.assertEqual(S1_GZ_IMPLEMENTATION_SEQUENCE, plan.implementation_sequence)
        self.assertEqual(5, len(set(plan.implementation_sequence)))
        self.assertEqual("pure-real-transition-builder", plan.implementation_sequence[0])
        self.assertEqual("gated-real-single-batch-adapter", plan.implementation_sequence[-1])

    def test_runtime_sequence_preserves_atomic_order(self) -> None:
        plan = self._build()
        runtime = plan.runtime_sequence
        self.assertEqual(S1_GZ_RUNTIME_SEQUENCE, runtime)
        consume = runtime.index("consume-token-immediately-before-adapter-call")
        adapter = runtime.index("perform-exactly-one-adapter-call-and-one-field-step")
        receipt = runtime.index(
            "create-authentic-receipt-inside-the-same-adapter-boundary"
        )
        transition = runtime.index(
            "build-pure-real-transition-from-receipt-and-new-field"
        )
        self.assertEqual(consume + 1, adapter)
        self.assertLess(adapter, receipt)
        self.assertLess(receipt, transition)

    def test_component_contracts_separate_ownership(self) -> None:
        plan = self._build()
        self.assertEqual(5, len(plan.component_contracts))
        self.assertIn(
            "adapter-boundary-alone-consumes-token-calls-kernel-and-seals-receipt",
            plan.atomic_ownership_boundaries,
        )
        self.assertIn(
            "transition-builder-never-owns-authorization-token-or-kernel-access",
            plan.atomic_ownership_boundaries,
        )

    def test_plan_does_not_pretend_implementation_or_authorization(self) -> None:
        plan = self._build()
        self.assertFalse(plan.implementation_started)
        self.assertFalse(plan.implementation_ready)
        self.assertFalse(plan.authorization_request_ready)
        self.assertFalse(plan.authorization_present)
        self.assertFalse(plan.token_created)
        self.assertFalse(plan.receipt_created)
        self.assertFalse(plan.transition_created)

    def test_plan_does_not_execute_persist_or_claim(self) -> None:
        plan = self._build()
        self.assertEqual((1, 1), (plan.maximum_adapter_calls, plan.maximum_field_steps))
        self.assertEqual((0, 0), (plan.adapter_calls, plan.field_steps_executed))
        self.assertFalse(plan.persistence_performed)
        self.assertFalse(plan.claims_permitted)
        self.assertEqual(
            "FIVE_COMPONENT_IMPLEMENTATION_ORDER_BOUND_EXECUTION_CLOSED",
            plan.decision,
        )

    def test_tampering_and_effectful_calls_fail_closed(self) -> None:
        plan = self._build()
        with self.assertRaises(E1FormationS1GZRealPathImplementationPlanError):
            replace(plan, implementation_started=True)
        with self.assertRaises(E1FormationS1GZRealPathImplementationPlanError):
            replace(plan, adapter_calls=1)
        source = inspect.getsource(
            build_e1_formation_s1gz_real_path_implementation_plan
        )
        for forbidden in (
            "E1FormationS1GWExternalOwnerAuthorization(",
            "issue_e1_formation_s1gt_synthetic_single_use_token(",
            "E1FormationS1GVRealAdapterCallReceipt(",
            "bind_e1_formation_s1gq_carrier_transition_envelope(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            ".consume(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
