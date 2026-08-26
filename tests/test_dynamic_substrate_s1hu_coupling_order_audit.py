from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1hu_coupling_order_audit import (
    DTS1S1HUCouplingOrderAuditError,
    S1_HU_DECISION,
    audit_dts1_s1hu_coupling_order,
)


class DTS1S1HUCouplingOrderAuditTests(unittest.TestCase):
    def _audit(self):
        return audit_dts1_s1hu_coupling_order()

    def test_audits_exactly_one_closed_prestate_parallel_order(self) -> None:
        audit = self._audit()
        self.assertEqual(1, audit.audited_order_count)
        self.assertEqual(
            "CLOSED_PRESTATE_PARALLEL_READ_ATOMIC_COMMIT",
            audit.order_id,
        )
        self.assertTrue(audit.one_closed_prestate_for_both_proposals)
        self.assertTrue(audit.atomic_pair_commit_required)

    def test_stage_order_keeps_resource_and_field_proposals_independent(self) -> None:
        stages = self._audit().stage_order
        self.assertLess(
            stages.index("derive-p_n-from-S_n-only-for-every-existing-edge"),
            stages.index("compute-A_next-from-A_n-p_n-and-Delta_t-with-s1hp"),
        )
        self.assertLess(
            stages.index("derive-active-or-ablated-G_n-from-A_n-only"),
            stages.index("compute-L_next-from-L_n-W_n-G_n-and-unchanged-fast-field-boundaries"),
        )
        self.assertEqual(
            "atomically-commit-pair-L_next-A_next-or-return-no-output",
            stages[-1],
        )

    def test_causal_identities_bind_explicit_one_substep_latency(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.explicit_one_substep_latency)
        for identity in (
            "p_n-never-reads-S_next-or-H_next",
            "G_n-never-reads-A_next",
            "new-binding-affects-the-field-no-earlier-than-the-next-substep",
            "new-field-values-affect-participation-no-earlier-than-the-next-substep",
        ):
            self.assertIn(identity, audit.causal_identities)

    def test_p0_a0_and_first_active_step_identities_are_explicit(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.exact_p0_a0_field_identity_required)
        for required in (
            "P0-delegates-bit-exactly-to-existing-neutral-field-path-without-dts1-arithmetic",
            "A0-evolves-dts1-but-delegates-field-proposal-to-the-exact-P0-path",
            "A1-and-A0-from-identical-prestate-produce-identical-A_next-in-that-substep",
            "A1-with-zero-prestate-binding-produces-the-same-first-field-proposal-as-A0",
        ):
            self.assertIn(required, audit.ablation_identities)

    def test_refinement_must_reduce_pair_residual_and_reader_latency(self) -> None:
        obligations = self._audit().refinement_obligations
        self.assertIn(
            "coarse-versus-fine-complete-pair-residual-must-decrease-before-use",
            obligations,
        )
        self.assertIn(
            "one-substep-reader-latency-must-shrink-under-refinement",
            obligations,
        )
        self.assertIn(
            "failure-of-refinement-stops-coupled-runtime-work",
            obligations,
        )

    def test_poststate_midpoint_implicit_and_partial_orders_are_not_active(self) -> None:
        rejected = dict(self._audit().rejected_orders)
        self.assertEqual(
            {
                "resource-first-poststate-reader",
                "field-first-endstate-participation",
                "midpoint-half-resource-full-field-half-resource",
                "implicit-iterated-coupled-solve",
                "call-order-partial-commit",
            },
            set(rejected),
        )

    def test_zulassen_selects_no_integrator_implementation_values_or_execution(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.coupling_order_selected)
        self.assertTrue(audit.first_order_coupling_only)
        for value in (
            audit.field_integrator_selected,
            audit.coupled_step_implemented,
            audit.material_rate_values_selected,
            audit.runtime_integration_present,
            audit.research_execution_permitted,
            audit.functional_effect_proven,
            audit.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, audit.field_steps_executed)
        self.assertEqual(S1_HU_DECISION, audit.decision)

    def test_audit_is_deterministic_tamper_evident_and_static(self) -> None:
        audit = self._audit()
        self.assertEqual(audit.audit_digest, self._audit().audit_digest)
        with self.assertRaises(DTS1S1HUCouplingOrderAuditError):
            replace(audit, audited_order_count=2)
        with self.assertRaises(DTS1S1HUCouplingOrderAuditError):
            replace(audit, explicit_one_substep_latency=False)
        source = inspect.getsource(audit_dts1_s1hu_coupling_order)
        for forbidden in ("numpy", "advance_", "field_runner", "open("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
