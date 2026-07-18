from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.field_input_capacity_audit import (
    run_field_input_capacity_audit,
)


def main() -> int:
    print(
        json.dumps(
            {
                "audit": asdict(run_field_input_capacity_audit()),
                "runtime_changed": False,
                "batch_reduction_selected": False,
                "field_transition_performed": False,
                "organism_memory_added": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
