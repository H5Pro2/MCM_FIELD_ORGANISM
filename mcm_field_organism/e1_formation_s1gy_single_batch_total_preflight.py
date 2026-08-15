"""S1-GY non-executing total preflight for the exact S1-GX pilot target."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
import inspect

from .e1_formation_s1gh_fresh_field_bridge import (
    E1FormationS1GHFreshFieldBridgeResult,
)
from .e1_formation_s1gq_carrier_transition_schema import (
    audit_e1_formation_s1gq_carrier_transition_schema,
)
from .e1_formation_s1gs_real_single_batch_gate_contract import (
    E1FormationS1GSRealSingleBatchGateContract,
)
from .e1_formation_s1gu_real_transition_builder_contract import (
    audit_e1_formation_s1gu_real_transition_builder_contract,
)
from .e1_formation_s1gv_real_adapter_call_receipt_schema import (
    audit_e1_formation_s1gv_real_adapter_call_receipt_schema,
)
from .e1_formation_s1gw_external_owner_authorization_schema import (
    audit_e1_formation_s1gw_external_owner_authorization_schema,
)
from .e1_formation_s1gx_deterministic_single_batch_target import (
    E1FormationS1GXDeterministicSingleBatchTarget,
    select_e1_formation_s1gx_deterministic_single_batch_target,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1GYSingleBatchTotalPreflightError(ValueError):
    """Raised when the preflight hides a blocker or opens execution."""


S1_GY_PREFLIGHT_ID = "e1.single-carrier-batch-total-preflight.s1gy.v1"
S1_GY_STATIC_GATE_NAMES = (
    "exact-s1gx-target-reproduces-from-current-bridge-and-gate",
    "target-run-role-and-batch-are-r2-ab-zero",
    "target-fresh-binding-carrier-and-batch-objects-are-explicit",
    "gate-budget-is-one-adapter-call-and-one-field-step",
    "gate-authorization-token-retry-and-persistence-remain-closed",
    "s1gq-separate-real-transition-schema-and-envelope-are-ready",
    "s1gu-builder-contract-requires-typed-adapter-call-receipt",
    "s1gv-receipt-schema-is-complete-but-has-no-factory",
    "s1gw-authorization-schema-binds-external-origin-and-exact-target",
    "continue-message-is-not-real-authorization",
    "source-fresh-field-remains-initial-and-unadvanced",
    "preflight-calls-no-transition-adapter-kernel-token-factory-or-writer",
)
S1_GY_IMPLEMENTATION_BLOCKERS = (
    "external-owner-authorization-origin-bridge-not-implemented",
    "real-single-use-token-factory-not-implemented",
    "atomic-real-adapter-call-receipt-factory-not-implemented",
    "pure-real-transition-builder-not-implemented",
    "gated-real-single-batch-adapter-not-implemented",
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
class E1FormationS1GYSingleBatchTotalPreflight:
    preflight_id: str
    source_s1gh_result_digest: str
    source_s1gs_gate_digest: str
    source_s1gq_audit_digest: str
    source_s1gu_contract_digest: str
    source_s1gv_audit_digest: str
    source_s1gw_audit_digest: str
    target_digest: str
    run_id: str
    refinement_id: str
    role_id: str
    binding_digest: str
    carrier_digest: str
    batch_index: int
    maximum_adapter_calls: int
    maximum_field_steps: int
    static_gates: tuple[tuple[str, bool], ...]
    implementation_blockers: tuple[str, ...]
    static_contracts_complete: bool
    implementation_ready: bool
    authorization_request_ready: bool
    authorization_present: bool
    real_token_present: bool
    receipt_factory_present: bool
    transition_builder_present: bool
    real_adapter_present: bool
    transition_created: bool
    adapter_calls: int
    field_steps_executed: int
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    reason: str
    preflight_digest: str
    target: E1FormationS1GXDeterministicSingleBatchTarget = field(
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"target", "preflight_digest"}
        }
        if (
            self.preflight_id != S1_GY_PREFLIGHT_ID
            or any(
                len(value) != 64
                for value in (
                    self.source_s1gh_result_digest,
                    self.source_s1gs_gate_digest,
                    self.source_s1gq_audit_digest,
                    self.source_s1gu_contract_digest,
                    self.source_s1gv_audit_digest,
                    self.source_s1gw_audit_digest,
                    self.target_digest,
                    self.binding_digest,
                    self.carrier_digest,
                )
            )
            or not isinstance(
                self.target, E1FormationS1GXDeterministicSingleBatchTarget
            )
            or self.target_digest != self.target.target_digest
            or self.run_id != "S1-GY-REAL-SINGLE-CARRIER-BATCH-PILOT"
            or (self.refinement_id, self.role_id, self.batch_index)
            != ("r2", "fixed-adapter-ab", 0)
            or self.binding_digest != self.target.selected_binding_digest
            or self.carrier_digest != self.target.selected_carrier_digest
            or self.maximum_adapter_calls != 1
            or self.maximum_field_steps != 1
            or tuple(name for name, _ in self.static_gates)
            != S1_GY_STATIC_GATE_NAMES
            or any(value is not True for _, value in self.static_gates)
            or self.implementation_blockers != S1_GY_IMPLEMENTATION_BLOCKERS
            or self.static_contracts_complete is not True
            or any(
                value is not False
                for value in (
                    self.implementation_ready,
                    self.authorization_request_ready,
                    self.authorization_present,
                    self.real_token_present,
                    self.receipt_factory_present,
                    self.transition_builder_present,
                    self.real_adapter_present,
                    self.transition_created,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.adapter_calls != 0
            or self.field_steps_executed != 0
            or self.decision
            != "STATIC_SINGLE_BATCH_PREFLIGHT_PASSES_IMPLEMENTATION_COMPONENTS_MISSING"
            or not self.reason
            or self.preflight_digest != _digest(payload)
        ):
            raise E1FormationS1GYSingleBatchTotalPreflightError(
                "S1-GY preflight hid a blocker or opened real execution"
            )


def prepare_e1_formation_s1gy_single_batch_total_preflight(
    bridge: E1FormationS1GHFreshFieldBridgeResult,
    gate: E1FormationS1GSRealSingleBatchGateContract,
    target: E1FormationS1GXDeterministicSingleBatchTarget,
) -> E1FormationS1GYSingleBatchTotalPreflight:
    """Check all static boundaries without requesting or executing a run."""

    if (
        not isinstance(bridge, E1FormationS1GHFreshFieldBridgeResult)
        or not isinstance(gate, E1FormationS1GSRealSingleBatchGateContract)
        or not isinstance(target, E1FormationS1GXDeterministicSingleBatchTarget)
    ):
        raise E1FormationS1GYSingleBatchTotalPreflightError(
            "S1-GY requires the exact bridge, gate, and target"
        )
    bridge.__post_init__()
    gate.__post_init__()
    target.__post_init__()
    expected_target = select_e1_formation_s1gx_deterministic_single_batch_target(
        bridge,
        gate,
    )
    transition_schema = audit_e1_formation_s1gq_carrier_transition_schema()
    builder_contract = audit_e1_formation_s1gu_real_transition_builder_contract()
    receipt_schema = audit_e1_formation_s1gv_real_adapter_call_receipt_schema()
    authorization_schema = (
        audit_e1_formation_s1gw_external_owner_authorization_schema()
    )
    preflight_source = inspect.getsource(
        prepare_e1_formation_s1gy_single_batch_total_preflight
    )
    forbidden_calls = {
        "advance_e1_formation_s1gn_live_field_carrier_synthetically",
        "bind_e1_formation_s1gq_carrier_transition_envelope",
        "map_proposal_batch_to_transient_docks",
        "project_transient_docks_to_neuron_inputs",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "issue_e1_formation_s1gt_synthetic_single_use_token",
        "consume",
        "open",
        "write_text",
        "write_bytes",
    }
    static_gates = (
        (
            S1_GY_STATIC_GATE_NAMES[0],
            expected_target.target_digest == target.target_digest
            and expected_target.selected_fresh_binding
            is target.selected_fresh_binding
            and expected_target.selected_batch is target.selected_batch,
        ),
        (
            S1_GY_STATIC_GATE_NAMES[1],
            (
                target.run_id,
                target.selected_refinement_id,
                target.selected_role_id,
                target.selected_batch_index,
            )
            == (
                "S1-GY-REAL-SINGLE-CARRIER-BATCH-PILOT",
                "r2",
                "fixed-adapter-ab",
                0,
            ),
        ),
        (
            S1_GY_STATIC_GATE_NAMES[2],
            target.selected_initial_carrier.fresh_binding
            is target.selected_fresh_binding
            and target.selected_initial_carrier.current_field
            is target.selected_fresh_binding.fresh_field
            and target.selected_fresh_binding.invocation.context.probe_plan
            .handoff.batches[0]
            is target.selected_batch,
        ),
        (
            S1_GY_STATIC_GATE_NAMES[3],
            gate.maximum_adapter_calls
            == target.maximum_adapter_calls
            == 1
            and gate.maximum_field_steps == target.maximum_field_steps == 1,
        ),
        (
            S1_GY_STATIC_GATE_NAMES[4],
            gate.authorization_present is False
            and gate.authorization_token_implemented is False
            and gate.retry_permitted is False
            and gate.persistence_permitted is False
            and gate.execution_permitted is False,
        ),
        (
            S1_GY_STATIC_GATE_NAMES[5],
            transition_schema.separate_semantics_enforced is True
            and transition_schema.shared_envelope_implemented is True
            and transition_schema.real_transition_builder_present is False,
        ),
        (
            S1_GY_STATIC_GATE_NAMES[6],
            builder_contract.typed_adapter_call_receipt_required is True
            and builder_contract.pure_transition_builder_implemented is False,
        ),
        (
            S1_GY_STATIC_GATE_NAMES[7],
            not receipt_schema.missing_required_fields
            and receipt_schema.receipt_factory_implemented is False
            and receipt_schema.receipt_instance_created is False,
        ),
        (
            S1_GY_STATIC_GATE_NAMES[8],
            authorization_schema.exact_target_binding_required is True
            and authorization_schema.external_origin_receipt_required is True
            and authorization_schema.authorization_instance_created is False,
        ),
        (
            S1_GY_STATIC_GATE_NAMES[9],
            authorization_schema.current_continue_message_is_authorization
            is False,
        ),
        (
            S1_GY_STATIC_GATE_NAMES[10],
            target.selected_initial_carrier.completed_batch_count == 0
            and target.selected_initial_carrier.actual_field_steps_executed == 0
            and target.selected_initial_carrier.current_field_digest
            == target.selected_initial_field_digest,
        ),
        (
            S1_GY_STATIC_GATE_NAMES[11],
            _called_names(preflight_source).isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "preflight_id": S1_GY_PREFLIGHT_ID,
        "source_s1gh_result_digest": bridge.result_digest,
        "source_s1gs_gate_digest": gate.gate_digest,
        "source_s1gq_audit_digest": transition_schema.audit_digest,
        "source_s1gu_contract_digest": builder_contract.contract_digest,
        "source_s1gv_audit_digest": receipt_schema.audit_digest,
        "source_s1gw_audit_digest": authorization_schema.audit_digest,
        "target_digest": target.target_digest,
        "run_id": target.run_id,
        "refinement_id": target.selected_refinement_id,
        "role_id": target.selected_role_id,
        "binding_digest": target.selected_binding_digest,
        "carrier_digest": target.selected_carrier_digest,
        "batch_index": target.selected_batch_index,
        "maximum_adapter_calls": 1,
        "maximum_field_steps": 1,
        "static_gates": static_gates,
        "implementation_blockers": S1_GY_IMPLEMENTATION_BLOCKERS,
        "static_contracts_complete": all(value for _, value in static_gates),
        "implementation_ready": False,
        "authorization_request_ready": False,
        "authorization_present": False,
        "real_token_present": False,
        "receipt_factory_present": False,
        "transition_builder_present": False,
        "real_adapter_present": False,
        "transition_created": False,
        "adapter_calls": 0,
        "field_steps_executed": 0,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "STATIC_SINGLE_BATCH_PREFLIGHT_PASSES_"
            "IMPLEMENTATION_COMPONENTS_MISSING"
        ),
        "reason": (
            "all-static-target-gate-schema-and-boundary-checks-pass-but-the-"
            "external-origin-bridge-real-token-factory-atomic-receipt-factory-"
            "pure-transition-builder-and-gated-real-adapter-are-not-"
            "implemented;authorization-request-and-execution-remain-closed"
        ),
    }
    payload = dict(values)
    return E1FormationS1GYSingleBatchTotalPreflight(
        **values,
        preflight_digest=_digest(payload),
        target=target,
    )
