from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.finite_linear_temporal_projection_audit import (
    run_finite_linear_temporal_projection_audit,
)


def main() -> int:
    print(
        json.dumps(
            asdict(run_finite_linear_temporal_projection_audit()),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
