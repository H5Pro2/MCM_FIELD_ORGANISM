"""Immutable preregistration for the first synthetic shared-field experiment."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import re

from .architecture_readiness import EvidenceLevel, RuntimePermission


class GF001MethodologyError(ValueError):
    """Raised when the preregistration selects or relaxes field mechanics."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")

REQUIRED_GF001_CONTROL_BASELINES = frozenset(
    {
        "b0.receptor_projection",
        "b1.hold_state",
    }
)

REQUIRED_GF001_EFFECT_BASELINES = frozenset(
    {
        "b2.symmetric_local_activation_mean",
        "b3.symmetric_contact_and_local_activation_mean",
    }
)

REQUIRED_GF001_BRANCHES = frozenset(
    {
        "original_inputs",
        "local_sample_ablation",
        "current_contact_ablation",
        "explicit_zero_contact",
        "missing_receptor",
        "sample_order_permutation",
        "neuron_order_permutation",
        "horizontal_geometry_reflection",
        "dock_row_exchange",
        "zero_source",
        "same_dock_locality",
        "cross_dock_locality",
        "observer_removal",
        "independent_rebuild",
    }
)

REQUIRED_GF001_MEASUREMENTS = frozenset(
    {
        "position_keyed_activation",
        "local_sample_causal_contrast",
        "current_contact_causal_contrast",
        "sample_order_error",
        "neuron_order_error",
        "reflection_error",
        "dock_exchange_error",
        "zero_source_error",
        "same_dock_effect",
        "cross_dock_effect",
        "observer_effect",
        "afterimage_change",
    }
)

REQUIRED_GF001_STOP_CONDITIONS = frozenset(
    {
        "afterimage_changes",
        "branch_state_is_reused",
        "dock_identity_changes_transition",
        "observer_changes_result",
        "order_changes_result",
        "reflection_breaks_equivariance",
        "same_tick_state_is_read",
        "source_free_activity_appears",
        "unregistered_state_is_required",
    }
)

FORBIDDEN_GF001_ROLES = frozenset(
    {
        "adaptive_parameter",
        "afterimage_update",
        "global_normalization",
        "global_winner",
        "history_carrier",
        "learning_rule",
        "modality_weight",
        "observer_writeback",
        "persistent_edge",
        "previous_self_state_feedback",
        "relationship_state",
        "resource_allocation",
        "reward",
        "semantic_label",
        "target_topology",
        "threshold",
    }
)


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise GF001MethodologyError(
            f"{role} must be a lowercase technical identifier"
        )
    return value


def _identifiers(values: tuple[str, ...], role: str) -> tuple[str, ...]:
    result = tuple(_identifier(value, role) for value in values)
    if not result or len(set(result)) != len(result):
        raise GF001MethodologyError(
            f"{role} values must be non-empty and unique"
        )
    return tuple(sorted(result))


