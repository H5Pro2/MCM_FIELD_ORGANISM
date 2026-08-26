from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_formation_s1fh_fresh_capture_one_shot_contract import (
    prepare_e1_formation_s1fh_fresh_capture_one_shot_contract,
)
from mcm_field_organism.e1_formation_s1fi_fresh_capture_preflight import (
    E1FormationS1FIResourceSnapshot,
    prepare_e1_formation_s1fi_inputs,
    preflight_e1_formation_s1fi_fresh_capture,
)
from mcm_field_organism.e1_formation_s1fk_real_coordinator_contract import (
    E1FormationS1FKOwnerAuthorizationToken,
    E1FormationS1FKRealCoordinatorContractError,
    S1_FK_REQUIRED_AUTHORIZATION_TEXT,
    audit_e1_formation_s1fk_real_coordinator_contract,
)
from mcm_field_organism.e1_refined_formation_runner import _digest


class E1FormationS1FKRealCoordinatorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.one_shot = prepare_e1_formation_s1fh_fresh_capture_one_shot_contract()
        inputs = prepare_e1_formation_s1fi_inputs(
            Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json")
        )
        payload = {"free_memory_bytes": 6 * 1024**3}
        resources = E1FormationS1FIResourceSnapshot(
            **payload, snapshot_digest=_digest(payload)
        )
        cls.preflight = preflight_e1_formation_s1fi_fresh_capture(
            cls.one_shot, inputs, resources
        )

    def test_real_callable_sequence_is_bound_but_closed(self) -> None:
        contract = audit_e1_formation_s1fk_real_coordinator_contract(
            self.one_shot
        )
        self.assertEqual(14_000, contract.maximum_formation_field_steps)
        self.assertEqual((1, 0), (
            contract.maximum_execution_count,
            contract.maximum_retry_count,
        ))
        self.assertIn("run-r2-five-arm-formation", contract.coordinator_sequence)
        self.assertIn("capture-with-s1ff", contract.coordinator_sequence)
        self.assertIn("evaluate-with-s1fd", contract.coordinator_sequence)
        self.assertFalse(contract.execution_permitted)

    def test_exact_authorization_token_is_single_use(self) -> None:
        contract = audit_e1_formation_s1fk_real_coordinator_contract(
            self.one_shot
        )
        token = E1FormationS1FKOwnerAuthorizationToken(
            S1_FK_REQUIRED_AUTHORIZATION_TEXT,
            contract.contract_digest,
            self.preflight,
        )
        self.assertFalse(token.consumed)
        token.consume()
        self.assertTrue(token.consumed)
        with self.assertRaises(E1FormationS1FKRealCoordinatorContractError):
            token.consume()

    def test_wrong_authorization_text_is_rejected(self) -> None:
        contract = audit_e1_formation_s1fk_real_coordinator_contract(
            self.one_shot
        )
        with self.assertRaises(E1FormationS1FKRealCoordinatorContractError):
            E1FormationS1FKOwnerAuthorizationToken(
                "ok weiter",
                contract.contract_digest,
                self.preflight,
            )

    def test_probe_persistence_retry_and_partial_results_are_closed(self) -> None:
        contract = audit_e1_formation_s1fk_real_coordinator_contract(
            self.one_shot
        )
        self.assertFalse(contract.probe_execution_permitted)
        self.assertFalse(contract.persistence_permitted)
        self.assertFalse(contract.automatic_retry_permitted)
        self.assertFalse(contract.posthoc_parameter_change_permitted)
        self.assertFalse(contract.partial_result_return_permitted)
        self.assertFalse(contract.memory_claim_permitted)

    def test_contract_is_deterministic_and_tamper_evident(self) -> None:
        first = audit_e1_formation_s1fk_real_coordinator_contract(self.one_shot)
        second = audit_e1_formation_s1fk_real_coordinator_contract(self.one_shot)
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(E1FormationS1FKRealCoordinatorContractError):
            replace(first, execution_permitted=True)

    def test_audit_calls_no_field_capture_evaluator_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_formation_s1fk_real_coordinator_contract
        )
        for forbidden in (
            "run_small_five_arm_formation_in_memory(",
            "run_prepared_real_formation_arm_in_memory(",
            "read_e1_formation_s1fi_resource_snapshot(",
            "capture_e1_formation_s1ff_in_memory(",
            "evaluate_e1_formation_s1fd_state_convergence(",
            "write_text(",
            "write_bytes(",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
