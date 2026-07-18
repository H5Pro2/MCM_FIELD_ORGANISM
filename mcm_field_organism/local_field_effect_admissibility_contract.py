"""Contract-only boundary for the first isolated local field effect."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import re

from .architecture_readiness import EvidenceLevel, RuntimePermission


class LocalFieldEffectAdmissibilityContractError(ValueError):
    """Raised when the contract preselects or overstates field dynamics."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")

REQUIRED_LOCAL_FIELD_INPUTS = frozenset(
    {
        "current_receptor_contact_or_absence",
        "prior_tick_local_field_samples",
        "relative_sample_geometry",
    }
)

REQUIRED_LOCAL_FIELD_INVARIANTS = frozenset(
    {
        "atomic_prior_tick_causality",
        "bounded_normalized_output",
        "candidate_self_state_independence",
        "identical_transition_at_every_neuron",
        "modality_neutral_transition",
        "no_same_tick_recursion",
        "observer_independence",
        "receptor_absence_distinct_from_zero",
        "sample_order_invariance",
        "spatial_reflection_equivariance",
        "zero_source_quiescence",
    }
)

REQUIRED_LOCAL_FIELD_CONTROLS = frozenset(
    {
        "receptor_projection_baseline",
        "hold_state_baseline",
        "local_sample_ablation",
        "receptor_contact_ablation",
        "sample_iteration_permutation",
        "neuron_iteration_permutation",
        "geometry_reflection",
        "zero_source_control",
        "missing_receptor_control",
        "same_dock_and_cross_dock_locality",
        "independent_branch_rebuild",
        "observer_removal",
    }
)

REQUIRED_LOCAL_FIELD_INTERPRETATION_LIMITS = frozenset(
    {
        "causal_local_effect_only",
        "fixed_transition_is_baseline",
        "propagation_is_not_topology",
        "repetition_is_not_learning",
        "single_step_effect_is_not_memory",
        "no_field_intelligence_claim",
    }
)

FORBIDDEN_LOCAL_FIELD_EFFECT_ROLES = frozenset(
    {
        "afterimage_update",
        "previous_self_state_feedback",
        "history_carrier",
        "sequence_archive",
        "persistent_edge",
        "adaptive_weight",
        "relationship_state",
        "resource_allocation",
        "decay_rate",
        "threshold",
        "direction_label",
        "modality_weight",
        "global_normalization",
        "global_winner",
        "semantic_label",
        "pattern_class",
        "target_response",
        "reward",
        "learning_rule",
        "target_topology",
        "observer_writeback",
    }
)


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise LocalFieldEffectAdmissibilityContractError(
            f"{role} must be a lowercase technical identifier"
        )
    return value


def _identifiers(values: tuple[str, ...], role: str) -> tuple[str, ...]:
    result = tuple(_identifier(value, role) for value in values)
    if not result or len(set(result)) != len(result):
        raise LocalFieldEffectAdmissibilityContractError(
            f"{role} values must be non-empty and unique"
        )
    return tuple(sorted(result))


@dataclass(frozen=True, slots=True)
class LocalFieldEffectAdmissibilityContract:
    """E0 boundary contract, not a neuron transition."""

    contract_id: str
    permission: RuntimePermission
    evidence: EvidenceLevel
    allowed_inputs: tuple[str, ...]
    required_invariants: tuple[str, ...]
    required_controls: tuple[str, ...]
    interpretation_limits: tuple[str, ...]
    forbidden_roles: tuple[str, ...]
    writes_back: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "contract_id",
            _identifier(self.contract_id, "contract_id"),
        )
        if self.permission is not RuntimePermission.CONTRACT_ONLY:
            raise LocalFieldEffectAdmissibilityContractError(
                "local field effect must remain contract-only"
            )
        if self.evidence is not EvidenceLevel.E0:
            raise LocalFieldEffectAdmissibilityContractError(
                "local field effect starts at E0"
            )
        inputs = _identifiers(tuple(self.allowed_inputs), "allowed_input")
        invariants = _identifiers(
            tuple(self.required_invariants),
            "required_invariant",
        )
        controls = _identifiers(
            tuple(self.required_controls),
            "required_control",
        )
        limits = _identifiers(
            tuple(self.interpretation_limits),
            "interpretation_limit",
        )
        forbidden = _identifiers(
            tuple(self.forbidden_roles),
            "forbidden_role",
        )
        requirements = (
            (REQUIRED_LOCAL_FIELD_INPUTS, inputs, "allowed inputs"),
            (
                REQUIRED_LOCAL_FIELD_INVARIANTS,
                invariants,
                "required invariants",
            ),
            (REQUIRED_LOCAL_FIELD_CONTROLS, controls, "required controls"),
            (
                REQUIRED_LOCAL_FIELD_INTERPRETATION_LIMITS,
                limits,
                "interpretation limits",
            ),
            (
                FORBIDDEN_LOCAL_FIELD_EFFECT_ROLES,
                forbidden,
                "forbidden roles",
            ),
        )
        for required, actual, label in requirements:
            if not required.issubset(actual):
                raise LocalFieldEffectAdmissibilityContractError(
                    f"{label} are incomplete"
                )
        permitted = set(inputs) | set(invariants) | set(controls) | set(limits)
        if permitted & set(forbidden):
            raise LocalFieldEffectAdmissibilityContractError(
                "required contract roles cannot also be forbidden"
            )
        if self.writes_back:
            raise LocalFieldEffectAdmissibilityContractError(
                "the admissibility contract cannot change field state"
            )
        object.__setattr__(self, "allowed_inputs", inputs)
        object.__setattr__(self, "required_invariants", invariants)
        object.__setattr__(self, "required_controls", controls)
        object.__setattr__(self, "interpretation_limits", limits)
        object.__setattr__(self, "forbidden_roles", forbidden)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "permission": self.permission.value,
            "evidence": self.evidence.value,
            "allowed_inputs": list(self.allowed_inputs),
            "required_invariants": list(self.required_invariants),
            "required_controls": list(self.required_controls),
            "interpretation_limits": list(self.interpretation_limits),
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


def reference_local_field_effect_admissibility_contract(
) -> LocalFieldEffectAdmissibilityContract:
    return LocalFieldEffectAdmissibilityContract(
        contract_id="field.local_effect_admissibility.v1",
        permission=RuntimePermission.CONTRACT_ONLY,
        evidence=EvidenceLevel.E0,
        allowed_inputs=tuple(REQUIRED_LOCAL_FIELD_INPUTS),
        required_invariants=tuple(REQUIRED_LOCAL_FIELD_INVARIANTS),
        required_controls=tuple(REQUIRED_LOCAL_FIELD_CONTROLS),
        interpretation_limits=tuple(
            REQUIRED_LOCAL_FIELD_INTERPRETATION_LIMITS
        ),
        forbidden_roles=tuple(FORBIDDEN_LOCAL_FIELD_EFFECT_ROLES),
    )


def local_field_effect_admissibility_contract_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name for item in fields(LocalFieldEffectAdmissibilityContract)
    )
