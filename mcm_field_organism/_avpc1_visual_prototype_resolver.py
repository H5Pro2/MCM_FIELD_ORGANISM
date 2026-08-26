"""Private read-only resolver for one AVPC-1 visual prototype state."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from ._avpc1_bounded_relation import (
    AVPC1BoundedRelationState,
    AVPC1ReadOnlyRelationFinding,
)
from ._ppb1_receptor_profiles import PPB1ReceptorProfileBinding
from ._ppb1_reference import (
    PPB1_ATOMIC_OUTPUT_REQUIRED,
    PPB1BankState,
    PPB1ReferenceError,
    _bounded_values,
    _positive_integer,
    _validate_state,
)
from ._ppb1_s1wq_perceptual_state_lifecycle import _state_identity_payload
from ._ppb1_s1wu_read_only_perceptual_probe import _prototype_digest
from .receptor_contract import technical_identifier


AVPC1_VISUAL_RESOLVER_SCHEMA_VERSION = (
    "avpc1.private.read-only-visual-prototype-state-resolver.v1"
)
AVPC1_VISUAL_RESOLVER_CONTRACT_DIGEST = (
    "48a7d0eac97956ea2cde69b249a9ab047fffc5b38a778ad9b9d364514d1d32a0"
)
AVPC1_VISUAL_RESOLVER_PREFLIGHT_DIGEST = (
    "765628431bc42482a5ea1ffbfaaa7ba2fda00f8c2b9a6641e4e9c84623af9ad9"
)
AVPC1_VISUAL_RESOLVER_INVALID_INPUT = "AVPC1_VISUAL_RESOLVER_INVALID_INPUT"
AVPC1_VISUAL_RESOLVER_RELATION_MISMATCH = (
    "AVPC1_VISUAL_RESOLVER_RELATION_MISMATCH"
)
AVPC1_VISUAL_RESOLVER_CONTENT_MISMATCH = (
    "AVPC1_VISUAL_RESOLVER_CONTENT_MISMATCH"
)
AVPC1_VISUAL_RESOLVER_TARGET_NOT_UNIQUE_STABLE = (
    "AVPC1_VISUAL_RESOLVER_TARGET_NOT_UNIQUE_STABLE"
)
AVPC1_VISUAL_RESOLVER_ATOMIC_RESULT_REQUIRED = (
    "AVPC1_VISUAL_RESOLVER_ATOMIC_RESULT_REQUIRED"
)

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


class AVPC1VisualPrototypeResolverError(ValueError):
    """One fail-closed private visual prototype resolution violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST_RE.fullmatch(value) is not None


def _identifier(value: object, role: str) -> str:
    try:
        return technical_identifier(value, role)
    except ValueError as exc:
        raise AVPC1VisualPrototypeResolverError(
            AVPC1_VISUAL_RESOLVER_INVALID_INPUT,
            str(exc),
        ) from exc


def _bank_state_identity_digest(state: PPB1BankState) -> str:
    return _digest(_state_identity_payload(state))


