from __future__ import annotations

from pathlib import Path
import unittest

from mcm_field_organism.finite_video_path import VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig
from mcm_field_organism.public_av_receptor_preflight import (
    PublicAVReceptorPreflight,
    PublicAVReceptorPreflightError,
    public_av_receptor_preflight_public_roles,
    run_public_av_receptor_preflight,
)
from mcm_field_organism.public_media_source_contract import (
    nasa_earthrise_av_source_contract,
)


NASA_SOURCE = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")


class PublicAVReceptorPreflightTests(unittest.TestCase):
    def test_default_audio_and_native_video_contracts_are_compatible(self) -> None:
        result = run_public_av_receptor_preflight(
            NASA_SOURCE,
            nasa_earthrise_av_source_contract(),
            LogSpectralConfig(),
            VisualGridConfig(320, 240, 10, 8, 29.97),
        )

        self.assertTrue(result.receptor_prerequisites_met)
        self.assertFalse(result.receptor_run_allowed)
        self.assertFalse(result.field_run_allowed)
        self.assertFalse(result.raw_payload_retained)

    def test_incompatible_video_geometry_keeps_prerequisites_negative(self) -> None:
        result = run_public_av_receptor_preflight(
            NASA_SOURCE,
            nasa_earthrise_av_source_contract(),
            LogSpectralConfig(),
            VisualGridConfig(640, 480, 10, 8, 29.97),
        )

        self.assertFalse(result.video_shape_matches)
        self.assertFalse(result.receptor_prerequisites_met)

    def test_disjoint_interval_preserves_receptor_contract(self) -> None:
        result = run_public_av_receptor_preflight(
            NASA_SOURCE,
            nasa_earthrise_av_source_contract(),
            LogSpectralConfig(),
            VisualGridConfig(320, 240, 10, 8, 29.97),
            start_tick=500_000_000,
        )

        self.assertTrue(result.receptor_prerequisites_met)

    def test_preflight_cannot_release_receptor_or_field(self) -> None:
        result = run_public_av_receptor_preflight(
            NASA_SOURCE,
            nasa_earthrise_av_source_contract(),
            LogSpectralConfig(),
            VisualGridConfig(320, 240, 10, 8, 29.97),
        )
        values = {
            role: getattr(result, role) for role in result.__dataclass_fields__
        }
        values["receptor_run_allowed"] = True

        with self.assertRaisesRegex(PublicAVReceptorPreflightError, "cannot release"):
            PublicAVReceptorPreflight(**values)

    def test_public_roles_exclude_content_and_organism_state(self) -> None:
        forbidden = {
            "samples",
            "pixels",
            "label",
            "meaning",
            "reward",
            "memory",
            "field_state",
            "receptor_values",
        }
        self.assertTrue(
            forbidden.isdisjoint(public_av_receptor_preflight_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
