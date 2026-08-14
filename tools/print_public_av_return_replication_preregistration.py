from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_return_replication_preregistration import (
    public_av_return_replication_preregistration,
    public_av_return_replication_preregistration_json_value,
)


def main() -> int:
    plan = public_av_return_replication_preregistration()
    print(
        json.dumps(
            public_av_return_replication_preregistration_json_value(plan),
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if plan.preregistration_complete and not plan.replication_run_allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
