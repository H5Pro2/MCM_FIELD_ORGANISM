from __future__ import annotations

from dataclasses import fields
from pathlib import Path
import unittest

from mcm_field_organism import current_api
from mcm_field_organism._ppb1_receptor_profiles import (
    PPB1_INVALID_PROFILE,
    PPB1_PROFILE_IDS,
    PPB1_PROFILE_PARAMETER_OUT_OF_RANGE,
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    PPB1ReceptorProfileError,
    bind_ppb1_receptor_profile,
)
from mcm_field_organism._ppb1_reference import (
    PPB1BankState,
    PPB1PrototypeSlot,
    advance_ppb1_bank,
    initial_ppb1_bank_state,
)
from mcm_field_organism.receptor_contract import ReceptorContactFrame
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "browser": (
        8,
        18,
        "auditory.log8.50-3000.w800.h80.v1",
        "visual.grid3x2.channels3.source120x80.v1",
    ),
    "controlled": (
        12,
        72,
        "auditory.log12.50-1500.w400.h40.v1",
        "visual.grid6x4.channels3.source24x16.v1",
    ),
    "public-av": (
        48,
        240,
        "auditory.log48.50-18000.w4800.h480.v1",
        "visual.grid10x8.channels3.source320x240.v1",
    ),
    "default-live": (
        48,
        288,
        "auditory.log48.50-18000.w4800.h480.v1",
        "visual.grid12x8.channels3.source1920x1080.v1",
    ),
}


def parameters(*, maximum: bool = False) -> PPB1ProfileParameters:
    if maximum:
        return PPB1ProfileParameters(
            PPB1ModalityParameters(32, 0.25, 0.50, 16, 8192),
            PPB1ModalityParameters(16, 0.20, 0.50, 12, 2048),
        )
    return PPB1ProfileParameters(
        PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
        PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
    )


def frame_for(config, *, end: int = 1) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        config.modality_id,
        config.geometry_id,
        f"synthetic.{config.modality_id}.{end}",
        f"clock.{config.modality_id}",
        end - 1,
        end,
        config.carrier_ids,
        (0.0,) * len(config.carrier_ids),
    )


def full_state(config) -> PPB1BankState:
    slots = tuple(
        PPB1PrototypeSlot(
            f"{config.bank_id}.slot.{index:03d}",
            True,
            (0.0,) * len(config.carrier_ids),
            1,
            1,
        )
        for index in range(config.capacity)
    )
    return PPB1BankState(
        config.bank_id,
        config.digest(),
        1,
        f"clock.{config.modality_id}",
        1,
        slots,
    )


