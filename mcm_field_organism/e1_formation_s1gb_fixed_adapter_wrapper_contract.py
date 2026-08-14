"""S1-GB static fixed-adapter wrapper contract and probe-context gap."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_confirmation_refinement_planner import E1ConfirmationRefinementPlan
from .e1_formation_s1ft_synthetic_fresh_chain_preflight import (
    E1FormationS1FTPreparedSyntheticChain,
)
from .e1_formation_s1fv_live_state_ten_role_contract import (
    E1FormationS1FVProbeSlotBinding,
)
from .e1_formation_s1fw_synthetic_live_state_handoff import (
    E1FormationS1FWSyntheticSlotHandoff,
)
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
)
from .e1_refined_formation_runner import _digest
from .e1_weighted_field_adapter import E1WeightedFieldAdapterResult
from .receptor_time_model import ReceptorTimeSequence


class E1FormationS1GBFixedAdapterWrapperContractError(ValueError):
    """Raised when S1-GB skips the probe-context bridge or opens execution."""


S1_GB_CONTRACT_ID = "e1.fixed-adapter-wrapper-contract.s1gb.v1"
S1_GB_CONTEXT_FIELDS = (
    "binding",
    "probe_sequences",
    "probe_plan",
    "probe_source_digest",
    "context_digest",
)
S1_GB_WRAPPER_INPUTS = (
    ("context", "E1FormationS1GBFixedAdapterProbeContext"),
    ("fresh_field", "object-separated SharedMCMField"),
    ("source_state", "exact E1LocalEdgePlasticityState for attestation only"),
    ("fixed_adapter", "exact E1WeightedFieldAdapterResult"),
)
S1_GB_DIGEST_GATES = (
    "fixed-role-binding-is-one-s1fv-slot",
    "context-probe-source-digest-matches-s1fp-and-s1ft",
    "probe-sequences-digest-matches-context",
    "probe-plan-refinement-matches-binding",
    "fresh-field-initial-digest-matches-bound-initial-field",
    "source-state-object-and-digest-match-s1fw-handoff",
    "fixed-adapter-object-and-digest-match-s1fw-handoff",
    "fixed-adapter-edge-inventory-matches-fresh-field",
    "source-state-and-adapter-digests-unchanged-after-wrapper",
)
S1_GB_LOOP_CONTRACT = (
    "iterate-probe-plan-handoff-batches-once-in-order",
    "map-each-batch-to-transient-docks",
    "project-complete-neuron-inputs",
    "construct-contact-free-boundary-distribution",
    "call-fixed-adapter-kernel-exactly-once-per-batch",
    "never-pass-source-state-object-to-field-kernel",
    "no-retry-no-posthoc-parameter-change",
)
S1_GB_OUTPUT_FIELDS = (
    "binding_digest",
    "probe_source_digest",
    "initial_field_digest",
    "terminal_field_digest",
    "ordered_neuron_ids",
    "activation_vector",
    "afterimage_vector",
    "field_step_count",
    "source_support_count",
    "source_state_digest",
    "fixed_adapter_digest",
    "source_state_preserved",
    "fixed_adapter_preserved",
    "persistence_performed",
    "claims_permitted",
    "output_digest",
)
S1_GB_FAIL_CLOSED_CONDITIONS = (
    "missing-or-untyped-probe-context",
    "digest-or-binding-mismatch",
    "non-fixed-adapter-role",
    "missing-exact-source-state-or-adapter-object",
    "field-geometry-or-neuron-order-mismatch",
    "probe-plan-or-support-mismatch",
    "source-state-or-adapter-mutation",
    "partial-output-or-exception-during-loop",
)
S1_GB_CHECK_NAMES = (
    "new-slot-binding-has-no-probe-object-fields",
    "s1fw-handoff-carries-state-and-fixed-adapter-objects",
    "s1ft-chain-carries-only-probe-source-digest",
    "required-probe-sequence-and-plan-types-exist",
    "fixed-adapter-kernel-signature-is-compatible",
    "source-state-is-excluded-from-kernel-signature",
    "contract-calls-no-probe-kernel-or-writer",
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
class E1FormationS1GBFixedAdapterWrapperContract:
    contract_id: str
    probe_context_fields: tuple[str, ...]
    wrapper_inputs: tuple[tuple[str, str], ...]
    digest_gates: tuple[str, ...]
    loop_contract: tuple[str, ...]
    output_fields: tuple[str, ...]
    fail_closed_conditions: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    fixed_role_count: int
    current_probe_source_digest_bound: bool
    exact_probe_sequence_object_present_in_ten_role_chain: bool
    exact_probe_plan_object_present_in_ten_role_chain: bool
    live_state_object_present_in_handoff: bool
    fixed_adapter_object_present_in_handoff: bool
    new_probe_context_bridge_required: bool
    probe_context_bridge_implementation_permitted: bool
    fixed_adapter_wrapper_implementation_permitted: bool
    execution_permitted: bool
    field_execution_performed: bool
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
            self.contract_id != S1_GB_CONTRACT_ID
            or self.probe_context_fields != S1_GB_CONTEXT_FIELDS
            or self.wrapper_inputs != S1_GB_WRAPPER_INPUTS
            or self.digest_gates != S1_GB_DIGEST_GATES
            or self.loop_contract != S1_GB_LOOP_CONTRACT
            or self.output_fields != S1_GB_OUTPUT_FIELDS
            or self.fail_closed_conditions != S1_GB_FAIL_CLOSED_CONDITIONS
            or tuple(name for name, _ in self.checks) != S1_GB_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or self.fixed_role_count != 6
            or any(
                value is not True
                for value in (
                    self.current_probe_source_digest_bound,
                    self.live_state_object_present_in_handoff,
                    self.fixed_adapter_object_present_in_handoff,
                    self.new_probe_context_bridge_required,
                    self.probe_context_bridge_implementation_permitted,
                )
            )
            or any(
                value is not False
                for value in (
                    self.exact_probe_sequence_object_present_in_ten_role_chain,
                    self.exact_probe_plan_object_present_in_ten_role_chain,
                    self.fixed_adapter_wrapper_implementation_permitted,
                    self.execution_permitted,
                    self.field_execution_performed,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "FIXED_ADAPTER_WRAPPER_BOUND_PROBE_CONTEXT_OBJECT_BRIDGE_MISSING"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1GBFixedAdapterWrapperContractError(
                "S1-GB contract changed, skipped context, or opened execution"
            )


def prepare_e1_formation_s1gb_fixed_adapter_wrapper_contract(
) -> E1FormationS1GBFixedAdapterWrapperContract:
    """Bind wrapper requirements without constructing context or running a field."""

    binding_fields = tuple(E1FormationS1FVProbeSlotBinding.__dataclass_fields__)
    handoff_fields = tuple(E1FormationS1FWSyntheticSlotHandoff.__dataclass_fields__)
    chain_fields = tuple(E1FormationS1FTPreparedSyntheticChain.__dataclass_fields__)
    kernel_parameters = tuple(
        inspect.signature(
            advance_fixed_e1_adapter_fast_shared_field_transient
        ).parameters
    )
    source = inspect.getsource(
        prepare_e1_formation_s1gb_fixed_adapter_wrapper_contract
    )
    forbidden_calls = {
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "advance_frozen_e1_fast_shared_field_transient",
        "advance_neutral_fast_shared_field_transient",
        "open",
        "write_text",
        "write_bytes",
    }
    checks = (
        (
            S1_GB_CHECK_NAMES[0],
            "probe_sequences" not in binding_fields
            and "probe_plan" not in binding_fields,
        ),
        (
            S1_GB_CHECK_NAMES[1],
            all(name in handoff_fields for name in ("state", "fixed_adapter")),
        ),
        (
            S1_GB_CHECK_NAMES[2],
            "probe_source_digest" in chain_fields
            and "probe_sequences" not in chain_fields
            and "probe_plan" not in chain_fields,
        ),
        (
            S1_GB_CHECK_NAMES[3],
            inspect.isclass(ReceptorTimeSequence)
            and inspect.isclass(E1ConfirmationRefinementPlan),
        ),
        (
            S1_GB_CHECK_NAMES[4],
            kernel_parameters
            == (
                "field",
                "fixed_adapter",
                "distribution",
                "transient_inputs",
                "substrate_config",
                "afterimage_config",
                "dissipation_config",
            ),
        ),
        (
            S1_GB_CHECK_NAMES[5],
            "state" not in kernel_parameters
            and "frozen_e1_state" not in kernel_parameters
            and inspect.isclass(E1WeightedFieldAdapterResult),
        ),
        (S1_GB_CHECK_NAMES[6], _called_names(source).isdisjoint(forbidden_calls)),
    )
    values = {
        "contract_id": S1_GB_CONTRACT_ID,
        "probe_context_fields": S1_GB_CONTEXT_FIELDS,
        "wrapper_inputs": S1_GB_WRAPPER_INPUTS,
        "digest_gates": S1_GB_DIGEST_GATES,
        "loop_contract": S1_GB_LOOP_CONTRACT,
        "output_fields": S1_GB_OUTPUT_FIELDS,
        "fail_closed_conditions": S1_GB_FAIL_CLOSED_CONDITIONS,
        "checks": checks,
        "fixed_role_count": 6,
        "current_probe_source_digest_bound": True,
        "exact_probe_sequence_object_present_in_ten_role_chain": False,
        "exact_probe_plan_object_present_in_ten_role_chain": False,
        "live_state_object_present_in_handoff": True,
        "fixed_adapter_object_present_in_handoff": True,
        "new_probe_context_bridge_required": True,
        "probe_context_bridge_implementation_permitted": True,
        "fixed_adapter_wrapper_implementation_permitted": False,
        "execution_permitted": False,
        "field_execution_performed": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "FIXED_ADAPTER_WRAPPER_BOUND_PROBE_CONTEXT_OBJECT_BRIDGE_MISSING"
        ),
        "reason": (
            "ten-role-chain-carries-fixed-slot-state-adapter-and-probe-digest-"
            "but-no-exact-probe-sequence-or-plan-object;old-eight-role-"
            "resolved-slot-cannot-substitute-for-the-new-binding"
        ),
    }
    return E1FormationS1GBFixedAdapterWrapperContract(
        **values,
        contract_digest=_digest(values),
    )
