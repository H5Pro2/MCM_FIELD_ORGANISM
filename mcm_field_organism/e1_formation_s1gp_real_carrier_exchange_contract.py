"""S1-GP static contract for the real carrier-transition exchange point."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_formation_s1gn_live_field_carrier import (
    E1FormationS1GNLiveFieldCarrier,
    E1FormationS1GNLiveFieldCarrierTransition,
    advance_e1_formation_s1gn_live_field_carrier_synthetically,
)
from .e1_formation_s1go_private_carrier_wrapper import (
    run_e1_formation_s1go_private_carrier_wrapper,
)
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
)
from .e1_refined_formation_runner import _digest
from .shared_mcm_field import SharedMCMField
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class E1FormationS1GPRealCarrierExchangeContractError(ValueError):
    """Raised when the static exchange contract opens execution or hides a gap."""


S1_GP_CONTRACT_ID = "e1.real-carrier-exchange-contract.s1gp.v1"
S1_GP_EXCHANGE_INPUTS = (
    ("fresh", "E1FormationS1GHFreshFieldBinding"),
    ("batch", "ReceptorProposalBatch"),
    ("carrier", "E1FormationS1GNLiveFieldCarrier"),
)
S1_GP_REAL_ADAPTER_SEQUENCE = (
    "validate-fresh-batch-and-current-carrier-before-any-adapter-call",
    "map-batch-to-carrier-current-field-docks",
    "project-complete-transient-neuron-inputs",
    "construct-empty-boundary-distribution-for-exact-batch-time",
    "advance-current-field-with-exact-bound-fixed-adapter",
    "validate-new-shared-field-object-and-one-step-advance",
    "construct-separate-real-carrier-transition",
    "return-next-carrier-only-after-complete-validation",
)
S1_GP_PRECONDITIONS = (
    "carrier-fresh-binding-object-is-exact-fresh",
    "carrier-binding-digest-matches-fresh",
    "carrier-current-field-digest-recomputes-exactly",
    "carrier-completed-batch-count-selects-exact-next-batch",
    "batch-index-time-and-support-match-bound-probe-plan",
    "source-state-and-fixed-adapter-attestations-unchanged",
    "persistence-and-claims-false",
)
S1_GP_POSTCONDITIONS = (
    "next-field-is-shared-mcm-field",
    "next-field-is-new-explicit-object",
    "next-field-digest-recomputed-from-next-field",
    "completed-batch-count-increments-by-one",
    "support-count-increments-by-batch-event-count",
    "actual-field-step-count-increments-by-one",
    "fresh-binding-and-neuron-order-remain-bound",
    "source-state-and-fixed-adapter-remain-unchanged",
    "no-persistence-retry-parametrization-or-claims",
)
S1_GP_REQUIRED_REAL_TRANSITION_FIELDS = (
    "previous_carrier",
    "next_carrier",
    "binding_digest",
    "batch_index",
    "previous_field_digest",
    "next_field_digest",
    "field_object_replaced",
    "accounted_field_steps",
    "actual_field_steps_executed",
    "persistence_performed",
    "claims_permitted",
    "transition_digest",
)
S1_GP_INCOMPATIBILITIES = (
    "s1gn-transition-requires-synthetic-no-field-advance",
    "s1gn-transition-requires-same-field-object",
    "s1gn-transition-requires-zero-actual-field-steps",
    "s1go-wrapper-rejects-non-s1gn-transition-type",
    "s1go-wrapper-rejects-nonzero-transition-field-steps",
)
S1_GP_CHECK_NAMES = (
    "s1go-injection-point-receives-fresh-batch-and-carrier",
    "s1gn-carrier-holds-complete-real-transition-input-state",
    "real-map-project-kernel-signatures-form-one-chain",
    "real-kernel-requires-shared-field-and-returns-shared-field",
    "s1gn-transition-is-provably-synthetic-only",
    "s1go-current-transition-check-is-provably-synthetic-only",
    "separate-real-transition-contract-is-smallest-safe-exchange",
    "audit-calls-no-adapter-kernel-or-writer",
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
class E1FormationS1GPRealCarrierExchangeContract:
    contract_id: str
    exchange_inputs: tuple[tuple[str, str], ...]
    real_adapter_sequence: tuple[str, ...]
    preconditions: tuple[str, ...]
    postconditions: tuple[str, ...]
    required_real_transition_fields: tuple[str, ...]
    incompatibilities: tuple[str, ...]
    go_wrapper_parameters: tuple[str, ...]
    synthetic_transition_parameters: tuple[str, ...]
    mapper_parameters: tuple[str, ...]
    projector_parameters: tuple[str, ...]
    real_kernel_parameters: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    carrier_input_is_real_adapter_complete: bool
    real_adapter_chain_is_signature_compatible: bool
    synthetic_transition_is_real_compatible: bool
    current_go_wrapper_is_real_transition_compatible: bool
    separate_real_transition_type_required: bool
    hidden_field_state_permitted: bool
    real_transition_schema_implementation_permitted: bool
    real_adapter_implementation_permitted: bool
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
            self.contract_id != S1_GP_CONTRACT_ID
            or self.exchange_inputs != S1_GP_EXCHANGE_INPUTS
            or self.real_adapter_sequence != S1_GP_REAL_ADAPTER_SEQUENCE
            or self.preconditions != S1_GP_PRECONDITIONS
            or self.postconditions != S1_GP_POSTCONDITIONS
            or self.required_real_transition_fields
            != S1_GP_REQUIRED_REAL_TRANSITION_FIELDS
            or self.incompatibilities != S1_GP_INCOMPATIBILITIES
            or self.go_wrapper_parameters
            != (
                "contract",
                "bridge",
                "gate",
                "carrier_transition",
                "terminal_output_factory",
            )
            or self.synthetic_transition_parameters
            != ("fresh", "batch", "carrier")
            or self.mapper_parameters != ("batch", "docks")
            or self.projector_parameters != ("trajectory", "docks")
            or self.real_kernel_parameters
            != (
                "field",
                "fixed_adapter",
                "distribution",
                "transient_inputs",
                "substrate_config",
                "afterimage_config",
                "dissipation_config",
            )
            or tuple(name for name, _ in self.checks) != S1_GP_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.carrier_input_is_real_adapter_complete,
                    self.real_adapter_chain_is_signature_compatible,
                    self.separate_real_transition_type_required,
                    self.real_transition_schema_implementation_permitted,
                )
            )
            or any(
                value is not False
                for value in (
                    self.synthetic_transition_is_real_compatible,
                    self.current_go_wrapper_is_real_transition_compatible,
                    self.hidden_field_state_permitted,
                    self.real_adapter_implementation_permitted,
                    self.execution_permitted,
                    self.field_execution_performed,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "REAL_EXCHANGE_POINT_BOUND_SEPARATE_REAL_TRANSITION_TYPE_REQUIRED"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1GPRealCarrierExchangeContractError(
                "S1-GP contract changed, hid the type gap, or opened execution"
            )


def audit_e1_formation_s1gp_real_carrier_exchange_contract(
) -> E1FormationS1GPRealCarrierExchangeContract:
    """Bind the real exchange point through inspection without calling it."""

    go_signature = inspect.signature(
        run_e1_formation_s1go_private_carrier_wrapper
    )
    synthetic_signature = inspect.signature(
        advance_e1_formation_s1gn_live_field_carrier_synthetically
    )
    mapper_signature = inspect.signature(map_proposal_batch_to_transient_docks)
    projector_signature = inspect.signature(
        project_transient_docks_to_neuron_inputs
    )
    kernel_signature = inspect.signature(
        advance_fixed_e1_adapter_fast_shared_field_transient
    )
    carrier_fields = tuple(E1FormationS1GNLiveFieldCarrier.__dataclass_fields__)
    transition_fields = tuple(
        E1FormationS1GNLiveFieldCarrierTransition.__dataclass_fields__
    )
    transition_validation_source = inspect.getsource(
        E1FormationS1GNLiveFieldCarrierTransition.__post_init__
    )
    go_source = inspect.getsource(
        run_e1_formation_s1go_private_carrier_wrapper
    )
    audit_source = inspect.getsource(
        audit_e1_formation_s1gp_real_carrier_exchange_contract
    )
    expected_carrier_fields = {
        "fresh_binding",
        "current_field",
        "binding_digest",
        "initial_field_digest",
        "current_field_digest",
        "ordered_neuron_ids",
        "completed_batch_count",
        "accounted_source_support_count",
        "actual_field_steps_executed",
        "carrier_digest",
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
    forbidden_calls = {
        "map_proposal_batch_to_transient_docks",
        "project_transient_docks_to_neuron_inputs",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "open",
        "write_text",
        "write_bytes",
    }
    checks = (
        (
            S1_GP_CHECK_NAMES[0],
            tuple(go_signature.parameters)
            == (
                "contract",
                "bridge",
                "gate",
                "carrier_transition",
                "terminal_output_factory",
            )
            and tuple(synthetic_signature.parameters)
            == ("fresh", "batch", "carrier"),
        ),
        (
            S1_GP_CHECK_NAMES[1],
            expected_carrier_fields.issubset(carrier_fields)
            and "current_field" in carrier_fields,
        ),
        (
            S1_GP_CHECK_NAMES[2],
            tuple(mapper_signature.parameters) == ("batch", "docks")
            and tuple(projector_signature.parameters)
            == ("trajectory", "docks")
            and tuple(kernel_signature.parameters) == expected_kernel_parameters,
        ),
        (
            S1_GP_CHECK_NAMES[3],
            kernel_signature.parameters["field"].annotation
            in (SharedMCMField, "SharedMCMField")
            and kernel_signature.return_annotation
            in (SharedMCMField, "SharedMCMField"),
        ),
        (
            S1_GP_CHECK_NAMES[4],
            "synthetic_no_field_advance" in transition_fields
            and "field_object_replaced" in transition_fields
            and "self.field_object_replaced is not False"
            in transition_validation_source
            and "self.actual_field_steps_executed != 0"
            in transition_validation_source,
        ),
        (
            S1_GP_CHECK_NAMES[5],
            "bind_e1_formation_s1gq_carrier_transition_envelope" in go_source
            and "synthetic-no-field-advance" in go_source
            and "envelope.actual_field_steps_executed != 0" in go_source,
        ),
        (
            S1_GP_CHECK_NAMES[6],
            set(S1_GP_REQUIRED_REAL_TRANSITION_FIELDS).issubset(
                set(transition_fields)
            )
            and len(S1_GP_INCOMPATIBILITIES) == 5,
        ),
        (
            S1_GP_CHECK_NAMES[7],
            _called_names(audit_source).isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "contract_id": S1_GP_CONTRACT_ID,
        "exchange_inputs": S1_GP_EXCHANGE_INPUTS,
        "real_adapter_sequence": S1_GP_REAL_ADAPTER_SEQUENCE,
        "preconditions": S1_GP_PRECONDITIONS,
        "postconditions": S1_GP_POSTCONDITIONS,
        "required_real_transition_fields": (
            S1_GP_REQUIRED_REAL_TRANSITION_FIELDS
        ),
        "incompatibilities": S1_GP_INCOMPATIBILITIES,
        "go_wrapper_parameters": tuple(go_signature.parameters),
        "synthetic_transition_parameters": tuple(
            synthetic_signature.parameters
        ),
        "mapper_parameters": tuple(mapper_signature.parameters),
        "projector_parameters": tuple(projector_signature.parameters),
        "real_kernel_parameters": tuple(kernel_signature.parameters),
        "checks": checks,
        "carrier_input_is_real_adapter_complete": True,
        "real_adapter_chain_is_signature_compatible": True,
        "synthetic_transition_is_real_compatible": False,
        "current_go_wrapper_is_real_transition_compatible": False,
        "separate_real_transition_type_required": True,
        "hidden_field_state_permitted": False,
        "real_transition_schema_implementation_permitted": True,
        "real_adapter_implementation_permitted": False,
        "execution_permitted": False,
        "field_execution_performed": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "REAL_EXCHANGE_POINT_BOUND_SEPARATE_REAL_TRANSITION_TYPE_REQUIRED"
        ),
        "reason": (
            "s1go-now-carries-the-complete-current-field-but-its-s1gn-"
            "transition-type-intentionally-requires-same-field-object-and-zero-"
            "real-steps;bind-one-separate-real-transition-schema-before-"
            "implementing-or-executing-the-real-batch-adapter"
        ),
    }
    return E1FormationS1GPRealCarrierExchangeContract(
        **values,
        contract_digest=_digest(values),
    )
