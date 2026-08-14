from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import (
    LocalChannelGridReceptor,
    VisualGridConfig,
    decode_public_visual_receptor_sequence,
    observe_public_visual_world,
)
from mcm_field_organism.public_media_source_contract import (
    audit_public_media_source,
    street_traffic_source_contract,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Process only the pixel track of one public real-world video "
            "through the visual receptor and shared MCM field."
        )
    )
    parser.add_argument("video", type=Path)
    parser.add_argument("--sampling-interval-ms", type=int, default=125)
    parser.add_argument("--max-duration-ms", type=int, default=60_000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = audit_public_media_source(
        args.video,
        street_traffic_source_contract(),
    )
    if not audit.accepted:
        print(
            json.dumps(
                {
                    role: getattr(audit, role)
                    for role in audit.__dataclass_fields__
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2

    receptor = LocalChannelGridReceptor(
        VisualGridConfig(
            source_width=1920,
            source_height=1080,
            grid_columns=8,
            grid_rows=6,
            frames_per_second=8.0,
        )
    )
    first = decode_public_visual_receptor_sequence(
        args.video,
        receptor,
        sampling_interval_ms=args.sampling_interval_ms,
        max_duration_ms=args.max_duration_ms,
    )
    repeated = decode_public_visual_receptor_sequence(
        args.video,
        receptor,
        sampling_interval_ms=args.sampling_interval_ms,
        max_duration_ms=args.max_duration_ms,
    )
    observation = observe_public_visual_world(first, repeated, receptor)
    print(
        json.dumps(
            {
                role: getattr(observation, role)
                for role in observation.__dataclass_fields__
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
