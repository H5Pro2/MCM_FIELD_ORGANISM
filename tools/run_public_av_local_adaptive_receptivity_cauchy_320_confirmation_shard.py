from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_local_adaptive_receptivity_cauchy_320_confirmation import (  # noqa: E402
    CONFIRMATION_ALPHA_AXIS,
    execute_public_av_local_adaptive_receptivity_cauchy_320_confirmation_shard,
)
from mcm_field_organism.public_media_source_contract import (  # noqa: E402
    nasa_earthrise_av_source_contract,
)

MEDIA = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")
OUTPUT_DIRECTORY = Path("reports/shards")


def _alpha_slug(alpha: float) -> str:
    if float(alpha) not in CONFIRMATION_ALPHA_AXIS:
        raise ValueError("alpha shard must belong to the confirmation axis")
    return f"{float(alpha):.2f}".replace(".", "_")


def _output_path(alpha: float) -> Path:
    return OUTPUT_DIRECTORY / (
        "public_av_local_adaptive_receptivity_cauchy_320_confirmation_"
        f"alpha_{_alpha_slug(alpha)}_v1.json"
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", required=True, type=float, choices=CONFIRMATION_ALPHA_AXIS)
    return parser


def main(argv=None) -> int:
    args = _parser().parse_args(argv)
    payload = execute_public_av_local_adaptive_receptivity_cauchy_320_confirmation_shard(
        MEDIA, nasa_earthrise_av_source_contract(), args.alpha
    )
    output = _output_path(args.alpha)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=output.parent, delete=False,
            prefix=f"{output.name}.", suffix=".tmp",
        ) as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            temporary = Path(handle.name)
        temporary.replace(output)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    print(output.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
