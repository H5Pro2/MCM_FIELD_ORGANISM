from __future__ import annotations

import json
import unittest

from mcm_field_organism.controlled_audio_phase_source import (
    shifted_sound_mute_sound_20s_source,
)
from mcm_field_organism.z4a_audio_receptor_source import (
    Z4AAudioReceptorSourceError,
    Z4AAudioSourceContract,
    audit_z4a_audio_binding,
    independent_z4a_audio_source_contract,
    reference_z4a_audio_source_contract,
    z4a_audio_binding_json_value,
)


class Z4AAudioReceptorSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = audit_z4a_audio_binding()

    def test_shifted_source_matches_the_bound_control_budget(self) -> None:
        source = shifted_sound_mute_sound_20s_source()
        self.assertEqual((375.0, 1500.0, 6000.0), source.frequencies)
        self.assertEqual((2000, 2000, 2000), source.phase_frame_counts)
        self.assertEqual(6000, source.total_frames)
        self.assertEqual(0.2, source.component_amplitude)

    def test_contracts_are_exact_and_reject_unbound_sources(self) -> None:
        reference = reference_z4a_audio_source_contract()
        independent = independent_z4a_audio_source_contract()
        self.assertEqual("z4a.audio.sound-mute-sound.v1", reference.world_id)
        self.assertEqual(
            "z4a.audio.shifted-sound-mute-sound.v1",
            independent.world_id,
        )
        self.assertNotEqual(reference.digest(), independent.digest())
        with self.assertRaises(Z4AAudioReceptorSourceError):
            Z4AAudioSourceContract(
                "z4a.audio.unbound.v1",
                (250.0, 1000.0, 4000.0),
            )

    def test_full_binding_reproduces_without_retaining_sequences(self) -> None:
        audit = self.audit
        self.assertTrue(all(value for _, value in audit.controls))
        self.assertEqual(5991, audit.reference.receptor_state_count)
        self.assertEqual(5991, audit.independent.receptor_state_count)
        self.assertEqual(1991, audit.reference.active_zero_count)
        self.assertEqual(4000, audit.reference.active_energy_count)
        self.assertNotEqual(
            audit.reference.receptor_sequence_digest,
            audit.independent.receptor_sequence_digest,
        )
        self.assertFalse(audit.raw_samples_retained)
        self.assertFalse(audit.receptor_sequences_retained)

    def test_json_projection_contains_only_scalar_binding_evidence(self) -> None:
        payload = z4a_audio_binding_json_value(self.audit)
        encoded = json.dumps(payload, allow_nan=False, sort_keys=True)
        self.assertNotIn('"samples":', encoded)
        self.assertNotIn('"frames":', encoded)
        self.assertNotIn('"values":', encoded)
        self.assertNotIn('"sequence.frames":', encoded)


if __name__ == "__main__":
    unittest.main()
