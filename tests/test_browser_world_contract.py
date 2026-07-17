from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism.browser_world_contract import (
    BrowserWorldContractError,
    BrowserWorldPhase,
    browser_world_contract_public_roles,
    reference_browser_world_contract,
)


class BrowserWorldContractTests(unittest.TestCase):
    def test_reference_contract_is_reproducible_and_external(self) -> None:
        first = reference_browser_world_contract()
        second = reference_browser_world_contract()
        self.assertEqual(first, second)
        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(35_000_000_000, first.total_duration_ns)
        self.assertEqual(30, first.startup_frame_count)
        self.assertFalse(first.raw_frames_retained)
        self.assertFalse(first.direct_sensor_feed)
        self.assertFalse(first.writes_back)
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            first.startup_frame_count = 3  # type: ignore[misc]

    def test_phases_are_static_moving_static_and_silent_tone_silent(self) -> None:
        contract = reference_browser_world_contract()
        self.assertEqual(
            ("static", "moving", "static"),
            tuple(phase.visual_mode for phase in contract.phases),
        )
        self.assertEqual(
            (0.0, 0.18, 0.0),
            tuple(phase.tone_gain for phase in contract.phases),
        )
        self.assertEqual((7, 7, 21), tuple(
            phase.duration_ns // 1_000_000_000 for phase in contract.phases
        ))

    def test_external_boundary_cannot_be_opened(self) -> None:
        contract = reference_browser_world_contract()
        for changes in (
            {"raw_frames_retained": True},
            {"direct_sensor_feed": True},
            {"writes_back": True},
        ):
            with self.assertRaises(BrowserWorldContractError):
                replace(contract, **changes)

    def test_invalid_phase_programs_are_rejected(self) -> None:
        contract = reference_browser_world_contract()
        with self.assertRaises(BrowserWorldContractError):
            replace(
                contract,
                phases=(
                    BrowserWorldPhase("rest.before", 1, "static", 0.0),
                    BrowserWorldPhase("change", 1, "static", 0.18),
                    BrowserWorldPhase("rest.after", 1, "static", 0.0),
                ),
            )
        with self.assertRaises(BrowserWorldContractError):
            BrowserWorldPhase("change", 1, "moving", -0.1)

    def test_public_roles_contain_no_semantic_or_runtime_shortcuts(self) -> None:
        roles = set(browser_world_contract_public_roles())
        self.assertTrue(
            {
                "semantic_label",
                "object_class",
                "pattern_id",
                "reward",
                "target_topology",
                "raw_frame",
                "sensor_injection",
                "field_writeback",
            }.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
