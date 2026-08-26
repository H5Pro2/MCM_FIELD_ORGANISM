"""Passive architecture readiness map; never part of field dynamics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re

from .architecture_contract import EvidenceLevel, RuntimePermission


class ArchitecturePlanError(ValueError):
    pass


class BoundaryKind(str, Enum):
    RECEPTOR = "receptor"
    RECEPTOR_DISTRIBUTOR = "receptor_distributor"
    SHARED_FIELD = "shared_field"
    FIELD_CAPABILITY = "field_capability"
    ENERGY_RESOURCE = "energy_resource"
    REFLECTION = "reflection"
    MEMORY = "memory"
    OFFLINE_RECOVERY = "offline_recovery"


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")
_FORBIDDEN_RUNTIME_ROLES = frozenset(
    {
        "semantic_label",
        "pattern_class",
        "reward",
        "target_topology",
        "raw_episode",
        "observer_writeback",
    }
)


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ArchitecturePlanError(f"{role} must be a lowercase technical identifier")
    return value


def _identifiers(values: tuple[str, ...], role: str) -> tuple[str, ...]:
    result = tuple(_identifier(value, role) for value in values)
    if len(set(result)) != len(result):
        raise ArchitecturePlanError(f"{role} values must be unique")
    return result


@dataclass(frozen=True, slots=True)
class ArchitectureBoundary:
    boundary_id: str
    kind: BoundaryKind
    permission: RuntimePermission
    evidence: EvidenceLevel
    accepts: tuple[str, ...] = ()
    emits: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    stateful: bool = False
    writes_back: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "boundary_id", _identifier(self.boundary_id, "boundary_id"))
        object.__setattr__(self, "accepts", _identifiers(tuple(self.accepts), "accepted_role"))
        object.__setattr__(self, "emits", _identifiers(tuple(self.emits), "emitted_role"))
        object.__setattr__(self, "depends_on", _identifiers(tuple(self.depends_on), "dependency"))
        if not isinstance(self.kind, BoundaryKind):
            raise ArchitecturePlanError("kind must be a BoundaryKind")
        if not isinstance(self.permission, RuntimePermission):
            raise ArchitecturePlanError("permission must be a RuntimePermission")
        if not isinstance(self.evidence, EvidenceLevel):
            raise ArchitecturePlanError("evidence must be an EvidenceLevel")
        if set(self.accepts + self.emits) & _FORBIDDEN_RUNTIME_ROLES:
            raise ArchitecturePlanError("architecture boundary contains a forbidden runtime role")
        if self.permission is not RuntimePermission.PASSIVE_AVAILABLE and self.writes_back:
            raise ArchitecturePlanError("closed or contract-only boundaries cannot write back")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "boundary_id": self.boundary_id,
            "kind": self.kind.value,
            "permission": self.permission.value,
            "evidence": self.evidence.value,
            "accepts": list(self.accepts),
            "emits": list(self.emits),
            "depends_on": list(self.depends_on),
            "stateful": self.stateful,
            "writes_back": self.writes_back,
        }


@dataclass(frozen=True, slots=True)
class ArchitectureReadinessPlan:
    boundaries: tuple[ArchitectureBoundary, ...]

    def __post_init__(self) -> None:
        boundaries = tuple(self.boundaries)
        if not boundaries:
            raise ArchitecturePlanError("architecture plan requires at least one boundary")
        ids = [boundary.boundary_id for boundary in boundaries]
        if len(set(ids)) != len(ids):
            raise ArchitecturePlanError("architecture boundary ids must be unique")
        known = set(ids)
        for boundary in boundaries:
            missing = set(boundary.depends_on) - known
            if missing:
                raise ArchitecturePlanError(
                    f"unknown dependencies for {boundary.boundary_id}: {sorted(missing)}"
                )
        object.__setattr__(
            self,
            "boundaries",
            tuple(sorted(boundaries, key=lambda boundary: boundary.boundary_id)),
        )

    def boundary(self, boundary_id: str) -> ArchitectureBoundary:
        boundary_id = _identifier(boundary_id, "boundary_id")
        for boundary in self.boundaries:
            if boundary.boundary_id == boundary_id:
                return boundary
        raise ArchitecturePlanError(f"unknown architecture boundary: {boundary_id}")

    @property
    def passive_available(self) -> tuple[str, ...]:
        return tuple(
            boundary.boundary_id
            for boundary in self.boundaries
            if boundary.permission is RuntimePermission.PASSIVE_AVAILABLE
        )

    @property
    def research_closed(self) -> tuple[str, ...]:
        return tuple(
            boundary.boundary_id
            for boundary in self.boundaries
            if boundary.permission is RuntimePermission.RESEARCH_CLOSED
        )

    def canonical_payload(self) -> dict[str, object]:
        return {"boundaries": [boundary.canonical_payload() for boundary in self.boundaries]}

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def reference_architecture_plan() -> ArchitectureReadinessPlan:
    """Return the documented plan without constructing any runtime mechanism."""

    return ArchitectureReadinessPlan(
        boundaries=(
            ArchitectureBoundary(
                "auditory.receptor",
                BoundaryKind.RECEPTOR,
                RuntimePermission.PASSIVE_AVAILABLE,
                EvidenceLevel.E1,
                accepts=("finite_audio_chunks",),
                emits=("auditory_receptor_state",),
            ),
            ArchitectureBoundary(
                "visual.receptor",
                BoundaryKind.RECEPTOR,
                RuntimePermission.PASSIVE_AVAILABLE,
                EvidenceLevel.E2,
                accepts=("finite_video_frames",),
                emits=("visual_receptor_state",),
            ),
            ArchitectureBoundary(
                "tactile.receptor",
                BoundaryKind.RECEPTOR,
                RuntimePermission.RESEARCH_CLOSED,
                EvidenceLevel.E0,
            ),
            ArchitectureBoundary(
                "receptor.distributor",
                BoundaryKind.RECEPTOR_DISTRIBUTOR,
                RuntimePermission.PASSIVE_AVAILABLE,
                EvidenceLevel.E1,
                accepts=("receptor_contact_frame",),
                emits=("distributed_receptor_contact",),
                depends_on=(
                    "auditory.receptor",
                    "visual.receptor",
                    "tactile.receptor",
                ),
            ),
            ArchitectureBoundary(
                "mcm.shared_field",
                BoundaryKind.SHARED_FIELD,
                RuntimePermission.PASSIVE_AVAILABLE,
                EvidenceLevel.E1,
                accepts=("distributed_receptor_contact",),
                emits=("shared_mcm_field_state",),
                depends_on=("receptor.distributor",),
                stateful=True,
            ),
            ArchitectureBoundary(
                "reflection.boundary",
                BoundaryKind.REFLECTION,
                RuntimePermission.RESEARCH_CLOSED,
                EvidenceLevel.E0,
                accepts=("shared_mcm_field_state",),
                depends_on=("mcm.shared_field",),
            ),
            ArchitectureBoundary(
                "field.semantic_resonance",
                BoundaryKind.FIELD_CAPABILITY,
                RuntimePermission.RESEARCH_CLOSED,
                EvidenceLevel.E0,
                accepts=("shared_mcm_field_state",),
                depends_on=("mcm.shared_field",),
            ),
            ArchitectureBoundary(
                "field.topology_memory",
                BoundaryKind.MEMORY,
                RuntimePermission.RESEARCH_CLOSED,
                EvidenceLevel.E0,
                accepts=(
                    "repeated_local_joint_field_effect",
                    "prior_local_field_organization",
                    "local_available_resource",
                ),
                emits=("changed_local_field_disposition",),
                depends_on=("mcm.shared_field",),
                stateful=True,
            ),
            ArchitectureBoundary(
                "field.energy_resource_boundary",
                BoundaryKind.ENERGY_RESOURCE,
                RuntimePermission.CONTRACT_ONLY,
                EvidenceLevel.E0,
                accepts=(
                    "current_world_contact",
                    "prior_internal_field_activity",
                    "prior_mcm_afterimage",
                    "local_available_resource",
                ),
                depends_on=("mcm.shared_field",),
            ),
            ArchitectureBoundary(
                "offline.recovery_boundary",
                BoundaryKind.OFFLINE_RECOVERY,
                RuntimePermission.CONTRACT_ONLY,
                EvidenceLevel.E0,
                accepts=("reduced_world_contact",),
                depends_on=("field.energy_resource_boundary",),
            ),
            ArchitectureBoundary(
                "field.self_regulation",
                BoundaryKind.FIELD_CAPABILITY,
                RuntimePermission.CONTRACT_ONLY,
                EvidenceLevel.E0,
                accepts=(
                    "prior_local_field_history",
                    "prior_internal_field_activity",
                    "local_available_resource",
                    "reduced_world_contact",
                ),
                emits=("candidate_local_field_disposition",),
                depends_on=(
                    "mcm.shared_field",
                    "field.energy_resource_boundary",
                ),
                stateful=True,
            ),
            ArchitectureBoundary(
                "sensory.self_regulation",
                BoundaryKind.RECEPTOR,
                RuntimePermission.CONTRACT_ONLY,
                EvidenceLevel.E0,
                accepts=(
                    "local_receptor_history",
                    "local_field_consequence",
                    "local_available_resource",
                    "reduced_world_contact",
                ),
                emits=("candidate_local_receptor_disposition",),
                depends_on=(
                    "auditory.receptor",
                    "visual.receptor",
                    "tactile.receptor",
                    "field.self_regulation",
                    "field.energy_resource_boundary",
                ),
                stateful=True,
            ),
        )
    )
