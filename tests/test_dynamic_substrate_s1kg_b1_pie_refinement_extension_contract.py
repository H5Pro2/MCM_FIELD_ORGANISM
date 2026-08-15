from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1kg_b1_pie_refinement_extension_contract import (
    DTS1S1KGB1PIERefinementExtensionContractError,
    S1_KG_BOUND_R2_COMPARISON_DIGEST,
    S1_KG_DECISION,
    build_dts1_s1kg_b1_pie_refinement_extension_contract,
)


class DTS1S1KGB1PIERefinementExtensionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1kg_b1_pie_refinement_extension_contract()

    def test_binds_exact_s1kf_source_and_r2_comparison(self) -> None:
        self.assertEqual(64, len(self.contract.source_s1kf_digest))
        self.assertEqual(
            S1_KG_BOUND_R2_COMPARISON_DIGEST,
            self.contract.bound_r2_comparison_digest,
        )

    def test_targets_only_registered_b1_pie_r4_and_r8(self) -> None:
        self.assertEqual((
            "B1:P_IE_CAUSAL_TWO_SUBSTEP:r4",
            "B1:P_IE_CAUSAL_TWO_SUBSTEP:r8",
        ), self.contract.target_replica_ids)
        self.assertEqual((4, 8), tuple(row[4] for row in self.contract.target_replica_records))
        self.assertTrue(all(row[1] == "B1" for row in self.contract.target_replica_records))

    def test_extends_only_replica_id_input_registry(self) -> None:
        extension = dict(self.contract.input_registry_extension)
        self.assertEqual(("schema_id", "replica_id"), extension["caller_fields"])
        self.assertFalse(extension["caller_supplied_state_or_parameters"])

    def test_binds_independent_replica_and_sequence_fresh_starts(self) -> None:
        rules = " ".join(self.contract.fresh_start_rules)
        self.assertIn("independent-S1-KB-corrected-B1-fresh-state", rules)
        self.assertIn("each-start-fresh-inside-each-refinement", rules)
        self.assertIn("no-field-private-state-or-provenance-carries-between", rules)

    def test_binds_exact_eight_new_interval_budget(self) -> None:
        self.assertEqual((2, 4, 8), (
            self.contract.target_replica_count,
            self.contract.intervals_per_target_replica,
            self.contract.maximum_new_interval_calls,
        ))
        self.assertEqual(0, dict(self.contract.execution_budget)["retry_or_repeat_calls"])

    def test_requires_two_atomic_v2_outputs_and_r2_comparison_identity(self) -> None:
        rules = " ".join(self.contract.output_acceptance_rules)
        self.assertIn("atomic-mcm.s1jz.complete-replica-output.v2", rules)
        self.assertIn("bit-equal-the-bound-r2-comparison-digest", rules)
        self.assertIn("must-not-be-used-for-equality", rules)
        self.assertIn("both-r4-and-r8-must-pass", rules)

    def test_executes_nothing_and_keeps_matrix_runtime_closed(self) -> None:
        self.assertFalse(self.contract.runner_extension_implemented)
        self.assertEqual((0, 0, 0), (
            self.contract.target_replicas_executed,
            self.contract.interval_calls_executed,
            self.contract.complete_matrix_cases_executed,
        ))
        self.assertFalse(self.contract.runtime_integration_present)

    def test_authorizes_only_exact_extension_implementation(self) -> None:
        self.assertTrue(self.contract.exact_extension_implementation_authorized_next_stage)
        self.assertEqual(S1_KG_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1kg_b1_pie_refinement_extension_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1KGB1PIERefinementExtensionContractError):
            replace(self.contract, runner_extension_implemented=True)
        source = inspect.getsource(build_dts1_s1kg_b1_pie_refinement_extension_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
