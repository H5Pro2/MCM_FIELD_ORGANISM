from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from mcm_field_organism.public_av_container_preflight import (
    PublicAVContainerPreflight,
    PublicAVDecoderCapability,
    audit_public_av_decoder_capability,
    public_av_container_preflight_public_roles,
    run_public_av_container_preflight,
)
from mcm_field_organism.public_media_source_contract import (
    PublicMediaSourceContract,
    nasa_earthrise_av_source_contract,
)


class PublicAVContainerPreflightTests(unittest.TestCase):
    def test_missing_file_blocks_adapter_and_field_run(self) -> None:
        contract = PublicMediaSourceContract(
            "source.av.test",
            10,
            "0" * 40,
        )

        result = run_public_av_container_preflight(
            Path("missing-av-container.webm"),
            contract,
        )

        self.assertFalse(result.source_audit.accepted)
        self.assertFalse(result.adapter_prerequisites_met)
        self.assertFalse(result.adapter_implementation_allowed)
        self.assertFalse(result.field_run_allowed)
        self.assertFalse(result.metadata_receptor_release_granted)

    def test_positive_source_and_decoder_gate_allows_only_adapter_work(self) -> None:
        payload = b"public-av"
        contract = PublicMediaSourceContract(
            "source.av.test",
            len(payload),
            hashlib.sha1(payload, usedforsecurity=False).hexdigest(),
        )
        decoder = PublicAVDecoderCapability(
            ffmpeg_path="ffmpeg",
            ffprobe_path="ffprobe",
            pyav_available=False,
            soundfile_available=False,
            opencv_available=True,
            vp9_opus_container_decoder_available=True,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.webm"
            path.write_bytes(payload)

            with patch(
                "mcm_field_organism.public_av_container_preflight."
                "audit_public_av_decoder_capability",
                return_value=decoder,
            ):
                result = run_public_av_container_preflight(path, contract)

        self.assertTrue(result.source_audit.accepted)
        self.assertTrue(result.adapter_prerequisites_met)
        self.assertTrue(result.adapter_implementation_allowed)
        self.assertFalse(result.field_run_allowed)

    def test_decoder_capability_does_not_require_media_decoding(self) -> None:
        capability = audit_public_av_decoder_capability()

        self.assertIsInstance(capability.opencv_available, bool)
        self.assertIsInstance(capability.pyav_available, bool)
        self.assertIsInstance(capability.soundfile_available, bool)
        self.assertIsInstance(
            capability.vp9_opus_container_decoder_available,
            bool,
        )

    def test_local_nasa_source_passes_adapter_gate_but_not_field_gate(self) -> None:
        result = run_public_av_container_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            nasa_earthrise_av_source_contract(),
        )

        self.assertTrue(result.source_audit.accepted)
        self.assertTrue(result.decoder_capability.pyav_available)
        self.assertTrue(result.adapter_prerequisites_met)
        self.assertTrue(result.adapter_implementation_allowed)
        self.assertFalse(result.field_run_allowed)
        self.assertFalse(result.metadata_receptor_release_granted)

    def test_public_roles_exclude_labels_memory_and_receptor_values(self) -> None:
        forbidden = {
            "label",
            "meaning",
            "reward",
            "memory",
            "receptor_values",
            "raw_audio",
            "raw_video",
            "subtitle",
            "description",
        }

        self.assertTrue(
            forbidden.isdisjoint(public_av_container_preflight_public_roles())
        )

    def test_preflight_cannot_release_field_or_metadata(self) -> None:
        decoder = PublicAVDecoderCapability(
            None,
            None,
            False,
            False,
            True,
            False,
        )

        with self.assertRaisesRegex(ValueError, "field runs or metadata"):
            PublicAVContainerPreflight(
                source_audit=run_public_av_container_preflight(
                    Path("missing.webm"),
                    PublicMediaSourceContract("source.av.test", 1, "0" * 40),
                ).source_audit,
                decoder_capability=decoder,
                adapter_prerequisites_met=False,
                adapter_implementation_allowed=False,
                field_run_allowed=True,
            )


if __name__ == "__main__":
    unittest.main()
