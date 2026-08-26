from __future__ import annotations

import unittest

from mcm_field_organism.mcm_f3_k2b_source import (
    build_mcm_f3_k2b_source,
    mcm_f3_k2b_source_public_roles,
)


class MCMF3K2BSourceTests(unittest.TestCase):
    def test_source_has_five_fixed_checkpoints(self) -> None:
        source = build_mcm_f3_k2b_source()

        self.assertEqual(4, len(source.contact_b_steps))
        self.assertEqual(4, len(source.interruption_steps))
        self.assertEqual(5, len(source.probes))
        self.assertEqual((391, 40), tuple(len(item.frames) for item in source.contact_a))
        self.assertEqual((100, 10), tuple(len(item.frames) for item in source.contact_b_steps[-1]))
        self.assertEqual((100, 10), tuple(len(item.frames) for item in source.interruption_steps[-1]))

    def test_prefix_and_probe_intervals_are_fixed(self) -> None:
        source = build_mcm_f3_k2b_source()

        for checkpoint in range(1, 5):
            for inventory in (source.contact_b_steps, source.interruption_steps):
                sequences = inventory[checkpoint - 1]
                self.assertEqual(
                    (3 + checkpoint) * 1_000_000,
                    sequences[1].frames[0].field_time.window_start_tick,
                )
                expected_audio_start = (3 + checkpoint) * 1_000_000
                if checkpoint == 1:
                    expected_audio_start += 90_000
                self.assertEqual(
                    expected_audio_start,
                    sequences[0].frames[0].field_time.window_start_tick,
                )
                self.assertEqual(
                    (4 + checkpoint) * 1_000_000,
                    sequences[0].frames[-1].field_time.window_end_tick,
                )
            probe = source.probes[checkpoint]
            self.assertEqual(
                (4 + checkpoint) * 1_000_000,
                probe[1].frames[0].field_time.window_start_tick,
            )
            self.assertEqual(
                (4 + checkpoint) * 1_000_000 + 90_000,
                probe[0].frames[0].field_time.window_start_tick,
            )

    def test_public_surface_has_no_content_or_claim_roles(self) -> None:
        roles = set(mcm_f3_k2b_source_public_roles())

        self.assertTrue(
            {"label", "meaning", "object", "reward", "memory"}.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
