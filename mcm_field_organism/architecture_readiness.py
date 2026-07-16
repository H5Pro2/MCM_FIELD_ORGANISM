"""Passive architecture readiness map; never part of field dynamics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re


class ArchitecturePlanError(ValueError):
    pass


class EvidenceLevel(str, Enum):
    E0 = "e0"
    E1 = "e1"
    E2 = "e2"
    E3 = "e3"
    E4 = "e4"
    E5 = "e5"
    E6 = "e6"


class RuntimePermission(str, Enum):
    PASSIVE_AVAILABLE = "passive_available"
    CONTRACT_ONLY = "contract_only"
    RESEARCH_CLOSED = "research_closed"


class BoundaryKind(str, Enum):
    RECEPTOR = "receptor"
    SENSOR_FIELD = "sensor_field"
    DISTRIBUTOR = "distributor"
    PASSIVE_CHECKER = "passive_checker"
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
                "auditory.mcm_field",
                BoundaryKind.SENSOR_FIELD,
                RuntimePermission.CONTRACT_ONLY,
                EvidenceLevel.E0,
                accepts=("auditory_receptor_state",),
                emits=("mcm_field_window",),
                depends_on=("auditory.receptor",),
                stateful=True,
            ),
            ArchitectureBoundary(
                "visual.mcm_field",
                BoundaryKind.SENSOR_FIELD,
                RuntimePermission.CONTRACT_ONLY,
                EvidenceLevel.E2,
                accepts=("visual_receptor_state",),
                emits=("mcm_field_window",),
                depends_on=("visual.receptor",),
                stateful=True,
            ),
            ArchitectureBoundary(
                "tactile.mcm_field",
                BoundaryKind.SENSOR_FIELD,
                RuntimePermission.RESEARCH_CLOSED,
                EvidenceLevel.E0,
                emits=("mcm_field_window",),
                depends_on=("tactile.receptor",),
                stateful=True,
            ),
            ArchitectureBoundary(
                "mcm.distributor",
                BoundaryKind.DISTRIBUTOR,
                RuntimePermission.PASSIVE_AVAILABLE,
                EvidenceLevel.E1,
                accepts=("mcm_field_window",),
                emits=("distributed_mcm_constellation",),
                depends_on=(
                    "auditory.mcm_field",
                    "visual.mcm_field",
                    "tactile.mcm_field",
                ),
            ),
            ArchitectureBoundary(
                "multimodal.pattern_checker",
                BoundaryKind.PASSIVE_CHECKER,
                RuntimePermission.PASSIVE_AVAILABLE,
                EvidenceLevel.E1,
                accepts=("distributed_mcm_constellation",),
                emits=("passive_pattern_result",),
                depends_on=("mcm.distributor",),
            ),
            ArchitectureBoundary(
                "reflection.boundary",
                BoundaryKind.REFLECTION,
                RuntimePermission.RESEARCH_CLOSED,
                EvidenceLevel.E0,
                accepts=("distributed_mcm_constellation",),
                depends_on=("mcm.distributor",),
            ),
            ArchitectureBoundary(
                "memory.sensory_afterimage",
                BoundaryKind.MEMORY,
                RuntimePermission.CONTRACT_ONLY,
                EvidenceLevel.E0,
                accepts=("mcm_field_activation",),
                emits=("mcm_field_afterimage",),
                depends_on=("auditory.mcm_field",),
                stateful=True,
            ),
            ArchitectureBoundary(
                "memory.relationship_history",
                BoundaryKind.MEMORY,
                RuntimePermission.RESEARCH_CLOSED,
                EvidenceLevel.E0,
                accepts=("local_joint_field_effect",),
                depends_on=("mcm.distributor",),
                stateful=True,
            ),
            ArchitectureBoundary(
                "memory.developed_topology",
                BoundaryKind.MEMORY,
                RuntimePermission.RESEARCH_CLOSED,
                EvidenceLevel.E0,
                accepts=("local_relationship_history",),
                depends_on=("memory.relationship_history",),
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
                depends_on=(
                    "auditory.mcm_field",
                    "visual.mcm_field",
                    "tactile.mcm_field",
                ),
            ),
            ArchitectureBoundary(
                "offline.recovery_boundary",
                BoundaryKind.OFFLINE_RECOVERY,
                RuntimePermission.CONTRACT_ONLY,
                EvidenceLevel.E0,
                accepts=("reduced_world_contact",),
                depends_on=("field.energy_resource_boundary",),
            ),
        )
    )
