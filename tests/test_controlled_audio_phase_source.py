from __future__ import annotations

import hashlib
import struct
import unittest

from mcm_field_organism import (
    AudioCaptureError,
    AudioGainPhase,
    AuditoryProbeConfig,
    AuditoryReceptorContact,
    BroadbandHearingPath,
    ControlledAudioPhaseSource,
    ControlledAudioGateSource,
    LogSpectralConfig,
    LogSpectralReceptor,
    SyntheticAudioFrameSource,
    pass_mute_pass_20s_gate,
    sound_mute_sound_20s_source,
)
from mcm_field_organism.auditory_fast_field_probe import (
    project_auditory_fast_field_candidate,
)


def frame_digest(source: ControlledAudioPhaseSource) -> str:
    digest = hashlib.sha256()
    for _ in range(source.total_frames):
        for sample in source.read_frame():
            digest.update(struct.pack("!d", sample))
    return digest.hexdigest()


class ControlledAudioPhaseSourceTests(unittest.TestCase):
    def test_default_schedule_is_exactly_20_20_20_seconds(self) -> None:
        source = sound_mute_sound_20s_source()
        self.assertEqual((2000, 2000, 2000), source.phase_frame_counts)
        self.assertEqual(6000, source.total_frames)
        self.assertFalse(hasattr(source, "frames"))
        self.assertFalse(hasattr(source, "__dict__"))
        self.assertEqual((0, 0), source.phase_for_frame(0))
        self.assertEqual((1, 0), source.phase_for_frame(2000))
        self.assertEqual((2, 0), source.phase_for_frame(4000))
        self.assertEqual((2, 1999), source.phase_for_frame(5999))

    def test_mute_phase_is_exact_zero_and_contact_phases_repeat(self) -> None:
        config = AuditoryProbeConfig(sample_rate=8000, frame_size=80)
        source = ControlledAudioPhaseSource(
            config=config,
            phases=(
                AudioGainPhase("contact.1", 0.02, 1.0),
                AudioGainPhase("mute", 0.02, 0.0),
                AudioGainPhase("contact.2", 0.02, 1.0),
            ),
            frequencies=(250.0, 1000.0),
        )
        first = (source.read_frame(), source.read_frame())
        middle = (source.read_frame(), source.read_frame())
        last = (source.read_frame(), source.read_frame())
        self.assertEqual(((0.0,) * 80,) * 2, middle)
        self.assertEqual(first, last)
        with self.assertRaises(AudioCaptureError):
            source.read_frame()

    def test_reset_reproduces_the_same_sequence_digest(self) -> None:
        config = AuditoryProbeConfig(sample_rate=8000, frame_size=80)
        source = ControlledAudioPhaseSource(
            config=config,
            phases=(AudioGainPhase("contact", 0.03, 1.0),),
            frequencies=(250.0, 1000.0),
        )
        first = frame_digest(source)
        source.reset()
        second = frame_digest(source)
        self.assertEqual(first, second)

    def test_invalid_phase_and_signal_domains_are_rejected(self) -> None:
        config = AuditoryProbeConfig(sample_rate=8000, frame_size=80)
        with self.assertRaises(AudioCaptureError):
            AudioGainPhase("Mute Phase", 1.0, 0.0)
        with self.assertRaises(AudioCaptureError):
            AudioGainPhase("mute", 0.0, 0.0)
        with self.assertRaises(AudioCaptureError):
            AudioGainPhase("mute", 1.0, 1.1)
        with self.assertRaises(AudioCaptureError):
            ControlledAudioPhaseSource(config=config, phases=())
        with self.assertRaises(AudioCaptureError):
            ControlledAudioPhaseSource(
                config=config,
                phases=(AudioGainPhase("short", 0.015, 1.0),),
            )
        with self.assertRaises(AudioCaptureError):
            ControlledAudioPhaseSource(
                config=config,
                phases=(AudioGainPhase("contact", 0.02, 1.0),),
                frequencies=(250.0, 1000.0),
                component_amplitude=0.6,
            )

    def test_full_receptor_and_field_chain_follows_the_exact_mute_phase(self) -> None:
        source = sound_mute_sound_20s_source()
        receptor = LogSpectralReceptor(LogSpectralConfig(band_count=48))
        path = BroadbandHearingPath(receptor)
        states = []
        for _ in range(source.total_frames):
            state = path.push(source.read_frame())
            if state is not None:
                states.append(state)

        self.assertEqual(5991, len(states))
        phase_1 = states[:1991]
        phase_2 = states[1991:3991]
        phase_3 = states[3991:]
        self.assertEqual((1991, 2000, 2000), tuple(map(len, (phase_1, phase_2, phase_3))))

        zero_states = [state for state in phase_2 if state.contact is AuditoryReceptorContact.ACTIVE_ZERO]
        self.assertEqual(1991, len(zero_states))
        self.assertTrue(all(state.energy == (0.0,) * 48 for state in zero_states))
        self.assertEqual(phase_1[0].energy, phase_3[9].energy)
        self.assertEqual(phase_1[-1].energy, phase_3[-1].energy)

        for tau in (0.05, 0.2, 1.0):
            windows = project_auditory_fast_field_candidate(states, dt=0.01, tau=tau)
            mute_windows = windows[1991:3991]
            self.assertGreater(sum(mute_windows[0].afterimage), sum(mute_windows[-1].afterimage))
            self.assertEqual(phase_1[0].energy, windows[4000].activation)
            self.assertEqual(phase_1[-1].energy, windows[-1].activation)


