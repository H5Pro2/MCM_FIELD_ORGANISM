from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_field_preregistration import (
    public_av_passive_field_preregistration,
)


def _value(value):
    if hasattr(value, "__dataclass_fields__"):
        return {role: _value(getattr(value, role)) for role in value.__dataclass_fields__}
    if isinstance(value, tuple):
        return [_value(item) for item in value]
    return value


def main() -> int:
    print(json.dumps(_value(public_av_passive_field_preregistration()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
