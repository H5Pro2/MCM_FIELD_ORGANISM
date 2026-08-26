from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from audit_public_av_return_replication_repeatability_single_slot_construction_acceptance import build_construction  # noqa: E402
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_construction_acceptance import accept_public_av_return_replication_repeatability_single_slot_construction  # noqa: E402
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_binding import bind_public_av_return_replication_repeatability_single_slot_factories, public_av_return_replication_repeatability_single_slot_factory_binding_to_jsonable  # noqa: E402


def build_factory_binding(repeat_index: int):
    acceptance = accept_public_av_return_replication_repeatability_single_slot_construction(
        build_construction(repeat_index)
    )
    return bind_public_av_return_replication_repeatability_single_slot_factories(acceptance)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit one locked single-slot factory binding.")
    parser.add_argument("--repeat-index", type=int, choices=(1, 2, 3), default=1)
    args = parser.parse_args(argv)
    binding = build_factory_binding(args.repeat_index)
    print(json.dumps(
        public_av_return_replication_repeatability_single_slot_factory_binding_to_jsonable(binding),
        indent=2, sort_keys=True,
    ))
    return 0 if binding.factory_identities_unique else 1


if __name__ == "__main__":
    raise SystemExit(main())
