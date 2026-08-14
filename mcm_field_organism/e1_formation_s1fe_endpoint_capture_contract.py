"""S1-FE static endpoint-capture contract for E1 formation states."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_confirmation_prepared_formation_consumer import (
    S1_EC7_FORMATION_ARMS,
    S1_EC7_REFINEMENTS,
)
from .e1_confirmation_formation_runner import E1ConfirmationFormationArmAudit
from .e1_confirmation_prepared_real_formation_kernel import (
    E1PreparedRealFormationArmResult,
)
from .e1_formation_s1fc_state_convergence_contract import (
    S1_FC_STATE_VECTOR_SCHEMA,
    audit_e1_formation_s1fc_state_convergence_contract,
)
from .e1_formation_s1fd_state_convergence_evaluator import (
    E1FormationS1FDSyntheticStateVector,
    S1_FD_EVALUATOR_ID,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1FEEndpointCaptureContractError(ValueError):
    """Raised when the S1-FE endpoint-capture boundary changes."""


S1_FE_CONTRACT_ID = "e1.formation-endpoint-capture-contract.s1fe.v1"
S1_FE_ROLE_MAP = (
    ("ab", "active-ab"),
    ("ba", "active-ba"),
    ("ab_identity", "identity-ab"),
    ("ab_formation_ablated", "formation-ablated-ab"),
    ("ba_formation_ablated", "formation-ablated-ba"),
)
S1_FE_SOURCE_RESULT_SCHEMA = (
    "arm_id",
    "refinement_id",
    "formation_enabled",
    "initial_field_digest",
    "initial_state_digest",
    "output_state",
    "output_state_digest",
    "audit",
    "input_objects_preserved",
    "copied_inputs_used",
    "canonical_execution_permitted",
    "claims_permitted",
    "result_digest",
)
S1_FE_CHECK_NAMES = (
    "r2-r4-r8-source-refinements-fixed",
    "five-source-arms-fixed",
    "source-result-schema-fixed",
    "source-validates-output-state-digest",
    "source-audit-carries-resource-budget-error",
    "role-map-is-total-and-bijective",
    "target-schema-equals-s1fc-schema",
    "target-type-carries-target-schema",
    "capture-is-after-formation-before-probe",
    "capture-audit-does-not-run-formation-probe-or-writer",
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
class E1FormationS1FEEndpointCaptureContract:
    contract_id: str
    source_s1fc_contract_digest: str
    source_s1fd_evaluator_id: str
    source_result_type: str
    source_refinements: tuple[tuple[str, int], ...]
    source_formation_arms: tuple[str, ...]
    source_result_schema: tuple[str, ...]
    role_map: tuple[tuple[str, str], ...]
    target_state_vector_schema: tuple[str, ...]
    required_source_result_count: int
    canonical_edge_id_rule: str
    edge_inventory_rule: str
    source_state_binding_rule: str
    resource_error_rule: str
    capture_timing_rule: str
    checks: tuple[tuple[str, bool], ...]
    atomic_capture_required: bool
    single_use_capture_required: bool
    object_separation_required: bool
    capture_adapter_implementation_permitted: bool
    formation_execution_permitted: bool
    capture_execution_permitted: bool
    probe_execution_permitted: bool
    persistence_permitted: bool
    threshold_change_permitted: bool
    memory_claim_permitted: bool
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
            self.contract_id != S1_FE_CONTRACT_ID
            or len(self.source_s1fc_contract_digest) != 64
            or self.source_s1fd_evaluator_id != S1_FD_EVALUATOR_ID
            or self.source_result_type
            != "E1PreparedRealFormationArmResult"
            or self.source_refinements != S1_EC7_REFINEMENTS
            or self.source_formation_arms != S1_EC7_FORMATION_ARMS
            or self.source_result_schema != S1_FE_SOURCE_RESULT_SCHEMA
            or self.role_map != S1_FE_ROLE_MAP
            or self.target_state_vector_schema != S1_FC_STATE_VECTOR_SCHEMA
            or self.required_source_result_count != 15
            or self.canonical_edge_id_rule
            != "sha256((first_neuron_id,second_neuron_id)):source-order"
            or self.edge_inventory_rule
            != "sha256(tuple(canonical-edge-id)):same-for-all-fifteen"
            or self.source_state_binding_rule
            != "output-state-digest-and-result-digest-validated-before-conversion"
            or self.resource_error_rule
            != "copy-audit-resource-budget-error-without-recalculation"
            or self.capture_timing_rule
            != "after-each-formation-result-and-before-any-probe-handoff"
            or tuple(name for name, _ in self.checks) != S1_FE_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.atomic_capture_required,
                    self.single_use_capture_required,
                    self.object_separation_required,
                    self.capture_adapter_implementation_permitted,
                )
            )
            or any(
                value is not False
                for value in (
                    self.formation_execution_permitted,
                    self.capture_execution_permitted,
                    self.probe_execution_permitted,
                    self.persistence_permitted,
                    self.threshold_change_permitted,
                    self.memory_claim_permitted,
                )
            )
            or self.decision != "ENDPOINT_CAPTURE_BOUND_IMPLEMENTATION_MISSING"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1FEEndpointCaptureContractError(
                "S1-FE capture contract changed or opened execution"
            )


def audit_e1_formation_s1fe_endpoint_capture_contract(
) -> E1FormationS1FEEndpointCaptureContract:
    """Bind the existing formation output to S1-FD without capturing it."""

    s1fc = audit_e1_formation_s1fc_state_convergence_contract()
    audit_source = inspect.getsource(
        audit_e1_formation_s1fe_endpoint_capture_contract
    )
    result_validation_source = inspect.getsource(
        E1PreparedRealFormationArmResult.__post_init__
    )
    source_fields = tuple(E1PreparedRealFormationArmResult.__dataclass_fields__)
    target_fields = tuple(E1FormationS1FDSyntheticStateVector.__dataclass_fields__)
    forbidden_calls = {
        "run_prepared_real_formation_arm_in_memory",
        "run_e1_asynchronous_field",
        "run_e1_common_probe_real_probe_wrapper",
        "evaluate_e1_formation_s1fd_state_convergence",
        "write_text",
        "write_bytes",
        "open",
    }
    mapped_sources = tuple(source for source, _ in S1_FE_ROLE_MAP)
    mapped_targets = tuple(target for _, target in S1_FE_ROLE_MAP)
    checks = (
        (S1_FE_CHECK_NAMES[0], S1_EC7_REFINEMENTS == s1fc.refinements),
        (S1_FE_CHECK_NAMES[1], len(S1_EC7_FORMATION_ARMS) == 5),
        (S1_FE_CHECK_NAMES[2], source_fields == S1_FE_SOURCE_RESULT_SCHEMA),
        (
            S1_FE_CHECK_NAMES[3],
            "output_state_digest" in result_validation_source
            and "_state_payload(self.output_state)" in result_validation_source,
        ),
        (
            S1_FE_CHECK_NAMES[4],
            "audit" in source_fields
            and "resource_budget_error"
            in E1ConfirmationFormationArmAudit.__dataclass_fields__,
        ),
        (
            S1_FE_CHECK_NAMES[5],
            mapped_sources == S1_EC7_FORMATION_ARMS
            and mapped_targets == s1fc.formation_roles
            and len(set(mapped_targets)) == 5,
        ),
        (
            S1_FE_CHECK_NAMES[6],
            S1_FC_STATE_VECTOR_SCHEMA == s1fc.state_vector_schema,
        ),
        (S1_FE_CHECK_NAMES[7], target_fields == S1_FC_STATE_VECTOR_SCHEMA),
        (
            S1_FE_CHECK_NAMES[8],
            "after-each-formation-result" in (
                "after-each-formation-result-and-before-any-probe-handoff"
            ),
        ),
        (
            S1_FE_CHECK_NAMES[9],
            _called_names(audit_source).isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "contract_id": S1_FE_CONTRACT_ID,
        "source_s1fc_contract_digest": s1fc.contract_digest,
        "source_s1fd_evaluator_id": S1_FD_EVALUATOR_ID,
        "source_result_type": "E1PreparedRealFormationArmResult",
        "source_refinements": S1_EC7_REFINEMENTS,
        "source_formation_arms": S1_EC7_FORMATION_ARMS,
        "source_result_schema": S1_FE_SOURCE_RESULT_SCHEMA,
        "role_map": S1_FE_ROLE_MAP,
        "target_state_vector_schema": S1_FC_STATE_VECTOR_SCHEMA,
        "required_source_result_count": 15,
        "canonical_edge_id_rule": (
            "sha256((first_neuron_id,second_neuron_id)):source-order"
        ),
        "edge_inventory_rule": (
            "sha256(tuple(canonical-edge-id)):same-for-all-fifteen"
        ),
        "source_state_binding_rule": (
            "output-state-digest-and-result-digest-validated-before-conversion"
        ),
        "resource_error_rule": (
            "copy-audit-resource-budget-error-without-recalculation"
        ),
        "capture_timing_rule": (
            "after-each-formation-result-and-before-any-probe-handoff"
        ),
        "checks": checks,
        "atomic_capture_required": True,
        "single_use_capture_required": True,
        "object_separation_required": True,
        "capture_adapter_implementation_permitted": True,
        "formation_execution_permitted": False,
        "capture_execution_permitted": False,
        "probe_execution_permitted": False,
        "persistence_permitted": False,
        "threshold_change_permitted": False,
        "memory_claim_permitted": False,
        "decision": "ENDPOINT_CAPTURE_BOUND_IMPLEMENTATION_MISSING",
        "reason": (
            "existing-r2-r4-r8-five-arm-results-map-to-fifteen-s1fd-vectors;"
            "capture-is-atomic-single-use-and-before-probe;no-execution"
        ),
    }
    return E1FormationS1FEEndpointCaptureContract(
        **values,
        contract_digest=_digest(values),
    )
