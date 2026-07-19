from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMNeuronValidationError,
    ReceptorContactFrame,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    VisualMCMEffectorSurfaceError,
    build_shared_mcm_field,
    project_visual_mcm_effector_surface,
    receptor_projection_baseline,
    visual_mcm_effector_surface_public_roles,
)


POSITIONS = ((-1, 2), (-1, 4), (0, 3), (1, 2), (1, 4))
ACTIVATIONS = (-1.0, -0.5, 0.0, 0.5, 1.0)
OFFSETS = ((-1, 0), (0, -1), (0, 1), (1, 0))


def completed_snapshot(values: tuple[float, ...] = ACTIVATIONS):
    frame = ReceptorContactFrame(
        modality_id="controlled",
        geometry_id="controlled.receptor.v1",
        snapshot_id="controlled.snapshot.0",
        clock_id="controlled.source",
        window_start_tick=10,
        window_end_tick=20,
        carrier_ids=tuple(
            f"controlled.carrier.{index}" for index in range(len(values))
        ),
        values=values,
    )
    anatomy = ReceptorDockAnatomy(
        modality_id="controlled",
        dock_id="dock.controlled",
        positions=POSITIONS,
    )
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock(
            anatomy.dock_id,
            frame.modality_id,
            frame.geometry_id,
        )
    )
    distribution = distributor.distribute(
        (frame,),
        CommonFieldTime("organism.test", 100, 120),
    )
    return build_shared_mcm_field(
        (frame,),
        {"controlled": anatomy},
        sample_offsets=OFFSETS,
    ).advance(
        distribution,
        receptor_projection_baseline,
    ).snapshot()


class VisualMCMEffectorSurfaceTests(unittest.TestCase):
    def test_complete_two_dimensional_geometry_is_preserved(self) -> None:
        result = project_visual_mcm_effector_surface(completed_snapshot())

        self.assertEqual((-1, 2), (result.row_origin, result.column_origin))
        self.assertEqual((3, 6), (result.rows, result.columns))
        self.assertEqual(1, result.source_tick)
        self.assertEqual(
            (100, 120),
            (
                result.source_window_start_tick,
                result.source_window_end_tick,
            ),
        )
        self.assertEqual(POSITIONS, tuple(cell.field_position for cell in result.cells))
        self.assertEqual(
            ((0, 0, 1), (0, 4, 5), (1, 2, 3), (2, 0, 1), (2, 4, 5)),
            tuple(
                (cell.output_row, cell.left_column, cell.right_column)
                for cell in result.cells
            ),
        )
        self.assertEqual((0.5, 0.5), result.intensities[1][0:2])
        self.assertEqual((0.5, 0.5), result.intensities[1][4:6])

    def test_neutral_field_is_exactly_middle_gray(self) -> None:
        result = project_visual_mcm_effector_surface(
            completed_snapshot((0.0,) * len(POSITIONS))
        )

        self.assertTrue(
            all(value == 0.5 for row in result.intensities for value in row)
        )
        self.assertTrue(
            all(
                cell.left_intensity == 0.5
                and cell.right_intensity == 0.5
                for cell in result.cells
            )
        )

    def test_positive_and_negative_values_exchange_pair_effect(self) -> None:
        result = project_visual_mcm_effector_surface(completed_snapshot())
        by_activation = {cell.activation: cell for cell in result.cells}

        self.assertEqual(
            (
                by_activation[-1.0].left_intensity,
                by_activation[-1.0].right_intensity,
            ),
            (
                by_activation[1.0].right_intensity,
                by_activation[1.0].left_intensity,
            ),
        )
        self.assertEqual((0.25, 0.75), (
            by_activation[-1.0].left_intensity,
            by_activation[-1.0].right_intensity,
        ))
        self.assertEqual((0.75, 0.25), (
            by_activation[1.0].left_intensity,
            by_activation[1.0].right_intensity,
        ))

    def test_transfer_is_exactly_affine_without_threshold_or_clipping(self) -> None:
        result = project_visual_mcm_effector_surface(completed_snapshot())

        for cell in result.cells:
            self.assertEqual(
                0.50 + 0.25 * cell.activation,
                cell.left_intensity,
            )
            self.assertEqual(
                0.50 - 0.25 * cell.activation,
                cell.right_intensity,
            )
            self.assertEqual(1.0, cell.left_intensity + cell.right_intensity)
        self.assertEqual(
            (0.25, 0.375, 0.5, 0.625, 0.75),
            tuple(cell.left_intensity for cell in result.cells),
        )

    def test_same_input_is_bitwise_reproducible_and_source_is_unchanged(self) -> None:
        snapshot = completed_snapshot()
        before = snapshot.digest()

        first = project_visual_mcm_effector_surface(snapshot)
        second = project_visual_mcm_effector_surface(snapshot)

        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(before, snapshot.digest())
        self.assertEqual(before, first.source_snapshot_digest)

    def test_surface_is_immutable_stateless_and_has_no_internal_return(self) -> None:
        result = project_visual_mcm_effector_surface(completed_snapshot())

        self.assertFalse(result.writes_back)
        self.assertFalse(result.stateful)
        self.assertFalse(result.random_source)
        with self.assertRaises(FrozenInstanceError):
            result.rows = 1  # type: ignore[misc]
        for role in (
            "writes_back",
            "stateful",
            "random_source",
        ):
            with self.assertRaises(VisualMCMEffectorSurfaceError):
                replace(result, **{role: True})

    def test_invalid_or_damaged_activation_is_rejected_without_clipping(self) -> None:
        snapshot = completed_snapshot()
        object.__setattr__(snapshot.layer.neurons[0], "activation", 1.0001)

        with self.assertRaisesRegex(
            VisualMCMEffectorSurfaceError,
            "activation must stay within",
        ):
            project_visual_mcm_effector_surface(snapshot)

        with self.assertRaises(MCMNeuronValidationError):
            replace(snapshot.layer.neurons[1], activation=-1.0001)

    def test_non_snapshot_and_non_two_dimensional_field_are_rejected(self) -> None:
        with self.assertRaises(VisualMCMEffectorSurfaceError):
            project_visual_mcm_effector_surface(object())  # type: ignore[arg-type]

        snapshot = completed_snapshot()
        object.__setattr__(snapshot.layer.neurons[0], "position", (0,))
        with self.assertRaisesRegex(
            VisualMCMEffectorSurfaceError,
            "two-dimensional",
        ):
            project_visual_mcm_effector_surface(snapshot)

    def test_public_roles_contain_no_semantics_selection_or_memory(self) -> None:
        roles = set(visual_mcm_effector_surface_public_roles())
        forbidden = {
            "action",
            "winner",
            "reward",
            "target",
            "meaning",
            "semantic_label",
            "object_id",
            "memory",
            "afterimage",
            "receptor_contact",
            "camera_frame",
            "screen_handle",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
