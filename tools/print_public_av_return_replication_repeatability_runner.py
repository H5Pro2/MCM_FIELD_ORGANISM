from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_return_replication_repeatability_runner import (
    public_av_return_replication_repeatability_runner_json_value,
    wire_public_av_return_replication_repeatability_runner,
)


def main() -> int:
    wiring = wire_public_av_return_replication_repeatability_runner()
    print(json.dumps(public_av_return_replication_repeatability_runner_json_value(wiring), indent=2, sort_keys=True))
    return 0 if wiring.all_repeat_slots_structurally_wired and not wiring.repeatability_run_allowed else 2


if __name__ == "__main__":
    raise SystemExit(main())
