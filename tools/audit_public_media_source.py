from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_media_source_contract import (
    audit_public_media_source,
    brokindsleden_av_source_contract,
    nasa_earthrise_av_source_contract,
    street_traffic_source_contract,
)


CONTRACTS = {
    "street-traffic": street_traffic_source_contract,
    "brokindsleden-av": brokindsleden_av_source_contract,
    "nasa-earthrise-av": nasa_earthrise_av_source_contract,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit one local public test-world file without decoding it."
    )
    parser.add_argument("media", type=Path)
    parser.add_argument(
        "--source",
        choices=tuple(CONTRACTS),
        default="street-traffic",
    )
    args = parser.parse_args()
    audit = audit_public_media_source(
        args.media,
        CONTRACTS[args.source](),
    )
    print(
        json.dumps(
            {
                role: getattr(audit, role)
                for role in audit.__dataclass_fields__
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if audit.accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
