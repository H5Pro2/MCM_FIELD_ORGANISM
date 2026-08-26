"""Run the non-canonical S1-EC13 full formation exactly once."""

from __future__ import annotations

import json
from pathlib import Path

from mcm_field_organism.e1_confirmation_descriptor_input_resolver import (
    prepare_e1_confirmation_descriptor_bundle_from_run_contract,
)
from mcm_field_organism.e1_confirmation_full_formation_lifecycle import (
    execute_prepared_full_formation_lifecycle,
)
from mcm_field_organism.e1_confirmation_research_corridor import (
    build_e1_confirmation_research_corridor,
    prepare_e1_confirmation_synthetic_run_contract,
)


WORKSPACE = Path(__file__).resolve().parents[1]
UPSTREAM = WORKSPACE / "reports" / "e1_refined_formation_transfer_s1ea_once_v1.json"
RUN_DIRECTORY = WORKSPACE / "synthetic_runs" / "s1ec13_full_formation_once_v1"


def main() -> int:
    RUN_DIRECTORY.mkdir(parents=True, exist_ok=True)
    descriptor = build_e1_confirmation_research_corridor(UPSTREAM)
    run_contract = prepare_e1_confirmation_synthetic_run_contract(
        descriptor, RUN_DIRECTORY
    )
    bundle = prepare_e1_confirmation_descriptor_bundle_from_run_contract(
        run_contract, UPSTREAM
    )
    result = execute_prepared_full_formation_lifecycle(bundle)
    print(
        json.dumps(
            {
                "decision": "FULL_PREPARED_FORMATION_EXECUTED_TEMPORARILY",
                "preflight_digest": result.preflight.result_digest,
                "formation_digest": result.formation.result_digest,
                "report_path": result.receipt.report_path,
                "report_sha256": result.receipt.report_sha256,
                "history_state_distances": (
                    result.formation.history_state_distances
                ),
                "r2_r4_state_residual": (
                    result.formation.r2_r4_state_residual
                ),
                "r4_r8_state_residual": (
                    result.formation.r4_r8_state_residual
                ),
                "convergence_nonincreasing": (
                    result.formation.convergence_nonincreasing
                ),
                "claims_permitted": False,
            },
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
