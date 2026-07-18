"""Contract-only boundary for functional equivalence of field histories."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import re

from .architecture_readiness import EvidenceLevel, RuntimePermission


class TemporalFunctionalEquivalenceContractError(ValueError):
    """Raised when the contract preselects a history effect."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")

REQUIRED_EQUIVALENCE_SCOPE = frozenset(
    {
        "registered_probe_family_only",
        "matched_external_present",
        "matched_fast_field_present",
        "isolated_candidate_history_carrier",
    }
)

REQUIRED_EQUIVALENCE_RULES = frozenset(
    {
        "all_registered_probe_consequences_equal",
        "equivalence_is_probe_relative",
        "history_identity_not_required",
        "no_complete_history_preservation_requirement",
    }
)

REQUIRED_DISTINCTION_RULES = frozenset(
    {
        "registered_probe_consequence_differs",
        "difference_reproduces",
        "difference_follows_carrier_swap",
        "difference_vanishes_on_carrier_neutralization",
        "difference_absent_without_history",
        "observer_removed_without_effect_change",
    }
)

REQUIRED_CONTROLS = frozenset(
    {
        "distinct_supported_histories",
        "identical_holdout_probe",
        "matched_receptor_present",
        "matched_fast_neuron_state",
        "candidate_carrier_isolation",
        "carrier_swap",
        "carrier_neutralization",
        "no_history_control",
        "independent_branch_rebuild",
        "observer_removal",
    }
)

FORBIDDEN_FUNCTIONAL_EQUIVALENCE_ROLES = frozenset(
    {
        "history_template",
        "sequence_archive",
        "semantic_label",
        "pattern_class",
        "target_response",
        "branch_specific_reader",
        "global_winner",
        "reward",
        "selected_representation",
        "fixed_history_effect",
        "observer_writeback",
        "runtime_field_writeback",
        "learning_rule",
        "target_topology",
    }
)


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise TemporalFunctionalEquivalenceContractError(
            f"{role} must be a lowercase technical identifier"
        )
    return value


def _identifiers(values: tuple[str, ...], role: str) -> tuple[str, ...]:
    result = tuple(_identifier(value, role) for value in values)
    if not result or len(set(result)) != len(result):
        raise TemporalFunctionalEquivalenceContractError(
            f"{role} values must be non-empty and unique"
        )
    return tuple(sorted(result))


@dataclass(frozen=True, slots=True)
class TemporalFunctionalEquivalenceContract:
    """Preregistration boundary, not a history carrier or reader."""

    contract_id: str
    permission: RuntimePermission
    evidence: EvidenceLevel
    equivalence_scope: tuple[str, ...]
    equivalence_rules: tuple[str, ...]
    distinction_rules: tuple[str, ...]
    required_controls: tuple[str, ...]
    forbidden_roles: tuple[str, ...]
    writes_back: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "contract_id",
            _identifier(self.contract_id, "contract_id"),
        )
        if self.permission is not RuntimePermission.CONTRACT_ONLY:
            raise TemporalFunctionalEquivalenceContractError(
                "functional equivalence must remain contract-only"
            )
        if self.evidence is not EvidenceLevel.E0:
            raise TemporalFunctionalEquivalenceContractError(
                "functional equivalence starts at E0"
            )
        scope = _identifiers(
            tuple(self.equivalence_scope),
            "equivalence_scope",
        )
        equivalence = _identifiers(
            tuple(self.equivalence_rules),
            "equivalence_rule",
        )
        distinction = _identifiers(
            tuple(self.distinction_rules),
            "distinction_rule",
        )
        controls = _identifiers(
            tuple(self.required_controls),
            "required_control",
        )
        forbidden = _identifiers(
            tuple(self.forbidden_roles),
            "forbidden_role",
        )
        requirements = (
            (REQUIRED_EQUIVALENCE_SCOPE, scope, "equivalence scope"),
            (REQUIRED_EQUIVALENCE_RULES, equivalence, "equivalence rules"),
            (REQUIRED_DISTINCTION_RULES, distinction, "distinction rules"),
            (REQUIRED_CONTROLS, controls, "required controls"),
            (
                FORBIDDEN_FUNCTIONAL_EQUIVALENCE_ROLES,
                forbidden,
                "forbidden roles",
            ),
        )
        for required, actual, label in requirements:
            if not required.issubset(actual):
                raise TemporalFunctionalEquivalenceContractError(
                    f"{label} are incomplete"
                )
        permitted = set(scope) | set(equivalence) | set(distinction) | set(controls)
        if permitted & set(forbidden):
            raise TemporalFunctionalEquivalenceContractError(
                "required contract roles cannot also be forbidden"
            )
        if self.writes_back:
            raise TemporalFunctionalEquivalenceContractError(
                "the equivalence contract cannot change field state"
            )
        object.__setattr__(self, "equivalence_scope", scope)
        object.__setattr__(self, "equivalence_rules", equivalence)
        object.__setattr__(self, "distinction_rules", distinction)
        object.__setattr__(self, "required_controls", controls)
        object.__setattr__(self, "forbidden_roles", forbidden)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "permission": self.permission.value,
            "evidence": self.evidence.value,
            "equivalence_scope": list(self.equivalence_scope),
            "equivalence_rules": list(self.equivalence_rules),
            "distinction_rules": list(self.distinction_rules),
            "required_controls": list(self.required_controls),
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


def reference_temporal_functional_equivalence_contract(
) -> TemporalFunctionalEquivalenceContract:
    return TemporalFunctionalEquivalenceContract(
        contract_id="field.temporal_functional_equivalence.v1",
        permission=RuntimePermission.CONTRACT_ONLY,
        evidence=EvidenceLevel.E0,
        equivalence_scope=tuple(REQUIRED_EQUIVALENCE_SCOPE),
        equivalence_rules=tuple(REQUIRED_EQUIVALENCE_RULES),
        distinction_rules=tuple(REQUIRED_DISTINCTION_RULES),
        required_controls=tuple(REQUIRED_CONTROLS),
        forbidden_roles=tuple(FORBIDDEN_FUNCTIONAL_EQUIVALENCE_ROLES),
    )


def temporal_functional_equivalence_contract_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name for item in fields(TemporalFunctionalEquivalenceContract)
    )
