from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_formation_s1fg_fresh_run_insertion_contract import (
    E1FormationS1FGFreshRunInsertionContractError,
    audit_e1_formation_s1fg_fresh_run_insertion_contract,
)


class E1FormationS1FGFreshRunInsertionContractTests(unittest.TestCase):
    def test_insertion_is_between_complete_formation_and_handoff(self) -> None:
        contract = audit_e1_formation_s1fg_fresh_run_insertion_contract()
        self.assertEqual(
            "execute-full-r2-r4-r8-five-arm-formation",
            contract.reference_predecessor_transition,
        )
        self.assertEqual(
            "build-complete-s1ec14-payload-while-states-are-live",
            contract.reference_successor_transition,
        )
        self.assertEqual(15, contract.required_flat_result_count)
        self.assertEqual("r2", contract.source_refinements[0][0])
        self.assertEqual("r8", contract.source_refinements[-1][0])

    def test_flattening_and_capture_sequence_are_explicit(self) -> None:
        contract = audit_e1_formation_s1fg_fresh_run_insertion_contract()
        self.assertIn("refinement-major:r2-r4-r8", contract.flattening_rule)
        self.assertEqual(5, len(contract.source_formation_arms))
        self.assertIn(
            "capture-fifteen-results-with-s1ff-in-memory",
            contract.insertion_sequence,
        )
        self.assertIn(
            "evaluate-captured-vectors-with-s1fd-before-probe",
            contract.insertion_sequence,
        )

    def test_historical_run_is_reference_only(self) -> None:
        contract = audit_e1_formation_s1fg_fresh_run_insertion_contract()
        self.assertTrue(
            contract.historical_ec16_used_as_architecture_reference_only
        )
        self.assertFalse(contract.historical_artifact_reuse_permitted)
        self.assertFalse(contract.historical_authorization_reuse_permitted)
        self.assertTrue(contract.fresh_run_contract_required)
        self.assertTrue(contract.new_owner_authorization_required)

    def test_contract_opens_no_execution_or_claim(self) -> None:
        contract = audit_e1_formation_s1fg_fresh_run_insertion_contract()
        self.assertFalse(contract.formation_execution_permitted)
        self.assertFalse(contract.capture_execution_permitted)
        self.assertFalse(contract.probe_execution_permitted)
        self.assertFalse(contract.persistence_permitted)
        self.assertFalse(contract.memory_claim_permitted)
        self.assertEqual(
            "INSERTION_POINT_BOUND_FRESH_RUN_CONTRACT_MISSING",
            contract.decision,
        )

    def test_contract_is_deterministic_and_tamper_evident(self) -> None:
        first = audit_e1_formation_s1fg_fresh_run_insertion_contract()
        second = audit_e1_formation_s1fg_fresh_run_insertion_contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(E1FormationS1FGFreshRunInsertionContractError):
            replace(first, historical_authorization_reuse_permitted=True)

    def test_audit_calls_no_formation_capture_probe_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_formation_s1fg_fresh_run_insertion_contract
        )
        for forbidden in (
            "consume_prepared_full_formation(",
            "run_small_five_arm_formation_in_memory(",
            "capture_e1_formation_s1ff_in_memory(",
            "evaluate_e1_formation_s1fd_state_convergence(",
            "build_full_formation_handoff_envelope(",
            "run_full_persistent_probe(",
            "write_text(",
            "write_bytes(",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
