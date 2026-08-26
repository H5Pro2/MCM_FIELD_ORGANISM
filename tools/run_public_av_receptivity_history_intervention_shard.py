from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_local_adaptive_receptivity_coupling_scheme_audit import (  # noqa: E402
    COUPLING_AUDIT_SCHEMES,
)
from mcm_field_organism.public_av_receptivity_history_intervention_audit import (  # noqa: E402
    HISTORY_INTERVENTION_ALPHA_AXIS,
    execute_public_av_receptivity_history_intervention_shard,
)
from mcm_field_organism.public_media_source_contract import (  # noqa: E402
    nasa_earthrise_av_source_contract,
)


MEDIA = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")
OUTPUT_DIRECTORY = Path("reports/shards")


def _output_path(alpha: float, scheme: str, start_tick: int = 0) -> Path:
    if float(alpha) not in HISTORY_INTERVENTION_ALPHA_AXIS:
        raise ValueError("alpha shard is not preregistered")
    if scheme not in COUPLING_AUDIT_SCHEMES:
        raise ValueError("scheme shard is not preregistered")
    alpha_slug = f"{float(alpha):.2f}".replace(".", "_")
    interval_slug = (
        ""
        if start_tick == 0
        else f"_source_ticks_{start_tick}_{start_tick + 500_000_000}"
    )
    return OUTPUT_DIRECTORY / (
        "public_av_receptivity_history_intervention_"
        f"alpha_{alpha_slug}_scheme_{scheme}{interval_slug}_v1.json"
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--alpha", required=True, type=float,
        choices=HISTORY_INTERVENTION_ALPHA_AXIS,
    )
    parser.add_argument(
        "--scheme", required=True, choices=COUPLING_AUDIT_SCHEMES
    )
    parser.add_argument("--start-tick", type=int, default=0)
    parser.add_argument("--expected-event-timeline-digest")
    return parser


def main(argv=None) -> int:
    args = _parser().parse_args(argv)
    if args.start_tick != 0 and not args.expected_event_timeline_digest:
        raise ValueError(
            "a disjoint source interval requires an expected event timeline digest"
        )
    payload = execute_public_av_receptivity_history_intervention_shard(
        MEDIA,
        nasa_earthrise_av_source_contract(),
        args.alpha,
        args.scheme,
        start_tick=args.start_tick,
        expected_event_timeline_digest=args.expected_event_timeline_digest,
    )
    output = _output_path(args.alpha, args.scheme, args.start_tick)
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
