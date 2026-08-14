from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from audit_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight import build_first_factory_step_preflight  # noqa: E402
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_first_factory_step_acceptance import accept_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight, public_av_return_replication_repeatability_single_slot_first_factory_step_acceptance_to_jsonable  # noqa: E402


def build_first_factory_step_acceptance(repeat_index: int):
    return accept_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight(
        build_first_factory_step_preflight(repeat_index)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit one locked first factory step acceptance.")
    parser.add_argument("--repeat-index", type=int, choices=(1, 2, 3), default=1)
    args = parser.parse_args(argv)
    acceptance = build_first_factory_step_acceptance(args.repeat_index)
    print(json.dumps(
        public_av_return_replication_repeatability_single_slot_first_factory_step_acceptance_to_jsonable(acceptance),
        indent=2, sort_keys=True,
    ))
    return 0 if acceptance.first_factory_step_acceptance_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
