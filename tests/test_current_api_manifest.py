from __future__ import annotations

import unittest

import mcm_field_organism as root_api
from mcm_field_organism import current_api


class CurrentAPIManifestTests(unittest.TestCase):
    def test_manifest_is_exact_complete_and_duplicate_free(self) -> None:
        manifest = current_api.__all__
        self.assertEqual(
            manifest,
            current_api.CURRENT_CONTROLLED_FIELD_EXPORTS
            + current_api.PASSIVE_COMPARISON_EXPORTS
            + current_api.CI_REFERENCE_EXPORTS
            + current_api.F3_REFERENCE_EXPORTS
            + current_api.S1B_REFERENCE_EXPORTS,
        )
        self.assertEqual(len(manifest), len(set(manifest)))
        self.assertTrue(current_api.CURRENT_CONTROLLED_FIELD_EXPORTS)
        self.assertTrue(current_api.PASSIVE_COMPARISON_EXPORTS)
        self.assertTrue(current_api.CI_REFERENCE_EXPORTS)
        self.assertTrue(current_api.F3_REFERENCE_EXPORTS)
        self.assertTrue(current_api.S1B_REFERENCE_EXPORTS)
        for name in manifest:
            with self.subTest(name=name):
                self.assertTrue(hasattr(current_api, name))

    def test_existing_root_exports_keep_identity(self) -> None:
        root_names = set(root_api.__all__)
        for name in current_api.__all__:
            if name not in root_names:
                continue
            with self.subTest(name=name):
                self.assertIs(getattr(root_api, name), getattr(current_api, name))

    def test_protocols_are_additive_device_neutral_exports(self) -> None:
        self.assertFalse(hasattr(root_api, "AudioFrameSource"))
        self.assertFalse(hasattr(root_api, "VideoFrameSource"))
        self.assertIn("AudioFrameSource", current_api.__all__)
        self.assertIn("VideoFrameSource", current_api.__all__)

    def test_forbidden_surfaces_are_absent(self) -> None:
        forbidden = (
            "SoundDeviceInputSource",
            "OpenCVVideoFrameSource",
            "capture_live_audio_video_field",
            "Z4ABrowserReceptorAdapter",
            "execute_z4a_one_shot",
            "execute_mcm_f3_history_run",
            "VisualMCMEffectorSequencePlan",
            "present_visual_mcm_effector_frame",
            "LocalSynapticMemoryState",
            "ContactMaterialLayerState",
            "NeuronRadialMaterialState",
            "S1BReciprocalAccommodationError",
        )
        for name in forbidden:
            with self.subTest(name=name):
                self.assertNotIn(name, current_api.__all__)
                self.assertFalse(hasattr(current_api, name))

    def test_reference_operations_are_not_neutral_core_exports(self) -> None:
        core = set(current_api.CURRENT_CONTROLLED_FIELD_EXPORTS)
        passive_comparison = set(current_api.PASSIVE_COMPARISON_EXPORTS)
        ci_reference = set(current_api.CI_REFERENCE_EXPORTS)
        reference = set(current_api.F3_REFERENCE_EXPORTS)
        s1b_reference = set(current_api.S1B_REFERENCE_EXPORTS)
        self.assertTrue(passive_comparison.isdisjoint(core))
        self.assertTrue(ci_reference.isdisjoint(core))
        self.assertTrue(reference.isdisjoint(core))
        self.assertTrue(s1b_reference.isdisjoint(core))
        self.assertTrue(passive_comparison.isdisjoint(ci_reference))
        self.assertTrue(passive_comparison.isdisjoint(reference))
        self.assertTrue(passive_comparison.isdisjoint(s1b_reference))
        self.assertTrue(ci_reference.isdisjoint(reference))
        self.assertTrue(ci_reference.isdisjoint(s1b_reference))
        self.assertTrue(s1b_reference.isdisjoint(reference))
        self.assertIn("compare_controlled_probe_snapshots", passive_comparison)
        self.assertNotIn("compare_controlled_probe_snapshots", core)
        self.assertIn("advance_ci_accommodation", ci_reference)
        self.assertIn("advance_ci_null_exposure", ci_reference)
        self.assertNotIn("advance_ci_accommodation", core)
        self.assertNotIn("advance_ci_null_exposure", core)
        self.assertIn("attach_uniform_mcm_substrate", reference)
        self.assertIn("advance_mcm_f3_shared_field", reference)
        self.assertNotIn("attach_uniform_mcm_substrate", core)
        self.assertNotIn("advance_mcm_f3_shared_field", core)
        self.assertIn("run_s1b_asynchronous_field", s1b_reference)
        self.assertNotIn("run_s1b_asynchronous_field", core)


if __name__ == "__main__":
    unittest.main()
