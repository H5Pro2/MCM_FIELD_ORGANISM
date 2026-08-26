from __future__ import annotations

import ast
import inspect
import unittest

from mcm_field_organism.kfs1_s1ni_sequence_comparison import (
    S1_NI_DECISION_SWITCHED,
    S1_NI_EVENTS,
    S1_NI_T1_EXPECTED,
    run_kfs1_s1ni_sequence_comparison,
)


class KFS1S1NISequenceComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_kfs1_s1ni_sequence_comparison()

    def test_bound_event_sequence_and_t1_predictions_are_exact(self) -> None:
        self.assertEqual((1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0), tuple(x[3] for x in S1_NI_EVENTS))
        observed = tuple(
            (boundary.ledger, boundary.transfers)
            for boundary in self.result.t1_arm.boundaries
        )
        self.assertEqual(S1_NI_T1_EXPECTED, observed)

    def test_closed_arm_inventory_and_call_budget(self) -> None:
        self.assertEqual(
            (
                "DTS1_REGISTERED:r1",
                "DTS1_REGISTERED:r2",
                "DTS1_REGISTERED:r4",
                "DTS1_REGISTERED:r8",
                "DTS1_STATIC_ZERO:r1",
            ),
            tuple(arm.arm_id for arm in self.result.dts1_arms),
        )
        self.assertEqual(7, self.result.t1_transition_calls)
        self.assertEqual(112, self.result.dts1_substep_calls)
        self.assertEqual(0, self.result.field_steps_executed)

    def test_all_ledgers_remain_conserved(self) -> None:
        arms = (self.result.t1_arm,) + self.result.dts1_arms
        for arm in arms:
            for boundary in arm.boundaries:
                self.assertAlmostEqual(1.0, sum(boundary.ledger), places=13)
                self.assertLessEqual(boundary.maximum_local_ledger_residual, 1.1368683772161603e-13)
                self.assertLessEqual(boundary.global_ledger_residual, 1.1368683772161603e-13)

    def test_static_zero_is_identity_and_not_t1_equivalent(self) -> None:
        arm = self.result.dts1_arms[-1]
        for boundary in arm.boundaries:
            self.assertEqual((1.0, 0.0, 0.0), boundary.ledger)
            self.assertEqual((0.0, 0.0, 0.0), boundary.transfers)
        self.assertNotIn(arm.arm_id, self.result.equivalent_arm_ids)

    def test_registered_dts1_profiles_do_not_reproduce_t1(self) -> None:
        self.assertEqual((), self.result.equivalent_arm_ids)
        for arm in self.result.dts1_arms[:4]:
            self.assertNotEqual(
                self.result.t1_arm.boundaries[0].ledger,
                arm.boundaries[0].ledger,
            )

    def test_t1_is_exactly_a_switched_dts1_role_map_on_this_sequence(self) -> None:
        self.assertTrue(self.result.switched_dts1_variant_exact)
        self.assertEqual(S1_NI_DECISION_SWITCHED, self.result.decision)

    def test_all_records_have_canonical_state_digests(self) -> None:
        arms = (self.result.t1_arm,) + self.result.dts1_arms
        for arm in arms:
            self.assertEqual(7, len(arm.boundaries))
            self.assertTrue(all(len(item.state_digest) == 64 for item in arm.boundaries))
        self.assertEqual(64, len(self.result.result_digest))

    def test_module_has_no_field_runner_runtime_or_io_dependency(self) -> None:
        import mcm_field_organism.kfs1_s1ni_sequence_comparison as module

        tree = ast.parse(inspect.getsource(module))
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        forbidden = ("shared_mcm_field", "runner", "audio", "video", "browser")
        self.assertFalse(any(part in name for name in imported for part in forbidden))
        source = inspect.getsource(module)
        for forbidden_call in ("open(", "write_", "SharedMCMField", "advance_field"):
            self.assertNotIn(forbidden_call, source)


if __name__ == "__main__":
    unittest.main()
