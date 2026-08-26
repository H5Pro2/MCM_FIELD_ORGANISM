"""S1-EC37 static integration contract for quantitative P0 collection."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .e1_refined_formation_runner import _digest
from .e1_repetition_pilot_p0_identifiability_audit import (
    E1RepetitionPilotP0IdentifiabilityAudit,
    S1_EC35_DECISION,
)
from .e1_repetition_pilot_quantitative_p0_schema import (
    S1_EC36_SCHEMA_ID,
    quantitative_p0_schema_roles,
)
from .e1_repetition_pilot_release_contract import (
    E1RepetitionPilotReleaseContract,
)


class E1RepetitionPilotQuantitativeP0IntegrationContractError(ValueError):
    """Raised when S1-EC37 permits execution or weakens P0 measurement."""


S1_EC37_CONTRACT_ID = (
    "e1.repetition-pilot-quantitative-p0-integration.s1ec37.v1"
)
S1_EC37_EC29_CONTRACT_DIGEST = (
    "834b2280cd55d099fe81fd3c0ba506cb6924abea94d27495e42b4480e8d7aff8"
)
S1_EC37_EC35_AUDIT_DIGEST = (
    "9423c4425de44ceb311c7600f0fcf2d57d2100831b2603a812a307a6ff0e290b"
)
S1_EC37_P0_ROLES = ("p0_repeated", "p0_continuous")
S1_EC37_REQUIRED_SCHEMA_ROLES = (
    "neuron_ids",
    "repeated_snapshot_digest",
    "continuous_snapshot_digest",
    "activation_contrast",
    "afterimage_contrast",
    "activation_linf",
    "afterimage_linf",
)
S1_EC37_REQUIRED_GATES = (
    "ec29-matrix-exact",
    "ec35-identifiability-gap-exact",
    "ec36-quantitative-schema-exact",
    "two-fresh-p0-snapshots-per-batch",
    "snapshot-collection-before-field-discard",
    "component-order-bound-to-neuron-ids",
    "r2-r4-r8-profile-after-complete-contact-trio",
    "ec34-result-or-authorization-not-reused",
    "no-output-path-or-persistence",
    "no-execution-decision-or-claim",
)


@dataclass(frozen=True, slots=True)
class E1QuantitativeP0BatchHandoff:
    batch_index: int
    contact_count: int
    refinement_id: str
    step_count_per_p0_arm: int
    p0_roles: tuple[str, ...]
    snapshot_count: int

    def __post_init__(self) -> None:
        expected_index = (self.contact_count - 1) * 3 + (
            ("r2", "r4", "r8").index(self.refinement_id)
        )
        expected_steps = {
            1: {"r2": 202, "r4": 404, "r8": 808},
            2: {"r2": 402, "r4": 804, "r8": 1608},
        }
        if (
            self.contact_count not in expected_steps
            or self.batch_index != expected_index
            or self.step_count_per_p0_arm
            != expected_steps[self.contact_count][self.refinement_id]
            or self.p0_roles != S1_EC37_P0_ROLES
            or self.snapshot_count != 2
        ):
            raise E1RepetitionPilotQuantitativeP0IntegrationContractError(
                "S1-EC37 batch handoff changed"
            )


@dataclass(frozen=True, slots=True)
class E1RepetitionPilotQuantitativeP0IntegrationContract:
    contract_id: str
    source_ec29_contract_digest: str
    source_ec35_audit_digest: str
    p0_schema_id: str
    required_schema_roles: tuple[str, ...]
    handoffs: tuple[E1QuantitativeP0BatchHandoff, ...]
    required_gates: tuple[str, ...]
    total_p0_snapshot_count: int
    old_ec34_result_accepted: bool
    old_ec34_authorization_reusable: bool
    runner_implementation_permitted: bool
    field_execution_permitted: bool
    persistence_permitted: bool
    result_decision_permitted: bool
    memory_claim_permitted: bool
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != S1_EC37_CONTRACT_ID
            or self.source_ec29_contract_digest != S1_EC37_EC29_CONTRACT_DIGEST
            or self.source_ec35_audit_digest != S1_EC37_EC35_AUDIT_DIGEST
            or self.p0_schema_id != S1_EC36_SCHEMA_ID
            or self.required_schema_roles != S1_EC37_REQUIRED_SCHEMA_ROLES
            or tuple(item.batch_index for item in self.handoffs) != tuple(range(6))
            or self.required_gates != S1_EC37_REQUIRED_GATES
            or self.total_p0_snapshot_count != 12
            or self.runner_implementation_permitted is not True
            or any(
                value is not False
                for value in (
                    self.old_ec34_result_accepted,
                    self.old_ec34_authorization_reusable,
                    self.field_execution_permitted,
                    self.persistence_permitted,
                    self.result_decision_permitted,
                    self.memory_claim_permitted,
                )
            )
        ):
            raise E1RepetitionPilotQuantitativeP0IntegrationContractError(
                "S1-EC37 contract changed or released execution"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"handoffs", "contract_digest"}
        }
        payload["handoffs"] = tuple(asdict(item) for item in self.handoffs)
        if self.contract_digest != _digest(payload):
            raise E1RepetitionPilotQuantitativeP0IntegrationContractError(
                "S1-EC37 contract digest changed"
            )


def build_e1_repetition_pilot_quantitative_p0_integration_contract(
    pilot_contract: E1RepetitionPilotReleaseContract,
    gap_audit: E1RepetitionPilotP0IdentifiabilityAudit,
) -> E1RepetitionPilotQuantitativeP0IntegrationContract:
    """Bind future runner handoffs without accepting a run authorization."""

    if not isinstance(pilot_contract, E1RepetitionPilotReleaseContract):
        raise E1RepetitionPilotQuantitativeP0IntegrationContractError(
            "S1-EC37 requires the exact EC29 pilot contract"
        )
    if not isinstance(gap_audit, E1RepetitionPilotP0IdentifiabilityAudit):
        raise E1RepetitionPilotQuantitativeP0IntegrationContractError(
            "S1-EC37 requires the exact EC35 audit"
        )
    pilot_contract.__post_init__()
    gap_audit.__post_init__()
    schema_roles = quantitative_p0_schema_roles()
    if (
        pilot_contract.contract_digest != S1_EC37_EC29_CONTRACT_DIGEST
        or gap_audit.audit_digest != S1_EC37_EC35_AUDIT_DIGEST
        or gap_audit.decision != S1_EC35_DECISION
        or any(role not in schema_roles for role in S1_EC37_REQUIRED_SCHEMA_ROLES)
    ):
        raise E1RepetitionPilotQuantitativeP0IntegrationContractError(
            "S1-EC37 upstream evidence or schema changed"
        )
    handoffs = tuple(
        E1QuantitativeP0BatchHandoff(
            batch_index=batch.batch_index,
            contact_count=batch.contact_count,
            refinement_id=batch.refinement_id,
            step_count_per_p0_arm=batch.step_count_per_arm,
            p0_roles=S1_EC37_P0_ROLES,
            snapshot_count=2,
        )
        for batch in pilot_contract.batches
    )
    payload = {
        "contract_id": S1_EC37_CONTRACT_ID,
        "source_ec29_contract_digest": pilot_contract.contract_digest,
        "source_ec35_audit_digest": gap_audit.audit_digest,
        "p0_schema_id": S1_EC36_SCHEMA_ID,
        "required_schema_roles": S1_EC37_REQUIRED_SCHEMA_ROLES,
        "handoffs": tuple(asdict(item) for item in handoffs),
        "required_gates": S1_EC37_REQUIRED_GATES,
        "total_p0_snapshot_count": 12,
        "old_ec34_result_accepted": False,
        "old_ec34_authorization_reusable": False,
        "runner_implementation_permitted": True,
        "field_execution_permitted": False,
        "persistence_permitted": False,
        "result_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    digest = _digest(payload)
    payload["handoffs"] = handoffs
    return E1RepetitionPilotQuantitativeP0IntegrationContract(
        **payload,
        contract_digest=digest,
    )

