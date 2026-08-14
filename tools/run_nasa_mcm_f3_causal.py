from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.mcm_f3_public_av_run import (
    execute_nasa_mcm_f3_causal_run,
    mcm_f3_public_av_run_json_value,
)
from mcm_field_organism.public_media_source_contract import (
    nasa_earthrise_av_source_contract,
)


def main() -> int:
    output = ROOT / "reports" / "mcm_f3_nasa_causal_lauf_188.json"
    if output.exists():
        raise FileExistsError(f"one-shot result already exists: {output}")
    result = execute_nasa_mcm_f3_causal_run(
        ROOT / "sources" / "media" / "NASA Earthrise Realtime Apollo 8.mp4",
        nasa_earthrise_av_source_contract(),
    )
    payload = json.dumps(
        mcm_f3_public_av_run_json_value(result),
        indent=2,
        sort_keys=True,
        allow_nan=False,
    )
    output.write_text(payload + "\n", encoding="ascii")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
