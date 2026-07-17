from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism.external_media_observation_contract import (
    ExternalMediaObservationContractError,
    ExternalMediaObservationPhase,
    external_media_observation_contract_public_roles,
    reference_external_media_observation_contract,
)


class ExternalMediaObservationContractTests(unittest.TestCase):
    def test_reference_contract_is_reproducible_and_passive(self) -> None:
        first = reference_external_media_observation_contract()
        second = reference_external_media_observation_contract()
        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(93_000_000_000, first.total_duration_ns)
        self.assertEqual(30, first.startup_frame_count)
        self.assertFalse(first.raw_payload_retained)
        self.assertFalse(first.direct_sensor_feed)
        self.assertFalse(first.writes_back)
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            first.startup_frame_count = 3  # type: ignore[misc]

    def test_phases_are_rest_contact_rest(self) -> None:
        contract = reference_external_media_observation_contract()
        self.assertEqual(
            (False, True, False),
            tuple(phase.media_contact for phase in contract.phases),
        )
        self.assertEqual(
            (10, 63, 20),
            tuple(
                phase.duration_ns // 1_000_000_000
                for phase in contract.phases
            ),
        )

    def test_external_boundary_cannot_be_opened(self) -> None:
        contract = reference_external_media_observation_contract()
        for changes in (
            {"raw_payload_retained": True},
            {"direct_sensor_feed": True},
            {"writes_back": True},
        ):
            with self.assertRaises(ExternalMediaObservationContractError):
                replace(contract, **changes)

    def test_invalid_contact_order_is_rejected(self) -> None:
        contract = reference_external_media_observation_contract()
        with self.assertRaises(ExternalMediaObservationContractError):
            replace(
                contract,
                phases=(
                    ExternalMediaObservationPhase("rest.before", 1, False),
                    ExternalMediaObservationPhase("media.contact", 1, False),
                    ExternalMediaObservationPhase("rest.after", 1, False),
                ),
            )

    def test_public_roles_exclude_content_and_semantic_shortcuts(self) -> None:
        roles = set(external_media_observation_contract_public_roles())
        self.assertTrue(
            {
                "url",
                "title",
                "semantic_label",
                "object_class",
                "pattern_id",
                "reward",
                "raw_frame",
                "raw_audio",
                "sensor_injection",
                "field_writeback",
            }.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
