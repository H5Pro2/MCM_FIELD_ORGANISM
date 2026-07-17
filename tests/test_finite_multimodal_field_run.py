from __future__ import annotations

from dataclasses import fields
import threading
import time
import unittest

from mcm_field_organism import (
    FiniteMultimodalFieldError,
    ReceptorContactFrame,
    ReceptorDockAnatomy,
    TimedReceptorFrame,
    assemble_shared_mcm_field,
    capture_overlapping_receptor_frames,
    finite_multimodal_public_roles,
)


def receptor_frame(modality: str, values: tuple[float, ...]) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=modality,
        geometry_id=f"{modality}.receptor.v1",
        snapshot_id=f"{modality}.receptor.0",
        clock_id=f"{modality}.source",
        window_start_tick=0,
        window_end_tick=10,
        carrier_ids=tuple(f"{modality}.carrier.{index}" for index in range(len(values))),
        values=values,
    )


def anatomy(modality: str, width: int) -> ReceptorDockAnatomy:
    return ReceptorDockAnatomy(
        modality_id=modality,
        dock_id=f"dock.{modality}",
        positions=tuple((index,) for index in range(width)),
        sample_offsets=((-1,), (1,)),
    )


class FiniteMultimodalCaptureTests(unittest.TestCase):
    def test_concurrent_capture_records_real_overlap_and_source_clocks(self) -> None:
        gate = threading.Barrier(2)

        def capture(modality: str, values: tuple[float, ...]):
            def run() -> ReceptorContactFrame:
                gate.wait(timeout=1.0)
                time.sleep(0.01)
                return receptor_frame(modality, values)

            return run

        result = capture_overlapping_receptor_frames({
            "visual": capture("visual", (0.3, 0.7)),
            "auditory": capture("auditory", (0.2, 0.4, 0.6)),
        })
        self.assertEqual(("auditory", "visual"), tuple(item.frame.modality_id for item in result))
        self.assertEqual({"auditory.source", "visual.source"}, {item.frame.clock_id for item in result})
        self.assertEqual({"organism.monotonic_ns"}, {item.organism_clock_id for item in result})
        self.assertLess(
            max(item.capture_start_tick for item in result),
            min(item.capture_end_tick for item in result),
        )

    def test_sequential_nonoverlap_is_rejected_before_field_assembly(self) -> None:
        ticks = iter((0, 10, 10, 20))
        with self.assertRaisesRegex(FiniteMultimodalFieldError, "did not overlap"):
            capture_overlapping_receptor_frames(
                {
                    "auditory": lambda: receptor_frame("auditory", (0.2, 0.4)),
                    "visual": lambda: receptor_frame("visual", (0.3, 0.7)),
                },
                clock=lambda: next(ticks),
            )


class FiniteSharedFieldAssemblyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.audio = TimedReceptorFrame(
            receptor_frame("auditory", (0.2, 0.4, 0.6)),
            "organism.test",
            100,
            220,
        )
        self.video = TimedReceptorFrame(
            receptor_frame("visual", (0.3, 0.7)),
            "organism.test",
            160,
            260,
        )
        self.anatomies = {
            "auditory": anatomy("auditory", 3),
            "visual": anatomy("visual", 2),
        }

    def test_receptor_docks_reach_one_shared_neuron_layer_losslessly(self) -> None:
        result = assemble_shared_mcm_field((self.video, self.audio), self.anatomies)
        self.assertEqual(
            (160, 220),
            (
                result.field_state.window_start_tick,
                result.field_state.window_end_tick,
            ),
        )
        self.assertEqual(
            ("auditory", "visual"),
            result.receptor_distribution.modality_ids,
        )
        self.assertEqual("organism.mcm_field", result.field_state.field_id)
        self.assertEqual("organism.mcm_layer", result.field_state.layer_id)
        self.assertEqual(1, result.shared_field.layer.tick)
        self.assertEqual(
            self.audio.frame.values + self.video.frame.values,
            result.field_state.activation,
        )
        self.assertEqual(
            (0.0,) * 5,
            result.field_state.afterimage,
        )
        self.assertEqual(
            {"organism.mcm_field"},
            {neuron.field_id for neuron in result.shared_field.layer.neurons},
        )
        self.assertEqual(
            {"organism"},
            {neuron.modality_id for neuron in result.shared_field.layer.neurons},
        )

    def test_input_order_does_not_change_distribution_or_field(self) -> None:
        first = assemble_shared_mcm_field((self.audio, self.video), self.anatomies)
        second = assemble_shared_mcm_field((self.video, self.audio), self.anatomies)
        self.assertEqual(
            first.receptor_distribution.digest(),
            second.receptor_distribution.digest(),
        )
        self.assertEqual(first.field_state.digest(), second.field_state.digest())
        self.assertEqual(
            first.shared_field.layer.digest(),
            second.shared_field.layer.digest(),
        )

    def test_disjoint_capture_cannot_enter_one_shared_present(self) -> None:
        disjoint = TimedReceptorFrame(
            self.video.frame,
            "organism.test",
            220,
            260,
        )
        with self.assertRaisesRegex(
            FiniteMultimodalFieldError, "do not retain measured overlap"
        ):
            assemble_shared_mcm_field((self.audio, disjoint), self.anatomies)

    def test_public_result_roles_exclude_raw_storage_and_semantics(self) -> None:
        roles = set(finite_multimodal_public_roles())
        roles.update(item.name for item in fields(ReceptorDockAnatomy))
        forbidden = {
            "raw_audio", "raw_video", "samples", "image", "label", "meaning",
            "word", "class_id", "memory", "winner", "reward",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
