from __future__ import annotations

import math
import unittest

from mcm_field_organism.s2_reference_worlds import (
    S2_INTERVENTION_WORLD_IDS,
    S2_MODEL_IDS,
    S2_SWAP_PARTNERS,
    S2_WORLD_IDS,
    build_s2_probe_world,
    build_s2_reference_tasks,
    build_s2_reference_worlds,
    s2_reference_inventory_digest,
)


class S2ReferenceWorldTests(unittest.TestCase):
    def test_world_inventory_has_bound_order_duration_and_frame_budgets(self) -> None:
        worlds = build_s2_reference_worlds()

        self.assertEqual(S2_WORLD_IDS, tuple(item.world_id[3:] for item in worlds))
        self.assertTrue(all(math.isclose(item.duration_seconds, 8.0) for item in worlds))
        self.assertEqual({800}, {item.audio_frame_count for item in worlds})
        self.assertEqual({80}, {item.video_frame_count for item in worlds})

    def test_each_rn_cn_pair_matches_contact_budget_and_centroid(self) -> None:
        worlds = {item.world_id[3:]: item for item in build_s2_reference_worlds()}

        for count in (1, 2, 4, 8):
            pair = (worlds[f"r{count}.a"], worlds[f"c{count}.a"])
            summaries = []
            for world in pair:
                cursor = 0.0
                active = 0.0
                moment = 0.0
                for phase in world.phases:
                    if phase.auditory_amplitude > 0.0:
                        active += phase.duration_seconds
                        moment += phase.duration_seconds * (
                            cursor + 0.5 * phase.duration_seconds
                        )
                    cursor += phase.duration_seconds
                summaries.append((active, moment / active))
            self.assertAlmostEqual(summaries[0][0], summaries[1][0], places=14)
            self.assertAlmostEqual(summaries[0][1], summaries[1][1], places=14)
            self.assertAlmostEqual(count * 0.4, summaries[0][0])
            self.assertAlmostEqual(4.0, summaries[0][1])

    def test_probe_is_separate_and_uses_the_bound_av_payload(self) -> None:
        probe = build_s2_probe_world()
        phase = probe.phases[0]

        self.assertEqual("s2.probe.p", probe.world_id)
        self.assertEqual(0.4, probe.duration_seconds)
        self.assertEqual(1120.0, phase.auditory_frequency)
        self.assertEqual((65, 210, 105), phase.visual_channels)
        self.assertEqual(40, probe.audio_frame_count)
        self.assertEqual(4, probe.video_frame_count)

    def test_task_inventory_is_complete_unique_and_canonical(self) -> None:
        tasks = build_s2_reference_tasks()

        self.assertEqual(152, len(tasks))
        self.assertEqual(152, len({item.task_id for item in tasks}))
        self.assertEqual(66, sum(item.kind == "main" for item in tasks))
        self.assertEqual(15, sum(item.kind == "intervention" for item in tasks))
        self.assertEqual(5, sum(item.kind == "observer" for item in tasks))
        self.assertEqual(66, sum(item.kind == "reproduction" for item in tasks))
        self.assertEqual(6, len(S2_MODEL_IDS))
        self.assertEqual(5, len(S2_INTERVENTION_WORLD_IDS))

    def test_swap_map_is_an_involution_and_inventory_digest_is_stable(self) -> None:
        for world_id, partner in S2_SWAP_PARTNERS.items():
            self.assertEqual(world_id, S2_SWAP_PARTNERS[partner])
        self.assertEqual(
            s2_reference_inventory_digest(),
            s2_reference_inventory_digest(),
        )


if __name__ == "__main__":
    unittest.main()
