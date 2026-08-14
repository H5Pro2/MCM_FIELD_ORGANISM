from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_return_replication_compatibility import (
    audit_public_av_return_replication_compatibility,
    public_av_return_replication_compatibility_json_value,
)


def main() -> int:
    audit = audit_public_av_return_replication_compatibility()
    print(json.dumps(public_av_return_replication_compatibility_json_value(audit), indent=2, sort_keys=True))
    return 0 if audit.audit_complete and not audit.replication_run_allowed else 2


if __name__ == "__main__":
    raise SystemExit(main())
