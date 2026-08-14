from __future__ import annotations

import unittest

from mcm_field_organism.current_api import (
    S1B_CAUSAL_BROWSER_WORLD_SET_DIGEST,
    s1b_causal_browser_world_set,
)


class S1BCausalBrowserWorldTests(unittest.TestCase):
    def test_world_set_binds_three_passive_camera_free_parts(self) -> None:
        world_set = s1b_causal_browser_world_set()

        contracts = (
            world_set.history_a_contract,
            world_set.history_b_contract,
            world_set.probe_contract,
        )
        self.assertEqual(3, len({item.contract_id for item in contracts}))
        self.assertTrue(
            all(
                not item.raw_frames_retained
                and not item.direct_sensor_feed
                and not item.writes_back
                for item in contracts
            )
        )
        self.assertEqual(
            world_set.history_a_contract.total_duration_ns,
            world_set.history_b_contract.total_duration_ns,
        )

    def test_histories_share_support_but_differ_in_two_input_dimensions(self) -> None:
        world_set = s1b_causal_browser_world_set()

        support_a = tuple(
            (item.duration_ns, item.visual_mode, item.tone_gain)
            for item in world_set.history_a_contract.phases
        )
        support_b = tuple(
            (item.duration_ns, item.visual_mode, item.tone_gain)
            for item in world_set.history_b_contract.phases
        )
        self.assertEqual(support_a, support_b)
        self.assertNotEqual(
            world_set.history_a_source.motion_axis,
            world_set.history_b_source.motion_axis,
        )
        self.assertNotEqual(
            world_set.history_a_contract.tone_frequency_hz,
            world_set.history_b_contract.tone_frequency_hz,
        )

    def test_all_parts_share_the_preregistered_receptor_source_geometry(self) -> None:
        world_set = s1b_causal_browser_world_set()
        sources = (
            world_set.history_a_source,
            world_set.history_b_source,
            world_set.probe_source,
        )

        self.assertEqual({(120, 80)}, {(s.canvas_width, s.canvas_height) for s in sources})
        self.assertEqual({30.0}, {s.visual_frames_per_second for s in sources})
        self.assertEqual({8000}, {s.audio_sample_rate for s in sources})
        self.assertEqual({80}, {s.audio_hop_size for s in sources})
        self.assertEqual(S1B_CAUSAL_BROWSER_WORLD_SET_DIGEST, world_set.digest())


if __name__ == "__main__":
    unittest.main()
