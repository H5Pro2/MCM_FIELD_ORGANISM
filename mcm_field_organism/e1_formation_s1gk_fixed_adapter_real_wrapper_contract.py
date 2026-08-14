"""S1-GK non-executing contract for the six-arm fixed-adapter wrapper."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture import (
    S1_GF_REFINEMENT_BATCH_COUNTS,
    S1_GF_ROLE_ORDER,
    S1_GF_TOTAL_BATCH_COUNT,
)
from .e1_formation_s1gh_fresh_field_bridge import (
    E1FormationS1GHFreshFieldBinding,
    E1FormationS1GHFreshFieldBridgeResult,
)
from .e1_formation_s1gi_fixed_adapter_output_converter import (
    E1FormationS1GIFixedAdapterCommonProbeReceipt,
    E1FormationS1GIFixedAdapterRealOutput,
)
from .e1_formation_s1gj_synthetic_fixed_adapter_receipt_integration import (
    E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationResult,
    S1_GJ_TOTAL_SUPPORT_COUNT,
)
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
)
from .e1_refined_formation_runner import _digest
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class E1FormationS1GKFixedAdapterRealWrapperContractError(ValueError):
    """Raised when the S1-GK contract changes or permits execution."""


S1_GK_CONTRACT_ID = "e1.fixed-adapter-real-wrapper-contract.s1gk.v1"
S1_GK_WRAPPER_INPUTS = (
    "six-exact-s1gh-fresh-field-bindings",
    "six-exact-s1gd-invocations",
    "six-exact-s1gc-probe-plans",
    "six-source-states-for-attestation-only",
    "six-fixed-adapters-for-kernel-use",
    "neutral-substrate-config-strength-1.0",
    "fast-afterimage-config-leak-rate-0.5",
    "no-additional-dissipation-config",
)
S1_GK_LOOP_SEQUENCE = (
    "validate-all-six-input-groups-before-first-kernel-call",
    "iterate-six-roles-in-r2-r4-r8-ab-ba-order",
    "iterate-each-probe-batch-once-in-order",
    "map-batch-to-current-fresh-field-docks",
    "project-complete-local-neuron-inputs",
    "construct-empty-boundary-distribution-for-batch-time",
    "advance-current-field-with-exact-fixed-adapter",
    "never-pass-source-state-to-field-kernel",
    "snapshot-only-after-complete-arm",
    "convert-output-to-common-receipt",
    "return-six-results-only-after-complete-validation",
)
S1_GK_ABORT_CONDITIONS = (
    "source-bridge-or-synthetic-schema-digest-mismatch",
    "role-order-binding-or-object-identity-mismatch",
    "fresh-field-initial-digest-or-neuron-order-mismatch",
    "source-state-or-fixed-adapter-digest-mismatch",
    "probe-batch-index-time-or-count-mismatch",
    "dock-mapping-or-neuron-projection-error",
    "field-kernel-exception-or-nonfinite-output",
    "field-step-or-support-accounting-mismatch",
    "source-state-or-fixed-adapter-mutation",
    "partial-output-receipt-or-cross-binding",
)
S1_GK_ABORT_POLICY = (
    "discard-all-six-fields-outputs-and-receipts",
    "return-no-partial-aggregate",
    "no-retry",
    "no-posthoc-parameter-change",
    "no-persistence",
)
S1_GK_RETURN_COMPONENTS = (
    "six-typed-fixed-adapter-outputs",
    "six-common-probe-receipts",
    "six-terminal-field-digests",
    "ordered-raw-activation-vectors",
    "ordered-raw-afterimage-vectors",
    "step-and-support-accounting",
    "source-state-and-fixed-adapter-attestations",
)
S1_GK_CHECK_NAMES = (
    "s1gh-and-s1gj-digest-chain-exact",
    "six-input-and-six-output-roles-match-in-order",
    "positive-step-and-support-budgets-exact",
    "fresh-binding-output-and-receipt-types-complete",
    "batch-dock-neuron-and-fixed-kernel-signatures-compatible",
    "fixed-kernel-excludes-live-state",
    "atomic-abort-policy-closes-partial-return-retry-and-persistence",
    "contract-builder-calls-no-field-kernel-or-writer",
)


def _called_names(source: str) -> frozenset[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return frozenset(names)


@dataclass(frozen=True, slots=True)
class E1FormationS1GKFixedAdapterRealWrapperContract:
    contract_id: str
    source_s1gh_result_digest: str
    source_s1gj_result_digest: str
    role_order: tuple[tuple[str, str], ...]
    refinement_step_counts: tuple[tuple[str, int], ...]
    wrapper_inputs: tuple[str, ...]
    loop_sequence: tuple[str, ...]
    abort_conditions: tuple[str, ...]
    abort_policy: tuple[str, ...]
    return_components: tuple[str, ...]
    output_fields: tuple[str, ...]
    receipt_fields: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    wrapper_arm_count: int
    planned_kernel_call_count: int
    planned_field_step_count: int
    planned_source_support_count: int
    atomic_six_return_required: bool
    live_state_permitted_in_fixed_kernel: bool
    real_wrapper_implementation_permitted: bool
    owner_authorization_present: bool
    execution_permitted: bool
    field_execution_performed: bool
    retry_permitted: bool
    posthoc_parameter_change_permitted: bool
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    reason: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if (
            self.contract_id != S1_GK_CONTRACT_ID
            or any(
                len(value) != 64
                for value in (
                    self.source_s1gh_result_digest,
                    self.source_s1gj_result_digest,
                )
            )
            or self.role_order != S1_GF_ROLE_ORDER
            or self.refinement_step_counts != S1_GF_REFINEMENT_BATCH_COUNTS
            or self.wrapper_inputs != S1_GK_WRAPPER_INPUTS
            or self.loop_sequence != S1_GK_LOOP_SEQUENCE
            or self.abort_conditions != S1_GK_ABORT_CONDITIONS
            or self.abort_policy != S1_GK_ABORT_POLICY
            or self.return_components != S1_GK_RETURN_COMPONENTS
            or self.output_fields
            != tuple(E1FormationS1GIFixedAdapterRealOutput.__dataclass_fields__)
            or self.receipt_fields
            != tuple(E1FormationS1GIFixedAdapterCommonProbeReceipt.__dataclass_fields__)
            or tuple(name for name, _ in self.checks) != S1_GK_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or self.wrapper_arm_count != 6
            or self.planned_kernel_call_count != S1_GF_TOTAL_BATCH_COUNT
            or self.planned_field_step_count != S1_GF_TOTAL_BATCH_COUNT
            or self.planned_source_support_count != S1_GJ_TOTAL_SUPPORT_COUNT
            or self.atomic_six_return_required is not True
            or self.real_wrapper_implementation_permitted is not True
            or any(
                value is not False
                for value in (
                    self.live_state_permitted_in_fixed_kernel,
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.field_execution_performed,
                    self.retry_permitted,
                    self.posthoc_parameter_change_permitted,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "FIXED_ADAPTER_REAL_WRAPPER_CONTRACT_BOUND_IMPLEMENTATION_ALLOWED_EXECUTION_CLOSED"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1GKFixedAdapterRealWrapperContractError(
                "S1-GK contract changed or opened real execution"
            )


def prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract(
    bridge: E1FormationS1GHFreshFieldBridgeResult,
    integration: E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationResult,
) -> E1FormationS1GKFixedAdapterRealWrapperContract:
    """Bind the real wrapper boundary without invoking any runtime function."""

    if not isinstance(bridge, E1FormationS1GHFreshFieldBridgeResult) or not isinstance(
        integration, E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationResult
    ):
        raise E1FormationS1GKFixedAdapterRealWrapperContractError(
            "S1-GK requires typed S1-GH and S1-GJ sources"
        )
    bridge.__post_init__()
    integration.__post_init__()
    bridge_roles = tuple(
        (item.refinement_id, item.role_id) for item in bridge.fresh_bindings
    )
    output_roles = tuple(
        (item.refinement_id, item.role_id) for item in integration.receipts
    )
    mapper_parameters = tuple(
        inspect.signature(map_proposal_batch_to_transient_docks).parameters
    )
    projector_parameters = tuple(
        inspect.signature(project_transient_docks_to_neuron_inputs).parameters
    )
    kernel_parameters = tuple(
        inspect.signature(
            advance_fixed_e1_adapter_fast_shared_field_transient
        ).parameters
    )
    builder_source = inspect.getsource(
        prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract
    )
    forbidden_calls = {
        "map_proposal_batch_to_transient_docks",
        "project_transient_docks_to_neuron_inputs",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "open",
        "write_text",
        "write_bytes",
    }
    expected_kernel_parameters = (
        "field",
        "fixed_adapter",
        "distribution",
        "transient_inputs",
        "substrate_config",
        "afterimage_config",
        "dissipation_config",
    )
    checks = (
        (
            S1_GK_CHECK_NAMES[0],
            integration.source_s1gh_result_digest == bridge.result_digest,
        ),
        (
            S1_GK_CHECK_NAMES[1],
            bridge_roles == output_roles == S1_GF_ROLE_ORDER
            and len(bridge.fresh_bindings) == len(integration.outputs) == 6,
        ),
        (
            S1_GK_CHECK_NAMES[2],
            integration.refinement_step_counts == S1_GF_REFINEMENT_BATCH_COUNTS
            and integration.planned_field_steps == S1_GF_TOTAL_BATCH_COUNT
            and integration.total_source_support_count == S1_GJ_TOTAL_SUPPORT_COUNT
            and integration.actual_field_steps_executed == 0,
        ),
        (
            S1_GK_CHECK_NAMES[3],
            inspect.isclass(E1FormationS1GHFreshFieldBinding)
            and len(E1FormationS1GIFixedAdapterRealOutput.__dataclass_fields__) == 18
            and len(E1FormationS1GIFixedAdapterCommonProbeReceipt.__dataclass_fields__)
            == 22,
        ),
        (
            S1_GK_CHECK_NAMES[4],
            mapper_parameters == ("batch", "docks")
            and projector_parameters == ("trajectory", "docks")
            and kernel_parameters == expected_kernel_parameters,
        ),
        (
            S1_GK_CHECK_NAMES[5],
            "state" not in kernel_parameters
            and "frozen_e1_state" not in kernel_parameters,
        ),
        (
            S1_GK_CHECK_NAMES[6],
            all(
                item in S1_GK_ABORT_POLICY
                for item in (
                    "discard-all-six-fields-outputs-and-receipts",
                    "return-no-partial-aggregate",
                    "no-retry",
                    "no-posthoc-parameter-change",
                    "no-persistence",
                )
            ),
        ),
        (
            S1_GK_CHECK_NAMES[7],
            _called_names(builder_source).isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "contract_id": S1_GK_CONTRACT_ID,
        "source_s1gh_result_digest": bridge.result_digest,
        "source_s1gj_result_digest": integration.result_digest,
        "role_order": bridge_roles,
        "refinement_step_counts": integration.refinement_step_counts,
        "wrapper_inputs": S1_GK_WRAPPER_INPUTS,
        "loop_sequence": S1_GK_LOOP_SEQUENCE,
        "abort_conditions": S1_GK_ABORT_CONDITIONS,
        "abort_policy": S1_GK_ABORT_POLICY,
        "return_components": S1_GK_RETURN_COMPONENTS,
        "output_fields": tuple(
            E1FormationS1GIFixedAdapterRealOutput.__dataclass_fields__
        ),
        "receipt_fields": tuple(
            E1FormationS1GIFixedAdapterCommonProbeReceipt.__dataclass_fields__
        ),
        "checks": checks,
        "wrapper_arm_count": 6,
        "planned_kernel_call_count": S1_GF_TOTAL_BATCH_COUNT,
        "planned_field_step_count": S1_GF_TOTAL_BATCH_COUNT,
        "planned_source_support_count": S1_GJ_TOTAL_SUPPORT_COUNT,
        "atomic_six_return_required": True,
        "live_state_permitted_in_fixed_kernel": False,
        "real_wrapper_implementation_permitted": True,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "field_execution_performed": False,
        "retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "FIXED_ADAPTER_REAL_WRAPPER_CONTRACT_BOUND_IMPLEMENTATION_ALLOWED_"
            "EXECUTION_CLOSED"
        ),
        "reason": (
            "six-real-input-groups-and-six-synthetic-output-schemas-bind-one-"
            "2800-call-660-support-wrapper;implementation-is-allowed-behind-"
            "closed-execution-gate;partial-return-retry-and-persistence-forbidden"
        ),
    }
    return E1FormationS1GKFixedAdapterRealWrapperContract(
        **values,
        contract_digest=_digest(values),
    )
