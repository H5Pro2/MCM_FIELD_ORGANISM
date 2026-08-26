from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from audit_public_av_return_replication_repeatability_single_slot_factory_execution_order_acceptance import build_factory_execution_order_acceptance  # noqa: E402
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_first_factory_step_preflight import preflight_public_av_return_replication_repeatability_single_slot_first_factory_step, public_av_return_replication_repeatability_single_slot_first_factory_step_preflight_to_jsonable  # noqa: E402


def build_first_factory_step_preflight(repeat_index: int):
    return preflight_public_av_return_replication_repeatability_single_slot_first_factory_step(
        build_factory_execution_order_acceptance(repeat_index)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit one locked first factory step preflight.")
    parser.add_argument("--repeat-index", type=int, choices=(1, 2, 3), default=1)
    args = parser.parse_args(argv)
    preflight = build_first_factory_step_preflight(args.repeat_index)
    print(json.dumps(
        public_av_return_replication_repeatability_single_slot_first_factory_step_preflight_to_jsonable(preflight),
        indent=2, sort_keys=True,
    ))
    return 0 if preflight.first_factory_step_preflight_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
