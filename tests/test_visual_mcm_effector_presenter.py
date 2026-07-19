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
    prepare_visual_mcm_effector_presentation,
    project_visual_mcm_effector_surface,
    receptor_projection_baseline,
    visual_mcm_effector_presentation_public_roles,
)


POSITIONS = ((-1, 2), (-1, 4), (0, 3), (1, 2), (1, 4))
OFFSETS = ((-1, 0), (0, -1), (0, 1), (1, 0))


def completed_frame(values: tuple[float, ...]):
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
    snapshot = build_shared_mcm_field(
        (frame,),
        {"controlled": anatomy},
        sample_offsets=OFFSETS,
    ).advance(
        distribution,
        receptor_projection_baseline,
    ).snapshot()
    return project_visual_mcm_effector_surface(snapshot)


class VisualMCMEffectorPresenterTests(unittest.TestCase):
    def test_static_plan_preserves_frame_geometry(self) -> None:
        frame = completed_frame((-1.0, -0.5, 0.0, 0.5, 1.0))
        plan = prepare_visual_mcm_effector_presentation(
            frame,
            duration_ms=2_000,
            cell_pixels=12,
        )

        self.assertEqual((frame.rows, frame.columns), (plan.rows, plan.columns))
        self.assertEqual(
            (frame.columns * 12, frame.rows * 12),
            (plan.width_pixels, plan.height_pixels),
        )
        self.assertEqual(frame.digest(), plan.source_frame_digest)

    def test_affine_intensities_receive_only_deterministic_gray_quantization(self) -> None:
        frame = completed_frame((-1.0, 0.0, 1.0, 0.0, 0.0))
        plan = prepare_visual_mcm_effector_presentation(frame)

        self.assertEqual((16384, 49151), plan.gray16_raster[0][0:2])
        self.assertEqual((49151, 16384), plan.gray16_raster[1][2:4])
        self.assertEqual((32768, 32768), plan.gray16_raster[2][4:6])

    def test_neutral_frame_is_uniform_middle_gray(self) -> None:
        plan = prepare_visual_mcm_effector_presentation(
            completed_frame((0.0,) * len(POSITIONS))
        )

        self.assertTrue(
            all(value == 32768 for row in plan.gray16_raster for value in row)
        )

    def test_same_frame_and_parameters_are_bitwise_reproducible(self) -> None:
        frame = completed_frame((-1.0, -0.5, 0.0, 0.5, 1.0))
        before = frame.digest()

        first = prepare_visual_mcm_effector_presentation(
            frame,
            duration_ms=7_500,
            cell_pixels=9,
        )
        second = prepare_visual_mcm_effector_presentation(
            frame,
            duration_ms=7_500,
            cell_pixels=9,
        )

        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(before, frame.digest())

    def test_duration_and_geometry_are_strictly_bounded(self) -> None:
        frame = completed_frame((0.0,) * len(POSITIONS))

        for duration in (0, 30_001):
            with self.assertRaises(VisualMCMEffectorPresentationError):
                prepare_visual_mcm_effector_presentation(
                    frame,
                    duration_ms=duration,
                )
        for cell_pixels in (0, 65):
            with self.assertRaises(VisualMCMEffectorPresentationError):
                prepare_visual_mcm_effector_presentation(
                    frame,
                    cell_pixels=cell_pixels,
                )

    def test_plan_is_immutable_and_forbids_runtime_extensions(self) -> None:
        plan = prepare_visual_mcm_effector_presentation(
            completed_frame((0.0,) * len(POSITIONS))
        )

        self.assertFalse(plan.animated)
        self.assertFalse(plan.writes_back)
        self.assertFalse(plan.camera_connected)
        self.assertFalse(plan.stateful)
        self.assertFalse(plan.random_source)
        with self.assertRaises(FrozenInstanceError):
            plan.duration_ms = 1  # type: ignore[misc]
        for role in (
            "animated",
            "writes_back",
            "camera_connected",
            "stateful",
            "random_source",
        ):
            with self.assertRaises(VisualMCMEffectorPresentationError):
                replace(plan, **{role: True})

    def test_non_effector_source_is_rejected(self) -> None:
        with self.assertRaises(VisualMCMEffectorPresentationError):
            prepare_visual_mcm_effector_presentation(object())  # type: ignore[arg-type]

    def test_public_roles_contain_no_semantics_memory_or_internal_return(self) -> None:
        roles = set(visual_mcm_effector_presentation_public_roles())
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
            "field_writeback",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
