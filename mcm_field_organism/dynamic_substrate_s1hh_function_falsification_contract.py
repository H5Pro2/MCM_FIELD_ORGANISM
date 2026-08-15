"""S1-HH function and falsification contract for one dynamic substrate."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json


class DynamicSubstrateS1HHContractError(ValueError):
    """Raised when the S1-HH candidate or its falsification boundary changes."""


S1_HH_CONTRACT_ID = "dynamic-substrate.function-falsification.s1hh.v1"
S1_HH_SOURCE_S1HG_AUDIT_DIGEST = (
    "167ec53334d42a0f4038590930103b45fe431d9b6b43469e9d05b4d0c8c76dc6"
)
S1_HH_CANDIDATE_ID = "D1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HH_CANDIDATE_NAME = "lokaler dreistufiger Kantenressourcen-Umsatz"
S1_HH_RESOURCE_ROLES = (
    "free: locally available for engagement on an existing edge",
    "conductive-bound: engaged on an existing edge and able to alter its coupling",
    "refractory: locally retained but temporarily unavailable for engagement",
)
S1_HH_ALLOWED_TRANSFERS = (
    "free-to-conductive-bound only from current local field participation",
    "conductive-bound-to-refractory as continuous local turnover without a phase command",
    "refractory-to-free as continuous local recovery without a reset command",
)
S1_HH_BASELINE_PREDICTIONS = (
    (
        "fixed-adapter-and-frozen-e1",
        "no single adapter fixed before the probe reproduces all within-probe checkpoints, "
        "competitor effects, and recovery checkpoints",
    ),
    (
        "leaky-trace-and-integrator",
        "A-B-A differs from exposure-matched A-gap-A when B uses the same local resource "
        "pool, including after fitting the passive baseline across all arms",
    ),
    (
        "dynamic-two-state-e1",
        "states matched in S, H, conductive binding, and total resource but differing only "
        "in free-versus-refractory partition produce different next engagement capacity",
    ),
    (
        "f3-and-const-v",
        "a free-versus-refractory intervention at unchanged spatial total and unchanged "
        "fixed coupling changes the next response without resource transport",
    ),
    (
        "fast-afterimage",
        "the substrate effect remains measurable after H is matched or ablated while the "
        "resource partition is preserved",
    ),
)
S1_HH_REQUIRED_MEASUREMENTS = (
    "exact local and global free-plus-conductive-bound-plus-refractory ledger residual",
    "conductive response attenuation across repeated equal contacts",
    "A-probe difference between A-B-A and exposure-matched A-gap-A",
    "recovery of free resource and reuse on a competing adjacent edge",
    "within-probe substrate change and field-response checkpoints",
    "S/H-matched free-versus-refractory state intervention",
    "null-path identity with the candidate disabled",
)
S1_HH_FALSIFICATION_CONDITIONS = (
    "any resource creation, loss, negativity, clipping, or post-hoc normalization",
    "need for labels, rewards, counters, phase detection, reset, or target topology",
    "no measurable attenuation under repeated equal local contact",
    "no competitor-specific displacement beyond the matched passive-gap control",
    "no measured release into free resource and no later capacity reuse",
    "one pre-probe fixed adapter reproduces the complete candidate trajectory",
    "one registered leaky or integrator baseline reproduces all required profiles",
    "F3 or CONST-V reproduces all profiles and direct partition interventions",
    "the effect vanishes when fast H is matched while the substrate partition remains",
    "the free-versus-refractory intervention has no effect on next engagement capacity",
)
S1_HH_BLOCKED_CLAIMS = (
    "memory",
    "learning",
    "engram",
    "reconstruction",
    "semantics",
    "inner-context",
    "organization",
    "self-regulation",
    "new-natural-law",
    "organism",
    "artificial-intelligence",
)
S1_HH_DECISION = (
    "ONE_DYNAMIC_THREE_STATE_RESOURCE_CANDIDATE_BOUND_NO_EQUATION"
)


def _digest(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DynamicSubstrateS1HHFunctionFalsificationContract:
    contract_id: str
    source_s1hg_audit_digest: str
    candidate_count: int
    candidate_id: str
    candidate_name: str
    functional_hypothesis: str
    substrate_location: str
    resource_roles: tuple[str, ...]
    allowed_transfers: tuple[str, ...]
    baseline_predictions: tuple[tuple[str, str], ...]
    required_measurements: tuple[str, ...]
    falsification_conditions: tuple[str, ...]
    blocked_claims: tuple[str, ...]
    frozen_e1_branch_remains_stopped: bool
    equation_selected: bool
    parameters_selected: bool
    runtime_implemented: bool
    execution_permitted: bool
    field_steps_executed: int
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if (
            self.contract_id != S1_HH_CONTRACT_ID
            or self.source_s1hg_audit_digest != S1_HH_SOURCE_S1HG_AUDIT_DIGEST
            or self.candidate_count != 1
            or self.candidate_id != S1_HH_CANDIDATE_ID
            or self.candidate_name != S1_HH_CANDIDATE_NAME
            or not self.functional_hypothesis
            or not self.substrate_location
            or self.resource_roles != S1_HH_RESOURCE_ROLES
            or self.allowed_transfers != S1_HH_ALLOWED_TRANSFERS
            or self.baseline_predictions != S1_HH_BASELINE_PREDICTIONS
            or self.required_measurements != S1_HH_REQUIRED_MEASUREMENTS
            or self.falsification_conditions != S1_HH_FALSIFICATION_CONDITIONS
            or self.blocked_claims != S1_HH_BLOCKED_CLAIMS
            or self.frozen_e1_branch_remains_stopped is not True
            or any(
                value is not False
                for value in (
                    self.equation_selected,
                    self.parameters_selected,
                    self.runtime_implemented,
                    self.execution_permitted,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision != S1_HH_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DynamicSubstrateS1HHContractError(
                "S1-HH weakened the one-candidate or falsification boundary"
            )


def build_dynamic_substrate_s1hh_contract(
) -> DynamicSubstrateS1HHFunctionFalsificationContract:
    """Build the static contract without selecting or executing dynamics."""

    values = {
        "contract_id": S1_HH_CONTRACT_ID,
        "source_s1hg_audit_digest": S1_HH_SOURCE_S1HG_AUDIT_DIGEST,
        "candidate_count": 1,
        "candidate_id": S1_HH_CANDIDATE_ID,
        "candidate_name": S1_HH_CANDIDATE_NAME,
        "functional_hypothesis": (
            "one finite endpoint-local resource pool turns continuously between free, "
            "conductive-bound, and refractory roles; only the conductive-bound role "
            "changes an existing edge coupling, while turnover during contact causes "
            "attenuation and shared-pool competition and recovery restores reuse"
        ),
        "substrate_location": (
            "existing undirected MCM edges with finite pools shared only by incident "
            "edges at their existing endpoints; no new edge or global allocator"
        ),
        "resource_roles": S1_HH_RESOURCE_ROLES,
        "allowed_transfers": S1_HH_ALLOWED_TRANSFERS,
        "baseline_predictions": S1_HH_BASELINE_PREDICTIONS,
        "required_measurements": S1_HH_REQUIRED_MEASUREMENTS,
        "falsification_conditions": S1_HH_FALSIFICATION_CONDITIONS,
        "blocked_claims": S1_HH_BLOCKED_CLAIMS,
        "frozen_e1_branch_remains_stopped": True,
        "equation_selected": False,
        "parameters_selected": False,
        "runtime_implemented": False,
        "execution_permitted": False,
        "field_steps_executed": 0,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": S1_HH_DECISION,
    }
    return DynamicSubstrateS1HHFunctionFalsificationContract(
        **values,
        contract_digest=_digest(values),
    )
