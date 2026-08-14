from __future__ import annotations

from dataclasses import fields
import math
import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    MCMSubstrateArmContract,
    NeutralFastAfterimageConfig,
    NeutralFieldSessionError,
    NeutralFieldSessionResult,
    NeutralFieldSessionWindow,
    NeutralLocalFieldSubstrateConfig,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorDockAnatomy,
    ReceptorTimeSequence,
    SharedMCMFieldSnapshot,
    attach_uniform_mcm_substrate,
    build_shared_mcm_field,
    restore_shared_mcm_field,
    run_neutral_field_session,
)


def frame(
    modality_id: str,
    index: int,
    value: float,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=modality_id,
        geometry_id=f"{modality_id}.geometry.v1",
        snapshot_id=f"{modality_id}.snapshot.{index}",
        clock_id=f"{modality_id}.source",
        window_start_tick=index,
        window_end_tick=index + 1,
        carrier_ids=(f"{modality_id}.carrier.0",),
        values=(value,),
    )


def sequence(
    modality_id: str,
    events: tuple[tuple[int, int, float], ...],
) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        modality_id,
        f"{modality_id}.geometry.v1",
        "organism.session",
        tuple(
            OrganismTimedReceptorFrame(
                frame(modality_id, index, value),
                CommonFieldTime("organism.session", completion - 1, completion),
            )
            for index, completion, value in events
        ),
    )


def field():
    return build_shared_mcm_field(
        (frame("auditory", 100, 0.0), frame("visual", 100, 0.0)),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                ((0,),),
            ),
            "visual": ReceptorDockAnatomy(
                "visual",
                "dock.visual",
                ((1,),),
            ),
        },
        sample_offsets=((-1,), (1,)),
    )


def window(
    start: int,
    end: int,
    auditory: tuple[tuple[int, int, float], ...],
    visual: tuple[tuple[int, int, float], ...],
) -> NeutralFieldSessionWindow:
    return NeutralFieldSessionWindow(
        (sequence("auditory", auditory), sequence("visual", visual)),
        (MCMFieldStepTime("organism.session", start, end, 10.0),),
    )


def windows() -> tuple[NeutralFieldSessionWindow, ...]:
    return (
        window(0, 6, ((0, 2, 0.8),), ((0, 4, -0.6),)),
        window(6, 12, ((1, 8, -0.2),), ((1, 10, 0.3),)),
        window(12, 18, ((2, 14, 0.4),), ((2, 16, 0.7),)),
    )


def long_windows(count: int = 24) -> tuple[NeutralFieldSessionWindow, ...]:
    return tuple(
        window(
            index * 6,
            (index + 1) * 6,
            ((index, index * 6 + 2, 0.8 * math.sin(index * 0.7)),),
            ((index, index * 6 + 4, 0.8 * math.cos(index * 0.5)),),
        )
        for index in range(count)
    )


def run(initial, selected):
    return run_neutral_field_session(
        initial,
        selected,
        NeutralLocalFieldSubstrateConfig(1.0),
        afterimage_config=NeutralFastAfterimageConfig(0.5),
        max_windows=len(selected),
    )


