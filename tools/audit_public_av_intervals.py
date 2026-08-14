from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_interval_audit import (
    public_av_interval_audit_json_value,
    run_public_av_interval_audit,
)
from mcm_field_organism.public_media_source_contract import (
    nasa_earthrise_av_source_contract,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit public AV raw-source intervals without feeding receptors or fields."
        )
    )
    parser.add_argument("media", type=Path)
    parser.add_argument("--duration-seconds", type=float, default=0.5)
    parser.add_argument("--start-tick", type=int, default=0)
    args = parser.parse_args()
    result = run_public_av_interval_audit(
        args.media,
        nasa_earthrise_av_source_contract(),
        duration_seconds=args.duration_seconds,
        start_tick=args.start_tick,
    )
    print(
        json.dumps(
            public_av_interval_audit_json_value(result),
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result.repeatable else 2


if __name__ == "__main__":
    raise SystemExit(main())
