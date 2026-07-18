from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.snapshot_change_baseline_probe import (
    run_snapshot_change_baseline_probe,
)


def main() -> int:
    print(
        json.dumps(
            {
                "result": asdict(run_snapshot_change_baseline_probe()),
                "selected_change_measure": None,
                "previous_snapshot_buffer_added": False,
                "field_advance_performed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
