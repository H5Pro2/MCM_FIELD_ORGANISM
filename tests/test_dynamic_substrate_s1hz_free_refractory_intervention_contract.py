from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1hh_function_falsification_contract import (
    build_dynamic_substrate_s1hh_contract,
)
from mcm_field_organism.dynamic_substrate_s1hz_free_refractory_intervention_contract import (
    DTS1S1HZFreeRefractoryInterventionContractError,
    S1_HZ_DECISION,
    build_dts1_s1hz_free_refractory_intervention_contract,
)


class DTS1S1HZFreeRefractoryInterventionContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1hz_free_refractory_intervention_contract()

    def test_binds_s1hh_candidate_and_successful_s1hy_receipt(self) -> None:
        contract = self._contract()
        self.assertEqual(
            build_dynamic_substrate_s1hh_contract().contract_digest,
            contract.source_s1hh_contract_digest,
        )
        self.assertEqual(
            "c6f75a0a1009c51dd03ad546ae04c4aded34ecf7ccd0b687bcbac4d715f24de2",
            contract.source_s1hy_audit_receipt_digest,
        )

    def test_binds_exactly_two_arms_differing_only_free_refractory(self) -> None:
        contract = self._contract()
        self.assertEqual(2, len(contract.arm_ids))
        joined = " ".join(contract.matched_prestate_rules)
        for required in (
            "identical-S-and-H",
            "identical-conductive-bound-resource",
            "identical-positive-current-participation",
            "only-free-versus-refractory-partition-may-differ",
            "strictly-more-free-and-strictly-less-refractory",
        ):
            self.assertIn(required, joined)

    def test_construction_uses_derived_free_resource_on_one_edge(self) -> None:
        contract = self._contract()
        joined = " ".join(contract.intervention_construction)
        self.assertTrue(contract.isolated_single_edge_required)
        self.assertIn("one-isolated-existing-edge", joined)
        self.assertIn("existing-S1HI-half-share-ledger", joined)
        self.assertIn("do-not-write-store-or-normalize-free-resource", joined)

    def test_primary_measure_is_direct_accepted_engagement(self) -> None:
        contract = self._contract()
        joined = " ".join(contract.measurement_rules)
        self.assertTrue(contract.direct_resource_measurement_required)
        self.assertIn("existing-S1HP-passive-edge-transfer-ledger", joined)
        self.assertIn("accepted-engagement-on-the-target-edge", joined)
        self.assertIn("strictly-greater-than", joined)
        self.assertIn("net-binding-and-field-output-are-not-primary", joined)

    def test_three_exact_null_controls_are_bound(self) -> None:
        controls = dict(self._contract().null_controls)
        self.assertEqual(
            {
                "N01_EQUAL_PARTITION_REPEAT",
                "N02_ZERO_PARTICIPATION",
                "N03_ZERO_BINDING_RATE",
            },
            set(controls),
        )
        self.assertIn("bit-exact", controls["N01_EQUAL_PARTITION_REPEAT"])
        self.assertIn("exactly-zero", controls["N02_ZERO_PARTICIPATION"])
        self.assertIn("exactly-zero", controls["N03_ZERO_BINDING_RATE"])

    def test_all_s1hh_baseline_groups_have_state_space_counterpredictions(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.complete_baseline_set_required)
        self.assertEqual(
            (
                "fixed-adapter-and-frozen-e1",
                "leaky-trace-and-integrator",
                "dynamic-two-state-e1",
                "f3-and-const-v",
                "fast-afterimage",
            ),
            tuple(name for name, _ in contract.baseline_counterpredictions),
        )

    def test_acceptance_and_every_failure_are_atomic(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.atomic_decision_required)
        self.assertIn(
            "one-failure-makes-the-whole-intervention-audit-STOPP-with-no-partial-PASS",
            contract.acceptance_rules,
        )
        self.assertEqual(9, len(contract.stopp_conditions))
        self.assertIn(
            "F_HIGH-engagement-not-strictly-greater-than-R_HIGH-engagement",
            contract.stopp_conditions,
        )

    def test_equation_values_runtime_execution_and_claims_remain_closed(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.existing_s1hp_transfer_law_reused)
        self.assertTrue(contract.finite_fixture_audit_contract_authorized_next_stage)
        for value in (
            contract.equation_added_or_changed,
            contract.parameter_values_selected,
            contract.intervention_implemented,
            contract.intervention_executed,
            contract.field_response_measured,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
            contract.functional_effect_proven,
            contract.claims_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual(0, contract.technical_field_steps_executed)
        self.assertEqual(0, contract.research_field_steps_executed)
        self.assertEqual(S1_HZ_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_static(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1HZFreeRefractoryInterventionContractError):
            replace(contract, field_response_measured=True)
        with self.assertRaises(DTS1S1HZFreeRefractoryInterventionContractError):
            replace(contract, direct_resource_measurement_required=False)
        source = inspect.getsource(
            build_dts1_s1hz_free_refractory_intervention_contract
        )
        for forbidden in ("advance_", "compute_", "numpy", "open(", "field_runner"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
