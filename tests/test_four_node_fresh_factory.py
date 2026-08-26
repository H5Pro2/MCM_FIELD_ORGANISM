from __future__ import annotations

from pathlib import Path
import unittest

from mcm_field_organism.four_node_fresh_factory import (
    FourNodeFixedAdapterState,
    FourNodeFreshFactoryError,
    FourNodeIntegratorState,
    FourNodeM4FreshState,
    FourNodeSubstrateFreshState,
    build_four_node_public_fresh_field,
    build_four_node_role_fresh_bundle,
)
from mcm_field_organism.four_node_fresh_manifest import load_four_node_fresh_manifest
from mcm_field_organism.m1_parallel_leak_replace_s_compositor import M1ParallelLeakBankState
from mcm_field_organism.m2_bounded_buffer_replace_s_compositor import M2BoundedBufferState
from mcm_field_organism.mcm_substrate_state import mcm_substrate_edge_inventory
from mcm_field_organism.w7n_capacity_function_baselines import W7NLocalBaselineState


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

    def test_all_fourteen_roles_build_in_registered_order(self) -> None:
        expected = (
            "A0_CURRENT_CONTACT", "A1_FAST_SH", "A2_B1_FIXED_ADAPTER",
            "A2_B2_INTEGRATOR", "A2_B3_LOCAL_LEAKY", "A2_B4_LINEAR_COUPLED",
            "A2_B5_F3_FULL", "A2_B6_CONST_V", "A3_NORM", "M1_PARALLEL_LEAK",
            "M2_DELAY", "M2_REPLAY", "M4_DTS1_T1", "M5_DIRECT",
        )
        bundles = tuple(build_four_node_role_fresh_bundle(self.manifest, role) for role in expected)
        self.assertEqual(expected, tuple(item.model_role for item in bundles))

    def test_a0_and_a1_remain_strictly_stateless(self) -> None:
        expected = {
            "A0_CURRENT_CONTACT": "STATELESS_MARKER:A0_CURRENT_CONTACT:S1RJ",
            "A1_FAST_SH": "FIELD_ONLY:A1_FAST_SH:S1RJ",
        }
        for role, marker in expected.items():
            with self.subTest(role=role):
                bundle = build_four_node_role_fresh_bundle(self.manifest, role)
                self.assertIsNone(bundle.private_state_or_none)
                self.assertIsNone(bundle.registered_private_digest_or_none)
                self.assertEqual(marker, bundle.stateless_marker_or_none)

    def test_b1_and_b2_use_exact_local_value_states(self) -> None:
        b1 = build_four_node_role_fresh_bundle(self.manifest, "A2_B1_FIXED_ADAPTER")
        b2 = build_four_node_role_fresh_bundle(self.manifest, "A2_B2_INTEGRATOR")
        self.assertIsInstance(b1.private_state_or_none.native_state, FourNodeFixedAdapterState)
        self.assertEqual((1.1, 1.1, 1.1), tuple(
            item.rate_per_second for item in b1.private_state_or_none.native_state.edge_rates
        ))
        self.assertIsInstance(b2.private_state_or_none.native_state, FourNodeIntegratorState)
        self.assertEqual((0.0, 0.0, 0.0, 0.0), tuple(
            item.value for item in b2.private_state_or_none.native_state.entries
        ))

    def test_b3_through_b6_use_native_substrate_with_explicit_edge_bridge(self) -> None:
        roles = (
            "A2_B3_LOCAL_LEAKY", "A2_B4_LINEAR_COUPLED",
            "A2_B5_F3_FULL", "A2_B6_CONST_V",
        )
        for role in roles:
            with self.subTest(role=role):
                bundle = build_four_node_role_fresh_bundle(self.manifest, role)
                private = bundle.private_state_or_none
                self.assertIsInstance(private.native_state, FourNodeSubstrateFreshState)
                self.assertEqual(1.0, private.native_state.substrate.total_mass)
                self.assertNotEqual(
                    private.registered_edge_inventory_digest_or_none,
                    private.native_edge_inventory_digest_or_none,
                )

    def test_a3_and_m5_use_separate_registered_w7_zero_states(self) -> None:
        a3 = build_four_node_role_fresh_bundle(self.manifest, "A3_NORM")
        m5 = build_four_node_role_fresh_bundle(self.manifest, "M5_DIRECT")
        self.assertIsInstance(a3.private_state_or_none.native_state, W7NLocalBaselineState)
        self.assertIsInstance(m5.private_state_or_none.native_state, W7NLocalBaselineState)
        self.assertEqual(("norm", "leak"), (
            a3.private_state_or_none.native_state.model_id,
            m5.private_state_or_none.native_state.model_id,
        ))
        self.assertIsNot(a3.private_state_or_none.native_state, m5.private_state_or_none.native_state)

    def test_m1_uses_two_distinct_registered_zero_traces(self) -> None:
        bundle = build_four_node_role_fresh_bundle(self.manifest, "M1_PARALLEL_LEAK")
        state = bundle.private_state_or_none.native_state
        self.assertIsInstance(state, M1ParallelLeakBankState)
        self.assertIsNot(state.fast_state, state.slow_state)
        self.assertEqual((0.0,) * 4, state.fast_state.latent)
        self.assertEqual((0.0,) * 4, state.slow_state.latent)

    def test_m2_modes_use_separate_native_geometry_bridge_states(self) -> None:
        for role, mode, phase in (
            ("M2_DELAY", "DELAY", "NOT_APPLICABLE"),
            ("M2_REPLAY", "REPLAY", "CAPTURE"),
        ):
            with self.subTest(role=role):
                bundle = build_four_node_role_fresh_bundle(self.manifest, role)
                private = bundle.private_state_or_none
                self.assertIsInstance(private.native_state, M2BoundedBufferState)
                self.assertEqual((mode, phase, (), 0), (
                    private.native_state.mode_id, private.native_state.replay_phase,
                    private.native_state.records, private.native_state.replay_cursor,
                ))
                self.assertNotEqual(
                    private.registered_geometry_digest_or_none,
                    private.native_geometry_digest_or_none,
                )

    def test_m4_anatomy_closes_local_and_global_resource_ledgers(self) -> None:
        bundle = build_four_node_role_fresh_bundle(self.manifest, "M4_DTS1_T1")
        state = bundle.private_state_or_none.native_state
        self.assertIsInstance(state, FourNodeM4FreshState)
        self.assertEqual((0.85, 0.7, 0.7, 0.85), tuple(
            item.free for item in state.anatomy.local_ledgers()
        ))
        self.assertEqual(4.0, state.anatomy.global_capacity)
        self.assertAlmostEqual(0.0, state.anatomy.global_residual)
        self.assertIsNone(state.candidate_sidecar_digest_or_none)

    def test_unknown_role_fails_closed(self) -> None:
        with self.assertRaisesRegex(FourNodeFreshFactoryError, "FRESH_FACTORY_MODEL_ROLE_INVALID"):
            build_four_node_role_fresh_bundle(self.manifest, "UNKNOWN")

    def test_repeated_role_builds_have_separate_public_and_private_objects(self) -> None:
        for role in (
            "A2_B1_FIXED_ADAPTER", "A2_B2_INTEGRATOR", "A2_B3_LOCAL_LEAKY",
            "A3_NORM", "M1_PARALLEL_LEAK", "M2_DELAY", "M4_DTS1_T1", "M5_DIRECT",
        ):
            with self.subTest(role=role):
                first = build_four_node_role_fresh_bundle(self.manifest, role)
                second = build_four_node_role_fresh_bundle(self.manifest, role)
                self.assertIsNot(first.public_field, second.public_field)
                self.assertIsNot(first.private_state_or_none, second.private_state_or_none)
                self.assertIsNot(
                    first.private_state_or_none.native_state,
                    second.private_state_or_none.native_state,
                )


if __name__ == "__main__":
    unittest.main()
