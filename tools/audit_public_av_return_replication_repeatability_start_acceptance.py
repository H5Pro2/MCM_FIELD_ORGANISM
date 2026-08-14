from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_return_permutation_contract import (  # noqa: E402
    public_av_return_permutation_contract,
)
from mcm_field_organism.public_av_return_replication_repeatability_executor_binding import (  # noqa: E402
    bind_public_av_return_replication_repeatability_slot_executors,
)
from mcm_field_organism.public_av_return_replication_repeatability_preflight import (  # noqa: E402
    audit_public_av_return_replication_repeatability_preflight,
)
from mcm_field_organism.public_av_return_replication_repeatability_runner import (  # noqa: E402
    wire_public_av_return_replication_repeatability_runner,
)
from mcm_field_organism.public_av_return_replication_repeatability_slot_start import (  # noqa: E402
    bind_public_av_return_replication_repeatability_slots,
)
from mcm_field_organism.public_av_return_replication_repeatability_start_acceptance import (  # noqa: E402
    build_public_av_return_replication_repeatability_start_acceptance,
    public_av_return_replication_repeatability_start_acceptance_to_jsonable,
)
from mcm_field_organism.public_av_return_replication_runner import (  # noqa: E402
    wire_public_av_return_replication_runner,
)
from mcm_field_organism.public_media_source_contract import (  # noqa: E402
    audit_public_media_source,
    nasa_earthrise_av_source_contract,
)


MEDIA_PATH = ROOT / "sources" / "media" / "NASA Earthrise Realtime Apollo 8.mp4"


def main() -> int:
    source_contract = nasa_earthrise_av_source_contract()
    source_audit = audit_public_media_source(MEDIA_PATH, source_contract)
    permutation = public_av_return_permutation_contract()
    base_runner = wire_public_av_return_replication_runner(
        permutation_contract=permutation
    )
    repeatability_runner = wire_public_av_return_replication_repeatability_runner(
        base_wiring=base_runner
    )
    preflight = audit_public_av_return_replication_repeatability_preflight(
        MEDIA_PATH,
        source_contract,
        source_audit=source_audit,
        repeatability_wiring=repeatability_runner,
        base_wiring=base_runner,
        permutation_contract=permutation,
    )
    slot_start = bind_public_av_return_replication_repeatability_slots(
        repeatability_runner,
        preflight,
    )
    executor_binding = (
        bind_public_av_return_replication_repeatability_slot_executors(
            slot_start,
            base_runner,
            permutation,
        )
    )
    acceptance = build_public_av_return_replication_repeatability_start_acceptance(
        preflight=preflight,
        slot_start_contract=slot_start,
        executor_binding_contract=executor_binding,
    )
    print(
        json.dumps(
            public_av_return_replication_repeatability_start_acceptance_to_jsonable(
                acceptance
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if acceptance.start_acceptance_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
