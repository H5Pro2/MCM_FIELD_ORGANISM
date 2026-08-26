from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_dts1_common_boundary import (
    build_dts1_s1iz_implementation_receipt,
)
from mcm_field_organism.dynamic_substrate_s1id_causal_field_readout_audit_contract import (
    build_dts1_s1id_causal_field_readout_audit_contract,
)
from mcm_field_organism.dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    build_dts1_s1ja_finite_configuration_matrix_contract,
)
from mcm_field_organism.dynamic_substrate_s1jg_common_interval_envelope_contract import (
    build_dts1_s1jg_common_interval_envelope_contract,
)
from mcm_field_organism.dynamic_substrate_s1jh_finite_common_interval_fixture_contract import (
    DTS1S1JHFiniteCommonIntervalFixtureContractError,
    S1_JH_DECISION,
    build_dts1_s1jh_finite_common_interval_fixture_contract,
)


class DTS1S1JHFiniteCommonIntervalFixtureContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1jh_finite_common_interval_fixture_contract()

    def test_binds_exact_authoritative_sources(self) -> None:
        contract = self._contract()
        self.assertEqual(build_dts1_s1jg_common_interval_envelope_contract().contract_digest, contract.source_s1jg_digest)
        self.assertEqual(build_dts1_s1id_causal_field_readout_audit_contract().contract_digest, contract.source_s1id_digest)
        self.assertEqual(build_dts1_s1iz_implementation_receipt().receipt_digest, contract.source_s1iz_digest)
        self.assertEqual(build_dts1_s1ja_finite_configuration_matrix_contract().contract_digest, contract.source_s1ja_digest)

    def test_binds_one_label_neutral_half_unit_step(self) -> None:
        self.assertEqual(("mcm.s1jh.common.interval", 0, 1, 2.0), self._contract().common_step_time)

    def test_binds_only_corrected_source_vectors(self) -> None:
        fixtures = {row[0]: row for row in self._contract().source_fixtures}
        self.assertEqual(((-1.0, 1.0), (-0.2, 0.2)), fixtures["P_IE_INITIAL_SH"][2:4])
        self.assertEqual(((-0.5, 0.5), (0.0, 0.0)), fixtures["A_BOUNDARY_2N"][2:4])
        self.assertEqual((-0.5, 0.0, 0.5), fixtures["PROBE_BOUNDARY"][2])
        self.assertNotIn((-1.0, 0.0, 1.0), tuple(row[2] for row in fixtures.values()))

    def test_binds_seven_sequences_and_twenty_three_envelopes(self) -> None:
        contract = self._contract()
        self.assertEqual((7, 23), (contract.sequence_count, contract.envelope_count))
        counts = {row[0]: row[3] for row in contract.sequence_fixtures}
        self.assertEqual((2, 2, 3, 4, 4, 4, 4), tuple(counts.values()))

    def test_binds_corrected_order_and_checkpoint_positions(self) -> None:
        contract = self._contract()
        sequence_by_digest = {row[4]: row[0] for row in contract.sequence_fixtures}
        rows: dict[str, list[tuple[object, ...]]] = {}
        for envelope in contract.envelope_fixtures:
            rows.setdefault(sequence_by_digest[envelope[0]], []).append(envelope)
        self.assertEqual(("APPLY_BOUNDARY_3N",) * 4, tuple(row[4] for row in rows["P_IK_A_B_A"]))
        self.assertEqual((False, False, False, True), tuple(row[8] for row in rows["P_IK_A_B_A"]))
        self.assertEqual((True, True, True), tuple(row[8] for row in rows["P_IH_A_A_A"]))

    def test_carry_links_to_immediately_prior_interval_digest(self) -> None:
        contract = self._contract()
        sequence_by_digest = {row[4]: row[0] for row in contract.sequence_fixtures}
        rows = [row for row in contract.envelope_fixtures if sequence_by_digest[row[0]] == "P_IE_F_HIGH"]
        self.assertEqual("CARRY_PRIOR_SH", rows[1][4])
        self.assertEqual(rows[0][9], rows[1][5])

    def test_contacts_clocks_and_sidecars_preserve_information_barrier(self) -> None:
        contract = self._contract()
        self.assertTrue(all(set(row[2]) == {0.0} for row in contract.contact_fixtures))
        self.assertTrue(all(row[7] == contract.common_step_time for row in contract.envelope_fixtures))
        self.assertEqual(4, len(contract.candidate_sidecars))
        rules = " ".join(contract.information_barrier_rules)
        self.assertIn("orchestrator-only", rules)
        self.assertIn("never-delivered-to-B1-through-B6", rules)

    def test_binds_finite_double_fixture_budget(self) -> None:
        budget = dict(self._contract().refinement_and_budget)
        self.assertEqual((2, 4, 8), budget["refinement_levels"])
        self.assertEqual(966, budget["double_fixture_max_interval_invocations"])
        self.assertEqual(798, budget["double_fixture_max_boundary_applications"])
        self.assertEqual(462, budget["double_fixture_max_checkpoint_captures"])

    def test_selects_no_implementation_or_execution(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.concrete_values_and_digests_bound)
        self.assertTrue(contract.private_fixture_implementation_authorized_next_stage)
        for value in (contract.common_interval_fixture_implemented, contract.adapters_implemented, contract.baseline_models_executed, contract.runtime_integration_present, contract.research_execution_permitted):
            self.assertFalse(value)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertEqual(S1_JH_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1JHFiniteCommonIntervalFixtureContractError):
            replace(contract, envelope_count=22)
        with self.assertRaises(DTS1S1JHFiniteCommonIntervalFixtureContractError):
            replace(contract, common_interval_fixture_implemented=True)
        source = inspect.getsource(build_dts1_s1jh_finite_common_interval_fixture_contract)
        for forbidden in ("compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