@dataclass(frozen=True, slots=True)
class AVPC1ReadOnlyVisualPrototypeState:
    resolver_id: str
    relation_finding_digest: str
    relation_state_identity_digest: str
    observed_relation_state_digest: str
    profile_binding_digest: str
    visual_bank_config_digest: str
    visual_bank_state_identity_digest: str
    visual_bank_state_digest: str
    relation_slot_id: str
    visual_prototype_slot_id: str
    visual_prototype_identity_digest: str
    modality_id: str
    geometry_id: str
    carrier_ids: tuple[str, ...]
    prototype_values: tuple[float, ...]
    support_count: int
    resolved_state_digest: str
    schema_version: str = AVPC1_VISUAL_RESOLVER_SCHEMA_VERSION

    def __post_init__(self) -> None:
        try:
            resolver_id = technical_identifier(self.resolver_id, "resolver_id")
            relation_slot_id = technical_identifier(
                self.relation_slot_id,
                "relation_slot_id",
            )
            prototype_slot_id = technical_identifier(
                self.visual_prototype_slot_id,
                "visual_prototype_slot_id",
            )
            geometry_id = technical_identifier(self.geometry_id, "geometry_id")
            carrier_ids = tuple(self.carrier_ids)
            for carrier_id in carrier_ids:
                technical_identifier(carrier_id, "carrier_id")
            prototype_values = _bounded_values(
                self.prototype_values,
                "prototype_values",
                PPB1_ATOMIC_OUTPUT_REQUIRED,
            )
            support_count = _positive_integer(
                self.support_count,
                "support_count",
                PPB1_ATOMIC_OUTPUT_REQUIRED,
            )
        except (ValueError, PPB1ReferenceError) as exc:
            raise AVPC1VisualPrototypeResolverError(
                AVPC1_VISUAL_RESOLVER_ATOMIC_RESULT_REQUIRED,
                "resolved visual prototype state has invalid identifiers or values",
            ) from exc
        digests = (
            self.relation_finding_digest,
            self.relation_state_identity_digest,
            self.observed_relation_state_digest,
            self.profile_binding_digest,
            self.visual_bank_config_digest,
            self.visual_bank_state_identity_digest,
            self.visual_bank_state_digest,
            self.visual_prototype_identity_digest,
            self.resolved_state_digest,
        )
        if (
            self.schema_version != AVPC1_VISUAL_RESOLVER_SCHEMA_VERSION
            or self.modality_id != "visual"
            or not carrier_ids
            or len(set(carrier_ids)) != len(carrier_ids)
            or len(carrier_ids) != len(prototype_values)
            or not all(_valid_digest(value) for value in digests)
            or self.visual_prototype_identity_digest
            != _prototype_digest(prototype_values)
        ):
            raise AVPC1VisualPrototypeResolverError(
                AVPC1_VISUAL_RESOLVER_ATOMIC_RESULT_REQUIRED,
                "resolved visual prototype state is incomplete",
            )
        object.__setattr__(self, "resolver_id", resolver_id)
        object.__setattr__(self, "relation_slot_id", relation_slot_id)
        object.__setattr__(self, "visual_prototype_slot_id", prototype_slot_id)
        object.__setattr__(self, "geometry_id", geometry_id)
        object.__setattr__(self, "carrier_ids", carrier_ids)
        object.__setattr__(self, "prototype_values", prototype_values)
        object.__setattr__(self, "support_count", support_count)
        if self.resolved_state_digest != _digest(self.payload_without_digest()):
            raise AVPC1VisualPrototypeResolverError(
                AVPC1_VISUAL_RESOLVER_ATOMIC_RESULT_REQUIRED,
                "resolved visual prototype state digest mismatch",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "contract_digest": AVPC1_VISUAL_RESOLVER_CONTRACT_DIGEST,
            "preflight_digest": AVPC1_VISUAL_RESOLVER_PREFLIGHT_DIGEST,
            "resolver_id": self.resolver_id,
            "relation_finding_digest": self.relation_finding_digest,
            "relation_state_identity_digest": self.relation_state_identity_digest,
            "observed_relation_state_digest": self.observed_relation_state_digest,
            "profile_binding_digest": self.profile_binding_digest,
            "visual_bank_config_digest": self.visual_bank_config_digest,
            "visual_bank_state_identity_digest": (
                self.visual_bank_state_identity_digest
            ),
            "visual_bank_state_digest": self.visual_bank_state_digest,
            "relation_slot_id": self.relation_slot_id,
            "visual_prototype_slot_id": self.visual_prototype_slot_id,
            "visual_prototype_identity_digest": (
                self.visual_prototype_identity_digest
            ),
            "modality_id": self.modality_id,
            "geometry_id": self.geometry_id,
            "carrier_ids": list(self.carrier_ids),
            "prototype_values": list(self.prototype_values),
            "support_count": self.support_count,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "resolved_state_digest": self.resolved_state_digest,
        }


