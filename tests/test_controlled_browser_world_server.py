from __future__ import annotations

import unittest

from tools.controlled_browser_world.server import (
    LiveFieldABAExperimentCoordinator,
)


class LiveFieldABAExperimentCoordinatorTests(unittest.TestCase):
    def test_default_contract_has_stable_a_b_a_horizons(self) -> None:
        coordinator = LiveFieldABAExperimentCoordinator(
            camera_device=0,
            audio_device=0,
        )

        self.assertEqual(
            ("rest.before", "change", "rest.after"),
            tuple(phase.phase_id for phase in coordinator.contract.phases),
        )
        self.assertEqual(
            (21, 7, 21),
            tuple(
                phase.duration_ns // 1_000_000_000
                for phase in coordinator.contract.phases
            ),
        )
        self.assertEqual(8_000_000_000, coordinator.contract.start_lead_ns)

    def test_controlled_world_remains_external_and_passive(self) -> None:
        coordinator = LiveFieldABAExperimentCoordinator(
            camera_device=0,
            audio_device=0,
        )
        contract = coordinator.contract

        self.assertFalse(contract.raw_frames_retained)
        self.assertFalse(contract.direct_sensor_feed)
        self.assertFalse(contract.writes_back)
        self.assertEqual("idle", coordinator.status_payload()["status"])


if __name__ == "__main__":
    unittest.main()
