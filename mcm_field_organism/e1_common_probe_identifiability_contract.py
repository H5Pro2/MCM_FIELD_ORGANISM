"""S1-EC45 static common-probe identifiability contract after EC44."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_refined_formation_runner import _digest


class E1CommonProbeIdentifiabilityContractError(ValueError):
    """Raised when EC45 permits a cross-space comparison or an execution."""


S1_EC45_CONTRACT_ID = "e1.common-probe-identifiability.s1ec45.v1"
S1_EC45_EC44_RUN_ID = "e1.repetition-pilot-quantitative-once.s1ec44.v1"
S1_EC45_EC44_RESULT_DIGEST = (
    "4de5d99e3a7c477520dffa120a3f74eac07aa8798fa9e9aad14a9af4141393a9"
)
S1_EC45_FORMATION_SPACES = (
    "p0-terminal-field:ordered-activation-and-afterimage",
    "e1-formed-substrate:ordered-edge-bindings",
)
S1_EC45_PROBE_ROLES = (
    "p0-reset-ab",
    "p0-reset-ba",
    "e1-active-ab",
    "e1-active-ba",
    "e1-probe-feedback-ablated-ab",
    "e1-probe-feedback-ablated-ba",
    "e1-formation-ablated-ab",
    "e1-formation-ablated-ba",
)
S1_EC45_REQUIRED_CONTRASTS = (
    "p0-reset-order",
    "e1-active-order",
    "e1-probe-feedback-ablated-order",
    "e1-formation-ablated-order",
    "ab-active-vs-probe-feedback-ablated",
    "ba-active-vs-probe-feedback-ablated",
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeIdentifiabilityContract:
    contract_id: str
    source_run_id: str
    source_result_digest: str
    source_evidence_scope: str
    formation_spaces: tuple[str, ...]
    direct_cross_space_subtraction_permitted: bool
    common_observation_space: str
    probe_roles: tuple[str, ...]
    required_contrasts: tuple[str, ...]
    identical_reset_field_required: bool
    identical_probe_required: bool
    identical_neuron_order_required: bool
    identical_probe_steps_required: bool
    frozen_formed_state_required: bool
    p0_reset_order_is_sanity_control: bool
    feedback_ablation_is_causal_control: bool
    formation_ablation_is_causal_control: bool
    refinement_profile_required: bool
    numerical_acceptance_bound_pre_registered: bool
    implementation_permitted: bool
    field_execution_permitted: bool
    persistence_permitted: bool
    result_decision_permitted: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != S1_EC45_CONTRACT_ID
            or self.source_run_id != S1_EC45_EC44_RUN_ID
            or self.source_result_digest != S1_EC45_EC44_RESULT_DIGEST
            or self.source_evidence_scope
            != "technical-scalar-summary-only-no-raw-result-reconstruction"
            or self.formation_spaces != S1_EC45_FORMATION_SPACES
            or self.direct_cross_space_subtraction_permitted is not False
            or self.common_observation_space
            != "post-reset-common-probe:ordered-activation-and-afterimage"
            or self.probe_roles != S1_EC45_PROBE_ROLES
            or self.required_contrasts != S1_EC45_REQUIRED_CONTRASTS
            or any(value is not True for value in (
                self.identical_reset_field_required,
                self.identical_probe_required,
                self.identical_neuron_order_required,
                self.identical_probe_steps_required,
                self.frozen_formed_state_required,
                self.p0_reset_order_is_sanity_control,
                self.feedback_ablation_is_causal_control,
                self.formation_ablation_is_causal_control,
                self.refinement_profile_required,
                self.implementation_permitted,
            ))
            or any(value is not False for value in (
                self.numerical_acceptance_bound_pre_registered,
                self.field_execution_permitted,
                self.persistence_permitted,
                self.result_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.decision
            != "COMMON_PROBE_IDENTIFIABLE_ACCEPTANCE_BOUND_MISSING"
            or not self.reason
        ):
            raise E1CommonProbeIdentifiabilityContractError(
                "S1-EC45 changed or crossed its static identifiability scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if self.contract_digest != _digest(payload):
            raise E1CommonProbeIdentifiabilityContractError(
                "S1-EC45 contract digest changed"
            )


def build_e1_common_probe_identifiability_contract(
) -> E1CommonProbeIdentifiabilityContract:
    """Define the first comparable E1/P0 outcome without running a field."""

    values = {
        "contract_id": S1_EC45_CONTRACT_ID,
        "source_run_id": S1_EC45_EC44_RUN_ID,
        "source_result_digest": S1_EC45_EC44_RESULT_DIGEST,
        "source_evidence_scope": (
            "technical-scalar-summary-only-no-raw-result-reconstruction"
        ),
        "formation_spaces": S1_EC45_FORMATION_SPACES,
        "direct_cross_space_subtraction_permitted": False,
        "common_observation_space": (
            "post-reset-common-probe:ordered-activation-and-afterimage"
        ),
        "probe_roles": S1_EC45_PROBE_ROLES,
        "required_contrasts": S1_EC45_REQUIRED_CONTRASTS,
        "identical_reset_field_required": True,
        "identical_probe_required": True,
        "identical_neuron_order_required": True,
        "identical_probe_steps_required": True,
        "frozen_formed_state_required": True,
        "p0_reset_order_is_sanity_control": True,
        "feedback_ablation_is_causal_control": True,
        "formation_ablation_is_causal_control": True,
        "refinement_profile_required": True,
        "numerical_acceptance_bound_pre_registered": False,
        "implementation_permitted": True,
        "field_execution_permitted": False,
        "persistence_permitted": False,
        "result_decision_permitted": False,
        "memory_claim_permitted": False,
        "decision": "COMMON_PROBE_IDENTIFIABLE_ACCEPTANCE_BOUND_MISSING",
        "reason": (
            "formation-states-are-incommensurate;compare-only-post-reset-"
            "common-probe-vectors;bind-numerical-acceptance-before-execution"
        ),
    }
    return E1CommonProbeIdentifiabilityContract(
        **values,
        contract_digest=_digest(values),
    )
