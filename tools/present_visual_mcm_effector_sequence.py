from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import (
    CommonFieldTime,
    ReceptorContactFrame,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    build_shared_mcm_field,
    prepare_visual_mcm_effector_sequence,
    prepare_visual_mcm_effector_sequence_presentation,
    present_visual_mcm_effector_sequence_plan,
    project_visual_mcm_effector_surface,
    receptor_projection_baseline,
)


POSITIONS = ((-1, 2), (-1, 4), (0, 3), (1, 2), (1, 4))
OFFSETS = ((-1, 0), (0, -1), (0, 1), (1, 0))
EVENT_VALUES = (-1.0, 0.0, 1.0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Present three bounded visual MCM effector frames.",
    )
    parser.add_argument("--frame-duration-ms", type=int, default=1_000)
    parser.add_argument("--neutral-duration-ms", type=int, default=1_000)
    parser.add_argument("--cell-pixels", type=int, default=48)
    parser.add_argument("--observation", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def controlled_frames():
    anatomy = ReceptorDockAnatomy(
        modality_id="controlled",
        dock_id="dock.controlled",
        positions=POSITIONS,
    )
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock(anatomy.dock_id, anatomy.modality_id, "controlled.receptor.v1")
    )
    reference = ReceptorContactFrame(
        modality_id=anatomy.modality_id,
        geometry_id="controlled.receptor.v1",
        snapshot_id="controlled.reference",
        clock_id="controlled.source",
        window_start_tick=0,
        window_end_tick=1,
        carrier_ids=tuple(
            f"controlled.carrier.{index}" for index in range(len(POSITIONS))
        ),
        values=(0.0,) * len(POSITIONS),
    )
    field = build_shared_mcm_field(
        (reference,),
        {anatomy.modality_id: anatomy},
        sample_offsets=OFFSETS,
    )
    result = []
    for index, value in enumerate(EVENT_VALUES):
        start = index * 10
        end = start + 10
        contact = replace(
            reference,
            snapshot_id=f"controlled.sequence.{index}",
            window_start_tick=start,
            window_end_tick=end,
            values=(value,) * len(POSITIONS),
        )
        distribution = distributor.distribute(
            (contact,),
            CommonFieldTime("organism.sequence.presentation", start, end),
        )
        field = field.advance(distribution, receptor_projection_baseline)
        result.append(project_visual_mcm_effector_surface(field.snapshot()))
    return tuple(result)


def main() -> int:
    args = parse_args()
    frames = controlled_frames()
    sequence = prepare_visual_mcm_effector_sequence(
        frames,
        frame_duration_ms=args.frame_duration_ms,
    )
    plan = prepare_visual_mcm_effector_sequence_presentation(
        sequence,
        frames,
        cell_pixels=args.cell_pixels,
        neutral_duration_ms=args.neutral_duration_ms,
    )
    if args.dry_run:
        payload = {
            "plan_digest": plan.digest(),
            "frame_count": len(plan.gray16_rasters),
            "frame_duration_ms": plan.frame_duration_ms,
            "neutral_duration_ms": plan.neutral_duration_ms,
            "total_runtime_ms": plan.total_runtime_ms,
        }
    else:
        payload = asdict(present_visual_mcm_effector_sequence_plan(plan))
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    if args.observation:
        args.observation.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
