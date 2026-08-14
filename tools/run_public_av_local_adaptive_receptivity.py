from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_local_adaptive_receptivity import (  # noqa: E402
    execute_public_av_local_adaptive_receptivity,
)
from mcm_field_organism.public_media_source_contract import (  # noqa: E402
    nasa_earthrise_av_source_contract,
)

MEDIA = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")
OUTPUT = Path("reports/public_av_local_adaptive_receptivity_v1.json")


def main() -> int:
    payload = execute_public_av_local_adaptive_receptivity(
        MEDIA, nasa_earthrise_av_source_contract()
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=OUTPUT.parent, delete=False,
        prefix=f"{OUTPUT.name}.", suffix=".tmp",
    ) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(OUTPUT)
    print(OUTPUT.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