class PPB1ReceptorProfileBindingTests(unittest.TestCase):
    def test_all_four_profiles_bind_exact_existing_geometry(self) -> None:
        self.assertEqual(tuple(EXPECTED), PPB1_PROFILE_IDS)
        for profile_id, expected in EXPECTED.items():
            binding = bind_ppb1_receptor_profile(profile_id, parameters())
            auditory_count, visual_count, auditory_geometry, visual_geometry = expected
            self.assertEqual(auditory_count, len(binding.auditory_config.carrier_ids))
            self.assertEqual(visual_count, len(binding.visual_config.carrier_ids))
            self.assertEqual(auditory_geometry, binding.auditory_config.geometry_id)
            self.assertEqual(visual_geometry, binding.visual_config.geometry_id)

    def test_profile_binding_is_canonical_and_deterministic(self) -> None:
        first = bind_ppb1_receptor_profile("default-live", parameters())
        second = bind_ppb1_receptor_profile("default-live", parameters())
        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(64, len(first.digest()))

    def test_unknown_profile_fails_closed(self) -> None:
        with self.assertRaises(PPB1ReceptorProfileError) as caught:
            bind_ppb1_receptor_profile("unknown", parameters())
        self.assertEqual(PPB1_INVALID_PROFILE, caught.exception.code)

    def test_lower_and_upper_parameter_corridor_edges_are_accepted(self) -> None:
        for edge in (parameters(), parameters(maximum=True)):
            binding = bind_ppb1_receptor_profile("default-live", edge)
            self.assertEqual(edge.auditory.capacity, binding.auditory_config.capacity)
            self.assertEqual(edge.visual.capacity, binding.visual_config.capacity)

    def test_auditory_values_outside_corridors_are_rejected(self) -> None:
        invalid = (
            PPB1ModalityParameters(7, 0.02, 0.05, 3, 256),
            PPB1ModalityParameters(33, 0.02, 0.05, 3, 256),
            PPB1ModalityParameters(8, 0.019, 0.05, 3, 256),
            PPB1ModalityParameters(8, 0.02, 0.501, 3, 256),
            PPB1ModalityParameters(8, 0.02, 0.05, 17, 256),
            PPB1ModalityParameters(8, 0.02, 0.05, 3, 8193),
        )
        for auditory in invalid:
            with self.assertRaises(PPB1ReceptorProfileError) as caught:
                PPB1ProfileParameters(auditory, parameters().visual)
            self.assertEqual(PPB1_PROFILE_PARAMETER_OUT_OF_RANGE, caught.exception.code)

    def test_visual_values_outside_corridors_are_rejected(self) -> None:
        invalid = (
            PPB1ModalityParameters(3, 0.01, 0.05, 3, 64),
            PPB1ModalityParameters(17, 0.01, 0.05, 3, 64),
            PPB1ModalityParameters(4, 0.009, 0.05, 3, 64),
            PPB1ModalityParameters(4, 0.01, 0.501, 3, 64),
            PPB1ModalityParameters(4, 0.01, 0.05, 13, 64),
            PPB1ModalityParameters(4, 0.01, 0.05, 3, 2049),
        )
        for visual in invalid:
            with self.assertRaises(PPB1ReceptorProfileError) as caught:
                PPB1ProfileParameters(parameters().auditory, visual)
            self.assertEqual(PPB1_PROFILE_PARAMETER_OUT_OF_RANGE, caught.exception.code)

    def test_empty_states_match_bound_capacities_and_dimensions(self) -> None:
        for profile_id in PPB1_PROFILE_IDS:
            binding = bind_ppb1_receptor_profile(profile_id, parameters())
            for config in (binding.auditory_config, binding.visual_config):
                state = initial_ppb1_bank_state(config)
                self.assertEqual(config.capacity, len(state.slots))
                self.assertTrue(all(not slot.occupied for slot in state.slots))

    def test_one_synthetic_step_scales_to_every_bound_dimension(self) -> None:
        for profile_id in PPB1_PROFILE_IDS:
            binding = bind_ppb1_receptor_profile(profile_id, parameters())
            for config in (binding.auditory_config, binding.visual_config):
                result = advance_ppb1_bank(
                    config,
                    initial_ppb1_bank_state(config),
                    frame_for(config),
                )
                self.assertEqual("CREATED", result.readout.event)
                self.assertEqual(
                    len(config.carrier_ids), len(result.readout.prototype_values)
                )

    def test_maximum_full_states_match_logical_value_limits(self) -> None:
        for profile_id in PPB1_PROFILE_IDS:
            binding = bind_ppb1_receptor_profile(
                profile_id, parameters(maximum=True)
            )
            auditory = full_state(binding.auditory_config)
            visual = full_state(binding.visual_config)
            count = sum(
                len(slot.prototype_values)
                for state in (auditory, visual)
                for slot in state.slots
            )
            self.assertEqual(binding.logical_prototype_value_limit, count)
            self.assertEqual(count * 8, binding.packed_float64_bytes)

    def test_default_live_maximum_is_exactly_s1vk_upper_bound(self) -> None:
        binding = bind_ppb1_receptor_profile(
            "default-live", parameters(maximum=True)
        )
        self.assertEqual(6144, binding.logical_prototype_value_limit)
        self.assertEqual(49152, binding.packed_float64_bytes)
        self.assertEqual(1536, binding.auditory_distance_term_limit)
        self.assertEqual(4608, binding.visual_distance_term_limit)

    def test_smaller_profiles_match_registered_upper_bounds(self) -> None:
        expected = {
            "browser": (544, 256, 288),
            "controlled": (1536, 384, 1152),
            "public-av": (5376, 1536, 3840),
        }
        for profile_id, limits in expected.items():
            binding = bind_ppb1_receptor_profile(
                profile_id, parameters(maximum=True)
            )
            self.assertEqual(
                limits,
                (
                    binding.logical_prototype_value_limit,
                    binding.auditory_distance_term_limit,
                    binding.visual_distance_term_limit,
                ),
            )

    def test_full_state_input_uses_deterministic_match_not_growth(self) -> None:
        binding = bind_ppb1_receptor_profile("default-live", parameters(maximum=True))
        for config in (binding.auditory_config, binding.visual_config):
            state = full_state(config)
            result = advance_ppb1_bank(config, state, frame_for(config, end=2))
            self.assertEqual("MATCHED", result.readout.event)
            self.assertEqual(config.capacity, len(result.poststate.slots))

    def test_profiles_do_not_import_field_or_media_runtime(self) -> None:
        source = (
            ROOT / "mcm_field_organism" / "_ppb1_receptor_profiles.py"
        ).read_text(encoding="utf-8")
        forbidden = (
            "shared_mcm_field",
            "neutral_local_field_substrate",
            "audio_video_neutral_field_runtime",
            "public_av_receptor_run",
            "live_audio_video_field",
        )
        for name in forbidden:
            self.assertNotIn(name, source)

    def test_ppb_profile_roles_remain_private_and_snapshot_free(self) -> None:
        names = set(getattr(current_api, "__all__", ())) | set(ROOT_LAZY_EXPORTS)
        names |= {item.name for item in fields(SharedMCMFieldSnapshot)}
        self.assertFalse(any("ppb1" in name.lower() for name in names))


if __name__ == "__main__":
    unittest.main()
