from __future__ import annotations

from dataclasses import replace
import ast
import math
from pathlib import Path
import unittest

import numpy as np

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.dynamic_substrate_dts1_backreaction import (
    DTS1BackreactionEdgeRate,
    DTS1BackreactionError,
    DTS1BackreactionResult,
    S1_HT_DECISION,
    build_dts1_diffusion_generator,
    build_dts1_s1ht_implementation_receipt,
    compute_dts1_edge_rates,
)
from mcm_field_organism.dynamic_substrate_s1hi_resource_anatomy import (
    DTS1EdgeResource,
    DTS1NodeCapacity,
    DTS1ResourceAnatomy,
    DTS1S1HIResourceAnatomyError,
)
from mcm_field_organism.mcm_substrate_state import (
    mcm_substrate_edge_inventory,
    mcm_substrate_edge_inventory_digest,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_e1_local_edge_plasticity import layer


class DTS1PureBackreactionTests(unittest.TestCase):
    def _anatomy(
        self,
        current=None,
        *,
        capacities: tuple[float, ...] = (1.0, 1.0, 1.0),
        resources: tuple[tuple[float, float], ...] = ((0.2, 0.1), (0.4, 0.2)),
        reverse: bool = False,
    ) -> DTS1ResourceAnatomy:
        current = layer() if current is None else current
        nodes = tuple(
            DTS1NodeCapacity(neuron.neuron_id, capacity)
            for neuron, capacity in zip(current.neurons, capacities, strict=True)
        )
        edge_ids = mcm_substrate_edge_inventory(current)
        edge_resources = tuple(
            DTS1EdgeResource(*edge, conductive, refractory)
            for edge, (conductive, refractory) in zip(
                edge_ids,
                resources,
                strict=True,
            )
        )
        if reverse:
            nodes = tuple(reversed(nodes))
            edge_resources = tuple(reversed(edge_resources))
        return DTS1ResourceAnatomy(nodes, edge_resources)

    def _rates(self, anatomy, *, enabled=True, response_time=0.5, current=None):
        current = layer() if current is None else current
        return compute_dts1_edge_rates(
            current,
            anatomy,
            NeutralLocalFieldSubstrateConfig(response_time),
            backreaction_enabled=enabled,
        )

    def test_t01_heterogeneous_capacity_active_formula(self) -> None:
        anatomy = self._anatomy(
            capacities=(0.5, 1.0, 2.0),
            resources=((0.4, 0.0), (0.6, 0.0)),
        )
        result = self._rates(anatomy, response_time=0.5)
        self.assertEqual(2.0, result.base_rate_per_second)
        self.assertEqual((2.8, 2.6), tuple(item.rate_per_second for item in result.edge_rates))

    def test_t02_ablation_returns_exact_base_rate_with_identical_anatomy(self) -> None:
        anatomy = self._anatomy()
        before = repr(anatomy)
        result = self._rates(anatomy, enabled=False, response_time=0.25)
        self.assertEqual((4.0, 4.0), tuple(item.rate_per_second for item in result.edge_rates))
        self.assertEqual(before, repr(anatomy))

    def test_t03_zero_conductive_binding_is_exactly_neutral(self) -> None:
        anatomy = self._anatomy(resources=((0.0, 0.5), (0.0, 0.25)))
        active = self._rates(anatomy, enabled=True)
        ablated = self._rates(anatomy, enabled=False)
        self.assertEqual(ablated.edge_rates, active.edge_rates)

    def test_t04_maximum_occupancy_attains_two_r0_without_exceeding_it(self) -> None:
        anatomy = self._anatomy(resources=((2.0, 0.0), (0.0, 0.0)))
        result = self._rates(anatomy)
        self.assertEqual(2.0, result.edge_rates[0].rate_per_second / result.base_rate_per_second)
        self.assertLessEqual(max(x.rate_per_second / result.base_rate_per_second for x in result.edge_rates), 2.0)

    def test_t05_same_b_different_refractory_has_identical_immediate_rates(self) -> None:
        first = self._anatomy(resources=((0.2, 0.0), (0.4, 0.0)))
        second = self._anatomy(resources=((0.2, 0.5), (0.4, 0.25)))
        self.assertEqual(self._rates(first).edge_rates, self._rates(second).edge_rates)

    def test_t06_complete_layer_anatomy_inventory_and_digest_are_required(self) -> None:
        current = layer()
        anatomy = self._anatomy(current)
        result = self._rates(anatomy, current=current)
        self.assertEqual(mcm_substrate_edge_inventory_digest(current), result.edge_inventory_digest)
        foreign_layer = layer((-1.0, 1.0))
        with self.assertRaises(DTS1BackreactionError):
            self._rates(anatomy, current=foreign_layer)

    def test_t07_invalid_inputs_and_rates_fail_closed(self) -> None:
        anatomy = self._anatomy()
        config = NeutralLocalFieldSubstrateConfig(1.0)
        with self.assertRaises(DTS1BackreactionError):
            compute_dts1_edge_rates(layer(), anatomy, config, backreaction_enabled=1)
        with self.assertRaises(DTS1BackreactionError):
            compute_dts1_edge_rates(layer(), anatomy, object(), backreaction_enabled=True)
        with self.assertRaises(DTS1BackreactionError):
            compute_dts1_edge_rates(layer(), object(), config, backreaction_enabled=True)
        with self.assertRaises(DTS1BackreactionError):
            DTS1BackreactionEdgeRate("neuron.0", "neuron.1", math.inf)
        with self.assertRaises(DTS1BackreactionError):
            DTS1BackreactionResult(
                True,
                1.0,
                (DTS1BackreactionEdgeRate("neuron.0", "neuron.1", 2.1),),
                "0" * 64,
            )
        with self.assertRaises(DTS1S1HIResourceAnatomyError):
            self._anatomy(resources=((2.1, 0.0), (0.0, 0.0)))

    def test_t08_input_declaration_order_does_not_change_ledger(self) -> None:
        self.assertEqual(self._rates(self._anatomy()), self._rates(self._anatomy(reverse=True)))

    def test_t09_all_adapter_inputs_remain_unchanged(self) -> None:
        current = layer()
        anatomy = self._anatomy(current)
        config = NeutralLocalFieldSubstrateConfig(0.5)
        before = (current.digest(), repr(anatomy), repr(config))
        compute_dts1_edge_rates(current, anatomy, config, backreaction_enabled=True)
        self.assertEqual(before, (current.digest(), repr(anatomy), repr(config)))

    def test_t10_generator_is_finite_square_float64_and_symmetric(self) -> None:
        current = layer()
        generator = build_dts1_diffusion_generator(current, self._rates(self._anatomy(current), current=current))
        self.assertEqual((3, 3), generator.shape)
        self.assertEqual(np.float64, generator.dtype)
        self.assertTrue(np.all(np.isfinite(generator)))
        np.testing.assert_array_equal(generator, generator.T)

    def test_t11_generator_has_zero_row_sum_and_constant_nullspace(self) -> None:
        current = layer()
        generator = build_dts1_diffusion_generator(current, self._rates(self._anatomy(current), current=current))
        np.testing.assert_allclose(generator.sum(axis=1), 0.0, rtol=0.0, atol=1e-15)
        np.testing.assert_allclose(generator @ np.ones(3), 0.0, rtol=0.0, atol=1e-15)

    def test_t12_generator_is_negative_semidefinite(self) -> None:
        current = layer()
        generator = build_dts1_diffusion_generator(current, self._rates(self._anatomy(current), current=current))
        self.assertLessEqual(float(np.max(np.linalg.eigvalsh(generator))), 1e-14)

    def test_t13_edge_flux_is_antisymmetric_and_sum_conserving(self) -> None:
        result = self._rates(self._anatomy())
        values = {"neuron.0": -0.5, "neuron.1": 0.25, "neuron.2": 0.75}
        balances = {node_id: 0.0 for node_id in values}
        for edge in result.edge_rates:
            flux = edge.rate_per_second * (values[edge.second_node_id] - values[edge.first_node_id])
            balances[edge.first_node_id] += flux
            balances[edge.second_node_id] -= flux
        self.assertTrue(any(value != 0.0 for value in balances.values()))
        self.assertEqual(0.0, math.fsum(balances.values()))

    def test_t14_invalid_rate_ledgers_fail_closed(self) -> None:
        current = layer()
        valid = self._rates(self._anatomy(current), current=current)
        incomplete = DTS1BackreactionResult(True, valid.base_rate_per_second, valid.edge_rates[:-1], valid.edge_inventory_digest)
        with self.assertRaises(DTS1BackreactionError):
            build_dts1_diffusion_generator(current, incomplete)
        with self.assertRaises(DTS1BackreactionError):
            DTS1BackreactionResult(True, valid.base_rate_per_second, (valid.edge_rates[0], valid.edge_rates[0]), valid.edge_inventory_digest)
        foreign = replace(valid, edge_inventory_digest="0" * 64)
        with self.assertRaises(DTS1BackreactionError):
            build_dts1_diffusion_generator(current, foreign)

    def test_t15_adapter_does_not_import_step_or_read_field_values(self) -> None:
        module_path = Path(__file__).parents[1] / "mcm_field_organism" / "dynamic_substrate_dts1_backreaction.py"
        tree = ast.parse(module_path.read_text(encoding="utf-8"))
        imported = {
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertFalse(any(name.endswith("dynamic_substrate_dts1_step") for name in imported))
        source = ast.get_source_segment(module_path.read_text(encoding="utf-8"), next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "compute_dts1_edge_rates"))
        self.assertNotIn("activation", source)
        self.assertNotIn("afterimage", source)

    def test_t16_module_has_no_runtime_snapshot_io_or_public_api_path(self) -> None:
        for name in ("compute_dts1_edge_rates", "build_dts1_diffusion_generator", "DTS1BackreactionResult"):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertFalse(hasattr(current_api, name))
        module_path = Path(__file__).parents[1] / "mcm_field_organism" / "dynamic_substrate_dts1_backreaction.py"
        source = module_path.read_text(encoding="utf-8")
        for forbidden in ("field_runner", "snapshot", "write_text(", "open(", "SharedMCMField"):
            self.assertNotIn(forbidden, source)

    def test_s1ht_receipt_is_deterministic_and_keeps_execution_closed(self) -> None:
        receipt = build_dts1_s1ht_implementation_receipt()
        self.assertEqual(receipt.receipt_digest, build_dts1_s1ht_implementation_receipt().receipt_digest)
        self.assertEqual(tuple(f"T{index:02d}" for index in range(1, 17)), receipt.matrix_case_ids)
        self.assertTrue(receipt.pure_adapter_implemented)
        self.assertTrue(receipt.pure_generator_implemented)
        self.assertFalse(receipt.runtime_integration_present)
        self.assertEqual(0, receipt.field_steps_executed)
        self.assertEqual(S1_HT_DECISION, receipt.decision)
        with self.assertRaises(DTS1BackreactionError):
            replace(receipt, resource_step_import_present=True)


if __name__ == "__main__":
    unittest.main()
