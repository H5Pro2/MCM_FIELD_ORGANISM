from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import tools.run_public_visual_temporal_map as runner


class RunPublicVisualTemporalMapToolTests(unittest.TestCase):
    def test_missing_public_media_stops_before_temporal_decoding(self) -> None:
        missing = Path("sources") / "Street traffic.webm"
        argv = ["run_public_visual_temporal_map.py", str(missing)]

        with (
            patch.object(sys, "argv", argv),
            patch.object(
                runner,
                "decode_public_visual_receptor_sequence",
                side_effect=AssertionError("decoder must not be reached"),
            ),
        ):
            exit_code = runner.main()

        self.assertEqual(2, exit_code)


if __name__ == "__main__":
    unittest.main()
