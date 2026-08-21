from __future__ import annotations

from pathlib import Path
import unittest

from mcm_field_organism.four_node_fresh_factory import (
    FourNodeFreshFactoryError,
    build_four_node_public_fresh_field,
)
from mcm_field_organism.four_node_fresh_manifest import load_four_node_fresh_manifest
from mcm_field_organism.mcm_substrate_state import mcm_substrate_edge_inventory


MANIFEST_PATH = (
    Path(__file__).resolve().parents[1]
    / "reports"
    / "s1rk_four_node_fresh_manifest.json"
)


class FourNodeFreshFactoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_four_node_fresh_manifest(MANIFEST_PATH)

    def test_public_field_has_registered_identifiers_and_node_order(self) -> None:
        field = build_four_node_public_fresh_field(self.manifest)
        self.assertEqual("mcm.s1rf.field.4n", field.field_id)
        self.assertEqual("mcm.s1rf.geometry.4n", field.geometry_id)
        self.assertEqual("mcm.s1rf.layer.4n", field.layer.layer_id)
        self.assertEqual(
            ("node-a", "node-b", "node-c", "node-d"),
            tuple(neuron.neuron_id for neuron in field.layer.neurons),
        )

    def test_public_field_is_the_exact_tick_zero_projection(self) -> None:
        field = build_four_node_public_fresh_field(self.manifest)
        for neuron in field.layer.neurons:
            self.assertEqual(0, neuron.tick)
            self.assertEqual(0.0, neuron.activation)
            self.assertEqual(0.0, neuron.afterimage)
            self.assertEqual(0.0, neuron.perception.receptor_contact)
            self.assertEqual((), neuron.perception.local_samples)
        self.assertIsNone(field.last_distribution)
        self.assertIsNone(field.substrate)
        self.assertIsNone(field.development)

    def test_public_field_has_registered_open_line_geometry(self) -> None:
        field = build_four_node_public_fresh_field(self.manifest)
        self.assertEqual(((-1,), (1,)), field.layer.sample_offsets)
        self.assertEqual((), field.layer.periodic_axes)
        self.assertEqual(
            (("node-a", "node-b"), ("node-b", "node-c"), ("node-c", "node-d")),
            mcm_substrate_edge_inventory(field.layer),
        )

    def test_public_field_has_one_lossless_registered_dock(self) -> None:
        field = build_four_node_public_fresh_field(self.manifest)
        self.assertEqual(1, len(field.docks))
        dock = field.docks[0]
        self.assertEqual("dock.s1rf.technical-control.4n", dock.dock_id)
        self.assertEqual("technical-control", dock.dock_map.modality_id)
        self.assertEqual(
            (
                ("carrier-a", "node-a"),
                ("carrier-b", "node-b"),
                ("carrier-c", "node-c"),
                ("carrier-d", "node-d"),
            ),
            dock.dock_map.pairs,
        )

    def test_repeated_builds_have_separate_object_graphs(self) -> None:
        first = build_four_node_public_fresh_field(self.manifest)
        second = build_four_node_public_fresh_field(self.manifest)
        self.assertIsNot(first, second)
        self.assertIsNot(first.layer, second.layer)
        self.assertIsNot(first.docks[0], second.docks[0])
        for left, right in zip(first.layer.neurons, second.layer.neurons, strict=True):
            self.assertIsNot(left, right)
            self.assertIsNot(left.perception, right.perception)

    def test_unvalidated_manifest_is_rejected(self) -> None:
        with self.assertRaisesRegex(FourNodeFreshFactoryError, "FRESH_FACTORY_PUBLIC_FIELD_INVALID"):
            build_four_node_public_fresh_field({})  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
