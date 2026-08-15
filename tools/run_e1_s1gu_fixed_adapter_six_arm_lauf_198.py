"""Prepared module entry for a separately authorized S1-GU run 198."""

from __future__ import annotations

import json
import math
import sys

from tests import (
    test_e1_formation_s1gk_fixed_adapter_real_wrapper_contract as source_fixture,
)

from mcm_field_organism.e1_formation_s1gk_fixed_adapter_real_wrapper_contract import (
    prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract,
)
from mcm_field_organism.e1_formation_s1gs_real_single_batch_transition import (
    advance_e1_formation_s1gs_real_single_batch_transition,
)
from mcm_field_organism.e1_formation_s1gt_six_arm_release_scope_contract import (
    bind_e1_formation_s1gt_six_arm_release_scope_contract,
)
from mcm_field_organism.e1_formation_s1gu_six_arm_counting_adapter import (
    run_e1_formation_s1gu_six_arm_counting_adapter,
)
from mcm_field_organism.e1_formation_s1hb_real_terminal_output import (
    build_e1_formation_s1hb_real_terminal_output,
)


RUN_NUMBER = 198
IMPORT_PREFLIGHT_ARGUMENT = "--import-preflight-only"
RUN_STATUS = "SIX_ARM_REAL_FIXED_ADAPTER_PROBE_COMPLETED_ATOMICALLY"
EXECUTION_PERMITTED = False


def _linf(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right):
        raise ValueError("Lauf 198 cannot compare vectors with different lengths")
    return max((abs(a - b) for a, b in zip(left, right, strict=True)), default=0.0)


def main() -> int:
    if EXECUTION_PERMITTED is not True:
        raise RuntimeError(
            "Lauf 198 completed atomically and cannot be executed again"
        )
    source = source_fixture.E1FormationS1GKFixedAdapterRealWrapperContractTests
    source.setUpClass()
    bridge = source.bridge
    source_contract = prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract(
        bridge,
        source.integration,
    )
    scope = bind_e1_formation_s1gt_six_arm_release_scope_contract(source_contract)

    result = run_e1_formation_s1gu_six_arm_counting_adapter(
        scope,
        source_contract,
        bridge,
        carrier_transition=advance_e1_formation_s1gs_real_single_batch_transition,
        terminal_output_factory=build_e1_formation_s1hb_real_terminal_output,
    )

    outputs = {
        (fresh.refinement_id, fresh.role_id): output
        for fresh, output in zip(
            bridge.fresh_bindings,
            result.outputs,
            strict=True,
        )
    }
    pair_metrics = []
    for refinement_id in ("r2", "r4", "r8"):
        ab = outputs[(refinement_id, "fixed-adapter-ab")]
        ba = outputs[(refinement_id, "fixed-adapter-ba")]
        pair_metrics.append(
            {
                "refinement_id": refinement_id,
                "activation_linf_ab_ba": _linf(ab.activation, ba.activation),
                "afterimage_linf_ab_ba": _linf(ab.afterimage, ba.afterimage),
            }
        )
    output_metrics = []
    for fresh, output, receipt in zip(
        bridge.fresh_bindings,
        result.outputs,
        result.receipts,
        strict=True,
    ):
        output_metrics.append(
            {
                "refinement_id": fresh.refinement_id,
                "role_id": fresh.role_id,
                "field_step_count": output.field_step_count,
                "source_support_count": output.source_support_count,
                "activation_linf": max(map(abs, output.activation), default=0.0),
                "activation_l2": math.sqrt(sum(value * value for value in output.activation)),
                "afterimage_linf": max(map(abs, output.afterimage), default=0.0),
                "afterimage_l2": math.sqrt(sum(value * value for value in output.afterimage)),
                "terminal_field_digest": output.terminal_field_digest,
                "output_digest": output.output_digest,
                "receipt_digest": receipt.receipt_digest,
            }
        )
    summary = {
        "run_number": RUN_NUMBER,
        "execution_mode": "real-in-memory-fixed-adapter-six-arm",
        "decision": result.decision,
        "result_digest": result.result_digest,
        "arm_count": result.arm_count,
        "transition_call_count": result.transition_call_count,
        "accounted_field_steps": result.accounted_field_steps,
        "actual_field_steps_executed": result.actual_field_steps_executed,
        "source_support_count": result.source_support_count,
        "transition_kind_counts": result.transition_kind_counts,
        "terminal_carrier_count": result.terminal_carrier_count,
        "terminal_output_count": result.terminal_output_count,
        "common_receipt_count": result.common_receipt_count,
        "atomic_return_complete": result.atomic_return_complete,
        "source_states_preserved": result.source_states_preserved,
        "fixed_adapters_preserved": result.fixed_adapters_preserved,
        "persistence_performed": result.persistence_performed,
        "claims_permitted": result.claims_permitted,
        "memory_decision_permitted": result.memory_decision_permitted,
        "terminal_carrier_digests": result.terminal_carrier_digests,
        "transition_digest_count": len(result.transition_digests),
        "transition_envelope_digest_count": len(
            result.transition_envelope_digests
        ),
        "pair_metrics": pair_metrics,
        "output_metrics": output_metrics,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == [IMPORT_PREFLIGHT_ARGUMENT]:
        print(
            json.dumps(
                {
                    "run_number": RUN_NUMBER,
                    "module_imported": True,
                    "s1gu_called": False,
                    "field_steps_executed": 0,
                },
                sort_keys=True,
            )
        )
    elif sys.argv[1:]:
        raise SystemExit("unsupported arguments")
    else:
        raise SystemExit(main())
