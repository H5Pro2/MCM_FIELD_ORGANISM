from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.local_field_effect_admissibility_contract import (
    reference_local_field_effect_admissibility_contract,
)


def main() -> int:
    contract = reference_local_field_effect_admissibility_contract()
    print(
        json.dumps(
            {
                "contract": contract.canonical_payload(),
                "digest": contract.digest(),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