class ControlledAudioGateSourceTests(unittest.TestCase):
    def test_default_live_gate_is_exactly_pass_mute_pass(self) -> None:
        config = AuditoryProbeConfig(sample_rate=48000, frame_size=480)
        source = SyntheticAudioFrameSource(((0.0,) * 480,) * 6000)
        gate = pass_mute_pass_20s_gate(source, config=config)
        self.assertEqual((2000, 2000, 2000), gate.phase_frame_counts)
        self.assertEqual(6000, gate.total_frames)
        self.assertFalse(hasattr(gate, "frames"))
        self.assertFalse(hasattr(gate, "__dict__"))

    def test_gate_passes_live_frames_and_drains_muted_frames(self) -> None:
        config = AuditoryProbeConfig(sample_rate=8000, frame_size=80)
        frames = tuple((value,) * 80 for value in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6))
        source = SyntheticAudioFrameSource(frames)
        gate = ControlledAudioGateSource(
            source=source,
            config=config,
            phases=(
                AudioGainPhase("pass.1", 0.02, 1.0),
                AudioGainPhase("mute", 0.02, 0.0),
                AudioGainPhase("pass.2", 0.02, 1.0),
            ),
        )
        output = tuple(gate.read_frame() for _ in range(6))
        self.assertEqual(frames[:2], output[:2])
        self.assertEqual(((0.0,) * 80,) * 2, output[2:4])
        self.assertEqual(frames[4:], output[4:])
        self.assertEqual(6, gate.frames_read)
        with self.assertRaises(AudioCaptureError):
            gate.read_frame()
        with self.assertRaises(AudioCaptureError):
            source.read_frame()

    def test_mute_does_not_hide_invalid_hardware_frames(self) -> None:
        config = AuditoryProbeConfig(sample_rate=8000, frame_size=80)
        source = SyntheticAudioFrameSource(((0.0,) * 79,))
        gate = ControlledAudioGateSource(
            source=source,
            config=config,
            phases=(AudioGainPhase("mute", 0.01, 0.0),),
        )
        with self.assertRaises(AudioCaptureError):
            gate.read_frame()

    def test_gate_rejects_fractional_gain_and_fractional_chunks(self) -> None:
        config = AuditoryProbeConfig(sample_rate=8000, frame_size=80)
        source = SyntheticAudioFrameSource(((0.0,) * 80,))
        with self.assertRaises(AudioCaptureError):
            ControlledAudioGateSource(
                source=source,
                config=config,
                phases=(AudioGainPhase("partial", 0.01, 0.5),),
            )
        with self.assertRaises(AudioCaptureError):
            ControlledAudioGateSource(
                source=source,
                config=config,
                phases=(AudioGainPhase("pass", 0.015, 1.0),),
            )


if __name__ == "__main__":
    unittest.main()
