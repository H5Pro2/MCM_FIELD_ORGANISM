from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
import inspect
import unittest

from mcm_field_organism.kfs1_t1_transition import (
    KFS1T1Ledger,
    KFS1T1TransitionError,
    advance_kfs1_t1_edge,
    compute_kfs1_t1_edge_participation,
)


EDGE = "edge:carrier-a:carrier-b"


def ledger(free: float, bound: float, blocked: float) -> KFS1T1Ledger:
    return KFS1T1Ledger(EDGE, 1.0, free, bound, blocked)


class KFS1S1NGT1TransitionTests(unittest.TestCase):
    def test_p01_fresh_null_is_bit_equal(self) -> None:
        pre = ledger(1.0, 0.0, 0.0)
        result = advance_kfs1_t1_edge(pre, 0.0, 0.0)
        self.assertEqual(0.0, result.participation)
        self.assertEqual(pre, result.post_ledger)
        self.assertEqual(("HOLD_FREE",), result.transition_ids)

    def test_p02_positive_contact_binds_to_target(self) -> None:
        result = advance_kfs1_t1_edge(ledger(1.0, 0.0, 0.0), -1.0, 1.0)
        self.assertEqual(1.0, result.participation)
        self.assertEqual(1.0, result.target_bound)
        self.assertEqual(ledger(0.0, 1.0, 0.0), result.post_ledger)
        self.assertEqual(1.0, result.transfers.bind)

    def test_p03_repeated_contact_at_target_has_no_transfer(self) -> None:
        pre = ledger(0.0, 1.0, 0.0)
        result = advance_kfs1_t1_edge(pre, -1.0, 1.0)
        self.assertEqual(pre, result.post_ledger)
        self.assertEqual(("HOLD_BOUND",), result.transition_ids)

    def test_p04_first_null_moves_bound_to_blocked_only(self) -> None:
        result = advance_kfs1_t1_edge(ledger(0.0, 1.0, 0.0), 0.0, 0.0)
        self.assertEqual(ledger(0.0, 0.0, 1.0), result.post_ledger)
        self.assertEqual(1.0, result.transfers.block)
        self.assertEqual(0.0, result.transfers.release)

    def test_p05_second_null_releases_preexisting_blocked(self) -> None:
        result = advance_kfs1_t1_edge(ledger(0.0, 0.0, 1.0), 0.0, 0.0)
        self.assertEqual(ledger(1.0, 0.0, 0.0), result.post_ledger)
        self.assertEqual(1.0, result.transfers.release)
        self.assertEqual(("LOCAL_REFRACTORY_RELEASE",), result.transition_ids)

    def test_p06_positive_contact_does_not_release_blocked(self) -> None:
        pre = ledger(0.0, 0.0, 1.0)
        result = advance_kfs1_t1_edge(pre, -1.0, 1.0)
        self.assertEqual(pre, result.post_ledger)
        self.assertEqual(0.0, result.transfers.bind)
        self.assertEqual(0.0, result.transfers.release)
        self.assertEqual(("HOLD_BLOCKED",), result.transition_ids)

    def test_p07_same_contact_differs_only_by_local_prestate(self) -> None:
        free_result = advance_kfs1_t1_edge(ledger(1.0, 0.0, 0.0), -1.0, 1.0)
        blocked_result = advance_kfs1_t1_edge(ledger(0.0, 0.0, 1.0), -1.0, 1.0)
        self.assertNotEqual(free_result.transfers, blocked_result.transfers)
        self.assertNotEqual(free_result.post_ledger, blocked_result.post_ledger)

    def test_p08_other_edge_state_cannot_change_this_edge_result(self) -> None:
        local = ledger(0.5, 0.5, 0.0)
        first = advance_kfs1_t1_edge(local, -1.0, 0.0)
        _unrelated = KFS1T1Ledger("edge:other-a:other-b", 1.0, 0.0, 0.0, 1.0)
        second = advance_kfs1_t1_edge(local, -1.0, 0.0)
        self.assertEqual(first, second)

    def test_parameter_free_observable_is_symmetric_and_bounded(self) -> None:
        self.assertEqual(
            compute_kfs1_t1_edge_participation(-0.5, 1.0),
            compute_kfs1_t1_edge_participation(1.0, -0.5),
        )
        self.assertEqual(0.0, compute_kfs1_t1_edge_participation(0.25, 0.25))
        with self.assertRaises(KFS1T1TransitionError):
            compute_kfs1_t1_edge_participation(-1.01, 0.0)

    def test_input_and_result_are_immutable_and_conserved(self) -> None:
        pre = ledger(0.5, 0.25, 0.25)
        result = advance_kfs1_t1_edge(pre, -1.0, 0.0)
        self.assertEqual(1.0, result.post_ledger.free + result.post_ledger.bound + result.post_ledger.blocked)
        self.assertEqual(ledger(0.5, 0.25, 0.25), pre)
        with self.assertRaises(FrozenInstanceError):
            result.post_ledger.free = 0.0  # type: ignore[misc]

    def test_module_imports_no_field_runner_or_dts1_code(self) -> None:
        import mcm_field_organism.kfs1_t1_transition as module

        tree = ast.parse(inspect.getsource(module))
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        forbidden = ("shared_mcm_field", "dynamic_substrate", "runner", "audio", "video", "browser")
        self.assertFalse(any(part in name for name in imported for part in forbidden))

    def test_no_runtime_side_effect_or_field_step_api_is_exposed(self) -> None:
        import mcm_field_organism.kfs1_t1_transition as module

        source = inspect.getsource(module)
        for forbidden in ("open(", "write_", "report", "requests", "SharedMCMField"):
            self.assertNotIn(forbidden, source)
        public = set(module.__all__)
        for forbidden in ("run", "field_step", "optimize", "fit", "score"):
            self.assertNotIn(forbidden, public)


if __name__ == "__main__":
    unittest.main()
