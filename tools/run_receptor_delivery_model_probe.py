from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.receptor_delivery_model_probe import (
    run_receptor_delivery_model_probe,
)


def main() -> int:
    print(
        json.dumps(
            {
                "result": asdict(run_receptor_delivery_model_probe()),
                "selected_model": None,
                "field_advance_performed": False,
                "hold_applied_to_runtime": False,
                "modality_weight_added": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
