from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.public_media_source_contract import (
    audit_public_media_source,
    street_traffic_source_contract,
)
from mcm_field_organism.public_visual_temporal_map import (
    ExternalTimeSection,
    observe_public_visual_temporal_map,
    temporal_map_json_value,
)
from mcm_field_organism.public_visual_world import decode_public_visual_receptor_sequence


LAUF_106_DIGEST = "f147109d3ac2c411328b0a514119df8fd18abd0bded487056d4a6502bc70780f"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a passive temporal field map for the Lauf 106 pixel sequence."
    )
    parser.add_argument("video", type=Path)
    parser.add_argument("--section-ms", type=int, nargs="+", default=[0, 5000, 10000, 15000, 20000, 25000, 30000, 35000])
    parser.add_argument("--output", type=Path)
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
        VisualGridConfig(1920, 1080, 8, 6, 8.0)
    )
    first = decode_public_visual_receptor_sequence(
        args.video, receptor, sampling_interval_ms=125, max_duration_ms=35_000
    )
    repeated = decode_public_visual_receptor_sequence(
        args.video, receptor, sampling_interval_ms=125, max_duration_ms=35_000
    )
    if len(first.states) != 280 or first.duration_ms != 35_000:
        raise ValueError("Lauf 106 requires exactly 280 intervals over 35000 ms")
    if first.reduced_digest() != LAUF_106_DIGEST:
        raise ValueError("input does not reproduce the documented Lauf 106 digest")
    bounds = tuple(args.section_ms)
    sections = tuple(
        ExternalTimeSection(start, end)
        for start, end in zip(bounds, bounds[1:], strict=False)
    )
    result = observe_public_visual_temporal_map(first, repeated, receptor, sections)
    document = temporal_map_json_value(result)
    document["temporal_map_digest"] = result.digest()
    encoded = json.dumps(document, indent=2, sort_keys=True, allow_nan=False)
    if args.output is None:
        print(encoded)
    else:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