class NeutralFieldSessionTests(unittest.TestCase):
    def test_multiple_windows_continue_one_current_field(self) -> None:
        result = run(field(), windows())
        self.assertEqual(3, result.window_count)
        self.assertEqual(6, result.source_support_count)
        self.assertEqual(18, result.field.last_distribution.field_time.window_end_tick)
        self.assertTrue(any(neuron.afterimage != 0.0 for neuron in result.field.layer.neurons))

    def test_json_snapshot_resume_matches_uninterrupted_session(self) -> None:
        uninterrupted = run(field(), windows())
        prefix = run(field(), windows()[:1])
        encoded = prefix.field.snapshot().to_json()
        decoded = SharedMCMFieldSnapshot.from_json(encoded)
        restored = restore_shared_mcm_field(decoded)
        resumed = run(restored, windows()[1:])
        self.assertEqual(
            uninterrupted.field.snapshot().digest(),
            resumed.field.snapshot().digest(),
        )

    def test_null_substrate_session_and_restore_preserve_fast_projection(self) -> None:
        legacy = run(field(), windows())
        initial = attach_uniform_mcm_substrate(
            field(),
            MCMSubstrateArmContract("p0.null", 0.0, 0.25, 0.5),
        )
        prefix = run(initial, windows()[:1])
        restored = restore_shared_mcm_field(
            SharedMCMFieldSnapshot.from_json(prefix.field.snapshot().to_json())
        )
        resumed = run(restored, windows()[1:])

        self.assertEqual(
            legacy.field.snapshot().digest(),
            resumed.field.snapshot().fast_state_projection_digest(),
        )
        self.assertEqual(
            initial.substrate.digest(),
            resumed.field.substrate.digest(),
        )

    def test_long_history_is_independent_of_checkpoint_frequency(self) -> None:
        history = long_windows()
        uninterrupted = run(field(), history)

        def checkpointed(chunk_sizes: tuple[int, ...]):
            current = field()
            offset = 0
            chunk_index = 0
            while offset < len(history):
                size = chunk_sizes[chunk_index % len(chunk_sizes)]
                selected = history[offset : offset + size]
                current = run(current, selected).field
                serialized = current.snapshot().to_json()
                self.assertNotIn("receptor_sequences", serialized)
                self.assertNotIn("handoff", serialized)
                current = restore_shared_mcm_field(
                    SharedMCMFieldSnapshot.from_json(serialized)
                )
                offset += len(selected)
                chunk_index += 1
            return current

        for chunk_sizes in ((1,), (2, 3, 5, 7), (11, 13)):
            with self.subTest(chunk_sizes=chunk_sizes):
                resumed = checkpointed(chunk_sizes)
                self.assertEqual(
                    uninterrupted.field.snapshot().digest(),
                    resumed.snapshot().digest(),
                )
        self.assertEqual(24, uninterrupted.window_count)
        self.assertEqual(48, uninterrupted.source_support_count)

    def test_gap_and_explicit_bound_are_rejected(self) -> None:
        gap = (windows()[0], windows()[2])
        with self.assertRaisesRegex(NeutralFieldSessionError, "contiguous"):
            run_neutral_field_session(
                field(),
                gap,
                NeutralLocalFieldSubstrateConfig(1.0),
                max_windows=2,
            )
        with self.assertRaisesRegex(NeutralFieldSessionError, "explicit maximum"):
            run_neutral_field_session(
                field(),
                windows(),
                NeutralLocalFieldSubstrateConfig(1.0),
                max_windows=2,
            )

    def test_restored_session_must_continue_at_serialized_boundary(self) -> None:
        prefix = run(field(), windows()[:1])
        with self.assertRaisesRegex(NeutralFieldSessionError, "serialized"):
            run(prefix.field, windows()[2:])

    def test_observer_receives_snapshots_but_result_retains_no_history(self) -> None:
        observed = []
        result = run_neutral_field_session(
            field(),
            windows(),
            NeutralLocalFieldSubstrateConfig(1.0),
            afterimage_config=NeutralFastAfterimageConfig(0.5),
            max_windows=3,
            observer=lambda index, snapshot: observed.append(
                (index, snapshot.digest())
            ),
        )
        self.assertEqual(3, len(observed))
        roles = {item.name for item in fields(NeutralFieldSessionResult)}
        self.assertEqual(
            {"field", "window_count", "source_support_count"},
            roles,
        )
        self.assertFalse(
            {
                "receptor_sequences",
                "handoff",
                "observer",
                "raw_audio",
                "raw_video",
                "meaning",
                "memory",
            }
            & roles
        )
        self.assertEqual(result.field.snapshot().digest(), observed[-1][1])


if __name__ == "__main__":
    unittest.main()
