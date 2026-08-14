from __future__ import annotations

import unittest

import numpy as np

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_local_edge_plasticity import (
    E1EdgeBinding,
    E1LocalEdgePlasticityState,
    build_neutral_e1_state,
)
from mcm_field_organism.e1_mirrored_history import (
    E1_MIRRORED_HISTORY_INTERVALS,
    E1MirroredHistoryError,
    produce_e1_mirrored_histories,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_e1_coupled_fast_field import contract
from tests.test_neutral_fast_afterimage import shared_field, values


class E1MirroredHistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.field = shared_field()
        self.state = build_neutral_e1_state(self.field.layer, contract())
        self.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        self.afterimage = NeutralFastAfterimageConfig(0.5)

    def produce(self):
        return produce_e1_mirrored_histories(
            self.field,
            self.state,
            self.substrate,
            self.afterimage,
        )

    def test_histories_use_eight_equal_energy_contacts(self) -> None:
        result = self.produce()

        self.assertEqual(8, E1_MIRRORED_HISTORY_INTERVALS)
        self.assertEqual(8.0, result.left_contact_energy)
        self.assertEqual(result.left_contact_energy, result.right_contact_energy)
        self.assertEqual(8, result.left_field.layer.tick)
        self.assertEqual(result.left_field.layer.tick, result.right_field.layer.tick)
        self.assertEqual(
            80,
            result.left_field.last_distribution.field_time.window_end_tick,
        )
        self.assertEqual(
            result.left_field.last_distribution.field_time,
            result.right_field.last_distribution.field_time,
        )

    def test_history_objects_are_separate_and_inputs_remain_unchanged(self) -> None:
        layer_digest = self.field.layer.digest()
        bindings = self.state.edge_bindings

        result = self.produce()

        self.assertIsNot(result.left_field, result.right_field)
        self.assertIsNot(result.left_e1_state, result.right_e1_state)
        self.assertIsNot(result.left_field, self.field)
        self.assertIsNot(result.left_e1_state, self.state)
        self.assertEqual(layer_digest, self.field.layer.digest())
        self.assertEqual(bindings, self.state.edge_bindings)

    def test_end_bindings_are_distinct_equal_total_and_mirrored(self) -> None:
        result = self.produce()
        left = tuple(item.binding for item in result.left_e1_state.edge_bindings)
        right = tuple(item.binding for item in result.right_e1_state.edge_bindings)

        self.assertNotEqual(left, right)
        np.testing.assert_allclose(left, right[::-1], rtol=0.0, atol=1e-14)
        self.assertLessEqual(result.total_binding_difference, 1e-14)
        self.assertLessEqual(result.maximum_mirror_binding_error, 1e-14)

    def test_end_fields_are_mirrored_but_not_equal_in_canonical_order(self) -> None:
        result = self.produce()
        for role in ("activation", "afterimage"):
            left = values(result.left_field, role)
            right = values(result.right_field, role)
            self.assertGreater(float(np.max(np.abs(left - right))), 1e-6)
            np.testing.assert_allclose(left, right[::-1], rtol=0.0, atol=1e-14)

    def test_producer_is_deterministic(self) -> None:
        first = self.produce()
        second = self.produce()

        self.assertEqual(first, second)

    def test_non_neutral_initial_e1_state_is_rejected(self) -> None:
        first = self.state.edge_bindings[0]
        non_neutral = E1LocalEdgePlasticityState(
            self.state.contract,
            (
                E1EdgeBinding(first.first_neuron_id, first.second_neuron_id, 0.1),
                self.state.edge_bindings[1],
            ),
            self.state.edge_inventory_digest,
        )
        with self.assertRaisesRegex(E1MirroredHistoryError, "neutral"):
            produce_e1_mirrored_histories(
                self.field,
                non_neutral,
                self.substrate,
                self.afterimage,
            )

    def test_first_corridor_rejects_non_three_node_geometry(self) -> None:
        field = shared_field(2)
        state = build_neutral_e1_state(field.layer, contract())
        with self.assertRaisesRegex(E1MirroredHistoryError, "positions"):
            produce_e1_mirrored_histories(
                field,
                state,
                self.substrate,
                self.afterimage,
            )

    def test_history_roles_are_not_exported_and_no_probe_is_returned(self) -> None:
        result = self.produce()
        self.assertFalse(hasattr(result, "probe"))
        self.assertFalse(hasattr(result, "probe_field"))
        for role in ("E1MirroredHistoryResult", "produce_e1_mirrored_histories"):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
