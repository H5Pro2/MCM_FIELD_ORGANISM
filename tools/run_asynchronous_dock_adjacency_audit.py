from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.asynchronous_dock_adjacency_audit import (
    run_asynchronous_dock_adjacency_audit,
)


def main() -> int:
    result = run_asynchronous_dock_adjacency_audit()
    print(
        json.dumps(
            {
                "audit": asdict(result),
                "rate_skewed_adjacent_pair_fractions": {
                    modality_id: result.rate_skewed.measure(
                        modality_id
                    ).globally_adjacent_pair_fraction
                    for modality_id in ("auditory", "visual")
                },
                "field_advance_performed": False,
                "contact_persistence_added": False,
                "completion_groups_used_as_field_ticks": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
