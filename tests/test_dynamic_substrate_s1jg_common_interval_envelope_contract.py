from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_dts1_common_boundary_2n import (
    build_dts1_s1jf_implementation_receipt,
)
from mcm_field_organism.dynamic_substrate_s1jg_common_interval_envelope_contract import (
    DTS1S1JGCommonIntervalEnvelopeContractError,
    S1_JG_DECISION,
    build_dts1_s1jg_common_interval_envelope_contract,
)


class DTS1S1JGCommonIntervalEnvelopeContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1jg_common_interval_envelope_contract()

    def test_binds_exact_s1jf_receipt(self) -> None:
        self.assertEqual(
            build_dts1_s1jf_implementation_receipt().receipt_digest,
            self._contract().source_s1jf_digest,
        )

    def test_binds_complete_orchestration_envelope_schema(self) -> None:
        fields = dict(self._contract().orchestration_envelope_fields)
        self.assertEqual(10, len(fields))
        for role in ("sequence_digest", "ordinal", "canonical_node_ids", "edge_inventory_digest", "prestate_directive", "prestate_source_digest", "receptor_contact", "step_time", "checkpoint_after_interval", "interval_digest"):
            self.assertIn(role, fields)

    def test_model_facing_view_excludes_labels_directives_and_sidecars(self) -> None:
        self.assertEqual(("field", "distribution", "step_time", "geometry_digest", "input_digest"), tuple(row[0] for row in self._contract().model_facing_fields))
        exclusions = " ".join(self._contract().model_facing_exclusions)
        self.assertIn("profile-block-arm-case", exclusions)
        self.assertIn("boundary-role-event-label", exclusions)
        self.assertIn("candidate-anatomy-participation", exclusions)

    def test_binds_all_four_corrected_sequence_topologies(self) -> None:
        rows = {row[0]: row[1:] for row in self._contract().profile_sequence_topology}
        self.assertEqual(4, self._contract().profile_block_count)
        self.assertEqual((2, 2, 2), rows["P_IE_CAUSAL_TWO_SUBSTEP"][:3])
        self.assertEqual((1, 3, 3), rows["P_IH_ATTENUATION"][:3])
        self.assertEqual((2, 4, 1), rows["P_IK_INTERFERENCE"][:3])
        self.assertEqual((2, 4, 1), rows["P_IN_RELEASE_REUSE"][:3])

    def test_binds_candidate_sidecars_outside_common_view(self) -> None:
        rules = " ".join(self._contract().candidate_sidecar_rules)
        self.assertIn("P_IE-only-DTS1", rules)
        self.assertIn("P_IN-only-DTS1", rules)
        self.assertIn("not-fields-of-the-common-envelope-or-model-facing-view", rules)
        self.assertIn("B1-through-B6-receive-no-sidecar", rules)

    def test_binds_exact_cardinality(self) -> None:
        cardinality = dict(self._contract().cardinality)
        self.assertEqual((4, 3, 8, 8), tuple(cardinality[key] for key in ("P_IE_envelopes_per_model_per_refinement", "P_IH_envelopes_per_model_per_refinement", "P_IK_envelopes_per_model_per_refinement", "P_IN_envelopes_per_model_per_refinement")))
        self.assertEqual(23, self._contract().envelopes_per_model_per_refinement)
        self.assertEqual((24, 28), (self._contract().baseline_case_count, self._contract().profile_component_count))

    def test_prevents_schedule_reconstruction_and_checkpoint_feedback(self) -> None:
        rules = " ".join(self._contract().sequence_rules)
        self.assertIn("before-any-model-role-is-selected", rules)
        self.assertIn("merged-split-delayed-repeated-reordered-or-skipped", rules)
        self.assertIn("checkpoint-capture-does-not-feed-back", rules)

    def test_selects_no_values_implementation_or_execution(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.schema_bound)
        self.assertTrue(contract.information_barrier_bound)
        self.assertTrue(contract.all_four_exposure_topologies_bound)
        for value in (
            contract.concrete_clock_ticks_selected,
            contract.concrete_envelope_digests_bound,
            contract.interval_envelope_implemented,
            contract.adapters_implemented,
            contract.baseline_models_executed,
            contract.runtime_integration_present,
            contract.research_execution_permitted,
        ):
            self.assertFalse(value)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertEqual(S1_JG_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1JGCommonIntervalEnvelopeContractError):
            replace(contract, envelopes_per_model_per_refinement=22)
        with self.assertRaises(DTS1S1JGCommonIntervalEnvelopeContractError):
            replace(contract, interval_envelope_implemented=True)
        source = inspect.getsource(build_dts1_s1jg_common_interval_envelope_contract)
        for forbidden in ("compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
