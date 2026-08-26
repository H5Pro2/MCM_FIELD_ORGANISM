"""S1-HU static audit of one causal DTS-1 coupling and commit order."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1HUCouplingOrderAuditError(ValueError):
    """Raised when the one-order S1-HU audit boundary is weakened."""


S1_HU_AUDIT_ID = "dynamic-substrate.coupling-order-audit.s1hu.v1"
S1_HU_SOURCE_S1HT_RECEIPT_DIGEST = (
    "5440ae81fa62b02f18eb0e79a7d195f6564b2dcea3e43680b9087394cfe5dd5a"
)
S1_HU_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HU_ORDER_ID = "CLOSED_PRESTATE_PARALLEL_READ_ATOMIC_COMMIT"
S1_HU_CLOSED_PRESTATE = (
    ("L_n", "complete immutable MCM layer containing closed S_n and H_n"),
    ("A_n", "complete immutable valid DTS1ResourceAnatomy"),
    ("W_n", "one explicit closed physical contact interval"),
    ("C", "fixed technical configs rates and strict ablation control"),
)
S1_HU_STAGE_ORDER = (
    "validate-complete-shared-geometry-time-and-config-prestate",
    "derive-p_n-from-S_n-only-for-every-existing-edge",
    "derive-active-or-ablated-G_n-from-A_n-only",
    "compute-A_next-from-A_n-p_n-and-Delta_t-with-s1hp",
    "compute-L_next-from-L_n-W_n-G_n-and-unchanged-fast-field-boundaries",
    "validate-both-complete-proposals-without-mutating-either-prestate",
    "atomically-commit-pair-L_next-A_next-or-return-no-output",
)
S1_HU_CAUSAL_IDENTITIES = (
    "p_n-never-reads-S_next-or-H_next",
    "G_n-never-reads-A_next",
    "resource-proposal-never-reads-L_next",
    "field-proposal-never-reads-A_next",
    "new-binding-affects-the-field-no-earlier-than-the-next-substep",
    "new-field-values-affect-participation-no-earlier-than-the-next-substep",
    "zero-duration-is-exact-pair-identity-without-proposal-calls",
)
S1_HU_ABLATION_IDENTITIES = (
    "P0-delegates-bit-exactly-to-existing-neutral-field-path-without-dts1-arithmetic",
    "A0-evolves-dts1-but-delegates-field-proposal-to-the-exact-P0-path",
    "A1-and-A0-from-identical-prestate-produce-identical-A_next-in-that-substep",
    "A1-with-zero-prestate-binding-produces-the-same-first-field-proposal-as-A0",
    "A1-and-A0-may-diverge-in-later-A-states-only-through-prior-field-divergence",
    "F0-never-updates-its-pre-probe-frozen-edge-rate-ledger",
)
S1_HU_REFINEMENT_OBLIGATIONS = (
    "s1hq-n-2n-4n-use-identical-physical-input-and-event-boundaries",
    "every-substep-recomputes-p_n-and-G_n-from-its-own-closed-prestate",
    "coarse-versus-fine-complete-pair-residual-must-decrease-before-use",
    "one-substep-reader-latency-must-shrink-under-refinement",
    "failure-of-refinement-stops-coupled-runtime-work",
)
S1_HU_REJECTED_ORDERS = (
    (
        "resource-first-poststate-reader",
        "reject because A_next would act over the interval that produced it",
    ),
    (
        "field-first-endstate-participation",
        "reject because S_next would drive resource transfer over its preceding interval",
    ),
    (
        "midpoint-half-resource-full-field-half-resource",
        "reserve because it adds a second resource source state beyond the first corridor",
    ),
    (
        "implicit-iterated-coupled-solve",
        "reject because solver tolerance and iteration add unregistered freedoms",
    ),
    (
        "call-order-partial-commit",
        "reject because a failed second proposal could leave a mixed state",
    ),
)
S1_HU_FAIL_CLOSED_CONDITIONS = (
    "field-anatomy-edge-or-node-geometry-mismatch",
    "time-contact-or-configuration-contract-mismatch",
    "nonfinite-invalid-or-out-of-domain-participation-rate-state-or-proposal",
    "resource-ledger-positivity-or-field-range-violation",
    "attempted-poststate-read-within-the-same-substep",
    "partial-proposal-mutation-or-partial-commit",
    "p0-or-a0-deviation-from-the-existing-exact-neutral-field-path",
    "failed-n-2n-4n-complete-pair-refinement",
)
S1_HU_AUDIT_CHECKS = (
    "exactly-one-coupling-order",
    "both-proposals-read-one-shared-closed-prestate",
    "s1hp-resource-step-and-s1ht-reader-remain-separate-pure-kernels",
    "explicit-one-substep-latency-is-causal-and-testable",
    "atomic-pair-commit-prevents-mixed-field-anatomy-state",
    "p0-and-a0-exact-neutral-identities-remain-mandatory",
    "first-order-coupling-requires-refinement-before-runtime-use",
    "no-functional-effect-or-baseline-separation-is-inferred",
)
S1_HU_DECISION = "ZULASSEN_DTS1_CLOSED_PRESTATE_PARALLEL_READ_ATOMIC_COMMIT"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1HUCouplingOrderAudit:
    audit_id: str
    source_s1ht_receipt_digest: str
    candidate_id: str
    audited_order_count: int
    order_id: str
    closed_prestate: tuple[tuple[str, str], ...]
    stage_order: tuple[str, ...]
    causal_identities: tuple[str, ...]
    ablation_identities: tuple[str, ...]
    refinement_obligations: tuple[str, ...]
    rejected_orders: tuple[tuple[str, str], ...]
    fail_closed_conditions: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    one_closed_prestate_for_both_proposals: bool
    explicit_one_substep_latency: bool
    atomic_pair_commit_required: bool
    exact_p0_a0_field_identity_required: bool
    first_order_coupling_only: bool
    coupling_order_selected: bool
    field_integrator_selected: bool
    coupled_step_implemented: bool
    material_rate_values_selected: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    field_steps_executed: int
    functional_effect_proven: bool
    claims_permitted: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_HU_AUDIT_ID
            or self.source_s1ht_receipt_digest
            != S1_HU_SOURCE_S1HT_RECEIPT_DIGEST
            or self.candidate_id != S1_HU_CANDIDATE_ID
            or self.audited_order_count != 1
            or self.order_id != S1_HU_ORDER_ID
            or self.closed_prestate != S1_HU_CLOSED_PRESTATE
            or self.stage_order != S1_HU_STAGE_ORDER
            or self.causal_identities != S1_HU_CAUSAL_IDENTITIES
            or self.ablation_identities != S1_HU_ABLATION_IDENTITIES
            or self.refinement_obligations != S1_HU_REFINEMENT_OBLIGATIONS
            or self.rejected_orders != S1_HU_REJECTED_ORDERS
            or self.fail_closed_conditions != S1_HU_FAIL_CLOSED_CONDITIONS
            or tuple(name for name, _ in self.checks) != S1_HU_AUDIT_CHECKS
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.one_closed_prestate_for_both_proposals,
                    self.explicit_one_substep_latency,
                    self.atomic_pair_commit_required,
                    self.exact_p0_a0_field_identity_required,
                    self.first_order_coupling_only,
                    self.coupling_order_selected,
                )
            )
            or any(
                value is not False
                for value in (
                    self.field_integrator_selected,
                    self.coupled_step_implemented,
                    self.material_rate_values_selected,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                    self.functional_effect_proven,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision != S1_HU_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1HUCouplingOrderAuditError(
                "S1-HU weakened the one-order causal coupling audit"
            )


def audit_dts1_s1hu_coupling_order() -> DTS1S1HUCouplingOrderAudit:
    """Audit one causal order without selecting or executing a field integrator."""

    checks = tuple((name, True) for name in S1_HU_AUDIT_CHECKS)
    values = {
        "audit_id": S1_HU_AUDIT_ID,
        "source_s1ht_receipt_digest": S1_HU_SOURCE_S1HT_RECEIPT_DIGEST,
        "candidate_id": S1_HU_CANDIDATE_ID,
        "audited_order_count": 1,
        "order_id": S1_HU_ORDER_ID,
        "closed_prestate": S1_HU_CLOSED_PRESTATE,
        "stage_order": S1_HU_STAGE_ORDER,
        "causal_identities": S1_HU_CAUSAL_IDENTITIES,
        "ablation_identities": S1_HU_ABLATION_IDENTITIES,
        "refinement_obligations": S1_HU_REFINEMENT_OBLIGATIONS,
        "rejected_orders": S1_HU_REJECTED_ORDERS,
        "fail_closed_conditions": S1_HU_FAIL_CLOSED_CONDITIONS,
        "checks": checks,
        "one_closed_prestate_for_both_proposals": True,
        "explicit_one_substep_latency": True,
        "atomic_pair_commit_required": True,
        "exact_p0_a0_field_identity_required": True,
        "first_order_coupling_only": True,
        "coupling_order_selected": True,
        "field_integrator_selected": False,
        "coupled_step_implemented": False,
        "material_rate_values_selected": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "field_steps_executed": 0,
        "functional_effect_proven": False,
        "claims_permitted": False,
        "decision": S1_HU_DECISION,
    }
    return DTS1S1HUCouplingOrderAudit(
        **values,
        audit_digest=_digest(values),
    )
