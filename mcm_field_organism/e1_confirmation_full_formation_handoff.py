"""Private S1-EC14 complete full-formation result and state handoff schema."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .e1_confirmation_formation_runner import E1ConfirmationFormationArmAudit
from .e1_confirmation_full_formation_lifecycle import (
    E1PreparedFullFormationResult,
)
from .e1_confirmation_prepared_formation_consumer import S1_EC7_FORMATION_ARMS
from .e1_confirmation_prepared_real_formation_kernel import (
    E1PreparedRealFormationArmResult,
)
from .e1_confirmation_small_five_arm_formation import (
    E1SmallFiveArmFormationResult,
)
from .e1_frozen_state_transfer import (
    _load_state as _load_canonical_state,
    _state_payload as _canonical_state_payload,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationFullFormationHandoffError(ValueError):
    """Raised when the S1-EC14 state handoff payload is incomplete."""


S1_EC14_SCHEMA_ID = "e1.full-formation-handoff.s1ec14.v1"
S1_EC14_STATE_COUNT = 15
S1_EC14_EDGE_BINDING_COUNT = 2_175
S1_EC14_ATOMIC_PUBLICATION_SEQUENCE = (
    "write-complete-temporary-payload",
    "fsync-temporary-payload",
    "reread-and-verify-payload-digest",
    "exclusive-publish-final-report",
    "reread-and-verify-final-report",
    "remove-attempt-after-verification",
    "release-lock",
)
S1_EC14_PROBE_CANDIDATE_ROLES = tuple(
    f"r8:{arm}" for arm in S1_EC7_FORMATION_ARMS
)
S1_EC14_CONTRACT_DIGEST = _digest(
    {
        "schema_id": S1_EC14_SCHEMA_ID,
        "state_count": S1_EC14_STATE_COUNT,
        "edge_binding_count": S1_EC14_EDGE_BINDING_COUNT,
        "atomic_publication_sequence": S1_EC14_ATOMIC_PUBLICATION_SEQUENCE,
        "probe_candidate_roles": S1_EC14_PROBE_CANDIDATE_ROLES,
        "verified_payload_required_for_future_probe": True,
        "runtime_execution_permitted": False,
        "publication_permitted": False,
        "canonical_execution_permitted": False,
        "probe_execution_permitted": False,
        "claims_permitted": False,
    }
)


def _arm_payload(arm: E1PreparedRealFormationArmResult) -> dict[str, object]:
    return {
        "arm_id": arm.arm_id,
        "refinement_id": arm.refinement_id,
        "formation_enabled": arm.formation_enabled,
        "initial_field_digest": arm.initial_field_digest,
        "initial_state_digest": arm.initial_state_digest,
        "output_state": _canonical_state_payload(arm.output_state),
        "output_state_digest": arm.output_state_digest,
        "audit": asdict(arm.audit),
        "input_objects_preserved": arm.input_objects_preserved,
        "copied_inputs_used": arm.copied_inputs_used,
        "canonical_execution_permitted": arm.canonical_execution_permitted,
        "claims_permitted": arm.claims_permitted,
        "result_digest": arm.result_digest,
    }


def _refinement_payload(
    refinement: E1SmallFiveArmFormationResult,
) -> dict[str, object]:
    return {
        "refinement_id": refinement.refinement_id,
        "arms": [_arm_payload(item) for item in refinement.arms],
        "ab_identity_repeated": refinement.ab_identity_repeated,
        "ablation_states_neutral": refinement.ablation_states_neutral,
        "output_states_object_separated": (
            refinement.output_states_object_separated
        ),
        "history_backreaction_field_controls_equal": (
            refinement.history_backreaction_field_controls_equal
        ),
        "resource_budget_preserved": refinement.resource_budget_preserved,
        "prepared_inputs_preserved": refinement.prepared_inputs_preserved,
        "maximum_resource_budget_error": (
            refinement.maximum_resource_budget_error
        ),
        "canonical_execution_permitted": (
            refinement.canonical_execution_permitted
        ),
        "claims_permitted": refinement.claims_permitted,
        "result_digest": refinement.result_digest,
    }


def _result_payload(result: E1PreparedFullFormationResult) -> dict[str, object]:
    return {
        "execution_id": result.execution_id,
        "run_contract_digest": result.run_contract_digest,
        "bundle_digest": result.bundle_digest,
        "pre_attempt_preflight_digest": result.pre_attempt_preflight_digest,
        "in_attempt_preflight_digest": result.in_attempt_preflight_digest,
        "refinements": [_refinement_payload(item) for item in result.refinements],
        "refinement_step_counts": result.refinement_step_counts,
        "history_state_distances": result.history_state_distances,
        "r2_r4_state_residual": result.r2_r4_state_residual,
        "r4_r8_state_residual": result.r4_r8_state_residual,
        "convergence_nonincreasing": result.convergence_nonincreasing,
        "attempt_present_during_execution": (
            result.attempt_present_during_execution
        ),
        "all_five_arm_controls_passed": (
            result.all_five_arm_controls_passed
        ),
        "prepared_inputs_preserved": result.prepared_inputs_preserved,
        "real_field_kernels_executed": result.real_field_kernels_executed,
        "full_prepared_formation_executed": (
            result.full_prepared_formation_executed
        ),
        "temporary_lifecycle_only": result.temporary_lifecycle_only,
        "canonical_execution_permitted": result.canonical_execution_permitted,
        "probe_execution_permitted": result.probe_execution_permitted,
        "claims_permitted": result.claims_permitted,
        "result_digest": result.result_digest,
    }


@dataclass(frozen=True, slots=True)
class E1FullFormationHandoffEnvelope:
    payload: dict[str, object]
    contract_digest: str
    payload_digest: str
    state_count: int
    edge_binding_count: int
    atomic_publication_sequence: tuple[str, ...]
    probe_candidate_roles: tuple[str, ...]
    verified_payload_required_for_future_probe: bool
    runtime_execution_permitted: bool
    publication_permitted: bool
    canonical_execution_permitted: bool
    probe_execution_permitted: bool
    claims_permitted: bool

    def __post_init__(self) -> None:
        payload = dict(self.payload)
        if (
            payload.get("schema_id") != S1_EC14_SCHEMA_ID
            or self.contract_digest != S1_EC14_CONTRACT_DIGEST
            or payload.get("contract_digest") != self.contract_digest
            or self.payload_digest != _digest(payload)
            or self.state_count != S1_EC14_STATE_COUNT
            or self.edge_binding_count != S1_EC14_EDGE_BINDING_COUNT
            or self.atomic_publication_sequence
            != S1_EC14_ATOMIC_PUBLICATION_SEQUENCE
            or self.probe_candidate_roles != S1_EC14_PROBE_CANDIDATE_ROLES
            or self.verified_payload_required_for_future_probe is not True
            or self.runtime_execution_permitted is not False
            or self.publication_permitted is not False
            or self.canonical_execution_permitted is not False
            or self.probe_execution_permitted is not False
            or self.claims_permitted is not False
        ):
            raise E1ConfirmationFullFormationHandoffError(
                "S1-EC14 handoff envelope changed"
            )
        object.__setattr__(self, "payload", payload)


def build_full_formation_handoff_envelope(
    result: E1PreparedFullFormationResult,
) -> E1FullFormationHandoffEnvelope:
    """Serialize one live full result completely without publishing it."""

    if not isinstance(result, E1PreparedFullFormationResult):
        raise E1ConfirmationFullFormationHandoffError(
            "S1-EC14 requires one complete live full-formation result"
        )
    result.__post_init__()
    state_count = sum(len(item.arms) for item in result.refinements)
    edge_count = sum(
        len(arm.output_state.edge_bindings)
        for refinement in result.refinements
        for arm in refinement.arms
    )
    if (
        state_count != S1_EC14_STATE_COUNT
        or edge_count != S1_EC14_EDGE_BINDING_COUNT
    ):
        raise E1ConfirmationFullFormationHandoffError(
            "S1-EC14 requires all 15 complete 145-edge states"
        )
    payload = {
        "schema_id": S1_EC14_SCHEMA_ID,
        "contract_digest": S1_EC14_CONTRACT_DIGEST,
        "result": _result_payload(result),
        "state_count": state_count,
        "edge_binding_count": edge_count,
        "atomic_publication_sequence": S1_EC14_ATOMIC_PUBLICATION_SEQUENCE,
        "probe_candidate_roles": S1_EC14_PROBE_CANDIDATE_ROLES,
        "verified_payload_required_for_future_probe": True,
        "runtime_execution_permitted": False,
        "publication_permitted": False,
        "canonical_execution_permitted": False,
        "probe_execution_permitted": False,
        "claims_permitted": False,
    }
    return E1FullFormationHandoffEnvelope(
        payload=payload,
        contract_digest=S1_EC14_CONTRACT_DIGEST,
        payload_digest=_digest(payload),
        state_count=state_count,
        edge_binding_count=edge_count,
        atomic_publication_sequence=S1_EC14_ATOMIC_PUBLICATION_SEQUENCE,
        probe_candidate_roles=S1_EC14_PROBE_CANDIDATE_ROLES,
        verified_payload_required_for_future_probe=True,
        runtime_execution_permitted=False,
        publication_permitted=False,
        canonical_execution_permitted=False,
        probe_execution_permitted=False,
        claims_permitted=False,
    )


def _load_arm(payload: Any, role: str) -> E1PreparedRealFormationArmResult:
    if not isinstance(payload, dict):
        raise E1ConfirmationFullFormationHandoffError(
            f"S1-EC14 {role} arm payload is invalid"
        )
    try:
        audit_payload = payload["audit"]
        if not isinstance(audit_payload, dict):
            raise TypeError
        return E1PreparedRealFormationArmResult(
            arm_id=payload["arm_id"],
            refinement_id=payload["refinement_id"],
            formation_enabled=payload["formation_enabled"],
            initial_field_digest=payload["initial_field_digest"],
            initial_state_digest=payload["initial_state_digest"],
            output_state=_load_canonical_state(payload["output_state"], role),
            output_state_digest=payload["output_state_digest"],
            audit=E1ConfirmationFormationArmAudit(**audit_payload),
            input_objects_preserved=payload["input_objects_preserved"],
            copied_inputs_used=payload["copied_inputs_used"],
            canonical_execution_permitted=payload[
                "canonical_execution_permitted"
            ],
            claims_permitted=payload["claims_permitted"],
            result_digest=payload["result_digest"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise E1ConfirmationFullFormationHandoffError(
            f"S1-EC14 {role} arm payload is invalid"
        ) from exc


def _load_refinement(payload: Any) -> E1SmallFiveArmFormationResult:
    if not isinstance(payload, dict) or not isinstance(payload.get("arms"), list):
        raise E1ConfirmationFullFormationHandoffError(
            "S1-EC14 refinement payload is invalid"
        )
    try:
        arms = tuple(
            _load_arm(item, f"{payload['refinement_id']}:{index}")
            for index, item in enumerate(payload["arms"])
        )
        return E1SmallFiveArmFormationResult(
            refinement_id=payload["refinement_id"],
            arms=arms,
            ab_identity_repeated=payload["ab_identity_repeated"],
            ablation_states_neutral=payload["ablation_states_neutral"],
            output_states_object_separated=payload[
                "output_states_object_separated"
            ],
            history_backreaction_field_controls_equal=payload[
                "history_backreaction_field_controls_equal"
            ],
            resource_budget_preserved=payload["resource_budget_preserved"],
            prepared_inputs_preserved=payload["prepared_inputs_preserved"],
            maximum_resource_budget_error=payload[
                "maximum_resource_budget_error"
            ],
            canonical_execution_permitted=payload[
                "canonical_execution_permitted"
            ],
            claims_permitted=payload["claims_permitted"],
            result_digest=payload["result_digest"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise E1ConfirmationFullFormationHandoffError(
            "S1-EC14 refinement payload is invalid"
        ) from exc


def load_full_formation_handoff_payload(
    payload: object,
) -> E1PreparedFullFormationResult:
    """Round-trip all 15 states from a future verified report payload."""

    if not isinstance(payload, dict) or payload.get("schema_id") != S1_EC14_SCHEMA_ID:
        raise E1ConfirmationFullFormationHandoffError(
            "S1-EC14 top-level payload is invalid"
        )
    expected_keys = {
        "schema_id",
        "contract_digest",
        "result",
        "state_count",
        "edge_binding_count",
        "atomic_publication_sequence",
        "probe_candidate_roles",
        "verified_payload_required_for_future_probe",
        "runtime_execution_permitted",
        "publication_permitted",
        "canonical_execution_permitted",
        "probe_execution_permitted",
        "claims_permitted",
    }
    if set(payload) != expected_keys:
        raise E1ConfirmationFullFormationHandoffError(
            "S1-EC14 top-level payload inventory changed"
        )
    if (
        payload["state_count"] != S1_EC14_STATE_COUNT
        or payload["contract_digest"] != S1_EC14_CONTRACT_DIGEST
        or payload["edge_binding_count"] != S1_EC14_EDGE_BINDING_COUNT
        or tuple(payload["atomic_publication_sequence"])
        != S1_EC14_ATOMIC_PUBLICATION_SEQUENCE
        or tuple(payload["probe_candidate_roles"])
        != S1_EC14_PROBE_CANDIDATE_ROLES
        or payload["verified_payload_required_for_future_probe"] is not True
        or any(
            payload[role] is not False
            for role in (
                "runtime_execution_permitted",
                "publication_permitted",
                "canonical_execution_permitted",
                "probe_execution_permitted",
                "claims_permitted",
            )
        )
    ):
        raise E1ConfirmationFullFormationHandoffError(
            "S1-EC14 top-level controls changed"
        )
    result = payload["result"]
    if not isinstance(result, dict) or not isinstance(result.get("refinements"), list):
        raise E1ConfirmationFullFormationHandoffError(
            "S1-EC14 result payload is invalid"
        )
    try:
        loaded = E1PreparedFullFormationResult(
            execution_id=result["execution_id"],
            run_contract_digest=result["run_contract_digest"],
            bundle_digest=result["bundle_digest"],
            pre_attempt_preflight_digest=result[
                "pre_attempt_preflight_digest"
            ],
            in_attempt_preflight_digest=result["in_attempt_preflight_digest"],
            refinements=tuple(
                _load_refinement(item) for item in result["refinements"]
            ),
            refinement_step_counts=tuple(
                tuple(item) for item in result["refinement_step_counts"]
            ),
            history_state_distances=tuple(
                (item[0], item[1]) for item in result["history_state_distances"]
            ),
            r2_r4_state_residual=result["r2_r4_state_residual"],
            r4_r8_state_residual=result["r4_r8_state_residual"],
            convergence_nonincreasing=result["convergence_nonincreasing"],
            attempt_present_during_execution=result[
                "attempt_present_during_execution"
            ],
            all_five_arm_controls_passed=result[
                "all_five_arm_controls_passed"
            ],
            prepared_inputs_preserved=result["prepared_inputs_preserved"],
            real_field_kernels_executed=result["real_field_kernels_executed"],
            full_prepared_formation_executed=result[
                "full_prepared_formation_executed"
            ],
            temporary_lifecycle_only=result["temporary_lifecycle_only"],
            canonical_execution_permitted=result[
                "canonical_execution_permitted"
            ],
            probe_execution_permitted=result["probe_execution_permitted"],
            claims_permitted=result["claims_permitted"],
            result_digest=result["result_digest"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise E1ConfirmationFullFormationHandoffError(
            "S1-EC14 result payload cannot be reconstructed"
        ) from exc
    state_count = sum(len(item.arms) for item in loaded.refinements)
    edge_count = sum(
        len(arm.output_state.edge_bindings)
        for refinement in loaded.refinements
        for arm in refinement.arms
    )
    if (
        state_count != payload["state_count"]
        or edge_count != payload["edge_binding_count"]
    ):
        raise E1ConfirmationFullFormationHandoffError(
            "S1-EC14 reconstructed state inventory changed"
        )
    return loaded
