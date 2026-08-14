from __future__ import annotations

from dataclasses import replace
import math
import unittest

import cv2
import numpy as np

from mcm_field_organism.current_api import (
    BroadbandHearingPath,
    BrowserReceptorBridge,
    BrowserReceptorBridgeConfig,
    BrowserWorldContract,
    BrowserWorldPhase,
    LocalChannelGridReceptor,
    LogSpectralConfig,
    LogSpectralReceptor,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    VisualGridConfig,
    advance_audio_video_receptor_sequences,
    restore_shared_mcm_field,
)


def png_payload(value: int, top_left_red_delta: int = 0) -> bytes:
    if not 0 <= value <= 255 or not 0 <= value + top_left_red_delta <= 255:
        raise AssertionError("controlled PNG values must stay within 0..255")
    rgb = np.full((8, 12, 3), value, dtype=np.uint8)
    rgb[:4, :6, 0] = value + top_left_red_delta
    ok, encoded = cv2.imencode(
        ".png",
        cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR),
    )
    if not ok:
        raise AssertionError("controlled PNG encoding failed")
    return encoded.tobytes()


def browser_payload_field(
    visual_values: tuple[int, int, int],
    audio_amplitudes: tuple[float, ...] = (0.25,) * 15,
    afterimage_time_seconds: float | None = None,
    sequence_start_tick: int = 0,
    visual_top_left_red_deltas: tuple[int, int, int] = (0, 0, 0),
):
    if len(audio_amplitudes) != 15:
        raise AssertionError("controlled audio baseline requires 15 amplitudes")
    if len(visual_top_left_red_deltas) != 3:
        raise AssertionError("controlled visual baseline requires three deltas")
    contract = BrowserWorldContract(
        contract_id="browser.world.current_api.test.v1",
        startup_frame_count=1,
        start_lead_ns=1,
        movement_cycles=1,
        tone_frequency_hz=100.0,
        phases=(
            BrowserWorldPhase("rest.before", 100_000_000, "static", 0.0),
            BrowserWorldPhase("change", 100_000_000, "moving", 0.2),
            BrowserWorldPhase("rest.after", 100_000_000, "static", 0.0),
        ),
    )
    visual_receptor = LocalChannelGridReceptor(
        VisualGridConfig(
            source_width=12,
            source_height=8,
            grid_columns=2,
            grid_rows=2,
            frames_per_second=10.0,
        )
    )
    audio_config = LogSpectralConfig(
        sample_rate=1000,
        window_size=100,
        hop_size=20,
        min_frequency=10.0,
        max_frequency=400.0,
        band_count=4,
    )
    bridge = BrowserReceptorBridge(
        contract,
        visual_receptor,
        BroadbandHearingPath(LogSpectralReceptor(audio_config)),
        BrowserReceptorBridgeConfig(sequence_start_tick=sequence_start_tick),
    )

    for frame_index, (value, delta) in enumerate(
        zip(visual_values, visual_top_left_red_deltas, strict=True)
    ):
        bridge.push_visual_png(
            png_payload(value, delta),
            frame_index=frame_index,
        )
    for chunk_index in range(15):
        amplitude = audio_amplitudes[chunk_index]
        bridge.push_audio_chunk(
            tuple(
                amplitude
                * math.sin(
                    2.0
                    * math.pi
                    * 100.0
                    * sample
                    / audio_config.sample_rate
                )
                for sample in range(
                    chunk_index * audio_config.hop_size,
                    (chunk_index + 1) * audio_config.hop_size,
                )
            ),
            chunk_index=chunk_index,
        )

    batch = bridge.finalize()
    field_result = advance_audio_video_receptor_sequences(
        batch.sequences,
        visual_receptor,
        NeutralLocalFieldSubstrateConfig(1.0),
        afterimage_config=(
            None
            if afterimage_time_seconds is None
            else NeutralFastAfterimageConfig(afterimage_time_seconds)
        ),
        ticks_per_second=1_000_000_000.0,
    )
    return bridge, batch, field_result


