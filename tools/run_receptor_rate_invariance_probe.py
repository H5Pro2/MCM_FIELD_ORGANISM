from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism import run_receptor_rate_invariance_probe


def main() -> int:
    result = run_receptor_rate_invariance_probe()
    payload = {
        "tick_seconds": result.tick_seconds,
        "dense_segment_count": result.dense_segment_count,
        "sparse_segment_count": result.sparse_segment_count,
        "observations": [
            {
                "tau_seconds": observation.tau_seconds,
                "physical_time_dense_end": observation.physical_time_dense_end,
                "physical_time_sparse_end": observation.physical_time_sparse_end,
                "physical_time_difference": observation.physical_time_difference,
                "event_count_dense_end": observation.event_count_dense_end,
                "event_count_sparse_end": observation.event_count_sparse_end,
                "event_count_difference": observation.event_count_difference,
            }
            for observation in result.observations
        ],
        "physical_time_baseline_is_rate_invariant": (
            result.physical_time_baseline_is_rate_invariant
        ),
        "event_count_baseline_is_rate_invariant": (
            result.event_count_baseline_is_rate_invariant
        ),
        "omitted_contact_difference": result.omitted_contact_difference,
        "runtime_changed": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
