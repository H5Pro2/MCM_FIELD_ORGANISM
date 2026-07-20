from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    CommonFieldTime,
    ReceptorContactFrame,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    VisualMCMEffectorPresentationError,
    build_shared_mcm_field,
    independent_visual_target_public_roles,
    prepare_independent_visual_target_plan,
    project_visual_mcm_effector_surface,
    receptor_projection_baseline,
)


POSITIONS = ((-1, 2), (-1, 4), (0, 3), (1, 2), (1, 4))
OFFSETS = ((-1, 0), (0, -1), (0, 1), (1, 0))


def completed_frame(values: tuple[float, ...]):
    contact = ReceptorContactFrame(
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
            contact.modality_id,
            contact.geometry_id,
        )
    )
    distribution = distributor.distribute(
        (contact,),
        CommonFieldTime("organism.test", 100, 120),
    )
    snapshot = build_shared_mcm_field(
        (contact,),
        {"controlled": anatomy},
        sample_offsets=OFFSETS,
    ).advance(
        distribution,
        receptor_projection_baseline,
    ).snapshot()
    return project_visual_mcm_effector_surface(snapshot)


class IndependentVisualTargetPresenterTests(unittest.TestCase):
    def test_affine_pairs_are_separated_without_changing_field_geometry(self) -> None:
        frame = completed_frame((-1.0, -0.5, 0.0, 0.5, 1.0))
        plan = prepare_independent_visual_target_plan(
            frame,
            cell_pixels=12,
            channel_gap_pixels=48,
        )

        self.assertEqual(frame.rows, plan.rows)
        self.assertEqual(frame.columns // 2, plan.columns_per_channel)
        self.assertEqual(
            2 * plan.columns_per_channel * 12 + 48,
            plan.width_pixels,
        )
        self.assertEqual(frame.rows * 12, plan.height_pixels)
        for row_index, row in enumerate(frame.intensities):
            self.assertEqual(
                tuple(round(row[index] * 65535) for index in range(0, frame.columns, 2)),
                plan.left_gray16_raster[row_index],
            )
            self.assertEqual(
                tuple(round(row[index] * 65535) for index in range(1, frame.columns, 2)),
                plan.right_gray16_raster[row_index],
            )

    def test_positive_and_negative_effects_remain_in_opposite_channels(self) -> None:
        plan = prepare_independent_visual_target_plan(
            completed_frame((-1.0, 0.0, 1.0, 0.0, 0.0))
        )

        self.assertEqual((16384, 49151), (
            plan.left_gray16_raster[0][0],
            plan.right_gray16_raster[0][0],
        ))
        self.assertEqual((49151, 16384), (
            plan.left_gray16_raster[1][1],
            plan.right_gray16_raster[1][1],
        ))

    def test_neutral_field_is_equal_middle_gray_on_both_targets(self) -> None:
        plan = prepare_independent_visual_target_plan(
            completed_frame((0.0,) * len(POSITIONS))
        )

        self.assertEqual(plan.left_gray16_raster, plan.right_gray16_raster)
        self.assertTrue(
            all(value == 32768 for row in plan.left_gray16_raster for value in row)
        )

    def test_same_source_and_parameters_are_bitwise_reproducible(self) -> None:
        frame = completed_frame((-1.0, -0.5, 0.0, 0.5, 1.0))

        first = prepare_independent_visual_target_plan(frame)
        second = prepare_independent_visual_target_plan(frame)

        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(frame.digest(), first.source_frame_digest)

    def test_plan_is_immutable_and_forbids_return_or_adaptation(self) -> None:
        plan = prepare_independent_visual_target_plan(
            completed_frame((0.0,) * len(POSITIONS))
        )

        with self.assertRaises(FrozenInstanceError):
            plan.rows = 1  # type: ignore[misc]
        for role in (
            "camera_connected",
            "writes_back",
            "stateful",
            "adaptive",
            "random_source",
        ):
            with self.assertRaises(VisualMCMEffectorPresentationError):
                replace(plan, **{role: True})

    def test_duration_cell_size_and_gap_are_bounded(self) -> None:
        frame = completed_frame((0.0,) * len(POSITIONS))

        for values in (
            {"duration_ms": 0},
            {"duration_ms": 30_001},
            {"cell_pixels": 0},
            {"cell_pixels": 65},
            {"channel_gap_pixels": 15},
            {"channel_gap_pixels": 513},
        ):
            with self.subTest(values=values):
                with self.assertRaises(VisualMCMEffectorPresentationError):
                    prepare_independent_visual_target_plan(frame, **values)

    def test_non_effector_source_is_rejected(self) -> None:
        with self.assertRaises(VisualMCMEffectorPresentationError):
            prepare_independent_visual_target_plan(object())  # type: ignore[arg-type]

    def test_public_roles_contain_no_semantics_memory_or_camera_data(self) -> None:
        forbidden = {
            "action",
            "winner",
            "reward",
            "target_label",
            "meaning",
            "semantic_label",
            "object_id",
            "memory",
            "afterimage",
            "receptor_contact",
            "camera_frame",
            "field_writeback",
        }
        self.assertTrue(
            forbidden.isdisjoint(independent_visual_target_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
