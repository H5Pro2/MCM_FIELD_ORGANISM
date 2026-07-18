from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.temporal_effect_functional_contract import (
    run_temporal_effect_functional_contract,
)


def main() -> int:
    print(
        json.dumps(
            {
                "contract": asdict(run_temporal_effect_functional_contract()),
                "ground_truth_observer_only": True,
                "field_effect_equation_selected": False,
                "runtime_changed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
