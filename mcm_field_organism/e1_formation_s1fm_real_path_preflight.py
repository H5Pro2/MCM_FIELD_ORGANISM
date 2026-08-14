"""S1-FM static preflight for the closed S1-FL real path."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_formation_s1fh_fresh_capture_one_shot_contract import (
    E1FormationS1FHFreshCaptureOneShotContract,
)
from .e1_formation_s1fi_fresh_capture_preflight import (
    E1FormationS1FIFreshCapturePreflight,
    E1FormationS1FIPreparedInputs,
)
from .e1_formation_s1fk_real_coordinator_contract import (
    E1FormationS1FKRealCoordinatorContract,
)
from .e1_formation_s1fl_real_coordinator import (
    E1FormationS1FLCoordinatorResult,
    S1_FL_COORDINATOR_ID,
    _coordinate_e1_formation_s1fl,
    run_e1_formation_s1fl_once,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1FMRealPathPreflightError(ValueError):
    """Raised when the S1-FM preflight structure is invalid."""


S1_FM_PREFLIGHT_ID = "e1.formation-capture-real-path-preflight.s1fm.v1"
S1_FM_CHECK_NAMES = (
    "s1fh-contract-bound",
    "s1fk-contract-bound",
    "s1fi-input-manifest-bound",
    "s1fi-source-preflight-passed",
    "s1fl-real-entry-signature-bound",
    "s1fl-production-adapters-bound",
    "s1fl-sequence-order-bound",
    "s1fl-atomic-result-schema-bound",
    "formation-budget-bound",
    "probe-persistence-retry-and-posthoc-closed",
    "owner-authorization-absent",
    "audit-does-not-read-resources-or-run-field",
)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
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
class E1FormationS1FMRealPathPreflight:
    preflight_id: str
    source_s1fh_contract_digest: str
    source_s1fk_contract_digest: str
    source_s1fi_preflight_digest: str
    source_input_manifest_digest: str
    source_resource_snapshot_digest: str
    source_s1fl_coordinator_id: str
    real_entry: str
    refinements: tuple[str, ...]
    formation_arm_count: int
    maximum_formation_field_steps: int
    free_memory_bytes_at_source_preflight: int
    minimum_free_memory_bytes: int
    checks: tuple[tuple[str, bool], ...]
    technical_real_path_ready: bool
    source_resource_snapshot_point_in_time_only: bool
    immediate_resource_recheck_required: bool
    owner_authorization_present: bool
    execution_permitted: bool
    field_execution_performed: bool
    capture_performed: bool
    probe_execution_performed: bool
    persistence_performed: bool
    automatic_retry_performed: bool
    posthoc_parameter_change_performed: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    preflight_digest: str

    def __post_init__(self) -> None:
        ready = all(value for _, value in self.checks)
        decision = (
            "REAL_PATH_TECHNICALLY_READY_AWAITING_EXPLICIT_OWNER_AUTHORIZATION"
            if ready
            else "REAL_PATH_PREFLIGHT_FAILED_EXECUTION_CLOSED"
        )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if (
            self.preflight_id != S1_FM_PREFLIGHT_ID
            or any(
                not _valid_digest(value)
                for value in (
                    self.source_s1fh_contract_digest,
                    self.source_s1fk_contract_digest,
                    self.source_s1fi_preflight_digest,
                    self.source_input_manifest_digest,
                    self.source_resource_snapshot_digest,
                )
            )
            or self.source_s1fl_coordinator_id != S1_FL_COORDINATOR_ID
            or self.real_entry != "run_e1_formation_s1fl_once"
            or self.refinements != ("r2", "r4", "r8")
            or self.formation_arm_count != 15
            or self.maximum_formation_field_steps != 14_000
            or self.minimum_free_memory_bytes != 4 * 1024**3
            or tuple(name for name, _ in self.checks) != S1_FM_CHECK_NAMES
            or self.technical_real_path_ready is not ready
            or self.source_resource_snapshot_point_in_time_only is not True
            or self.immediate_resource_recheck_required is not True
            or any(
                value is not False
                for value in (
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.field_execution_performed,
                    self.capture_performed,
                    self.probe_execution_performed,
                    self.persistence_performed,
                    self.automatic_retry_performed,
                    self.posthoc_parameter_change_performed,
                    self.memory_claim_permitted,
                )
            )
            or self.decision != decision
            or not self.reason
            or self.preflight_digest != _digest(payload)
        ):
            raise E1FormationS1FMRealPathPreflightError(
                "S1-FM preflight changed or opened execution"
            )


def audit_e1_formation_s1fm_real_path_preflight(
    one_shot: E1FormationS1FHFreshCaptureOneShotContract,
    contract: E1FormationS1FKRealCoordinatorContract,
    source_preflight: E1FormationS1FIFreshCapturePreflight,
    inputs: E1FormationS1FIPreparedInputs,
) -> E1FormationS1FMRealPathPreflight:
    """Audit the bound real path without reading resources or running it."""

    if not isinstance(one_shot, E1FormationS1FHFreshCaptureOneShotContract):
        raise E1FormationS1FMRealPathPreflightError(
            "S1-FM requires the typed S1-FH contract"
        )
    if not isinstance(contract, E1FormationS1FKRealCoordinatorContract):
        raise E1FormationS1FMRealPathPreflightError(
            "S1-FM requires the typed S1-FK contract"
        )
    if not isinstance(source_preflight, E1FormationS1FIFreshCapturePreflight):
        raise E1FormationS1FMRealPathPreflightError(
            "S1-FM requires the typed S1-FI source preflight"
        )
    if not isinstance(inputs, E1FormationS1FIPreparedInputs):
        raise E1FormationS1FMRealPathPreflightError(
            "S1-FM requires the typed S1-FI inputs"
        )
    one_shot.__post_init__()
    contract.__post_init__()
    source_preflight.__post_init__()
    inputs.__post_init__()

    real_signature = tuple(inspect.signature(run_e1_formation_s1fl_once).parameters)
    real_source = inspect.getsource(run_e1_formation_s1fl_once)
    core_source = inspect.getsource(_coordinate_e1_formation_s1fl)
    audit_source = inspect.getsource(
        audit_e1_formation_s1fm_real_path_preflight
    )
    sequence_tokens = (
        "resources = resource_reader()",
        "immediate = preflight_e1_formation_s1fi_fresh_capture",
        "token = E1FormationS1FKOwnerAuthorizationToken",
        "token.consume()",
        "for ab_plan, ba_plan in zip",
        "capture = capture_e1_formation_s1ff_in_memory",
        "evaluation = evaluate_e1_formation_s1fd_state_convergence",
    )
    sequence_positions = tuple(core_source.find(token) for token in sequence_tokens)
    forbidden_audit_calls = {
        "read_e1_formation_s1fi_resource_snapshot",
        "run_e1_formation_s1fl_once",
        "run_small_five_arm_formation_in_memory",
        "capture_e1_formation_s1ff_in_memory",
        "evaluate_e1_formation_s1fd_state_convergence",
        "open",
        "write_text",
        "write_bytes",
    }
    result_fields = tuple(E1FormationS1FLCoordinatorResult.__dataclass_fields__)
    checks = (
        (
            S1_FM_CHECK_NAMES[0],
            contract.source_s1fh_contract_digest == one_shot.contract_digest,
        ),
        (
            S1_FM_CHECK_NAMES[1],
            contract.coordinator_implementation_permitted is True
            and contract.execution_permitted is False,
        ),
        (
            S1_FM_CHECK_NAMES[2],
            source_preflight.input_manifest_digest == inputs.input_manifest_digest
            and source_preflight.source_s1fh_contract_digest
            == one_shot.contract_digest,
        ),
        (
            S1_FM_CHECK_NAMES[3],
            source_preflight.technical_preflight_passed is True,
        ),
        (
            S1_FM_CHECK_NAMES[4],
            real_signature
            == (
                "contract",
                "one_shot",
                "source_preflight",
                "inputs",
                "authorization_text",
            ),
        ),
        (
            S1_FM_CHECK_NAMES[5],
            "read_e1_formation_s1fi_resource_snapshot" in real_source
            and "run_small_five_arm_formation_in_memory" in real_source
            and 'execution_mode="real"' in real_source,
        ),
        (
            S1_FM_CHECK_NAMES[6],
            all(position >= 0 for position in sequence_positions)
            and sequence_positions == tuple(sorted(sequence_positions)),
        ),
        (
            S1_FM_CHECK_NAMES[7],
            all(
                field_name in result_fields
                for field_name in (
                    "capture",
                    "evaluation",
                    "atomic_result_complete",
                    "result_digest",
                )
            ),
        ),
        (
            S1_FM_CHECK_NAMES[8],
            one_shot.formation_arm_count == 15
            and one_shot.maximum_formation_field_steps == 14_000
            and contract.maximum_formation_field_steps == 14_000,
        ),
        (
            S1_FM_CHECK_NAMES[9],
            all(
                value is False
                for value in (
                    contract.probe_execution_permitted,
                    contract.persistence_permitted,
                    contract.automatic_retry_permitted,
                    contract.posthoc_parameter_change_permitted,
                    contract.partial_result_return_permitted,
                    contract.memory_claim_permitted,
                )
            ),
        ),
        (
            S1_FM_CHECK_NAMES[10],
            contract.owner_authorization_present is False
            and source_preflight.owner_authorization_present is False,
        ),
        (
            S1_FM_CHECK_NAMES[11],
            _called_names(audit_source).isdisjoint(forbidden_audit_calls),
        ),
    )
    ready = all(value for _, value in checks)
    values = {
        "preflight_id": S1_FM_PREFLIGHT_ID,
        "source_s1fh_contract_digest": one_shot.contract_digest,
        "source_s1fk_contract_digest": contract.contract_digest,
        "source_s1fi_preflight_digest": source_preflight.preflight_digest,
        "source_input_manifest_digest": inputs.input_manifest_digest,
        "source_resource_snapshot_digest": source_preflight.resource_snapshot_digest,
        "source_s1fl_coordinator_id": S1_FL_COORDINATOR_ID,
        "real_entry": "run_e1_formation_s1fl_once",
        "refinements": ("r2", "r4", "r8"),
        "formation_arm_count": 15,
        "maximum_formation_field_steps": 14_000,
        "free_memory_bytes_at_source_preflight": source_preflight.free_memory_bytes,
        "minimum_free_memory_bytes": source_preflight.minimum_free_memory_bytes,
        "checks": checks,
        "technical_real_path_ready": ready,
        "source_resource_snapshot_point_in_time_only": True,
        "immediate_resource_recheck_required": True,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "field_execution_performed": False,
        "capture_performed": False,
        "probe_execution_performed": False,
        "persistence_performed": False,
        "automatic_retry_performed": False,
        "posthoc_parameter_change_performed": False,
        "memory_claim_permitted": False,
        "decision": (
            "REAL_PATH_TECHNICALLY_READY_AWAITING_EXPLICIT_OWNER_AUTHORIZATION"
            if ready
            else "REAL_PATH_PREFLIGHT_FAILED_EXECUTION_CLOSED"
        ),
        "reason": (
            "s1fl-real-path-bound-source-preflight-passed-authorization-absent"
            if ready
            else "one-or-more-static-real-path-gates-failed-execution-remains-closed"
        ),
    }
    return E1FormationS1FMRealPathPreflight(
        **values,
        preflight_digest=_digest(values),
    )
