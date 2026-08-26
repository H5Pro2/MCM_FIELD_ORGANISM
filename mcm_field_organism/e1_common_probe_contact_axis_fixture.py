"""S1-EC51 contact-aware synthetic common-probe adapter correction."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_common_probe_acceptance_contract import (
    E1CommonProbeAcceptanceContract,
    decide_common_probe_evidence,
)
from .e1_common_probe_contact_axis_audit import (
    E1CommonProbeContactAxisAudit,
    S1_EC50_REQUIRED_CONTACT_COUNTS,
)
from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_common_probe_synthetic_runner_fixture import S1_EC47_REFINEMENTS
from .e1_refined_formation_runner import _digest


class E1CommonProbeContactAxisFixtureError(ValueError):
    """Raised when EC51 mixes n1/n2 or crosses its zero-field boundary."""


S1_EC51_FIXTURE_ID = "e1.common-probe-contact-axis-fixture.s1ec51.v1"
S1_EC51_EC46_CONTRACT_DIGEST = (
    "672239cddf2a1e8a8856a5bd2570ebaf0a9bdda5f52fb45aa0306e2570dd144b"
)
S1_EC51_EC50_AUDIT_DIGEST = (
    "e4e779ba04a955bea10f10d34a42727f9d89cd19c3ac50a96e54aa71ceb9ec14"
)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64


@dataclass(frozen=True, slots=True)
class E1ContactFormationHandoff:
    contact_count: int
    refinement_id: str
    state_digests: tuple[tuple[str, str], ...]
    field_steps_executed: int
    synthetic: bool
    handoff_digest: str

    def __post_init__(self) -> None:
        if (
            self.contact_count not in S1_EC50_REQUIRED_CONTACT_COUNTS
            or self.refinement_id not in S1_EC47_REFINEMENTS
            or tuple(role for role, _ in self.state_digests) != (
                "active-ab", "active-ba", "formation-ablated-ab",
                "formation-ablated-ba",
            )
            or any(not _valid_digest(value) for _, value in self.state_digests)
            or len({value for _, value in self.state_digests}) != 4
            or self.field_steps_executed != 0
            or self.synthetic is not True
        ):
            raise E1CommonProbeContactAxisFixtureError(
                "S1-EC51 contact formation handoff changed"
            )
        payload = {name: getattr(self, name) for name in self.__dataclass_fields__ if name != "handoff_digest"}
        if self.handoff_digest != _digest(payload):
            raise E1CommonProbeContactAxisFixtureError(
                "S1-EC51 formation handoff digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1ContactResetSlot:
    contact_count: int
    refinement_id: str
    role_id: str
    slot_id: str
    initial_field_digest: str
    field_steps_executed: int
    synthetic: bool
    slot_digest: str

    def __post_init__(self) -> None:
        if (
            self.contact_count not in S1_EC50_REQUIRED_CONTACT_COUNTS
            or self.refinement_id not in S1_EC47_REFINEMENTS
            or self.role_id not in S1_EC45_PROBE_ROLES
            or self.slot_id
            != f"n{self.contact_count}:{self.refinement_id}:{self.role_id}"
            or not _valid_digest(self.initial_field_digest)
            or self.field_steps_executed != 0
            or self.synthetic is not True
        ):
            raise E1CommonProbeContactAxisFixtureError(
                "S1-EC51 contact reset slot changed"
            )
        payload = {name: getattr(self, name) for name in self.__dataclass_fields__ if name != "slot_digest"}
        if self.slot_digest != _digest(payload):
            raise E1CommonProbeContactAxisFixtureError(
                "S1-EC51 reset slot digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1ContactRoleReceipt:
    contact_count: int
    refinement_id: str
    role_id: str
    selected_state_digest: str | None
    backreaction_enabled: bool
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    reset_slot_digest: str
    field_steps_executed: int
    synthetic: bool
    receipt_digest: str

    def __post_init__(self) -> None:
        is_p0 = self.role_id.startswith("p0-reset-")
        expected_backreaction = not is_p0 and "probe-feedback-ablated" not in self.role_id
        if (
            self.contact_count not in S1_EC50_REQUIRED_CONTACT_COUNTS
            or self.refinement_id not in S1_EC47_REFINEMENTS
            or self.role_id not in S1_EC45_PROBE_ROLES
            or (self.selected_state_digest is None) is not is_p0
            or (self.selected_state_digest is not None and not _valid_digest(self.selected_state_digest))
            or self.backreaction_enabled is not expected_backreaction
            or len(self.activation) != 3
            or len(self.afterimage) != 3
            or not _valid_digest(self.reset_slot_digest)
            or self.field_steps_executed != 0
            or self.synthetic is not True
        ):
            raise E1CommonProbeContactAxisFixtureError(
                "S1-EC51 contact role receipt changed"
            )
        payload = {name: getattr(self, name) for name in self.__dataclass_fields__ if name != "receipt_digest"}
        if self.receipt_digest != _digest(payload):
            raise E1CommonProbeContactAxisFixtureError(
                "S1-EC51 role receipt digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1CommonProbeContactAxisFixtureResult:
    fixture_id: str
    source_contract_digest: str
    source_audit_digest: str
    contact_counts: tuple[int, ...]
    formation_handoff_digests: tuple[str, ...]
    reset_slot_digests: tuple[str, ...]
    role_receipt_digests: tuple[str, ...]
    branch_decisions: tuple[tuple[int, str], ...]
    formation_handoff_count: int
    reset_slot_count: int
    role_receipt_count: int
    n1_n2_separated: bool
    all_reset_fields_identical_within_and_across_branches: bool
    all_slots_unique: bool
    field_steps_executed: int
    contact_axis_correction_complete: bool
    static_real_binding_permitted: bool
    pilot_execution_performed: bool
    persistence_performed: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    result_digest: str

    def __post_init__(self) -> None:
        if (
            self.fixture_id != S1_EC51_FIXTURE_ID
            or self.source_contract_digest != S1_EC51_EC46_CONTRACT_DIGEST
            or self.source_audit_digest != S1_EC51_EC50_AUDIT_DIGEST
            or self.contact_counts != (1, 2)
            or len(self.formation_handoff_digests) != 6
            or len(self.reset_slot_digests) != 48
            or len(self.role_receipt_digests) != 48
            or self.branch_decisions != (
                (1, "NO_MEASURABLE_COMMON_PROBE_DIFFERENCE"),
                (2, "NUMERICALLY_CLEAR_STATE_DEPENDENT_COMMON_PROBE_DIFFERENCE"),
            )
            or (self.formation_handoff_count, self.reset_slot_count, self.role_receipt_count) != (6, 48, 48)
            or any(value is not True for value in (
                self.n1_n2_separated,
                self.all_reset_fields_identical_within_and_across_branches,
                self.all_slots_unique,
                self.contact_axis_correction_complete,
                self.static_real_binding_permitted,
            ))
            or self.field_steps_executed != 0
            or any(value is not False for value in (
                self.pilot_execution_performed,
                self.persistence_performed,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
        ):
            raise E1CommonProbeContactAxisFixtureError(
                "S1-EC51 result changed or crossed zero-field scope"
            )
        payload = {name: getattr(self, name) for name in self.__dataclass_fields__ if name != "result_digest"}
        if self.result_digest != _digest(payload):
            raise E1CommonProbeContactAxisFixtureError(
                "S1-EC51 result digest changed"
            )


def _handoff(contact_count: int, refinement: str) -> E1ContactFormationHandoff:
    state_digests = tuple(
        (role, _digest((contact_count, refinement, role)))
        for role in (
            "active-ab", "active-ba", "formation-ablated-ab",
            "formation-ablated-ba",
        )
    )
    values = {
        "contact_count": contact_count,
        "refinement_id": refinement,
        "state_digests": state_digests,
        "field_steps_executed": 0,
        "synthetic": True,
    }
    return E1ContactFormationHandoff(**values, handoff_digest=_digest(values))


def _state_for(role: str, handoff: E1ContactFormationHandoff) -> str | None:
    if role.startswith("p0-reset-"):
        return None
    side = "ab" if role.endswith("-ab") else "ba"
    kind = "formation-ablated" if "formation-ablated" in role else "active"
    return dict(handoff.state_digests)[f"{kind}-{side}"]


def _active_levels(contact_count: int, refinement: str) -> tuple[float, float]:
    if contact_count == 1:
        return 0.0, 0.0
    return {
        "r2": (0.0010015, 0.0020030),
        "r4": (0.0010005, 0.0020010),
        "r8": (0.0010000, 0.0020000),
    }[refinement]


def _linf(values: tuple[float, ...]) -> float:
    return max(abs(value) for value in values)


def _difference(left: tuple[float, ...], right: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(a - b for a, b in zip(left, right, strict=True))


def run_e1_common_probe_contact_axis_fixture(
    contract: E1CommonProbeAcceptanceContract,
    audit: E1CommonProbeContactAxisAudit,
) -> E1CommonProbeContactAxisFixtureResult:
    """Restore n1/n2 over every synthetic EC45 slot without field execution."""

    if not isinstance(contract, E1CommonProbeAcceptanceContract) or not isinstance(audit, E1CommonProbeContactAxisAudit):
        raise E1CommonProbeContactAxisFixtureError("S1-EC51 requires typed EC46 and EC50 inputs")
    contract.__post_init__()
    audit.__post_init__()
    if contract.contract_digest != S1_EC51_EC46_CONTRACT_DIGEST or audit.audit_digest != S1_EC51_EC50_AUDIT_DIGEST or audit.contact_axis_correction_permitted is not True:
        raise E1CommonProbeContactAxisFixtureError("S1-EC51 upstream binding changed")
    handoffs = []
    slots = []
    receipts = []
    for contact_count in S1_EC50_REQUIRED_CONTACT_COUNTS:
        for refinement in S1_EC47_REFINEMENTS:
            handoff = _handoff(contact_count, refinement)
            handoffs.append(handoff)
            for role in S1_EC45_PROBE_ROLES:
                slot_values = {
                    "contact_count": contact_count,
                    "refinement_id": refinement,
                    "role_id": role,
                    "slot_id": f"n{contact_count}:{refinement}:{role}",
                    "initial_field_digest": _digest("ec51-identical-reset-field"),
                    "field_steps_executed": 0,
                    "synthetic": True,
                }
                slot = E1ContactResetSlot(**slot_values, slot_digest=_digest(slot_values))
                activation = (0.0, 0.0, 0.0)
                afterimage = (0.0, 0.0, 0.0)
                if role == "e1-active-ab":
                    s, h = _active_levels(contact_count, refinement)
                    activation = (s, -0.5 * s, 0.0)
                    afterimage = (h, -0.5 * h, 0.0)
                receipt_values = {
                    "contact_count": contact_count,
                    "refinement_id": refinement,
                    "role_id": role,
                    "selected_state_digest": _state_for(role, handoff),
                    "backreaction_enabled": not role.startswith("p0-reset-") and "probe-feedback-ablated" not in role,
                    "activation": activation,
                    "afterimage": afterimage,
                    "reset_slot_digest": slot.slot_digest,
                    "field_steps_executed": 0,
                    "synthetic": True,
                }
                slots.append(slot)
                receipts.append(E1ContactRoleReceipt(**receipt_values, receipt_digest=_digest(receipt_values)))

    by_key = {(x.contact_count, x.refinement_id, x.role_id): x for x in receipts}
    decisions = []
    for contact_count in S1_EC50_REQUIRED_CONTACT_COUNTS:
        active_s_vectors = []
        active_h_vectors = []
        for refinement in S1_EC47_REFINEMENTS:
            ab = by_key[(contact_count, refinement, "e1-active-ab")]
            ba = by_key[(contact_count, refinement, "e1-active-ba")]
            active_s_vectors.append(_difference(ab.activation, ba.activation))
            active_h_vectors.append(_difference(ab.afterimage, ba.afterimage))
        def control(prefix: str, component: str) -> float:
            return max(
                _linf(_difference(
                    getattr(by_key[(contact_count, refinement, f"{prefix}-ab")], component),
                    getattr(by_key[(contact_count, refinement, f"{prefix}-ba")], component),
                ))
                for refinement in S1_EC47_REFINEMENTS
            )
        inputs = {
            "active_s": _linf(active_s_vectors[2]),
            "active_h": _linf(active_h_vectors[2]),
            "coarse_s": _linf(_difference(active_s_vectors[0], active_s_vectors[1])),
            "coarse_h": _linf(_difference(active_h_vectors[0], active_h_vectors[1])),
            "fine_s": _linf(_difference(active_s_vectors[1], active_s_vectors[2])),
            "fine_h": _linf(_difference(active_h_vectors[1], active_h_vectors[2])),
            "p0_reset_s": control("p0-reset", "activation"),
            "p0_reset_h": control("p0-reset", "afterimage"),
            "feedback_ablation_s": control("e1-probe-feedback-ablated", "activation"),
            "feedback_ablation_h": control("e1-probe-feedback-ablated", "afterimage"),
            "formation_ablation_s": control("e1-formation-ablated", "activation"),
            "formation_ablation_h": control("e1-formation-ablated", "afterimage"),
        }
        decisions.append((contact_count, decide_common_probe_evidence(**inputs)))

    slot_ids = {item.slot_id for item in slots}
    values = {
        "fixture_id": S1_EC51_FIXTURE_ID,
        "source_contract_digest": contract.contract_digest,
        "source_audit_digest": audit.audit_digest,
        "contact_counts": S1_EC50_REQUIRED_CONTACT_COUNTS,
        "formation_handoff_digests": tuple(item.handoff_digest for item in handoffs),
        "reset_slot_digests": tuple(item.slot_digest for item in slots),
        "role_receipt_digests": tuple(item.receipt_digest for item in receipts),
        "branch_decisions": tuple(decisions),
        "formation_handoff_count": len(handoffs),
        "reset_slot_count": len(slots),
        "role_receipt_count": len(receipts),
        "n1_n2_separated": len({(x.contact_count, x.refinement_id, x.role_id) for x in receipts}) == 48,
        "all_reset_fields_identical_within_and_across_branches": len({x.initial_field_digest for x in slots}) == 1,
        "all_slots_unique": len(slot_ids) == 48,
        "field_steps_executed": sum(x.field_steps_executed for x in (*handoffs, *slots, *receipts)),
        "contact_axis_correction_complete": True,
        "static_real_binding_permitted": True,
        "pilot_execution_performed": False,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeContactAxisFixtureResult(**values, result_digest=_digest(values))
