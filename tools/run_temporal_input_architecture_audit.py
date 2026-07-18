from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.temporal_input_architecture_audit import (
    run_temporal_input_architecture_audit,
)


def main() -> int:
    print(
        json.dumps(
            {
                "audit": asdict(run_temporal_input_architecture_audit()),
                "runtime_changed": False,
                "temporal_reduction_selected": False,
                "asynchronous_local_state_added": False,
                "runtime_candidate_released": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
