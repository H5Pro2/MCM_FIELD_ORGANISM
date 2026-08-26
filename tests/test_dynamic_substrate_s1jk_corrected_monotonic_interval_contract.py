from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1jh_finite_common_interval_fixture_contract import (
    build_dts1_s1jh_finite_common_interval_fixture_contract,
)
from mcm_field_organism.dynamic_substrate_s1jj_interval_clock_compatibility_precheck import (
    build_dts1_s1jj_interval_clock_compatibility_precheck,
)
from mcm_field_organism.dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    DTS1S1JKCorrectedMonotonicIntervalContractError,
    S1_JK_DECISION,
    build_dts1_s1jk_corrected_monotonic_interval_contract,
)


class DTS1S1JKCorrectedMonotonicIntervalContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1jk_corrected_monotonic_interval_contract()

    def test_binds_exact_s1jj_and_s1jh_sources(self) -> None:
        contract = self._contract()
        self.assertEqual(build_dts1_s1jj_interval_clock_compatibility_precheck().audit_digest, contract.source_s1jj_digest)
        self.assertEqual(build_dts1_s1jh_finite_common_interval_fixture_contract().contract_digest, contract.source_s1jh_digest)

    def test_binds_four_contiguous_half_unit_windows(self) -> None:
        self.assertEqual(
            ((1, "mcm.s1jk.common.interval", 0, 1, 2.0), (2, "mcm.s1jk.common.interval", 1, 2, 2.0), (3, "mcm.s1jk.common.interval", 2, 3, 2.0), (4, "mcm.s1jk.common.interval", 3, 4, 2.0)),
            self._contract().ordinal_step_times,
        )

    def test_all_seven_sequences_are_monotonic_and_restart_at_zero(self) -> None:
        contract = self._contract()
        sequence_by_digest = {row[4]: row for row in contract.sequence_fixtures}
        grouped: dict[str, list[tuple[object, ...]]] = {}
        for row in contract.envelope_fixtures:
            grouped.setdefault(sequence_by_digest[row[0]][0], []).append(row)
        self.assertEqual(7, len(grouped))
        for rows in grouped.values():
            self.assertEqual(0, rows[0][7][1])
            for prior, current in zip(rows, rows[1:]):
                self.assertEqual(prior[7][2], current[7][1])
                self.assertGreater(current[7][2], prior[7][2])

    def test_preserves_non_time_s1jh_fixtures_exactly(self) -> None:
        old = build_dts1_s1jh_finite_common_interval_fixture_contract()
        new = self._contract()
        self.assertEqual(old.geometries, new.preserved_geometries)
        self.assertEqual(old.source_fixtures, new.preserved_source_fixtures)
        self.assertEqual(old.contact_fixtures, new.preserved_contact_fixtures)
        self.assertEqual(old.candidate_sidecars, new.preserved_candidate_sidecars)
        self.assertEqual(old.refinement_and_budget, new.preserved_refinement_and_budget)

    def test_recomputes_unique_sequence_and_interval_digests(self) -> None:
        contract = self._contract()
        sequence_digests = tuple(row[4] for row in contract.sequence_fixtures)
        interval_digests = tuple(row[9] for row in contract.envelope_fixtures)
        self.assertEqual(7, len(set(sequence_digests)))
        self.assertEqual(23, len(set(interval_digests)))
        old = build_dts1_s1jh_finite_common_interval_fixture_contract()
        self.assertTrue(set(sequence_digests).isdisjoint(row[4] for row in old.sequence_fixtures))
        self.assertTrue(set(interval_digests).isdisjoint(row[9] for row in old.envelope_fixtures))

    def test_carry_links_to_prior_corrected_interval(self) -> None:
        contract = self._contract()
        sequence_by_digest = {row[4]: row[0] for row in contract.sequence_fixtures}
        rows = [row for row in contract.envelope_fixtures if sequence_by_digest[row[0]] == "P_IE_F_HIGH"]
        self.assertEqual("CARRY_PRIOR_SH", rows[1][4])
        self.assertEqual(rows[0][9], rows[1][5])

    def test_keeps_materialization_and_execution_closed(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.monotonic_time_and_digests_bound)
        for value in (contract.materialization_schema_complete, contract.common_interval_fixture_implemented, contract.adapters_implemented, contract.baseline_models_executed, contract.runtime_integration_present, contract.research_execution_permitted):
            self.assertFalse(value)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertTrue(contract.corrected_materialization_schema_contract_authorized_next_stage)
        self.assertEqual(S1_JK_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1JKCorrectedMonotonicIntervalContractError):
            replace(contract, corrected_continuation_envelope_count=15)
        with self.assertRaises(DTS1S1JKCorrectedMonotonicIntervalContractError):
            replace(contract, common_interval_fixture_implemented=True)
        source = inspect.getsource(build_dts1_s1jk_corrected_monotonic_interval_contract)
        for forbidden in ("apply_", "compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
