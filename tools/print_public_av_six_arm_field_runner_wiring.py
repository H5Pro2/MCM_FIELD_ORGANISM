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
)
from mcm_field_organism.public_av_receptor_run import run_public_av_receptor_run
from mcm_field_organism.public_av_six_arm_field_runner import (
    public_av_six_arm_field_runner_json_value,
    wire_public_av_six_arm_field_runner,
)
from mcm_field_organism.public_media_source_contract import (
    nasa_earthrise_av_source_contract,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print non-executable six-arm public AV field-runner wiring."
    )
    parser.add_argument("media", type=Path)
    parser.add_argument("--duration-seconds", type=float, default=0.5)
    args = parser.parse_args()

    auditory_config = LogSpectralConfig()
    visual_config = VisualGridConfig(320, 240, 10, 8, 29.97)
    receptor_run = run_public_av_receptor_run(
        args.media,
        nasa_earthrise_av_source_contract(),
        auditory_config,
        visual_config,
        duration_seconds=args.duration_seconds,
    )
    compatibility = audit_public_av_field_path_compatibility(
        receptor_run,
        auditory_config=auditory_config,
    )
    wiring = wire_public_av_six_arm_field_runner(compatibility)
    print(
        json.dumps(
            public_av_six_arm_field_runner_json_value(wiring),
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if wiring.wiring_complete and not wiring.executable else 1


if __name__ == "__main__":
    raise SystemExit(main())