def resolve_avpc1_visual_prototype_state(
    resolver_id: str,
    relation_finding: AVPC1ReadOnlyRelationFinding,
    relation_state: AVPC1BoundedRelationState,
    profile: PPB1ReceptorProfileBinding,
    visual_bank_state: PPB1BankState,
) -> AVPC1ReadOnlyVisualPrototypeState:
    """Resolve one exact stable visual prototype without changing any source."""

    exact_inputs = (
        (relation_finding, AVPC1ReadOnlyRelationFinding),
        (relation_state, AVPC1BoundedRelationState),
        (profile, PPB1ReceptorProfileBinding),
        (visual_bank_state, PPB1BankState),
    )
    if not all(type(value) is expected for value, expected in exact_inputs):
        raise AVPC1VisualPrototypeResolverError(
            AVPC1_VISUAL_RESOLVER_INVALID_INPUT,
            "exact relation finding, relation state, profile and visual state required",
        )
    resolver_id = _identifier(resolver_id, "resolver_id")
    before = (
        relation_finding.finding_digest,
        relation_state.state_digest,
        profile.digest(),
        profile.visual_config.digest(),
        _bank_state_identity_digest(visual_bank_state),
        visual_bank_state.digest(),
    )
    target_digest = relation_finding.visual_prototype_identity_digest
    relation_slot_id = relation_finding.selected_relation_slot_id
    if (
        relation_finding.result_role != "MATCH"
        or target_digest is None
        or relation_slot_id is None
    ):
        raise AVPC1VisualPrototypeResolverError(
            AVPC1_VISUAL_RESOLVER_RELATION_MISMATCH,
            "resolver requires one positive relation finding",
        )
    if (
        relation_finding.relation_state_identity_digest
        != relation_state.state_identity_digest
        or relation_finding.observed_relation_state_digest
        != relation_state.state_digest
        or relation_finding.frozen_visual_bank_state_digest
        != relation_state.visual_bank_state_digest
    ):
        raise AVPC1VisualPrototypeResolverError(
            AVPC1_VISUAL_RESOLVER_RELATION_MISMATCH,
            "relation finding does not bind the supplied relation state",
        )
    relation_slots = tuple(
        slot
        for slot in relation_state.slots
        if slot.slot_id == relation_slot_id
    )
    if (
        len(relation_slots) != 1
        or relation_slots[0].status != "STABLE"
        or relation_slots[0].visual_target_digest != target_digest
    ):
        raise AVPC1VisualPrototypeResolverError(
            AVPC1_VISUAL_RESOLVER_RELATION_MISMATCH,
            "selected relation slot is not one stable binding to the target",
        )
    visual_config = profile.visual_config
    if (
        profile.digest() != relation_state.profile_binding_digest
        or visual_config.modality_id != "visual"
        or visual_config.digest() != relation_state.visual_bank_config_digest
    ):
        raise AVPC1VisualPrototypeResolverError(
            AVPC1_VISUAL_RESOLVER_CONTENT_MISMATCH,
            "profile or visual config does not bind the relation state",
        )
    try:
        validated_visual_state = _validate_state(
            visual_config,
            visual_bank_state,
        )
    except PPB1ReferenceError as exc:
        raise AVPC1VisualPrototypeResolverError(
            AVPC1_VISUAL_RESOLVER_CONTENT_MISMATCH,
            "visual bank state does not validate against the profile config",
        ) from exc
    visual_identity_digest = _bank_state_identity_digest(validated_visual_state)
    visual_state_digest = validated_visual_state.digest()
    if (
        visual_identity_digest != relation_state.visual_bank_state_identity_digest
        or visual_state_digest != relation_state.visual_bank_state_digest
        or visual_state_digest != relation_finding.frozen_visual_bank_state_digest
    ):
        raise AVPC1VisualPrototypeResolverError(
            AVPC1_VISUAL_RESOLVER_CONTENT_MISMATCH,
            "visual bank identity or state digest does not bind all sources",
        )
    if relation_state.visual_prototype_inventory.count(target_digest) != 1:
        raise AVPC1VisualPrototypeResolverError(
            AVPC1_VISUAL_RESOLVER_TARGET_NOT_UNIQUE_STABLE,
            "target must occur once in the relation visual inventory",
        )
    matching_slots = tuple(
        slot
        for slot in validated_visual_state.slots
        if (
            slot.occupied
            and slot.support_count is not None
            and slot.support_count >= visual_config.stable_after
            and _prototype_digest(slot.prototype_values) == target_digest
        )
    )
    if len(matching_slots) != 1:
        raise AVPC1VisualPrototypeResolverError(
            AVPC1_VISUAL_RESOLVER_TARGET_NOT_UNIQUE_STABLE,
            "target must identify exactly one stabilized visual bank slot",
        )
    selected = matching_slots[0]
    if selected.support_count is None:
        raise AVPC1VisualPrototypeResolverError(
            AVPC1_VISUAL_RESOLVER_ATOMIC_RESULT_REQUIRED,
            "selected stable slot has no support",
        )
    values = {
        "resolver_id": resolver_id,
        "relation_finding_digest": relation_finding.finding_digest,
        "relation_state_identity_digest": relation_state.state_identity_digest,
        "observed_relation_state_digest": relation_state.state_digest,
        "profile_binding_digest": profile.digest(),
        "visual_bank_config_digest": visual_config.digest(),
        "visual_bank_state_identity_digest": visual_identity_digest,
        "visual_bank_state_digest": visual_state_digest,
        "relation_slot_id": relation_slot_id,
        "visual_prototype_slot_id": selected.slot_id,
        "visual_prototype_identity_digest": target_digest,
        "modality_id": "visual",
        "geometry_id": visual_config.geometry_id,
        "carrier_ids": visual_config.carrier_ids,
        "prototype_values": selected.prototype_values,
        "support_count": selected.support_count,
    }
    payload = {
        "schema_version": AVPC1_VISUAL_RESOLVER_SCHEMA_VERSION,
        "contract_digest": AVPC1_VISUAL_RESOLVER_CONTRACT_DIGEST,
        "preflight_digest": AVPC1_VISUAL_RESOLVER_PREFLIGHT_DIGEST,
        **{
            key: list(value) if key in {"carrier_ids", "prototype_values"} else value
            for key, value in values.items()
        },
    }
    output = AVPC1ReadOnlyVisualPrototypeState(
        **values,
        resolved_state_digest=_digest(payload),
    )
    after = (
        relation_finding.finding_digest,
        relation_state.state_digest,
        profile.digest(),
        profile.visual_config.digest(),
        _bank_state_identity_digest(visual_bank_state),
        visual_bank_state.digest(),
    )
    if after != before:
        raise AVPC1VisualPrototypeResolverError(
            AVPC1_VISUAL_RESOLVER_ATOMIC_RESULT_REQUIRED,
            "resolver source changed during read-only resolution",
        )
    return output
