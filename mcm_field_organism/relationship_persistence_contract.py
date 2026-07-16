"""Architecture-only contract for a future local relationship substrate."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import re

from .architecture_readiness import EvidenceLevel, RuntimePermission


class RelationshipPersistenceContractError(ValueError):
    """Raised when a persistence contract preprograms memory or semantics."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")

REQUIRED_CAUSES = frozenset(
    {
        "repeated_local_joint_field_effect",
        "prior_local_field_organization",
        "local_available_resource",
    }
)

REQUIRED_EFFECTS = frozenset(
    {
        "changed_later_local_field_intake",
        "changed_later_local_forwarding",
        "local_resource_release",
        "complete_functional_loss",
        "new_local_rebinding",
    }
)

REQUIRED_PROPERTIES = frozenset(
    {
        "local_origin",
        "world_history_dependence",
        "causal_later_effect",
        "source_provenance",
        "finite_resource_use",
        "atomic_time",
        "observer_independence",
        "no_same_step_self_evidence",
        "reversible_weakening",
        "complete_dissolution",
        "local_rebinding",
        "baseline_separation",
        "representation_open",
    }
)

FORBIDDEN_PERSISTENCE_ROLES = frozenset(
    {
        "raw_audio",
        "raw_video",
        "raw_image",
        "raw_frame",
        "episode_record",
        "object_template",
        "person_record",
        "event_list",
        "vector_embedding",
        "pattern_id",
        "similarity_score",
        "global_winner",
        "semantic_label",
        "word_token",
        "syntax_class",
        "reward",
        "target_topology",
        "replay_buffer",
        "permanent_edge",
        "monotonic_accumulator",
    }
)


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise RelationshipPersistenceContractError(
            f"{role} must be a lowercase technical identifier"
        )
    return value


def _identifiers(values: tuple[str, ...], role: str) -> tuple[str, ...]:
    result = tuple(_identifier(value, role) for value in values)
    if not result or len(set(result)) != len(result):
        raise RelationshipPersistenceContractError(
            f"{role} values must be non-empty and unique"
        )
    return tuple(sorted(result))


@dataclass(frozen=True, slots=True)
class RelationshipPersistenceContract:
    """Admissibility contract, not a persistent state or update equation."""

    contract_id: str
    permission: RuntimePermission
    evidence: EvidenceLevel
    accepted_causes: tuple[str, ...]
    observable_effects: tuple[str, ...]
    required_properties: tuple[str, ...]
    forbidden_roles: tuple[str, ...]
    writes_back: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "contract_id", _identifier(self.contract_id, "contract_id"))
        if self.permission is not RuntimePermission.CONTRACT_ONLY:
            raise RelationshipPersistenceContractError(
                "relationship persistence must remain contract-only"
            )
        if self.evidence is not EvidenceLevel.E0:
            raise RelationshipPersistenceContractError(
                "relationship persistence starts at E0"
            )
        causes = _identifiers(tuple(self.accepted_causes), "accepted_cause")
        effects = _identifiers(tuple(self.observable_effects), "observable_effect")
        properties = _identifiers(tuple(self.required_properties), "required_property")
        forbidden = _identifiers(tuple(self.forbidden_roles), "forbidden_role")
        if not REQUIRED_CAUSES.issubset(causes):
            raise RelationshipPersistenceContractError("required local causes are missing")
        if not REQUIRED_EFFECTS.issubset(effects):
            raise RelationshipPersistenceContractError("required causal effects are missing")
        if not REQUIRED_PROPERTIES.issubset(properties):
            raise RelationshipPersistenceContractError("required organic properties are missing")
        if not FORBIDDEN_PERSISTENCE_ROLES.issubset(forbidden):
            raise RelationshipPersistenceContractError("forbidden persistence roles are missing")
        if (set(causes) | set(effects)) & set(forbidden):
            raise RelationshipPersistenceContractError(
                "accepted causes and effects cannot contain forbidden roles"
            )
        if self.writes_back:
            raise RelationshipPersistenceContractError(
                "an architecture contract cannot write into the field"
            )
        object.__setattr__(self, "accepted_causes", causes)
        object.__setattr__(self, "observable_effects", effects)
        object.__setattr__(self, "required_properties", properties)
        object.__setattr__(self, "forbidden_roles", forbidden)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "permission": self.permission.value,
            "evidence": self.evidence.value,
            "accepted_causes": list(self.accepted_causes),
            "observable_effects": list(self.observable_effects),
            "required_properties": list(self.required_properties),
            "forbidden_roles": list(self.forbidden_roles),
            "writes_back": self.writes_back,
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def reference_relationship_persistence_contract() -> RelationshipPersistenceContract:
    return RelationshipPersistenceContract(
        contract_id="field.relationship_persistence.v1",
        permission=RuntimePermission.CONTRACT_ONLY,
        evidence=EvidenceLevel.E0,
        accepted_causes=tuple(REQUIRED_CAUSES),
        observable_effects=tuple(REQUIRED_EFFECTS),
        required_properties=tuple(REQUIRED_PROPERTIES),
        forbidden_roles=tuple(FORBIDDEN_PERSISTENCE_ROLES),
    )


def relationship_persistence_contract_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(RelationshipPersistenceContract))
