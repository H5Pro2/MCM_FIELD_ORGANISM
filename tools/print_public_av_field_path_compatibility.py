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
from mcm_field_organism.public_av_field_path_compatibility import (
    audit_public_av_field_path_compatibility,
    public_av_field_path_compatibility_json_value,
)
from mcm_field_organism.public_av_receptor_run import run_public_av_receptor_run
from mcm_field_organism.public_media_source_contract import (
    nasa_earthrise_av_source_contract,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Structurally audit preregistered public AV field-path arms."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--duration-seconds", type=float, default=0.5)
    args = parser.parse_args()

    auditory_config = LogSpectralConfig()
    visual_config = VisualGridConfig(320, 240, 10, 8, 29.97)
    receptor_run = run_public_av_receptor_run(
        args.path,
        nasa_earthrise_av_source_contract(),
        auditory_config,
        visual_config,
        duration_seconds=args.duration_seconds,
    )
    audit = audit_public_av_field_path_compatibility(
        receptor_run,
        auditory_config=auditory_config,
    )
    print(
        json.dumps(
            public_av_field_path_compatibility_json_value(audit),
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not audit.field_run_allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
