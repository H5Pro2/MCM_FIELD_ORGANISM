from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_container_preflight import (
    run_public_av_container_preflight,
)
from mcm_field_organism.public_media_source_contract import (
    brokindsleden_av_source_contract,
    nasa_earthrise_av_source_contract,
)


CONTRACTS = {
    "brokindsleden-av": brokindsleden_av_source_contract,
    "nasa-earthrise-av": nasa_earthrise_av_source_contract,
}


def _json_value(value):
    if hasattr(value, "__dataclass_fields__"):
        return {
            role: _json_value(getattr(value, role))
            for role in value.__dataclass_fields__
        }
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Preflight one public AV container candidate without decoding it "
            "or releasing any receptor path."
        )
    )
    parser.add_argument("media", type=Path)
    parser.add_argument(
        "--source",
        choices=tuple(CONTRACTS),
        default="brokindsleden-av",
    )
    args = parser.parse_args()
    result = run_public_av_container_preflight(
        args.media,
        CONTRACTS[args.source](),
    )
    print(json.dumps(_json_value(result), indent=2, sort_keys=True))
    return 0 if result.adapter_implementation_allowed else 2


if __name__ == "__main__":
    raise SystemExit(main())
