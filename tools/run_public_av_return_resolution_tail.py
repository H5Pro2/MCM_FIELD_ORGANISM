from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_return_resolution_tail import (  # noqa: E402
    execute_public_av_return_resolution_tail,
    public_av_return_resolution_tail_to_jsonable,
)
from mcm_field_organism.public_media_source_contract import nasa_earthrise_av_source_contract  # noqa: E402


MEDIA = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")
OUTPUT = Path("reports/public_av_return_resolution_tail_v1.json")


def main() -> int:
    tail = execute_public_av_return_resolution_tail(MEDIA, nasa_earthrise_av_source_contract())
    payload = public_av_return_resolution_tail_to_jsonable(tail)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=OUTPUT.parent, delete=False,
        prefix=f"{OUTPUT.name}.", suffix=".tmp",
    ) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temp_path = Path(handle.name)
    temp_path.replace(OUTPUT)
    print(OUTPUT.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
