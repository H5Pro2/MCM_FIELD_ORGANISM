from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_two_stage_return_preflight import (
    audit_public_av_two_stage_return_preflight,
    public_av_two_stage_return_preflight_json_value,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight exactly one bounded public AV two-stage return run."
    )
    parser.add_argument(
        "media",
        nargs="?",
        type=Path,
        default=Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
    )
    args = parser.parse_args()
    preflight = audit_public_av_two_stage_return_preflight(args.media)
    print(
        json.dumps(
            public_av_two_stage_return_preflight_json_value(preflight),
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if preflight.single_bounded_run_release_granted and not preflight.field_run_started else 2


if __name__ == "__main__":
    raise SystemExit(main())
