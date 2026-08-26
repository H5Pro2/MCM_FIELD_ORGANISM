from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_return_permutation_contract import (
    public_av_return_permutation_contract,
    public_av_return_permutation_contract_json_value,
)


def main() -> int:
    contract = public_av_return_permutation_contract()
    print(
        json.dumps(
            public_av_return_permutation_contract_json_value(contract),
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if contract.fully_specified and not contract.replication_run_allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
