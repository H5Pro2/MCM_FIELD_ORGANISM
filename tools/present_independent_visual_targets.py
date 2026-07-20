from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import (
    SharedMCMFieldSnapshot,
    prepare_independent_visual_target_plan,
    present_independent_visual_target_plan,
    project_visual_mcm_effector_surface,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Present one MCM field snapshot as two separated light channels "
            "for passive external target surfaces."
        ),
    )
    parser.add_argument(
        "snapshot",
        type=Path,
        help="Path to one canonical SharedMCMFieldSnapshot JSON file.",
    )
    parser.add_argument(
        "--duration-ms",
        type=int,
        default=5_000,
        help="Static presentation duration in milliseconds (1..30000).",
    )
    parser.add_argument(
        "--cell-pixels",
        type=int,
        default=16,
        help="Fixed square display size per channel value (1..64).",
    )
    parser.add_argument(
        "--channel-gap-pixels",
        type=int,
        default=64,
        help="Opaque physical separation shown between both channels (16..512).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    snapshot = SharedMCMFieldSnapshot.from_json(
        args.snapshot.read_text(encoding="utf-8")
    )
    frame = project_visual_mcm_effector_surface(snapshot)
    plan = prepare_independent_visual_target_plan(
        frame,
        duration_ms=args.duration_ms,
        cell_pixels=args.cell_pixels,
        channel_gap_pixels=args.channel_gap_pixels,
    )
    present_independent_visual_target_plan(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
