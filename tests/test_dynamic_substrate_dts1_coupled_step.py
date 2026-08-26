from __future__ import annotations

from dataclasses import replace
import ast
import inspect
import math
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.dynamic_substrate_dts1_backreaction import (
    compute_dts1_edge_rates,
)
from mcm_field_organism.dynamic_substrate_dts1_coupled_step import (
    DTS1CoupledStepError,
    S1_HW_DECISION,
    advance_dts1_coupled_fast_shared_field,
    build_dts1_s1hw_implementation_receipt,
)
from mcm_field_organism.dynamic_substrate_dts1_step import (
    DTS1StepError,
    DTS1StepRates,
    compute_dts1_closed_prestate_step,
)
from mcm_field_organism.dynamic_substrate_s1hi_resource_anatomy import (
    DTS1EdgeResource,
    DTS1NodeCapacity,
    DTS1ResourceAnatomy,
)
from mcm_field_organism.field_step_time import (
    MCMFieldStepTime,
    MCMFieldStepTimeError,
)
from mcm_field_organism.mcm_substrate_state import mcm_substrate_edge_inventory
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    advance_neutral_fast_shared_field,
)
from tests.test_neutral_fast_afterimage import (
    distribution,
    shared_field,
    step,
    values,
    with_fast_state,
)


