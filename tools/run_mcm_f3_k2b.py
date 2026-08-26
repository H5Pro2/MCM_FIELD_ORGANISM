from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.mcm_f3_k2b_run import (
    execute_mcm_f3_k2b_run,
    mcm_f3_k2b_run_json_value,
)


def main() -> int:
    output = ROOT / "reports" / "mcm_f3_k2b_lauf_194.json"
    if output.exists():
        raise FileExistsError(f"one-shot result already exists: {output}")
    result = execute_mcm_f3_k2b_run()
    payload = json.dumps(
        mcm_f3_k2b_run_json_value(result),
        indent=2,
        sort_keys=True,
        allow_nan=False,
    )
    output.write_text(payload + "\n", encoding="ascii")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
