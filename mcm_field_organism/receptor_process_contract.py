"""Architecture-only admissibility contract for local receptor processes."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import re

from .architecture_contract import EvidenceLevel, RuntimePermission


class ReceptorProcessContractError(ValueError):
    """Raised when a receptor-process contract preselects input dynamics."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")

REQUIRED_RECEPTOR_PROCESS_CAUSES = frozenset(
    {
        "new_local_source_contact",
        "source_support_progress",
        "explicit_test_reset",
    }
)

REQUIRED_RECEPTOR_PROCESS_OBSERVATIONS = frozenset(
    {
        "completed_snapshot_emission",
        "finite_history_loss_for_stateful_process",
        "fresh_probe_equivalence_for_stateless_process",
        "absence_without_contact_inference",
        "source_provenance_preservation",
    }
)

REQUIRED_RECEPTOR_PROCESS_PROPERTIES = frozenset(
    {
        "modality_local_state_ownership",
        "causal_source_update",
        "finite_process_state",
        "explicit_statelessness_allowed",
        "process_specific_dynamics",
        "shared_immutable_snapshot_interface",
        "native_source_clock_preservation",
        "observer_independence",
        "no_field_writeback",
        "no_implicit_hold",
        "no_missing_contact_substitution",
        "representation_open",
    }
)

FORBIDDEN_RECEPTOR_PROCESS_ROLES = frozenset(
    {
        "sample_and_hold",
        "valid_until",
        "last_value_buffer",
        "invented_contact_duration",
        "forced_shared_dynamics",
        "shared_window_size",
        "shared_hop_size",
        "shared_decay_rate",
        "global_rate_normalization",
        "modality_weight",
        "modality_winner",
        "field_feedback",
        "field_activation",
        "relationship_memory",
        "semantic_label",
        "object_class",
        "pattern_id",
        "reward",
        "target_topology",
        "raw_payload_retention",
    }
)


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ReceptorProcessContractError(
            f"{role} must be a lowercase technical identifier"
        )
    return value


def _identifiers(values: tuple[str, ...], role: str) -> tuple[str, ...]:
    result = tuple(_identifier(value, role) for value in values)
    if not result or len(set(result)) != len(result):
        raise ReceptorProcessContractError(
            f"{role} values must be non-empty and unique"
        )
    return tuple(sorted(result))


@dataclass(frozen=True, slots=True)
class ReceptorProcessContract:
    """Boundary contract, not a receptor state or transition equation."""

    contract_id: str
    permission: RuntimePermission
    evidence: EvidenceLevel
    accepted_causes: tuple[str, ...]
    required_observations: tuple[str, ...]
    required_properties: tuple[str, ...]
    forbidden_roles: tuple[str, ...]
    writes_back: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "contract_id",
            _identifier(self.contract_id, "contract_id"),
        )
        if self.permission is not RuntimePermission.CONTRACT_ONLY:
            raise ReceptorProcessContractError(
                "receptor process must remain contract-only"
            )
        if self.evidence is not EvidenceLevel.E0:
            raise ReceptorProcessContractError(
                "the future common receptor-process contract starts at E0"
            )
        causes = _identifiers(tuple(self.accepted_causes), "accepted_cause")
        observations = _identifiers(
            tuple(self.required_observations), "required_observation"
        )
        properties = _identifiers(
            tuple(self.required_properties), "required_property"
        )
        forbidden = _identifiers(tuple(self.forbidden_roles), "forbidden_role")
        if not REQUIRED_RECEPTOR_PROCESS_CAUSES.issubset(causes):
            raise ReceptorProcessContractError(
                "required receptor-process causes are missing"
            )
        if not REQUIRED_RECEPTOR_PROCESS_OBSERVATIONS.issubset(observations):
            raise ReceptorProcessContractError(
                "required receptor-process observations are missing"
            )
        if not REQUIRED_RECEPTOR_PROCESS_PROPERTIES.issubset(properties):
            raise ReceptorProcessContractError(
                "required receptor-process properties are missing"
            )
        if not FORBIDDEN_RECEPTOR_PROCESS_ROLES.issubset(forbidden):
            raise ReceptorProcessContractError(
                "forbidden receptor-process roles are missing"
            )
        if (set(causes) | set(observations)) & set(forbidden):
            raise ReceptorProcessContractError(
                "causes and observations cannot contain forbidden roles"
            )
        if self.writes_back:
            raise ReceptorProcessContractError(
                "an architecture contract cannot change receptor or field state"
            )
        object.__setattr__(self, "accepted_causes", causes)
        object.__setattr__(self, "required_observations", observations)
        object.__setattr__(self, "required_properties", properties)
        object.__setattr__(self, "forbidden_roles", forbidden)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "permission": self.permission.value,
            "evidence": self.evidence.value,
            "accepted_causes": list(self.accepted_causes),
            "required_observations": list(self.required_observations),
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


def reference_receptor_process_contract() -> ReceptorProcessContract:
    return ReceptorProcessContract(
        contract_id="sensory.receptor_process.v1",
        permission=RuntimePermission.CONTRACT_ONLY,
        evidence=EvidenceLevel.E0,
        accepted_causes=tuple(REQUIRED_RECEPTOR_PROCESS_CAUSES),
        required_observations=tuple(REQUIRED_RECEPTOR_PROCESS_OBSERVATIONS),
        required_properties=tuple(REQUIRED_RECEPTOR_PROCESS_PROPERTIES),
        forbidden_roles=tuple(FORBIDDEN_RECEPTOR_PROCESS_ROLES),
    )


def receptor_process_contract_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(ReceptorProcessContract))
