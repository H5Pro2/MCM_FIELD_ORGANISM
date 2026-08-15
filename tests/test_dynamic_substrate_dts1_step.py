from __future__ import annotations

from dataclasses import replace
import ast
import math
from pathlib import Path
import unittest

from mcm_field_organism.dynamic_substrate_dts1_step import (
    DTS1EdgeParticipation,
    DTS1S1HPImplementationReceipt,
    DTS1StepResult,
    DTS1StepError,
    DTS1StepRates,
    S1_HP_DECISION,
    build_dts1_s1hp_implementation_receipt,
    compute_dts1_closed_prestate_step,
)
from mcm_field_organism.dynamic_substrate_s1hi_resource_anatomy import (
    DTS1EdgeResource,
    DTS1NodeCapacity,
    DTS1ResourceAnatomy,
    DTS1S1HIResourceAnatomyError,
)


class DTS1PureStepTests(unittest.TestCase):
    def _anatomy(
        self,
        edges: tuple[tuple[str, str, float, float], ...] = (
            ("a", "b", 0.2, 0.1),
        ),
        capacities: tuple[tuple[str, float], ...] = (("a", 1.0), ("b", 1.0)),
    ) -> DTS1ResourceAnatomy:
        return DTS1ResourceAnatomy(
            node_capacities=tuple(DTS1NodeCapacity(*item) for item in capacities),
            edge_resources=tuple(DTS1EdgeResource(*item) for item in edges),
        )

    def _participations(
        self,
        anatomy: DTS1ResourceAnatomy,
        value: float = 1.0,
    ) -> tuple[DTS1EdgeParticipation, ...]:
        return tuple(DTS1EdgeParticipation(*edge.edge, value) for edge in anatomy.edge_resources)

    def _step(
        self,
        anatomy: DTS1ResourceAnatomy,
        rates: DTS1StepRates,
        elapsed: float = 0.25,
        participation: float = 1.0,
    ):
        return compute_dts1_closed_prestate_step(
            anatomy,
            self._participations(anatomy, participation),
            elapsed,
            rates,
        )

    def test_t01_zero_interval_is_exact_identity_with_zero_transfers(self) -> None:
        anatomy = self._anatomy()
        result = self._step(anatomy, DTS1StepRates(0.7, 0.4, 0.2), elapsed=0.0)
        self.assertEqual(anatomy, result.next_anatomy)
        self.assertEqual(result.input_anatomy_digest, result.output_anatomy_digest)
        for transfer in result.edge_transfers:
            self.assertEqual((0.0, 0.0, 0.0), (transfer.engagement, transfer.turnover, transfer.recovery))

    def test_t02_zero_rates_are_exact_identity(self) -> None:
        anatomy = self._anatomy()
        result = self._step(anatomy, DTS1StepRates(0.0, 0.0, 0.0), elapsed=4.0)
        self.assertEqual(anatomy, result.next_anatomy)

    def test_t03_zero_participation_blocks_only_engagement(self) -> None:
        anatomy = self._anatomy()
        result = self._step(anatomy, DTS1StepRates(1.0, 0.5, 0.25), participation=0.0)
        transfer = result.edge_transfers[0]
        self.assertEqual(0.0, transfer.engagement)
        self.assertGreater(transfer.turnover, 0.0)
        self.assertGreater(transfer.recovery, 0.0)

    def test_t04_zero_free_endpoint_blocks_engagement(self) -> None:
        anatomy = self._anatomy(edges=(("a", "b", 1.0, 1.0),))
        result = self._step(anatomy, DTS1StepRates(1.0, 0.0, 0.0))
        self.assertEqual(0.0, result.edge_transfers[0].engagement)

    def test_t05_single_edge_binding_matches_interval_fraction(self) -> None:
        anatomy = self._anatomy(edges=(("a", "b", 0.0, 0.0),))
        elapsed = 0.3
        rate = 0.7
        result = self._step(anatomy, DTS1StepRates(rate, 0.0, 0.0), elapsed)
        expected = -math.expm1(-rate * elapsed) * 2.0
        self.assertAlmostEqual(expected, result.edge_transfers[0].engagement)

    def test_t06_single_edge_turnover_matches_interval_fraction(self) -> None:
        anatomy = self._anatomy(edges=(("a", "b", 0.6, 0.0),))
        elapsed = 0.4
        rate = 0.8
        result = self._step(anatomy, DTS1StepRates(0.0, rate, 0.0), elapsed)
        self.assertAlmostEqual(
            -math.expm1(-rate * elapsed) * 0.6,
            result.edge_transfers[0].turnover,
        )

    def test_t07_single_edge_recovery_matches_interval_fraction(self) -> None:
        anatomy = self._anatomy(edges=(("a", "b", 0.0, 0.6),))
        elapsed = 0.4
        rate = 0.8
        result = self._step(anatomy, DTS1StepRates(0.0, 0.0, rate), elapsed)
        self.assertAlmostEqual(
            -math.expm1(-rate * elapsed) * 0.6,
            result.edge_transfers[0].recovery,
        )

    def test_t08_shared_node_competition_is_simultaneous_without_overdraw(self) -> None:
        anatomy = self._anatomy(
            edges=(("a", "b", 0.0, 0.0), ("a", "c", 0.0, 0.0)),
            capacities=(("a", 1.0), ("b", 1.0), ("c", 1.0)),
        )
        result = self._step(anatomy, DTS1StepRates(100.0, 0.0, 0.0), elapsed=1.0)
        self.assertAlmostEqual(1.0, 0.5 * math.fsum(x.engagement for x in result.edge_transfers))
        self.assertGreaterEqual(result.next_anatomy.local_ledgers()[0].free, 0.0)

    def test_t09_edge_order_does_not_change_result_or_digest(self) -> None:
        edges = (("a", "b", 0.1, 0.2), ("a", "c", 0.2, 0.1))
        anatomy = self._anatomy(edges=edges, capacities=(("a", 1.0), ("b", 1.0), ("c", 1.0)))
        participations = self._participations(anatomy)
        rates = DTS1StepRates(0.4, 0.3, 0.2)
        first = compute_dts1_closed_prestate_step(anatomy, participations, 0.5, rates)
        second = compute_dts1_closed_prestate_step(anatomy, tuple(reversed(participations)), 0.5, rates)
        self.assertEqual(first, second)

    def test_t10_local_and_global_resource_identities_remain_bounded(self) -> None:
        anatomy = self._anatomy()
        result = self._step(anatomy, DTS1StepRates(0.7, 0.4, 0.2))
        self.assertLessEqual(result.maximum_local_ledger_residual, 1e-15)
        self.assertLessEqual(result.global_ledger_residual, 1e-15)
        self.assertAlmostEqual(
            result.next_anatomy.global_capacity,
            result.next_anatomy.global_accounted_resource,
        )

    def test_t11_new_resources_are_not_reused_in_same_step(self) -> None:
        anatomy = self._anatomy(edges=(("a", "b", 0.0, 0.0),))
        result = self._step(anatomy, DTS1StepRates(1.0, 1.0, 1.0))
        transfer = result.edge_transfers[0]
        self.assertGreater(transfer.engagement, 0.0)
        self.assertEqual(0.0, transfer.turnover)
        self.assertEqual(0.0, transfer.recovery)
        self.assertEqual(0.0, result.next_anatomy.edge_resources[0].refractory)

    def test_t12_inputs_are_immutable_and_repeated_call_is_deterministic(self) -> None:
        anatomy = self._anatomy()
        participations = self._participations(anatomy, 0.75)
        before = (repr(anatomy), repr(participations))
        rates = DTS1StepRates(0.4, 0.3, 0.2)
        first = compute_dts1_closed_prestate_step(anatomy, participations, 0.5, rates)
        second = compute_dts1_closed_prestate_step(anatomy, participations, 0.5, rates)
        self.assertEqual(first, second)
        self.assertEqual(before, (repr(anatomy), repr(participations)))

    def test_t13_invalid_scalars_and_participations_fail_closed(self) -> None:
        for invalid in (True, -0.1, math.nan, math.inf, "value"):
            with self.assertRaises(DTS1StepError):
                DTS1StepRates(invalid, 0.0, 0.0)
            with self.assertRaises(DTS1StepError):
                DTS1EdgeParticipation("a", "b", invalid)
        anatomy = self._anatomy()
        with self.assertRaises(DTS1StepError):
            self._step(anatomy, DTS1StepRates(0.0, 0.0, 0.0), elapsed=True)
        with self.assertRaises(DTS1StepError):
            DTS1EdgeParticipation("a", "b", 1.1)
        with self.assertRaises(DTS1StepError):
            compute_dts1_closed_prestate_step(
                anatomy,
                None,
                0.1,
                DTS1StepRates(0.0, 0.0, 0.0),
            )

    def test_t14_invalid_edge_ledgers_fail_closed(self) -> None:
        anatomy = self._anatomy()
        rates = DTS1StepRates(0.0, 0.0, 0.0)
        participation = DTS1EdgeParticipation("a", "b", 1.0)
        for ledger in ((), (participation, participation), (DTS1EdgeParticipation("a", "c", 1.0),)):
            with self.assertRaises(DTS1StepError):
                compute_dts1_closed_prestate_step(anatomy, ledger, 0.1, rates)
        with self.assertRaises(DTS1StepError):
            DTS1EdgeParticipation("b", "a", 1.0)

    def test_t15_invalid_anatomy_fails_before_calculation(self) -> None:
        with self.assertRaises(DTS1S1HIResourceAnatomyError):
            self._anatomy(edges=(("a", "b", 2.1, 0.0),))
        with self.assertRaises(DTS1StepError):
            compute_dts1_closed_prestate_step(
                object(),
                (DTS1EdgeParticipation("a", "b", 1.0),),
                0.1,
                DTS1StepRates(0.1, 0.1, 0.1),
            )

    def test_t16_step_refinement_converges_for_mixed_cycle(self) -> None:
        anatomy = self._anatomy(edges=(("a", "b", 0.2, 0.3),))
        rates = DTS1StepRates(0.4, 0.7, 0.5)

        def evolved(steps: int) -> DTS1ResourceAnatomy:
            state = anatomy
            for _ in range(steps):
                state = self._step(state, rates, elapsed=1.0 / steps).next_anatomy
            return state

        reference = evolved(256).edge_resources[0]
        errors = []
        for steps in (1, 2, 4):
            edge = evolved(steps).edge_resources[0]
            errors.append(abs(edge.conductive_bound - reference.conductive_bound) + abs(edge.refractory - reference.refractory))
        self.assertGreater(errors[0], errors[1])
        self.assertGreater(errors[1], errors[2])

    def test_t17_module_is_private_and_has_no_field_runtime_or_io_import(self) -> None:
        module_path = Path(__file__).parents[1] / "mcm_field_organism" / "dynamic_substrate_dts1_step.py"
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        )
        for forbidden in ("mcm_neuron_layer", "runtime", "pathlib", "os", "random", "subprocess"):
            self.assertFalse(any(forbidden in name for name in imported))
        import mcm_field_organism
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(mcm_field_organism, "compute_dts1_closed_prestate_step"))
        self.assertFalse(hasattr(current_api, "compute_dts1_closed_prestate_step"))

    def test_s1hp_receipt_is_tamper_evident_and_keeps_execution_closed(self) -> None:
        receipt = build_dts1_s1hp_implementation_receipt()
        self.assertEqual(receipt.receipt_digest, build_dts1_s1hp_implementation_receipt().receipt_digest)
        self.assertEqual(tuple(f"T{index:02d}" for index in range(1, 18)), receipt.matrix_case_ids)
        self.assertTrue(receipt.pure_step_implemented)
        self.assertFalse(receipt.research_execution_permitted)
        self.assertEqual(0, receipt.field_steps_executed)
        self.assertEqual(S1_HP_DECISION, receipt.decision)
        with self.assertRaises(DTS1StepError):
            replace(receipt, field_import_present=True)
        self.assertIsInstance(receipt, DTS1S1HPImplementationReceipt)

    def test_result_rejects_a_digest_not_matching_its_anatomy(self) -> None:
        anatomy = self._anatomy()
        result = self._step(anatomy, DTS1StepRates(0.1, 0.2, 0.3))
        with self.assertRaises(DTS1StepError):
            DTS1StepResult(
                next_anatomy=result.next_anatomy,
                edge_transfers=result.edge_transfers,
                input_anatomy_digest=result.input_anatomy_digest,
                output_anatomy_digest="0" * 64,
                maximum_local_ledger_residual=result.maximum_local_ledger_residual,
                global_ledger_residual=result.global_ledger_residual,
            )


if __name__ == "__main__":
    unittest.main()