@dataclass(frozen=True, slots=True)
class GF001LocalFieldEffectMethodology:
    """Complete passive method boundary without a selected MCM transition."""

    experiment_id: str
    status: str
    runtime_permission: RuntimePermission
    evidence_target: EvidenceLevel
    geometry_shape: tuple[int, int]
    dock_rows: tuple[tuple[str, int], ...]
    sample_offsets: tuple[tuple[int, int], ...]
    control_baselines: tuple[str, ...]
    effect_baselines: tuple[str, ...]
    branches: tuple[str, ...]
    measurements: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    forbidden_roles: tuple[str, ...]
    synthetic_only: bool = True
    writes_back: bool = False
    selects_runtime_candidate: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "experiment_id",
            _identifier(self.experiment_id, "experiment_id"),
        )
        if self.status != "preregistered":
            raise GF001MethodologyError("GF_001 must remain preregistered")
        if self.runtime_permission is not RuntimePermission.CONTRACT_ONLY:
            raise GF001MethodologyError("GF_001 cannot release runtime mechanics")
        if self.evidence_target is not EvidenceLevel.E2:
            raise GF001MethodologyError(
                "GF_001 targets E2 only for isolated baseline causality"
            )
        if self.geometry_shape != (2, 3):
            raise GF001MethodologyError(
                "GF_001 requires the preregistered two-by-three geometry"
            )
        dock_rows = tuple(
            sorted(
                (
                    _identifier(dock_id, "dock_id"),
                    row,
                )
                for dock_id, row in self.dock_rows
            )
        )
        if dock_rows != (("dock.auditory", 0), ("dock.visual", 1)):
            raise GF001MethodologyError(
                "GF_001 requires one auditory and one visual dock row"
            )
        offsets = tuple(sorted(tuple(offset) for offset in self.sample_offsets))
        required_offsets = ((-1, 0), (0, -1), (0, 1), (1, 0))
        if offsets != required_offsets:
            raise GF001MethodologyError(
                "GF_001 requires the four symmetric axial offsets"
            )

        controls = _identifiers(self.control_baselines, "control_baseline")
        effects = _identifiers(self.effect_baselines, "effect_baseline")
        branches = _identifiers(self.branches, "branch")
        measurements = _identifiers(self.measurements, "measurement")
        stops = _identifiers(self.stop_conditions, "stop_condition")
        forbidden = _identifiers(self.forbidden_roles, "forbidden_role")
        requirements = (
            (REQUIRED_GF001_CONTROL_BASELINES, controls, "control baselines"),
            (REQUIRED_GF001_EFFECT_BASELINES, effects, "effect baselines"),
            (REQUIRED_GF001_BRANCHES, branches, "branches"),
            (REQUIRED_GF001_MEASUREMENTS, measurements, "measurements"),
            (REQUIRED_GF001_STOP_CONDITIONS, stops, "stop conditions"),
            (FORBIDDEN_GF001_ROLES, forbidden, "forbidden roles"),
        )
        for required, actual, label in requirements:
            if not required.issubset(actual):
                raise GF001MethodologyError(f"{label} are incomplete")
        if set(controls + effects + branches + measurements + stops) & set(
            forbidden
        ):
            raise GF001MethodologyError(
                "method roles cannot also be forbidden"
            )
        if not self.synthetic_only:
            raise GF001MethodologyError("GF_001 must remain synthetic")
        if self.writes_back or self.selects_runtime_candidate:
            raise GF001MethodologyError(
                "GF_001 cannot write back or select a runtime candidate"
            )

        object.__setattr__(self, "dock_rows", dock_rows)
        object.__setattr__(self, "sample_offsets", offsets)
        object.__setattr__(self, "control_baselines", controls)
        object.__setattr__(self, "effect_baselines", effects)
        object.__setattr__(self, "branches", branches)
        object.__setattr__(self, "measurements", measurements)
        object.__setattr__(self, "stop_conditions", stops)
        object.__setattr__(self, "forbidden_roles", forbidden)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "experiment_id": self.experiment_id,
            "status": self.status,
            "runtime_permission": self.runtime_permission.value,
            "evidence_target": self.evidence_target.value,
            "geometry_shape": list(self.geometry_shape),
            "dock_rows": [list(item) for item in self.dock_rows],
            "sample_offsets": [list(item) for item in self.sample_offsets],
            "control_baselines": list(self.control_baselines),
            "effect_baselines": list(self.effect_baselines),
            "branches": list(self.branches),
            "measurements": list(self.measurements),
            "stop_conditions": list(self.stop_conditions),
            "forbidden_roles": list(self.forbidden_roles),
            "synthetic_only": self.synthetic_only,
            "writes_back": self.writes_back,
            "selects_runtime_candidate": self.selects_runtime_candidate,
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def reference_gf001_local_field_effect_methodology(
) -> GF001LocalFieldEffectMethodology:
    return GF001LocalFieldEffectMethodology(
        experiment_id="gf.001.local_field_effect",
        status="preregistered",
        runtime_permission=RuntimePermission.CONTRACT_ONLY,
        evidence_target=EvidenceLevel.E2,
        geometry_shape=(2, 3),
        dock_rows=(("dock.auditory", 0), ("dock.visual", 1)),
        sample_offsets=((-1, 0), (0, -1), (0, 1), (1, 0)),
        control_baselines=tuple(REQUIRED_GF001_CONTROL_BASELINES),
        effect_baselines=tuple(REQUIRED_GF001_EFFECT_BASELINES),
        branches=tuple(REQUIRED_GF001_BRANCHES),
        measurements=tuple(REQUIRED_GF001_MEASUREMENTS),
        stop_conditions=tuple(REQUIRED_GF001_STOP_CONDITIONS),
        forbidden_roles=tuple(FORBIDDEN_GF001_ROLES),
    )


def gf001_methodology_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(GF001LocalFieldEffectMethodology))