class CurrentAPIBrowserPayloadConsumerTests(unittest.TestCase):
    def test_controlled_browser_payload_reaches_restorable_neutral_field(self) -> None:
        bridge, batch, field_result = browser_payload_field((48, 128, 208))
        snapshot = field_result.field_run.field.snapshot()
        restored = restore_shared_mcm_field(snapshot)

        self.assertEqual(1, snapshot.schema_version)
        self.assertEqual(
            {"schema_version", "layer", "docks", "last_distribution"},
            set(snapshot.canonical_payload()),
        )
        self.assertEqual(
            (11, 3),
            tuple(len(sequence.frames) for sequence in batch.sequences),
        )
        self.assertFalse(batch.raw_payloads_retained)
        self.assertFalse(bridge.raw_payloads_retained)
        self.assertEqual(14, field_result.field_run.source_support_count)
        self.assertEqual(14, field_result.field_run.handoff.assigned_event_count)
        self.assertEqual(snapshot.digest(), restored.snapshot().digest())
        self.assertIsNone(restored.substrate)
        self.assertIsNone(restored.development)

    def test_repetition_and_single_visual_change_form_a_controlled_pair(self) -> None:
        _, first_batch, first_field = browser_payload_field((48, 128, 208))
        _, repeated_batch, repeated_field = browser_payload_field((48, 128, 208))
        _, changed_batch, changed_field = browser_payload_field((48, 129, 208))

        self.assertEqual(first_batch.digest(), repeated_batch.digest())
        self.assertEqual(
            first_field.field_run.field.snapshot().digest(),
            repeated_field.field_run.field.snapshot().digest(),
        )
        self.assertEqual(
            first_batch.sequences[0],
            changed_batch.sequences[0],
        )
        self.assertNotEqual(
            first_batch.sequences[1],
            changed_batch.sequences[1],
        )
        self.assertNotEqual(first_batch.digest(), changed_batch.digest())
        self.assertNotEqual(
            first_field.field_run.field.snapshot().digest(),
            changed_field.field_run.field.snapshot().digest(),
        )

    def test_single_audio_change_leaves_visual_reduction_unchanged(self) -> None:
        _, control_batch, control_field = browser_payload_field((48, 128, 208))
        changed_amplitudes = (0.25,) * 7 + (0.30,) + (0.25,) * 7
        _, changed_batch, changed_field = browser_payload_field(
            (48, 128, 208),
            changed_amplitudes,
        )

        self.assertNotEqual(
            control_batch.sequences[0],
            changed_batch.sequences[0],
        )
        self.assertEqual(
            control_batch.sequences[1],
            changed_batch.sequences[1],
        )
        self.assertNotEqual(control_batch.digest(), changed_batch.digest())
        self.assertNotEqual(
            control_field.field_run.field.snapshot().digest(),
            changed_field.field_run.field.snapshot().digest(),
        )

    def test_visual_order_is_preserved_with_identical_payload_inventory(self) -> None:
        _, control_batch, control_field = browser_payload_field((48, 128, 208))
        _, reordered_batch, reordered_field = browser_payload_field((128, 48, 208))

        self.assertEqual(
            sorted(frame.frame.values for frame in control_batch.sequences[1].frames),
            sorted(frame.frame.values for frame in reordered_batch.sequences[1].frames),
        )
        self.assertEqual(
            control_batch.sequences[1].frames[-1].frame.values,
            reordered_batch.sequences[1].frames[-1].frame.values,
        )
        self.assertEqual(
            control_batch.sequences[0],
            reordered_batch.sequences[0],
        )
        self.assertNotEqual(
            control_batch.sequences[1],
            reordered_batch.sequences[1],
        )
        self.assertNotEqual(control_batch.digest(), reordered_batch.digest())
        self.assertNotEqual(
            control_field.field_run.field.snapshot().digest(),
            reordered_field.field_run.field.snapshot().digest(),
        )

    def test_audio_order_is_preserved_with_identical_amplitude_inventory(self) -> None:
        control_amplitudes = (
            (0.25,) * 7 + (0.15,) + (0.25,) * 3 + (0.35,) + (0.25,) * 3
        )
        reordered_amplitudes = (
            (0.25,) * 7 + (0.35,) + (0.25,) * 3 + (0.15,) + (0.25,) * 3
        )
        _, control_batch, control_field = browser_payload_field(
            (48, 128, 208),
            control_amplitudes,
        )
        _, reordered_batch, reordered_field = browser_payload_field(
            (48, 128, 208),
            reordered_amplitudes,
        )

        self.assertEqual(sorted(control_amplitudes), sorted(reordered_amplitudes))
        self.assertEqual(control_amplitudes[-1], reordered_amplitudes[-1])
        self.assertEqual(
            control_batch.sequences[1],
            reordered_batch.sequences[1],
        )
        self.assertNotEqual(
            control_batch.sequences[0],
            reordered_batch.sequences[0],
        )
        self.assertNotEqual(control_batch.digest(), reordered_batch.digest())
        self.assertNotEqual(
            control_field.field_run.field.snapshot().digest(),
            reordered_field.field_run.field.snapshot().digest(),
        )

    def test_order_effect_is_localized_to_activation_without_optional_states(self) -> None:
        _, _, visual_control = browser_payload_field((48, 128, 208))
        _, _, visual_reordered = browser_payload_field((128, 48, 208))
        control_amplitudes = (
            (0.25,) * 7 + (0.15,) + (0.25,) * 3 + (0.35,) + (0.25,) * 3
        )
        reordered_amplitudes = (
            (0.25,) * 7 + (0.35,) + (0.25,) * 3 + (0.15,) + (0.25,) * 3
        )
        _, _, audio_control = browser_payload_field(
            (48, 128, 208),
            control_amplitudes,
        )
        _, _, audio_reordered = browser_payload_field(
            (48, 128, 208),
            reordered_amplitudes,
        )

        for control, reordered in (
            (visual_control, visual_reordered),
            (audio_control, audio_reordered),
        ):
            control_snapshot = control.field_run.field.snapshot()
            reordered_snapshot = reordered.field_run.field.snapshot()
            self.assertNotEqual(
                control_snapshot.activation,
                reordered_snapshot.activation,
            )
            self.assertEqual(
                control_snapshot.afterimage,
                reordered_snapshot.afterimage,
            )
            self.assertTrue(all(value == 0.0 for value in control_snapshot.afterimage))
            self.assertIsNone(control_snapshot.substrate)
            self.assertIsNone(reordered_snapshot.substrate)
            self.assertIsNone(control_snapshot.development)
            self.assertIsNone(reordered_snapshot.development)

    def test_neutral_afterimage_carries_both_controlled_order_differences(self) -> None:
        _, _, visual_control = browser_payload_field(
            (48, 128, 208),
            afterimage_time_seconds=0.5,
        )
        _, _, visual_reordered = browser_payload_field(
            (128, 48, 208),
            afterimage_time_seconds=0.5,
        )
        control_amplitudes = (
            (0.25,) * 7 + (0.15,) + (0.25,) * 3 + (0.35,) + (0.25,) * 3
        )
        reordered_amplitudes = (
            (0.25,) * 7 + (0.35,) + (0.25,) * 3 + (0.15,) + (0.25,) * 3
        )
        _, _, audio_control = browser_payload_field(
            (48, 128, 208),
            control_amplitudes,
            0.5,
        )
        _, _, audio_reordered = browser_payload_field(
            (48, 128, 208),
            reordered_amplitudes,
            0.5,
        )

        for control, reordered in (
            (visual_control, visual_reordered),
            (audio_control, audio_reordered),
        ):
            control_snapshot = control.field_run.field.snapshot()
            reordered_snapshot = reordered.field_run.field.snapshot()
            self.assertNotEqual(
                control_snapshot.activation,
                reordered_snapshot.activation,
            )
            self.assertNotEqual(
                control_snapshot.afterimage,
                reordered_snapshot.afterimage,
            )
            self.assertTrue(any(value != 0.0 for value in control_snapshot.afterimage))
            self.assertTrue(any(value != 0.0 for value in reordered_snapshot.afterimage))
            self.assertIsNone(control_snapshot.substrate)
            self.assertIsNone(reordered_snapshot.substrate)
            self.assertIsNone(control_snapshot.development)
            self.assertIsNone(reordered_snapshot.development)

    def test_neutral_afterimage_does_not_feed_back_into_activation(self) -> None:
        control_amplitudes = (
            (0.25,) * 7 + (0.15,) + (0.25,) * 3 + (0.35,) + (0.25,) * 3
        )
        reordered_amplitudes = (
            (0.25,) * 7 + (0.35,) + (0.25,) * 3 + (0.15,) + (0.25,) * 3
        )
        arms = (
            ((48, 128, 208), (0.25,) * 15),
            ((128, 48, 208), (0.25,) * 15),
            ((48, 128, 208), control_amplitudes),
            ((48, 128, 208), reordered_amplitudes),
        )

        for visual_values, audio_amplitudes in arms:
            _, _, without_afterimage = browser_payload_field(
                visual_values,
                audio_amplitudes,
            )
            _, _, with_afterimage = browser_payload_field(
                visual_values,
                audio_amplitudes,
                0.5,
            )
            without_snapshot = without_afterimage.field_run.field.snapshot()
            with_snapshot = with_afterimage.field_run.field.snapshot()

            self.assertEqual(
                without_snapshot.activation,
                with_snapshot.activation,
            )
            self.assertTrue(
                all(value == 0.0 for value in without_snapshot.afterimage)
            )
            self.assertTrue(any(value != 0.0 for value in with_snapshot.afterimage))
            self.assertNotEqual(without_snapshot.digest(), with_snapshot.digest())
            self.assertIsNone(without_snapshot.substrate)
            self.assertIsNone(with_snapshot.substrate)
            self.assertIsNone(without_snapshot.development)
            self.assertIsNone(with_snapshot.development)

    def test_afterimage_intervention_does_not_change_activation_continuation(self) -> None:
        _, _, formed = browser_payload_field(
            (48, 128, 208),
            afterimage_time_seconds=0.5,
        )
        formed_snapshot = formed.field_run.field.snapshot()
        neutralized_layer = replace(
            formed_snapshot.layer,
            neurons=tuple(
                replace(neuron, afterimage=0.0)
                for neuron in formed_snapshot.layer.neurons
            ),
        )
        neutralized_snapshot = replace(
            formed_snapshot,
            layer=neutralized_layer,
        )

        continuation_bridge, continuation_batch, _ = browser_payload_field(
            (64, 64, 64),
            (0.20,) * 15,
            0.5,
            formed_snapshot.window_end_tick,
        )
        continuation_config = NeutralLocalFieldSubstrateConfig(1.0)
        continuation_afterimage = NeutralFastAfterimageConfig(0.5)
        control = advance_audio_video_receptor_sequences(
            continuation_batch.sequences,
            continuation_bridge.visual_receptor,
            continuation_config,
            afterimage_config=continuation_afterimage,
            initial_field=restore_shared_mcm_field(formed_snapshot),
            ticks_per_second=1_000_000_000.0,
        ).field_run.field.snapshot()
        neutralized = advance_audio_video_receptor_sequences(
            continuation_batch.sequences,
            continuation_bridge.visual_receptor,
            continuation_config,
            afterimage_config=continuation_afterimage,
            initial_field=restore_shared_mcm_field(neutralized_snapshot),
            ticks_per_second=1_000_000_000.0,
        ).field_run.field.snapshot()

        self.assertEqual(
            formed_snapshot.activation,
            neutralized_snapshot.activation,
        )
        self.assertNotEqual(
            formed_snapshot.afterimage,
            neutralized_snapshot.afterimage,
        )
        self.assertTrue(
            all(value == 0.0 for value in neutralized_snapshot.afterimage)
        )
        self.assertEqual(formed_snapshot.docks, neutralized_snapshot.docks)
        self.assertEqual(
            formed_snapshot.last_distribution,
            neutralized_snapshot.last_distribution,
        )
        self.assertEqual(
            formed_snapshot.window_end_tick,
            continuation_batch.sequences[1].frames[0].field_time.window_start_tick,
        )
        self.assertEqual(control.activation, neutralized.activation)
        self.assertNotEqual(control.afterimage, neutralized.afterimage)
        self.assertIsNone(control.substrate)
        self.assertIsNone(neutralized.substrate)
        self.assertIsNone(control.development)
        self.assertIsNone(neutralized.development)

    def test_small_modal_differences_survive_high_valid_payload_load(self) -> None:
        for afterimage_time_seconds in (None, 0.5):
            _, _, moderate = browser_payload_field(
                (128, 128, 128),
                (0.25,) * 15,
                afterimage_time_seconds,
            )
            _, high_batch, high = browser_payload_field(
                (230, 230, 230),
                (0.85,) * 15,
                afterimage_time_seconds,
            )
            _, visual_batch, visual_difference = browser_payload_field(
                (230, 230, 230),
                (0.85,) * 15,
                afterimage_time_seconds,
                visual_top_left_red_deltas=(5, 5, 5),
            )
            _, audio_batch, audio_difference = browser_payload_field(
                (230, 230, 230),
                (0.87,) * 15,
                afterimage_time_seconds,
            )

            moderate_snapshot = moderate.field_run.field.snapshot()
            high_snapshot = high.field_run.field.snapshot()
            visual_snapshot = visual_difference.field_run.field.snapshot()
            audio_snapshot = audio_difference.field_run.field.snapshot()
            snapshots = (
                moderate_snapshot,
                high_snapshot,
                visual_snapshot,
                audio_snapshot,
            )

            self.assertLess(
                max(abs(value) for value in moderate_snapshot.activation),
                max(abs(value) for value in high_snapshot.activation),
            )
            self.assertTrue(
                all(
                    max(abs(value) for value in item.activation) < 1.0
                    for item in snapshots
                )
            )
            self.assertEqual(high_batch.sequences[0], visual_batch.sequences[0])
            self.assertNotEqual(high_batch.sequences[1], visual_batch.sequences[1])
            self.assertNotEqual(high_snapshot.activation, visual_snapshot.activation)
            self.assertNotEqual(high_batch.sequences[0], audio_batch.sequences[0])
            self.assertEqual(high_batch.sequences[1], audio_batch.sequences[1])
            self.assertNotEqual(high_snapshot.activation, audio_snapshot.activation)
            self.assertTrue(all(item.substrate is None for item in snapshots))
            self.assertTrue(all(item.development is None for item in snapshots))
            if afterimage_time_seconds is None:
                self.assertTrue(
                    all(
                        all(value == 0.0 for value in item.afterimage)
                        for item in snapshots
                    )
                )
            else:
                self.assertTrue(
                    all(
                        any(value != 0.0 for value in item.afterimage)
                        for item in snapshots
                    )
                )


if __name__ == "__main__":
    unittest.main()
