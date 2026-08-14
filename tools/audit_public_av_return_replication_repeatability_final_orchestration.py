from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from audit_public_av_return_replication_repeatability_callable_gate_binding_acceptance import (  # noqa: E402
    MEDIA_PATH,
)
from mcm_field_organism.public_av_return_permutation_contract import public_av_return_permutation_contract  # noqa: E402
from mcm_field_organism.public_av_return_replication_repeatability_callable_gate_binding_acceptance import accept_public_av_return_replication_repeatability_callable_gate_bindings  # noqa: E402
from mcm_field_organism.public_av_return_replication_repeatability_callable_preparation import prepare_public_av_return_replication_repeatability_executor_callables  # noqa: E402
from mcm_field_organism.public_av_return_replication_repeatability_executor_binding import bind_public_av_return_replication_repeatability_slot_executors  # noqa: E402
from mcm_field_organism.public_av_return_replication_repeatability_final_orchestration import orchestrate_public_av_return_replication_repeatability_candidates, public_av_return_replication_repeatability_final_orchestration_to_jsonable  # noqa: E402
from mcm_field_organism.public_av_return_replication_repeatability_gate_instantiation import reserve_public_av_return_replication_repeatability_gate_instances  # noqa: E402
from mcm_field_organism.public_av_return_replication_repeatability_preflight import audit_public_av_return_replication_repeatability_preflight  # noqa: E402
from mcm_field_organism.public_av_return_replication_repeatability_runner import wire_public_av_return_replication_repeatability_runner  # noqa: E402
from mcm_field_organism.public_av_return_replication_repeatability_slot_start import bind_public_av_return_replication_repeatability_slots  # noqa: E402
from mcm_field_organism.public_av_return_replication_repeatability_start_acceptance import build_public_av_return_replication_repeatability_start_acceptance  # noqa: E402
from mcm_field_organism.public_av_return_replication_runner import wire_public_av_return_replication_runner  # noqa: E402
from mcm_field_organism.public_media_source_contract import audit_public_media_source, nasa_earthrise_av_source_contract  # noqa: E402


def main() -> int:
    source = nasa_earthrise_av_source_contract()
    source_audit = audit_public_media_source(MEDIA_PATH, source)
    permutation = public_av_return_permutation_contract()
    base = wire_public_av_return_replication_runner(permutation_contract=permutation)
    repeatability = wire_public_av_return_replication_repeatability_runner(base_wiring=base)
    preflight = audit_public_av_return_replication_repeatability_preflight(
        MEDIA_PATH, source, source_audit=source_audit, repeatability_wiring=repeatability,
        base_wiring=base, permutation_contract=permutation,
    )
    slot_start = bind_public_av_return_replication_repeatability_slots(repeatability, preflight)
    executors = bind_public_av_return_replication_repeatability_slot_executors(slot_start, base, permutation)
    start = build_public_av_return_replication_repeatability_start_acceptance(
        preflight=preflight, slot_start_contract=slot_start, executor_binding_contract=executors
    )
    gates = reserve_public_av_return_replication_repeatability_gate_instances(start)
    callables = prepare_public_av_return_replication_repeatability_executor_callables(gates)
    binding = accept_public_av_return_replication_repeatability_callable_gate_bindings(callables)
    contract = orchestrate_public_av_return_replication_repeatability_candidates(binding)
    print(json.dumps(
        public_av_return_replication_repeatability_final_orchestration_to_jsonable(contract),
        indent=2, sort_keys=True,
    ))
    return 0 if contract.final_orchestration_contract_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