class DTS1CoupledStepTests(unittest.TestCase):
    def setUp(self) -> None:
        self.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        self.afterimage = NeutralFastAfterimageConfig(0.5)
        self.rates = DTS1StepRates(0.4, 0.3, 0.2)

    def _field(self):
        return with_fast_state(
            shared_field(),
            (-0.8, 0.1, 0.7),
            (0.2, -0.1, 0.3),
        )

    def _anatomy(
        self,
        field,
        *,
        resources: tuple[tuple[float, float], ...] = ((0.2, 0.1), (0.4, 0.2)),
        capacities: tuple[float, ...] | None = None,
        reverse: bool = False,
    ) -> DTS1ResourceAnatomy:
        capacities = capacities or (1.0,) * len(field.layer.neurons)
        nodes = tuple(
            DTS1NodeCapacity(neuron.neuron_id, capacity)
            for neuron, capacity in zip(
                field.layer.neurons,
                capacities,
                strict=True,
            )
        )
        edges = tuple(
            DTS1EdgeResource(*edge, conductive, refractory)
            for edge, (conductive, refractory) in zip(
                mcm_substrate_edge_inventory(field.layer),
                resources,
                strict=True,
            )
        )
        if reverse:
            nodes = tuple(reversed(nodes))
            edges = tuple(reversed(edges))
        return DTS1ResourceAnatomy(nodes, edges)

    def _call(
        self,
        field,
        anatomy,
        *,
        start: int = 0,
        end: int = 10,
        contact: tuple[float, ...] = (0.9, -0.2, 0.4),
        enabled: bool = True,
        rates: DTS1StepRates | None = None,
        dissipation: NeutralFieldDissipationConfig | None = None,
    ):
        return advance_dts1_coupled_fast_shared_field(
            field,
            anatomy,
            distribution(start, end, f"contact.{start}.{end}", contact),
            step(start, end),
            self.substrate,
            self.afterimage,
            self.rates if rates is None else rates,
            dissipation,
            backreaction_enabled=enabled,
        )

    def test_t01_positive_step_time_required_and_zero_is_unrepresentable(self) -> None:
        with self.assertRaises(MCMFieldStepTimeError):
            MCMFieldStepTime("organism.test", 0, 0, 10.0)
        field = self._field()
        with self.assertRaises(DTS1CoupledStepError):
            advance_dts1_coupled_fast_shared_field(
                field,
                self._anatomy(field),
                distribution(0, 10, "contact", (0.0,) * 3),
                step(10, 20),
                self.substrate,
                self.afterimage,
                self.rates,
                backreaction_enabled=True,
            )

    def test_t02_complete_shared_geometry_and_digest_are_required(self) -> None:
        field = self._field()
        foreign = shared_field(4)
        with self.assertRaises(DTS1CoupledStepError):
            self._call(foreign, self._anatomy(field), contact=(0.0,) * 4)
        result = self._call(field, self._anatomy(field))
        self.assertEqual(
            tuple(item.edge for item in result.anatomy.edge_resources),
            result.applied_adapter.edges,
        )

    def test_t03_participation_is_complete_canonical_and_reads_only_s_n(self) -> None:
        field = self._field()
        result = self._call(field, self._anatomy(field))
        activation = {item.neuron_id: item.activation for item in field.layer.neurons}
        expected = tuple(
            ((activation[first] - activation[second]) / 2.0) ** 2
            for first, second in mcm_substrate_edge_inventory(field.layer)
        )
        self.assertEqual(
            mcm_substrate_edge_inventory(field.layer),
            tuple(item.edge for item in result.participations),
        )
        np.testing.assert_allclose(
            tuple(item.participation for item in result.participations),
            expected,
            rtol=0.0,
            atol=0.0,
        )

    def test_t04_resource_result_matches_direct_s1hp_prestate_call(self) -> None:
        field = self._field()
        anatomy = self._anatomy(field)
        result = self._call(field, anatomy)
        expected = compute_dts1_closed_prestate_step(
            anatomy,
            result.participations,
            result.elapsed_time,
            self.rates,
        )
        self.assertEqual(expected.next_anatomy, result.anatomy)
        self.assertEqual(expected.edge_transfers, result.resource_transfers)

    def test_t05_adapter_matches_direct_s1ht_prestate_reader(self) -> None:
        field = self._field()
        anatomy = self._anatomy(field)
        result = self._call(field, anatomy)
        expected = compute_dts1_edge_rates(
            field.layer,
            anatomy,
            self.substrate,
            backreaction_enabled=True,
        )
        self.assertEqual(expected, result.applied_adapter)

    def test_t06_a0_field_is_bit_exact_direct_neutral_output(self) -> None:
        field = self._field()
        anatomy = self._anatomy(field)
        world = distribution(0, 10, "contact", (0.9, -0.2, 0.4))
        interval = step(0, 10)
        p0 = advance_neutral_fast_shared_field(
            field,
            world,
            interval,
            self.substrate,
            self.afterimage,
        )
        a0 = advance_dts1_coupled_fast_shared_field(
            field,
            anatomy,
            world,
            interval,
            self.substrate,
            self.afterimage,
            self.rates,
            backreaction_enabled=False,
        )
        self.assertEqual(p0.snapshot().digest(), a0.field.snapshot().digest())
        self.assertFalse(a0.applied_adapter.backreaction_enabled)

    def test_t07_a0_and_a1_same_substep_resource_results_are_identical(self) -> None:
        field = self._field()
        anatomy = self._anatomy(field)
        a0 = self._call(field, anatomy, enabled=False)
        a1 = self._call(field, anatomy, enabled=True)
        self.assertEqual(a0.anatomy, a1.anatomy)
        self.assertEqual(a0.participations, a1.participations)
        self.assertEqual(a0.resource_transfers, a1.resource_transfers)

    def test_t08_a1_zero_prestate_binding_is_bit_exact_a0_and_p0(self) -> None:
        field = self._field()
        anatomy = self._anatomy(
            field,
            resources=((0.0, 0.2), (0.0, 0.3)),
        )
        world = distribution(0, 10, "contact", (0.9, -0.2, 0.4))
        interval = step(0, 10)
        p0 = advance_neutral_fast_shared_field(
            field, world, interval, self.substrate, self.afterimage
        )
        a0 = advance_dts1_coupled_fast_shared_field(
            field,
            anatomy,
            world,
            interval,
            self.substrate,
            self.afterimage,
            self.rates,
            backreaction_enabled=False,
        )
        a1 = advance_dts1_coupled_fast_shared_field(
            field,
            anatomy,
            world,
            interval,
            self.substrate,
            self.afterimage,
            self.rates,
            backreaction_enabled=True,
        )
        self.assertEqual(p0.snapshot().digest(), a0.field.snapshot().digest())
        self.assertEqual(a0.field.snapshot().digest(), a1.field.snapshot().digest())

    def test_t09_new_binding_cannot_affect_current_field_proposal(self) -> None:
        field = self._field()
        anatomy = self._anatomy(field, resources=((0.0, 0.0), (0.0, 0.0)))
        rates = DTS1StepRates(1.0, 0.0, 0.0)
        a0 = self._call(field, anatomy, enabled=False, rates=rates)
        a1 = self._call(field, anatomy, enabled=True, rates=rates)
        self.assertEqual(a0.field.snapshot().digest(), a1.field.snapshot().digest())
        self.assertTrue(
            any(item.conductive_bound > 0.0 for item in a1.anatomy.edge_resources)
        )

    def test_t10_new_field_values_cannot_affect_current_resource_proposal(self) -> None:
        field = self._field()
        anatomy = self._anatomy(field, resources=((0.8, 0.0), (0.6, 0.0)))
        a0 = self._call(field, anatomy, enabled=False)
        a1 = self._call(field, anatomy, enabled=True)
        self.assertNotEqual(a0.field.snapshot().digest(), a1.field.snapshot().digest())
        self.assertEqual(a0.anatomy, a1.anatomy)
        self.assertEqual(a0.resource_transfers, a1.resource_transfers)

    def test_t11_active_nonzero_binding_uses_generator_and_neutral_boundary(self) -> None:
        field = self._field()
        anatomy = self._anatomy(field, resources=((0.8, 0.0), (0.6, 0.0)))
        with patch(
            "mcm_field_organism.dynamic_substrate_dts1_coupled_step."
            "build_dts1_diffusion_generator",
            wraps=__import__(
                "mcm_field_organism.dynamic_substrate_dts1_coupled_step",
                fromlist=["build_dts1_diffusion_generator"],
            ).build_dts1_diffusion_generator,
        ) as generator, patch(
            "mcm_field_organism.dynamic_substrate_dts1_coupled_step."
            "_generator_and_boundary",
            wraps=__import__(
                "mcm_field_organism.dynamic_substrate_dts1_coupled_step",
                fromlist=["_generator_and_boundary"],
            )._generator_and_boundary,
        ) as boundary, patch(
            "mcm_field_organism.dynamic_substrate_dts1_coupled_step."
            "_diffusion_generator",
            wraps=__import__(
                "mcm_field_organism.dynamic_substrate_dts1_coupled_step",
                fromlist=["_diffusion_generator"],
            )._diffusion_generator,
        ) as neutral_internal:
            result = self._call(field, anatomy, enabled=True)
        generator.assert_called_once()
        boundary.assert_called_once()
        neutral_internal.assert_called_once()
        self.assertTrue(
            any(
                item.rate_per_second > result.applied_adapter.base_rate_per_second
                for item in result.applied_adapter.edge_rates
            )
        )
        uniform = with_fast_state(shared_field(), (0.0,) * 3, (0.0,) * 3)
        uniform_result = self._call(
            uniform,
            self._anatomy(
                uniform,
                resources=((0.8, 0.0), (0.6, 0.0)),
            ),
            enabled=True,
            contact=(0.5,) * 3,
        )
        np.testing.assert_allclose(
            values(uniform_result.field, "activation"),
            0.5 * (1.0 - math.exp(-1.0)),
            rtol=0.0,
            atol=2e-15,
        )

    def test_t12_afterimage_dissipation_domain_and_time_semantics_unchanged(self) -> None:
        field = self._field()
        anatomy = self._anatomy(field)
        leak = NeutralFieldDissipationConfig(0.25)
        world = distribution(0, 10, "contact", (0.9, -0.2, 0.4))
        interval = step(0, 10)
        p0 = advance_neutral_fast_shared_field(
            field, world, interval, self.substrate, self.afterimage, leak
        )
        a0 = advance_dts1_coupled_fast_shared_field(
            field,
            anatomy,
            world,
            interval,
            self.substrate,
            self.afterimage,
            self.rates,
            leak,
            backreaction_enabled=False,
        )
        self.assertEqual(1.0, a0.elapsed_time)
        self.assertEqual(p0.snapshot().digest(), a0.field.snapshot().digest())
        for role in ("activation", "afterimage"):
            self.assertTrue(np.all(np.abs(values(a0.field, role)) <= 1.0))

    def test_t13_inputs_immutable_and_repeat_deterministic(self) -> None:
        field = self._field()
        anatomy = self._anatomy(field)
        before = (repr(field), repr(anatomy), repr(self.rates))
        first = self._call(field, anatomy)
        second = self._call(field, anatomy)
        self.assertEqual(first, second)
        self.assertEqual(before, (repr(field), repr(anatomy), repr(self.rates)))

    def test_t14_resource_failure_yields_no_field_or_pair_output(self) -> None:
        field = self._field()
        anatomy = self._anatomy(field)
        with patch(
            "mcm_field_organism.dynamic_substrate_dts1_coupled_step."
            "compute_dts1_closed_prestate_step",
            side_effect=DTS1StepError("forced resource failure"),
        ), patch(
            "mcm_field_organism.dynamic_substrate_dts1_coupled_step."
            "advance_neutral_fast_shared_field"
        ) as neutral, patch(
            "mcm_field_organism.dynamic_substrate_dts1_coupled_step."
            "_advance_active_field"
        ) as active:
            with self.assertRaisesRegex(DTS1CoupledStepError, "forced resource"):
                self._call(field, anatomy)
        neutral.assert_not_called()
        active.assert_not_called()

    def test_t15_field_failure_yields_no_anatomy_or_pair_output(self) -> None:
        field = self._field()
        anatomy = self._anatomy(field)
        before = repr(anatomy)
        with patch(
            "mcm_field_organism.dynamic_substrate_dts1_coupled_step."
            "advance_neutral_fast_shared_field",
            side_effect=NeutralLocalFieldSubstrateError("forced field failure"),
        ):
            with self.assertRaisesRegex(DTS1CoupledStepError, "forced field"):
                self._call(field, anatomy, enabled=False)
        self.assertEqual(before, repr(anatomy))

    def test_t16_invalid_types_controls_time_configs_and_geometry_fail_closed(self) -> None:
        field = self._field()
        anatomy = self._anatomy(field)
        valid = (
            field,
            anatomy,
            distribution(0, 10, "contact", (0.0,) * 3),
            step(0, 10),
            self.substrate,
            self.afterimage,
            self.rates,
        )
        for index in range(7):
            args = list(valid)
            args[index] = object()
            with self.subTest(index=index), self.assertRaises(DTS1CoupledStepError):
                advance_dts1_coupled_fast_shared_field(
                    *args,
                    backreaction_enabled=True,
                )
        with self.assertRaisesRegex(DTS1CoupledStepError, "boolean"):
            advance_dts1_coupled_fast_shared_field(
                *valid,
                backreaction_enabled=1,
            )

    def test_t17_declaration_order_does_not_change_value_output(self) -> None:
        field = self._field()
        first = self._call(field, self._anatomy(field))
        second = self._call(field, self._anatomy(field, reverse=True))
        self.assertEqual(first, second)

    def test_t18_pair_residual_and_reader_latency_are_measurable(self) -> None:
        def run(partitions: int):
            field = self._field()
            anatomy = self._anatomy(field)
            duration = 20 // partitions
            for index in range(partitions):
                result = self._call(
                    field,
                    anatomy,
                    start=index * duration,
                    end=(index + 1) * duration,
                )
                field, anatomy = result.field, result.anatomy
            state = np.concatenate(
                (
                    values(field, "activation"),
                    values(field, "afterimage"),
                    np.asarray(
                        [
                            value
                            for edge in anatomy.edge_resources
                            for value in (edge.conductive_bound, edge.refractory)
                        ]
                    ),
                )
            )
            return state, result.elapsed_time

        one, dt_one = run(1)
        two, dt_two = run(2)
        four, dt_four = run(4)
        residuals = (
            float(np.max(np.abs(one - two))),
            float(np.max(np.abs(two - four))),
        )
        self.assertTrue(all(math.isfinite(value) and value >= 0.0 for value in residuals))
        self.assertGreater(dt_one, dt_two)
        self.assertGreater(dt_two, dt_four)

    def test_t19_no_midpoint_implicit_adaptive_or_partial_commit_path(self) -> None:
        source = inspect.getsource(advance_dts1_coupled_fast_shared_field)
        for forbidden in ("midpoint", "while ", "solve", "adaptive", "callback"):
            self.assertNotIn(forbidden, source)
        self.assertLess(source.index("resource_result ="), source.index("next_field ="))
        self.assertLess(source.index("next_field ="), source.index("return DTS1Coupled"))

    def test_t20_no_runtime_io_snapshot_public_api_values_or_research_run(self) -> None:
        for role in (
            "DTS1CoupledFastFieldStepResult",
            "advance_dts1_coupled_fast_shared_field",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))
        module_path = (
            Path(__file__).parents[1]
            / "mcm_field_organism"
            / "dynamic_substrate_dts1_coupled_step.py"
        )
        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertFalse(any("runtime" in name for name in imported))
        for forbidden in ("write_text(", "write_bytes(", "open(", "snapshot("):
            self.assertNotIn(forbidden, source)

    def test_s1hw_receipt_is_deterministic_and_keeps_research_closed(self) -> None:
        receipt = build_dts1_s1hw_implementation_receipt()
        self.assertEqual(
            receipt.receipt_digest,
            build_dts1_s1hw_implementation_receipt().receipt_digest,
        )
        self.assertEqual(tuple(f"T{index:02d}" for index in range(1, 21)), receipt.matrix_case_ids)
        self.assertTrue(receipt.private_coupled_step_implemented)
        self.assertTrue(receipt.technical_matrix_execution_only)
        self.assertFalse(receipt.runtime_integration_present)
        self.assertFalse(receipt.research_execution_permitted)
        self.assertEqual(0, receipt.research_field_steps_executed)
        self.assertEqual(S1_HW_DECISION, receipt.decision)


if __name__ == "__main__":
    unittest.main()
