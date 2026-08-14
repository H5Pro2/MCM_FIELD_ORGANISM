from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.finite_video_path import VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig
from mcm_field_organism.public_av_receptor_preflight import (
    run_public_av_receptor_preflight,
)
from mcm_field_organism.public_media_source_contract import (
    nasa_earthrise_av_source_contract,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit public AV compatibility without running receptors or fields."
    )
    parser.add_argument("media", type=Path)
    parser.add_argument("--duration", type=float, default=0.5)
    parser.add_argument("--start-tick", type=int, default=0)
    args = parser.parse_args()
    result = run_public_av_receptor_preflight(
        args.media,
        nasa_earthrise_av_source_contract(),
        LogSpectralConfig(),
        VisualGridConfig(320, 240, 10, 8, 29.97),
        duration_seconds=args.duration,
        start_tick=args.start_tick,
    )
    print(
        json.dumps(
            {role: getattr(result, role) for role in result.__dataclass_fields__},
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result.receptor_prerequisites_met else 2


if __name__ == "__main__":
    raise SystemExit(main())
