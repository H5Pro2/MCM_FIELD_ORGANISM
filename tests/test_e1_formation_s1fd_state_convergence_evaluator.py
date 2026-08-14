from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_formation_s1fd_state_convergence_evaluator import (
    E1FormationS1FDStateConvergenceEvaluatorError,
    build_e1_formation_s1fd_synthetic_state_vector,
    evaluate_e1_formation_s1fd_state_convergence,
)


_EDGES = ("edge-0", "edge-1")
_REFINEMENTS = ("r2", "r4", "r8")
_ROLES = (
    "active-ab",
    "active-ba",
    "identity-ab",
    "formation-ablated-ab",
    "formation-ablated-ba",
)


def _inventory(
    *,
    mode: str = "converged",
    control_error: float = 0.0,
):
    if mode == "converged":
        ab = {"r2": (0.71, 0.29), "r4": (0.7004, 0.2996), "r8": (0.7, 0.3)}
        ba = {"r2": (0.29, 0.71), "r4": (0.2996, 0.7004), "r8": (0.3, 0.7)}
    elif mode == "not-converged":
        ab = {"r2": (0.701, 0.299), "r4": (0.71, 0.29), "r8": (0.7, 0.3)}
        ba = {"r2": (0.299, 0.701), "r4": (0.29, 0.71), "r8": (0.3, 0.7)}
    elif mode == "no-order":
        ab = {key: (0.5, 0.5) for key in _REFINEMENTS}
        ba = dict(ab)
    else:
        raise AssertionError(mode)
    states = []
    for refinement in _REFINEMENTS:
        for role in _ROLES:
            if role == "active-ab":
                vector = ab[refinement]
            elif role == "active-ba":
                vector = ba[refinement]
            elif role == "identity-ab":
                vector = ab[refinement]
                if refinement == "r8" and control_error:
                    vector = (vector[0] + control_error, vector[1])
            else:
                vector = (0.0, 0.0)
            states.append(
                build_e1_formation_s1fd_synthetic_state_vector(
                    refinement_id=refinement,
                    formation_role=role,
                    ordered_edge_ids=_EDGES,
                    ordered_binding_vector=vector,
                )
            )
    return tuple(states)


class E1FormationS1FDStateConvergenceEvaluatorTests(unittest.TestCase):
    def test_convergent_fixture_is_diagnostic_only(self) -> None:
        result = evaluate_e1_formation_s1fd_state_convergence(_inventory())
        self.assertEqual(
            "FORMATION_STATE_CONVERGED_DIAGNOSTIC_ONLY", result.decision
        )
        self.assertTrue(result.controls_valid)
        self.assertTrue(result.order_state_distinguishable)
        self.assertTrue(result.all_components_converged)
        self.assertEqual(
            ("active-ab", "active-ba", "active-order"),
            tuple(item.component for item in result.components),
        )
        self.assertFalse(result.memory_claim_allowed)

    def test_nonconvergent_fixture_is_rejected_numerically(self) -> None:
        result = evaluate_e1_formation_s1fd_state_convergence(
            _inventory(mode="not-converged")
        )
        self.assertEqual("FORMATION_STATE_NOT_CONVERGED", result.decision)
        self.assertFalse(result.all_components_converged)

    def test_control_failure_has_priority(self) -> None:
        result = evaluate_e1_formation_s1fd_state_convergence(
            _inventory(control_error=2e-12)
        )
        self.assertEqual("INVALID_FORMATION_STATE_CONTROLS", result.decision)
        self.assertFalse(result.controls_valid)

    def test_no_order_fixture_is_reported_without_claim(self) -> None:
        result = evaluate_e1_formation_s1fd_state_convergence(
            _inventory(mode="no-order")
        )
        self.assertEqual(
            "NO_DISTINGUISHABLE_FORMATION_ORDER_STATE", result.decision
        )
        self.assertFalse(result.order_state_distinguishable)

    def test_inventory_edge_order_and_state_digest_are_fail_closed(self) -> None:
        inventory = _inventory()
        with self.assertRaises(E1FormationS1FDStateConvergenceEvaluatorError):
            evaluate_e1_formation_s1fd_state_convergence(inventory[:-1])
        with self.assertRaises(E1FormationS1FDStateConvergenceEvaluatorError):
            evaluate_e1_formation_s1fd_state_convergence(
                inventory[:1] + (replace(inventory[1], state_digest="changed"),) + inventory[2:]
            )
        changed = build_e1_formation_s1fd_synthetic_state_vector(
            refinement_id="r2",
            formation_role="active-ba",
            ordered_edge_ids=tuple(reversed(_EDGES)),
            ordered_binding_vector=(0.29, 0.71),
        )
        with self.assertRaises(E1FormationS1FDStateConvergenceEvaluatorError):
            evaluate_e1_formation_s1fd_state_convergence(
                inventory[:1] + (changed,) + inventory[2:]
            )

    def test_evaluator_contains_no_field_probe_or_writer_call(self) -> None:
        source = inspect.getsource(evaluate_e1_formation_s1fd_state_convergence)
        for forbidden in (
            "run_prepared_real_formation_arm_in_memory(",
            "run_e1_asynchronous_field(",
            "run_e1_common_probe_real_probe_wrapper(",
            "decide_common_probe_evidence(",
            "write_text(",
            "write_bytes(",
            "open(",
        ):
            self.assertNotIn(forbidden, source)

    def test_result_is_deterministic_and_not_publicly_exported(self) -> None:
        first = evaluate_e1_formation_s1fd_state_convergence(_inventory())
        second = evaluate_e1_formation_s1fd_state_convergence(_inventory())
        self.assertEqual(first.result_digest, second.result_digest)
        import mcm_field_organism
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(mcm_field_organism, "evaluate_e1_formation_s1fd_state_convergence")
        )
        self.assertFalse(
            hasattr(current_api, "evaluate_e1_formation_s1fd_state_convergence")
        )


if __name__ == "__main__":
    unittest.main()
