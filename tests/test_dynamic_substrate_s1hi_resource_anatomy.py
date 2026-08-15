from __future__ import annotations

from dataclasses import fields, replace
import inspect
import math
import unittest

from mcm_field_organism.dynamic_substrate_s1hi_resource_anatomy import (
    DTS1EdgeResource,
    DTS1NodeCapacity,
    DTS1ResourceAnatomy,
    DTS1S1HIResourceAnatomyError,
    S1_HI_DECISION,
    build_dts1_s1hi_anatomy_contract,
)


class DTS1S1HIResourceAnatomyTests(unittest.TestCase):
    def _anatomy(self) -> DTS1ResourceAnatomy:
        return DTS1ResourceAnatomy(
            node_capacities=(
                DTS1NodeCapacity("a", 1.0),
                DTS1NodeCapacity("b", 1.0),
                DTS1NodeCapacity("c", 1.0),
            ),
            edge_resources=(
                DTS1EdgeResource("a", "b", 0.5, 0.25),
                DTS1EdgeResource("b", "c", 0.25, 0.5),
            ),
        )

    def test_binds_three_roles_without_storing_free_resource(self) -> None:
        anatomy = self._anatomy()
        self.assertEqual(
            ("node_capacities", "edge_resources"),
            tuple(field.name for field in fields(DTS1ResourceAnatomy)),
        )
        self.assertEqual(2, len(anatomy.edge_resources))
        self.assertNotIn("free", tuple(field.name for field in fields(DTS1EdgeResource)))
        self.assertEqual(64, len(anatomy.edge_inventory_digest))

    def test_local_and_global_conservation_identities_are_derived(self) -> None:
        anatomy = self._anatomy()
        ledgers = {item.node_id: item for item in anatomy.local_ledgers()}
        self.assertEqual(0.625, ledgers["a"].free)
        self.assertEqual(0.25, ledgers["b"].free)
        self.assertEqual(0.625, ledgers["c"].free)
        self.assertTrue(all(item.residual == 0.0 for item in ledgers.values()))
        self.assertEqual(3.0, anatomy.global_capacity)
        self.assertEqual(3.0, anatomy.global_accounted_resource)
        self.assertEqual(0.0, anatomy.global_residual)

    def test_rejects_negative_nonfinite_and_overallocated_resources(self) -> None:
        with self.assertRaises(DTS1S1HIResourceAnatomyError):
            DTS1EdgeResource("a", "b", -0.1, 0.0)
        with self.assertRaises(DTS1S1HIResourceAnatomyError):
            DTS1EdgeResource("a", "b", 0.0, math.inf)
        with self.assertRaises(DTS1S1HIResourceAnatomyError):
            DTS1ResourceAnatomy(
                node_capacities=(
                    DTS1NodeCapacity("a", 0.25),
                    DTS1NodeCapacity("b", 1.0),
                ),
                edge_resources=(DTS1EdgeResource("a", "b", 0.6, 0.0),),
            )

    def test_rejects_invalid_or_incomplete_inventories_fail_closed(self) -> None:
        nodes = (DTS1NodeCapacity("a", 1.0), DTS1NodeCapacity("b", 1.0))
        with self.assertRaises(DTS1S1HIResourceAnatomyError):
            DTS1ResourceAnatomy(node_capacities=nodes, edge_resources=())
        with self.assertRaises(DTS1S1HIResourceAnatomyError):
            DTS1ResourceAnatomy(
                node_capacities=(
                    DTS1NodeCapacity("a", 1.0),
                    DTS1NodeCapacity("a", 1.0),
                ),
                edge_resources=(DTS1EdgeResource("a", "b", 0.0, 0.0),),
            )
        with self.assertRaises(DTS1S1HIResourceAnatomyError):
            DTS1ResourceAnatomy(
                node_capacities=nodes,
                edge_resources=(
                    DTS1EdgeResource("a", "b", 0.0, 0.0),
                    DTS1EdgeResource("a", "b", 0.0, 0.0),
                ),
            )
        with self.assertRaises(DTS1S1HIResourceAnatomyError):
            DTS1ResourceAnatomy(
                node_capacities=nodes,
                edge_resources=(DTS1EdgeResource("b", "c", 0.0, 0.0),),
            )
        with self.assertRaises(DTS1S1HIResourceAnatomyError):
            DTS1EdgeResource("b", "a", 0.0, 0.0)

    def test_contract_separates_anatomy_from_baselines_and_function(self) -> None:
        contract = build_dts1_s1hi_anatomy_contract()
        self.assertEqual(
            {"fixed-adapter", "gain", "fast-afterimage", "integrator", "replay"},
            {name for name, _ in contract.structural_distinctions},
        )
        self.assertFalse(contract.equation_selected)
        self.assertFalse(contract.parameters_selected)
        self.assertFalse(contract.runtime_implemented)
        self.assertFalse(contract.field_coupling_selected)
        self.assertFalse(contract.functional_effect_proven)
        self.assertFalse(contract.execution_permitted)
        self.assertEqual(0, contract.field_steps_executed)
        self.assertEqual(S1_HI_DECISION, contract.decision)

    def test_contract_is_deterministic_tamper_evident_and_static(self) -> None:
        first = build_dts1_s1hi_anatomy_contract()
        second = build_dts1_s1hi_anatomy_contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1HIResourceAnatomyError):
            replace(first, functional_effect_proven=True)
        source = inspect.getsource(build_dts1_s1hi_anatomy_contract)
        for forbidden in ("advance_", "field_runner", "open(", "write_text("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
