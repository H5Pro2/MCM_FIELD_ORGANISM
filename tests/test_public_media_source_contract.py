from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from mcm_field_organism.public_media_source_contract import (
    PublicMediaSourceContract,
    audit_public_media_source,
    brokindsleden_av_source_contract,
    nasa_earthrise_av_source_contract,
    public_media_source_contract_public_roles,
    street_traffic_source_contract,
)


class PublicMediaSourceContractTests(unittest.TestCase):
    def test_matching_local_source_is_accepted_without_receptor_release(self) -> None:
        payload = b"bounded-public-world"
        digest = hashlib.sha1(payload, usedforsecurity=False).hexdigest()
        contract = PublicMediaSourceContract("source.test", len(payload), digest)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "world.bin"
            path.write_bytes(payload)

            audit = audit_public_media_source(path, contract)

        self.assertTrue(audit.accepted)
        self.assertTrue(audit.size_matches)
        self.assertTrue(audit.sha1_matches)
        self.assertFalse(audit.receptor_release_granted)

    def test_missing_source_is_a_complete_negative_audit(self) -> None:
        audit = audit_public_media_source(
            Path("missing-public-world.webm"),
            street_traffic_source_contract(),
        )

        self.assertFalse(audit.file_present)
        self.assertFalse(audit.accepted)
        self.assertIsNone(audit.observed_size_bytes)
        self.assertIsNone(audit.observed_sha1)

    def test_missing_audiovisual_candidate_is_not_receptor_released(self) -> None:
        contract = brokindsleden_av_source_contract()

        audit = audit_public_media_source(
            Path("sources/media/Brokindsleden - The sounds of traffic.webm"),
            contract,
        )

        self.assertEqual(
            "public.audiovisual.brokindsleden-traffic-sound.commons.2018-12-18",
            audit.source_id,
        )
        self.assertFalse(audit.file_present)
        self.assertFalse(audit.accepted)
        self.assertFalse(audit.receptor_release_granted)

    def test_changed_bytes_are_rejected_even_at_identical_size(self) -> None:
        expected = b"first-world"
        changed = b"other-world"
        self.assertEqual(len(expected), len(changed))
        contract = PublicMediaSourceContract(
            "source.test",
            len(expected),
            hashlib.sha1(expected, usedforsecurity=False).hexdigest(),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "world.bin"
            path.write_bytes(changed)

            audit = audit_public_media_source(path, contract)

        self.assertTrue(audit.size_matches)
        self.assertFalse(audit.sha1_matches)
        self.assertFalse(audit.accepted)

    def test_local_nasa_earthrise_original_is_accepted_without_release(self) -> None:
        audit = audit_public_media_source(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            nasa_earthrise_av_source_contract(),
        )

        self.assertEqual(
            "public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20",
            audit.source_id,
        )
        self.assertTrue(audit.file_present)
        self.assertTrue(audit.accepted)
        self.assertEqual(13_547_755, audit.observed_size_bytes)
        self.assertEqual(
            "c63198a925ad227950cca597c4a8500656bacdfc",
            audit.observed_sha1,
        )
        self.assertFalse(audit.receptor_release_granted)

    def test_public_roles_exclude_semantics_and_organism_state(self) -> None:
        forbidden = {
            "label",
            "meaning",
            "reward",
            "memory",
            "field_state",
            "receptor_values",
            "raw_media",
        }
        self.assertTrue(
            forbidden.isdisjoint(public_media_source_contract_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
