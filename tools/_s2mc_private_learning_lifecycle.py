"""Private role-free S2-MC lifecycle adapter."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from tools import _s2ma_private_arecent_two_view_integration as integration
from tools import _s2mb_private_bstable_two_view as bstable


SCHEMA = "s2mc.private-learning-lifecycle.v1"


class S2MCLifecycleError(ValueError):
    """A lifecycle context decision is invalid."""


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MCLifecycleError(message)


def _valid_digest(value: object) -> bool:
    return type(value) is str and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


@dataclass(frozen=True, slots=True)
class LifecycleContextDecisionV1:
    status: str
    selected_slot_id: str | None
    reason: str
    evidence_status: str
    open_set_decision_digest: str | None
    first_look_digest: str
    second_look_digest: str
    field_contact_digests: tuple[str, str]
    memory_prestate_digest: str
    memory_poststate_digest: str
    decision_digest: str

    def __post_init__(self) -> None:
        _require(self.status in {"ADMITTED", "ABSTAINED"}, "decision status differs")
        _require(
            self.evidence_status in {"ABSENT_VALID", "VALID_CANDIDATES", "PAIR_INVALID"},
            "evidence status differs",
        )
        _require(
            (self.status == "ADMITTED") == (self.selected_slot_id is not None),
            "selected slot differs",
        )
        _require(type(self.reason) is str and self.reason, "decision reason differs")
        _require(
            self.open_set_decision_digest is None
            or _valid_digest(self.open_set_decision_digest),
            "open-set digest differs",
        )
        _require(
            _valid_digest(self.first_look_digest)
            and _valid_digest(self.second_look_digest)
            and type(self.field_contact_digests) is tuple
            and len(self.field_contact_digests) == 2
            and all(_valid_digest(item) for item in self.field_contact_digests)
            and _valid_digest(self.memory_prestate_digest)
            and self.memory_prestate_digest == self.memory_poststate_digest,
            "read-only binding differs",
        )
        _require(
            self.decision_digest == _digest(self.payload_without_digest()),
            "decision digest differs",
        )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "status": self.status,
            "selected_slot_id": self.selected_slot_id,
            "reason": self.reason,
            "evidence_status": self.evidence_status,
            "open_set_decision_digest": self.open_set_decision_digest,
            "first_look_digest": self.first_look_digest,
            "second_look_digest": self.second_look_digest,
            "field_contact_digests": list(self.field_contact_digests),
            "memory_prestate_digest": self.memory_prestate_digest,
            "memory_poststate_digest": self.memory_poststate_digest,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "decision_digest": self.decision_digest}


def _build_decision(
    *,
    status: str,
    selected_slot_id: str | None,
    reason: str,
    evidence_status: str,
    open_set_decision_digest: str | None,
    first: integration.ARecentObservedLookV1,
    second: integration.ARecentObservedLookV1,
    memory_prestate_digest: str,
    memory_poststate_digest: str,
) -> LifecycleContextDecisionV1:
    _require(
        first.field_contact_digest is not None and second.field_contact_digest is not None,
        "field contact is absent",
    )
    payload = {
        "schema": SCHEMA,
        "status": status,
        "selected_slot_id": selected_slot_id,
        "reason": reason,
        "evidence_status": evidence_status,
        "open_set_decision_digest": open_set_decision_digest,
        "first_look_digest": first.digest(),
        "second_look_digest": second.digest(),
        "field_contact_digests": [first.field_contact_digest, second.field_contact_digest],
        "memory_prestate_digest": memory_prestate_digest,
        "memory_poststate_digest": memory_poststate_digest,
    }
    return LifecycleContextDecisionV1(
        status,
        selected_slot_id,
        reason,
        evidence_status,
        open_set_decision_digest,
        first.digest(),
        second.digest(),
        (first.field_contact_digest, second.field_contact_digest),
        memory_prestate_digest,
        memory_poststate_digest,
        _digest(payload),
    )


def decide_lifecycle_context(
    *,
    first: integration.ARecentObservedLookV1,
    second: integration.ARecentObservedLookV1,
    candidates: bstable.BStableVisualCandidateSetV1 | None,
    geometry_digest: str,
    view_a_mask_digest: str,
    view_b_mask_digest: str,
    union_mask_digest: str,
    union_positions: tuple[int, ...],
    memory_prestate_digest: str,
    memory_poststate_digest: str,
) -> LifecycleContextDecisionV1:
    _require(
        type(first) is integration.ARecentObservedLookV1
        and type(second) is integration.ARecentObservedLookV1
        and _valid_digest(geometry_digest)
        and _valid_digest(view_a_mask_digest)
        and _valid_digest(view_b_mask_digest)
        and _valid_digest(union_mask_digest)
        and type(union_positions) is tuple
        and len(union_positions) == 192
        and memory_prestate_digest == memory_poststate_digest,
        "lifecycle inputs differ",
    )
    if candidates is not None:
        _require(
            type(candidates) is bstable.BStableVisualCandidateSetV1
            and candidates.memory_state_digest == memory_prestate_digest
            and candidates.union_mask_digest == union_mask_digest
            and candidates.union_positions == union_positions,
            "candidate-state binding differs",
        )
        product = integration.ARecentTransientTwoViewIntegrator(
            geometry_digest=geometry_digest,
            view_a_mask_digest=view_a_mask_digest,
            view_b_mask_digest=view_b_mask_digest,
            union_mask_digest=union_mask_digest,
            union_positions=union_positions,
            model_envelopes=candidates.model_envelopes(),
        )
        pending = product.process(first)
        _require(pending.status == "PENDING", "first look did not open a window")
        result = product.process(second)
        _require(product.pending_count == 0, "two-view window was retained")
        evidence = "VALID_CANDIDATES" if result.reason != "PAIR_INCOMPATIBLE_NO_UNION" else "PAIR_INVALID"
        return _build_decision(
            status=result.status,
            selected_slot_id=result.selected_model_id,
            reason=result.reason,
            evidence_status=evidence,
            open_set_decision_digest=result.open_set_decision_digest,
            first=first,
            second=second,
            memory_prestate_digest=memory_prestate_digest,
            memory_poststate_digest=memory_poststate_digest,
        )

    compatible = (
        first.geometry_digest == second.geometry_digest == geometry_digest
        and first.mask_id == "VIEW_A_96"
        and second.mask_id == "VIEW_B_96"
        and first.mask_digest == view_a_mask_digest
        and second.mask_digest == view_b_mask_digest
        and first.case_plan_digest == second.case_plan_digest
        and first.source_id == second.source_id
        and first.payload_sha256 == second.payload_sha256
        and first.source_values_digest == second.source_values_digest
        and second.tick - first.tick == 1
        and first.observed_positions + second.observed_positions == union_positions
    )
    return _build_decision(
        status="ABSTAINED",
        selected_slot_id=None,
        reason="NO_STABLE_CONTEXT" if compatible else "PAIR_INCOMPATIBLE_NO_UNION",
        evidence_status="ABSENT_VALID" if compatible else "PAIR_INVALID",
        open_set_decision_digest=None,
        first=first,
        second=second,
        memory_prestate_digest=memory_prestate_digest,
        memory_poststate_digest=memory_poststate_digest,
    )


def direct_lifecycle_baseline(
    *,
    first: integration.ARecentObservedLookV1,
    second: integration.ARecentObservedLookV1,
    candidates: bstable.BStableVisualCandidateSetV1 | None,
    geometry_digest: str,
    view_a_mask_digest: str,
    view_b_mask_digest: str,
    union_mask_digest: str,
    union_positions: tuple[int, ...],
    memory_prestate_digest: str,
    memory_poststate_digest: str,
) -> LifecycleContextDecisionV1:
    _require(memory_prestate_digest == memory_poststate_digest, "baseline changed memory")
    if candidates is not None:
        _require(
            type(candidates) is bstable.BStableVisualCandidateSetV1
            and candidates.memory_state_digest == memory_prestate_digest
            and candidates.union_mask_digest == union_mask_digest
            and candidates.union_positions == union_positions,
            "baseline candidate binding differs",
        )
        direct = bstable.direct_bstable_two_view_baseline(
            first=first,
            second=second,
            candidates=candidates,
            geometry_digest=geometry_digest,
            view_a_mask_digest=view_a_mask_digest,
            view_b_mask_digest=view_b_mask_digest,
        )
        evidence = "VALID_CANDIDATES" if direct["reason"] != "PAIR_INCOMPATIBLE_NO_UNION" else "PAIR_INVALID"
        return _build_decision(
            status=str(direct["status"]),
            selected_slot_id=direct["selected_model_id"],
            reason=str(direct["reason"]),
            evidence_status=evidence,
            open_set_decision_digest=str(direct["decision_digest"]),
            first=first,
            second=second,
            memory_prestate_digest=memory_prestate_digest,
            memory_poststate_digest=memory_poststate_digest,
        )

    valid_pair = (
        type(first) is integration.ARecentObservedLookV1
        and type(second) is integration.ARecentObservedLookV1
        and first.geometry_digest == geometry_digest
        and second.geometry_digest == geometry_digest
        and first.mask_id == "VIEW_A_96"
        and second.mask_id == "VIEW_B_96"
        and first.mask_digest == view_a_mask_digest
        and second.mask_digest == view_b_mask_digest
        and first.case_plan_digest == second.case_plan_digest
        and first.source_id == second.source_id
        and first.payload_sha256 == second.payload_sha256
        and first.source_values_digest == second.source_values_digest
        and second.tick - first.tick == 1
        and first.observed_positions + second.observed_positions == union_positions
    )
    return _build_decision(
        status="ABSTAINED",
        selected_slot_id=None,
        reason="NO_STABLE_CONTEXT" if valid_pair else "PAIR_INCOMPATIBLE_NO_UNION",
        evidence_status="ABSENT_VALID" if valid_pair else "PAIR_INVALID",
        open_set_decision_digest=None,
        first=first,
        second=second,
        memory_prestate_digest=memory_prestate_digest,
        memory_poststate_digest=memory_poststate_digest,
    )


__all__: tuple[str, ...] = ()
