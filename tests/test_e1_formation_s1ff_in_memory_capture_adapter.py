from __future__ import annotations

from dataclasses import asdict
import inspect
import unittest

from mcm_field_organism.e1_confirmation_formation_runner import (
    E1ConfirmationFormationArmAudit,
)
from mcm_field_organism.e1_confirmation_prepared_formation_consumer import (
    S1_EC7_FORMATION_ARMS,
    S1_EC7_REFINEMENTS,
)
from mcm_field_organism.e1_confirmation_prepared_real_formation_kernel import (
    E1PreparedRealFormationArmResult,
)
from mcm_field_organism.e1_formation_s1fd_state_convergence_evaluator import (
    evaluate_e1_formation_s1fd_state_convergence,
)
from mcm_field_organism.e1_formation_s1ff_in_memory_capture_adapter import (
    E1FormationS1FFInMemoryCaptureAdapterError,
    capture_e1_formation_s1ff_in_memory,
)
from mcm_field_organism.e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1EdgeBinding,
    E1LocalEdgePlasticityContract,
    E1LocalEdgePlasticityState,
)
from mcm_field_organism.e1_refined_formation_runner import _digest, _state_payload


_EDGES = (("n0", "n1"), ("n2", "n3"))
_CONTRACT = E1LocalEdgePlasticityContract(E1_CONTRACT_ID, 1.0, 0.1, 0.05, 0.2)
_AB = {
    "r2": (0.71, 0.29),
    "r4": (0.7004, 0.2996),
    "r8": (0.7, 0.3),
}
_BA = {
    "r2": (0.29, 0.71),
    "r4": (0.2996, 0.7004),
    "r8": (0.3, 0.7),
}


def _state(values: tuple[float, ...]) -> E1LocalEdgePlasticityState:
    return E1LocalEdgePlasticityState(
        contract=_CONTRACT,
        edge_bindings=tuple(
            E1EdgeBinding(first, second, value)
            for (first, second), value in zip(_EDGES, values, strict=True)
        ),
        edge_inventory_digest=_digest(_EDGES),
    )


def _typed_result(
    refinement: str,
    arm: str,
    state: E1LocalEdgePlasticityState,
) -> E1PreparedRealFormationArmResult:
    enabled = not arm.endswith("formation_ablated")
    audit = E1ConfirmationFormationArmAudit(
        refinement_id=refinement,
        arm_id=arm,
        handoff_digest=_digest(("s1ff-handoff", refinement, arm)),
        field_digest=_digest(("s1ff-field", refinement, arm)),
        source_support_count=2,
        assigned_event_count=2,
        resource_budget_error=0.0,
        formation_enabled=enabled,
        history_backreaction_enabled=False,
        state_remained_neutral=not enabled,
    )
    values = {
        "arm_id": arm,
        "refinement_id": refinement,
        "formation_enabled": enabled,
        "initial_field_digest": _digest(("s1ff-initial-field", refinement, arm)),
        "initial_state_digest": _digest(("s1ff-initial-state", refinement, arm)),
        "output_state": state,
        "output_state_digest": _digest(_state_payload(state)),
        "audit": audit,
        "input_objects_preserved": True,
        "copied_inputs_used": True,
        "canonical_execution_permitted": False,
        "claims_permitted": False,
    }
    payload = {
        name: value for name, value in values.items() if name not in {"output_state", "audit"}
    }
    payload["output_state"] = _state_payload(state)
    payload["audit"] = asdict(audit)
    return E1PreparedRealFormationArmResult(
        **values,
        result_digest=_digest(payload),
    )


def _inventory() -> tuple[E1PreparedRealFormationArmResult, ...]:
    results = []
    for refinement, _ in S1_EC7_REFINEMENTS:
        for arm in S1_EC7_FORMATION_ARMS:
            if arm in {"ab", "ab_identity"}:
                values = _AB[refinement]
            elif arm == "ba":
                values = _BA[refinement]
            else:
                values = (0.0, 0.0)
            results.append(_typed_result(refinement, arm, _state(values)))
    return tuple(results)


class E1FormationS1FFInMemoryCaptureAdapterTests(unittest.TestCase):
    def test_fifteen_typed_results_are_captured_and_evaluable(self) -> None:
        capture = capture_e1_formation_s1ff_in_memory(_inventory())
        self.assertEqual(15, capture.source_result_count)
        self.assertEqual(15, len(capture.state_vectors))
        self.assertTrue(capture.each_source_result_consumed_once)
        self.assertTrue(capture.source_state_objects_separated)
        decision = evaluate_e1_formation_s1fd_state_convergence(
            capture.state_vectors
        )
        self.assertEqual(
            "FORMATION_STATE_CONVERGED_DIAGNOSTIC_ONLY", decision.decision
        )
        self.assertFalse(decision.memory_claim_allowed)

    def test_role_mapping_and_source_digests_are_exact(self) -> None:
        source = _inventory()
        capture = capture_e1_formation_s1ff_in_memory(source)
        expected_roles = (
            "active-ab",
            "active-ba",
            "identity-ab",
            "formation-ablated-ab",
            "formation-ablated-ba",
        ) * 3
        self.assertEqual(
            expected_roles,
            tuple(item.formation_role for item in capture.state_vectors),
        )
        self.assertEqual(
            tuple(item.result_digest for item in source),
            tuple(
                item.source_formation_result_digest
                for item in capture.state_vectors
            ),
        )

    def test_incomplete_reordered_or_tampered_inventory_fails_closed(self) -> None:
        source = _inventory()
        with self.assertRaises(E1FormationS1FFInMemoryCaptureAdapterError):
            capture_e1_formation_s1ff_in_memory(source[:-1])
        with self.assertRaises(E1FormationS1FFInMemoryCaptureAdapterError):
            capture_e1_formation_s1ff_in_memory(
                (source[1], source[0]) + source[2:]
            )
        object.__setattr__(source[0], "result_digest", "changed")
        with self.assertRaises(E1FormationS1FFInMemoryCaptureAdapterError):
            capture_e1_formation_s1ff_in_memory(source)

    def test_shared_state_object_fails_closed(self) -> None:
        source = list(_inventory())
        shared = source[0].output_state
        source[1] = _typed_result("r2", "ba", shared)
        with self.assertRaises(E1FormationS1FFInMemoryCaptureAdapterError):
            capture_e1_formation_s1ff_in_memory(tuple(source))

    def test_capture_is_deterministic_and_has_no_side_effect_flags(self) -> None:
        first = capture_e1_formation_s1ff_in_memory(_inventory())
        second = capture_e1_formation_s1ff_in_memory(_inventory())
        self.assertEqual(first.capture_digest, second.capture_digest)
        self.assertTrue(first.synthetic_in_memory_capture_performed)
        self.assertFalse(first.formation_execution_performed)
        self.assertFalse(first.probe_execution_performed)
        self.assertFalse(first.persistence_performed)
        self.assertFalse(first.memory_claim_allowed)

    def test_adapter_calls_no_formation_probe_evaluator_or_writer(self) -> None:
        source = inspect.getsource(capture_e1_formation_s1ff_in_memory)
        for forbidden in (
            "run_prepared_real_formation_arm_in_memory(",
            "run_e1_asynchronous_field(",
            "run_e1_common_probe_real_probe_wrapper(",
            "evaluate_e1_formation_s1fd_state_convergence(",
            "write_text(",
            "write_bytes(",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
