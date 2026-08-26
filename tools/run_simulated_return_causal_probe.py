from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.simulated_return_causal_probe import (
    run_simulated_return_causal_probe,
    run_simulated_two_step_causal_probe,
)


def main() -> int:
    results = {
        "single_step": asdict(run_simulated_return_causal_probe()),
        "two_step": asdict(run_simulated_two_step_causal_probe()),
    }
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
