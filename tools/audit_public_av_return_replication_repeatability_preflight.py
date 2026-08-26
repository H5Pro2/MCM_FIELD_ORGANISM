from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_return_replication_repeatability_preflight import (
    audit_public_av_return_replication_repeatability_preflight,
    public_av_return_replication_repeatability_preflight_json_value,
)


MEDIA = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")


def main() -> int:
    preflight = audit_public_av_return_replication_repeatability_preflight(MEDIA)
    print(json.dumps(public_av_return_replication_repeatability_preflight_json_value(preflight), indent=2, sort_keys=True))
    return 0 if preflight.repeatability_preflight_complete and not preflight.repeatability_run_allowed else 2


if __name__ == "__main__":
    raise SystemExit(main())
