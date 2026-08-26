from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from audit_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight import build_callable_factory_call_execution_preflight  # noqa: E402
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight_acceptance import accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight, public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight_acceptance_to_jsonable  # noqa: E402


def build_callable_factory_call_execution_preflight_acceptance(repeat_index: int):
    return accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight(
        build_callable_factory_call_execution_preflight(repeat_index)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit one locked callable factory call execution preflight acceptance.")
    parser.add_argument("--repeat-index", type=int, choices=(1, 2, 3), default=1)
    args = parser.parse_args(argv)
    acceptance = build_callable_factory_call_execution_preflight_acceptance(args.repeat_index)
    print(json.dumps(public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight_acceptance_to_jsonable(acceptance), indent=2, sort_keys=True))
    return 0 if acceptance.call_execution_preflight_acceptance_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
