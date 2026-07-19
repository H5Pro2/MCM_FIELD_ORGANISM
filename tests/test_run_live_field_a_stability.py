from __future__ import annotations

import unittest

from tools.run_live_field_a_stability import (
    _late_block_metrics,
    _mean_l1,
    _mean_profile,
)


class LiveFieldAStabilitySummaryTests(unittest.TestCase):
    def test_mean_profile_and_l1_preserve_field_width(self) -> None:
        self.assertEqual((2.0, 4.0), _mean_profile(((1.0, 3.0), (3.0, 5.0))))
        self.assertEqual(2.0, _mean_l1((1.0, 5.0), (3.0, 3.0)))

    def test_three_late_a_blocks_remain_separate(self) -> None:
        result = _late_block_metrics(
            (
                ((0.0, 0.0), (1.0, 1.0)),
                ((0.0, 0.0), (2.0, 2.0)),
                ((0.0, 0.0), (3.0, 3.0)),
            ),
            late_window_count=1,
        )

        self.assertEqual((0.0, 0.0, 0.0), result["internal_l1"])
        self.assertEqual(1.0, result["block_2_vs_block_1_l1"])
        self.assertEqual(2.0, result["block_3_vs_block_1_l1"])
        self.assertEqual(1.0, result["block_3_vs_block_2_l1"])

    def test_invalid_block_shape_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            _late_block_metrics((((0.0,),),), late_window_count=1)


if __name__ == "__main__":
    unittest.main()
