from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcm_field_organism.public_av_return_permutation_contract import (  # noqa: E402
    public_av_return_permutation_contract,
)
from mcm_field_organism.public_av_return_replication_repeatability_callable_gate_binding_acceptance import (  # noqa: E402
    accept_public_av_return_replication_repeatability_callable_gate_bindings,
)
from mcm_field_organism.public_av_return_replication_repeatability_callable_preparation import (  # noqa: E402
    prepare_public_av_return_replication_repeatability_executor_callables,
)
from mcm_field_organism.public_av_return_replication_repeatability_executor_binding import (  # noqa: E402
    bind_public_av_return_replication_repeatability_slot_executors,
)
from mcm_field_organism.public_av_return_replication_repeatability_final_execution_preflight import (  # noqa: E402
    audit_public_av_return_replication_repeatability_final_execution_preflight,
)
from mcm_field_organism.public_av_return_replication_repeatability_final_orchestration import (  # noqa: E402
    orchestrate_public_av_return_replication_repeatability_candidates,
)
from mcm_field_organism.public_av_return_replication_repeatability_gate_instantiation import (  # noqa: E402
    reserve_public_av_return_replication_repeatability_gate_instances,
)
from mcm_field_organism.public_av_return_replication_repeatability_preflight import (  # noqa: E402
    audit_public_av_return_replication_repeatability_preflight,
)
from mcm_field_organism.public_av_return_replication_repeatability_runner import (  # noqa: E402
    wire_public_av_return_replication_repeatability_runner,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_instantiation_order import (  # noqa: E402
    derive_public_av_return_replication_repeatability_single_slot_instantiation_order,
    public_av_return_replication_repeatability_single_slot_instantiation_order_to_jsonable,
)
from mcm_field_organism.public_av_return_replication_repeatability_slot_start import (  # noqa: E402
    bind_public_av_return_replication_repeatability_slots,
)
from mcm_field_organism.public_av_return_replication_repeatability_start_acceptance import (  # noqa: E402
    build_public_av_return_replication_repeatability_start_acceptance,
)
from mcm_field_organism.public_av_return_replication_runner import (  # noqa: E402
    wire_public_av_return_replication_runner,
)
from mcm_field_organism.public_media_source_contract import (  # noqa: E402
    audit_public_media_source,
    nasa_earthrise_av_source_contract,
)


MEDIA_PATH = ROOT / "sources" / "media" / "NASA Earthrise Realtime Apollo 8.mp4"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit one locked repeatability single-slot instantiation order."
    )
    parser.add_argument("--repeat-index", type=int, choices=(1, 2, 3), default=1)
    args = parser.parse_args(argv)

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
    executor_binding = bind_public_av_return_replication_repeatability_slot_executors(
        slot_start,
        base_runner,
        permutation,
    )
    start_acceptance = build_public_av_return_replication_repeatability_start_acceptance(
        preflight=preflight,
        slot_start_contract=slot_start,
        executor_binding_contract=executor_binding,
    )
    gate_contract = reserve_public_av_return_replication_repeatability_gate_instances(
        start_acceptance
    )
    callable_preparation = prepare_public_av_return_replication_repeatability_executor_callables(
        gate_contract
    )
    binding_acceptance = accept_public_av_return_replication_repeatability_callable_gate_bindings(
        callable_preparation
    )
    orchestration = orchestrate_public_av_return_replication_repeatability_candidates(
        binding_acceptance
    )
    final_preflight = audit_public_av_return_replication_repeatability_final_execution_preflight(
        orchestration,
        source_audit,
    )
    order = derive_public_av_return_replication_repeatability_single_slot_instantiation_order(
        final_preflight,
        repeat_index=args.repeat_index,
    )
    print(
        json.dumps(
            public_av_return_replication_repeatability_single_slot_instantiation_order_to_jsonable(
                order
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if order.exactly_one_slot_selected else 1


if __name__ == "__main__":
    raise SystemExit(main())
