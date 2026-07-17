"""Architecture-only contract for future organic sensory self-regulation."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import re

from .architecture_readiness import EvidenceLevel, RuntimePermission


class SensorySelfRegulationContractError(ValueError):
    """Raised when self-regulation preprograms a gain controller."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")

REQUIRED_REGULATION_CAUSES = frozenset(
    {
        "local_receptor_history",
        "local_field_consequence",
        "local_available_resource",
        "reduced_world_contact",
    }
)

REQUIRED_REGULATION_EFFECTS = frozenset(
    {
        "changed_later_local_receptor_intake",
        "changed_later_local_dynamic_range",
        "changed_local_energy_cost",
        "reversible_local_sensitivity_change",
        "recovery_toward_prior_range",
    }
)

REQUIRED_REGULATION_PROPERTIES = frozenset(
    {
        "local_origin",
        "world_history_dependence",
        "causal_later_effect",
        "modality_locality",
        "source_provenance",
        "finite_sensitivity_range",
        "finite_resource_use",
        "atomic_time",
        "observer_independence",
        "device_independence",
        "no_same_step_self_evidence",
        "reversible_adaptation",
        "recovery_without_replay",
        "baseline_separation",
        "representation_open",
    }
)

REQUIRED_REGULATION_BASELINES = frozenset(
    {
        "fixed_gain",
        "automatic_gain_control",
        "static_clipping",
        "fatigue_recovery_integrator",
        "multi_timescale_leaky_adaptation",
    }
)

FORBIDDEN_REGULATION_ROLES = frozenset(
    {
        "device_volume",
        "operating_system_gain",
        "microphone_gain",
        "camera_exposure_control",
        "direct_world_control",
        "target_loudness",
        "target_brightness",
        "automatic_gain_control",
        "global_gain",
        "global_controller",
        "fixed_adaptation_rate",
        "fixed_activation_threshold",
        "modality_winner",
        "attention_command",
        "reflection_command",
        "semantic_label",
        "object_class",
        "pattern_id",
        "reward",
        "target_topology",
        "raw_audio",
        "raw_video",
        "replay_buffer",
    }
)


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise SensorySelfRegulationContractError(
            f"{role} must be a lowercase technical identifier"
        )
    return value


def _identifiers(values: tuple[str, ...], role: str) -> tuple[str, ...]:
    result = tuple(_identifier(value, role) for value in values)
    if not result or len(set(result)) != len(result):
        raise SensorySelfRegulationContractError(
            f"{role} values must be non-empty and unique"
        )
    return tuple(sorted(result))


@dataclass(frozen=True, slots=True)
class SensorySelfRegulationContract:
    """Admissibility contract, not a sensitivity state or update equation."""

    contract_id: str
    permission: RuntimePermission
    evidence: EvidenceLevel
    accepted_causes: tuple[str, ...]
    observable_effects: tuple[str, ...]
    required_properties: tuple[str, ...]
    required_baselines: tuple[str, ...]
    forbidden_roles: tuple[str, ...]
    writes_back: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "contract_id",
            _identifier(self.contract_id, "contract_id"),
        )
        if self.permission is not RuntimePermission.CONTRACT_ONLY:
            raise SensorySelfRegulationContractError(
                "sensory self-regulation must remain contract-only"
            )
        if self.evidence is not EvidenceLevel.E0:
            raise SensorySelfRegulationContractError(
                "sensory self-regulation starts at E0"
            )
        causes = _identifiers(tuple(self.accepted_causes), "accepted_cause")
        effects = _identifiers(tuple(self.observable_effects), "observable_effect")
        properties = _identifiers(
            tuple(self.required_properties),
            "required_property",
        )
        baselines = _identifiers(tuple(self.required_baselines), "required_baseline")
        forbidden = _identifiers(tuple(self.forbidden_roles), "forbidden_role")
        if not REQUIRED_REGULATION_CAUSES.issubset(causes):
            raise SensorySelfRegulationContractError(
                "required local causes are missing"
            )
        if not REQUIRED_REGULATION_EFFECTS.issubset(effects):
            raise SensorySelfRegulationContractError(
                "required later effects are missing"
            )
        if not REQUIRED_REGULATION_PROPERTIES.issubset(properties):
            raise SensorySelfRegulationContractError(
                "required organic properties are missing"
            )
        if not REQUIRED_REGULATION_BASELINES.issubset(baselines):
            raise SensorySelfRegulationContractError(
                "required regulation baselines are missing"
            )
        if not FORBIDDEN_REGULATION_ROLES.issubset(forbidden):
            raise SensorySelfRegulationContractError(
                "forbidden controller roles are missing"
            )
        if (set(causes) | set(effects)) & set(forbidden):
            raise SensorySelfRegulationContractError(
                "accepted causes and effects cannot contain forbidden roles"
            )
        if self.writes_back:
            raise SensorySelfRegulationContractError(
                "an architecture contract cannot change receptor intake"
            )
        object.__setattr__(self, "accepted_causes", causes)
        object.__setattr__(self, "observable_effects", effects)
        object.__setattr__(self, "required_properties", properties)
        object.__setattr__(self, "required_baselines", baselines)
        object.__setattr__(self, "forbidden_roles", forbidden)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "permission": self.permission.value,
            "evidence": self.evidence.value,
            "accepted_causes": list(self.accepted_causes),
            "observable_effects": list(self.observable_effects),
            "required_properties": list(self.required_properties),
            "required_baselines": list(self.required_baselines),
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


def reference_sensory_self_regulation_contract(
) -> SensorySelfRegulationContract:
    return SensorySelfRegulationContract(
        contract_id="sensory.self_regulation.v1",
        permission=RuntimePermission.CONTRACT_ONLY,
        evidence=EvidenceLevel.E0,
        accepted_causes=tuple(REQUIRED_REGULATION_CAUSES),
        observable_effects=tuple(REQUIRED_REGULATION_EFFECTS),
        required_properties=tuple(REQUIRED_REGULATION_PROPERTIES),
        required_baselines=tuple(REQUIRED_REGULATION_BASELINES),
        forbidden_roles=tuple(FORBIDDEN_REGULATION_ROLES),
    )


def sensory_self_regulation_contract_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(SensorySelfRegulationContract))
