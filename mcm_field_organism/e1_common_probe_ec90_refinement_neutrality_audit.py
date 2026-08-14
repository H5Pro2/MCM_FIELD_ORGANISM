"""S1-EC90 static r4/r8 refinement-neutrality audit of the r2 path."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import inspect
from pathlib import Path

from .e1_common_probe_ec89_r4_r8_object_handoffs import (
    E1CommonProbeEC89R4R8ObjectHandoffSet,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC90RefinementNeutralityAuditError(ValueError):
    """Raised when EC90 source identity or audit scope changes."""


S1_EC90_AUDIT_ID = "e1.common-probe-refinement-neutrality-audit.s1ec90.v1"
S1_EC90_EC89_RESULT_DIGEST = (
    "eadaee38d591f4ad36acbf00aec3681cd9da0069173a62055ca8ea70a34ffae9"
)
S1_EC90_SOURCE_FILES = (
    (
        "e1_common_probe_real_wrappers.py",
        "d737e9599c0136fa5de8b259c1b5b8d54d736284a558191fc85b44d52de505fb",
    ),
    (
        "e1_common_probe_n2_r2_real_call_adapters.py",
        "4fc2159d573570f11df27e0437f4dead219abfa6ccae6f71f9bb1dc313c69220",
    ),
    (
        "e1_common_probe_n2_r2_real_output_converters.py",
        "6e72f30489be527a6da1cb06fa8d45c16bff518e6bedddc55a45c8101a70225d",
    ),
    (
        "e1_common_probe_n2_r2_positive_step_receipt_contract.py",
        "d8cd2486a293f4a42273a63d37db4ffb7a0cd420c73c95bd7e15454904a70861",
    ),
)
S1_EC90_CHECK_NAMES = (
    "ec89-r4-r8-handoffs-exact-and-zero-step",
    "ec54-resolver-selects-plan-by-binding-refinement",
    "ec54-formation-wrapper-forwards-binding-refinement",
    "ec54-probe-wrapper-consumes-selected-probe-plan",
    "ec65-adapters-delegate-resolved-objects-without-step-literal",
    "ec64-formation-gate-is-not-refinement-neutral",
    "ec64-probe-gate-is-not-refinement-neutral",
    "ec63-formation-receipt-is-not-refinement-neutral",
    "ec63-probe-receipt-is-not-refinement-neutral",
    "ec64-synthetic-helper-is-locked-to-r2-handoff",
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC90RefinementNeutralityAudit:
    audit_id: str
    source_ec89_result_digest: str
    source_digests: tuple[tuple[str, str, str], ...]
    checks: tuple[tuple[str, bool], ...]
    wrapper_plan_selection_refinement_neutral: bool
    adapter_call_order_refinement_neutral: bool
    converter_step_validation_refinement_neutral: bool
    receipt_step_validation_refinement_neutral: bool
    synthetic_r4_r8_route_available: bool
    generalized_extension_required: bool
    existing_r2_sources_must_remain_unchanged: bool
    field_execution_permitted: bool
    owner_authorization_present: bool
    persistence_permitted: bool
    ec46_decision_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    audit_digest: str

    def __post_init__(self) -> None:
        checks = dict(self.checks)
        if (
            self.audit_id != S1_EC90_AUDIT_ID
            or self.source_ec89_result_digest != S1_EC90_EC89_RESULT_DIGEST
            or len(self.source_digests) != 4
            or any(expected != observed for _, expected, observed in self.source_digests)
            or tuple(name for name, _ in self.checks) != S1_EC90_CHECK_NAMES
            or any(
                checks[name] is not True
                for name in S1_EC90_CHECK_NAMES[:5]
            )
            or any(
                checks[name] is not True
                for name in S1_EC90_CHECK_NAMES[5:]
            )
            or self.wrapper_plan_selection_refinement_neutral is not True
            or self.adapter_call_order_refinement_neutral is not True
            or self.converter_step_validation_refinement_neutral is not False
            or self.receipt_step_validation_refinement_neutral is not False
            or self.synthetic_r4_r8_route_available is not False
            or self.generalized_extension_required is not True
            or self.existing_r2_sources_must_remain_unchanged is not True
            or any(
                value is not False
                for value in (
                    self.field_execution_permitted,
                    self.owner_authorization_present,
                    self.persistence_permitted,
                    self.ec46_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision != "STOP_R4_R8_ROUTE_RECEIPT_CONVERTER_STEP_LOCK"
            or not self.reason
        ):
            raise E1CommonProbeEC90RefinementNeutralityAuditError(
                "S1-EC90 audit changed or crossed static scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if self.audit_digest != _digest(payload):
            raise E1CommonProbeEC90RefinementNeutralityAuditError(
                "S1-EC90 audit digest changed"
            )


def audit_e1_common_probe_ec90_refinement_neutrality(
    project_root: Path,
    handoffs: E1CommonProbeEC89R4R8ObjectHandoffSet,
) -> E1CommonProbeEC90RefinementNeutralityAudit:
    """Inspect the existing path without invoking wrappers, adapters, or fields."""

    if not isinstance(handoffs, E1CommonProbeEC89R4R8ObjectHandoffSet):
        raise E1CommonProbeEC90RefinementNeutralityAuditError(
            "S1-EC90 requires the typed EC89 handoff set"
        )
    handoffs.__post_init__()
    if handoffs.result_digest != S1_EC90_EC89_RESULT_DIGEST:
        raise E1CommonProbeEC90RefinementNeutralityAuditError(
            "S1-EC90 EC89 binding changed"
        )
    source_root = Path(project_root) / "mcm_field_organism"
    source_digests = []
    sources = {}
    for name, expected in S1_EC90_SOURCE_FILES:
        try:
            data = (source_root / name).read_bytes()
        except OSError as exc:
            raise E1CommonProbeEC90RefinementNeutralityAuditError(
                f"S1-EC90 source missing: {name}"
            ) from exc
        observed = hashlib.sha256(data).hexdigest()
        if observed != expected:
            raise E1CommonProbeEC90RefinementNeutralityAuditError(
                f"S1-EC90 source changed: {name}"
            )
        source_digests.append((name, expected, observed))
        sources[name] = data.decode("utf-8")
    wrappers = sources[S1_EC90_SOURCE_FILES[0][0]]
    adapters = sources[S1_EC90_SOURCE_FILES[1][0]]
    converters = sources[S1_EC90_SOURCE_FILES[2][0]]
    receipts = sources[S1_EC90_SOURCE_FILES[3][0]]
    checks = (
        (
            "ec89-r4-r8-handoffs-exact-and-zero-step",
            handoffs.refinement_ids == ("r4", "r8")
            and handoffs.field_steps_executed == 0,
        ),
        (
            "ec54-resolver-selects-plan-by-binding-refinement",
            "x.refinement_id == binding.refinement_id" in wrappers,
        ),
        (
            "ec54-formation-wrapper-forwards-binding-refinement",
            "resolved.binding.refinement_id" in wrappers,
        ),
        (
            "ec54-probe-wrapper-consumes-selected-probe-plan",
            "resolved.probe_plan" in wrappers,
        ),
        (
            "ec65-adapters-delegate-resolved-objects-without-step-literal",
            "= 402" not in adapters and "= 200" not in adapters,
        ),
        (
            "ec64-formation-gate-is-not-refinement-neutral",
            "formation-plan-step-count-exactly-402" in converters
            and "len(resolved.formation_plan.proposal_steps) == 402" in converters,
        ),
        (
            "ec64-probe-gate-is-not-refinement-neutral",
            "output.field_step_count != 200" in converters,
        ),
        (
            "ec63-formation-receipt-is-not-refinement-neutral",
            "self.accounted_field_steps != 402" in receipts,
        ),
        (
            "ec63-probe-receipt-is-not-refinement-neutral",
            "self.accounted_field_steps != 200" in receipts,
        ),
        (
            "ec64-synthetic-helper-is-locked-to-r2-handoff",
            "E1CommonProbeN2R2ObjectHandoff" in converters
            and 'refinement_id="r2"' in converters,
        ),
    )
    values = {
        "audit_id": S1_EC90_AUDIT_ID,
        "source_ec89_result_digest": handoffs.result_digest,
        "source_digests": tuple(source_digests),
        "checks": checks,
        "wrapper_plan_selection_refinement_neutral": True,
        "adapter_call_order_refinement_neutral": True,
        "converter_step_validation_refinement_neutral": False,
        "receipt_step_validation_refinement_neutral": False,
        "synthetic_r4_r8_route_available": False,
        "generalized_extension_required": True,
        "existing_r2_sources_must_remain_unchanged": True,
        "field_execution_permitted": False,
        "owner_authorization_present": False,
        "persistence_permitted": False,
        "ec46_decision_permitted": False,
        "claims_permitted": False,
        "decision": "STOP_R4_R8_ROUTE_RECEIPT_CONVERTER_STEP_LOCK",
        "reason": (
            "ec54-ec65-plan-driven;ec63-ec64-hardcode-r2-step-counts-and-types;"
            "add-separate-generalized-receipts-and-converters-without-changing-r2"
        ),
    }
    return E1CommonProbeEC90RefinementNeutralityAudit(
        **values, audit_digest=_digest(values)
    )
