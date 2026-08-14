"""S1-FG static insertion contract for a future fresh formation run."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_confirmation_full_formation_lifecycle import (
    E1PreparedFullFormationResult,
    consume_prepared_full_formation,
)
from .e1_confirmation_full_published_run_contract import S1_EC16_TRANSITIONS
from .e1_confirmation_prepared_formation_consumer import (
    S1_EC7_FORMATION_ARMS,
    S1_EC7_REFINEMENTS,
)
from .e1_confirmation_small_five_arm_formation import (
    E1SmallFiveArmFormationResult,
)
from .e1_formation_s1ff_in_memory_capture_adapter import S1_FF_ADAPTER_ID
from .e1_refined_formation_runner import _digest


class E1FormationS1FGFreshRunInsertionContractError(ValueError):
    """Raised when the fresh-run insertion boundary changes."""


S1_FG_CONTRACT_ID = "e1.formation-fresh-run-insertion-contract.s1fg.v1"
S1_FG_PREDECESSOR = "execute-full-r2-r4-r8-five-arm-formation"
S1_FG_SUCCESSOR = "build-complete-s1ec14-payload-while-states-are-live"
S1_FG_INSERTION_SEQUENCE = (
    "validate-fresh-full-formation-result",
    "flatten-r2-r4-r8-five-arm-results-in-canonical-order",
    "capture-fifteen-results-with-s1ff-in-memory",
    "evaluate-captured-vectors-with-s1fd-before-probe",
    "bind-diagnostic-digests-to-future-fresh-run-result",
)
S1_FG_FRESH_RUN_REQUIREMENTS = (
    "new-run-identity",
    "new-owner-authorization",
    "fresh-unconsumed-attempt-lock-and-report-paths-if-persistence-is-later-approved",
    "new-pre-attempt-and-in-attempt-resource-checks",
    "no-historical-result-or-authorization-reuse",
    "formation-only-until-capture-and-diagnostic-return-complete",
)
S1_FG_CHECK_NAMES = (
    "full-result-carries-three-refinements",
    "refinement-result-carries-five-arms",
    "source-formation-completes-before-return",
    "fifteen-arm-flattening-is-canonical",
    "ec16-reference-transitions-are-adjacent",
    "s1ff-adapter-is-bound",
    "insertion-is-before-handoff-and-probe",
    "historical-run-is-reference-only",
    "audit-does-not-run-formation-capture-probe-or-writer",
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
class E1FormationS1FGFreshRunInsertionContract:
    contract_id: str
    source_full_result_type: str
    source_refinement_result_type: str
    source_refinements: tuple[tuple[str, int], ...]
    source_formation_arms: tuple[str, ...]
    required_flat_result_count: int
    source_full_result_schema: tuple[str, ...]
    source_refinement_result_schema: tuple[str, ...]
    s1ff_adapter_id: str
    reference_predecessor_transition: str
    reference_successor_transition: str
    insertion_sequence: tuple[str, ...]
    flattening_rule: str
    fresh_run_requirements: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    historical_ec16_used_as_architecture_reference_only: bool
    fresh_run_contract_required: bool
    new_owner_authorization_required: bool
    formation_execution_permitted: bool
    capture_execution_permitted: bool
    probe_execution_permitted: bool
    persistence_permitted: bool
    historical_artifact_reuse_permitted: bool
    historical_authorization_reuse_permitted: bool
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
            self.contract_id != S1_FG_CONTRACT_ID
            or self.source_full_result_type != "E1PreparedFullFormationResult"
            or self.source_refinement_result_type
            != "E1SmallFiveArmFormationResult"
            or self.source_refinements != S1_EC7_REFINEMENTS
            or self.source_formation_arms != S1_EC7_FORMATION_ARMS
            or self.required_flat_result_count != 15
            or "refinements" not in self.source_full_result_schema
            or "arms" not in self.source_refinement_result_schema
            or self.s1ff_adapter_id != S1_FF_ADAPTER_ID
            or self.reference_predecessor_transition != S1_FG_PREDECESSOR
            or self.reference_successor_transition != S1_FG_SUCCESSOR
            or self.insertion_sequence != S1_FG_INSERTION_SEQUENCE
            or self.flattening_rule
            != "refinement-major:r2-r4-r8;arm-minor:ab-ba-ab_identity-ab_formation_ablated-ba_formation_ablated"
            or self.fresh_run_requirements != S1_FG_FRESH_RUN_REQUIREMENTS
            or tuple(name for name, _ in self.checks) != S1_FG_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.historical_ec16_used_as_architecture_reference_only,
                    self.fresh_run_contract_required,
                    self.new_owner_authorization_required,
                )
            )
            or any(
                value is not False
                for value in (
                    self.formation_execution_permitted,
                    self.capture_execution_permitted,
                    self.probe_execution_permitted,
                    self.persistence_permitted,
                    self.historical_artifact_reuse_permitted,
                    self.historical_authorization_reuse_permitted,
                    self.memory_claim_permitted,
                )
            )
            or self.decision
            != "INSERTION_POINT_BOUND_FRESH_RUN_CONTRACT_MISSING"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1FGFreshRunInsertionContractError(
                "S1-FG insertion contract changed or reused historical authority"
            )


def audit_e1_formation_s1fg_fresh_run_insertion_contract(
) -> E1FormationS1FGFreshRunInsertionContract:
    """Locate the future insertion point without executing either side."""

    audit_source = inspect.getsource(
        audit_e1_formation_s1fg_fresh_run_insertion_contract
    )
    formation_source = inspect.getsource(consume_prepared_full_formation)
    full_fields = tuple(E1PreparedFullFormationResult.__dataclass_fields__)
    refinement_fields = tuple(E1SmallFiveArmFormationResult.__dataclass_fields__)
    predecessor_index = S1_EC16_TRANSITIONS.index(S1_FG_PREDECESSOR)
    successor_index = S1_EC16_TRANSITIONS.index(S1_FG_SUCCESSOR)
    forbidden_calls = {
        "consume_prepared_full_formation",
        "run_small_five_arm_formation_in_memory",
        "capture_e1_formation_s1ff_in_memory",
        "evaluate_e1_formation_s1fd_state_convergence",
        "build_full_formation_handoff_envelope",
        "run_full_persistent_probe",
        "write_text",
        "write_bytes",
        "open",
    }
    checks = (
        (
            S1_FG_CHECK_NAMES[0],
            "refinements" in full_fields
            and "refinements = tuple(formed)" in formation_source,
        ),
        (S1_FG_CHECK_NAMES[1], "arms" in refinement_fields),
        (
            S1_FG_CHECK_NAMES[2],
            formation_source.index("refinements = tuple(formed)")
            < formation_source.index("return E1PreparedFullFormationResult"),
        ),
        (
            S1_FG_CHECK_NAMES[3],
            len(S1_EC7_REFINEMENTS) * len(S1_EC7_FORMATION_ARMS) == 15,
        ),
        (
            S1_FG_CHECK_NAMES[4],
            successor_index == predecessor_index + 1,
        ),
        (S1_FG_CHECK_NAMES[5], bool(S1_FF_ADAPTER_ID)),
        (
            S1_FG_CHECK_NAMES[6],
            "before-probe" in S1_FG_INSERTION_SEQUENCE[3],
        ),
        (S1_FG_CHECK_NAMES[7], True),
        (
            S1_FG_CHECK_NAMES[8],
            _called_names(audit_source).isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "contract_id": S1_FG_CONTRACT_ID,
        "source_full_result_type": "E1PreparedFullFormationResult",
        "source_refinement_result_type": "E1SmallFiveArmFormationResult",
        "source_refinements": S1_EC7_REFINEMENTS,
        "source_formation_arms": S1_EC7_FORMATION_ARMS,
        "required_flat_result_count": 15,
        "source_full_result_schema": full_fields,
        "source_refinement_result_schema": refinement_fields,
        "s1ff_adapter_id": S1_FF_ADAPTER_ID,
        "reference_predecessor_transition": S1_FG_PREDECESSOR,
        "reference_successor_transition": S1_FG_SUCCESSOR,
        "insertion_sequence": S1_FG_INSERTION_SEQUENCE,
        "flattening_rule": (
            "refinement-major:r2-r4-r8;arm-minor:ab-ba-ab_identity-"
            "ab_formation_ablated-ba_formation_ablated"
        ),
        "fresh_run_requirements": S1_FG_FRESH_RUN_REQUIREMENTS,
        "checks": checks,
        "historical_ec16_used_as_architecture_reference_only": True,
        "fresh_run_contract_required": True,
        "new_owner_authorization_required": True,
        "formation_execution_permitted": False,
        "capture_execution_permitted": False,
        "probe_execution_permitted": False,
        "persistence_permitted": False,
        "historical_artifact_reuse_permitted": False,
        "historical_authorization_reuse_permitted": False,
        "memory_claim_permitted": False,
        "decision": "INSERTION_POINT_BOUND_FRESH_RUN_CONTRACT_MISSING",
        "reason": (
            "all-fifteen-live-results-exist-after-full-formation-return-and-"
            "before-s1ec14-handoff;fresh-run-contract-and-authorization-required"
        ),
    }
    return E1FormationS1FGFreshRunInsertionContract(
        **values,
        contract_digest=_digest(values),
    )
